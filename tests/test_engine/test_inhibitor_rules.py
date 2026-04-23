"""FieldAttenuationRule / FieldAmplificationRule 테스트 (v1.2 Iter 11).

reviewer (Gemini) 지적 반영: 유다 조기 배반 방지를 위한 inhibitor rule.
engine/ 는 인물 비종속이어야 하므로 generic rule + content-level instantiation.
"""

import random

import pytest

from engine.core.state import AgentState, EmotionalState
from engine.rules.base import RuleContext
from engine.rules.inhibitor import (
    FieldAmplificationRule,
    FieldAttenuationRule,
)


def _agent(aid: str, fear: float = 5.0, awe: float = 0.0) -> AgentState:
    return AgentState(
        agent_id=aid,
        emotions=EmotionalState(fear=fear, awe=awe),
    )


def _ctx(dt_hours: float = 2.0, all_agents: dict | None = None) -> RuleContext:
    return RuleContext(
        tick=0, delta_tick=1, dt_hours=dt_hours,
        rng=random.Random(0), all_agents=all_agents or {},
    )


class TestFieldAttenuationRule:
    def test_skip_non_subject_agent(self):
        """subject_agent_id가 아니면 no-op."""
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="source", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, attenuation_per_hour=0.1,
        )
        state = _agent("other", fear=5.0)
        result = rule.apply(state, _ctx())
        assert result is state  # unchanged

    def test_no_trigger_state_no_op(self):
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="missing", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, attenuation_per_hour=0.1,
        )
        state = _agent("target", fear=5.0)
        result = rule.apply(state, _ctx(all_agents={"target": state}))
        assert result.emotions.fear == 5.0  # unchanged

    def test_below_threshold_no_op(self):
        """trigger 값이 threshold 미만이면 감쇄 없음."""
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="source", trigger_field_path="emotions.awe",
            trigger_threshold=5.0, attenuation_per_hour=0.1,
        )
        target = _agent("target", fear=5.0)
        source = _agent("source", awe=3.0)  # 5.0 미만
        result = rule.apply(target, _ctx(all_agents={
            "target": target, "source": source,
        }))
        assert result.emotions.fear == 5.0

    def test_above_threshold_attenuates(self):
        """trigger 초과 시 target 감쇄 (attenuation × dt_hours)."""
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="source", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, attenuation_per_hour=0.1,
        )
        target = _agent("target", fear=5.0)
        source = _agent("source", awe=7.0)  # threshold 초과
        result = rule.apply(target, _ctx(dt_hours=2.0, all_agents={
            "target": target, "source": source,
        }))
        # 0.1/hour × 2h = 0.2 감소 → 5.0 - 0.2 = 4.8
        assert abs(result.emotions.fear - 4.8) < 1e-9

    def test_dt_hours_scaling(self):
        """phase-variable: 24h/tick에서 12배 더 감쇄."""
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="source", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, attenuation_per_hour=0.1,
        )
        target = _agent("target", fear=5.0)
        source = _agent("source", awe=7.0)

        # dense 2h/tick
        result_dense = rule.apply(target, _ctx(dt_hours=2.0, all_agents={
            "target": target, "source": source,
        }))
        # sparse 24h/tick
        result_sparse = rule.apply(target, _ctx(dt_hours=24.0, all_agents={
            "target": target, "source": source,
        }))

        dense_delta = 5.0 - result_dense.emotions.fear
        sparse_delta = 5.0 - result_sparse.emotions.fear
        # sparse가 dense보다 12배 감쇄
        assert abs(sparse_delta - dense_delta * 12) < 1e-9

    def test_min_value_clamp(self):
        """min_target_value 아래로는 안 내려감."""
        rule = FieldAttenuationRule(
            subject_agent_id="target", target_field_path="emotions.fear",
            trigger_agent_id="source", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, attenuation_per_hour=10.0,
            min_target_value=1.0,
        )
        target = _agent("target", fear=2.0)
        source = _agent("source", awe=5.0)
        result = rule.apply(target, _ctx(dt_hours=24.0, all_agents={
            "target": target, "source": source,
        }))
        # 10/h × 24h = 240 감쇄 요청, but clamp at 1.0
        assert result.emotions.fear == 1.0


class TestFieldAmplificationRule:
    def test_amplifies_when_triggered(self):
        rule = FieldAmplificationRule(
            subject_agent_id="peter", target_field_path="emotions.hope",
            trigger_agent_id="peter", trigger_field_path="emotions.awe",
            trigger_threshold=5.0, amplification_per_hour=0.05,
        )
        peter = AgentState(
            agent_id="peter",
            emotions=EmotionalState(awe=7.0, hope=5.0),
        )
        ctx = _ctx(dt_hours=2.0, all_agents={"peter": peter})
        result = rule.apply(peter, ctx)
        # 0.05/h × 2h = 0.1 증가
        assert abs(result.emotions.hope - 5.1) < 1e-9

    def test_max_value_clamp(self):
        rule = FieldAmplificationRule(
            subject_agent_id="peter", target_field_path="emotions.hope",
            trigger_agent_id="peter", trigger_field_path="emotions.awe",
            trigger_threshold=3.0, amplification_per_hour=10.0,
            max_target_value=10.0,
        )
        peter = AgentState(
            agent_id="peter",
            emotions=EmotionalState(awe=5.0, hope=9.5),
        )
        ctx = _ctx(dt_hours=24.0, all_agents={"peter": peter})
        result = rule.apply(peter, ctx)
        assert result.emotions.hope == 10.0  # clamped


class TestInhibitorRealisticScenario:
    """실제 시나리오: Peter awe 상승 → Judas disillusionment 감쇄."""

    def test_scenario_blueprint(self):
        """Inhibitor rule이 content 수준에서 인물 관계를 구성하는 방식."""
        # content/peter/phases/02_galilean/rules.json 같은 파일에서
        # 다음 rule을 instantiate:
        inhibitor = FieldAttenuationRule(
            subject_agent_id="judas",
            target_field_path="domain_state.disillusionment",
            trigger_agent_id="peter",
            trigger_field_path="emotions.awe",
            trigger_threshold=6.0,
            attenuation_per_hour=0.03,  # 적당히 느림: 기적 목격 효과는 지속적
            min_target_value=0.0,
        )
        # 검증: 이 rule이 agent-agnostic하지 않음 (content 설정)
        assert inhibitor.subject_agent_id == "judas"
        assert inhibitor.target_field_path == "domain_state.disillusionment"

    def test_no_judas_present_no_crash(self):
        """subject agent (Judas) 없으면 rule apply는 no-op."""
        inhibitor = FieldAttenuationRule(
            subject_agent_id="judas",
            target_field_path="domain_state.disillusionment",
            trigger_agent_id="peter",
            trigger_field_path="emotions.awe",
            trigger_threshold=5.0, attenuation_per_hour=0.05,
        )
        peter = _agent("peter", awe=8.0)
        # Judas 없는 상황에서 Peter state 전달
        result = inhibitor.apply(peter, _ctx(all_agents={"peter": peter}))
        # peter는 subject가 아니므로 변경 없음
        assert result is peter


class TestDocumentedIntent:
    def test_gemini_review_feedback_addressed(self):
        """문서화 검증: Gemini 지적 반영 — inhibitor rule 존재 확인."""
        from engine.rules import inhibitor as module
        # module 존재 + 클래스 2개 export
        assert hasattr(module, "FieldAttenuationRule")
        assert hasattr(module, "FieldAmplificationRule")
        # docstring에 reviewer 피드백 명시
        assert "Inhibitor" in module.__doc__
        assert "Gemini" in module.__doc__ or "억제" in module.__doc__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
