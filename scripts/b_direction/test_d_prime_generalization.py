"""Test D' (oscillation hypothesis) generalization across accusation + sacred.

Per BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md §4 D' refined hypothesis:
- spread (gap >=30) -> RECOVERY
- mild-cluster (gap 2-5) -> SATURATION
- very-cluster (gap 1, consecutive) -> PARTIAL
- late-spread (events 100+ ticks in) -> STRONGEST RECOVERY

Question: does this 3-regime spacing pattern generalize across scenarios?

Test plan: run 4 spacing variants in accusation + sacred (8 probes total).
Compare to scarcity baseline (LOOP 70 results).

If accusation + sacred match scarcity: D' is mechanism-level, scenario-invariant.
If they diverge: nonmonotonicity is scarcity-specific.
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

from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorld, MicroWorldConfig
from scripts.b_direction.generate_readability_probes import N_TICKS
from scripts.b_direction.run_accusation_scene import (
    build_accusation_cast,
)
from scripts.b_direction.run_accusation_scene import (
    build_locations as acc_locs,
)
from scripts.b_direction.run_accusation_scene import (
    build_social_network as acc_net,
)
from scripts.b_direction.run_sacred_gathering import (
    build_cast as sacred_cast,
)
from scripts.b_direction.run_sacred_gathering import (
    build_locations as sa_locs,
)
from scripts.b_direction.run_sacred_gathering import (
    build_network as sa_net,
)

SPACING_VARIANTS = {
    "spread":         [5, 40, 100],
    "mild-cluster":   [5, 7, 10],
    "very-cluster":   [5, 6, 7],
    "late-spread":    [100, 140, 180],
}


def run_accusation_variant(spacing_label):
    ticks = SPACING_VARIANTS[spacing_label]
    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": t, "event_id": "public_accusation",
         "target_role": "disciple_follower", "location": "priest_courtyard"}
        for t in ticks
    ]
    seed_events.append({"tick": 12, "event_id": "guard_approaches", "location": "upper_room"})
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=acc_locs(),
        initial_placements={
            "agent_01": "upper_room", "agent_02": "upper_room",
            "agent_03": "upper_room", "agent_04": "priest_courtyard",
            "agent_05": "priest_courtyard", "agent_06": "city_street",
            "agent_07": "city_street", "agent_08": "city_street",
            "agent_09": "upper_room", "agent_10": "city_street",
        },
        crowd_instances={
            "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
            "city_street": CrowdState(crowd_id="city_street", density=0.6),
        },
        social_network=acc_net(aids),
        seed_events=seed_events,
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=0,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def run_sacred_variant(spacing_label):
    """Sacred uses miracle_witnessed instead of public_accusation, with 1 baseline accusation."""
    ticks = SPACING_VARIANTS[spacing_label]
    agents = sacred_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [{"tick": 5, "event_id": "prayer_invitation",
                    "location": "temple_outer_court"}]
    for t in ticks:
        seed_events.append({"tick": t, "event_id": "miracle_witnessed",
                            "location": "temple_outer_court"})
    seed_events.append({"tick": 50, "event_id": "public_accusation",
                        "target_role": "spiritual_wanderer", "location": "city_street"})
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sa_locs(),
        initial_placements={
            "agent_01": "temple_outer_court", "agent_02": "temple_inner",
            "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
            "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
            "agent_07": "city_street", "agent_08": "city_street",
        },
        crowd_instances={
            "temple_outer_court": CrowdState(crowd_id="temple_outer_court",
                                              density=0.6, dominant_emotion="awe"),
            "city_street": CrowdState(crowd_id="city_street", density=0.3),
        },
        social_network=sa_net(aids),
        seed_events=seed_events,
        seed_rumors=[{
            "content_tag": "miracle_news",
            "target_role": "spiritual_wanderer",
            "origin_source": "agent_01",
            "initial_reach": ["agent_01", "agent_02"],
            "intensity": 0.6, "credibility": 0.7,
        }],
        seed=0,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def measure(world):
    aids = list(world._agents.keys())
    cohort_groups = defaultdict(list)
    for aid in aids:
        cohort_groups[world._spatial.where(aid)].append(aid)
    per_shame = defaultdict(list)
    confessions = 0
    forgiveness = 0
    for tick in range(N_TICKS):
        result = world.step()
        for aid, a in world._agents.items():
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
    return outcome, confessions, forgiveness, final_mean_overall


def main():
    print("D' generalization test: scarcity vs accusation vs sacred\n")
    print("Scarcity reference (from LOOP 70):")
    print("  spread:       RECOVERY (115 conf, 81 forg, final 1.37)")
    print("  mild-cluster: SATURATION (63 conf, 39 forg, final 3.58)")
    print("  very-cluster: PARTIAL (106 conf, 74 forg, final 1.84)")
    print("  late-spread:  RECOVERY (215 conf, 156 forg, final 0.97)")
    print()

    rows = []
    for scenario, runner in [("accusation", run_accusation_variant),
                              ("sacred", run_sacred_variant)]:
        print(f"  === {scenario} ===")
        for spacing in ["spread", "mild-cluster", "very-cluster", "late-spread"]:
            w = runner(spacing)
            outcome, conf, forg, final = measure(w)
            rows.append({
                "scenario": scenario,
                "spacing": spacing,
                "outcome": outcome,
                "conf": conf,
                "forg": forg,
                "final": final,
            })
            print(f"  {spacing:<14}: {outcome:<22} conf={conf}, forg={forg}, final={final:.2f}")
        print()

    # Verdict
    print("=" * 60)
    print("D' generalization verdict:")
    scarcity_ref = {
        "spread": "RECOVERY_DOMINATED",
        "mild-cluster": "SATURATION_DOMINATED",
        "very-cluster": "PARTIAL",
        "late-spread": "RECOVERY_DOMINATED",
    }
    matches = {"accusation": 0, "sacred": 0}
    for r in rows:
        if r["outcome"] == scarcity_ref[r["spacing"]]:
            matches[r["scenario"]] += 1
    for scen in ["accusation", "sacred"]:
        m = matches[scen]
        if m == 4:
            verdict = "FULL match - D' generalizes"
        elif m >= 2:
            verdict = "PARTIAL match - D' partially generalizes"
        else:
            verdict = "MISMATCH - nonmonotonicity is scenario-specific"
        print(f"  {scen}: {m}/4 outcomes match scarcity ({verdict})")


if __name__ == "__main__":
    main()
