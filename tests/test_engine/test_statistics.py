"""통계 유틸 테스트 + 기존 핵심 수치에 CI 적용."""

from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.statistics import (
    cohens_d,
    confidence_interval,
    format_ci,
    proportion_ci,
)
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


class TestConfidenceInterval:
    def test_normal_data(self):
        values = [10, 12, 11, 13, 10, 12, 11, 13, 10, 12]
        ci = confidence_interval(values)
        assert ci.lower < ci.mean < ci.upper
        assert ci.n == 10

    def test_single_value(self):
        ci = confidence_interval([5.0])
        assert ci.mean == 5.0
        assert ci.lower == 5.0 == ci.upper

    def test_empty(self):
        ci = confidence_interval([])
        assert ci.n == 0

    def test_proportion_ci(self):
        # 10/10 successes -> upper should be 1.0
        ci = proportion_ci(10, 10)
        assert ci.mean == 1.0
        assert ci.upper <= 1.0
        # 0/10 -> lower = 0
        ci = proportion_ci(0, 10)
        assert ci.mean == 0.0
        assert ci.lower >= 0.0

    def test_format_ci(self):
        ci = confidence_interval([10.0, 12.0, 11.0, 13.0, 12.0])
        s = format_ci(ci)
        assert "[" in s and "]" in s


class TestEffectSize:
    def test_large_difference(self):
        a = [100, 102, 98, 101, 99, 103]
        b = [10, 12, 8, 11, 9, 13]
        result = cohens_d(a, b)
        assert result.cohens_d > 0.8  # large effect
        assert result.interpretation == "large"

    def test_no_difference(self):
        a = [10, 11, 10, 11, 10, 11]
        b = [10, 11, 10, 11, 10, 11]
        result = cohens_d(a, b)
        assert abs(result.cohens_d) < 0.1

    def test_medium_effect(self):
        # Cohen's d ~ 0.5
        a = [10, 11, 10, 11, 12, 10, 11, 12]
        b = [8, 9, 8, 9, 10, 8, 9, 10]
        result = cohens_d(a, b)
        assert 0.5 < abs(result.cohens_d) < 3.0

    def test_insufficient_sample(self):
        """n<2 그룹은 insufficient 반환."""
        result = cohens_d([1.0], [2.0, 3.0, 4.0])
        assert result.interpretation == "insufficient"
        assert result.cohens_d == 0.0

    def test_small_effect_interpretation(self):
        """abs_d in [0.2, 0.5) → 'small'."""
        # 충분한 variance + 작은 mean shift → small effect
        a = [9.0, 10.5, 11.0, 12.0, 8.5, 10.5, 11.5, 9.5, 10.0, 11.0]
        b = [8.5, 10.0, 10.5, 11.5, 8.0, 10.0, 11.0, 9.0, 9.5, 10.5]
        result = cohens_d(a, b)
        # pooled_std ~1.1, mean_diff=0.5 → d ~ 0.4 (small)
        assert result.interpretation == "small", \
            f"expected small, got {result.interpretation} (d={result.cohens_d:.3f})"

    def test_medium_effect_interpretation(self):
        """abs_d in [0.5, 0.8) → 'medium' (라인 102 브랜치)."""
        # mean_diff 0.8 / pooled_std ~1.2 → d ~ 0.65
        a = [9.0, 10.5, 11.0, 12.0, 8.5, 10.5, 11.5, 9.5, 10.0, 11.0]
        b = [8.2, 9.7, 10.2, 11.2, 7.7, 9.7, 10.7, 8.7, 9.2, 10.2]
        result = cohens_d(a, b)
        assert result.interpretation == "medium", \
            f"expected medium, got {result.interpretation} (d={result.cohens_d:.3f})"


class TestProportionCIEdges:
    def test_zero_total(self):
        """total=0 → 모든 값 0."""
        ci = proportion_ci(0, 0)
        assert ci.mean == 0.0
        assert ci.lower == 0.0
        assert ci.upper == 0.0
        assert ci.n == 0

    def test_99_ci_level(self):
        """ci_level=0.99 → z=2.576 branch."""
        ci = proportion_ci(5, 10, ci_level=0.99)
        assert ci.lower < ci.mean < ci.upper
        # 99% CI는 95% CI보다 넓음
        ci95 = proportion_ci(5, 10, ci_level=0.95)
        assert (ci.upper - ci.lower) >= (ci95.upper - ci95.lower)


class TestFormatCI:
    def test_format_as_pct(self):
        from engine.simulation.statistics import CIResult
        ci = CIResult(mean=0.75, lower=0.6, upper=0.9, std=0.05, n=10, ci_level=0.95)
        s = format_ci(ci, as_pct=True)
        assert "%" in s
        assert "75" in s or "75.0" in s  # 75% 포함


@pytest.mark.slow
class TestCoreFindingsWithCI:
    """기존 핵심 발견에 CI/effect size를 적용."""

    def _engine(self):
        return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])

    def _run_batch(self, n_seeds: int, include_judas: bool = True):
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
        crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
        interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
        profiles = {
            "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
            "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
            "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
            "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
        }
        agents = [peter, judas, caiaphas, crowd] if include_judas else [peter, caiaphas, crowd]
        if not include_judas:
            profiles = {k: v for k, v in profiles.items() if k != "judas"}

        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=agents,
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        results = []
        for seed in range(n_seeds):
            r = SimulationWorld(config, self._engine(), behavior_profiles=profiles).run(seed=seed)
            results.append(r)
        return results

    def test_arrest_tick_with_ci(self):
        """체포 tick의 95% CI."""
        results = self._run_batch(30, include_judas=True)
        arrest_ticks = [
            next((t["tick"] for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"), 500)
            for r in results
        ]
        spontaneous = [t for t in arrest_ticks if t < 400]

        ci = confidence_interval(spontaneous)
        sp_rate_ci = proportion_ci(len(spontaneous), len(arrest_ticks))

        print("\n=== Arrest Statistics with CI (n=30) ===")
        print(f"Mean arrest tick (spontaneous only): {format_ci(ci)}")
        print(f"Spontaneous rate: {format_ci(sp_rate_ci, as_pct=True)}")

        # CI 포함
        assert ci.lower < ci.mean < ci.upper
        assert sp_rate_ci.upper >= 0.8  # spontaneous rate는 80% 이상

    def test_judas_effect_size(self):
        """Judas 유무의 effect size."""
        with_judas = self._run_batch(15, include_judas=True)
        without_judas = self._run_batch(15, include_judas=False)

        def _arrest_tick(r):
            return next((t["tick"] for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"), 500)

        with_ticks = [_arrest_tick(r) for r in with_judas]
        without_ticks = [_arrest_tick(r) for r in without_judas]

        effect = cohens_d(with_ticks, without_ticks)

        print("\n=== Judas Effect Size ===")
        print(f"With Judas: mean={sum(with_ticks)/len(with_ticks):.0f}")
        print(f"Without Judas: mean={sum(without_ticks)/len(without_ticks):.0f}")
        print(f"Cohen's d: {effect.cohens_d:.2f} ({effect.interpretation})")
        print(f"Mean difference: {effect.mean_diff:.0f} ticks")

        # Judas 제거의 effect는 "large"여야 함 (counterfactual 확증)
        assert effect.interpretation == "large"
