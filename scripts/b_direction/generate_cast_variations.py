"""Generate cast composition variation probes (Branch C S4 second slice).

Per BRANCH_C_DESIGN_DRAFT.md §3 S4: cross-scenario cast composition variation.
Engine touch=NO. Generator-level cast filter + placement adjustment.

3 scenarios * 3 cast variants = 9 probes.

Cast variants (role-based drops):
  "full"          - all baseline agents
  "no_authority"  - drop authority_priest + soldier_enforcer agents
  "no_outsider"   - drop outsider + elite_strategist + spiritual_wanderer agents

Output: docs/b_direction/readability_probes_cast/P_CV_{n}.txt
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
# Cast filter rules per scenario
# ============================================================

CAST_DROP_RULES = {
    "accusation": {
        "full": set(),
        "no_authority": {"authority_priest", "soldier_enforcer"},
        "no_outsider": {"outsider"},
    },
    "scarcity": {
        "full": set(),
        "no_authority": {"authority_priest", "soldier_enforcer"},
        "no_outsider": {"outsider", "elite_strategist"},
    },
    "sacred": {
        "full": set(),
        "no_authority": {"authority_priest"},
        "no_outsider": {"spiritual_wanderer"},
    },
}

BASELINE_PLACEMENTS = {
    "accusation": {
        "agent_01": "upper_room", "agent_02": "upper_room",
        "agent_03": "upper_room", "agent_04": "priest_courtyard",
        "agent_05": "priest_courtyard", "agent_06": "city_street",
        "agent_07": "city_street", "agent_08": "city_street",
        "agent_09": "upper_room", "agent_10": "city_street",
    },
    "scarcity": {
        "agent_01": "granary", "agent_02": "poor_quarter",
        "agent_03": "marketplace", "agent_04": "poor_quarter",
        "agent_05": "marketplace", "agent_06": "granary",
        "agent_07": "granary", "agent_08": "marketplace",
        "agent_09": "marketplace", "agent_10": "poor_quarter",
        "agent_11": "poor_quarter", "agent_12": "granary",
    },
    "sacred": {
        "agent_01": "temple_outer_court", "agent_02": "temple_inner",
        "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
        "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
        "agent_07": "city_street", "agent_08": "city_street",
    },
}

CAST_BUILDERS = {
    "accusation": build_accusation_cast,
    "scarcity": build_scarcity_cast,
    "sacred": sacred_cast,
}


def filter_cast(scenario, variant):
    """Return (filtered_agents, filtered_placements)."""
    agents = CAST_BUILDERS[scenario]()
    drop_roles = CAST_DROP_RULES[scenario][variant]
    filtered = [a for a in agents if a.role_id not in drop_roles]
    kept_aids = {a.agent_id for a in filtered}
    placements = {
        aid: loc for aid, loc in BASELINE_PLACEMENTS[scenario].items()
        if aid in kept_aids
    }
    return filtered, placements


def _filter_network(net, kept_aids):
    """Filter social network dict to kept agent ids only."""
    out = {}
    for k, v in net.items():
        if k in kept_aids:
            out[k] = {x for x in v if x in kept_aids}
    return out


def build_world_with_cast(scenario, variant, seed=0, p2a=True, sham_mul=None):
    # Build full cast first to compute network, then filter
    full_agents = CAST_BUILDERS[scenario]()
    full_aids = [a.agent_id for a in full_agents]
    drop_roles = CAST_DROP_RULES[scenario][variant]
    agents = [a for a in full_agents if a.role_id not in drop_roles]
    aids = [a.agent_id for a in agents]
    kept_aids = set(aids)
    placements = {
        aid: loc for aid, loc in BASELINE_PLACEMENTS[scenario].items()
        if aid in kept_aids
    }

    if scenario == "accusation":
        full_net = acc_net(full_aids)
        net = _filter_network(full_net, kept_aids)
        return MicroWorld(MicroWorldConfig(
            agents=agents, locations=acc_locs(),
            initial_placements=placements,
            crowd_instances={
                "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
                "city_street": CrowdState(crowd_id="city_street", density=0.6),
            },
            social_network=net,
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
                "origin_source": agents[0].agent_id,
                "initial_reach": [agents[0].agent_id, agents[1].agent_id] if len(agents) >= 2 else [agents[0].agent_id],
                "intensity": 0.6, "credibility": 0.5,
            }],
            seed=seed,
            forgiveness_phase_enabled=p2a,
            forgiveness_agent_shame_multiplier=sham_mul,
        ))
    if scenario == "scarcity":
        full_net = sc_net(full_aids)
        net = _filter_network(full_net, kept_aids)
        return MicroWorld(MicroWorldConfig(
            agents=agents, locations=sc_locs(),
            initial_placements=placements,
            crowd_instances={
                "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
                "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
            },
            social_network=net,
            seed_events=[
                {"tick": 5, "event_id": "public_accusation",
                 "target_role": "merchant", "location": "marketplace"},
                {"tick": 15, "event_id": "guard_approaches", "location": "marketplace"},
            ],
            seed_rumors=[{
                "content_tag": "misdeed", "target_role": "merchant",
                "origin_source": agents[0].agent_id,
                "initial_reach": [agents[0].agent_id],
                "intensity": 0.7, "credibility": 0.6,
            }],
            seed=seed,
            forgiveness_phase_enabled=p2a,
            forgiveness_agent_shame_multiplier=sham_mul,
        ))
    if scenario == "sacred":
        full_net = sa_net(full_aids)
        net = _filter_network(full_net, kept_aids)
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
            social_network=net,
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
                "origin_source": agents[0].agent_id,
                "initial_reach": [agents[0].agent_id],
                "intensity": 0.6, "credibility": 0.7,
            }],
            seed=seed,
            forgiveness_phase_enabled=p2a,
            forgiveness_agent_shame_multiplier=sham_mul,
        ))


def make_annotated_cast_variant(probe_label, scenario, variant, seed=0):
    """Reuses logic from generate_placement_variations.py make_annotated_placement."""
    w = build_world_with_cast(scenario, variant, seed=seed)
    aids = list(w._agents.keys())
    cast_size = len(aids)
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
    blame_per_target_per_tick = []  # v4

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
        # v4 per-target blame
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
        f"=== PROBE {probe_label} (cast variant: {scenario}/{variant}, n={cast_size}, v4) ===",
        "",
        "[Annotated headline summary]",
        f"  Final summary:    {final_summary}",
        f"  Primary pressure: {primary_pressure}",
    ]
    if failure_mode is not None:
        headline.append(f"  Failure mode:     {failure_mode}")
    headline.append(f"  Cast size:        {cast_size}")
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
        f"Cast variant: {variant} (n={cast_size})",
        "",
    ]

    return "\n".join(lines), final_summary, primary_pressure, failure_mode, cast_size


def main():
    out_dir = ROOT / "docs" / "b_direction" / "readability_probes_cast"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    n = 0
    for scenario in ["accusation", "scarcity", "sacred"]:
        for variant in ["full", "no_authority", "no_outsider"]:
            n += 1
            label = f"P_CV_{n:02d}"
            text, fs, pp, fm, cs = make_annotated_cast_variant(label, scenario, variant)
            (out_dir / f"{label}.txt").write_text(text, encoding="utf-8")
            summary.append((label, scenario, variant, cs, fs, pp, fm or "-"))
            print(f"  {label}: {scenario}/{variant} (n={cs}) -> {fs} / {pp} / {fm or '-'}")

    print(f"\nWrote {n} cast variation probes to {out_dir}")
    print("\n=== Summary ===")
    print(f"{'Label':<10} {'Scenario':<12} {'Variant':<14} {'n':>3} {'Final summary':<22} {'Pressure':<12} Failure")
    for row in summary:
        print(f"{row[0]:<10} {row[1]:<12} {row[2]:<14} {row[3]:>3} {row[4]:<22} {row[5]:<12} {row[6]}")


if __name__ == "__main__":
    main()
