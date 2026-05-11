"""Tests for engine.observer.replay (Phase O4)."""

from __future__ import annotations

import pytest

from engine.observer.core import Observer
from engine.observer.replay import (
    ReplayCursor,
    auto_bookmark_turning_points,
    before_after_window,
    recent_window,
)
from engine.observer.snapshot_schema import (
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


def _make_stream() -> list[Snapshot]:
    """5-tick stream with 1 event + 1 turning point."""
    return [
        Snapshot(
            tick=t,
            active_events=["public_accusation"] if t in (2, 3) else [],
            world=WorldSnapshot(
                scarcity_pressure=0.1 if t == 0 else (0.5 if t >= 2 else 0.2)
            ),
            groups=[
                GroupSnapshot(
                    id="L1",
                    dominant_mode="saturation" if t < 4 else "recovery",
                )
            ],
        )
        for t in range(5)
    ]


class TestReplayCursorInit:
    def test_empty_observer_rejected(self) -> None:
        # Observer itself rejects empty list, so ReplayCursor too
        with pytest.raises(ValueError):
            Observer([])

    def test_starts_at_first_tick(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        assert cursor.current_tick == 0


class TestJumpAdvance:
    def test_jump_to_tick(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_tick(3)
        assert cursor.current_tick == 3

    def test_jump_invalid_tick(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        with pytest.raises(KeyError):
            cursor.jump_to_tick(99)

    def test_advance_forward(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        new_tick = cursor.advance(2)
        assert new_tick == 2
        assert cursor.current_tick == 2

    def test_advance_backward(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_tick(3)
        new_tick = cursor.advance(-2)
        assert new_tick == 1

    def test_advance_clamps_to_end(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        new_tick = cursor.advance(99)
        assert new_tick == 4  # last tick

    def test_advance_clamps_to_start(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_tick(2)
        new_tick = cursor.advance(-99)
        assert new_tick == 0

    def test_reset(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_tick(3)
        cursor.reset()
        assert cursor.current_tick == 0

    def test_jump_to_end(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_end()
        assert cursor.current_tick == 4


class TestEventJump:
    def test_jump_to_event_start(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        new_tick = cursor.jump_to_event_start("public_accusation")
        assert new_tick == 2  # first active tick

    def test_event_absent_raises(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        with pytest.raises(KeyError):
            cursor.jump_to_event_start("ghost_event")


class TestBookmark:
    def test_bookmark_current(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.jump_to_tick(2)
        cursor.bookmark("middle")
        assert cursor.list_bookmarks() == {"middle": 2}

    def test_bookmark_explicit_tick(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.bookmark("event_start", tick=3)
        assert cursor.list_bookmarks()["event_start"] == 3

    def test_jump_to_bookmark(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.bookmark("checkpoint", tick=4)
        cursor.jump_to_tick(0)
        cursor.jump_to_bookmark("checkpoint")
        assert cursor.current_tick == 4

    def test_bookmark_invalid_tick(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        with pytest.raises(KeyError):
            cursor.bookmark("bad", tick=99)

    def test_jump_to_unknown_bookmark(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        with pytest.raises(KeyError):
            cursor.jump_to_bookmark("nonexistent")

    def test_remove_bookmark(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.bookmark("x", tick=1)
        cursor.remove_bookmark("x")
        assert "x" not in cursor.list_bookmarks()

    def test_remove_nonexistent_noop(self) -> None:
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        cursor.remove_bookmark("nonexistent")  # should not raise


class TestAutoBookmarkTurningPoints:
    def test_recovery_turning_point_bookmarked(self) -> None:
        # Stream where group transitions saturation→recovery at tick 4
        obs = Observer(_make_stream())
        cursor = ReplayCursor(obs)
        bookmarks = auto_bookmark_turning_points(cursor)
        # Recovery turning point at tick 4 (saturation → recovery)
        assert "first_recovery_turning_point" in bookmarks
        assert bookmarks["first_recovery_turning_point"] == 4


class TestRecentWindow:
    def test_recent_window_full(self) -> None:
        obs = Observer(_make_stream())
        window = recent_window(obs, tick=4, window_size=3)
        assert len(window) == 3
        assert [s.tick for s in window] == [2, 3, 4]

    def test_recent_window_clamped(self) -> None:
        obs = Observer(_make_stream())
        window = recent_window(obs, tick=1, window_size=10)
        assert [s.tick for s in window] == [0, 1]

    def test_recent_window_invalid_tick(self) -> None:
        obs = Observer(_make_stream())
        with pytest.raises(KeyError):
            recent_window(obs, tick=99)


class TestBeforeAfterWindow:
    def test_split_around_pivot(self) -> None:
        obs = Observer(_make_stream())
        win = before_after_window(obs, pivot_tick=2, span=2)
        assert [s.tick for s in win["before"]] == [0, 1]
        assert [s.tick for s in win["pivot"]] == [2]
        assert [s.tick for s in win["after"]] == [3, 4]

    def test_invalid_pivot(self) -> None:
        obs = Observer(_make_stream())
        with pytest.raises(KeyError):
            before_after_window(obs, pivot_tick=99)
