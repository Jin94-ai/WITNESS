"""Phase 1-4 전체 아크 emergent 패턴 앙상블 검증 (v1.2 Iter 30).

POM-style: 단일 seed의 결과가 아니라 N seed 앙상블에서 canonical-compatible
패턴이 나타나는지 확인. reviewer 질문 §3 Q4 (MVP 선택), Q6 (연속 vs stitched)
에 대한 empirical evidence.

검증 패턴 (개별 run이 아닌 앙상블 평균/비율):
1. 완주율: 모든 seed에서 4 phase 모두 완주
2. awe 진행: Phase 1 (calling) < Phase 3 (transfiguration peak) 평균값
3. obedience_maturity 단조 성장: Phase 1 → 4 평균값이 non-decreasing
4. fear bounded: [0, 10] at every phase end
5. jesus_understanding 전환: Phase 1 종료 시 None이 아닌 값으로 전환
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
N_SEEDS = 10


@pytest.fixture(scope="module")
def _setup_domain():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
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


def _build_arc_config():
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    phases = [
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
        ),
    ]
    return SimulationConfig(
        initial_state=peter, initial_states=[peter, judas],
        max_tick=5000, state_noise_scale=0.02, phases=phases,
    )


@pytest.fixture(scope="module")
def ensemble_results(_setup_domain):
    """N_SEEDS × 4 phase 앙상블 실행 결과 캐싱."""
    config = _build_arc_config()
    results = []
    for seed in range(N_SEEDS):
        world = PhasedSimulationWorld(config, _rules())
        results.append(world.run(seed=seed))
    return results


class TestArcCompletion:
    def test_all_seeds_complete_all_phases(self, ensemble_results):
        for i, r in enumerate(ensemble_results):
            assert len(r.per_phase_results) == 4, \
                f"seed {i}: only {len(r.per_phase_results)} phases completed"

    def test_all_seeds_have_final_peter(self, ensemble_results):
        for r in ensemble_results:
            assert "peter" in r.final_states


class TestAweProgression:
    """Awe는 Phase 1 calling에서 시작, Phase 3 transfiguration에서 peak 기대."""

    def test_phase1_end_awe_positive(self, ensemble_results):
        """Phase 1 종료 시 awe 평균 > 3.0 (기적 어획 효과)."""
        awes = [
            r.per_phase_results["01_calling"].final_states["peter"].emotions.awe
            for r in ensemble_results
        ]
        mean_awe = sum(awes) / len(awes)
        assert mean_awe >= 3.0, f"mean awe after Phase 1 = {mean_awe}"

    def test_awe_grows_through_arc(self, ensemble_results):
        """Phase 1 end < Phase 3 end 평균 (transfiguration 피크)."""
        p1 = [
            r.per_phase_results["01_calling"].final_states["peter"].emotions.awe
            for r in ensemble_results
        ]
        p3 = [
            r.per_phase_results["03_confession"].final_states["peter"].emotions.awe
            for r in ensemble_results
        ]
        mean_p1 = sum(p1) / len(p1)
        mean_p3 = sum(p3) / len(p3)
        assert mean_p3 >= mean_p1, f"P1 mean {mean_p1} > P3 mean {mean_p3}"


class TestObedienceAccumulation:
    """obedience_maturity는 phase별 non-decreasing 평균 (canonical 누적)."""

    def test_obedience_non_decreasing_ensemble(self, ensemble_results):
        means = []
        for phase_id in ["01_calling", "02_galilean", "03_confession", "04_journey"]:
            vals = [
                r.per_phase_results[phase_id].final_states["peter"].domain_state.obedience_maturity
                for r in ensemble_results
            ]
            means.append(sum(vals) / len(vals))
        # 각 phase 평균이 전보다 >= (최대 noise로 소폭 역전 가능하므로 -0.3 허용)
        for i in range(1, len(means)):
            assert means[i] >= means[i - 1] - 0.3, (
                f"obedience phase means not increasing: {means}"
            )

    def test_final_obedience_strongly_positive(self, ensemble_results):
        """4-phase 종료 평균 obedience_maturity > 5.0."""
        obs = [
            r.final_states["peter"].domain_state.obedience_maturity
            for r in ensemble_results
        ]
        mean_ob = sum(obs) / len(obs)
        assert mean_ob >= 5.0, f"mean final obedience = {mean_ob}"


class TestBoundedness:
    """모든 phase 종료 시 fast state가 [0, 10] 범위."""

    def test_fear_bounded_at_all_phase_ends(self, ensemble_results):
        for r in ensemble_results:
            for phase_id, phase_r in r.per_phase_results.items():
                fear = phase_r.final_states["peter"].emotions.fear
                assert 0.0 <= fear <= 10.0, f"{phase_id}: fear={fear} out of bounds"

    def test_awe_bounded_at_all_phase_ends(self, ensemble_results):
        for r in ensemble_results:
            for phase_id, phase_r in r.per_phase_results.items():
                awe = phase_r.final_states["peter"].emotions.awe
                assert 0.0 <= awe <= 10.0


class TestJesusUnderstandingTransition:
    """Phase 1 종료 시 peter.jesus_understanding이 None에서 값 있는 상태로 전환.

    canonical_events의 effects가 jesus_understanding 필드를 직접 세팅하는지는
    content 결정이지만, 앙상블에서 절반 이상 전환이 일어났다면 emergent transition.
    (이 test는 느슨한 필수조건만 — content side effect 여부에 따라 결과 변동 가능)
    """

    def test_understanding_stays_or_transitions(self, ensemble_results):
        """Phase 1 완료 시 jesus_understanding이 None이거나 canonical literal."""
        allowed = {
            None, "teacher", "prophet", "messiah_political",
            "messiah_suffering", "son_of_god", "risen_lord", "sending_lord",
        }
        for r in ensemble_results:
            val = r.per_phase_results["01_calling"].final_states["peter"].domain_state.jesus_understanding
            assert val in allowed, f"unexpected jesus_understanding: {val}"


class TestReproducibility:
    def test_same_seed_deterministic(self, _setup_domain):
        config = _build_arc_config()
        w1 = PhasedSimulationWorld(config, _rules()).run(seed=42)
        w2 = PhasedSimulationWorld(config, _rules()).run(seed=42)
        assert (
            w1.final_states["peter"].emotions.awe
            == w2.final_states["peter"].emotions.awe
        )
        assert (
            w1.final_states["peter"].domain_state.obedience_maturity
            == w2.final_states["peter"].domain_state.obedience_maturity
        )

    def test_different_seeds_vary(self, ensemble_results):
        """state_noise_scale=0.02로 최소 2개 이상 서로 다른 fear 값."""
        fears = {r.final_states["peter"].emotions.fear for r in ensemble_results}
        assert len(fears) >= 2, f"no variation across seeds: {fears}"
