"""Generate placement variation probes (Branch C S5 first execution slice).

Per BRANCH_C_DESIGN_DRAFT.md §3.1: S5 (placement variation) is the safest
first slice — engine touch=NO, mechanical, immediate Q3b world-side measurement.

Reuses build_world from generate_readability_probes.py for cast/locations,
but overrides initial_placements per variant. Annotated v3 fields surface
how placement affects world-side observables.

Output: docs/b_direction/readability_probes_placement/P_PV_{n}_ANNOTATED.txt

Variants (9 total, 3 per scenario):
  accusation: original / inverted / clustered
  scarcity:   original / inverted / clustered
  sacred:     original / inverted / clustered
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

from scripts.b_direction.generate_readability_probes import (
    N_TICKS, ANONYMIZED_ROLE_MAP, anonymize_role,
)
from scripts.b_direction.run_accusation_scene import (
    build_accusation_cast, build_locations as acc_locs, build_social_network as acc_net,
)
from scripts.b_direction.run_scarcity_scene import (
    build_scarcity_cast, build_locations as sc_locs, build_network as sc_net,
)
from scripts.b_direction.run_sacred_gathering import (
    build_cast as sacred_cast, build_locations as sa_locs, build_network as sa_net,
)
from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorldConfig, MicroWorld


# ============================================================
# Placement variants per scenario
# ============================================================

ACCUSATION_PLACEMENTS = {
    "original": {
        "agent_01": "upper_room", "agent_02": "upper_room",
        "agent_03": "upper_room", "agent_04": "priest_courtyard",
        "agent_05": "priest_courtyard", "agent_06": "city_street",
        "agent_07": "city_street", "agent_08": "city_street",
        "agent_09": "upper_room", "agent_10": "city_street",
    },
    "inverted": {
        # Swap upper_room <-> city_street groupings
        "agent_01": "city_street", "agent_02": "city_street",
        "agent_03": "city_street", "agent_04": "priest_courtyard",
        "agent_05": "priest_courtyard", "agent_06": "upper_room",
        "agent_07": "upper_room", "agent_08": "upper_room",
        "agent_09": "city_street", "agent_10": "upper_room",
    },
    "clustered": {
        # Pack everyone into priest_courtyard (high authority_reach location)
        "agent_01": "priest_courtyard", "agent_02": "priest_courtyard",
        "agent_03": "priest_courtyard", "agent_04": "priest_courtyard",
        "agent_05": "priest_courtyard", "agent_06": "priest_courtyard",
        "agent_07": "priest_courtyard", "agent_08": "city_street",
        "agent_09": "priest_courtyard", "agent_10": "city_street",
    },
}

SCARCITY_PLACEMENTS = {
    "original": {
        "agent_01": "granary", "agent_02": "poor_quarter",
        "agent_03": "marketplace", "agent_04": "poor_quarter",
        "agent_05": "marketplace", "agent_06": "granary",
        "agent_07": "granary", "agent_08": "marketplace",
        "agent_09": "marketplace", "agent_10": "poor_quarter",
        "agent_11": "poor_quarter", "agent_12": "granary",
    },
    "inverted": {
        # Swap granary <-> poor_quarter
        "agent_01": "poor_quarter", "agent_02": "granary",
        "agent_03": "marketplace", "agent_04": "granary",
        "agent_05": "marketplace", "agent_06": "poor_quarter",
        "agent_07": "poor_quarter", "agent_08": "marketplace",
        "agent_09": "marketplace", "agent_10": "granary",
        "agent_11": "granary", "agent_12": "poor_quarter",
    },
    "clustered": {
        # Concentrate in marketplace (where accusation hits)
        "agent_01": "marketplace", "agent_02": "marketplace",
        "agent_03": "marketplace", "agent_04": "marketplace",
        "agent_05": "marketplace", "agent_06": "marketplace",
        "agent_07": "granary", "agent_08": "marketplace",
        "agent_09": "marketplace", "agent_10": "poor_quarter",
        "agent_11": "marketplace", "agent_12": "granary",
    },
}

SACRED_PLACEMENTS = {
    "original": {
        "agent_01": "temple_outer_court", "agent_02": "temple_inner",
        "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
        "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
        "agent_07": "city_street", "agent_08": "city_street",
    },
    "inverted": {
        # Swap temple <-> city_street
        "agent_01": "city_street", "agent_02": "temple_inner",
        "agent_03": "city_street", "agent_04": "city_street",
        "agent_05": "city_street", "agent_06": "city_street",
        "agent_07": "temple_outer_court", "agent_08": "temple_outer_court",
    },
    "clustered": {
        # All in temple_inner (deepest sacred)
        "agent_01": "temple_inner", "agent_02": "temple_inner",
        "agent_03": "temple_inner", "agent_04": "temple_inner",
        "agent_05": "temple_inner", "agent_06": "temple_inner",
        "agent_07": "city_street", "agent_08": "temple_inner",
    },
}


def build_accusation_world(seed, p2a, sham_mul, placements):
    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=acc_locs(),
        initial_placements=placements,
        crowd_instances={
            "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
            "city_street": CrowdState(crowd_id="city_street", density=0.6),
        },
        social_network=acc_net(aids),
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
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
        forgiveness_phase_enabled=p2a,
        forgiveness_agent_shame_multiplier=sham_mul,
    ))


def build_scarcity_world(seed, p2a, sham_mul, placements):
    agents = build_scarcity_cast()
    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sc_locs(),
        initial_placements=placements,
        crowd_instances={
            "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
            "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
        },
        social_network=sc_net(aids),
        seed_events=[
            {"tick": 5, "event_id": "public_accusation",
             "target_role": "merchant", "location": "marketplace"},
            {"tick": 15, "event_id": "guard_approaches", "location": "marketplace"},
        ],
        seed_rumors=[{
            "content_tag": "misdeed", "target_role": "merchant",
            "origin_source": "agent_09",
            "initial_reach": ["agent_09", "agent_10"],
            "intensity": 0.7, "credibility": 0.6,
        }],
        seed=seed,
        forgiveness_phase_enabled=p2a,
        forgiveness_agent_shame_multiplier=sham_mul,
    ))


def build_sacred_world(seed, p2a, sham_mul, placements):
    agents = sacred_cast()
    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sa_locs(),
        initial_placements=placements,
        crowd_instances={
            "temple_outer_court": CrowdState(
                crowd_id="temple_outer_court", density=0.6,
                dominant_emotion="awe",
            ),
            "city_street": CrowdState(crowd_id="city_street", density=0.3),
        },
        social_network=sa_net(aids),
        seed_events=[
            {"tick": 10, "event_id": "prayer_invitation",
             "location": "temple_outer_court"},
            {"tick": 30, "event_id": "miracle_witnessed",
             "location": "temple_outer_court"},
            {"tick": 50, "event_id": "public_accusation",
             "target_role": "spiritual_wanderer", "location": "city_street"},
            {"tick": 250, "event_id": "miracle_witnessed",
             "location": "temple_outer_court"},
        ],
        seed_rumors=[{
            "content_tag": "miracle_news",
            "target_role": "spiritual_wanderer",
            "origin_source": "agent_01",
            "initial_reach": ["agent_01", "agent_02"],
            "intensity": 0.6, "credibility": 0.7,
        }],
        seed=seed,
        forgiveness_phase_enabled=p2a,
        forgiveness_agent_shame_multiplier=sham_mul,
    ))


SCENARIO_BUILDERS = {
    "accusation": (build_accusation_world, ACCUSATION_PLACEMENTS),
    "scarcity": (build_scarcity_world, SCARCITY_PLACEMENTS),
    "sacred": (build_sacred_world, SACRED_PLACEMENTS),
}


# ============================================================
# Annotated probe generation (reuses logic from generate_annotated_probes_all)
# ============================================================

def make_annotated_placement(probe_label, scenario, variant, seed=0):
    builder, placements_dict = SCENARIO_BUILDERS[scenario]
    placements = placements_dict[variant]
    w = builder(seed=seed, p2a=True, sham_mul=None, placements=placements)

    aids = list(w._agents.keys())
    agent_map = {aid: f"A{i+1}" for i, aid in enumerate(aids)}
    location_anon = {}
    for i, loc_id in enumerate(w._spatial._locations.keys()):
        location_anon[loc_id] = f"L{i+1}"

    cohort_groups = defaultdict(list)
    for aid in aids:
        loc = w._spatial.where(aid)
        cohort_groups[loc].append(aid)

    per_shame = defaultdict(list)
    per_awe = defaultdict(list)
    confessions = []
    forgiveness_count = 0
    accusations = []
    sacred_events = []
    crowd_blame_total = []
    crowd_public_suspicion_total = []
    crowd_authority_vigilance_total = []
    blame_per_target_per_tick = []  # v4

    for tick in range(N_TICKS):
        result = w.step()
        for aid, a in w._agents.items():
            per_shame[aid].append(
                a.state.get("shame", {}).get("public_group", 0.0))
            per_awe[aid].append(a.state.get("awe", 0.0))
        for aid, action in result.agent_actions.items():
            if action == "confess":
                confessions.append((tick + 1, aid, w._agents[aid].role_id))
        for ev in result.spawned_events:
            eid = ev.get("event_id")
            if eid == "forgiveness_emitted":
                forgiveness_count += 1
            elif eid == "public_accusation":
                accusations.append((tick + 1, ev.get("target_role", "?"), ev.get("location", "?")))
            elif eid in ("prayer_invitation", "miracle_witnessed"):
                sacred_events.append((tick + 1, eid))
        crowd_blame_total.append(sum(
            sum(c.blame_concentration.values()) for c in w._crowds.values()))
        crowd_public_suspicion_total.append(sum(c.public_suspicion for c in w._crowds.values()))
        crowd_authority_vigilance_total.append(sum(c.authority_vigilance for c in w._crowds.values()))
        # v4 per-target blame
        per_target_now = defaultdict(float)
        for c in w._crowds.values():
            for target, val in c.blame_concentration.items():
                per_target_now[target] += val
        blame_per_target_per_tick.append(dict(per_target_now))

    # cohort summary
    cohort_summary_lines = []
    cohort_arc_types = []
    for loc, members in sorted(cohort_groups.items()):
        peaks = [max(per_shame[a]) for a in members if per_shame[a]]
        finals = [per_shame[a][-1] for a in members if per_shame[a]]
        if not peaks:
            continue
        peak = max(peaks)
        final_mean = sum(finals) / len(finals)
        if peak < 1.5:
            arc, arc_type = "no shame accumulation", "no_shame"
        elif final_mean < 4 and peak >= 5:
            arc = f"recovery: peak~{peak:.1f} → final~{final_mean:.1f}"
            arc_type = "recovery"
        elif final_mean >= 7:
            arc = f"saturation: peak~{peak:.1f} → final~{final_mean:.1f} (stuck)"
            arc_type = "saturation"
        else:
            arc = f"partial: peak~{peak:.1f} → final~{final_mean:.1f}"
            arc_type = "partial"
        cohort_arc_types.append(arc_type)
        cohort_summary_lines.append(
            f"    [{location_anon[loc]} cohort, {len(members)} agents]:  {arc}")

    arcs = set(cohort_arc_types)
    if arcs <= {"no_shame"}:
        final_summary = "LOW_ACTIVITY"
    elif "recovery" in arcs and "saturation" in arcs:
        final_summary = "MIXED"
    elif "saturation" in arcs and "recovery" not in arcs:
        final_summary = "SATURATION_DOMINATED"
    elif "recovery" in arcs and "saturation" not in arcs:
        final_summary = "RECOVERY_DOMINATED"
    else:
        final_summary = "PARTIAL"

    awe_max = max((max(per_awe[a]) for a in per_awe if per_awe[a]), default=0.0)
    scarcity_roles = {"merchant", "fisher_laborer", "beggar", "laborer"}
    scarcity_locations = {"granary", "marketplace", "poor_quarter"}
    cast_roles = {w._agents[aid].role_id for aid in w._agents}
    location_ids = set(w._spatial._locations.keys())
    has_scarcity_cast = bool(cast_roles & scarcity_roles)
    has_scarcity_locations = bool(location_ids & scarcity_locations)
    is_scarcity_context = has_scarcity_cast and has_scarcity_locations

    if final_summary == "LOW_ACTIVITY":
        primary_pressure = "none_clear"
    elif len(sacred_events) >= 2 or awe_max >= 5.0:
        primary_pressure = "sacred"
    elif is_scarcity_context:
        primary_pressure = "scarcity"
    elif len(accusations) >= 2:
        primary_pressure = "accusation"
    elif len(accusations) == 1:
        primary_pressure = "accusation"
    else:
        primary_pressure = "mixed"

    failure_mode = None
    if final_summary == "SATURATION_DOMINATED":
        all_peaks = [max(per_shame[a]) for a in per_shame if per_shame[a]]
        all_finals = [per_shame[a][-1] for a in per_shame if per_shame[a]]
        probe_peak = max(all_peaks) if all_peaks else 0
        probe_final_max = max(all_finals) if all_finals else 0
        blame_max_v = max(crowd_blame_total) if crowd_blame_total else 0
        blame_final_v = crowd_blame_total[-1] if crowd_blame_total else 0
        if probe_peak >= 9.5 and probe_final_max >= 9.5:
            failure_mode = "shame_cap"
        elif forgiveness_count >= 10 and probe_final_max >= 7.0:
            failure_mode = "no_forgiveness_uptake"
        elif blame_max_v >= 1.5 and blame_final_v >= 1.0:
            failure_mode = "crowd_blame_persists"
        elif len(accusations) >= 3:
            failure_mode = "repeat_retrigger"
        else:
            failure_mode = "shame_decay_absent"

    accusation_targets = sorted(set(a[1] for a in accusations)) if accusations else []
    pressure_lines = [
        f"    Accusations: {len(accusations)} fired"
        + (f" (targets: {', '.join(accusation_targets)})" if accusation_targets else " (none)"),
        f"    Recovery actions: {len(confessions)} confessions, {forgiveness_count} forgiveness rumors emitted",
    ]

    blame_max = max(crowd_blame_total) if crowd_blame_total else 0
    blame_max_t = crowd_blame_total.index(blame_max) + 1 if blame_max > 0 else 0
    blame_final = crowd_blame_total[-1] if crowd_blame_total else 0
    blame_line = (
        "    Crowd blame total:   negligible (peak < 0.1)"
        if blame_max < 0.1 else
        f"    Crowd blame total:   peak {blame_max:.1f} at t={blame_max_t} → final {blame_final:.1f}"
    )

    # v4 top blame target
    target_peaks = defaultdict(float)
    for tick_dict in blame_per_target_per_tick:
        for target, val in tick_dict.items():
            if val > target_peaks[target]:
                target_peaks[target] = val
    if target_peaks:
        top_target = max(target_peaks.items(), key=lambda kv: kv[1])
        top_blame_role, top_blame_peak = top_target
    else:
        top_blame_role, top_blame_peak = None, 0.0

    susp_max = max(crowd_public_suspicion_total) if crowd_public_suspicion_total else 0
    susp_final = crowd_public_suspicion_total[-1] if crowd_public_suspicion_total else 0
    auth_max = max(crowd_authority_vigilance_total) if crowd_authority_vigilance_total else 0
    auth_final = crowd_authority_vigilance_total[-1] if crowd_authority_vigilance_total else 0
    world_side_lines = []
    if susp_max < 0.05:
        world_side_lines.append("    Public suspicion:    negligible (peak < 0.05)")
    else:
        world_side_lines.append(f"    Public suspicion:    peak {susp_max:.2f} → final {susp_final:.2f}")
    if auth_max < 0.05:
        world_side_lines.append("    Authority vigilance: negligible (peak < 0.05)")
    else:
        world_side_lines.append(f"    Authority vigilance: peak {auth_max:.2f} → final {auth_final:.2f}")
    if top_blame_role and top_blame_peak >= 0.3:
        world_side_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f})")
    elif top_blame_role and top_blame_peak >= 0.05:
        world_side_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f}, weak)")
    else:
        world_side_lines.append("    Top blame target:    none (peak < 0.05)")

    headline_lines = [
        f"=== PROBE {probe_label} (placement variant: {scenario}/{variant}, v4) ===",
        "",
        "[Annotated headline summary]",
        f"  Final summary:    {final_summary}",
        f"  Primary pressure: {primary_pressure}",
    ]
    if failure_mode is not None:
        headline_lines.append(f"  Failure mode:     {failure_mode}")
    headline_lines.append("")
    headline_lines.append("  Cohort outcomes:")
    lines = headline_lines
    lines.extend(cohort_summary_lines)
    lines.append("")
    lines.append("  Pressure events + recovery actions:")
    lines.extend(pressure_lines)
    lines.append("")
    lines.append("  World-level dynamics:")
    lines.append(blame_line)
    lines.extend(world_side_lines)
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Agents: " + ", ".join(
        f"{agent_map[aid]}={anonymize_role(w._agents[aid].role_id)}"
        for aid in aids[:12]
    ))
    lines.append(f"Locations: {', '.join(sorted(location_anon.values()))}")
    lines.append("")
    lines.append("Placement variant: " + variant)
    lines.append("")

    return "\n".join(lines), final_summary, primary_pressure, failure_mode


def main():
    out_dir = ROOT / "docs" / "b_direction" / "readability_probes_placement"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    n = 0
    for scenario in ["accusation", "scarcity", "sacred"]:
        for variant in ["original", "inverted", "clustered"]:
            n += 1
            label = f"P_PV_{n:02d}"
            text, fs, pp, fm = make_annotated_placement(label, scenario, variant, seed=0)
            (out_dir / f"{label}.txt").write_text(text, encoding="utf-8")
            summary.append((label, scenario, variant, fs, pp, fm or "-"))
            print(f"  {label}: {scenario}/{variant} -> {fs} / {pp} / {fm or '-'}")

    print(f"\nWrote {n} placement variation probes to {out_dir}")
    print("\n=== Summary ===")
    print(f"{'Label':<10} {'Scenario':<12} {'Variant':<12} {'Final summary':<22} {'Pressure':<12} Failure")
    for row in summary:
        print(f"{row[0]:<10} {row[1]:<12} {row[2]:<12} {row[3]:<22} {row[4]:<12} {row[5]}")


if __name__ == "__main__":
    main()
