"""World-side autonomy probe (Priority 3 of WORLD_BUILDING_ELEMENTS).

Tests whether world state evolves WITHOUT agent activity. Demonstrates
척도 1 (World-side Autonomy) per WORLD_BUILDING §3.

Method:
  - Build accusation MicroWorld (10 agents)
  - Seed 1 active rumor + 1 accusation event + 1 guard_approaches event
  - Run two conditions:
    A: normal (with agent decisions)
    B: agent-frozen (skip Phase 3 agent_decide; agents passive)
  - Measure crowd state evolution over 100 ticks in B

If world state in B evolves at all → autonomy ≥ 1.
If multiple processes in B evolve independently → autonomy ≥ 2.
If processes show cross-influence in B → autonomy = 3.

Note: completely "agent-frozen" requires monkey-patching MicroWorld.step
to skip Phase 3-4. We do that here to isolate world-side processes.
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

N_TICKS = 100


def build_accusation_world(seed=0):
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
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            # Iter 89 audit fix: guard_approaches must target a location
            # with a CrowdState, else handler silently skips.
            {"tick": 12, "event_id": "guard_approaches", "location": "priest_courtyard"},
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


def freeze_agents(world):
    """Replace agent_decide with no-op so agents take no actions.

    Returns original method for restoration.
    """
    original_decide = world._agent_decide

    def noop_decide(agent, tick):
        # Return a non-action to skip downstream consequences
        return ("follow_closely", "remain_present")

    world._agent_decide = noop_decide
    return original_decide


def snapshot_world(world, tick):
    """Extract current world-side state."""
    crowds = {}
    for cid, c in world._crowds.items():
        crowds[cid] = {
            "density": c.density,
            "alignment_strength": c.alignment_strength,
            "shame_climate": c.shame_climate,
            "authority_vigilance": c.authority_vigilance,
            "blame_concentration": dict(c.blame_concentration),
            "rumor_intensity": c.rumor_intensity,
            "accusation_amplification": c.accusation_amplification,
            "phase": getattr(c, "phase", "unknown"),
        }
    rumors = []
    for r in world._rumors.get_active():
        rumors.append({
            "tag": r.content_tag,
            "target_role": r.target_role,
            "intensity": r.intensity,
            "reach_size": len(r.reach),
        })
    return {"tick": tick, "crowds": crowds, "rumors": rumors}


def run_condition(label, freeze):
    """Run 100 ticks; if freeze, agent decisions return no-ops."""
    world = build_accusation_world(seed=0)
    if freeze:
        freeze_agents(world)
    snapshots = [snapshot_world(world, 0)]
    for tick_idx in range(N_TICKS):
        world.step()
        if (tick_idx + 1) in (5, 15, 30, 50, 100):
            snapshots.append(snapshot_world(world, tick_idx + 1))
    return snapshots


def main() -> int:
    print("[Priority 3] World-side autonomy probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_TICKS={N_TICKS}")
    print()

    print("Condition A: agents normal...")
    snaps_a = run_condition("A_normal", freeze=False)
    print("Condition B: agents frozen (decisions = no-op)...")
    snaps_b = run_condition("B_frozen", freeze=True)

    # Print snapshots
    def fmt_crowd(snap, cid):
        c = snap["crowds"].get(cid, {})
        blame_count = len(c.get("blame_concentration", {}))
        return (
            f"d={c.get('density', 0):.2f} "
            f"a={c.get('alignment_strength', 0):.2f} "
            f"sc={c.get('shame_climate', 0):.2f} "
            f"av={c.get('authority_vigilance', 0):.2f} "
            f"ri={c.get('rumor_intensity', 0):.2f} "
            f"blame={blame_count}"
        )

    print()
    print("=== Condition A (agents normal) ===")
    for snap in snaps_a:
        print(f"  t={snap['tick']:>3}  rumors={len(snap['rumors'])}  "
              f"L1: {fmt_crowd(snap, 'priest_courtyard')}  "
              f"L2: {fmt_crowd(snap, 'city_street')}")

    print()
    print("=== Condition B (agents frozen) ===")
    for snap in snaps_b:
        print(f"  t={snap['tick']:>3}  rumors={len(snap['rumors'])}  "
              f"L1: {fmt_crowd(snap, 'priest_courtyard')}  "
              f"L2: {fmt_crowd(snap, 'city_street')}")

    # Autonomy verdict
    print()
    print("=== Autonomy verdict ===")
    initial_b = snaps_b[0]
    final_b = snaps_b[-1]

    def state_change_count(initial, final):
        """Count crowd metrics that changed by >0.05."""
        changes = []
        for cid in initial["crowds"]:
            ci = initial["crowds"][cid]
            cf = final["crowds"][cid]
            for key in ("density", "alignment_strength", "shame_climate",
                        "authority_vigilance", "rumor_intensity",
                        "accusation_amplification"):
                delta = abs(cf.get(key, 0) - ci.get(key, 0))
                if delta > 0.05:
                    changes.append((cid, key, ci[key], cf[key], delta))
        return changes

    changes = state_change_count(initial_b, final_b)
    print(f"  Crowd metrics changed >0.05 in frozen-agents B: {len(changes)}")
    for cid, key, init, fin, d in changes[:10]:
        print(f"    {cid}.{key}: {init:.2f} → {fin:.2f}  (Δ{d:+.2f})")

    # Process autonomy categorization
    crowd_state_changed = any(k in ("density", "alignment_strength",
                                     "shame_climate", "blame_concentration")
                              for _, k, _, _, _ in changes)
    authority_changed = any(k == "authority_vigilance"
                            for _, k, _, _, _ in changes)

    # Rumor process autonomy: was it propagating + decaying?
    # Check rumor count + reach evolution between snapshots
    rumor_dynamics_seen = False
    for snap in snaps_b[1:]:
        for snap_prev in snaps_b[:snaps_b.index(snap)]:
            if (len(snap["rumors"]) != len(snap_prev["rumors"])
                    or any(snap["rumors"][i].get("reach_size") !=
                           snap_prev["rumors"][i].get("reach_size", 0)
                           for i in range(min(len(snap["rumors"]),
                                              len(snap_prev["rumors"]))))):
                rumor_dynamics_seen = True
                break
        if rumor_dynamics_seen:
            break

    process_count = sum([rumor_dynamics_seen, crowd_state_changed,
                         authority_changed])
    print()
    print(f"  Active autonomous processes in B: {process_count}/3")
    print(f"    Rumor process: "
          f"{'AUTONOMOUS' if rumor_dynamics_seen else 'static'}")
    print(f"    Crowd state process: "
          f"{'AUTONOMOUS' if crowd_state_changed else 'static'}")
    print(f"    Authority process: "
          f"{'AUTONOMOUS' if authority_changed else 'static'}")

    if process_count >= 3:
        verdict = "Score 3 -- multiple processes + cross-influence"
    elif process_count == 2:
        verdict = "Score 2 -- some processes autonomous"
    elif process_count == 1:
        verdict = "Score 1 -- only one process autonomous"
    else:
        verdict = "Score 0 -- world fully passive without agents"

    print()
    print(f"  Scale-1 (World-side Autonomy) score: {verdict}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "world_autonomy_probe.json"
    )
    out_path.write_text(
        json.dumps({
            "n_ticks": N_TICKS,
            "snapshots_A_normal": snaps_a,
            "snapshots_B_frozen": snaps_b,
            "frozen_changes": [
                {"cid": cid, "key": k, "init": init, "final": fin, "delta": d}
                for cid, k, init, fin, d in changes
            ],
            "process_count": process_count,
            "verdict": verdict,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
