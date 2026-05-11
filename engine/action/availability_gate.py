"""Availability gate (Dynamics Step 3).

2단 행동 선택 구조의 1단계. 각 action에 gate 조건을 걸어 맥락 강한 행동이
일상적 옵션으로 취급되지 않도록 한다.

Step 3 rationale (ChatGPT):
    "run_to_tomb 7회는 availability gating 부재 문제. 정책이 이런 행동을 상시
    옵션으로 취급. gate가 강해야 튀지 않음."

Rule #12 준수: gate는 인물 측 로직 (월드가 행동 결정하지 않음). gate 조건에
월드 상태(primitives, recent events)를 참조하는 것은 OK.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from engine.person.state_v3 import ActiveState
from engine.world.primitives import PrimitiveState

# ---------------------------------------------------------------------
# Context bag passed into each gate
# ---------------------------------------------------------------------

@dataclass
class GateContext:
    """Snapshot passed into each gate predicate.

    recent_events: event_id -> ticks_since_firing (0 = this tick).
    """
    state: ActiveState
    primitives: PrimitiveState
    recent_events: dict[str, int] = field(default_factory=dict)
    tick_index: int = 0

    def has_recent(self, event_id: str, within: int = 3) -> bool:
        age = self.recent_events.get(event_id)
        return age is not None and age <= within

    def has_any_recent(self, event_ids: list[str], within: int = 3) -> bool:
        return any(self.has_recent(e, within) for e in event_ids)


GatePredicate = Callable[[GateContext], bool]


# ---------------------------------------------------------------------
# Gate predicates (Dynamics §5.4)
# ---------------------------------------------------------------------

def _always(_: GateContext) -> bool:
    return True


def _run_to_tomb(ctx: GateContext) -> bool:
    # Only when resurrection-adjacent context is fresh.
    return ctx.has_any_recent(
        ["restoration_moment", "forgiveness_offered", "miracle_witnessed"],
        within=3,
    )


def _draw_sword(ctx: GateContext) -> bool:
    threat = ctx.has_any_recent(
        ["guard_approaches", "weapon_drawn_nearby"], within=2,
    )
    return threat and ctx.state.anger > 3.0


def _deny(ctx: GateContext) -> bool:
    # Denial must be prompted by an accusation in the immediate vicinity.
    return ctx.has_any_recent(
        ["public_accusation", "crowd_mockery"], within=1,
    )


def _fall_asleep(ctx: GateContext) -> bool:
    tired = ctx.state.fatigue > 5.0
    sacred_context = ctx.has_any_recent(
        ["prayer_invitation", "sacred_meal"], within=5,
    )
    # Sleep either when very tired OR in a low-stakes sacred wait
    return tired or (sacred_context and ctx.state.fatigue > 3.0)


def _confess(ctx: GateContext) -> bool:
    guilt_max = max(ctx.state.guilt.values()) if ctx.state.guilt else 0.0
    forgiven = ctx.has_recent("forgiveness_offered", within=3)
    restored = ctx.has_recent("restoration_moment", within=5)
    return forgiven or restored or guilt_max > 6.0


def _weep(ctx: GateContext) -> bool:
    guilt_max = max(ctx.state.guilt.values()) if ctx.state.guilt else 0.0
    # Weep when grief/guilt cross a threshold OR just after eye_contact
    return (
        ctx.state.grief > 3.0
        or guilt_max > 4.0
        or ctx.has_recent("eye_contact", within=1)
    )


def _withdraw_in_fear(ctx: GateContext) -> bool:
    return ctx.state.fear > 3.0 or ctx.has_recent("public_accusation", within=2)


def _flee(ctx: GateContext) -> bool:
    # Flee requires concrete physical threat, not just ambient fear
    return (
        ctx.has_any_recent(
            ["guard_approaches", "weapon_drawn_nearby", "betrayal_witnessed"],
            within=3,
        )
        and ctx.state.fear > 4.0
    )


def _follow_at_distance(ctx: GateContext) -> bool:
    # Available once a threat has been seen; doesn't disappear
    return ctx.state.fear > 2.0 or any(
        ctx.has_recent(e, within=10)
        for e in ["guard_approaches", "betrayal_witnessed", "weapon_drawn_nearby"]
    )


def _stay_hiding(ctx: GateContext) -> bool:
    shame_crowd = ctx.state.shame.get("crowd", 0.0)
    return shame_crowd > 2.0 or ctx.state.fear > 5.0


def _assert_loyalty(ctx: GateContext) -> bool:
    loyalty_max = max(ctx.state.loyalty.values()) if ctx.state.loyalty else 0.0
    # Loyalty assertion needs an audience or peers
    audience = ctx.primitives.ally_proximity > 0.3 or ctx.primitives.group_cohesion > 0.4
    return loyalty_max > 5.0 and audience


def _pray(ctx: GateContext) -> bool:
    # Available in religious context OR under heavy distress
    sacred_ctx = ctx.primitives.religious_context > 0.2
    distressed = ctx.state.grief > 3.0 or ctx.state.fear > 5.0
    return sacred_ctx or distressed


def _stay_awake(ctx: GateContext) -> bool:
    # Basically always, but skip if very tired
    return ctx.state.fatigue < 8.0


# ---------------------------------------------------------------------
# Registry + evaluator
# ---------------------------------------------------------------------

# STRICT: requires specific event/state context.
# MEDIUM: requires mild state cue.
# LOOSE: always available or near-always.

AVAILABILITY: dict[str, GatePredicate] = {
    # STRICT
    "run_to_tomb": _run_to_tomb,
    "draw_sword": _draw_sword,
    "deny": _deny,
    "confess": _confess,
    "flee": _flee,
    # MEDIUM
    "weep": _weep,
    "withdraw_in_fear": _withdraw_in_fear,
    "follow_at_distance": _follow_at_distance,
    "stay_hiding": _stay_hiding,
    "assert_loyalty": _assert_loyalty,
    "pray": _pray,
    "fall_asleep": _fall_asleep,
    "stay_awake": _stay_awake,
    # LOOSE
    "follow_closely": _always,
    "discuss_with_disciples": _always,
}


DEFAULT_FALLBACK: tuple[str, ...] = (
    "follow_closely",
    "stay_awake",
    "discuss_with_disciples",
)


def is_available(action_id: str, ctx: GateContext) -> bool:
    """True if the action is contextually permitted. Unknown actions default to True
    (backward compat; new action ids should be added to AVAILABILITY)."""
    gate = AVAILABILITY.get(action_id)
    if gate is None:
        return True
    return gate(ctx)


def filter_available(
    candidates: list[str], ctx: GateContext,
) -> list[str]:
    """Keep only actions whose gate allows in the current context.
    If none pass, return DEFAULT_FALLBACK (filtered through gates too)."""
    available = [a for a in candidates if is_available(a, ctx)]
    if available:
        return available
    fallback = [a for a in DEFAULT_FALLBACK if is_available(a, ctx)]
    return fallback or ["follow_closely"]
