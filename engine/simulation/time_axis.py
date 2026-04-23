"""Absolute time axis utilities (v1.2 Iter 22).

reviewer (ChatGPT) 지적:
    "모든 장기 분석을 tick이 아니라 absolute time(hours since call)로
    바꿔야 한다. 안 그러면 같은 수치를 phase 간 비교할 수 없다.
    linear R²=0.998 같은 지표도 phase 경계 이후엔 재해석해야 한다."

핵심:
- Phase-variable tick_scale_hours 환경에서 tick은 단위가 다름
- 장기 분석은 실시간(hours 또는 days) 기준으로만 유효
- 이 모듈은 PhasedMultiAgentResult를 받아 (absolute_hours, value) 쌍으로 변환

제공 함수:
- ticks_to_absolute_hours: phase boundary + tick 기반 → hours since phase-0-start
- extract_field_trajectory_absolute: 특정 field의 (hours, value) 시계열
- convert_phase_boundaries_to_hours: phase 경계를 hours로 변환
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.core.state import AgentState, get_nested_value


@dataclass
class TimePoint:
    """단일 데이터 포인트: (absolute_hours, value, phase_id)."""

    hours: float
    value: float
    phase_id: str
    local_tick: int


def ticks_to_absolute_hours(
    local_tick: int,
    phase_id: str,
    phase_boundaries: list[dict[str, Any]],
) -> float:
    """Phase-local tick을 arc 시작 이후 absolute hours로 변환.

    Args:
        local_tick: phase 내부 tick (0-indexed from phase start)
        phase_id: 해당 phase의 ID
        phase_boundaries: PhasedMultiAgentResult.phase_boundaries
            각 원소: {phase_id, start_tick, end_tick, tick_scale_hours}

    Returns:
        phase-0 시작으로부터 경과된 hours.

    Raises:
        ValueError: phase_id가 boundaries에 없으면.
    """
    hours_offset = 0.0
    for b in phase_boundaries:
        scale = float(b["tick_scale_hours"])
        if b["phase_id"] == phase_id:
            return hours_offset + local_tick * scale
        # 이 phase 전부 지남: 전체 hours 추가
        phase_ticks = int(b["end_tick"]) - int(b["start_tick"])
        hours_offset += phase_ticks * scale
    raise ValueError(f"phase_id '{phase_id}' not in boundaries")


def extract_field_trajectory_absolute(
    per_phase_snapshots: dict[str, dict[str, dict[int, AgentState]]],
    phase_boundaries: list[dict[str, Any]],
    agent_id: str,
    field_path: str,
) -> list[TimePoint]:
    """Phase별 snapshot에서 특정 field의 absolute-hours 시계열 추출.

    Args:
        per_phase_snapshots: {phase_id: {agent_id: {local_tick: state}}}
        phase_boundaries: phase 경계 정보
        agent_id: 추적할 agent
        field_path: dot-separated (e.g., "emotions.awe", "domain_state.obedience_maturity")

    Returns:
        hours 오름차순으로 정렬된 TimePoint 목록.
    """
    points: list[TimePoint] = []
    for phase_id, agents_snaps in per_phase_snapshots.items():
        agent_snaps = agents_snaps.get(agent_id, {})
        for local_tick, state in agent_snaps.items():
            value = get_nested_value(state, field_path)
            if not isinstance(value, (int, float)):
                continue
            hours = ticks_to_absolute_hours(local_tick, phase_id, phase_boundaries)
            points.append(TimePoint(
                hours=hours,
                value=float(value),
                phase_id=phase_id,
                local_tick=local_tick,
            ))
    points.sort(key=lambda p: p.hours)
    return points


def convert_phase_boundaries_to_hours(
    phase_boundaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Phase 경계를 tick 기반에서 hours 기반으로 변환.

    Returns:
        각 원소에 start_hours / end_hours / duration_hours 추가된 list.
    """
    result = []
    cumulative_hours = 0.0
    for b in phase_boundaries:
        tick_span = b["end_tick"] - b["start_tick"]
        duration_hours = tick_span * b["tick_scale_hours"]
        result.append({
            **b,
            "start_hours": cumulative_hours,
            "end_hours": cumulative_hours + duration_hours,
            "duration_hours": duration_hours,
        })
        cumulative_hours += duration_hours
    return result


def hours_to_days(hours: float) -> float:
    return hours / 24.0


def hours_to_years(hours: float) -> float:
    return hours / (24.0 * 365.25)


def extract_final_states_at_phase_boundaries(
    per_phase_results: dict[str, Any],
    phase_boundaries: list[dict[str, Any]],
    agent_id: str,
    field_path: str,
) -> list[TimePoint]:
    """각 phase 종료 시점의 특정 field 값만 추출.

    장기 추세 분석에 유용 (phase 내부 noise 제거).
    """
    points: list[TimePoint] = []
    for b in phase_boundaries:
        pid = b["phase_id"]
        phase_result = per_phase_results.get(pid)
        if phase_result is None:
            continue
        state = phase_result.final_states.get(agent_id)
        if state is None:
            continue
        value = get_nested_value(state, field_path)
        if not isinstance(value, (int, float)):
            continue
        end_hours = sum(
            (prev_b["end_tick"] - prev_b["start_tick"]) * prev_b["tick_scale_hours"]
            for prev_b in phase_boundaries
            if prev_b["phase_id"] != pid
            and phase_boundaries.index(prev_b) < phase_boundaries.index(b)
        ) + (b["end_tick"] - b["start_tick"]) * b["tick_scale_hours"]
        points.append(TimePoint(
            hours=end_hours,
            value=float(value),
            phase_id=pid,
            local_tick=b["end_tick"] - b["start_tick"],
        ))
    return points
