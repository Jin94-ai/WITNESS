"""Phase 2.8 polish tests — structured outline + quality warnings + comparison summary.

Per `docs/WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md` §6.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPARISON_SCRIPT = ROOT / "scripts/narrative/run_genre_comparison.py"
DEPLOYED_SKELETON = ROOT / "docs/portfolio/demo/skeleton_output.json"


# ---------------------------------------------------------------------------
# 1. Rulebook v2.8 fields
# ---------------------------------------------------------------------------

def test_korean_rulebook_has_genre_lens_and_outline_templates():
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    assert rb.genre_lens_ko, "genre_lens_ko required for Phase 2.8 polish"
    assert "침묵" in rb.genre_lens_ko or "오해" in rb.genre_lens_ko
    # outline_templates: 4 core flow_roles
    for role in ("main_arc", "witness_arc", "supporting_uncertainty",
                  "delayed_response_arc"):
        assert role in rb.outline_templates, f"missing outline_templates[{role}]"


def test_japanese_rulebook_has_distinct_genre_lens():
    from engine.observer.genre_rulebook import load_rulebook
    rb_kr = load_rulebook("korean_morning_melodrama")
    rb_jp = load_rulebook("japanese_quiet_drama")
    assert rb_kr.genre_lens_ko != rb_jp.genre_lens_ko, (
        "two genres must have distinct genre_lens_ko"
    )


def test_outline_step_mapping_covers_episode_rhythm():
    """모든 episode_rhythm step이 outline_step_mapping에 있어야."""
    from engine.observer.genre_rulebook import load_rulebook
    for gid in ("korean_morning_melodrama", "japanese_quiet_drama"):
        rb = load_rulebook(gid)
        for step in rb.episode_rhythm:
            assert step in rb.outline_step_mapping, (
                f"{gid}: rhythm step {step!r} missing in outline_step_mapping"
            )


# ---------------------------------------------------------------------------
# 2. Structured outline (Issue 1+6)
# ---------------------------------------------------------------------------

def test_structured_outline_has_no_awkward_josa():
    """Phase 2.8 Issue 1: '사람이(가)' 같은 placeholder 조사 표현 0건."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    for gid in ("korean_morning_melodrama", "japanese_quiet_drama"):
        rb = load_rulebook(gid)
        out = adapt_skeleton_to_genre(sk, rb)
        for step in out.adapted_flow.adapted_outline_steps:
            for pat in ("이(가)", "을(를)", "은(는)"):
                assert pat not in step.line_ko, (
                    f"{gid} outline step {step.step!r} contains {pat!r}: "
                    f"{step.line_ko}"
                )


def test_structured_outline_steps_present():
    """Phase 2.8 Issue 6: adapted_outline_steps가 source_seed_id 보존."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)
    steps = out.adapted_flow.adapted_outline_steps
    assert len(steps) == len(rb.episode_rhythm)
    for step in steps:
        assert step.source_seed_id, f"step {step.step}: empty source_seed_id"
        assert step.line_ko, f"step {step.step}: empty line_ko"
        # source_seed_id가 skeleton에 실제 있어야
        assert step.source_seed_id in {s.seed_id for s in sk.seeds}


def test_structured_outline_step_distinct_lines():
    """Issue 1: 같은 line이 2회 이상 반복되지 않아야 (서로 다른 step에서)."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)
    lines = [s.line_ko for s in out.adapted_flow.adapted_outline_steps]
    # 각 line이 unique
    assert len(lines) == len(set(lines)), (
        f"outline lines not all distinct: {lines}"
    )


def test_structured_outline_step_uses_phase_template():
    """Issue 6: outline_templates의 phase별 template이 실제 line으로 변환."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)
    steps = out.adapted_flow.adapted_outline_steps
    # main_arc + early phase: "버티는 사람은 아직 자리를 지키지만, ..." 패턴
    main_early = next(
        (s for s in steps if s.source_flow_role == "main_arc" and
         rb.outline_step_mapping.get(s.step) == "early"),
        None,
    )
    assert main_early is not None
    assert "버티는 사람" in main_early.line_ko
    assert "아직 자리를 지키지만" in main_early.line_ko


# ---------------------------------------------------------------------------
# 3. Quality warnings (Issue 5)
# ---------------------------------------------------------------------------

def test_audit_quality_warnings_field_present():
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_audit import audit_genre_output
    from engine.observer.genre_rulebook import load_audit_blocklist, load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)
    audit = audit_genre_output(out, bl)
    assert hasattr(audit, "quality_warnings")
    # Phase 2.8 후 deployed는 warnings 0
    assert len(audit.quality_warnings) == 0, audit.quality_warnings
    # to_dict에도 포함
    assert "quality_warnings" in audit.to_dict()


def test_quality_warning_catches_awkward_josa():
    """legacy '사람이(가)' 같은 표현이 강제 주입되면 quality_warning이 잡아야."""
    from dataclasses import replace
    from engine.observer.genre_adapter import (
        GenreAdaptedOutlineStep, adapt_skeleton_to_genre,
    )
    from engine.observer.genre_audit import audit_genre_output
    from engine.observer.genre_rulebook import load_audit_blocklist, load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)

    # 첫 step의 line_ko에 placeholder 강제 주입
    bad_steps = list(out.adapted_flow.adapted_outline_steps)
    bad_steps[0] = replace(
        bad_steps[0],
        line_ko="버티는 사람이(가) 침묵으로 다음 회차를 만든다",
    )
    bad_flow = replace(
        out.adapted_flow, adapted_outline_steps=tuple(bad_steps),
    )
    bad_out = replace(out, adapted_flow=bad_flow)
    audit = audit_genre_output(bad_out, bl)
    assert audit.overall == "pass"   # hard audit은 통과
    assert len(audit.quality_warnings) > 0
    assert any("이(가)" in w for w in audit.quality_warnings)


def test_quality_warning_catches_duplicate_outline_lines():
    from dataclasses import replace
    from engine.observer.genre_adapter import (
        GenreAdaptedOutlineStep, adapt_skeleton_to_genre,
    )
    from engine.observer.genre_audit import audit_genre_output
    from engine.observer.genre_rulebook import load_audit_blocklist, load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    sk = _make_clean_skeleton()
    rb = load_rulebook("korean_morning_melodrama")
    bl = load_audit_blocklist("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(sk, rb)

    # 모든 step을 같은 line으로 (artificial duplication)
    bad_steps = tuple(
        replace(s, line_ko="동일한 줄") for s in out.adapted_flow.adapted_outline_steps
    )
    bad_flow = replace(
        out.adapted_flow, adapted_outline_steps=bad_steps,
        adapted_outline_ko=("동일한 줄",) * len(bad_steps),
    )
    bad_out = replace(out, adapted_flow=bad_flow)
    audit = audit_genre_output(bad_out, bl)
    assert any("repeated" in w for w in audit.quality_warnings)


# ---------------------------------------------------------------------------
# 4. Comparison summary (Issue 4)
# ---------------------------------------------------------------------------

def test_comparison_json_has_comparison_summary(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    rc = subprocess.run(
        [sys.executable, str(COMPARISON_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    d = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
    assert d["schema_version"] == "genre_comparison_output_v1"
    cs = d["comparison_summary"]
    assert "shared_conflict_axes" in cs
    assert "differences_by_seed" in cs
    assert cs["audit_overall"] == "pass"
    assert cs["total_quality_warnings"] >= 0
    # differences_by_seed에 두 장르 premise 비교
    assert len(cs["differences_by_seed"]) >= 1
    first_diff = cs["differences_by_seed"][0]
    assert "by_genre" in first_diff
    assert "korean_morning_melodrama" in first_diff["by_genre"]
    assert "japanese_quiet_drama" in first_diff["by_genre"]
    # 두 장르 premise는 달라야
    assert (first_diff["by_genre"]["korean_morning_melodrama"]
            != first_diff["by_genre"]["japanese_quiet_drama"])


def test_comparison_html_has_genre_lens_section(tmp_path):
    """Phase 2.8 Issue 3: HTML에 genre lens 섹션."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(COMPARISON_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "장르 렌즈" in html or "lens-card" in html
    assert "왜 다르게 나오는가" in html
    # Phase 2.8 Issue 2: plain Korean labels in skeleton table
    assert "흐름 위치" in html  # plain header
    # 내부 ID는 small 태그 안에만 (일반 본문 위계에 단독 노출 안 됨)
    assert "<small" in html


def test_comparison_html_no_awkward_josa(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(COMPARISON_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    for pat in ("이(가)", "을(를)", "은(는)"):
        assert pat not in html, f"comparison HTML contains {pat!r}"


def test_comparison_premise_differs_between_genres(tmp_path):
    """같은 source_seed_id에 대한 두 장르의 adapted_premise가 달라야 한다."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    out_dir = tmp_path / "cmp"
    subprocess.run(
        [sys.executable, str(COMPARISON_SCRIPT),
         "--skeleton", str(DEPLOYED_SKELETON),
         "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    d = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
    by_seed = {
        diff["source_seed_id"]: diff["by_genre"]
        for diff in d["comparison_summary"]["differences_by_seed"]
    }
    for sid, premises in by_seed.items():
        assert len(set(premises.values())) == len(premises), (
            f"seed {sid}: premises identical across genres ({premises})"
        )
