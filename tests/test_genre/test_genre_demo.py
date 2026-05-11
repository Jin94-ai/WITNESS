"""Tests for apply_genre_adapter.py + run_genre_demo.py CLIs (Phase 2.75 §9)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APPLY_SCRIPT = ROOT / "scripts/narrative/apply_genre_adapter.py"
DEMO_SCRIPT = ROOT / "scripts/narrative/run_genre_demo.py"
DEPLOYED_SKELETON = ROOT / "docs/portfolio/demo/skeleton_output.json"


# ---------------------------------------------------------------------------
# 1. apply_genre_adapter.py
# ---------------------------------------------------------------------------

def test_apply_help_runs():
    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_apply_on_deployed_skeleton(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton_output.json missing")
    out = tmp_path / "out.json"
    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT),
         "--input", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["schema_version"].startswith("genre_adapted_output_v1")
    assert d["genre_id"] == "korean_morning_melodrama"
    assert len(d["adapted_seeds"]) >= 1
    assert d["audit"]["overall"] == "pass"


def test_apply_strict_audit_passes_on_clean(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton_output.json missing")
    out = tmp_path / "out.json"
    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT),
         "--input", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out),
         "--strict-audit"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr


def test_apply_exit_2_on_missing_skeleton(tmp_path):
    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT),
         "--input", str(tmp_path / "missing.json"),
         "--genre", "korean_morning_melodrama",
         "--output", str(tmp_path / "out.json")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2


def test_apply_exit_2_on_unknown_genre(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton_output.json missing")
    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT),
         "--input", str(DEPLOYED_SKELETON),
         "--genre", "nonexistent_genre_xyz",
         "--output", str(tmp_path / "out.json")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2


def test_apply_exit_1_on_skeleton_with_unknown_axis(tmp_path):
    """input gate: unknown_axis_count > 0이면 exit 1."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton_output.json missing")
    raw = json.loads(DEPLOYED_SKELETON.read_text(encoding="utf-8"))
    raw["audit_trail"]["unknown_axis_count"] = 1
    bad = tmp_path / "bad_skeleton.json"
    bad.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

    rc = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT),
         "--input", str(bad),
         "--genre", "korean_morning_melodrama",
         "--output", str(tmp_path / "out.json")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1


# ---------------------------------------------------------------------------
# 2. run_genre_demo.py
# ---------------------------------------------------------------------------

def test_demo_help_runs():
    rc = subprocess.run(
        [sys.executable, str(DEMO_SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_demo_generates_all_artifacts(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton_output.json missing")
    out_dir = tmp_path / "demo_genre"
    rc = subprocess.run(
        [sys.executable, str(DEMO_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    for fname in ("genre_adapted_output.json", "genre_adapted_output.md",
                   "evidence_audit.md", "index.html"):
        assert (out_dir / fname).exists(), f"missing {fname}"


def test_demo_html_self_contained(tmp_path):
    """index.html이 self-contained (외부 CSS/JS / asset 없음)."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "demo_genre"
    subprocess.run(
        [sys.executable, str(DEMO_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    # external fetch markers must NOT exist
    forbidden = ('<script src="http', '<link rel="stylesheet" href="http',
                 'cdn.jsdelivr', 'googleapis.com', 'cdnjs.cloudflare')
    for tok in forbidden:
        assert tok not in html, f"HTML uses external resource: {tok}"
    # core markers present
    assert "WITNESS" in html
    assert "korean_morning_melodrama" in html
    assert "audit-pass" in html or "audit-fail" in html


def test_demo_html_has_no_dialogue_markers(tmp_path):
    """Plan §11.2: 출력 본문에 대사 / 따옴표 / '라고 말했다' 없음."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "demo_genre"
    subprocess.run(
        [sys.executable, str(DEMO_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    md = (out_dir / "genre_adapted_output.md").read_text(encoding="utf-8")
    # Body content (not headers about audit) — check no Korean curly quotes / 라고 말했다
    for marker in ("라고 말했다", "라고 외쳤다", "라고 소리쳤다"):
        assert marker not in md, f"genre demo body contains dialogue marker: {marker!r}"


def test_demo_md_preserves_source_seed_ids(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "demo_genre"
    subprocess.run(
        [sys.executable, str(DEMO_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genre", "korean_morning_melodrama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    md = (out_dir / "genre_adapted_output.md").read_text(encoding="utf-8")
    # 원본 seed ids 모두 등장해야
    raw = json.loads(DEPLOYED_SKELETON.read_text(encoding="utf-8"))
    for s in raw["seeds"]:
        assert s["seed_id"] in md
