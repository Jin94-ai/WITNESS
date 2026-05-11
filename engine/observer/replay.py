"""World Observer — Replay / Jump / Bookmark (Phase O4).

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §4.5.

실시간 stream 위에서 *시간 navigation* 제공:
- 특정 tick 점프
- event 시작점 점프
- turning point bookmark
- recent N ticks replay
- before/after 비교

ABSOLUTE Rule #1: no person hardcoding.
"""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.salience import detect_salience_tags
from engine.observer.snapshot_schema import Snapshot


class ReplayCursor:
    """Stream 위에서 위치 추적하는 cursor.

    Read-only navigation. Snapshot stream 자체를 변경하지 않음.

    Example:
        cursor = ReplayCursor(observer)
        cursor.jump_to_tick(50)
        snap = cursor.current()
        cursor.advance(10)
        snap = cursor.current()
        cursor.bookmark("turning_point_1")
        cursor.jump_to_bookmark("turning_point_1")
    """

    def __init__(self, observer: Observer) -> None:
        self._observer = observer
        self._ticks: list[int] = observer.list_ticks()
        if not self._ticks:
            raise ValueError("ReplayCursor requires non-empty observer")
        self._cursor_idx: int = 0
        self._bookmarks: dict[str, int] = {}

    @property
    def current_tick(self) -> int:
        return self._ticks[self._cursor_idx]

    def current(self) -> Snapshot:
        """Snapshot at current cursor position."""
        return self._observer._tick_index[self.current_tick]

    # ============================================================
    # Jump / advance
    # ============================================================

    def jump_to_tick(self, tick: int) -> None:
        """Jump cursor to tick (must be in stream)."""
        if tick not in self._ticks:
            raise KeyError(f"Tick {tick} not in stream")
        self._cursor_idx = self._ticks.index(tick)

    def advance(self, steps: int = 1) -> int:
        """Advance cursor by N ticks (or backward if negative). Returns new tick."""
        new_idx = max(0, min(len(self._ticks) - 1, self._cursor_idx + steps))
        self._cursor_idx = new_idx
        return self.current_tick

    def reset(self) -> None:
        """Reset cursor to first tick."""
        self._cursor_idx = 0

    def jump_to_end(self) -> None:
        """Jump cursor to last tick."""
        self._cursor_idx = len(self._ticks) - 1

    def jump_to_event_start(self, event_id: str) -> int:
        """Jump cursor to first tick where event was active. Raises KeyError if absent."""
        ev = self._observer.get_event_view(event_id)
        if ev["first_tick"] is None:
            raise KeyError(f"Event '{event_id}' not active in any tick")
        self.jump_to_tick(ev["first_tick"])
        return self.current_tick

    # ============================================================
    # Bookmark
    # ============================================================

    def bookmark(self, name: str, tick: int | None = None) -> int:
        """Bookmark current tick (or given tick). Returns bookmarked tick."""
        target = tick if tick is not None else self.current_tick
        if target not in self._ticks:
            raise KeyError(f"Tick {target} not in stream")
        self._bookmarks[name] = target
        return target

    def jump_to_bookmark(self, name: str) -> int:
        """Jump cursor to bookmarked tick. Raises KeyError if absent."""
        if name not in self._bookmarks:
            raise KeyError(f"Bookmark '{name}' not set")
        self.jump_to_tick(self._bookmarks[name])
        return self.current_tick

    def list_bookmarks(self) -> dict[str, int]:
        """Read-only view of bookmarks."""
        return dict(self._bookmarks)

    def remove_bookmark(self, name: str) -> None:
        """Remove a bookmark. No-op if absent."""
        self._bookmarks.pop(name, None)


# ============================================================
# Auto-bookmark salient turning points
# ============================================================


def auto_bookmark_turning_points(
    cursor: ReplayCursor,
    tags_of_interest: tuple[str, ...] = (
        "recovery_turning_point",
        "saturation_lock",
        "cohort_split",
        "pressure_spike",
    ),
) -> dict[str, int]:
    """Scan stream and auto-bookmark first occurrence of each salience tag.

    Returns dict of created bookmarks.
    """
    snapshots = [cursor._observer._tick_index[t] for t in cursor._ticks]
    seen: dict[str, int] = {}
    for tick in cursor._ticks:
        tags = detect_salience_tags(snapshots, tick)
        for tag in tags_of_interest:
            if tag in tags and tag not in seen:
                seen[tag] = tick
                cursor.bookmark(f"first_{tag}", tick)
    return {f"first_{tag}": t for tag, t in seen.items()}


# ============================================================
# Window helpers
# ============================================================


def recent_window(
    observer: Observer, tick: int, window_size: int = 10
) -> list[Snapshot]:
    """Get last N snapshots up to and including given tick."""
    if tick not in observer._tick_index:
        raise KeyError(f"Tick {tick} not in stream")
    ticks = observer.list_ticks()
    end_idx = ticks.index(tick)
    start_idx = max(0, end_idx - window_size + 1)
    return [observer._tick_index[t] for t in ticks[start_idx : end_idx + 1]]


def before_after_window(
    observer: Observer, pivot_tick: int, span: int = 5
) -> dict[str, list[Snapshot]]:
    """Split window around pivot into 'before' and 'after' lists.

    Returns:
        {"before": [...], "pivot": [...], "after": [...]}
    """
    if pivot_tick not in observer._tick_index:
        raise KeyError(f"Tick {pivot_tick} not in stream")
    ticks = observer.list_ticks()
    pivot_idx = ticks.index(pivot_tick)
    before_ticks = ticks[max(0, pivot_idx - span) : pivot_idx]
    after_ticks = ticks[pivot_idx + 1 : pivot_idx + 1 + span]
    return {
        "before": [observer._tick_index[t] for t in before_ticks],
        "pivot": [observer._tick_index[pivot_tick]],
        "after": [observer._tick_index[t] for t in after_ticks],
    }
