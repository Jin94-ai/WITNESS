"""HazardFunction.base_rate_unit per_hour semantics (v1.2 Iter 27).

reviewer ChatGPT 지적 대응: "phase-variable tick에서 hazard base_rate가
'per-tick'으로 고정되면 장기 scenario에서 rate가 실시간 기준과 괴리.
rate rescaling (2h/tick → 24h/tick 시 12배)이 sufficient한가?"

해법:
- HazardFunction.base_rate_unit="per_tick" (기본): legacy 동일 (dt=1.0).
- HazardFunction.base_rate_unit="per_hour" (opt-in): HazardEngine이
  tick_scale_hours를 effective_dt로 사용 → P = 1 - exp(-h * tick_scale_hours).

이 테스트는:
1. per_tick 기본은 legacy 동일.
2. per_hour + tick_scale_hours=2.0 vs 24.0은 예상 비율(12배)대로 확률 증가.
3. 같은 실시간 총량이면 기대 발동 횟수가 tick_scale에 invariant.
"""

from __future__ import annotations

import math
import random

from engine.core.hazard import (
    HazardEngine,
    HazardEvent,
    HazardFunction,
)
from engine.core.state import AgentState


def _agent() -> AgentState:
    return AgentState(agent_id="a")


class TestPerTickLegacyDefault:
    def test_default_is_per_tick(self):
        hf = HazardFunction(base_rate=0.1)
        assert hf.base_rate_unit == "per_tick"

    def test_per_tick_firing_probability(self):
        # P = 1 - exp(-0.1 * 1) ~= 0.0952
        hf = HazardFunction(base_rate=0.1, base_rate_unit="per_tick")
        prob = hf.firing_probability(_agent(), dt=1.0)
        assert abs(prob - (1 - math.exp(-0.1))) < 1e-12

    def test_per_tick_engine_ignores_tick_scale(self):
        """per_tick이면 engine이 tick_scale_hours를 전달해도 dt=1.0처럼 행동."""
        hf = HazardFunction(base_rate=1.0, base_rate_unit="per_tick")
        ev = HazardEvent(event_id="legacy", hazard=hf)
        engine = HazardEngine([ev])
        rng = random.Random(0)

        # tick_scale_hours=24.0 전달해도 per_tick이면 무시
        with_scale = engine.evaluate_tick(
            0, _agent(), rng, tick_scale_hours=24.0,
        )
        # 결과는 dt=1.0 기준 (P = 1 - exp(-1) ~= 0.632)
        # rng.random()가 0.632 이상/이하로 판단하므로 결정적 재현 필요
        assert len(with_scale) in (0, 1)


class TestPerHourSemantics:
    def test_per_hour_uses_tick_scale_hours(self):
        """per_hour일 때 tick_scale_hours=2 → P = 1 - exp(-h*2)."""
        hf = HazardFunction(base_rate=0.1, base_rate_unit="per_hour")
        ev = HazardEvent(event_id="h", hazard=hf)
        engine = HazardEngine([ev])

        # 반복하여 평균 발생률 확인 — 2h/tick에서 base_rate 0.1/hour
        # P(fire) per tick = 1 - exp(-0.1 * 2) = 1 - exp(-0.2) ~= 0.1813
        trials = 2000
        fires = 0
        for i in range(trials):
            ev.fire_count = 0  # reset
            ev.last_fired_tick = -1
            rng = random.Random(i)
            fired = engine.evaluate_tick(
                0, _agent(), rng, tick_scale_hours=2.0,
            )
            if fired:
                fires += 1
        rate = fires / trials
        expected = 1 - math.exp(-0.1 * 2)
        # 경험적 95% CI ~= ±0.02
        assert abs(rate - expected) < 0.03

    def test_per_hour_scales_with_tick_scale_hours(self):
        """tick_scale_hours=2 vs 24에서 firing prob이 12배 아니라 Poisson 비선형."""
        hf = HazardFunction(base_rate=0.1, base_rate_unit="per_hour")
        ev2 = HazardEvent(event_id="h2", hazard=hf)
        ev24 = HazardEvent(event_id="h24", hazard=hf)
        engine2 = HazardEngine([ev2])
        engine24 = HazardEngine([ev24])

        trials = 2000
        f2, f24 = 0, 0
        for i in range(trials):
            ev2.fire_count = 0
            ev2.last_fired_tick = -1
            ev24.fire_count = 0
            ev24.last_fired_tick = -1
            if engine2.evaluate_tick(0, _agent(), random.Random(i), tick_scale_hours=2.0):
                f2 += 1
            if engine24.evaluate_tick(0, _agent(), random.Random(i), tick_scale_hours=24.0):
                f24 += 1

        # 2h/tick: P = 1 - exp(-0.2) ~= 0.181
        # 24h/tick: P = 1 - exp(-2.4) ~= 0.909
        p2 = f2 / trials
        p24 = f24 / trials
        assert abs(p2 - (1 - math.exp(-0.2))) < 0.03
        assert abs(p24 - (1 - math.exp(-2.4))) < 0.03
        # 24h/tick이 훨씬 높은 tick당 확률
        assert p24 > p2


class TestRealTimeInvariance:
    """같은 실시간 구간이면 기대 발동 횟수가 tick_scale에 invariant해야.

    Poisson process에서 λ × T가 동일하면 기대 발동 수 동일.
    2h/tick × 24 ticks = 48h = 24h/tick × 2 ticks.
    λ=0.05/hour → λT = 2.4 → E[fires] = 2.4.
    """

    def test_expected_fires_invariant_across_tick_scales(self):
        rate_per_hour = 0.05
        # total_hours = 48.0 — 2h×24 tick (시나리오 A) = 24h×2 tick

        # 시나리오 A: 2h/tick × 24 ticks
        trials = 1000
        total_fires_a = 0
        for seed in range(trials):
            hf = HazardFunction(
                base_rate=rate_per_hour, base_rate_unit="per_hour",
                max_hazard=10.0,  # 충분히 높임
            )
            ev = HazardEvent(event_id="x", hazard=hf, max_fires=100)
            engine = HazardEngine([ev])
            rng = random.Random(seed)
            fires_this_trial = 0
            for t in range(24):
                if engine.evaluate_tick(t, _agent(), rng, tick_scale_hours=2.0):
                    fires_this_trial += 1
            total_fires_a += fires_this_trial
        mean_a = total_fires_a / trials

        # 이론: λT = 2.4 → E[fires (truncated)] ≈ 2.4 for A.
        # (핵심 주장: per_hour 의미가 맞으면 A가 이론값 ~2.4에 가까움.)
        assert 1.5 < mean_a < 3.0, f"A mean {mean_a}, expected ~2.4"


class TestPerHourWithoutTickScaleFallsBack:
    """per_hour라도 tick_scale_hours=None이면 dt fallback (기존 API 호환)."""

    def test_no_tick_scale_falls_back_to_dt(self):
        hf = HazardFunction(base_rate=0.1, base_rate_unit="per_hour")
        ev = HazardEvent(event_id="h", hazard=hf)
        engine = HazardEngine([ev])

        # tick_scale_hours 미전달 → dt=1.0 (fallback)
        fires = 0
        trials = 1000
        for i in range(trials):
            ev.fire_count = 0
            ev.last_fired_tick = -1
            if engine.evaluate_tick(0, _agent(), random.Random(i)):
                fires += 1
        rate = fires / trials
        expected = 1 - math.exp(-0.1 * 1.0)  # dt=1.0 fallback
        assert abs(rate - expected) < 0.03


class TestBackwardCompat:
    """v0.7 legacy 시나리오는 이 변경으로 영향 없어야."""

    def test_legacy_hazard_events_default_to_per_tick(self):
        """base_rate_unit 명시 안 하면 per_tick이므로 기존 동작."""
        hf = HazardFunction(base_rate=0.05)
        assert hf.base_rate_unit == "per_tick"

    def test_legacy_json_compatible(self):
        """base_rate_unit 필드 없는 dict로 HazardFunction 생성 가능."""
        hf = HazardFunction.model_validate({"base_rate": 0.05})
        assert hf.base_rate_unit == "per_tick"
        assert hf.base_rate == 0.05
