"""Tests for genre_audit (Phase 2.75 §11)."""
from __future__ import annotations

from dataclasses import replace

import pytest

from engine.observer.genre_adapter import (
    GenreAdaptedFlow, GenreAdaptedOutput, GenreAdaptedSeed,
    adapt_skeleton_to_genre,
)
from engine.observer.genre_audit import GenreAuditResult, audit_genre_output
from engine.observer.genre_rulebook import load_audit_blocklist, load_rulebook

from tests.test_genre.test_genre_adapter import _make_clean_skeleton


def _build_clean_output() -> GenreAdaptedOutput:
    rb = load_rulebook("korean_morning_melodrama")
    return adapt_skeleton_to_genre(_make_clean_skeleton(), rb)


# ---------------------------------------------------------------------------
# 1. Pass case
# ---------------------------------------------------------------------------

def test_audit_passes_clean_genre_output():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    result = audit_genre_output(out, bl)
    assert result.overall == "pass"
    assert not result.forbidden_event_violations
    assert not result.dialogue_violations
    assert not result.source_imitation_violations
    assert not result.evidence_violations


# ---------------------------------------------------------------------------
# 2. Forbidden event tokens (Plan §11.1)
# ---------------------------------------------------------------------------

def test_audit_catches_forbidden_event_in_premise():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    # Inject "출생의 비밀" into the first adapted seed's premise
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(
        bad_seeds[0],
        adapted_premise_ko=bad_seeds[0].adapted_premise_ko + " 출생의 비밀",
    )
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("출생의 비밀" in v for v in result.forbidden_event_violations)


def test_audit_catches_forbidden_event_in_flow_outline():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_outline = list(out.adapted_flow.adapted_outline_ko)
    bad_outline[0] = "1. 평온한 표면 — 사실은 살인 사건이 발생한다."
    bad_flow = replace(out.adapted_flow, adapted_outline_ko=tuple(bad_outline))
    bad_out = replace(out, adapted_flow=bad_flow)
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("살인" in v for v in result.forbidden_event_violations)


# ---------------------------------------------------------------------------
# 3. Dialogue audit (Plan §11.2)
# ---------------------------------------------------------------------------

def test_audit_catches_dialogue_quotes():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(
        bad_seeds[0],
        adapted_premise_ko="“정말 미안해”라고 외쳤다",
    )
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("“" in v or "외쳤다" in v for v in result.dialogue_violations)


def test_audit_catches_라고_말했다():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(
        bad_seeds[0],
        cliffhanger_ko="이건 끝이라고 말했다",
    )
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("라고 말했다" in v for v in result.dialogue_violations)


# ---------------------------------------------------------------------------
# 4. Source imitation audit (Plan §5.3)
# ---------------------------------------------------------------------------

def test_audit_catches_source_imitation():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_flow = replace(
        out.adapted_flow,
        title_ko="아내의 유혹 — 막장 변환",
    )
    bad_out = replace(out, adapted_flow=bad_flow)
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("아내의 유혹" in v for v in result.source_imitation_violations)


# ---------------------------------------------------------------------------
# 5. Evidence preservation audit (Plan §11.3)
# ---------------------------------------------------------------------------

def test_audit_catches_missing_source_seed_id():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(bad_seeds[0], source_seed_id="")
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("source_seed_id" in v for v in result.evidence_violations)


def test_audit_catches_non_structure_only_transformation():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(
        bad_seeds[0], transformation_level="full_rewrite",
    )
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("structure_only" in v for v in result.evidence_violations)


def test_audit_catches_evidence_preserved_false():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(bad_seeds[0], evidence_preserved=False)
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("evidence_preserved" in v for v in result.evidence_violations)


def test_audit_catches_forbidden_added_true():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    bad_seeds = list(out.adapted_seeds)
    bad_seeds[0] = replace(bad_seeds[0], forbidden_added=True)
    bad_out = replace(out, adapted_seeds=tuple(bad_seeds))
    result = audit_genre_output(bad_out, bl)
    assert result.overall == "fail"
    assert any("forbidden_added" in v for v in result.evidence_violations)


def test_audit_catches_genre_id_mismatch():
    out = _build_clean_output()
    # blocklist for a different genre
    from engine.observer.genre_rulebook import GenreAuditBlocklist
    wrong_bl = GenreAuditBlocklist(
        schema_version="genre_audit_blocklist_v1",
        genre_id="some_other_genre",
        forbidden_event_tokens=(),
        forbidden_dialogue_markers=(),
        forbidden_source_imitation=(),
    )
    result = audit_genre_output(out, wrong_bl)
    assert result.overall == "fail"
    assert any("genre_id mismatch" in v for v in result.evidence_violations)


# ---------------------------------------------------------------------------
# 6. Result serialization
# ---------------------------------------------------------------------------

def test_audit_result_to_dict():
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = _build_clean_output()
    result = audit_genre_output(out, bl)
    d = result.to_dict()
    assert d["overall"] == "pass"
    assert d["genre_id"] == "korean_morning_melodrama"
    assert isinstance(d["forbidden_event_violations"], list)
