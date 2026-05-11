"""World event registry -- single source of truth for event names.

Motivation: Iter 34's M6 retraction revealed that `_confess` motif
activator was checking `forgiveness_offered` while producing code
spawned `forgiveness_emitted`. The naming mismatch hid autonomous
recovery behavior for 30 iterations.

This registry formalizes:
- PRODUCED_EVENTS: events that some code path in the engine spawns
- CONSUMED_EVENTS: events that motif activators / consumers read
- Their intersection is the working contract. Mismatches indicate
  either dead emissions or orphan consumers.

Rule: adding a new event must update both sets if the event is
expected to feed back into agent decision logic.
"""

from __future__ import annotations

# =============================================================================
# PRODUCED EVENTS -- spawned by action handlers, seed events, or hazards
# =============================================================================

# From MicroWorld._apply_agent_action (action -> event spawning):
AGENT_ACTION_EVENTS: frozenset[str] = frozenset({
    "public_denial",          # deny action
    "public_confession",      # confess action
    "forgiveness_emitted",    # confess action (Iter 31, target_role = confessor's role)
    "visible_grief",          # weep action
    "visible_withdrawal",     # withdraw_in_fear action (in visible location)
    "discussion_emitted",     # discuss_with_disciples action
    "public_devotion",        # pray action (sacred location)
    "public_loyalty",         # assert_loyalty action (high visibility)
})

# From MicroWorld._apply_seed_event (scenario-injected triggers):
SEED_EVENTS: frozenset[str] = frozenset({
    "public_accusation",      # raises blame + shame_climate (scenario trigger)
    "guard_approaches",       # raises authority_vigilance (scenario trigger)
    "role_transition",        # mid-simulation role change (Iter 1)
    "shame_repair",           # shame_climate reduction + spawn forgiveness rumor (Iter 28)
    "prayer_invitation",      # calling scene; Iter 95 wired: agents_at_location awe +2 + crowd dominant=awe
    "miracle_witnessed",      # calling scene; Iter 95 wired: agents_at_location awe +4 + crowd dominant=awe
})

# All events engine-wide (union)
PRODUCED_EVENTS: frozenset[str] = AGENT_ACTION_EVENTS | SEED_EVENTS


# =============================================================================
# LEGACY V3 EVENTS -- cataloged in engine/world/events.py, from v3-era
# PersonV3Loop pipeline. NOT spawned by MicroWorld. Motif activator still
# checks some of these, creating "orphan consumer" appearance.
# =============================================================================

LEGACY_V3_EVENTS: frozenset[str] = frozenset({
    "forgiveness_offered",       # engine/world/events.py:97
    "restoration_moment",        # engine/world/events.py:102
    "eye_contact",               # engine/world/events.py:48
    "primary_figure_suffering_visible",
    "betrayal_witnessed",
    "accusation",
    "covert_bargain",
    "crowd_mockery",
    "sacred_meal",
    "self_harm_impulse",
    "weapon_raised",
    "weapon_drawn_nearby",
    "public_declaration",
    "hidden_information_revealed",
    "remorse_trigger",
    "creative_surge",
    "creative_conflict",
    "return_token",
    "time_running_out",
    "ally_arrival",
    "ally_departure",
    "identification_signal",
    "visible_distress",
    "withdrawal",
    "voluntary",                 # legacy PersonV3Loop/SimulationWorld placeholder
    "primary_figure_visible",    # engine/world/events.py primitive update derivation
})


# =============================================================================
# CONSUMED EVENTS -- read by motif activators in engine/persona/motif.py
# =============================================================================

CONSUMED_EVENTS: frozenset[str] = frozenset({
    "forgiveness_offered",                # _confess, _seek_repair (LEGACY v3 hook)
    "restoration_moment",                 # _confess, _seek_repair (LEGACY v3 hook)
    "forgiveness_emitted",                # _confess (Iter 34 fix — matches AGENT_ACTION_EVENTS)
    "public_confession",                  # _confess (Iter 34 fix — matches AGENT_ACTION_EVENTS)
    "eye_contact",                        # _grieve (LEGACY v3 hook)
    "primary_figure_suffering_visible",   # _grieve (LEGACY v3 hook)
})


# =============================================================================
# Contract analysis
# =============================================================================

def orphan_consumers() -> frozenset[str]:
    """Events consumed by motif activators but never produced by
    MicroWorld (B-direction). Some are legacy v3 hooks catalogued in
    engine/world/events.py but not ported to MicroWorld pipeline.

    Iter 51 finding: Motif activator's events_recent hook checks 6
    events; only 2 are actually wired to MicroWorld emissions
    (forgiveness_emitted, public_confession -- both Iter 34 fix).
    The other 4 are v3-era hooks left dormant by the B-direction
    transition.
    """
    return CONSUMED_EVENTS - PRODUCED_EVENTS


def legacy_dormant_consumers() -> frozenset[str]:
    """Subset of orphan consumers that are known legacy v3 hooks.

    Distinguishing dormant (known legacy) from truly undesigned
    orphans helps prioritize: dormant are port candidates;
    truly-orphan need design review.
    """
    return (CONSUMED_EVENTS - PRODUCED_EVENTS) & LEGACY_V3_EVENTS


def dead_emissions() -> frozenset[str]:
    """Events produced by engine but never consumed by any motif activator.

    These may still have indirect downstream effects (e.g., rumor spawn
    with matching content_tag, crowd state inject), but they do not
    directly gate motif activation.
    """
    return PRODUCED_EVENTS - CONSUMED_EVENTS


def active_contract() -> frozenset[str]:
    """Events that are both produced and consumed -- the working
    feedback contract for motif activation."""
    return PRODUCED_EVENTS & CONSUMED_EVENTS


def audit() -> dict:
    """Return full audit dict for inspection or test assertions."""
    return {
        "produced_count": len(PRODUCED_EVENTS),
        "consumed_count": len(CONSUMED_EVENTS),
        "orphan_consumers": sorted(orphan_consumers()),
        "dead_emissions": sorted(dead_emissions()),
        "active_contract": sorted(active_contract()),
    }
