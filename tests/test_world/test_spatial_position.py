"""Direct coverage for ``world.space.position.SpatialState``.

The broader spatial tests in ``test_spatial.py`` exercise the movement +
rumour paths; this file pins the query helpers and edge branches that
those tests do not touch.
"""

from __future__ import annotations

from world.space.position import AgentPosition, SpatialState


def test_agents_at_returns_matching_ids() -> None:
    state = SpatialState()
    state.place("peter", "temple")
    state.place("judas", "temple")
    state.place("jesus", "gethsemane")
    assert sorted(state.agents_at("temple")) == ["judas", "peter"]
    assert state.agents_at("praetorium") == []


def test_agents_in_transit_lists_only_transit_agents() -> None:
    state = SpatialState()
    state.place("peter", "temple")
    state.place("judas", "praetorium")
    state.begin_move("judas", "temple", cost_substeps=2)
    assert state.agents_in_transit() == ["judas"]


def test_same_location_handles_missing_and_transit_agents() -> None:
    state = SpatialState()
    state.place("peter", "temple")
    # Missing second agent → False, not error.
    assert state.same_location("peter", "ghost") is False
    assert state.same_location("ghost", "peter") is False
    # Transit breaks co-location (line 58-59).
    state.begin_move("peter", "praetorium", cost_substeps=2)
    state.place("judas", "praetorium")
    assert state.same_location("peter", "judas") is False


def test_same_location_true_when_both_at_same_place() -> None:
    state = SpatialState()
    state.place("peter", "temple")
    state.place("judas", "temple")
    assert state.same_location("peter", "judas") is True


def test_begin_move_zero_cost_places_directly() -> None:
    """cost_substeps <= 0 must teleport (lines 71-73)."""
    state = SpatialState()
    state.place("pilate", "caesarea")
    state.begin_move("pilate", "praetorium", cost_substeps=0)
    assert state.where("pilate") == "praetorium"
    assert state.agents_in_transit() == []


def test_advance_one_substep_preserves_stationary_agents() -> None:
    """Non-transit agents must pass through advance_one_substep (line 99)."""
    state = SpatialState()
    state.place("peter", "temple")
    state.begin_move("judas", "praetorium", cost_substeps=2)
    before = state.where("peter")
    state.advance_one_substep()
    assert state.where("peter") == before
    # Judas still in transit (2 → 1).
    assert state.where("judas") == "transit"


def test_initial_populates_starting_positions() -> None:
    """``initial`` helper (lines 104-106) is a fluent seeder."""
    state = SpatialState().initial([
        ("peter", "temple"),
        ("jesus", "gethsemane"),
        ("pilate", "praetorium"),
    ])
    assert state.where("peter") == "temple"
    assert state.where("jesus") == "gethsemane"
    assert state.where("pilate") == "praetorium"


def test_agent_position_is_in_transit_flag() -> None:
    settled = AgentPosition(agent_id="x", current_location="temple")
    moving = AgentPosition(
        agent_id="x", current_location="transit",
        destination="praetorium", substeps_remaining=2,
    )
    assert settled.is_in_transit is False
    assert moving.is_in_transit is True
