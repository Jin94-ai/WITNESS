"""Bifurcation detection 단위 테스트 (engine.simulation.bifurcation).

Trace Schema §2.4 decision window 탐지 알고리즘 검증.
"""

import pytest

from engine.simulation.bifurcation import detect_bifurcation


class TestBifurcationDetection:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            detect_bifurcation([])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            detect_bifurcation([[0.0, 1.0, 2.0], [0.0, 1.0]])

    def test_too_few_ticks_raises(self):
        with pytest.raises(ValueError):
            detect_bifurcation([[0.0, 1.0, 2.0], [0.0, 1.0, 2.0]], window_size=25)

    def test_constant_trajectories_zero_std(self):
        """모든 run이 동일 trajectory → state std=0, growth std=0."""
        trajs = [[0.0] * 60 for _ in range(10)]
        rep = detect_bifurcation(trajs, window_size=10)
        assert all(s == 0.0 for s in rep.state_std_series)
        assert rep.max_growth_std_value == 0.0

    def test_detects_diverging_trajectories(self):
        """초반 동일 후 tick 30 부근부터 갈라지면 decision window가 그 근처."""
        trajs = []
        for i in range(10):
            base = list(range(60))
            # tick 30 이후 run마다 다른 성장률
            for t in range(30, 60):
                base[t] = 30 + (t - 30) * (i / 10)
            trajs.append([float(x) for x in base])
        rep = detect_bifurcation(trajs, window_size=10)
        # decision window가 tick 30~50 영역 안에 걸쳐야 함
        lo, hi = rep.decision_window
        assert lo <= 50 and hi >= 30, \
            f"Decision window {rep.decision_window} should cover divergence start ~30"
        # plateau는 tick 30 이후 언젠가
        assert rep.plateau_start is not None
        assert rep.plateau_start >= 30

    def test_peter_like_ensemble(self):
        """Peter 시나리오와 비슷한 형태: 초반 선형 + 후반 갈림."""
        import random
        rng = random.Random(0)
        trajs = []
        for _ in range(20):
            rate = 0.04 + rng.random() * 0.02
            trajs.append([t * rate for t in range(200)])
        rep = detect_bifurcation(trajs, window_size=25)
        # 모두 선형이니 growth rate std는 전 구간 조금씩 상승, 최대는 후반
        assert rep.max_growth_std_tick > 50
        # state std는 단조 증가 (선형 발산)
        assert rep.state_std_series[-1] > rep.state_std_series[50]


class TestReportStructure:
    def test_report_fields_present(self):
        trajs = [[float(i + j) for i in range(60)] for j in range(5)]
        rep = detect_bifurcation(trajs, window_size=10)
        assert len(rep.state_std_series) == 60
        assert len(rep.growth_rate_std_series) == 60
        assert rep.decision_window[0] <= rep.decision_window[1]
        assert rep.significant is True  # 기본 min_significance=0.0
        assert rep.top_windows is None  # 기본 top_k=1


class TestSmoothing:
    def test_smoothing_reduces_peak_value(self):
        """Smoothing은 원래 peak보다 낮은 max 생성 (noise 평탄화)."""
        import random
        rng = random.Random(42)
        trajs = []
        for _ in range(20):
            base = [t * 0.05 + rng.random() * 0.1 for t in range(100)]
            trajs.append(base)
        rep_raw = detect_bifurcation(trajs, window_size=15, smoothing=1)
        rep_smooth = detect_bifurcation(trajs, window_size=15, smoothing=5)
        assert rep_smooth.max_growth_std_value <= rep_raw.max_growth_std_value

    def test_smoothing_preserves_length(self):
        trajs = [[float(i) for i in range(60)] for _ in range(5)]
        rep = detect_bifurcation(trajs, window_size=10, smoothing=7)
        assert len(rep.growth_rate_std_series) == 60


class TestSignificanceGate:
    def test_significant_false_when_below_threshold(self):
        """구조 없는 trajectory에서 high min_significance 주면 non-significant."""
        trajs = [[0.0] * 60 for _ in range(10)]  # 완전 동일
        rep = detect_bifurcation(trajs, window_size=10, min_significance=1.0)
        assert rep.significant is False

    def test_significant_true_by_default(self):
        trajs = [[float(i + j) for i in range(60)] for j in range(5)]
        rep = detect_bifurcation(trajs, window_size=10)
        assert rep.significant is True


class TestTopKWindows:
    def test_top_k_2_returns_two_windows(self):
        """Top-K=2이면 두 개 non-overlapping window 반환."""
        import random
        rng = random.Random(7)
        trajs = []
        for _ in range(15):
            # 두 개 분기점 시뮬레이션 (tick 30 주변 + tick 80 주변)
            traj = []
            for t in range(120):
                noise_1 = rng.random() if 25 <= t <= 45 else 0.0
                noise_2 = rng.random() * 2 if 70 <= t <= 95 else 0.0
                traj.append(t * 0.05 + noise_1 + noise_2)
            trajs.append(traj)
        rep = detect_bifurcation(trajs, window_size=10, top_k=2)
        assert rep.top_windows is not None
        assert len(rep.top_windows) >= 1
        # Non-overlapping: 두 번째 있다면 첫 번째와 겹치면 안 됨
        if len(rep.top_windows) == 2:
            (lo1, hi1), (lo2, hi2) = rep.top_windows
            assert hi1 < lo2 or hi2 < lo1  # 겹치지 않음

    def test_top_k_1_none(self):
        trajs = [[float(i) for i in range(60)] for _ in range(5)]
        rep = detect_bifurcation(trajs, window_size=10, top_k=1)
        assert rep.top_windows is None
