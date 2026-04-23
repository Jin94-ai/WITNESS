"""Unit tests — Layer 2 EconomyLayer (Spike 1B)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from world.core.layer import LayerContext
from world.core.world_config import WorldConfig
from world.core.world_state import CalendarState, CrowdState, EconomyState, WorldState
from world.economy.economy import EconomyLayer
from world.environment.calendar import PASSOVER_DAY, CalendarLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _seed_state(influx: float = 0.0, price: float = 1.0) -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=PASSOVER_DAY,
        pilgrim_influx_target=influx,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=1.0,
    )
    econ = EconomyState(
        staple_price=price, price_floor=1.0,
        price_ceiling=10.0, demand_pressure_3d_avg=0.0,
    )
    return WorldState(calendar=cal, crowd=crowd, economy=econ)


def _ctx(state: WorldState, *, tick: int = 0, seed: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=seed,
    )


@pytest.fixture()
def econ() -> EconomyLayer:
    layer = EconomyLayer()
    layer.initial_state({
        "price_floor": 1.0, "price_ceiling": 10.0,
        "price_tau_days": 5.0, "demand_weight": 0.08,
        "demand_memory": 0.66, "sigma_daily": 0.0,  # deterministic
        "initial_price": 1.0,
    })
    return layer


def test_initial_state_honours_config() -> None:
    e = EconomyLayer()
    state = e.initial_state({
        "price_floor": 2.0, "price_ceiling": 20.0, "initial_price": 5.0,
    })
    assert state.price_floor == 2.0
    assert state.price_ceiling == 20.0
    assert state.staple_price == 5.0


def test_zero_influx_decays_to_floor(econ: EconomyLayer) -> None:
    state = _seed_state(influx=0.0, price=7.0)
    s = state.economy
    for t in range(40):
        s = econ.tick(s, _ctx(state.with_economy(s), tick=t))
    assert s.staple_price == pytest.approx(1.0, abs=0.01)


def test_sustained_influx_raises_price_with_delay(econ: EconomyLayer) -> None:
    """Reviewer #2 — the 3-day IIR brake means price rises *gradually*, not
    instantly, after a demand spike."""
    state = _seed_state(influx=8.0, price=1.0)
    s = state.economy
    prices = [s.staple_price]
    for t in range(12):
        s = econ.tick(s, _ctx(state.with_economy(s), tick=t))
        prices.append(s.staple_price)
    # Day 1: small movement (demand_3d still low).
    assert prices[1] - prices[0] < 0.5
    # Day 10: clearly elevated.
    assert prices[10] > prices[0] + 0.2
    # Monotone non-decreasing when noise is zero (brake + sustained demand).
    for a, b in zip(prices[:-1], prices[1:]):
        assert b >= a - 1e-9


def test_price_clamped_to_ceiling() -> None:
    e = EconomyLayer()
    e.initial_state({
        "price_floor": 1.0, "price_ceiling": 5.0,
        "price_tau_days": 5.0, "demand_weight": 1.0,
        "demand_memory": 0.0,  # no brake — any influx hits ceiling
        "sigma_daily": 0.0, "initial_price": 4.5,
    })
    state = _seed_state(influx=100.0, price=4.5)
    # Need a fresh WorldState with ceiling=5 for the econ
    state = state.with_economy(EconomyState(
        staple_price=4.5, price_floor=1.0, price_ceiling=5.0,
        demand_pressure_3d_avg=0.0,
    ))
    out = e.tick(state.economy, _ctx(state, tick=0))
    assert out.staple_price <= 5.0
    assert e.clamp_hits >= 1


def test_describe_dynamics_lists_dependency(econ: EconomyLayer) -> None:
    desc = econ.describe_dynamics()
    assert desc["layer_id"] == "economy"
    assert "calendar.pilgrim_influx_target" in desc["causal_dependencies"]
    assert "delay" in desc["brake_type"] and "saturation" in desc["brake_type"]


def test_world_tick_with_economy_passover_price_peak() -> None:
    """Reviewer #7 causal consistency — prices must peak during/after Passover.

    Also verifies the delay brake: the price peak should *lag* the crowd peak
    by a few days, not coincide exactly with it.
    """
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=0)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        economy_layer=EconomyLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    prices = []
    for _ in range(30):
        state = runner.tick(state)
        prices.append(state.economy.staple_price)
    baseline_day = prices[2]
    passover_window_peak = max(prices[13:20])
    assert passover_window_peak > baseline_day
    # Price peak should lag the Passover peak: max price in post-feast window.
    post_passover_peak = max(prices[14:20])
    pre_passover = max(prices[8:12])
    assert post_passover_peak > pre_passover  # lag confirmed
