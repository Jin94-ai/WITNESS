"""Generate readability-blind probes (Step C, freeze audit).

Per docs/b_direction/READABILITY_BLIND_PROTOCOL.md.

Produces 12 compact text logs in docs/b_direction/readability_probes/
with scrambled IDs P1-P12 (no scenario/seed/variant label leak).

Ground truth written separately (internal) to
docs/b_direction/READABILITY_BLIND_GROUND_TRUTH.md.

Usage:
    PYTHONHASHSEED=0 python scripts/b_direction/generate_readability_probes.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

OUT_DIR = ROOT / "docs" / "b_direction" / "readability_probes"
GT_PATH = ROOT / "docs" / "b_direction" / "READABILITY_BLIND_GROUND_TRUTH.md"


# 12 probe configurations (scenario, seed, variant_label, config_dict)
# Variant applied via forgiveness_phase_enabled + forgiveness_agent_shame_multiplier
PROBES_GROUND_TRUTH = [
    ("accusation", 0, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("accusation", 3, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("accusation", 0, "p2a_off",       {"p2a": False, "sham_mul": None}),
    ("accusation", 0, "sham_mul_0.8",  {"p2a": True,  "sham_mul": 0.8}),
    ("scarcity",   0, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("scarcity",   2, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("scarcity",   0, "p2a_off",       {"p2a": False, "sham_mul": None}),
    ("scarcity",   0, "sham_mul_0.8",  {"p2a": True,  "sham_mul": 0.8}),
    ("sacred",     0, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("sacred",     1, "baseline",      {"p2a": True,  "sham_mul": None}),
    ("sacred",     0, "p2a_off",       {"p2a": False, "sham_mul": None}),
    ("sacred",     0, "sham_mul_0.05", {"p2a": True,  "sham_mul": 0.05}),
]

N_TICKS = 200
SNAPSHOT_TICKS = [0, 50, 100, 150, 200]


def build_world(scenario, seed, p2a, sham_mul):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_social_network,
    )
    from scripts.b_direction.run_accusation_scene import (
        build_locations as acc_locs,
    )

    if scenario == "accusation":
        agents = build_accusation_cast()
        aids = [a.agent_id for a in agents]
        return MicroWorld(MicroWorldConfig(
            agents=agents, locations=acc_locs(),
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

    if scenario == "scarcity":
        from scripts.b_direction.run_scarcity_scene import (
            build_locations as sc_locs,
        )
        from scripts.b_direction.run_scarcity_scene import (
            build_network,
            build_scarcity_cast,
        )
        agents = build_scarcity_cast()
        aids = [a.agent_id for a in agents]
        return MicroWorld(MicroWorldConfig(
            agents=agents, locations=sc_locs(),
            initial_placements={
                "agent_01": "granary", "agent_02": "poor_quarter",
                "agent_03": "marketplace", "agent_04": "poor_quarter",
                "agent_05": "marketplace", "agent_06": "granary",
                "agent_07": "granary", "agent_08": "marketplace",
                "agent_09": "marketplace", "agent_10": "poor_quarter",
                "agent_11": "poor_quarter", "agent_12": "granary",
            },
            crowd_instances={
                "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
                "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
            },
            social_network=build_network(aids),
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

    if scenario == "sacred":
        from scripts.b_direction.run_sacred_gathering import (
            build_cast,
            build_network,
        )
        from scripts.b_direction.run_sacred_gathering import (
            build_locations as sa_locs,
        )
        agents = build_cast()
        aids = [a.agent_id for a in agents]
        return MicroWorld(MicroWorldConfig(
            agents=agents, locations=sa_locs(),
            initial_placements={
                "agent_01": "temple_outer_court", "agent_02": "temple_inner",
                "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
                "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
                "agent_07": "city_street", "agent_08": "city_street",
            },
            crowd_instances={
                "temple_outer_court": CrowdState(
                    crowd_id="temple_outer_court", density=0.6,
                    dominant_emotion="awe",
                ),
                "city_street": CrowdState(crowd_id="city_street", density=0.3),
            },
            social_network=build_network(aids),
            seed_events=[
                {"tick": 5, "event_id": "prayer_invitation",
                 "location": "temple_outer_court"},
                {"tick": 10, "event_id": "miracle_witnessed",
                 "location": "temple_outer_court"},
                {"tick": 18, "event_id": "public_accusation",
                 "target_role": "spiritual_wanderer",
                 "location": "temple_outer_court"},
            ],
            seed_rumors=[], seed=seed,
            forgiveness_phase_enabled=p2a,
            forgiveness_agent_shame_multiplier=sham_mul,
        ))

    raise ValueError(scenario)


def anonymize_agents(agent_ids):
    """Map agent_01..agent_12 to A1..A12 with role label kept."""
    return {aid: f"A{i+1}" for i, aid in enumerate(agent_ids)}


def anonymize_locations(loc_ids):
    """Map location IDs to L1, L2, L3."""
    return {lid: f"L{i+1}" for i, lid in enumerate(loc_ids)}


# Iter 120: anonymize scenario-specific role names. Without this,
# scenario-specific roles (fisher_laborer/scarcity, spiritual_wanderer/
# sacred, disciple_follower/accusation) leak the scenario in probe
# header, breaking blind evaluation.
ANONYMIZED_ROLE_MAP = {
    # Accusation cast
    "disciple_follower": "follower",
    "authority_priest": "authority",
    "soldier_enforcer": "enforcer",
    "crowd_participant": "crowd",
    "family_anchor": "family",
    "outsider": "outsider",
    # Scarcity cast
    "fisher_laborer": "laborer",
    "merchant": "merchant",
    # Sacred cast
    "spiritual_wanderer": "wanderer",
    "prophet": "speaker",
    # Generic fallbacks
}


def anonymize_role(role_id: str) -> str:
    return ANONYMIZED_ROLE_MAP.get(role_id, role_id)


def compact_state(a, fields=("shame.public_group", "guilt.primary_focus", "fear", "grief")):
    parts = []
    for f in fields:
        if "." in f:
            parent, child = f.split(".")
            v = a.state.get(parent, {})
            if isinstance(v, dict):
                v = v.get(child, 0.0)
        else:
            v = a.state.get(f, 0.0)
        if isinstance(v, (int, float)) and v > 0.1:
            short = f.split(".")[0][:3]
            parts.append(f"{short}={v:.1f}")
    return " ".join(parts) if parts else "-"


def generate_probe_log(probe_id, scenario, seed, variant, config):
    """Run simulation and produce compact text log."""
    w = build_world(
        scenario, seed,
        config["p2a"], config["sham_mul"],
    )
    agent_map = anonymize_agents(list(w._agents.keys()))
    loc_map = anonymize_locations(list(w._crowds.keys()) if hasattr(w, "_crowds") else [])
    # Fallback: locations from spatial registry
    if not loc_map:
        loc_map = anonymize_locations(list(w._spatial._locations.keys()))

    lines = [
        f"=== PROBE {probe_id} ===",
        "",
        "Agents: " + ", ".join(
            f"{agent_map[aid]}={anonymize_role(w._agents[aid].role_id)}"
            for aid in list(w._agents.keys())[:10]
        ),
        "Locations: " + ", ".join(f"{v}" for v in loc_map.values()),
        "",
        "--- Event log (selected ticks) ---",
    ]

    snapshot_data = {}

    for tick_idx in range(N_TICKS):
        step = w.step()
        if tick_idx + 1 in SNAPSHOT_TICKS:
            snap = []
            for aid in list(w._agents.keys())[:10]:
                a = w._agents[aid]
                nickname = agent_map[aid]
                state_str = compact_state(a)
                if state_str != "-":
                    snap.append(f"  {nickname}: {state_str}")
            # Crowd snapshot
            crowd_desc = []
            for cid, c in w._crowds.items():
                blame = c.blame_concentration
                top_blame = ""
                if blame:
                    k, v = max(blame.items(), key=lambda kv: kv[1])
                    top_blame = f" blame[{k}]={v:.1f}"
                crowd_desc.append(
                    f"  {loc_map.get(cid, cid)}: shame_climate={c.shame_climate:.1f}"
                    f" align={c.alignment_strength:.1f}{top_blame}"
                )
            snapshot_data[tick_idx + 1] = (snap, crowd_desc)

        # Log significant events (cap to ~40 lines total)
        if step.spawned_events:
            for ev in step.spawned_events:
                ev_id = ev.get("event_id", "?")
                actor = ev.get("by", "")
                loc = ev.get("location", "")
                nickname = agent_map.get(actor, actor) if actor else ""
                loc_lbl = loc_map.get(loc, loc) if loc else ""
                # Filter to narrative-relevant events
                if ev_id in ("public_accusation", "guard_approaches",
                             "public_confession", "public_denial",
                             "visible_grief", "forgiveness_emitted",
                             "prayer_invitation", "miracle_witnessed"):
                    tag = f"{loc_lbl}:{nickname}" if nickname else loc_lbl
                    lines.append(f"  t={tick_idx+1:>3}  {ev_id:<22} {tag}")

    # Inject snapshots
    for snap_tick in SNAPSHOT_TICKS[1:]:
        if snap_tick not in snapshot_data:
            continue
        snap, crowd = snapshot_data[snap_tick]
        lines.append("")
        lines.append(f"--- State snapshot at t={snap_tick} ---")
        lines.extend(snap)
        lines.append("  (crowd)")
        lines.extend(crowd)

    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Scramble probe order
    probe_order = list(range(12))
    rng = random.Random(42)
    rng.shuffle(probe_order)

    # probe_id (presented as P1..P12) → ground truth index
    ground_truth_rows = []
    for display_i, gt_i in enumerate(probe_order):
        probe_id = f"P{display_i + 1}"
        scenario, seed, variant, config = PROBES_GROUND_TRUTH[gt_i]
        print(f"Generating {probe_id}: {scenario} seed={seed} variant={variant}...")
        log = generate_probe_log(probe_id, scenario, seed, variant, config)
        (OUT_DIR / f"{probe_id}.txt").write_text(log, encoding="utf-8")

        ground_truth_rows.append({
            "probe_id": probe_id,
            "scenario": scenario,
            "seed": seed,
            "variant": variant,
            "config": config,
        })

    # Write ground truth (held internal)
    gt_lines = [
        "# Readability Blind — GROUND TRUTH (internal)",
        "",
        "**Do not share with evaluator until post-eval.**",
        "",
        "| probe_id | scenario | seed | variant | config |",
        "|---|---|---|---|---|",
    ]
    for row in ground_truth_rows:
        gt_lines.append(
            f"| {row['probe_id']} | {row['scenario']} | {row['seed']} | "
            f"{row['variant']} | p2a={row['config']['p2a']} "
            f"sham_mul={row['config']['sham_mul']} |"
        )
    GT_PATH.write_text("\n".join(gt_lines), encoding="utf-8")
    print(f"\nWrote 12 probes to {OUT_DIR.relative_to(ROOT)}")
    print(f"Wrote ground truth to {GT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
