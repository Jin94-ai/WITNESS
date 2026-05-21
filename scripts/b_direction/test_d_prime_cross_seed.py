"""Cross-seed re-test of D' generalization (HARNESS H1 followup).

⚠️ STATUS: **abandoned / Branch C era** (cycle 57 audit, 2026-05-11).

This script references `run_accusation_variant_with_seed` and `run_sacred_variant_with_seed`
functions that were planned but never implemented (see TODO comment in main() around line 95).
Running this script fails with NameError. Branch C work was archived after Phase 2 transition;
this file remains as a historical record of the planned cross-seed D' re-test that was
absorbed into the broader Phase 3.05 review §H8 5+ seed ensemble discipline.

If revival needed: implement the two `_with_seed` variants (extending the seed=0-hardcoded
existing variants), or re-run the analysis via current Phase 3.05 Rubric ensemble tools
(see `scripts/rubric/build_ensemble_html.py` + `docs/portfolio/demo_rubric/`).

ORIGINAL DESCRIPTION:
Per LOOP 73 seed-robustness finding: all S2 + D' findings used seed=0 only.
Test if D' rejection (scenario-specific dynamics) holds across seeds 0-4.

For each (scenario, spacing) combination, run 5 seeds. Report majority outcome.

If D' rejection holds: scenario-specific dynamics confirmed across seeds.
If D' rejection collapses: nonmonotonicity/scenario-specificity is seed-artifact.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

from scripts.b_direction.test_d_prime_generalization import (
    SPACING_VARIANTS,
    measure,
)


def run_scarcity_variant(spacing_label, seed):
    ticks = SPACING_VARIANTS[spacing_label]
    if len(ticks) == 1:
        ec = "single"
    elif len(ticks) == 2:
        ec = "double"
    else:
        ec = "triple"
    # build_scarcity_depth_world uses fixed event_count -> need custom build for spacing variants
    # Reuse hypothesis D test logic (build directly with custom ticks)
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_scarcity_scene import (
        build_locations as sc_locs,
    )
    from scripts.b_direction.run_scarcity_scene import (
        build_network as sc_net,
    )
    from scripts.b_direction.run_scarcity_scene import (
        build_scarcity_cast,
    )
    agents = build_scarcity_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": t, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"}
        for t in ticks
    ]
    seed_events.append({"tick": 15, "event_id": "guard_approaches", "location": "marketplace"})
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sc_locs(),
        initial_placements={
            "agent_01": "granary", "agent_02": "poor_quarter",
            "agent_03": "marketplace", "agent_04": "poor_quarter",
            "agent_05": "marketplace", "agent_06": "granary",
            "agent_07": "granary", "agent_08": "marketplace",
            "agent_09": "marketplace", "agent_10": "poor_quarter",
            "agent_11": "poor_quarter", "agent_12": "granary",
        },
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
        seed=seed,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def main():
    print("Cross-seed D' re-test (HARNESS H1 followup)\n")
    print("Each (scenario, spacing) = 5 seeds (0-4)\n")

    SCENARIOS = {
        "scarcity": run_scarcity_variant,
        "accusation": lambda s, seed: run_accusation_variant_with_seed(s, seed),
        "sacred":     lambda s, seed: run_sacred_variant_with_seed(s, seed),
    }

    # Need run_*_variant_with_seed - existing functions hardcode seed=0
    # Inline override
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
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

    def acc_seeded(spacing_label, seed):
        ticks = SPACING_VARIANTS[spacing_label]
        agents = build_accusation_cast()
        aids = [a.agent_id for a in agents]
        events = [
            {"tick": t, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"}
            for t in ticks
        ]
        events.append({"tick": 12, "event_id": "guard_approaches", "location": "upper_room"})
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
            seed_events=events,
            seed_rumors=[{
                "content_tag": "threat_to_authority",
                "target_role": "disciple_follower",
                "origin_source": "agent_04",
                "initial_reach": ["agent_04", "agent_05"],
                "intensity": 0.6, "credibility": 0.5,
            }],
            seed=seed, forgiveness_phase_enabled=True, forgiveness_agent_shame_multiplier=None,
        ))

    def sac_seeded(spacing_label, seed):
        ticks = SPACING_VARIANTS[spacing_label]
        agents = sacred_cast()
        aids = [a.agent_id for a in agents]
        events = [{"tick": 5, "event_id": "prayer_invitation",
                   "location": "temple_outer_court"}]
        for t in ticks:
            events.append({"tick": t, "event_id": "miracle_witnessed",
                           "location": "temple_outer_court"})
        events.append({"tick": 50, "event_id": "public_accusation",
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
            seed_events=events,
            seed_rumors=[{
                "content_tag": "miracle_news",
                "target_role": "spiritual_wanderer",
                "origin_source": "agent_01",
                "initial_reach": ["agent_01", "agent_02"],
                "intensity": 0.6, "credibility": 0.7,
            }],
            seed=seed, forgiveness_phase_enabled=True, forgiveness_agent_shame_multiplier=None,
        ))

    runners = {"scarcity": run_scarcity_variant, "accusation": acc_seeded, "sacred": sac_seeded}
    spacings = ["spread", "mild-cluster", "very-cluster", "late-spread"]

    results = defaultdict(list)
    for scenario, runner in runners.items():
        for spacing in spacings:
            outcomes_per_seed = []
            for seed in range(5):
                w = runner(spacing, seed)
                outcome, _, _, _ = measure(w)
                outcomes_per_seed.append(outcome)
            results[(scenario, spacing)] = outcomes_per_seed

    # Print per-(scenario, spacing) table
    print(f"{'Scenario':<11} {'Spacing':<14} {'s0':<22} {'s1':<22} {'s2':<22} {'s3':<22} {'s4':<22}")
    for (scen, sp), outs in results.items():
        line = f"{scen:<11} {sp:<14} " + " ".join(f"{o:<22}" for o in outs)
        print(line)

    print()
    print("Modal outcome per (scenario, spacing):")
    print(f"{'Scenario':<11} {'Spacing':<14} Modal (count/5)")
    for (scen, sp), outs in results.items():
        mode = Counter(outs).most_common(1)[0]
        print(f"  {scen:<11} {sp:<14} {mode[0]} ({mode[1]}/5)")

    # Verdict: D' rejection robustness
    print()
    print("=" * 60)
    print("D' rejection robustness (cross-seed):")
    # Compare modal outcome scarcity vs accusation vs sacred at each spacing
    for sp in spacings:
        scar_mode = Counter(results[("scarcity", sp)]).most_common(1)[0][0]
        acc_mode = Counter(results[("accusation", sp)]).most_common(1)[0][0]
        sac_mode = Counter(results[("sacred", sp)]).most_common(1)[0][0]
        match_acc = scar_mode == acc_mode
        match_sac = scar_mode == sac_mode
        print(f"  {sp:<14}: scarcity={scar_mode}, accusation={'(match)' if match_acc else acc_mode}, sacred={'(match)' if match_sac else sac_mode}")

    # Within-scenario seed variance
    print()
    print("Within-scenario seed variance (how often do all 5 seeds agree?):")
    for (scen, sp), outs in results.items():
        if len(set(outs)) == 1:
            agreement = "5/5 unanimous"
        else:
            mode_count = Counter(outs).most_common(1)[0][1]
            agreement = f"{mode_count}/5 modal"
        print(f"  {scen:<11} {sp:<14}: {agreement}")


if __name__ == "__main__":
    main()
