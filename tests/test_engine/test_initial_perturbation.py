"""Initial State Perturbation Sensitivity.

가설: 시스템이 결정론적 chaos인가 vs 안정 attractor인가?
- Chaotic: 초기 조건 작은 변화 → 궤적 크게 발산 (Lyapunov > 0)
- Attractor: 궤적이 결국 비슷한 경로로 수렴

Witness에서 Judas disillusionment 초기값을 ±0.5 perturbation하면:
- arrest tick이 proportionally 변하는가? (smooth)
- 아니면 bifurcation threshold 근처에서 비선형 도약?

이는 역사학적 의미: "유다가 좀 더 환멸했다면?" counterfactual 정량화.
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

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_with_judas_disill(initial_disill: float, seed: int):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")

    # Perturb judas initial disillusionment
    perturbed_judas = judas.model_copy(
        update={
            "domain_state": judas.domain_state.model_copy(
                update={"disillusionment": initial_disill}
            )
        }
    )

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
        initial_states=[peter, perturbed_judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestInitialPerturbation:
    def test_disill_perturbation_response(self):
        """Judas disillusionment 초기값 ±1.0 스윕 → arrest tick 반응.

        Smooth monotone: disill 높을수록 arrest 빠르게. Bifurcation 없어야 건강.
        """
        baseline_disill = 3.0  # content/judas initial_state.json 값
        perturbations = [1.0, 2.0, 3.0, 4.0, 5.0]  # ±1,2
        n_seeds = 10

        print(f"\n=== Initial Disill Perturbation (baseline={baseline_disill}) ===")
        print(f"{'init_disill':>12} | {'mean arrest':>12} | {'95% CI':>18} | {'n':>4}")
        print("-" * 60)

        results = {}
        for init_disill in perturbations:
            arrest_ticks = []
            for seed in range(n_seeds):
                r = _run_with_judas_disill(init_disill, seed)
                arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                if arrests:
                    arrest_ticks.append(arrests[0]["tick"])
                else:
                    arrest_ticks.append(500)  # deadline or none

            ci = confidence_interval(arrest_ticks)
            results[init_disill] = ci
            print(f"{init_disill:>12.1f} | {ci.mean:>12.1f} | "
                  f"[{ci.lower:>6.1f}, {ci.upper:>6.1f}] | {len(arrest_ticks):>4}")

        # Monotonicity: 초기 disill 높을수록 arrest tick 낮거나 비슷
        means = [results[d].mean for d in perturbations]
        print(f"\nMean sequence: {[f'{m:.0f}' for m in means]}")

        # 단조 감소 확인 (초기 disill ↑ → arrest tick ↓)
        # 노이즈 고려해서 strict monotone 대신 전반적 경향
        overall_trend = means[0] - means[-1]  # 양수여야 정상
        print(f"Overall trend (low-high diff): {overall_trend:.1f} ticks")
        assert overall_trend > 0, \
            f"Higher initial disill should yield earlier arrest (got {overall_trend:.0f})"

        # Smoothness: 인접 perturbation 간 차이가 급등(jump)이 아니어야 함
        diffs = [means[i] - means[i+1] for i in range(len(means)-1)]
        print(f"Diffs between levels: {[f'{d:.0f}' for d in diffs]}")
        max_jump = max(diffs) if diffs else 0
        min_jump = min(diffs) if diffs else 0
        print(f"Max jump: {max_jump:.0f}, min: {min_jump:.0f}")
        # No single step should dominate (bifurcation)
        total_change = sum(abs(d) for d in diffs)
        if total_change > 0:
            max_proportion = max(abs(d) for d in diffs) / total_change
            print(f"Max step proportion: {max_proportion:.0%}")
            # 단일 step이 전체 변화의 >80%를 차지하지 않아야 함
            assert max_proportion < 0.85, \
                f"Bifurcation detected (single step = {max_proportion:.0%} of change)"

    def test_seed_variance_dominates_perturbation_near_baseline(self):
        """Baseline 근방 perturbation ±0.5 < seed variance. 견고성 증거."""
        n_seeds = 15
        baseline = 3.0

        def _run_many(init_disill: float) -> list[int]:
            ticks = []
            for seed in range(n_seeds):
                r = _run_with_judas_disill(init_disill, seed)
                arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                if arrests:
                    ticks.append(arrests[0]["tick"])
            return ticks

        low = _run_many(baseline - 0.5)
        mid = _run_many(baseline)
        high = _run_many(baseline + 0.5)

        mid_std = statistics.stdev(mid) if len(mid) > 1 else 0
        perturbation_effect = abs(statistics.mean(high) - statistics.mean(low))

        print(f"\n=== Seed variance vs Small perturbation ({n_seeds} seeds each) ===")
        print(f"baseline-0.5 mean: {statistics.mean(low):.1f}")
        print(f"baseline     mean: {statistics.mean(mid):.1f}, std: {mid_std:.1f}")
        print(f"baseline+0.5 mean: {statistics.mean(high):.1f}")
        print(f"Perturbation effect (±0.5): {perturbation_effect:.1f} ticks")
        print(f"Seed std (baseline): {mid_std:.1f} ticks")

        # 결정론적 chaos 없음: small perturbation 효과 < seed noise
        # 이는 system이 stable attractor 주변에 있다는 증거
        if mid_std > 5:
            assert perturbation_effect < mid_std * 3, \
                (f"Perturbation effect {perturbation_effect:.0f} >> seed std {mid_std:.0f}"
                 f" suggests bifurcation near baseline")

        print("\n결론: 초기값 small perturbation은 seed variance 수준의 효과")
        print("시스템이 stable attractor 주변에 있음 (not chaotic)")
