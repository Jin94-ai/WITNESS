"""jesus_understanding canonical discrete transitions (v1.2 Iter 51).

Reviewer (GPT+Gemini) 합의: Peter의 신앙 이해 전환은 자연 창발이 아니라
canonical event effects로 명시되어야 함. 이전까지 Phase 1-4 실행 결과
final state에서 jesus_understanding=None 유지되는 문제 해결.

추가된 transition:
- Phase 1 calling_05_call_and_follow: None → "teacher"
- Phase 3 conf_03_peters_confession: → "messiah_political"

이 테스트는 content JSON의 effects가 실제 state를 전환시킴을 lock in.
"""

from pathlib import Path

import pytest

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
from engine.simulation.phased_world import PhasedSimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _handoff_with_understanding() -> PhaseHandoffSpec:
    """Handoff이 jesus_understanding도 carry해야 Phase 2에서 teacher 유지."""
    return PhaseHandoffSpec(
        mappings=[
            FieldMapping("peter", "domain_state.jesus_understanding",
                         "peter", "domain_state.jesus_understanding"),
            FieldMapping("peter", "domain_state.obedience_maturity",
                         "peter", "domain_state.obedience_maturity"),
        ],
    )


def _phase_1_only_config():
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    return SimulationConfig(
        initial_state=peter, initial_states=[peter],
        max_tick=200, state_noise_scale=0.0,
        phases=[Phase(
            phase_id="01_calling", agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
            ),
        )],
    )


def _phase_1_to_3_config():
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    return SimulationConfig(
        initial_state=peter, initial_states=[peter, judas],
        max_tick=1000, state_noise_scale=0.0,
        phases=[
            Phase(
                phase_id="01", agents_active=["peter"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=84),
                canonical_events_path=str(
                    CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
                ),
                handoff_to_next=_handoff_with_understanding(),
            ),
            Phase(
                phase_id="02", agents_active=["peter", "judas"],
                tick_scale_hours=24.0,
                exit_condition=PhaseExitCondition(max_tick=60),
                canonical_events_path=str(
                    CONTENT / "peter" / "phases" / "02_galilean" / "canonical_events.json",
                ),
                handoff_to_next=_handoff_with_understanding(),
            ),
            Phase(
                phase_id="03", agents_active=["peter", "judas"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=50),
                canonical_events_path=str(
                    CONTENT / "peter" / "phases" / "03_confession" / "canonical_events.json",
                ),
            ),
        ],
    )


class TestPhase1CallingTransition:
    def test_initial_state_is_none(self, _setup):
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        assert peter.domain_state.jesus_understanding is None

    def test_phase1_end_is_teacher(self, _setup):
        """Phase 1 종료 시 calling_05 event가 None → teacher 전이."""
        config = _phase_1_only_config()
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        final = result.final_states["peter"]
        assert final.domain_state.jesus_understanding == "teacher"

    def test_phase1_transition_is_deterministic(self, _setup):
        """noise=0에서 여러 seed 전부 teacher로 전환."""
        config = _phase_1_only_config()
        for seed in [0, 1, 7, 42]:
            r = PhasedSimulationWorld(config, _rules()).run(seed=seed)
            assert r.final_states["peter"].domain_state.jesus_understanding == "teacher"


class TestPhase3ConfessionTransition:
    def test_phase3_end_is_messiah_political(self, _setup):
        """Phase 1→2→3 linked. Phase 3에서 conf_03 event로 teacher → messiah_political."""
        config = _phase_1_to_3_config()
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        final = result.final_states["peter"]
        assert final.domain_state.jesus_understanding == "messiah_political"

    def test_transition_progression_phase_by_phase(self, _setup):
        """각 phase 끝에서 understanding이 canonical sequence를 따름."""
        config = _phase_1_to_3_config()
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)

        p1 = result.per_phase_results["01"].final_states["peter"]
        p2 = result.per_phase_results["02"].final_states["peter"]
        p3 = result.per_phase_results["03"].final_states["peter"]

        assert p1.domain_state.jesus_understanding == "teacher"
        # Phase 2는 galilean 사역으로 teacher 유지 (canonical event effect 없음)
        assert p2.domain_state.jesus_understanding == "teacher"
        assert p3.domain_state.jesus_understanding == "messiah_political"


class TestLegacyPhase5Transitions:
    """v0.7 legacy 500-tick scenario에서 resurrection/ascension 전환 확인.

    content/peter/canonical_events.json tick 237 (엠마오-예루살렘) → risen_lord.
    tick 495 (승천) → sending_lord.
    """

    def test_full_legacy_run_reaches_sending_lord(self, _setup):
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        from engine.io.loader import load_events
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter],
            max_tick=500,
            state_noise_scale=0.0,
            events=events,
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        # 승천(tick 495) 후 sending_lord
        assert result.final_states["peter"].domain_state.jesus_understanding == "sending_lord"

    def test_post_resurrection_before_ascension_is_risen_lord(self, _setup):
        """tick 300에서 snapshot: 엠마오(237) 후, 승천(495) 전 → risen_lord."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        from engine.io.loader import load_events
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter],
            max_tick=300,
            state_noise_scale=0.0,
            events=events,
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        assert result.final_states["peter"].domain_state.jesus_understanding == "risen_lord"

    def test_pre_arrest_still_messiah_political(self, _setup):
        """tick 100 (체포 전): 초기 messiah_political 유지 (Phase 5 전환 아직)."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        from engine.io.loader import load_events
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter],
            max_tick=100,
            state_noise_scale=0.0,
            events=events,
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        assert result.final_states["peter"].domain_state.jesus_understanding == "messiah_political"


class TestHandoffCarriesUnderstanding:
    def test_handoff_none_is_passthrough(self, _setup):
        """handoff_to_next=None 이어도 state는 next phase로 pass-through.

        (handoff spec은 **선택적 override용**. None은 reset이 아니다.)
        """
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter, judas],
            max_tick=1000, state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="01", agents_active=["peter"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    canonical_events_path=str(
                        CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
                    ),
                    # handoff 없음
                ),
                Phase(
                    phase_id="02", agents_active=["peter", "judas"],
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=5),
                ),
            ],
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        p2_final = result.per_phase_results["02"].final_states["peter"]
        # Phase 1의 teacher가 Phase 2로 pass-through
        assert p2_final.domain_state.jesus_understanding == "teacher"
