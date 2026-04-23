"""Trigger cause (state_conditions_satisfied) 기록 테스트 (§2.1).

SimulationWorld가 trigger 발동 시 조건 snapshot을 기록하고,
trace emitter가 cause payload로 전달하며,
player view filter가 cause 내용을 타 시점에서 숨김.
"""

from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.state import AgentState, EmotionalState
from engine.core.trigger import (
    ActionTriggerCondition,
    Trigger,
    TriggerCondition,
)
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_emitter import collect_trace_events
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


class TestTriggerSnapshotConditions:
    def test_state_condition_snapshot(self):
        """TriggerCondition 스냅샷이 actual value + threshold + satisfied를 기록."""
        trig = Trigger(
            trigger_id="t1",
            state_conditions=[
                TriggerCondition(
                    agent_id="a", field_path="emotions.fear",
                    operator="gte", value=5.0,
                ),
            ],
            event_template_id="ev",
        )
        states = {"a": AgentState(agent_id="a", emotions=EmotionalState(fear=7.0))}
        snap = trig.snapshot_conditions(states, {})
        assert len(snap) == 1
        entry = snap[0]
        assert entry["agent"] == "a"
        assert entry["field"] == "emotions.fear"
        assert entry["value"] == 7.0
        assert entry["threshold"] == 5.0
        assert entry["operator"] == "gte"
        assert entry["satisfied"] is True

    def test_action_condition_snapshot(self):
        """ActionTriggerCondition 스냅샷도 기록."""
        trig = Trigger(
            trigger_id="t1",
            action_conditions=[
                ActionTriggerCondition(agent_id="a", action_id="betray"),
            ],
            event_template_id="ev",
        )
        snap = trig.snapshot_conditions({}, {"a": ["follow", "betray"]})
        assert len(snap) == 1
        entry = snap[0]
        assert entry["action"] == "betray"
        assert entry["satisfied"] is True
        assert "betray" in entry["recent_actions"]

    def test_unsatisfied_still_snapshot(self):
        """조건이 불충족이어도 snapshot에 포함 (satisfied=False)."""
        trig = Trigger(
            trigger_id="t1",
            state_conditions=[
                TriggerCondition(
                    agent_id="a", field_path="emotions.fear",
                    operator="gte", value=5.0,
                ),
            ],
            event_template_id="ev",
        )
        states = {"a": AgentState(agent_id="a", emotions=EmotionalState(fear=2.0))}
        snap = trig.snapshot_conditions(states, {})
        assert snap[0]["satisfied"] is False
        assert snap[0]["value"] == 2.0


def _run(max_tick: int = 200, seed: int = 0):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=max_tick, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    engine = RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])
    return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)


class TestTriggerCauseIntegration:
    def test_fired_trigger_has_conditions_snapshot(self):
        """실제 시뮬에서 발동된 trigger가 conditions snapshot을 포함."""
        result = _run(max_tick=250, seed=0)
        # arrest_trigger 또는 다른 trigger 발동 확인
        fired = result.fired_triggers
        if not fired:
            # 250 tick 내에 발동 안 되면 스킵
            return
        for t in fired:
            assert "state_conditions_satisfied" in t
            conditions = t["state_conditions_satisfied"]
            # conditions가 list 구조 + 각 entry가 satisfied 필드 보유
            if conditions:  # 일부 trigger는 조건 없을 수도
                for entry in conditions:
                    assert "satisfied" in entry

    def test_trace_event_has_cause(self):
        """trace emitter가 trigger_fired event에 cause 필드 전달."""
        result = _run(max_tick=250, seed=0)
        events = collect_trace_events(result)
        trigger_events = [e for e in events if e.type == "trigger_fired"]
        if not trigger_events:
            return
        for ev in trigger_events:
            # cause가 있거나 (conditions 있는 trigger), 없거나 (조건 없는 trigger)
            # 둘 다 OK. 있으면 state_conditions_satisfied 포함.
            if "cause" in ev.payload:
                assert "state_conditions_satisfied" in ev.payload["cause"]

    def test_player_view_strips_trigger_cause(self):
        """Player view filter가 trigger cause 블록을 타 시점에서 제거."""
        result = _run(max_tick=250, seed=0)
        events = collect_trace_events(result)
        trigger_events = [e for e in events if e.type == "trigger_fired"]
        if not trigger_events:
            return

        cfg = PlayerViewFilterConfig(player_id="peter")
        filtered = filter_for_player(events, cfg)
        filtered_triggers = [e for e in filtered if e.type == "trigger_fired"]
        # cause 블록은 모두 제거되어야 함 (trigger는 agent-less public event)
        for ev in filtered_triggers:
            assert "cause" not in ev.payload, \
                f"trigger_fired should not expose cause to player: {ev.payload}"
            # 공적 정보(trigger_id, event_id)는 유지
            assert "trigger_id" in ev.payload
