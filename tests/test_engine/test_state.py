"""engine/core/state.py 단위 테스트."""

import pytest
from pydantic import ValidationError

from engine.core.state import (
    AgentState,
    DomainState,
    EmotionalState,
    PhysicalState,
    Relationship,
    clamp,
    get_nested_value,
    set_nested_value,
)


class TestPhysicalState:
    def test_defaults(self):
        ps = PhysicalState()
        assert ps.fatigue == 0.0
        assert ps.health == 10.0
        assert ps.location == "unknown"

    def test_valid_range(self):
        ps = PhysicalState(fatigue=5.0, hunger=3.0, health=7.0)
        assert ps.fatigue == 5.0

    def test_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            PhysicalState(fatigue=11.0)
        with pytest.raises(ValidationError):
            PhysicalState(health=-1.0)


class TestEmotionalState:
    def test_defaults(self):
        es = EmotionalState()
        assert es.fear == 0.0
        assert es.hope == 5.0

    def test_boundary_values(self):
        es = EmotionalState(fear=0.0, hope=10.0, grief=0.0, confusion=10.0, love=0.0)
        assert es.fear == 0.0
        assert es.confusion == 10.0

    def test_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            EmotionalState(fear=-0.1)
        with pytest.raises(ValidationError):
            EmotionalState(love=10.1)


class TestRelationship:
    def test_creation(self):
        r = Relationship(target_id="jesus")
        assert r.target_id == "jesus"
        assert r.trust == 5.0

    def test_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            Relationship(target_id="x", trust=11.0)


class TestDomainState:
    def test_base_domain(self):
        ds = DomainState()
        assert ds.type == "base"

    def test_custom_type(self):
        ds = DomainState(type="faith_journey")
        assert ds.type == "faith_journey"


class TestAgentState:
    def test_minimal_creation(self):
        agent = AgentState(agent_id="test")
        assert agent.agent_id == "test"
        assert agent.tick == 0
        assert agent.physical.fatigue == 0.0
        assert agent.emotions.fear == 0.0
        assert agent.relationships == {}
        assert agent.domain_state is None

    def test_full_creation(self):
        agent = AgentState(
            agent_id="test",
            tick=10,
            physical=PhysicalState(fatigue=5.0, location="jerusalem"),
            emotions=EmotionalState(fear=7.0, hope=3.0),
            relationships={
                "jesus": Relationship(target_id="jesus", trust=8.0, awe=9.0),
            },
            domain_state=DomainState(type="faith_journey"),
        )
        assert agent.tick == 10
        assert agent.physical.location == "jerusalem"
        assert agent.emotions.fear == 7.0
        assert agent.relationships["jesus"].awe == 9.0

    def test_immutable_copy(self):
        """model_copy로 갱신 시 원본이 변경되지 않는다."""
        original = AgentState(agent_id="test", tick=0)
        updated = original.model_copy(
            update={"tick": 1, "emotions": EmotionalState(fear=5.0)}
        )
        assert original.tick == 0
        assert original.emotions.fear == 0.0
        assert updated.tick == 1
        assert updated.emotions.fear == 5.0

    def test_serialization_roundtrip(self):
        """JSON 직렬화/역직렬화 왕복."""
        agent = AgentState(
            agent_id="test",
            tick=5,
            emotions=EmotionalState(fear=3.0),
            relationships={"a": Relationship(target_id="a", trust=7.0)},
        )
        json_str = agent.model_dump_json()
        restored = AgentState.model_validate_json(json_str)
        assert restored.agent_id == "test"
        assert restored.emotions.fear == 3.0
        assert restored.relationships["a"].trust == 7.0


class TestClamp:
    def test_within_range(self):
        assert clamp(5.0) == 5.0

    def test_below_min(self):
        assert clamp(-1.0) == 0.0

    def test_above_max(self):
        assert clamp(11.0) == 10.0

    def test_custom_range(self):
        assert clamp(15.0, 0.0, 20.0) == 15.0
        assert clamp(-5.0, -10.0, 10.0) == -5.0


class TestGetNestedValue:
    def test_top_level(self):
        agent = AgentState(agent_id="test", tick=5)
        assert get_nested_value(agent, "tick") == 5

    def test_two_level(self):
        agent = AgentState(agent_id="test", emotions=EmotionalState(fear=7.0))
        assert get_nested_value(agent, "emotions.fear") == 7.0

    def test_relationship_three_level(self):
        agent = AgentState(
            agent_id="test",
            relationships={"jesus": Relationship(target_id="jesus", trust=8.0)},
        )
        assert get_nested_value(agent, "relationships.jesus.trust") == 8.0

    def test_invalid_path_returns_none(self):
        agent = AgentState(agent_id="test")
        assert get_nested_value(agent, "nonexistent.field") is None

    def test_location_string(self):
        agent = AgentState(
            agent_id="test", physical=PhysicalState(location="jerusalem")
        )
        assert get_nested_value(agent, "physical.location") == "jerusalem"


class TestSetNestedValue:
    def test_two_level(self):
        agent = AgentState(agent_id="test", emotions=EmotionalState(fear=3.0))
        new_agent = set_nested_value(agent, "emotions.fear", 8.0)
        assert new_agent.emotions.fear == 8.0
        assert agent.emotions.fear == 3.0  # 원본 불변

    def test_physical_field(self):
        agent = AgentState(agent_id="test")
        new_agent = set_nested_value(agent, "physical.fatigue", 7.0)
        assert new_agent.physical.fatigue == 7.0

    def test_relationship_three_level(self):
        agent = AgentState(
            agent_id="test",
            relationships={"jesus": Relationship(target_id="jesus", trust=5.0)},
        )
        new_agent = set_nested_value(agent, "relationships.jesus.trust", 9.0)
        assert new_agent.relationships["jesus"].trust == 9.0
        assert agent.relationships["jesus"].trust == 5.0  # 원본 불변

    def test_invalid_path_returns_same(self):
        agent = AgentState(agent_id="test")
        result = set_nested_value(agent, "nonexistent.deep.path", 5.0)
        assert result.agent_id == "test"  # 에러 없이 원본 반환

    def test_basemodel_deep_path_returns_state(self):
        """BaseModel 필드에 3+ depth 접근 → fallback (line 219)."""
        agent = AgentState(agent_id="test")
        # emotions는 BaseModel. emotions.fear.something은 유효하지 않음
        result = set_nested_value(agent, "emotions.fear.subfield", 5.0)
        # 에러 없이 원본 유사 반환
        assert result.agent_id == "test"

    def test_dict_key_missing_returns_state(self):
        """dict 필드에 없는 key → fallback (line 232)."""
        agent = AgentState(
            agent_id="test",
            relationships={"jesus": Relationship(target_id="jesus", trust=5.0)},
        )
        result = set_nested_value(agent, "relationships.unknown.trust", 9.0)
        # unknown이 relationships에 없으므로 원본 반환
        assert result.relationships == agent.relationships
