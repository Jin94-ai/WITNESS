"""engine/core/event.py 단위 테스트."""

from engine.core.event import (
    ActionOption,
    CanonicalIntervention,
    ExternalEvent,
    Precondition,
    StateEffect,
    StateMultiplier,
    WeightFormula,
)
from engine.core.state import AgentState, EmotionalState, PhysicalState, Relationship


def _make_agent(**kwargs) -> AgentState:
    defaults = {
        "agent_id": "test",
        "emotions": EmotionalState(fear=5.0, hope=5.0),
        "physical": PhysicalState(fatigue=5.0),
        "relationships": {
            "jesus": Relationship(target_id="jesus", trust=8.0),
        },
    }
    defaults.update(kwargs)
    return AgentState(**defaults)


class TestPrecondition:
    def test_gt(self):
        agent = _make_agent()
        assert Precondition(field_path="emotions.fear", operator="gt", value=4.0).evaluate(agent)
        assert not Precondition(field_path="emotions.fear", operator="gt", value=5.0).evaluate(agent)

    def test_lte(self):
        agent = _make_agent()
        assert Precondition(field_path="emotions.fear", operator="lte", value=5.0).evaluate(agent)

    def test_eq(self):
        agent = _make_agent()
        assert Precondition(field_path="physical.location", operator="eq", value="unknown").evaluate(agent)

    def test_in_operator(self):
        agent = _make_agent()
        p = Precondition(field_path="physical.location", operator="in", value=["unknown", "jerusalem"])
        assert p.evaluate(agent)

    def test_invalid_path(self):
        agent = _make_agent()
        assert not Precondition(field_path="nonexistent", operator="gt", value=0).evaluate(agent)


class TestStateEffect:
    def test_set(self):
        agent = _make_agent()
        result = StateEffect(field_path="emotions.fear", operation="set", value=9.0).apply(agent)
        assert result.emotions.fear == 9.0
        assert agent.emotions.fear == 5.0  # 원본 불변

    def test_add(self):
        agent = _make_agent()
        result = StateEffect(field_path="emotions.fear", operation="add", value=3.0).apply(agent)
        assert result.emotions.fear == 8.0

    def test_add_clamped(self):
        agent = _make_agent()
        result = StateEffect(field_path="emotions.fear", operation="add", value=7.0).apply(agent)
        assert result.emotions.fear == 10.0  # clamped

    def test_multiply(self):
        agent = _make_agent()
        result = StateEffect(field_path="physical.fatigue", operation="multiply", value=1.5).apply(agent)
        assert result.physical.fatigue == 7.5

    def test_invalid_path(self):
        agent = _make_agent()
        result = StateEffect(field_path="nonexistent.field", operation="add", value=1.0).apply(agent)
        assert result == agent  # 변경 없음


class TestStateMultiplier:
    def test_linear(self):
        agent = _make_agent()
        m = StateMultiplier(field_path="emotions.fear", factor_type="linear", params={"scale": 0.1})
        # fear=5.0 -> 1.0 + 5.0 * 0.1 = 1.5
        assert m.compute(agent) == 1.5

    def test_inverse(self):
        agent = _make_agent()
        m = StateMultiplier(field_path="emotions.fear", factor_type="inverse", params={"scale": 0.1})
        # fear=5.0 -> 1.0 + (10-5) * 0.1 = 1.5
        assert m.compute(agent) == 1.5

    def test_threshold_above(self):
        agent = _make_agent()
        m = StateMultiplier(
            field_path="emotions.fear", factor_type="threshold",
            params={"threshold": 4.0, "bonus": 0.5},
        )
        assert m.compute(agent) == 1.5  # fear=5 >= 4

    def test_threshold_below(self):
        agent = _make_agent()
        m = StateMultiplier(
            field_path="emotions.fear", factor_type="threshold",
            params={"threshold": 6.0, "bonus": 0.5},
        )
        assert m.compute(agent) == 1.0  # fear=5 < 6

    def test_invalid_path(self):
        agent = _make_agent()
        m = StateMultiplier(field_path="nonexistent", factor_type="linear", params={"scale": 0.1})
        assert m.compute(agent) == 1.0


class TestWeightFormula:
    def test_base_only(self):
        agent = _make_agent()
        wf = WeightFormula(base_weight=0.5)
        assert wf.compute_weight(agent) == 0.5

    def test_with_multipliers(self):
        agent = _make_agent()
        wf = WeightFormula(
            base_weight=1.0,
            state_multipliers=[
                StateMultiplier(field_path="emotions.fear", factor_type="linear", params={"scale": 0.1}),
            ],
        )
        # 1.0 * (1.0 + 5.0*0.1) = 1.0 * 1.5 = 1.5
        assert wf.compute_weight(agent) == 1.5

    def test_minimum_weight(self):
        """가중치가 0 이하로 내려가지 않는다."""
        agent = _make_agent()
        wf = WeightFormula(base_weight=0.0)
        assert wf.compute_weight(agent) == 0.001


class TestCanonicalIntervention:
    def test_apply_overrides(self):
        agent = _make_agent()
        intervention = CanonicalIntervention(
            event_id="restoration",
            tick=360,
            scripture_ref="요 21:15-17",
            state_overrides={
                "emotions.grief": 2.0,
                "emotions.love": 9.0,
            },
        )
        result = intervention.apply(agent)
        assert result.emotions.grief == 2.0
        assert result.emotions.love == 9.0
        assert agent.emotions.grief == 0.0  # 원본 불변

    def test_override_relationship(self):
        agent = _make_agent()
        intervention = CanonicalIntervention(
            event_id="test",
            tick=100,
            scripture_ref="test",
            state_overrides={"relationships.jesus.trust": 10.0},
        )
        result = intervention.apply(agent)
        assert result.relationships["jesus"].trust == 10.0


class TestExternalEvent:
    def test_creation(self):
        event = ExternalEvent(
            event_id="scene_01",
            tick=1,
            effects=[StateEffect(field_path="emotions.hope", operation="add", value=3.0)],
            action_options=[
                ActionOption(
                    action_id="join",
                    weight_formula=WeightFormula(base_weight=0.5),
                ),
            ],
        )
        assert event.event_id == "scene_01"
        assert len(event.effects) == 1
        assert len(event.action_options) == 1

    def test_apply_effects(self):
        agent = _make_agent()
        event = ExternalEvent(
            event_id="test",
            tick=1,
            effects=[
                StateEffect(field_path="emotions.fear", operation="add", value=2.0),
                StateEffect(field_path="physical.fatigue", operation="add", value=1.0),
            ],
        )
        result = agent
        for effect in event.effects:
            result = effect.apply(result)
        assert result.emotions.fear == 7.0
        assert result.physical.fatigue == 6.0
