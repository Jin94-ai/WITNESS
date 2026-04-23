"""Spike 5 Phase 5B — Pilate + Caiaphas + light agent behavior tests.

Per spec §3.4: counterfactual tests banned; pure behavior tests only.
"""

from __future__ import annotations

from pathlib import Path

from world.agents.base import WorldAgentContext
from world.agents.caiaphas import CaiaphasAgent
from world.agents.light.barabbas import BarabbasAgent
from world.agents.light.disciples import JamesAgent, JohnAgent, ThomasAgent
from world.agents.pilate import PilateAgent, PilateState

ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = ROOT / "content" / "worlds" / "jerusalem_ad30" / "agents"
PILATE_PATH = AGENTS_DIR / "pilate_profile.json"
CAIAPHAS_PATH = AGENTS_DIR / "caiaphas_profile.json"
LIGHT_DISCIPLES_PATH = AGENTS_DIR / "light_disciples.json"
BARABBAS_PATH = AGENTS_DIR / "barabbas_profile.json"


def _ctx(**overrides) -> WorldAgentContext:
    base = dict(
        agent_id="test", substep_index=0, day_index=0,
        current_location="praetorium",
        co_located_agents=[], recent_rumours=[],
        crowd_density_here=0.3, surveillance_level_here=0.3,
        active_feast="none", agent_state_digest={},
    )
    base.update(overrides)
    return WorldAgentContext(**base)


# =====================================================================
# Pilate tests (2 spec tests).

def test_pilate_delays_judgment_under_political_pressure() -> None:
    """Spec §3.4 #1 — high political_pressure → delay_judgment wins."""
    agent = PilateAgent.from_world_profile_path(PILATE_PATH)
    # Force high pressure.
    agent.state = PilateState(
        alertness=0.3, political_pressure=0.9, wife_dream_influence=0.0,
    )
    outcome = agent.decide_with_outcome(_ctx(day_index=5))
    assert outcome.decision.action_id == "delay_judgment"
    assert (
        outcome.considered_weights["delay_judgment"]
        > outcome.considered_weights["order_action"]
    )


def test_pilate_wash_hands_triggered_by_canonical_constraint() -> None:
    """Spec §3.4 #2 — day_index 14 forces wash_hands."""
    agent = PilateAgent.from_world_profile_path(PILATE_PATH)
    outcome = agent.decide_with_outcome(_ctx(day_index=14))
    assert outcome.canonical_fired
    assert outcome.decision.action_id == "wash_hands"


def test_pilate_wife_dream_on_day_13_shifts_state() -> None:
    """Day 13 canonical state_effect: wife_dream_influence → 0.8."""
    agent = PilateAgent.from_world_profile_path(PILATE_PATH)
    outcome = agent.decide_with_outcome(_ctx(day_index=13))
    assert outcome.state_after is not None
    assert outcome.state_after.wife_dream_influence == 0.8


def test_pilate_order_action_on_high_alertness() -> None:
    """High alertness weights order_action above baseline."""
    agent = PilateAgent.from_world_profile_path(PILATE_PATH)
    agent.state = PilateState(
        alertness=0.9, political_pressure=0.1, wife_dream_influence=0.0,
    )
    outcome = agent.decide_with_outcome(_ctx(day_index=5))
    assert outcome.considered_weights["order_action"] > 1.5


# =====================================================================
# Caiaphas tests (2 spec tests).

def test_caiaphas_convenes_sanhedrin_when_theological_anxiety_high() -> None:
    """Spec §3.4 #3."""
    agent = CaiaphasAgent.from_world_profile_path(CAIAPHAS_PATH)
    # Force high anxiety.
    from world.agents.caiaphas import CaiaphasState
    agent.state = CaiaphasState(
        sanhedrin_authority=0.7, roman_relationship=0.5, theological_anxiety=0.9,
    )
    outcome = agent.decide_with_outcome(_ctx())
    assert outcome.decision.action_id == "convene_sanhedrin"
    assert (
        outcome.considered_weights["convene_sanhedrin"]
        > outcome.considered_weights["temple_decree"]
    )


def test_caiaphas_hub_role_connects_pharisees_and_sadducees() -> None:
    """Spec §3.4 #4 — hub check: ≥2 actions reach each faction channel."""
    agent = CaiaphasAgent.from_world_profile_path(CAIAPHAS_PATH)
    pharisee_actions = agent.hub_reaches("pharisees")
    sadducee_actions = agent.hub_reaches("sadducees")
    # Hub property: multiple actions reach each of the two factions.
    assert len(pharisee_actions) >= 2, (
        f"Caiaphas only reaches pharisees via {pharisee_actions} — "
        f"not enough for hub role."
    )
    assert len(sadducee_actions) >= 2, (
        f"Caiaphas only reaches sadducees via {sadducee_actions} — "
        f"not enough for hub role."
    )
    # Overlap: convene_sanhedrin is in BOTH sets (it's the canonical hub action).
    assert "convene_sanhedrin" in pharisee_actions
    assert "convene_sanhedrin" in sadducee_actions


def test_caiaphas_appeal_to_rome_emits_pilate_pressure() -> None:
    """Non-spec sanity: appeal_to_rome → pilate_political_pressure channel."""
    agent = CaiaphasAgent.from_world_profile_path(CAIAPHAS_PATH)
    # Smoke: decide runs end-to-end with a high-influence context.
    agent.decide_with_outcome(_ctx(
        agent_state_digest={"jesus_movement_influence": 10.0},
    ))
    # The effects for whichever action won must at least expose
    # the canonical channel set this agent owns.
    paths = agent.describe_influence_paths()
    assert "pilate_political_pressure" in paths["appeal_to_rome"]


# =====================================================================
# Barabbas test (1 spec test).

def test_barabbas_activates_at_canonical_trial_scene() -> None:
    """Spec §3.4 #5 — active only on day_index 14 per profile."""
    agent = BarabbasAgent.from_world_profile_path(BARABBAS_PATH)

    inactive = agent.decide_with_outcome(_ctx(day_index=5))
    active = agent.decide_with_outcome(_ctx(day_index=14))

    assert inactive.active is False
    assert inactive.decision.action_id == "idle"

    assert active.active is True
    assert active.decision.action_id != "idle"
    assert "crowd_choice_variable" in active.decision.world_effects


# =====================================================================
# Light disciple tests (4 spec tests + 1 differentiation).

def test_john_witness_action_more_frequent_than_thomas() -> None:
    """Spec §3.4 #6 — John's witness weight > Thomas's for same context."""
    john = JohnAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    thomas = ThomasAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    shared_ctx = _ctx(co_located_agents=["jesus"])
    john_out = john.decide_with_outcome(shared_ctx)
    thomas_out = thomas.decide_with_outcome(shared_ctx)
    assert john_out.considered_weights["witness"] > thomas_out.considered_weights["witness"]


def test_thomas_rumour_trust_lower_than_james() -> None:
    """Spec §3.4 #7 — Thomas has lower rumour_trust_bias than James."""
    thomas = ThomasAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    james = JamesAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    assert thomas.profile.rumour_trust_bias < james.profile.rumour_trust_bias


def test_james_reacts_to_political_tension_more_than_john() -> None:
    """Spec §3.4 #8 — James political_sensitivity > John's."""
    james = JamesAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    john = JohnAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    shared_ctx = _ctx(agent_state_digest={"political_tension": 0.8})
    james_out = james.decide_with_outcome(shared_ctx)
    john_out = john.decide_with_outcome(shared_ctx)
    # Weight on react_political reflects sensitivity × tension.
    assert (
        james_out.considered_weights["react_political"]
        > john_out.considered_weights["react_political"]
    )


def test_disciples_differ_in_response_to_same_event() -> None:
    """Spec §3.4 #9 — graded-proximity foundation.

    All three disciples receive the same WorldAgentContext. Their
    chosen actions or relative weights must differ — this is the
    structural basis for future graded-control experiments.
    """
    john = JohnAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    james = JamesAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    thomas = ThomasAgent.from_disciples_path(LIGHT_DISCIPLES_PATH)
    # Mildly charged scenario: Jesus co-located + some political tension.
    ctx = _ctx(
        co_located_agents=["jesus"],
        agent_state_digest={"political_tension": 0.4, "event_understanding": 0.4},
    )
    john_out = john.decide_with_outcome(ctx)
    james_out = james.decide_with_outcome(ctx)
    thomas_out = thomas.decide_with_outcome(ctx)
    actions = {john_out.decision.action_id, james_out.decision.action_id,
               thomas_out.decision.action_id}
    assert len(actions) >= 2, (
        "All three disciples chose the same action — graded proximity "
        "foundation is broken."
    )
