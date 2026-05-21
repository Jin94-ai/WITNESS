"""Unit tests for the Moment extractor (Narrative Mining Phase 1)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.moment import Moment
from engine.observer.moment_extractor import (
    MomentThresholds,
    extract_moments,
    serialize_moments,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


# ============ Moment dataclass invariants ============

def test_moment_rejects_inverted_tick_range():
    with pytest.raises(ValueError):
        Moment(
            moment_id="bad",
            tick=10,
            tick_range=(15, 12),
            moment_type="agent_state_shift",
        )


def test_moment_rejects_tick_outside_range():
    with pytest.raises(ValueError):
        Moment(
            moment_id="bad",
            tick=20,
            tick_range=(5, 10),
            moment_type="agent_state_shift",
        )


def test_moment_rejects_out_of_range_salience():
    with pytest.raises(ValueError):
        Moment(
            moment_id="bad",
            tick=5,
            tick_range=(0, 10),
            moment_type="agent_state_shift",
            salience_score=1.5,
        )


def test_moment_to_from_dict_roundtrip():
    m = Moment(
        moment_id="M_t10_a01_fear",
        tick=10,
        tick_range=(8, 12),
        moment_type="agent_state_shift",
        agents=("agent_01",),
        pressures=("fear",),
        signals=("agent_state_shift",),
        summary="agent_01 fear rises (+1.7)",
        salience_score=0.34,
        provenance="source_derived",
    )
    d = m.to_dict()
    m2 = Moment.from_dict(d)
    assert m == m2
    # JSON-serializable
    json.dumps(d)


# ============ extractor against synthetic minimal observer ============

def _synth_observer(ticks_data: list[dict]) -> dict:
    """Produce a minimal-shape observer dump for unit tests."""
    return {
        "meta": {"schema_version": "v1", "anchor_id": "test"},
        "ticks": ticks_data,
    }


def _agent(aid, *, fear=0.0, hope=5.0, shame=0.0, state="calm", group="L1"):
    return {
        "id": aid, "group_id": group, "x": 100, "y": 100,
        "fear": fear, "hope": hope, "shame_self": shame,
        "dominant_state": state, "salient": False,
    }


def _world(mood="calm", blame=0.1, suspicion=0.1, authority=0.1):
    return {
        "crowd_mood": mood,
        "blame_concentration": blame,
        "public_suspicion": suspicion,
        "authority_vigilance": authority,
    }


def _group(gid="L1", mode="low_activity", tension=0.1, members=4):
    return {
        "id": gid, "dominant_mode": mode, "tension": tension, "member_count": members,
    }


def test_agent_state_shift_emitted_on_fear_jump():
    obs = _synth_observer([
        {"tick": 1, "world": _world(), "groups": [_group()],
         "agents": [_agent("a01", fear=0.5)], "active_events": []},
        {"tick": 2, "world": _world(), "groups": [_group()],
         "agents": [_agent("a01", fear=3.0)], "active_events": []},
    ])
    moments = extract_moments(obs)
    state_shifts = [m for m in moments if m.moment_type == "agent_state_shift"]
    assert len(state_shifts) == 1
    m = state_shifts[0]
    assert m.agents == ("a01",)
    assert "fear" in m.pressures
    assert "rises" in m.summary


def test_no_moment_when_below_threshold():
    obs = _synth_observer([
        {"tick": 1, "world": _world(), "groups": [_group()],
         "agents": [_agent("a01", fear=0.5)], "active_events": []},
        {"tick": 2, "world": _world(), "groups": [_group()],
         "agents": [_agent("a01", fear=1.0)], "active_events": []},
    ])
    moments = extract_moments(obs)
    assert all(m.moment_type != "agent_state_shift" for m in moments)


def test_group_tension_shift_emitted():
    obs = _synth_observer([
        {"tick": 1, "world": _world(), "groups": [_group(tension=0.1)],
         "agents": [_agent("a01")], "active_events": []},
        {"tick": 2, "world": _world(), "groups": [_group(tension=0.4)],
         "agents": [_agent("a01")], "active_events": []},
    ])
    moments = extract_moments(obs)
    tens = [m for m in moments if m.moment_type == "group_tension_shift"]
    assert len(tens) == 1
    assert tens[0].groups == ("L1",)


def test_world_pressure_shift_on_authority_rise():
    obs = _synth_observer([
        {"tick": 1, "world": _world(authority=0.10), "groups": [_group()],
         "agents": [_agent("a01")], "active_events": []},
        {"tick": 2, "world": _world(authority=0.30), "groups": [_group()],
         "agents": [_agent("a01")], "active_events": []},
    ])
    moments = extract_moments(obs)
    wps = [m for m in moments if m.moment_type == "world_pressure_shift"
           and "authority_vigilance" in m.pressures]
    assert len(wps) == 1


def test_world_mood_change_emits_moment():
    obs = _synth_observer([
        {"tick": 1, "world": _world(mood="calm"), "groups": [_group()],
         "agents": [_agent("a01")], "active_events": []},
        {"tick": 2, "world": _world(mood="agitated"), "groups": [_group()],
         "agents": [_agent("a01")], "active_events": []},
    ])
    moments = extract_moments(obs)
    moods = [m for m in moments if "crowd_mood" in m.pressures]
    assert len(moods) == 1


def test_unresolved_thread_emitted_on_sustained_high_fear():
    th = MomentThresholds(sustained_pressure_min_ticks=5,
                           sustained_pressure_threshold=7.0)
    ticks = []
    for i in range(1, 9):
        ticks.append({
            "tick": i, "world": _world(), "groups": [_group()],
            "agents": [_agent("a01", fear=8.0)], "active_events": [],
        })
    obs = _synth_observer(ticks)
    moments = extract_moments(obs, thresholds=th)
    runs = [m for m in moments if m.moment_type == "unresolved_thread"]
    assert len(runs) == 1
    assert runs[0].agents == ("a01",)
    assert runs[0].tick_range[0] == 1


def test_conflict_marker_co_occurrence_fear_and_authority():
    th = MomentThresholds(conflict_window=4)
    obs = _synth_observer([
        {"tick": 1, "world": _world(authority=0.10), "groups": [_group()],
         "agents": [_agent("a01", fear=1.0)], "active_events": []},
        {"tick": 2, "world": _world(authority=0.35), "groups": [_group()],
         "agents": [_agent("a01", fear=4.0)], "active_events": []},
    ])
    moments = extract_moments(obs, thresholds=th)
    conflicts = [m for m in moments if m.moment_type == "conflict_marker"]
    assert any("authority" in m.summary.lower() and "fear" in m.summary.lower()
               for m in conflicts)


def test_extractor_is_deterministic():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    a = extract_moments(obs)
    b = extract_moments(obs)
    assert [m.moment_id for m in a] == [m.moment_id for m in b]


def test_extractor_no_hardcoded_hero():
    """Rule #1: extractor must not embed agent IDs in its source.

    Pull the module source and grep for known forbidden hero strings.
    """
    src = (ROOT / "engine" / "observer" / "moment_extractor.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden hero name '{forbidden}' in extractor source"


# ============ peter_scarcity_baseline regression ============

def test_real_run_produces_at_least_one_of_each_core_type():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    types = {m.moment_type for m in moments}
    assert "agent_state_shift" in types
    assert "world_pressure_shift" in types
    assert "group_tension_shift" in types


def test_real_run_moments_are_sorted_by_tick():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    ticks = [m.tick for m in moments]
    assert ticks == sorted(ticks)


def test_real_run_provenance_is_subset_of_three_classes():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    classes = {m.provenance for m in moments}
    assert classes <= {"source_derived", "source_inferred", "not_used"}


def test_serialize_moments_shape():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    payload = serialize_moments(moments, run_label="peter_scarcity_baseline")
    assert payload["schema_version"] == "moments_v1"
    assert payload["run_label"] == "peter_scarcity_baseline"
    assert len(payload["moments"]) == len(moments)
    assert payload["summary"]["total"] == len(moments)
    assert sum(payload["summary"]["by_type"].values()) == len(moments)


def test_default_thresholds_yield_reasonable_moment_count():
    """Sanity gate: 200 ticks × 12 agents should produce 30–300 moments.

    Outside this range hints that a threshold drifted (too noisy or too quiet).
    """
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    assert 30 <= len(moments) <= 300, (
        f"unexpected moment count {len(moments)} — thresholds may have drifted"
    )
