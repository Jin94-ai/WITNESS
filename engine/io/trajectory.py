"""Trajectory 데이터셋 저장/로드.

각 시뮬레이션 run의 전체 경로를 구조화된 데이터셋으로 저장한다.
v0.3: 최종 상태 대신 경로 자체를 feature로 (path feature).

저장 형식: JSONL (한 줄 = 한 run)
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from engine.simulation.runner import SimulationResult


def result_to_record(result: SimulationResult, params: dict[str, float] | None = None) -> dict[str, Any]:
    """SimulationResult를 저장 가능한 flat record로 변환한다."""
    event_sequence = [
        {"event_id": a.event_id, "tick": a.tick, "action": a.chosen_action}
        for a in result.action_history
    ]

    state_series: list[dict[str, Any]] = []
    for tick in sorted(result.state_snapshots.keys()):
        s = result.state_snapshots[tick]
        state_series.append({
            "tick": tick,
            "fear": s.emotions.fear,
            "hope": s.emotions.hope,
            "grief": s.emotions.grief,
            "confusion": s.emotions.confusion,
            "love": s.emotions.love,
            "fatigue": s.physical.fatigue,
            "location": s.physical.location,
        })

    cp_results = {cp.checkpoint_id: cp.passed for cp in result.checkpoint_results}
    fired_ticks = {fe["event_id"]: fe["tick"] for fe in result.fired_events}

    return {
        "seed": result.seed,
        "params": params or {},
        "canonical_match_rate": result.canonical_match_rate,
        "checkpoint_results": cp_results,
        "event_sequence": event_sequence,
        "fired_events": fired_ticks,
        "state_series": state_series,
        "final_state": {
            "fear": result.final_state.emotions.fear,
            "hope": result.final_state.emotions.hope,
            "grief": result.final_state.emotions.grief,
            "confusion": result.final_state.emotions.confusion,
            "love": result.final_state.emotions.love,
            "fatigue": result.final_state.physical.fatigue,
        },
        "n_denials": sum(1 for a in result.action_history if a.chosen_action == "deny"),  # legacy compat
        "n_confessions": sum(1 for a in result.action_history if a.chosen_action == "confess"),  # legacy compat
        "n_fired_events": len(result.fired_events),
        "action_counts": _count_actions(result),
        # slow state (비가역적 흔적) -- state에 slow_state가 있으면 포함
        "slow_state": _extract_slow_state(result),
    }


def _count_actions(result: SimulationResult) -> dict[str, int]:
    """모든 행동 ID별 카운트. 인물 비종속."""
    from collections import Counter
    counts = Counter(a.chosen_action for a in result.action_history)
    return dict(counts)


def _extract_slow_state(result: SimulationResult) -> dict[str, Any]:
    """slow state 필드가 있으면 추출."""
    fs = result.final_state
    if hasattr(fs, "slow_state") and fs.slow_state is not None:
        return fs.slow_state.model_dump()
    return {}


def save_trajectory_dataset(
    results: list[SimulationResult],
    path: Path,
    params_list: list[dict[str, float]] | None = None,
) -> None:
    """시뮬레이션 결과 목록을 JSONL로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for i, result in enumerate(results):
            params = params_list[i] if params_list and i < len(params_list) else None
            record = result_to_record(result, params)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def multi_result_to_record(result: Any) -> dict[str, Any]:
    """MultiAgentResult를 저장 가능한 flat record로 변환한다.

    에이전트별 행동/상태를 하나의 레코드로 통합.
    UMAP 클러스터링 파이프라인과 호환.
    """
    from collections import Counter

    record: dict[str, Any] = {
        "seed": result.seed,
    }

    # 에이전트별 최종 상태
    for aid, state in result.final_states.items():
        record[f"{aid}_fear"] = state.emotions.fear
        record[f"{aid}_hope"] = state.emotions.hope
        record[f"{aid}_grief"] = state.emotions.grief
        record[f"{aid}_love"] = state.emotions.love
        record[f"{aid}_moral_injury"] = state.slow_state.moral_injury
        record[f"{aid}_identity_shift"] = state.slow_state.identity_shift
        record[f"{aid}_trust_scar"] = state.slow_state.trust_scar

    # 에이전트별 행동 카운트
    for aid, history in result.action_histories.items():
        counts = Counter(a.chosen_action for a in history)
        for action, count in counts.items():
            record[f"{aid}_action_{action}"] = count

    # 트리거 이벤트
    trigger_ticks: dict[str, int] = {}
    for t in result.fired_triggers:
        tid = t["trigger_id"]
        if tid not in trigger_ticks:
            trigger_ticks[tid] = t["tick"]
    record["trigger_ticks"] = trigger_ticks

    # Hazard 이벤트
    record["n_hazard_events"] = len(result.fired_events)
    record["n_triggers"] = len(result.fired_triggers)

    # 정경 일치율 (있으면)
    for aid, rate in result.canonical_match_rates.items():
        record[f"{aid}_match_rate"] = rate

    return record


def multi_dataset_to_feature_matrix(
    records: list[dict[str, Any]],
    feature_keys: list[str] | None = None,
) -> tuple[list[list[float]], list[str]]:
    """multi-agent 레코드 목록을 feature matrix로 변환한다.

    UMAP 클러스터링 파이프라인과 호환.

    Args:
        records: multi_result_to_record 결과 목록
        feature_keys: 사용할 feature 키 목록. None이면 자동 탐지.

    Returns:
        (feature_matrix, feature_names) 튜플
    """
    if not records:
        return [], []

    # 자동 탐지: 모든 레코드에서 숫자형 키 수집
    if feature_keys is None:
        all_keys: set[str] = set()
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, (int, float)) and k != "seed":
                    all_keys.add(k)
        feature_keys = sorted(all_keys)

    matrix = []
    for rec in records:
        row = [float(rec.get(k, 0.0)) for k in feature_keys]
        matrix.append(row)

    return matrix, feature_keys


def load_trajectory_dataset(path: Path) -> list[dict[str, Any]]:
    """JSONL에서 trajectory 데이터셋을 로드한다."""
    records: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _series_stats(values: list[float]) -> dict[str, float]:
    """시계열 요약 통계."""
    if not values:
        return {"mean": 0.0, "max": 0.0, "min": 0.0, "std": 0.0, "auc": 0.0}
    return {
        "mean": statistics.mean(values),
        "max": max(values),
        "min": min(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "auc": sum(values),  # 누적 면적 (단순 합)
    }


def _find_event_tick(record: dict, event_id: str) -> int:
    """이벤트 발동 tick을 찾는다. 없으면 -1."""
    return int(record.get("fired_events", {}).get(event_id, -1))


def _state_at_tick(series: list[dict], target_tick: int, field: str) -> float:
    """특정 tick에 가장 가까운 상태 값을 반환."""
    if not series:
        return 0.0
    best = min(series, key=lambda s: abs(s["tick"] - target_tick))
    return float(best.get(field, 0.0))


def _state_window(series: list[dict], start: int, end: int, field: str) -> list[float]:
    """tick 범위 내 상태 값 목록."""
    return [s[field] for s in series if start <= s["tick"] <= end and field in s]


def dataset_to_path_features(
    records: list[dict[str, Any]],
    pivot_event: str = "arrest",
    action_events: list[str] | None = None,
    recovery_event: str | None = None,
) -> tuple[list[list[float]], list[str]]:
    """경로 기반 feature matrix. 인물 비종속 -- 이벤트 이름은 파라미터로 주입.

    Args:
        records: trajectory 레코드 목록
        pivot_event: 분기점 이벤트 ID (기본: "arrest")
        action_events: 행동을 추적할 이벤트 ID 목록 (기본: 없으면 자동 탐지)
        recovery_event: 회복 이벤트 ID (기본: 없으면 마지막 이벤트)

    Returns:
        (feature_matrix, feature_names) 튜플
    """
    # 자동 탐지: 모든 레코드에서 등장하는 이벤트 ID와 행동 ID 수집
    all_event_ids: set[str] = set()
    all_action_ids: set[str] = set()
    for rec in records:
        for fe_id in rec.get("fired_events", {}):
            all_event_ids.add(fe_id)
        for seq in rec.get("event_sequence", []):
            all_action_ids.add(seq["action"])

    # 이벤트 timing feature 이름
    event_list = sorted(all_event_ids)
    action_list = sorted(all_action_ids)

    feature_names = (
        # 이벤트 timing
        [f"event_{eid}_tick" for eid in event_list]
        # 행동 카운트
        + [f"action_{aid}_count" for aid in action_list]
        + ["n_fired_events"]
        # pivot 이벤트 전후 상태
        + [f"pre_{pivot_event}_fear", f"pre_{pivot_event}_fatigue",
           f"pre_{pivot_event}_confusion", f"pre_{pivot_event}_hope",
           f"pre_{pivot_event}_love"]
        + [f"post_{pivot_event}_fear", f"post_{pivot_event}_grief"]
        # 경로 중 peak/trough
        + ["peak_fear", "peak_grief", "peak_confusion", "trough_hope"]
        # pivot window AUC
        + [f"fear_auc_{pivot_event}_window", f"grief_auc_post_{pivot_event}"]
        # slow state
        + ["slow_moral_injury", "slow_breach_count", "slow_trust_scar", "slow_identity_shift"]
    )

    matrix: list[list[float]] = []
    for rec in records:
        series = rec.get("state_series", [])
        fired = rec.get("fired_events", {})
        seq = rec.get("event_sequence", [])

        # 이벤트 timing
        event_ticks = [float(fired.get(eid, -1)) for eid in event_list]

        # 행동 카운트
        action_counts = []
        for aid in action_list:
            action_counts.append(float(sum(1 for s in seq if s["action"] == aid)))

        # pivot 전후 상태
        pivot_tick = fired.get(pivot_event, -1)
        pre_tick = max(pivot_tick - 5, 0) if pivot_tick > 0 else 0
        post_tick = pivot_tick + 5 if pivot_tick > 0 else 0

        # 전체 시계열 통계
        all_fear = [s["fear"] for s in series if "fear" in s]
        all_grief = [s["grief"] for s in series if "grief" in s]
        all_confusion = [s["confusion"] for s in series if "confusion" in s]
        all_hope = [s["hope"] for s in series if "hope" in s]

        fear_pivot_window = _state_window(
            series, max(pivot_tick - 10, 0), pivot_tick + 20, "fear"
        ) if pivot_tick > 0 else []
        grief_post_pivot = _state_window(
            series, pivot_tick, pivot_tick + 50, "grief"
        ) if pivot_tick > 0 else []

        slow = rec.get("slow_state", {})

        row = (
            event_ticks
            + action_counts
            + [float(rec.get("n_fired_events", 0))]
            + [
                _state_at_tick(series, pre_tick, "fear"),
                _state_at_tick(series, pre_tick, "fatigue"),
                _state_at_tick(series, pre_tick, "confusion"),
                _state_at_tick(series, pre_tick, "hope"),
                _state_at_tick(series, pre_tick, "love"),
                _state_at_tick(series, post_tick, "fear"),
                _state_at_tick(series, post_tick, "grief"),
            ]
            + [
                max(all_fear) if all_fear else 0.0,
                max(all_grief) if all_grief else 0.0,
                max(all_confusion) if all_confusion else 0.0,
                min(all_hope) if all_hope else 0.0,
            ]
            + [sum(fear_pivot_window), sum(grief_post_pivot)]
            + [
                float(slow.get("moral_injury", 0)),
                float(slow.get("breach_count", 0)),
                float(slow.get("trust_scar", 0)),
                float(slow.get("identity_shift", 0)),
            ]
        )
        matrix.append(row)

    return matrix, feature_names


# 하위 호환: 기존 함수 유지
def dataset_to_feature_matrix(records: list[dict[str, Any]]) -> tuple[list[list[float]], list[str]]:
    """Legacy feature matrix (최종 상태 기반). 하위 호환용."""
    feature_names = [
        "canonical_match_rate", "n_denials", "n_confessions", "n_fired_events",
        "final_fear", "final_hope", "final_grief", "final_confusion", "final_love", "final_fatigue",
    ]
    matrix: list[list[float]] = []
    for rec in records:
        row = [
            rec.get("canonical_match_rate", 0.0),
            rec.get("n_denials", 0),
            rec.get("n_confessions", 0),
            rec.get("n_fired_events", 0),
            rec.get("final_state", {}).get("fear", 0.0),
            rec.get("final_state", {}).get("hope", 0.0),
            rec.get("final_state", {}).get("grief", 0.0),
            rec.get("final_state", {}).get("confusion", 0.0),
            rec.get("final_state", {}).get("love", 0.0),
            rec.get("final_state", {}).get("fatigue", 0.0),
        ]
        matrix.append(row)
    return matrix, feature_names
