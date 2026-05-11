"""Iter 163: Prototype annotated probe formatter.

Per WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md §6
improvement point 5: improve probe readability via:
- dominant pressure summary
- cohort delta / relation delta highlighting
- event grouping
- compact summary of key shifts

This script generates ONE annotated probe (e.g., for accusation
scenario seed=0) as a prototype. If Lee approves, similar
annotation can be applied to all 12 probes via
`generate_readability_probes.py` modification.

Output: `docs/b_direction/readability_probes/P_ANNOTATED_DEMO.txt`
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

N_TICKS = 200


def build_world(seed):
    """Accusation baseline scenario (P10 in current 12-probe set)."""
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
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches",
             "location": "priest_courtyard"},
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


# Anonymization (matches Iter 120)
ANONYMIZED_ROLE_MAP = {
    "disciple_follower": "follower",
    "authority_priest": "authority",
    "soldier_enforcer": "enforcer",
    "crowd_participant": "crowd",
    "family_anchor": "family",
    "outsider": "outsider",
}


def anonymize_role(role_id):
    return ANONYMIZED_ROLE_MAP.get(role_id, role_id)


def make_annotated_probe(seed=0):
    w = build_world(seed)
    aids = list(w._agents.keys())
    agent_map = {aid: f"A{i+1}" for i, aid in enumerate(aids)}

    # Trace per-tick state
    per_shame = defaultdict(list)
    confessions = []  # (tick, agent_id, role)
    forgiveness = []  # (tick, role)
    accusations = []  # (tick, target_role, loc)
    crowd_blame_total = []  # per-tick total blame across all crowds

    for tick in range(N_TICKS):
        result = w.step()
        for aid, a in w._agents.items():
            per_shame[aid].append(
                a.state.get("shame", {}).get("public_group", 0.0))
        for aid, action in result.agent_actions.items():
            if action == "confess":
                confessions.append((tick + 1, aid, w._agents[aid].role_id))
        for ev in result.spawned_events:
            eid = ev.get("event_id")
            if eid == "forgiveness_emitted":
                forgiveness.append(
                    (tick + 1, ev.get("target_role", "?")))
            elif eid == "public_accusation":
                accusations.append(
                    (tick + 1, ev.get("target_role", "?"), ev.get("location", "?")))
        # Crowd blame total
        total_blame = sum(
            sum(c.blame_concentration.values())
            for c in w._crowds.values())
        crowd_blame_total.append(total_blame)

    # ===== HEADLINE SUMMARY =====
    cohort_groups = {
        "priest_courtyard": ["agent_04", "agent_05"],
        "city_street": ["agent_06", "agent_07", "agent_08", "agent_10"],
        "upper_room": ["agent_01", "agent_02", "agent_03", "agent_09"],
    }
    location_anon = {"priest_courtyard": "L1", "city_street": "L2", "upper_room": "L3"}

    cohort_summary = []
    for loc, members in cohort_groups.items():
        # Compute peak and final shame for cohort
        peaks = []
        finals = []
        for aid in members:
            ts = per_shame[aid]
            peaks.append(max(ts) if ts else 0)
            finals.append(ts[-1] if ts else 0)
        peak = max(peaks)
        peak_t = max(range(len(per_shame[members[0]])), key=lambda i: max(per_shame[a][i] for a in members)) + 1
        final_mean = sum(finals) / len(finals)
        if peak < 1.5:
            arc = "no shame accumulation"
        elif final_mean < 4 and peak >= 5:
            arc = f"recovery: peak~{peak:.1f} at t={peak_t} → final~{final_mean:.1f}"
        elif final_mean >= 7:
            arc = f"saturation: peak~{peak:.1f} → final~{final_mean:.1f} (stuck)"
        else:
            arc = f"partial: peak~{peak:.1f} → final~{final_mean:.1f}"
        cohort_summary.append(
            f"    [{location_anon[loc]} cohort]:  {arc}")

    # Pressure events summary
    pressure_summary = []
    if accusations:
        pressure_summary.append(
            f"    Accusations: {len(accusations)} fired ({', '.join(set(a[1] for a in accusations))})")
    pressure_summary.append(
        f"    Recovery actions: {len(confessions)} confessions, "
        f"{len(forgiveness)} forgiveness rumors emitted")

    # Crowd-level blame trajectory
    blame_max = max(crowd_blame_total)
    blame_max_t = crowd_blame_total.index(blame_max) + 1
    blame_final = crowd_blame_total[-1]
    blame_trajectory = (
        f"    Crowd blame total:   peak {blame_max:.1f} at t={blame_max_t} → "
        f"final {blame_final:.1f}")

    # ===== ASSEMBLE =====
    lines = [
        "=== PROBE P_ANNOTATED_DEMO ===",
        "",
        "[Annotated headline summary]",
        "  Cohort outcomes:",
    ]
    lines.extend(cohort_summary)
    lines.append("")
    lines.append("  Pressure events + recovery actions:")
    lines.extend(pressure_summary)
    lines.append("")
    lines.append("  World-level dynamics:")
    lines.append(blame_trajectory)
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Agents: " + ", ".join(
        f"{agent_map[aid]}={anonymize_role(w._agents[aid].role_id)}"
        for aid in aids[:10]
    ))
    lines.append(f"Locations: {', '.join(location_anon.values())}")
    lines.append("")
    lines.append("--- Event log (selected ticks) ---")

    # Group events by 50-tick windows for readability
    event_windows = defaultdict(list)
    for tick, target, loc in accusations:
        window = tick // 50
        event_windows[window].append(
            f"  t={tick:>3}  accusation against {target}")
    for tick, aid, role in confessions[:30]:  # limit display
        window = tick // 50
        event_windows[window].append(
            f"  t={tick:>3}  confession by {agent_map.get(aid, aid)} ({anonymize_role(role)})")

    for window in sorted(event_windows.keys()):
        lines.append(f"  --- Tick {window*50}-{(window+1)*50-1} ---")
        for ev in sorted(event_windows[window], key=lambda x: int(x.split("=")[1].split()[0])):
            lines.append(ev)

    return "\n".join(lines)


def main():
    print(f"[Iter 163] Generating annotated probe prototype")
    annotated = make_annotated_probe(seed=0)
    out_path = (
        ROOT / "docs" / "b_direction" / "readability_probes"
        / "P_ANNOTATED_DEMO.txt"
    )
    out_path.write_text(annotated, encoding="utf-8")
    print(f"  Saved: {out_path.relative_to(ROOT)}")
    print()
    print("=" * 60)
    print(annotated[:1500])  # preview
    print("...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
