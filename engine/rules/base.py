"""규칙 엔진 프레임워크.

Rule Protocol과 RuleEngine을 정의한다.
모든 확률적 판단은 RuleContext.rng를 통해 시드 재현성을 보장한다.
"""

from __future__ import annotations

import random
from typing import Protocol

from pydantic import BaseModel, Field

from engine.core.event import ExternalEvent
from engine.core.state import AgentState


class RuleContext(BaseModel):
    """규칙 적용 시 전달되는 컨텍스트.

    v1.2 phase-linked architecture (2026-04-19):
    - `dt_hours` 필드 추가: 이 tick이 실제 몇 시간에 해당하는가.
      phase-variable tick scale에서 rule이 "per tick" 상수가 아닌
      "per hour" rate로 재스케일링하기 위해 필수.
    - Backward compat: 기본값 2.0 (= v0.5 수난 scenario 호환).
    - rule 구현체는 점진적으로 dt_hours를 활용하도록 마이그레이션.
      기존 per-tick rule은 delta_tick을 그대로 사용해도 동작 (단, 분석
      좌표계는 absolute time 기준으로 재정의되어야 함).
    """

    model_config = {"arbitrary_types_allowed": True}

    tick: int = Field(ge=0, description="현재 tick")
    delta_tick: int = Field(default=1, description="이전 tick과의 차이")
    dt_hours: float = Field(
        default=2.0, gt=0.0,
        description="이 tick이 실제 몇 시간에 해당하는가 (v1.2 phase-variable). "
                    "기본값 2.0 = v0.5 수난 scenario 호환. "
                    "Phase-aware rule은 rate를 dt_hours 기준으로 계산.",
    )
    active_events: list[ExternalEvent] = Field(
        default_factory=list, description="현재 tick에 활성화된 이벤트"
    )
    environment: dict[str, object] = Field(
        default_factory=dict, description="환경 변수"
    )
    rng: random.Random = Field(
        default_factory=random.Random, description="시드 주입 가능한 난수 생성기"
    )
    all_agents: dict[str, AgentState] = Field(
        default_factory=dict,
        description="다중 에이전트 시뮬레이션 시 모든 에이전트 상태. 단일 에이전트 시 빈 dict.",
    )


class Rule(Protocol):
    """규칙 인터페이스. 모든 규칙은 이 프로토콜을 구현한다."""

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        """상태에 규칙을 적용하여 새 상태를 반환한다."""
        ...


class RuleEngine:
    """규칙 목록을 순차 적용하는 엔진.

    규칙 적용 순서가 중요하다: physical -> emotional -> social -> temporal.
    """

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    @property
    def rules(self) -> list[Rule]:
        return list(self._rules)

    def apply_all(self, state: AgentState, context: RuleContext) -> AgentState:
        """모든 규칙을 순차 적용한다."""
        for rule in self._rules:
            state = rule.apply(state, context)
        return state
