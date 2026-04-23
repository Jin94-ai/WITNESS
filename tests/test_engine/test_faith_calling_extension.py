"""FaithJourneyState 소명 phase 확장 검증 (v1.2 Iteration 6).

- EmotionalState.awe 추가 (backward compat, default 0.0)
- FaithJourneyState.jesus_understanding = None 허용 (소명 이전)
- FaithJourneyState.communal_role = None 허용 (아직 제자 아님)
- content/peter/initial_state_calling.json 로드 성공
"""

from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.core.state import AgentState, EmotionalState
from engine.io.loader import load_agent_state, register_domain_type

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


class TestEmotionalStateAwe:
    def test_default_zero(self):
        e = EmotionalState()
        assert e.awe == 0.0

    def test_backward_compat_without_awe(self):
        """기존 dict (awe 없음)에서 생성해도 문제 없음."""
        e = EmotionalState.model_validate({
            "fear": 5.0, "hope": 5.0, "grief": 0.0,
            "confusion": 0.0, "love": 5.0,
        })
        assert e.awe == 0.0

    def test_can_set_awe(self):
        e = EmotionalState(awe=7.5)
        assert e.awe == 7.5

    def test_awe_range_clamped(self):
        """0-10 범위 제약 유지."""
        import pytest
        with pytest.raises(Exception):  # pydantic ValidationError
            EmotionalState(awe=11.0)


class TestFaithJourneyStateNullable:
    def test_jesus_understanding_none_allowed(self):
        s = FaithJourneyState(jesus_understanding=None)
        assert s.jesus_understanding is None

    def test_jesus_understanding_default_still_set(self):
        """default는 여전히 'messiah_political' (backward compat)."""
        s = FaithJourneyState()
        assert s.jesus_understanding == "messiah_political"

    def test_communal_role_none_allowed(self):
        s = FaithJourneyState(communal_role=None)
        assert s.communal_role is None

    def test_jesus_understanding_literal_still_enforced(self):
        """Literal 값은 여전히 검증됨 (invalid string 거부)."""
        import pytest
        with pytest.raises(Exception):
            FaithJourneyState(jesus_understanding="bogus_value")

    def test_roundtrip_with_none(self):
        """None 필드 JSON 직렬화 round-trip."""
        s = FaithJourneyState(
            jesus_understanding=None,
            communal_role=None,
            obedience_maturity=0.0,
        )
        data = s.model_dump()
        restored = FaithJourneyState.model_validate(data)
        assert restored.jesus_understanding is None
        assert restored.communal_role is None
        assert restored.obedience_maturity == 0.0


class TestCallingInitialStateLoad:
    """content/peter/initial_state_calling.json 로드 및 구조 검증."""

    def setup_method(self):
        register_domain_type("faith_journey", FaithJourneyState)

    def test_loads_successfully(self):
        state = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        assert isinstance(state, AgentState)
        assert state.agent_id == "peter"

    def test_calling_context(self):
        """소명 phase 시작 상태의 역사적 정합성."""
        state = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        # 어부: Gennesaret 호숫가
        assert state.physical.location == "gennesaret_shore"
        # 밤새 허탕: fatigue 높음
        assert state.physical.fatigue >= 5.0
        # 예수를 아직 모름
        assert state.domain_state.jesus_understanding is None
        assert state.domain_state.communal_role is None
        # obedience_maturity 0 (아직 형성 안 됨)
        assert state.domain_state.obedience_maturity == 0.0
        # awe 없음 (아직 기적 목격 전)
        assert state.emotions.awe == 0.0

    def test_relationships_fishermen_not_disciples(self):
        """소명 이전: 관계가 동업자(andrew/james/john) 기준."""
        state = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        assert "andrew" in state.relationships
        assert "judas" not in state.relationships  # 아직 만남 없음
        assert "jesus" not in state.relationships  # 아직 개인 관계 없음

    def test_legacy_initial_state_unchanged(self):
        """기존 initial_state.json은 여전히 "messiah_political"로 로드."""
        state = load_agent_state(CONTENT / "peter" / "initial_state.json")
        assert state.domain_state.jesus_understanding == "messiah_political"
        assert state.domain_state.communal_role == "inner_circle"
