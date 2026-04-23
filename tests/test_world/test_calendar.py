"""Unit tests — Layer 1 Jewish calendar (Spike 1A)."""

from __future__ import annotations

import pytest

from world.core.layer import LayerContext
from world.core.world_state import CalendarState, CrowdState, WorldState
from world.environment.calendar import (
    FIRSTFRUITS_DAY,
    PASSOVER_DAY,
    SHAVUOT_DAY,
    UNLEAVENED_END,
    UNLEAVENED_START,
    CalendarLayer,
)


def _seed_state() -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=PASSOVER_DAY,
        pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0, density_ceiling=10.0,
        peak_density_observed=1.0,
    )
    return WorldState(calendar=cal, crowd=crowd)


def _ctx(state: WorldState, tick: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=0,
    )


@pytest.fixture()
def layer() -> CalendarLayer:
    layer = CalendarLayer()
    layer.initial_state({"shabbat_anchor_day_index": 14})
    return layer


def test_initial_state_is_nisan_1(layer: CalendarLayer) -> None:
    state = layer.initial_state({"shabbat_anchor_day_index": 14})
    assert state.day_index == 0
    assert state.hebrew_month == "nisan"
    assert state.day_of_month == 1
    assert state.active_feast == "none"


def test_passover_lands_on_nisan_14(layer: CalendarLayer) -> None:
    state = _seed_state()
    world = state
    for t in range(20):
        world = world.with_calendar(layer.tick(world.calendar, _ctx(world, t)))
    # After 13 forward ticks from day 0, we are at day_index=13 == Nisan 14.
    assert world.calendar.day_index == 20  # loop advanced 20 ticks
    # Inspect specific day via the layer's helper.
    cal_at_passover = layer._state_at(PASSOVER_DAY)
    assert cal_at_passover.hebrew_month == "nisan"
    assert cal_at_passover.day_of_month == 14
    assert cal_at_passover.active_feast == "passover"


def test_unleavened_bread_spans_nisan_15_to_21(layer: CalendarLayer) -> None:
    for d in range(UNLEAVENED_START, UNLEAVENED_END + 1):
        cal = layer._state_at(d)
        if d == FIRSTFRUITS_DAY:
            assert cal.active_feast == "firstfruits"
        else:
            assert cal.active_feast == "unleavened_bread"


def test_firstfruits_is_nisan_16(layer: CalendarLayer) -> None:
    cal = layer._state_at(FIRSTFRUITS_DAY)
    assert cal.hebrew_month == "nisan"
    assert cal.day_of_month == 16
    assert cal.active_feast == "firstfruits"


def test_shavuot_is_sivan_6_and_50_days_inclusive_from_firstfruits(
    layer: CalendarLayer,
) -> None:
    cal = layer._state_at(SHAVUOT_DAY)
    assert cal.hebrew_month == "sivan"
    assert cal.day_of_month == 6
    assert cal.active_feast == "shavuot"
    # Lev 23:15-16: 50 days counted from Firstfruits (inclusive).
    # Firstfruits = day 15; Shavuot = day 64 → delta 49 → 50 inclusive days.
    assert SHAVUOT_DAY - FIRSTFRUITS_DAY == 49


def test_shabbat_recurs_every_7_days(layer: CalendarLayer) -> None:
    # shabbat_anchor_day_index was 14 in fixture; (d - 14) % 7 == 0.
    shabbat_days = [d for d in range(90) if layer._state_at(d).is_shabbat]
    assert shabbat_days, "no Shabbat detected in 90-day window"
    # All consecutive pairs 7 days apart.
    diffs = {b - a for a, b in zip(shabbat_days, shabbat_days[1:])}
    assert diffs == {7}, f"shabbat cadence broken: diffs={diffs}"


def test_days_to_next_passover_counts_down(layer: CalendarLayer) -> None:
    # Before Passover the field decreases by 1 each day.
    d5 = layer._state_at(5)
    d6 = layer._state_at(6)
    assert d5.days_to_next_passover - d6.days_to_next_passover == 1
    # After Passover it is clamped to 0 (no second-year passover in Spike 1A).
    d14 = layer._state_at(14)
    assert d14.days_to_next_passover == 0


def test_pilgrim_influx_peaks_at_passover_and_shavuot(layer: CalendarLayer) -> None:
    influx = [layer.pilgrim_influx(d) for d in range(90)]
    # Two clear maxima — one at Passover, one at Shavuot.
    passover_val = influx[PASSOVER_DAY]
    shavuot_val = influx[SHAVUOT_DAY]
    # Not the global max but clearly a local max at both feasts.
    for offset in (-3, -1, 1, 3):
        assert influx[PASSOVER_DAY + offset] <= passover_val
        assert influx[SHAVUOT_DAY + offset] <= shavuot_val


def test_pilgrim_influx_is_non_negative(layer: CalendarLayer) -> None:
    for d in range(120):
        assert layer.pilgrim_influx(d) >= 0.0


def test_describe_dynamics_exposes_feast_days(layer: CalendarLayer) -> None:
    desc = layer.describe_dynamics()
    assert desc["layer_id"] == "calendar"
    assert desc["feast_days"]["passover"] == PASSOVER_DAY
    assert desc["feast_days"]["shavuot"] == SHAVUOT_DAY
