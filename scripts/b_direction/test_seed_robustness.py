"""Quick seed-robustness check for D / S2 finding.

Per HARNESS H4: 'all probes use seed=0' is a known limitation.
Test if scarcity triple→RECOVERY pattern holds across seeds 0-4.

If 5/5 seeds produce RECOVERY: finding is seed-robust.
If <3/5 produce RECOVERY: finding is seed-dependent, weakened.
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
from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world


def measure(world):
    aids = list(world._agents.keys())
    cohort_groups = defaultdict(list)
    for aid in aids:
        cohort_groups[world._spatial.where(aid)].append(aid)
    per_shame = defaultdict(list)
    for tick in range(N_TICKS):
        result = world.step()
        for aid, a in world._agents.items():
            per_shame[aid].append(a.state.get("shame", {}).get("public_group", 0.0))

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
        return "LOW_ACTIVITY"
    elif "recovery" in arcs and "saturation" in arcs:
        return "MIXED"
    elif "saturation" in arcs and "recovery" not in arcs:
        return "SATURATION_DOMINATED"
    elif "recovery" in arcs and "saturation" not in arcs:
        return "RECOVERY_DOMINATED"
    return "PARTIAL"


def main():
    print("Seed robustness test for S2 nonmonotonicity\n")
    print("Testing scarcity triple/baseline (seeds 0-4) - should be RECOVERY 5/5 if D supported\n")

    triple_outcomes = []
    single_outcomes = []
    double_outcomes = []
    for seed in range(5):
        for ec, dest in [("single", single_outcomes), ("double", double_outcomes), ("triple", triple_outcomes)]:
            w = build_scarcity_depth_world(seed=seed, event_count=ec, crowd_density="baseline")
            outcome = measure(w)
            dest.append(outcome)
            print(f"  seed={seed}, {ec}/baseline -> {outcome}")
        print()

    print("=" * 60)
    for ec, outcomes in [("single", single_outcomes), ("double", double_outcomes), ("triple", triple_outcomes)]:
        rec_n = outcomes.count("RECOVERY_DOMINATED")
        sat_n = outcomes.count("SATURATION_DOMINATED")
        print(f"  {ec}: RECOVERY {rec_n}/5, SATURATION {sat_n}/5, other {5-rec_n-sat_n}/5")

    print()
    triple_rec = triple_outcomes.count("RECOVERY_DOMINATED")
    if triple_rec >= 4:
        print(f"D verdict: SEED-ROBUST (triple RECOVERY {triple_rec}/5)")
    elif triple_rec >= 2:
        print(f"D verdict: PARTIALLY SEED-DEPENDENT (triple RECOVERY {triple_rec}/5)")
    else:
        print(f"D verdict: SEED-DEPENDENT (triple RECOVERY {triple_rec}/5) - finding weakened")


if __name__ == "__main__":
    main()
