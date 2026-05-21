"""Generate sacred event density variations (Branch C S3 third execution slice).

Per BRANCH_C_DESIGN_DRAFT.md §3 S3: sacred depth expansion = awe + miracle
frequency variation. Tests whether miracle event density (count and spacing)
shifts final-summary outcome under fixed cast + baseline placement.

Engine touch=NO. Generator-level seed_events list variation only.

3 miracle counts (1, 3, 5) x 3 spacings (early-burst, even-spread, late-burst)
= 9 probes, all sacred scenario, all 200 ticks, all seed=0, all baseline placement.

Output: docs/b_direction/readability_probes_event_density/P_ED_{n}.txt

Hypothesis: density and spacing affect awe peak + RECOVERY/SATURATION balance
independently of cast/placement (S4/S5 already covered those).
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

from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import MicroWorld, MicroWorldConfig
from scripts.b_direction.generate_readability_probes import (
    N_TICKS,
    anonymize_role,
)
from scripts.b_direction.run_sacred_gathering import (
    build_cast as sacred_cast,
)
from scripts.b_direction.run_sacred_gathering import (
    build_locations as sa_locs,
)
from scripts.b_direction.run_sacred_gathering import (
    build_network as sa_net,
)

# ============================================================
# Miracle timing variants per density level
# ============================================================
#
# Each variant provides a list of miracle ticks within [10, 195] window.
# Density: count of miracle_witnessed events.
# Spacing: early-burst / even-spread / late-burst.
#
MIRACLE_TIMINGS = {
    ("low", "early"):  [10],
    ("low", "even"):   [100],
    ("low", "late"):   [190],
    ("med", "early"):  [10, 30, 60],
    ("med", "even"):   [10, 100, 190],
    ("med", "late"):   [140, 170, 190],
    ("high", "early"): [10, 20, 40, 70, 100],
    ("high", "even"):  [10, 50, 100, 150, 190],
    ("high", "late"):  [90, 120, 150, 170, 190],
}

BASELINE_PLACEMENTS = {
    "agent_01": "temple_outer_court", "agent_02": "temple_inner",
    "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
    "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
    "agent_07": "city_street", "agent_08": "city_street",
}


def build_sacred_density_world(seed, miracle_ticks):
    agents = sacred_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": 5, "event_id": "prayer_invitation",
         "location": "temple_outer_court"},
    ]
    for t in miracle_ticks:
        seed_events.append({
            "tick": t, "event_id": "miracle_witnessed",
            "location": "temple_outer_court",
        })
    # Single accusation midway to introduce shame pressure baseline
    seed_events.append({
        "tick": 50, "event_id": "public_accusation",
        "target_role": "spiritual_wanderer", "location": "city_street",
    })
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=sa_locs(),
        initial_placements=BASELINE_PLACEMENTS,
        crowd_instances={
            "temple_outer_court": CrowdState(
                crowd_id="temple_outer_court", density=0.6,
                dominant_emotion="awe",
            ),
            "city_street": CrowdState(crowd_id="city_street", density=0.3),
        },
        social_network=sa_net(aids),
        seed_events=seed_events,
        seed_rumors=[{
            "content_tag": "miracle_news",
            "target_role": "spiritual_wanderer",
            "origin_source": "agent_01",
            "initial_reach": ["agent_01", "agent_02"],
            "intensity": 0.6, "credibility": 0.7,
        }],
        seed=seed,
        forgiveness_phase_enabled=True,
        forgiveness_agent_shame_multiplier=None,
    ))


def make_annotated_density(probe_label, density, spacing, seed=0):
    miracle_ticks = MIRACLE_TIMINGS[(density, spacing)]
    w = build_sacred_density_world(seed=seed, miracle_ticks=miracle_ticks)
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
    if final_summary == "LOW_ACTIVITY":
        primary_pressure = "none_clear"
    elif len(sacred_events) >= 2 or awe_max >= 5.0:
        primary_pressure = "sacred"
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
        f"    Sacred events:    {len(sacred_events)} fired ({len(miracle_ticks)} miracles, 1 prayer)",
        f"    Accusations:      {len(accusations)} fired",
        f"    Recovery actions: {len(confessions)} confessions, {forgiveness_count} forgiveness rumors emitted",
        f"    Awe peak:         {awe_max:.2f}",
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
        f"=== PROBE {probe_label} (event density: sacred/{density}-density/{spacing}-spacing, v4) ===",
        "",
        "[Annotated headline summary]",
        f"  Final summary:    {final_summary}",
        f"  Primary pressure: {primary_pressure}",
    ]
    if failure_mode is not None:
        headline.append(f"  Failure mode:     {failure_mode}")
    headline.append(f"  Miracle count:    {len(miracle_ticks)} ({density})")
    headline.append(f"  Spacing:          {spacing} (ticks: {miracle_ticks})")
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
        f"Event density variant: {density}-density / {spacing}-spacing",
        "",
    ]

    return "\n".join(lines), final_summary, primary_pressure, failure_mode, awe_max


def main():
    out_dir = ROOT / "docs" / "b_direction" / "readability_probes_event_density"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    n = 0
    for density in ["low", "med", "high"]:
        for spacing in ["early", "even", "late"]:
            n += 1
            label = f"P_ED_{n:02d}"
            text, fs, pp, fm, awe = make_annotated_density(label, density, spacing)
            (out_dir / f"{label}.txt").write_text(text, encoding="utf-8")
            summary.append((label, density, spacing, fs, pp, fm or "-", awe))
            print(f"  {label}: {density}/{spacing} -> {fs} / {pp} / {fm or '-'} (awe={awe:.2f})")

    print(f"\nWrote {n} event density variation probes to {out_dir}")
    print("\n=== Summary ===")
    print(f"{'Label':<10} {'Density':<8} {'Spacing':<8} {'Final summary':<22} {'Pressure':<12} {'Awe':<6} Failure")
    for row in summary:
        print(f"{row[0]:<10} {row[1]:<8} {row[2]:<8} {row[3]:<22} {row[4]:<12} {row[6]:<6.2f} {row[5]}")


if __name__ == "__main__":
    main()
