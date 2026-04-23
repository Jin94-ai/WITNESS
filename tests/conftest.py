"""공유 테스트 fixture.

반복적인 엔진/설정 생성을 fixture로 통합.

Usage:
    pytest                    # 전체 테스트 (fast + slow)
    pytest -m "not slow"      # 빠른 테스트만 (~30초)
    pytest -m slow            # 느린 테스트만
"""

from pathlib import Path

import pytest

from engine.core.state import AgentState, EmotionalState, PhysicalState, Relationship
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HighStressConsequenceRule, HomeostasisRule, SlowStateRule


@pytest.fixture
def full_rule_engine() -> RuleEngine:
    """모든 규칙을 포함한 전체 규칙 엔진."""
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), SlowStateRule(), HighStressConsequenceRule(), CircadianRule(),
    ])


@pytest.fixture
def basic_agent() -> AgentState:
    """기본 에이전트 상태."""
    return AgentState(
        agent_id="test",
        physical=PhysicalState(fatigue=5.0, hunger=3.0, health=8.0),
        emotions=EmotionalState(fear=5.0, hope=5.0, grief=2.0, confusion=3.0, love=6.0),
        relationships={
            "ally": Relationship(target_id="ally", trust=7.0),
        },
    )


PETER_CONTENT_DIR = Path(__file__).parent.parent / "content" / "peter"
VANGOGH_CONTENT_DIR = Path(__file__).parent.parent / "content" / "vangogh"
