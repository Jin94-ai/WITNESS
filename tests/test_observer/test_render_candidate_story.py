"""Tests for scripts.observer.render_candidate_story (Phase P3)."""

from __future__ import annotations

import pytest

from engine.observer.candidate import StoryCandidate
from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)
from scripts.observer.render_candidate_story import (
    compare_lenses,
    render_candidate_story,
)


def _make_stream() -> list[Snapshot]:
    return [
        Snapshot(
            tick=t,
            active_events=["public_accusation"] if t in (1, 2) else [],
            world=WorldSnapshot(
                crowd_mood="tense" if t in (1, 2) else "calm",
                blame_concentration=0.7 if t in (1, 2) else 0.0,
            ),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation" if t >= 1 else "low_activity")],
            agents=[
                AgentSnapshot(
                    id="a1",
                    role="follower",
                    fear=2.0 + t,
                    delta=["fear_up"] if t == 1 else [],
                )
            ],
        )
        for t in range(4)
    ]


def _make_candidate(candidate_type: str = "world") -> StoryCandidate:
    return StoryCandidate(
        candidate_id="C01",
        source_run="test",
        tick=2,
        tick_range=(1, 3),
        candidate_type=candidate_type,
        agents_involved=["a1"],
        events_involved=["public_accusation"],
    )


class TestRenderCandidateStory:
    def test_world_lens(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        text = render_candidate_story(cand, obs, lens="world")
        assert "Story render" in text
        assert "world" in text.lower()
        assert "Narrative" in text
        assert "Detail" in text  # default detail=True

    def test_person_lens(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        text = render_candidate_story(cand, obs, lens="person")
        assert "person" in text.lower()
        assert "a1" in text

    def test_event_lens(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        text = render_candidate_story(cand, obs, lens="event")
        assert "event" in text.lower()
        assert "public_accusation" in text

    def test_detail_off(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        text = render_candidate_story(cand, obs, lens="world", detail=False)
        assert "Narrative" in text
        assert "Detail" not in text  # detail suppressed

    def test_invalid_lens_raises(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        with pytest.raises(ValueError, match="Unknown lens"):
            render_candidate_story(cand, obs, lens="invalid")  # type: ignore[arg-type]

    def test_no_agents_handled(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.agents_involved = []
        text = render_candidate_story(cand, obs, lens="person")
        assert "인물 정보 없음" in text

    def test_no_events_handled(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.events_involved = []
        text = render_candidate_story(cand, obs, lens="event")
        assert "활성 이벤트 없음" in text


class TestCompareLenses:
    def test_three_sections(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        text = compare_lenses(cand, obs)
        assert "Compare lenses" in text
        assert "[Person lens]" in text
        assert "[Event lens]" in text
        assert "[World lens]" in text

    def test_handles_missing_agents(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.agents_involved = []
        # Should not raise — uses "ghost" placeholder
        text = compare_lenses(cand, obs)
        # Person lens text mentions absent agent
        assert "ghost" in text
