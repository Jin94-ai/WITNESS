"""Tests for Phase Q3 Packet schema v2 — curation fields.

Per `docs/observer/CANDIDATE_CURATION_PLAN.md` §Phase Q3.

Coverage:
    - build_curated_packet attaches use_mode + strongest_lens + related
    - format_packet_text shows curation block when present, hides when None
    - format_packet_compact shows use/lens
    - Backward compat: build_packet without curation has None fields
"""

from __future__ import annotations

import pytest

from engine.observer.candidate import StoryCandidate
from engine.observer.candidate_curation import (
    CuratedCandidate,
    curate_candidates,
)
from engine.observer.core import Observer
from engine.observer.recorder import SnapshotStream
from scripts.observer.candidate_packet import (
    build_curated_packet,
    build_packet,
    format_packet_compact,
    format_packet_markdown,
    format_packet_text,
)


@pytest.fixture
def observer() -> Observer:
    """Active observer with substantial world dynamics."""
    stream = SnapshotStream()
    for t in range(15):
        in_active = 5 <= t <= 10
        stream.append_from_stats(
            tick=t,
            active_events=["public_accusation"] if in_active else [],
            world_stats={
                "crowd_mood": "agitated" if in_active else "calm",
                "blame_concentration": 0.6 if in_active else 0.0,
                "public_suspicion": 0.5 if in_active else 0.0,
                "authority_vigilance": 0.4 if in_active else 0.0,
                "scarcity_pressure": 0.0,
            },
            group_stats_list=[
                {
                    "id": "G1",
                    "dominant_mode": "saturation" if in_active else "low_activity",
                    "tension": 0.8 if in_active else 0.1,
                    "member_count": 3,
                },
            ],
            agent_stats_list=[
                {"id": "agent_01", "role": "follower", "fear": 7.0 if in_active else 1.0,
                 "hope": 2.0, "shame_self": 4.0 if in_active else 0.0},
            ],
        )
    return Observer(stream.snapshots)


def _candidate(cid: str, tick: int) -> StoryCandidate:
    return StoryCandidate(
        candidate_id=cid,
        source_run="test",
        tick=tick,
        tick_range=(max(0, tick - 2), tick + 2),
        candidate_type="world",
        salience_score=3,
        signals=["cohort_split", "saturation_lock"],
        dominant_pressure="accusation",
        crowd_mood="agitated",
        dominant_mode="saturation",
        agents_involved=["agent_01"],
        events_involved=["public_accusation"],
        rationale="test",
    )


class TestBackwardCompat:
    def test_build_packet_curation_fields_default_none(
        self, observer: Observer
    ) -> None:
        c = _candidate("c1", tick=7)
        packet = build_packet(c, observer)
        assert packet.use_mode is None
        assert packet.strongest_lens is None
        assert packet.related_candidate_ids == []


class TestBuildCuratedPacket:
    def test_attaches_curation_metadata(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=["c2", "c3"],
        )
        packet = build_curated_packet(cc, observer)
        assert packet.use_mode == "story_ready"
        assert packet.strongest_lens == "world"
        assert packet.related_candidate_ids == ["c2", "c3"]

    def test_pipeline_curation_then_packet(self, observer: Observer) -> None:
        candidates = [_candidate("c1", tick=7)]
        curated = curate_candidates(candidates, observer)
        all_cc = (
            curated.story_ready
            + curated.observation_only
            + curated.low_activity_hold
        )
        assert len(all_cc) == 1
        packet = build_curated_packet(all_cc[0], observer)
        assert packet.use_mode in (
            "story_ready",
            "observation_only",
            "low_activity_hold",
        )


class TestFormatTextCuration:
    def test_curation_block_when_present(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=[],
        )
        packet = build_curated_packet(cc, observer)
        text = format_packet_text(packet)
        assert "[Use mode]" in text
        assert "story_ready" in text
        assert "[Strongest lens]" in text
        assert "world" in text

    def test_no_curation_block_when_absent(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        packet = build_packet(c, observer)
        text = format_packet_text(packet)
        assert "[Use mode]" not in text
        assert "[Strongest lens]" not in text

    def test_related_block_when_related_present(
        self, observer: Observer
    ) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=["c2", "c3"],
        )
        packet = build_curated_packet(cc, observer)
        text = format_packet_text(packet)
        assert "[Related candidates]" in text
        assert "c2" in text
        assert "c3" in text

    def test_no_related_block_when_empty(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=[],
        )
        packet = build_curated_packet(cc, observer)
        text = format_packet_text(packet)
        assert "[Related candidates]" not in text


class TestFormatMarkdownCuration:
    def test_markdown_curation_section(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=["c2"],
        )
        packet = build_curated_packet(cc, observer)
        md = format_packet_markdown(packet)
        assert "### Curation" in md
        assert "Use mode: `story_ready`" in md
        assert "Strongest lens: `world`" in md
        assert "Related" in md


class TestFormatCompactCuration:
    def test_compact_uses_use_mode_when_curated(
        self, observer: Observer
    ) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=[],
        )
        packet = build_curated_packet(cc, observer)
        compact = format_packet_compact(packet)
        assert "use=story_ready" in compact
        assert "lens=world" in compact

    def test_compact_shows_related_count(self, observer: Observer) -> None:
        c = _candidate("c1", tick=7)
        cc = CuratedCandidate(
            candidate=c,
            use_mode="story_ready",
            strongest_lens="world",
            related_candidate_ids=["c2", "c3"],
        )
        packet = build_curated_packet(cc, observer)
        compact = format_packet_compact(packet)
        assert "+2 related" in compact

    def test_compact_falls_back_to_render_when_no_curation(
        self, observer: Observer
    ) -> None:
        c = _candidate("c1", tick=7)
        packet = build_packet(c, observer)
        compact = format_packet_compact(packet)
        # Falls back to render→ format
        assert "use=" not in compact
