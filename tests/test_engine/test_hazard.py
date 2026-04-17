"""Hazard 시스템 단위 테스트."""

import random

from engine.core.hazard import (
    HazardEngine,
    HazardEvent,
    HazardFactor,
    HazardFunction,
    HazardPrecondition,
)
from engine.core.state import AgentState, EmotionalState, PhysicalState


def _agent(**kwargs) -> AgentState:
    defaults = {
        "agent_id": "test",
        "emotions": EmotionalState(fear=5.0, hope=5.0),
        "physical": PhysicalState(fatigue=5.0),
    }
    defaults.update(kwargs)
    return AgentState(**defaults)


class TestHazardFunction:
    def test_base_rate_only(self):
        hf = HazardFunction(base_rate=0.1)
        assert hf.compute_hazard(_agent()) == 0.1

    def test_with_factors(self):
        hf = HazardFunction(
            base_rate=0.1,
            factors=[HazardFactor(field_path="emotions.fear", weight=0.5, transform="linear")],
        )
        agent = _agent(emotions=EmotionalState(fear=8.0))
        # 0.1 + (8/10 * 0.5) = 0.1 + 0.4 = 0.5
        assert abs(hf.compute_hazard(agent) - 0.5) < 0.01

    def test_max_hazard_clamp(self):
        hf = HazardFunction(
            base_rate=0.5,
            factors=[HazardFactor(field_path="emotions.fear", weight=2.0)],
            max_hazard=0.8,
        )
        agent = _agent(emotions=EmotionalState(fear=10.0))
        assert hf.compute_hazard(agent) == 0.8

    def test_firing_probability(self):
        hf = HazardFunction(base_rate=0.5)
        prob = hf.firing_probability(_agent())
        assert 0.0 < prob < 1.0

    def test_zero_hazard_zero_probability(self):
        hf = HazardFunction(base_rate=0.0)
        assert hf.firing_probability(_agent()) == 0.0


class TestHazardEvent:
    def test_eligible_basic(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.1),
            anchor_window=(10, 50),
        )
        assert event.is_eligible(20, _agent())
        assert not event.is_eligible(5, _agent())
        assert not event.is_eligible(60, _agent())

    def test_precondition_blocks(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.1),
            preconditions=[
                HazardPrecondition(field_path="physical.fatigue", operator="gte", value=8.0),
            ],
        )
        low_fatigue = _agent(physical=PhysicalState(fatigue=3.0))
        high_fatigue = _agent(physical=PhysicalState(fatigue=9.0))
        assert not event.is_eligible(10, low_fatigue)
        assert event.is_eligible(10, high_fatigue)

    def test_max_fires(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.1),
            max_fires=2,
        )
        event.record_fire(10)
        assert event.is_eligible(20, _agent())  # 1/2
        event.record_fire(20)
        assert not event.is_eligible(30, _agent())  # 2/2 -- exhausted

    def test_cooldown(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.1),
            max_fires=3,
            cooldown=5,
        )
        event.record_fire(10)
        assert not event.is_eligible(12, _agent())  # 10+5=15 전
        assert event.is_eligible(16, _agent())  # 쿨다운 해제

    def test_deadline(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.001),
            deadline_tick=100,
        )
        assert not event.is_deadline(50)
        assert event.is_deadline(100)


class TestHazardEngine:
    def test_fires_probabilistically(self):
        """높은 hazard 이벤트는 자주 발동한다."""
        event = HazardEvent(
            event_id="high_hazard",
            hazard=HazardFunction(base_rate=0.8),
            max_fires=100,
        )
        engine = HazardEngine([event])
        agent = _agent()
        fire_count = 0
        for tick in range(100):
            fired = engine.evaluate_tick(tick, agent, random.Random(tick))
            fire_count += len(fired)
        assert fire_count > 30  # 높은 hazard이므로 자주 발동

    def test_deadline_forces_fire(self):
        """deadline 도달 시 강제 발동."""
        event = HazardEvent(
            event_id="forced",
            hazard=HazardFunction(base_rate=0.0),  # 자발 발동 불가
            deadline_tick=50,
        )
        engine = HazardEngine([event])
        agent = _agent()
        fired = engine.evaluate_tick(50, agent, random.Random(42))
        assert len(fired) == 1
        assert fired[0].event_id == "forced"

    def test_seed_reproducibility(self):
        """동일 시드 -> 동일 발동 패턴."""
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.3),
            max_fires=10,
        )
        agent = _agent()

        def run_pattern(seed_base):
            e = event.model_copy(deep=True)
            eng = HazardEngine([e])
            pattern = []
            for t in range(50):
                fired = eng.evaluate_tick(t, agent, random.Random(seed_base + t))
                pattern.append(len(fired))
            return pattern

        p1 = run_pattern(1000)
        p2 = run_pattern(1000)
        assert p1 == p2

    def test_reset(self):
        event = HazardEvent(
            event_id="test",
            hazard=HazardFunction(base_rate=0.5),
            max_fires=1,
        )
        engine = HazardEngine([event])
        engine.evaluate_tick(10, _agent(), random.Random(42))
        engine.reset()
        assert event.fire_count == 0

    def test_event_tick_varies_across_seeds(self):
        """다른 시드 -> 이벤트 발생 tick이 다르다. 이게 hazard의 핵심."""
        event = HazardEvent(
            event_id="variable",
            hazard=HazardFunction(base_rate=0.05),
            anchor_window=(10, 100),
            max_fires=1,
        )
        agent = _agent(emotions=EmotionalState(fear=7.0))
        fire_ticks = []
        for seed in range(100):
            e = event.model_copy(deep=True)
            eng = HazardEngine([e])
            for t in range(10, 101):
                fired = eng.evaluate_tick(t, agent, random.Random(seed * 1000 + t))
                if fired:
                    fire_ticks.append(t)
                    break
        # 발생 tick이 분산되어야 함
        if fire_ticks:
            assert max(fire_ticks) - min(fire_ticks) > 5, f"tick 분산 부족: {fire_ticks[:10]}"
