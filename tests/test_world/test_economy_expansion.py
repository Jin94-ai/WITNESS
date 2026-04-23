"""Spike 5 Phase 5D — Temple + Taxation + Cross-economy behavior tests.

Per spec §4.4: counterfactual tests banned; pure behavior tests only.
"""

from __future__ import annotations

from pathlib import Path

from world.economy import (
    CrossEconomyCoordinator,
    TaxationInputs,
    TaxationLayer,
    TempleEconomyInputs,
    TempleEconomyLayer,
)

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLE_CFG = (
    ROOT / "content" / "worlds" / "jerusalem_ad30" / "economy" / "temple_economy_config.json"
)
TAXATION_CFG = (
    ROOT / "content" / "worlds" / "jerusalem_ad30" / "economy" / "taxation_config.json"
)


# =====================================================================
# Phase 5D.1 — Temple Economy.

def test_temple_economy_passover_price_spike() -> None:
    """Spec §4.4 #1 — passover multiplies fee and sacrifice price."""
    layer = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    state = layer.initial_state()
    base_fee = state.money_changer_fee
    base_sac = state.sacrifice_animal_price
    out = layer.tick(state, TempleEconomyInputs(active_feast="passover", dt_days=1.0))
    assert out.money_changer_fee > base_fee
    assert out.sacrifice_animal_price > base_sac
    # Crowd frustration rises under passover pressure.
    assert out.crowd_frustration > state.crowd_frustration


def test_jesus_temple_cleansing_disrupts_money_changer() -> None:
    """Spec §4.4 #2 — cleansing fired last tick drops fee + sacrifice."""
    layer = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    state = layer.initial_state()
    # First raise with passover to give a visible delta.
    high = layer.tick(state, TempleEconomyInputs(active_feast="passover", dt_days=1.0))
    dropped = layer.tick(
        high,
        TempleEconomyInputs(
            active_feast="none", jesus_cleansing_fired_last_tick=True, dt_days=1.0,
        ),
    )
    assert dropped.money_changer_fee < high.money_changer_fee
    assert dropped.sacrifice_animal_price < high.sacrifice_animal_price


def test_caiaphas_temple_decree_adjusts_sacrifice_price() -> None:
    """Spec §4.4 #3 — decree intensity moves sacrifice price."""
    layer = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    state = layer.initial_state()
    up = layer.tick(
        state,
        TempleEconomyInputs(
            active_feast="none",
            caiaphas_decree_intensity_last_tick=1.0,
            dt_days=1.0,
        ),
    )
    down = layer.tick(
        state,
        TempleEconomyInputs(
            active_feast="none",
            caiaphas_decree_intensity_last_tick=-1.0,
            dt_days=1.0,
        ),
    )
    assert up.sacrifice_animal_price > state.sacrifice_animal_price
    assert down.sacrifice_animal_price < state.sacrifice_animal_price


# =====================================================================
# Phase 5D.2 — Roman Taxation.

def test_pilate_political_pressure_raises_taxation_intensity() -> None:
    """Spec §4.4 #4."""
    layer = TaxationLayer.from_config_path(TAXATION_CFG)
    state = layer.initial_state()
    high_pressure = layer.tick(
        state, TaxationInputs(pilate_political_pressure_last_tick=0.9, dt_days=1.0),
    )
    no_pressure = layer.tick(
        state, TaxationInputs(pilate_political_pressure_last_tick=0.0, dt_days=1.0),
    )
    assert high_pressure.collection_intensity > no_pressure.collection_intensity


def test_taxation_spike_increases_zealot_militancy_channel() -> None:
    """Spec §4.4 #5 — taxation.intensity feeds zealot.militancy channel."""
    layer = TaxationLayer.from_config_path(TAXATION_CFG)
    state = layer.initial_state()
    # Pump intensity high over a few ticks.
    s = state
    for _ in range(5):
        s = layer.tick(s, TaxationInputs(pilate_political_pressure_last_tick=1.0, dt_days=1.0))
    militancy_signal_high = layer.zealot_militancy_channel(s)
    militancy_signal_baseline = layer.zealot_militancy_channel(state)
    assert militancy_signal_high > militancy_signal_baseline
    assert militancy_signal_high > 0.0


# =====================================================================
# Phase 5D.3 — Cross-economy.

def test_temple_shock_reaches_jesus_movement_via_crowd_frustration() -> None:
    """Spec §4.4 #6 — indirect path temple → crowd_frustration → jesus.sympathy."""
    temple = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    tax = TaxationLayer.from_config_path(TAXATION_CFG)
    coord = CrossEconomyCoordinator(temple=temple, taxation=tax)

    t_state = temple.initial_state()
    x_state = tax.initial_state()
    baseline_channels = coord.snapshot_channels(
        temple_state=t_state, taxation_state=x_state, staple_price=1.0,
    )
    # Run passover for several days to accumulate crowd_frustration.
    for _ in range(3):
        t_state = temple.tick(
            t_state, TempleEconomyInputs(active_feast="passover", dt_days=1.0),
        )
    raised = coord.snapshot_channels(
        temple_state=t_state, taxation_state=x_state, staple_price=1.0,
    )
    assert raised.temple_to_jesus_sympathy > baseline_channels.temple_to_jesus_sympathy
    assert raised.temple_to_jesus_sympathy > 0.0


def test_three_economies_independent_but_connected() -> None:
    """Spec §4.4 #7 — temple, taxation, staple each evolve independently;
    cross-coordinator exposes all three channels.
    """
    temple = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    tax = TaxationLayer.from_config_path(TAXATION_CFG)
    coord = CrossEconomyCoordinator(temple=temple, taxation=tax)

    t_state = temple.initial_state()
    x_state = tax.initial_state()

    # Move only temple (passover).
    t_after = temple.tick(
        t_state, TempleEconomyInputs(active_feast="passover", dt_days=1.0),
    )
    assert t_after.money_changer_fee != t_state.money_changer_fee
    # Taxation untouched by the temple tick.
    assert x_state.collection_intensity == tax.initial_state().collection_intensity

    # Move only taxation (pilate pressure).
    x_after = tax.tick(
        x_state, TaxationInputs(pilate_political_pressure_last_tick=0.8, dt_days=1.0),
    )
    assert x_after.collection_intensity != x_state.collection_intensity
    # Temple state is not coupled to taxation's tick.
    assert t_state.money_changer_fee == temple.initial_state().money_changer_fee

    channels = coord.snapshot_channels(
        temple_state=t_after, taxation_state=x_after, staple_price=3.0,
    )
    # All three channels exist (independent layers connected through coord).
    assert channels.staple_to_discontent > 0.0
    assert channels.taxation_to_zealot_militancy > 0.0
    # Temple frustration only rose one tick (small but non-negative).
    assert channels.temple_to_jesus_sympathy >= 0.0


def test_no_same_tick_feedback_in_economy_layer() -> None:
    """Spec §4.4 #8 (ABSOLUTE RULE #9 guard) — a change in pilate_pressure
    this tick must NOT loop back into the same-tick output of the coord.

    Check: calling ``tick`` once with high pressure must produce a NEXT
    state whose zealot-militancy channel has risen, but the SAME-TICK
    coord snapshot (using *this* tick's input state) has not yet.
    """
    tax = TaxationLayer.from_config_path(TAXATION_CFG)
    temple = TempleEconomyLayer.from_config_path(TEMPLE_CFG)
    coord = CrossEconomyCoordinator(temple=temple, taxation=tax)

    t_state = temple.initial_state()
    x_state = tax.initial_state()

    pre_channels = coord.snapshot_channels(
        temple_state=t_state, taxation_state=x_state, staple_price=1.0,
    )
    # Apply high pressure: the NEW state is produced but not yet visible
    # to a consumer that still holds the pre-tick state.
    x_next = tax.tick(
        x_state, TaxationInputs(pilate_political_pressure_last_tick=0.9, dt_days=1.0),
    )
    # Same-tick consumer still sees pre_channels (no feedback).
    assert pre_channels.taxation_to_zealot_militancy == tax.zealot_militancy_channel(x_state)
    # Next-substep consumer sees the raised channel.
    next_channels = coord.snapshot_channels(
        temple_state=t_state, taxation_state=x_next, staple_price=1.0,
    )
    assert next_channels.taxation_to_zealot_militancy > pre_channels.taxation_to_zealot_militancy
