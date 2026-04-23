"""Multi-Horizon Withdraw Rate Analysis.

Withdraw forecast at tick 100 → 83% accuracy.
얼마나 이른 tick까지 withdraw rate이 예측력을 유지하는가?

tick 50, 75, 100, 125에서 rate 측정 → 각각의 threshold 찾기 → accuracy.
"""

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
from engine.simulation.statistics import proportion_ci
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

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


def _withdraw_rate_at(result, target_tick: int) -> float:
    judas_actions = result.action_histories.get("judas", [])
    count = sum(
        1 for rec in judas_actions
        if rec.chosen_action == "withdraw" and rec.tick < target_tick
    )
    return count / max(target_tick, 1)


def _actual_early_vs_mid(arrest_tick: int) -> str:
    return "early" if arrest_tick < 200 else "mid"


@pytest.mark.slow
class TestMultiHorizonWithdraw:
    def test_withdraw_forecast_multi_horizon(self):
        """여러 horizon에서 withdraw rate 예측력."""
        n_seeds = 30
        horizons = [50, 75, 100, 125, 150]

        # Collect all runs data once
        all_runs = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            if at < 100:  # very early, exclude from 2-class
                continue
            actual = _actual_early_vs_mid(at)

            rates_at = {h: _withdraw_rate_at(r, h) for h in horizons if at > h}
            all_runs.append({"actual": actual, "rates": rates_at, "arrest_tick": at})

        print(f"\n=== Withdraw Rate Forecast Multi-Horizon (n={len(all_runs)}) ===")
        print(f"{'horizon':>10} | {'best thresh':>12} | {'accuracy':>10} | {'CI':>18} | {'n_valid':>8}")
        print("-" * 70)

        for h in horizons:
            valid = [r for r in all_runs if h in r["rates"]]
            if len(valid) < 5:
                continue
            rates = sorted(set(r["rates"][h] for r in valid))
            best_acc = 0.0
            best_th = 0.0
            for th in rates:
                correct = sum(
                    1 for r in valid
                    if ("early" if r["rates"][h] >= th else "mid") == r["actual"]
                )
                acc = correct / len(valid)
                if acc > best_acc:
                    best_acc = acc
                    best_th = th
            ci = proportion_ci(int(best_acc * len(valid)), len(valid))
            print(f"{h:>10} | {best_th:>12.4f} | {ci.mean:>9.1%} | "
                  f"[{ci.lower:>4.1%}, {ci.upper:>4.1%}] | {len(valid):>8}")

        print("\nReference:")
        print("  Witness state-based (disill@200): 86%")
        print("  Withdraw @100: 83% (from previous test)")
        print("  Question: 더 이른 horizon에서도 예측 가능한가?")
