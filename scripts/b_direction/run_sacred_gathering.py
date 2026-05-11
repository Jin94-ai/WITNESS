"""Phase 5 Micro-World 3 — sacred_gathering.

8-agent religious/ritual scene (per MICRO_WORLD_SPECS.md §2).
Different dynamic than accusation or scarcity — sacred_salience drives,
prophet + priest tension, crowd may split (fragmentation) instead of
converge (blame).

Cast (8):
  - 1 spiritual_wanderer (prophet figure)
  - 1 authority_priest (establishment)
  - 3 disciple_follower (devoted, hesitant)
  - 2 crowd_participant
  - 1 family_anchor

No pre-seeded rumors. No crowd accusation. Emergence from sacred calendar
baseline + prophet/priest interaction.
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

    if archetype == "devoted":
        profile.relation_bias.primary_focus_attachment_strength = min(
            2.0, profile.relation_bias.primary_focus_attachment_strength + 0.4,
        )
        profile.motif_tendency.seek_repair = min(
            2.0, profile.motif_tendency.seek_repair + 0.3,
        )
    elif archetype == "authority_defiant":
        profile.motif_tendency.confront = min(
            2.0, profile.motif_tendency.confront + 0.3,
        )
        profile.relation_bias.authority_reactivity = max(
            0.0, profile.relation_bias.authority_reactivity - 0.3,
        )
    elif archetype == "shame_sensitive":
        profile.pressure_sensitivity.shame_exposure = min(
            2.0, profile.pressure_sensitivity.shame_exposure + 0.4,
        )
    elif archetype == "calculating":
        profile.motif_tendency.observe_wait = min(
            2.0, profile.motif_tendency.observe_wait + 0.4,
        )
    elif archetype == "hesitant":
        profile.motif_tendency.observe_wait = min(
            2.0, profile.motif_tendency.observe_wait + 0.3,
        )
        profile.motif_tendency.remain_present = min(
            2.0, profile.motif_tendency.remain_present + 0.2,
        )
    elif archetype == "protective":
        profile.motif_tendency.remain_present = min(
            2.0, profile.motif_tendency.remain_present + 0.3,
        )

    profile.motif_action_priors = copy.deepcopy(DEFAULT_PROFILE.motif_action_priors)
    return profile


def _baseline_state() -> dict:
    return {
        "fear": 2.0, "hope": 6.0, "grief": 1.0,
        "confusion": 2.0, "awe": 7.0,                     # high awe baseline
        "anger": 1.5, "fatigue": 3.0, "vitality": 6.0,
        "doubt": 2.0, "resolve": 6.0, "trauma": 0.5,
        "joy": 5.0, "hunger": 3.0,
        "guilt": {"self": 1.0},
        "love": {"primary_focus": 7.0},
        "loyalty": {"primary_focus": 7.0},
        "trust": {"primary_focus": 7.0},
        "shame": {"public_group": 0.3, "self": 0.5, "peer_group": 0.5},
        "belonging": {"peer_group": 6.0, "public_group": 4.0},
    }


def build_cast() -> list[AgentHandle]:
    roster = [
        # prophet — devoted + authority_defiant
        ("agent_01", "spiritual_wanderer", "authority_defiant",
         {"awe": 8.0, "resolve": 9.0, "hope": 8.0}),
        # priest — calculating
        ("agent_02", "authority_priest", "calculating",
         {"resolve": 7.0, "doubt": 3.0}),
        # 3 disciples
        ("agent_03", "disciple_follower", "devoted", {"awe": 8.0}),
        ("agent_04", "disciple_follower", "devoted", {"awe": 8.0}),
        ("agent_05", "disciple_follower", "hesitant", {}),
        # 2 crowd
        ("agent_06", "crowd_participant", "", {}),
        ("agent_07", "crowd_participant", "shame_sensitive", {}),
        # 1 family
        ("agent_08", "family_anchor", "protective", {"love": 7.0}),
    ]
    agents = []
    for aid, role_id, arche, overrides in roster:
        profile = _build_profile_from_role(role_id, arche)
        state = _baseline_state()
        for k, v in overrides.items():
            if k == "love":
                state["love"]["primary_focus"] = v
            elif k in state:
                state[k] = v
        agents.append(AgentHandle(
            agent_id=aid, role_id=role_id, profile=profile,
            state=state, relations={"peer_group": "followers"},
            affordance_pack=list(ROLE_CLUSTERS[role_id].affordance_pack),
        ))
    return agents


def build_locations() -> list[Location]:
    return [
        Location(
            location_id="temple_outer_court",
            visibility=0.9, concealment=0.1,
            crowdability=0.8, authority_reach=0.5,
            sacred_proximity=0.9,             # HIGH sacred
            escape_routes=["city_street"],
            tags=["public", "sacred"],
        ),
        Location(
            location_id="temple_inner",
            visibility=0.6, concealment=0.3,
            crowdability=0.3, authority_reach=0.8,
            sacred_proximity=1.0,
            escape_routes=["temple_outer_court"],
            tags=["sacred", "authority"],
        ),
        Location(
            location_id="city_street",
            visibility=0.6, concealment=0.3,
            crowdability=0.7, authority_reach=0.4,
            escape_routes=["temple_outer_court"],
            tags=["public", "outdoor"],
        ),
    ]


def build_network(agent_ids: list[str]) -> dict[str, set[str]]:
    # Prophet ↔ disciples strong bond
    # Priest ↔ crowd uneven, opposing prophet
    network = {a: set() for a in agent_ids}
    network["agent_01"].update({"agent_03", "agent_04", "agent_05"})
    for d in ("agent_03", "agent_04", "agent_05"):
        network[d].add("agent_01")
        for other in ("agent_03", "agent_04", "agent_05"):
            if d != other:
                network[d].add(other)
    # Priest ↔ crowd (observing prophet)
    network["agent_02"].update({"agent_06", "agent_07"})
    network["agent_06"].update({"agent_02", "agent_07", "agent_08"})
    network["agent_07"].update({"agent_02", "agent_06"})
    # family ↔ any
    network["agent_08"].update({"agent_06", "agent_05"})
    return network


def build_micro_world(seed: int = 0) -> MicroWorld:
    agents = build_cast()
    locations = build_locations()
    placements = {
        "agent_01": "temple_outer_court",   # prophet in outer court
        "agent_02": "temple_inner",          # priest inside
        "agent_03": "temple_outer_court",    # disciples with prophet
        "agent_04": "temple_outer_court",
        "agent_05": "temple_outer_court",
        "agent_06": "temple_outer_court",    # crowd present
        "agent_07": "city_street",           # crowd peripheral
        "agent_08": "city_street",           # family nearby
    }
    # Sacred festival baseline — no blame seed
    crowds = {
        "temple_outer_court": CrowdState(
            crowd_id="temple_outer_court", density=0.6,
            dominant_emotion="awe",            # sacred energy
        ),
        "city_street": CrowdState(
            crowd_id="city_street", density=0.3,
        ),
    }
    # Sacred events rather than accusation
    seed_events = [
        # Prophet gives sacred speech
        {"tick": 5, "event_id": "prayer_invitation",
         "location": "temple_outer_court"},
        # Miracle moment
        {"tick": 10, "event_id": "miracle_witnessed",
         "location": "temple_outer_court"},
        # Priest intervention attempt (mid-way)
        {"tick": 18, "event_id": "public_accusation",
         "target_role": "spiritual_wanderer",
         "location": "temple_outer_court"},
    ]
    seed_rumors: list[dict] = []

    config = MicroWorldConfig(
        agents=agents, locations=locations,
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
    print(f"[Phase 5 Micro-World 3] sacred_gathering | seed={seed} ticks={n_ticks}")
    world = build_micro_world(seed=seed)
    print("  Cast: 8 agents (prophet + priest + 3 disciples + 2 crowd + family)")
    print("  Setup: high sacred_proximity temple. no pre-blame.")
    print("  Seed: prayer_invitation t5, miracle t10, priest_accusation_of_prophet t18")
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

    from engine.world.crowd_dynamics import compute_phase
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
    print(f"  Emergent events: {emergent}")
    print(f"  Final rumor count: {len(world.get_rumors())}")
    for cid in ("temple_outer_court", "city_street"):
        c = world.get_crowd(cid)
        if c:
            print(f"  {cid}: phase={compute_phase(c)} align={c.alignment_strength:.2f} "
                  f"emotion={c.dominant_emotion} fragment={c.fragmentation:.2f}")

    out_dir = ROOT / "docs" / "b_direction" / "probe_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"sacred_gathering_seed{seed}_ticks{n_ticks}.json"
    payload = {
        "seed": seed, "n_ticks": n_ticks,
        "motif_distribution": dict(all_motifs),
        "action_distribution": dict(all_actions),
        "emergent_events": emergent,
        "final_rumor_count": len(world.get_rumors()),
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
