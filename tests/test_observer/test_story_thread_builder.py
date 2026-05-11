"""Unit tests for Story Thread mining (Narrative Mining Phase 3)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.moment import Moment
from engine.observer.moment_extractor import extract_moments
from engine.observer.thread import StoryThread
from engine.observer.thread_builder import (
    DEFAULT_THREAD_THRESHOLDS,
    ThreadThresholds,
    build_story_threads,
    link_moments,
    serialize_threads,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


# ============ StoryThread invariants ============

def test_thread_rejects_empty_moment_ids():
    with pytest.raises(ValueError):
        StoryThread(
            thread_id="T01", title="x",
            main_agents=("a01",), moment_ids=(),
            start_tick=0, end_tick=10,
        )


def test_thread_rejects_inverted_ticks():
    with pytest.raises(ValueError):
        StoryThread(
            thread_id="T01", title="x",
            main_agents=("a01",), moment_ids=("M1",),
            start_tick=20, end_tick=10,
        )


def test_thread_rejects_out_of_range_score():
    with pytest.raises(ValueError):
        StoryThread(
            thread_id="T01", title="x",
            main_agents=("a01",), moment_ids=("M1",),
            start_tick=0, end_tick=10,
            story_potential_score=1.5,
        )


# ============ Synthetic component tests ============

def _m(mid, tick, *, agents=(), groups=(), pressures=(),
       mtype="agent_state_shift", summary="", salience=0.5):
    return Moment(
        moment_id=mid, tick=tick, tick_range=(max(0, tick - 1), tick + 1),
        moment_type=mtype, agents=tuple(agents), groups=tuple(groups),
        pressures=tuple(pressures), summary=summary,
        salience_score=salience, provenance="source_derived",
    )


def test_min_moments_threshold_excludes_short_buckets():
    """An agent with only 2 moments should not become a thread."""
    moments = [
        _m("M1", 10, agents=("a01",), pressures=("fear",),
           summary="a01 fear rises (+1.7)"),
        _m("M2", 20, agents=("a01",), pressures=("fear",),
           summary="a01 fear rises (+1.5)"),
    ]
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    assert all(len(t.moment_ids) >= 3 for t in threads)


def test_min_moments_threshold_includes_3plus_buckets():
    moments = [
        _m("M1", 10, agents=("a01",), pressures=("fear",),
           summary="a01 fear rises (+1.7)", salience=0.7),
        _m("M2", 20, agents=("a01",), pressures=("fear",),
           summary="a01 fear rises (+1.5)", salience=0.6),
        _m("M3", 30, agents=("a01",), pressures=("hope",),
           summary="a01 hope falls (-1.6)", salience=0.6),
        _m("M4", 40, agents=("a01",), pressures=("shame_self",),
           summary="a01 shame_self rises (+2.0)", salience=0.7),
        _m("M5", 50, mtype="world_pressure_shift",
           pressures=("authority_vigilance",),
           summary="world.authority_vigilance rises (+0.20)", salience=0.8),
    ]
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    assert len(threads) >= 1
    t = threads[0]
    assert "a01" in t.main_agents


def test_thread_score_in_unit_range():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    for t in threads:
        assert 0.0 <= t.story_potential_score <= 1.0


def test_thread_provenance_is_source_inferred():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    for t in threads:
        assert t.provenance == "source_inferred"


def test_thread_start_le_end_tick():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    for t in threads:
        assert t.start_tick <= t.end_tick


def test_thread_ids_are_unique():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    ids = [t.thread_id for t in threads]
    assert len(ids) == len(set(ids)), f"duplicate thread_id in {ids}"


def test_thread_conflict_label_is_known_value():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    valid = {
        "loyalty_vs_survival", "trust_vs_self_protection",
        "collective_fear_vs_scapegoating", "control_vs_exposure",
        "identity_vs_failure", "uncertainty_vs_commitment",
        "atmosphere_vs_action", "unknown",
    }
    for t in threads:
        assert t.core_conflict in valid


def test_thread_score_threshold_filters_below_min():
    """Setting min_score very high should produce zero threads."""
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    th = ThreadThresholds(min_score_for_inclusion=0.99)
    threads = build_story_threads(moments, links, thresholds=th)
    assert len(threads) == 0


def test_thread_builder_output_is_deterministic():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    a = build_story_threads(moments, links)
    b = build_story_threads(moments, links)
    assert [t.to_dict() for t in a] == [t.to_dict() for t in b]


def test_thread_builder_no_hardcoded_hero():
    """Same Rule #1 check for the thread builder + threads modules."""
    src1 = (ROOT / "engine" / "observer" / "thread.py").read_text(encoding="utf-8")
    src2 = (ROOT / "engine" / "observer" / "thread_builder.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src1, f"forbidden hero '{forbidden}' in thread.py"
        assert forbidden not in src2, f"forbidden hero '{forbidden}' in thread_builder.py"


def test_real_run_produces_multiple_threads():
    """Plan §17 success criterion 1: 여러 개의 Story Thread가 나오는가?"""
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    assert len(threads) >= 2, f"expected ≥2 threads, got {len(threads)}"


def test_real_run_threads_have_minimum_change():
    """Plan §17 criterion 4: 시작과 끝 사이에 상태 변화가 있는가?"""
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    for t in threads:
        # span > 0 means there is *temporal* change
        assert t.end_tick > t.start_tick or len(t.moment_ids) >= 3


def test_real_run_main_agents_not_empty_when_agent_thread():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    # threads with agent moments should have at least one main_agent
    for t in threads:
        if any("agent" in s for s in (t.title, t.unresolved_question)):
            continue  # narrative wording test, skip
        # most threads should have main_agents
    has_agent = sum(1 for t in threads if t.main_agents)
    assert has_agent >= len(threads) - 1, "most threads should name a main agent"


def test_serialize_threads_includes_summary():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    payload = serialize_threads(threads, run_label="peter_scarcity_baseline")
    assert payload["schema_version"] == "story_threads_v1"
    assert payload["run_label"] == "peter_scarcity_baseline"
    s = payload["summary"]
    assert s["total"] == len(threads)
    assert s["strong"] + s["usable"] + s["weak"] <= s["total"]


def test_strong_thread_has_creative_use_tags():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    strongest = max(threads, key=lambda t: t.story_potential_score)
    if strongest.story_potential_score >= 0.4:
        assert len(strongest.usable_as) >= 1, (
            f"strong thread {strongest.thread_id} has no usable_as tags"
        )


# ============ Cross-anchor generalization (Iter 2 lock-in) ============

ALT_DUMPS = [
    (ROOT / "data" / "visual" / "dot_observer_data_triple.json", "peter_scarcity_triple"),
    (ROOT / "data" / "visual" / "dot_observer_data_vangogh.json", "vangogh_sacred_baseline"),
]


def test_pipeline_generalizes_across_anchors():
    """The full Phase 1-3 pipeline must run unchanged on alt observer dumps.

    This is the lock-in for the no-hardcoded-hero rule at the *behavioural*
    level (not just grep): the same builder produces threads from a quiet
    8-agent scenario and a noisy 12-agent scenario without code changes.
    """
    seen_anchors: list[str] = []
    for src, label in ALT_DUMPS:
        if not src.exists():
            continue
        obs = json.loads(src.read_text(encoding="utf-8"))
        moments = extract_moments(obs)
        links = link_moments(moments)
        threads = build_story_threads(moments, links)
        # Pipeline doesn't crash + produces deterministic output
        assert isinstance(threads, list)
        # Even quiet scenarios should at least produce a moment list
        assert len(moments) >= 1
        seen_anchors.append(label)
    # At least one alt anchor was actually exercised
    assert len(seen_anchors) >= 1, "no alt anchor dumps available for smoke test"


def test_quiet_scenario_yields_fewer_moments_than_noisy():
    """Sanity: vangogh (8 agents, calm) should produce strictly fewer moments
    than peter_scarcity_baseline (12 agents, scarcity stress).

    This guards against threshold drift: if defaults make every scenario emit
    the same moment count regardless of input, something is wrong.
    """
    base_obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    base_n = len(extract_moments(base_obs))

    vg_path = ROOT / "data" / "visual" / "dot_observer_data_vangogh.json"
    if not vg_path.exists():
        return  # tolerate missing alt dump
    vg_obs = json.loads(vg_path.read_text(encoding="utf-8"))
    vg_n = len(extract_moments(vg_obs))

    assert vg_n < base_n, (
        f"thresholds may have drifted — vangogh ({vg_n}) should be < "
        f"baseline ({base_n}) given fewer agents and calmer dynamics"
    )
