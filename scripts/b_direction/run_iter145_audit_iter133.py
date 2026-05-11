"""Iter 145: Audit Iter 133 V2 (low authority_reach +13% recovery claim).

Iter 133 V2: weak accusation (1 acc at priest_courtyard) with
authority_reach lowered 0.9 -> 0.2. Claimed recovery 53%->67% (+13%).

In Iter 133, agents stay at default placement (priest_courtyard
agents 04, 05 stay there). Authority_reach modified IN PLACE. So
they should still experience shame from the accusation event AT
their location.

Audit: do agents at modified priest_courtyard actually experience
peak shame > 1.5, or is this another no-shame artifact?
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

N_SEEDS = 5
N_TICKS = 500


def build_world(seed, *, location_overrides):
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    locations = build_locations()
    for loc in locations:
        if loc.location_id == "priest_courtyard":
            for k, v in location_overrides.items():
                setattr(loc, k, v)

    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=locations,
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


def audit(label, overrides):
    per_agent_peak = defaultdict(list)
    per_agent_final = defaultdict(list)
    for seed in range(N_SEEDS):
        w = build_world(seed, location_overrides=overrides)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        for aid, ts in per_shame.items():
            per_agent_peak[aid].append(max(ts))
            per_agent_final[aid].append(ts[-1])
    return per_agent_peak, per_agent_final


def main() -> int:
    print(f"[Iter 145] Audit Iter 133 V2 (low authority_reach)")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    variants = [
        ("V0_default", {}),
        ("V2_low_authority", {"authority_reach": 0.2}),
    ]
    results = {}
    for name, overrides in variants:
        print(f"  Running {name}...")
        peaks, finals = audit(name, overrides)
        results[name] = (peaks, finals)
        print(f"  {'agent':<10} {'peak (max across N seeds)':<30} {'final (max across N seeds)'}")
        for aid in sorted(peaks.keys()):
            max_peak = max(peaks[aid])
            max_final = max(finals[aid])
            tag = ""
            if max_peak < 1.5:
                tag = " [no-shame]"
            elif max_final < 4.0:
                tag = " [REAL RECOVERY]"
            else:
                tag = " [saturated]"
            print(f"  {aid:<10} {max_peak:<30.2f} {max_final:.2f}{tag}")
        print()

    print("=== Verdict on Iter 133 V2 ===")
    v0_peaks, v0_finals = results["V0_default"]
    v2_peaks, v2_finals = results["V2_low_authority"]
    # Count agents with real recovery (peak >= 1.5 AND final < 4) per variant
    def real_recovery_count(peaks, finals):
        count = 0
        for aid in peaks:
            if max(peaks[aid]) >= 1.5 and max(finals[aid]) < 4.0:
                count += 1
        return count
    v0_real = real_recovery_count(v0_peaks, v0_finals)
    v2_real = real_recovery_count(v2_peaks, v2_finals)
    print(f"  V0 default: {v0_real} agents had real recovery (peak>1.5, final<4)")
    print(f"  V2 low authority: {v2_real} agents had real recovery")
    if v2_real > v0_real:
        print(f"  Iter 133 finding holds: low_auth genuinely improves agent recovery")
    elif v2_real == v0_real:
        print(f"  No change in real recovery agents -- Iter 133's +13% was per-seed-mean shift")
    else:
        print(f"  V2 has FEWER real recovery agents -- Iter 133 finding may be artifact")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "audit_iter133_iter145.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS,
            "v0": {"peaks": v0_peaks, "finals": v0_finals},
            "v2": {"peaks": v2_peaks, "finals": v2_finals},
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
