"""Disillusionment × Greed Interaction Effect.

개별 파라미터 sensitivity (disill 180 tick vs greed 23 tick) 확인 후,
두 파라미터의 interaction을 분석:
- high disill + high greed: synergy 있는가?
- high disill 상태에서 greed 추가 상승이 효과 있는가?

2x2 factorial design:
- (low disill, low greed) vs (low disill, high greed)
- (high disill, low greed) vs (high disill, high greed)

Main effect of disill = (high_d - low_d) 평균
Main effect of greed = (high_g - low_g) 평균
Interaction = (high_d, high_g) - (high_d, low_g) - ((low_d, high_g) - (low_d, low_g))
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
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_with_judas(disill: float, greed: float, seed: int):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")

    new_ds = judas.domain_state.model_copy(update={"disillusionment": disill, "greed": greed})
    judas = judas.model_copy(update={"domain_state": new_ds})

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
    r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
    arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
    return arrests[0]["tick"] if arrests else 500


@pytest.mark.slow
class TestDisillGreedInteraction:
    def test_2x2_factorial(self):
        """2x2 factorial: disill {low=2, high=4} × greed {low=3, high=5}."""
        n_seeds = 5
        low_d, high_d = 2.0, 4.0
        low_g, high_g = 3.0, 5.0

        cells: dict[tuple[float, float], list[int]] = {
            (low_d, low_g): [],
            (low_d, high_g): [],
            (high_d, low_g): [],
            (high_d, high_g): [],
        }

        for d, g in cells:
            for seed in range(n_seeds):
                ticks = _run_with_judas(d, g, seed)
                cells[(d, g)].append(ticks)

        means = {k: statistics.mean(v) for k, v in cells.items()}

        print(f"\n=== 2x2 Factorial: Disill × Greed (n={n_seeds}) ===")
        print(f"{'':>15} | {'greed=low ('+str(low_g)+')':>12} | {'greed=high ('+str(high_g)+')':>13}")
        print("-" * 50)
        print(
            f"{'disill=low  ('+str(low_d)+')':>15} | "
            f"{means[(low_d, low_g)]:>11.1f} | {means[(low_d, high_g)]:>12.1f}"
        )
        print(
            f"{'disill=high ('+str(high_d)+')':>15} | "
            f"{means[(high_d, low_g)]:>11.1f} | {means[(high_d, high_g)]:>12.1f}"
        )

        # Main effects
        main_disill = (
            (means[(high_d, low_g)] + means[(high_d, high_g)]) / 2
            - (means[(low_d, low_g)] + means[(low_d, high_g)]) / 2
        )
        main_greed = (
            (means[(low_d, high_g)] + means[(high_d, high_g)]) / 2
            - (means[(low_d, low_g)] + means[(high_d, low_g)]) / 2
        )
        # Interaction = (high_d, high_g) - (high_d, low_g) - ((low_d, high_g) - (low_d, low_g))
        interaction = (
            (means[(high_d, high_g)] - means[(high_d, low_g)])
            - (means[(low_d, high_g)] - means[(low_d, low_g)])
        )

        print(f"\nMain effect of disill: {main_disill:+.1f} ticks (higher disill → arrest)")
        print(f"Main effect of greed:  {main_greed:+.1f} ticks (higher greed → arrest)")
        print(f"Interaction (disill × greed): {interaction:+.1f} ticks")

        # 검증: disill main effect가 가장 큼
        assert abs(main_disill) > abs(main_greed), \
            f"Disill main effect {main_disill:.1f} should dominate greed {main_greed:.1f}"

        # disill main effect는 negative (높을수록 빠름)
        assert main_disill < 0, \
            f"Disill main effect {main_disill:.1f} should be negative"

        # Interaction magnitude (얼마나 두 변수가 서로 영향 주는가)
        ratio = abs(interaction) / abs(main_disill) if abs(main_disill) > 0 else 0
        print(f"\nInteraction magnitude / disill main: {ratio:.2f}")
        if ratio < 0.3:
            print("-> Weak interaction, mostly additive (두 변수 독립적)")
        else:
            print("-> Notable interaction (두 변수 상호작용)")
