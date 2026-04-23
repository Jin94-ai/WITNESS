"""Spike 3 Phase 3A: FactionLayer unit tests (independent dynamics).

Scope:
- FactionState + FactionSnapshot shape.
- FactionLayer initial_state honours per-faction config.
- Independent drift dynamics (no cross-layer edges in Phase 3A).
- WorldTick integration keeps existing layers intact when faction_layer is None.
- DAG check: factions declares no same-tick dependencies in Phase 3A.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from world.core.layer import LayerContext
from world.core.world_state import (
    CalendarState,
    CrowdState,
    FactionState,
    WorldState,
)
from world.factions.factions import FactionLayer


def _seed_world_state() -> WorldState:
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13,
        pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=1.0,
    )
    return WorldState(calendar=cal, crowd=crowd)


def _ctx(state: WorldState, *, tick: int = 0, seed: int = 0) -> LayerContext:
    return LayerContext(
        tick_index=tick, dt_days=1.0, world_snapshot=state, rng_seed=seed,
    )


def _sample_config() -> dict:
    return {
        "influence_ceiling": 10.0,
        "factions": {
            "pharisees": {
                "initial_influence": 6.0,
                "initial_militancy": 1.0,
                "initial_roman_stance": "neutral",
                "target_influence": 5.0,
                "tau_influence": 20.0,
                "growth_rate": 0.0,
                "sigma_influence": 0.0,
                "sigma_militancy": 0.0,
            },
            "zealots": {
                "initial_influence": 2.0,
                "initial_militancy": 7.0,
                "initial_roman_stance": "resistant",
                "target_influence": 2.0,
                "tau_influence": 40.0,
                "growth_rate": 0.0,
                "sigma_influence": 0.0,
                "sigma_militancy": 0.0,
            },
        },
    }


# ----------------------------------------------------------------------
# Layer shape.

def test_initial_state_creates_configured_factions() -> None:
    layer = FactionLayer()
    state = layer.initial_state(_sample_config())
    assert isinstance(state, FactionState)
    assert set(state.factions) == {"pharisees", "zealots"}
    pharisees = state.get("pharisees")
    assert pharisees is not None
    assert pharisees.influence == pytest.approx(6.0)
    assert pharisees.roman_stance == "neutral"
    zealots = state.get("zealots")
    assert zealots is not None
    assert zealots.militancy == pytest.approx(7.0)


def test_initial_state_empty_when_no_config() -> None:
    layer = FactionLayer()
    state = layer.initial_state({})
    assert state.factions == {}


# ----------------------------------------------------------------------
# Phase 3A dynamics.

def test_influence_decays_toward_target() -> None:
    """Zero noise + target < initial → influence monotonically decreases."""
    layer = FactionLayer()
    state = layer.initial_state(_sample_config())
    world_state = _seed_world_state()
    trajectory = [state.factions["pharisees"].influence]
    for t in range(80):
        state = layer.tick(state, _ctx(world_state.with_factions(state), tick=t))
        trajectory.append(state.factions["pharisees"].influence)
    # Monotone non-increasing (noise = 0) and converges close to target.
    # tau=20 with 80 days → exp(-80/20) = exp(-4) ≈ 0.018 residual on a
    # (initial - target) = 1.0 gap, so expect trajectory end ~ 5.018.
    assert trajectory[-1] == pytest.approx(5.0, abs=0.05)
    for a, b in zip(trajectory[:-1], trajectory[1:]):
        assert b <= a + 1e-9


def test_influence_clamped_to_ceiling() -> None:
    cfg = {
        "influence_ceiling": 5.0,
        "factions": {
            "big": {
                "initial_influence": 4.9,
                "target_influence": 100.0,  # way above ceiling
                "tau_influence": 1.0,
                "growth_rate": 10.0,
                "sigma_influence": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    world_state = _seed_world_state()
    state = layer.tick(state, _ctx(world_state.with_factions(state), tick=0))
    assert state.factions["big"].influence <= 5.0
    assert layer.clamp_hits >= 1


def test_militancy_stays_in_bounds_under_random_walk() -> None:
    cfg = {
        "factions": {
            "noisy": {
                "initial_influence": 1.0, "initial_militancy": 5.0,
                "target_influence": 1.0, "sigma_influence": 0.0,
                "sigma_militancy": 2.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    world_state = _seed_world_state()
    for t in range(200):
        state = layer.tick(state, _ctx(world_state.with_factions(state), tick=t))
        mil = state.factions["noisy"].militancy
        assert 0.0 <= mil <= 10.0


def test_determinism_same_seed() -> None:
    cfg = {
        "factions": {
            "a": {
                "initial_influence": 3.0, "target_influence": 5.0,
                "tau_influence": 10.0, "sigma_influence": 0.1,
                "sigma_militancy": 0.1,
            },
        },
    }
    world_state = _seed_world_state()
    l1 = FactionLayer()
    s1 = l1.initial_state(cfg)
    l2 = FactionLayer()
    s2 = l2.initial_state(cfg)
    for t in range(15):
        s1 = l1.tick(s1, _ctx(world_state.with_factions(s1), tick=t, seed=42))
        s2 = l2.tick(s2, _ctx(world_state.with_factions(s2), tick=t, seed=42))
    assert (
        s1.factions["a"].influence == s2.factions["a"].influence
    )


# ----------------------------------------------------------------------
# DAG invariant (A-3 ABSOLUTE RULE #9).

def test_describe_dynamics_declares_expected_dependencies_phase3d() -> None:
    """Phase 3D: factions declare TWO same-tick edges.

    Transition log:
    - Phase 3A (loop #9):  []
    - Phase 3B (loop #11): ["crowd.crowd_density"]
    - Phase 3D (loop #15): ["crowd.crowd_density", "rumors.active_intensity"]

    When Phase 3E adds further edges (politics → faction stance drift),
    update this assertion consciously."""
    layer = FactionLayer()
    layer.initial_state(_sample_config())
    desc = layer.describe_dynamics()
    assert desc["layer_id"] == "factions"
    assert set(desc["causal_dependencies"]) == {
        "crowd.crowd_density", "rumors.active_intensity",
    }
    assert desc["phase"] == "3D_rumor_influence_edge"
    assert "threshold" in desc["brake_type"]
    assert "rumour" in desc["brake_type"] or "rumor" in desc["brake_type"]


def test_phase_3b_crowd_boosts_zealot_militancy() -> None:
    """Crowd ≥ threshold ⇒ zealot militancy rises; other factions unaffected."""
    cfg = {
        "militancy_crowd_threshold": 5.0,
        "militancy_step": 0.3,
        "factions": {
            "zealots": {
                "initial_influence": 2.0, "initial_militancy": 3.0,
                "target_influence": 2.0, "tau_influence": 50.0,
                "sigma_influence": 0.0, "sigma_militancy": 0.0,
            },
            "pharisees": {
                "initial_influence": 5.0, "initial_militancy": 3.0,
                "target_influence": 5.0, "tau_influence": 50.0,
                "sigma_influence": 0.0, "sigma_militancy": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    # Build a WorldState with HIGH crowd density to trigger the threshold.
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=10.0,
    )
    crowd = CrowdState(
        crowd_density=8.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=8.0,
    )
    world_state = WorldState(calendar=cal, crowd=crowd, factions=state)

    for t in range(10):
        state = layer.tick(state, _ctx(world_state.with_factions(state), tick=t))

    zealots_mil = state.factions["zealots"].militancy
    pharisees_mil = state.factions["pharisees"].militancy

    # 10 daily threshold hits × 0.3 step = 3.0 boost on top of 3.0 starting
    # value → 6.0 (assuming no clamp yet). Allow small tolerance for noise=0.
    assert zealots_mil == pytest.approx(6.0, abs=0.01)
    # Pharisees (not in threshold_factions) stays at its floor.
    assert pharisees_mil == pytest.approx(3.0, abs=0.01)
    assert layer.militancy_threshold_hits == 10


def test_phase_3b_low_crowd_does_not_boost_zealots() -> None:
    """Below threshold, zealot militancy doesn't rise from this edge."""
    cfg = {
        "militancy_crowd_threshold": 5.0,
        "militancy_step": 0.3,
        "factions": {
            "zealots": {
                "initial_influence": 2.0, "initial_militancy": 3.0,
                "target_influence": 2.0, "tau_influence": 50.0,
                "sigma_influence": 0.0, "sigma_militancy": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=2.0, baseline_density=1.0,  # below threshold 5.0
        density_ceiling=10.0, peak_density_observed=2.0,
    )
    world_state = WorldState(calendar=cal, crowd=crowd, factions=state)

    for t in range(10):
        state = layer.tick(state, _ctx(world_state.with_factions(state), tick=t))

    assert state.factions["zealots"].militancy == pytest.approx(3.0, abs=0.01)
    assert layer.militancy_threshold_hits == 0


# ----------------------------------------------------------------------
# Phase 3D: rumour → faction influence.

def test_phase_3d_rumor_boosts_jesus_movement_only() -> None:
    """Active rumours lift jesus_movement influence above its target;
    other factions (pharisees) unaffected by rumours."""
    from world.core.world_state import Rumor, RumorState
    cfg = {
        "rumor_gain_per_unit_intensity": 0.2,
        "rumor_sensitive_factions": ["jesus_movement"],
        "factions": {
            "jesus_movement": {
                "initial_influence": 1.0, "initial_militancy": 0.5,
                "target_influence": 1.0, "tau_influence": 60.0,
                "growth_rate": 0.0, "sigma_influence": 0.0,
                "sigma_militancy": 0.0,
            },
            "pharisees": {
                "initial_influence": 5.0, "initial_militancy": 0.5,
                "target_influence": 5.0, "tau_influence": 60.0,
                "growth_rate": 0.0, "sigma_influence": 0.0,
                "sigma_militancy": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    rumors = RumorState(rumors=(
        Rumor("r1", "temple", "judas", spread=0.5, credibility=0.8, age_days=1.0),
        Rumor("r2", "betrayal", "judas", spread=0.3, credibility=0.7, age_days=1.0),
    ))  # active_intensity = 0.5*0.8 + 0.3*0.7 = 0.61
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=1.0,
    )
    world = WorldState(calendar=cal, crowd=crowd, rumors=rumors, factions=state)

    for t in range(30):
        state = layer.tick(state, _ctx(world.with_factions(state), tick=t))

    jm = state.factions["jesus_movement"].influence
    phar = state.factions["pharisees"].influence
    # jesus_movement pushed above target 1.0 by sustained rumour pressure.
    assert jm > 1.5
    # pharisees stays near target (no rumour sensitivity).
    assert phar == pytest.approx(5.0, abs=0.05)
    assert layer.rumor_boost_applied_ticks == 30


def test_phase_3d_zero_rumor_intensity_leaves_jesus_movement_at_target() -> None:
    """With no rumours, jesus_movement dynamics stay Phase-3A baseline."""
    from world.core.world_state import RumorState
    cfg = {
        "rumor_gain_per_unit_intensity": 0.2,
        "rumor_sensitive_factions": ["jesus_movement"],
        "factions": {
            "jesus_movement": {
                "initial_influence": 1.0, "initial_militancy": 0.5,
                "target_influence": 1.0, "tau_influence": 20.0,
                "growth_rate": 0.0, "sigma_influence": 0.0,
                "sigma_militancy": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    empty_rumors = RumorState(rumors=())
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=1.0,
    )
    world = WorldState(
        calendar=cal, crowd=crowd, rumors=empty_rumors, factions=state,
    )

    for t in range(50):
        state = layer.tick(state, _ctx(world.with_factions(state), tick=t))

    assert state.factions["jesus_movement"].influence == pytest.approx(1.0, abs=0.05)
    assert layer.rumor_boost_applied_ticks == 0


def test_phase_3d_without_rumors_state_in_world() -> None:
    """When WorldState.rumors is None entirely, factions tick without error.

    Necessary for test_world_tick.py and any runner that omits RumorLayer."""
    cfg = {
        "factions": {
            "jesus_movement": {
                "initial_influence": 1.0, "initial_militancy": 0.5,
                "target_influence": 1.0, "tau_influence": 20.0,
                "sigma_influence": 0.0, "sigma_militancy": 0.0,
            },
        },
    }
    layer = FactionLayer()
    state = layer.initial_state(cfg)
    cal = CalendarState(
        day_index=0, hebrew_month="nisan", day_of_month=1,
        is_shabbat=False, active_feast="none",
        days_to_next_passover=13, pilgrim_influx_target=0.0,
    )
    crowd = CrowdState(
        crowd_density=1.0, baseline_density=1.0,
        density_ceiling=10.0, peak_density_observed=1.0,
    )
    world = WorldState(calendar=cal, crowd=crowd, factions=state)  # rumors=None
    for t in range(5):
        state = layer.tick(state, _ctx(world.with_factions(state), tick=t))
    # Should complete without exception; influence stays near target.
    assert state.factions["jesus_movement"].influence == pytest.approx(1.0, abs=0.05)


# ----------------------------------------------------------------------
# WorldTick integration (optional layer).

def test_world_tick_factions_only_when_layer_provided() -> None:
    """Creating a WorldTick without faction_layer keeps WorldState.factions None."""
    from world.core.world_config import WorldConfig
    from world.environment.calendar import CalendarLayer
    from world.simulation.world_tick import WorldTick
    from world.social.crowd import CrowdLayer

    cfg = WorldConfig(
        world_id="test", total_ticks=5, dt_days=1.0, rng_seed=0,
        calendar_config={"shabbat_anchor_day_index": 14},
        crowd_config={"sigma_daily": 0.0},
    )
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    state = runner.tick(state)
    assert state.factions is None


def test_world_tick_factions_present_when_layer_provided() -> None:
    from world.core.world_config import WorldConfig
    from world.environment.calendar import CalendarLayer
    from world.simulation.world_tick import WorldTick
    from world.social.crowd import CrowdLayer

    cfg = WorldConfig(
        world_id="test", total_ticks=5, dt_days=1.0, rng_seed=0,
        calendar_config={"shabbat_anchor_day_index": 14},
        crowd_config={"sigma_daily": 0.0},
        factions_config=_sample_config(),
    )
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        faction_layer=FactionLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    assert state.factions is not None
    assert set(state.factions.factions) == {"pharisees", "zealots"}

    # Advance 3 ticks, factions should tick without error.
    for _ in range(3):
        state = runner.tick(state)
    assert state.factions is not None
    assert "pharisees" in state.factions.factions


def test_absolute_rule_9_no_same_tick_cycle_after_factions_added() -> None:
    """Re-run the DAG invariant with the full Spike 3 tick order.

    Order: calendar → crowd → economy → politics → rumors → factions.
    ``aggregated_effects.*`` pseudo-dependencies are allowed (they arrive
    from the previous world-day via the Sync Layer)."""
    from world.economy.economy import EconomyLayer
    from world.environment.calendar import CalendarLayer
    from world.politics.politics import PoliticsLayer
    from world.social.crowd import CrowdLayer
    from world.social.rumors import RumorLayer

    tick_order = [
        ("calendar", CalendarLayer()),
        ("crowd",    CrowdLayer()),
        ("economy",  EconomyLayer()),
        ("politics", PoliticsLayer()),
        ("rumors",   RumorLayer()),
        ("factions", FactionLayer()),
    ]
    scheduled: set[str] = {"aggregated_effects"}  # world-level pseudo-source
    for lid, layer in tick_order:
        deps = layer.describe_dynamics().get("causal_dependencies", [])
        deps_same_tick = [d for d in deps if "@prev_tick" not in d]
        for dep in deps_same_tick:
            dep_layer = dep.split(".", 1)[0]
            assert dep_layer in scheduled, (
                f"layer '{lid}' reads same-tick from '{dep_layer}' which is "
                f"not yet scheduled. Phase 3A had no faction deps; Phase 3B "
                f"added crowd; Phase 3D added rumors. Newer same-tick edges "
                f"must point to a layer already scheduled, or be marked "
                f"'@prev_tick' to use the previous tick's value."
            )
        scheduled.add(lid)
    _ = replace  # keep import
