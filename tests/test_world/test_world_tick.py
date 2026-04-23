"""Integration tests — WorldTick orchestrator + causal consistency."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from world.core.world_config import WorldConfig
from world.environment.calendar import PASSOVER_DAY, CalendarLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _load(seed: int) -> WorldConfig:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = WorldConfig.from_json(payload)
    return replace(cfg, rng_seed=seed)


def _make_runner(seed: int = 0) -> WorldTick:
    cfg = _load(seed)
    return WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )


def test_world_tick_initial_state_matches_config() -> None:
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    assert state.calendar.day_index == 0
    assert state.crowd.crowd_density == pytest.approx(1.0)
    assert "calendar" in state.telemetry
    assert "crowd" in state.telemetry


def test_world_tick_progresses_calendar_by_one_day(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    state = runner.tick(state)
    assert state.calendar.day_index == 1
    state = runner.tick(state)
    assert state.calendar.day_index == 2


def test_world_tick_passover_crowd_peak_at_least_3x_baseline() -> None:
    """Success criterion #1 — Passover peak >= 3x baseline."""
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    densities: list[float] = []
    for _ in range(30):
        state = runner.tick(state)
        densities.append(state.crowd.crowd_density)
    peak = max(densities)
    assert peak >= 3.0 * state.crowd.baseline_density


def test_world_tick_post_passover_density_declines() -> None:
    """Success criterion #2 — crowd density decreases after Passover."""
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    density_at_day: dict[int, float] = {}
    for _ in range(45):
        state = runner.tick(state)
        density_at_day[state.calendar.day_index] = state.crowd.crowd_density
    # Density at day 30 must be materially below density at Passover peak day.
    peak_density = max(
        density_at_day[d] for d in range(PASSOVER_DAY, PASSOVER_DAY + 3)
    )
    assert density_at_day[30] < 0.5 * peak_density


def test_world_tick_second_peak_at_shavuot() -> None:
    """Success criterion #3 — Shavuot produces a distinct second peak."""
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    densities = [state.crowd.crowd_density]
    for _ in range(90):
        state = runner.tick(state)
        densities.append(state.crowd.crowd_density)
    # Quiet window between 25 and 55 days.
    mid_trough = min(densities[26:55])
    shavuot_peak = max(densities[60:70])
    assert shavuot_peak > mid_trough
    assert shavuot_peak >= 3.0  # ≥ 3x baseline (reviewer #3)


def test_causal_consistency_influx_monotonically_raises_density() -> None:
    """Reviewer #7 — pilgrim influx ↑ implies crowd density ↑.

    Compares two runs: the default influx amplitude vs. a doubled one. The
    doubled-influx run must end with a higher (or equal, at ceiling) peak
    density on the *same calendar day*.
    """
    def _peak_for_amplitude(mult: float) -> float:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        payload["calendar_config"]["passover_amplitude"] *= mult
        # Lift the ceiling so both runs can be distinguished before clamping.
        payload["crowd_config"]["density_ceiling"] = 30.0
        payload["runaway_limits"]["crowd_density_ceiling"] = 30.0
        cfg = WorldConfig.from_json(payload)
        runner = WorldTick(
            calendar_layer=CalendarLayer(),
            crowd_layer=CrowdLayer(),
            config=cfg,
        )
        state = runner.initial_world_state()
        vals = []
        for _ in range(25):
            state = runner.tick(state)
            vals.append(state.crowd.crowd_density)
        return max(vals)

    base_peak = _peak_for_amplitude(1.0)
    doubled_peak = _peak_for_amplitude(2.0)
    assert doubled_peak > base_peak


def test_shabbat_count_in_90_days_matches_cadence() -> None:
    """Success criterion — Shabbat every 7 days, ~12-13 per 90 days."""
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    shabbats = []
    for _ in range(90):
        state = runner.tick(state)
        if state.calendar.is_shabbat:
            shabbats.append(state.calendar.day_index)
    assert 12 <= len(shabbats) <= 14
    diffs = {b - a for a, b in zip(shabbats, shabbats[1:])}
    assert diffs == {7}


def test_determinism_across_runs_same_seed() -> None:
    a = _make_runner(seed=5)
    b = _make_runner(seed=5)
    sa = a.initial_world_state()
    sb = b.initial_world_state()
    for _ in range(40):
        sa = a.tick(sa)
        sb = b.tick(sb)
    assert sa.crowd.crowd_density == sb.crowd.crowd_density
    assert sa.calendar.day_index == sb.calendar.day_index


def test_runaway_detector_flags_ceiling_saturation() -> None:
    """Reviewer #6 — clamp saturation is logged as a warning."""
    runner = _make_runner(seed=0)
    state = runner.initial_world_state()
    for _ in range(20):
        state = runner.tick(state)
    # Default amplitude saturates around Passover, so we expect ceiling hits.
    assert runner.runaway_detector.report.ceiling_hits >= 1
