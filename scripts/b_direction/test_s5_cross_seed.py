"""S5 placement variation cross-seed ensemble test.

Per LOOP 73 caveat + LOOP 74 D' cross-seed pattern: validate within-scenario
configuration sensitivity claim (67%/67%/22%/44%) by running S5 9 probes
across seeds 0-4. 45 runs.

For each (scenario, variant), report 5-seed modal outcome + variance.
Compute new sensitivity ratio: how often does (variant != baseline) modal flip?
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

from scripts.b_direction.generate_placement_variations import (
    SCENARIO_BUILDERS,
)
from scripts.b_direction.test_d_prime_generalization import measure


def main():
    print("S5 placement cross-seed ensemble test\n")
    print("9 (scenario, variant) cells x 5 seeds = 45 runs\n")

    # Map (scenario, variant) -> outcomes per seed
    results = defaultdict(list)
    for scenario in ["accusation", "scarcity", "sacred"]:
        builder, placements_dict = SCENARIO_BUILDERS[scenario]
        for variant in ["original", "inverted", "clustered"]:
            placements = placements_dict[variant]
            for seed in range(5):
                w = builder(seed=seed, p2a=True, sham_mul=None, placements=placements)
                outcome, _, _, _ = measure(w)
                results[(scenario, variant)].append(outcome)

    # Per-cell modal report
    print(f"{'Scenario':<11} {'Variant':<10} {'s0':<22} {'s1':<22} {'s2':<22} {'s3':<22} {'s4':<22}")
    for (scen, var), outs in results.items():
        line = f"{scen:<11} {var:<10} " + " ".join(f"{o:<22}" for o in outs)
        print(line)

    print()
    print("Modal outcome per cell:")
    for (scen, var), outs in results.items():
        modal = Counter(outs).most_common(1)[0]
        print(f"  {scen:<11} {var:<10}: {modal[0]} ({modal[1]}/5)")

    # Compute cross-seed sensitivity vs baseline ('original') per scenario
    print()
    print("Cross-seed configuration sensitivity (modal flip vs baseline 'original'):")
    flip_total = 0
    cell_total = 0
    for scenario in ["accusation", "scarcity", "sacred"]:
        baseline_modal = Counter(results[(scenario, "original")]).most_common(1)[0][0]
        for variant in ["original", "inverted", "clustered"]:
            variant_modal = Counter(results[(scenario, variant)]).most_common(1)[0][0]
            flips = variant_modal != baseline_modal
            cell_total += 1
            if flips:
                flip_total += 1
            print(f"  {scenario:<11} {variant:<10}: modal {variant_modal}, vs baseline {baseline_modal}, flip={'yes' if flips else 'no'}")

    print()
    print(f"Cross-seed S5 sensitivity: {flip_total}/{cell_total} = {flip_total/cell_total*100:.1f}%")
    print("(Compare to seed=0-only LOOP 59 result: 6/9 = 67%)")

    # Within-cell variance summary
    print()
    print("Within-cell variance (5/5 unanimous? mode-share?):")
    unan = 0
    for (scen, var), outs in results.items():
        unique = set(outs)
        if len(unique) == 1:
            unan += 1
            print(f"  {scen:<11} {var:<10}: 5/5 unanimous ({outs[0]})")
        else:
            modal = Counter(outs).most_common(1)[0]
            print(f"  {scen:<11} {var:<10}: {modal[1]}/5 modal, {len(unique)} distinct outcomes")
    print(f"  -> {unan}/9 cells unanimous across 5 seeds")


if __name__ == "__main__":
    main()
