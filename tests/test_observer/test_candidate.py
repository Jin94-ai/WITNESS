"""Tests for engine.observer.candidate (Phase P1)."""

from __future__ import annotations

from engine.observer.candidate import (
    StoryCandidate,
    extract_event_candidates,
    extract_person_candidates,
    extract_story_candidates,
    extract_world_candidates,
)
from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


def _make_stream() -> list[Snapshot]:
    """6-tick stream with mixed signals."""
    return [
        Snapshot(
            tick=0,
            world=WorldSnapshot(crowd_mood="calm"),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="low_activity"),
                GroupSnapshot(id="L2", dominant_mode="low_activity"),
            ],
            agents=[AgentSnapshot(id="a1"), AgentSnapshot(id="a2")],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="tense", blame_concentration=0.6, public_suspicion=0.4
            ),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.7),
                GroupSnapshot(id="L2", dominant_mode="recovery", tension=0.3),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=7.0, delta=["fear_up"]),
                AgentSnapshot(id="a2", fear=5.0, delta=["fear_up"]),
            ],
        ),
        Snapshot(
            tick=2,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="agitated", blame_concentration=0.85
            ),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.9),
                GroupSnapshot(id="L2", dominant_mode="mixed", tension=0.5),
            ],
            agents=[
                AgentSnapshot(id="a1", fear=8.0),
                AgentSnapshot(id="a2", fear=4.0, delta=["fear_down"]),
            ],
        ),
        Snapshot(
            tick=3,
            world=WorldSnapshot(crowd_mood="tense", blame_concentration=0.6),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.85),
                GroupSnapshot(id="L2", dominant_mode="recovery", tension=0.2),
            ],
            agents=[AgentSnapshot(id="a1"), AgentSnapshot(id="a2")],
        ),
        Snapshot(
            tick=4,
            world=WorldSnapshot(crowd_mood="calm", blame_concentration=0.2),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="recovery", tension=0.3),
                GroupSnapshot(id="L2", dominant_mode="recovery", tension=0.1),
            ],
            agents=[AgentSnapshot(id="a1"), AgentSnapshot(id="a2", delta=["fear_down"])],
        ),
        Snapshot(
            tick=5,
            world=WorldSnapshot(crowd_mood="calm"),
            groups=[
                GroupSnapshot(id="L1", dominant_mode="recovery", tension=0.1),
                GroupSnapshot(id="L2", dominant_mode="low_activity"),
            ],
            agents=[AgentSnapshot(id="a1"), AgentSnapshot(id="a2")],
        ),
    ]


class TestExtractStoryCandidates:
    def test_returns_top_k(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_story_candidates(obs, source_run="test", top_k=3)
        assert len(candidates) <= 3
        # All should have non-empty signals (top salient)
        assert all(isinstance(c, StoryCandidate) for c in candidates)

    def test_source_run_recorded(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_story_candidates(obs, source_run="peter_test", top_k=2)
        for c in candidates:
            assert c.source_run == "peter_test"

    def test_unique_ticks(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_story_candidates(obs, top_k=5)
        ticks = [c.tick for c in candidates]
        assert len(ticks) == len(set(ticks))


class TestExtractWorldCandidates:
    def test_world_type_forced(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_world_candidates(obs, top_k=2)
        for c in candidates:
            assert c.candidate_type == "world"

    def test_skips_low_signal(self) -> None:
        # Stream where world signal is always low — should produce 0 candidates
        snaps = [
            Snapshot(
                tick=t,
                world=WorldSnapshot(blame_concentration=0.05),
            )
            for t in range(3)
        ]
        obs = Observer(snaps)
        candidates = extract_world_candidates(obs, top_k=3)
        assert len(candidates) == 0

    def test_orders_by_world_signal(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_world_candidates(obs, top_k=3)
        # tick 2 has highest blame_concentration (0.85) — should rank first
        if candidates:
            assert candidates[0].tick == 2


class TestExtractPersonCandidates:
    def test_person_type_forced(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_person_candidates(obs, top_k=2)
        for c in candidates:
            assert c.candidate_type == "person"

    def test_focal_agent_recorded(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_person_candidates(obs, top_k=2)
        if candidates:
            # agents_involved should be narrowed to focal agent
            assert len(candidates[0].agents_involved) == 1


class TestExtractEventCandidates:
    def test_event_type_forced(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_event_candidates(obs, top_k=2)
        for c in candidates:
            assert c.candidate_type == "event"

    def test_no_events_returns_empty(self) -> None:
        snaps = [Snapshot(tick=t) for t in range(3)]
        obs = Observer(snaps)
        candidates = extract_event_candidates(obs, top_k=3)
        assert len(candidates) == 0

    def test_focal_event_recorded(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_event_candidates(obs, top_k=2)
        if candidates:
            assert candidates[0].events_involved == ["public_accusation"]
            assert candidates[0].tick_range == (1, 2)  # event span


class TestRationaleAndType:
    def test_rationale_non_empty(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_story_candidates(obs, top_k=3)
        for c in candidates:
            assert c.rationale  # non-empty

    def test_signals_recorded(self) -> None:
        obs = Observer(_make_stream())
        candidates = extract_story_candidates(obs, top_k=3)
        # At least top candidate should have signals
        if candidates:
            assert candidates[0].salience_score >= 1


class TestCandidateDataclass:
    def test_default_fields(self) -> None:
        c = StoryCandidate(
            candidate_id="C01",
            source_run="test",
            tick=10,
            tick_range=(8, 12),
            candidate_type="world",
        )
        assert c.salience_score == 0
        assert c.signals == []
        assert c.dominant_pressure == "none_clear"
        assert c.rationale == ""
