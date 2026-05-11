"""Iter 138: Per-agent audit of Iter 118 V3 (3 outsiders, 2 acc diff).

Discovery: outsider role's affordance_pack does NOT include 'confess'.
But Iter 118 V3 reported 93% recovery rate.

Question: how does the outsider cohort get forgiven if they can't confess?

Hypothesis options:
  A) Outsiders DO recover via crowd-layer climate reduction (ambient
     forgiveness from disciple confessions reduces shame_climate at
     city_street, indirectly reducing outsider shame)
  B) Outsiders DON'T recover; mean is dominated by non-outsider agents
  C) Some other agent confesses with target_role = outsider somehow

Probe: examine per-agent finals broken out by role in Iter 118 V3
condition (aug cast 3 outsiders + 2 acc diff roles).
"""

from __future__ import annotations

import copy
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

N_SEEDS = 5  # smaller for per-agent detail
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
    print(f"[Iter 138] Per-agent audit of Iter 118 V3")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    per_agent_finals_by_role = defaultdict(list)
    per_agent_finals_by_id = defaultdict(list)
    confessor_role_count = defaultdict(int)
    for seed in range(N_SEEDS):
        w = build_world(seed)
        # Note role mapping
        aid_to_role = {aid: a.role_id for aid, a in w._agents.items()}
        per_shame = defaultdict(list)
        for tick in range(N_TICKS):
            result = w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            for aid, action in result.agent_actions.items():
                if action == "confess":
                    confessor_role_count[aid_to_role[aid]] += 1
        for aid, ts in per_shame.items():
            role = aid_to_role[aid]
            per_agent_finals_by_role[role].append(ts[-1])
            per_agent_finals_by_id[aid].append(ts[-1])

    print("=== Per-role final shame ===")
    print(f"  {'role':<24} {'mean final':<12} {'min':<8} {'max':<8} {'n_samples'}")
    for role, finals in per_agent_finals_by_role.items():
        m = mean(finals)
        print(f"  {role:<24} {m:<12.2f} {min(finals):<8.2f} {max(finals):<8.2f} {len(finals)}")

    print()
    print("=== Per-agent final shame (across N seeds) ===")
    print(f"  {'agent':<10} {'role':<22} {'finals across seeds'}")
    for aid in sorted(per_agent_finals_by_id.keys()):
        # Get the role from any seed (consistent)
        w_check = build_world(0)
        role = w_check._agents[aid].role_id
        finals = per_agent_finals_by_id[aid]
        finals_str = ", ".join(f"{f:.1f}" for f in finals)
        print(f"  {aid:<10} {role:<22} [{finals_str}]")

    print()
    print("=== Confessor role distribution ===")
    print(f"  {'role':<22} {'confess count'}")
    for role, count in sorted(confessor_role_count.items(), key=lambda x: -x[1]):
        print(f"  {role:<22} {count}")

    print()
    print("=== Hypothesis verdict ===")
    outsider_finals = per_agent_finals_by_role.get("outsider", [])
    outsider_recover_rate = sum(1 for f in outsider_finals if f < 4.0) / len(outsider_finals) if outsider_finals else 0
    print(f"  Outsider final shame: mean={mean(outsider_finals):.2f}, "
          f"recover rate (<4.0)={outsider_recover_rate*100:.0f}%")
    if "outsider" in confessor_role_count and confessor_role_count["outsider"] > 0:
        print(f"  Outsiders DID confess ({confessor_role_count['outsider']} times)")
        print(f"  -> Outsiders not strictly bound by affordance_pack? Investigate further")
    else:
        print(f"  Outsiders did NOT confess")
        if outsider_recover_rate > 0.5:
            print(f"  -> Outsiders recover via OTHER mechanism (likely crowd-layer climate)")
        else:
            print(f"  -> Outsiders DON'T recover; Iter 118 mean was misleading")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "per_agent_iter138.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS,
            "per_role": {role: {"mean": mean(finals), "min": min(finals), "max": max(finals), "n": len(finals)}
                        for role, finals in per_agent_finals_by_role.items()},
            "confessor_role_count": dict(confessor_role_count),
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
