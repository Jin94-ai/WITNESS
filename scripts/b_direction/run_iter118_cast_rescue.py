"""Iter 118: Cast augmentation rescue test.

Iter 117 confirmed conjunctive recovery model:
  recovery_rate ~ Π P(each accused role gets timely forgiveness)

Hypothesis: 2-acc-diff-roles fails because cast has only 1 outsider
(agent_10), so P(timely outsider confess) is low. Adding more
outsider agents should rescue recovery rate substantially.

Conditions (N=15 × 500t):
  V0: original cast (1 outsider) + 1 acc disciple              -- baseline 53%
  V1: original cast + 2 acc diff roles (Iter 117 V3)           -- baseline 0%
  V2: augmented cast (3 outsiders) + 1 acc disciple            -- predict ~53%
  V3: augmented cast (3 outsiders) + 2 acc diff roles          -- predict >> 0%
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

N_SEEDS = 15
N_TICKS = 500


def build_augmented_cast():
    """Cast with 3 outsiders instead of 1.

    Same total 10 agents, but: agents 07, 08 reassigned from
    crowd_participant to outsider; agent_10 stays outsider.
    """
    from engine.population import ROLE_CLUSTERS
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
    )

    base = build_accusation_cast()
    aug = []
    for a in base:
        new_agent = copy.deepcopy(a)
        if a.agent_id in ("agent_07", "agent_08"):
            # Reassign to outsider
            new_agent.role_id = "outsider"
            new_agent.affordance_pack = list(
                ROLE_CLUSTERS["outsider"].affordance_pack)
        aug.append(new_agent)
    return aug


def build_world(seed, *, augmented_cast, accusations):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    if augmented_cast:
        agents = build_augmented_cast()
    else:
        agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": tick, "event_id": "public_accusation",
         "target_role": role, "location": loc}
        for tick, role, loc in accusations
    ]

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
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
    ))


def run_variant(label, *, augmented_cast, accusations):
    finals = []
    for seed in range(N_SEEDS):
        w = build_world(seed, augmented_cast=augmented_cast,
                        accusations=accusations)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        ag_finals = []
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                ag_finals.append(ts[-1])
        finals.append(mean(ag_finals) if ag_finals else 0.0)
    rec_count = sum(1 for f in finals if f < 4.0)
    return {
        "label": label,
        "augmented_cast": augmented_cast,
        "accusations": accusations,
        "finals": [round(f, 2) for f in finals],
        "mean": round(mean(finals), 3),
        "stdev": round(stdev(finals) if len(finals) > 1 else 0, 3),
        "recovery_rate": f"{rec_count}/{N_SEEDS}",
        "recovery_pct": round(100 * rec_count / N_SEEDS, 1),
    }


def main() -> int:
    print("[Iter 118] Cast augmentation rescue test")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    one_acc = [(3, "disciple_follower", "priest_courtyard")]
    two_acc_diff = [
        (3, "disciple_follower", "priest_courtyard"),
        (7, "outsider", "city_street"),
    ]
    variants = [
        ("V0_orig_1acc", False, one_acc),
        ("V1_orig_2acc_diff", False, two_acc_diff),
        ("V2_aug_1acc", True, one_acc),
        ("V3_aug_2acc_diff", True, two_acc_diff),
    ]
    results = {}
    for name, aug, accs in variants:
        print(f"  Running {name} (augmented={aug})...")
        r = run_variant(name, augmented_cast=aug, accusations=accs)
        results[name] = r
        print(f"    final mean={r['mean']} stdev={r['stdev']}  "
              f"recovery={r['recovery_rate']} ({r['recovery_pct']}%)")
        print(f"    finals: {r['finals']}")

    print()
    print("=== Cast augmentation effect ===")
    print(f"  {'variant':<24} {'cast':<10} {'accusations':<8} {'recovery'}")
    for name, aug, accs in variants:
        r = results[name]
        cast = "aug(3o)" if aug else "orig(1o)"
        n_acc = f"{len(accs)} acc"
        print(f"  {name:<24} {cast:<10} {n_acc:<8} {r['recovery_rate']}")

    print()
    print("=== Conjunctive model verdict ===")
    v1 = results["V1_orig_2acc_diff"]["recovery_pct"]
    v3 = results["V3_aug_2acc_diff"]["recovery_pct"]
    print(f"  V1 (orig cast + 2 diff roles):    {v1}%  (Iter 117: 0%)")
    print(f"  V3 (aug cast + 2 diff roles):     {v3}%")
    print()
    if v3 > v1 + 15:
        print(f"  DELTA = +{v3 - v1}% -- conjunctive model PREDICTION CONFIRMED")
        print("    Adding outsider agents raises P(timely outsider confess)")
        print("    -> P(both forgiveness rumors fire) increases")
        print("    -> recovery rate rises substantially")
    elif v3 > v1:
        print(f"  DELTA = +{v3 - v1}% -- modest support; could be noise")
    else:
        print(f"  DELTA = {v3 - v1}% -- model NOT confirmed; investigate")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "cast_rescue_iter118.json"
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
