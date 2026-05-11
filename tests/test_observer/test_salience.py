"""Tests for engine.observer.salience."""

from __future__ import annotations

from engine.observer.salience import (
    detect_salience_tags,
    top_salient_moments,
    top_unstable_agents,
)
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


class TestDetectSalienceTags:
    def test_empty_stream(self) -> None:
        assert detect_salience_tags([], 0) == []

    def test_target_tick_absent(self) -> None:
        snaps = [Snapshot(tick=0)]
        assert detect_salience_tags(snaps, 99) == []

    def test_pressure_spike_detected(self) -> None:
        snaps = [
            Snapshot(tick=0, world=WorldSnapshot(scarcity_pressure=0.1)),
            Snapshot(tick=1, world=WorldSnapshot(scarcity_pressure=0.5)),
        ]
        tags = detect_salience_tags(snaps, target_tick=1)
        assert "pressure_spike" in tags

    def test_authority_vigilance_spike(self) -> None:
        snaps = [
            Snapshot(tick=0, world=WorldSnapshot(authority_vigilance=0.1)),
            Snapshot(tick=1, world=WorldSnapshot(authority_vigilance=0.5)),
        ]
        tags = detect_salience_tags(snaps, target_tick=1)
        assert "authority_vigilance_spike" in tags

    def test_cohort_split(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                groups=[
                    GroupSnapshot(id="L1", dominant_mode="saturation"),
                    GroupSnapshot(id="L2", dominant_mode="recovery"),
                ],
            )
        ]
        tags = detect_salience_tags(snaps, target_tick=0)
        assert "cohort_split" in tags

    def test_no_cohort_split_when_modes_match(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                groups=[
                    GroupSnapshot(id="L1", dominant_mode="saturation"),
                    GroupSnapshot(id="L2", dominant_mode="saturation"),
                ],
            )
        ]
        tags = detect_salience_tags(snaps, target_tick=0)
        assert "cohort_split" not in tags

    def test_recovery_turning_point(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                groups=[GroupSnapshot(id="L1", dominant_mode="saturation")],
            ),
            Snapshot(
                tick=1,
                groups=[GroupSnapshot(id="L1", dominant_mode="recovery")],
            ),
        ]
        tags = detect_salience_tags(snaps, target_tick=1)
        assert "recovery_turning_point" in tags

    def test_saturation_lock(self) -> None:
        # 5 consecutive ticks with same group in saturation
        snaps = [
            Snapshot(
                tick=t,
                groups=[GroupSnapshot(id="L1", dominant_mode="saturation")],
            )
            for t in range(6)
        ]
        tags = detect_salience_tags(snaps, target_tick=5)
        assert "saturation_lock" in tags

    def test_low_activity_tension(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                world=WorldSnapshot(crowd_mood="tense"),
                active_events=[],
            )
        ]
        tags = detect_salience_tags(snaps, target_tick=0)
        assert "low_activity_tension" in tags

    def test_agent_state_shift(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                agents=[AgentSnapshot(id="a1", delta=["fear_up"])],
            )
        ]
        tags = detect_salience_tags(snaps, target_tick=0)
        assert "agent_state_shift" in tags


class TestTopSalientMoments:
    def test_top_n_default(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                groups=[
                    GroupSnapshot(id="L1", dominant_mode="saturation"),
                    GroupSnapshot(id="L2", dominant_mode="recovery"),
                ],
            ),
        ]
        moments = top_salient_moments(snaps)
        assert len(moments) >= 1
        assert moments[0]["score"] >= 1
        assert "cohort_split" in moments[0]["tags"]

    def test_sorted_by_score_desc(self) -> None:
        # tick 1 has 1 tag (pressure_spike), tick 2 has 2 tags (cohort_split + agent_state_shift)
        snaps = [
            Snapshot(tick=0, world=WorldSnapshot(scarcity_pressure=0.1)),
            Snapshot(tick=1, world=WorldSnapshot(scarcity_pressure=0.5)),
            Snapshot(
                tick=2,
                groups=[
                    GroupSnapshot(id="L1", dominant_mode="saturation"),
                    GroupSnapshot(id="L2", dominant_mode="recovery"),
                ],
                agents=[AgentSnapshot(id="a1", delta=["fear_up"])],
            ),
        ]
        moments = top_salient_moments(snaps)
        assert moments[0]["tick"] == 2
        assert moments[0]["score"] >= 2

    def test_top_n_limit(self) -> None:
        # Many salient ticks, request top_n=2
        snaps = []
        for t in range(10):
            snaps.append(
                Snapshot(
                    tick=t,
                    groups=[
                        GroupSnapshot(id="L1", dominant_mode="saturation"),
                        GroupSnapshot(id="L2", dominant_mode="recovery"),
                    ],
                )
            )
        moments = top_salient_moments(snaps, top_n=2)
        assert len(moments) == 2


class TestTopUnstableAgents:
    def test_no_shifts_returns_empty(self) -> None:
        snaps = [
            Snapshot(tick=0, agents=[AgentSnapshot(id="a1")]),
        ]
        result = top_unstable_agents(snaps)
        assert result == []

    def test_ranks_by_shift_count(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                agents=[
                    AgentSnapshot(id="a1", delta=["fear_up"]),
                    AgentSnapshot(id="a2"),
                ],
            ),
            Snapshot(
                tick=1,
                agents=[
                    AgentSnapshot(id="a1", delta=["fear_up"]),
                    AgentSnapshot(id="a2", delta=["hope_down"]),
                ],
            ),
        ]
        result = top_unstable_agents(snaps, top_n=2)
        assert result[0]["agent_id"] == "a1"
        assert result[0]["score"] == 2
        assert result[1]["agent_id"] == "a2"
        assert result[1]["score"] == 1
