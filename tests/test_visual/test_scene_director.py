"""Unit tests for Scene Director rules in scripts/visual/build_scene_beats.py.

Pure deterministic logic — protects the Director from regressions.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make scripts/visual importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "visual"))

import build_scene_beats as bsd  # type: ignore  # noqa: E402


# ============ focal event priority ============

def test_focal_event_priority_guard_first():
    """guard_approaches has highest priority over confession/denial."""
    candidate = {
        "events_involved": ["public_confession", "guard_approaches", "discussion_emitted"]
    }
    tick = {"active_events": ["discussion_emitted"]}
    assert bsd.pick_focal_event(candidate, tick) == "guard_approaches"


def test_focal_event_priority_confession_over_grief():
    candidate = {"events_involved": ["visible_grief", "public_confession"]}
    tick = {"active_events": []}
    assert bsd.pick_focal_event(candidate, tick) == "public_confession"


def test_focal_event_priority_denial_over_grief():
    candidate = {"events_involved": ["visible_grief", "public_denial"]}
    tick = {"active_events": []}
    assert bsd.pick_focal_event(candidate, tick) == "public_denial"


def test_focal_event_fallback_discussion():
    candidate = {"events_involved": ["discussion_emitted"]}
    tick = {"active_events": []}
    assert bsd.pick_focal_event(candidate, tick) == "discussion_emitted"


def test_focal_event_uses_tick_active_events():
    """Should consider tick.active_events as well."""
    candidate = {"events_involved": ["discussion_emitted"]}
    tick = {"active_events": ["guard_approaches"]}
    assert bsd.pick_focal_event(candidate, tick) == "guard_approaches"


# ============ layout selection ============

def _make_tick(group_modes: dict[str, str]) -> dict:
    return {
        "groups": [
            {"id": gid, "dominant_mode": mode, "tension": 0.5, "member_count": 4}
            for gid, mode in group_modes.items()
        ],
        "agents": [],
    }


def test_layout_authority_pressure_when_vigilance_spike():
    candidate = {"signals": ["authority_vigilance_spike", "cohort_split"]}
    tick = _make_tick({"L1": "partial", "L2": "low_activity", "L3": "low_activity"})
    assert bsd.select_layout(candidate, tick) == "authority_pressure"


def test_layout_crowd_semicircle_when_saturation_present():
    """Saturation in any group -> crowd_semicircle (lock formed)."""
    candidate = {"signals": ["saturation_lock", "cohort_split"]}
    tick = _make_tick({"L1": "saturation", "L2": "low_activity", "L3": "low_activity"})
    assert bsd.select_layout(candidate, tick) == "crowd_semicircle"


def test_layout_split_group_when_split_without_saturation():
    """cohort_split without saturation -> split_group (still splitting)."""
    candidate = {"signals": ["cohort_split", "saturation_lock", "agent_state_shift"]}
    tick = _make_tick({"L1": "partial", "L2": "low_activity", "L3": "low_activity"})
    assert bsd.select_layout(candidate, tick) == "split_group"


def test_layout_internal_collapse_for_solo_state_shift():
    candidate = {"signals": ["agent_state_shift"]}
    tick = _make_tick({"L1": "low_activity", "L2": "low_activity", "L3": "low_activity"})
    assert bsd.select_layout(candidate, tick) == "internal_collapse"


def test_layout_center_focal_default():
    candidate = {"signals": []}
    tick = _make_tick({"L1": "low_activity"})
    assert bsd.select_layout(candidate, tick) == "center_focal"


# ============ visual cue derivation (denial_x bug fix) ============

def test_denial_x_emitted_when_turning_away_exists():
    """denial_x cue should be added if a turning_away action is in scene
    AND the tick has a denial event.
    """
    actions = [
        {"agent": "agent_03", "pose": "turning_away", "target": None, "effect": None},
        {"agent": "agent_09", "pose": "shaking", "target": "__authority", "effect": "pressure_ring"},
    ]
    candidate = {"events_involved": []}
    tick = {"active_events": ["public_denial", "discussion_emitted"]}
    cues = bsd.derive_visual_cues(actions, candidate, tick, focal_event="guard_approaches")
    assert "denial_x" in cues


def test_denial_x_NOT_emitted_when_no_turning_away():
    """denial_x must NOT be added if there's no turning_away action,
    even if the tick has denial events. Avoids misleading attachment to
    unrelated focal agents (the bug fix from autonomous LOOP).
    """
    actions = [
        {"agent": "agent_03", "pose": "speaking", "target": "group_L1", "effect": "confession_wave"},
        {"agent": "agent_05", "pose": "kneeling", "target": None, "effect": "grief_drop"},
    ]
    candidate = {"events_involved": []}
    tick = {"active_events": ["public_confession", "public_denial", "visible_grief"]}
    cues = bsd.derive_visual_cues(actions, candidate, tick, focal_event="public_confession")
    assert "denial_x" not in cues


def test_denial_x_emitted_when_focal_event_is_denial():
    """If focal_event itself is public_denial, denial_x is added even without
    a turning_away action (the focal action implies it).
    """
    actions = [
        {"agent": "agent_03", "pose": "turning_away", "target": "__authority", "effect": "denial_x"},
    ]
    candidate = {"events_involved": []}
    tick = {"active_events": ["public_denial"]}
    cues = bsd.derive_visual_cues(actions, candidate, tick, focal_event="public_denial")
    assert "denial_x" in cues


def test_speech_bubble_when_speaking_action():
    actions = [
        {"agent": "agent_03", "pose": "speaking", "target": "group_L1", "effect": "confession_wave"},
    ]
    candidate = {"events_involved": []}
    tick = {"active_events": []}
    cues = bsd.derive_visual_cues(actions, candidate, tick, focal_event="public_confession")
    assert "speech_bubble" in cues
    assert "confession_wave" in cues  # action effect propagated


def test_authority_aura_when_guard_event():
    actions = [
        {"agent": "__authority", "pose": "approaching", "target": "agent_03", "effect": "authority_aura"},
    ]
    candidate = {"events_involved": ["guard_approaches"]}
    tick = {"active_events": []}
    cues = bsd.derive_visual_cues(actions, candidate, tick, focal_event="guard_approaches")
    assert "authority_aura" in cues


# ============ role assignment ============

def test_assign_roles_focal_excluded_from_other_lists():
    """Focal agents must not appear in supporting/bystanders/withdrawn."""
    tick = {
        "agents": [
            {"id": "agent_01", "group_id": "L2", "dominant_state": "calm", "fear": 0, "salient": False},
            {"id": "agent_03", "group_id": "L1", "dominant_state": "fragmenting", "fear": 9, "salient": True},
            {"id": "agent_06", "group_id": "L1", "dominant_state": "calm", "fear": 1, "salient": False},
            {"id": "agent_09", "group_id": "L1", "dominant_state": "fragmenting", "fear": 10, "salient": False},
        ],
    }
    focal = ["agent_03", "agent_09"]
    roles = bsd.assign_roles(tick, focal, focal_event="public_confession")
    for fid in focal:
        assert fid not in roles["supporting"]
        assert fid not in roles["bystanders"]
        assert fid not in roles["withdrawn"]


def test_assign_roles_authority_only_when_guard_event():
    tick = {"agents": []}
    roles_with_guard = bsd.assign_roles(tick, [], focal_event="guard_approaches")
    roles_without = bsd.assign_roles(tick, [], focal_event="public_confession")
    assert roles_with_guard["authority"] == ["__authority"]
    assert roles_without["authority"] == []


def test_assign_roles_withdrawn_collected():
    tick = {
        "agents": [
            {"id": "agent_01", "group_id": "L2", "dominant_state": "withdrawn", "fear": 0, "salient": False},
            {"id": "agent_03", "group_id": "L1", "dominant_state": "fragmenting", "fear": 9, "salient": False},
        ],
    }
    roles = bsd.assign_roles(tick, ["agent_03"], focal_event="public_confession")
    assert "agent_01" in roles["withdrawn"]
    assert "agent_01" not in roles["supporting"]
    assert "agent_01" not in roles["bystanders"]
