"""Partial Holdout Forecast: Train/Test Split Generalization.

LLM 리뷰 4차 핵심 지적: external validity 부족.
지금까지 forecast 검증은 "같은 데이터로 fit + 평가" (in-sample).
진짜 generalization 검증: train seeds로 threshold fit → test seeds로 accuracy 측정.

방법:
- n_total=60 seeds
- Train: seeds 0-29 (30 runs)
- Test:  seeds 30-59 (30 runs)
- Train 데이터로 best threshold 찾기
- Test 데이터에 동일 threshold 적용 → out-of-sample accuracy

비교:
- In-sample (train accuracy): 기존 방식과 동일
- Out-of-sample (test accuracy): 일반화 성능
- Gap = overfitting 정도
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


def _collect_record(seed: int, holdout: int) -> dict | None:
    """Single-run feature collection."""
    r = _run(seed)
    arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
    if not arrests:
        return None
    at = arrests[0]["tick"]
    if at <= holdout:
        return None

    actual = "early" if at < 200 else "mid"

    judas_snaps = r.state_snapshots.get("judas", {})
    cand = [t for t in judas_snaps if t <= holdout]
    disill = judas_snaps[max(cand)].domain_state.disillusionment if cand else 0.0

    withdraw_count = sum(
        1 for rec in r.action_histories.get("judas", [])
        if rec.chosen_action == "withdraw" and rec.tick < holdout
    )
    withdraw_rate = withdraw_count / max(holdout, 1)

    return {
        "seed": seed,
        "arrest_tick": at,
        "actual": actual,
        "disill": disill,
        "withdraw_rate": withdraw_rate,
    }


def _find_best_threshold(records: list[dict], feature: str) -> tuple[float, str, float]:
    """Return (best_threshold, best_direction, train_accuracy)."""
    values = sorted(set(r[feature] for r in records))
    best_acc = 0.0
    best_th = values[0]
    best_dir = "positive"  # high -> early
    for th in values:
        for direction in ["positive", "negative"]:
            if direction == "positive":
                preds = ["early" if r[feature] >= th else "mid" for r in records]
            else:
                preds = ["mid" if r[feature] >= th else "early" for r in records]
            correct = sum(1 for i, r in enumerate(records) if preds[i] == r["actual"])
            acc = correct / len(records)
            if acc > best_acc:
                best_acc = acc
                best_th = th
                best_dir = direction
    return best_th, best_dir, best_acc


def _apply_rule(records: list[dict], feature: str, threshold: float, direction: str) -> float:
    """Apply fixed rule, return test accuracy."""
    if direction == "positive":
        preds = ["early" if r[feature] >= threshold else "mid" for r in records]
    else:
        preds = ["mid" if r[feature] >= threshold else "early" for r in records]
    correct = sum(1 for i, r in enumerate(records) if preds[i] == r["actual"])
    return correct / len(records)


@pytest.mark.slow
class TestPartialHoldoutGeneralization:
    def test_withdraw_rate_train_test_split(self):
        """Withdraw rate rule: train set에서 threshold fit, test set에서 평가."""
        HOLDOUT = 100
        n_total = 60

        # Collect records from all seeds
        all_records = []
        for seed in range(n_total):
            rec = _collect_record(seed, HOLDOUT)
            if rec is not None:
                all_records.append(rec)

        if len(all_records) < 40:
            pytest.skip("not enough valid runs")

        # Deterministic train/test split (seeds 0-29 vs 30-59)
        train = [r for r in all_records if r["seed"] < 30]
        test = [r for r in all_records if r["seed"] >= 30]

        print(f"\n=== Partial Holdout Train/Test Split (withdraw rate @ tick {HOLDOUT}) ===")
        print(f"Train: {len(train)} runs, Test: {len(test)} runs")

        # Fit threshold on TRAIN only
        th, direction, train_acc = _find_best_threshold(train, "withdraw_rate")
        # Apply to TEST
        test_acc = _apply_rule(test, "withdraw_rate", th, direction)

        # CI for test accuracy
        correct_test = int(test_acc * len(test))
        test_ci = proportion_ci(correct_test, len(test))
        train_ci = proportion_ci(int(train_acc * len(train)), len(train))

        print(f"Fitted threshold: {th:.4f} ({direction})")
        print(f"Train (in-sample):  {train_acc:.1%} "
              f"[{train_ci.lower:.1%}, {train_ci.upper:.1%}]")
        print(f"Test (out-of-sample): {test_acc:.1%} "
              f"[{test_ci.lower:.1%}, {test_ci.upper:.1%}]")

        overfit_gap = train_acc - test_acc
        print(f"Overfitting gap: {overfit_gap:+.1%}")
        print("(Small gap = generalization OK; large gap = overfit to train)")

        # 검증 1: test accuracy가 random (50%)보다 유의미
        assert test_ci.lower > 0.5, \
            f"Test lower CI {test_ci.lower:.1%} not above random (50%)"

        # 검증 2: overfitting gap < 15pp (일반화 가능)
        assert overfit_gap < 0.15, \
            f"Overfitting gap {overfit_gap:.1%} too large"

    def test_disill_train_test_split(self):
        """State-based (disill) rule: 동일 train/test 분할로 일반화 검증."""
        HOLDOUT = 150
        n_total = 60

        all_records = []
        for seed in range(n_total):
            rec = _collect_record(seed, HOLDOUT)
            if rec is not None:
                all_records.append(rec)

        if len(all_records) < 40:
            pytest.skip("not enough valid runs")

        train = [r for r in all_records if r["seed"] < 30]
        test = [r for r in all_records if r["seed"] >= 30]

        print(f"\n=== Partial Holdout Train/Test Split (disill @ tick {HOLDOUT}) ===")
        print(f"Train: {len(train)} runs, Test: {len(test)} runs")

        th, direction, train_acc = _find_best_threshold(train, "disill")
        test_acc = _apply_rule(test, "disill", th, direction)

        test_ci = proportion_ci(int(test_acc * len(test)), len(test))
        train_ci = proportion_ci(int(train_acc * len(train)), len(train))

        print(f"Fitted threshold: {th:.3f} ({direction})")
        print(f"Train (in-sample):  {train_acc:.1%} "
              f"[{train_ci.lower:.1%}, {train_ci.upper:.1%}]")
        print(f"Test (out-of-sample): {test_acc:.1%} "
              f"[{test_ci.lower:.1%}, {test_ci.upper:.1%}]")
        print(f"Overfitting gap: {train_acc - test_acc:+.1%}")

        assert test_ci.lower > 0.45, \
            f"Test lower CI {test_ci.lower:.1%} below 45%"

    def test_cross_validation_5fold(self):
        """5-fold CV로 robust한 generalization estimate."""
        HOLDOUT = 100
        n_total = 50

        all_records = []
        for seed in range(n_total):
            rec = _collect_record(seed, HOLDOUT)
            if rec is not None:
                all_records.append(rec)

        if len(all_records) < 30:
            pytest.skip("not enough valid runs")

        # 5-fold CV
        n = len(all_records)
        fold_size = n // 5
        cv_accuracies = []

        print(f"\n=== 5-fold CV (withdraw rate @ tick {HOLDOUT}) ===")
        for fold in range(5):
            test_start = fold * fold_size
            test_end = test_start + fold_size
            test = all_records[test_start:test_end]
            train = all_records[:test_start] + all_records[test_end:]

            th, direction, _ = _find_best_threshold(train, "withdraw_rate")
            test_acc = _apply_rule(test, "withdraw_rate", th, direction)
            cv_accuracies.append(test_acc)
            print(f"  Fold {fold+1}: test accuracy {test_acc:.1%} "
                  f"(threshold={th:.4f}, {direction})")

        mean_cv = statistics.mean(cv_accuracies)
        std_cv = statistics.stdev(cv_accuracies) if len(cv_accuracies) > 1 else 0
        print(f"\nCV mean: {mean_cv:.1%}, std: {std_cv:.1%}")
        print(f"CV range: [{min(cv_accuracies):.1%}, {max(cv_accuracies):.1%}]")

        # CV mean이 random 기준선(50%) 이상
        assert mean_cv > 0.55, \
            f"CV mean {mean_cv:.1%} below 55% (weak generalization)"
        # CV std가 과도하게 크지 않음 (< 20pp)
        assert std_cv < 0.20, \
            f"CV std {std_cv:.1%} too high (unstable generalization)"
