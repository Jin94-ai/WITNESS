"""전체 5 phase 아크 E2E: Phase 1-4 (Peter only) + Phase 5 legacy 통합 (v1.2 Iter 18).

3년 공생애 + 42일 수난이 하나의 phase-linked simulation으로 실행되는지 검증.
Phase 5에서 Judas/Caiaphas/Crowd가 agent introduction으로 등장.
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
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


@pytest.fixture(scope="module")
def _setup():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
    return None


def _all_peter_scenario_agents():
    """Peter 시나리오 전체 agents — config.initial_states에 모두 포함."""
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    return peter, judas, caiaphas, crowd


def _build_5phase_config(peter, judas, caiaphas, crowd) -> SimulationConfig:
    """5-phase 전체 공생애+수난 아크 config."""
    phases = [
        Phase(
            phase_id="01_calling",
            agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=30),  # MVP 단축
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="02_galilean",
            agents_active=["peter", "judas"],  # Judas 등장!
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=20),  # MVP 단축
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="03_confession",
            agents_active=["peter", "judas"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=20),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="04_journey",
            agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=10),
            handoff_to_next=PhaseHandoffSpec(),
        ),
        Phase(
            phase_id="05_passion",
            agents_active=["peter", "judas", "caiaphas", "crowd"],  # 전원 등장
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=50),  # MVP 단축
        ),
    ]
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],  # 전체 풀
        max_tick=5000,
        state_noise_scale=0.02,
        phases=phases,
    )


class TestFullArcFivePhases:
    def test_all_five_phases_execute(self, _setup):
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        assert isinstance(result, PhasedMultiAgentResult)
        assert len(result.phase_boundaries) == 5
        expected_phases = [
            "01_calling", "02_galilean", "03_confession",
            "04_journey", "05_passion",
        ]
        for pid in expected_phases:
            assert pid in result.per_phase_results

    def test_judas_introduced_at_phase_2(self, _setup):
        """Judas가 Phase 2 갈릴리 사역 시작부터 등장."""
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # Phase 1: Peter만
        p1 = result.per_phase_results["01_calling"]
        assert "peter" in p1.final_states
        assert "judas" not in p1.final_states

        # Phase 2: Peter + Judas
        p2 = result.per_phase_results["02_galilean"]
        assert "peter" in p2.final_states
        assert "judas" in p2.final_states
        # Caiaphas / Crowd는 아직 아님
        assert "caiaphas" not in p2.final_states
        assert "crowd" not in p2.final_states

    def test_caiaphas_crowd_introduced_at_phase_5(self, _setup):
        """Caiaphas + Crowd는 Phase 5 수난에서 등장."""
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        p4 = result.per_phase_results["04_journey"]
        assert "caiaphas" not in p4.final_states
        assert "crowd" not in p4.final_states

        p5 = result.per_phase_results["05_passion"]
        assert "caiaphas" in p5.final_states
        assert "crowd" in p5.final_states
        assert "peter" in p5.final_states
        assert "judas" in p5.final_states

    def test_peter_state_continuity_through_5_phases(self, _setup):
        """Peter의 state가 5 phase 모두 통과하며 연속성 유지."""
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # 각 phase의 Peter final state
        peter_states = [
            result.per_phase_results[pid].final_states["peter"]
            for pid in ["01_calling", "02_galilean", "03_confession", "04_journey", "05_passion"]
        ]
        # 모든 phase에서 Peter 존재
        assert all(s is not None for s in peter_states)
        # 최종 상태의 감정이 유효 범위
        final = peter_states[-1]
        assert 0.0 <= final.emotions.fear <= 10.0
        assert 0.0 <= final.emotions.hope <= 10.0

    def test_phase_boundaries_cumulative_ticks(self, _setup):
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        boundaries = result.phase_boundaries
        assert boundaries[0]["start_tick"] == 0
        assert boundaries[0]["end_tick"] == 30  # calling 30
        assert boundaries[1]["start_tick"] == 30
        assert boundaries[1]["end_tick"] == 50  # + galilean 20
        assert boundaries[2]["start_tick"] == 50
        assert boundaries[2]["end_tick"] == 70  # + confession 20
        assert boundaries[3]["start_tick"] == 70
        assert boundaries[3]["end_tick"] == 80  # + journey 10
        assert boundaries[4]["start_tick"] == 80
        assert boundaries[4]["end_tick"] == 130  # + passion 50

    def test_tick_scale_per_phase(self, _setup):
        peter, judas, caiaphas, crowd = _all_peter_scenario_agents()
        config = _build_5phase_config(peter, judas, caiaphas, crowd)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        scales = [b["tick_scale_hours"] for b in result.phase_boundaries]
        assert scales == [2.0, 24.0, 2.0, 24.0, 2.0]  # dense/sparse/dense/sparse/dense


class TestLegacyV07Compat:
    """v0.7 수치 보존 검증."""

    def test_legacy_peter_scenario_unchanged(self, _setup):
        """기존 initial_state.json + phases=None 모드는 v0.7 동작 그대로."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        caiaphas = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")

        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter, judas, caiaphas, crowd],
            max_tick=100,
            state_noise_scale=0.05,
            # phases=None → v0.7 동작
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # PhasedMultiAgentResult 아님
        from engine.simulation.world import MultiAgentResult
        assert isinstance(result, MultiAgentResult)
        assert not isinstance(result, PhasedMultiAgentResult)

        # 4 agents 모두 활성 (v0.7 multi-agent scenario)
        assert "peter" in result.final_states
        assert "judas" in result.final_states
        assert "caiaphas" in result.final_states
        assert "crowd" in result.final_states

        # Peter jesus_understanding = messiah_political (legacy)
        assert result.final_states["peter"].domain_state.jesus_understanding == "messiah_political"
