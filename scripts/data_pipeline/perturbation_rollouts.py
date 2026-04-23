"""Phase 2B + 2D (merged) — initial-state perturbation rollouts.

Diag 6 established that mid-run branching needs engine modification. So both
2B (mild counterfactual ±1–3) and 2D (stress injection extremes ≥8 / ≤2) use
the same mechanism: **pick a baseline waypoint, rebuild it as an initial
AgentState with the perturbation applied, run a fresh short rollout**.

This is a weaker approximation than true mid-run branching — the agent
"forgets" the trajectory that led to the perturbed state — but for behavior
cloning of ``state → action`` the loss of temporal context is acceptable
(the current model has no history input anyway).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.simulation.training_samples import (  # noqa: E402
    extract_samples,
    state_to_feature_vector,
)
from scripts.data_pipeline._common import (  # noqa: E402
    make_peter_state,
    register_domain_types,
    run_peter,
)

FEATURE_NAMES = [
    "fear", "hope", "grief", "confusion", "love",
    "fatigue", "hunger", "health",
    "moral_injury", "identity_shift", "event_trauma", "trust_scar",
]

# (a) mild counterfactual perturbations (±1-3 on a single feature around
#     the "default" state). These mimic "decision boundary" samples.
MILD_PERTURBATIONS: list[dict[str, float]] = []
for feat in ["fear", "hope", "grief", "confusion", "love"]:
    for delta in [-3, -1.5, 1.5, 3]:
        MILD_PERTURBATIONS.append({feat: delta})

# (b) stress extremes — push a constant/under-varied feature to bounds.
#     These directly break the 5-feature-constant-constraint from diag 1.
STRESS_EXTREMES: list[dict[str, float]] = [
    {"fear": 9.5, "fatigue": 8.0},
    {"fear": 9.5, "moral_injury": 7.0},
    {"fear": 9.5, "event_trauma": 6.0},
    {"hope": 9.8, "love": 9.0, "fear": 2.0},
    {"grief": 7.5, "moral_injury": 6.0},
    {"confusion": 8.0, "trust_scar": 4.0},
    {"fatigue": 9.0, "hunger": 6.0, "health": 3.0},
    {"identity_shift": -5.0, "moral_injury": 6.0},
    {"identity_shift": 5.0, "hope": 9.5},
    {"event_trauma": 8.0, "fear": 8.0, "moral_injury": 5.0},
    # Edge combos that never appear in canonical runs.
    {"fear": 0.5, "hope": 3.0, "confusion": 8.0},   # doubt at rest
    {"fear": 8.0, "hope": 2.0, "grief": 6.0},       # despair
    {"love": 9.5, "fear": 8.0, "moral_injury": 4.0},  # costly loyalty
]


def _apply(base: dict[str, float], perturb: dict[str, float]) -> dict[str, float]:
    out = dict(base)
    for k, v in perturb.items():
        out[k] = float(max(0.0, min(10.0, out.get(k, 5.0) + v))) if abs(v) <= 3.5 \
            else float(max(-10.0 if k == "identity_shift" else 0.0,
                          min(10.0, v)))
    return out


def _rollout_from(peter_state_kwargs: dict[str, float], seed: int, rollout_tick: int):
    peter = make_peter_state(**peter_state_kwargs)
    result = run_peter(seed=seed, max_tick=rollout_tick, peter_override=peter)
    return extract_samples(result)


def harvest_mild(rollout_tick: int = 15, seed_base: int = 30_000) -> dict[str, Any]:
    """Mild perturbations ±1.5/±3 applied to the default Peter state."""
    rng = random.Random(0)
    X, acts, combos, ticks, seeds = [], [], [], [], []
    base = {"fear": 5.0, "hope": 8.5, "grief": 0.5, "confusion": 5.0, "love": 7.0}
    for i, p in enumerate(MILD_PERTURBATIONS):
        state_kwargs = _apply(base, p)
        seed = seed_base + i
        for s in _rollout_from(state_kwargs, seed, rollout_tick):
            if s.agent_id == "peter" and s.action is not None:
                X.append(state_to_feature_vector(s.state))
                acts.append(s.action)
                combos.append(p)
                ticks.append(s.tick)
                seeds.append(seed)
    # 2 extra random seeds per combo for noise
    for i, p in enumerate(MILD_PERTURBATIONS):
        state_kwargs = _apply(base, p)
        for j in range(2):
            seed = seed_base + 10_000 + i * 10 + j + rng.randint(0, 99)
            for s in _rollout_from(state_kwargs, seed, rollout_tick):
                if s.agent_id == "peter" and s.action is not None:
                    X.append(state_to_feature_vector(s.state))
                    acts.append(s.action)
                    combos.append(p)
                    ticks.append(s.tick)
                    seeds.append(seed)
    return {
        "source": "mild_perturbation",
        "X": np.asarray(X, dtype=np.float32) if X else np.zeros((0, 12), dtype=np.float32),
        "actions": acts, "combos": combos, "ticks": ticks, "seeds": seeds,
    }


def harvest_stress(rollout_tick: int = 20, seed_base: int = 40_000) -> dict[str, Any]:
    """Extreme initial states — forces constant features to move."""
    X, acts, combos, ticks, seeds = [], [], [], [], []
    # Run each stress combo over several seeds — the stress state is the
    # important part, but seed variety gives different trajectories.
    seeds_per_combo = 5
    for i, combo in enumerate(STRESS_EXTREMES):
        state_kwargs = dict(combo)
        # Fill in defaults for unspecified fields so the state is complete.
        for feat, default in [
            ("fear", 5.0), ("hope", 5.0), ("grief", 0.5), ("confusion", 5.0),
            ("love", 5.0), ("fatigue", 3.0), ("hunger", 2.0), ("health", 8.0),
            ("moral_injury", 0.0), ("identity_shift", 0.0),
            ("event_trauma", 0.0), ("trust_scar", 0.0),
        ]:
            state_kwargs.setdefault(feat, default)
        for j in range(seeds_per_combo):
            seed = seed_base + i * seeds_per_combo + j
            for s in _rollout_from(state_kwargs, seed, rollout_tick):
                if s.agent_id == "peter" and s.action is not None:
                    X.append(state_to_feature_vector(s.state))
                    acts.append(s.action)
                    combos.append(combo)
                    ticks.append(s.tick)
                    seeds.append(seed)
    return {
        "source": "stress_extreme",
        "X": np.asarray(X, dtype=np.float32) if X else np.zeros((0, 12), dtype=np.float32),
        "actions": acts, "combos": combos, "ticks": ticks, "seeds": seeds,
    }


def main() -> int:
    register_domain_types()
    out = ROOT / "data" / "person" / "pipeline_v1"

    print(f"[2B] Mild perturbations: {len(MILD_PERTURBATIONS)} combos × 3 seeds × 15 tick")
    mild = harvest_mild()
    print(f"     → {mild['X'].shape[0]} samples")
    (out / "mild").mkdir(parents=True, exist_ok=True)
    np.save(out / "mild" / "X.npy", mild["X"])
    (out / "mild" / "meta.json").write_text(
        json.dumps({
            "source": mild["source"], "actions": mild["actions"],
            "ticks": mild["ticks"], "seeds": mild["seeds"],
            "n_samples": int(mild["X"].shape[0]),
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[2D] Stress extremes: {len(STRESS_EXTREMES)} combos × 5 seeds × 20 tick")
    stress = harvest_stress()
    print(f"     → {stress['X'].shape[0]} samples")
    (out / "stress").mkdir(parents=True, exist_ok=True)
    np.save(out / "stress" / "X.npy", stress["X"])
    (out / "stress" / "meta.json").write_text(
        json.dumps({
            "source": stress["source"], "actions": stress["actions"],
            "ticks": stress["ticks"], "seeds": stress["seeds"],
            "n_samples": int(stress["X"].shape[0]),
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    from collections import Counter
    print(f"\n  mild distribution:   {dict(Counter(mild['actions']))}")
    print(f"  stress distribution: {dict(Counter(stress['actions']))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
