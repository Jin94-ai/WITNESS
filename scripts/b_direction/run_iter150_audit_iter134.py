"""Iter 150: Audit Iter 134 timing finding (53% at t=3 vs 20% at t=50+).

Iter 134 claimed accusation timing matters: t=3 -> 53% recovery, t=50+ -> 20%.
Iter 135 corrected mechanism (rumor interferes, not amplifies).

But did agents actually EXPERIENCE shame at later timings? Or is the
"20% recovery" artifact-prone like Iter 140-142?

Audit: t=3 vs t=50 with per-agent peak/final classification.
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

N_SEEDS = 5
N_TICKS = 500


def build_world(seed, accusation_tick):
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
            {"tick": accusation_tick, "event_id": "public_accusation",
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


def audit(label, accusation_tick):
    per_agent_peak = defaultdict(list)
    per_agent_final = defaultdict(list)
    role_map = {}
    for seed in range(N_SEEDS):
        w = build_world(seed, accusation_tick)
        role_map.update({aid: a.role_id for aid, a in w._agents.items()})
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        for aid, ts in per_shame.items():
            per_agent_peak[aid].append(max(ts))
            per_agent_final[aid].append(ts[-1])
    return per_agent_peak, per_agent_final, role_map


def main() -> int:
    print(f"[Iter 150] Audit Iter 134 timing finding")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    for label, tick in [("V0_t3", 3), ("V1_t50", 50)]:
        print(f"  Running {label} (accusation at tick={tick})...")
        peaks, finals, role_map = audit(label, tick)
        no_shame, real_recovery, saturated = 0, 0, 0
        print(f"  {'agent':<10} {'role':<22} {'peak':<14} {'final':<14} {'tag'}")
        for aid in sorted(peaks.keys()):
            max_peak = max(peaks[aid])
            max_final = max(finals[aid])
            if max_peak < 1.5:
                no_shame += 1
                tag = "[no-shame]"
            elif max_final < 4.0:
                real_recovery += 1
                tag = "[REAL RECOVERY]"
            else:
                saturated += 1
                tag = "[saturated]"
            peaks_str = str([round(p, 2) for p in peaks[aid][:3]])
            finals_str = str([round(f, 2) for f in finals[aid][:3]])
            print(f"  {aid:<10} {role_map[aid]:<22} {peaks_str:<14} {finals_str:<14} {tag}")
        print(f"    Total: no-shame={no_shame}, real recovery={real_recovery}, saturated={saturated}")
        print()

    print("=== Iter 134 timing finding audit verdict ===")
    print(f"  If V0 (t=3) and V1 (t=50) both have agents reaching peak >=1.5,")
    print(f"  then timing finding is real recovery vs different recovery.")
    print(f"  If V1 has fewer/no real recovery agents, the 'lower recovery rate'")
    print(f"  is masked by no-shame artifacts at later tick.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
