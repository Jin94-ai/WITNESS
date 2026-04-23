"""Phase 2C — rare-action parameter sweep.

Spec §3.4: systematically visit state regions where rare actions fire.

Diag 1 action means guide the target zones:
  withdraw_in_fear:  fear≈8.0, (fatigue/moral_injury constant in baseline so
                     we intentionally vary them here to inject signal into the
                     5 previously-constant features)
  assert_loyalty:    hope≈9.3 + love≈7.3
  pray:              fear≈5.8 + confusion≈5.2
  discuss:           love≈7.25 + confusion≈4.8
"""

from __future__ import annotations

import itertools
import json
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

# Diag 1 target zones. First axis is the dominant driver; the remaining axes
# deliberately move *constant* features (fatigue, moral_injury, etc.) so they
# contribute signal.
TARGET_ZONES: dict[str, dict[str, Any]] = {
    "withdraw_in_fear": {
        "fear": np.linspace(7.0, 10.0, 4),
        "fatigue": np.linspace(4.0, 9.0, 4),
        "moral_injury": np.linspace(3.0, 8.0, 3),
        "hope": np.linspace(3.0, 8.0, 3),
    },
    "assert_loyalty": {
        "hope": np.linspace(8.5, 10.0, 3),
        "love": np.linspace(7.0, 9.5, 3),
        "fear": np.linspace(2.0, 6.0, 3),
        "confusion": np.linspace(2.0, 5.0, 3),
        "identity_shift": np.linspace(-2.0, 2.0, 3),
    },
    "pray": {
        "fear": np.linspace(4.0, 7.5, 4),
        "confusion": np.linspace(4.0, 7.0, 3),
        "grief": np.linspace(0.5, 4.0, 3),
        "moral_injury": np.linspace(1.0, 5.0, 3),
    },
    "discuss_with_disciples": {
        "hope": np.linspace(7.0, 9.5, 3),
        "love": np.linspace(6.5, 9.0, 3),
        "confusion": np.linspace(3.0, 6.5, 3),
        "trust_scar": np.linspace(0.0, 3.0, 3),
    },
}


def sweep_zone(
    target_action: str, zone: dict[str, np.ndarray],
    *, rollout_tick: int = 10, seed_base: int = 10_000,
) -> dict[str, Any]:
    """Enumerate grid in ``zone``, run a short rollout from each combination."""
    axes = list(zone.keys())
    values = [zone[a].tolist() for a in axes]

    X: list[list[float]] = []
    actions: list[str] = []
    ticks: list[int] = []
    seeds: list[int] = []
    combos: list[dict[str, float]] = []

    for idx, combo in enumerate(itertools.product(*values)):
        overrides = dict(zip(axes, combo))
        peter = make_peter_state(**overrides)
        seed = seed_base + idx
        result = run_peter(seed=seed, max_tick=rollout_tick, peter_override=peter)
        samples = extract_samples(result)
        for s in samples:
            if s.agent_id == "peter" and s.action is not None:
                X.append(state_to_feature_vector(s.state))
                actions.append(s.action)
                ticks.append(s.tick)
                seeds.append(seed)
                combos.append(overrides)

    return {
        "target_action": target_action,
        "X": np.asarray(X, dtype=np.float32) if X else np.zeros((0, 12), dtype=np.float32),
        "actions": actions,
        "ticks": ticks,
        "seeds": seeds,
        "combos": combos,
    }


def main() -> int:
    register_domain_types()
    out = ROOT / "data" / "person" / "pipeline_v1" / "rare_sweep"
    out.mkdir(parents=True, exist_ok=True)

    rollout_tick = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    all_X: list[np.ndarray] = []
    all_actions: list[str] = []
    all_ticks: list[int] = []
    all_seeds: list[int] = []
    targets_by_sample: list[str] = []

    for target, zone in TARGET_ZONES.items():
        n_combos = int(np.prod([len(v) for v in zone.values()]))
        print(f"[2C] {target}: {n_combos} combos × {rollout_tick} tick rollout...")
        harvest = sweep_zone(target, zone, rollout_tick=rollout_tick)
        print(f"     → {harvest['X'].shape[0]} samples")
        all_X.append(harvest["X"])
        all_actions.extend(harvest["actions"])
        all_ticks.extend(harvest["ticks"])
        all_seeds.extend(harvest["seeds"])
        targets_by_sample.extend([target] * len(harvest["actions"]))

    X = np.concatenate(all_X, axis=0) if all_X else np.zeros((0, 12), dtype=np.float32)
    np.save(out / "X.npy", X)
    (out / "meta.json").write_text(
        json.dumps({
            "source": "rare_action_sweep",
            "actions": all_actions,
            "ticks": all_ticks,
            "seeds": all_seeds,
            "target_zones": targets_by_sample,
            "n_samples": int(X.shape[0]),
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    from collections import Counter
    print(f"\n  total samples: {X.shape[0]}")
    print(f"  distribution:  {dict(Counter(all_actions))}")
    print(f"  saved to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
