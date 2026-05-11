"""Tests for Phase 6 prep — universal seed renderer + skeleton_output 통합.

Per `docs/witness_narrative_mode_plan.md` §3.5 + Phase 6:
    포트폴리오 표면이 universal seed + AnchorRegistry를 결합해 anchor 버전을
    렌더링한다.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# 1. universal_seed_renderer (engine/anchor)
# ============================================================================

def test_renderer_uses_binding_for_main_display():
    from engine.anchor import AnchorRegistry, render_universal_seed_to_korean
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01",
        conflict_axis_id="loyalty_vs_survival",
        main_role="main_loyal_under_pressure",
        main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
        dominant_desires=("loyalty",),
    )
    reg = AnchorRegistry()
    binding = reg.get("peter_scarcity_baseline")
    assert binding is not None
    out = render_universal_seed_to_korean(seed, binding)
    assert "베드로" in out
    # universal id가 외부 surface에 leak되지 않음
    assert "loyal_under_pressure" not in out


def test_renderer_falls_back_without_binding():
    from engine.anchor import render_universal_seed_to_korean
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01",
        conflict_axis_id="loyalty_vs_survival",
        main_role="some_role",
        main_archetype="some_archetype",
        dominant_pressures=("fear",),
        dominant_desires=("loyalty",),
    )
    out = render_universal_seed_to_korean(seed, None)
    # binding 없으면 archetype label이 표시 (한국어 매핑 없음)
    assert "some_archetype" in out or "some_role" in out


def test_renderer_to_dict_has_required_keys():
    from engine.anchor import AnchorRegistry, render_universal_seed_to_dict
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01",
        conflict_axis_id="loyalty_vs_survival",
        main_role="main_loyal_under_pressure",
        main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
        dominant_desires=("loyalty",),
    )
    reg = AnchorRegistry()
    binding = reg.get("peter_scarcity_baseline")
    d = render_universal_seed_to_dict(seed, binding)
    for k in ("seed_id", "main_display", "conflict_axis_id",
              "conflict_axis_label_ko", "conflict_axis_question_ko",
              "pressures_ko", "desires_ko"):
        assert k in d, f"missing key: {k}"
    assert d["main_display"] == "베드로"
    assert d["pressures_ko"] == ["두려움"]
    assert d["desires_ko"] == ["곁에 남으려는 마음"]


def test_renderer_translates_conflict_axis_to_korean():
    from engine.anchor import render_universal_seed_to_dict
    from engine.observer.universal_story_seed import UniversalStorySeed
    for axis_id, expected_ko in (
        ("loyalty_vs_survival", "곁에 남기 vs 살아남기"),
        ("uncertainty_vs_commitment", "결정 미루기 vs 결정하기"),
        ("control_vs_exposure", "통제하기 vs 노출되기"),
    ):
        seed = UniversalStorySeed(
            seed_id="X", conflict_axis_id=axis_id, main_role="m",
        )
        d = render_universal_seed_to_dict(seed, None)
        assert d["conflict_axis_label_ko"] == expected_ko


# ============================================================================
# 2. skeleton_output.json from orchestrator
# ============================================================================

DEMO_DIR = ROOT / "docs" / "portfolio" / "demo"


def test_skeleton_output_json_is_emitted_by_orchestrator():
    p = DEMO_DIR / "skeleton_output.json"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["schema_version"] == "skeleton_output_v1"
    assert isinstance(d["seeds"], list)
    assert d["evidence_ledger"]["total_signals"] > 0
    assert d["anchor_metadata"]["anchor_id"] == "peter_scarcity_baseline"


def test_skeleton_output_json_seeds_are_anchor_clean():
    """skeleton_output.json 의 seeds 자체는 한국어/영어 인물명 0.

    한국어 substring match는 false positive (예: "요한" ⊂ "필요한")가 가능하므로
    한글 word boundary regex로 검사한다. 영어 이름은 직접 substring으로
    충분 (PascalCase + 일반 텍스트에서 매칭되면 거의 확실히 인물명).
    """
    import re
    p = DEMO_DIR / "skeleton_output.json"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    d = json.loads(p.read_text(encoding="utf-8"))
    seeds_text = json.dumps(d["seeds"], ensure_ascii=False)

    # 영어 이름 — substring으로 충분
    for tok in ("Peter", "Andrew", "James", "John", "Vangogh", "Talleyrand"):
        assert tok not in seeds_text, (
            f"skeleton_output seeds leaked English anchor name: {tok!r}"
        )

    # 한국어 이름 — 한글이 앞뒤로 *없는* 위치에서만 매칭 (word-boundary)
    for tok in ("베드로", "안드레", "야고보", "요한", "유다", "가야바"):
        pattern = r"(?<![가-힣])" + re.escape(tok) + r"(?![가-힣])"
        m = re.search(pattern, seeds_text)
        assert m is None, (
            f"skeleton_output seeds leaked Korean anchor name: {tok!r} "
            f"at: ...{seeds_text[max(0, m.start()-20):m.end()+20]}..."
        )


def test_skeleton_output_seeds_have_valid_conflict_axis():
    p = DEMO_DIR / "skeleton_output.json"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    d = json.loads(p.read_text(encoding="utf-8"))
    valid_axes = {
        "loyalty_vs_survival", "uncertainty_vs_commitment",
        "control_vs_exposure", "collective_fear_vs_scapegoating",
        "identity_vs_failure", "atmosphere_vs_action",
        "trust_vs_self_protection", "unknown",
    }
    for s in d["seeds"]:
        assert s["conflict_axis_id"] in valid_axes


# ============================================================================
# 3. End-to-end: pipeline → skeleton output → render with binding
# ============================================================================

def test_e2e_skeleton_output_roundtrips_through_renderer():
    """skeleton_output.json 의 universal seed가 다시 한국어 surface로
    렌더링 가능 (Phase 6 통합 데모의 핵심 흐름)."""
    p = DEMO_DIR / "skeleton_output.json"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    d = json.loads(p.read_text(encoding="utf-8"))

    from engine.anchor import (
        AnchorRegistry, render_universal_seed_to_korean,
    )
    from engine.observer.universal_story_seed import UniversalStorySeed

    reg = AnchorRegistry()
    binding = reg.get("peter_scarcity_baseline")

    for seed_dict in d["seeds"]:
        seed = UniversalStorySeed.from_dict(seed_dict)
        rendered = render_universal_seed_to_korean(seed, binding)
        # 렌더링된 surface는 한국어 + 베드로 (또는 fallback main display)
        # 적어도 한 conflict axis label이 한국어로 들어가 있어야
        assert any(label in rendered for label in (
            "곁에 남기", "결정 미루기", "통제하기", "이름 지키기",
            "분위기 vs 행동", "신뢰 지키기", "두려움", "표적",
            "정리되지 않은 긴장",
        )), f"rendered surface lacks Korean conflict label: {rendered}"


# ============================================================================
# 4. Phase 6 demo HTML — main index.html에 skeleton section 통합
# ============================================================================

def test_index_html_contains_skeleton_section():
    """main index.html에 'skeletonSeeds' div가 있어야 (Phase 6 partial demo)."""
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    html = p.read_text(encoding="utf-8")
    assert 'id="skeletonSeeds"' in html
    assert "뼈대 엔진 출력" in html or "universal seeds" in html


def test_index_html_payload_contains_skeleton_output():
    """payload script tag에 skeleton_output 포함."""
    import re as _re
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    html = p.read_text(encoding="utf-8")
    m = _re.search(
        r'<script type="application/json" id="data-payload">(.*?)</script>',
        html, _re.DOTALL,
    )
    assert m
    data = json.loads(m.group(1))
    assert "skeleton_output" in data
    assert data["skeleton_output"]["schema_version"] == "skeleton_output_v1"
    assert isinstance(data["skeleton_output"]["seeds"], list)


def test_index_html_links_to_witness_narrative_mode_plan():
    """index.html footer가 새 plan 링크 포함."""
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run portfolio orchestrator first")
    html = p.read_text(encoding="utf-8")
    assert "witness_narrative_mode_plan.md" in html
    assert "skeleton_output.json" in html


# ============================================================================
# 5. CLAUDE.md / DESIGN.md skeleton-flesh framing
# ============================================================================

def test_claude_md_mentions_skeleton_flesh_dual_structure():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "뼈대" in text and "살" in text
    assert "SkeletonOutput" in text
    assert "FROZEN" in text


def test_design_md_has_v2_skeleton_flesh_section():
    text = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    assert "Narrative Mode Refactor" in text or "v2" in text
    assert "Skeleton" in text and "Flesh" in text
    assert "witness_narrative_mode_plan.md" in text


# Note (cycle 37): `test_claude_md_references_match_reality` moved to
# `tests/test_skeleton/test_phase3_1_baseline.py::_DOC_REALITY_REGISTRY`
# (registry-driven generic detector — L85 pattern). One test covers all docs.
