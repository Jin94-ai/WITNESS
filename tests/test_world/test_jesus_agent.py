"""Spike 5 Phase 5A — Jesus Agent behavior tests.

Per spec §4.4, no counterfactual tests; these are pure behavior tests
of the world-side Jesus adapter.
"""

from __future__ import annotations

import json
from pathlib import Path

from world.agents.base import (
    BaseWorldAgent,
    ContentBackedWorldAgent,
    WorldAgentContext,
)
from world.agents.jesus import JesusAgent

ROOT = Path(__file__).resolve().parent.parent.parent
WORLD_PROFILE_PATH = (
    ROOT / "content" / "worlds" / "jerusalem_ad30" / "jesus_profile.json"
)


def _load_world_profile() -> dict:
    return json.loads(WORLD_PROFILE_PATH.read_text(encoding="utf-8"))


def _ctx(**overrides) -> WorldAgentContext:
    base = dict(
        agent_id="jesus",
        substep_index=0,
        day_index=0,
        current_location="temple",
        co_located_agents=[],
        recent_rumours=[],
        crowd_density_here=0.3,
        surveillance_level_here=0.3,
        active_feast="none",
        agent_state_digest={},
    )
    base.update(overrides)
    return WorldAgentContext(**base)


# ---------------------------------------------------------------------
# Spec test #1: Jesus teaches more when disciple understanding low.

def test_jesus_teaches_more_when_disciple_understanding_low() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    low_under = agent.decide_with_outcome(
        _ctx(agent_state_digest={"disciple_understanding": 2.0}),
    )
    high_under = agent.decide_with_outcome(
        _ctx(agent_state_digest={"disciple_understanding": 9.0}),
    )
    # Weight on teach should be strictly higher with low understanding.
    assert low_under.considered_weights["teach"] > high_under.considered_weights["teach"]


# ---------------------------------------------------------------------
# Spec test #2: Jesus withdraws when crowd density high.

def test_jesus_withdraws_when_crowd_density_high() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    busy = agent.decide_with_outcome(_ctx(crowd_density_here=0.95))
    assert busy.considered_weights["withdraw"] > busy.considered_weights["teach"]
    assert busy.decision.action_id == "withdraw"


# ---------------------------------------------------------------------
# Spec test #3: Heal at temple → high-intensity rumour.

def test_jesus_heal_at_temple_generates_high_intensity_rumour() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    # Make heal win: suffering co-located + low crowd to suppress withdraw.
    outcome = agent.decide_with_outcome(_ctx(
        current_location="temple",
        agent_state_digest={"colocated_suffering": 9.0,
                            "disciple_understanding": 9.0},
        crowd_density_here=0.1,
    ))
    # Either heal wins or rumor_seed channel is at least in the effect set
    # for the chosen action — we strongly prefer heal via the bonus.
    assert outcome.decision.action_id == "heal"
    assert "rumor_seed" in outcome.decision.world_effects
    # Heal emits rumor_seed with magnitude 1.0 (constant).
    assert outcome.decision.world_effects["rumor_seed"] == 1.0


# ---------------------------------------------------------------------
# Spec test #4: Confront pharisees → authority threat channel activated.

def test_jesus_confront_pharisees_increases_roman_alertness() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    outcome = agent.decide_with_outcome(_ctx(
        co_located_agents=["caiaphas", "pharisees"],
        crowd_density_here=0.2,
        agent_state_digest={"disciple_understanding": 9.0},
    ))
    # With the pharisees bonus (+2.5), confront should beat teach (3.0 base + 0 bonus).
    # confront 1.0 + 2.5 = 3.5 > teach 3.0.
    assert outcome.decision.action_id == "confront"
    assert "authority_threat" in outcome.decision.world_effects


# ---------------------------------------------------------------------
# Spec test #5 ★ single-point failure avoidance.

def test_jesus_influence_reaches_factions_via_multiple_paths() -> None:
    """Phase 5A §4.2.2 — jesus_movement must receive influence through
    AT LEAST THREE distinct action paths, so removing jesus later does
    not zero the faction via a single choke point.

    Paths in Spike 5 Part 1:
    - teach → faction_influence_jesus_movement (direct)
    - heal → faction_influence_jesus_movement (via crowd testimony)
    - bless → faction_influence_jesus_movement (via disciple witness)
    """
    agent = JesusAgent(world_profile=_load_world_profile())
    paths = agent.describe_influence_paths()

    channel = "faction_influence_jesus_movement"
    actions_emitting = [
        action for action, channels in paths.items() if channel in channels
    ]
    assert len(actions_emitting) >= 3, (
        f"Only {len(actions_emitting)} action(s) emit {channel}: "
        f"{actions_emitting}. Spec requires ≥3 to avoid single-point "
        f"failure."
    )


# ---------------------------------------------------------------------
# Spec test #6: canonical constraint overrides free choice.

def test_jesus_canonical_event_on_passover_triggers_entry() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    # Day index 9 = passover_entry in jesus_profile.json.
    outcome = agent.decide_with_outcome(_ctx(
        day_index=9, crowd_density_here=0.99,  # would normally → withdraw
    ))
    assert outcome.canonical_fired
    assert outcome.decision.action_id == "teach"
    assert outcome.decision.meta.get("canonical_id") == "passover_entry"
    assert outcome.decision.meta.get("forced_location") == "temple"


def test_jesus_canonical_event_on_temple_cleanse_forces_confront() -> None:
    agent = JesusAgent(world_profile=_load_world_profile())
    outcome = agent.decide_with_outcome(_ctx(day_index=10))
    assert outcome.canonical_fired
    assert outcome.decision.action_id == "confront"
    assert outcome.decision.meta.get("canonical_id") == "temple_cleanse"


# ---------------------------------------------------------------------
# Spec test #7: Jesus uses same base interface as Peter adapter.

def test_jesus_agent_uses_same_base_interface_as_peter() -> None:
    """Spec §4.3: jesus must not have privileged mechanism.
    BaseWorldAgent protocol is satisfied by both Jesus and the default
    ContentBackedWorldAgent (used for Peter/Judas/etc.)."""
    jesus = JesusAgent(world_profile=_load_world_profile())
    peter_adapter = ContentBackedWorldAgent(
        agent_id="peter", content_actions=["follow_closely", "pray"],
    )
    # runtime_checkable Protocol.
    assert isinstance(jesus, BaseWorldAgent)
    assert isinstance(peter_adapter, BaseWorldAgent)
    # Both expose agent_id + decide().
    assert jesus.agent_id == "jesus"
    assert peter_adapter.agent_id == "peter"
    d1 = jesus.decide(_ctx())
    d2 = peter_adapter.decide(_ctx(agent_id="peter"))
    assert isinstance(d1.action_id, str)
    assert isinstance(d2.action_id, str)


# ---------------------------------------------------------------------
# Extra sanity: profile loading from disk.

def test_jesus_from_world_profile_path_loads_canonical_constraints() -> None:
    agent = JesusAgent.from_world_profile_path(WORLD_PROFILE_PATH)
    # Day 9 + 10 both have canonical entries.
    assert agent._canonical_lookup(9) is not None
    assert agent._canonical_lookup(10) is not None
    assert agent._canonical_lookup(7) is None


# ---------------------------------------------------------------------
# Canonical preservation — every Jesus action visible_signal quotes Scripture.

def test_all_jesus_visible_signals_cite_korean_scripture() -> None:
    profile = json.loads(
        (ROOT / "content" / "jesus" / "behavior_profile.json").read_text(
            encoding="utf-8",
        )
    )
    for action in profile["actions"]:
        sig = action.get("visible_signal", "")
        # ABSOLUTE RULE #2 check: the visible_signal must contain the
        # 개역개정 marker.
        assert "개역개정" in sig, (
            f"Action {action['action_id']}: visible_signal does not cite "
            f"개역개정 — {sig!r}"
        )
