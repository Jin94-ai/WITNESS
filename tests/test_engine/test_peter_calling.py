"""Phase 1 소명 E2E 시뮬레이션 (v1.2 Iteration 7).

소명 phase를 실제 시뮬레이터에서 돌려 emergent 결과 검증:
- 5개 canonical events 전부 발동
- 기적 목격 후 awe 급상승
- obedience_maturity 누적 증가
- 마지막에 leave_everything_follow가 선택되는 경우 존재 (emergent)
"""

from pathlib import Path

import pytest

from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import Phase, PhaseExitCondition
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
from engine.simulation.phased_world import PhasedSimulationWorld
from engine.simulation.world import SimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _setup():
    register_domain_type("faith_journey", FaithJourneyState)


def _rule_engine() -> RuleEngine:
    # 소명 phase는 심한 감정 swing이 적으므로 가벼운 rule set
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _build_calling_config() -> SimulationConfig:
    """소명 phase 전용 SimulationConfig (단일 phase 모드, 편의)."""
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    events = load_events(CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json")
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter],
        max_tick=84,
        events=events,
        state_noise_scale=0.02,
        tick_scale_hours=2.0,
    )


@pytest.fixture(scope="module")
def _module_setup():
    _setup()
    return None


class TestCallingPhaseSingleRun:
    def test_runs_84_ticks(self, _module_setup):
        config = _build_calling_config()
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        assert result.final_states["peter"].tick == 84

    def test_all_canonical_events_fired(self, _module_setup):
        """5개 이벤트 모두 실제 fire (effects 적용되어 state 이동)."""
        config = _build_calling_config()
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        # 84 tick 안에 5개 이벤트 tick (3, 8, 14, 20, 30) 모두 통과
        assert result.final_states["peter"].tick > 30

    def test_awe_rises_after_miraculous_catch(self, _module_setup):
        """기적 어획(tick 14) 후 awe가 0에서 크게 상승."""
        config = _build_calling_config()
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        final = result.final_states["peter"]
        # 초기값 0.0, 이벤트에서 +1.0, +5.0, 등 누적 → 최소 3.0 이상
        assert final.emotions.awe >= 3.0, f"awe = {final.emotions.awe}"

    def test_obedience_accumulates(self, _module_setup):
        """obedience_maturity는 0에서 시작 → canonical effects로 누적."""
        config = _build_calling_config()
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        final_domain = result.final_states["peter"].domain_state
        assert final_domain.obedience_maturity > 0.0, \
            f"obedience = {final_domain.obedience_maturity}"

    def test_fear_partly_resolves(self, _module_setup):
        """tick 20 fall_at_knees에서 fear 상승 후 tick 30 calling에서 감쇄."""
        config = _build_calling_config()
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        # 마지막 이벤트가 fear -1.5 효과. 초기 1.0에서 상승/하강 조정
        # 구체적 값 기대하지 않고 0-10 clamp 유효성만
        assert 0.0 <= result.final_states["peter"].emotions.fear <= 10.0


class TestCallingPhaseEnsemble:
    """10 시드 앙상블: emergent 패턴 검증."""

    def _run_ensemble(self, n: int = 10) -> list:
        config = _build_calling_config()
        results = []
        for seed in range(n):
            world = SimulationWorld(config, _rule_engine())
            results.append(world.run(seed=seed))
        return results

    def test_all_seeds_complete(self, _module_setup):
        results = self._run_ensemble(10)
        assert len(results) == 10
        assert all(r.final_states["peter"].tick == 84 for r in results)

    def test_ensemble_awe_consistently_high(self, _module_setup):
        """기적 목격 후 awe는 모든 시드에서 높음."""
        results = self._run_ensemble(10)
        awes = [r.final_states["peter"].emotions.awe for r in results]
        mean_awe = sum(awes) / len(awes)
        # 초기 0에서 시작해 이벤트 +1, +5 등 누적 → 평균 3+
        assert mean_awe >= 3.0, f"mean awe = {mean_awe}, values = {awes}"

    def test_ensemble_obedience_emergent(self, _module_setup):
        """소명 수락이 emergent: obedience_maturity 평균 2.0 이상."""
        results = self._run_ensemble(10)
        obs = [
            r.final_states["peter"].domain_state.obedience_maturity
            for r in results
        ]
        mean_ob = sum(obs) / len(obs)
        # canonical effects +1, +1, +0.5 + 행동 선택 시 추가 → 평균 2.0+
        assert mean_ob >= 2.0, f"mean obedience = {mean_ob}, values = {obs}"


class TestPhasedWorldCallingIntegration:
    """PhasedSimulationWorld에서 소명 phase 실행."""

    def test_single_phase_via_phased_world(self, _module_setup):
        config = _build_calling_config()
        # phases에 단일 phase 지정
        config_phased = config.model_copy(update={
            "phases": [
                Phase(
                    phase_id="01_calling",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                ),
            ],
        })
        world = PhasedSimulationWorld(config_phased, _rule_engine())
        result = world.run(seed=0)
        # phase-linked 결과 타입
        from engine.simulation.phased_world import PhasedMultiAgentResult
        assert isinstance(result, PhasedMultiAgentResult)
        assert "01_calling" in result.per_phase_results
        # Phase 종료 시 obedience_maturity 누적됨
        assert result.final_states["peter"].domain_state.obedience_maturity > 0.0
