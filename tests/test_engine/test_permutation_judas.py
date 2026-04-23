"""Permutation Test: Judas Counterfactual Significance.

기존 결과: Judas 제거 시 spontaneous rate 100% -> 0%, Cohen's d = -6.87.
이를 permutation test로 p-value 계산해 비모수 significance 검증.

방법:
- Group A: with Judas (arrest_tick 분포)
- Group B: without Judas (arrest_tick 분포, deadline/none)
- H0: 두 그룹이 같은 분포에서 나옴
- Permutation 1000회, 관측된 mean difference보다 극단 비율이 p-value
"""

import random
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
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
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int, include_judas: bool):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")

    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    states = [peter, caiaphas, crowd]

    if include_judas:
        from content.judas.domain_betrayal import BetrayalPsychologyState
        register_domain_type("betrayal_psychology", BetrayalPsychologyState)
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        profiles["judas"] = load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json")
        states.insert(1, judas)

    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=states,
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestPermutationJudas:
    def test_arrest_tick_permutation(self):
        """With-Judas vs Without-Judas arrest tick 평균 차이 permutation test."""
        n_seeds = 20

        with_judas = []
        without_judas = []

        for seed in range(n_seeds):
            r = _run(seed, include_judas=True)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            with_judas.append(arrests[0]["tick"] if arrests else 500)

            r_no = _run(seed, include_judas=False)
            arrests_no = [
                t for t in r_no.fired_triggers if t["trigger_id"] == "arrest_trigger"
            ]
            without_judas.append(arrests_no[0]["tick"] if arrests_no else 500)

        observed_diff = sum(without_judas) / len(without_judas) - sum(with_judas) / len(with_judas)

        # Permutation test
        combined = with_judas + without_judas
        rng = random.Random(42)
        n_perm = 1000
        count_extreme = 0

        for _ in range(n_perm):
            rng.shuffle(combined)
            group_a = combined[:n_seeds]
            group_b = combined[n_seeds:]
            perm_diff = sum(group_b) / len(group_b) - sum(group_a) / len(group_a)
            if abs(perm_diff) >= abs(observed_diff):
                count_extreme += 1

        p_value = count_extreme / n_perm

        print(f"\n=== Permutation Test: Judas Effect on Arrest Tick (n={n_seeds}) ===")
        print(f"With Judas mean: {sum(with_judas)/len(with_judas):.1f}")
        print(f"Without Judas mean: {sum(without_judas)/len(without_judas):.1f}")
        print(f"Observed difference: {observed_diff:.1f} tick")
        print(f"Permutation p-value (2-sided): {p_value:.4f}")
        print(f"Interpretation: {'significant' if p_value < 0.05 else 'not significant'} at alpha=0.05")

        # 큰 효과이므로 p << 0.05 기대
        assert p_value < 0.05, \
            f"Permutation p-value {p_value:.3f} >= 0.05 (Judas effect should be significant)"

    def test_spontaneous_rate_permutation(self):
        """Spontaneous (arrest < 400) rate 차이 permutation test."""
        n_seeds = 20

        def _spontaneous(r):
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            return 1 if arrests and arrests[0]["tick"] < 400 else 0

        with_judas = [_spontaneous(_run(s, True)) for s in range(n_seeds)]
        without_judas = [_spontaneous(_run(s, False)) for s in range(n_seeds)]

        observed_diff = sum(with_judas) / n_seeds - sum(without_judas) / n_seeds

        combined = with_judas + without_judas
        rng = random.Random(42)
        n_perm = 1000
        count_extreme = 0

        for _ in range(n_perm):
            rng.shuffle(combined)
            group_a = combined[:n_seeds]
            group_b = combined[n_seeds:]
            perm_diff = sum(group_a) / n_seeds - sum(group_b) / n_seeds
            if abs(perm_diff) >= abs(observed_diff):
                count_extreme += 1

        p_value = count_extreme / n_perm

        print(f"\n=== Permutation Test: Spontaneous Rate (n={n_seeds} each) ===")
        print(f"With Judas: {sum(with_judas)}/{n_seeds} ({sum(with_judas)/n_seeds:.0%})")
        print(f"Without Judas: {sum(without_judas)}/{n_seeds} ({sum(without_judas)/n_seeds:.0%})")
        print(f"Observed rate difference: {observed_diff:.2f}")
        print(f"Permutation p-value: {p_value:.4f}")

        # 100% vs 0% 차이는 극단적이라 p=0 (or 1/n_perm)
        assert p_value < 0.01, \
            f"Permutation p-value {p_value:.3f} unexpectedly high"
