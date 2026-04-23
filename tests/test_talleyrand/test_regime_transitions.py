"""Talleyrand 시나리오 regime transition E2E (Iter 55).

canonical_events.json의 6 regime transition이 실제 `SimulationWorld`에서
fire되어 Talleyrand.domain_state를 정확히 전환시키는지 검증.

POM 예비 스코어카드 (ChatGPT 권장 Type A 패턴):
1. 다체제 생존: 5+ regime 거침
2. 다중 체제 인맥: network_regime_span이 최종 > 4
3. 평판 분산: reputation_ambiguity 증가
4. 원칙 vs 실용: legitimacy_anchor 낮음 유지
5. 재기: falls_from_favor 후에도 다음 체제에서 leverage 회복
"""

from pathlib import Path

import pytest

from content.talleyrand.domain_diplomacy import DiplomacyState
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


def _run_full_career(seed: int = 0, max_tick: int = 500):
    talleyrand = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
    events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
    config = SimulationConfig(
        initial_state=talleyrand,
        initial_states=[talleyrand],
        max_tick=max_tick,
        state_noise_scale=0.0,
        events=events,
    )
    return SimulationWorld(config, _rules()).run(seed=seed)


class TestRegimeProgression:
    def test_initial_is_ancien_regime(self, _setup):
        t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
        assert t.domain_state.current_regime == "ancien_regime"

    def test_after_tick_0_revolution(self, _setup):
        result = _run_full_career(max_tick=5)
        assert result.final_states["talleyrand"].domain_state.current_regime == "revolution"

    def test_after_tick_100_directory_or_consulate(self, _setup):
        """tick 100 시점 — Directory(72) 지남, Consulate(120) 전."""
        result = _run_full_career(max_tick=100)
        assert result.final_states["talleyrand"].domain_state.current_regime == "directory"

    def test_after_tick_200_empire(self, _setup):
        result = _run_full_career(max_tick=200)
        # tick 180 empire, tick 216 falls_from_favor (regime 유지)
        assert result.final_states["talleyrand"].domain_state.current_regime == "empire"

    def test_full_career_ends_july_monarchy(self, _setup):
        result = _run_full_career(max_tick=500)
        assert result.final_states["talleyrand"].domain_state.current_regime == "july_monarchy"


class TestNegotiatorEmergentPatterns:
    """Type A 협상형 POM 예비 패턴."""

    def test_multi_regime_survival(self, _setup):
        """모든 6 regime 전환을 거치면서 agent 생존."""
        result = _run_full_career(max_tick=500)
        assert result.final_states["talleyrand"].tick == 500

    def test_network_regime_span_grows(self, _setup):
        """network_regime_span은 체제 전환마다 +1 → 최종 > initial."""
        result = _run_full_career(max_tick=500)
        span = result.final_states["talleyrand"].domain_state.network_regime_span
        # 초기 1 → +1(directory) +1(consulate) +1(restoration) +1(july) = 5
        assert span >= 4

    def test_reputation_ambiguity_increases(self, _setup):
        """다중 체제 봉사로 평판 ambiguity 축적."""
        result = _run_full_career(max_tick=500)
        final_amb = result.final_states["talleyrand"].domain_state.reputation_ambiguity
        # 초기 4.0 → canonical +1.0 (rev) +0.5 (cons) +1.5 (fall) +1.0 (restore) +1.0 (july) = 9.0 cap
        assert final_amb >= 7.0

    def test_compromise_count_accumulates(self, _setup):
        result = _run_full_career(max_tick=500)
        count = result.final_states["talleyrand"].domain_state.compromise_count
        # revolution + consulate + falls = 3건 최소
        assert count >= 3

    def test_no_single_bottleneck_event(self, _setup):
        """Peter의 sword_drawn 같은 단일 rare-action bottleneck 없음.

        대신 6개 regime 전환이 고르게 분포. fired_events 6개 이상.
        """
        result = _run_full_career(max_tick=500)
        assert len(result.fired_events) >= 6


class TestStructuralContrast:
    """Peter/VG와 구조적으로 다름을 증명."""

    def test_no_emotional_crisis_collapse(self, _setup):
        """Peter의 denial/Gauguin의 departure 같은 극단적 감정 붕괴 없음.
        fear/grief가 bounded."""
        result = _run_full_career(max_tick=500)
        final = result.final_states["talleyrand"]
        assert 0.0 <= final.emotions.fear <= 10.0
        assert 0.0 <= final.emotions.grief <= 10.0

    def test_regime_is_categorical_not_continuous(self, _setup):
        """current_regime은 Literal — 누적 threshold가 아닌 discrete state."""
        result = _run_full_career(max_tick=500)
        regime = result.final_states["talleyrand"].domain_state.current_regime
        allowed = {
            "ancien_regime", "revolution", "directory", "consulate",
            "empire", "bourbon_restoration", "july_monarchy",
        }
        assert regime in allowed
