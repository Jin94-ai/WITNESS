"""Talleyrand POM scorecard 앙상블 검증 (Iter 56).

20 seed × 500 tick full career 실행 → 7개 Type A 패턴 동시 통과율 측정.
Peter POM all_pass 47.5%, VG POM 38.6% 대비 Talleyrand가 유사 범위 도달하면
"엔진이 3번째 이질적 시나리오 타입도 수용함"의 POM 수준 증거.
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
    register_domain_type("diplomacy", DiplomacyState)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
        FatigueRule(), HomeostasisRule(),
    ])


def _run(seed: int, max_tick: int = 500):
    t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
    events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
    config = SimulationConfig(
        initial_state=t, initial_states=[t],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events,
    )
    return SimulationWorld(config, _rules()).run(seed=seed)


@pytest.fixture(scope="module")
def ensemble(_setup):
    return [_run(seed=s) for s in range(20)]


class TestScorecardShape:
    def test_seven_patterns(self):
        sc = make_talleyrand_scorecard()
        assert len(sc) == 7

    def test_all_named_uniquely(self):
        sc = make_talleyrand_scorecard()
        names = [p.name for p in sc]
        assert len(set(names)) == len(names)


class TestIndividualPatternsOnSingleRun:
    """seed=0 single run: 각 패턴이 True/False 제대로 반환."""

    def test_all_patterns_evaluate(self, _setup):
        r = _run(seed=0)
        sc = make_talleyrand_scorecard()
        evaluation = evaluate_pom(r, sc)
        assert len(evaluation) == 7
        # 각 결과는 bool
        for name, v in evaluation.items():
            assert isinstance(v, bool), f"{name} returned non-bool {v}"


class TestEnsemblePassRates:
    """20 seed 앙상블: 패턴별 통과율 + all-pass rate."""

    def test_multi_regime_survival_high_pass(self, ensemble):
        """regime 전환은 deterministic (tick-fixed) 하므로 100% 통과 기대."""
        sc = make_talleyrand_scorecard()
        survival_p = next(p for p in sc if p.name == "multi_regime_survival")
        passes = sum(1 for r in ensemble if survival_p.evaluate(r))
        assert passes == 20

    def test_network_regime_span_grown(self, ensemble):
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "network_regime_span_grown")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        assert passes == 20  # canonical effects deterministic

    def test_reputation_ambiguity_emergent(self, ensemble):
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "reputation_ambiguity_emergent")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        # canonical effects 누적 ~9.0 > 6.0 threshold
        assert passes == 20

    def test_compromise_accumulation(self, ensemble):
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "compromise_accumulation")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        assert passes == 20  # canonical 3 compromises deterministic

    def test_no_emotional_collapse(self, ensemble):
        """fear/grief 붕괴 없이 career 유지 — noise 고려 최소 17/20."""
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "no_emotional_collapse")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        assert passes >= 17

    def test_career_continuity(self, ensemble):
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "career_continuity")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        assert passes == 20  # max_tick 500 도달 보장

    def test_legitimacy_below_anchor(self, ensemble):
        """초기 3.5, canonical 누적 -0.5 → 3.0. pragmatic 유지."""
        sc = make_talleyrand_scorecard()
        p = next(p for p in sc if p.name == "legitimacy_below_anchor")
        passes = sum(1 for r in ensemble if p.evaluate(r))
        assert passes == 20


class TestAllPassRate:
    def test_all_pass_rate_high(self, ensemble):
        """Type A 패턴은 대부분 canonical effects 결정적 → all_pass > 80%."""
        sc = make_talleyrand_scorecard()
        all_pass = 0
        for r in ensemble:
            ev = evaluate_pom(r, sc)
            if all(ev.values()):
                all_pass += 1
        rate = all_pass / len(ensemble)
        # canonical 결정적이라 높아야 함 (Peter 47.5%, VG 38.6% 대비 Talleyrand는 단순)
        assert rate >= 0.80, f"all_pass = {all_pass}/{len(ensemble)} = {rate:.2%}"
