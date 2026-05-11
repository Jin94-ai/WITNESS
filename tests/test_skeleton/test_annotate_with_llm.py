"""Tests for annotate_with_llm.py (Phase 2 산출).

Per `docs/witness_narrative_mode_plan.md` §6 Phase 2 산출물:
    scripts/annotation/annotate_with_llm.py

이 스크립트는 *네트워크 호출 0*. dry-run 모드로 prompt 빌드 + fixture 모드로
LLM 응답 검증을 검증한다. 실제 live 모드는 별도 turn에서 ToS 확인 후 추가.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/annotation/annotate_with_llm.py"


# ============================================================================
# Helpers
# ============================================================================

def _make_synopsis() -> dict:
    return {
        "schema_version": "synopsis_v1",
        "title_id": "test_drama",
        "title_ko": "테스트 드라마",
        "title_en": "Test Drama",
        "category": "melodrama",
        "episode_no": 5,
        "synopsis_text_ko": "5회차 줄거리 — 인물들의 비밀이 드러나는 시점.",
        "source_url": "https://example.com/wiki/test_drama/episode_5",
        "source_license": "CC-BY-SA-4.0",
        "fetched_at_iso": "2026-05-09T00:00:00Z",
    }


def _make_response() -> dict:
    return {
        "schema_version": "annotation_v1",
        "title_id": "test_drama",
        "episode_no": 5,
        "annotator_id": "claude-3.5-sonnet",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {
            "conflict_intensity_peak": 0.6,
            "revelation_density": 0.7,
            "coincidence_frequency": 0.4,
            "relationship_polarization": 0.5,
            "new_conflict_introduction_rate": 0.5,
            "dangling_thread_generation": 0.3,
            "cliffhanger_intensity": 0.8,
        },
        "evidence_quotes": [
            {"feature": "revelation_density", "quote_ko": "비밀이 드러나는 시점"},
        ],
        "confidence": 0.75,
        "notes": [],
    }


# ============================================================================
# 1. CLI smoke
# ============================================================================

def test_help_runs():
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_subcommands_listed_in_help():
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert "dry-run" in rc.stdout
    assert "fixture" in rc.stdout


# ============================================================================
# 2. dry-run mode — build prompt
# ============================================================================

def test_dry_run_builds_prompt_file(tmp_path):
    syn_path = tmp_path / "ep05.json"
    syn_path.write_text(json.dumps(_make_synopsis()), encoding="utf-8")
    out = tmp_path / "prompts" / "ep05_claude.txt"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "dry-run",
         "--episode", str(syn_path),
         "--annotator-id", "claude-3.5-sonnet",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    # 헤더에 metadata
    assert "title_id: test_drama" in text
    assert "episode_no: 5" in text
    assert "annotator_id: claude-3.5-sonnet" in text
    # SYSTEM + USER prompt 모두 포함
    assert "=== SYSTEM PROMPT ===" in text
    assert "=== USER PROMPT ===" in text
    # 7 features 포함 (USER prompt 안)
    for f in (
        "conflict_intensity_peak",
        "revelation_density",
        "cliffhanger_intensity",
    ):
        assert f in text


def test_dry_run_rejects_invalid_synopsis(tmp_path):
    bad = tmp_path / "bad.json"
    # missing required fields
    bad.write_text(json.dumps({"schema_version": "synopsis_v1"}), encoding="utf-8")
    out = tmp_path / "p.txt"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "dry-run",
         "--episode", str(bad),
         "--annotator-id", "claude",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1
    assert not out.exists()


def test_dry_run_rejects_missing_synopsis(tmp_path):
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "dry-run",
         "--episode", str(tmp_path / "missing.json"),
         "--annotator-id", "claude",
         "--output", str(tmp_path / "out.txt")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1


# ============================================================================
# 3. fixture mode — validate + save LLM response
# ============================================================================

def test_fixture_validates_and_saves_valid_response(tmp_path):
    response_path = tmp_path / "response.json"
    response_path.write_text(json.dumps(_make_response()), encoding="utf-8")
    out = tmp_path / "annotated" / "test_drama" / "05.json"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "fixture",
         "--response", str(response_path),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["title_id"] == "test_drama"
    assert saved["episode_no"] == 5
    assert saved["features"]["cliffhanger_intensity"] == 0.8


def test_fixture_rejects_out_of_range_features(tmp_path):
    bad = _make_response()
    bad["features"]["cliffhanger_intensity"] = 1.5  # out of range
    response_path = tmp_path / "response.json"
    response_path.write_text(json.dumps(bad), encoding="utf-8")
    out = tmp_path / "annotated" / "x" / "01.json"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "fixture",
         "--response", str(response_path),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1
    assert not out.exists()


def test_fixture_migrate_deprecated_v1_to_v1_1(tmp_path):
    """Phase 2.5 cycle 7: --migrate-deprecated 플래그가 v1 응답을 자동 변환."""
    v1_response = {
        "schema_version": "annotation_v1",
        "title_id": "test_drama",
        "episode_no": 5,
        "annotator_id": "claude-v1",
        "annotated_at_iso": "2026-04-15T00:00:00Z",
        "features": {
            "conflict_amplification_rate": 0.4,    # v1 name
            "revelation_density": 0.5,
            "coincidence_frequency": 0.3,
            "relationship_polarization": 0.6,
            "new_conflict_introduction_rate": 0.4,
            "resolution_to_dangling_ratio": 0.4,    # v1 name
            "cliffhanger_intensity": 0.7,
        },
        "evidence_quotes": [
            {"feature": "conflict_amplification_rate", "quote_ko": "갈등 폭발"},
        ],
        "confidence": 0.7,
    }
    response_path = tmp_path / "response.json"
    response_path.write_text(json.dumps(v1_response), encoding="utf-8")
    out = tmp_path / "annotated" / "test_drama" / "05.json"

    # without --migrate-deprecated → fail with hint
    rc_no = subprocess.run(
        [sys.executable, str(SCRIPT), "fixture",
         "--response", str(response_path),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_no.returncode == 1
    assert "missing feature" in rc_no.stderr
    assert "migrate-deprecated" in rc_no.stderr
    assert not out.exists()

    # with --migrate-deprecated → success, saved with v1.1 names
    rc_ok = subprocess.run(
        [sys.executable, str(SCRIPT), "fixture",
         "--response", str(response_path),
         "--output", str(out),
         "--migrate-deprecated"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_ok.returncode == 0, rc_ok.stderr
    assert out.exists()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert "conflict_intensity_peak" in saved["features"]
    assert "dangling_thread_generation" in saved["features"]
    assert "conflict_amplification_rate" not in saved["features"]
    # evidence_quote feature 필드도 변환
    assert saved["evidence_quotes"][0]["feature"] == "conflict_intensity_peak"


def test_fixture_rejects_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    out = tmp_path / "out.json"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "fixture",
         "--response", str(bad),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1


# ============================================================================
# 4. End-to-end: dry-run prompt → fixture validation
# ============================================================================

def test_e2e_dry_run_prompt_matches_fixture_response_schema(tmp_path):
    """dry-run의 prompt에 명시된 schema_version이 fixture가 검증하는 schema와 일치."""
    syn_path = tmp_path / "ep05.json"
    syn_path.write_text(json.dumps(_make_synopsis()), encoding="utf-8")
    prompt_out = tmp_path / "prompt.txt"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "dry-run",
         "--episode", str(syn_path),
         "--annotator-id", "claude",
         "--output", str(prompt_out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0
    text = prompt_out.read_text(encoding="utf-8")
    # dry-run header should reference annotation_v1
    assert "annotation_v1" in text
