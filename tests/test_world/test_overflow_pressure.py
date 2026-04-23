"""A-2: overflow_pressure tests."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from world.core.layer import LayerContext
from world.core.world_config import WorldConfig
from world.core.world_state import CalendarState, CrowdState, WorldState
from world.environment.calendar import PASSOVER_DAY, CalendarLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _make_state(influx: float, density: float = 1.0) -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=PASSOVER_DAY,
        pilgrim_influx_target=influx,
    )
    crowd = CrowdState(
        crowd_density=density, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=density,
    )
    return WorldState(calendar=cal, crowd=crowd)


def _ctx(state: WorldState, *, tick: int = 0, seed: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=seed,
    )


def test_overflow_zero_on_initial_state() -> None:
    c = CrowdLayer()
    state = c.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "initial_density": 5.0,
    })
    assert state.overflow_pressure == 0.0


def test_overflow_zero_when_density_below_ceiling() -> None:
    c = CrowdLayer()
    c.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.0, "initial_density": 2.0,
    })
    state = _make_state(influx=1.0, density=2.0)
    out = c.tick(state.crowd, _ctx(state))
    assert out.overflow_pressure == 0.0
    assert out.crowd_density <= 10.0


def test_overflow_positive_when_ceiling_hit() -> None:
    """Massive influx must produce overflow_pressure > 0 even though the
    clamped density stops at the ceiling."""
    c = CrowdLayer()
    c.initial_state({
        "baseline_density": 1.0, "density_ceiling": 10.0,
        "tau_days": 3.5, "inflow_weight": 0.30,
        "sigma_daily": 0.0, "initial_density": 9.0,
    })
    state = _make_state(influx=200.0, density=9.0)
    out = c.tick(state.crowd, _ctx(state))
    assert out.crowd_density == 10.0
    assert out.overflow_pressure > 0.0


def test_passover_peak_has_overflow() -> None:
    """Default Jerusalem AD-30 config saturates on Passover — we should see
    non-zero overflow_pressure on at least one tick in that window."""
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=0)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    overflow_days: list[float] = []
    for _ in range(30):
        state = runner.tick(state)
        overflow_days.append(state.crowd.overflow_pressure)
    passover_window = overflow_days[10:20]
    assert any(p > 0.0 for p in passover_window)


def test_overflow_decays_post_passover() -> None:
    """After the Passover window, overflow_pressure should return to 0."""
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=0)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    overflow_by_day: dict[int, float] = {}
    for _ in range(40):
        state = runner.tick(state)
        overflow_by_day[state.calendar.day_index] = state.crowd.overflow_pressure
    # By day 25 (5 days after UB ends), overflow should be 0 — city drained.
    assert overflow_by_day[25] == 0.0
    assert overflow_by_day[30] == 0.0


def test_overflow_propagates_through_world_state() -> None:
    """WorldState.crowd.overflow_pressure is readable after a tick (not just
    inside the layer)."""
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=0)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    for _ in range(14):  # up to Passover
        state = runner.tick(state)
    assert hasattr(state.crowd, "overflow_pressure")
    assert state.crowd.overflow_pressure >= 0.0
