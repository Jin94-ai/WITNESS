"""Tests for engine/observer/candidate_curation.py — Phase Q1.

Per `docs/observer/CANDIDATE_CURATION_PLAN.md`.

Coverage:
    - assign_use_mode 3-bucket logic
    - pick_strongest_lens (type → lens, mixed fallback)
    - temporal_diversity_filter (greedy by salience)
    - near_duplicate_reduce (group adjacent + similar signals)
    - curate_candidates pipeline (3 buckets + temporal diversity)
"""

from __future__ import annotations

import pytest

from engine.observer.candidate import StoryCandidate
from engine.observer.candidate_curation import (
    CuratedCandidate,
    CuratedSet,
    assign_use_mode,
    curate_candidates,
    near_duplicate_reduce,
    pick_strongest_lens,
    temporal_diversity_filter,
)
from engine.observer.core import Observer
from engine.observer.recorder import SnapshotStream

# ============================================================
# Test fixtures — minimal observer stream
# ============================================================


@pytest.fixture
def low_activity_observer() -> Observer:
    """Build observer with low_activity baseline (no agent delta)."""
    stream = SnapshotStream()
    for t in range(20):
        stream.append_from_stats(
            tick=t,
            active_events=[],
            world_stats={
                "crowd_mood": "calm",
                "blame_concentration": 0.0,
                "public_suspicion": 0.0,
                "authority_vigilance": 0.0,
                "scarcity_pressure": 0.0,
            },
            group_stats_list=[
                {
                    "id": "G1",
                    "dominant_mode": "low_activity",
                    "tension": 0.1,
                    "member_count": 3,
                },
            ],
            agent_stats_list=[
                {"id": "agent_01", "role": "follower", "fear": 1.0, "hope": 5.0, "shame_self": 0.0},
            ],
        )
    return Observer(stream.snapshots)


@pytest.fixture
def active_observer() -> Observer:
    """Build observer with active dynamics (substantial state shifts)."""
    stream = SnapshotStream()
    for t in range(20):
        # Active period 5-10
        in_active = 5 <= t <= 10
        stream.append_from_stats(
            tick=t,
            active_events=["public_accusation"] if in_active else [],
            world_stats={
                "crowd_mood": "agitated" if in_active else "calm",
                "blame_concentration": 0.6 if in_active else 0.1,
                "public_suspicion": 0.5 if in_active else 0.0,
                "authority_vigilance": 0.4 if in_active else 0.1,
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
                {
                    "id": "agent_01",
                    "role": "follower",
                    "fear": 7.0 if in_active else 1.0,
                    "hope": 2.0 if in_active else 5.0,
                    "shame_self": 4.0 if in_active else 0.0,
                },
            ],
        )
    return Observer(stream.snapshots)


def _make_candidate(
    candidate_id: str,
    tick: int,
    candidate_type: str = "person",
    salience_score: int = 2,
    signals: list[str] | None = None,
    dominant_mode: str = "saturation",
    agents_involved: list[str] | None = None,
    events_involved: list[str] | None = None,
    tick_range: tuple[int, int] | None = None,
) -> StoryCandidate:
    """Construct a synthetic StoryCandidate for tests."""
    return StoryCandidate(
        candidate_id=candidate_id,
        source_run="test_run",
        tick=tick,
        tick_range=tick_range or (max(0, tick - 2), tick + 2),
        candidate_type=candidate_type,  # type: ignore[arg-type]
        salience_score=salience_score,
        signals=signals or ["cohort_split"],
        dominant_pressure="none_clear",
        crowd_mood="calm",
        dominant_mode=dominant_mode,
        agents_involved=agents_involved or ["agent_01"],
        events_involved=events_involved or [],
        rationale="test",
    )


# ============================================================
# pick_strongest_lens
# ============================================================


class TestPickStrongestLens:
    def test_person_type(self, active_observer: Observer) -> None:
        c = _make_candidate("c1", tick=7, candidate_type="person")
        assert pick_strongest_lens(c, active_observer) == "person"

    def test_event_type(self, active_observer: Observer) -> None:
        c = _make_candidate("c1", tick=7, candidate_type="event")
        assert pick_strongest_lens(c, active_observer) == "event"

    def test_world_type(self, active_observer: Observer) -> None:
        c = _make_candidate("c1", tick=7, candidate_type="world")
        assert pick_strongest_lens(c, active_observer) == "world"

    def test_mixed_falls_back_to_world_when_world_substantial(
        self, active_observer: Observer
    ) -> None:
        c = _make_candidate("c1", tick=7, candidate_type="mixed")
        # Active period has blame_concentration = 0.6 > 0.3 threshold
        assert pick_strongest_lens(c, active_observer) == "world"


# ============================================================
# assign_use_mode
# ============================================================


class TestAssignUseMode:
    def test_low_activity_hold_when_low_mode_and_weak_signal(
        self, low_activity_observer: Observer
    ) -> None:
        c = _make_candidate(
            "c1", tick=5, dominant_mode="low_activity", salience_score=1
        )
        assert assign_use_mode(c, low_activity_observer) == "low_activity_hold"

    def test_story_ready_when_substance_and_strong_signal(
        self, active_observer: Observer
    ) -> None:
        c = _make_candidate(
            "c1",
            tick=7,
            candidate_type="world",
            dominant_mode="saturation",
            salience_score=3,
        )
        # Active observer at tick 7: blame=0.6, mood=agitated → world substance ✓
        assert assign_use_mode(c, active_observer) == "story_ready"

    def test_observation_only_when_signal_but_no_substance(
        self, low_activity_observer: Observer
    ) -> None:
        c = _make_candidate(
            "c1",
            tick=5,
            candidate_type="world",
            dominant_mode="saturation",  # not low_activity
            salience_score=2,  # has signal
        )
        # low_activity_observer: world metrics all 0 → no world substance
        assert assign_use_mode(c, low_activity_observer) == "observation_only"


# ============================================================
# temporal_diversity_filter
# ============================================================


class TestTemporalDiversity:
    def test_min_gap_zero_returns_all(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, salience_score=3),
            _make_candidate("c2", tick=11, salience_score=2),
            _make_candidate("c3", tick=12, salience_score=1),
        ]
        result = temporal_diversity_filter(candidates, min_gap=0)
        assert len(result) == 3

    def test_filters_within_min_gap(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, salience_score=3),
            _make_candidate("c2", tick=11, salience_score=2),
            _make_candidate("c3", tick=12, salience_score=1),
        ]
        result = temporal_diversity_filter(candidates, min_gap=5)
        # c1 (highest score) kept, c2/c3 within 5 ticks → dropped
        assert len(result) == 1
        assert result[0].candidate_id == "c1"

    def test_keeps_well_separated(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, salience_score=3),
            _make_candidate("c2", tick=20, salience_score=2),
            _make_candidate("c3", tick=30, salience_score=1),
        ]
        result = temporal_diversity_filter(candidates, min_gap=5)
        assert len(result) == 3

    def test_greedy_picks_high_score_first(self) -> None:
        # Lower-score earlier candidate, higher-score later
        candidates = [
            _make_candidate("c_low", tick=10, salience_score=1),
            _make_candidate("c_high", tick=12, salience_score=5),
        ]
        result = temporal_diversity_filter(candidates, min_gap=5)
        # c_high picked first, then c_low blocked (within 5 ticks)
        assert len(result) == 1
        assert result[0].candidate_id == "c_high"


# ============================================================
# near_duplicate_reduce
# ============================================================


class TestNearDuplicateReduce:
    def test_empty_returns_empty(self) -> None:
        assert near_duplicate_reduce([]) == []

    def test_single_candidate_no_grouping(self) -> None:
        c = _make_candidate("c1", tick=10)
        result = near_duplicate_reduce([c])
        assert len(result) == 1
        rep, related = result[0]
        assert rep.candidate_id == "c1"
        assert related == []

    def test_groups_adjacent_with_same_signals(self) -> None:
        # Same signals + tick gap <= 3 → same group
        candidates = [
            _make_candidate("c1", tick=10, signals=["cohort_split"], salience_score=3),
            _make_candidate("c2", tick=11, signals=["cohort_split"], salience_score=2),
            _make_candidate("c3", tick=12, signals=["cohort_split"], salience_score=1),
        ]
        result = near_duplicate_reduce(candidates, tick_window=3)
        assert len(result) == 1
        rep, related = result[0]
        assert rep.candidate_id == "c1"  # highest salience
        assert set(related) == {"c2", "c3"}

    def test_separates_distant_ticks(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, signals=["cohort_split"]),
            _make_candidate("c2", tick=20, signals=["cohort_split"]),
        ]
        result = near_duplicate_reduce(candidates, tick_window=3)
        assert len(result) == 2

    def test_separates_different_signals(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, signals=["cohort_split"]),
            _make_candidate("c2", tick=11, signals=["agent_state_shift"]),
        ]
        # No overlap → separate groups
        result = near_duplicate_reduce(candidates, signal_overlap=0.5)
        assert len(result) == 2

    def test_separates_different_types(self) -> None:
        candidates = [
            _make_candidate("c1", tick=10, candidate_type="person", signals=["cohort_split"]),
            _make_candidate("c2", tick=11, candidate_type="world", signals=["cohort_split"]),
        ]
        result = near_duplicate_reduce(candidates)
        # Different candidate_type → separate groups
        assert len(result) == 2


# ============================================================
# curate_candidates pipeline
# ============================================================


class TestCurateCandidates:
    def test_returns_curated_set(self, active_observer: Observer) -> None:
        candidates = [
            _make_candidate("c1", tick=7, candidate_type="world", salience_score=3),
        ]
        result = curate_candidates(candidates, active_observer)
        assert isinstance(result, CuratedSet)
        assert result.total_count() == 1

    def test_buckets_assigned(self, active_observer: Observer) -> None:
        candidates = [
            # Story-ready: active period + signal + substance
            _make_candidate(
                "sr1", tick=7, candidate_type="world", salience_score=3,
            ),
            # Low activity hold: low_mode + weak signal
            _make_candidate(
                "la1", tick=15, dominant_mode="low_activity", salience_score=1,
                signals=[], tick_range=(13, 17),
            ),
        ]
        result = curate_candidates(candidates, active_observer)
        assert any(cc.candidate.candidate_id == "sr1" for cc in result.story_ready)
        assert any(
            cc.candidate.candidate_id == "la1" for cc in result.low_activity_hold
        )

    def test_temporal_diversity_demotes_to_observation_only(
        self, active_observer: Observer
    ) -> None:
        # Two story-ready candidates within min_gap → second demoted
        # Need different signal sets so near_dup_reduce doesn't merge them
        candidates = [
            _make_candidate(
                "sr1", tick=6, candidate_type="world", salience_score=3,
                signals=["cohort_split"],
            ),
            _make_candidate(
                "sr2", tick=8, candidate_type="world", salience_score=3,
                signals=["agent_state_shift"],  # different signal — no near-dup merge
            ),
        ]
        result = curate_candidates(candidates, active_observer, min_tick_gap=5)
        # First (or higher-id tiebreak) kept in story_ready,
        # other demoted to observation_only
        sr_ids = {cc.candidate.candidate_id for cc in result.story_ready}
        oo_ids = {cc.candidate.candidate_id for cc in result.observation_only}
        assert len(sr_ids) == 1
        assert len(oo_ids) == 1
        assert sr_ids | oo_ids == {"sr1", "sr2"}

    def test_curated_candidate_has_metadata(
        self, active_observer: Observer
    ) -> None:
        candidates = [
            _make_candidate("c1", tick=7, candidate_type="world", salience_score=3),
        ]
        result = curate_candidates(candidates, active_observer)
        all_cc = (
            result.story_ready
            + result.observation_only
            + result.low_activity_hold
        )
        assert len(all_cc) == 1
        cc = all_cc[0]
        assert isinstance(cc, CuratedCandidate)
        assert cc.use_mode in ("story_ready", "observation_only", "low_activity_hold")
        assert cc.strongest_lens in ("person", "event", "world")
        assert isinstance(cc.related_candidate_ids, list)

    def test_near_duplicates_collapsed(
        self, active_observer: Observer
    ) -> None:
        # 3 adjacent candidates with same signals — should collapse to 1
        candidates = [
            _make_candidate(
                "c1", tick=6, candidate_type="world",
                signals=["cohort_split"], salience_score=3,
            ),
            _make_candidate(
                "c2", tick=7, candidate_type="world",
                signals=["cohort_split"], salience_score=2,
            ),
            _make_candidate(
                "c3", tick=8, candidate_type="world",
                signals=["cohort_split"], salience_score=1,
            ),
        ]
        result = curate_candidates(candidates, active_observer)
        # All collapsed into 1 representative; its related = [c2, c3] or similar
        all_cc = (
            result.story_ready
            + result.observation_only
            + result.low_activity_hold
        )
        assert len(all_cc) == 1
        rep_cc = all_cc[0]
        assert len(rep_cc.related_candidate_ids) == 2
