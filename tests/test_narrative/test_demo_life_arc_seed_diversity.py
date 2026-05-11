"""Tests for demo_life_arc_seed_diversity script.

Verifies that running 3 seeds through life_arc_narrative produces:
    - markdown comparison table
    - script exits 0 (means at least one event differs across seeds)
    - output cites scripture refs + Korean action descriptions
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/narrative/demo_life_arc_seed_diversity.py"


def test_script_exists():
    assert SCRIPT.exists()


def test_script_runs_three_seeds_and_writes_markdown(tmp_path):
    out = tmp_path / "diversity.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,7,11",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"{rc.stderr}\n{rc.stdout}"
    assert out.exists()


def test_script_output_has_comparison_table(tmp_path):
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
    # Required sections
    assert "# Life Arc Seed Diversity" in md
    assert "Engine-driven" in md
    # Table header
    assert "seed 0" in md
    assert "seed 7" in md
    # 차이 카운트 표시
    assert "다른 선택" in md
    # ⚡ marker for differing events (at least one)
    assert "⚡" in md


def test_script_output_includes_scripture_refs(tmp_path):
    out = tmp_path / "div.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,11",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    md = out.read_text(encoding="utf-8")
    # 일부 잘 알려진 scripture refs
    refs_found = sum(
        ref in md for ref in ("눅 5", "마 16", "마 26", "요 13", "요 21")
    )
    assert refs_found >= 3


def test_script_includes_korean_action_descriptions(tmp_path):
    out = tmp_path / "div.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,7",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    md = out.read_text(encoding="utf-8")
    # 한국어 action_options.description의 예시들
    found_korean_actions = sum(
        s in md for s in (
            "그물", "고백", "부인", "달려감", "잠듦", "발씻음",
            "조용히", "허탕", "맹세",
        )
    )
    assert found_korean_actions >= 3


def test_script_no_passion_uses_4_phase(tmp_path):
    out = tmp_path / "div.md"
    rc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--seeds", "0,7",
         "--no-passion",
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # 4-phase는 fewer events라서 differing이 0일 수도 있음.
    # rc==1이라도 markdown은 작성되었어야 함.
    assert out.exists()
