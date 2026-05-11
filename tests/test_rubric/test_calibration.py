"""Phase G Step G4 / G5 — calibration + recovery profile smoke tests."""

from __future__ import annotations

import pytest

from engine.person.recovery_profile import RECOVERY_PROFILES, DecayProfile


def test_all_variables_have_profile() -> None:
    expected = {"fear", "confusion", "anger", "awe", "grief", "guilt", "shame"}
    assert set(RECOVERY_PROFILES.keys()) == expected


def test_fear_half_life_fast() -> None:
    """fear: fast spike / fast decay (spec §5.2)."""
    assert RECOVERY_PROFILES["fear"].half_life_ticks <= 6.0


def test_grief_half_life_slow_with_floor() -> None:
    """grief: slow decay + long tail (spec §5.2)."""
    assert RECOVERY_PROFILES["grief"].half_life_ticks >= 10.0
    assert RECOVERY_PROFILES["grief"].floor > 0.0


def test_guilt_has_nonzero_floor() -> None:
    """guilt: slow decay + rebound ready (spec §5.2)."""
    assert RECOVERY_PROFILES["guilt"].floor > 0.0


def test_decay_profile_applies_toward_floor() -> None:
    p = DecayProfile(half_life_ticks=5.0, floor=0.1)
    # One tick: should decay toward floor
    v1 = p.apply(5.0)
    assert v1 < 5.0
    assert v1 > 0.1  # not yet at floor

    # Many ticks: converge to floor
    v = 5.0
    for _ in range(50):
        v = p.apply(v)
    assert abs(v - 0.1) < 0.01


def test_decay_profile_noop_below_floor() -> None:
    p = DecayProfile(half_life_ticks=5.0, floor=0.5)
    assert p.apply(0.3) == 0.3  # below floor, no change


def test_grief_retains_long_tail_echo() -> None:
    """Critical: after many ticks, grief does not reach 0.0."""
    p = RECOVERY_PROFILES["grief"]
    v = 8.0
    for _ in range(100):
        v = p.apply(v)
    # Should be close to floor, not 0
    assert v > 0.05
    assert abs(v - p.floor) < 0.1


def test_fear_decays_to_zero() -> None:
    p = RECOVERY_PROFILES["fear"]
    v = 8.0
    for _ in range(100):
        v = p.apply(v)
    assert v < 0.01
