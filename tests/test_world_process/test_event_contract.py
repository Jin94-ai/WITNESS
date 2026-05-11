"""Event contract tests (Iter 51, Updated Loop Phase 0 gate).

Ensures:
- Registry declarations match what motif activator consumes.
- No new undeclared producers creep in.
- Active contract (both produced and consumed in B-direction) is
  not silently reduced.
"""

from __future__ import annotations

from engine.world.event_registry import (
    AGENT_ACTION_EVENTS,
    CONSUMED_EVENTS,
    LEGACY_V3_EVENTS,
    SEED_EVENTS,
    active_contract,
    audit,
    dead_emissions,
    orphan_consumers,
)


def test_registry_audit_shape():
    """Smoke: audit dict has expected keys and reasonable values."""
    a = audit()
    assert a["produced_count"] >= 8, a
    assert a["consumed_count"] >= 4, a
    assert isinstance(a["orphan_consumers"], list)
    assert isinstance(a["dead_emissions"], list)
    assert isinstance(a["active_contract"], list)


def test_active_contract_minimum():
    """B-direction must have at least 2 active contract events.

    As of Iter 51, these are forgiveness_emitted + public_confession
    (both established by Iter 34's M6 fix). If this drops, motif
    activator lost its wiring to MicroWorld.
    """
    ac = active_contract()
    assert len(ac) >= 2, f"active contract dropped: {sorted(ac)}"
    assert "forgiveness_emitted" in ac, (
        "forgiveness_emitted should be wired both sides"
    )
    assert "public_confession" in ac, (
        "public_confession should be wired both sides"
    )


def test_no_motif_consumer_has_mystery_events():
    """Any event consumed by motif activator must be declared in
    CONSUMED_EVENTS. Prevents silent addition of new consumers."""
    # Scan engine/persona/motif.py for events_recent.get calls
    import re
    from pathlib import Path

    motif_path = Path(__file__).resolve().parents[2] / "engine" / "persona" / "motif.py"
    text = motif_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"events_recent\.get\(\s*[\"']([a-z_][a-z_0-9]*)[\"']"
    )
    consumed_in_code = set(pattern.findall(text))
    declared = set(CONSUMED_EVENTS)
    undeclared = consumed_in_code - declared
    assert not undeclared, (
        f"motif activator consumes undeclared events: {undeclared}"
    )


def test_orphan_consumers_are_legacy_only():
    """Every orphan consumer (motif reads, nothing produces) must be a
    known legacy v3 hook. Truly-novel orphans are contract bugs.
    """
    orphans = orphan_consumers()
    non_legacy = orphans - LEGACY_V3_EVENTS
    assert not non_legacy, (
        f"unknown orphan consumers (bugs): {sorted(non_legacy)}. "
        "Either wire a producer or remove the consumer."
    )


def test_produced_seed_and_action_events_are_disjoint_categories():
    """Sanity: an event shouldn't be in both AGENT_ACTION_EVENTS
    (spawned by agent actions) and SEED_EVENTS (scenario triggers).
    """
    overlap = AGENT_ACTION_EVENTS & SEED_EVENTS
    assert not overlap, f"event categorized as both action and seed: {overlap}"


def test_dead_emissions_count_reasonable():
    """Observability events (dead emissions) are expected but should
    be tracked. If the count explodes, new emissions may be adding
    without corresponding consumers."""
    dead = dead_emissions()
    # As of Iter 51: 12 dead emissions. If it grows to 20+, something
    # changed structurally that should be reviewed.
    assert len(dead) <= 20, (
        f"dead emissions count high: {len(dead)}. Review whether "
        f"new emissions need consumers."
    )
