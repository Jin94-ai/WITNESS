"""Iter 161: Spatial disengagement recovery experiment.

Per WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md §7
priority 4 + §6 improvement point 2: explore recovery families
beyond Phase 2a.

Candidate: spatial disengagement -- if agent at high-pressure
location is MOVED MID-SIM to low-pressure location AFTER shame
has accumulated, does shame decrease?

This is different from Iter 140-144 (initial placement) -- here
agents accumulate shame AT high-pressure location, then relocate.

Setup:
  Start: agents 06, 07, 08 (city_street) accumulating shame from
    accusation event at city_street.
  At tick 80 (after shame accumulates): MOVE them to upper_room (low-pressure).
  Continue to tick 500.

V0: no relocation (control) -- expect saturation
V1: relocate at tick 80 -- if shame drops, spatial disengagement is a real recovery family

If V1 produces real recovery (peak >= 1.5 with final < 4 for relocated agents),
spatial disengagement is a NEW recovery family separate from Phase 2a.
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
RELOCATE_TICK = 80


def build_world(seed):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

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


def run_variant(label, relocate):
    """Run scenario; if relocate, move city_street agents to upper_room at tick 80."""
    per_seed_finals = []
    per_seed_peaks = []
    target_agents = ["agent_06", "agent_07", "agent_08"]
    for seed in range(N_SEEDS):
        w = build_world(seed)
        per_shame = defaultdict(list)
        for tick in range(N_TICKS):
            w.step()
            # Mid-sim relocation (priority 4 experiment)
            if relocate and tick == RELOCATE_TICK - 1:
                for aid in target_agents:
                    w._spatial.move(aid, "upper_room")
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        seed_finals = {aid: per_shame[aid][-1] for aid in target_agents}
        seed_peaks = {aid: max(per_shame[aid]) for aid in target_agents}
        per_seed_finals.append(seed_finals)
        per_seed_peaks.append(seed_peaks)

    # Aggregate by agent
    summary = {}
    for aid in target_agents:
        peaks = [p[aid] for p in per_seed_peaks]
        finals = [f[aid] for f in per_seed_finals]
        # Real recovery: peak >= 1.5 AND final < 4
        real_recovery = sum(
            1 for p, f in zip(peaks, finals) if p >= 1.5 and f < 4.0)
        summary[aid] = {
            "peaks": [round(p, 2) for p in peaks],
            "finals": [round(f, 2) for f in finals],
            "real_recovery_count": real_recovery,
        }
    return {"label": label, "relocate": relocate, "per_agent": summary}


def main() -> int:
    print("[Iter 161] Spatial disengagement recovery experiment")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print(f"  RELOCATE_TICK={RELOCATE_TICK}")
    print()

    for label, relocate in [("V0_no_relocate", False), ("V1_relocate_t80", True)]:
        print(f"  Running {label}...")
        r = run_variant(label, relocate)
        for aid, info in r["per_agent"].items():
            tag = ""
            if info["real_recovery_count"] >= 3:
                tag = " [RECOVERY MAJORITY]"
            elif info["real_recovery_count"] > 0:
                tag = " [partial]"
            print(f"    {aid}: peaks={info['peaks']} finals={info['finals']} "
                  f"real_recovery={info['real_recovery_count']}/{N_SEEDS}{tag}")
        print()

    print("=== Spatial disengagement verdict ===")
    print("  V0 (no relocate): control -- expect saturation")
    print(f"  V1 (relocate at t={RELOCATE_TICK}): if real recovery > 0, spatial disengagement is a real recovery family")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "spatial_disengage_iter161.json"
    )
    out_path.write_text(
        json.dumps({"n_seeds": N_SEEDS, "n_ticks": N_TICKS,
                    "relocate_tick": RELOCATE_TICK}, indent=2),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
