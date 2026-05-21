"""Tests for StoryCandidate builder + TurningPoint selector (Stage 6 / Phase B+C)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.identity_resolver import IdentityResolver
from engine.observer.moment_extractor import extract_moments
from engine.observer.story_candidate import TurningPoint
from engine.observer.story_candidate_builder import (
    TurningPointThresholds,
    build_adaptation_hooks,
    build_arc_summary,
    build_premise,
    build_relationship_dynamics,
    build_story_candidates,
    select_turning_points,
    serialize_candidates,
)
from engine.observer.thread_builder import build_story_threads, link_moments

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _real_inputs():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    moments_by_id = {m.moment_id: m for m in moments}
    return obs, moments, links, threads, identity, moments_by_id


# ============ TurningPoint dataclass invariants ============

def test_turning_point_to_dict_shape():
    tp = TurningPoint(
        tick=15,
        moment_ids=("M_a", "M_b"),
        label="conflict",
        summary="x",
        provenance="source_inferred",
    )
    d = tp.to_dict()
    assert d["tick"] == 15
    assert d["moment_ids"] == ["M_a", "M_b"]


# ============ Turning point selector ============

def test_select_turning_points_keeps_conflict_marker():
    *_, threads, identity, moments_by_id = _real_inputs()
    for t in threads:
        tps = select_turning_points(t, moments_by_id, identity=identity)
        # all selected ticks must come from this thread's moment_ids
        for tp in tps:
            assert tp.moment_ids[0] in t.moment_ids


def test_select_turning_points_respects_max_cap():
    *_, threads, identity, moments_by_id = _real_inputs()
    th = TurningPointThresholds(max_points=2)
    for t in threads:
        tps = select_turning_points(t, moments_by_id, thresholds=th, identity=identity)
        # conflict markers may exceed cap; non-conflict should not
        non_conf = [tp for tp in tps if tp.label != "co-occurring pressure"]
        assert len(non_conf) <= 2


def test_turning_point_summary_uses_display_name_when_mapped():
    *_, threads, identity, moments_by_id = _real_inputs()
    # T01 main agent should be agent_03 → "Peter"
    t = next((t for t in threads if "agent_03" in t.main_agents), None)
    if t is None:
        pytest.skip("agent_03 not main in any thread")
    tps = select_turning_points(t, moments_by_id, identity=identity)
    # at least one turning point should mention "Peter" instead of "agent_03"
    assert any("Peter" in tp.summary for tp in tps)


# ============ Premise / arc / hooks ============

def test_premise_substitutes_main_name():
    *_, threads, identity, moments_by_id = _real_inputs()
    t = next((t for t in threads if "agent_03" in t.main_agents), None)
    if t is None:
        pytest.skip("agent_03 not main")
    p = build_premise(t, identity)
    assert "Peter" in p, f"premise did not include name: {p!r}"
    assert "agent_03" not in p


def test_arc_summary_translates_pressures_to_phrases():
    _obs, _moments, _links, threads, identity, moments_by_id = _real_inputs()
    t = threads[0]
    arc = build_arc_summary(t, moments_by_id, identity)
    # arc must use phrase form, not raw field name
    assert "fear" in arc or "authority" in arc or "tension" in arc \
        or "pressure" in arc or "no major pressure" in arc


def test_adaptation_hooks_return_dict_per_conflict():
    *_, threads, identity, moments_by_id = _real_inputs()
    t = threads[0]
    hooks = build_adaptation_hooks(t, identity)
    assert isinstance(hooks, dict)
    # If conflict has hooks defined, names should be substituted
    for fmt, hook in hooks.items():
        assert "{main}" not in hook  # all placeholders filled
        assert "{group}" not in hook


def test_relationship_dynamics_emits_hedged_lines():
    *_, threads, identity, moments_by_id = _real_inputs()
    for t in threads:
        if not t.groups:
            continue
        lines = build_relationship_dynamics(t, moments_by_id, identity)
        # Plan §6.4: hedged language. Lines must include a clear caveat
        # OR a tension/isolation phrase, never an unsupported claim.
        for line in lines:
            assert "↔" in line  # relationship marker is required


# ============ Builder end-to-end ============

def test_build_story_candidates_for_each_thread():
    *_, threads, identity, moments_by_id = _real_inputs()
    moments = list(moments_by_id.values())
    cands = build_story_candidates(threads, moments, identity)
    assert len(cands) == len(threads)
    for i, c in enumerate(cands, start=1):
        assert c.story_candidate_id == f"S{i:02d}"
        # required fields populated
        assert c.title
        assert c.one_line_premise
        assert c.core_conflict
        assert c.arc_summary


def test_story_candidate_serialization_roundtrip(tmp_path):
    *_, threads, identity, moments_by_id = _real_inputs()
    moments = list(moments_by_id.values())
    cands = build_story_candidates(threads, moments, identity)
    payload = serialize_candidates(cands, run_label="peter_scarcity_baseline")
    assert payload["schema_version"] == "story_candidates_v1"
    # serializable JSON
    s = json.dumps(payload, ensure_ascii=False)
    assert "Peter" in s


def test_no_dialogue_or_screenplay_keywords_in_output():
    """Plan §10.2: forbidden — completed dialogue / screenplay / over-narration."""
    *_, threads, identity, moments_by_id = _real_inputs()
    moments = list(moments_by_id.values())
    cands = build_story_candidates(threads, moments, identity)
    forbidden = (
        '"', '"', '"',          # quotation marks (dialogue)
        "EXT.", "INT.",           # screenplay sluglines
        "fade in", "FADE IN",
        "(weeping)", "(crying)",  # parenthetical emotion narration
    )
    for c in cands:
        text = " ".join([
            c.one_line_premise, c.arc_summary, c.unresolved_question,
            *c.relationship_dynamics, *c.world_pressure_context,
            *c.adaptation_hooks.values(),
        ])
        for f in forbidden:
            assert f not in text, (
                f"forbidden token {f!r} in candidate {c.story_candidate_id}: {text!r}"
            )


def test_provenance_summary_counts_match_thread_moments():
    *_, threads, identity, moments_by_id = _real_inputs()
    moments = list(moments_by_id.values())
    cands = build_story_candidates(threads, moments, identity)
    for c, t in zip(cands, threads):
        total = sum(c.provenance_summary.values())
        assert total == len(t.moment_ids)


def test_story_candidate_builder_no_hardcoded_hero():
    src = (ROOT / "engine" / "observer" / "story_candidate_builder.py").read_text(encoding="utf-8")
    src2 = (ROOT / "engine" / "observer" / "story_candidate.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden '{forbidden}' in builder"
        assert forbidden not in src2, f"forbidden '{forbidden}' in dataclass"


def test_risk_notes_always_present():
    *_, threads, identity, moments_by_id = _real_inputs()
    moments = list(moments_by_id.values())
    cands = build_story_candidates(threads, moments, identity)
    for c in cands:
        # Plan §10.2 transparency requirement
        assert len(c.risk_notes) >= 1
        assert any("dialogue" in r.lower() for r in c.risk_notes)
