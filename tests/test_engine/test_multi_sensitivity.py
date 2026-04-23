"""다중 에이전트 민감도 분석 테스트.

유다의 초기 파라미터가 체포 tick에 미치는 영향을 측정한다.
"""

import statistics
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.state import set_nested_value
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
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


def _base_config():
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
    }
    return peter, judas, caiaphas, triggers, hazards, interventions, profiles


def _run_with_judas_override(
    param_path: str, value: float, n_seeds: int = 5,
) -> list[int]:
    """유다의 파라미터를 오버라이드하고 체포 tick을 수집한다."""
    peter, judas, caiaphas, triggers, hazards, interventions, profiles = _base_config()
    judas = set_nested_value(judas, param_path, value)

    config = SimulationConfig(
        max_tick=500,
        initial_state=peter,
        initial_states=[peter, judas, caiaphas],
        hazard_events=hazards,
        interventions=interventions,
        triggers=triggers,
        state_noise_scale=0.05,
    )

    arrest_ticks = []
    for seed in range(n_seeds):
        result = SimulationWorld(
            config, _engine(), behavior_profiles=profiles,
        ).run(seed=seed)
        arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        if arrests:
            arrest_ticks.append(arrests[0]["tick"])
    return arrest_ticks


class TestMultiAgentSensitivity:
    def test_disillusionment_affects_arrest(self):
        """유다의 초기 환멸이 높을수록 체포가 빨라진다."""
        low_ticks = _run_with_judas_override("domain_state.disillusionment", 1.0)
        high_ticks = _run_with_judas_override("domain_state.disillusionment", 7.0)

        low_mean = statistics.mean(low_ticks) if low_ticks else 500
        high_mean = statistics.mean(high_ticks) if high_ticks else 500

        print("\nDisillusionment sensitivity:")
        print(f"  Low (1.0): mean arrest tick = {low_mean:.0f} ({low_ticks})")
        print(f"  High (7.0): mean arrest tick = {high_mean:.0f} ({high_ticks})")

        # 높은 환멸 -> 더 빠른 체포
        assert high_mean < low_mean, "Higher disillusionment should lead to earlier arrest"

    def test_greed_affects_arrest(self):
        """유다의 초기 탐욕이 높을수록 체포가 빨라진다."""
        low_ticks = _run_with_judas_override("domain_state.greed", 1.0)
        high_ticks = _run_with_judas_override("domain_state.greed", 7.0)

        low_mean = statistics.mean(low_ticks) if low_ticks else 500
        high_mean = statistics.mean(high_ticks) if high_ticks else 500

        print("\nGreed sensitivity:")
        print(f"  Low (1.0): mean arrest tick = {low_mean:.0f} ({low_ticks})")
        print(f"  High (7.0): mean arrest tick = {high_mean:.0f} ({high_ticks})")

        # 높은 탐욕 -> 더 빠른 체포 (betray 전제조건: greed >= 5.0)
        assert high_mean < low_mean, "Higher greed should lead to earlier arrest"

    def test_caiaphas_threat_affects_arrest(self):
        """가야바의 초기 위협 평가가 높을수록 체포가 빨라진다."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _base_config()

        results_low = []
        results_high = []

        for seed in range(5):
            # Low threat
            c_low = set_nested_value(caiaphas, "domain_state.threat_assessment", 1.0)
            config = SimulationConfig(
                max_tick=500, initial_state=peter,
                initial_states=[peter, judas, c_low],
                hazard_events=hazards, interventions=interventions,
                triggers=triggers, state_noise_scale=0.05,
            )
            r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                results_low.append(arrests[0]["tick"])

            # High threat
            c_high = set_nested_value(caiaphas, "domain_state.threat_assessment", 8.0)
            config2 = SimulationConfig(
                max_tick=500, initial_state=peter,
                initial_states=[peter, judas, c_high],
                hazard_events=hazards, interventions=interventions,
                triggers=triggers, state_noise_scale=0.05,
            )
            r2 = SimulationWorld(config2, _engine(), behavior_profiles=profiles).run(seed=seed)
            arrests2 = [t for t in r2.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests2:
                results_high.append(arrests2[0]["tick"])

        low_mean = statistics.mean(results_low) if results_low else 500
        high_mean = statistics.mean(results_high) if results_high else 500

        print("\nCaiaphas threat sensitivity:")
        print(f"  Low (1.0): mean arrest tick = {low_mean:.0f}")
        print(f"  High (8.0): mean arrest tick = {high_mean:.0f}")

        # 높은 위협 평가 -> 더 빠른 체포 (arrest_trigger 조건: threat >= 7)
        assert high_mean <= low_mean
