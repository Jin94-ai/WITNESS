"""Tests for Portfolio Demo Pipeline (Stage 0-8)."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "docs" / "portfolio" / "demo"


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ============ Pressure Summary ============

ps_mod = _load("pressure_summary",
               "engine/observer/pressure_summary.py")


def test_pressure_summary_three_phases():
    obs = json.loads(
        (ROOT / "data/visual/dot_observer_data.json").read_text(encoding="utf-8")
    )
    summary = ps_mod.build_pressure_summary(obs)
    assert len(summary.pressure_phases) == 3
    assert summary.total_ticks > 0


def test_pressure_summary_phase_labels_in_korean():
    obs = json.loads(
        (ROOT / "data/visual/dot_observer_data.json").read_text(encoding="utf-8")
    )
    summary = ps_mod.build_pressure_summary(obs)
    plain_labels = [p.plain_label for p in summary.pressure_phases]
    assert plain_labels == ["초반", "중반", "후반"]


def test_pressure_summary_no_internal_terms_in_plain_summary():
    obs = json.loads(
        (ROOT / "data/visual/dot_observer_data.json").read_text(encoding="utf-8")
    )
    summary = ps_mod.build_pressure_summary(obs)
    forbidden_in_plain = (
        "tick", "source_derived", "source_inferred", "co-occurrence",
        "authority_vigilance", "public_suspicion", "blame_concentration",
        "deterministic", "MomentLink",
    )
    full_text = summary.plain_language_summary + " ".join(
        p.summary for p in summary.pressure_phases
    )
    for f in forbidden_in_plain:
        assert f not in full_text, (
            f"plan §9.1 위반: '{f}' 가 일반인용 텍스트에 노출됨"
        )


def test_pressure_summary_serializable():
    obs = json.loads(
        (ROOT / "data/visual/dot_observer_data.json").read_text(encoding="utf-8")
    )
    summary = ps_mod.build_pressure_summary(obs)
    json.dumps(summary.to_dict(), ensure_ascii=False)


def test_pressure_summary_empty_observer_handled():
    summary = ps_mod.build_pressure_summary({"ticks": []})
    assert summary.total_ticks == 0
    assert summary.pressure_phases == ()


# ============ Story Seed Card ============

ssc_mod = _load("story_seed_card",
                "engine/observer/story_seed_card.py")


def _full_pipeline_inputs():
    """Build a real candidate / brief / score for end-to-end seed-card test."""
    from engine.observer.identity_resolver import IdentityResolver
    from engine.observer.moment_extractor import extract_moments
    from engine.observer.scene_brief import build_scene_brief
    from engine.observer.story_candidate_builder import build_story_candidates
    from engine.observer.story_viability import score_candidate
    from engine.observer.thread_builder import build_story_threads, link_moments
    from engine.observer.treatment import build_treatment

    obs = json.loads(
        (ROOT / "data/visual/dot_observer_data.json").read_text(encoding="utf-8")
    )
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    candidates = build_story_candidates(threads, moments, identity)
    out = []
    for c in candidates:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        out.append((c, b, sc))
    return out


def test_seed_card_uses_korean_plain_title():
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    c, b, sc = triples[0]
    card = ssc_mod.build_seed_card(c, b, sc)
    assert card.title in {
        "침묵으로 변해가는 충성", "결정을 미루는 사람",
        "드러날수록 조여오는 통제", "두려움이 누군가를 가리킬 때",
        "무너진 자리에서 남는 이름", "아무도 움직이지 않는 방",
        "거리를 두기 시작하는 마음", "정리되지 않은 긴장",
    }


def test_seed_card_uses_main_character_name():
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    c, b, sc = triples[0]
    card = ssc_mod.build_seed_card(c, b, sc)
    if c.main_characters and not c.main_characters[0].startswith("agent_"):
        assert c.main_characters[0] in card.subtitle
        assert c.main_characters[0] in card.plain_premise


def test_seed_card_no_internal_terms():
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    forbidden = (
        "tick", "source_derived", "source_inferred", "co-occurrence",
        "authority_vigilance", "public_suspicion", "blame_concentration",
        "MomentLink", "StoryThread", "viable_with_gaps", "strong_viable",
        "loyalty_vs_survival", "uncertainty_vs_commitment",
    )
    for c, b, sc in triples:
        card = ssc_mod.build_seed_card(c, b, sc)
        text = " ".join([
            card.title, card.subtitle, card.plain_premise,
            card.why_interesting, card.scene_image,
            card.unresolved_question, card.risk_note,
            *card.usable_for, card.confidence_label,
        ])
        for f in forbidden:
            assert f not in text, (
                f"seed card {card.seed_id}: forbidden internal term '{f}'"
            )


def test_seed_card_no_dialogue_or_fabricated_action():
    """Plan §6 forbidden expressions."""
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    forbidden = ("배신했다", "울부짖었다", "도망쳤다", "체포했다", "고발했다",
                 "고백했다", "닭이 울었다",
                 "rooster crowed", "denied him",
                 "EXT.", "INT.", "FADE IN", "FADE OUT",
                 '"', "'")
    for c, b, sc in triples:
        card = ssc_mod.build_seed_card(c, b, sc)
        text = " ".join([
            card.plain_premise, card.why_interesting, card.scene_image,
            card.unresolved_question,
        ])
        for f in forbidden:
            assert f not in text, (
                f"seed card {card.seed_id}: plan §6 forbidden '{f}' in: {text!r}"
            )


def test_seed_card_evidence_summary_has_korean_signals():
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    c, b, sc = triples[0]
    card = ssc_mod.build_seed_card(c, b, sc)
    # 영어 pressure name이 그대로 노출되면 안 됨
    for sig in card.evidence_summary.strongest_signals:
        for forbidden in ("authority_vigilance", "public_suspicion",
                          "blame_concentration", "fear", "shame_self"):
            assert forbidden not in sig, (
                f"signal '{sig}' contains untranslated internal term"
            )


def test_seed_card_serializable():
    triples = _full_pipeline_inputs()
    if not triples:
        pytest.skip("no candidates")
    c, b, sc = triples[0]
    card = ssc_mod.build_seed_card(c, b, sc)
    json.dumps(card.to_dict(), ensure_ascii=False)


def test_seed_card_module_no_hardcoded_hero():
    """Templates는 일반 conflict label로 lookup. 특정 인물 이름이 코드에 없어야."""
    src = (ROOT / "engine/observer/story_seed_card.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "Judas", "Caiaphas"):
        assert forbidden not in src, f"hero '{forbidden}' in seed_card source"


# ============ End-to-end pipeline (run_portfolio_demo) ============

def test_run_portfolio_demo_produces_all_outputs():
    """Run the orchestrator and verify all 5 main outputs exist + parseable."""
    orchestrator = ROOT / "scripts/narrative/run_portfolio_demo.py"
    rc = subprocess.run(
        [sys.executable, str(orchestrator)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"orchestrator failed: {rc.stderr}"

    expected = [
        "index.html",
        "story_seed_cards.md",
        "story_seed_cards.json",
        "evidence_report.md",
        "pressure_summary.json",
        "demo_run_summary.json",
    ]
    for fname in expected:
        p = DEMO_DIR / fname
        assert p.exists(), f"{fname} missing after orchestrator run"
        assert p.stat().st_size > 100, f"{fname} suspiciously small"


def test_demo_html_is_self_contained():
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run orchestrator first")
    text = p.read_text(encoding="utf-8")
    forbidden_external = (
        '<script src=', '<link rel="stylesheet" href=',
        "fonts.googleapis", "cdn.jsdelivr", "unpkg.com",
    )
    for f in forbidden_external:
        assert f not in text, f"external asset detected: {f}"


def test_demo_html_links_to_life_arc_demo():
    """Reviewer가 메인 index.html에서 life_arc.html로 navigate할 수 있어야."""
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run orchestrator first")
    text = p.read_text(encoding="utf-8")
    # Footer cross-links to life_arc outputs
    assert 'href="life_arc_demo.html"' in text
    assert 'href="life_arc_demo_by_week.html"' in text
    assert 'href="life_arc_seed_diversity.md"' in text


def test_demo_html_embeds_data_payload():
    p = DEMO_DIR / "index.html"
    if not p.exists():
        pytest.skip("run orchestrator first")
    text = p.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="data-payload">(.*?)</script>',
        text, re.DOTALL,
    )
    assert m, "data-payload script tag missing"
    data = json.loads(m.group(1))
    assert "run_summary" in data
    assert "pressure_summary" in data
    assert "seed_cards" in data
    assert "evidence" in data
    assert len(data["seed_cards"]) >= 1


def test_demo_summary_audit_pass_count_matches():
    """demo_run_summary.json's audit_pass count must equal seeds - audit_fail."""
    p = DEMO_DIR / "demo_run_summary.json"
    if not p.exists():
        pytest.skip("run orchestrator first")
    summary = json.loads(p.read_text(encoding="utf-8"))
    # Internal consistency
    assert summary["audit_pass"] + summary["audit_fail"] <= summary["seeds"]


def test_seed_cards_md_uses_only_korean_friendly_terms():
    p = DEMO_DIR / "story_seed_cards.md"
    if not p.exists():
        pytest.skip("run orchestrator first")
    md = p.read_text(encoding="utf-8")
    forbidden = (
        "tick ", "source_derived", "source_inferred", "co-occurrence",
        "authority_vigilance", "public_suspicion", "MomentLink",
        "StoryThread", "viable_with_gaps", "loyalty_vs_survival",
        "uncertainty_vs_commitment",
    )
    for f in forbidden:
        assert f not in md, f"plan §9 위반: '{f}' in story_seed_cards.md"


def test_evidence_report_includes_audit_summary():
    p = DEMO_DIR / "evidence_report.md"
    if not p.exists():
        pytest.skip("run orchestrator first")
    md = p.read_text(encoding="utf-8")
    assert "감사" in md or "검증" in md
    assert "통과" in md or "실패" in md
