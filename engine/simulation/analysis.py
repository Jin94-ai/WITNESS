"""시뮬레이션 결과 분석.

배치 통계, 민감도 분석, 경로 클러스터링, 분기점 탐지.
SALib(전역 민감도), UMAP(차원 축소), sklearn HDBSCAN(클러스터링).
"""

from __future__ import annotations

import statistics
from collections import Counter
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.runner import SimulationResult


class AggregateStats(BaseModel):
    """배치 시뮬레이션 집계 통계."""

    n_runs: int
    match_rates: list[float] = Field(description="각 run의 정경 일치율")
    mean_match_rate: float
    std_match_rate: float
    checkpoint_pass_rates: dict[str, float] = Field(
        description="체크포인트별 통과율 (0~1)"
    )
    action_frequency: dict[str, dict[str, int]] = Field(
        description="이벤트별 행동 선택 빈도"
    )


def compute_aggregate(results: list[SimulationResult]) -> AggregateStats:
    """배치 결과를 집계한다."""
    n = len(results)
    if n == 0:
        return AggregateStats(
            n_runs=0, match_rates=[], mean_match_rate=0.0,
            std_match_rate=0.0, checkpoint_pass_rates={}, action_frequency={},
        )

    match_rates = [r.canonical_match_rate for r in results]
    mean_rate = statistics.mean(match_rates)
    std_rate = statistics.stdev(match_rates) if n > 1 else 0.0

    cp_counts: dict[str, int] = Counter()
    cp_totals: dict[str, int] = Counter()
    for r in results:
        for cp_result in r.checkpoint_results:
            cp_totals[cp_result.checkpoint_id] += 1
            if cp_result.passed:
                cp_counts[cp_result.checkpoint_id] += 1
    cp_pass_rates = {
        cp_id: cp_counts[cp_id] / cp_totals[cp_id] for cp_id in cp_totals
    }

    action_freq: dict[str, dict[str, int]] = {}
    for r in results:
        for action in r.action_history:
            if action.event_id not in action_freq:
                action_freq[action.event_id] = Counter()
            action_freq[action.event_id][action.chosen_action] += 1
    action_freq_dict = {k: dict(v) for k, v in action_freq.items()}

    return AggregateStats(
        n_runs=n, match_rates=match_rates, mean_match_rate=mean_rate,
        std_match_rate=std_rate, checkpoint_pass_rates=cp_pass_rates,
        action_frequency=action_freq_dict,
    )


def parameter_sensitivity(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    param_path: str,
    values: list[float],
    n_runs_per_value: int = 50,
    checkpoints: list[Checkpoint] | None = None,
) -> dict[float, AggregateStats]:
    """1차원 파라미터 민감도 분석."""
    results: dict[float, AggregateStats] = {}
    for val in values:
        overrides = {**config.parameter_overrides, param_path: val}
        modified = config.model_copy(update={"parameter_overrides": overrides})
        batch = run_batch(modified, rule_engine, n_runs_per_value, checkpoints)
        results[val] = compute_aggregate(batch)
    return results


# --- SALib 전역 민감도 분석 ---

def sobol_sensitivity(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    param_ranges: dict[str, tuple[float, float]],
    n_samples: int = 64,
    checkpoints: list[Checkpoint] | None = None,
    outcome_action: str = "",
) -> dict[str, Any]:
    """Sobol 전역 민감도 분석.

    파라미터 공간 전체에서 어떤 변수가 결과에 가장 큰 영향을 미치는지 측정.

    Args:
        config: 기본 설정
        rule_engine: 규칙 엔진
        param_ranges: 파라미터별 범위 {"emotions.fear": (0.0, 10.0), ...}
        n_samples: Saltelli 샘플 수 (실행 횟수 = n_samples * (2D+2))
        checkpoints: 체크포인트

    Returns:
        {"S1": {param: value}, "ST": {param: value}, "param_names": [...]}
    """
    from SALib.sample import saltelli
    from SALib.analyze import sobol

    param_names = list(param_ranges.keys())
    bounds = [list(param_ranges[p]) for p in param_names]

    problem = {
        "num_vars": len(param_names),
        "names": param_names,
        "bounds": bounds,
    }

    param_values = saltelli.sample(problem, n_samples)
    Y = np.zeros(param_values.shape[0])

    for i, pv in enumerate(param_values):
        overrides = {name: float(val) for name, val in zip(param_names, pv)}
        modified = config.model_copy(update={"parameter_overrides": overrides})
        # 여러 run의 평균을 사용하여 노이즈 감소
        batch = run_batch(modified, rule_engine, 3, checkpoints)
        # 지정된 행동의 횟수를 outcome으로
        action_counts = [
            sum(1 for a in r.action_history if a.chosen_action == outcome_action)
            for r in batch
        ]
        Y[i] = float(np.mean(action_counts))

    # 노이즈 추가하여 constant result 방지
    Y = Y + np.random.default_rng(42).normal(0, 0.001, size=Y.shape)

    si = sobol.analyze(problem, Y, print_to_console=False)

    # SALib 버전에 따라 S1이 스칼라 또는 배열일 수 있음
    def _extract(arr, j):
        val = arr[j]
        return float(val) if np.ndim(val) == 0 else float(np.mean(val))

    return {
        "S1": {name: _extract(si["S1"], j) for j, name in enumerate(param_names)},
        "ST": {name: _extract(si["ST"], j) for j, name in enumerate(param_names)},
        "param_names": param_names,
    }


def morris_sensitivity(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    param_ranges: dict[str, tuple[float, float]],
    n_trajectories: int = 10,
    checkpoints: list[Checkpoint] | None = None,
) -> dict[str, Any]:
    """Morris 스크리닝. Sobol보다 빠르고 초기 탐색에 적합.

    Returns:
        {"mu_star": {param: value}, "sigma": {param: value}}
    """
    from SALib.sample import morris as morris_sample
    from SALib.analyze import morris as morris_analyze

    param_names = list(param_ranges.keys())
    bounds = [list(param_ranges[p]) for p in param_names]

    problem = {
        "num_vars": len(param_names),
        "names": param_names,
        "bounds": bounds,
    }

    param_values = morris_sample.sample(problem, n_trajectories)
    Y = np.zeros(param_values.shape[0])

    for i, pv in enumerate(param_values):
        overrides = {name: float(val) for name, val in zip(param_names, pv)}
        modified = config.model_copy(update={"parameter_overrides": overrides})
        result = run_batch(modified, rule_engine, 1, checkpoints)[0]
        Y[i] = result.canonical_match_rate

    si = morris_analyze.analyze(problem, param_values, Y, print_to_console=False)

    return {
        "mu_star": {name: float(si["mu_star"][j]) for j, name in enumerate(param_names)},
        "sigma": {name: float(si["sigma"][j]) for j, name in enumerate(param_names)},
        "param_names": param_names,
    }


# --- 경로 클러스터링 (UMAP + HDBSCAN) ---

def cluster_trajectories(
    feature_matrix: list[list[float]],
    min_cluster_size: int = 5,
    n_neighbors: int = 15,
) -> dict[str, Any]:
    """경로를 UMAP으로 차원 축소하고 HDBSCAN으로 클러스터링한다.

    Args:
        feature_matrix: N x D feature matrix (dataset_to_feature_matrix 결과)
        min_cluster_size: HDBSCAN 최소 클러스터 크기
        n_neighbors: UMAP 이웃 수

    Returns:
        {"labels": [...], "embedding_2d": [[x,y], ...], "n_clusters": int, "noise_ratio": float}
    """
    import umap
    from sklearn.cluster import HDBSCAN

    X = np.array(feature_matrix)
    if X.shape[0] < 10:
        return {"labels": [-1] * X.shape[0], "embedding_2d": X[:, :2].tolist(),
                "n_clusters": 0, "noise_ratio": 1.0}

    # UMAP 2D 임베딩
    effective_neighbors = min(n_neighbors, X.shape[0] - 1)
    reducer = umap.UMAP(n_components=2, n_neighbors=effective_neighbors, random_state=42)
    embedding = reducer.fit_transform(X)

    # HDBSCAN 클러스터링
    clusterer = HDBSCAN(min_cluster_size=min_cluster_size)
    labels = clusterer.fit_predict(embedding)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    noise_ratio = float(np.sum(labels == -1)) / len(labels) if len(labels) > 0 else 0.0

    return {
        "labels": labels.tolist(),
        "embedding_2d": embedding.tolist(),
        "n_clusters": n_clusters,
        "noise_ratio": noise_ratio,
    }


# --- 분기점 탐지 ---

def detect_bifurcation(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    param_path: str,
    values: list[float],
    outcome_fn: str = "canonical_match_rate",
    n_runs_per_value: int = 30,
    checkpoints: list[Checkpoint] | None = None,
) -> dict[str, Any]:
    """파라미터 변화에 따른 결과 변동성을 측정하여 분기점을 탐지한다.

    분기점 = 파라미터를 조금 바꿨을 때 결과 분산이 급증하는 지점.

    Returns:
        {"param_values": [...], "means": [...], "stds": [...],
         "bifurcation_candidates": [...]}
    """
    means: list[float] = []
    stds: list[float] = []

    for val in values:
        overrides = {**config.parameter_overrides, param_path: val}
        modified = config.model_copy(update={"parameter_overrides": overrides})
        results = run_batch(modified, rule_engine, n_runs_per_value, checkpoints)

        if outcome_fn == "canonical_match_rate":
            outcomes = [r.canonical_match_rate for r in results]
        elif outcome_fn.startswith("action_count:"):
            action_id = outcome_fn.split(":", 1)[1]
            outcomes = [
                float(sum(1 for a in r.action_history if a.chosen_action == action_id))
                for r in results
            ]
        else:
            outcomes = [r.canonical_match_rate for r in results]

        means.append(statistics.mean(outcomes) if outcomes else 0.0)
        stds.append(statistics.stdev(outcomes) if len(outcomes) > 1 else 0.0)

    # 분기점 후보: 평균의 기울기가 급변하거나 분산이 급증하는 지점
    bifurcation_candidates: list[dict[str, Any]] = []
    for i in range(1, len(values) - 1):
        # 평균 변화율
        slope_before = abs(means[i] - means[i - 1]) / max(abs(values[i] - values[i - 1]), 0.01)
        slope_after = abs(means[i + 1] - means[i]) / max(abs(values[i + 1] - values[i]), 0.01)
        slope_change = abs(slope_after - slope_before)

        # 분산 급증
        std_spike = stds[i] / max(statistics.mean(stds), 0.001)

        if slope_change > 0.5 or std_spike > 1.5:
            bifurcation_candidates.append({
                "param_value": values[i],
                "slope_change": slope_change,
                "std_spike": std_spike,
                "mean": means[i],
                "std": stds[i],
            })

    return {
        "param_values": values,
        "means": means,
        "stds": stds,
        "bifurcation_candidates": bifurcation_candidates,
    }
