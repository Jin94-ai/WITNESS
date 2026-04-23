"""Tests for state transition direct edges (Dynamics Step 4)."""

from __future__ import annotations

from engine.person.state_transitions import (
    StateTransitionEngine,
    TransitionContext,
)
from engine.person.state_v3 import ActiveState
from engine.world.primitives import PrimitiveState


def _apply(
    *, state: ActiveState, primitives: PrimitiveState | None = None,
    events: list[str] | None = None,
) -> ActiveState:
    engine = StateTransitionEngine()
    ctx = TransitionContext(events_this_tick=events or [])
    engine.apply(state, primitives or PrimitiveState(), ctx)
    return state


# ==============================================================
# Category A — 외부 이벤트 → 내부 상태
# ==============================================================

def test_A1_accusation_visible_raises_fear_shame_confusion() -> None:
    s = ActiveState(fear=1.0, confusion=1.0, shame={"crowd": 0.0})
    p = PrimitiveState(accusation_visibility=0.8)
    _apply(state=s, primitives=p)
    assert s.fear > 1.0
    assert s.shame["crowd"] > 0.0
    assert s.confusion > 1.0


def test_A3_guard_approaches_bumps_fear_and_anger() -> None:
    s = ActiveState(fear=2.0, anger=1.0)
    _apply(state=s, events=["guard_approaches"])
    assert s.fear > 2.0
    assert s.anger > 1.0


def test_A4_weapon_drawn_bumps_fear_and_confusion() -> None:
    s = ActiveState(fear=1.0, confusion=1.0)
    _apply(state=s, events=["weapon_drawn_nearby"])
    assert s.fear > 1.0
    assert s.confusion > 1.0


def test_A2_public_visibility_bumps_shame_crowd() -> None:
    s = ActiveState(shame={"crowd": 0.0})
    p = PrimitiveState(public_visibility=0.8)
    _apply(state=s, primitives=p)
    assert s.shame["crowd"] > 0.0


# ==============================================================
# Category B — 가시적 고통/상실
# ==============================================================

def test_B1_primary_figure_suffering_raises_grief_awe_loyalty() -> None:
    s = ActiveState(grief=0.5, awe=5.0, loyalty={"primary_figure": 8.0})
    p = PrimitiveState(proximity_of_suffering=0.8, primary_figure_visible=True)
    _apply(state=s, primitives=p)
    assert s.grief > 0.5  # grief path 1 (event-induced)
    assert s.awe >= 5.0  # awe up or maintained (might clip)
    assert s.loyalty["primary_figure"] >= 8.0


def test_B2_betrayal_witnessed_raises_grief_and_self_shame() -> None:
    s = ActiveState(grief=0.0, shame={"self": 0.0})
    _apply(state=s, events=["betrayal_witnessed"])
    assert s.grief > 0.0
    assert s.shame["self"] > 0.0


def test_B3_ally_departure_decreases_belonging_raises_fear() -> None:
    s = ActiveState(fear=1.0, belonging={"peers": 7.0})
    _apply(state=s, events=["ally_departure"])
    assert s.belonging["peers"] < 7.0
    assert s.fear > 1.0


def test_B4_prolonged_suffering_no_sacred_raises_grief_doubt() -> None:
    s = ActiveState(grief=0.0, doubt=0.0)
    p = PrimitiveState(proximity_of_suffering=0.7, religious_context=0.1)
    _apply(state=s, primitives=p)
    assert s.grief > 0.0
    assert s.doubt > 0.0


# ==============================================================
# Category C — 내부 상태 간 전이 (Grief path 2)
# ==============================================================

def test_C1_high_guilt_triggers_grief_doubt_confusion() -> None:
    s = ActiveState(guilt={"primary_figure": 7.0},
                    grief=0.5, doubt=0.5, confusion=0.5)
    _apply(state=s)
    assert s.grief > 0.5
    assert s.doubt > 0.5
    assert s.confusion > 0.5


def test_C3_fear_plus_guilt_path_to_grief() -> None:
    """Grief path 2: state-induced helplessness."""
    s = ActiveState(fear=7.0, guilt={"primary_figure": 5.0}, grief=0.0, confusion=0.0)
    _apply(state=s)
    assert s.grief > 0.0
    assert s.confusion > 0.0


def test_C2_high_shame_decreases_resolve_raises_trauma() -> None:
    s = ActiveState(shame={"self": 7.0}, resolve=7.0, trauma=0.0)
    _apply(state=s)
    assert s.resolve < 7.0
    assert s.trauma > 0.0


def test_C4_high_doubt_decreases_hope() -> None:
    s = ActiveState(doubt=7.0, hope=5.0)
    _apply(state=s)
    assert s.hope < 5.0


# ==============================================================
# Category D — 관계/소속
# ==============================================================

def test_D1_ally_proximity_increases_belonging_decreases_fear() -> None:
    s = ActiveState(fear=5.0, belonging={"peers": 5.0})
    p = PrimitiveState(ally_proximity=0.8)
    _apply(state=s, primitives=p)
    assert s.belonging["peers"] > 5.0
    assert s.fear < 5.0


def test_D3_primary_figure_presence_bumps_awe_loyalty() -> None:
    s = ActiveState(awe=5.0, loyalty={"primary_figure": 8.0})
    p = PrimitiveState(primary_figure_presence=0.8)
    _apply(state=s, primitives=p)
    assert s.awe > 5.0
    assert s.loyalty["primary_figure"] > 8.0


def test_D4_total_isolation_raises_confusion_lowers_hope() -> None:
    s = ActiveState(confusion=0.0, hope=5.0)
    p = PrimitiveState(ally_proximity=0.0, group_cohesion=0.1)
    _apply(state=s, primitives=p)
    assert s.confusion > 0.0
    assert s.hope < 5.0


def test_D2_group_cohesion_raises_belonging() -> None:
    s = ActiveState(belonging={"twelve_disciples": 5.0})
    p = PrimitiveState(group_cohesion=0.9)
    _apply(state=s, primitives=p)
    assert s.belonging["twelve_disciples"] > 5.0


# ==============================================================
# Category E — 신성 이벤트
# ==============================================================

def test_E1_sacred_meal_raises_awe_trust() -> None:
    s = ActiveState(awe=5.0, trust={"primary_figure": 7.0})
    _apply(state=s, events=["sacred_meal"])
    assert s.awe > 5.0
    assert s.trust["primary_figure"] > 7.0


def test_E2_prayer_invitation_raises_awe_hope() -> None:
    s = ActiveState(awe=5.0, hope=5.0)
    _apply(state=s, events=["prayer_invitation"])
    assert s.awe > 5.0
    assert s.hope > 5.0


def test_E3_miracle_raises_awe_trust_hope() -> None:
    s = ActiveState(awe=5.0, hope=5.0, trust={"primary_figure": 7.0})
    _apply(state=s, events=["miracle_witnessed"])
    assert s.awe > 5.0
    assert s.hope > 5.0
    assert s.trust["primary_figure"] > 7.0


def test_E4_forgiveness_reduces_guilt_raises_hope_resolve() -> None:
    s = ActiveState(hope=4.0, resolve=5.0,
                    guilt={"primary_figure": 5.0})
    _apply(state=s, events=["forgiveness_offered"])
    assert s.guilt["primary_figure"] < 5.0
    assert s.hope > 4.0
    assert s.resolve > 5.0


# ==============================================================
# Clip invariants
# ==============================================================

def test_all_values_stay_in_0_to_10() -> None:
    s = ActiveState(
        fear=10.0, grief=10.0, confusion=10.0, hope=10.0, doubt=10.0,
        awe=10.0, resolve=10.0, trauma=10.0, anger=10.0,
        loyalty={"primary_figure": 10.0},
        trust={"primary_figure": 10.0},
        love={"primary_figure": 10.0},
        guilt={"primary_figure": 10.0},
        shame={"self": 10.0, "crowd": 10.0},
        belonging={"peers": 10.0},
    )
    p = PrimitiveState(
        accusation_visibility=1.0, public_visibility=1.0,
        proximity_of_suffering=1.0, primary_figure_visible=True,
        primary_figure_presence=1.0, ally_proximity=1.0, group_cohesion=1.0,
    )
    _apply(state=s, primitives=p, events=["sacred_meal", "miracle_witnessed"])
    for name in ("fear", "grief", "confusion", "hope", "doubt", "awe",
                 "resolve", "trauma", "anger"):
        val = getattr(s, name)
        assert 0.0 <= val <= 10.0, f"{name}={val} out of range"
    for d in (s.loyalty, s.trust, s.love, s.guilt, s.shame, s.belonging):
        for k, v in d.items():
            assert 0.0 <= v <= 10.0, f"{k}={v} out of range"


def test_no_op_context_leaves_zero_state_near_zero() -> None:
    """Empty state + empty events + default primitives should not spawn spurious values."""
    s = ActiveState()
    _apply(state=s)
    # nothing should spontaneously rise above 0 from nothing
    assert s.fear == 0.0
    assert s.grief == 0.0
    assert s.awe == 0.0


# ==============================================================
# Grief 3 paths (Step 4.6 requirement)
# ==============================================================

# ==============================================================
# Category F — Recovery edges (D1+D4: 7 additional edges)
# ==============================================================

def test_F1_high_hope_decays_fear() -> None:
    s = ActiveState(fear=5.0, hope=9.0)
    _apply(state=s)
    # fear has passive decay too, plus F1 extra
    assert s.fear < 4.9  # both passive + F1 active


def test_F2_high_awe_decays_grief_slightly() -> None:
    s = ActiveState(grief=5.0, awe=9.0)
    _apply(state=s)
    assert s.grief < 5.0


def test_F3_trust_pf_high_decays_confusion() -> None:
    s = ActiveState(confusion=5.0, trust={"primary_figure": 9.0})
    _apply(state=s)
    assert s.confusion < 5.0


def test_F4_high_belonging_decays_crowd_shame() -> None:
    s = ActiveState(shame={"crowd": 7.0}, belonging={"peers": 9.0})
    _apply(state=s)
    assert s.shame["crowd"] < 7.0


def test_F5_maintained_loyalty_restores_resolve() -> None:
    s = ActiveState(loyalty={"primary_figure": 8.0}, resolve=5.0)
    _apply(state=s)
    assert s.resolve > 5.0


def test_F6_grief_natural_decay_when_guilt_low_hope_high() -> None:
    s = ActiveState(grief=3.0, hope=7.0, guilt={"primary_figure": 1.0})
    _apply(state=s)
    assert s.grief < 3.0


def test_F7_vitality_decays_confusion() -> None:
    s = ActiveState(vitality=9.0, confusion=5.0)
    _apply(state=s)
    assert s.confusion < 5.0


def test_fear_does_not_saturate_with_hope() -> None:
    """Regression: fear at 9 with hope=8 should drop meaningfully per tick."""
    s = ActiveState(fear=9.0, hope=8.0)
    _apply(state=s)
    # passive decay 0.1 + F1 (9-6)/4 * 0.1 = 0.1 + 0.05 = 0.15
    assert s.fear < 8.9


def test_grief_three_paths_exist() -> None:
    """Grief must be reachable via three independent mechanisms."""
    # Path 1: event-induced (suffering visible)
    s1 = ActiveState(grief=0.0)
    p1 = PrimitiveState(proximity_of_suffering=0.8, primary_figure_visible=True)
    _apply(state=s1, primitives=p1)
    assert s1.grief > 0.0, "Path 1 (event-induced) failed"

    # Path 2: state-induced (fear+guilt helplessness)
    s2 = ActiveState(grief=0.0, fear=7.0, guilt={"primary_figure": 5.0})
    _apply(state=s2)
    assert s2.grief > 0.0, "Path 2 (state-induced) failed"

    # Path 3: ally_departure (alternative event)
    s3 = ActiveState(grief=0.0)
    _apply(state=s3, events=["betrayal_witnessed"])
    assert s3.grief > 0.0, "Path 3 (peer-failure event) failed"
