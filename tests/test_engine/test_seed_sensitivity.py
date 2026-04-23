"""Seed Sensitivity Quantification.

ChatGPT 피드백: "seed sensitivity 정량화"

동일 파라미터 + 다른 seed -> arrest tick 분산 측정.
이것은 "stochastic uncertainty" (같은 조건에서 결과 변동)를 보여준다.

vs "parametric uncertainty" (다른 파라미터에서 결과 변동) -- 이전 sensitivity 테스트.

결과 해석:
- seed sensitivity가 작으면: 시스템이 결정론적에 가까움 (stochastic이 약함)
- seed sensitivity가 크면: noise가 실질적 역할 (더 풍부한 ensemble 필요)
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


def _run(seed: int, state_noise_scale: float = 0.05):
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
        triggers=triggers, state_noise_scale=state_noise_scale,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestSeedSensitivity:
    def test_arrest_tick_variance(self):
        """동일 파라미터 + 30 seeds -> arrest tick의 std/CV."""
        n_seeds = 30
        ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests and arrests[0]["tick"] < 400:
                ticks.append(arrests[0]["tick"])

        mean = statistics.mean(ticks)
        std = statistics.stdev(ticks)
        cv = std / mean  # coefficient of variation

        ci = confidence_interval(ticks)

        print(f"\n=== Seed Sensitivity (n={len(ticks)}/30) ===")
        print(f"Arrest tick mean: {mean:.1f}")
        print(f"Arrest tick std:  {std:.1f}")
        print(f"Coefficient of variation (CV): {cv:.2%}")
        print(f"95% CI: [{ci.lower:.1f}, {ci.upper:.1f}]")
        print(f"Range: [{min(ticks)}, {max(ticks)}]")

        # CV < 50%면 "결정론적에 가까움"
        # CV 50-100%면 "적당한 stochasticity"
        # CV > 100%면 "매우 stochastic"
        if cv < 0.2:
            print("Interpretation: highly deterministic")
        elif cv < 0.5:
            print("Interpretation: moderately stochastic")
        else:
            print("Interpretation: highly stochastic")

        # 최소 합리적 variation (deterministic이면 안 됨)
        assert cv > 0.05, "System should not be fully deterministic"

    def test_noise_scale_effect(self):
        """state_noise_scale 변화 -> arrest tick 분산 변화.

        noise가 커지면 분산이 증가해야 하는지 확인.
        """
        scales = [0.0, 0.05, 0.1, 0.2]
        n_seeds = 15

        print("\n=== Noise Scale Effect ===")
        print(f"{'noise_scale':>12} | {'std':>6} | {'range':>12}")
        print("-" * 40)

        for scale in scales:
            ticks = []
            for seed in range(n_seeds):
                r = _run(seed, state_noise_scale=scale)
                arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                if arrests and arrests[0]["tick"] < 400:
                    ticks.append(arrests[0]["tick"])

            if len(ticks) > 1:
                std = statistics.stdev(ticks)
                print(f"{scale:>12.2f} | {std:>5.1f} | [{min(ticks)}, {max(ticks)}]")
            else:
                print(f"{scale:>12.2f} | (n={len(ticks)})")

        # 이 test는 정보만 출력하는 용도 (assert 없음 -- 관측만)

    def test_deterministic_noise_zero(self):
        """state_noise_scale=0이면 더 결정론적.

        하지만 scheduler의 agent activation order가 여전히 random이므로
        완전 결정론은 아님.
        """
        n_seeds = 10
        ticks_zero_noise = []
        ticks_with_noise = []

        for seed in range(n_seeds):
            r0 = _run(seed, state_noise_scale=0.0)
            rn = _run(seed, state_noise_scale=0.1)

            a0 = [t for t in r0.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            an = [t for t in rn.fired_triggers if t["trigger_id"] == "arrest_trigger"]

            if a0 and a0[0]["tick"] < 400:
                ticks_zero_noise.append(a0[0]["tick"])
            if an and an[0]["tick"] < 400:
                ticks_with_noise.append(an[0]["tick"])

        if len(ticks_zero_noise) > 1 and len(ticks_with_noise) > 1:
            std_zero = statistics.stdev(ticks_zero_noise)
            std_noise = statistics.stdev(ticks_with_noise)
            print("\n=== Deterministic test ===")
            print(f"noise=0.0 std: {std_zero:.1f}")
            print(f"noise=0.1 std: {std_noise:.1f}")
            # noise가 없어도 scheduler 랜덤성 때문에 std > 0일 수 있음
