"""content/peter/domain_faith.py 단위 테스트."""

import pytest
from pydantic import ValidationError

from content.peter.domain_faith import (
    FaithJourneyState,
    FearProfile,
    RepentanceCycle,
)
from engine.core.state import AgentState


class TestFearProfile:
    def test_defaults(self):
        fp = FearProfile()
        assert fp.natural == 3.0
        assert fp.social == 4.0
        assert fp.existential == 2.0
        assert fp.type == "fear_profile"

    def test_out_of_range(self):
        with pytest.raises(ValidationError):
            FearProfile(natural=11.0)


class TestRepentanceCycle:
    def test_creation(self):
        rc = RepentanceCycle(tick=170, trigger="denial", depth=9.0)
        assert rc.tick == 170
        assert rc.trigger == "denial"
        assert rc.depth == 9.0


class TestFaithJourneyState:
    def test_defaults(self):
        fjs = FaithJourneyState()
        assert fjs.type == "faith_journey"
        assert fjs.jesus_understanding == "messiah_political"
        assert fjs.communal_role == "inner_circle"
        assert fjs.obedience_maturity == 5.0
        assert fjs.repentance_history == []

    def test_state_transitions(self):
        """상태 전환: inner_circle -> failed (부인 시나리오)."""
        fjs = FaithJourneyState(communal_role="inner_circle")
        updated = fjs.model_copy(update={"communal_role": "failed"})
        assert updated.communal_role == "failed"
        assert fjs.communal_role == "inner_circle"  # 원본 불변

    def test_repentance_append(self):
        fjs = FaithJourneyState()
        cycle = RepentanceCycle(tick=175, trigger="rooster_crow", depth=9.5)
        updated = fjs.model_copy(
            update={"repentance_history": [*fjs.repentance_history, cycle]}
        )
        assert len(updated.repentance_history) == 1
        assert updated.repentance_history[0].trigger == "rooster_crow"

    def test_integration_with_agent_state(self):
        """AgentState.domain_state로 FaithJourneyState를 사용할 수 있다."""
        fjs = FaithJourneyState(
            jesus_understanding="son_of_god",
            communal_role="restored",
        )
        agent = AgentState(agent_id="test", domain_state=fjs)
        assert agent.domain_state is not None
        assert agent.domain_state.type == "faith_journey"

    def test_full_journey(self):
        """전체 여정: messiah_political -> failed -> restored -> shepherd."""
        fjs = FaithJourneyState()
        assert fjs.jesus_understanding == "messiah_political"

        # 수난 전 이해 깊어짐
        fjs = fjs.model_copy(update={"jesus_understanding": "messiah_suffering"})

        # 부인
        fjs = fjs.model_copy(update={
            "communal_role": "failed",
            "repentance_history": [
                RepentanceCycle(tick=175, trigger="denial", depth=9.0),
            ],
        })
        assert fjs.communal_role == "failed"

        # 부활 후 회복
        fjs = fjs.model_copy(update={
            "communal_role": "restored",
            "jesus_understanding": "risen_lord",
        })

        # 디베랴 -- 양을 먹이라
        fjs = fjs.model_copy(update={
            "communal_role": "shepherd",
            "jesus_understanding": "sending_lord",
        })
        assert fjs.communal_role == "shepherd"
        assert fjs.jesus_understanding == "sending_lord"
