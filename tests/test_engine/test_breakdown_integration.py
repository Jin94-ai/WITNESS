"""Action weight breakdown이 실제 SimulationWorld 출력에 기록되는지 통합 테스트.

TRACE_SCHEMA §2.2 필드가 end-to-end로 populate됨을 증명.
"""

from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
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


def _run(max_tick: int = 30, seed: int = 0):
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
        triggers=triggers, state_noise_scale=0.01,
    )
    engine = RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])
    return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)


class TestBreakdownInActionRecord:
    def test_breakdown_populated(self):
        """SimulationWorld가 각 행동마다 weight_breakdown을 기록."""
        result = _run()
        # 적어도 하나의 agent에 voluntary action 있어야 함
        found_breakdown = False
        for _, recs in result.action_histories.items():
            for rec in recs:
                if rec.event_id != "voluntary":
                    continue
                if rec.weight_breakdown is None:
                    continue
                found_breakdown = True
                # breakdown은 base + final 최소 포함
                assert "base" in rec.weight_breakdown
                assert "final" in rec.weight_breakdown
                # final >= 0.001 (계약)
                assert rec.weight_breakdown["final"] >= 0.001
                break
            if found_breakdown:
                break
        assert found_breakdown, "No voluntary ActionRecord with breakdown found"


class TestBreakdownInTraceEvents:
    def test_weight_breakdown_in_emitted_event(self):
        """trace_emitter가 weight_breakdown을 payload에 포함."""
        result = _run()
        events = collect_trace_events(result)

        # weight_breakdown 있는 voluntary action 찾기
        found = False
        for ev in events:
            if ev.type != "action_taken":
                continue
            if ev.payload.get("event_id") != "voluntary":
                continue
            if "weight_breakdown" in ev.payload:
                assert "base" in ev.payload["weight_breakdown"]
                assert "final" in ev.payload["weight_breakdown"]
                found = True
                break
        assert found, "No action_taken event with weight_breakdown in trace"
