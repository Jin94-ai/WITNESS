"""Tests for Phase 2 CLI scripts: synthesize_annotations + sample_for_human_review.

Per `docs/witness_narrative_mode_plan.md` §6 Phase 2 산출물:
    - scripts/annotation/synthesize_annotations.py
    - scripts/annotation/sample_for_human_review.py

Both scripts must work *without network IO* — fixture inputs only.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SYN_SCRIPT = ROOT / "scripts/annotation/synthesize_annotations.py"
SAMPLE_SCRIPT = ROOT / "scripts/annotation/sample_for_human_review.py"

ANNOTATION_FEATURES = (
    "conflict_intensity_peak",
    "revelation_density",
    "coincidence_frequency",
    "relationship_polarization",
    "new_conflict_introduction_rate",
    "dangling_thread_generation",
    "cliffhanger_intensity",
)


def _make_annotation(annotator_id: str, feat_value: float) -> dict:
    return {
        "schema_version": "annotation_v1",
        "title_id": "test_drama",
        "episode_no": 5,
        "annotator_id": annotator_id,
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {f: feat_value for f in ANNOTATION_FEATURES},
        "evidence_quotes": [
            {"feature": "revelation_density",
             "quote_ko": f"q-from-{annotator_id}"}
        ],
        "confidence": 0.8,
    }


# ============================================================================
# 1. synthesize_annotations.py
# ============================================================================

def test_synthesize_cli_help():
    rc = subprocess.run(
        [sys.executable, str(SYN_SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_synthesize_inputs_mode_writes_correct_synthesis(tmp_path):
    a1 = tmp_path / "a1.json"
    a2 = tmp_path / "a2.json"
    a3 = tmp_path / "a3.json"
    a1.write_text(json.dumps(_make_annotation("claude", 0.4)), encoding="utf-8")
    a2.write_text(json.dumps(_make_annotation("gpt", 0.6)), encoding="utf-8")
    a3.write_text(json.dumps(_make_annotation("gemini", 0.5)), encoding="utf-8")

    out = tmp_path / "syn.json"
    rc = subprocess.run(
        [sys.executable, str(SYN_SCRIPT),
         "--inputs", str(a1), str(a2), str(a3),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["schema_version"] == "synthesized_annotation_v1"
    assert d["title_id"] == "test_drama"
    assert d["episode_no"] == 5
    # Mean of 0.4, 0.6, 0.5 = 0.5
    for f in ANNOTATION_FEATURES:
        assert abs(d["features"][f] - 0.5) < 1e-3
    assert set(d["contributing_annotators"]) == {"claude", "gpt", "gemini"}
    assert len(d["evidence_quotes"]) == 3
    assert all("source_annotator_id" in q for q in d["evidence_quotes"])


def test_synthesize_per_annotator_dir_mode(tmp_path):
    base = tmp_path / "_per_annotator"
    for ann_id, val in [("claude", 0.3), ("gpt", 0.7)]:
        p = base / ann_id / "test_drama" / "05.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(_make_annotation(ann_id, val)), encoding="utf-8")

    out = tmp_path / "syn.json"
    rc = subprocess.run(
        [sys.executable, str(SYN_SCRIPT),
         "--per-annotator-dir", str(base),
         "--title-id", "test_drama",
         "--episode", "5",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    # Mean of 0.3, 0.7 = 0.5
    for f in ANNOTATION_FEATURES:
        assert abs(d["features"][f] - 0.5) < 1e-3
    # Spread = 0.4 → confidence = 1 - 0.4 = 0.6
    assert 0.59 <= d["confidence"] <= 0.61


def test_synthesize_migrate_deprecated_v1_to_v1_1(tmp_path):
    """Phase 2.5 cycle 6: --migrate-deprecated 가 v1 어노테이션을 자동 변환."""
    # v1 names — conflict_amplification_rate / resolution_to_dangling_ratio
    v1_annotation = {
        "schema_version": "annotation_v1",
        "title_id": "test_drama",
        "episode_no": 5,
        "annotator_id": "claude-v1",
        "annotated_at_iso": "2026-04-15T00:00:00Z",
        "features": {
            "conflict_amplification_rate": 0.4,
            "revelation_density": 0.5,
            "coincidence_frequency": 0.3,
            "relationship_polarization": 0.6,
            "new_conflict_introduction_rate": 0.4,
            "resolution_to_dangling_ratio": 0.4,
            "cliffhanger_intensity": 0.7,
        },
        "evidence_quotes": [
            {"feature": "conflict_amplification_rate", "quote_ko": "갈등 폭발 장면"},
            {"feature": "resolution_to_dangling_ratio", "quote_ko": "미해결 떡밥"},
        ],
        "confidence": 0.7,
    }
    a1 = tmp_path / "a1.json"
    a2 = tmp_path / "a2.json"
    a1.write_text(json.dumps(v1_annotation), encoding="utf-8")
    # 두 번째도 같은 v1 형식
    v1_2 = dict(v1_annotation)
    v1_2["annotator_id"] = "gpt-v1"
    a2.write_text(json.dumps(v1_2), encoding="utf-8")

    # --migrate-deprecated 없이 → fail (missing feature)
    out = tmp_path / "syn.json"
    rc_no_migrate = subprocess.run(
        [sys.executable, str(SYN_SCRIPT),
         "--inputs", str(a1), str(a2),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_no_migrate.returncode != 0
    assert "missing feature" in rc_no_migrate.stderr or "invalid" in rc_no_migrate.stderr

    # --migrate-deprecated 와 함께 → 성공 + 새 이름으로 출력
    rc_migrate = subprocess.run(
        [sys.executable, str(SYN_SCRIPT),
         "--inputs", str(a1), str(a2),
         "--output", str(out),
         "--migrate-deprecated"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_migrate.returncode == 0, rc_migrate.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    # features는 새 이름으로 변환됨
    assert "conflict_intensity_peak" in d["features"]
    assert "dangling_thread_generation" in d["features"]
    assert "conflict_amplification_rate" not in d["features"]
    assert "resolution_to_dangling_ratio" not in d["features"]
    # evidence_quotes의 feature 필드도 변환
    quote_features = {q["feature"] for q in d["evidence_quotes"]}
    assert "conflict_intensity_peak" in quote_features
    assert "dangling_thread_generation" in quote_features
    assert "conflict_amplification_rate" not in quote_features


def test_migrate_deprecated_annotation_helper():
    from scripts.annotation.prompt_templates import migrate_deprecated_annotation

    v1 = {
        "title_id": "x", "episode_no": 1, "annotator_id": "claude",
        "features": {
            "conflict_amplification_rate": 0.4,
            "revelation_density": 0.5,
            "resolution_to_dangling_ratio": 0.6,
        },
        "evidence_quotes": [
            {"feature": "conflict_amplification_rate", "quote_ko": "..."},
            {"feature": "revelation_density", "quote_ko": "..."},
            {"feature": "resolution_to_dangling_ratio", "quote_ko": "..."},
        ],
    }
    new = migrate_deprecated_annotation(v1)
    assert "conflict_intensity_peak" in new["features"]
    assert "dangling_thread_generation" in new["features"]
    assert new["features"]["revelation_density"] == 0.5  # 미변환 보존
    quote_features = [q["feature"] for q in new["evidence_quotes"]]
    assert quote_features == [
        "conflict_intensity_peak",
        "revelation_density",
        "dangling_thread_generation",
    ]
    # 원본 dict는 수정되지 않음 (shallow copy 약속)
    assert "conflict_amplification_rate" in v1["features"]


def test_synthesize_rejects_invalid_input(tmp_path):
    bad = tmp_path / "bad.json"
    invalid_annotation = {
        "schema_version": "annotation_v1",
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "test",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {"conflict_intensity_peak": 1.5},  # missing other 6 + out of range
        "confidence": 0.5,
    }
    bad.write_text(json.dumps(invalid_annotation), encoding="utf-8")
    out = tmp_path / "syn.json"
    rc = subprocess.run(
        [sys.executable, str(SYN_SCRIPT),
         "--inputs", str(bad),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode != 0
    assert not out.exists()


# ============================================================================
# 2. sample_for_human_review.py
# ============================================================================

def _make_synthesized(title_id: str, episode_no: int, confidence: float) -> dict:
    return {
        "schema_version": "synthesized_annotation_v1",
        "title_id": title_id,
        "episode_no": episode_no,
        "features": {f: 0.5 for f in ANNOTATION_FEATURES},
        "confidence": confidence,
        "contributing_annotators": ["claude", "gpt"],
        "evidence_quotes": [],
    }


def test_sample_cli_help():
    rc = subprocess.run(
        [sys.executable, str(SAMPLE_SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_sample_low_confidence_picks_lowest(tmp_path):
    annotated_dir = tmp_path / "annotated"
    confidences = {(f"drama_{i}", 1): 0.1 + i * 0.1 for i in range(10)}
    for (title, ep), conf in confidences.items():
        p = annotated_dir / title / f"{ep:02d}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(_make_synthesized(title, ep, conf)),
            encoding="utf-8",
        )

    out = tmp_path / "sample.json"
    rc = subprocess.run(
        [sys.executable, str(SAMPLE_SCRIPT),
         "--annotated-dir", str(annotated_dir),
         "--output", str(out),
         "--pct", "30",
         "--strategy", "low_confidence"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["strategy"] == "low_confidence"
    # 10 records × 30% = 3 sampled
    assert d["sampled_count"] == 3
    # 가장 낮은 confidence 3개여야
    confs = [item["confidence"] for item in d["items"]]
    assert all(c <= 0.31 for c in confs), (
        f"low_confidence strategy should pick lowest 3 ({confs})"
    )


def test_sample_random_stratified_is_deterministic(tmp_path):
    annotated_dir = tmp_path / "annotated"
    for title in ("a", "b", "c"):
        for ep in range(1, 6):
            p = annotated_dir / title / f"{ep:02d}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                json.dumps(_make_synthesized(title, ep, 0.5)),
                encoding="utf-8",
            )
    out1 = tmp_path / "s1.json"
    out2 = tmp_path / "s2.json"
    for out in (out1, out2):
        rc = subprocess.run(
            [sys.executable, str(SAMPLE_SCRIPT),
             "--annotated-dir", str(annotated_dir),
             "--output", str(out),
             "--pct", "20",
             "--strategy", "random",
             "--seed", "42"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT),
        )
        assert rc.returncode == 0, rc.stderr

    d1 = json.loads(out1.read_text(encoding="utf-8"))
    d2 = json.loads(out2.read_text(encoding="utf-8"))
    # 같은 seed → 같은 결과
    items1 = [(i["title_id"], i["episode_no"]) for i in d1["items"]]
    items2 = [(i["title_id"], i["episode_no"]) for i in d2["items"]]
    assert items1 == items2


def test_sample_handles_empty_annotated_dir(tmp_path):
    """No annotations yet — script should still produce empty sample, exit 0."""
    out = tmp_path / "sample.json"
    rc = subprocess.run(
        [sys.executable, str(SAMPLE_SCRIPT),
         "--annotated-dir", str(tmp_path / "nonexistent"),
         "--output", str(out),
         "--pct", "5"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["total_records"] == 0
    assert d["sampled_count"] == 0


def test_sample_minimum_one(tmp_path):
    """If pct rounds to <1 but records exist, must sample at least 1."""
    annotated_dir = tmp_path / "annotated"
    p = annotated_dir / "drama_1" / "01.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(_make_synthesized("drama_1", 1, 0.5)),
        encoding="utf-8",
    )
    out = tmp_path / "sample.json"
    # 1 record × 1% = 0.01 → must round to 1
    rc = subprocess.run(
        [sys.executable, str(SAMPLE_SCRIPT),
         "--annotated-dir", str(annotated_dir),
         "--output", str(out),
         "--pct", "1"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["sampled_count"] == 1


# ============================================================================
# 3. PROJECT_STRUCTURE.md 갱신 검증
# ============================================================================

def test_project_structure_lists_v2_dirs():
    """PROJECT_STRUCTURE.md uses tree format — search for distinctive tokens
    rather than path-style strings."""
    text = (ROOT / "docs" / "PROJECT_STRUCTURE.md").read_text(encoding="utf-8")
    for required in (
        "Anchor-agnostic taxonomy",      # content/universal section comment
        "Anchor-specific bindings",      # content/anchors section comment
        "engine/anchor/",                # engine/anchor block heading
        "scripts/data/",
        "scripts/annotation/",
        "models/",
        "tests/test_skeleton/",
        "RFC_TEMPLATE",
        "ANNOTATION_GUIDE",
        "SELECTION_CRITERIA",
    ):
        assert required in text, f"PROJECT_STRUCTURE.md missing entry: {required}"
