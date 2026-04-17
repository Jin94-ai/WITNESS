"""규칙 엔진 단위 테스트."""

import random

from engine.core.event import ExternalEvent
from engine.core.state import AgentState, EmotionalState, PhysicalState, Relationship
from engine.rules.base import RuleContext, RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HomeostasisRule


def _ctx(tick: int = 0, events: list[ExternalEvent] | None = None) -> RuleContext:
    return RuleContext(tick=tick, active_events=events or [], rng=random.Random(42))


def _agent(**kwargs) -> AgentState:
    defaults = {
        "agent_id": "test",
        "physical": PhysicalState(fatigue=5.0, hunger=3.0, health=8.0),
        "emotions": EmotionalState(fear=5.0, hope=5.0, grief=2.0, confusion=3.0, love=6.0),
        "relationships": {
            "ally": Relationship(target_id="ally", trust=7.0),
        },
    }
    defaults.update(kwargs)
    return AgentState(**defaults)


class TestFatigueRule:
    def test_natural_increase(self):
        agent = _agent()
        result = FatigueRule().apply(agent, _ctx())
        assert result.physical.fatigue > 5.0

    def test_rest_recovery(self):
        agent = _agent(physical=PhysicalState(fatigue=7.0))
        ctx = _ctx(events=[ExternalEvent(event_id="rest_event", tick=0)])
        result = FatigueRule().apply(agent, ctx)
        assert result.physical.fatigue < 7.0


class TestHungerRule:
    def test_natural_increase(self):
        agent = _agent()
        result = HungerRule().apply(agent, _ctx())
        assert result.physical.hunger > 3.0

    def test_meal_recovery(self):
        agent = _agent(physical=PhysicalState(hunger=6.0))
        ctx = _ctx(events=[ExternalEvent(event_id="meal_event", tick=0)])
        result = HungerRule().apply(agent, ctx)
        assert result.physical.hunger < 6.0


class TestHealthRule:
    def test_no_degradation_normal(self):
        agent = _agent()
        result = HealthRule().apply(agent, _ctx())
        assert result.physical.health == 8.0  # fatigue=5 < threshold=8

    def test_degradation_high_fatigue(self):
        agent = _agent(physical=PhysicalState(fatigue=9.0, health=8.0))
        result = HealthRule().apply(agent, _ctx())
        assert result.physical.health < 8.0


class TestFearResponseRule:
    def test_natural_decay(self):
        agent = _agent()
        result = FearResponseRule().apply(agent, _ctx())
        assert result.emotions.fear < 5.0

    def test_fatigue_amplification(self):
        """피로가 높으면 공포가 증폭된다."""
        agent = _agent(physical=PhysicalState(fatigue=9.0))
        ctx = _ctx(events=[ExternalEvent(event_id="threat", tick=0)])
        result = FearResponseRule().apply(agent, ctx)
        assert result.emotions.fear > 5.0


class TestConfusionRule:
    def test_cross_effect_fatigue_fear(self):
        """핵심 교차 효과: 피로>7 AND 공포>6 -> 혼란 증폭."""
        agent = _agent(
            physical=PhysicalState(fatigue=9.0),
            emotions=EmotionalState(fear=8.0, confusion=3.0),
        )
        result = ConfusionRule().apply(agent, _ctx())
        assert result.emotions.confusion > 3.0

    def test_no_cross_effect_below_threshold(self):
        """피로/공포가 임계값 미만이면 교차 효과 없음."""
        agent = _agent(
            physical=PhysicalState(fatigue=5.0),
            emotions=EmotionalState(fear=4.0, confusion=3.0),
        )
        result = ConfusionRule().apply(agent, _ctx())
        # 항상성 감쇠만 적용 (이벤트 없으므로)
        assert result.emotions.confusion <= 3.0

    def test_grief_hope_cross_effect(self):
        """슬픔>8 AND 희망<3 -> 혼란 증가."""
        agent = _agent(
            emotions=EmotionalState(grief=9.0, hope=1.0, confusion=3.0),
        )
        result = ConfusionRule().apply(agent, _ctx())
        assert result.emotions.confusion > 3.0


class TestGriefRule:
    def test_natural_decay(self):
        agent = _agent(emotions=EmotionalState(grief=5.0))
        result = GriefRule().apply(agent, _ctx())
        assert result.emotions.grief < 5.0


class TestHopeRule:
    def test_grief_suppresses_hope(self):
        agent = _agent(emotions=EmotionalState(hope=5.0, grief=8.0))
        result = HopeRule().apply(agent, _ctx())
        assert result.emotions.hope < 5.0


class TestRelationshipDecayRule:
    def test_drift_to_baseline(self):
        agent = _agent()
        result = RelationshipDecayRule().apply(agent, _ctx())
        # trust 7.0 -> baseline 5.0 방향으로 미세 이동
        assert result.relationships["ally"].trust < 7.0


class TestGroupIsolationRule:
    def test_no_effect_without_isolation(self):
        agent = _agent()
        result = GroupIsolationRule().apply(agent, _ctx())
        assert result.relationships["ally"].trust == 7.0

    def test_trust_decay_on_isolation(self):
        agent = _agent()
        ctx = _ctx(events=[ExternalEvent(event_id="isolation_event", tick=0)])
        result = GroupIsolationRule().apply(agent, ctx)
        assert result.relationships["ally"].trust < 7.0


class TestHomeostasisRule:
    def test_extreme_values_decay(self):
        agent = _agent(emotions=EmotionalState(fear=10.0, hope=0.0))
        result = HomeostasisRule().apply(agent, _ctx())
        assert result.emotions.fear < 10.0
        assert result.emotions.hope > 0.0


class TestCircadianRule:
    def test_produces_variation(self):
        """다른 tick에서 다른 피로 변화가 발생한다."""
        agent = _agent()
        r1 = CircadianRule().apply(agent, _ctx(tick=3))  # 낮
        r2 = CircadianRule().apply(agent, _ctx(tick=9))  # 밤
        assert r1.physical.fatigue != r2.physical.fatigue


class TestRuleEngine:
    def test_sequential_application(self):
        """규칙이 순차 적용된다."""
        engine = RuleEngine([FatigueRule(), FearResponseRule()])
        agent = _agent()
        result = engine.apply_all(agent, _ctx())
        assert result.physical.fatigue != agent.physical.fatigue
        assert result.emotions.fear != agent.emotions.fear

    def test_empty_rules(self):
        engine = RuleEngine([])
        agent = _agent()
        result = engine.apply_all(agent, _ctx())
        assert result == agent


class TestSlowStateRule:
    def test_extreme_fear_adds_trauma(self):
        """극한 공포 시 event_trauma 누적."""
        from engine.rules.temporal import SlowStateRule
        agent = _agent(emotions=EmotionalState(fear=9.0))
        ctx = _ctx(events=[ExternalEvent(event_id="threat", tick=0)])
        result = SlowStateRule().apply(agent, ctx)
        assert result.slow_state.event_trauma > 0

    def test_extreme_grief_adds_trauma(self):
        """극한 슬픔 시 event_trauma 누적."""
        from engine.rules.temporal import SlowStateRule
        agent = _agent(emotions=EmotionalState(grief=9.0))
        result = SlowStateRule().apply(agent, _ctx())
        assert result.slow_state.event_trauma > 0

    def test_high_hope_positive_identity(self):
        """높은 희망 시 identity_shift 양수 이동."""
        from engine.rules.temporal import SlowStateRule
        agent = _agent(emotions=EmotionalState(hope=8.0))
        result = SlowStateRule().apply(agent, _ctx())
        assert result.slow_state.identity_shift > 0

    def test_high_fear_low_hope_negative_identity(self):
        """공포 높고 희망 낮으면 identity 음수."""
        from engine.rules.temporal import SlowStateRule
        agent = _agent(emotions=EmotionalState(fear=8.0, hope=2.0))
        result = SlowStateRule().apply(agent, _ctx())
        assert result.slow_state.identity_shift < 0

    def test_no_change_when_normal(self):
        """정상 범위에서는 변화 없음."""
        from engine.rules.temporal import SlowStateRule
        agent = _agent(emotions=EmotionalState(fear=4.0, grief=3.0, hope=5.0))
        result = SlowStateRule().apply(agent, _ctx())
        assert result.slow_state.event_trauma == 0
        assert result.slow_state.identity_shift == 0


class TestHighStressConsequenceRule:
    def test_high_stress_adds_injury(self):
        """grief+fear 동시 높으면 moral_injury 누적."""
        from engine.rules.temporal import HighStressConsequenceRule
        agent = _agent(emotions=EmotionalState(grief=7.0, fear=7.0))
        ctx = _ctx(events=[ExternalEvent(event_id="crisis", tick=0)])
        result = HighStressConsequenceRule().apply(agent, ctx)
        assert result.slow_state.moral_injury > 0

    def test_no_injury_below_threshold(self):
        """임계 이하면 변화 없음."""
        from engine.rules.temporal import HighStressConsequenceRule
        agent = _agent(emotions=EmotionalState(grief=3.0, fear=3.0))
        ctx = _ctx(events=[ExternalEvent(event_id="normal", tick=0)])
        result = HighStressConsequenceRule().apply(agent, ctx)
        assert result.slow_state.moral_injury == 0

    def test_no_injury_without_events(self):
        """이벤트 없으면 변화 없음."""
        from engine.rules.temporal import HighStressConsequenceRule
        agent = _agent(emotions=EmotionalState(grief=9.0, fear=9.0))
        result = HighStressConsequenceRule().apply(agent, _ctx())
        assert result.slow_state.moral_injury == 0
