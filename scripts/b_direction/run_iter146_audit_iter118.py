"""Iter 146: Audit Iter 118 V3 strongest finding (cast augmentation rescue).

Iter 118 V3: aug cast (3 outsiders) + 2 acc diff roles -> 93% recovery.
This is the strongest single finding of the arc. After Iter 143-144
cascade-corrections of Iter 140-142, audit this one too.

Question: did agents at city_street (07, 08, 10 outsiders, 06 crowd)
actually experience peak shame > 1.5 and recover, or is the
'recovery' another no-shame artifact?

Per Iter 138 we saw their finals at 0.0. But peaks weren't measured.
"""

from __future__ import annotations

import copy
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


def build_augmented_cast():
    from scripts.b_direction.run_accusation_scene import build_accusation_cast
    from engine.population import ROLE_CLUSTERS
    base = build_accusation_cast()
    aug = []
    for a in base:
        new_agent = copy.deepcopy(a)
        if a.agent_id in ("agent_07", "agent_08"):
            new_agent.role_id = "outsider"
            new_agent.affordance_pack = list(
                ROLE_CLUSTERS["outsider"].affordance_pack)
        aug.append(new_agent)
    return aug


def build_world(seed):
    """Iter 118 V3: aug cast + 2 acc diff."""
    from scripts.b_direction.run_accusation_scene import (
        build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_augmented_cast()
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


def main() -> int:
    print(f"[Iter 146] Audit Iter 118 V3 strongest finding")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    per_agent_peak = defaultdict(list)
    per_agent_final = defaultdict(list)
    role_map = {}
    for seed in range(N_SEEDS):
        w = build_world(seed)
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

    print(f"  {'agent':<10} {'role':<22} {'peak (max)':<12} {'final (max)':<12} {'classification'}")
    no_shame, real_recovery, saturated = 0, 0, 0
    for aid in sorted(per_agent_peak.keys()):
        max_peak = max(per_agent_peak[aid])
        max_final = max(per_agent_final[aid])
        if max_peak < 1.5:
            no_shame += 1
            tag = "[no-shame]"
        elif max_final < 4.0:
            real_recovery += 1
            tag = "[REAL RECOVERY]"
        else:
            saturated += 1
            tag = "[saturated]"
        print(f"  {aid:<10} {role_map[aid]:<22} {max_peak:<12.2f} {max_final:<12.2f} {tag}")

    print()
    print(f"  Total: 10 agents")
    print(f"  No shame: {no_shame}, Real recovery: {real_recovery}, Saturated: {saturated}")

    print()
    print("=== Iter 118 V3 verdict ===")
    if real_recovery >= 3:
        print(f"  Iter 118 finding HOLDS: {real_recovery} agents had real recovery")
        print(f"  Cast augmentation rescue is genuine for {real_recovery} agents")
        print(f"  Saturating agents (priest cohort) per Iter 138 are also real (real shame)")
    else:
        print(f"  Iter 118 finding QUESTIONABLE: only {real_recovery} agents had real recovery")
        print(f"  Cast augmentation may be partially no-shame artifact too")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "audit_iter118_iter146.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS,
            "per_agent_peaks": {aid: per_agent_peak[aid] for aid in per_agent_peak},
            "per_agent_finals": {aid: per_agent_final[aid] for aid in per_agent_final},
            "no_shame": no_shame, "real_recovery": real_recovery,
            "saturated": saturated,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
