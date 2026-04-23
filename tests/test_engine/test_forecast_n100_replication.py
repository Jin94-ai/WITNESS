"""Forecast Replication at n=100.

RESEARCH.md 한계: "대부분 n=20~30, n=100+에서 재검증 필요".
핵심 발견인 "holdout tick 200에서 80% accuracy"가 n=100에서도 유지되는지 검증.

Sample size 증가의 효과:
- CI 좁아짐: [63%, 90%] -> 더 좁은 구간 (예: [72%, 85%])
- Mean stability: sample variance 감소
- 결과: RESEARCH.md 핵심 수치 statistical power 강화

예상: 80% point estimate는 ±5pp 내외 유지, CI는 상당히 좁아짐.
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
HOLDOUT_TICK = 200


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


def _get_disill_at(result, target_tick: int) -> float | None:
    snapshots = result.state_snapshots.get("judas", {})
    candidates = [t for t in snapshots if t <= target_tick]
    if not candidates:
        return None
    return snapshots[max(candidates)].domain_state.disillusionment


def _forecast(disill: float) -> str:
    """test_forecasting_holdout.py와 동일한 rule (재현성)."""
    if disill >= 9.5:
        return "early"
    if disill >= 8.0:
        return "early"
    if disill >= 6.5:
        return "mid"
    if disill >= 4.5:
        return "late"
    return "deadline_or_none"


def _actual(arrest_tick: int | None) -> str:
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


@pytest.mark.slow
class TestForecastN100Replication:
    def test_accuracy_at_large_n(self):
        """n=100에서 forecast accuracy가 random baseline(20%)보다 유의미하게 높은가."""
        n_seeds = 100
        correct = 0
        close = 0
        total = 0
        categories = ["very_early", "early", "mid", "late", "deadline_or_none"]

        arrest_ticks = []
        predictions: dict[str, int] = {c: 0 for c in categories}
        actuals: dict[str, int] = {c: 0 for c in categories}

        for seed in range(n_seeds):
            r = _run(seed)
            disill = _get_disill_at(r, HOLDOUT_TICK)
            if disill is None:
                continue

            pred = _forecast(disill)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            at = arrests[0]["tick"] if arrests else None
            if at is not None:
                arrest_ticks.append(at)
            act = _actual(at)

            predictions[pred] = predictions.get(pred, 0) + 1
            actuals[act] = actuals.get(act, 0) + 1

            total += 1
            if pred == act:
                correct += 1
            elif abs(categories.index(pred) - categories.index(act)) == 1:
                close += 1

        exact_ci = proportion_ci(correct, total)
        close_ci = proportion_ci(correct + close, total)

        print(f"\n=== Forecast Replication n={n_seeds} ===")
        print(f"Exact match: {correct}/{total} = {exact_ci.mean:.1%} "
              f"[{exact_ci.lower:.1%}, {exact_ci.upper:.1%}]")
        print(f"Close (+/-1): {correct+close}/{total} = {close_ci.mean:.1%} "
              f"[{close_ci.lower:.1%}, {close_ci.upper:.1%}]")
        print("Random baseline (1/5): 20%")

        print(f"\nArrest tick distribution (n with arrest={len(arrest_ticks)}):")
        import statistics as stats
        if arrest_ticks:
            print(f"  mean={stats.mean(arrest_ticks):.1f}, "
                  f"std={stats.stdev(arrest_ticks):.1f}, "
                  f"median={stats.median(arrest_ticks):.0f}")
            print(f"  range=[{min(arrest_ticks)}, {max(arrest_ticks)}]")

        print("\nActual category distribution:")
        for c in categories:
            print(f"  {c:>18}: {actuals[c]:>3}")

        print("\nPredicted category distribution:")
        for c in categories:
            print(f"  {c:>18}: {predictions[c]:>3}")

        # 핵심 검증: CI 하한이 random baseline을 초과
        assert exact_ci.lower > 0.20, \
            f"Forecast lower CI {exact_ci.lower:.1%} must beat random baseline 20%"

        # RESEARCH.md 일관성: 기존 n=20 결과(80%)와 ±15pp 내 일치
        # (stochastic variation 허용)
        assert abs(exact_ci.mean - 0.80) < 0.15, \
            f"n=100 accuracy {exact_ci.mean:.1%} diverges from n=20 (80%) too much"

    def test_arrest_rate_at_n100(self):
        """Spontaneous arrest rate가 n=100에서도 높게 유지되는가."""
        n_seeds = 100
        arrest_count = 0

        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_count += 1

        ci = proportion_ci(arrest_count, n_seeds)
        print(f"\n=== Arrest Rate n={n_seeds} ===")
        print(f"Spontaneous arrest: {arrest_count}/{n_seeds} = {ci.mean:.1%} "
              f"[{ci.lower:.1%}, {ci.upper:.1%}]")
        print("RESEARCH.md n=50: 100% [92.9%, 100%]")

        # 핵심 발견 재현: 체포 발생률 >= 90%
        assert ci.lower >= 0.90, \
            f"Arrest rate lower CI {ci.lower:.1%} below 90% threshold"
