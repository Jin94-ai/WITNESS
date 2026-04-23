"""Unit tests — Layer 5 crowd density (Spike 1A)."""

from __future__ import annotations

import pytest

from world.core.layer import LayerContext
from world.core.world_state import CalendarState, CrowdState, WorldState
from world.environment.calendar import PASSOVER_DAY
from world.social.crowd import CrowdLayer


def _make_state(influx: float, density: float = 1.0) -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=PASSOVER_DAY,
        pilgrim_influx_target=influx,
    )
    crowd = CrowdState(
        crowd_density=density, baseline_density=1.0, density_ceiling=10.0,
        peak_density_observed=density,
    )
    return WorldState(calendar=cal, crowd=crowd)


def _ctx(state: WorldState, *, tick: int = 0, seed: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=seed,
    )


@pytest.fixture()
def crowd() -> CrowdLayer:
    layer = CrowdLayer()
    layer.initial_state({
        "baseline_density": 1.0,
        "density_ceiling": 10.0,
        "tau_days": 3.5,
        "inflow_weight": 0.30,
        "sigma_daily": 0.0,  # zero noise for deterministic tests
        "initial_density": 1.0,
    })
    return layer


def test_crowd_initial_state_honours_config() -> None:
    c = CrowdLayer()
    state = c.initial_state({
        "baseline_density": 2.0, "density_ceiling": 20.0,
        "initial_density": 5.0,
    })
    assert state.baseline_density == 2.0
    assert state.density_ceiling == 20.0
    assert state.crowd_density == 5.0


def test_zero_influx_decays_toward_baseline(crowd: CrowdLayer) -> None:
    state = _make_state(influx=0.0, density=8.0)
    s = state.crowd
    # 40 days of zero influx — should converge close to baseline (exp decay).
    for t in range(40):
        s = crowd.tick(s, _ctx(state.with_crowd(s), tick=t))
    assert s.crowd_density == pytest.approx(1.0, abs=0.01)


def test_higher_influx_yields_higher_density(crowd: CrowdLayer) -> None:
    low = _make_state(influx=1.0)
    high = _make_state(influx=8.0)
    c_low = crowd.tick(low.crowd, _ctx(low, tick=0, seed=7))
    # Reset the layer (so clamp counters are isolated) before the second call.
    crowd2 = CrowdLayer()
    crowd2.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.0, "initial_density": 1.0,
    })
    c_high = crowd2.tick(high.crowd, _ctx(high, tick=0, seed=7))
    assert c_high.crowd_density > c_low.crowd_density


def test_density_clamped_to_ceiling(crowd: CrowdLayer) -> None:
    state = _make_state(influx=100.0, density=9.0)
    out = crowd.tick(state.crowd, _ctx(state, tick=0))
    assert out.crowd_density <= state.crowd.density_ceiling
    assert crowd.clamp_hits >= 1


def test_density_clamped_to_baseline(crowd: CrowdLayer) -> None:
    # Force negative drift by starting below baseline — layer should clamp up.
    c = CrowdLayer()
    c.initial_state({
        "baseline_density": 2.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.0,
        "sigma_daily": 0.0, "initial_density": 0.5,  # will clamp to 2.0
    })
    state = _make_state(influx=0.0, density=0.5)
    state = WorldState(
        calendar=state.calendar,
        crowd=CrowdState(
            crowd_density=0.5, baseline_density=2.0,
            density_ceiling=10.0, peak_density_observed=0.5,
        ),
    )
    out = c.tick(state.crowd, _ctx(state, tick=0))
    assert out.crowd_density >= 2.0


def test_determinism_same_seed(crowd: CrowdLayer) -> None:
    state = _make_state(influx=5.0)
    # Two independent layer instances with sigma > 0 should produce identical
    # sequences for identical seeds.
    a = CrowdLayer()
    a.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.1, "initial_density": 1.0,
    })
    b = CrowdLayer()
    b.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.1, "initial_density": 1.0,
    })
    sa = state.crowd
    sb = state.crowd
    for t in range(30):
        sa = a.tick(sa, _ctx(state, tick=t, seed=42))
        sb = b.tick(sb, _ctx(state, tick=t, seed=42))
    assert sa.crowd_density == sb.crowd_density


def test_determinism_different_seed_diverges() -> None:
    state = _make_state(influx=5.0)
    a = CrowdLayer()
    a.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.2, "initial_density": 1.0,
    })
    b = CrowdLayer()
    b.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.2, "initial_density": 1.0,
    })
    sa = state.crowd
    sb = state.crowd
    for t in range(30):
        sa = a.tick(sa, _ctx(state, tick=t, seed=1))
        sb = b.tick(sb, _ctx(state, tick=t, seed=2))
    assert sa.crowd_density != sb.crowd_density


def test_describe_dynamics_lists_causal_dependency(crowd: CrowdLayer) -> None:
    desc = crowd.describe_dynamics()
    assert desc["layer_id"] == "crowd"
    assert "calendar.pilgrim_influx_target" in desc["causal_dependencies"]
    assert desc["tau_days"] == 3.5
    assert desc["inflow_weight"] == 0.30
