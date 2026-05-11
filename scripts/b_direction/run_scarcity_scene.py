"""Phase 5 Micro-World 2 — scarcity_scene.

12-agent world: material-layer scarcity driving rumor + blame chain.
NO religious/sacred content — contrast bench for accusation_scene.

Setup (MICRO_WORLD_SPECS.md §3):
  - 12 mixed-role agents (merchant / family_anchor / fisherman / priest /
    soldier / crowd_participant / outsider / elite_strategist)
  - 3 locations (marketplace / granary / poor_quarter)
  - Famine-like food scarcity baseline (rumors "hoarding")
  - NO sacred / religious events

Runs:
    python scripts/b_direction/run_scarcity_scene.py [seed=0] [ticks=30]

Rule #21: 튜닝 대상 아님. contrast bench only.
"""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.persona.profile import DEFAULT_PROFILE, PersonaProfile  # noqa: E402
from engine.population import ROLE_CLUSTERS  # noqa: E402
from engine.world.crowd_dynamics import CrowdState  # noqa: E402
from engine.world.micro_world import (  # noqa: E402
    AgentHandle,
    MicroWorld,
    MicroWorldConfig,
)
from engine.world.spatial import Location  # noqa: E402


def _build_profile_from_role(role_id: str, archetype: str = "") -> PersonaProfile:
    role = ROLE_CLUSTERS[role_id]
    profile = copy.deepcopy(DEFAULT_PROFILE)
    profile.name = f"{role_id}_{archetype}" if archetype else role_id

    for section_name, params in role.profile_prior.items():
        section = getattr(profile, section_name, None)
        if section is None:
            continue
        for k, v in params.items():
            if hasattr(section, k):
                setattr(section, k, v)

    # Minimal archetype overlays
    if archetype == "calculating":
        profile.motif_tendency.observe_wait = min(
            2.0, profile.motif_tendency.observe_wait + 0.4,
        )
    elif archetype == "protective":
        profile.motif_tendency.remain_present = min(
            2.0, profile.motif_tendency.remain_present + 0.3,
        )
        profile.motif_tendency.confront = min(
            2.0, profile.motif_tendency.confront + 0.2,
        )
    elif archetype == "shame_sensitive":
        profile.pressure_sensitivity.shame_exposure = min(
            2.0, profile.pressure_sensitivity.shame_exposure + 0.4,
        )
    elif archetype == "impulsive":
        profile.motif_tendency.confront = min(
            2.0, profile.motif_tendency.confront + 0.3,
        )
        profile.motif_tendency.observe_wait = max(
            0.0, profile.motif_tendency.observe_wait - 0.3,
        )
    elif archetype == "opportunistic":
        profile.motif_tendency.conceal = min(
            2.0, profile.motif_tendency.conceal + 0.3,
        )
        profile.motif_tendency.observe_wait = min(
            2.0, profile.motif_tendency.observe_wait + 0.2,
        )
    elif archetype == "authority_defiant":
        profile.motif_tendency.confront = min(
            2.0, profile.motif_tendency.confront + 0.3,
        )
        profile.relation_bias.authority_reactivity = max(
            0.0, profile.relation_bias.authority_reactivity - 0.3,
        )

    profile.motif_action_priors = copy.deepcopy(DEFAULT_PROFILE.motif_action_priors)
    return profile


def _baseline_state() -> dict:
    return {
        "fear": 2.5, "hope": 4.0, "grief": 1.0,
        "confusion": 2.0, "awe": 1.0, "anger": 3.0,      # higher anger baseline (scarcity)
        "fatigue": 4.0, "vitality": 5.0, "doubt": 3.0,
        "resolve": 5.0, "trauma": 0.5, "joy": 2.0,        # lower joy
        "hunger": 6.0,                                    # scarcity baseline
        "guilt": {"self": 1.0},
        "love": {"primary_focus": 5.0},
        "loyalty": {"primary_focus": 4.0},
        "trust": {"primary_focus": 4.0},
        "shame": {"public_group": 1.0, "self": 1.0, "peer_group": 1.0},
        "belonging": {"peer_group": 5.0, "public_group": 3.0},
    }


def build_scarcity_cast() -> list[AgentHandle]:
    """12-agent mixed-role cast."""
    roster = [
        ("agent_01", "merchant", "opportunistic", {"resolve": 6.0, "hunger": 3.0}),  # wealthy hoarder
        ("agent_02", "family_anchor", "protective", {"grief": 3.0, "hunger": 7.0}),
        ("agent_03", "fisher_laborer", "impulsive", {"anger": 5.0}),
        ("agent_04", "fisher_laborer", "", {}),
        ("agent_05", "fisher_laborer", "", {}),
        ("agent_06", "authority_priest", "calculating", {}),
        ("agent_07", "soldier_enforcer", "protective", {}),
        ("agent_08", "soldier_enforcer", "", {}),
        ("agent_09", "crowd_participant", "impulsive", {"anger": 6.0}),
        ("agent_10", "crowd_participant", "", {}),
        ("agent_11", "outsider", "shame_sensitive", {"grief": 5.0, "hunger": 8.0}),
        ("agent_12", "elite_strategist", "calculating", {"resolve": 7.0}),
    ]
    agents = []
    for aid, role_id, arche, overrides in roster:
        profile = _build_profile_from_role(role_id, arche)
        state = _baseline_state()
        for k, v in overrides.items():
            if k in state:
                state[k] = v
        agents.append(AgentHandle(
            agent_id=aid,
            role_id=role_id,
            profile=profile,
            state=state,
            relations={"peer_group": "mixed_peers"},
            affordance_pack=list(ROLE_CLUSTERS[role_id].affordance_pack),
        ))
    return agents


def build_locations() -> list[Location]:
    return [
        Location(
            location_id="marketplace",
            visibility=0.9, concealment=0.1,
            crowdability=0.9, authority_reach=0.4,
            escape_routes=["poor_quarter"],
            tags=["public", "commercial"],
        ),
        Location(
            location_id="granary",
            visibility=0.5, concealment=0.3,
            crowdability=0.3, authority_reach=0.6,
            escape_routes=["marketplace"],
            tags=["commercial", "authority"],
        ),
        Location(
            location_id="poor_quarter",
            visibility=0.3, concealment=0.6,
            crowdability=0.5, authority_reach=0.2,
            escape_routes=["marketplace"],
            tags=["public", "outdoor"],
        ),
    ]


def build_network(agent_ids: list[str]) -> dict[str, set[str]]:
    merchants = ["agent_01", "agent_12"]  # + strategist
    family = ["agent_02", "agent_03"]
    fishers = ["agent_03", "agent_04", "agent_05"]
    authority = ["agent_06", "agent_07", "agent_08"]
    crowd = ["agent_09", "agent_10"]
    outsider = ["agent_11"]

    network = {a: set() for a in agent_ids}
    for group in (fishers, authority, crowd):
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                network[group[i]].add(group[j])
                network[group[j]].add(group[i])
    # Merchant/strategist hub
    network["agent_01"].update({"agent_06", "agent_09", "agent_12"})
    network["agent_12"].update({"agent_06", "agent_01"})
    # Family-fisher cross
    network["agent_02"].update({"agent_03", "agent_04"})
    # Outsider → crowd link (peripheral)
    network["agent_11"].add("agent_09")
    network["agent_09"].add("agent_11")
    return network


def build_micro_world(seed: int = 0) -> MicroWorld:
    agents = build_scarcity_cast()
    locations = build_locations()
    placements = {
        "agent_01": "granary",    # merchant
        "agent_02": "poor_quarter",  # family
        "agent_03": "marketplace",
        "agent_04": "poor_quarter",
        "agent_05": "marketplace",
        "agent_06": "granary",    # priest
        "agent_07": "granary",    # soldier guarding granary
        "agent_08": "marketplace",
        "agent_09": "marketplace",
        "agent_10": "poor_quarter",
        "agent_11": "poor_quarter",  # outsider
        "agent_12": "granary",    # strategist near authority
    }
    crowds = {
        "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
        "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
    }
    # Seed: "hoarding" rumor against merchant
    seed_rumors = [
        {
            "content_tag": "misdeed",
            "target_role": "merchant",
            "origin_source": "agent_09",
            "initial_reach": ["agent_09", "agent_10"],
            "intensity": 0.7, "credibility": 0.6,
        },
    ]
    # Events: no accusation seeded initially — let emerge from material scarcity
    seed_events = [
        # At tick 5: visible hoarding (granary activity noticed) → marketplace crowd
        {"tick": 5, "event_id": "public_accusation",
         "target_role": "merchant", "location": "marketplace"},
        # At tick 15: authority response (suppression attempt)
        {"tick": 15, "event_id": "guard_approaches", "location": "marketplace"},
    ]
    config = MicroWorldConfig(
        agents=agents,
        locations=locations,
        initial_placements=placements,
        crowd_instances=crowds,
        social_network=build_network([a.agent_id for a in agents]),
        seed_events=seed_events,
        seed_rumors=seed_rumors,
        seed=seed,
    )
    return MicroWorld(config)


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    print(f"[Phase 5 Micro-World 2] scarcity_scene | seed={seed} ticks={n_ticks}")
    world = build_micro_world(seed=seed)
    print(f"  Cast: 12 mixed-role agents, 3 locations")
    print(f"  Setup: food scarcity baseline (hunger high). 'hoarding' rumor vs merchant.")
    print(f"  Seed events: public_accusation @ tick 5, guard_approaches @ tick 15")
    print()

    for _ in range(n_ticks):
        step = world.step()
        if step.tick % 5 == 0 or step.spawned_events:
            motif_counts = Counter(step.agent_motifs.values())
            top_actions = Counter(step.agent_actions.values()).most_common(3)
            actions_str = " ".join(f"{a}:{n}" for a, n in top_actions)
            motifs_str = " ".join(f"{m}:{n}" for m, n in motif_counts.most_common(3))
            events = ",".join(ev.get("event_id", "?") for ev in step.spawned_events)[:24]
            crowds_str = " ".join(
                f"{cid}:{s['phase']}/{s['alignment']:.2f}"
                for cid, s in step.crowd_state_snapshot.items()
            )
            print(f"  t{step.tick:>2} | {events:<24} | {actions_str:<40} | "
                  f"{motifs_str:<30} | {len(step.rumor_snapshot)}r | {crowds_str}")

    all_motifs = Counter()
    all_actions = Counter()
    emergent = 0
    for step in world.history:
        all_motifs.update(step.agent_motifs.values())
        all_actions.update(step.agent_actions.values())
        for ev in step.spawned_events:
            if ev.get("by"):
                emergent += 1

    print("\n=== Summary ===")
    print(f"  Motif distribution: {dict(all_motifs.most_common())}")
    print(f"  Action distribution: {dict(all_actions.most_common())}")
    print(f"  Emergent events (agent-caused): {emergent}")
    print(f"  Final rumor count: {len(world.get_rumors())}")
    from engine.world.crowd_dynamics import compute_phase
    for cid in ("marketplace", "poor_quarter"):
        c = world.get_crowd(cid)
        if c:
            print(f"  {cid}: phase={compute_phase(c)} align={c.alignment_strength:.2f} "
                  f"blame={dict(c.blame_concentration)}")

    # Save
    out_dir = ROOT / "docs" / "b_direction" / "probe_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"scarcity_scene_seed{seed}_ticks{n_ticks}.json"
    payload = {
        "seed": seed, "n_ticks": n_ticks,
        "motif_distribution": dict(all_motifs),
        "action_distribution": dict(all_actions),
        "emergent_event_count": emergent,
        "final_rumor_count": len(world.get_rumors()),
        "final_crowd": {
            cid: {
                "phase": compute_phase(world.get_crowd(cid)),
                "alignment": world.get_crowd(cid).alignment_strength,
                "blame": dict(world.get_crowd(cid).blame_concentration),
            } for cid in ("marketplace", "poor_quarter") if world.get_crowd(cid)
        },
        "history": [
            {"tick": s.tick, "actions": s.agent_actions, "motifs": s.agent_motifs,
             "crowd": s.crowd_state_snapshot, "rumors": s.rumor_snapshot,
             "events": s.spawned_events}
            for s in world.history
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
