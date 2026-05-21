"""Iter 148: Test cast over-representation past n=3.

Iter 136 (no-rumor): n=2: 100%, n=3: 73% (drop). Question: does
the trend continue at n=4, or stabilize?

n=4 outsiders requires reassigning all crowd_participants (06, 07, 08)
to outsider, leaving 0 crowd_participants. Cast becomes:
- 3 disciples, 1 priest, 1 soldier, 0 crowd, 1 family, 4 outsiders

If recovery continues to drop: over-representation is harmful
If it stabilizes: n=2 sweet spot but plateau follows

Conditions (N=15 × 500t):
  V0 n=3 with rumor (Iter 119 reference, 93%)
  V1 n=4 with rumor
  V2 n=4 no rumor
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

N_SEEDS = 15
N_TICKS = 500


def build_cast_with_n_outsiders(n_outsiders):
    from engine.population import ROLE_CLUSTERS
    from scripts.b_direction.run_accusation_scene import build_accusation_cast
    base = build_accusation_cast()
    reassign_candidates = ["agent_07", "agent_08", "agent_06"]
    n_to_reassign = n_outsiders - 1
    reassign_set = set(reassign_candidates[:max(0, n_to_reassign)])
    aug = []
    for a in base:
        new_agent = copy.deepcopy(a)
        if a.agent_id in reassign_set:
            new_agent.role_id = "outsider"
            new_agent.affordance_pack = list(
                ROLE_CLUSTERS["outsider"].affordance_pack)
        aug.append(new_agent)
    return aug


def build_world(seed, *, n_outsiders, include_rumor):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_locations,
        build_social_network,
    )

    agents = build_cast_with_n_outsiders(n_outsiders)
    aids = [a.agent_id for a in agents]
    seed_rumors = []
    if include_rumor:
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
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
        ],
        seed_rumors=seed_rumors,
        seed=seed,
    ))


def run_variant(label, *, n_outsiders, include_rumor):
    finals = []
    for seed in range(N_SEEDS):
        w = build_world(seed, n_outsiders=n_outsiders,
                        include_rumor=include_rumor)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        # Real recovery requires peak >= 1.5 AND final < 4
        # But for compatibility with previous probes, also report population recovery
        ag_peak = []
        ag_finals = []
        real_recovery_count = 0
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                ag_peak.append(max(ts))
                ag_finals.append(ts[-1])
                if ts[-1] < 4.0:
                    real_recovery_count += 1
        avg_final = mean(ag_finals) if ag_finals else 0.0
        finals.append(avg_final)
    rec_count = sum(1 for f in finals if f < 4.0)
    return {
        "label": label,
        "n_outsiders": n_outsiders,
        "include_rumor": include_rumor,
        "finals": [round(f, 2) for f in finals],
        "mean": round(mean(finals), 3),
        "recovery_rate": f"{rec_count}/{N_SEEDS}",
        "recovery_pct": round(100 * rec_count / N_SEEDS, 1),
    }


def main() -> int:
    print("[Iter 148] Cast over-representation curve (n=4)")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    variants = [
        ("V0_n3_rumor", 3, True),
        ("V1_n4_rumor", 4, True),
        ("V2_n4_no_rumor", 4, False),
    ]
    results = {}
    for name, n, with_rumor in variants:
        rumor_str = "rumor" if with_rumor else "no-rumor"
        print(f"  Running {name} (n={n} outsiders, {rumor_str})...")
        r = run_variant(name, n_outsiders=n, include_rumor=with_rumor)
        results[name] = r
        print(f"    final mean={r['mean']}  recovery={r['recovery_rate']} ({r['recovery_pct']}%)")

    print()
    print("=== Cast over-representation curve ===")
    print(f"  {'config':<24} {'recovery'}")
    print(f"  {'n=2 with rumor (Iter 119)':<24} 100%")
    print(f"  {'n=2 no rumor (Iter 136)':<24} 100%")
    print(f"  {'n=3 with rumor (Iter 119)':<24} 93%")
    print(f"  {'n=3 no rumor (Iter 136)':<24} 73%")
    for name, _, _ in variants:
        r = results[name]
        print(f"  {name:<24} {r['recovery_pct']}%")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "n4_outsiders_iter148.json"
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
