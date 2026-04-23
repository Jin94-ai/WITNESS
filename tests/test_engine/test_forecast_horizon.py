"""Forecast Horizon Analysis.

"얼마나 일찍 예측 가능한가?" 를 정량화.
holdout tick을 50, 100, 150, 200으로 변화시키며 예측 정확도 측정.

예상:
- tick 50: disill ~3 (초기값 근처), 정보 부족 -> 낮은 정확도
- tick 100: disill이 좀 쌓임 -> 중간 정확도
- tick 150: disill이 확실히 갈라짐 -> 높은 정확도
- tick 200: 대부분 포화 -> 가장 높은 정확도
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


def _get_disill_at_tick(result, target_tick: int) -> float | None:
    judas_snaps = result.state_snapshots.get("judas", {})
    candidates = [t for t in judas_snaps if t <= target_tick]
    if not candidates:
        return None
    return judas_snaps[max(candidates)].domain_state.disillusionment


def _forecast_from_disill(disill: float, holdout_tick: int) -> str:
    """Holdout tick마다 다른 threshold 적용.

    이른 holdout에서는 disill이 낮아도 "미래에 오를 수 있음"을 고려.
    늦은 holdout에서는 현재 값이 미래 결과에 더 직접적.
    """
    # holdout tick별 threshold 조정
    # tick 50: disill이 4면 이미 빠르게 쌓이고 있음
    # tick 200: disill이 9여야 이미 arrest가 일어났거나 임박
    if holdout_tick <= 75:
        if disill >= 5.0:
            return "early"
        if disill >= 3.5:
            return "mid"
        if disill >= 2.0:
            return "late"
        return "deadline_or_none"
    if holdout_tick <= 125:
        if disill >= 7.0:
            return "early"
        if disill >= 5.0:
            return "mid"
        if disill >= 3.0:
            return "late"
        return "deadline_or_none"
    if holdout_tick <= 175:
        if disill >= 8.0:
            return "early"
        if disill >= 6.0:
            return "mid"
        if disill >= 4.0:
            return "late"
        return "deadline_or_none"
    # tick 200+
    if disill >= 8.0:
        return "early"
    if disill >= 6.5:
        return "mid"
    if disill >= 4.5:
        return "late"
    return "deadline_or_none"


@pytest.mark.slow
class TestForecastHorizon:
    def test_accuracy_vs_horizon(self):
        """Horizon이 늦어질수록 예측 정확도가 높아진다."""
        n_seeds = 20
        horizons = [50, 100, 150, 200]

        # 각 horizon에 대해 결과 수집
        all_runs = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            arrest_tick = arrests[0]["tick"] if arrests else None
            actual = _actual_category(arrest_tick)

            disill_at = {h: _get_disill_at_tick(r, h) for h in horizons}
            all_runs.append({"actual": actual, "disill_at": disill_at, "arrest_tick": arrest_tick})

        print(f"\n=== Forecast Horizon Analysis (n={n_seeds}) ===")
        print(f"{'Horizon':>10} | {'Accuracy':>10} | {'95% CI':>18}")
        print("-" * 50)

        accuracies = {}
        for h in horizons:
            correct = 0
            valid = 0
            for run in all_runs:
                if run["disill_at"][h] is None:
                    continue
                # holdout 이전에 이미 arrest가 발생했으면 스킵
                if run["arrest_tick"] is not None and run["arrest_tick"] <= h:
                    continue
                valid += 1
                pred = _forecast_from_disill(run["disill_at"][h], h)
                if pred == run["actual"]:
                    correct += 1

            if valid > 0:
                ci = proportion_ci(correct, valid)
                accuracies[h] = ci
                print(f"{h:>10} | {ci.mean:>9.0%}  | [{ci.lower:>4.0%}, {ci.upper:>4.0%}] (n={valid})")

        # 단조 증가해야 함 (horizon 늦어질수록 정확)
        accs = [accuracies[h].mean for h in horizons if h in accuracies]
        print(f"\nAccuracy sequence: {[f'{a:.0%}' for a in accs]}")

        # 평균 disill at each horizon
        print(f"\n{'Horizon':>10} | {'Mean disill':>12}")
        print("-" * 30)
        for h in horizons:
            disills = [run["disill_at"][h] for run in all_runs if run["disill_at"][h] is not None]
            if disills:
                mean_disill = sum(disills) / len(disills)
                print(f"{h:>10} | {mean_disill:>11.1f}")

        # 단조 증가 확인: 늦은 horizon에서 더 정확
        # (tick 50 -> 200으로 갈수록 정확도 증가 또는 유지)
        if 50 in accuracies and 200 in accuracies:
            assert accuracies[200].mean >= accuracies[50].mean, \
                "Late horizon should be at least as accurate as early horizon"
