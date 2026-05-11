"""Tests for scripts.observer.candidate_packet (Phase P2)."""

from __future__ import annotations

from engine.observer.candidate import StoryCandidate
from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)
from scripts.observer.candidate_packet import (
    CandidatePacket,
    build_packet,
    format_packet_compact,
    format_packet_markdown,
    format_packet_text,
)


def _make_stream() -> list[Snapshot]:
    return [
        Snapshot(
            tick=0,
            world=WorldSnapshot(crowd_mood="calm"),
            groups=[GroupSnapshot(id="L1", dominant_mode="low_activity")],
            agents=[AgentSnapshot(id="a1", role="follower")],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(crowd_mood="tense", blame_concentration=0.7),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.8)],
            agents=[AgentSnapshot(id="a1", role="follower", fear=7.0, delta=["fear_up"])],
        ),
        Snapshot(
            tick=2,
            active_events=["public_accusation"],
            world=WorldSnapshot(crowd_mood="agitated", blame_concentration=0.85),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.9)],
            agents=[AgentSnapshot(id="a1", role="follower", fear=8.0)],
        ),
    ]


def _make_candidate() -> StoryCandidate:
    return StoryCandidate(
        candidate_id="C01_t1",
        source_run="test_run",
        tick=1,
        tick_range=(0, 2),
        candidate_type="mixed",
        salience_score=2,
        signals=["pressure_spike", "agent_state_shift"],
        dominant_pressure="accusation",
        crowd_mood="tense",
        dominant_mode="saturation",
        agents_involved=["a1"],
        events_involved=["public_accusation"],
        rationale="Surfaced by pressure_spike, agent_state_shift",
    )


class TestBuildPacket:
    def test_packet_basic_fields(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        assert isinstance(packet, CandidatePacket)
        assert packet.candidate_id == "C01_t1"
        assert packet.source_run == "test_run"
        assert packet.candidate_type == "mixed"

    def test_lens_summaries_populated(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        assert packet.person_lens  # non-empty (a1 present in tick range)
        assert packet.event_lens
        assert packet.world_lens

    def test_potential_arcs(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        # has agents + events → all 3 arcs (Lee §3.4: person_arc / event_arc / world_arc)
        assert "person_arc" in packet.potential_arcs
        assert "event_arc" in packet.potential_arcs
        assert "world_arc" in packet.potential_arcs

    def test_render_recommended_for_strong_candidate(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.salience_score = 3  # strong
        packet = build_packet(cand, obs)
        assert packet.render_recommended is True
        assert packet.render_lens is not None

    def test_render_not_recommended_for_weak(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.salience_score = 1  # weak
        packet = build_packet(cand, obs)
        assert packet.render_recommended is False

    def test_no_agents_lens_handles(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.agents_involved = []
        packet = build_packet(cand, obs)
        assert "(인물 활동 신호 없음)" in packet.person_lens

    def test_no_events_lens_handles(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.events_involved = []
        packet = build_packet(cand, obs)
        assert "(활성 이벤트 없음)" in packet.event_lens


class TestFormatText:
    def test_format_text_contains_id(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        text = format_packet_text(packet)
        assert "C01_t1" in text
        assert "Why surfaced" in text
        assert "Person lens" in text
        assert "Event lens" in text
        assert "World lens" in text
        assert "Story potential" in text
        assert "Render link" in text
        assert "Human check" in text

    def test_format_text_includes_signals(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        text = format_packet_text(packet)
        assert "pressure_spike" in text


class TestFormatMarkdown:
    def test_format_markdown_headings(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        md = format_packet_markdown(packet)
        assert "## Candidate" in md
        assert "### Why surfaced" in md
        assert "### Person lens" in md
        assert "### Render link" in md
        assert "### Human check" in md


class TestFormatCompact:
    def test_format_compact_single_line(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        packet = build_packet(cand, obs)
        compact = format_packet_compact(packet)
        # Single line (no newlines)
        assert "\n" not in compact
        assert "C01_t1" in compact

    def test_format_compact_render_marker(self) -> None:
        obs = Observer(_make_stream())
        cand = _make_candidate()
        cand.salience_score = 3
        packet = build_packet(cand, obs)
        compact = format_packet_compact(packet)
        assert "render→" in compact
