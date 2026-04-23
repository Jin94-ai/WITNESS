"""Unit tests — Layer 3 PoliticsLayer (Spike 1C)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from world.core.layer import LayerContext
from world.core.world_config import WorldConfig
from world.core.world_state import (
    CalendarState,
    CrowdState,
    PoliticsState,
    WorldState,
)
from world.environment.calendar import PASSOVER_DAY, SHAVUOT_DAY, CalendarLayer
from world.politics.politics import PoliticsLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _make_state(
    *, crowd_density: float, alertness: float = 2.0,
    day_index: int = 0, active_feast: str = "none",
) -> WorldState:
    cal = CalendarState(
        day_index=day_index, hebrew_month="nisan", day_of_month=1 + day_index,
        is_shabbat=False, active_feast=active_feast,
        days_to_next_passover=max(0, PASSOVER_DAY - day_index),
        pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=crowd_density, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=crowd_density,
    )
    pol = PoliticsState(
        roman_alertness=alertness, alertness_floor=2.0,
        alertness_ceiling=10.0, pilate_location="caesarea",
        crowd_threshold_exceeded_ticks=0,
    )
    return WorldState(calendar=cal, crowd=crowd, politics=pol)


def _ctx(state: WorldState, *, tick: int = 0, seed: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=seed,
    )


@pytest.fixture()
def politics() -> PoliticsLayer:
    layer = PoliticsLayer()
    layer.initial_state({
        "alertness_floor": 2.0, "alertness_ceiling": 10.0,
        "alert_tau_days": 4.0, "crowd_trigger_threshold": 5.0,
        "threshold_step": 1.5, "pilate_bonus": 0.4,
        "sigma_daily": 0.0, "initial_alertness": 2.0,
    })
    return layer


def test_initial_state_honours_config() -> None:
    p = PoliticsLayer()
    state = p.initial_state({
        "alertness_floor": 1.0, "alertness_ceiling": 8.0,
        "initial_alertness": 3.0,
    })
    assert state.alertness_floor == 1.0
    assert state.roman_alertness == 3.0
    assert state.pilate_location == "caesarea"


def test_low_crowd_leaves_alertness_near_floor(politics: PoliticsLayer) -> None:
    """Reviewer #2 threshold brake — crowd below threshold does NOT raise alertness."""
    state = _make_state(crowd_density=3.0, alertness=4.0)
    s = state.politics
    for t in range(20):
        s = politics.tick(s, _ctx(state.with_politics(s), tick=t))
    # After 20 days without threshold trip, alertness decays toward floor.
    assert s.roman_alertness == pytest.approx(2.0, abs=0.1)


def test_high_crowd_raises_alertness(politics: PoliticsLayer) -> None:
    """Reviewer #7 causal — sustained crowd above threshold raises alertness."""
    state = _make_state(crowd_density=8.0, alertness=2.0)
    s = state.politics
    for t in range(10):
        s = politics.tick(s, _ctx(state.with_politics(s), tick=t))
    # 10 daily threshold hits × 1.5 step >> 0 — alertness well above floor.
    assert s.roman_alertness > 5.0
    assert politics.threshold_hits >= 10


def test_pilate_location_jerusalem_during_passover(politics: PoliticsLayer) -> None:
    state = _make_state(
        crowd_density=3.0, day_index=PASSOVER_DAY,
        active_feast="passover",
    )
    out = politics.tick(state.politics, _ctx(state, tick=0))
    assert out.pilate_location == "jerusalem"


def test_pilate_location_jerusalem_during_shavuot(politics: PoliticsLayer) -> None:
    state = _make_state(
        crowd_density=3.0, day_index=SHAVUOT_DAY,
        active_feast="shavuot",
    )
    out = politics.tick(state.politics, _ctx(state, tick=0))
    assert out.pilate_location == "jerusalem"


def test_pilate_location_caesarea_on_ordinary_day(politics: PoliticsLayer) -> None:
    state = _make_state(crowd_density=3.0, day_index=40)
    out = politics.tick(state.politics, _ctx(state, tick=0))
    assert out.pilate_location == "caesarea"


def test_pilate_approach_window_before_passover(politics: PoliticsLayer) -> None:
    # approach_lead_days = 4 (default); so day 9..12 → Jerusalem.
    state = _make_state(crowd_density=3.0, day_index=10)
    out = politics.tick(state.politics, _ctx(state, tick=0))
    assert out.pilate_location == "jerusalem"


def test_alertness_clamped_to_ceiling() -> None:
    p = PoliticsLayer()
    p.initial_state({
        "alertness_floor": 0.0, "alertness_ceiling": 5.0,
        "alert_tau_days": 100.0,  # effectively no decay
        "crowd_trigger_threshold": 1.0, "threshold_step": 10.0,
        "pilate_bonus": 0.0, "sigma_daily": 0.0,
        "initial_alertness": 0.0,
    })
    state = _make_state(crowd_density=8.0, alertness=0.0)
    state = state.with_politics(PoliticsState(
        roman_alertness=0.0, alertness_floor=0.0, alertness_ceiling=5.0,
        pilate_location="caesarea", crowd_threshold_exceeded_ticks=0,
    ))
    out = p.tick(state.politics, _ctx(state, tick=0))
    assert out.roman_alertness <= 5.0
    assert p.clamp_hits >= 1


def test_threshold_hits_counter_correct(politics: PoliticsLayer) -> None:
    """Threshold brake transparency — the counter increments exactly when
    crowd >= threshold on a tick."""
    state = _make_state(crowd_density=5.5, alertness=2.0)
    s = state.politics
    for t in range(5):
        s = politics.tick(s, _ctx(state.with_politics(s), tick=t))
    assert s.crowd_threshold_exceeded_ticks == 5


def test_world_tick_passover_alertness_spike() -> None:
    """Integration — full world tick produces alertness spike around Passover."""
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=0)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        politics_layer=PoliticsLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    alerts = []
    for _ in range(30):
        state = runner.tick(state)
        alerts.append(state.politics.roman_alertness)
    floor = state.politics.alertness_floor
    # Baseline before any pilgrim arrival.
    baseline = alerts[2]
    # Passover-window peak.
    peak = max(alerts[13:22])
    assert peak >= baseline + 3.0  # clearly elevated
    # Day 30 should have relaxed (though not all the way to floor).
    assert alerts[29] < peak
    assert alerts[29] >= floor


def test_describe_dynamics_lists_dependencies(politics: PoliticsLayer) -> None:
    desc = politics.describe_dynamics()
    assert desc["layer_id"] == "politics"
    assert "calendar.active_feast" in desc["causal_dependencies"]
    assert "crowd.crowd_density" in desc["causal_dependencies"]
    assert "threshold" in desc["brake_type"]
