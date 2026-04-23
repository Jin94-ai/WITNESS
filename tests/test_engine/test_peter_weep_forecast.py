"""Peter Weep Rate as Late-Arrest Forecast Signal.

Judas withdraw (r=-0.94): driver의 disengagement → 빠른 arrest
Peter weep (r=+0.796): reactor의 emotional expression → 늦은 arrest

"weeping" rate가 높으면 arrest 늦음: Peter가 감정적으로 계속 관여하며 상황이 지연됨.
이는 "Peter가 적극 반응 = 사태 지연, Judas 철회 = 사태 가속"의 인과 구조.
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


def _weep_rate_at(result, target_tick: int) -> float:
    actions = result.action_histories.get("peter", [])
    count = sum(
        1 for rec in actions
        if rec.chosen_action == "weep" and rec.tick < target_tick
    )
    return count / max(target_tick, 1)


def _actual(arrest_tick: int) -> str:
    return "early" if arrest_tick < 200 else "mid"


@pytest.mark.slow
class TestPeterWeepForecast:
    def test_peter_weep_rate_forecast(self):
        """Peter weep rate: positive correlate with arrest_tick → 높으면 arrest 늦음."""
        n_seeds = 30

        # For Peter, weep mostly happens post-arrest.
        # So we need to look at weep rate AFTER arrest to see if it correlates
        # with arrest timing. But that's retrospective...
        # Alternative: weep rate during mid-phase (tick 100-150) as forecast
        HOLDOUT = 150

        records = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            if at <= HOLDOUT:
                continue

            wr = _weep_rate_at(r, HOLDOUT)
            records.append((wr, _actual(at), at))

        if len(records) < 10:
            pytest.skip("not enough runs")

        # Find best threshold for 2-class prediction
        rates = sorted(set(r[0] for r in records))
        best_acc = 0.0
        best_th = 0.0
        best_direction = "positive"  # high rate -> early
        for th in rates:
            # Two directions to try
            # Direction 1: weep >= th → mid (late arrest)
            acc1 = sum(
                1 for wr, a, _ in records
                if ("mid" if wr >= th else "early") == a
            ) / len(records)
            # Direction 2: weep >= th → early
            acc2 = sum(
                1 for wr, a, _ in records
                if ("early" if wr >= th else "mid") == a
            ) / len(records)
            if max(acc1, acc2) > best_acc:
                best_acc = max(acc1, acc2)
                best_th = th
                best_direction = "positive" if acc1 > acc2 else "negative"

        ci = proportion_ci(int(best_acc * len(records)), len(records))
        print(f"\n=== Peter Weep Rate Forecast at tick {HOLDOUT} (n={len(records)}) ===")
        print(f"Best threshold: {best_th:.4f} per tick, direction: {best_direction}")
        print(f"Accuracy: {ci.mean:.1%} [{ci.lower:.1%}, {ci.upper:.1%}]")

        early_rates = [wr for wr, a, _ in records if a == "early"]
        mid_rates = [wr for wr, a, _ in records if a == "mid"]
        if early_rates and mid_rates:
            print(f"\nEarly mean: {statistics.mean(early_rates):.4f}")
            print(f"Mid mean:   {statistics.mean(mid_rates):.4f}")

        print("\nCompare: Judas withdraw rate@100 → 83% (behavioral early-warning)")
        print("Peter weep rate@150 → current result")

    def test_cross_agent_signal_comparison(self):
        """Judas withdraw vs Peter weep signals at same HOLDOUT=150."""
        n_seeds = 25
        HOLDOUT = 150

        # Collect both signals
        data = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            if at <= HOLDOUT:
                continue

            wr_judas = sum(
                1 for rec in r.action_histories.get("judas", [])
                if rec.chosen_action == "withdraw" and rec.tick < HOLDOUT
            ) / HOLDOUT
            wr_peter = _weep_rate_at(r, HOLDOUT)
            data.append((wr_judas, wr_peter, _actual(at)))

        if len(data) < 10:
            pytest.skip("not enough runs")

        # Each signal's best accuracy
        def best_accuracy(features: list[float], labels: list[str]) -> float:
            thresh_values = sorted(set(features))
            best = 0.0
            for th in thresh_values:
                for direction in ["pos", "neg"]:
                    if direction == "pos":
                        preds = ["early" if f >= th else "mid" for f in features]
                    else:
                        preds = ["mid" if f >= th else "early" for f in features]
                    correct = sum(1 for i, p in enumerate(preds) if p == labels[i])
                    best = max(best, correct / len(labels))
            return best

        labels = [a for _, _, a in data]
        judas_acc = best_accuracy([d[0] for d in data], labels)
        peter_acc = best_accuracy([d[1] for d in data], labels)

        # Combined (use both signals with OR/AND)
        # Simple: if judas_wr >= th1 OR peter_wr >= th2 → early
        combined_acc = 0.0
        for th1 in sorted(set(d[0] for d in data))[::2]:
            for th2 in sorted(set(d[1] for d in data))[::2]:
                # Judas positive (early), Peter negative (late)
                preds = [
                    "early" if (d[0] >= th1 and d[1] <= th2) else "mid"
                    for d in data
                ]
                correct = sum(1 for i, p in enumerate(preds) if p == labels[i])
                combined_acc = max(combined_acc, correct / len(labels))

        print(f"\n=== Cross-Agent Signal Accuracy (HOLDOUT={HOLDOUT}, n={len(data)}) ===")
        print(f"Judas withdraw rate alone: {judas_acc:.1%}")
        print(f"Peter weep rate alone:     {peter_acc:.1%}")
        print(f"Combined (AND rule):       {combined_acc:.1%}")
