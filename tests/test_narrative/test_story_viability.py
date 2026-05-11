"""Unit tests for Story Viability Validation pipeline (Stage A-D + F)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.identity_resolver import IdentityResolver
from engine.observer.moment_extractor import extract_moments
from engine.observer.scene_brief import (
    SceneBrief, build_scene_brief,
)
from engine.observer.story_audit import audit_pair
from engine.observer.story_candidate import StoryCandidate, TurningPoint
from engine.observer.story_candidate_builder import build_story_candidates
from engine.observer.story_viability import score_candidate
from engine.observer.thread_builder import build_story_threads, link_moments
from engine.observer.treatment import Treatment, build_treatment

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _real_candidates() -> list[StoryCandidate]:
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    return build_story_candidates(threads, moments, identity)


# ============ Scene Brief ============

def test_scene_brief_has_six_required_fields_for_strong_candidate():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    c = cands[0]  # S01 = strongest
    b = build_scene_brief(c)
    assert b.main_character
    assert b.scene_question
    assert b.internal_pressure or b.external_pressure
    assert b.turning_point
    assert b.ending_state
    assert b.completeness == "complete"


def test_scene_brief_pressure_classification():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    c = cands[0]
    b = build_scene_brief(c)
    # External pressure must contain world-level fields
    valid_ext = {"authority_vigilance", "public_suspicion",
                 "blame_concentration", "group_tension", "crowd_mood"}
    assert all(p in valid_ext for p in b.external_pressure)
    # Internal pressure must contain agent-level fields
    valid_int = {"fear", "hope", "shame_self", "confusion", "grief", "love", "awe"}
    assert all(p in valid_int for p in b.internal_pressure)


def test_scene_brief_uses_named_main_when_identity_map_present():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    # peter_scarcity_baseline has identity_map → main should be named
    c = cands[0]
    b = build_scene_brief(c)
    # First candidate's main should be a named character (Peter / John / Andrew / James)
    assert b.main_character in {"Peter", "John", "Andrew", "James"} or \
        not b.main_character.startswith("agent_")


def test_scene_brief_to_dict_serializable():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    b = build_scene_brief(cands[0])
    json.dumps(b.to_dict())


# ============ Treatment ============

def test_treatment_three_acts_present():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    c = cands[0]
    b = build_scene_brief(c)
    t = build_treatment(c, b)
    assert t.act_1_setup
    assert t.act_2_pressure_build
    assert t.act_3_turn_consequence
    assert t.end_hook
    assert t.treatment_completeness == "complete"


def test_treatment_premise_preserved():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    c = cands[0]
    b = build_scene_brief(c)
    t = build_treatment(c, b)
    assert t.premise == c.one_line_premise


def test_treatment_no_dialogue_quotes():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        # Plan §10.2: no dialogue
        text = t.act_1_setup + t.act_2_pressure_build + t.act_3_turn_consequence
        # Heuristic: no smart-quotes or attributed speech
        for forbidden in ('“', '”', '"',):
            assert forbidden not in text, f"forbidden char {forbidden!r} in act text"


# ============ Viability scoring ============

def test_viability_score_in_unit_range():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        assert 0.0 <= sc.score <= 100.0
        assert sc.grade in {"strong_viable", "viable_with_gaps", "weak_seed", "not_viable"}


def test_viability_named_main_yields_full_character_clarity():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    c = cands[0]
    b = build_scene_brief(c)
    t = build_treatment(c, b)
    sc = score_candidate(c, b, t)
    # If main is named (Peter / etc.), character_clarity == 1.0
    if c.main_characters and not c.main_characters[0].startswith("agent_"):
        assert sc.factor_breakdown["character_clarity"] == 1.0


def test_viability_strong_candidate_scores_above_threshold():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    # peter_scarcity_baseline S01 is "strong" thread; should at least reach viable_with_gaps
    c = cands[0]
    b = build_scene_brief(c)
    t = build_treatment(c, b)
    sc = score_candidate(c, b, t, cross_seed_frequency=5)
    assert sc.score >= 65, (
        f"S01 expected ≥65, got {sc.score}: {sc.factor_breakdown}"
    )


# ============ Audit ============

def test_audit_passes_for_well_formed_outputs():
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        ar = audit_pair(b, t)
        # No screenplay markers / parentheticals / scripture injection allowed
        assert ar.scene_brief_audit == "pass", (
            f"{c.story_candidate_id} brief audit failed: {ar.violations}"
        )
        assert ar.treatment_audit == "pass", (
            f"{c.story_candidate_id} treatment audit failed: {ar.violations}"
        )


def test_audit_catches_dialogue_quotes_with_saying_verb():
    """If a verb-of-saying is followed by a quote, audit must flag it."""
    from engine.observer.story_audit import _scan_for_violations
    text = 'Peter said, "I do not know him."'
    violations = _scan_for_violations(text, "treatment")
    assert any("said" in v.phrase for v in violations)


def test_audit_does_not_falsefail_on_field_quoting():
    """A quoted unresolved_question (system field) must NOT trigger audit_fail."""
    from engine.observer.story_audit import _scan_for_violations
    text = 'question still open: Will the central agents stay in place under pressure?'
    violations = _scan_for_violations(text, "scene_brief")
    assert violations == []


def test_audit_catches_scripture_injection_via_blocklist():
    from engine.observer.story_audit import _scan_for_violations
    text = "the rooster crowed three times"
    blocklist = ("the rooster crowed",)
    violations = _scan_for_violations(text, "treatment", blocklist)
    assert any("rooster crowed" in v.phrase for v in violations)


def test_audit_loads_blocklist_for_known_anchor():
    """peter_scarcity_baseline anchor has audit_blocklist.json — must load."""
    from engine.observer.story_audit import load_anchor_blocklist
    bl = load_anchor_blocklist("peter_scarcity_baseline")
    assert isinstance(bl, tuple)
    assert len(bl) >= 1


def test_audit_blocklist_returns_empty_for_unknown_anchor():
    from engine.observer.story_audit import load_anchor_blocklist
    bl = load_anchor_blocklist("nonexistent_anchor_xyz")
    assert bl == ()


def test_audit_module_no_hardcoded_hero():
    src = (ROOT / "engine" / "observer" / "story_audit.py").read_text(encoding="utf-8")
    # The audit module IS allowed to mention specific historical names as
    # *forbidden patterns* — but not as positive prescriptions. Allow Caiaphas/Pilate/Judas/etc
    # in the forbidden-pattern list, since they're listed as *what to avoid*.
    # Only check for hero strings outside of quoted patterns.
    # Simplification: make sure 'peter said' style does not appear (not in our patterns).
    assert "peter said" not in src.lower()
    assert "베드로" not in src


# ============ End-to-end pipeline ============

def test_end_to_end_produces_at_least_one_viable():
    """Plan §13 acceptance: at least one strong_viable or viable_with_gaps."""
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    grades: list[str] = []
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t, cross_seed_frequency=5)
        grades.append(sc.grade)
    assert any(g in {"strong_viable", "viable_with_gaps"} for g in grades), (
        f"plan §13 acceptance failed — no viable candidate: {grades}"
    )


def test_audit_fail_zero_on_real_run():
    """Plan §15 'Ship' decision requires audit_fail=0."""
    cands = _real_candidates()
    if not cands:
        pytest.skip("no candidates")
    failures: list[str] = []
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        ar = audit_pair(b, t)
        if ar.overall == "audit_fail":
            failures.append(c.story_candidate_id)
    assert not failures, f"audit_fail on {failures}"
