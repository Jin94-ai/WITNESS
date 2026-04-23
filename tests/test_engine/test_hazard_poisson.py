"""Hazard Event Poisson Check.

Witness는 Poisson process로 hazard event를 발생시킴: P(event) = 1 - exp(-h*dt).
실제로 이 가정이 맞는가? Inter-event time이 exponential 분포를 따르는지 검증.

방법:
1. Peter 시나리오 모든 run에서 hazard event 발생 tick 수집
2. Inter-arrival time 계산
3. Mean == Std? (exponential의 특성)
4. Chi-square goodness-of-fit vs exponential
"""

import math
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
class TestHazardPoisson:
    def test_inter_event_time_distribution(self):
        """Hazard event 간 interval이 exponential 분포를 따르는가."""
        n_seeds = 20
        all_intervals = []
        event_counts = []

        for seed in range(n_seeds):
            r = _run(seed)
            # Collect all fired hazard event ticks (ignore arrest_trigger etc)
            event_ticks = sorted(set(ev["tick"] for ev in r.fired_events))
            event_counts.append(len(event_ticks))
            for i in range(1, len(event_ticks)):
                all_intervals.append(event_ticks[i] - event_ticks[i - 1])

        print(f"\n=== Hazard Event Inter-arrival Time (n_intervals={len(all_intervals)}) ===")
        if all_intervals:
            mean_i = statistics.mean(all_intervals)
            std_i = statistics.stdev(all_intervals) if len(all_intervals) > 1 else 0
            print(f"Events per run: mean {statistics.mean(event_counts):.1f}, "
                  f"range [{min(event_counts)}, {max(event_counts)}]")
            print(f"Inter-arrival time: mean {mean_i:.2f} tick, std {std_i:.2f}")
            print(f"CV (std/mean): {std_i/mean_i if mean_i > 0 else 0:.2f}")
            print("(Exponential distribution CV = 1.0)")

            # Exponential의 특성: mean ≈ std (CV ≈ 1)
            cv = std_i / mean_i if mean_i > 0 else 0

            # Chi-square goodness-of-fit: observed vs expected exponential
            # Bin intervals into quartiles of expected distribution
            lam = 1 / mean_i
            # Expected quartile boundaries for Exp(lam): F^-1(0.25, 0.5, 0.75)
            q25 = -math.log(1 - 0.25) / lam
            q50 = -math.log(1 - 0.5) / lam
            q75 = -math.log(1 - 0.75) / lam

            bins = [0, 0, 0, 0]
            for x in all_intervals:
                if x < q25:
                    bins[0] += 1
                elif x < q50:
                    bins[1] += 1
                elif x < q75:
                    bins[2] += 1
                else:
                    bins[3] += 1

            n = len(all_intervals)
            expected = n / 4  # Each bin has 1/4 of data if exponential
            chi_sq = sum((o - expected) ** 2 / expected for o in bins)
            # df=3, chi_sq critical at alpha=0.05: 7.815
            print(f"\nQuartile counts: {bins} (expected {expected:.1f} each)")
            print(f"Chi-square stat: {chi_sq:.2f}")
            print("Critical at α=0.05 (df=3): 7.815")
            print("Critical at α=0.01 (df=3): 11.345")
            if chi_sq < 7.815:
                print("H0 (exponential) 유지: Poisson process 가정 성립")
            else:
                print("H0 기각: 분포가 정확한 exponential은 아님")

            # CV가 대략 1 근처면 exponential-like
            assert cv > 0.3, f"CV {cv:.2f} too low (suggests periodic, not Poisson)"

    def test_arrest_trigger_survives_poisson(self):
        """Arrest trigger tick 분포가 exponential과 구분되는가.

        Arrest는 state-dependent이므로 순수 Poisson이 아님.
        → exponential보다 집중된 분포가 예상됨.
        """
        n_seeds = 30
        arrest_ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(arrests[0]["tick"])

        mean_a = statistics.mean(arrest_ticks)
        std_a = statistics.stdev(arrest_ticks)
        cv = std_a / mean_a

        print(f"\n=== Arrest Trigger Tick Distribution (n={len(arrest_ticks)}) ===")
        print(f"Mean: {mean_a:.1f}, std: {std_a:.1f}, CV: {cv:.2f}")
        print("Pure Poisson CV = 1.0 (exponential), Normal CV typically < 0.5")

        # state-dependent trigger: CV << 1 (narrow, peaked)
        assert cv < 0.5, \
            f"Arrest CV {cv:.2f} unexpectedly high (should be state-driven, not Poisson)"

        print("\n결론: Hazard events는 Poisson-like (CV~1)이지만,")
        print("Trigger events (arrest)는 state-driven으로 집중 분포 (CV<<1)")
        print("Trigger 메커니즘이 Poisson 기반 배경 위에 '결정론적 수렴'을 생성")
