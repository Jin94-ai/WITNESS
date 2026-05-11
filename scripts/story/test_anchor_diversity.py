"""J-Alpha follow-up - anchor diversity 빠른 테스트.

Van Gogh→sacred 5/5 PARTIAL FAIL의 보완 시도. 다른 anchor 후보를
5 seeds로 빠르게 측정.

Anchor 후보:
- accusation baseline (1 accusation against disciple_follower)
- accusation more events (multiple accusations)
- scarcity high crowd density (cross-seed test에서 가장 sensitive)
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

from scripts.b_direction.generate_readability_probes import N_TICKS
from scripts.b_direction.test_d_prime_generalization import measure
from scripts.b_direction.run_accusation_scene import (
    build_accusation_cast, build_locations as acc_locs, build_social_network as acc_net,
)
from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world
from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorldConfig, MicroWorld


def build_accusation_baseline(seed: int):
    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=acc_locs(),
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
        social_network=acc_net(aids),
        seed_events=[
            {"tick": 5, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 12, "event_id": "guard_approaches", "location": "upper_room"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def main():
    print("J-Alpha follow-up: anchor diversity test\n")

    candidates = {
        "accusation_baseline": (
            build_accusation_baseline,
            "accusation 1 acc + 1 guard + baseline placement",
        ),
        "scarcity_high_density": (
            lambda s: build_scarcity_depth_world(seed=s, event_count="single", crowd_density="high"),
            "scarcity single accusation + high crowd density (0.9, 0.8)",
        ),
    }

    for label, (builder, desc) in candidates.items():
        print(f"\n=== {label} ===")
        print(f"  {desc}")
        outcomes = []
        for seed in range(5):
            w = builder(seed)
            outcome, conf, forg, final = measure(w)
            outcomes.append(outcome)
            print(f"  seed={seed}: {outcome}")
        unique = Counter(outcomes)
        n_distinct = len(unique)
        print(f"  -> {n_distinct} distinct outcomes (most common: {unique.most_common(1)[0]})")
        if n_distinct >= 3:
            print(f"  [READY] J-Alpha anchor: {n_distinct} distinct outcomes (>=3, like Peter scarcity)")
        elif n_distinct == 2:
            print(f"  [MARGINAL] 2 distinct - possible but less variation")
        else:
            print(f"  [FAIL] {n_distinct} distinct - too uniform like VG sacred substitute")


if __name__ == "__main__":
    main()
