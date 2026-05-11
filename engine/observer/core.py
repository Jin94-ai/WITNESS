"""World Observer — Core API.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §4.

Read-only observation lens API. snapshot stream을 받아 다양한 view 제공.

ABSOLUTE Rule #1: no person hardcoding.
ABSOLUTE Rule #6: existing engine API 무수정.
원칙: 관찰기 ≠ 평가기. 관측 태그까지만, 해석/판정 안 함.
"""

from __future__ import annotations

from typing import Any

from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)


class Observer:
    """Read-only view over snapshot stream.

    Initialize with pre-recorded snapshots. Provides 4 lenses:
    World / Person / Group / Event + listing/filtering helpers.

    Example:
        snapshots = [s1, s2, s3, ...]  # built via recorder
        obs = Observer(snapshots)
        world_at_t = obs.get_world_view(tick=10)
        agent_arc = obs.get_person_view("agent_001", tick=10)
        ripple = obs.get_event_view("public_accusation")
    """

    def __init__(self, snapshots: list[Snapshot]) -> None:
        if not snapshots:
            raise ValueError("Observer requires non-empty snapshot list")
        # Sort by tick to ensure order even if input unordered.
        self._snapshots: list[Snapshot] = sorted(snapshots, key=lambda s: s.tick)
        self._tick_index: dict[int, Snapshot] = {s.tick: s for s in self._snapshots}

    # ============================================================
    # Listing / metadata
    # ============================================================

    def list_ticks(self) -> list[int]:
        """All ticks present in snapshot stream."""
        return [s.tick for s in self._snapshots]

    def list_agents(self) -> list[str]:
        """All unique agent IDs across all ticks."""
        seen: dict[str, None] = {}
        for s in self._snapshots:
            for a in s.agents:
                seen[a.id] = None
        return list(seen.keys())

    def list_groups(self) -> list[str]:
        """All unique group IDs across all ticks."""
        seen: dict[str, None] = {}
        for s in self._snapshots:
            for g in s.groups:
                seen[g.id] = None
        return list(seen.keys())

    def list_events(self) -> list[str]:
        """All unique event IDs across all ticks."""
        seen: dict[str, None] = {}
        for s in self._snapshots:
            for ev in s.active_events:
                seen[ev] = None
        return list(seen.keys())

    @property
    def tick_range(self) -> tuple[int, int]:
        """(min_tick, max_tick) range."""
        return self._snapshots[0].tick, self._snapshots[-1].tick

    # ============================================================
    # Lens 1 — World View
    # ============================================================

    def get_world_view(self, tick: int) -> WorldSnapshot:
        """World-level state at one tick."""
        snap = self._get_snapshot(tick)
        return snap.world

    def get_world_trace(
        self, tick_from: int | None = None, tick_to: int | None = None
    ) -> list[tuple[int, WorldSnapshot]]:
        """World view trajectory across tick window."""
        snaps = self._window(tick_from, tick_to)
        return [(s.tick, s.world) for s in snaps]

    # ============================================================
    # Lens 2 — Person View
    # ============================================================

    def get_person_view(self, agent_id: str, tick: int) -> AgentSnapshot | None:
        """One agent's state at one tick. Returns None if agent absent."""
        snap = self._get_snapshot(tick)
        return snap.get_agent(agent_id)

    def get_person_arc(
        self,
        agent_id: str,
        tick_from: int | None = None,
        tick_to: int | None = None,
    ) -> list[tuple[int, AgentSnapshot]]:
        """Agent's state arc across tick window. Skips ticks where agent absent."""
        result: list[tuple[int, AgentSnapshot]] = []
        for s in self._window(tick_from, tick_to):
            agent = s.get_agent(agent_id)
            if agent is not None:
                result.append((s.tick, agent))
        return result

    # ============================================================
    # Lens 3 — Group View
    # ============================================================

    def get_group_view(self, group_id: str, tick: int) -> GroupSnapshot | None:
        """Group state at one tick. Returns None if group absent."""
        snap = self._get_snapshot(tick)
        return snap.get_group(group_id)

    def get_group_arc(
        self,
        group_id: str,
        tick_from: int | None = None,
        tick_to: int | None = None,
    ) -> list[tuple[int, GroupSnapshot]]:
        """Group state arc across window."""
        result: list[tuple[int, GroupSnapshot]] = []
        for s in self._window(tick_from, tick_to):
            group = s.get_group(group_id)
            if group is not None:
                result.append((s.tick, group))
        return result

    # ============================================================
    # Lens 4 — Event View
    # ============================================================

    def get_event_view(self, event_id: str) -> dict[str, Any]:
        """Event ripple — all ticks where event was active.

        Returns dict:
            event_id: str
            active_ticks: list[int]  — 활성 tick list
            first_tick: int | None  — 첫 등장 tick
            last_tick: int | None  — 마지막 활성 tick
            agent_ids_present: list[str]  — 활성 동안 등장한 agent IDs
        """
        active_ticks = [
            s.tick for s in self._snapshots if event_id in s.active_events
        ]
        agent_ids: dict[str, None] = {}
        for s in self._snapshots:
            if event_id in s.active_events:
                for a in s.agents:
                    agent_ids[a.id] = None
        return {
            "event_id": event_id,
            "active_ticks": active_ticks,
            "first_tick": active_ticks[0] if active_ticks else None,
            "last_tick": active_ticks[-1] if active_ticks else None,
            "agent_ids_present": list(agent_ids.keys()),
        }

    # ============================================================
    # Salience window
    # ============================================================

    def get_salience_window(
        self, tick_from: int | None = None, tick_to: int | None = None
    ) -> list[tuple[int, list[str]]]:
        """Salience hints in window.

        Returns list of (tick, hints_list) for ticks where hints present.
        """
        result: list[tuple[int, list[str]]] = []
        for s in self._window(tick_from, tick_to):
            if s.salience_hints:
                result.append((s.tick, list(s.salience_hints)))
        return result

    # ============================================================
    # Internal helpers
    # ============================================================

    def _get_snapshot(self, tick: int) -> Snapshot:
        """Get snapshot by tick. Raises KeyError if absent."""
        if tick not in self._tick_index:
            available = self.list_ticks()
            raise KeyError(
                f"Tick {tick} not in snapshot stream. Available: {available[:5]}..."
                if len(available) > 5
                else f"Tick {tick} not in snapshot stream. Available: {available}"
            )
        return self._tick_index[tick]

    def _window(
        self, tick_from: int | None, tick_to: int | None
    ) -> list[Snapshot]:
        """Filter snapshots to [tick_from, tick_to] inclusive. None = open-ended."""
        lo = tick_from if tick_from is not None else self._snapshots[0].tick
        hi = tick_to if tick_to is not None else self._snapshots[-1].tick
        return [s for s in self._snapshots if lo <= s.tick <= hi]
