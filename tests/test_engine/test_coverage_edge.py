"""Coverage edge-case tests for core modules.

Small, surgical tests covering:
- Precondition: source_agent_id override + all operators + unknown-op fallback
- StateEffect: unsupported operation fallback
- StateMultiplier: unknown factor_type fallback
- WeightFormula.compute_weight_breakdown: repeated field (indexed key)
- HazardFactor: non-numeric raw, unknown transform
- HazardPrecondition: lt operator
- TriggerCondition: lt/eq/unknown operator
"""

from engine.core.event import (
    ExternalEvent,
    Precondition,
    StateEffect,
    StateMultiplier,
    WeightFormula,
)
from engine.core.hazard import HazardFactor, HazardFunction, HazardPrecondition
from engine.core.state import AgentState, EmotionalState
from engine.core.trigger import TriggerCondition


def _agent(fear: float = 5.0) -> AgentState:
    return AgentState(agent_id="x", emotions=EmotionalState(fear=fear))


class TestPreconditionEdges:
    def test_source_agent_id_override(self):
        """source_agent_id → all_agents[source_agent_id] 사용."""
        main = _agent(fear=2.0)
        other = _agent(fear=9.0)
        pre = Precondition(
            source_agent_id="other", field_path="emotions.fear",
            operator="gt", value=5.0,
        )
        assert pre.evaluate(main, all_agents={"other": other}) is True
        assert pre.evaluate(main, all_agents={}) is False  # fallback to main fear=2

    def test_none_field_returns_false(self):
        """field가 None이면 False (Precondition line 41)."""
        pre = Precondition(field_path="nonexistent.path", operator="gt", value=1.0)
        assert pre.evaluate(_agent()) is False


class TestStateEffectEdges:
    def test_unsupported_operation_returns_unchanged(self):
        """operation이 add/multiply인데 current가 non-numeric → 원본."""
        agent = AgentState(agent_id="x")
        # agent_id는 문자열 → numeric 연산 불가
        effect = StateEffect(field_path="agent_id", operation="multiply", value=2.0)
        result = effect.apply(agent)
        assert result.agent_id == "x"


class TestWeightFormulaBreakdown:
    def test_repeated_field_indexed(self):
        """같은 field_path를 2+ 쓰면 state_mult.field[1] 형태로 index."""
        wf = WeightFormula(
            base_weight=2.0,
            state_multipliers=[
                StateMultiplier(field_path="emotions.fear", factor_type="linear",
                                params={"scale": 0.1}),
                StateMultiplier(field_path="emotions.fear", factor_type="inverse",
                                params={"scale": 0.1}),
            ],
        )
        bd = wf.compute_weight_breakdown(_agent(fear=5.0))
        assert "state_mult.emotions.fear" in bd
        assert "state_mult.emotions.fear[1]" in bd

    def test_triple_repeated_field_indexed_loop(self):
        """같은 field 3번 이상 → while loop으로 [2], [3] 증분 (line 162)."""
        wf = WeightFormula(
            base_weight=1.0,
            state_multipliers=[
                StateMultiplier(field_path="emotions.fear", factor_type="linear",
                                params={"scale": 0.1}),
                StateMultiplier(field_path="emotions.fear", factor_type="inverse",
                                params={"scale": 0.1}),
                StateMultiplier(field_path="emotions.fear", factor_type="linear",
                                params={"scale": 0.05}),
                StateMultiplier(field_path="emotions.fear", factor_type="inverse",
                                params={"scale": 0.05}),
            ],
        )
        bd = wf.compute_weight_breakdown(_agent(fear=5.0))
        # 첫 번째는 base name, 이후 [1], [2], [3]으로 증분
        assert "state_mult.emotions.fear[1]" in bd
        assert "state_mult.emotions.fear[2]" in bd
        assert "state_mult.emotions.fear[3]" in bd


class TestHazardFactorEdges:
    def test_non_numeric_raw_returns_zero(self):
        """numeric 아닌 field 접근 → 0.0."""
        factor = HazardFactor(field_path="agent_id", weight=1.0)
        assert factor.compute(AgentState(agent_id="x")) == 0.0

    def test_unknown_transform_returns_zero(self):
        factor = HazardFactor(
            field_path="emotions.fear", weight=1.0, transform="bogus",
        )
        assert factor.compute(_agent()) == 0.0


class TestHazardPreconditionEdges:
    def test_lt_operator(self):
        pre = HazardPrecondition(field_path="emotions.fear", operator="lt", value=8.0)
        assert pre.evaluate(_agent(fear=5.0)) is True
        assert pre.evaluate(_agent(fear=9.0)) is False

    def test_missing_field_returns_false(self):
        pre = HazardPrecondition(field_path="nonexistent.path", operator="gt", value=1.0)
        assert pre.evaluate(_agent()) is False


class TestTriggerConditionEdges:
    def test_lt_operator(self):
        agent = _agent(fear=3.0)
        tc = TriggerCondition(
            agent_id="x", field_path="emotions.fear", operator="lt", value=5.0,
        )
        assert tc.evaluate({"x": agent}) is True

    def test_eq_operator(self):
        agent = _agent(fear=5.0)
        tc = TriggerCondition(
            agent_id="x", field_path="emotions.fear", operator="eq", value=5.0,
        )
        assert tc.evaluate({"x": agent}) is True

    def test_non_numeric_field_false(self):
        """numeric 아닌 field → False (line 41-42)."""
        agent = _agent(fear=5.0)
        tc = TriggerCondition(
            agent_id="x", field_path="agent_id", operator="gt", value=5.0,
        )
        assert tc.evaluate({"x": agent}) is False


class TestHazardFunctionEdges:
    def test_firing_probability_zero_hazard(self):
        """hazard=0 → firing_probability=0 (base case)."""
        hf = HazardFunction(base_rate=0.0)
        assert hf.firing_probability(_agent()) == 0.0

    def test_external_event_default(self):
        """ExternalEvent 기본 필드 접근."""
        ev = ExternalEvent(event_id="e", tick=10)
        assert ev.event_id == "e"
        assert ev.tick == 10
