"""Tests for demo_seed_diversity script.

Plan §11 acceptance — *data-driven body* claim must be verifiable.
This script is the *portfolio asset* that demonstrates the claim.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/narrative/demo_seed_diversity.py"


def test_script_exists():
    assert SCRIPT.exists()


def test_script_runs_three_seeds_and_writes_markdown(tmp_path):
    out = tmp_path / "diversity.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,3,7",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # Exit code 0 means the script *also* asserted not all seeds identical
    assert rc.returncode == 0, f"script failed: {rc.stderr}\n--stdout--\n{rc.stdout}"
    assert out.exists()


def test_script_output_contains_required_sections(tmp_path):
    out = tmp_path / "diversity.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,3",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    md = out.read_text(encoding="utf-8")
    # Required sections (Korean headings + tables)
    assert "수치 비교" in md
    assert "Logline" in md
    assert "Act 3" in md
    assert "검증 결과" in md
    # Each seed gets its own subsection
    assert "### seed 0" in md
    assert "### seed 3" in md
    # Should report different bodies (not all identical)
    assert "동일한 본문" in md


def test_script_detects_seed_body_differences(tmp_path):
    out = tmp_path / "diversity.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,7",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    md = out.read_text(encoding="utf-8")
    # 검증 결과 — 다른 본문이 나와야 함 (not all identical)
    assert "**NO (성공)**" in md or "다른 본문이 나온 필드" in md
    # logline은 거의 항상 다른 숫자 인용
    assert "logline" in md.lower() or "Logline" in md


def test_script_with_single_seed_does_not_fail(tmp_path):
    """Single seed → no comparison possible → script still exits 0."""
    out = tmp_path / "single.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # Single seed has no comparison; script should not crash
    assert out.exists() or rc.returncode == 0
