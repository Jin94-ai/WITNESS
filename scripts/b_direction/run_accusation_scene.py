"""Phase 5 Micro-World 1 runner — accusation_scene.

10-agent micro-world with 3 locations + rumor + crowd dynamics.
NO handcrafted action boosts — everything emerges from:
  - persona engine (motif mediation)
  - role_cluster priors
  - world process layers (crowd / rumor / space)

Run:
    python scripts/b_direction/run_accusation_scene.py [seed=0] [ticks=30]
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

from engine.persona.profile import (  # noqa: E402
    DEFAULT_PROFILE,
    MotifTendency,
    PersonaProfile,
    PressureSensitivity,
    RelationBias,
)
from engine.population import ROLE_CLUSTERS  # noqa: E402
from engine.world.crowd_dynamics import CrowdState  # noqa: E402
from engine.world.micro_world import (  # noqa: E402
    AgentHandle,
    MicroWorld,
    MicroWorldConfig,
)
from engine.world.spatial import Location  # noqa: E402


# =============================================================================
# Agent construction (10 agents from role clusters)
# =============================================================================

def _build_profile_from_role(role_id: str, archetype: str = "") -> PersonaProfile:
    """Build a PersonaProfile from a role cluster prior + archetype tweaks."""
    role = ROLE_CLUSTERS[role_id]
    profile = copy.deepcopy(DEFAULT_PROFILE)
    profile.name = f"{role_id}_{archetype}" if archetype else role_id
    profile.description = f"{role_id} with archetype={archetype}"

    # Apply role prior
    for section_name, params in role.profile_prior.items():
        section = getattr(profile, section_name, None)
        if section is None:
            continue
        for k, v in params.items():
            if hasattr(section, k):
                setattr(section, k, v)

    # Minimal archetype tweaks (inline to avoid over-engineering)
    if archetype == "impulsive":
        profile.motif_tendency.confront = min(2.0, profile.motif_tendency.confront + 0.3)
        profile.motif_tendency.observe_wait = max(0.0, profile.motif_tendency.observe_wait - 0.3)
    elif archetype == "calculating":
        profile.motif_tendency.observe_wait = min(2.0, profile.motif_tendency.observe_wait + 0.4)
    elif archetype == "devoted":
        profile.relation_bias.primary_focus_attachment_strength = min(
            2.0, profile.relation_bias.primary_focus_attachment_strength + 0.4,
        )
        profile.motif_tendency.seek_repair = min(
            2.0, profile.motif_tendency.seek_repair + 0.3,
        )
    elif archetype == "shame_sensitive":
        profile.pressure_sensitivity.shame_exposure = min(
            2.0, profile.pressure_sensitivity.shame_exposure + 0.4,
        )
        profile.motif_tendency.conceal = min(2.0, profile.motif_tendency.conceal + 0.2)
    elif archetype == "detached":
        profile.relation_bias.primary_focus_attachment_strength = max(
            0.0, profile.relation_bias.primary_focus_attachment_strength - 0.3,
        )
        profile.motif_tendency.withdraw = min(2.0, profile.motif_tendency.withdraw + 0.2)
    elif archetype == "authority_sensitive":
        profile.pressure_sensitivity.social_threat = min(
            2.0, profile.pressure_sensitivity.social_threat + 0.3,
        )

    profile.motif_action_priors = copy.deepcopy(DEFAULT_PROFILE.motif_action_priors)
    return profile


def _build_baseline_state() -> dict:
    return {
        "fear": 3.0, "hope": 5.0, "grief": 1.0,
        "confusion": 2.0, "awe": 3.0, "anger": 2.0,
        "fatigue": 3.0, "vitality": 6.0, "doubt": 2.0,
        "resolve": 5.0, "trauma": 0.5, "joy": 4.0, "hunger": 2.0,
        "guilt": {"self": 1.0},
        "love": {"primary_focus": 5.0},
        "loyalty": {"primary_focus": 5.0},
        "trust": {"primary_focus": 5.0},
        "shame": {"public_group": 0.5, "self": 1.0, "peer_group": 1.0},
        "belonging": {"peer_group": 5.0, "public_group": 3.0},
    }


def build_accusation_cast() -> list[AgentHandle]:
    """10-agent cast per MICRO_WORLD_SPECS.md §1.1."""
    roster = [
        # (agent_id, role_cluster, archetype, state_overrides)
        ("agent_01", "disciple_follower", "impulsive",
         {"hope": 7.0, "loyalty_pf": 9.0}),  # Peter analog
        ("agent_02", "disciple_follower", "calculating",
         {"loyalty_pf": 4.5, "doubt": 6.0}),  # Judas analog
        ("agent_03", "disciple_follower", "devoted", {"hope": 7.0}),
        ("agent_04", "authority_priest", "calculating", {"resolve": 7.5}),
        ("agent_05", "soldier_enforcer", "authority_sensitive", {"resolve": 7.0}),
        ("agent_06", "crowd_participant", "impulsive", {"anger": 3.0}),
        ("agent_07", "crowd_participant", "shame_sensitive", {"doubt": 4.0}),
        ("agent_08", "crowd_participant", "", {"fear": 2.5}),
        ("agent_09", "family_anchor", "", {"love": 7.0}),
        ("agent_10", "outsider", "", {"grief": 4.0, "hope": 3.0}),
    ]
    agents = []
    for aid, role_id, arche, overrides in roster:
        profile = _build_profile_from_role(role_id, arche)
        state = _build_baseline_state()
        # Apply overrides into state
        for k, v in overrides.items():
            if k == "loyalty_pf":
                state["loyalty"]["primary_focus"] = v
            elif k in state:
                state[k] = v
        agents.append(AgentHandle(
            agent_id=aid,
            role_id=role_id,
            profile=profile,
            state=state,
            relations={"peer_group": "disciple_peers"},
            affordance_pack=list(ROLE_CLUSTERS[role_id].affordance_pack),
        ))
    return agents


# =============================================================================
# World build
# =============================================================================

def build_locations() -> list[Location]:
    return [
        Location(
            location_id="priest_courtyard",
            visibility=0.9, concealment=0.1,
            crowdability=0.7, authority_reach=0.9,
            escape_routes=["city_street"],
            tags=["public", "authority"],
        ),
        Location(
            location_id="upper_room",
            visibility=0.2, concealment=0.7,
            crowdability=0.3, authority_reach=0.1,
            escape_routes=["city_street"],
            tags=["private", "indoor"],
        ),
        Location(
            location_id="city_street",
            visibility=0.6, concealment=0.3,
            crowdability=0.9, authority_reach=0.5,
            escape_routes=["priest_courtyard", "upper_room"],
            tags=["public", "outdoor"],
        ),
    ]


def build_social_network(agent_ids: list[str]) -> dict[str, set[str]]:
    """Simple network: peer_group fully connected; crowd fully connected;
    merchants/hubs link groups."""
    disciples = ["agent_01", "agent_02", "agent_03"]
    authorities = ["agent_04", "agent_05"]
    crowd = ["agent_06", "agent_07", "agent_08"]
    others = ["agent_09", "agent_10"]

    network = {a: set() for a in agent_ids}
    # Intra-group edges
    for group in (disciples, authorities, crowd):
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                network[group[i]].add(group[j])
                network[group[j]].add(group[i])
    # Cross-group bridges
    network["agent_05"].update({"agent_04", "agent_06"})  # soldier ↔ priest ↔ crowd
    network["agent_04"].update({"agent_05", "agent_07"})
    network["agent_09"].update({"agent_01", "agent_06"})  # family bridges
    network["agent_10"].update({"agent_07"})              # outsider ↔ crowd
    return network


def build_micro_world(seed: int = 0) -> MicroWorld:
    agents = build_accusation_cast()
    agent_ids = [a.agent_id for a in agents]
    locations = build_locations()

    # Initial placements (MICRO_WORLD_SPECS.md §1.2)
    placements = {
        "agent_01": "upper_room",
        "agent_02": "upper_room",
        "agent_03": "upper_room",
        "agent_04": "priest_courtyard",
        "agent_05": "priest_courtyard",
        "agent_06": "city_street",
        "agent_07": "city_street",
        "agent_08": "city_street",
        "agent_09": "upper_room",
        "agent_10": "city_street",
    }

    # Crowd instances — one per location where crowdability high
    crowds = {
        "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
        "city_street": CrowdState(crowd_id="city_street", density=0.6),
    }

    # Seed events
    seed_events = [
        {"tick": 3, "event_id": "public_accusation",
         "target_role": "disciple_follower", "location": "priest_courtyard"},
        {"tick": 7, "event_id": "public_accusation",
         "target_role": "outsider", "location": "city_street"},
        {"tick": 12, "event_id": "guard_approaches",
         "location": "upper_room"},
    ]

    # Seed rumor
    seed_rumors = [
        {
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        },
    ]

    config = MicroWorldConfig(
        agents=agents,
        locations=locations,
        initial_placements=placements,
        crowd_instances=crowds,
        social_network=build_social_network(agent_ids),
        seed_events=seed_events,
        seed_rumors=seed_rumors,
        seed=seed,
    )
    return MicroWorld(config)


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    print(f"[Phase 5 Micro-World 1] accusation_scene | seed={seed} ticks={n_ticks}")
    world = build_micro_world(seed=seed)

    print(f"\n  Cast: 10 agents across 3 locations")
    print(f"  Crowds: priest_courtyard (0.4), city_street (0.6)")
    print(f"  Seed events: public_accusation @ tick 3/7, guard_approaches @ tick 12")
    print(f"  Seed rumor: threat_to_authority → disciple_follower")

    print("\n  tick | scene | key actions | motifs | rumors | crowd phases")
    print("  " + "-" * 100)

    for _ in range(n_ticks):
        step = world.step()
        motif_counts = Counter(step.agent_motifs.values())
        key_actions = Counter(step.agent_actions.values()).most_common(3)
        actions_str = " ".join(f"{a}:{n}" for a, n in key_actions)
        motifs_str = " ".join(f"{m}:{n}" for m, n in motif_counts.most_common(3))

        crowd_phases = " ".join(
            f"{cid}:{s['phase']}" for cid, s in step.crowd_state_snapshot.items()
        )

        events = ",".join(ev.get("event_id", "?") for ev in step.spawned_events)[:20]
        print(f"  {step.tick:>4} | {events:<20} | {actions_str:<45} | "
              f"{motifs_str:<35} | {len(step.rumor_snapshot)}r | {crowd_phases}")

    # Summary
    all_motifs = Counter()
    all_actions = Counter()
    emergent_events = 0
    for step in world.history:
        all_motifs.update(step.agent_motifs.values())
        all_actions.update(step.agent_actions.values())
        for ev in step.spawned_events:
            if ev.get("by"):  # agent-caused is emergent
                emergent_events += 1

    print("\n=== Summary ===")
    print(f"  Total motif distribution: {dict(all_motifs.most_common())}")
    print(f"  Total action distribution: {dict(all_actions.most_common())}")
    print(f"  Final rumor count: {len(world.get_rumors())}")
    print(f"  Emergent events (agent-caused): {emergent_events}")

    for cid in ("priest_courtyard", "city_street"):
        crowd = world.get_crowd(cid)
        if crowd:
            from engine.world.crowd_dynamics import compute_phase
            print(f"  {cid}: phase={compute_phase(crowd)} "
                  f"align={crowd.alignment_strength:.2f} "
                  f"blame={dict(crowd.blame_concentration)}")

    # Save artifact
    out_dir = ROOT / "docs" / "b_direction" / "probe_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"accusation_scene_seed{seed}_ticks{n_ticks}.json"
    payload = {
        "seed": seed, "n_ticks": n_ticks,
        "motif_distribution": dict(all_motifs),
        "action_distribution": dict(all_actions),
        "emergent_event_count": emergent_events,
        "final_rumor_count": len(world.get_rumors()),
        "final_crowd_phases": {
            cid: {
                "phase": (world.get_crowd(cid) and
                          __import__("engine.world.crowd_dynamics",
                                      fromlist=["compute_phase"]).compute_phase(
                              world.get_crowd(cid)) or "idle"),
                "alignment": world.get_crowd(cid).alignment_strength
                             if world.get_crowd(cid) else 0.0,
            }
            for cid in ("priest_courtyard", "city_street")
        },
        "history": [
            {
                "tick": s.tick,
                "actions": s.agent_actions,
                "motifs": s.agent_motifs,
                "crowd": s.crowd_state_snapshot,
                "rumors": s.rumor_snapshot,
                "events": s.spawned_events,
            }
            for s in world.history
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
