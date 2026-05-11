"""Generate scarcity depth variations (Branch C S2 fourth execution slice).

Per BRANCH_C_S2_DESIGN_PLAN.md: scarcity scenario only, baseline cast (n=12),
baseline placement, 200 ticks. Vary (event_count x crowd_density) = 9 probes.

Engine touch=NO. Generator-level seed_events list + CrowdState density variation.

Hypothesis: scarcity SATURATION robustness depends on event count + crowd density.
Open: which dimension dominates?

Output: docs/b_direction/readability_probes_scarcity_depth/P_S2_{n}.txt
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

from scripts.b_direction.generate_readability_probes import (
    N_TICKS, anonymize_role,
)
from scripts.b_direction.run_scarcity_scene import (
    build_scarcity_cast, build_locations as sc_locs, build_network as sc_net,
)
from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorldConfig, MicroWorld


# ============================================================
# Variants: 3 event counts x 3 crowd densities = 9 probes
# ============================================================

EVENT_COUNTS = {
    "single":  [{"tick": 5, "event_id": "public_accusation",
                 "target_role": "merchant", "location": "marketplace"}],
    "double":  [
        {"tick": 5, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
        {"tick": 40, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
    ],
    "triple":  [
        {"tick": 5, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
        {"tick": 40, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
        {"tick": 100, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
    ],
}

CROWD_DENSITIES = {
    "low":      {"marketplace": 0.3, "poor_quarter": 0.2},
    "baseline": {"marketplace": 0.7, "poor_quarter": 0.5},
    "high":     {"marketplace": 0.9, "poor_quarter": 0.8},
}

BASELINE_PLACEMENTS = {
    "agent_01": "granary", "agent_02": "poor_quarter",
    "agent_03": "marketplace", "agent_04": "poor_quarter",
    "agent_05": "marketplace", "agent_06": "granary",
    "agent_07": "granary", "agent_08": "marketplace",
    "agent_09": "marketplace", "agent_10": "poor_quarter",
    "agent_11": "poor_quarter", "agent_12": "granary",
}


def build_scarcity_depth_world(seed, event_count, crowd_density):
    agents = build_scarcity_cast()
    aids = [a.agent_id for a in agents]
    seed_events = list(EVENT_COUNTS[event_count])
    seed_events.append({"tick": 15, "event_id": "guard_approaches", "location": "marketplace"})
    densities = CROWD_DENSITIES[crowd_density]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sc_locs(),
        initial_placements=BASELINE_PLACEMENTS,
        crowd_instances={
            "marketplace": CrowdState(crowd_id="marketplace", density=densities["marketplace"]),
            "poor_quarter": CrowdState(crowd_id="poor_quarter", density=densities["poor_quarter"]),
        },
        social_network=sc_net(aids),
        seed_events=seed_events,
        seed_rumors=[{
            "content_tag": "misdeed", "target_role": "merchant",
            "origin_source": "agent_09",
            "initial_reach": ["agent_09", "agent_10"],
            "intensity": 0.7, "credibility": 0.6,
        }],
        seed=seed,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def make_annotated_scarcity_depth(probe_label, event_count, crowd_density, seed=0):
    w = build_scarcity_depth_world(seed=seed, event_count=event_count, crowd_density=crowd_density)
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
    crowd_pub_susp = []
    crowd_auth_vig = []
    blame_per_target_per_tick = []

    for tick in range(N_TICKS):
        result = w.step()
        for aid, a in w._agents.items():
            per_shame[aid].append(a.state.get("shame", {}).get("public_group", 0.0))
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
        crowd_blame_total.append(sum(sum(c.blame_concentration.values()) for c in w._crowds.values()))
        crowd_pub_susp.append(sum(c.public_suspicion for c in w._crowds.values()))
        crowd_auth_vig.append(sum(c.authority_vigilance for c in w._crowds.values()))
        per_target_now = defaultdict(float)
        for c in w._crowds.values():
            for target, val in c.blame_concentration.items():
                per_target_now[target] += val
        blame_per_target_per_tick.append(dict(per_target_now))

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
            arc = f"recovery: peak~{peak:.1f} -> final~{final_mean:.1f}"
            arc_type = "recovery"
        elif final_mean >= 7:
            arc = f"saturation: peak~{peak:.1f} -> final~{final_mean:.1f} (stuck)"
            arc_type = "saturation"
        else:
            arc = f"partial: peak~{peak:.1f} -> final~{final_mean:.1f}"
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
    is_scarcity_context = bool(cast_roles & scarcity_roles) and bool(location_ids & scarcity_locations)

    if final_summary == "LOW_ACTIVITY":
        primary_pressure = "none_clear"
    elif len(sacred_events) >= 2 or awe_max >= 5.0:
        primary_pressure = "sacred"
    elif is_scarcity_context:
        primary_pressure = "scarcity"
    elif len(accusations) >= 1:
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

    pressure_lines = [
        f"    Accusations:      {len(accusations)} fired ({event_count} variant)",
        f"    Recovery actions: {len(confessions)} confessions, {forgiveness_count} forgiveness rumors emitted",
    ]

    blame_max = max(crowd_blame_total) if crowd_blame_total else 0
    blame_max_t = crowd_blame_total.index(blame_max) + 1 if blame_max > 0 else 0
    blame_final = crowd_blame_total[-1] if crowd_blame_total else 0
    blame_line = (
        "    Crowd blame total:   negligible (peak < 0.1)"
        if blame_max < 0.1 else
        f"    Crowd blame total:   peak {blame_max:.1f} at t={blame_max_t} -> final {blame_final:.1f}"
    )

    susp_max = max(crowd_pub_susp) if crowd_pub_susp else 0
    susp_final = crowd_pub_susp[-1] if crowd_pub_susp else 0
    auth_max = max(crowd_auth_vig) if crowd_auth_vig else 0
    auth_final = crowd_auth_vig[-1] if crowd_auth_vig else 0

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

    world_lines = []
    world_lines.append(
        "    Public suspicion:    negligible (peak < 0.05)" if susp_max < 0.05
        else f"    Public suspicion:    peak {susp_max:.2f} -> final {susp_final:.2f}"
    )
    world_lines.append(
        "    Authority vigilance: negligible (peak < 0.05)" if auth_max < 0.05
        else f"    Authority vigilance: peak {auth_max:.2f} -> final {auth_final:.2f}"
    )
    if top_blame_role and top_blame_peak >= 0.3:
        world_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f})")
    elif top_blame_role and top_blame_peak >= 0.05:
        world_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f}, weak)")
    else:
        world_lines.append("    Top blame target:    none (peak < 0.05)")

    headline = [
        f"=== PROBE {probe_label} (scarcity depth: {event_count}-events/{crowd_density}-density, v4) ===",
        "",
        "[Annotated headline summary]",
        f"  Final summary:    {final_summary}",
        f"  Primary pressure: {primary_pressure}",
    ]
    if failure_mode is not None:
        headline.append(f"  Failure mode:     {failure_mode}")
    headline.append(f"  Event count:      {len(accusations)} accusations + 1 guard")
    headline.append(f"  Crowd density:    marketplace={CROWD_DENSITIES[crowd_density]['marketplace']}, poor_quarter={CROWD_DENSITIES[crowd_density]['poor_quarter']}")
    headline.append("")
    headline.append("  Cohort outcomes:")
    lines = headline + cohort_summary_lines + [
        "",
        "  Pressure events + recovery actions:",
        *pressure_lines,
        "",
        "  World-level dynamics:",
        blame_line,
        *world_lines,
        "",
        "=" * 60,
        "",
        "Agents: " + ", ".join(
            f"{agent_map[aid]}={anonymize_role(w._agents[aid].role_id)}"
            for aid in aids[:12]
        ),
        f"Locations: {', '.join(sorted(location_anon.values()))}",
        "",
        f"Scarcity depth variant: {event_count}-events / {crowd_density}-density",
        "",
    ]

    return "\n".join(lines), final_summary, primary_pressure, failure_mode


def main():
    out_dir = ROOT / "docs" / "b_direction" / "readability_probes_scarcity_depth"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    n = 0
    for event_count in ["single", "double", "triple"]:
        for crowd_density in ["low", "baseline", "high"]:
            n += 1
            label = f"P_S2_{n:02d}"
            text, fs, pp, fm = make_annotated_scarcity_depth(label, event_count, crowd_density)
            (out_dir / f"{label}.txt").write_text(text, encoding="utf-8")
            summary.append((label, event_count, crowd_density, fs, pp, fm or "-"))
            print(f"  {label}: {event_count}/{crowd_density} -> {fs} / {pp} / {fm or '-'}")

    print(f"\nWrote {n} scarcity depth probes to {out_dir}")
    print("\n=== Summary ===")
    print(f"{'Label':<10} {'Events':<8} {'Density':<10} {'Final summary':<22} {'Pressure':<12} Failure")
    for row in summary:
        print(f"{row[0]:<10} {row[1]:<8} {row[2]:<10} {row[3]:<22} {row[4]:<12} {row[5]}")


if __name__ == "__main__":
    main()
