"""Tests for target-aware variable structure (Rule #18, v2 §4)."""

from __future__ import annotations

from engine.person.state_v3 import ACTIVE_VARIABLES_META, ActiveState


def test_target_aware_default_is_empty_dict() -> None:
    s = ActiveState()
    assert s.love == {}
    assert s.loyalty == {}
    assert s.trust == {}
    assert s.belonging == {}
    assert s.guilt == {}
    assert s.shame == {}


def test_target_aware_supports_multiple_targets() -> None:
    s = ActiveState(love={
        "primary_figure": 9.0,
        "peers": 7.0,
        "family": 8.0,
    })
    assert len(s.love) == 3
    assert s.love["primary_figure"] == 9.0


def test_target_aware_values_are_independent() -> None:
    """Different targets should not alias each other."""
    s = ActiveState(
        loyalty={"primary_figure": 10.0, "peers": 3.0},
    )
    # Changing one target's value should not affect another
    s.loyalty["primary_figure"] = 5.0
    assert s.loyalty["peers"] == 3.0


def test_target_aware_metadata_has_default_targets() -> None:
    """Each target-aware variable should declare default_targets."""
    for m in ACTIVE_VARIABLES_META:
        if m.structure == "target_aware":
            assert len(m.default_targets) >= 1, (
                f"{m.name} is target_aware but has no default_targets"
            )


def test_target_aware_metadata_examples() -> None:
    """Verify the core relational variables have appropriate target seeds."""
    by_name = {m.name: m for m in ACTIVE_VARIABLES_META}
    # love targets primary_figure + peers + family
    assert "primary_figure" in by_name["love"].default_targets
    # guilt targets self and primary_figure
    assert "self" in by_name["guilt"].default_targets
    # belonging targets groups
    assert len(by_name["belonging"].default_targets) >= 2


def test_scalar_metadata_does_not_have_default_targets() -> None:
    """Scalar variables should have empty default_targets."""
    for m in ACTIVE_VARIABLES_META:
        if m.structure == "scalar":
            assert m.default_targets == [], (
                f"{m.name} is scalar but declares default_targets={m.default_targets}"
            )
