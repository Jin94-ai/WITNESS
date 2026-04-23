"""Tests for availability gate (Dynamics Step 3)."""

from __future__ import annotations

from engine.action.availability_gate import (
    AVAILABILITY,
    DEFAULT_FALLBACK,
    GateContext,
    filter_available,
    is_available,
)
from engine.person.state_v3 import ActiveState
from engine.world.primitives import PrimitiveState


def _ctx(
    *, state: ActiveState | None = None,
    primitives: PrimitiveState | None = None,
    recent: dict[str, int] | None = None,
    tick: int = 10,
) -> GateContext:
    return GateContext(
        state=state or ActiveState(),
        primitives=primitives or PrimitiveState(),
        recent_events=recent or {},
        tick_index=tick,
    )


# -----------------------------------------------------------------
# STRICT gates: blocked by default, open only with specific context
# -----------------------------------------------------------------

def test_run_to_tomb_blocked_without_resurrection_context() -> None:
    assert not is_available("run_to_tomb", _ctx())


def test_run_to_tomb_open_with_restoration_moment() -> None:
    ctx = _ctx(recent={"restoration_moment": 1})
    assert is_available("run_to_tomb", ctx)


def test_run_to_tomb_open_with_miracle_witnessed() -> None:
    ctx = _ctx(recent={"miracle_witnessed": 2})
    assert is_available("run_to_tomb", ctx)


def test_draw_sword_blocked_without_threat() -> None:
    s = ActiveState(anger=7.0)
    assert not is_available("draw_sword", _ctx(state=s))


def test_draw_sword_open_with_guard_approaches_and_anger() -> None:
    s = ActiveState(anger=5.0)
    ctx = _ctx(state=s, recent={"guard_approaches": 0})
    assert is_available("draw_sword", ctx)


def test_draw_sword_blocked_if_anger_low_even_with_threat() -> None:
    s = ActiveState(anger=1.0)
    ctx = _ctx(state=s, recent={"guard_approaches": 0})
    assert not is_available("draw_sword", ctx)


def test_deny_blocked_without_accusation() -> None:
    s = ActiveState(fear=8.0)
    assert not is_available("deny", _ctx(state=s))


def test_deny_open_with_recent_accusation() -> None:
    ctx = _ctx(recent={"public_accusation": 0})
    assert is_available("deny", ctx)


def test_deny_blocked_after_accusation_aging() -> None:
    ctx = _ctx(recent={"public_accusation": 3})  # aged beyond within=1
    assert not is_available("deny", ctx)


def test_confess_blocked_when_guilt_low_and_no_forgiveness() -> None:
    s = ActiveState(guilt={"primary_figure": 1.0})
    assert not is_available("confess", _ctx(state=s))


def test_confess_open_on_high_guilt() -> None:
    s = ActiveState(guilt={"primary_figure": 7.0})
    assert is_available("confess", _ctx(state=s))


def test_confess_open_after_forgiveness_offered() -> None:
    ctx = _ctx(recent={"forgiveness_offered": 2})
    assert is_available("confess", ctx)


def test_flee_blocked_without_concrete_threat() -> None:
    s = ActiveState(fear=9.0)
    assert not is_available("flee", _ctx(state=s))


def test_flee_open_with_guard_approaches_and_fear() -> None:
    s = ActiveState(fear=6.0)
    ctx = _ctx(state=s, recent={"guard_approaches": 1})
    assert is_available("flee", ctx)


# -----------------------------------------------------------------
# LOOSE gates: always available
# -----------------------------------------------------------------

def test_follow_closely_always_available() -> None:
    assert is_available("follow_closely", _ctx())


def test_discuss_with_disciples_always_available() -> None:
    assert is_available("discuss_with_disciples", _ctx())


def test_unknown_action_defaults_available() -> None:
    assert is_available("invented_action_xyz", _ctx())


# -----------------------------------------------------------------
# filter_available + fallback
# -----------------------------------------------------------------

def test_filter_available_returns_only_permitted() -> None:
    s = ActiveState(anger=0.0, fear=0.0, grief=0.0, resolve=0.0,
                    loyalty={}, guilt={}, shame={})
    ctx = _ctx(state=s)
    candidates = list(AVAILABILITY.keys())
    survivors = filter_available(candidates, ctx)
    # Strict gates must be excluded
    assert "run_to_tomb" not in survivors
    assert "deny" not in survivors
    assert "draw_sword" not in survivors
    assert "flee" not in survivors
    # Loose gates must survive
    assert "follow_closely" in survivors


def test_filter_available_fallback_when_all_blocked() -> None:
    # Fabricate a context where almost nothing passes, but
    # DEFAULT_FALLBACK items (follow_closely always True) should still appear.
    ctx = _ctx()
    survivors = filter_available(["run_to_tomb", "draw_sword", "deny"], ctx)
    # All three blocked → fallback used
    assert set(survivors).issubset(set(DEFAULT_FALLBACK) | {"follow_closely"})
    assert "follow_closely" in survivors


# -----------------------------------------------------------------
# Registry shape
# -----------------------------------------------------------------

def test_minimum_ten_actions_have_gates() -> None:
    """Step 3 completion criterion: ≥10 actions with explicit gate."""
    assert len(AVAILABILITY) >= 10
