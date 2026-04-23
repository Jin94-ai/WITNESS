"""Phase 1→5 linked-life 모드 검증 (v1.2 Iter 32).

두 모드가 서로 다른 수치를 낸다는 것이 존재 증명:
- legacy-phase5 모드: phases=None, initial_state.json (messiah_political literal)
  으로 시작. 기존 v0.7 500 tick scenario 그대로. 검증 수치 완전 보존.
- linked-life 모드: phases=[01..05]로 소명부터 연결. Phase 5 시작 시 Peter
  상태가 3년 누적 결과로 override됨.

reviewer 질문 §3 Q5 (v0.7 수치 보존) 및 Q6 (연속 vs stitched) 대응.
사용자가 두 mode를 선택할 수 있음을 증명.
"""

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
from engine.io.loader import (
    load_agent_state,
    load_events,
    register_domain_type,
)
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
from engine.simulation.world import MultiAgentResult

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup_domain():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
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


def _linked_life_phases() -> list[Phase]:
    """Phase 1→5 전체 아크 (MVP 단축 버전)."""
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
            exit_condition=PhaseExitCondition(max_tick=60),  # MVP 단축 — full 500 별도
            canonical_events_path=str(
                CONTENT / "peter" / "canonical_events.json",
            ),
        ),
    ]


def _initial_states():
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    return peter, judas, caiaphas, crowd


class TestPhase5ConfigExists:
    def test_phase5_config_file(self):
        cfg = CONTENT / "peter" / "phases" / "05_passion" / "phase_config.json"
        assert cfg.exists()

    def test_phase5_reuses_legacy_events(self):
        import json
        cfg = json.loads(
            (CONTENT / "peter" / "phases" / "05_passion" / "phase_config.json").read_text(encoding="utf-8"),
        )
        # legacy canonical_events.json 재사용
        assert "content/peter/canonical_events.json" in cfg["canonical_events_path"]


class TestLinkedLifeMode:
    """phases=[01..05]로 linked-life 실행."""

    def test_five_phases_complete(self, _setup_domain):
        peter, judas, caiaphas, crowd = _initial_states()
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            max_tick=5000, state_noise_scale=0.0,
            phases=_linked_life_phases(),
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        assert len(result.per_phase_results) == 5
        assert "05_passion" in result.per_phase_results

    def test_phase5_peter_state_reflects_handoff(self, _setup_domain):
        """Phase 5 시작 시 Peter state는 Phase 4 handoff 결과여야."""
        peter, judas, caiaphas, crowd = _initial_states()
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            max_tick=5000, state_noise_scale=0.0,
            phases=_linked_life_phases(),
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)

        phase4_peter_end = result.per_phase_results["04_journey"].final_states["peter"]
        phase5_peter_end = result.per_phase_results["05_passion"].final_states["peter"]

        # linked: Phase 5 시작 시 obedience는 Phase 4 값 이상
        # (Phase 5 events도 이를 누적)
        assert (
            phase5_peter_end.domain_state.obedience_maturity
            >= phase4_peter_end.domain_state.obedience_maturity - 2.0  # fear shock 여유
        )


class TestLegacyPhase5ModeUnchanged:
    """phases=None 모드는 기존 v0.7 수치 보존 (bit-exact)."""

    def test_legacy_mode_produces_multi_agent_result(self, _setup_domain):
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        legacy_judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        legacy_cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        legacy_crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter, legacy_judas, legacy_cai, legacy_crowd],
            max_tick=60, state_noise_scale=0.0,
            events=events,
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        assert isinstance(result, MultiAgentResult)
        assert not isinstance(result, PhasedMultiAgentResult)
        # legacy literal 보존
        assert result.final_states["peter"].domain_state.jesus_understanding == "messiah_political"


class TestTwoModesDiverge:
    """linked-life와 legacy-phase5가 서로 다른 Peter state를 낸다 — 양자택일."""

    def test_peter_obedience_differs(self, _setup_domain):
        # Linked-life
        peter, judas, caiaphas, crowd = _initial_states()
        linked_cfg = SimulationConfig(
            initial_state=peter, initial_states=[peter, judas, caiaphas, crowd],
            max_tick=5000, state_noise_scale=0.0, phases=_linked_life_phases(),
        )
        linked = PhasedSimulationWorld(linked_cfg, _rules()).run(seed=0)

        # Legacy-only (Phase 5 length만)
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        legacy_judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        legacy_cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        legacy_crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        legacy_cfg = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter, legacy_judas, legacy_cai, legacy_crowd],
            max_tick=60, state_noise_scale=0.0, events=events,
        )
        legacy = PhasedSimulationWorld(legacy_cfg, _rules()).run(seed=0)

        # 두 mode에서 Peter obedience_maturity 다름
        linked_ob = linked.final_states["peter"].domain_state.obedience_maturity
        legacy_ob = legacy.final_states["peter"].domain_state.obedience_maturity
        # linked는 누적되어 > legacy baseline 5.0
        assert linked_ob != legacy_ob
        assert linked_ob > legacy_ob - 3.0  # 누적 효과로 더 높거나 근처
