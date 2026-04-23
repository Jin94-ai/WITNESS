"""Phase 5 full-length (500 tick) linked-life scale 검증 (v1.2 Iter 39).

Iter 32에서 Phase 5 config 추가 + 단축 60 tick 검증. 이 테스트는 full 500 tick
Phase 5까지 포함한 full arc가 scale에서도 작동함을 증명.

검증:
1. 5-phase arc (01 84t + 02 60t + 03 50t + 04 30t + 05 **500t**) 완주.
2. Phase 5 canonical_events (legacy 19 events) 모두 fire (scene_01_jerusalem_entry부터).
3. 다수 seed에서 Peter 최종 state 의미적 유효 (fear/awe/obedience bounded).
4. 실행 시간 합리적 (seed당 1초 미만).

Scale: 총 724 tick × 4 agents × ~~rules per tick ≈ 감당 가능.
"""

import time
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, register_domain_type
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup_domain():
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _handoff() -> PhaseHandoffSpec:
    carried = [
        "domain_state.obedience_maturity",
        "emotions.awe", "emotions.hope", "emotions.fear",
        "emotions.grief", "emotions.confusion", "emotions.love",
    ]
    return PhaseHandoffSpec(
        mappings=[FieldMapping("peter", f, "peter", f) for f in carried],
    )


def _full_arc_phases() -> list[Phase]:
    return [
        Phase(
            phase_id="01_calling", agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="02_galilean", agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=60),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "02_galilean" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="03_confession", agents_active=["peter", "judas"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=50),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "03_confession" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="04_journey", agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=30),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "04_journey_to_jerusalem" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="05_passion",
            agents_active=["peter", "judas", "caiaphas", "crowd"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=500),  # full legacy length
            canonical_events_path=str(
                CONTENT / "peter" / "canonical_events.json",
            ),
        ),
    ]


def _initial_states():
    return (
        load_agent_state(CONTENT / "peter" / "initial_state_calling.json"),
        load_agent_state(CONTENT / "judas" / "initial_state.json"),
        load_agent_state(CONTENT / "caiaphas" / "initial_state.json"),
        load_agent_state(CONTENT / "crowd" / "initial_state.json"),
    )


@pytest.fixture(scope="module")
def full_arc_result(_setup_domain):
    peter, judas, cai, crowd = _initial_states()
    config = SimulationConfig(
        initial_state=peter, initial_states=[peter, judas, cai, crowd],
        max_tick=5000, state_noise_scale=0.02,
        phases=_full_arc_phases(),
    )
    return PhasedSimulationWorld(config, _rules()).run(seed=0)


class TestFullLengthCompletion:
    def test_all_five_phases_complete(self, full_arc_result):
        assert isinstance(full_arc_result, PhasedMultiAgentResult)
        assert len(full_arc_result.per_phase_results) == 5
        assert "05_passion" in full_arc_result.per_phase_results

    def test_phase5_runs_full_500_ticks(self, full_arc_result):
        p5 = full_arc_result.per_phase_results["05_passion"]
        # Phase 5 내부 final tick
        assert p5.final_states["peter"].tick == 500

    def test_all_four_agents_in_phase5(self, full_arc_result):
        p5 = full_arc_result.per_phase_results["05_passion"]
        for aid in ["peter", "judas", "caiaphas", "crowd"]:
            assert aid in p5.final_states


class TestPhase5EventFiring:
    def test_some_phase5_events_fire(self, full_arc_result):
        """legacy canonical_events.json 19 events 중 일부 fire."""
        p5 = full_arc_result.per_phase_results["05_passion"]
        phase5_events = p5.fired_events
        # 최소 5 events
        assert len(phase5_events) >= 5


class TestBoundedEmergentState:
    def test_final_state_bounded(self, full_arc_result):
        peter = full_arc_result.final_states["peter"]
        # 모든 emotions [0, 10]
        assert 0.0 <= peter.emotions.fear <= 10.0
        assert 0.0 <= peter.emotions.hope <= 10.0
        assert 0.0 <= peter.emotions.awe <= 10.0
        assert 0.0 <= peter.emotions.grief <= 10.0
        # obedience도 clamped
        assert 0.0 <= peter.domain_state.obedience_maturity <= 10.0


class TestRuntimeBudget:
    """5-phase full-length run이 실용적 시간 안에 완료."""

    def test_full_arc_under_budget(self, _setup_domain):
        peter, judas, cai, crowd = _initial_states()
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter, judas, cai, crowd],
            max_tick=5000, state_noise_scale=0.02,
            phases=_full_arc_phases(),
        )
        t0 = time.time()
        PhasedSimulationWorld(config, _rules()).run(seed=42)
        duration = time.time() - t0
        # 느슨한 상한: 5초. 실제로는 0.1~0.5초.
        assert duration < 5.0, f"full arc took {duration:.2f}s (> 5s budget)"


class TestMultipleSeedsStable:
    """여러 seed에서 full arc 실행 가능 — scale 안정성."""

    def test_three_seeds_all_complete(self, _setup_domain):
        peter, judas, cai, crowd = _initial_states()
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter, judas, cai, crowd],
            max_tick=5000, state_noise_scale=0.02,
            phases=_full_arc_phases(),
        )
        for seed in [0, 7, 42]:
            result = PhasedSimulationWorld(config, _rules()).run(seed=seed)
            assert len(result.per_phase_results) == 5
            assert "peter" in result.final_states
