"""Bifurcation Point Detection (Trace Schema §2.4).

Ensemble trajectory에서 결과가 갈라지기 시작하는 "decision window" 자동 탐지.
v2.0 renderer가 플레이어에게 긴장감을 강조할 시점 감지용.

방법:
- 여러 run의 state trajectory를 정렬
- tick별 cross-run std (분산)를 계산
- std가 상승해 plateau 직전의 "ascending flank" = decision window
- Growth rate std (시간당 상태 변화량의 cross-run std)도 병행

참조:
- test_tick100_analysis.py — decision window 75-100 (growth std 0.69, max)
- test_cross_decision_window.py (example): 시나리오 A 20-40%, 시나리오 B 60-80%
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass
class BifurcationReport:
    """Decision window / bifurcation 탐지 결과 (trace entry §2.4 예정)."""

    decision_window: tuple[int, int]
    """갈림이 가장 활발한 tick 구간 (growth rate std 최대)."""

    plateau_start: int | None
    """상태 std가 고정되기 시작한 tick (갈래 완성)."""

    max_growth_std_tick: int
    """Growth rate std가 최대가 되는 tick."""

    max_growth_std_value: float
    """Growth rate std 최대값."""

    state_std_series: list[float]
    """tick별 state cross-run std."""

    growth_rate_std_series: list[float]
    """tick별 growth rate cross-run std."""

    significant: bool = True
    """min_significance 문턱 이상인가. False면 bifurcation 없음/약함."""

    top_windows: list[tuple[int, int]] | None = None
    """Top-K candidate windows (옵션, top_k > 1 때). 가장 강한 것이 decision_window."""


def _moving_average(series: list[float], k: int) -> list[float]:
    """k-point centered moving average. k<=1이면 원본 반환."""
    if k <= 1 or len(series) < k:
        return list(series)
    out = [0.0] * len(series)
    half = k // 2
    for i in range(len(series)):
        lo = max(0, i - half)
        hi = min(len(series), i + half + 1)
        window = series[lo:hi]
        out[i] = sum(window) / len(window)
    return out


def _find_non_overlapping_peaks(
    series: list[float], top_k: int, min_gap: int,
) -> list[int]:
    """Top-K peaks, 상호 >= min_gap tick 간격. Greedy."""
    if not series:
        return []
    indexed = sorted(
        range(len(series)), key=lambda i: series[i], reverse=True,
    )
    picked: list[int] = []
    for idx in indexed:
        if all(abs(idx - p) >= min_gap for p in picked):
            picked.append(idx)
            if len(picked) >= top_k:
                break
    return picked


def detect_bifurcation(
    trajectories: list[list[float]],
    window_size: int = 25,
    *,
    smoothing: int = 1,
    min_significance: float = 0.0,
    top_k: int = 1,
) -> BifurcationReport:
    """여러 run의 state trajectory에서 bifurcation 구간 탐지.

    Args:
        trajectories: [[state_at_tick_0, state_at_tick_1, ...], ...] (run마다 길이 같아야)
        window_size: growth rate 계산에 쓸 window (default 25 tick)
        smoothing: growth rate std에 적용할 centered moving-average window (1=비적용).
            Noisy ensemble에서 spurious peak 억제.
        min_significance: growth rate std 최대값이 이 값 미만이면 significant=False.
            0.0 (기본)이면 항상 significant.
        top_k: 반환할 non-overlapping candidate windows 수 (default 1).
            둘 이상이면 top_windows 필드 채워짐.

    Returns:
        BifurcationReport

    Raises:
        ValueError: trajectories가 비거나 길이가 다르면.
    """
    if not trajectories:
        raise ValueError("Empty trajectories")
    n_ticks = len(trajectories[0])
    if any(len(t) != n_ticks for t in trajectories):
        raise ValueError("Trajectory lengths must match")
    if n_ticks < window_size + 1:
        raise ValueError(f"Need >= {window_size + 1} ticks")

    # tick별 cross-run std
    state_std_series: list[float] = []
    for t in range(n_ticks):
        vals = [tr[t] for tr in trajectories]
        if len(vals) > 1:
            state_std_series.append(statistics.stdev(vals))
        else:
            state_std_series.append(0.0)

    # Growth rate: state[t] - state[t-window_size], cross-run std
    raw_growth_std: list[float] = [0.0] * window_size
    for t in range(window_size, n_ticks):
        deltas = [tr[t] - tr[t - window_size] for tr in trajectories]
        if len(deltas) > 1:
            raw_growth_std.append(statistics.stdev(deltas))
        else:
            raw_growth_std.append(0.0)

    # Smoothing (optional)
    growth_rate_std_series = _moving_average(raw_growth_std, smoothing)

    # Decision window = growth rate std 최대인 주변 window
    max_idx = max(
        range(len(growth_rate_std_series)),
        key=lambda i: growth_rate_std_series[i],
    )
    max_val = growth_rate_std_series[max_idx]

    # Decision window: max_idx 중심 ± window_size/2
    lo = max(0, max_idx - window_size // 2)
    hi = min(n_ticks - 1, max_idx + window_size // 2)

    # Top-K candidate windows (옵션)
    top_windows: list[tuple[int, int]] | None = None
    if top_k > 1:
        # min_gap = window_size + 1 ensures strict non-overlap of ± window_size/2 windows
        peaks = _find_non_overlapping_peaks(
            growth_rate_std_series, top_k, min_gap=window_size + 1,
        )
        top_windows = [
            (max(0, p - window_size // 2), min(n_ticks - 1, p + window_size // 2))
            for p in peaks
        ]

    # Plateau: state_std가 max의 90% 이상에 도달한 첫 tick
    peak_state_std = max(state_std_series) if state_std_series else 0.0
    plateau_start: int | None = None
    if peak_state_std > 0:
        threshold = peak_state_std * 0.9
        for t, s in enumerate(state_std_series):
            if s >= threshold:
                plateau_start = t
                break

    significant = max_val >= min_significance

    return BifurcationReport(
        decision_window=(lo, hi),
        plateau_start=plateau_start,
        max_growth_std_tick=max_idx,
        max_growth_std_value=max_val,
        state_std_series=state_std_series,
        growth_rate_std_series=growth_rate_std_series,
        significant=significant,
        top_windows=top_windows,
    )
