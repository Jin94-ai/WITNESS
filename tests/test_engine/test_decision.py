"""행동 결정 + 이벤트 스케줄러 테스트."""

import random

from engine.core.event import (
    ActionOption,
    CanonicalIntervention,
    ExternalEvent,
    Precondition,
    WeightFormula,
)
from engine.core.state import AgentState, EmotionalState, PhysicalState
from engine.simulation.decision import decide_action
from engine.simulation.event_scheduler import EventScheduler


def _agent(**kwargs) -> AgentState:
    defaults = {"agent_id": "test", "emotions": EmotionalState(fear=5.0)}
    defaults.update(kwargs)
    return AgentState(**defaults)


class TestDecideAction:
    def test_basic_selection(self):
        agent = _agent()
        options = [
            ActionOption(action_id="a", weight_formula=WeightFormula(base_weight=0.9)),
            ActionOption(action_id="b", weight_formula=WeightFormula(base_weight=0.1)),
        ]
        rng = random.Random(42)
        result = decide_action(agent, options, rng)
        assert result is not None
        assert result.action_id in ("a", "b")

    def test_seed_reproducibility(self):
        """동일 시드 -> 동일 결과."""
        agent = _agent()
        options = [
            ActionOption(action_id="a", weight_formula=WeightFormula(base_weight=0.5)),
            ActionOption(action_id="b", weight_formula=WeightFormula(base_weight=0.5)),
        ]
        results = []
        for _ in range(5):
            rng = random.Random(42)
            r = decide_action(agent, options, rng)
            results.append(r.action_id if r else None)
        assert len(set(results)) == 1  # 모두 동일

    def test_empty_options(self):
        agent = _agent()
        assert decide_action(agent, [], random.Random(42)) is None

    def test_all_options_filtered_by_preconditions(self):
        """모든 option이 precondition에 실패 → None."""
        agent = _agent(emotions=EmotionalState(fear=2.0))
        options = [
            ActionOption(
                action_id="a",
                preconditions=[Precondition(field_path="emotions.fear", operator="gt", value=5.0)],
                weight_formula=WeightFormula(base_weight=1.0),
            ),
            ActionOption(
                action_id="b",
                preconditions=[Precondition(field_path="emotions.fear", operator="gt", value=8.0)],
                weight_formula=WeightFormula(base_weight=1.0),
            ),
        ]
        assert decide_action(agent, options, random.Random(42)) is None

    def test_precondition_filtering(self):
        agent = _agent(emotions=EmotionalState(fear=3.0))
        options = [
            ActionOption(
                action_id="needs_high_fear",
                preconditions=[Precondition(field_path="emotions.fear", operator="gt", value=7.0)],
                weight_formula=WeightFormula(base_weight=1.0),
            ),
            ActionOption(
                action_id="always_available",
                weight_formula=WeightFormula(base_weight=0.5),
            ),
        ]
        result = decide_action(agent, options, random.Random(42))
        assert result is not None
        assert result.action_id == "always_available"

    def test_high_fear_biases_deny(self):
        """공포가 높으면 부인 확률이 높아진다."""
        agent = _agent(
            emotions=EmotionalState(fear=9.0),
            physical=PhysicalState(fatigue=9.0),
        )
        deny = ActionOption(
            action_id="deny",
            weight_formula=WeightFormula(
                base_weight=0.3,
                state_multipliers=[
                    {"field_path": "emotions.fear", "factor_type": "linear", "params": {"scale": 0.1}},
                    {"field_path": "physical.fatigue", "factor_type": "linear", "params": {"scale": 0.05}},
                ],
            ),
        )
        confess = ActionOption(
            action_id="confess",
            weight_formula=WeightFormula(
                base_weight=0.5,
                state_multipliers=[
                    {"field_path": "emotions.fear", "factor_type": "inverse", "params": {"scale": 0.1}},
                ],
            ),
        )
        # 100회 실행해서 deny가 더 많이 나오는지 확인
        deny_count = 0
        for i in range(100):
            result = decide_action(agent, [deny, confess], random.Random(i))
            if result and result.action_id == "deny":
                deny_count += 1
        assert deny_count > 50  # 공포가 높으면 부인이 더 많아야 함


class TestEventScheduler:
    def test_events_by_tick(self):
        events = [
            ExternalEvent(event_id="a", tick=5),
            ExternalEvent(event_id="b", tick=5),
            ExternalEvent(event_id="c", tick=10),
        ]
        scheduler = EventScheduler(events)
        assert len(scheduler.get_events_for_tick(5)) == 2
        assert len(scheduler.get_events_for_tick(6)) == 0
        assert len(scheduler.get_events_for_tick(10)) == 1

    def test_interventions(self):
        interventions = [
            CanonicalIntervention(
                event_id="restore", tick=358, scripture_ref="요 21:15",
                state_overrides={"emotions.grief": 3.0},
            ),
        ]
        scheduler = EventScheduler([], interventions)
        assert len(scheduler.get_interventions_for_tick(358)) == 1
        assert len(scheduler.get_interventions_for_tick(359)) == 0

    def test_has_remaining(self):
        events = [ExternalEvent(event_id="a", tick=5)]
        scheduler = EventScheduler(events)
        assert scheduler.has_remaining()
        scheduler.get_events_for_tick(5)
        assert not scheduler.has_remaining()

    def test_reset(self):
        events = [ExternalEvent(event_id="a", tick=5)]
        scheduler = EventScheduler(events)
        scheduler.get_events_for_tick(5)
        scheduler.reset()
        assert scheduler.has_remaining()
        assert len(scheduler.get_events_for_tick(5)) == 1
