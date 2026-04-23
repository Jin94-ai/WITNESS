"""Spike 3 Phase 3C: RumorLayer skeleton unit tests."""

from __future__ import annotations

import pytest

from world.core.layer import LayerContext
from world.core.world_state import (
    CalendarState,
    CrowdState,
    Rumor,
    RumorState,
    WorldState,
)
from world.social.rumors import RumorLayer


def _world(*, crowd_density: float = 1.0) -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=crowd_density, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=crowd_density,
    )
    return WorldState(calendar=cal, crowd=crowd)


def _ctx(state: WorldState, *, tick: int = 0, effects: dict | None = None) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=0,
        aggregated_effects=effects or {},
    )


def _config(**overrides) -> dict:
    base = {
        "spread_rate_per_day": 0.05,
        "spread_decay_per_day": 0.03,
        "credibility_decay_per_day": 0.02,
        "initial_spread": 0.1,
        "initial_credibility": 0.8,
        "max_age_days": 30.0,
        "max_active_rumors": 40,
        "seed_content": "test_rumor",
    }
    base.update(overrides)
    return base


# ----------------------------------------------------------------------
# Shape & empty init.

def test_initial_state_empty_when_no_seeds() -> None:
    layer = RumorLayer()
    state = layer.initial_state(_config())
    assert isinstance(state, RumorState)
    assert state.rumors == ()
    assert state.seeded_total == 0


def test_initial_state_loads_seed_rumors() -> None:
    layer = RumorLayer()
    state = layer.initial_state({
        **_config(),
        "initial_rumors": [
            {"content": "temple incident", "source_agent": "peter",
             "spread": 0.2, "credibility": 0.9, "age_days": 0.0},
            {"content": "zealot sighting", "source_agent": "crowd",
             "spread": 0.1, "credibility": 0.6, "age_days": 5.0},
        ],
    })
    assert len(state.rumors) == 2
    assert state.seeded_total == 2
    r0 = state.rumors[0]
    assert r0.content == "temple incident"
    assert r0.spread == pytest.approx(0.2)


# ----------------------------------------------------------------------
# Independent dynamics.

def test_spread_rises_in_busy_city() -> None:
    layer = RumorLayer()
    state = layer.initial_state({
        **_config(),
        "initial_rumors": [{"content": "x", "source_agent": "a",
                            "spread": 0.1, "credibility": 0.9,
                            "age_days": 0.0}],
    })
    world = _world(crowd_density=8.0)
    prev = state.rumors[0].spread
    for t in range(5):
        state = layer.tick(state, _ctx(world.with_rumors(state), tick=t))
    new = state.rumors[0].spread
    assert new > prev


def test_spread_decays_in_quiet_city() -> None:
    layer = RumorLayer()
    state = layer.initial_state({
        **_config(spread_rate_per_day=0.05, spread_decay_per_day=0.03),
        "initial_rumors": [{"content": "x", "source_agent": "a",
                            "spread": 0.5, "credibility": 0.9,
                            "age_days": 0.0}],
    })
    # crowd == baseline → drive = 0 → no new spread, only decay.
    world = _world(crowd_density=1.0)
    prev = state.rumors[0].spread
    for t in range(10):
        state = layer.tick(state, _ctx(world.with_rumors(state), tick=t))
    assert state.rumors[0].spread < prev


def test_credibility_monotonically_decays() -> None:
    layer = RumorLayer()
    state = layer.initial_state({
        **_config(credibility_decay_per_day=0.05),
        "initial_rumors": [{"content": "x", "source_agent": "a",
                            "spread": 0.3, "credibility": 0.9,
                            "age_days": 0.0}],
    })
    world = _world(crowd_density=1.0)
    creds = [state.rumors[0].credibility]
    for t in range(5):
        state = layer.tick(state, _ctx(world.with_rumors(state), tick=t))
        creds.append(state.rumors[0].credibility)
    for a, b in zip(creds[:-1], creds[1:]):
        assert b <= a + 1e-9


def test_rumor_expires_after_max_age() -> None:
    layer = RumorLayer()
    state = layer.initial_state({
        **_config(max_age_days=5.0),
        "initial_rumors": [{"content": "x", "source_agent": "a",
                            "spread": 0.5, "credibility": 0.9,
                            "age_days": 4.0}],
    })
    world = _world(crowd_density=2.0)
    # 3 day ticks should push age past 5.0.
    for t in range(3):
        state = layer.tick(state, _ctx(world.with_rumors(state), tick=t))
    assert state.rumors == ()
    assert state.expired_total >= 1


# ----------------------------------------------------------------------
# Seeding from aggregated_effects.

def test_rumor_seed_creates_new_rumor() -> None:
    layer = RumorLayer()
    state = layer.initial_state(_config())
    world = _world(crowd_density=3.0)
    # No effect → no new rumour.
    state = layer.tick(state, _ctx(world.with_rumors(state), tick=0))
    assert len(state.rumors) == 0

    # Threshold effect fires (1.0 from SyncLayer THRESHOLD aggregation).
    state = layer.tick(state, _ctx(
        world.with_rumors(state), tick=1, effects={"rumor_seed": 1.0},
    ))
    assert len(state.rumors) == 1
    assert state.seeded_total == 1
    assert state.rumors[0].content == "test_rumor"


def test_seed_cap_respected() -> None:
    layer = RumorLayer()
    cfg = {**_config(max_active_rumors=3), "seed_content": "x"}
    state = layer.initial_state(cfg)
    world = _world(crowd_density=2.0)
    for t in range(10):
        state = layer.tick(
            state,
            _ctx(world.with_rumors(state), tick=t,
                 effects={"rumor_seed": 1.0}),
        )
    assert len(state.rumors) <= 3


# ----------------------------------------------------------------------
# Active intensity helper.

def test_active_intensity_sums_spread_times_credibility() -> None:
    rumors = (
        Rumor("r1", "x", "a", spread=0.5, credibility=0.6, age_days=1.0),
        Rumor("r2", "y", "b", spread=0.3, credibility=0.4, age_days=2.0),
    )
    state = RumorState(rumors=rumors)
    assert state.active_intensity() == pytest.approx(0.5 * 0.6 + 0.3 * 0.4)


def test_active_intensity_empty_is_zero() -> None:
    state = RumorState()
    assert state.active_intensity() == 0.0


# ----------------------------------------------------------------------
# describe_dynamics + DAG.

def test_describe_dynamics_declares_crowd_and_aggregated_deps() -> None:
    layer = RumorLayer()
    layer.initial_state(_config())
    desc = layer.describe_dynamics()
    assert desc["layer_id"] == "rumors"
    deps = desc["causal_dependencies"]
    assert "crowd.crowd_density" in deps
    assert "aggregated_effects.rumor_seed" in deps
    assert "saturation" in desc["brake_type"]


# ----------------------------------------------------------------------
# WorldTick integration.

def test_world_tick_runs_with_rumor_layer_and_produces_nothing_by_default() -> None:
    from world.core.world_config import WorldConfig
    from world.environment.calendar import CalendarLayer
    from world.simulation.world_tick import WorldTick
    from world.social.crowd import CrowdLayer

    cfg = WorldConfig(
        world_id="test", total_ticks=10, dt_days=1.0, rng_seed=0,
        calendar_config={"shabbat_anchor_day_index": 14},
        crowd_config={"sigma_daily": 0.0},
        rumors_config=_config(),
    )
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        rumor_layer=RumorLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    assert state.rumors is not None
    for _ in range(10):
        state = runner.tick(state)
    # No initial rumours + no seeds → still empty, but field persists.
    assert state.rumors is not None
    assert state.rumors.rumors == ()
