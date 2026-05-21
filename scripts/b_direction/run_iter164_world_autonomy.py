"""Iter 164: World-side autonomy probe.

Per directive §6 improvement point 3: world-side processes should
move somewhat independently. Lee's criterion: "사람이 없어도 world
state가 조금은 움직일 것".

Test: run accusation scenario with NO seed events at all. Does
anything happen on the world side?

V0: standard scenario (events at t=3, 7, 12, seed rumor) -- baseline
V1: no events, no seed rumor -- pure idle world
V2: no events, only seed rumor -- rumor decay only
V3: no events, no rumor -- pure agent behavior in static world

If V1 produces ZERO world-side change → world is purely reactive.
If V1 produces movement → world has some autonomy.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

N_SEEDS = 5
N_TICKS = 200


def build_world(seed, *, with_events=True, with_rumor=True):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    seed_events = []
    if with_events:
        seed_events = [
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches",
             "location": "priest_courtyard"},
        ]
    seed_rumors = []
    if with_rumor:
        seed_rumors.append({
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        })

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
        seed_events=seed_events,
        seed_rumors=seed_rumors,
        seed=seed,
    ))


def measure_world_activity(label, *, with_events, with_rumor):
    """Track world-side metrics: did anything change?"""
    activity = {
        "shame_climate_max": [],
        "public_susp_max": [],
        "blame_total_max": [],
        "rumor_count_max": [],
        "agent_action_diversity": [],
        "spawned_event_count": [],
    }
    for seed in range(N_SEEDS):
        w = build_world(seed, with_events=with_events, with_rumor=with_rumor)
        max_shame_clim = 0
        max_pub_susp = 0
        max_blame = 0
        max_rumor_count = 0
        action_set = set()
        spawned_count = 0
        for _ in range(N_TICKS):
            result = w.step()
            for c in w._crowds.values():
                max_shame_clim = max(max_shame_clim, c.shame_climate)
                max_pub_susp = max(max_pub_susp, c.public_suspicion)
                max_blame = max(max_blame, sum(c.blame_concentration.values()))
            max_rumor_count = max(max_rumor_count, len(result.rumor_snapshot))
            for action in result.agent_actions.values():
                action_set.add(action)
            spawned_count += len(result.spawned_events)
        activity["shame_climate_max"].append(max_shame_clim)
        activity["public_susp_max"].append(max_pub_susp)
        activity["blame_total_max"].append(max_blame)
        activity["rumor_count_max"].append(max_rumor_count)
        activity["agent_action_diversity"].append(len(action_set))
        activity["spawned_event_count"].append(spawned_count)
    return {
        "label": label,
        "with_events": with_events,
        "with_rumor": with_rumor,
        "shame_climate_peak": round(max(activity["shame_climate_max"]), 3),
        "public_susp_peak": round(max(activity["public_susp_max"]), 3),
        "blame_total_peak": round(max(activity["blame_total_max"]), 3),
        "rumor_count_peak": max(activity["rumor_count_max"]),
        "action_diversity_mean": round(mean(activity["agent_action_diversity"]), 1),
        "spawned_events_total": sum(activity["spawned_event_count"]),
    }


def main() -> int:
    print("[Iter 164] World-side autonomy probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    variants = [
        ("V0_full", True, True),
        ("V1_no_events_no_rumor", False, False),
        ("V2_no_events_with_rumor", False, True),
        ("V3_with_events_no_rumor", True, False),
    ]
    results = {}
    for name, w_ev, w_ru in variants:
        print(f"  Running {name} (events={w_ev}, rumor={w_ru})...")
        r = measure_world_activity(name, with_events=w_ev, with_rumor=w_ru)
        results[name] = r
        print(f"    shame_climate_peak={r['shame_climate_peak']}  "
              f"pub_susp_peak={r['public_susp_peak']}")
        print(f"    blame_peak={r['blame_total_peak']}  "
              f"rumor_count_peak={r['rumor_count_peak']}")
        print(f"    action_diversity={r['action_diversity_mean']}  "
              f"spawned_events={r['spawned_events_total']}")

    print()
    print("=== World-side autonomy verdict ===")
    v1 = results["V1_no_events_no_rumor"]
    print("  V1 (no events, no rumor) shows world activity?")
    print(f"    shame_climate_peak: {v1['shame_climate_peak']} (was 0 → autonomous if > 0)")
    print(f"    public_susp_peak: {v1['public_susp_peak']}")
    print(f"    blame_total_peak: {v1['blame_total_peak']}")
    print(f"    spawned_events: {v1['spawned_events_total']} (events spawned by agent actions)")
    print()
    autonomy_level = 0
    if v1["spawned_events_total"] > 0:
        autonomy_level += 1
        print("  -> Agents spawn events autonomously (no seed events needed)")
    if v1["shame_climate_peak"] > 0.1:
        autonomy_level += 1
        print("  -> shame_climate accumulates without seed events")
    if v1["blame_total_peak"] > 0.1:
        autonomy_level += 1
        print("  -> blame_concentration accumulates without seed events")
    if v1["rumor_count_peak"] > 0:
        autonomy_level += 1
        print("  -> Rumors spawn without seed rumors (forgiveness from confessions)")
    print()
    print(f"  Autonomy signals: {autonomy_level}/4")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "world_autonomy_iter164.json"
    )
    out_path.write_text(
        json.dumps({"n_seeds": N_SEEDS, "n_ticks": N_TICKS, "results": results},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
