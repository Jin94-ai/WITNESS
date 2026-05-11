"""Tests for engine.observer.adapter — MultiAgentResult → Observer conversion."""

from __future__ import annotations

import pytest

from engine.core.state import (
    AgentState,
    EmotionalState,
    PhysicalState,
    SlowState,
)
from engine.observer.adapter import (
    agent_state_to_snapshot,
    result_to_observer,
)


def _make_agent_state(
    agent_id: str,
    tick: int = 0,
    fear: float = 0.0,
    hope: float = 5.0,
    moral_injury: float = 0.0,
) -> AgentState:
    """Build minimal AgentState for testing."""
    return AgentState(
        agent_id=agent_id,
        tick=tick,
        physical=PhysicalState(),
        emotions=EmotionalState(fear=fear, hope=hope),
        slow_state=SlowState(moral_injury=moral_injury),
    )


class _MockResult:
    """Minimal stand-in for MultiAgentResult (avoids full pydantic construction)."""

    def __init__(
        self,
        state_snapshots: dict[str, dict[int, AgentState]],
        fired_events: list[dict] | None = None,
    ) -> None:
        self.state_snapshots = state_snapshots
        self.fired_events = fired_events or []


class TestAgentStateToSnapshot:
    def test_basic_mapping(self) -> None:
        state = _make_agent_state("a1", fear=7.0, hope=4.0, moral_injury=3.0)
        snap = agent_state_to_snapshot(state, role="follower")
        assert snap.id == "a1"
        assert snap.role == "follower"
        assert snap.fear == 7.0
        assert snap.hope == 4.0
        assert snap.shame_self == 3.0  # moral_injury → shame_self
        assert snap.delta == []

    def test_default_role_generic(self) -> None:
        state = _make_agent_state("a1")
        snap = agent_state_to_snapshot(state)
        assert snap.role == "generic"

    def test_with_delta_tags(self) -> None:
        state = _make_agent_state("a1")
        snap = agent_state_to_snapshot(state, delta_tags=["fear_up"])
        assert snap.delta == ["fear_up"]


class TestResultToObserver:
    def test_basic_two_agent_three_tick(self) -> None:
        states = {
            "a1": {
                0: _make_agent_state("a1", tick=0, fear=2.0),
                1: _make_agent_state("a1", tick=1, fear=2.5),
                2: _make_agent_state("a1", tick=2, fear=3.0),
            },
            "a2": {
                0: _make_agent_state("a2", tick=0, fear=1.0),
                1: _make_agent_state("a2", tick=1, fear=4.0),  # +3 → delta
                2: _make_agent_state("a2", tick=2, fear=4.0),
            },
        }
        result = _MockResult(state_snapshots=states)
        obs = result_to_observer(result)
        assert obs.list_ticks() == [0, 1, 2]
        assert set(obs.list_agents()) == {"a1", "a2"}
        # a2 fear shift detected
        a2_at_t1 = obs.get_person_view("a2", tick=1)
        assert a2_at_t1 is not None
        assert "fear_up" in a2_at_t1.delta

    def test_empty_states_rejected(self) -> None:
        result = _MockResult(state_snapshots={})
        with pytest.raises(ValueError, match="no state_snapshots"):
            result_to_observer(result)

    def test_role_map_applied(self) -> None:
        states = {
            "a1": {0: _make_agent_state("a1")},
            "a2": {0: _make_agent_state("a2")},
        }
        result = _MockResult(state_snapshots=states)
        role_map = {"a1": "authority", "a2": "crowd"}
        obs = result_to_observer(result, role_map=role_map)
        a1 = obs.get_person_view("a1", tick=0)
        a2 = obs.get_person_view("a2", tick=0)
        assert a1 is not None and a1.role == "authority"
        assert a2 is not None and a2.role == "crowd"

    def test_default_role_generic(self) -> None:
        states = {"a1": {0: _make_agent_state("a1")}}
        result = _MockResult(state_snapshots=states)
        obs = result_to_observer(result)
        a = obs.get_person_view("a1", tick=0)
        assert a is not None
        assert a.role == "generic"

    def test_world_stats_applied(self) -> None:
        states = {"a1": {0: _make_agent_state("a1")}}
        result = _MockResult(state_snapshots=states)
        world_stats = {
            0: {
                "crowd_mood": "tense",
                "blame_concentration": 0.7,
                "scarcity_pressure": 0.3,
            }
        }
        obs = result_to_observer(result, world_stats_per_tick=world_stats)
        ws = obs.get_world_view(tick=0)
        assert ws.crowd_mood == "tense"
        assert ws.blame_concentration == 0.7

    def test_world_stats_default_when_missing(self) -> None:
        states = {"a1": {0: _make_agent_state("a1")}}
        result = _MockResult(state_snapshots=states)
        obs = result_to_observer(result)
        ws = obs.get_world_view(tick=0)
        assert ws.crowd_mood == "calm"  # default

    def test_group_stats_applied(self) -> None:
        states = {"a1": {0: _make_agent_state("a1")}}
        result = _MockResult(state_snapshots=states)
        group_stats = {
            0: [
                {"id": "L1", "dominant_mode": "saturation", "tension": 0.8},
                {"id": "L2", "dominant_mode": "recovery", "tension": 0.3},
            ]
        }
        obs = result_to_observer(result, group_stats_per_tick=group_stats)
        l1 = obs.get_group_view("L1", tick=0)
        l2 = obs.get_group_view("L2", tick=0)
        assert l1 is not None and l1.dominant_mode == "saturation"
        assert l2 is not None and l2.dominant_mode == "recovery"

    def test_active_events_from_fired_events(self) -> None:
        states = {"a1": {0: _make_agent_state("a1"), 1: _make_agent_state("a1", tick=1)}}
        fired_events = [
            {"tick": 1, "event_id": "public_accusation"},
        ]
        result = _MockResult(state_snapshots=states, fired_events=fired_events)
        obs = result_to_observer(result)
        snap_t1 = obs._tick_index[1]
        assert "public_accusation" in snap_t1.active_events

    def test_active_events_explicit_override(self) -> None:
        states = {"a1": {0: _make_agent_state("a1")}}
        fired_events = [{"tick": 0, "event_id": "from_result"}]
        result = _MockResult(state_snapshots=states, fired_events=fired_events)
        obs = result_to_observer(
            result,
            active_events_per_tick={0: ["explicit_override"]},
        )
        snap = obs._tick_index[0]
        assert "explicit_override" in snap.active_events
        assert "from_result" not in snap.active_events

    def test_agent_only_in_some_ticks(self) -> None:
        # a2 only present at tick 1
        states = {
            "a1": {
                0: _make_agent_state("a1", tick=0),
                1: _make_agent_state("a1", tick=1),
            },
            "a2": {
                1: _make_agent_state("a2", tick=1),
            },
        }
        result = _MockResult(state_snapshots=states)
        obs = result_to_observer(result)
        assert obs.get_person_view("a2", tick=0) is None
        assert obs.get_person_view("a2", tick=1) is not None

    def test_delta_calc_across_ticks(self) -> None:
        # fear: 2 → 4 (delta_up since +2 > 1.0)
        states = {
            "a1": {
                0: _make_agent_state("a1", tick=0, fear=2.0),
                1: _make_agent_state("a1", tick=1, fear=4.0),
                2: _make_agent_state("a1", tick=2, fear=4.0),  # no delta
            }
        }
        result = _MockResult(state_snapshots=states)
        obs = result_to_observer(result)
        a_t0 = obs.get_person_view("a1", tick=0)
        a_t1 = obs.get_person_view("a1", tick=1)
        a_t2 = obs.get_person_view("a1", tick=2)
        assert a_t0.delta == []  # first tick — no delta
        assert "fear_up" in a_t1.delta
        assert a_t2.delta == []  # no change tick 1→2
