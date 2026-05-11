"""Unit tests for Moment linking (Narrative Mining Phase 2)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.moment import Moment
from engine.observer.moment_extractor import extract_moments
from engine.observer.thread import MomentLink
from engine.observer.thread_builder import (
    DEFAULT_LINK_THRESHOLDS,
    LinkThresholds,
    link_moments,
    serialize_links,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


# ============ MomentLink invariants ============

def test_link_rejects_self_loop():
    with pytest.raises(ValueError):
        MomentLink(
            source_moment_id="m1",
            target_moment_id="m1",
            link_type="same_agent",
            weight=0.5,
            rationale="x",
        )


def test_link_rejects_out_of_range_weight():
    with pytest.raises(ValueError):
        MomentLink(
            source_moment_id="m1", target_moment_id="m2",
            link_type="same_agent", weight=1.5, rationale="x",
        )


# ============ Synthetic moment helpers ============

def _m(mid, tick, *, agents=(), groups=(), pressures=(), mtype="agent_state_shift",
       summary="", tick_range=None):
    if tick_range is None:
        tick_range = (max(0, tick - 1), tick + 1)
    return Moment(
        moment_id=mid, tick=tick, tick_range=tick_range,
        moment_type=mtype, agents=tuple(agents), groups=tuple(groups),
        pressures=tuple(pressures), summary=summary,
        salience_score=0.5, provenance="source_derived",
    )


def test_same_agent_link_emitted():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",))
    b = _m("M2", 12, agents=("a01",), pressures=("hope",))
    links = link_moments([a, b])
    types = {l.link_type for l in links}
    assert "same_agent" in types


def test_same_pressure_link_emitted():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",))
    b = _m("M2", 14, agents=("a02",), pressures=("fear",))
    links = link_moments([a, b])
    assert any(l.link_type == "same_pressure" for l in links)


def test_same_group_link_emitted():
    a = _m("M1", 10, groups=("L1",), pressures=("group_tension",), mtype="group_tension_shift")
    b = _m("M2", 18, groups=("L1",), pressures=("group_tension",), mtype="group_tension_shift")
    links = link_moments([a, b])
    types = {l.link_type for l in links}
    assert "same_group" in types
    assert "same_pressure" in types


def test_max_gap_filters_distant_pairs():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",))
    b = _m("M2", 200, agents=("a01",), pressures=("fear",))
    links = link_moments([a, b])
    # gap ~189 > 30; no agent or pressure link should survive
    assert all(l.source_moment_id != "M1" or l.target_moment_id != "M2"
               for l in links if l.link_type in ("same_agent", "same_pressure"))


def test_unresolved_thread_extends_gap_budget():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",),
           mtype="unresolved_thread", tick_range=(10, 50))
    b = _m("M2", 70, agents=("a01",), pressures=("fear",))
    # gap = 70 - 50 = 20 — within unresolved budget (60), past base (30)
    links = link_moments([a, b])
    assert any(l.source_moment_id == "M1" and l.target_moment_id == "M2"
               for l in links)


def test_link_weights_within_unit_range():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",))
    b = _m("M2", 12, agents=("a01",), pressures=("fear",))
    links = link_moments([a, b])
    for l in links:
        assert 0.0 <= l.weight <= 1.0


def test_temporal_continuity_only_fires_without_other_links():
    """If pair has no shared agent/group/pressure/family but is close in
    time, only temporal_continuity should fire."""
    a = _m("M1", 10, agents=("a01",), pressures=("hope",))
    b = _m("M2", 13, agents=("a02",), pressures=("crowd_mood",))
    links = link_moments([a, b])
    # Note: hope and crowd_mood are in different conflict families
    # (internal_collapse vs atmosphere) — no overlap. So same_conflict_axis
    # also should not fire.
    types = {l.link_type for l in links}
    assert "same_agent" not in types
    assert "same_group" not in types
    assert "same_pressure" not in types
    # temporal_continuity should be the only fallback (gap 3 ≤ max_gap/2=15)
    assert "temporal_continuity" in types


def test_causal_order_authority_to_fear():
    a = _m("M1", 10, mtype="world_pressure_shift",
           pressures=("authority_vigilance",),
           summary="world.authority_vigilance rises (+0.20)")
    b = _m("M2", 14, agents=("a01",), pressures=("fear",),
           summary="a01 fear rises (+1.8)")
    links = link_moments([a, b])
    types = {l.link_type for l in links}
    assert "causal_order" in types


def test_link_output_is_deterministic_and_sorted():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    a = link_moments(moments)
    b = link_moments(moments)
    assert [(l.source_moment_id, l.target_moment_id, l.link_type) for l in a] == \
           [(l.source_moment_id, l.target_moment_id, l.link_type) for l in b]
    # Sort key: (source, target, type)
    keys = [(l.source_moment_id, l.target_moment_id, l.link_type) for l in a]
    assert keys == sorted(keys)


def test_link_serialize_roundtrip():
    a = _m("M1", 10, agents=("a01",), pressures=("fear",))
    b = _m("M2", 12, agents=("a01",), pressures=("hope",))
    links = link_moments([a, b])
    payload = serialize_links(links)
    assert payload["schema_version"] == "moment_links_v1"
    assert payload["summary"]["total"] == len(links)
    # Roundtrip via from_dict
    restored = [MomentLink.from_dict(d) for d in payload["links"]]
    assert restored == links


# ============ Real run sanity ============

def test_real_run_link_count_in_reasonable_range():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    # 105 moments, max_gap 30 — expect O(few hundred) links
    assert 50 <= len(links) <= 5000, (
        f"unexpected link count {len(links)} for {len(moments)} moments"
    )


def test_real_run_link_types_diverse():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    types = {l.link_type for l in links}
    # Should see at least 3 different link types in a real run
    assert len(types) >= 3, f"only {len(types)} link types: {types}"


def test_thread_builder_no_hardcoded_hero():
    src = (ROOT / "engine" / "observer" / "thread_builder.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, (
            f"forbidden hero name '{forbidden}' in thread_builder source"
        )
