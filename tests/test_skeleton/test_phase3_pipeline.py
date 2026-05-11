"""Phase 3.0 v1.1 Pipeline tests — Mode A (manual input) end-to-end.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10+§16.

검증 대상 스크립트 (외부 의존 0):
    1. scripts/data/normalize_synopsis.py
    2. scripts/data/validate_synopsis_dataset.py
    3. scripts/data/build_annotation_inputs.py
    4. scripts/data/build_public_safe_dataset.py
    5. scripts/annotation/validate_annotation_outputs.py
    6. scripts/annotation/build_feature_matrix.py
    7. scripts/annotation/build_reliability_report.py
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *cmd],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_raw_synopsis_dir(tmp_path: Path, count: int = 3) -> Path:
    """raw private synopsis dir에 .json 파일 N개 생성."""
    raw_dir = tmp_path / "synopsis_raw"
    raw_dir.mkdir()
    for i in range(1, count + 1):
        record = {
            "genre_id": "korean_morning_melodrama",
            "title_id": "titleA",
            "episode_number": i,
            "synopsis_text": (
                f"베드로는 회차 {i}에서 침묵을 선택하고, "
                "권위자의 시선이 좁혀오는 가운데 결정을 미룬다."
            ),
            "source_name": "manual_input",
            "fetched_at": "2026-05-11",
            "public_safe_summary": f"ep{i} 짧은 요약",
        }
        (raw_dir / f"titleA_ep{i:02d}.json").write_text(
            json.dumps(record, ensure_ascii=False), encoding="utf-8",
        )
    return raw_dir


def _make_annotation_output(
    record_id: str, annotator_id: str, scores: dict[str, int],
    quotes: dict[str, list[str]] | None = None,
) -> dict:
    return {
        "annotation_id": f"ann_{annotator_id}_{record_id}",
        "record_id": record_id,
        "annotator_id": annotator_id,
        "genre_id": "korean_morning_melodrama",
        "features": dict(scores),
        "evidence_quotes": quotes or {},
        "confidence": {"overall": 0.78},
        "warnings": [],
    }


# ---------------------------------------------------------------------------
# 1. normalize_synopsis.py
# ---------------------------------------------------------------------------

NORM = ROOT / "scripts/data/normalize_synopsis.py"


def test_normalize_help():
    rc = _run([str(NORM), "--help"])
    assert rc.returncode == 0


def test_normalize_json_records(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=3)
    out = tmp_path / "normalized.jsonl"
    rc = _run([str(NORM), "--input", str(raw), "--output", str(out)])
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    lines = [
        json.loads(line)
        for line in out.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == 3
    # record_id deterministic
    assert lines[0]["record_id"] == "km_titleA_ep001"
    assert lines[2]["record_id"] == "km_titleA_ep003"
    # raw_text_storage = "private"
    assert all(r["raw_text_storage"] == "private" for r in lines)


def test_normalize_txt_records(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "titleB_ep01.txt").write_text(
        "회차 1 줄거리: 권위자의 시선이 깊어진다. 침묵이 길어진다.",
        encoding="utf-8",
    )
    out = tmp_path / "norm.jsonl"
    rc = _run([str(NORM), "--input", str(raw), "--output", str(out)])
    assert rc.returncode == 0, rc.stderr
    d = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(d) == 1
    assert d[0]["title_id"] == "titleB"
    assert d[0]["episode_number"] == 1


def test_normalize_handles_missing_dir(tmp_path):
    rc = _run([str(NORM),
                "--input", str(tmp_path / "nonexistent"),
                "--output", str(tmp_path / "out.jsonl")])
    assert rc.returncode == 2


# ---------------------------------------------------------------------------
# 2. validate_synopsis_dataset.py
# ---------------------------------------------------------------------------

VAL_DS = ROOT / "scripts/data/validate_synopsis_dataset.py"


def test_validate_dataset_clean(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=3)
    out = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(out)])
    rc = _run([str(VAL_DS), "--input", str(out)])
    assert rc.returncode == 0, rc.stderr
    assert "PASS" in rc.stdout


def test_validate_catches_short_synopsis(tmp_path):
    out = tmp_path / "norm.jsonl"
    out.write_text(json.dumps({
        "schema_version": "episode_synopsis_record_v1",
        "record_id": "km_t_ep001", "genre_id": "korean_morning_melodrama",
        "title_id": "t", "episode_number": 1, "source_name": "x",
        "raw_text_storage": "private", "synopsis_text": "짧음",  # too short
    }), encoding="utf-8")
    rc = _run([str(VAL_DS), "--input", str(out)])
    assert rc.returncode == 1
    assert "synopsis_text too short" in rc.stdout


def test_validate_catches_duplicate_record_id(tmp_path):
    out = tmp_path / "norm.jsonl"
    rec = {
        "schema_version": "episode_synopsis_record_v1",
        "record_id": "km_t_ep001", "genre_id": "korean_morning_melodrama",
        "title_id": "t", "episode_number": 1, "source_name": "x",
        "raw_text_storage": "private",
        "synopsis_text": "충분히 긴 줄거리 텍스트입니다 — 베드로의 침묵.",
    }
    out.write_text(
        json.dumps(rec) + "\n" + json.dumps(rec) + "\n", encoding="utf-8",
    )
    rc = _run([str(VAL_DS), "--input", str(out)])
    assert rc.returncode == 1
    assert "duplicate record_id" in rc.stdout


def test_validate_strict_min_records(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=3)
    out = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(out)])
    rc = _run([str(VAL_DS), "--input", str(out), "--strict-min-records", "10"])
    assert rc.returncode == 1
    assert "< required min" in rc.stdout


# ---------------------------------------------------------------------------
# 3. build_annotation_inputs.py
# ---------------------------------------------------------------------------

BUILD_INPUTS = ROOT / "scripts/data/build_annotation_inputs.py"


def test_build_annotation_inputs(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=2)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    inputs_dir = tmp_path / "annotation_inputs"
    rc = _run([
        str(BUILD_INPUTS),
        "--input", str(norm),
        "--output", str(inputs_dir),
    ])
    assert rc.returncode == 0, rc.stderr
    files = list(inputs_dir.glob("*.json"))
    assert len(files) == 2
    sample = json.loads(files[0].read_text(encoding="utf-8"))
    assert sample["task"] == "annotate_episode_synopsis_v1"
    assert sample["output_schema"] == "episode_annotation_v1"
    assert "synopsis_text" in sample
    assert isinstance(sample["features_to_score"], list)
    assert "conflict_intensity_peak" in sample["features_to_score"]
    assert "instructions_ko" in sample


# ---------------------------------------------------------------------------
# 4. build_public_safe_dataset.py
# ---------------------------------------------------------------------------

BUILD_PS = ROOT / "scripts/data/build_public_safe_dataset.py"


def test_build_public_safe_redacts_synopsis(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=2)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    out = tmp_path / "public_safe.jsonl"
    rc = _run([str(BUILD_PS), "--input", str(norm), "--output", str(out)])
    assert rc.returncode == 0, rc.stderr
    lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    for r in lines:
        # synopsis_text 절대 없어야
        assert "synopsis_text" not in r
        # source_url 제거
        assert "source_url" not in r
        # public_safe_summary 또는 redacted
        assert r["public_safe_summary"]
        assert r["schema_version"] == "public_safe_dataset_v1"


def test_public_safe_max_length(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    long_summary = "가" * 200
    (raw / "titleA_ep01.json").write_text(json.dumps({
        "genre_id": "korean_morning_melodrama",
        "title_id": "titleA", "episode_number": 1,
        "synopsis_text": "충분히 긴 줄거리 텍스트입니다 — 베드로의 침묵.",
        "public_safe_summary": long_summary,
    }), encoding="utf-8")
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    out = tmp_path / "ps.jsonl"
    rc = _run([str(BUILD_PS), "--input", str(norm), "--output", str(out),
                "--max-summary-length", "30"])
    assert rc.returncode == 0
    d = json.loads(out.read_text(encoding="utf-8").strip())
    assert len(d["public_safe_summary"]) <= 35  # 30 + ellipsis


# ---------------------------------------------------------------------------
# 5. validate_annotation_outputs.py
# ---------------------------------------------------------------------------

VAL_OUT = ROOT / "scripts/annotation/validate_annotation_outputs.py"


def test_validate_outputs_clean(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=2)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])

    outputs = tmp_path / "outputs"
    outputs.mkdir()
    for i in (1, 2):
        rid = f"km_titleA_ep{i:03d}"
        # quote가 원본에 실제 등장 (synopsis text의 공통 phrase)
        ann = _make_annotation_output(
            rid, "modelA",
            scores={"conflict_intensity_peak": 4, "dangling_thread_generation": 3},
            quotes={"conflict_intensity_peak": ["권위자의 시선"]},
        )
        (outputs / f"{rid}_modelA.json").write_text(
            json.dumps(ann, ensure_ascii=False), encoding="utf-8",
        )

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0, rc.stderr
    assert "validated:" in rc.stdout
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    assert summary["hallucination_rate"] == 0.0
    assert summary["phase3_threshold_pass"] is True


def test_validate_outputs_catches_hallucination(tmp_path):
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    rid = "km_titleA_ep001"
    ann = _make_annotation_output(
        rid, "modelA", scores={"conflict_intensity_peak": 4},
        quotes={"conflict_intensity_peak": ["원본에 절대 없는 인용"]},
    )
    (outputs / f"{rid}_modelA.json").write_text(
        json.dumps(ann, ensure_ascii=False), encoding="utf-8",
    )
    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0  # quote miss는 schema fail 아님 (warning)
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    assert summary["hallucination_rate"] == 1.0
    assert summary["phase3_threshold_pass"] is False
    assert summary["phase3_threshold_no_go"] is True


def test_validate_outputs_strict_fails_on_schema_violation(tmp_path):
    """Phase 3.05 Step 3: --strict는 --synopsis 필요 (그것이 충족된 후 schema violation 시 exit 1)."""
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])

    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # missing required fields
    (outputs / "bad.json").write_text(json.dumps({"record_id": "x"}), encoding="utf-8")
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--strict"])
    assert rc.returncode == 1


def test_validate_outputs_strict_requires_synopsis(tmp_path):
    """Phase 3.05 Step 3: --strict + --synopsis 없음 → exit 2.

    이유: quote hallucination check는 원본 synopsis가 있어야 의미가 있다.
    strict mode에서 synopsis 없이 통과시키면 hallucination 검사가 무력화된다.
    """
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # schema가 valid해도 strict mode이면 synopsis 강제
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--strict"])
    assert rc.returncode == 2
    assert "--strict requires --synopsis" in rc.stderr or "synopsis" in rc.stderr.lower()


def test_validate_outputs_non_strict_runs_without_synopsis(tmp_path):
    """Phase 3.05 Step 3: --strict 아닌 경우 synopsis 없이도 정상 동작 (backwards compat)."""
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    rc = _run([str(VAL_OUT), "--input", str(outputs)])
    assert rc.returncode == 0


def test_validate_outputs_report_has_valid_only_summary(tmp_path):
    """Phase 3.05 Step 4: hallucination report에 valid_files_only_summary / all_files_summary / invalid_files 3 layer."""
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # 1 valid annotation
    valid_ann = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 4},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},
    )
    (outputs / "valid.json").write_text(
        json.dumps(valid_ann, ensure_ascii=False), encoding="utf-8",
    )
    # 1 invalid annotation (missing required fields)
    (outputs / "invalid.json").write_text(
        json.dumps({"record_id": "x"}), encoding="utf-8",
    )

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0  # non-strict, schema fail은 warning만
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    # Phase 3.05 Step 4 — 3 layer 분리 존재
    assert "valid_files_only_summary" in summary
    assert "all_files_summary" in summary
    assert "invalid_files" in summary
    valid = summary["valid_files_only_summary"]
    all_ = summary["all_files_summary"]
    assert valid["n_files"] == 1   # 1 valid
    assert all_["n_files"] == 2    # 1 valid + 1 invalid (schema fail은 per_file_stats엔 있음)
    # invalid files 목록에 invalid.json
    invalid = summary["invalid_files"]
    assert len(invalid) == 1
    assert invalid[0]["path"] == "invalid.json"
    # top-level threshold = valid_files_only 기준
    assert summary["phase3_threshold_pass"] is True
    assert summary["hallucination_rate"] == 0.0  # valid file은 quote 정확


def test_validate_outputs_invalid_files_dont_pollute_valid_summary(tmp_path):
    """Phase 3.05 Step 4: invalid file의 hallucinated quote가 valid_files_only_summary에 섞이지 않음."""
    raw = _make_raw_synopsis_dir(tmp_path, count=2)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # valid: substring 매칭 (hallucination 0)
    valid_ann = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 4},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},
    )
    (outputs / "valid.json").write_text(
        json.dumps(valid_ann, ensure_ascii=False), encoding="utf-8",
    )
    # invalid: schema OK이지만 invalid score (out of range) + hallucinated quote
    invalid_ann = _make_annotation_output(
        "km_titleA_ep002", "modelA",
        scores={"conflict_intensity_peak": 999},  # out of range
        quotes={"conflict_intensity_peak": ["완전히 fake한 인용"]},
    )
    (outputs / "invalid.json").write_text(
        json.dumps(invalid_ann, ensure_ascii=False), encoding="utf-8",
    )

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    valid = summary["valid_files_only_summary"]
    all_ = summary["all_files_summary"]
    # valid_files_only는 hallucination 0 (valid 파일만 집계)
    assert valid["hallucination_rate"] == 0.0
    assert valid["phase3_threshold_pass"] is True
    # all_files는 invalid의 fake quote 포함 → rate > 0
    assert all_["hallucination_rate"] > 0.0
    # top-level은 valid 기준
    assert summary["hallucination_rate"] == 0.0
    assert summary["phase3_threshold_pass"] is True


def test_validate_outputs_invalid_json_in_invalid_files(tmp_path):
    """Phase 3.05 Step 4: JSON parse fail도 invalid_files 목록에 포함됨."""
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "broken.json").write_text("not json {{", encoding="utf-8")
    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    invalid = summary["invalid_files"]
    assert any(i["path"] == "broken.json" for i in invalid)
    assert any("invalid JSON" in e for i in invalid for e in i["errors"])


# ---------------------------------------------------------------------------
# 9. verify_phase3_0_acceptance.py — Plan §18 12 항목 자동 검증 (cycle 5)
# ---------------------------------------------------------------------------

VERIFY_ACCEPTANCE = ROOT / "scripts/data/verify_phase3_0_acceptance.py"


def test_verify_acceptance_help():
    rc = _run([str(VERIFY_ACCEPTANCE), "--help"])
    assert rc.returncode == 0


def test_verify_acceptance_empty_pilot_fails_auto(tmp_path):
    """Pilot 미운영 상태에서 AUTO FAIL이 검출됨 (exit 1).

    Phase 3.05 cycle 7: approval doc 미존재 시 §18.1/2 MANUAL fallback (n_auto=8 / n_manual=2).
    """
    pilot = tmp_path / "phase3_pilot"  # 미존재 의도적
    report = tmp_path / "report.json"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--raw-private-dir", str(tmp_path / "raw_missing"),
                "--data-card", str(tmp_path / "data_card_missing.md"),
                "--pilot-report", str(tmp_path / "pilot_report_missing.md"),
                "--approval-doc", str(tmp_path / "approval_missing.md"),
                "--source-review-doc", str(tmp_path / "source_review_missing.md"),
                "--output", str(report)])
    assert rc.returncode == 1   # AUTO FAIL 존재
    data = json.loads(report.read_text(encoding="utf-8"))
    summary = data["summary"]
    # 12 항목 모두 검증
    assert summary["n_total"] == 12
    assert summary["n_auto"] == 8        # §18.3-10 (8 AUTO, approval_doc 없어 §18.1/2는 MANUAL)
    assert summary["n_heuristic"] == 2   # §18.11, 12 (2 HEURISTIC)
    assert summary["n_manual"] == 2      # §18.1, 2 (approval_doc fallback)
    assert summary["auto_pass"] < 8      # 일부는 PASS (gitignore 보호 등) 또는 모두 FAIL
    assert summary["auto_fail"] > 0


def test_verify_acceptance_passes_when_all_artifacts_present(tmp_path):
    """모든 산출물 준비 시 AUTO PASS — exit 0."""
    pilot = tmp_path / "phase3_pilot"
    raw = tmp_path / "raw_private"
    pilot.mkdir()
    raw.mkdir()

    # §18.3 — raw synopsis 10+
    for i in range(1, 11):
        (raw / f"titleA_ep{i:02d}.json").write_text(
            json.dumps({"genre_id": "g", "title_id": "t", "episode_number": i,
                        "synopsis_text": "x"}), encoding="utf-8",
        )

    # §18.5 — annotation_inputs
    (pilot / "annotation_inputs").mkdir()
    (pilot / "annotation_inputs" / "a.json").write_text("{}", encoding="utf-8")

    # §18.6 — annotation_outputs
    (pilot / "annotation_outputs").mkdir()
    (pilot / "annotation_outputs" / "a.json").write_text("{}", encoding="utf-8")

    # §18.7-10 — reports
    (pilot / "reports").mkdir()
    (pilot / "reports" / "hallucination_report.json").write_text(json.dumps({
        "invalid_files": [],
        "valid_files_only_summary": {
            "n_files": 10, "hallucination_rate": 0.01, "phase3_threshold_pass": True,
        },
        "all_files_summary": {"n_files": 10, "hallucination_rate": 0.01},
    }), encoding="utf-8")
    (pilot / "reports" / "reliability.json").write_text(json.dumps({
        "summary": {
            "keep": ["f1", "f2", "f3", "f4", "f5"],
            "revise": ["f6"],
            "drop": ["f7"],
            "phase3_threshold_pass": True,
        }
    }), encoding="utf-8")

    # §18.4 — gitignore 보호 검증을 위해 ROOT 안 path 회피 — tmp_path는 outside repo
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--raw-private-dir", str(raw),
                "--data-card", str(tmp_path / "missing_card.md"),  # FAIL 의도적
                "--pilot-report", str(tmp_path / "missing_report.md"),  # FAIL 의도적
                "--approval-doc", str(tmp_path / "approval_missing.md"),  # MANUAL fallback
                "--gitignore", str(tmp_path / "no_gitignore")])
    # AUTO 8개 (§18.3-10) 모두 PASS — approval_doc 없어서 §18.1/2는 MANUAL
    # HEURISTIC 2개는 FAIL (data card / pilot report missing)
    # exit 0 — AUTO 기준이면 PASS (heuristic은 exit code에 영향 0)
    assert rc.returncode == 0, rc.stdout + rc.stderr
    assert "8/8 PASS" in rc.stdout
    assert "AUTO FAIL" not in rc.stdout or "0 FAIL" in rc.stdout


def test_verify_acceptance_detects_unfilled_template(tmp_path):
    """Data Card에 template marker 다수면 HEURISTIC FAIL."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    card = tmp_path / "card.md"
    # template marker 5개 이상
    card.write_text(
        "# Data Card\n\n## §1\nTODO: fill\n\n## §2\nTBD\n\n## §3\nTODO\n\n## §4\n[작성]\n\n## §5\nTODO\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.json"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--data-card", str(card),
                "--output", str(output)])
    data = json.loads(output.read_text(encoding="utf-8"))
    card_check = next(c for c in data["checks"] if c["item_id"] == 11)
    assert card_check["status"] == "FAIL"
    assert "template marker" in card_check["detail"]


def test_verify_acceptance_detects_filled_pilot_report(tmp_path):
    """Pilot Report에 Go/No-Go 키워드 있으면 HEURISTIC PASS."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    report_md = tmp_path / "pilot_report.md"
    report_md.write_text(
        "# Phase 3.0 Pilot Report\n\n## Verdict\n\n판정: GO\n\n"
        "## 상세 분석\n\nhallucination 0% / KEEP feature 5개 / 모든 acceptance 통과.\n"
        "## 다음 단계\n\nPhase 3.1 진입 결정.\n" * 3,
        encoding="utf-8",
    )
    output = tmp_path / "out.json"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--pilot-report", str(report_md),
                "--output", str(output)])
    data = json.loads(output.read_text(encoding="utf-8"))
    verdict_check = next(c for c in data["checks"] if c["item_id"] == 12)
    assert verdict_check["status"] == "PASS"
    assert "Go/No-Go 판정 키워드 발견" in verdict_check["detail"]


def test_verify_acceptance_parse_approval_checklist():
    """Phase 3.05 cycle 7: approval checklist 헤더 파싱.

    `### ☐ N. title` 또는 `### ☑ N. title` 형식 인식.
    """
    from scripts.data.verify_phase3_0_acceptance import parse_approval_checklist
    text = (
        "# Title\n\n"
        "## 1. 핵심 항목\n\n"
        "### ☐ 1. 실제 데이터 fetch 승인\n\n"
        "content\n\n"
        "### ☑ 2. ToS 검토 승인\n\n"
        "more content\n\n"
        "### ☐ 3. LLM API 사용 승인\n"
    )
    items = parse_approval_checklist(text)
    assert len(items) == 3
    assert items[0] == {"item_no": 1, "checked": False, "title": "실제 데이터 fetch 승인"}
    assert items[1] == {"item_no": 2, "checked": True, "title": "ToS 검토 승인"}
    assert items[2] == {"item_no": 3, "checked": False, "title": "LLM API 사용 승인"}


def test_verify_acceptance_approval_all_checked_pass(tmp_path):
    """approval checklist 7/7 모두 체크 → §18.1 PASS (AUTO)."""
    approval = tmp_path / "approval.md"
    approval.write_text(
        "## 1. 5+2 핵심 승인\n\n"
        "### ☑ 1. fetch 승인\n\n"
        "### ☑ 2. ToS 검토\n\n"
        "### ☑ 3. LLM API\n\n"
        "### ☑ 4. 비용 상한\n\n"
        "### ☑ 5. 저장 위치\n\n"
        "### ☑ 6. (보조) repo 정책\n\n"
        "### ☑ 7. (보조) mini pilot\n",
        encoding="utf-8",
    )
    pilot = tmp_path / "p"
    pilot.mkdir()
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--approval-doc", str(approval),
                "--output", str(tmp_path / "report.json")])
    data = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    check_1 = next(c for c in data["checks"] if c["item_id"] == 1)
    check_2 = next(c for c in data["checks"] if c["item_id"] == 2)
    assert check_1["status"] == "PASS"
    assert check_1["category"] == "AUTO"
    assert check_2["status"] == "PASS"
    assert check_2["category"] == "AUTO"
    assert "7/7" in check_1["detail"]


def test_verify_acceptance_approval_partial_pending(tmp_path):
    """partial check → §18.1 PENDING (AUTO, exit 0)."""
    approval = tmp_path / "approval.md"
    approval.write_text(
        "## 1. 항목\n\n"
        "### ☑ 1. fetch\n\n"
        "### ☐ 2. ToS\n\n"
        "### ☐ 3. LLM\n",
        encoding="utf-8",
    )
    pilot = tmp_path / "p"
    pilot.mkdir()
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--approval-doc", str(approval),
                "--output", str(tmp_path / "report.json")])
    data = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    check_1 = next(c for c in data["checks"] if c["item_id"] == 1)
    check_2 = next(c for c in data["checks"] if c["item_id"] == 2)
    assert check_1["status"] == "PENDING"
    assert check_1["category"] == "AUTO"
    assert check_2["status"] == "PENDING"  # #2가 unchecked
    assert "1/3" in check_1["detail"] or "체크리스트 1" in check_1["detail"]
    # exit code: PENDING은 FAIL 아님 — auto_fail 기준
    assert data["summary"]["auto_pending"] >= 1


def test_verify_acceptance_approval_missing_falls_back_to_manual(tmp_path):
    """approval doc 없으면 MANUAL fallback (backwards compat)."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--approval-doc", str(tmp_path / "nonexistent.md"),
                "--source-review-doc", str(tmp_path / "nonexistent2.md"),
                "--output", str(tmp_path / "report.json")])
    data = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    check_1 = next(c for c in data["checks"] if c["item_id"] == 1)
    check_2 = next(c for c in data["checks"] if c["item_id"] == 2)
    assert check_1["status"] == "MANUAL"
    assert check_1["category"] == "MANUAL"
    assert check_2["status"] == "MANUAL"


def test_verify_acceptance_md_report_output(tmp_path):
    """Phase 3.05 cycle 11: --md-report flag — markdown 보고서 export."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    md_out = tmp_path / "report.md"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--approval-doc", str(tmp_path / "missing.md"),
                "--md-report", str(md_out)])
    # md report 파일 생성됨
    assert md_out.exists()
    text = md_out.read_text(encoding="utf-8")
    # markdown 구조 검증
    assert "# Phase 3.0 §18 Acceptance Verification Report" in text
    assert "## Summary" in text
    assert "## 12 Acceptance 항목별 결과" in text
    assert "| § | 항목 | Category | Status | 상세 |" in text
    # 12 항목 모두 표에 (각 행이 "| 18." 시작)
    n_rows = text.count("| 18.")
    assert n_rows == 12
    # status legend
    assert "PENDING" in text
    assert "MANUAL" in text
    # generated timestamp
    assert "Generated:" in text


def test_verify_acceptance_md_report_with_passed_state(tmp_path):
    """md-report에 PASS 상태도 정확히 표시됨."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    raw = tmp_path / "raw"
    raw.mkdir()
    # 10 raw files for §18.3 PASS
    for i in range(1, 11):
        (raw / f"a{i:02d}.json").write_text("{}", encoding="utf-8")

    md_out = tmp_path / "report.md"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--raw-private-dir", str(raw),
                "--approval-doc", str(tmp_path / "missing.md"),
                "--gitignore", str(tmp_path / "no_gi"),  # outside repo → §18.4 PASS
                "--md-report", str(md_out)])
    text = md_out.read_text(encoding="utf-8")
    # §18.3 PASS (10 raw files)
    assert "✓ PASS" in text
    # §18.4 PASS
    # FAIL 행도 존재 (annotation_inputs etc 없음)
    assert "✗ FAIL" in text


def test_verify_acceptance_real_approval_checklist():
    """실제 docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md 파싱 — 7 항목 인식."""
    from scripts.data.verify_phase3_0_acceptance import parse_approval_checklist
    doc = ROOT / "docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md"
    if not doc.exists():
        pytest.skip("approval doc missing")
    items = parse_approval_checklist(doc.read_text(encoding="utf-8"))
    # 5+2 = 7개
    assert len(items) == 7
    # 모두 unchecked (현재 상태)
    assert all(not i["checked"] for i in items)
    # 순서 보존
    assert [i["item_no"] for i in items] == [1, 2, 3, 4, 5, 6, 7]


def test_verify_acceptance_exit_code_only_auto_fails(tmp_path):
    """exit code 1 조건: AUTO FAIL만 의존. HEURISTIC FAIL은 exit 0에 영향 0."""
    pilot = tmp_path / "p"
    pilot.mkdir()
    raw = tmp_path / "raw"
    raw.mkdir()
    # AUTO 8개 모두 PASS 가능하게 준비
    for i in range(1, 11):
        (raw / f"a{i}.json").write_text("{}", encoding="utf-8")
    (pilot / "annotation_inputs").mkdir()
    (pilot / "annotation_inputs" / "a.json").write_text("{}", encoding="utf-8")
    (pilot / "annotation_outputs").mkdir()
    (pilot / "annotation_outputs" / "a.json").write_text("{}", encoding="utf-8")
    (pilot / "reports").mkdir()
    (pilot / "reports" / "hallucination_report.json").write_text(json.dumps({
        "invalid_files": [],
        "valid_files_only_summary": {"n_files": 10, "hallucination_rate": 0.0},
    }), encoding="utf-8")
    (pilot / "reports" / "reliability.json").write_text(json.dumps({
        "summary": {"keep": ["a", "b", "c", "d"], "revise": [], "drop": []}
    }), encoding="utf-8")

    # HEURISTIC 모두 FAIL이어도 (data_card / pilot_report 미존재) — exit 0
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot),
                "--raw-private-dir", str(raw),
                "--data-card", str(tmp_path / "missing.md"),
                "--pilot-report", str(tmp_path / "missing.md"),
                "--gitignore", str(tmp_path / "no_gi")])
    assert rc.returncode == 0  # AUTO PASS면 exit 0
    assert "HEURISTIC" in rc.stdout
    # heuristic fail이 보고에 표시되지만 exit는 0


def test_validate_outputs_feature_coverage_aggregate(tmp_path):
    """Cycle 12 — per-feature quote coverage 집계.

    annotation 2개에서 어떤 feature가 quote를 받았는지 추적.
    """
    raw = _make_raw_synopsis_dir(tmp_path, count=2)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # ep001: feature A에만 quote / ep002: feature A와 B 모두 quote
    ann1 = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 3, "cliffhanger_strength": 2},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},
    )
    ann2 = _make_annotation_output(
        "km_titleA_ep002", "modelA",
        scores={"conflict_intensity_peak": 4, "cliffhanger_strength": 3},
        quotes={
            "conflict_intensity_peak": ["권위자의 시선"],
            "cliffhanger_strength": ["권위자의 시선"],
        },
    )
    (outputs / "ann1.json").write_text(json.dumps(ann1, ensure_ascii=False), encoding="utf-8")
    (outputs / "ann2.json").write_text(json.dumps(ann2, ensure_ascii=False), encoding="utf-8")

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report),
                "--expected-features",
                "conflict_intensity_peak", "cliffhanger_strength"])
    assert rc.returncode == 0, rc.stderr
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    # 새 stat 필드들
    assert summary["n_annotations"] == 2
    pf_count = summary["per_feature_quote_count"]
    assert pf_count["conflict_intensity_peak"] == 2  # 두 annotation 모두 quote
    assert pf_count["cliffhanger_strength"] == 1     # ann2만
    pf_cov = summary["per_feature_annotation_coverage"]
    assert pf_cov["conflict_intensity_peak"] == 2    # 2/2 annotation에 quote 있음
    assert pf_cov["cliffhanger_strength"] == 1       # 1/2
    cov_ratio = summary["expected_features_coverage_ratio"]
    assert cov_ratio["conflict_intensity_peak"] == 1.0
    assert cov_ratio["cliffhanger_strength"] == 0.5
    assert summary["min_coverage_feature"] == "cliffhanger_strength"
    assert summary["min_coverage_ratio"] == 0.5
    # 0-coverage feature 없음
    assert summary["expected_features_with_zero_coverage"] == []


def test_validate_outputs_zero_coverage_warning(tmp_path):
    """quote가 없는 expected feature가 있으면 stderr WARN."""
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    ann = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 4, "cliffhanger_strength": 3},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},  # cliffhanger 없음
    )
    (outputs / "a.json").write_text(json.dumps(ann, ensure_ascii=False), encoding="utf-8")

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report),
                "--expected-features",
                "conflict_intensity_peak", "cliffhanger_strength"])
    assert rc.returncode == 0  # not strict
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    assert summary["expected_features_with_zero_coverage"] == ["cliffhanger_strength"]
    # stdout에 WARN 메시지
    assert "0 quotes" in rc.stdout or "WARN" in rc.stdout


def test_validate_outputs_strict_with_quote_coverage_min(tmp_path):
    """--strict + --quote-coverage-min로 coverage threshold 위반시 exit 1."""
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # cliffhanger feature에 quote 없음 → coverage = 0
    ann = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 4, "cliffhanger_strength": 3},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},
    )
    (outputs / "a.json").write_text(json.dumps(ann, ensure_ascii=False), encoding="utf-8")

    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--expected-features",
                "conflict_intensity_peak", "cliffhanger_strength",
                "--quote-coverage-min", "0.5",
                "--strict"])
    assert rc.returncode == 1


def test_validate_outputs_default_expected_features(tmp_path):
    """--expected-features 미지정 시 Phase 3.0 §11 7 features default 사용."""
    raw = _make_raw_synopsis_dir(tmp_path, count=1)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    ann = _make_annotation_output(
        "km_titleA_ep001", "modelA",
        scores={"conflict_intensity_peak": 4},
        quotes={"conflict_intensity_peak": ["권위자의 시선"]},
    )
    (outputs / "a.json").write_text(json.dumps(ann, ensure_ascii=False), encoding="utf-8")

    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0
    summary = json.loads(halluc_report.read_text(encoding="utf-8"))
    # 7 features default → 6개는 zero coverage
    assert len(summary["expected_features"]) == 7
    assert "conflict_intensity_peak" not in summary["expected_features_with_zero_coverage"]
    assert len(summary["expected_features_with_zero_coverage"]) == 6


# ---------------------------------------------------------------------------
# 6. build_feature_matrix.py
# ---------------------------------------------------------------------------

BUILD_MAT = ROOT / "scripts/annotation/build_feature_matrix.py"


def test_build_feature_matrix(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    for i in (1, 2):
        for ann_id in ("modelA", "modelB"):
            rid = f"km_titleA_ep{i:03d}"
            ann = _make_annotation_output(
                rid, ann_id,
                scores={"conflict_intensity_peak": i + 2, "cliffhanger_strength": i},
            )
            (outputs / f"{rid}_{ann_id}.json").write_text(
                json.dumps(ann, ensure_ascii=False), encoding="utf-8",
            )
    out = tmp_path / "feat.csv"
    rc = _run([str(BUILD_MAT), "--input", str(outputs), "--output", str(out)])
    assert rc.returncode == 0, rc.stderr
    with out.open(encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    # 2 records × 2 annotators × 2 features = 8 rows
    assert len(rows) == 8
    assert all(r["genre_id"] == "korean_morning_melodrama" for r in rows)


# ---------------------------------------------------------------------------
# 7. build_reliability_report.py
# ---------------------------------------------------------------------------

BUILD_REL = ROOT / "scripts/annotation/build_reliability_report.py"


def test_build_reliability_perfect_agreement(tmp_path):
    """완벽 일치 (modelA == modelB) → r=1.0 → KEEP."""
    feat = tmp_path / "feat.csv"
    rows = []
    for i in range(1, 5):
        for ann in ("modelA", "modelB"):
            rows.append({
                "record_id": f"km_t_ep{i:03d}",
                "genre_id": "km",
                "annotator_id": ann,
                "feature": "conflict_intensity_peak",
                "score": str(i),  # 같은 score → r=1.0
            })
    with feat.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["record_id", "genre_id", "annotator_id", "feature", "score"])
        writer.writeheader()
        writer.writerows(rows)
    out = tmp_path / "rel.json"
    rc = _run([str(BUILD_REL), "--features", str(feat), "--output", str(out)])
    assert rc.returncode == 0, rc.stderr
    rel = json.loads(out.read_text(encoding="utf-8"))
    assert rel["schema_version"] == "phase3_reliability_report_v1"
    feat_info = rel["feature_reliability"]["conflict_intensity_peak"]
    assert feat_info["mean_r"] == 1.0
    assert feat_info["decision"] == "KEEP"


def test_build_reliability_disagreement_drops(tmp_path):
    """완벽 불일치 (modelA reverse modelB) → r=-1 → DROP."""
    feat = tmp_path / "feat.csv"
    rows = []
    for i in range(1, 5):
        rows.append({
            "record_id": f"km_t_ep{i:03d}",
            "genre_id": "km",
            "annotator_id": "modelA",
            "feature": "f1",
            "score": str(i),
        })
        rows.append({
            "record_id": f"km_t_ep{i:03d}",
            "genre_id": "km",
            "annotator_id": "modelB",
            "feature": "f1",
            "score": str(5 - i),  # reverse
        })
    with feat.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["record_id", "genre_id", "annotator_id", "feature", "score"])
        writer.writeheader()
        writer.writerows(rows)
    out = tmp_path / "rel.json"
    rc = _run([str(BUILD_REL), "--features", str(feat), "--output", str(out)])
    assert rc.returncode == 0
    rel = json.loads(out.read_text(encoding="utf-8"))
    info = rel["feature_reliability"]["f1"]
    assert info["mean_r"] < 0
    assert info["decision"] == "DROP"


def test_build_reliability_threshold_4_keep(tmp_path):
    """4개 이상 KEEP feature → phase3_threshold_pass=True (Phase 3.1 진입 조건)."""
    feat = tmp_path / "feat.csv"
    rows = []
    for fname in ("f1", "f2", "f3", "f4"):  # 4 features all perfect
        for i in range(1, 5):
            rows.append({
                "record_id": f"km_t_ep{i:03d}", "genre_id": "km",
                "annotator_id": "modelA", "feature": fname, "score": str(i),
            })
            rows.append({
                "record_id": f"km_t_ep{i:03d}", "genre_id": "km",
                "annotator_id": "modelB", "feature": fname, "score": str(i),
            })
    with feat.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["record_id", "genre_id", "annotator_id", "feature", "score"])
        writer.writeheader()
        writer.writerows(rows)
    out = tmp_path / "rel.json"
    _run([str(BUILD_REL), "--features", str(feat), "--output", str(out)])
    rel = json.loads(out.read_text(encoding="utf-8"))
    assert len(rel["summary"]["keep"]) == 4
    assert rel["summary"]["phase3_threshold_pass"] is True


# ---------------------------------------------------------------------------
# End-to-end: Mode A pipeline (normalize → validate → build_inputs)
# ---------------------------------------------------------------------------

def test_mode_a_e2e_pipeline(tmp_path):
    """Mode A 전체 파이프라인 — fetch 0, LLM 0, fixture만."""
    raw = _make_raw_synopsis_dir(tmp_path, count=5)
    norm = tmp_path / "norm.jsonl"
    inputs_dir = tmp_path / "annotation_inputs"
    public_safe = tmp_path / "public_safe.jsonl"

    # 1. normalize
    rc = _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    assert rc.returncode == 0
    # 2. validate
    rc = _run([str(VAL_DS), "--input", str(norm)])
    assert rc.returncode == 0
    # 3. build inputs
    rc = _run([str(BUILD_INPUTS), "--input", str(norm), "--output", str(inputs_dir)])
    assert rc.returncode == 0
    # 4. public-safe dataset
    rc = _run([str(BUILD_PS), "--input", str(norm), "--output", str(public_safe)])
    assert rc.returncode == 0

    # 5. annotation_inputs 안에 synopsis_text 있어야 (Mode A 가정)
    sample = json.loads(next(inputs_dir.glob("*.json")).read_text(encoding="utf-8"))
    assert "synopsis_text" in sample
    # 6. public_safe에는 synopsis_text 없어야
    ps_first = json.loads(public_safe.read_text(encoding="utf-8").splitlines()[0])
    assert "synopsis_text" not in ps_first


# ---------------------------------------------------------------------------
# 8. Public-safe fixture demo (cycle 2) — 사용자가 따라할 수 있는 e2e
# ---------------------------------------------------------------------------

PUBLIC_SAFE_FIXTURE = ROOT / "tests/fixtures/annotation_public_safe"


def test_public_safe_fixture_files_exist():
    """fixture 디렉토리 + 10 synopsis (2 titles × 5 ep) + 20 annotation outputs (× 2 models)."""
    assert (PUBLIC_SAFE_FIXTURE / "README.md").exists()
    raw = PUBLIC_SAFE_FIXTURE / "synopsis_raw_demo"
    assert raw.exists()
    raw_files = sorted(raw.glob("*.json"))
    assert len(raw_files) == 10, (
        f"expected 10 raw fixtures (2 titles × 5 episodes per plan §5), got {len(raw_files)}"
    )
    titles = sorted({f.name.split("_")[0] for f in raw_files})
    assert titles == ["titleA", "titleB"], f"unexpected titles: {titles}"
    outputs = PUBLIC_SAFE_FIXTURE / "annotation_outputs_demo"
    assert outputs.exists()
    output_files = sorted(outputs.glob("*.json"))
    assert len(output_files) == 20, (
        f"expected 20 annotation outputs (10 episodes × 2 models), got {len(output_files)}"
    )


def test_public_safe_fixture_e2e(tmp_path):
    """fixture e2e — fetch 0, LLM 0. Phase 3.1 GO 판정까지 도달.

    이 test는 Mode A 파이프라인이 *실제 사용자 시나리오*에서 작동함을 증명.
    """
    raw = PUBLIC_SAFE_FIXTURE / "synopsis_raw_demo"
    outputs = PUBLIC_SAFE_FIXTURE / "annotation_outputs_demo"
    if not (raw.exists() and outputs.exists()):
        pytest.skip("public-safe fixtures missing")

    norm = tmp_path / "norm.jsonl"
    halluc_report = tmp_path / "halluc.json"
    feat_csv = tmp_path / "feat.csv"
    rel_json = tmp_path / "reliability.json"

    # 1. normalize (2 titles × 5 ep = 10 records)
    rc = _run([str(NORM), "--input", str(raw), "--output", str(norm)])
    assert rc.returncode == 0, rc.stderr
    # 2. validate dataset
    rc = _run([str(VAL_DS), "--input", str(norm), "--strict-min-records", "10"])
    assert rc.returncode == 0
    # 3. validate annotation outputs (hallucination check)
    rc = _run([str(VAL_OUT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report)])
    assert rc.returncode == 0, rc.stderr
    halluc = json.loads(halluc_report.read_text(encoding="utf-8"))
    # fixture quotes는 모두 substring 매칭으로 작성됨 → hallucination 0
    assert halluc["hallucination_rate"] < 0.05, (
        f"fixture hallucination rate {halluc['hallucination_rate']} ≥ 5%; "
        "fixture quotes have drifted from synopsis substrings"
    )
    assert halluc["phase3_threshold_pass"] is True
    # 4. feature matrix
    rc = _run([str(BUILD_MAT), "--input", str(outputs), "--output", str(feat_csv)])
    assert rc.returncode == 0
    # 5. reliability — 2 models, 10 episodes (2 titles × 5), 7 features
    rc = _run([str(BUILD_REL), "--features", str(feat_csv), "--output", str(rel_json)])
    assert rc.returncode == 0
    rel = json.loads(rel_json.read_text(encoding="utf-8"))
    # fixture는 두 모델이 거의 일치 (의도적) → 대부분 KEEP
    assert rel["n_records"] == 10
    assert rel["n_annotators"] == 2
    keep_count = len(rel["summary"]["keep"])
    assert keep_count >= 4, (
        f"fixture should produce ≥4 KEEP features (got {keep_count}); "
        f"summary={rel['summary']}"
    )
    # Phase 3.1 GO threshold
    assert rel["summary"]["phase3_threshold_pass"] is True


def test_public_safe_fixture_no_synopsis_in_outputs():
    """fixture annotation outputs에 synopsis_text 노출 0건 보장.

    저작권 안전성 — annotation_outputs는 quote만, full synopsis 없음.
    """
    outputs = PUBLIC_SAFE_FIXTURE / "annotation_outputs_demo"
    if not outputs.exists():
        pytest.skip()
    for path in outputs.glob("*.json"):
        d = json.loads(path.read_text(encoding="utf-8"))
        assert "synopsis_text" not in d, (
            f"{path.name}: synopsis_text leaked into annotation output"
        )
