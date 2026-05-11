"""J-Alpha Step A6 — 5-variation demo generator.

같은 anchor (cast/placement/event 고정) × 5 seeds → 5 annotated probes →
5 한국어 stories. outputs/creative_demo/ 에 묶음 출력.

Per WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md §4.4 Step A6 + §4.3 산출물 A.

Usage:
    python scripts/story/generate_anchor_variations.py
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

from scripts.story.selector import get_curated_anchors, get_variations
from scripts.b_direction.generate_readability_probes import N_TICKS, anonymize_role
from scripts.story.extract_story_features import parse_probe
from scripts.story.build_narrative_ir import build_ir
from scripts.story.render_story_ko import render_summary, render_narrative


# Reuse annotated probe formatting from generate_scarcity_depth_variations etc.
def world_to_annotated_text(world, probe_label: str, anchor_id: str, seed: int) -> str:
    """Run simulation and produce annotated probe text in v4 format."""
    aids = list(world._agents.keys())
    agent_map = {aid: f"A{i+1}" for i, aid in enumerate(aids)}
    location_anon = {}
    for i, loc_id in enumerate(world._spatial._locations.keys()):
        location_anon[loc_id] = f"L{i+1}"

    cohort_groups = defaultdict(list)
    for aid in aids:
        cohort_groups[world._spatial.where(aid)].append(aid)

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
        result = world.step()
        for aid, a in world._agents.items():
            per_shame[aid].append(a.state.get("shame", {}).get("public_group", 0.0))
            per_awe[aid].append(a.state.get("awe", 0.0))
        for aid, action in result.agent_actions.items():
            if action == "confess":
                confessions.append((tick + 1, aid, world._agents[aid].role_id))
        for ev in result.spawned_events:
            eid = ev.get("event_id")
            if eid == "forgiveness_emitted":
                forgiveness_count += 1
            elif eid == "public_accusation":
                accusations.append((tick + 1, ev.get("target_role", "?"), ev.get("location", "?")))
            elif eid in ("prayer_invitation", "miracle_witnessed"):
                sacred_events.append((tick + 1, eid))
        crowd_blame_total.append(sum(sum(c.blame_concentration.values()) for c in world._crowds.values()))
        crowd_pub_susp.append(sum(c.public_suspicion for c in world._crowds.values()))
        crowd_auth_vig.append(sum(c.authority_vigilance for c in world._crowds.values()))
        per_target_now = defaultdict(float)
        for c in world._crowds.values():
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
    cast_roles = {world._agents[aid].role_id for aid in world._agents}
    location_ids = set(world._spatial._locations.keys())
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
    if susp_max < 0.05:
        world_lines.append("    Public suspicion:    negligible (peak < 0.05)")
    else:
        world_lines.append(f"    Public suspicion:    peak {susp_max:.2f} -> final {susp_final:.2f}")
    if auth_max < 0.05:
        world_lines.append("    Authority vigilance: negligible (peak < 0.05)")
    else:
        world_lines.append(f"    Authority vigilance: peak {auth_max:.2f} -> final {auth_final:.2f}")
    if top_blame_role and top_blame_peak >= 0.3:
        world_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f})")
    elif top_blame_role and top_blame_peak >= 0.05:
        world_lines.append(f"    Top blame target:    {top_blame_role} (peak {top_blame_peak:.2f}, weak)")
    else:
        world_lines.append("    Top blame target:    none (peak < 0.05)")

    headline = [
        f"=== PROBE {probe_label} (anchor: {anchor_id}, seed={seed}, v4) ===",
        "",
        "[Annotated headline summary]",
        f"  Final summary:    {final_summary}",
        f"  Primary pressure: {primary_pressure}",
        "",
        "  Cohort outcomes:",
    ]
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
            f"{agent_map[aid]}={anonymize_role(world._agents[aid].role_id)}"
            for aid in aids[:12]
        ),
        f"Locations: {', '.join(sorted(location_anon.values()))}",
        "",
    ]
    return "\n".join(lines), final_summary


def main():
    out_dir = ROOT / "outputs" / "creative_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    anchors = get_curated_anchors()
    for anchor in anchors:
        # Use full anchor_id for uniqueness (avoid peter_baseline vs peter_high_density collision)
        bundle_path = out_dir / f"{anchor.anchor_id}_5_variations_ko.txt"
        sections = []
        sections.append(f"=== {anchor.anchor_id} — 5 seed variations ===\n")
        sections.append(f"{anchor.description}\n\n---\n")
        outcomes = []
        pairs = get_variations(anchor, max_seeds=5)
        for seed, world in pairs:
            probe_label = f"{anchor.anchor_id}_seed{seed}"
            annotated_text, fs = world_to_annotated_text(world, probe_label, anchor.anchor_id, seed)
            outcomes.append((seed, fs))
            features = parse_probe(annotated_text)
            features["probe_id"] = probe_label  # override (parser sets to "unknown" for new format)
            ir = build_ir(features)
            ir["probe_id"] = probe_label
            summary = render_summary(ir)
            narrative = render_narrative(ir)
            sections.append(f"\n=== Variation {seed+1}/5 (seed={seed}) — final: {fs} ===\n")
            sections.append("\n[Summary form]\n")
            sections.append(summary)
            sections.append("\n\n[Narrative form]\n")
            sections.append(narrative)
            sections.append("\n\n---\n")
        bundle_path.write_text("\n".join(sections), encoding="utf-8")
        print(f"\n{anchor.anchor_id}: 5 variations -> {bundle_path}")
        for seed, fs in outcomes:
            print(f"  seed={seed}: {fs}")

    print(f"\nWrote {len(anchors)} anchor bundles to {out_dir}")


if __name__ == "__main__":
    main()
