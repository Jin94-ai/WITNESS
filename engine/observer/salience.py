"""World Observer — Salience Detector.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §5.

Salience = *attention pointer*, NOT *quality verdict*. 평가 안 함.

감지 후보 (Lee directive §4.4):
- pressure spike (scarcity_pressure delta)
- authority vigilance spike
- public suspicion jump
- cohort split (2+ groups in different dominant_modes)
- recovery turning point (group mode shift saturation→recovery)
- saturation lock (group mode "saturation" 5+ ticks 연속)
- low-activity but tense (crowd_mood "tense" + active_events 0)
- agent state급변 (delta non-empty)
"""

from __future__ import annotations

from typing import Any

from engine.observer.snapshot_schema import Snapshot

# ============================================================
# Thresholds
# ============================================================

_PRESSURE_SPIKE_THRESHOLD: float = 0.2  # tick-over-tick world.* delta
_SATURATION_LOCK_TICKS: int = 5  # 연속 saturation 임계 tick 수
_TOP_N_DEFAULT: int = 5


# ============================================================
# Per-tick salience tags (annotate single snapshot in stream context)
# ============================================================


def detect_salience_tags(
    snapshots: list[Snapshot], target_tick: int
) -> list[str]:
    """target_tick에 대한 salience tag list 감지.

    snapshots는 *전체 stream* (delta 계산을 위해 직전 tick 필요).

    Returns list of tags like ['pressure_spike', 'cohort_split'].
    """
    if not snapshots:
        return []
    tick_index = {s.tick: s for s in snapshots}
    if target_tick not in tick_index:
        return []
    current = tick_index[target_tick]
    # 직전 tick (가장 가까운 이전 tick)
    prev_ticks = sorted([t for t in tick_index if t < target_tick], reverse=True)
    previous = tick_index[prev_ticks[0]] if prev_ticks else None

    tags: list[str] = []

    # 1. World-level delta spikes
    if previous is not None:
        if (
            current.world.scarcity_pressure - previous.world.scarcity_pressure
            > _PRESSURE_SPIKE_THRESHOLD
        ):
            tags.append("pressure_spike")
        if (
            current.world.authority_vigilance
            - previous.world.authority_vigilance
            > _PRESSURE_SPIKE_THRESHOLD
        ):
            tags.append("authority_vigilance_spike")
        if (
            current.world.public_suspicion - previous.world.public_suspicion
            > _PRESSURE_SPIKE_THRESHOLD
        ):
            tags.append("public_suspicion_jump")
        if (
            current.world.blame_concentration
            - previous.world.blame_concentration
            > _PRESSURE_SPIKE_THRESHOLD
        ):
            tags.append("blame_concentration_spike")

    # 2. Cohort split detection
    if len(current.groups) >= 2:
        modes = {g.dominant_mode for g in current.groups}
        if len(modes) >= 2:
            tags.append("cohort_split")

    # 3. Recovery turning point (group mode shift saturation→recovery)
    if previous is not None:
        prev_modes = {g.id: g.dominant_mode for g in previous.groups}
        for g in current.groups:
            if (
                prev_modes.get(g.id) == "saturation"
                and g.dominant_mode == "recovery"
            ):
                tags.append("recovery_turning_point")
                break

    # 4. Saturation lock (5+ ticks consecutive saturation in any group)
    if _detect_saturation_lock(snapshots, target_tick):
        tags.append("saturation_lock")

    # 5. Low-activity but tense
    if (
        current.world.crowd_mood == "tense"
        and not current.active_events
    ):
        tags.append("low_activity_tension")

    # 6. Agent state delta
    if any(a.delta for a in current.agents):
        tags.append("agent_state_shift")

    return tags


def _detect_saturation_lock(
    snapshots: list[Snapshot], target_tick: int
) -> bool:
    """target_tick 기준으로 어떤 group이 5+ 연속 saturation인지 검사."""
    tick_index = {s.tick: s for s in snapshots}
    target = tick_index.get(target_tick)
    if target is None:
        return False
    for g in target.groups:
        if g.dominant_mode != "saturation":
            continue
        # 직전 N-1 tick에서도 같은 group이 saturation인지 확인
        consecutive = 1
        for t in sorted(
            [t for t in tick_index if t < target_tick], reverse=True
        ):
            prev_snap = tick_index[t]
            prev_group = prev_snap.get_group(g.id)
            if prev_group is None or prev_group.dominant_mode != "saturation":
                break
            consecutive += 1
            if consecutive >= _SATURATION_LOCK_TICKS:
                return True
    return False


# ============================================================
# Top-N salient moments
# ============================================================


def top_salient_moments(
    snapshots: list[Snapshot],
    tick_from: int | None = None,
    tick_to: int | None = None,
    top_n: int = _TOP_N_DEFAULT,
) -> list[dict[str, Any]]:
    """Top-N salient moments in window.

    Score = number of salience tags at that tick (단순 count). 평가 아님,
    *attention pointer*.

    Returns list of dicts:
        tick: int
        score: int  — tag count
        tags: list[str]
    """
    lo = tick_from if tick_from is not None else snapshots[0].tick
    hi = tick_to if tick_to is not None else snapshots[-1].tick
    moments: list[dict[str, Any]] = []
    for s in snapshots:
        if not (lo <= s.tick <= hi):
            continue
        tags = detect_salience_tags(snapshots, s.tick)
        if tags:
            moments.append({"tick": s.tick, "score": len(tags), "tags": tags})
    # Sort by score desc, then tick asc (earliest among ties first)
    moments.sort(key=lambda m: (-m["score"], m["tick"]))
    return moments[:top_n]


# ============================================================
# Top-N unstable agents
# ============================================================


def top_unstable_agents(
    snapshots: list[Snapshot],
    tick_from: int | None = None,
    tick_to: int | None = None,
    top_n: int = 3,
) -> list[dict[str, Any]]:
    """Top-N agents with most state-shift moments in window.

    Score = number of ticks where agent's delta is non-empty.

    Returns list of dicts:
        agent_id: str
        score: int
        ticks_with_shift: list[int]
    """
    lo = tick_from if tick_from is not None else snapshots[0].tick
    hi = tick_to if tick_to is not None else snapshots[-1].tick
    counter: dict[str, list[int]] = {}
    for s in snapshots:
        if not (lo <= s.tick <= hi):
            continue
        for a in s.agents:
            if a.delta:
                counter.setdefault(a.id, []).append(s.tick)
    ranked = sorted(counter.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [
        {"agent_id": aid, "score": len(ticks), "ticks_with_shift": ticks}
        for aid, ticks in ranked[:top_n]
    ]
