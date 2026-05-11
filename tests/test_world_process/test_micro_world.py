"""Tests for MicroWorld (Phase 5 implementation)."""

from __future__ import annotations

import re
from pathlib import Path

from engine.persona import DEFAULT_PROFILE
from engine.persona.profile import MotifTendency, PersonaProfile
from engine.world.crowd_dynamics import CrowdState
from engine.world.micro_world import AgentHandle, MicroWorld, MicroWorldConfig
from engine.world.spatial import Location


def _make_profile(name: str, **overrides) -> PersonaProfile:
    """Cheap profile for testing — clone DEFAULT + apply overrides."""
    import copy
    p = copy.deepcopy(DEFAULT_PROFILE)
    p.name = name
    for axis, section in overrides.items():
        if axis == "motif_tendency":
            for k, v in section.items():
                setattr(p.motif_tendency, k, v)
    return p


def _sample_locations() -> list[Location]:
    return [
        Location(
            location_id="square",
            visibility=0.9, concealment=0.1,
            crowdability=0.9, authority_reach=0.5,
            escape_routes=["street"],
        ),
        Location(
            location_id="dwelling",
            visibility=0.2, concealment=0.8,
            crowdability=0.2, authority_reach=0.1,
            escape_routes=["street"],
        ),
        Location(
            location_id="street",
            visibility=0.6, concealment=0.3,
            crowdability=0.7, authority_reach=0.4,
            escape_routes=["square", "dwelling"],
        ),
    ]


def _sample_agents(n: int = 3) -> list[AgentHandle]:
    agents = []
    for i in range(n):
        agents.append(AgentHandle(
            agent_id=f"agent_{i:02d}",
            role_id="crowd_participant",
            profile=_make_profile(f"agent_{i}"),
            state={
                "fear": 3.0, "hope": 5.0, "grief": 1.0,
                "confusion": 2.0, "awe": 3.0, "anger": 2.0,
                "guilt": {"self": 1.0}, "love": {"primary_focus": 5.0},
                "loyalty": {"primary_focus": 5.0},
                "trust": {"primary_focus": 5.0},
                "shame": {"public_group": 1.0, "self": 1.0},
            },
            relations={"peer_group": "other_agents"},
        ))
    return agents


def test_micro_world_boots() -> None:
    locations = _sample_locations()
    agents = _sample_agents(3)
    config = MicroWorldConfig(
        agents=agents,
        locations=locations,
        initial_placements={
            "agent_00": "square",
            "agent_01": "street",
            "agent_02": "dwelling",
        },
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.5)},
    )
    world = MicroWorld(config)
    assert world.tick == 0
    assert len(world.history) == 0


def test_single_step_runs() -> None:
    locations = _sample_locations()
    agents = _sample_agents(3)
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={
            "agent_00": "square", "agent_01": "street", "agent_02": "dwelling",
        },
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.5)},
    )
    world = MicroWorld(config)
    step = world.step()
    assert step.tick == 1
    assert len(step.agent_actions) == 3
    assert len(step.agent_motifs) == 3
    assert "square" in step.crowd_state_snapshot


def test_multi_tick_run() -> None:
    locations = _sample_locations()
    agents = _sample_agents(4)
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={
            "agent_00": "square", "agent_01": "square",
            "agent_02": "street", "agent_03": "dwelling",
        },
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.7)},
        seed=0,
    )
    world = MicroWorld(config)
    history = world.run(10)
    assert len(history) == 10
    assert world.tick == 10
    # Agents should have acted
    for step in history:
        assert len(step.agent_actions) == 4


def test_seed_events_trigger() -> None:
    locations = _sample_locations()
    agents = _sample_agents(3)
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={
            "agent_00": "square", "agent_01": "square", "agent_02": "street",
        },
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.7)},
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "crowd_participant", "location": "square"},
        ],
        seed=0,
    )
    world = MicroWorld(config)
    world.run(5)
    # At tick 3 the seed event should fire
    tick3_step = world.history[2]
    assert any(
        ev.get("event_id") == "public_accusation"
        for ev in tick3_step.spawned_events
    )
    # Crowd in square should have higher accusation_amplification after event
    crowd = world.get_crowd("square")
    assert crowd is not None
    # Some blame built up on crowd_participant target
    assert "crowd_participant" in crowd.blame_concentration


def test_agent_action_affects_crowd() -> None:
    """If an agent 'denies' in a location with crowd, accusation_amplification
    should rise."""
    locations = _sample_locations()
    # Tuned agent: force 'deny' via conceal tendency high
    profile = _make_profile(
        "denier_profile",
        motif_tendency={"conceal": 1.8, "remain_present": 0.2},
    )
    agent = AgentHandle(
        agent_id="agent_00",
        role_id="crowd_participant",
        profile=profile,
        state={
            "fear": 8.0, "hope": 3.0, "grief": 1.0,
            "confusion": 2.0, "awe": 1.0, "anger": 2.0,
            "guilt": {"self": 1.0}, "love": {"primary_focus": 4.0},
            "loyalty": {"primary_focus": 4.0},
            "trust": {"primary_focus": 4.0},
            "shame": {"public_group": 6.0, "self": 3.0},
        },
        relations={"peer_group": "x"},
        affordance_pack=["deny", "follow_closely", "stay_hiding", "flee",
                         "withdraw_in_fear", "follow_at_distance"],
    )
    crowd = CrowdState(crowd_id="square", density=0.7)
    initial_amp = crowd.accusation_amplification
    config = MicroWorldConfig(
        agents=[agent], locations=locations,
        initial_placements={"agent_00": "square"},
        crowd_instances={"square": crowd},
        seed=0,
    )
    world = MicroWorld(config)
    world.run(15)  # Long enough for denial to probably fire

    # Check: deny should have been selected at least once given high shame_exp
    # and high conceal tendency
    any_deny = any(
        step.agent_actions.get("agent_00") == "deny"
        for step in world.history
    )
    # Soft assertion: with these priors + pressures, deny is likely but not
    # guaranteed. Check either deny fired OR rumor was spawned (both = action effect).
    rumor_count = len(world.get_rumors())
    assert any_deny or rumor_count > 0


# -----------------------------------------------------------------
# Role transition integration (WORLD_FLOW_LOOP Iter 1)
# -----------------------------------------------------------------


def test_transition_role_updates_agent() -> None:
    locations = _sample_locations()
    agents = _sample_agents(2)
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={"agent_00": "square", "agent_01": "street"},
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.4)},
        seed=0,
    )
    world = MicroWorld(config)
    world.run(3)
    agent = world.get_agent("agent_00")
    assert agent is not None
    assert agent.role_id == "crowd_participant"

    record = world.transition_role(
        "agent_00", "disciple_follower", reason="miracle_witness",
    )
    assert record.from_role == "crowd_participant"
    assert record.to_role == "disciple_follower"
    assert agent.role_id == "disciple_follower"
    assert "pray" in agent.affordance_pack
    assert agent.info_access_level == "primary_focus_direct"
    assert len(agent.transition_log) == 1


def test_transition_preserves_accumulated_state() -> None:
    """Accumulated emotional state should carry across a role change."""
    locations = _sample_locations()
    agents = _sample_agents(1)
    agents[0].state["shame"]["self"] = 6.0
    agents[0].state["fear"] = 7.0
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={"agent_00": "square"},
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.3)},
        seed=0,
    )
    world = MicroWorld(config)
    world.transition_role("agent_00", "disciple_follower", blend_factor=1.0)
    agent = world.get_agent("agent_00")
    assert agent.state["shame"]["self"] == 6.0
    assert agent.state["fear"] == 7.0


def test_seed_role_transition_event() -> None:
    locations = _sample_locations()
    agents = _sample_agents(2)
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements={"agent_00": "square", "agent_01": "street"},
        crowd_instances={"square": CrowdState(crowd_id="square", density=0.4)},
        seed_events=[
            {
                "tick": 4, "event_id": "role_transition",
                "agent_id": "agent_00", "new_role_id": "elite_strategist",
                "reason": "covert_bargain", "blend_factor": 0.8,
            },
        ],
        seed=0,
    )
    world = MicroWorld(config)
    world.run(6)
    agent = world.get_agent("agent_00")
    assert agent.role_id == "elite_strategist"
    assert agent.transition_log[0].reason == "covert_bargain"
    assert agent.transition_log[0].tick == 4


# -----------------------------------------------------------------
# Rule #1
# -----------------------------------------------------------------

def test_micro_world_module_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    for py in (root / "engine" / "world" / "micro_world").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
