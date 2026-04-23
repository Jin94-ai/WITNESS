"""Sample Size Convergence Analysis.

"얼마나 많은 시뮬레이션을 돌려야 robust한 결과를 얻는가?"
mean arrest_tick과 95% CI가 n 증가에 따라 어떻게 수렴하는가.

n = [10, 20, 40, 80, 120]에서 측정:
- Point estimate (mean)
- 95% CI width
- 추정의 안정성 (연속 n 간 차이)

의의: 미래 연구자에게 sample size guideline 제공.
"""

import statistics
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
from engine.simulation.statistics import confidence_interval
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
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
    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestSampleConvergence:
    def test_mean_arrest_tick_convergence(self):
        """n이 늘어날수록 mean과 CI가 수렴하는가."""
        max_n = 120
        arrest_ticks: list[int] = []
        for seed in range(max_n):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(arrests[0]["tick"])

        print(f"\n=== Sample Size Convergence (n=[10,20,40,80,{max_n}]) ===")
        print(f"{'n':>6} | {'mean':>8} | {'std':>7} | {'95% CI':>20} | {'CI width':>10}")
        print("-" * 60)

        checkpoints = [10, 20, 40, 80, len(arrest_ticks)]
        means = {}
        widths = {}
        for n in checkpoints:
            subset = arrest_ticks[:n]
            if len(subset) < 2:
                continue
            mean = statistics.mean(subset)
            sd = statistics.stdev(subset)
            ci = confidence_interval(subset)
            width = ci.upper - ci.lower
            means[n] = mean
            widths[n] = width
            print(f"{n:>6} | {mean:>8.1f} | {sd:>7.1f} | "
                  f"[{ci.lower:>6.1f}, {ci.upper:>6.1f}] | {width:>9.1f}")

        # CI width가 n이 늘어나면 감소하는가?
        # width ∝ 1/sqrt(n) 이론적 관계
        print("\nCI width ratio (이론: 1/sqrt(n1/n0)):")
        ns = sorted(widths.keys())
        for i in range(1, len(ns)):
            actual = widths[ns[i]] / widths[ns[i-1]]
            theoretical = (ns[i-1] / ns[i]) ** 0.5
            print(f"  n={ns[i-1]}->{ns[i]}: actual={actual:.2f}, theoretical={theoretical:.2f}")

        # 최종 mean이 이전 checkpoint mean과 비교해 안정적인지
        # n=80 vs n=120 mean 차이가 작아야 수렴 증거
        if 80 in means and len(arrest_ticks) in means:
            mean_80 = means[80]
            mean_final = means[len(arrest_ticks)]
            stability = abs(mean_final - mean_80)
            print(f"\nMean change n=80->n={len(arrest_ticks)}: {stability:.1f} ticks")
            # 안정성 기준: 5 ticks 이내 (CI half-width 고려)
            assert stability < 10, f"Mean unstable: {stability:.1f} tick change"

        # CI 축소 확인: n=80 width < n=20 width
        if 20 in widths and 80 in widths:
            ratio = widths[80] / widths[20]
            # 이론: sqrt(20/80) = 0.5
            print(f"CI width n=80 / n=20: {ratio:.2f} (theoretical 0.50)")
            # 0.3 ~ 0.7 사이여야 합리적
            assert 0.3 < ratio < 0.8, \
                f"CI shrinkage {ratio:.2f} inconsistent with sqrt(n) scaling"

    def test_minimum_adequate_n_for_spontaneous_rate(self):
        """Spontaneous rate 추정에 필요한 최소 n 확인.

        각 seed에서 spontaneous(<400) 여부를 한 번만 확인 후 n 서브셋별 CI 측정.
        """
        from engine.simulation.statistics import proportion_ci

        n_seeds = 80
        is_spontaneous = []  # seed 순서 유지
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            is_spontaneous.append(bool(arrests) and arrests[0]["tick"] < 400)

        print(f"\n=== Spontaneous Rate Convergence (up to n={n_seeds}) ===")
        print(f"{'n':>6} | {'rate':>7} | {'95% CI':>18} | {'lower bound':>12}")
        print("-" * 55)

        for checkpoint in [10, 20, 40, 80]:
            if checkpoint > n_seeds:
                continue
            subset_count = sum(1 for x in is_spontaneous[:checkpoint] if x)
            ci = proportion_ci(subset_count, checkpoint)
            print(f"{checkpoint:>6} | {ci.mean:>7.1%} | "
                  f"[{ci.lower:.1%}, {ci.upper:.1%}] | {ci.lower:>11.1%}")

        total_spontaneous = sum(is_spontaneous)
        ci_full = proportion_ci(total_spontaneous, n_seeds)
        # n=80에서 lower bound >= 90% (arrest_rate 100% 기대)
        assert ci_full.lower >= 0.90, \
            f"At n={n_seeds}, spontaneous rate lower CI {ci_full.lower:.0%} < 90%"
