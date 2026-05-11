"""Iter 166: Generate annotated probe set for all 12 probes.

Per directive §6 improvement 5 (readability-facing representation):
extend Iter 163 annotated prototype to all 12 probes.

These supplement original P1.txt-P12.txt (preserved as blind eval
materials per Iter 163 Option C). Annotated versions go to
P1_ANNOTATED.txt-P12_ANNOTATED.txt for Lee's reference / case
study use.

This script imports build_world from generate_readability_probes
to ensure same scenarios as original blind eval.
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

# Import the same build_world + ground truth from main probe generator
from scripts.b_direction.generate_readability_probes import (
    PROBES_GROUND_TRUTH, N_TICKS, build_world,
    ANONYMIZED_ROLE_MAP, anonymize_role,
)

OUT_DIR = ROOT / "docs" / "b_direction" / "readability_probes"


def get_cohort_groups(w):
    """Group agents by location for per-cohort summary."""
    groups = defaultdict(list)
    for aid in w._agents:
        loc = w._spatial.where(aid)
        groups[loc].append(aid)
    return dict(groups)


def make_annotated_probe(probe_id, scenario, seed, variant, config):
    w = build_world(scenario, seed, config["p2a"], config["sham_mul"])
    aids = list(w._agents.keys())
    agent_map = {aid: f"A{i+1}" for i, aid in enumerate(aids)}
    location_anon = {}
    for i, loc_id in enumerate(w._spatial._locations.keys()):
        location_anon[loc_id] = f"L{i+1}"

    # Cohort groups by initial location
    cohort_groups = defaultdict(list)
    for aid in aids:
        loc = w._spatial.where(aid)
        cohort_groups[loc].append(aid)

    # Trace per-tick
    per_shame = defaultdict(list)
    per_awe = defaultdict(list)  # v2: track awe for sacred/awe pressure detect
    confessions = []
    forgiveness_count = 0
    accusations = []
    sacred_events = []  # v2: prayer_invitation + miracle_witnessed
    scarcity_events = []  # v2: scarcity-related event ids
    crowd_blame_total = []
    crowd_public_suspicion_total = []  # v3: aggregate public_suspicion across crowds
    crowd_authority_vigilance_total = []  # v3: aggregate authority_vigilance across crowds
    blame_per_target_per_tick = []  # v4: list of dict {target_role: total_blame}

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
                accusations.append(
                    (tick + 1, ev.get("target_role", "?"), ev.get("location", "?")))
            elif eid in ("prayer_invitation", "miracle_witnessed"):
                sacred_events.append((tick + 1, eid))
            elif eid in ("scarcity_strain", "scarcity_pressure", "resource_shortage"):
                scarcity_events.append((tick + 1, eid))
        total_blame = sum(
            sum(c.blame_concentration.values())
            for c in w._crowds.values())
        crowd_blame_total.append(total_blame)
        # v3: world-side dynamics (per Q3b world-side gap finding)
        total_pub_suspicion = sum(c.public_suspicion for c in w._crowds.values())
        total_auth_vigilance = sum(c.authority_vigilance for c in w._crowds.values())
        crowd_public_suspicion_total.append(total_pub_suspicion)
        crowd_authority_vigilance_total.append(total_auth_vigilance)
        # v4: per-target blame (Q3b interpersonal axis)
        per_target_now = defaultdict(float)
        for c in w._crowds.values():
            for target, val in c.blame_concentration.items():
                per_target_now[target] += val
        blame_per_target_per_tick.append(dict(per_target_now))

    # Build cohort summary
    cohort_summary_lines = []
    cohort_arc_types: list[str] = []  # Iter 187: track arc types for final summary
    for loc, members in sorted(cohort_groups.items()):
        peaks = [max(per_shame[a]) for a in members if per_shame[a]]
        finals = [per_shame[a][-1] for a in members if per_shame[a]]
        if not peaks:
            continue
        peak = max(peaks)
        final_mean = sum(finals) / len(finals)
        if peak < 1.5:
            arc = "no shame accumulation"
            arc_type = "no_shame"
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

    # Iter 187: final summary rollup of cohort arc types
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

    # v2 (LOOP 28, post-pilot blind): empirically detect primary pressure
    # to address Q2a-typing gap = 0 pp finding (P-A+C decision).
    # v2.1 (LOOP 32): scarcity detection enhanced via cast/location multi-signal.
    #   Finding: scarcity scenario uses public_accusation events (same as accusation
    #   scenario), but distinctive cast (merchant/fisher_laborer/beggar) + locations
    #   (granary/marketplace/poor_quarter).
    awe_max = max((max(per_awe[a]) for a in per_awe if per_awe[a]), default=0.0)
    # Cast/location signature for scarcity scenario
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
    elif len(scarcity_events) >= 2 or is_scarcity_context:
        primary_pressure = "scarcity"
    elif len(accusations) >= 2:
        primary_pressure = "accusation"
    elif len(accusations) == 1:
        primary_pressure = "accusation"  # weak signal
    else:
        primary_pressure = "mixed"

    # v2: empirically detect failure mode (only for SATURATION_DOMINATED)
    # Rule per ANNOTATED_PROBE_FORMAT v1.4-spec §8.2.
    failure_mode: str | None = None
    if final_summary == "SATURATION_DOMINATED":
        # Compute peaks/finals at probe level
        all_peaks = [max(per_shame[a]) for a in per_shame if per_shame[a]]
        all_finals = [per_shame[a][-1] for a in per_shame if per_shame[a]]
        probe_peak = max(all_peaks) if all_peaks else 0
        probe_final_max = max(all_finals) if all_finals else 0
        blame_max_v = max(crowd_blame_total) if crowd_blame_total else 0
        blame_final_v = crowd_blame_total[-1] if crowd_blame_total else 0
        # Precedence: shame_cap > no_forgiveness_uptake > crowd_blame_persists > shame_decay_absent
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

    # Pressure events summary
    accusation_targets = sorted(set(a[1] for a in accusations)) if accusations else []
    pressure_lines = [
        f"    Accusations: {len(accusations)} fired"
        + (f" (targets: {', '.join(accusation_targets)})" if accusation_targets else " (none)")
    ]
    pressure_lines.append(
        f"    Recovery actions: {len(confessions)} confessions, "
        f"{forgiveness_count} forgiveness rumors emitted")

    # Crowd-level blame trajectory
    blame_max = max(crowd_blame_total) if crowd_blame_total else 0
    blame_max_t = crowd_blame_total.index(blame_max) + 1 if blame_max > 0 else 0
    blame_final = crowd_blame_total[-1] if crowd_blame_total else 0
    if blame_max < 0.1:
        blame_line = "    Crowd blame total:   negligible (peak < 0.1)"
    else:
        blame_line = (
            f"    Crowd blame total:   peak {blame_max:.1f} at t={blame_max_t} → "
            f"final {blame_final:.1f}")

    # v4: top blame target (Q3b interpersonal axis)
    # Find target with highest peak across all ticks
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

    # v3: world-side dynamics (Q3b world-side gap address)
    susp_max = max(crowd_public_suspicion_total) if crowd_public_suspicion_total else 0
    susp_final = crowd_public_suspicion_total[-1] if crowd_public_suspicion_total else 0
    auth_max = max(crowd_authority_vigilance_total) if crowd_authority_vigilance_total else 0
    auth_final = crowd_authority_vigilance_total[-1] if crowd_authority_vigilance_total else 0
    world_side_lines = []
    if susp_max < 0.05:
        world_side_lines.append("    Public suspicion:    negligible (peak < 0.05)")
    else:
        world_side_lines.append(
            f"    Public suspicion:    peak {susp_max:.2f} → final {susp_final:.2f}")
    if auth_max < 0.05:
        world_side_lines.append("    Authority vigilance: negligible (peak < 0.05)")
    else:
        world_side_lines.append(
            f"    Authority vigilance: peak {auth_max:.2f} → final {auth_final:.2f}")

    # Assemble (v4: + top blame target for Q3b interpersonal axis)
    headline_lines = [
        f"=== PROBE {probe_id} (annotated supplement, v4) ===",
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
    # v4: Top blame target (Q3b interpersonal axis)
    if top_blame_role and top_blame_peak >= 0.3:
        lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f})")
    elif top_blame_role and top_blame_peak >= 0.05:
        lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f}, weak)")
    else:
        lines.append("    Top blame target:    none (peak < 0.05)")
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
    lines.append("--- Event log (grouped by 50-tick windows) ---")

    # Iter 185: cap disclosure — evaluator가 정보 누락을 인지할 수 있도록
    confess_total = len(confessions)
    confess_cap = 30
    if confess_total > confess_cap:
        lines.append(
            f"  (showing first {confess_cap} of {confess_total} confessions; "
            f"total in headline)"
        )

    # Window-grouped event log
    event_windows = defaultdict(list)
    for tick, target, loc in accusations:
        window = tick // 50
        event_windows[window].append(
            (tick, f"  t={tick:>3}  accusation against {target}"))
    for tick, aid, role in confessions[:confess_cap]:
        window = tick // 50
        event_windows[window].append(
            (tick, f"  t={tick:>3}  confession by {agent_map.get(aid, aid)} ({anonymize_role(role)})"))

    for window in sorted(event_windows.keys()):
        lines.append(f"  --- Tick {window*50}-{(window+1)*50-1} ---")
        for _, ev_str in sorted(event_windows[window]):
            lines.append(ev_str)

    return "\n".join(lines)


def main() -> int:
    print(f"[Iter 166] Generating 12 annotated probes")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Use same probe order as main generator (deterministic shuffle)
    import random
    probe_order = list(range(12))
    rng = random.Random(42)
    rng.shuffle(probe_order)

    for display_i, gt_i in enumerate(probe_order):
        probe_id = f"P{display_i + 1}_ANNOTATED"
        scenario, seed, variant, config = PROBES_GROUND_TRUTH[gt_i]
        print(f"  Generating {probe_id}: {scenario} seed={seed} variant={variant}")
        annotated = make_annotated_probe(probe_id, scenario, seed, variant, config)
        out = OUT_DIR / f"{probe_id}.txt"
        out.write_text(annotated, encoding="utf-8")

    print(f"\n  Wrote 12 annotated probes to {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
