"""2D Parameter Space Map.

유다의 disillusionment x greed 조합이 체포 시점에 미치는 영향을 매핑.
프로젝트의 근본 목적: "파라미터 공간 지형도를 통해 분기점을 발견한다."
"""

import statistics
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
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


def _run_with_params(disill: float, greed: float, n_seeds: int = 3) -> dict:
    """유다의 disillusionment/greed를 오버라이드하고 결과를 수집."""
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

    judas = set_nested_value(judas, "domain_state.disillusionment", disill)
    judas = set_nested_value(judas, "domain_state.greed", greed)

    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )

    ticks = []
    spontaneous = 0
    for seed in range(n_seeds):
        r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
        arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        if arrests:
            tick = arrests[0]["tick"]
            ticks.append(tick)
            if tick < 400:
                spontaneous += 1

    return {
        "mean_tick": statistics.mean(ticks) if ticks else 500,
        "spontaneous_rate": spontaneous / n_seeds,
        "ticks": ticks,
    }


@pytest.mark.slow
class TestParamSpaceMap:
    def test_2d_sweep(self):
        """disillusionment x greed 2D 스윕."""
        disill_values = [0.0, 3.0, 5.0, 7.0, 10.0]
        greed_values = [0.0, 3.0, 5.0, 7.0, 10.0]

        print("\n=== 2D Parameter Space: disill x greed -> mean arrest tick ===")
        print(f"{'':>8}", end="")
        for g in greed_values:
            print(f" g={g:<4.0f}", end="")
        print()
        print("-" * 45)

        results = {}
        for d in disill_values:
            print(f"d={d:<4.0f}|", end="")
            for g in greed_values:
                r = _run_with_params(d, g, n_seeds=3)
                results[(d, g)] = r
                tick = r["mean_tick"]
                sp = r["spontaneous_rate"]
                marker = "*" if sp >= 0.5 else " "
                print(f" {tick:>4.0f}{marker}", end="")
            print()

        print()
        print("* = spontaneous rate >= 50%")

        # 핵심 검증: 높은 disill + greed -> 낮은 arrest tick
        low_both = results[(0.0, 0.0)]["mean_tick"]
        high_both = results[(10.0, 10.0)]["mean_tick"]
        assert high_both < low_both, "High disill+greed should yield earlier arrest"

        # 분기점 식별: disill >= 5, greed >= 5인 영역에서 spontaneous > 0
        high_region = [
            results[(d, g)]["spontaneous_rate"]
            for d in [5.0, 7.0, 10.0] for g in [5.0, 7.0, 10.0]
        ]
        assert statistics.mean(high_region) > 0.5, "High parameter region should be mostly spontaneous"
