"""Parameter Recovery Test (Synthetic Truth).

엔진에 알려진 "진짜 파라미터"를 넣고 데이터를 생성한 뒤,
분석 파이프라인이 그 파라미터를 복원하는지 검증한다.

POM 방법론의 핵심: 여러 패턴을 동시에 맞추는 파라미터 영역이
진짜 파라미터를 포함하는가?
"""

from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.pom import PatternCriterion, pom_filter
from engine.simulation.runner import SimulationResult


def generate_synthetic_data(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    true_params: dict[str, float],
    n_runs: int = 100,
    checkpoints: list[Checkpoint] | None = None,
) -> list[SimulationResult]:
    """진짜 파라미터로 데이터를 생성한다."""
    modified = config.model_copy(update={"parameter_overrides": true_params})
    return run_batch(modified, rule_engine, n_runs, checkpoints)


def recovery_test(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    true_params: dict[str, float],
    param_ranges: dict[str, tuple[float, float]],
    scorecard: list[PatternCriterion],
    n_synthetic: int = 50,
    n_recovery: int = 500,
    checkpoints: list[Checkpoint] | None = None,
) -> dict[str, Any]:
    """Parameter Recovery Test를 실행한다.

    1. true_params로 synthetic data 생성
    2. synthetic data에서 POM 패턴 추출
    3. 파라미터 공간을 탐색하며 같은 패턴을 재현하는 영역 탐색
    4. 재현 영역이 true_params를 포함하는지 검증

    Returns:
        {
            "true_params": 진짜 파라미터,
            "true_pom_rate": 진짜 파라미터에서의 POM 통과율,
            "recovered_params_mean": 복원된 파라미터 평균,
            "recovery_error": |true - recovered| 평균,
            "true_in_recovered_box": 진짜가 복원 박스 안에 있는가,
            "pom_pass_rate_at_recovered": 복원된 파라미터에서의 POM 통과율,
        }
    """
    import random

    # 1. Synthetic data 생성 + POM 평가
    synthetic_results = generate_synthetic_data(
        config, rule_engine, true_params, n_synthetic, checkpoints
    )
    true_pom = pom_filter(synthetic_results, scorecard)

    # 2. 파라미터 공간 탐색
    rng = random.Random(42)
    param_names = list(param_ranges.keys())

    pom_passing_params: list[dict[str, float]] = []

    for i in range(n_recovery):
        test_params = {
            name: rng.uniform(lo, hi)
            for name, (lo, hi) in param_ranges.items()
        }
        test_config = config.model_copy(update={"parameter_overrides": test_params})
        test_results = run_batch(test_config, rule_engine, 10, checkpoints)
        test_pom = pom_filter(test_results, scorecard)

        # POM 통과율이 20% 이상이면 "유효" 영역
        if test_pom["all_pass_rate"] >= 0.2:
            pom_passing_params.append(test_params)

    # 3. 복원 결과 분석
    if not pom_passing_params:
        return {
            "true_params": true_params,
            "true_pom_rate": true_pom["all_pass_rate"],
            "n_pom_passing": 0,
            "recovered_params_mean": {},
            "recovery_error": float("inf"),
            "true_in_recovered_box": False,
            "pom_pass_rate_at_recovered": 0.0,
        }

    # 복원 파라미터 평균
    recovered_mean = {
        name: np.mean([p[name] for p in pom_passing_params])
        for name in param_names
    }

    # 복원 박스 (min/max)
    recovered_box = {
        name: (
            min(p[name] for p in pom_passing_params),
            max(p[name] for p in pom_passing_params),
        )
        for name in param_names
    }

    # 진짜가 박스 안에 있는가
    true_in_box = all(
        recovered_box[name][0] <= true_params[name] <= recovered_box[name][1]
        for name in param_names
    )

    # 복원 오류
    errors = [
        abs(true_params[name] - recovered_mean[name])
        for name in param_names
    ]
    mean_error = np.mean(errors)

    # 복원된 파라미터에서의 POM 통과율
    recovered_config = config.model_copy(update={"parameter_overrides": recovered_mean})
    recovered_results = run_batch(recovered_config, rule_engine, 30, checkpoints)
    recovered_pom = pom_filter(recovered_results, scorecard)

    return {
        "true_params": true_params,
        "true_pom_rate": true_pom["all_pass_rate"],
        "n_pom_passing": len(pom_passing_params),
        "recovered_params_mean": {k: round(v, 2) for k, v in recovered_mean.items()},
        "recovered_box": {k: (round(v[0], 2), round(v[1], 2)) for k, v in recovered_box.items()},
        "recovery_error": round(float(mean_error), 2),
        "true_in_recovered_box": true_in_box,
        "pom_pass_rate_at_recovered": recovered_pom["all_pass_rate"],
    }
