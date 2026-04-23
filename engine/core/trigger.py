"""트리거 시스템.

다중 에이전트 시뮬레이션에서 에이전트 간 상호작용으로 이벤트를 발생시킨다.
tick 하드코딩 대신 조건 충족 시 이벤트가 동적으로 생성된다.

예시:
  agent_A.disillusionment >= 8 AND agent_B.threat >= 7 AND agent_A가 "betray" 수행
  -> "arrest" 이벤트를 다음 tick에 주입

CanonicalDeadline: 조건이 충족되지 않아도 deadline_tick에 강제 발동 (하위 호환).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.core.state import AgentState, get_nested_value


class TriggerCondition(BaseModel):
    """에이전트 상태 기반 트리거 조건.

    특정 에이전트의 상태 필드가 조건을 충족하는지 평가한다.
    """

    agent_id: str = Field(description="대상 에이전트 ID")
    field_path: str = Field(description="AgentState의 점 구분 필드 경로")
    operator: Literal["gt", "lt", "gte", "lte", "eq"] = Field(
        description="비교 연산자"
    )
    value: float = Field(description="비교 대상 값")

    def evaluate(self, all_agents: dict[str, AgentState]) -> bool:
        """조건이 충족되는지 평가한다."""
        state = all_agents.get(self.agent_id)
        if state is None:
            return False
        actual = get_nested_value(state, self.field_path)
        if not isinstance(actual, (int, float)):
            return False
        val = float(actual)
        if self.operator == "gt":
            return val > self.value
        if self.operator == "lt":
            return val < self.value
        if self.operator == "gte":
            return val >= self.value
        if self.operator == "lte":
            return val <= self.value
        if self.operator == "eq":
            return val == self.value
        return False


class ActionTriggerCondition(BaseModel):
    """에이전트 행동 기반 트리거 조건.

    특정 에이전트가 특정 행동을 수행했을 때 충족된다.
    """

    agent_id: str = Field(description="대상 에이전트 ID")
    action_id: str = Field(description="감지할 행동 ID")

    def evaluate(self, recent_actions: dict[str, list[str]]) -> bool:
        """최근 행동 기록에서 조건 충족 여부를 평가한다.

        Args:
            recent_actions: {agent_id: [action_id, ...]} 최근 tick의 행동 기록
        """
        actions = recent_actions.get(self.agent_id, [])
        return self.action_id in actions


class Trigger(BaseModel):
    """다중 에이전트 트리거.

    모든 state_conditions AND action_conditions가 충족되면 발동한다.
    발동 시 event_template_id로 지정된 이벤트를 생성한다.
    """

    trigger_id: str = Field(description="트리거 고유 ID")
    description: str = Field(default="")
    state_conditions: list[TriggerCondition] = Field(
        default_factory=list, description="상태 기반 조건 (AND)"
    )
    action_conditions: list[ActionTriggerCondition] = Field(
        default_factory=list, description="행동 기반 조건 (AND)"
    )
    event_template_id: str = Field(
        description="발동 시 생성할 이벤트 템플릿 ID"
    )
    effects_on_fire: list[dict[str, Any]] = Field(
        default_factory=list, description="발동 시 추가 StateEffect 데이터"
    )
    cooldown: int = Field(default=0, ge=0, description="발동 후 재발동 대기 tick")
    max_fires: int = Field(default=1, ge=1, description="최대 발동 횟수")
    fire_count: int = Field(default=0, ge=0)
    last_fired_tick: int = Field(default=-1)
    deadline_tick: int | None = Field(
        default=None,
        description="이 tick까지 미발동 시 강제 발동 (정경 호환). None이면 강제 없음.",
    )

    def is_eligible(self, tick: int) -> bool:
        """쿨다운/횟수 제한을 확인한다."""
        if self.fire_count >= self.max_fires:
            return False
        if self.cooldown > 0 and self.last_fired_tick >= 0:
            if tick - self.last_fired_tick < self.cooldown:
                return False
        return True

    def evaluate(
        self,
        tick: int,
        all_agents: dict[str, AgentState],
        recent_actions: dict[str, list[str]],
    ) -> bool:
        """트리거 조건이 모두 충족되는지 평가한다.

        Args:
            tick: 현재 tick
            all_agents: 모든 에이전트 상태 맵
            recent_actions: 최근 tick의 에이전트별 행동 기록
        """
        if not self.is_eligible(tick):
            return False

        for state_cond in self.state_conditions:
            if not state_cond.evaluate(all_agents):
                return False

        for action_cond in self.action_conditions:
            if not action_cond.evaluate(recent_actions):
                return False

        return True

    def is_deadline(self, tick: int) -> bool:
        """deadline에 도달했는지."""
        if self.deadline_tick is None:
            return False
        return tick >= self.deadline_tick and self.fire_count < self.max_fires

    def snapshot_conditions(
        self,
        all_agents: dict[str, AgentState],
        recent_actions: dict[str, list[str]],
    ) -> list[dict[str, Any]]:
        """이 트리거 조건들의 현재 state 값 스냅샷 (TRACE_SCHEMA §2.1).

        Returns:
            각 state condition과 action condition에 대해:
              {"agent", "field", "value" (or "action"), "threshold", "operator", "satisfied"}
        """
        snapshots: list[dict[str, Any]] = []

        for sc in self.state_conditions:
            state = all_agents.get(sc.agent_id)
            value: float | None = None
            if state is not None:
                got = get_nested_value(state, sc.field_path)
                if isinstance(got, (int, float)):
                    value = float(got)
            snapshots.append({
                "agent": sc.agent_id,
                "field": sc.field_path,
                "value": value,
                "threshold": sc.value,
                "operator": sc.operator,
                "satisfied": sc.evaluate(all_agents),
            })

        for ac in self.action_conditions:
            recent = recent_actions.get(ac.agent_id, [])
            snapshots.append({
                "agent": ac.agent_id,
                "action": ac.action_id,
                "recent_actions": list(recent),
                "satisfied": ac.evaluate(recent_actions),
            })

        return snapshots

    def record_fire(self, tick: int) -> None:
        """발동을 기록한다."""
        self.fire_count += 1
        self.last_fired_tick = tick


class TriggerEngine:
    """트리거 평가 엔진.

    매 tick:
    1. deadline 도달 트리거 강제 발동
    2. 조건 충족 트리거 발동
    """

    def __init__(self, triggers: list[Trigger]) -> None:
        self._triggers = triggers

    @property
    def triggers(self) -> list[Trigger]:
        return list(self._triggers)

    def evaluate_tick(
        self,
        tick: int,
        all_agents: dict[str, AgentState],
        recent_actions: dict[str, list[str]] | None = None,
    ) -> list[Trigger]:
        """이 tick에서 발동하는 트리거 목록을 반환한다."""
        if recent_actions is None:
            recent_actions = {}

        fired: list[Trigger] = []

        # 1. deadline 강제 발동
        for trigger in self._triggers:
            if trigger.is_deadline(tick):
                trigger.record_fire(tick)
                fired.append(trigger)

        fired_ids = {t.trigger_id for t in fired}

        # 2. 조건 충족 트리거
        for trigger in self._triggers:
            if trigger.trigger_id in fired_ids:
                continue
            if trigger.evaluate(tick, all_agents, recent_actions):
                trigger.record_fire(tick)
                fired.append(trigger)

        return fired

    def reset(self) -> None:
        """모든 트리거의 발동 상태를 초기화한다."""
        for trigger in self._triggers:
            trigger.fire_count = 0
            trigger.last_fired_tick = -1
