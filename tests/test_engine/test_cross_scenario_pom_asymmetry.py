"""Cross-scenario POM asymmetry — universality 증거 (Iter 57).

핵심 주장:
    **엔진은 범용, 패턴은 시나리오 특이**

검증 방식:
- Peter scorecard on Peter: expected high pass rate (~50%)
- Peter scorecard on Talleyrand: expected LOW pass rate (구조적 부정합)
- Talleyrand scorecard on Talleyrand: high pass rate (>80%, Iter 56)
- Talleyrand scorecard on Peter: expected LOW pass rate

이 비대칭성이 성립하면:
(a) 동일 엔진이 이질적 시나리오 동역학을 모두 수용 (= universality)
(b) 각 시나리오 ground truth는 그 시나리오의 POM으로만 평가 가능
    (= structural isomorphism이 아니라 스페셜라이제이션)
"""

from pathlib import Path

import pytest

from content.talleyrand.domain_diplomacy import DiplomacyState
from content.talleyrand.pom_scorecard import make_talleyrand_scorecard
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
)
from engine.rules.physical import FatigueRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.pom import evaluate_pom
from engine.simulation.world import SimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup():
    from content.judas.domain_betrayal import BetrayalPsychologyState
    from content.peter.domain_faith import FaithJourneyState
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("diplomacy", DiplomacyState)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
        FatigueRule(), HomeostasisRule(),
    ])


def _run_talleyrand(seed: int, max_tick: int = 500):
    t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
    events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
    config = SimulationConfig(
        initial_state=t, initial_states=[t],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events,
    )
    return SimulationWorld(config, _rules()).run(seed=seed)


def _run_peter_legacy(seed: int, max_tick: int = 500):
    """Peter legacy 수난 시나리오 (v0.7 scenario)."""
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    config = SimulationConfig(
        initial_state=peter, initial_states=[peter],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events,
    )
    return SimulationWorld(config, _rules()).run(seed=seed)


N = 10  # ensemble size


@pytest.fixture(scope="module")
def talleyrand_ensemble(_setup):
    return [_run_talleyrand(s) for s in range(N)]


@pytest.fixture(scope="module")
def peter_ensemble(_setup):
    return [_run_peter_legacy(s) for s in range(N)]


def _all_pass_rate(ensemble, scorecard) -> float:
    n = 0
    for r in ensemble:
        ev = evaluate_pom(r, scorecard)
        if all(ev.values()):
            n += 1
    return n / len(ensemble)


class TestTalleyrandScorecardOnTalleyrand:
    """기준선: Talleyrand 스코어카드는 Talleyrand run에서 높은 통과율."""

    def test_high_pass_rate(self, talleyrand_ensemble):
        rate = _all_pass_rate(talleyrand_ensemble, make_talleyrand_scorecard())
        assert rate >= 0.80


class TestTalleyrandScorecardOnPeter:
    """핵심: Talleyrand 패턴(regime transition, network span 등)은 Peter run에서
    구조적으로 성립 불가 → all_pass ~ 0%."""

    def test_no_peter_run_passes_talleyrand_scorecard(self, peter_ensemble):
        rate = _all_pass_rate(peter_ensemble, make_talleyrand_scorecard())
        # Peter는 talleyrand agent가 없음 → 거의 모든 패턴 실패
        assert rate == 0.0

    def test_multi_regime_survival_pattern_fails_on_peter(self, peter_ensemble):
        """regime transition event는 Peter scenario에 없음."""
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "multi_regime_survival")
        passes = sum(1 for r in peter_ensemble if p.evaluate(r))
        assert passes == 0

    def test_peter_ensemble_fails_talleyrand_reputation_pattern(self, peter_ensemble):
        """Peter run엔 'talleyrand' 에이전트 없음 → KeyError 방어로 false 반환."""
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "reputation_ambiguity_emergent")
        # Peter ensemble에서 각 run에 talleyrand가 없으므로 pattern이 KeyError로 fail
        failures = 0
        for r in peter_ensemble:
            try:
                if not p.evaluate(r):
                    failures += 1
            except (KeyError, AttributeError):
                failures += 1
        assert failures == len(peter_ensemble)


class TestStructuralDistinction:
    """양쪽 scenario의 구조적 대비를 직접 측정."""

    def test_talleyrand_has_regime_events_peter_does_not(
        self, talleyrand_ensemble, peter_ensemble,
    ):
        t_regime_events = [
            len([e for e in r.fired_events if str(e.get("event_id", "")).startswith("regime_")])
            for r in talleyrand_ensemble
        ]
        p_regime_events = [
            len([e for e in r.fired_events if str(e.get("event_id", "")).startswith("regime_")])
            for r in peter_ensemble
        ]
        assert min(t_regime_events) >= 6
        assert max(p_regime_events) == 0

    def test_peter_has_denial_events_talleyrand_does_not(
        self, peter_ensemble, talleyrand_ensemble,
    ):
        p_denial_events = [
            len([e for e in r.fired_events if "denial" in str(e.get("event_id", ""))])
            for r in peter_ensemble
        ]
        t_denial_events = [
            len([e for e in r.fired_events if "denial" in str(e.get("event_id", ""))])
            for r in talleyrand_ensemble
        ]
        # Peter scenario에 3회 denial event 있음
        assert max(p_denial_events) >= 3
        # Talleyrand scenario엔 전혀 없음
        assert max(t_denial_events) == 0


class TestUniversalityClaim:
    """종합: 엔진은 범용이고 패턴은 특이하다."""

    def test_same_engine_runs_both_scenarios(self, _setup):
        """같은 SimulationWorld + RuleEngine이 Peter와 Talleyrand 모두 실행 완료."""
        t_run = _run_talleyrand(seed=0, max_tick=50)
        p_run = _run_peter_legacy(seed=0, max_tick=50)
        assert "talleyrand" in t_run.final_states
        assert "peter" in p_run.final_states

    def test_scorecards_are_not_interchangeable(
        self, talleyrand_ensemble, peter_ensemble,
    ):
        """Talleyrand 스코어카드는 Peter run에 적용해도 0%이고, 그 역도 유사하게 낮다.
        → 스코어카드는 시나리오 자산이지 범용 metric 아님."""
        talleyrand_on_peter = _all_pass_rate(
            peter_ensemble, make_talleyrand_scorecard(),
        )
        talleyrand_on_talleyrand = _all_pass_rate(
            talleyrand_ensemble, make_talleyrand_scorecard(),
        )
        # asymmetry > 0.7: 같은 scorecard가 cross-scenario에서 극단적으로 다른 결과
        assert (talleyrand_on_talleyrand - talleyrand_on_peter) >= 0.7
