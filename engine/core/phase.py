"""Phase-linked continuous life architecture (v1.2 MVP).

사용자 경험 차원에서는 하나의 연속된 생애 시뮬레이터이지만,
엔진/검증 차원에서는 여러 local phase simulator가 state handoff로
이어지는 stitched 구조. 각 phase는:
- 고유 tick_scale_hours (dense 2h/tick vs sparse 1일/tick)
- 자체 max_tick + exit_condition
- phase-local canonical events + triggers
- 다음 phase로 전달할 handoff spec

reviewer 피드백 반영:
- 연속/stitched 혼합: 서사는 연속, 검증은 phase-local
- tick_scale_hours는 모든 rule에 dt로 전달 필요 (Iteration 2에서)
- canonical intervention = reparameterization shock (완전 회복 아님)

참조: `frolicking-sleeping-whistle.md` §2.2-2.6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PhaseExitCondition:
    """Phase 종료 조건.

    세 가지 방식 중 하나 이상 충족 시 phase 종료:
    - max_tick 도달 (항상 적용되는 hard cap)
    - trigger_id 발동 (trigger-driven exit)
    - state_predicate 함수 평가 True (e.g., "jesus_understanding >= messiah_political")

    Args:
        max_tick: phase 내부 tick 기준. None이면 다른 조건에 의존.
        triggered_by: 이 trigger_id가 발동하면 즉시 종료.
        state_predicate: (state_dict) -> bool. None이면 비활성.
    """

    max_tick: int | None = None
    triggered_by: str | None = None
    state_predicate: Any | None = None  # callable, not easily typed

    def is_met(
        self,
        tick: int,
        fired_trigger_ids: list[str],
        states: dict[str, Any],
    ) -> bool:
        """종료 조건 충족 여부."""
        if self.max_tick is not None and tick >= self.max_tick:
            return True
        if self.triggered_by is not None and self.triggered_by in fired_trigger_ids:
            return True
        if self.state_predicate is not None:
            try:
                return bool(self.state_predicate(states))
            except Exception:
                return False
        return False


@dataclass
class PhaseHandoffSpec:
    """Phase N 종료 상태 → Phase N+1 시작 상태 매핑.

    각 필드는 source agent의 field_path를 target agent의 field_path로 전달.
    `default_if_missing`이 있으면 source에 없을 때 기본값 사용.

    사용 예 (content 레이어에서):
        PhaseHandoffSpec(
            mappings=[
                FieldMapping("<agent_id>", "domain_state.<field_a>",
                             "<agent_id>", "domain_state.<field_a>"),
                FieldMapping("<agent_id>", "domain_state.<field_b>",
                             "<agent_id>", "domain_state.<field_b>"),
                FieldMapping("<agent_id>", "slow_state.<field_c>",
                             "<agent_id>", "slow_state.<field_c>"),
            ]
        )

    reviewer 피드백: canonical intervention은 완전 회복이 아니므로
    handoff는 state를 reset하지 않고 carry-forward만 수행.
    """

    mappings: list["FieldMapping"] = field(default_factory=list)
    carry_all_slow_state: bool = True
    """True면 mappings 외에도 모든 agent의 slow_state 자동 전달 (irreversible이므로 기본값)."""


@dataclass
class FieldMapping:
    """한 agent의 한 field를 다음 phase로 전달.

    Args:
        source_agent_id: 원본 agent ID (phase N).
        source_field_path: dot-separated path (e.g., "emotions.fear").
        target_agent_id: 대상 agent ID (phase N+1). 보통 same.
        target_field_path: 대상 path. 보통 same.
        default_if_missing: source가 비어있을 때 기본값 (float/int/str). None이면 skip.
    """

    source_agent_id: str
    source_field_path: str
    target_agent_id: str
    target_field_path: str
    default_if_missing: Any = None


@dataclass
class Phase:
    """단일 phase의 full 설정.

    Args:
        phase_id: 식별자 (e.g., "01_calling", "05_passion").
        description: 사람 읽기용 설명.
        tick_scale_hours: 이 phase에서 1 tick이 몇 시간에 해당하는가.
            기본 2.0 (= v0.5 수난 scenario 호환).
            Phase 2 같은 sparse phase는 24.0 (1일/tick).
        exit_condition: 종료 조건.
        agents_active: 이 phase에서 활성화된 agent IDs.
            None이면 SimulationConfig.initial_states 그대로 사용.
        handoff_to_next: 다음 phase로 전달할 state mapping.
            None이면 마지막 phase 또는 handoff 비활성.
        canonical_events_path: content 경로 (e.g., "content/<agent>/phases/<N>/canonical_events.json").
            None이면 상위 SimulationConfig의 interventions 그대로 사용.
        tick_offset: 전체 life arc에서 이 phase의 시작 tick offset.
            analysis.py 등이 phase-conditional local 분석에서 사용.
    """

    phase_id: str
    description: str = ""
    tick_scale_hours: float = 2.0
    exit_condition: PhaseExitCondition = field(default_factory=PhaseExitCondition)
    agents_active: list[str] | None = None
    handoff_to_next: PhaseHandoffSpec | None = None
    canonical_events_path: str | None = None
    tick_offset: int = 0

    def __post_init__(self) -> None:
        if self.tick_scale_hours <= 0:
            raise ValueError(
                f"tick_scale_hours must be > 0, got {self.tick_scale_hours}"
            )
        if not self.phase_id:
            raise ValueError("phase_id must be non-empty")

    def hours_for_ticks(self, n_ticks: int) -> float:
        """이 phase에서 n tick은 몇 시간인가."""
        return n_ticks * self.tick_scale_hours

    def days_for_ticks(self, n_ticks: int) -> float:
        """이 phase에서 n tick은 몇 일인가."""
        return self.hours_for_ticks(n_ticks) / 24.0
