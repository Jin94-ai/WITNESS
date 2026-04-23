"""에이전트 행동 프로파일.

에이전트가 이벤트 없이도 자체적으로 수행할 수 있는 행동을 정의한다.
다중 에이전트 시뮬레이션에서 각 에이전트는 매 tick 행동을 선택할 수 있다.

이벤트 기반 행동(ActionOption)과 구분:
  - ActionOption: 이벤트 발생 시 반응으로 선택하는 행동
  - AgentAction: 이벤트 없이도 에이전트가 자발적으로 수행하는 행동
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from engine.core.event import Precondition, StateEffect, WeightFormula
from engine.core.state import AgentState


class AgentAction(BaseModel):
    """에이전트의 자발적 행동 정의.

    매 tick 행동 선택지에 포함되며, 전제조건과 가중치 공식에 따라 선택된다.
    """

    action_id: str = Field(description="행동 고유 ID")
    description: str = Field(default="")
    preconditions: list[Precondition] = Field(
        default_factory=list, description="행동 가능 전제조건"
    )
    weight_formula: WeightFormula = Field(description="행동 선택 가중치 공식")
    effects: list[StateEffect] = Field(
        default_factory=list, description="행동 수행 시 상태 효과"
    )
    visible_signal: str | None = Field(
        default=None,
        description="외부에서 관찰되는 행동 서술 (TRACE_SCHEMA.md §2.2, v2.0 renderer 전용). "
                    "None이면 trace_narrator fallback 템플릿 사용.",
    )
    observable_from: list[str] = Field(
        default_factory=list,
        description="이 행동을 관찰 가능한 agent IDs (TRACE_SCHEMA §3.1 정보 비대칭성). "
                    "비어있으면 모두에게 공개 (default). 특정 ID 리스트면 해당 agent만 관찰. "
                    "예: 'inform_authorities' → ['caiaphas'] — 당국만 봄.",
    )
    cooldown: int = Field(default=0, ge=0, description="수행 후 재수행 대기 tick")
    last_performed_tick: int = Field(default=-1)

    def is_available(self, tick: int, state: AgentState) -> bool:
        """이 tick에서 행동 수행 가능 여부."""
        if self.cooldown > 0 and self.last_performed_tick >= 0:
            if tick - self.last_performed_tick < self.cooldown:
                return False
        return all(p.evaluate(state) for p in self.preconditions)

    def record_perform(self, tick: int) -> None:
        """수행을 기록한다."""
        self.last_performed_tick = tick


class AgentBehaviorProfile(BaseModel):
    """에이전트의 행동 프로파일.

    에이전트가 수행할 수 있는 자발적 행동 목록과 기본 행동을 정의한다.
    """

    agent_id: str = Field(description="에이전트 ID")
    actions: list[AgentAction] = Field(
        default_factory=list, description="가능한 행동 목록"
    )
    default_action_id: str = Field(
        default="idle", description="가능한 행동이 없을 때 기본 행동"
    )

    def get_available_actions(self, tick: int, state: AgentState) -> list[AgentAction]:
        """현재 수행 가능한 행동 목록을 반환한다."""
        return [a for a in self.actions if a.is_available(tick, state)]

    def select_action(
        self,
        tick: int,
        state: AgentState,
        rng: Any,
        environment: Any = None,
        policy: Any = None,
    ) -> AgentAction | None:
        """가중치 기반으로 행동을 선택한다.

        Args:
            policy: 선택적 DecisionPolicy (Spike 6). ``weights(state, options,
                    environment)`` 반환. ``None``이면 기존 규칙 기반 로직 그대로.
                    반환 합이 0 이하이면 abstain으로 간주해 규칙 기반 폴백
                    (Rule #11 dual-path).

        Returns:
            선택된 행동. 가능한 행동이 없으면 None.
        """
        available = self.get_available_actions(tick, state)
        if not available:
            return None

        if policy is not None:
            weights = list(policy.weights(state, available, environment))
            if sum(weights) <= 0:
                # policy abstains → rule-based fallback (Rule #11)
                weights = [
                    a.weight_formula.compute_weight(state, environment)
                    for a in available
                ]
        else:
            weights = [
                a.weight_formula.compute_weight(state, environment)
                for a in available
            ]
        total = sum(weights)
        if total <= 0:
            return None

        r = rng.random() * total
        cumulative = 0.0
        for action, weight in zip(available, weights):
            cumulative += weight
            if r <= cumulative:
                return action

        return available[-1]  # 부동소수점 안전장치
