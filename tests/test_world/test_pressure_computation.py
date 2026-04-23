"""Tests for Layer C pressure computation (v2 §2.3, Dynamics Step 2).

Dynamics Step 2: all 8 pressures are weighted-sum + clip.
"""

from __future__ import annotations

import pytest

from engine.person.state_v3 import ActiveState
from engine.world.pressure import (
    PRESSURE_NAMES,
    EventMemory,
    PressureLayer,
    PressureVector,
)
from engine.world.primitives import PrimitiveState


def test_pressure_vector_8_fields() -> None:
    v = PressureVector()
    for name in PRESSURE_NAMES:
        assert hasattr(v, name)


def test_pressure_zero_when_social_primitives_zero() -> None:
    """social_threat = 0 when accusation/crowd/authority are 0."""
    layer = PressureLayer()
    p = PrimitiveState()  # defaults: those three are 0
    s = ActiveState()
    pv = layer.compute(p, s)
    assert pv.social_threat == 0.0
    assert pv.physical_threat == 0.0


# -----------------------------------------------------------------
# Single-component non-zero: Step 2 key property (no All-or-Nothing)
# -----------------------------------------------------------------

def test_social_threat_single_component_nonzero() -> None:
    """Weighted sum: if accusation_visibility > 0 alone, pressure > 0
    (곱셈 AND 구조였다면 0이었어야 함)."""
    layer = PressureLayer()
    p = PrimitiveState(accusation_visibility=0.5)  # crowd/authority still 0
    pv = layer.compute(p, ActiveState())
    # 5.0 * 0.5 = 2.5
    assert pv.social_threat == pytest.approx(2.5)


def test_social_threat_weighted_sum_formula() -> None:
    """social_threat = 5*accusation + 3*crowd + 2*authority, clipped [0,10]."""
    layer = PressureLayer()
    p = PrimitiveState(
        accusation_visibility=0.4, crowd_density=0.5, authority_presence=1.0,
    )
    pv = layer.compute(p, ActiveState())
    # 5*0.4 + 3*0.5 + 2*1.0 = 2.0 + 1.5 + 2.0 = 5.5
    assert pv.social_threat == pytest.approx(5.5)


def test_social_threat_saturates_at_ten() -> None:
    layer = PressureLayer()
    p = PrimitiveState(
        accusation_visibility=1.0, crowd_density=1.0, authority_presence=1.0,
    )
    pv = layer.compute(p, ActiveState())
    assert pv.social_threat == 10.0


def test_physical_threat_formula() -> None:
    layer = PressureLayer()
    p = PrimitiveState(roman_presence=0.5, volatility=0.5)
    pv = layer.compute(p, ActiveState())
    # 6*0.5 + 4*0.5 = 3 + 2 = 5
    assert pv.physical_threat == pytest.approx(5.0)


# -----------------------------------------------------------------
# Isolation: boundary cases still hold under new formula
# -----------------------------------------------------------------

def test_isolation_pressure_when_alone() -> None:
    layer = PressureLayer()
    p = PrimitiveState(group_cohesion=0.0, ally_proximity=0.0)
    pv = layer.compute(p, ActiveState())
    assert pv.isolation_pressure == 10.0


def test_isolation_pressure_when_embedded() -> None:
    layer = PressureLayer()
    p = PrimitiveState(group_cohesion=1.0, ally_proximity=1.0)
    pv = layer.compute(p, ActiveState())
    assert pv.isolation_pressure == 0.0


# -----------------------------------------------------------------
# sacred_salience: hope dependency removed, event-driven
# -----------------------------------------------------------------

def test_sacred_salience_independent_of_hope() -> None:
    """Step 2.5: sacred_salience no longer driven by hope."""
    layer = PressureLayer()
    p = PrimitiveState(religious_context=1.0)
    s_low = ActiveState(hope=0.0)
    s_high = ActiveState(hope=10.0)
    pv_low = layer.compute(p, s_low)
    pv_high = layer.compute(p, s_high)
    # both should be the same (3*1.0 contribution, no hope term)
    assert pv_low.sacred_salience == pytest.approx(pv_high.sacred_salience)


def test_sacred_salience_responds_to_recent_event() -> None:
    """Recent sacred event bumps sacred_salience via event memory."""
    layer = PressureLayer()
    p = PrimitiveState(religious_context=0.0)
    # baseline: 0
    pv0 = layer.compute(p, ActiveState())
    assert pv0.sacred_salience == 0.0
    # fire sacred event
    layer.note_event("sacred_meal", intensity=1.0)
    pv1 = layer.compute(p, ActiveState())
    assert pv1.sacred_salience > 0.0
    # decays next tick
    layer.decay_event_memory()
    pv2 = layer.compute(p, ActiveState())
    assert pv2.sacred_salience < pv1.sacred_salience


def test_sacred_salience_figure_presence_contributes() -> None:
    layer = PressureLayer()
    p = PrimitiveState(primary_figure_presence=1.0)
    pv = layer.compute(p, ActiveState())
    # 2.0 * 1.0 = 2.0 (no other terms active by default)
    assert pv.sacred_salience == pytest.approx(2.0)


def test_sacred_salience_loyalty_and_awe_minor_contribution() -> None:
    layer = PressureLayer()
    p = PrimitiveState()
    s = ActiveState(awe=10.0, loyalty={"primary_figure": 10.0})
    pv = layer.compute(p, s)
    # 1*(10/10) + 1*(10/10) = 2.0
    assert pv.sacred_salience == pytest.approx(2.0)


# -----------------------------------------------------------------
# Shame exposure: recent accusation via event memory
# -----------------------------------------------------------------

def test_shame_exposure_includes_recent_accusation() -> None:
    layer = PressureLayer()
    p = PrimitiveState(public_visibility=0.0, prior_failure_salience=0.0)
    # No accusation
    pv0 = layer.compute(p, ActiveState())
    assert pv0.shame_exposure == 0.0
    # Record accusation
    layer.note_event("public_accusation", intensity=1.0)
    pv1 = layer.compute(p, ActiveState())
    assert pv1.shame_exposure > pv0.shame_exposure
    # 3.0 * 1.0 = 3.0 from accusation memory
    assert pv1.shame_exposure == pytest.approx(3.0)


def test_set_recent_accusation_backcompat() -> None:
    """Old API compatibility: set_recent_accusation pushes into memory."""
    layer = PressureLayer()
    layer.set_recent_accusation(0.8)
    p = PrimitiveState()
    pv = layer.compute(p, ActiveState())
    # 3.0 * 0.8 = 2.4
    assert pv.shame_exposure == pytest.approx(2.4)


# -----------------------------------------------------------------
# Event memory decay
# -----------------------------------------------------------------

def test_event_memory_decays_with_half_life() -> None:
    mem = EventMemory()
    mem.sacred = 1.0
    # half-life is 5 ticks; after 5 decays should be ~0.5
    for _ in range(5):
        mem.decay()
    assert 0.4 < mem.sacred < 0.55


def test_event_memory_multiple_events_max() -> None:
    mem = EventMemory()
    mem.note_event("sacred_meal", intensity=0.6)
    mem.note_event("prayer_invitation", intensity=0.3)
    # max behaviour
    assert mem.sacred == pytest.approx(0.6)


# -----------------------------------------------------------------
# Rule #16 invariant + determinism
# -----------------------------------------------------------------

def test_pressure_not_stored_as_active() -> None:
    state = ActiveState()
    for name in PRESSURE_NAMES:
        assert not hasattr(state, name), (
            f"ActiveState has '{name}' field -- Rule #16 violation"
        )


def test_compute_is_deterministic() -> None:
    layer = PressureLayer()
    p = PrimitiveState(crowd_density=0.3, accusation_visibility=0.5)
    s = ActiveState(hope=5.0)
    pv1 = layer.compute(p, s)
    pv2 = layer.compute(p, s)
    assert pv1.to_dict() == pv2.to_dict()


def test_all_max_primitives_saturate_ten() -> None:
    """Sanity: all pressures approach 10 when all inputs maxed."""
    layer = PressureLayer()
    p = PrimitiveState(
        crowd_density=1.0, accusation_visibility=1.0, authority_presence=1.0,
        roman_presence=1.0, volatility=1.0,
        public_visibility=1.0, prior_failure_salience=1.0,
        primary_figure_presence=1.0, proximity_of_suffering=1.0,
        information_gap=1.0, decision_stakes=1.0,
        time_pressure=1.0, decision_criticality=1.0,
        group_cohesion=0.0, ally_proximity=0.0,  # isolation wants these low
        religious_context=1.0,
    )
    layer.note_event("sacred_meal", 1.0)
    layer.note_event("public_accusation", 1.0)
    pv = layer.compute(p, ActiveState(awe=10.0,
                                      loyalty={"primary_figure": 10.0}))
    for name in PRESSURE_NAMES:
        val = getattr(pv, name)
        assert val >= 9.0, f"{name} only reached {val} at max inputs"
