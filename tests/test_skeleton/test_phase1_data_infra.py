"""Tests for Phase 1 data infrastructure.

Per `docs/witness_narrative_mode_plan.md` Phase 1:
    - synopsis schema: structure-only validation, no network
    - selection log skeletons exist
    - annotation guide content matches Plan §5.3 / §6 phase 2
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# Synopsis schema
# ============================================================================

def test_synopsis_schema_module_imports_cleanly():
    from scripts.data.synopsis_schema import (
        SCHEMA_VERSION,
        EpisodeSynopsis,
        SelectionEntry,
        validate_episode_dict,
        episode_path,
        write_episode,
        load_episode,
        now_iso_utc,
    )
    assert SCHEMA_VERSION.startswith("synopsis_v")


def test_validate_episode_dict_catches_missing_fields():
    from scripts.data.synopsis_schema import validate_episode_dict
    errs = validate_episode_dict({})
    assert errs
    assert any("schema_version" in e or "missing" in e for e in errs)


def test_validate_episode_dict_catches_bad_category():
    from scripts.data.synopsis_schema import (
        validate_episode_dict, SCHEMA_VERSION,
    )
    bad = {
        "schema_version": SCHEMA_VERSION,
        "title_id": "x",
        "title_ko": "한국어",
        "title_en": "X",
        "category": "drama",  # invalid — must be melodrama|control
        "episode_no": 1,
        "synopsis_text_ko": "...",
        "source_url": "http://...",
        "source_license": "CC-BY-SA-4.0",
        "fetched_at_iso": "2026-05-09T00:00:00Z",
    }
    errs = validate_episode_dict(bad)
    assert any("category" in e for e in errs)


def test_validate_episode_dict_accepts_valid_record():
    from scripts.data.synopsis_schema import (
        validate_episode_dict, SCHEMA_VERSION,
    )
    good = {
        "schema_version": SCHEMA_VERSION,
        "title_id": "test_title",
        "title_ko": "테스트 작품",
        "title_en": "Test Title",
        "category": "melodrama",
        "episode_no": 5,
        "synopsis_text_ko": "회차 줄거리.",
        "source_url": "https://example.com/wiki/x",
        "source_license": "CC-BY-SA-4.0",
        "fetched_at_iso": "2026-05-09T00:00:00Z",
    }
    errs = validate_episode_dict(good)
    assert not errs, f"unexpected errors: {errs}"


def test_episode_synopsis_dataclass_writes_to_canonical_path(tmp_path, monkeypatch):
    from scripts.data import synopsis_schema as ss
    # Redirect ROOT to tmp for this test
    monkeypatch.setattr(ss, "ROOT", tmp_path)
    from scripts.data.synopsis_schema import (
        EpisodeSynopsis, episode_path, write_episode, load_episode,
    )
    syn = EpisodeSynopsis(
        title_id="t", title_ko="제목", title_en="T",
        category="melodrama", episode_no=3,
        synopsis_text_ko="줄거리",
        source_url="http://x", source_license="public",
        fetched_at_iso="2026-05-09T00:00:00Z",
    )
    p = write_episode(syn)
    assert p.exists()
    assert p.parent.name == "episodes"
    assert p.name == "03.json"
    # round trip
    d = load_episode(p)
    assert d["title_id"] == "t"
    assert d["episode_no"] == 3


# ============================================================================
# Selection log skeletons
# ============================================================================

def test_selection_logs_exist_for_both_categories():
    for cat in ("melodrama", "control"):
        p = ROOT / "data" / "raw" / cat / "_selection_log.json"
        assert p.exists()
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d["_meta"]["category"] == cat
        assert d["_meta"]["criteria_doc"] == "docs/data/SELECTION_CRITERIA.md"


# ============================================================================
# Annotation guide content
# ============================================================================

def test_annotation_guide_exists_and_covers_required_features():
    p = ROOT / "docs" / "annotation" / "ANNOTATION_GUIDE.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    # Plan §2.3의 7 features 모두 명시 (Phase 2.5 renamed)
    for feature in (
        "conflict_intensity_peak",
        "revelation_density",
        "coincidence_frequency",
        "relationship_polarization",
        "new_conflict_introduction_rate",
        "dangling_thread_generation",
        "cliffhanger_intensity",
    ):
        assert feature in text, f"ANNOTATION_GUIDE.md missing feature: {feature}"


def test_annotation_guide_specifies_multi_ai_synthesis():
    p = ROOT / "docs" / "annotation" / "ANNOTATION_GUIDE.md"
    text = p.read_text(encoding="utf-8")
    for required in ("multi-AI", "Cohen", "Pearson", "evidence_quote"):
        assert required in text, f"ANNOTATION_GUIDE.md missing: {required}"


def test_annotation_guide_states_phase2_acceptance_mapping():
    p = ROOT / "docs" / "annotation" / "ANNOTATION_GUIDE.md"
    text = p.read_text(encoding="utf-8")
    assert "Phase 2 acceptance" in text


# ============================================================================
# CLI smoke
# ============================================================================

def test_collect_synopsis_cli_help_runs():
    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/data/collect_synopsis.py"), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_collect_synopsis_list_candidates_handles_empty_log():
    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/data/collect_synopsis.py"),
         "list-candidates", "--category", "melodrama"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # Empty list should still exit 0 + report 'No candidates yet'
    assert rc.returncode == 0
    assert "No candidates" in rc.stdout or "candidates yet" in rc.stdout


# ============================================================================
# README skeleton-flesh framing
# ============================================================================

def test_readme_mentions_skeleton_flesh_dual_structure():
    """Phase 2.9: README가 ML Flesh Engine을 *완료된 것처럼* 표현하지 않으면서
    뼈대/살 이중 구조는 유지해야 한다.

    "Narrative Mode" 명시는 Phase 2.9 §4 Issue 1에서 의도적으로 제거됨
    (rule-based Genre Adapter가 현재 / ML Flesh Engine은 Phase 3 후).
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "뼈대" in readme and "살" in readme
    # plan link 보유 (모ㅏplan)
    assert "witness_narrative_mode_plan.md" in readme
    # Phase 2.9: rule-based Genre Adapter / Phase 3.0 Pilot 명시
    assert "Genre Adapter" in readme or "장르 변환" in readme or "장르 어댑터" in readme
    assert "Phase 3" in readme
