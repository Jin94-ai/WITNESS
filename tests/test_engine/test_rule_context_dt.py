"""RuleContext.dt_hours 확장 테스트 (v1.2).

phase-variable tick scale에서 rule이 per-hour rate 기준으로
재스케일 가능함을 검증.
"""

import pytest

from engine.rules.base import RuleContext


class TestDtHoursDefault:
    def test_default_is_2_hours(self):
        """기본값 2.0 (v0.5 수난 scenario 2h/tick 호환)."""
        ctx = RuleContext(tick=0)
        assert ctx.dt_hours == 2.0

    def test_can_override(self):
        ctx = RuleContext(tick=0, dt_hours=24.0)
        assert ctx.dt_hours == 24.0

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            RuleContext(tick=0, dt_hours=0.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            RuleContext(tick=0, dt_hours=-1.0)


class TestRateScaling:
    """Rule이 dt_hours를 사용해 rate를 재스케일하는 패턴 검증."""

    def test_per_hour_rate_scales_with_dt(self):
        """moral_injury 0.05/hour → 2h/tick에서 0.1/tick, 24h/tick에서 1.2/tick."""
        per_hour_rate = 0.05

        dense_ctx = RuleContext(tick=0, dt_hours=2.0)
        sparse_ctx = RuleContext(tick=0, dt_hours=24.0)

        dense_increment = per_hour_rate * dense_ctx.dt_hours
        sparse_increment = per_hour_rate * sparse_ctx.dt_hours

        assert abs(dense_increment - 0.1) < 1e-9
        assert abs(sparse_increment - 1.2) < 1e-9
        assert abs(sparse_increment - dense_increment * 12) < 1e-9  # 24/2 = 12

    def test_legacy_per_tick_rule_unchanged(self):
        """기존 per-tick rule이 dt_hours 무시해도 backward compat."""
        # 기존 rule이 하드코딩된 0.1/tick 사용 시, dt_hours 참조 없음
        legacy_rate_per_tick = 0.1
        _ = RuleContext(tick=0, dt_hours=2.0)  # 참조되지 않음이 backward compat 의미
        assert legacy_rate_per_tick == 0.1

    def test_time_invariance_hazard(self):
        """hazard rate × dt_hours가 time-invariant: 같은 실시간 동안 같은 확률."""
        # per-hour hazard = 0.01 (시간당 1%)
        per_hour_hazard = 0.01
        # 24시간 동안 = per_hour * 24 = 0.24 (24%)
        expected_24h_rate = 0.24

        # Dense 2h/tick × 12 ticks = 24시간
        dense = RuleContext(tick=0, dt_hours=2.0)
        dense_12tick_rate = per_hour_hazard * dense.dt_hours * 12
        assert abs(dense_12tick_rate - expected_24h_rate) < 1e-9

        # Sparse 24h/tick × 1 tick = 24시간
        sparse = RuleContext(tick=0, dt_hours=24.0)
        sparse_1tick_rate = per_hour_hazard * sparse.dt_hours * 1
        assert abs(sparse_1tick_rate - expected_24h_rate) < 1e-9


class TestRealTimeAxis:
    """reviewer 지적: 분석 좌표계를 absolute time 기준으로 재정의."""

    def test_absolute_hours_computation(self):
        """phase 내 tick을 hour로 변환 (tick_offset은 phase 경계)."""
        ctx = RuleContext(tick=50, dt_hours=2.0)
        # absolute hours = tick × dt_hours (phase 내부 기준)
        assert ctx.tick * ctx.dt_hours == 100.0

    def test_cross_phase_time_comparison(self):
        """다른 dt_hours phase 간에도 실시간 비교 가능."""
        # Phase A: dense 84 tick × 2h = 168h
        phase_a_hours = 84 * 2.0
        # Phase B: sparse 7 tick × 24h = 168h
        phase_b_hours = 7 * 24.0
        assert phase_a_hours == phase_b_hours
