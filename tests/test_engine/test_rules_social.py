"""Social rules unit tests."""

import random

from engine.core.state import AgentState, EmotionalState
from engine.rules.base import RuleContext
from engine.rules.social import RelationshipDecayRule


def _ctx(delta_tick: int = 1) -> RuleContext:
    return RuleContext(
        tick=0, delta_tick=delta_tick, rng=random.Random(0), all_agents={},
    )


class TestRelationshipDecayRule:
    def test_no_relationships_returns_state_unchanged(self):
        """relationships가 비어있으면 원본 반환 (line 21)."""
        state = AgentState(agent_id="x", emotions=EmotionalState())
        rule = RelationshipDecayRule()
        result = rule.apply(state, _ctx())
        assert result is state  # short-circuit

    def test_drift_toward_baseline(self):
        """trust가 baseline으로 수렴."""
        from engine.core.state import Relationship
        state = AgentState(
            agent_id="x", emotions=EmotionalState(),
            relationships={"peter": Relationship(target_id="peter", trust=2.0)},
        )
        rule = RelationshipDecayRule(baseline=5.0, drift_rate=0.1)
        result = rule.apply(state, _ctx(delta_tick=1))
        # trust < baseline이면 증가
        assert result.relationships["peter"].trust > 2.0
