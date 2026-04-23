"""Van Gogh POM pass rate bootstrap CI + pattern phi.

Peter POM 대응: all_pass rate와 per-pattern 분석.
Phi로 병목 패턴 식별.

목표:
- VG all_pass rate의 bootstrap CI
- VG 시나리오의 병목 패턴 식별
- Peter의 sword_drawn에 대응하는 패턴이 VG에도 존재하는가?
"""

import random
import statistics
from pathlib import Path

import pytest

from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from content.vangogh.pom_scorecard import make_vangogh_scorecard
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.statistics import proportion_ci
from engine.simulation.world import SimulationWorld

register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
    vg = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
    g = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
    t = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "vangogh" / "hazard_events.json")
    profiles = {
        "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=150, initial_state=vg,
        initial_states=[vg, g, t],
        hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestVGPOMBootstrap:
    def test_vg_pom_bootstrap_ci(self):
        """VG all_pass rate + per-pattern + phi 분석."""
        n_seeds = 40
        scorecard = make_vangogh_scorecard()
        pattern_names = [p.name for p in scorecard]

        per_run_results: list[dict[str, bool]] = []
        all_pass_results: list[bool] = []

        for seed in range(n_seeds):
            mr = _run(seed)
            sr = mr.extract_agent_result("vangogh")
            per_run = {p.name: p.evaluate(sr) for p in scorecard}
            per_run_results.append(per_run)
            all_pass_results.append(all(per_run.values()))

        all_pass_count = sum(all_pass_results)
        point_rate = all_pass_count / n_seeds

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

        print(f"\n=== VG POM Bootstrap CI (n={n_seeds}, B={B}) ===")
        print(f"Point estimate (all_pass): {point_rate:.1%}")
        print(f"Bootstrap mean: {mean_bs:.1%}")
        print(f"Bootstrap 95% CI: [{lo:.1%}, {hi:.1%}]")
        print("Peter reference: 47.5%, CI [32.5%, 62.5%]")

        # Per-pattern
        print("\nPer-pattern pass rates (n=40):")
        print(f"{'pattern':>20} | {'pass rate':>10} | {'95% CI':>18} | {'phi':>7}")
        print("-" * 65)
        ranked = []
        for name in pattern_names:
            count = sum(1 for r in per_run_results if r[name])
            ci = proportion_ci(count, n_seeds)
            # Phi with all_pass
            a = sum(1 for i, r in enumerate(per_run_results) if r[name] and all_pass_results[i])
            b = sum(1 for i, r in enumerate(per_run_results) if r[name] and not all_pass_results[i])
            c = sum(1 for i, r in enumerate(per_run_results) if not r[name] and all_pass_results[i])
            d = sum(1 for i, r in enumerate(per_run_results) if not r[name] and not all_pass_results[i])
            denom = ((a + b) * (c + d) * (a + c) * (b + d)) ** 0.5
            phi = (a * d - b * c) / denom if denom > 0 else 0
            ranked.append((name, ci.mean, phi))
            print(f"{name:>20} | {ci.mean:>10.1%} | "
                  f"[{ci.lower:>5.1%}, {ci.upper:>5.1%}] | {phi:>6.3f}")

        bottleneck = min(ranked, key=lambda x: x[1])
        most_discriminating = max(ranked, key=lambda x: abs(x[2]))
        print(f"\nBottleneck (lowest pass rate): {bottleneck[0]} ({bottleneck[1]:.1%})")
        print(f"Most discriminating (highest |phi|): {most_discriminating[0]} (phi={most_discriminating[2]:.3f})")

        # P(all_pass | bottleneck fails)
        bn_results = [r[bottleneck[0]] for r in per_run_results]
        fails = [not b for b in bn_results]
        p_all_given_fail = (
            sum(
                1 for i in range(n_seeds)
                if fails[i] and all_pass_results[i]
            ) / max(sum(fails), 1)
        )
        print(f"P(all_pass | {bottleneck[0]} fails) = {p_all_given_fail:.1%}")

        # VG all_pass rate는 0보다 높아야 함
        assert point_rate > 0.10, f"VG POM rate {point_rate:.0%} too low"

        # 병목 패턴이 all_pass와 유의미한 관계
        if most_discriminating[1] < 1.0 and most_discriminating[1] > 0.0:
            assert abs(most_discriminating[2]) > 0.1, \
                f"Top phi {most_discriminating[2]:.3f} too weak"

    def test_cross_scenario_pom_comparison(self):
        """Peter와 VG POM 병목 패턴 비교."""
        # 이미 Peter POM 알려짐: sword_drawn 50% phi=0.951
        # VG 분석: same pattern or different structure?
        n_seeds = 30
        scorecard = make_vangogh_scorecard()

        per_run_results = []
        for seed in range(n_seeds):
            mr = _run(seed)
            sr = mr.extract_agent_result("vangogh")
            per_run = {p.name: p.evaluate(sr) for p in scorecard}
            per_run_results.append(per_run)

        rates = {}
        for p in scorecard:
            rates[p.name] = sum(1 for r in per_run_results if r[p.name]) / n_seeds

        print(f"\n=== VG Pattern Rates (n={n_seeds}) ===")
        for name, rate in sorted(rates.items(), key=lambda x: x[1]):
            print(f"  {name}: {rate:.1%}")

        print("\nCross-scenario bottleneck comparison:")
        print("  Peter: sword_drawn (50%) - 행동 선택")
        vg_bottleneck = min(rates.items(), key=lambda x: x[1])
        print(f"  VG: {vg_bottleneck[0]} ({vg_bottleneck[1]:.1%})")

        # 둘 다 0% 또는 100%가 아닌 "중간 대역" 패턴이 병목
        assert 0 < vg_bottleneck[1] < 1, \
            f"VG bottleneck should be in (0,1), got {vg_bottleneck[1]:.1%}"
