"""Rule #16 -- 외부 변수 3 Layer 분리 검증.

Primitive(A) / Event(B) / Pressure(C) 가 섞이면 안 됨.
이름이 서로 다른 layer 간 중복되면 안 됨.
"""

from __future__ import annotations

import re
from pathlib import Path

from engine.world.events import EVENT_REGISTRY_DRAFT, EventRegistry
from engine.world.pressure import PRESSURE_NAMES
from engine.world.primitives import (
    PRIMITIVE_REGISTRY,
    PrimitiveState,
    n_primitives,
)


def test_primitives_are_declared() -> None:
    """Layer A: primitive list exists with substantive count."""
    assert n_primitives() >= 15


def test_events_are_declared() -> None:
    """Layer B: event registry has at least 15 entries."""
    reg = EventRegistry()
    assert reg.n_events() >= 15


def test_pressure_has_8_names() -> None:
    """Layer C: exactly 8 pressure names (v2 §2.3)."""
    assert len(PRESSURE_NAMES) == 8


def test_no_name_overlap_between_layers() -> None:
    """Rule #16: same name in different Layer = violation."""
    primitive_names = {p.name for p in PRIMITIVE_REGISTRY}
    event_names = {e.event_id for e in EVENT_REGISTRY_DRAFT}
    pressure_names = set(PRESSURE_NAMES)

    assert not (primitive_names & event_names), (
        f"Names in both Primitive and Event: {primitive_names & event_names}"
    )
    assert not (primitive_names & pressure_names), (
        f"Names in both Primitive and Pressure: {primitive_names & pressure_names}"
    )
    # Exception: 'shame_exposure' is legitimately in both event-delta and pressure
    # because pressure sums event-deltas over time. We explicitly allow this by
    # checking pressure names are not in event registry ids.
    event_pressure_conflict = event_names & pressure_names
    assert not event_pressure_conflict, (
        f"Event id collides with Pressure name: {event_pressure_conflict}"
    )


def test_action_events_are_marked_source_action() -> None:
    """Events caused by person actions have source='action' (v2 §5 polecop)."""
    reg = EventRegistry()
    action_events = reg.action_caused()
    assert len(action_events) >= 5, "Expected some action-caused events"
    for e in action_events:
        assert e.source == "action"


def test_event_apply_to_primitive_updates_fields() -> None:
    """Event's primitive_updates should mutate PrimitiveState."""
    reg = EventRegistry()
    p = PrimitiveState()
    assert p.crowd_density == 0.0
    updated = reg.apply_to_primitives("crowd_mockery", p)
    assert "crowd_density" in updated
    assert p.crowd_density > 0.0


def test_event_unknown_id_returns_empty_list() -> None:
    reg = EventRegistry()
    p = PrimitiveState()
    updated = reg.apply_to_primitives("nonexistent_event", p)
    assert updated == []


def test_world_engine_modules_no_person_hardcoding() -> None:
    """Rule #1 on engine/world/ and engine/action/."""
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parent.parent.parent
    for subdir in ("engine/world", "engine/action"):
        for py in (root / subdir).glob("*.py"):
            src = py.read_text(encoding="utf-8").lower()
            for b in banned:
                if re.search(rf"\b{b}\b", src):
                    raise AssertionError(
                        f"{py.name} contains '{b}' -- Rule #1",
                    )
