"""Tests for engine.observer.recorder."""

from __future__ import annotations

from engine.observer.recorder import (
    SnapshotStream,
    build_agent_snapshot,
    build_group_snapshot,
    build_world_snapshot,
    record_snapshot,
)


class TestBuildHelpers:
    def test_build_world_snapshot_defaults(self) -> None:
        ws = build_world_snapshot({})
        assert ws.crowd_mood == "calm"

    def test_build_world_snapshot_custom(self) -> None:
        ws = build_world_snapshot(
            {
                "crowd_mood": "tense",
                "blame_concentration": 0.7,
                "scarcity_pressure": 0.3,
            }
        )
        assert ws.crowd_mood == "tense"
        assert ws.blame_concentration == 0.7
        assert ws.scarcity_pressure == 0.3

    def test_build_group_snapshot(self) -> None:
        gs = build_group_snapshot(
            {"id": "L1", "dominant_mode": "saturation", "tension": 0.9, "member_count": 4}
        )
        assert gs.id == "L1"
        assert gs.dominant_mode == "saturation"

    def test_build_agent_snapshot_no_delta(self) -> None:
        a = build_agent_snapshot({"id": "a1", "fear": 5.0})
        assert a.id == "a1"
        assert a.delta == []

    def test_build_agent_snapshot_with_delta_up(self) -> None:
        current = {"id": "a1", "fear": 7.0, "shame_self": 5.0}
        previous = {"id": "a1", "fear": 5.0, "shame_self": 5.0}
        a = build_agent_snapshot(current, previous)
        assert "fear_up" in a.delta
        assert "shame_self_up" not in a.delta

    def test_build_agent_snapshot_with_delta_down(self) -> None:
        current = {"id": "a1", "hope": 3.0}
        previous = {"id": "a1", "hope": 7.0}
        a = build_agent_snapshot(current, previous)
        assert "hope_down" in a.delta

    def test_build_agent_snapshot_below_threshold(self) -> None:
        current = {"id": "a1", "fear": 5.5}
        previous = {"id": "a1", "fear": 5.0}
        # diff = 0.5 < threshold 1.0
        a = build_agent_snapshot(current, previous)
        assert a.delta == []


class TestRecordSnapshot:
    def test_minimal_record(self) -> None:
        snap = record_snapshot(tick=10)
        assert snap.tick == 10
        assert snap.world.crowd_mood == "calm"
        assert snap.agents == []
        assert snap.groups == []

    def test_full_record(self) -> None:
        snap = record_snapshot(
            tick=17,
            active_events=["public_accusation"],
            world_stats={"crowd_mood": "tense", "blame_concentration": 0.82},
            group_stats_list=[
                {"id": "L1", "dominant_mode": "saturation", "tension": 0.88},
                {"id": "L2", "dominant_mode": "mixed"},
            ],
            agent_stats_list=[
                {"id": "a1", "fear": 7.0},
                {"id": "a2", "fear": 4.0},
            ],
            salience_hints=["blame_target_shift"],
        )
        assert snap.tick == 17
        assert "public_accusation" in snap.active_events
        assert len(snap.groups) == 2
        assert len(snap.agents) == 2
        assert snap.salience_hints == ["blame_target_shift"]

    def test_delta_via_previous_agent_stats(self) -> None:
        snap = record_snapshot(
            tick=5,
            agent_stats_list=[{"id": "a1", "fear": 7.0}],
            previous_agent_stats={"a1": {"id": "a1", "fear": 5.0}},
        )
        a = snap.get_agent("a1")
        assert a is not None
        assert "fear_up" in a.delta


class TestSnapshotStream:
    def test_empty_stream(self) -> None:
        stream = SnapshotStream()
        assert len(stream) == 0
        assert stream.snapshots == []

    def test_append_from_stats_tracks_delta_across_ticks(self) -> None:
        stream = SnapshotStream()
        # tick 0: fear=5
        stream.append_from_stats(
            tick=0,
            agent_stats_list=[{"id": "a1", "fear": 5.0}],
        )
        # tick 1: fear=7 → delta should detect fear_up vs tick 0
        stream.append_from_stats(
            tick=1,
            agent_stats_list=[{"id": "a1", "fear": 7.0}],
        )
        # tick 2: fear=7 → no delta (no change)
        stream.append_from_stats(
            tick=2,
            agent_stats_list=[{"id": "a1", "fear": 7.0}],
        )
        assert len(stream) == 3
        snaps = stream.snapshots
        # tick 0 has no previous → no delta
        assert snaps[0].agents[0].delta == []
        # tick 1 has fear_up
        assert "fear_up" in snaps[1].agents[0].delta
        # tick 2 has no delta
        assert snaps[2].agents[0].delta == []

    def test_snapshots_property_returns_copy(self) -> None:
        stream = SnapshotStream()
        stream.append_from_stats(tick=0)
        snaps_a = stream.snapshots
        snaps_b = stream.snapshots
        # Different list instances (copies)
        assert snaps_a is not snaps_b
        # Same content
        assert len(snaps_a) == len(snaps_b)
