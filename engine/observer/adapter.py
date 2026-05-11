"""World Observer — Adapter from SimulationWorld results to Snapshot stream.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §3 Phase O6.

기존 SimulationWorld 결과 (MultiAgentResult)를 *post-hoc*으로 snapshot stream으로
변환. SimulationWorld 자체는 무수정 (ABSOLUTE Rule #6 준수).

ABSOLUTE Rule #1: no person hardcoding. caller가 generic role_map 제공.

Usage:
    from engine.simulation.world import SimulationWorld
    from engine.observer.adapter import result_to_observer

    world = SimulationWorld(config, ...)
    result = world.run()

    # role_map: caller-provided, generic roles only
    role_map = {"agent_001": "follower", "agent_002": "crowd"}
    observer = result_to_observer(result, role_map=role_map)
"""

from __future__ import annotations

from typing import Any

from engine.core.state import AgentState
from engine.observer.core import Observer
from engine.observer.recorder import SnapshotStream
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)

# ============================================================
# AgentState → AgentSnapshot field mapping
# ============================================================

# AgentState.slow_state.moral_injury → AgentSnapshot.shame_self
# (closest semantic match — moral_injury는 자기 신념 위반 후 누적)


def agent_state_to_snapshot(
    state: AgentState,
    role: str = "generic",
    delta_tags: list[str] | None = None,
) -> AgentSnapshot:
    """Convert engine AgentState → observer AgentSnapshot (light view).

    Args:
        state: engine.core.state.AgentState
        role: generic role tag (caller provides — no person hardcoding here)
        delta_tags: optional tick-over-tick change tags

    Returns:
        AgentSnapshot with subset of state fields.
    """
    return AgentSnapshot(
        id=state.agent_id,
        role=role,
        fear=state.emotions.fear,
        hope=state.emotions.hope,
        shame_self=state.slow_state.moral_injury,
        delta=delta_tags or [],
    )


def _detect_state_delta(
    current: AgentState, previous: AgentState | None
) -> list[str]:
    """Detect tick-over-tick state shifts. Returns delta tags."""
    if previous is None:
        return []
    threshold = 1.0
    deltas: list[str] = []
    for field, cur_val, prev_val in [
        ("fear", current.emotions.fear, previous.emotions.fear),
        ("hope", current.emotions.hope, previous.emotions.hope),
        (
            "shame_self",
            current.slow_state.moral_injury,
            previous.slow_state.moral_injury,
        ),
    ]:
        diff = cur_val - prev_val
        if diff > threshold:
            deltas.append(f"{field}_up")
        elif diff < -threshold:
            deltas.append(f"{field}_down")
    return deltas


# ============================================================
# Result-level → Observer
# ============================================================


def result_to_observer(
    result: Any,  # MultiAgentResult — Any to avoid circular import
    role_map: dict[str, str] | None = None,
    world_stats_per_tick: dict[int, dict[str, Any]] | None = None,
    group_stats_per_tick: dict[int, list[dict[str, Any]]] | None = None,
    active_events_per_tick: dict[int, list[str]] | None = None,
) -> Observer:
    """Convert MultiAgentResult → Observer (snapshot stream).

    Args:
        result: SimulationWorld.run() output (MultiAgentResult).
        role_map: {agent_id: generic_role}. Defaults to "generic" for missing.
        world_stats_per_tick: optional {tick: world_stats_dict} for WorldSnapshot.
                              If None, WorldSnapshot uses defaults.
        group_stats_per_tick: optional {tick: [group_stats_dicts]} for GroupSnapshot.
        active_events_per_tick: optional {tick: [event_id]} for events list.
                                If None, derived from result.fired_events.

    Returns:
        Observer with snapshot stream.
    """
    role_map = role_map or {}

    # Collect all tick numbers from agent state_snapshots
    all_ticks: set[int] = set()
    for ticks_dict in result.state_snapshots.values():
        all_ticks.update(ticks_dict.keys())

    if not all_ticks:
        raise ValueError(
            "Result has no state_snapshots — cannot build observer"
        )

    # Derive active_events_per_tick from fired_events if not provided
    if active_events_per_tick is None:
        active_events_per_tick = {}
        for ev in result.fired_events:
            tick = ev.get("tick")
            event_id = ev.get("event_id") or ev.get("id") or "unknown_event"
            if tick is not None:
                active_events_per_tick.setdefault(tick, []).append(event_id)

    # Build snapshot stream
    stream = SnapshotStream()
    sorted_ticks = sorted(all_ticks)
    previous_states: dict[str, AgentState] = {}

    for tick in sorted_ticks:
        # Build agent snapshots for this tick
        agent_snapshots: list[AgentSnapshot] = []
        current_states: dict[str, AgentState] = {}
        for agent_id, ticks_dict in result.state_snapshots.items():
            if tick not in ticks_dict:
                continue
            state = ticks_dict[tick]
            role = role_map.get(agent_id, "generic")
            delta = _detect_state_delta(state, previous_states.get(agent_id))
            agent_snapshots.append(
                agent_state_to_snapshot(state, role=role, delta_tags=delta)
            )
            current_states[agent_id] = state

        # World snapshot
        if world_stats_per_tick and tick in world_stats_per_tick:
            world = _build_world_snapshot_from_dict(world_stats_per_tick[tick])
        else:
            world = WorldSnapshot()

        # Group snapshots
        groups: list[GroupSnapshot] = []
        if group_stats_per_tick and tick in group_stats_per_tick:
            for gs in group_stats_per_tick[tick]:
                groups.append(_build_group_snapshot_from_dict(gs))

        snap = Snapshot(
            tick=tick,
            active_events=active_events_per_tick.get(tick, []),
            world=world,
            groups=groups,
            agents=agent_snapshots,
            salience_hints=[],
        )
        stream.append(snap)
        previous_states = current_states

    return Observer(stream.snapshots)


def _build_world_snapshot_from_dict(d: dict[str, Any]) -> WorldSnapshot:
    """Helper: dict → WorldSnapshot with defaults."""
    return WorldSnapshot(
        crowd_mood=d.get("crowd_mood", "calm"),
        blame_concentration=d.get("blame_concentration", 0.0),
        public_suspicion=d.get("public_suspicion", 0.0),
        authority_vigilance=d.get("authority_vigilance", 0.0),
        scarcity_pressure=d.get("scarcity_pressure", 0.0),
    )


def _build_group_snapshot_from_dict(d: dict[str, Any]) -> GroupSnapshot:
    """Helper: dict → GroupSnapshot."""
    return GroupSnapshot(
        id=d["id"],
        dominant_mode=d.get("dominant_mode", "low_activity"),
        tension=d.get("tension", 0.0),
        member_count=d.get("member_count", 0),
    )
