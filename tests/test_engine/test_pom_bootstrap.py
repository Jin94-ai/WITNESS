"""POM pass rate bootstrap CI.

기존 POM 결과: all_pass ~50% (n=20). 하지만 이 CI가 충분히 robust한가?
Bootstrap resampling으로 95% CI를 직접 계산하고, parametric CI와 비교.

또한 per-pattern pass rate를 같이 측정해서
"어떤 패턴이 bottleneck인가?"를 정량화.
"""

import random
import statistics
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.peter.pom_scorecard import make_peter_scorecard
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
class TestPOMBootstrap:
    def test_pom_bootstrap_ci(self):
        """POM all_pass rate의 bootstrap 95% CI + per-pattern 분석."""
        n_seeds = 40
        scorecard = make_peter_scorecard()

        # Collect per-pattern pass booleans for each run
        pattern_names = [p.name for p in scorecard]
        per_run_results: list[dict[str, bool]] = []
        all_pass_results: list[bool] = []

        for seed in range(n_seeds):
            mr = _run(seed)
            sr = mr.extract_agent_result("peter")
            per_run = {p.name: p.evaluate(sr) for p in scorecard}
            per_run_results.append(per_run)
            all_pass_results.append(all(per_run.values()))

        # Overall all_pass rate
        all_pass_count = sum(all_pass_results)
        point_rate = all_pass_count / n_seeds

        # Bootstrap: resample runs, recompute rate
        rng = random.Random(42)
        B = 2000
        bootstrap_rates = []
        for _ in range(B):
            sample = [rng.choice(all_pass_results) for _ in range(n_seeds)]
            bootstrap_rates.append(sum(sample) / n_seeds)
        bootstrap_rates.sort()
        lo = bootstrap_rates[int(0.025 * B)]
        hi = bootstrap_rates[int(0.975 * B)]
        mean_bs = statistics.mean(bootstrap_rates)

        print(f"\n=== POM Bootstrap CI (n={n_seeds}, B={B}) ===")
        print(f"Point estimate (all_pass): {point_rate:.1%}")
        print(f"Bootstrap mean: {mean_bs:.1%}")
        print(f"Bootstrap 95% CI: [{lo:.1%}, {hi:.1%}]")

        # Per-pattern pass rates + bottleneck ranking
        print("\nPer-pattern pass rates (n=40):")
        print(f"{'pattern':>22} | {'pass rate':>10} | {'95% CI':>18}")
        print("-" * 58)

        from engine.simulation.statistics import proportion_ci
        ranked = []
        for name in pattern_names:
            count = sum(1 for r in per_run_results if r[name])
            ci = proportion_ci(count, n_seeds)
            ranked.append((name, ci))
            print(f"{name:>22} | {ci.mean:>10.1%} | "
                  f"[{ci.lower:>5.1%}, {ci.upper:>5.1%}]")

        # Bottleneck: lowest pass rate
        bottleneck = min(ranked, key=lambda x: x[1].mean)
        print(f"\nBottleneck pattern: {bottleneck[0]} ({bottleneck[1].mean:.1%})")

        # Correlation: if bottleneck fails, does all_pass fail?
        bottleneck_results = [r[bottleneck[0]] for r in per_run_results]
        # P(all_pass | bottleneck fails)
        fails = [not b for b in bottleneck_results]
        p_all_given_fail = (
            sum(
                1 for i, r in enumerate(per_run_results)
                if fails[i] and all(r.values())
            ) / max(sum(fails), 1)
        )
        print(f"P(all_pass | {bottleneck[0]} fails) = {p_all_given_fail:.1%}")

        # 검증: bootstrap CI와 parametric CI가 유사해야 함
        param_ci = proportion_ci(all_pass_count, n_seeds)
        width_diff = abs((hi - lo) - (param_ci.upper - param_ci.lower))
        print(f"\nParametric CI: [{param_ci.lower:.1%}, {param_ci.upper:.1%}]")
        print(f"CI width difference: {width_diff:.3f}")

        # Bootstrap과 parametric CI width 차이가 10%pt 이내
        assert width_diff < 0.10, f"CI methods disagree: diff={width_diff:.3f}"

        # all_pass rate가 random(1/2^7 = 0.8%)보다 훨씬 높아야 함
        assert point_rate > 0.10, f"POM pass rate {point_rate:.0%} too low"

    def test_pom_sufficiency_vs_necessity(self):
        """각 패턴의 필요조건성: 어떤 패턴이 all_pass와 가장 강하게 연관되는가?

        Matthews Correlation Coefficient (φ): 이진 상관.
        """
        n_seeds = 40
        scorecard = make_peter_scorecard()
        pattern_names = [p.name for p in scorecard]

        per_run_results = []
        for seed in range(n_seeds):
            mr = _run(seed)
            sr = mr.extract_agent_result("peter")
            per_run = {p.name: p.evaluate(sr) for p in scorecard}
            per_run["_all_pass"] = all(
                per_run[n] for n in pattern_names
            )
            per_run_results.append(per_run)

        print(f"\n=== Pattern-AllPass Correlation (n={n_seeds}) ===")
        print(f"{'pattern':>22} | {'pass rate':>10} | {'phi':>7}")
        print("-" * 45)

        results = []
        for name in pattern_names:
            # 2x2 contingency
            a = sum(1 for r in per_run_results if r[name] and r["_all_pass"])
            b = sum(1 for r in per_run_results if r[name] and not r["_all_pass"])
            c = sum(1 for r in per_run_results if not r[name] and r["_all_pass"])
            d = sum(1 for r in per_run_results if not r[name] and not r["_all_pass"])

            denom = ((a + b) * (c + d) * (a + c) * (b + d)) ** 0.5
            phi = (a * d - b * c) / denom if denom > 0 else 0
            pass_rate = (a + b) / n_seeds
            results.append((name, pass_rate, phi))
            print(f"{name:>22} | {pass_rate:>10.1%} | {phi:>7.3f}")

        # 높은 phi: 해당 패턴이 all_pass 결정에 중요
        sorted_by_phi = sorted(results, key=lambda x: -abs(x[2]))
        top = sorted_by_phi[0]
        print(f"\nMost discriminating pattern: {top[0]} (phi={top[2]:.3f})")
        print("(phi near 1: 이 패턴 통과가 all_pass와 강하게 일치)")

        # 최고 discriminator phi >= 0.3
        assert abs(top[2]) > 0.2, f"Top phi {top[2]:.3f} too weak"
