"""Inhibitor rules — cross-agent field attenuation (v1.2 Iteration 11).

reviewer (Gemini) 지적:
    "3년 모델에서 환멸이 쌓이다가도 '기적 목격'이나 '가르침'을 통해
    감쇄되는 '억제 기전(Inhibitor Rules)'이 반드시 추가되어야 합니다.
    그렇지 않으면 모든 시뮬레이션이 1년 차에 종료되는 오류가 발생할
    수 있습니다."

설계 원칙 (ABSOLUTE RULE #1 준수):
- engine/ 규칙은 인물 비종속이어야 함
- content 쪽에서 agent_id + field_path 지정
- 예: "A agent의 disillusionment가 B agent의 awe 상승 시 감쇄" 같은
  content-specific 규칙은 FieldAttenuationRule을 인스턴스화해서 구현

MVP 기능:
- 지정된 trigger field(다른 agent의 감정/상태)가 threshold 초과 시
- 자신의 target field를 지정 rate로 감소
- dt_hours 인식 (phase-variable tick scale 호환)
- Reviewer ChatGPT 지적: 모든 rule이 dt-aware여야 함
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.core.state import AgentState, get_nested_value, set_nested_value
from engine.rules.base import RuleContext


@dataclass
class FieldAttenuationRule:
    """한 field를 다른 agent의 field 조건에 따라 감쇄.

    예시 (content 수준):
        FieldAttenuationRule(
            subject_agent_id="<agent_a>",
            target_field_path="domain_state.disillusionment",
            trigger_agent_id="<agent_b>",
            trigger_field_path="emotions.awe",
            trigger_threshold=5.0,
            attenuation_per_hour=0.05,
            min_target_value=0.0,
        )

    의미: agent_b의 awe >= 5.0이면, agent_a의 disillusionment를
    시간당 0.05씩 감쇄 (0 아래로는 내려가지 않음).

    attenuation_per_hour × dt_hours = per-tick 감쇄량
    → phase-variable tick scale 자동 호환
    """

    subject_agent_id: str
    target_field_path: str
    trigger_agent_id: str
    trigger_field_path: str
    trigger_threshold: float
    attenuation_per_hour: float
    min_target_value: float = 0.0

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        """state에 rule 적용. subject agent가 아니면 no-op."""
        if state.agent_id != self.subject_agent_id:
            return state

        trigger_state = context.all_agents.get(self.trigger_agent_id)
        if trigger_state is None:
            return state

        trigger_val = get_nested_value(trigger_state, self.trigger_field_path)
        if not isinstance(trigger_val, (int, float)):
            return state
        if float(trigger_val) < self.trigger_threshold:
            return state

        current = get_nested_value(state, self.target_field_path)
        if not isinstance(current, (int, float)):
            return state

        delta = self.attenuation_per_hour * context.dt_hours
        new_value = max(float(current) - delta, self.min_target_value)
        return set_nested_value(state, self.target_field_path, new_value)


@dataclass
class FieldAmplificationRule:
    """대칭 — trigger가 충족되면 subject의 target을 증가.

    예시 (content 수준):
        FieldAmplificationRule(
            subject_agent_id="<agent_a>",
            target_field_path="emotions.hope",
            trigger_agent_id="<agent_a>",  # self-trigger 가능
            trigger_field_path="emotions.awe",
            trigger_threshold=5.0,
            amplification_per_hour=0.02,
            max_target_value=10.0,
        )
    """

    subject_agent_id: str
    target_field_path: str
    trigger_agent_id: str
    trigger_field_path: str
    trigger_threshold: float
    amplification_per_hour: float
    max_target_value: float = 10.0

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        if state.agent_id != self.subject_agent_id:
            return state

        trigger_state = context.all_agents.get(self.trigger_agent_id)
        if trigger_state is None:
            return state

        trigger_val = get_nested_value(trigger_state, self.trigger_field_path)
        if not isinstance(trigger_val, (int, float)):
            return state
        if float(trigger_val) < self.trigger_threshold:
            return state

        current = get_nested_value(state, self.target_field_path)
        if not isinstance(current, (int, float)):
            return state

        delta = self.amplification_per_hour * context.dt_hours
        new_value = min(float(current) + delta, self.max_target_value)
        return set_nested_value(state, self.target_field_path, new_value)
