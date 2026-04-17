"""pyABC 기반 파라미터 보정 (Approximate Bayesian Computation).

역사 경로(ground truth)에 가장 가까운 파라미터 posterior를 추정한다.
likelihood를 명시할 수 없는 복잡한 시뮬레이터에 적합한 likelihood-free 방식.

사용법:
    posterior = calibrate_parameters(config, rule_engine, param_ranges, checkpoints)
"""

from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint


def calibrate_parameters(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    param_ranges: dict[str, tuple[float, float]],
    checkpoints: list[Checkpoint],
    n_populations: int = 5,
    pop_size: int = 50,
    n_runs_per_eval: int = 10,
    target_match_rate: float = 0.5,
    target_action: str = "",
    target_action_count: float = 3.0,
) -> dict[str, Any]:
    """pyABC로 파라미터 posterior를 추정한다.

    Args:
        config: 기본 설정
        rule_engine: 규칙 엔진
        param_ranges: 파라미터별 사전분포 범위
        checkpoints: ground truth 체크포인트
        n_populations: ABC-SMC 세대 수
        pop_size: 세대당 population 크기
        n_runs_per_eval: 각 파라미터 평가 시 배치 크기
        target_match_rate: 목표 정경 일치율

    Returns:
        {"best_params": {...}, "history_summary": [...], "posterior_samples": [...]}
    """
    import pyabc

    param_names = list(param_ranges.keys())

    # 사전분포 정의
    prior = pyabc.Distribution(**{
        name: pyabc.RV("uniform", lo, hi - lo)
        for name, (lo, hi) in param_ranges.items()
    })

    def model(params: dict) -> dict:
        """시뮬레이션 실행 + 요약 통계 반환."""
        overrides = {name: float(params[name]) for name in param_names}
        modified = config.model_copy(update={"parameter_overrides": overrides})
        results = run_batch(modified, rule_engine, n_runs_per_eval, checkpoints)

        match_rates = [r.canonical_match_rate for r in results]
        action_counts = [
            sum(1 for a in r.action_history if a.chosen_action == target_action)
            for r in results
        ]

        return {
            "mean_match_rate": float(np.mean(match_rates)),
            "mean_action_count": float(np.mean(action_counts)),
        }

    def distance(x: dict, y: dict) -> float:
        """관측값과 시뮬레이션 요약 통계의 거리."""
        match_diff = abs(x["mean_match_rate"] - y["mean_match_rate"])
        action_diff = abs(x["mean_action_count"] - y["mean_action_count"]) / max(target_action_count, 1.0)
        return float(match_diff + action_diff)

    observation = {
        "mean_match_rate": target_match_rate,
        "mean_action_count": target_action_count,
    }

    abc = pyabc.ABCSMC(model, prior, distance, population_size=pop_size)
    db_path = "sqlite:///witness_abc.db"
    abc.new(db_path, observation)

    history = abc.run(max_nr_populations=n_populations)

    # 결과 추출
    df, w = history.get_distribution()
    best_idx = w.argmax()
    best_params = {name: float(df.iloc[best_idx][name]) for name in param_names}

    posterior_samples = [
        {name: float(row[name]) for name in param_names}
        for _, row in df.iterrows()
    ]

    history_summary = []
    for t in range(history.max_t + 1):
        pop_df, pop_w = history.get_distribution(t=t)
        history_summary.append({
            "generation": t,
            "n_particles": len(pop_df),
            "epsilon": float(history.get_all_populations().iloc[t]["epsilon"]),
        })

    return {
        "best_params": best_params,
        "history_summary": history_summary,
        "posterior_samples": posterior_samples[:20],  # 상위 20개만
    }
