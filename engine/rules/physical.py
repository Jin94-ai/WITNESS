"""물리 상태 전이 규칙.

피로, 배고픔, 건강의 자연 변화를 처리한다.
"""

from __future__ import annotations

from engine.core.state import AgentState, clamp
from engine.rules.base import RuleContext


class FatigueRule:
    """피로 규칙. 시간 경과에 따라 피로 증가. 휴식 이벤트 시 감소."""

    def __init__(
        self,
        natural_rate: float = 0.05,
        rest_recovery: float = 2.0,
    ) -> None:
        self.natural_rate = natural_rate
        self.rest_recovery = rest_recovery

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        fatigue = state.physical.fatigue

        # 휴식/수면 이벤트 체크
        has_rest = any(
            "rest" in e.event_id or "sleep" in e.event_id
            for e in context.active_events
        )
        if has_rest:
            fatigue = clamp(fatigue - self.rest_recovery)
        else:
            fatigue = clamp(fatigue + self.natural_rate * context.delta_tick)

        new_physical = state.physical.model_copy(update={"fatigue": fatigue})
        return state.model_copy(update={"physical": new_physical})


class HungerRule:
    """배고픔 규칙. 시간 경과에 따라 배고픔 증가. 식사 이벤트 시 감소."""

    def __init__(
        self,
        natural_rate: float = 0.03,
        meal_recovery: float = 4.0,
    ) -> None:
        self.natural_rate = natural_rate
        self.meal_recovery = meal_recovery

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        hunger = state.physical.hunger

        has_meal = any("meal" in e.event_id or "feast" in e.event_id for e in context.active_events)
        if has_meal:
            hunger = clamp(hunger - self.meal_recovery)
        else:
            hunger = clamp(hunger + self.natural_rate * context.delta_tick)

        new_physical = state.physical.model_copy(update={"hunger": hunger})
        return state.model_copy(update={"physical": new_physical})


class HealthRule:
    """건강 규칙. 극한 피로/배고픔이 건강을 저하시킨다."""

    def __init__(self, fatigue_threshold: float = 8.0, degradation_rate: float = 0.1) -> None:
        self.fatigue_threshold = fatigue_threshold
        self.degradation_rate = degradation_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        health = state.physical.health

        if state.physical.fatigue > self.fatigue_threshold:
            health = clamp(health - self.degradation_rate * context.delta_tick)

        if state.physical.hunger > self.fatigue_threshold:
            health = clamp(health - self.degradation_rate * 0.5 * context.delta_tick)

        new_physical = state.physical.model_copy(update={"health": health})
        return state.model_copy(update={"physical": new_physical})
