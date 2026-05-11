"""Test hypothesis D — Shame oscillation enables confession.

Per BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md §4 D:
- Triple-spread (t=5,40,100) -> RECOVERY (observed)
- Triple-clustered (t=5,7,10) -> SATURATION (predicted)

If predicted outcome holds, D supported.
If clustered triple also gives RECOVERY, D rejected.

This is a 1-probe test for falsification.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

from scripts.b_direction.generate_readability_probes import N_TICKS
from scripts.b_direction.run_scarcity_scene import (
    build_scarcity_cast, build_locations as sc_locs, build_network as sc_net,
)
from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorldConfig, MicroWorld

BASELINE_PLACEMENTS = {
    "agent_01": "granary", "agent_02": "poor_quarter",
    "agent_03": "marketplace", "agent_04": "poor_quarter",
    "agent_05": "marketplace", "agent_06": "granary",
    "agent_07": "granary", "agent_08": "marketplace",
    "agent_09": "marketplace", "agent_10": "poor_quarter",
    "agent_11": "poor_quarter", "agent_12": "granary",
}


def run_variant(timing_label, accusation_ticks):
    agents = build_scarcity_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": t, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"}
        for t in accusation_ticks
    ]
    seed_events.append({"tick": 15, "event_id": "guard_approaches", "location": "marketplace"})
    w = MicroWorld(MicroWorldConfig(
        agents=agents, locations=sc_locs(),
        initial_placements=BASELINE_PLACEMENTS,
        crowd_instances={
            "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
            "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
        },
        social_network=sc_net(aids),
        seed_events=seed_events,
        seed_rumors=[{
            "content_tag": "misdeed", "target_role": "merchant",
            "origin_source": "agent_09",
            "initial_reach": ["agent_09", "agent_10"],
            "intensity": 0.7, "credibility": 0.6,
        }],
        seed=0,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))
    aids = list(w._agents.keys())
    cohort_groups = defaultdict(list)
    for aid in aids:
        cohort_groups[w._spatial.where(aid)].append(aid)
    per_shame = defaultdict(list)
    confessions = 0
    forgiveness = 0
    for tick in range(N_TICKS):
        result = w.step()
        for aid, a in w._agents.items():
            per_shame[aid].append(a.state.get("shame", {}).get("public_group", 0.0))
        for aid, action in result.agent_actions.items():
            if action == "confess":
                confessions += 1
        for ev in result.spawned_events:
            if ev.get("event_id") == "forgiveness_emitted":
                forgiveness += 1

    cohort_arcs = []
    for loc, members in cohort_groups.items():
        peaks = [max(per_shame[a]) for a in members if per_shame[a]]
        finals = [per_shame[a][-1] for a in members if per_shame[a]]
        if not peaks:
            continue
        peak = max(peaks)
        final_mean = sum(finals) / len(finals)
        if peak < 1.5:
            arc = "no_shame"
        elif final_mean < 4 and peak >= 5:
            arc = "recovery"
        elif final_mean >= 7:
            arc = "saturation"
        else:
            arc = "partial"
        cohort_arcs.append(arc)
    arcs = set(cohort_arcs)
    if arcs <= {"no_shame"}:
        outcome = "LOW_ACTIVITY"
    elif "recovery" in arcs and "saturation" in arcs:
        outcome = "MIXED"
    elif "saturation" in arcs and "recovery" not in arcs:
        outcome = "SATURATION_DOMINATED"
    elif "recovery" in arcs and "saturation" not in arcs:
        outcome = "RECOVERY_DOMINATED"
    else:
        outcome = "PARTIAL"

    final_mean_overall = sum(per_shame[a][-1] for a in per_shame) / len(per_shame)
    return {
        "label": timing_label,
        "ticks": accusation_ticks,
        "n_conf": confessions,
        "n_forg": forgiveness,
        "outcome": outcome,
        "final_mean": final_mean_overall,
    }


def main():
    print("Hypothesis D test: shame oscillation enables confession\n")
    variants = [
        ("triple-spread (t5,40,100)", [5, 40, 100]),
        ("triple-clustered (t5,7,10)", [5, 7, 10]),
        ("triple-very-clustered (t5,6,7)", [5, 6, 7]),
        ("triple-late-spread (t100,140,180)", [100, 140, 180]),
    ]

    results = []
    for label, ticks in variants:
        r = run_variant(label, ticks)
        results.append(r)
        print(f"  {label:<35}: outcome={r['outcome']}, conf={r['n_conf']}, forg={r['n_forg']}, final_mean={r['final_mean']:.2f}")

    spread = next(r for r in results if "spread" in r["label"] and "late" not in r["label"])
    clustered = next(r for r in results if "very-clustered" in r["label"])

    print()
    print("=" * 60)
    print("Hypothesis D verdict:")
    if spread["outcome"] == "RECOVERY_DOMINATED" and clustered["outcome"] == "SATURATION_DOMINATED":
        print("  SUPPORTED: spread->RECOVERY, clustered->SATURATION (as predicted)")
    elif spread["outcome"] == clustered["outcome"]:
        print(f"  REJECTED: both spread and clustered give {clustered['outcome']}")
        print("  -> spacing does NOT drive nonmonotonicity")
    else:
        print(f"  PARTIAL: spread={spread['outcome']}, clustered={clustered['outcome']}")
        print("  -> spacing matters, but not in the predicted direction")


if __name__ == "__main__":
    main()
