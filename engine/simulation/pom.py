"""Pattern-Oriented Modeling (POM) 검증 체계.

단일 지표가 아니라 여러 관측 패턴을 동시에 맞추는 필터.
이 필터를 통과하는 파라미터/규칙군만 "유효"로 판정.

Grimm et al.의 POM 방법론을 Witness에 적용:
- 여러 독립적 패턴을 정의
- 시뮬레이션 결과가 각 패턴을 충족하는지 평가
- 모든 패턴을 동시에 충족하는 run만 "canonical-compatible"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.simulation.runner import SimulationResult


@dataclass
class PatternCriterion:
    """하나의 관측 패턴 기준."""

    name: str
    description: str
    evaluate: Any  # Callable[[SimulationResult], bool]



def evaluate_pom(
    result: SimulationResult,
    scorecard: list[PatternCriterion],
) -> dict[str, bool]:
    """개별 run에 대해 POM scorecard를 평가한다.

    Returns:
        {pattern_name: passed} 매핑
    """
    return {p.name: p.evaluate(result) for p in scorecard}


def pom_filter(
    results: list[SimulationResult],
    scorecard: list[PatternCriterion],
    min_patterns: int | None = None,
) -> dict[str, Any]:
    """배치 결과에 POM 필터를 적용한다.

    Args:
        results: 시뮬레이션 결과 목록
        scorecard: 패턴 기준 목록
        min_patterns: 최소 통과 패턴 수. None이면 전체 통과 필요.

    Returns:
        {
            "n_total": 총 run 수,
            "n_all_pass": 모든 패턴 통과 수,
            "all_pass_rate": 모든 패턴 통과율,
            "pattern_pass_rates": {패턴명: 통과율},
            "n_min_pass": min_patterns 이상 통과 수 (지정 시),
            "pass_counts": [각 run의 통과 패턴 수],
            "all_pass_indices": 모든 패턴 통과한 run의 인덱스,
        }
    """
    n = len(results)
    if n == 0:
        return {
            "n_total": 0, "n_all_pass": 0, "all_pass_rate": 0.0,
            "pattern_pass_rates": {}, "pass_counts": [],
            "all_pass_indices": [],
        }

    threshold = min_patterns if min_patterns is not None else len(scorecard)

    pattern_counts: dict[str, int] = {p.name: 0 for p in scorecard}
    pass_counts: list[int] = []
    all_pass_indices: list[int] = []

    for i, result in enumerate(results):
        evaluation = evaluate_pom(result, scorecard)
        count = sum(evaluation.values())
        pass_counts.append(count)

        for name, passed in evaluation.items():
            if passed:
                pattern_counts[name] += 1

        if count >= len(scorecard):
            all_pass_indices.append(i)

    n_all_pass = len(all_pass_indices)
    n_min_pass = sum(1 for c in pass_counts if c >= threshold)

    return {
        "n_total": n,
        "n_all_pass": n_all_pass,
        "all_pass_rate": n_all_pass / n if n > 0 else 0.0,
        "pattern_pass_rates": {
            name: count / n for name, count in pattern_counts.items()
        },
        "n_min_pass": n_min_pass,
        "min_pass_rate": n_min_pass / n if n > 0 else 0.0,
        "pass_counts": pass_counts,
        "all_pass_indices": all_pass_indices,
    }
