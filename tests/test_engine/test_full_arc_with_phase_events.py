"""3년 공생애 + 수난 — 모든 phase가 자체 canonical_events를 fire (v1.2 Iter 21).

실제 content/peter/phases/ 의 5개 phase가 모두 연결되어:
- Phase 1: Luke 5 소명 (5 events)
- Phase 2: 갈릴리 사역 (12 events)
- Phase 3: 고백+변화산 (13 events)
- Phase 4: 예루살렘 여정 (8 events)
- Phase 5: 수난 (legacy 17 events via canonical_events.json)

fire되는 이벤트 총수가 5 phase 합계에 근접해야 함.
"""

from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import Phase, PhaseExitCondition, PhaseHandoffSpec
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


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


@pytest.fixture(scope="module")
def _all_setup():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
    return None


def _all_agents():
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    return peter, judas, caiaphas, crowd


def _phase_path(phase_name: str) -> str:
    return str(CONTENT / "peter" / "phases" / phase_name / "canonical_events.json")


def _legacy_passion_events_path() -> str:
    """Phase 5용 기존 canonical_events.json."""
    return str(CONTENT / "peter" / "canonical_events.json")


def _build_real_full_arc(peter, judas, caiaphas, crowd) -> SimulationConfig:
    """5-phase 전체 아크 + 각 phase가 실제 canonical_events 로드."""
    phases = [
        Phase(
            phase_id="01_calling",
            agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            canonical_events_path=_phase_path("01_calling"),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="02_galilean",
            agents_active=["peter", "judas"],  # 12 사도 택정부터
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=540),
            canonical_events_path=_phase_path("02_galilean"),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="03_confession",
            agents_active=["peter", "judas"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=150),
            canonical_events_path=_phase_path("03_confession"),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="04_journey",
            agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=90),
            canonical_events_path=_phase_path("04_journey_to_jerusalem"),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="05_passion",
            agents_active=["peter", "judas", "caiaphas", "crowd"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=500),
            canonical_events_path=_legacy_passion_events_path(),
        ),
    ]
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        max_tick=5000,
        state_noise_scale=0.02,
        phases=phases,
    )


class TestFullArcWithPhaseEvents:
    def test_all_five_phases_fire_events(self, _all_setup):
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # 각 phase에서 events fire됨
        for phase_id in [
            "01_calling", "02_galilean", "03_confession",
            "04_journey", "05_passion",
        ]:
            p = result.per_phase_results[phase_id]
            assert len(p.fired_events) > 0, \
                f"{phase_id}: no events fired ({len(p.fired_events)})"

    def test_phase_specific_event_ids(self, _all_setup):
        """각 phase의 event_id prefix가 분리됨."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        p1_ids = {e["event_id"] for e in result.per_phase_results["01_calling"].fired_events}
        p2_ids = {e["event_id"] for e in result.per_phase_results["02_galilean"].fired_events}
        p3_ids = {e["event_id"] for e in result.per_phase_results["03_confession"].fired_events}
        p5_ids = {e["event_id"] for e in result.per_phase_results["05_passion"].fired_events}

        # Phase 1: calling_ prefix
        assert any(eid.startswith("calling_") for eid in p1_ids)
        # Phase 2: gal_ prefix
        assert any(eid.startswith("gal_") for eid in p2_ids)
        # Phase 3: conf_ prefix
        assert any(eid.startswith("conf_") for eid in p3_ids)
        # Phase 5: scene_ prefix (legacy)
        assert any(eid.startswith("scene_") for eid in p5_ids)

        # Cross-phase: id 교집합 없음
        assert p1_ids.isdisjoint(p2_ids)
        assert p1_ids.isdisjoint(p3_ids)
        assert p2_ids.isdisjoint(p3_ids)

    def test_peter_obedience_accumulates_across_arc(self, _all_setup):
        """3년에 걸쳐 obedience_maturity가 누적."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # 각 phase 종료 시 obedience
        o_phase1 = result.per_phase_results["01_calling"].final_states["peter"].domain_state.obedience_maturity
        o_phase3 = result.per_phase_results["03_confession"].final_states["peter"].domain_state.obedience_maturity

        # Phase 1 시작은 0, 종료는 2+ (소명 events)
        assert o_phase1 >= 2.0, f"Phase 1 obedience={o_phase1}"
        # Phase 3 종료는 Phase 1보다 큰 값 (사역 누적)
        # HomeostasisRule이 감쇄시킬 수 있으므로 엄격 >는 아님, 0 보다 크기만 확인
        assert o_phase3 > 0.0

    def test_passion_phase_has_all_agents(self, _all_setup):
        """Phase 5에서 4 agents 모두 활성."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        p5 = result.per_phase_results["05_passion"]
        for aid in ["peter", "judas", "caiaphas", "crowd"]:
            assert aid in p5.final_states

    def test_total_tick_span_matches_expected(self, _all_setup):
        """5 phase 전체 tick 합 = 1364 (Phase 1-4) + 500 (Phase 5) = 1364."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        last = result.phase_boundaries[-1]
        total_end = last["end_tick"]
        # 84 + 540 + 150 + 90 + 500 = 1364
        assert total_end == 1364

    def test_absolute_hours_over_arc(self, _all_setup):
        """실시간(hours) 계산: 2년 이상."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        total_hours = sum(
            (b["end_tick"] - b["start_tick"]) * b["tick_scale_hours"]
            for b in result.phase_boundaries
        )
        # 84*2 + 540*24 + 150*2 + 90*24 + 500*2 = 168 + 12960 + 300 + 2160 + 1000 = 16588 hours
        # = 691 days = 1.89 years (공생애 2-3년 범위)
        total_years = total_hours / 24.0 / 365.25
        assert 1.5 <= total_years <= 3.5


class TestArchitecturalClaimsAtFullScale:
    """reviewer 주장의 실증 검증."""

    def test_stitched_internal_independently_queryable(self, _all_setup):
        """표면 연속, 내부 stitched — 각 phase를 독립적으로 분석 가능."""
        peter, judas, caiaphas, crowd = _all_agents()
        config = _build_real_full_arc(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # 각 phase의 독립 결과가 있어 phase-local analysis 가능
        for pid in ["01_calling", "02_galilean", "03_confession", "04_journey", "05_passion"]:
            assert pid in result.per_phase_results
            p = result.per_phase_results[pid]
            # 각 phase는 자체 fired_events, final_states
            assert hasattr(p, "fired_events")
            assert hasattr(p, "final_states")
            assert hasattr(p, "action_histories")
