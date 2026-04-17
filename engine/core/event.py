"""이벤트 시스템.

시뮬레이션의 외부 입력(정경 사건)과 상태 효과를 정의한다.
CanonicalIntervention은 규칙 엔진을 무시하고 상태를 직접 재조정하는 특수 이벤트.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.core.state import AgentState, clamp, get_nested_value, set_nested_value


class Precondition(BaseModel):
    """이벤트 발동 전제조건."""

    field_path: str = Field(description="AgentState의 점 구분 필드 경로")
    operator: Literal["gt", "lt", "gte", "lte", "eq", "in"] = Field(
        description="비교 연산자"
    )
    value: Any = Field(description="비교 대상 값")

    def evaluate(self, state: AgentState) -> bool:
        """전제조건이 충족되는지 평가한다."""
        actual = get_nested_value(state, self.field_path)
        if actual is None:
            return False
        if self.operator == "gt":
            return bool(actual > self.value)
        if self.operator == "lt":
            return bool(actual < self.value)
        if self.operator == "gte":
            return bool(actual >= self.value)
        if self.operator == "lte":
            return bool(actual <= self.value)
        if self.operator == "eq":
            return bool(actual == self.value)
        if self.operator == "in":
            return bool(actual in self.value)
        return False


class StateEffect(BaseModel):
    """상태 변경 효과. 이벤트가 에이전트 상태에 미치는 영향."""

    field_path: str = Field(description="AgentState의 점 구분 필드 경로")
    operation: Literal["set", "add", "multiply"] = Field(description="연산 종류")
    value: float | str = Field(description="연산 값")

    def apply(self, state: AgentState) -> AgentState:
        """상태에 효과를 적용한 새 AgentState를 반환한다."""
        current = get_nested_value(state, self.field_path)
        if current is None and self.operation != "set":
            return state

        if self.operation == "set":
            new_value = self.value
        elif self.operation == "add" and isinstance(current, (int, float)):
            # identity_shift 등 음수 허용 필드를 위해 -10~10 범위 사용
            new_value = clamp(current + float(self.value), -10.0, 10.0)
        elif self.operation == "multiply" and isinstance(current, (int, float)):
            new_value = clamp(current * float(self.value), -10.0, 10.0)
        else:
            return state

        return set_nested_value(state, self.field_path, new_value)


class StateMultiplier(BaseModel):
    """행동 가중치 계산에 사용하는 승수. 에이전트 상태 또는 환경에서 값을 읽는다."""

    field_path: str = Field(description="점 구분 필드 경로")
    factor_type: Literal["linear", "inverse", "threshold"] = Field(
        description="승수 계산 방식"
    )
    params: dict[str, float] = Field(
        default_factory=dict, description="승수 파라미터"
    )
    source: str = Field(
        default="agent",
        description="값의 출처: 'agent' 또는 'environment'",
    )

    def compute(self, state: AgentState, environment: Any = None) -> float:
        """현재 상태/환경에서 승수 값을 계산한다."""
        if self.source == "environment" and environment is not None:
            raw = getattr(environment, self.field_path, None)
        else:
            raw = get_nested_value(state, self.field_path)
        if not isinstance(raw, (int, float)):
            return 1.0

        val = float(raw)
        scale = self.params.get("scale", 0.1)

        if self.factor_type == "linear":
            return 1.0 + val * scale
        if self.factor_type == "inverse":
            return 1.0 + (10.0 - val) * scale
        if self.factor_type == "threshold":
            threshold = self.params.get("threshold", 5.0)
            bonus = self.params.get("bonus", 0.5)
            return 1.0 + bonus if val >= threshold else 1.0
        return 1.0


class WeightFormula(BaseModel):
    """행동 선택 가중치 공식. eval() 없이 구조화된 계산."""

    base_weight: float = Field(ge=0.0, description="기본 가중치")
    state_multipliers: list[StateMultiplier] = Field(
        default_factory=list, description="상태 기반 승수 목록"
    )

    def compute_weight(self, state: AgentState, environment: Any = None) -> float:
        """현재 상태/환경에서 최종 가중치를 계산한다."""
        weight = self.base_weight
        for mult in self.state_multipliers:
            weight *= mult.compute(state, environment)
        return max(weight, 0.001)  # 0 방지


class ActionOption(BaseModel):
    """이벤트 발생 시 에이전트가 선택할 수 있는 행동."""

    action_id: str = Field(description="행동 고유 ID")
    description: str = Field(default="", description="행동 설명")
    preconditions: list[Precondition] = Field(
        default_factory=list, description="이 행동이 가능하기 위한 전제조건"
    )
    weight_formula: WeightFormula = Field(description="행동 선택 가중치 공식")
    effects: list[StateEffect] = Field(
        default_factory=list, description="행동 수행 시 상태 효과"
    )


class ExternalEvent(BaseModel):
    """외부 이벤트. 정경 사건 등 시뮬레이션에 주어지는 고정된 입력."""

    event_id: str = Field(description="이벤트 고유 ID")
    tick: int = Field(ge=0, description="발생 tick")
    event_type: Literal["canonical", "environmental"] = Field(
        default="canonical", description="이벤트 유형"
    )
    description: str = Field(default="", description="이벤트 설명")
    source_ref: str | None = Field(default=None, description="출처 참조 (예: '마 26:69')")
    preconditions: list[Precondition] = Field(
        default_factory=list, description="이벤트 발동 전제조건"
    )
    effects: list[StateEffect] = Field(
        default_factory=list, description="이벤트의 직접 상태 효과"
    )
    action_options: list[ActionOption] = Field(
        default_factory=list, description="이 이벤트에서 가능한 행동 목록"
    )


class CanonicalIntervention(BaseModel):
    """정경 개입. 규칙 엔진을 무시하고 상태를 직접 재조정한다.

    신학적으로 '은혜의 개입'을 시스템에 반영한 것.
    """

    event_id: str = Field(description="이벤트 고유 ID")
    tick: int = Field(ge=0, description="발생 tick")
    scripture_ref: str = Field(description="성경 참조 (예: '요 21:15-17')")
    description: str = Field(default="", description="개입 설명")
    state_overrides: dict[str, Any] = Field(
        description="강제 설정할 상태 값 (field_path: value)"
    )

    def apply(self, state: AgentState) -> AgentState:
        """상태를 강제 재조정한다. 규칙 엔진과 무관."""
        result = state
        for field_path, value in self.state_overrides.items():
            result = set_nested_value(result, field_path, value)
        return result
