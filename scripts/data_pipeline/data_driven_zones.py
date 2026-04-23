"""Phase A re-design -- Data-driven boundary zones.

Evidence from DATA_PIPELINE_v2_V2_VS_V3_COMPARISON.md: my hand-designed
zones were systematically inverted vs engine's natural distribution
(e.g., `withdraw_in_fear` natural love=8.52 vs my zone love=2.04).

This module builds zones **from** observed natural trajectory:
    for each action:
        collect all (state, action=a) pairs from baseline harvest
        zone[a] = {feat: (mean - k*std, mean + k*std)} clipped to [0,10]

The resulting zone bounds **by construction** match where engine actually
produces this action. Subsequent forced sampling (Phase A core) then
draws states from this zone and forces the label.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.simulation.training_samples import (  # noqa: E402
    extract_samples,
    state_to_feature_vector,
)
from scripts.data_pipeline._common import (  # noqa: E402
    register_domain_types,
    run_peter,
)

FEATURE_NAMES = [
    "fear", "hope", "grief", "confusion", "love",
    "fatigue", "hunger", "health",
    "moral_injury", "identity_shift", "event_trauma", "trust_scar",
]
FEATURE_BOUNDS = {  # (lo, hi) per feature
    "identity_shift": (-10.0, 10.0),
    # all others [0, 10]
}


def collect_action_states(n_seeds: int = 30, max_tick: int = 200) -> dict[str, np.ndarray]:
    """Harvest natural trajectory, return {action_id: (n, 12) np.array}."""
    register_domain_types()
    by_action: dict[str, list[list[float]]] = defaultdict(list)

    for seed in range(n_seeds):
        result = run_peter(seed=seed, max_tick=max_tick)
        samples = extract_samples(result)
        for s in samples:
            if s.agent_id != "peter" or s.action is None:
                continue
            by_action[s.action].append(state_to_feature_vector(s.state))

    return {a: np.asarray(xs, dtype=np.float32) for a, xs in by_action.items()}


def derive_zones(
    action_states: dict[str, np.ndarray],
    *,
    k_std: float = 1.2,
    min_samples: int = 5,
) -> dict[str, dict[str, tuple[float, float]]]:
    """Per-action zone: mean ± k_std*std, clipped to feature bounds.

    Actions with < min_samples natural observations are skipped (caller can
    fall back to a hand-defined zone or exclude the action).
    """
    zones: dict[str, dict[str, tuple[float, float]]] = {}
    for action, states in action_states.items():
        if len(states) < min_samples:
            continue
        mean = states.mean(axis=0)
        std = states.std(axis=0)
        zone: dict[str, tuple[float, float]] = {}
        for i, feat in enumerate(FEATURE_NAMES):
            lo_bound, hi_bound = FEATURE_BOUNDS.get(feat, (0.0, 10.0))
            lo = float(max(lo_bound, mean[i] - k_std * std[i]))
            hi = float(min(hi_bound, mean[i] + k_std * std[i]))
            # Widen minimum range so we don't collapse to a point when std=0
            if hi - lo < 0.5:
                mid = (hi + lo) / 2
                lo = max(lo_bound, mid - 0.3)
                hi = min(hi_bound, mid + 0.3)
            zone[feat] = (lo, hi)
        zones[action] = zone
    return zones


def main() -> int:
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    out_json = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "person" / "pipeline_v2" / "zones.json"

    print(f"[data-driven zones] harvesting {n_seeds} seeds x 200 tick...")
    by_action = collect_action_states(n_seeds=n_seeds, max_tick=200)
    print(f"  natural samples collected: {sum(len(v) for v in by_action.values())}")
    print(f"  actions observed: {len(by_action)}")
    for a, xs in sorted(by_action.items(), key=lambda kv: -len(kv[1])):
        print(f"    {a:<24} n={len(xs)}")

    zones = derive_zones(by_action)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    # JSON can't serialize tuples as tuples; convert.
    serializable = {
        a: {f: [lo, hi] for f, (lo, hi) in z.items()}
        for a, z in zones.items()
    }
    out_json.write_text(
        json.dumps({
            "zones": serializable,
            "n_seeds": n_seeds,
            "k_std": 1.2,
            "feature_names": FEATURE_NAMES,
            "action_counts": {a: int(len(v)) for a, v in by_action.items()},
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  saved zones: {out_json}")
    return 0


def load_zones(path: Path | str) -> dict[str, dict[str, tuple[float, float]]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        a: {f: (float(lo), float(hi)) for f, (lo, hi) in z.items()}
        for a, z in data["zones"].items()
    }


if __name__ == "__main__":
    sys.exit(main())
