"""Tests for engine.observer.core — Observer 4-lens API."""

from __future__ import annotations

import pytest

from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


def _make_test_stream() -> list[Snapshot]:
    """3-tick test stream with 2 agents, 2 groups, 1 event."""
    return [
        Snapshot(
            tick=0,
            active_events=[],
            world=WorldSnapshot(crowd_mood="calm"),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="low_activity"),
                GroupSnapshot(id="L2", dominant_mode="low_activity"),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=3.0),
                AgentSnapshot(id="a2", fear=2.0),
            ],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="tense", blame_concentration=0.7, public_suspicion=0.5
            ),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.8),
                GroupSnapshot(id="L2", dominant_mode="mixed", tension=0.5),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=7.0, delta=["fear_up"]),
                AgentSnapshot(id="a2", fear=3.0),
            ],
            salience_hints=["pressure_spike"],
        ),
        Snapshot(
            tick=2,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="agitated", blame_concentration=0.85
            ),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.9),
                GroupSnapshot(id="L2", dominant_mode="recovery", tension=0.3),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=8.0),
                AgentSnapshot(id="a3", fear=5.0),  # new agent appears
            ],
        ),
    ]


class TestObserverInit:
    def test_empty_snapshots_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            Observer([])

    def test_unsorted_snapshots_get_sorted(self) -> None:
        stream = _make_test_stream()
        # Reverse order
        obs = Observer(list(reversed(stream)))
        assert obs.list_ticks() == [0, 1, 2]


class TestListing:
    def test_list_ticks(self) -> None:
        obs = Observer(_make_test_stream())
        assert obs.list_ticks() == [0, 1, 2]

    def test_list_agents_unique(self) -> None:
        obs = Observer(_make_test_stream())
        agents = obs.list_agents()
        assert "a1" in agents
        assert "a2" in agents
        assert "a3" in agents

    def test_list_groups(self) -> None:
        obs = Observer(_make_test_stream())
        groups = obs.list_groups()
        assert set(groups) == {"L1", "L2"}

    def test_list_events(self) -> None:
        obs = Observer(_make_test_stream())
        assert "public_accusation" in obs.list_events()

    def test_tick_range(self) -> None:
        obs = Observer(_make_test_stream())
        assert obs.tick_range == (0, 2)


class TestWorldView:
    def test_get_world_view_at_tick(self) -> None:
        obs = Observer(_make_test_stream())
        ws = obs.get_world_view(tick=1)
        assert ws.crowd_mood == "tense"
        assert ws.blame_concentration == 0.7

    def test_get_world_view_invalid_tick(self) -> None:
        obs = Observer(_make_test_stream())
        with pytest.raises(KeyError):
            obs.get_world_view(tick=99)

    def test_get_world_trace(self) -> None:
        obs = Observer(_make_test_stream())
        trace = obs.get_world_trace(tick_from=0, tick_to=2)
        assert len(trace) == 3
        assert trace[0][0] == 0
        assert trace[2][1].crowd_mood == "agitated"

    def test_get_world_trace_window(self) -> None:
        obs = Observer(_make_test_stream())
        trace = obs.get_world_trace(tick_from=1, tick_to=1)
        assert len(trace) == 1


class TestPersonView:
    def test_get_person_view_present(self) -> None:
        obs = Observer(_make_test_stream())
        a = obs.get_person_view("a1", tick=1)
        assert a is not None
        assert a.fear == 7.0

    def test_get_person_view_absent(self) -> None:
        obs = Observer(_make_test_stream())
        a = obs.get_person_view("a3", tick=1)  # a3 only exists at tick 2
        assert a is None

    def test_get_person_arc_continuous(self) -> None:
        obs = Observer(_make_test_stream())
        arc = obs.get_person_arc("a1")
        assert len(arc) == 3
        assert arc[0][0] == 0 and arc[0][1].fear == 3.0
        assert arc[2][1].fear == 8.0

    def test_get_person_arc_partial(self) -> None:
        obs = Observer(_make_test_stream())
        # a3 only at tick 2
        arc = obs.get_person_arc("a3")
        assert len(arc) == 1
        assert arc[0][0] == 2

    def test_get_person_arc_window(self) -> None:
        obs = Observer(_make_test_stream())
        arc = obs.get_person_arc("a1", tick_from=1, tick_to=2)
        assert len(arc) == 2


class TestGroupView:
    def test_get_group_view(self) -> None:
        obs = Observer(_make_test_stream())
        g = obs.get_group_view("L1", tick=1)
        assert g is not None
        assert g.dominant_mode == "saturation"

    def test_get_group_arc(self) -> None:
        obs = Observer(_make_test_stream())
        arc = obs.get_group_arc("L2")
        assert len(arc) == 3
        assert arc[2][1].dominant_mode == "recovery"


class TestEventView:
    def test_get_event_view_present(self) -> None:
        obs = Observer(_make_test_stream())
        ev = obs.get_event_view("public_accusation")
        assert ev["event_id"] == "public_accusation"
        assert ev["active_ticks"] == [1, 2]
        assert ev["first_tick"] == 1
        assert ev["last_tick"] == 2

    def test_get_event_view_absent(self) -> None:
        obs = Observer(_make_test_stream())
        ev = obs.get_event_view("nonexistent_event")
        assert ev["active_ticks"] == []
        assert ev["first_tick"] is None
        assert ev["last_tick"] is None

    def test_event_view_agents_present(self) -> None:
        obs = Observer(_make_test_stream())
        ev = obs.get_event_view("public_accusation")
        # tick 1: a1, a2; tick 2: a1, a3
        assert "a1" in ev["agent_ids_present"]
        assert "a2" in ev["agent_ids_present"]
        assert "a3" in ev["agent_ids_present"]


class TestSalienceWindow:
    def test_get_salience_window(self) -> None:
        obs = Observer(_make_test_stream())
        sw = obs.get_salience_window()
        # tick 1 has hint, others empty
        assert len(sw) == 1
        assert sw[0][0] == 1
        assert "pressure_spike" in sw[0][1]
