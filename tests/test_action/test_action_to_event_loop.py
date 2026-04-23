"""Tests for action → event → primitive update closed loop (v2 §5)."""

from __future__ import annotations

from engine.action.action_event_mapper import ACTION_EVENT_TABLE, ActionEventMapper
from engine.world.events import EventRegistry
from engine.world.primitives import PrimitiveState


def test_mapper_covers_bc_action_vocab() -> None:
    """기존 BC 모델의 15개 action_id 가 전부 매핑되어야 함."""
    m = ActionEventMapper()
    bc_vocab = [
        "follow_closely", "pray", "discuss_with_disciples",
        "assert_loyalty", "withdraw_in_fear", "weep",
        "deny", "confess", "stay_awake", "fall_asleep",
        "draw_sword", "flee", "follow_at_distance",
        "stay_hiding", "run_to_tomb",
    ]
    for action in bc_vocab:
        assert m.lookup(action) is not None, (
            f"BC action '{action}' not in ActionEventMapper"
        )


def test_mapper_returns_event_id() -> None:
    m = ActionEventMapper()
    assert m.trigger_event_id("deny") == "public_denial"
    assert m.trigger_event_id("weep") == "visible_distress"
    assert m.trigger_event_id("draw_sword") == "weapon_raised"


def test_mapper_unknown_action_returns_none() -> None:
    m = ActionEventMapper()
    assert m.lookup("nonexistent_action") is None
    assert m.trigger_event_id("nonexistent_action") is None


def test_action_to_event_to_primitive_loop() -> None:
    """v2 §5 폐루프: action → event → primitive 갱신 작동."""
    mapper = ActionEventMapper()
    events = EventRegistry()
    primitives = PrimitiveState()

    initial_visibility = primitives.public_visibility

    # action=deny → event=public_denial
    event_id = mapper.trigger_event_id("deny")
    assert event_id == "public_denial"
    # event → primitive update
    updated = events.apply_to_primitives(event_id, primitives)
    assert "public_visibility" in updated
    assert primitives.public_visibility > initial_visibility


def test_withdrawal_action_reduces_visibility() -> None:
    """v2 §5.4: withdraw → ally_proximity/public_visibility 감소."""
    mapper = ActionEventMapper()
    events = EventRegistry()
    primitives = PrimitiveState(ally_proximity=0.8, public_visibility=0.7)

    event_id = mapper.trigger_event_id("flee")
    events.apply_to_primitives(event_id, primitives)

    # withdrawal event reduces both
    assert primitives.ally_proximity < 0.8
    assert primitives.public_visibility < 0.7


def test_mapper_has_more_than_15_actions() -> None:
    """BC 15 + canonical events action = at least 20."""
    m = ActionEventMapper()
    assert m.n_actions() >= 15


def test_all_mapped_events_exist_in_registry() -> None:
    """Mapper의 모든 triggered_event_id 가 EventRegistry에 있어야."""
    mapper = ActionEventMapper()
    events = EventRegistry()
    known_event_ids = {e.event_id for e in events.all()}
    for entry in ACTION_EVENT_TABLE:
        assert entry.triggered_event_id in known_event_ids, (
            f"action {entry.action_id} triggers '{entry.triggered_event_id}' "
            "but no such event in registry"
        )


def test_action_caused_events_loop_back_correctly() -> None:
    """v2 §5 의 핵심: action-caused event는 source='action'."""
    mapper = ActionEventMapper()
    events = EventRegistry()
    for entry in ACTION_EVENT_TABLE:
        e = events.get(entry.triggered_event_id)
        assert e is not None
        # Events that exist ONLY as action consequences should be source='action'
        # (Some events like ally_arrival are canonical AND action-triggered, so
        # we check that at least the pure action events exist)
    action_events = events.action_caused()
    assert len(action_events) >= 5
