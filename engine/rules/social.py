"""사회적 관계 전이 규칙.

관계 변화, 고립 효과를 처리한다.
"""

from __future__ import annotations

from engine.core.state import AgentState, Relationship, clamp
from engine.rules.base import RuleContext


class RelationshipDecayRule:
    """관계 자연 감쇠. 상호작용 없으면 trust가 서서히 중앙으로 이동."""

    def __init__(self, baseline: float = 5.0, drift_rate: float = 0.002) -> None:
        self.baseline = baseline
        self.drift_rate = drift_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        if not state.relationships:
            return state

        new_rels: dict[str, Relationship] = {}
        for key, rel in state.relationships.items():
            diff = self.baseline - rel.trust
            new_trust = clamp(rel.trust + diff * self.drift_rate * context.delta_tick)
            new_rels[key] = rel.model_copy(update={"trust": new_trust})

        return state.model_copy(update={"relationships": new_rels})


class GroupIsolationRule:
    """고립 규칙. 동료와 분리되면 사회적 두려움이 간접적으로 증가.

    직접 fear를 올리지 않고, 관계의 trust를 감소시킨다.
    fear 증가는 FearResponseRule의 고립 감지로 처리.
    """

    def __init__(self, isolation_decay: float = 0.01) -> None:
        self.isolation_decay = isolation_decay

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        # 이벤트에서 "isolation" 키워드 감지
        is_isolated = any(
            "isolation" in e.event_id or "alone" in e.event_id
            for e in context.active_events
        )
        if not is_isolated:
            return state

        new_rels: dict[str, Relationship] = {}
        for key, rel in state.relationships.items():
            new_trust = clamp(rel.trust - self.isolation_decay * context.delta_tick)
            new_rels[key] = rel.model_copy(update={"trust": new_trust})

        return state.model_copy(update={"relationships": new_rels})
