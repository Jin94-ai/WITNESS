"""Iter 165: Meso-scale field cross-coupling probe.

Per directive §6 improvement 4 (Meso-scale 강화), test whether
existing meso fields (shame_climate, public_suspicion, blame_total,
alignment_strength) cross-correlate -- indicating effective
coupling via indirect path even when step_crowd treats them as
independent decay processes.

If high correlation: meso-scale already has rich dynamics
If low correlation: meso fields are independent → 'strengthening'
  could mean adding direct couplings

Method: trace per-tick values, compute Pearson correlation matrix
across N=5 seeds × 200 ticks at priest_courtyard.
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

N_SEEDS = 5
N_TICKS = 200


def correlation(xs, ys):
    """Pearson correlation. Returns nan if undefined."""
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    denom = (dx * dy) ** 0.5
    if denom < 1e-9:
        return float("nan")
    return num / denom


def build_world(seed):
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
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
        social_network=build_social_network(aids),
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches",
             "location": "priest_courtyard"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
    ))


def trace_meso(seed):
    w = build_world(seed)
    traces = {
        "shame_climate": [],
        "public_susp": [],
        "blame_total": [],
        "alignment": [],
        "density": [],
    }
    for _ in range(N_TICKS):
        w.step()
        c = w._crowds["priest_courtyard"]
        traces["shame_climate"].append(c.shame_climate)
        traces["public_susp"].append(c.public_suspicion)
        traces["blame_total"].append(sum(c.blame_concentration.values()))
        traces["alignment"].append(c.alignment_strength)
        traces["density"].append(c.density)
    return traces


def main() -> int:
    print(f"[Iter 165] Meso field cross-coupling probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print(f"  Location: priest_courtyard")
    print()

    fields = ["shame_climate", "public_susp", "blame_total", "alignment", "density"]
    # Aggregate traces from all seeds (concatenate)
    all_traces = {f: [] for f in fields}
    for seed in range(N_SEEDS):
        t = trace_meso(seed)
        for f in fields:
            all_traces[f].extend(t[f])

    # Correlation matrix
    print(f"  Correlation matrix (Pearson, across {N_SEEDS}×{N_TICKS}={N_SEEDS*N_TICKS} samples):")
    print(f"  {'':<16}" + "".join(f"{f:>16}" for f in fields))
    corr_matrix = {}
    for f1 in fields:
        row = {}
        line = f"  {f1:<16}"
        for f2 in fields:
            c = correlation(all_traces[f1], all_traces[f2])
            row[f2] = c
            line += f"{c:>16.3f}" if not (c != c) else f"{'nan':>16}"
        print(line)
        corr_matrix[f1] = row

    print()
    print("=== Cross-coupling verdict ===")
    # Look at off-diagonal correlations
    high_couplings = []
    for f1 in fields:
        for f2 in fields:
            if f1 < f2:  # avoid duplicates
                c = corr_matrix[f1][f2]
                if c == c and abs(c) > 0.3:  # > 0.3 absolute = meaningful
                    high_couplings.append((f1, f2, c))
    if high_couplings:
        print(f"  Notable cross-couplings (|r| > 0.3):")
        for f1, f2, c in sorted(high_couplings, key=lambda x: -abs(x[2])):
            print(f"    {f1} ↔ {f2}: r={c:+.3f}")
    else:
        print(f"  No notable cross-couplings (|r| < 0.3 across all pairs)")
        print(f"  Meso fields are EFFECTIVELY DECOUPLED")
    print()
    print(f"  Per directive §6 improvement 4 (meso-scale 강화):")
    if len(high_couplings) >= 3:
        print(f"  -> Already richly coupled ({len(high_couplings)} pairs); 'strengthening' could mean exposing this in probes")
    elif len(high_couplings) >= 1:
        print(f"  -> Partial coupling ({len(high_couplings)} pairs); strengthening would add direct couplings")
    else:
        print(f"  -> Decoupled processes; strengthening means adding direct cross-field rules")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "meso_coupling_iter165.json"
    )
    out_path.write_text(
        json.dumps({"n_seeds": N_SEEDS, "n_ticks": N_TICKS,
                    "correlation_matrix": corr_matrix},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
