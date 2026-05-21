"""Iter 144: Audit Iter 140 V1 (priest/soldier at upper_room).

Iter 143 found Iter 142 'rescue' was no-shame artifact. Apply same
audit to Iter 140 V1: agents 04 (priest) and 05 (soldier) relocated
from priest_courtyard to upper_room. Reported '100% recovery'.

Same question: did they recover from shame, or never experience it?
Different answer expected because OTHER agents in the scenario ARE
at high-pressure locations (city_street outsider accusation site).
The cross-crowd dynamics may still propagate to upper_room agents.

If peak shame > 1.5: real recovery
If peak shame ~= 1.0 or less: same no-shame artifact, Iter 140
finding also corrected
"""

from __future__ import annotations

import copy
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


def build_augmented_cast():
    from engine.population import ROLE_CLUSTERS
    from scripts.b_direction.run_accusation_scene import build_accusation_cast
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
    """Iter 140 V1: agents 04, 05 at upper_room."""
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_locations,
        build_social_network,
    )

    agents = build_augmented_cast()
    aids = [a.agent_id for a in agents]
    placements = {
        "agent_01": "upper_room", "agent_02": "upper_room",
        "agent_03": "upper_room",
        "agent_04": "upper_room",  # MOVED (Iter 140 V1)
        "agent_05": "upper_room",  # MOVED (Iter 140 V1)
        "agent_06": "city_street", "agent_07": "city_street",
        "agent_08": "city_street", "agent_09": "upper_room",
        "agent_10": "city_street",
    }
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements=placements,
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
    print("[Iter 144] Audit Iter 140 V1 (priest/soldier at upper_room)")
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

    print(f"  {'agent':<10} {'role':<22} {'peak':<28} {'final'}")
    no_shame, real_recovery, saturated = 0, 0, 0
    for aid in sorted(per_agent_peak.keys()):
        peaks = [round(p, 2) for p in per_agent_peak[aid]]
        finals = [round(f, 2) for f in per_agent_final[aid]]
        max_peak = max(peaks)
        if max_peak < 1.5:
            no_shame += 1
            tag = " [no-shame]"
        elif max(finals) < 4.0:
            real_recovery += 1
            tag = " [REAL RECOVERY]"
        else:
            saturated += 1
            tag = " [saturated]"
        print(f"  {aid:<10} {role_map[aid]:<22} {str(peaks):<28} {str(finals)}{tag}")

    print()
    print("=== Iter 140 V1 verdict ===")
    print(f"  No shame: {no_shame}, Real recovery: {real_recovery}, Saturated: {saturated}")

    a04_peaks = per_agent_peak.get("agent_04", [])
    a05_peaks = per_agent_peak.get("agent_05", [])
    a04_max = max(a04_peaks) if a04_peaks else 0
    a05_max = max(a05_peaks) if a05_peaks else 0
    print(f"  agent_04 (priest) peak shame max: {a04_max}")
    print(f"  agent_05 (soldier) peak shame max: {a05_max}")
    print()
    if a04_max < 1.5 and a05_max < 1.5:
        print("  CAVEAT TRIGGERED: agents 04, 05 never experienced meaningful shame")
        print("  Iter 140 V1 'recovery' was likely no-shame artifact")
    elif a04_max >= 1.5 and a05_max >= 1.5:
        print("  REAL RECOVERY: agents 04, 05 had peak shame > 1.5 then recovered")
        print("  Iter 140 finding stands")
    else:
        print("  MIXED: one recovered, one no-shame")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "iter140_audit_iter144.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS,
            "per_agent_peaks": {aid: per_agent_peak[aid] for aid in per_agent_peak},
            "per_agent_finals": {aid: per_agent_final[aid] for aid in per_agent_final},
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
