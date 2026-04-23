"""Threshold Response Sweep + Large-scale Arrest Classification.

LLM 피드백:
- Gemini: "disillusionment 스윕 시 체포 확률이 선형인지 임계점형인지 확인"
- ChatGPT: "spontaneous vs deadline-assisted vs no-arrest 비율을 대규모(500+)로 분리"

NOTE (4차 LLM 리뷰 교정): 전반 disill 궤적은 linear (R²=0.998).
이 테스트는 "arrest 확률/시점의 threshold response"를 측정 —
"phase transition dynamics" 용어는 과장이라 본 리뷰에서 제거.
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

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


def _load_all():
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


def _classify_arrests(config, profiles, n_seeds):
    """체포를 spontaneous/deadline/no_arrest로 분류."""
    spontaneous = 0
    deadline = 0
    no_arrest = 0
    sp_ticks = []

    for seed in range(n_seeds):
        r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
        arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        if not arrests:
            no_arrest += 1
        elif arrests[0]["tick"] >= 400:
            deadline += 1
        else:
            spontaneous += 1
            sp_ticks.append(arrests[0]["tick"])

    return spontaneous, deadline, no_arrest, sp_ticks


@pytest.mark.slow
class TestPhaseTransition:
    """disillusionment 0~10 스윕으로 체포 확률/시점의 상전이를 관측한다."""

    def test_disillusionment_sweep(self):
        """disillusionment 스윕: 체포 확률 곡선이 S자 형태인지 확인."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _load_all()

        n_per_value = 10
        values = [0.0, 2.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        results = []

        print("\n=== Threshold Response: disillusionment sweep ===")
        print(f"{'disill':>6} | {'spont':>5} | {'dead':>4} | {'none':>4} | {'mean_tick':>9}")
        print("-" * 45)

        for val in values:
            j = set_nested_value(judas, "domain_state.disillusionment", val)
            config = SimulationConfig(
                max_tick=500, initial_state=peter,
                initial_states=[peter, j, caiaphas],
                hazard_events=hazards, interventions=interventions,
                triggers=triggers, state_noise_scale=0.05,
            )
            sp, dl, na, sp_ticks = _classify_arrests(config, profiles, n_per_value)
            mean_t = statistics.mean(sp_ticks) if sp_ticks else 400 if dl > 0 else 500
            results.append((val, sp, dl, na, mean_t))
            print(f"{val:>6.1f} | {sp:>5} | {dl:>4} | {na:>4} | {mean_t:>9.0f}")

        # 핵심 검증: 낮은 환멸 -> deadline 의존, 높은 환멸 -> spontaneous
        low_sp = sum(r[1] for r in results if r[0] <= 2.0)
        high_sp = sum(r[1] for r in results if r[0] >= 8.0)
        print(f"\nLow disill (0-2) spontaneous: {low_sp}")
        print(f"High disill (8-10) spontaneous: {high_sp}")

        # 높은 환멸에서 spontaneous가 더 많아야 함
        assert high_sp > low_sp, "Higher disillusionment should yield more spontaneous arrests"

        # mean tick이 단조감소하는지 (환멸↑ -> 체포 빨라짐)
        mean_ticks = [r[4] for r in results]
        first_half_mean = statistics.mean(mean_ticks[:4])
        second_half_mean = statistics.mean(mean_ticks[5:])
        assert second_half_mean < first_half_mean, "Arrest should come earlier with higher disillusionment"


@pytest.mark.slow
class TestLargeScaleClassification:
    """대규모(50+ runs) 체포 분류."""

    def test_50_runs_classification(self):
        """50 runs에서 spontaneous vs deadline 비율."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _load_all()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        sp, dl, na, sp_ticks = _classify_arrests(config, profiles, n_seeds=50)

        sp_rate = sp / 50
        dl_rate = dl / 50
        mean_t = statistics.mean(sp_ticks) if sp_ticks else 0
        std_t = statistics.stdev(sp_ticks) if len(sp_ticks) > 1 else 0

        print("\n=== Large-scale (50 runs) ===")
        print(f"Spontaneous: {sp}/50 ({sp_rate:.0%})")
        print(f"Deadline:    {dl}/50 ({dl_rate:.0%})")
        print(f"No arrest:   {na}/50")
        if sp_ticks:
            print(f"Mean tick:   {mean_t:.0f} +/- {std_t:.0f}")
            print(f"Range:       {min(sp_ticks)} - {max(sp_ticks)}")

        # spontaneous가 대부분이어야 함
        assert sp_rate >= 0.8, f"Spontaneous rate {sp_rate:.0%} should be >= 80%"
