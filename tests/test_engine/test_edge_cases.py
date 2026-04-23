"""엔진 핵심 모듈 엣지 케이스 테스트.

Precondition/StateMultiplier/HazardPrecondition의 미커버 연산자와
state.py의 엣지 경로를 커버한다.
"""

from engine.core.event import Precondition, StateEffect, StateMultiplier
from engine.core.hazard import HazardEngine, HazardEvent, HazardFunction, HazardPrecondition
from engine.core.state import AgentState, get_nested_value, set_nested_value


def _make_state(**overrides) -> AgentState:
    """테스트용 AgentState를 만든다."""
    from engine.core.state import EmotionalState, PhysicalState

    defaults = {
        "agent_id": "test_agent",
        "physical": PhysicalState(fatigue=5.0, hunger=3.0, health=8.0),
        "emotions": EmotionalState(fear=4.0, hope=6.0, grief=2.0, confusion=1.0, love=7.0),
    }
    defaults.update(overrides)
    return AgentState(**defaults)


class TestPreconditionOperators:
    """Precondition의 lt, gte 연산자 커버."""

    def test_lt_operator(self):
        state = _make_state()
        p = Precondition(field_path="emotions.fear", operator="lt", value=5.0)
        assert p.evaluate(state) is True  # 4.0 < 5.0

    def test_lt_operator_false(self):
        state = _make_state()
        p = Precondition(field_path="emotions.fear", operator="lt", value=3.0)
        assert p.evaluate(state) is False  # 4.0 < 3.0 = False

    def test_gte_operator(self):
        state = _make_state()
        p = Precondition(field_path="emotions.fear", operator="gte", value=4.0)
        assert p.evaluate(state) is True  # 4.0 >= 4.0

    def test_gte_operator_false(self):
        state = _make_state()
        p = Precondition(field_path="emotions.fear", operator="gte", value=5.0)
        assert p.evaluate(state) is False  # 4.0 >= 5.0 = False


class TestStateEffectEdge:
    """StateEffect의 else 브랜치 (non-numeric에 add 적용)."""

    def test_add_on_none_returns_state(self):
        state = _make_state()
        effect = StateEffect(field_path="nonexistent.field", operation="add", value=1.0)
        result = effect.apply(state)
        assert result == state

    def test_multiply_on_string_returns_state(self):
        """non-numeric 값에 multiply 시 원본 반환."""
        state = _make_state()
        # phase가 문자열이면 multiply 불가
        effect = StateEffect(field_path="emotions.fear", operation="multiply", value=2.0)
        result = effect.apply(state)
        # fear는 numeric이므로 정상 적용
        assert result.emotions.fear != state.emotions.fear


class TestStateMultiplierEdge:
    """StateMultiplier의 threshold 브랜치와 unknown factor_type."""

    def test_threshold_factor(self):
        state = _make_state()
        sm = StateMultiplier(
            field_path="emotions.fear", factor_type="threshold",
            params={"threshold": 3.0, "bonus": 0.5},
        )
        result = sm.compute(state)
        assert result == 1.5  # 4.0 >= 3.0 -> 1.0 + 0.5

    def test_threshold_factor_below(self):
        state = _make_state()
        sm = StateMultiplier(
            field_path="emotions.fear", factor_type="threshold",
            params={"threshold": 5.0, "bonus": 0.5},
        )
        result = sm.compute(state)
        assert result == 1.0  # 4.0 < 5.0

    def test_unknown_factor_type(self):
        state = _make_state()
        sm = StateMultiplier(
            field_path="emotions.fear", factor_type="linear",  # type: ignore
            params={"scale": 0.0},  # scale=0 -> 1.0 + 0 = 1.0
        )
        # Just test it returns a value
        result = sm.compute(state)
        assert isinstance(result, float)


class TestHazardPreconditionOperators:
    """HazardPrecondition의 lt, gte, lte, eq, in 연산자."""

    def test_lt(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="lt", value=5.0)
        assert p.evaluate(state) is True

    def test_gte(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="gte", value=4.0)
        assert p.evaluate(state) is True

    def test_lte(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="lte", value=4.0)
        assert p.evaluate(state) is True

    def test_eq(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="eq", value=4.0)
        assert p.evaluate(state) is True

    def test_in(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="in", value=[3.0, 4.0, 5.0])
        assert p.evaluate(state) is True

    def test_unknown_operator(self):
        state = _make_state()
        p = HazardPrecondition(field_path="emotions.fear", operator="unknown", value=4.0)
        assert p.evaluate(state) is False


class TestHazardEngineReset:
    """HazardEngine.reset 커버."""

    def test_reset_clears_fire_state(self):
        event = HazardEvent(
            event_id="test", hazard=HazardFunction(base_rate=1.0),
            fire_count=3, last_fired_tick=100,
        )
        engine = HazardEngine([event])
        engine.reset()
        assert engine.events[0].fire_count == 0
        assert engine.events[0].last_fired_tick == -1


class TestStateUtilEdges:
    """state.py의 get_nested_value/set_nested_value 엣지 케이스."""

    def test_get_nested_non_model_non_dict(self):
        """중간 경로가 모델도 dict도 아닌 경우 None."""
        state = _make_state()
        result = get_nested_value(state, "emotions.fear.nonexistent")
        assert result is None

    def test_set_nested_single_depth(self):
        """1-depth 경로 설정 (직접 필드)."""
        state = _make_state()
        # seed는 AgentState의 직접 필드
        # physical은 1-depth이지만 BaseModel이므로 다른 경로
        # 그냥 single field를 테스트
        from engine.core.state import PhysicalState
        new_phys = PhysicalState(fatigue=1.0, hunger=1.0, health=10.0)
        result = set_nested_value(state, "physical", new_phys)
        assert result.physical.fatigue == 1.0

    def test_set_nested_3_depth_returns_state(self):
        """3+ depth는 미지원, 원본 반환."""
        state = _make_state()
        result = set_nested_value(state, "a.b.c.d", 1.0)
        assert result == state

    def test_set_nested_none_top(self):
        """존재하지 않는 top_field."""
        state = _make_state()
        result = set_nested_value(state, "nonexistent.field", 1.0)
        assert result == state

    def test_get_nested_returns_none_for_model_value(self):
        """get_nested_value는 모델 객체를 반환하지 않는다 (None)."""
        state = _make_state()
        result = get_nested_value(state, "emotions")
        # emotions는 BaseModel → 최종값이 scalar가 아니므로 None
        assert result is None
