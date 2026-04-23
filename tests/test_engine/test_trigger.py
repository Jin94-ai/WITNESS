"""트리거 시스템 테스트."""

from engine.core.state import AgentState, EmotionalState
from engine.core.trigger import (
    ActionTriggerCondition,
    Trigger,
    TriggerCondition,
    TriggerEngine,
)


def _agent(agent_id: str, fear: float = 5.0, hope: float = 5.0) -> AgentState:
    return AgentState(
        agent_id=agent_id,
        emotions=EmotionalState(fear=fear, hope=hope),
    )


class TestTriggerCondition:
    def test_gt(self):
        agents = {"judas": _agent("judas", fear=8.0)}
        cond = TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gt", value=7.0)
        assert cond.evaluate(agents) is True

    def test_lte(self):
        agents = {"judas": _agent("judas", fear=5.0)}
        cond = TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="lte", value=5.0)
        assert cond.evaluate(agents) is True

    def test_missing_agent(self):
        cond = TriggerCondition(agent_id="unknown", field_path="emotions.fear", operator="gt", value=0.0)
        assert cond.evaluate({}) is False

    def test_missing_field(self):
        agents = {"a": _agent("a")}
        cond = TriggerCondition(agent_id="a", field_path="nonexistent.field", operator="gt", value=0.0)
        assert cond.evaluate(agents) is False


class TestActionTriggerCondition:
    def test_action_present(self):
        cond = ActionTriggerCondition(agent_id="judas", action_id="betray")
        recent = {"judas": ["betray", "withdraw"]}
        assert cond.evaluate(recent) is True

    def test_action_absent(self):
        cond = ActionTriggerCondition(agent_id="judas", action_id="betray")
        recent = {"judas": ["withdraw"]}
        assert cond.evaluate(recent) is False

    def test_no_actions_for_agent(self):
        cond = ActionTriggerCondition(agent_id="judas", action_id="betray")
        assert cond.evaluate({}) is False


class TestTrigger:
    def test_all_conditions_met(self):
        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gte", value=8.0),
            ],
            action_conditions=[
                ActionTriggerCondition(agent_id="judas", action_id="betray"),
            ],
            event_template_id="arrest_event",
        )
        agents = {"judas": _agent("judas", fear=9.0)}
        actions = {"judas": ["betray"]}
        assert trigger.evaluate(10, agents, actions) is True

    def test_state_condition_not_met(self):
        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gte", value=8.0),
            ],
            event_template_id="arrest_event",
        )
        agents = {"judas": _agent("judas", fear=3.0)}
        assert trigger.evaluate(10, agents, {}) is False

    def test_cooldown(self):
        trigger = Trigger(
            trigger_id="test", cooldown=5, max_fires=3, event_template_id="e",
            fire_count=1, last_fired_tick=8,
        )
        assert trigger.is_eligible(10) is False  # 10 - 8 = 2 < 5
        assert trigger.is_eligible(13) is True   # 13 - 8 = 5 >= 5

    def test_max_fires(self):
        trigger = Trigger(
            trigger_id="test", max_fires=2, fire_count=2, event_template_id="e",
        )
        assert trigger.is_eligible(100) is False

    def test_deadline(self):
        trigger = Trigger(
            trigger_id="test", deadline_tick=100, event_template_id="e",
        )
        assert trigger.is_deadline(99) is False
        assert trigger.is_deadline(100) is True

    def test_deadline_not_after_fire(self):
        trigger = Trigger(
            trigger_id="test", deadline_tick=100, fire_count=1, max_fires=1,
            event_template_id="e",
        )
        assert trigger.is_deadline(100) is False

    def test_record_fire(self):
        trigger = Trigger(trigger_id="test", event_template_id="e")
        trigger.record_fire(50)
        assert trigger.fire_count == 1
        assert trigger.last_fired_tick == 50


class TestTriggerEngine:
    def test_condition_trigger(self):
        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gte", value=8.0),
            ],
            event_template_id="arrest_event",
        )
        engine = TriggerEngine([trigger])
        agents = {"judas": _agent("judas", fear=9.0)}
        fired = engine.evaluate_tick(10, agents)
        assert len(fired) == 1
        assert fired[0].trigger_id == "arrest"

    def test_no_trigger(self):
        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gte", value=8.0),
            ],
            event_template_id="arrest_event",
        )
        engine = TriggerEngine([trigger])
        agents = {"judas": _agent("judas", fear=3.0)}
        fired = engine.evaluate_tick(10, agents)
        assert len(fired) == 0

    def test_deadline_forced(self):
        trigger = Trigger(
            trigger_id="arrest", deadline_tick=100,
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="emotions.fear", operator="gte", value=99.0),
            ],
            event_template_id="arrest_event",
        )
        engine = TriggerEngine([trigger])
        agents = {"judas": _agent("judas", fear=1.0)}  # 조건 미충족
        fired = engine.evaluate_tick(100, agents)
        assert len(fired) == 1  # deadline 강제 발동

    def test_reset(self):
        trigger = Trigger(trigger_id="t", event_template_id="e", fire_count=3, last_fired_tick=50)
        engine = TriggerEngine([trigger])
        engine.reset()
        assert engine.triggers[0].fire_count == 0
        assert engine.triggers[0].last_fired_tick == -1
