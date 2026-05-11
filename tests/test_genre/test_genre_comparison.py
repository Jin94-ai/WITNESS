"""Tests for run_genre_comparison.py CLI (Phase 2.75 cycle 4)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/narrative/run_genre_comparison.py"
DEPLOYED = ROOT / "docs/portfolio/demo/skeleton_output.json"


def test_help_runs():
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_comparison_generates_artifacts(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    for fname in ("index.html", "comparison.json", "comparison.md"):
        assert (out_dir / fname).exists(), f"missing {fname}"


def test_comparison_html_self_contained(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    forbidden = ('<script src="http', '<link rel="stylesheet" href="http',
                 'cdn.jsdelivr', 'googleapis.com', 'cdnjs.cloudflare')
    for tok in forbidden:
        assert tok not in html, f"HTML uses external resource: {tok}"
    # 양쪽 장르 모두 등장
    assert "korean_morning_melodrama" in html
    assert "japanese_quiet_drama" in html
    assert "한국 아침 막장 드라마" in html or "버티는" in html
    assert "정적" in html or "조용" in html


def test_comparison_json_schema(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    d = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
    assert d["schema_version"].startswith("genre_comparison_")
    # Phase 2.8: comparison_summary
    assert "comparison_summary" in d
    assert "shared_conflict_axes" in d["comparison_summary"]
    assert "audit_overall" in d["comparison_summary"]
    assert len(d["genres"]) == 2
    for g in d["genres"]:
        assert g["audit"]["overall"] == "pass"
        assert "adapted" in g
        assert g["adapted"]["schema_version"].startswith("genre_adapted_output_v1")


def test_comparison_requires_at_least_two_genres(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama",
         "--output", str(tmp_path / "cmp")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2
    assert "at least 2" in rc.stderr


def test_comparison_exit_2_on_unknown_genre(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "nonexistent_xyz",
         "--output", str(tmp_path / "cmp")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2


def test_comparison_md_lists_both_genres(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    md = (out_dir / "comparison.md").read_text(encoding="utf-8")
    assert "korean_morning_melodrama" in md
    assert "japanese_quiet_drama" in md
    # 입력 skeleton의 seed_ids도 등장
    raw = json.loads(DEPLOYED.read_text(encoding="utf-8"))
    for s in raw["seeds"]:
        assert s["seed_id"] in md


def test_comparison_html_no_dialogue_markers(tmp_path):
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    md = (out_dir / "comparison.md").read_text(encoding="utf-8")
    for marker in ("라고 말했다", "라고 외쳤다"):
        assert marker not in md, f"comparison MD contains dialogue marker: {marker!r}"
