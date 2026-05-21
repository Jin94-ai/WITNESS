"""Iter 113: Sacred ablation - is t=250 late miracle causal for recovery?

Iter 112 finding: sacred standalone has 60% recovery rate at N=15.
The scenario has 4 events: prayer t=5, miracle t=10, accusation t=18,
miracle t=250.

Hypothesis test:
  V0: full sacred (4 events, baseline)
  V1: ablate late miracle (3 events, no t=250)
  V2: ablate early miracle (3 events, no t=10)
  V3: ablate accusation (3 events, no t=18)

If V1 recovery rate << V0 -> late miracle is critical
If V2 << V0 -> early miracle is critical
If V3 == V0 or higher -> accusation event is suppressing recovery
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

N_SEEDS = 15
N_TICKS = 500


def build_sacred(seed, *, include_late_miracle=True,
                 include_early_miracle=True, include_accusation=True):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_sacred_gathering import (
        build_cast,
        build_locations,
        build_network,
    )

    agents = build_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": 5, "event_id": "prayer_invitation",
         "location": "temple_outer_court"},
    ]
    if include_early_miracle:
        seed_events.append(
            {"tick": 10, "event_id": "miracle_witnessed",
             "location": "temple_outer_court"})
    if include_accusation:
        seed_events.append(
            {"tick": 18, "event_id": "public_accusation",
             "target_role": "spiritual_wanderer",
             "location": "temple_outer_court"})
    if include_late_miracle:
        seed_events.append(
            {"tick": 250, "event_id": "miracle_witnessed",
             "location": "temple_outer_court"})

    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements={
            "agent_01": "temple_outer_court", "agent_02": "temple_inner",
            "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
            "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
            "agent_07": "city_street", "agent_08": "city_street",
        },
        crowd_instances={
            "temple_outer_court": CrowdState(
                crowd_id="temple_outer_court", density=0.6,
                dominant_emotion="awe",
            ),
            "city_street": CrowdState(crowd_id="city_street", density=0.3),
        },
        social_network=build_network(aids),
        seed_events=seed_events,
        seed_rumors=[],
        seed=seed,
    ))


def run_variant(label, **kwargs):
    finals = []
    for seed in range(N_SEEDS):
        w = build_sacred(seed, **kwargs)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        ag_finals = []
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                ag_finals.append(ts[-1])
        finals.append(mean(ag_finals) if ag_finals else 0.0)
    rec_count = sum(1 for f in finals if f < 4.0)
    return {
        "label": label,
        "finals": [round(f, 2) for f in finals],
        "mean": round(mean(finals), 3),
        "stdev": round(stdev(finals) if len(finals) > 1 else 0, 3),
        "recovery_rate": f"{rec_count}/{N_SEEDS}",
        "recovery_pct": round(100 * rec_count / N_SEEDS, 1),
    }


def main() -> int:
    print("[Iter 113] Sacred ablation -- causal test")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    variants = [
        ("V0_full", {}),
        ("V1_no_late_miracle", {"include_late_miracle": False}),
        ("V2_no_early_miracle", {"include_early_miracle": False}),
        ("V3_no_accusation", {"include_accusation": False}),
    ]
    results = {}
    for name, kwargs in variants:
        print(f"  Running {name}...")
        r = run_variant(name, **kwargs)
        results[name] = r
        print(f"    final mean={r['mean']} stdev={r['stdev']}  "
              f"recovery={r['recovery_rate']} ({r['recovery_pct']}%)")
        print(f"    finals: {r['finals']}")

    print()
    print("=== Recovery rate comparison ===")
    print(f"  {'variant':<24} {'final mean':<12} {'stdev':<8} {'recovery'}")
    for name, _ in variants:
        r = results[name]
        print(f"  {name:<24} {r['mean']:<12} {r['stdev']:<8} {r['recovery_rate']}")

    print()
    print("=== Causal test deltas vs V0 ===")
    v0 = results["V0_full"]
    for name, _ in variants[1:]:
        r = results[name]
        d_rec = r["recovery_pct"] - v0["recovery_pct"]
        d_mean = r["mean"] - v0["mean"]
        print(f"  {name}: Δrecovery_pct={d_rec:+.1f}%  Δmean={d_mean:+.2f}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "sacred_ablation_iter113.json"
    )
    out_path.write_text(
        json.dumps({"n_seeds": N_SEEDS, "n_ticks": N_TICKS, "results": results},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
