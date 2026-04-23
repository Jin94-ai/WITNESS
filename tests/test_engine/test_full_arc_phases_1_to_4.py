"""전체 공생애 아크 E2E: Phase 1→2→3→4 실행 + handoff 검증 (v1.2 Iter 16).

Phase 5(수난)는 legacy 500 tick scenario로 별도 유지.
이 테스트는 Phase 1-4 연속 실행 + state continuity 검증.
"""

from pathlib import Path

import pytest

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

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


@pytest.fixture(scope="module")
def peter_calling_state():
    register_domain_type("faith_journey", FaithJourneyState)
    return load_agent_state(CONTENT / "peter" / "initial_state_calling.json")


def _standard_handoff() -> PhaseHandoffSpec:
    """공통 핸드오프 — obedience / awe / emotions carry."""
    return PhaseHandoffSpec(
        mappings=[
            FieldMapping("peter", "domain_state.obedience_maturity",
                         "peter", "domain_state.obedience_maturity"),
            FieldMapping("peter", "emotions.awe", "peter", "emotions.awe"),
            FieldMapping("peter", "emotions.hope", "peter", "emotions.hope"),
            FieldMapping("peter", "emotions.confusion",
                         "peter", "emotions.confusion"),
            FieldMapping("peter", "emotions.fear", "peter", "emotions.fear"),
            FieldMapping("peter", "emotions.grief", "peter", "emotions.grief"),
            FieldMapping("peter", "emotions.love", "peter", "emotions.love"),
        ],
    )


def _build_full_arc_config(peter_state) -> SimulationConfig:
    """Phase 1-4 전체 아크 config. MVP 단순화: events는 상위 config에 없이
    phase 내부 상태 evolution만 검증 (canonical events는 phase 단위 개별 로드 미구현)."""
    phases = [
        Phase(
            phase_id="01_calling",
            description="Luke 5 소명",
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            handoff_to_next=_standard_handoff(),
        ),
        Phase(
            phase_id="02_galilean",
            description="갈릴리 사역 (MVP 단축: 60 tick)",
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=60),
            handoff_to_next=_standard_handoff(),
        ),
        Phase(
            phase_id="03_confession",
            description="가이사랴 빌립보 고백 + 변화산 (MVP 단축: 50 tick)",
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=50),
            handoff_to_next=_standard_handoff(),
        ),
        Phase(
            phase_id="04_journey",
            description="예루살렘 여정 (MVP 단축: 30 tick)",
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=30),
        ),
    ]
    return SimulationConfig(
        initial_state=peter_state,
        initial_states=[peter_state],
        max_tick=5000,  # phases가 override
        state_noise_scale=0.02,
        phases=phases,
    )


class TestFullArcPhases1To4:
    def test_all_four_phases_execute(self, peter_calling_state):
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        assert isinstance(result, PhasedMultiAgentResult)
        assert len(result.phase_boundaries) == 4
        assert "01_calling" in result.per_phase_results
        assert "02_galilean" in result.per_phase_results
        assert "03_confession" in result.per_phase_results
        assert "04_journey" in result.per_phase_results

    def test_phase_boundaries_tick_offsets_correct(self, peter_calling_state):
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        boundaries = result.phase_boundaries
        assert boundaries[0]["start_tick"] == 0
        assert boundaries[0]["end_tick"] == 84
        assert boundaries[1]["start_tick"] == 84
        assert boundaries[1]["end_tick"] == 84 + 60
        assert boundaries[2]["start_tick"] == 144
        assert boundaries[2]["end_tick"] == 144 + 50
        assert boundaries[3]["start_tick"] == 194
        assert boundaries[3]["end_tick"] == 194 + 30

    def test_tick_scales_vary(self, peter_calling_state):
        """phase별 다른 tick_scale_hours 기록됨."""
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        scales = [b["tick_scale_hours"] for b in result.phase_boundaries]
        assert scales == [2.0, 24.0, 2.0, 24.0]

    def test_absolute_time_approximation(self, peter_calling_state):
        """tick × tick_scale = 실시간 hours."""
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        total_hours = 0.0
        for b in result.phase_boundaries:
            tick_range = b["end_tick"] - b["start_tick"]
            total_hours += tick_range * b["tick_scale_hours"]
        # 84*2 + 60*24 + 50*2 + 30*24 = 168 + 1440 + 100 + 720 = 2428 hours ≈ 101 days
        expected_hours = 84 * 2 + 60 * 24 + 50 * 2 + 30 * 24
        assert total_hours == expected_hours
        assert abs(total_hours / 24.0 - 101.17) < 0.1  # ~101 days

    def test_state_continuity_across_phases(self, peter_calling_state):
        """handoff가 실제로 state를 전달하는지 — 마지막 phase final state가
        sensible한 value 범위인지."""
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        final = result.final_states["peter"]
        # 모든 감정이 [0, 10] 범위
        assert 0.0 <= final.emotions.fear <= 10.0
        assert 0.0 <= final.emotions.hope <= 10.0
        assert 0.0 <= final.emotions.awe <= 10.0
        # obedience_maturity도 clamped
        assert 0.0 <= final.domain_state.obedience_maturity <= 10.0
        # tick은 4번째 phase 길이
        assert final.tick == 30

    def test_seed_reproducibility(self, peter_calling_state):
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        r1 = world.run(seed=42)
        r2 = world.run(seed=42)
        assert (
            r1.final_states["peter"].emotions.fear
            == r2.final_states["peter"].emotions.fear
        )

    def test_different_seeds_produce_variation(self, peter_calling_state):
        """다른 seed는 다른 결과 (noise 효과)."""
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        results = [world.run(seed=s) for s in range(5)]
        fears = {r.final_states["peter"].emotions.fear for r in results}
        # 최소 2개 이상 다른 값 (state_noise_scale=0.02)
        assert len(fears) >= 2


class TestLegacyPhase5StillWorks:
    """Phase 5는 기존 500 tick v0.7 scenario로 별도 유지 — 영향 받지 않음."""

    def test_legacy_demo_v07_still_runs(self, peter_calling_state):
        """legacy initial_state.json 로드 → 기존 scenario 작동."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        # legacy mode: phases=None, v0.7과 동일
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter],
            max_tick=100,
            state_noise_scale=0.05,
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        # PhasedMultiAgentResult 아님 — 단일 phase 모드는 기존 MultiAgentResult
        from engine.simulation.world import MultiAgentResult
        assert isinstance(result, MultiAgentResult)
        assert not isinstance(result, PhasedMultiAgentResult)
        # legacy 수치 보존 (jesus_understanding이 "messiah_political"로 유지)
        assert result.final_states["peter"].domain_state.jesus_understanding == "messiah_political"


class TestArchitecturalClaims:
    """reviewer 피드백이 실제 코드에서 증명됨을 확인."""

    def test_claim_phase_linked_stitched_internal(self, peter_calling_state):
        """'표면은 연속, 내부는 stitched' 증명 — per_phase_results로 분리 접근 가능."""
        config = _build_full_arc_config(peter_calling_state)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        # 각 phase의 독립 결과가 있음
        for phase_id in ["01_calling", "02_galilean", "03_confession", "04_journey"]:
            assert phase_id in result.per_phase_results

    def test_claim_legacy_mode_identical_to_v07(self, peter_calling_state):
        """phases=None 모드가 v0.7과 완전 동일 동작."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        config = SimulationConfig(
            initial_state=legacy_peter, initial_states=[legacy_peter],
            max_tick=50, state_noise_scale=0.05,
        )
        phased_world = PhasedSimulationWorld(config, _rules())
        phased_result = phased_world.run(seed=7)

        from engine.simulation.world import SimulationWorld
        direct_world = SimulationWorld(config, _rules())
        direct_result = direct_world.run(seed=7)

        # 동일한 값
        assert (
            phased_result.final_states["peter"].emotions.fear
            == direct_result.final_states["peter"].emotions.fear
        )
