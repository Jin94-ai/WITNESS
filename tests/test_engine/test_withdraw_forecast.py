"""Judas Withdraw Rate as Early-Warning Forecast Signal.

이전 발견: Judas withdraw rate vs arrest_tick r=-0.942.
이를 forecast rule로 구체화: tick 100에서 withdraw 비율만으로 arrest 카테고리 예측.

비교:
- State-based forecast (disill@200): 86% accuracy (n=100)
- Action-rate forecast (withdraw rate@100): ?

목표: behavior-only forecast도 state-based와 비슷한 정확도 달성 가능한가.
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


def _actual_category(arrest_tick: int | None) -> str:
    if arrest_tick is None:
        return "deadline_or_none"
    if arrest_tick < 100:
        return "very_early"
    if arrest_tick < 200:
        return "early"
    if arrest_tick < 300:
        return "mid"
    if arrest_tick < 400:
        return "late"
    return "deadline_or_none"


def _withdraw_rate_at(result, target_tick: int) -> float:
    """Judas withdraw count up to target_tick / target_tick."""
    judas_actions = result.action_histories.get("judas", [])
    count = sum(
        1 for rec in judas_actions
        if rec.chosen_action == "withdraw" and rec.tick < target_tick
    )
    return count / max(target_tick, 1)


@pytest.mark.slow
class TestWithdrawForecast:
    def test_withdraw_rate_100_forecast(self):
        """Tick 100 기준 withdraw rate만으로 arrest 카테고리 예측."""
        n_seeds = 30
        HOLDOUT = 100

        # Collect (withdraw_rate, actual_category)
        records = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            at = arrests[0]["tick"] if arrests else None
            if at is not None and at <= HOLDOUT:
                continue
            actual = _actual_category(at)
            wr = _withdraw_rate_at(r, HOLDOUT)
            records.append((wr, actual, at))

        # Empirical threshold fitting: find rate threshold that splits early vs mid best
        rates = sorted(set(r[0] for r in records))
        best_accuracy = 0.0
        best_thresh = 0.0
        for th in rates:
            correct = 0
            for wr, actual, _ in records:
                # Rule: high rate -> early, low rate -> mid
                pred = "early" if wr >= th else "mid"
                if pred == actual:
                    correct += 1
            acc = correct / len(records)
            if acc > best_accuracy:
                best_accuracy = acc
                best_thresh = th

        ci = proportion_ci(int(best_accuracy * len(records)), len(records))
        print(f"\n=== Withdraw Rate Forecast at tick {HOLDOUT} (n={len(records)}) ===")
        print(f"Best threshold: {best_thresh:.4f} per tick")
        print(f"Best accuracy: {ci.mean:.1%} [{ci.lower:.1%}, {ci.upper:.1%}]")
        print("Reference: state-based (disill@200) 86% [77.9%, 91.5%] (n=100)")
        print("(Note: withdraw only distinguishes early vs mid, 2-class)")

        # Show distribution
        early_rates = [wr for wr, a, _ in records if a == "early"]
        mid_rates = [wr for wr, a, _ in records if a == "mid"]
        if early_rates and mid_rates:
            import statistics
            print(f"\nEarly (actual): {len(early_rates)} runs, "
                  f"mean withdraw rate {statistics.mean(early_rates):.4f}")
            print(f"Mid   (actual): {len(mid_rates)} runs, "
                  f"mean withdraw rate {statistics.mean(mid_rates):.4f}")

        # 최소 검증: 2-class 분류기 대비 random baseline(50%)보다 유의미
        assert ci.mean > 0.55, \
            f"Withdraw forecast {ci.mean:.0%} too close to random"

    def test_withdraw_vs_disill_complementarity(self):
        """Withdraw rate와 disill을 결합하면 각각보다 좋은가."""
        n_seeds = 30
        HOLDOUT = 100

        records = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            at = arrests[0]["tick"] if arrests else None
            if at is not None and at <= HOLDOUT:
                continue
            actual = _actual_category(at)
            wr = _withdraw_rate_at(r, HOLDOUT)
            # disill at holdout
            judas_snaps = r.state_snapshots.get("judas", {})
            c = [t for t in judas_snaps if t <= HOLDOUT]
            disill = judas_snaps[max(c)].domain_state.disillusionment if c else 0
            records.append((wr, disill, actual))

        def uni_wr(wr: float) -> str:
            return "early" if wr >= 0.1 else "mid"

        def uni_disill(d: float) -> str:
            # tick 100 disill scale: baseline ~5-6
            return "early" if d >= 6.0 else "mid"

        def combined(wr: float, d: float) -> str:
            # OR rule: either signal says early -> early
            if wr >= 0.1 or d >= 6.0:
                return "early"
            return "mid"

        uni_wr_c = sum(1 for wr, _, a in records if uni_wr(wr) == a)
        uni_d_c = sum(1 for _, d, a in records if uni_disill(d) == a)
        combined_c = sum(1 for wr, d, a in records if combined(wr, d) == a)

        n = len(records)
        print(f"\n=== Combined Forecast (n={n}, HOLDOUT={HOLDOUT}) ===")
        print(f"Withdraw rate only: {uni_wr_c/n:.1%}")
        print(f"Disill only:        {uni_d_c/n:.1%}")
        print(f"Combined (OR):      {combined_c/n:.1%}")
        # 결합 성능이 개별보다 나을 수도 있음 (complementarity)
