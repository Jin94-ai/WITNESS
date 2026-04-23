"""통계적 분석 헬퍼.

ChatGPT 피드백: "분포적으로, 통계적으로, 구조적으로 그렇다"를 보여주기 위한
confidence interval, effect size, statistical test 유틸.
"""

from __future__ import annotations

import math
import statistics
from typing import NamedTuple


class CIResult(NamedTuple):
    """Confidence interval 결과."""

    mean: float
    lower: float
    upper: float
    std: float
    n: int
    ci_level: float  # e.g. 0.95


class EffectSizeResult(NamedTuple):
    """Effect size (Cohen's d)."""

    cohens_d: float
    interpretation: str  # "negligible", "small", "medium", "large"
    mean_diff: float
    pooled_std: float


def confidence_interval(
    values: list[float],
    ci_level: float = 0.95,
) -> CIResult:
    """95% confidence interval (t-distribution 근사 -> normal 근사).

    n >= 30이면 normal 근사로 충분.
    """
    n = len(values)
    if n < 2:
        m = values[0] if n == 1 else 0.0
        return CIResult(mean=m, lower=m, upper=m, std=0.0, n=n, ci_level=ci_level)

    mean = statistics.mean(values)
    std = statistics.stdev(values)
    sem = std / math.sqrt(n)  # standard error of mean

    # 95% = 1.96 normal approximation (n >= 30 good)
    # t-critical for smaller n is slightly wider but this is ensemble-level
    z = 1.96 if ci_level == 0.95 else 2.576  # 95% or 99%
    margin = z * sem

    return CIResult(
        mean=mean,
        lower=mean - margin,
        upper=mean + margin,
        std=std,
        n=n,
        ci_level=ci_level,
    )


def cohens_d(group_a: list[float], group_b: list[float]) -> EffectSizeResult:
    """Cohen's d effect size.

    |d| 해석:
    - < 0.2: negligible
    - 0.2 ~ 0.5: small
    - 0.5 ~ 0.8: medium
    - > 0.8: large
    """
    if len(group_a) < 2 or len(group_b) < 2:
        return EffectSizeResult(
            cohens_d=0.0, interpretation="insufficient",
            mean_diff=0.0, pooled_std=0.0,
        )

    m_a = statistics.mean(group_a)
    m_b = statistics.mean(group_b)
    s_a = statistics.stdev(group_a)
    s_b = statistics.stdev(group_b)
    n_a = len(group_a)
    n_b = len(group_b)

    # Pooled standard deviation
    pooled_var = (
        ((n_a - 1) * s_a**2 + (n_b - 1) * s_b**2) / (n_a + n_b - 2)
    )
    pooled_std = math.sqrt(pooled_var) if pooled_var > 0 else 1e-10

    d = (m_a - m_b) / pooled_std
    abs_d = abs(d)

    if abs_d < 0.2:
        interp = "negligible"
    elif abs_d < 0.5:
        interp = "small"
    elif abs_d < 0.8:
        interp = "medium"
    else:
        interp = "large"

    return EffectSizeResult(
        cohens_d=d,
        interpretation=interp,
        mean_diff=m_a - m_b,
        pooled_std=pooled_std,
    )


def proportion_ci(
    successes: int,
    total: int,
    ci_level: float = 0.95,
) -> CIResult:
    """이항 비율의 Wilson score confidence interval.

    proportion(예: spontaneous rate)에 대한 CI.
    Normal approximation (Wald)은 극단값에서 부정확하므로 Wilson 사용.
    """
    if total == 0:
        return CIResult(mean=0.0, lower=0.0, upper=0.0, std=0.0, n=0, ci_level=ci_level)

    p = successes / total
    z = 1.96 if ci_level == 0.95 else 2.576

    # Wilson score
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    half_width = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom

    std = math.sqrt(p * (1 - p) / total) if total > 0 else 0.0

    return CIResult(
        mean=p,
        lower=max(0.0, center - half_width),
        upper=min(1.0, center + half_width),
        std=std,
        n=total,
        ci_level=ci_level,
    )


def format_ci(ci: CIResult, as_pct: bool = False) -> str:
    """CI를 'mean [lower, upper]' 형식으로."""
    if as_pct:
        return f"{ci.mean:.1%} [{ci.lower:.1%}, {ci.upper:.1%}]"
    return f"{ci.mean:.1f} [{ci.lower:.1f}, {ci.upper:.1f}]"
