"""Tests for engine.observer.snapshot_schema — Pydantic schema validity."""

from __future__ import annotations

import pytest

from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


class TestWorldSnapshot:
    def test_default_values(self) -> None:
        ws = WorldSnapshot()
        assert ws.crowd_mood == "calm"
        assert ws.blame_concentration == 0.0
        assert ws.public_suspicion == 0.0
        assert ws.authority_vigilance == 0.0
        assert ws.scarcity_pressure == 0.0

    def test_custom_values(self) -> None:
        ws = WorldSnapshot(
            crowd_mood="tense",
            blame_concentration=0.8,
            public_suspicion=0.7,
            authority_vigilance=0.4,
            scarcity_pressure=0.2,
        )
        assert ws.crowd_mood == "tense"
        assert ws.blame_concentration == 0.8

    def test_invalid_crowd_mood_rejected(self) -> None:
        with pytest.raises(Exception):
            WorldSnapshot(crowd_mood="invalid_mood")  # type: ignore[arg-type]

    def test_blame_concentration_out_of_range(self) -> None:
        with pytest.raises(Exception):
            WorldSnapshot(blame_concentration=1.5)


class TestGroupSnapshot:
    def test_minimal_required(self) -> None:
        gs = GroupSnapshot(id="L1")
        assert gs.id == "L1"
        assert gs.dominant_mode == "low_activity"
        assert gs.tension == 0.0
        assert gs.member_count == 0

    def test_full(self) -> None:
        gs = GroupSnapshot(
            id="L2",
            dominant_mode="saturation",
            tension=0.88,
            member_count=4,
        )
        assert gs.dominant_mode == "saturation"

    def test_negative_member_count_rejected(self) -> None:
        with pytest.raises(Exception):
            GroupSnapshot(id="L1", member_count=-1)


class TestAgentSnapshot:
    def test_minimal_required(self) -> None:
        a = AgentSnapshot(id="agent_1")
        assert a.id == "agent_1"
        assert a.role == "generic"
        assert a.fear == 0.0
        assert a.hope == 5.0
        assert a.shame_self == 0.0
        assert a.delta == []

    def test_with_delta(self) -> None:
        a = AgentSnapshot(
            id="agent_2",
            role="follower",
            fear=7.2,
            shame_self=6.1,
            delta=["fear_up", "shame_self_up"],
        )
        assert a.fear == 7.2
        assert "fear_up" in a.delta

    def test_fear_out_of_range(self) -> None:
        with pytest.raises(Exception):
            AgentSnapshot(id="x", fear=11.0)


class TestSnapshot:
    def test_minimal_required(self) -> None:
        s = Snapshot(tick=0)
        assert s.tick == 0
        assert s.active_events == []
        assert s.world.crowd_mood == "calm"
        assert s.groups == []
        assert s.agents == []
        assert s.salience_hints == []

    def test_full_construction(self) -> None:
        s = Snapshot(
            tick=17,
            active_events=["public_accusation"],
            world=WorldSnapshot(crowd_mood="tense", blame_concentration=0.82),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.88),
                GroupSnapshot(id="L2", dominant_mode="mixed", tension=0.64),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=7.2, shame_self=6.1),
                AgentSnapshot(id="a2", fear=4.8),
            ],
            salience_hints=["blame_target_shift"],
        )
        assert s.tick == 17
        assert s.world.blame_concentration == 0.82
        assert len(s.groups) == 2
        assert len(s.agents) == 2

    def test_get_agent_present(self) -> None:
        s = Snapshot(
            tick=0,
            agents=[AgentSnapshot(id="a1"), AgentSnapshot(id="a2")],
        )
        assert s.get_agent("a1") is not None
        assert s.get_agent("a1").id == "a1"

    def test_get_agent_absent(self) -> None:
        s = Snapshot(tick=0)
        assert s.get_agent("nonexistent") is None

    def test_get_group_present(self) -> None:
        s = Snapshot(
            tick=0,
            groups=[GroupSnapshot(id="L1"), GroupSnapshot(id="L2")],
        )
        assert s.get_group("L2") is not None

    def test_get_group_absent(self) -> None:
        s = Snapshot(tick=0)
        assert s.get_group("nonexistent") is None

    def test_negative_tick_rejected(self) -> None:
        with pytest.raises(Exception):
            Snapshot(tick=-1)
