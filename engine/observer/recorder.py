"""World Observer — snapshot recorder.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §3.

Post-hoc snapshot 생성:
- input: tick, world stats dict, group stats list, agent state dict, prev agent state dict (optional)
- output: Snapshot (Pydantic)

ABSOLUTE Rule #1: no person hardcoding. recorder는 *generic schema*로 받음.
ABSOLUTE Rule #6: existing simulation API 무수정. recorder는 외부 helper.
"""

from __future__ import annotations

from typing import Any

from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)

# ============================================================
# Delta detection — tick-over-tick 주요 변화 tag
# ============================================================

# Threshold for "significant" tick-over-tick agent state change
_AGENT_DELTA_THRESHOLD: float = 1.0

_AGENT_FIELDS_TRACKED: tuple[str, ...] = ("fear", "hope", "shame_self")


def _detect_agent_delta(
    current: dict[str, Any],
    previous: dict[str, Any] | None,
) -> list[str]:
    """직전 tick 대비 agent state delta 감지.

    Returns list of tags like ['fear_up', 'shame_self_down'].
    """
    if previous is None:
        return []
    deltas: list[str] = []
    for field in _AGENT_FIELDS_TRACKED:
        cur = current.get(field, 0.0)
        prev = previous.get(field, 0.0)
        diff = cur - prev
        if diff > _AGENT_DELTA_THRESHOLD:
            deltas.append(f"{field}_up")
        elif diff < -_AGENT_DELTA_THRESHOLD:
            deltas.append(f"{field}_down")
    return deltas


# ============================================================
# Recorder API
# ============================================================


def build_world_snapshot(world_stats: dict[str, Any]) -> WorldSnapshot:
    """Build WorldSnapshot from generic dict.

    Expected keys (all optional, defaults applied):
        crowd_mood: str
        blame_concentration: float (0.0-1.0)
        public_suspicion: float (0.0-1.0)
        authority_vigilance: float (0.0-1.0)
        scarcity_pressure: float (0.0-1.0)
    """
    return WorldSnapshot(
        crowd_mood=world_stats.get("crowd_mood", "calm"),
        blame_concentration=world_stats.get("blame_concentration", 0.0),
        public_suspicion=world_stats.get("public_suspicion", 0.0),
        authority_vigilance=world_stats.get("authority_vigilance", 0.0),
        scarcity_pressure=world_stats.get("scarcity_pressure", 0.0),
    )


def build_group_snapshot(group_stats: dict[str, Any]) -> GroupSnapshot:
    """Build GroupSnapshot from generic dict.

    Required keys:
        id: str
    Optional keys (defaults applied):
        dominant_mode: str
        tension: float
        member_count: int
    """
    return GroupSnapshot(
        id=group_stats["id"],
        dominant_mode=group_stats.get("dominant_mode", "low_activity"),
        tension=group_stats.get("tension", 0.0),
        member_count=group_stats.get("member_count", 0),
    )


def build_agent_snapshot(
    agent_stats: dict[str, Any],
    previous_agent_stats: dict[str, Any] | None = None,
) -> AgentSnapshot:
    """Build AgentSnapshot from generic dict + optional previous tick state.

    Required keys:
        id: str
    Optional keys (defaults applied):
        role: str (generic role tag)
        fear: float (0.0-10.0)
        hope: float (0.0-10.0)
        shame_self: float (0.0-10.0)

    delta는 previous_agent_stats가 주어지면 자동 계산.
    """
    delta = _detect_agent_delta(agent_stats, previous_agent_stats)
    return AgentSnapshot(
        id=agent_stats["id"],
        role=agent_stats.get("role", "generic"),
        fear=agent_stats.get("fear", 0.0),
        hope=agent_stats.get("hope", 5.0),
        shame_self=agent_stats.get("shame_self", 0.0),
        delta=delta,
    )


def record_snapshot(
    *,
    tick: int,
    active_events: list[str] | None = None,
    world_stats: dict[str, Any] | None = None,
    group_stats_list: list[dict[str, Any]] | None = None,
    agent_stats_list: list[dict[str, Any]] | None = None,
    previous_agent_stats: dict[str, dict[str, Any]] | None = None,
    salience_hints: list[str] | None = None,
) -> Snapshot:
    """One tick's complete snapshot 빌드.

    Lee directive §5.1 schema 매핑.

    Args:
        tick: Simulation tick number
        active_events: 이 tick에 활성 이벤트 ID list
        world_stats: WorldSnapshot 빌드용 dict
        group_stats_list: GroupSnapshot list 빌드용
        agent_stats_list: AgentSnapshot list 빌드용
        previous_agent_stats: {agent_id: prev_stats_dict} — delta 계산용
        salience_hints: 이 tick의 salience tag (recorder는 안 만듬, 외부에서 주입)

    Returns:
        Snapshot Pydantic model
    """
    world = (
        build_world_snapshot(world_stats) if world_stats else WorldSnapshot()
    )
    groups = (
        [build_group_snapshot(gs) for gs in group_stats_list]
        if group_stats_list
        else []
    )
    if agent_stats_list:
        prev_map = previous_agent_stats or {}
        agents = [
            build_agent_snapshot(ags, prev_map.get(ags["id"]))
            for ags in agent_stats_list
        ]
    else:
        agents = []
    return Snapshot(
        tick=tick,
        active_events=active_events or [],
        world=world,
        groups=groups,
        agents=agents,
        salience_hints=salience_hints or [],
    )


# ============================================================
# Stream-level recorder helper
# ============================================================


class SnapshotStream:
    """Snapshot accumulator — append snapshots tick by tick.

    Use:
        stream = SnapshotStream()
        for tick in range(max_tick):
            ... (run simulation step)
            stream.append(record_snapshot(tick=tick, ...))
        snapshots = stream.snapshots
    """

    def __init__(self) -> None:
        self._snapshots: list[Snapshot] = []
        self._previous_agent_stats: dict[str, dict[str, Any]] = {}

    def append(self, snapshot: Snapshot) -> None:
        """Append a complete snapshot. previous_agent_stats는 외부 관리."""
        self._snapshots.append(snapshot)

    def append_from_stats(
        self,
        *,
        tick: int,
        active_events: list[str] | None = None,
        world_stats: dict[str, Any] | None = None,
        group_stats_list: list[dict[str, Any]] | None = None,
        agent_stats_list: list[dict[str, Any]] | None = None,
        salience_hints: list[str] | None = None,
    ) -> Snapshot:
        """Build snapshot from raw stats + auto-track previous agent stats for delta.

        Returns the built snapshot (also appended to stream).
        """
        snapshot = record_snapshot(
            tick=tick,
            active_events=active_events,
            world_stats=world_stats,
            group_stats_list=group_stats_list,
            agent_stats_list=agent_stats_list,
            previous_agent_stats=self._previous_agent_stats if self._previous_agent_stats else None,
            salience_hints=salience_hints,
        )
        self._snapshots.append(snapshot)
        if agent_stats_list:
            self._previous_agent_stats = {
                ags["id"]: ags for ags in agent_stats_list
            }
        return snapshot

    @property
    def snapshots(self) -> list[Snapshot]:
        """Read-only view of accumulated snapshots."""
        return list(self._snapshots)

    def __len__(self) -> int:
        return len(self._snapshots)
