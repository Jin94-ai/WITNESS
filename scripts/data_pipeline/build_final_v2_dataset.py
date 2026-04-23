"""Phase C + F integration build -- baseline ≤ 50% + forced (data-driven) ≥ 50%
+ 15-dim extended features + dual storage (balanced_for_training / raw_natural).

Spec §4 verbatim (baseline 비율 제한):
> baseline: ≤ 50%
> forced sampling (Phase A): ≥ 50%

Spec §4.4 verbatim (Dual dataset):
> data/person/pipeline_v2/
>   balanced_for_training/    ← baseline ≤ 50%, 학습에 사용
>   raw_natural/              ← 원본 분포 보존, calibration용

Spec §3.3.3 verbatim (in_dim change):
> 기존: BehaviorCloningMLP(in_dim=12, n_actions=5)
> 신규: BehaviorCloningMLP(in_dim=15, n_actions=15) (또는 현재 15 action 유지)

This module:
1. Harvests natural baseline (raw_natural/) via baseline_harvest (already built)
2. Uses data-driven zones (zones.json) + forced sampling to fill rare actions
3. Builds event context for every sample (15-dim)
4. Produces balanced_for_training/ with baseline ≤ 50% cap
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.core.event import ActionOption  # noqa: E402
from engine.io.loader import load_events  # noqa: E402
from engine.simulation.decision import decide_action  # noqa: E402
from engine.simulation.training_samples import extract_samples  # noqa: E402
from scripts.data_pipeline._common import (  # noqa: E402
    CONTENT,
    make_peter_state,
    register_domain_types,
    run_peter,
    run_peter_with_policy,
)
from scripts.data_pipeline.data_driven_zones import load_zones
from scripts.data_pipeline.extended_features import (  # noqa: E402
    extract_event_context_per_tick,
    serialize_vocab,
    state_to_extended_feature_vector,
)
from scripts.data_pipeline.forced_sampling import ForcingPolicy  # noqa: E402

PIPELINE = ROOT / "data" / "person" / "pipeline_v2"


# ---------------------------------------------------------------------
# raw_natural harvest with 15-dim features
# ---------------------------------------------------------------------

def harvest_raw_natural(
    n_seeds: int = 100, max_tick: int = 300,
) -> dict:
    print(f"[raw_natural] {n_seeds} seeds x {max_tick} tick ...")
    register_domain_types()
    X_rows, acts = [], []

    for seed in range(n_seeds):
        result = run_peter(seed=seed, max_tick=max_tick)
        ctx_by_tick = extract_event_context_per_tick(result)
        samples = extract_samples(result)
        for s in samples:
            if s.agent_id != "peter" or s.action is None:
                continue
            ctx = ctx_by_tick.get(s.tick, {})
            ext = state_to_extended_feature_vector(
                s.state,
                recent_event_id=ctx.get("recent_event_id"),
                time_since_event=float(ctx.get("time_since_event", 0)),
                hazard_proximity=float(ctx.get("hazard_proximity", max_tick)),
                max_tick_norm=float(max_tick),
            )
            X_rows.append(ext)
            acts.append(s.action)

    X = np.asarray(X_rows, dtype=np.float32)
    print(f"  natural samples: {X.shape[0]}")
    print(f"  distribution: {dict(Counter(acts))}")
    return {"X": X, "actions": acts, "source": "raw_natural"}


# ---------------------------------------------------------------------
# forced harvest using data-driven zones (voluntary + event)
# ---------------------------------------------------------------------

def _build_event_options_map() -> dict[str, list[ActionOption]]:
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    by_action: dict[str, list[ActionOption]] = {}
    for e in events:
        opts = list(e.action_options or [])
        if not opts:
            continue
        for o in opts:
            if o.action_id not in by_action:
                by_action[o.action_id] = opts
    return by_action


def _sample_from_zone(
    zone: dict[str, tuple[float, float]], rng: np.random.Generator,
):
    kwargs = {}
    for field, (lo, hi) in zone.items():
        if hi <= lo:
            kwargs[field] = (lo + hi) / 2
        else:
            kwargs[field] = float(rng.uniform(lo, hi))
    # Fill defaults
    defaults = {
        "fear": 5.0, "hope": 5.0, "grief": 1.0, "confusion": 5.0, "love": 5.0,
        "fatigue": float(rng.uniform(2, 7)), "hunger": float(rng.uniform(1, 6)),
        "health": float(rng.uniform(5, 9)),
        "moral_injury": float(rng.uniform(0, 5)),
        "identity_shift": float(rng.uniform(-5, 5)),
        "event_trauma": float(rng.uniform(0, 5)),
        "trust_scar": float(rng.uniform(0, 3)),
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)
    return make_peter_state(**kwargs)


def harvest_forced_data_driven(
    zones_path: str | Path,
    *, target_per_action: int = 300, seed_base: int = 80_000,
    max_tick_norm: float = 200.0,
) -> dict:
    register_domain_types()
    zones = load_zones(zones_path)
    event_opts = _build_event_options_map()

    rng = np.random.default_rng(0)
    X_rows, acts = [], []
    per_action_saved: dict[str, int] = {}

    for action_id, zone in zones.items():
        # Voluntary or event?
        is_event = action_id in event_opts

        saved = 0
        for attempt in range(target_per_action * 3):
            if saved >= target_per_action:
                break
            state = _sample_from_zone(zone, rng)
            # No event context for forced -- set to 'voluntary' placeholder
            # (feature will encode as one of the known vocab indices)
            ext = state_to_extended_feature_vector(
                state,
                recent_event_id="voluntary" if not is_event else action_id,
                time_since_event=0.0,
                hazard_proximity=max_tick_norm,
                max_tick_norm=max_tick_norm,
            )
            if is_event:
                # Use decide_action with event options list
                options = event_opts[action_id]
                policy = ForcingPolicy(action_id)
                try:
                    chosen = decide_action(
                        state, options,
                        random.Random(seed_base + attempt),
                        policy=policy,
                    )
                except Exception:
                    continue
                if chosen is None or chosen.action_id != action_id:
                    continue
                X_rows.append(ext)
                acts.append(action_id)
                saved += 1
            else:
                # Voluntary: run 1-tick simulation with forced policy
                try:
                    result = run_peter_with_policy(
                        seed=seed_base + attempt, max_tick=1,
                        peter_override=state,
                        policies={"peter": ForcingPolicy(action_id)},
                    )
                except Exception:
                    continue
                ar = result.action_histories.get("peter", [])
                if not ar or ar[0].chosen_action != action_id:
                    continue
                X_rows.append(ext)
                acts.append(action_id)
                saved += 1

        per_action_saved[action_id] = saved
        print(f"  [forced-dd] {action_id:<22} saved={saved}/{target_per_action}")

    X = np.asarray(X_rows, dtype=np.float32) if X_rows else np.zeros((0, 15), dtype=np.float32)
    return {"X": X, "actions": acts, "source": "forced_data_driven",
            "per_action_saved": per_action_saved}


# ---------------------------------------------------------------------
# Merge with baseline ≤ 50% cap + stratified per-class balance
# ---------------------------------------------------------------------

def build_balanced_for_training(
    natural: dict, forced: dict,
    *, baseline_cap_ratio: float = 0.5,
    target_per_class: int = 600,
    seed: int = 0,
) -> dict:
    rng = np.random.default_rng(seed)

    # Per-class indices in each source
    def _per_class(source):
        pc: dict[str, list[int]] = defaultdict(list)
        for i, a in enumerate(source["actions"]):
            pc[a].append(i)
        return pc

    nat_pc = _per_class(natural)
    forced_pc = _per_class(forced)

    all_actions = sorted(set(nat_pc) | set(forced_pc))
    X_rows = []
    acts = []
    sources = []

    for action in all_actions:
        nat_idx = nat_pc.get(action, [])
        forced_idx = forced_pc.get(action, [])

        # target: baseline_cap_ratio * target_per_class
        baseline_take = int(target_per_class * baseline_cap_ratio)
        forced_take = target_per_class - baseline_take

        # Sample from natural (limited by availability)
        n_from_nat = min(len(nat_idx), baseline_take)
        if n_from_nat > 0:
            chosen_nat = rng.choice(nat_idx, size=n_from_nat, replace=False).tolist()
            for i in chosen_nat:
                X_rows.append(natural["X"][i])
                acts.append(action)
                sources.append("natural")

        # Remainder from forced
        remaining = target_per_class - n_from_nat
        n_from_forced = min(len(forced_idx), remaining)
        if n_from_forced > 0:
            chosen_forced = rng.choice(forced_idx, size=n_from_forced, replace=False).tolist()
            for i in chosen_forced:
                X_rows.append(forced["X"][i])
                acts.append(action)
                sources.append("forced")

    X = np.asarray(X_rows, dtype=np.float32)
    return {
        "X": X, "actions": acts, "sources": sources,
        "n_natural": sum(1 for s in sources if s == "natural"),
        "n_forced": sum(1 for s in sources if s == "forced"),
    }


# ---------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------

def main() -> int:
    PIPELINE.mkdir(parents=True, exist_ok=True)

    # 1. Harvest natural (15-dim features)
    natural = harvest_raw_natural(n_seeds=100, max_tick=300)
    (PIPELINE / "raw_natural").mkdir(parents=True, exist_ok=True)
    np.savez(PIPELINE / "raw_natural" / "dataset.npz",
             X=natural["X"],
             y_actions=np.asarray(natural["actions"], dtype=object))
    (PIPELINE / "raw_natural" / "meta.json").write_text(
        json.dumps({
            "source": "raw_natural",
            "n_samples": int(natural["X"].shape[0]),
            "distribution": dict(Counter(natural["actions"])),
            "feature_dim": 15,
        }, ensure_ascii=False), encoding="utf-8")

    # 2. Forced sampling with data-driven zones
    zones_path = PIPELINE / "zones.json"
    forced = harvest_forced_data_driven(zones_path, target_per_action=300)
    (PIPELINE / "forced_data_driven").mkdir(parents=True, exist_ok=True)
    np.savez(PIPELINE / "forced_data_driven" / "dataset.npz",
             X=forced["X"],
             y_actions=np.asarray(forced["actions"], dtype=object))
    (PIPELINE / "forced_data_driven" / "meta.json").write_text(
        json.dumps({
            "source": "forced_data_driven",
            "n_samples": int(forced["X"].shape[0]),
            "distribution": dict(Counter(forced["actions"])),
            "per_action_saved": forced["per_action_saved"],
            "feature_dim": 15,
        }, ensure_ascii=False), encoding="utf-8")

    # 3. Balanced for training (baseline ≤ 50%)
    balanced = build_balanced_for_training(
        natural, forced,
        baseline_cap_ratio=0.5, target_per_class=600,
    )
    vocab = sorted(set(balanced["actions"]))
    y = np.asarray([vocab.index(a) for a in balanced["actions"]], dtype=np.int64)

    (PIPELINE / "balanced_for_training").mkdir(parents=True, exist_ok=True)
    np.savez(PIPELINE / "balanced_for_training" / "dataset.npz",
             X=balanced["X"], y=y)
    (PIPELINE / "balanced_for_training" / "meta.json").write_text(
        json.dumps({
            "source": "balanced_for_training",
            "action_vocab": vocab,
            "n_samples": int(balanced["X"].shape[0]),
            "n_natural": balanced["n_natural"],
            "n_forced": balanced["n_forced"],
            "natural_ratio": balanced["n_natural"] / max(1, balanced["X"].shape[0]),
            "distribution": dict(Counter(balanced["actions"])),
            "baseline_cap_ratio": 0.5,
            "target_per_class": 600,
            "feature_dim": 15,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. Event vocab persist
    serialize_vocab(PIPELINE / "event_vocab.json")

    print(f"\n[balanced] X={balanced['X'].shape}, classes={len(vocab)}")
    print(f"  natural={balanced['n_natural']}  forced={balanced['n_forced']}")
    print(f"  natural_ratio={balanced['n_natural'] / max(1, balanced['X'].shape[0]):.3f}")
    print(f"  distribution: {dict(Counter(balanced['actions']))}")
    print(f"\n  saved: {PIPELINE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
