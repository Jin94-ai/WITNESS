"""Tests for Narrative Opportunity export (Phase 4)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.observer.moment_extractor import extract_moments  # noqa: E402
from engine.observer.narrative_opportunity import (  # noqa: E402
    from_thread,
)
from engine.observer.thread import StoryThread  # noqa: E402
from engine.observer.thread_builder import (  # noqa: E402
    build_story_threads,
    link_moments,
)


def _load_export_script():
    spec = importlib.util.spec_from_file_location(
        "export_narrative_opportunities",
        ROOT / "scripts" / "narrative" / "export_narrative_opportunities.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["export_narrative_opportunities"] = mod
    spec.loader.exec_module(mod)
    return mod


export = _load_export_script()
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _build_real(tmp_path):
    """Run the full pipeline and write all artifacts to tmp_path."""
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)

    moments_path = tmp_path / "moments.json"
    threads_path = tmp_path / "threads.json"

    moments_path.write_text(json.dumps({
        "run_label": "peter_scarcity_baseline",
        "schema_version": "moments_v1",
        "moments": [m.to_dict() for m in moments],
    }), encoding="utf-8")

    threads_path.write_text(json.dumps({
        "run_label": "peter_scarcity_baseline",
        "schema_version": "story_threads_v1",
        "threads": [t.to_dict() for t in threads],
    }), encoding="utf-8")

    out_md = tmp_path / "ops.md"
    out_json = tmp_path / "ops.json"
    export.main(
        str(threads_path), str(moments_path),
        str(out_md), str(out_json),
    )
    return out_md, out_json


# ============ Opportunity model ============

def test_rank_classification():
    from engine.observer.narrative_opportunity import _rank_for_score
    assert _rank_for_score(0.85) == "strong"
    assert _rank_for_score(0.65) == "usable"
    assert _rank_for_score(0.45) == "weak"
    assert _rank_for_score(0.20) == "hold"


def test_from_thread_preserves_fields():
    t = StoryThread(
        thread_id="T01", title="Test",
        main_agents=("a01",), groups=(),
        core_conflict="loyalty_vs_survival",
        arc_direction="fear_to_withdrawal",
        moment_ids=("M1", "M2", "M3"),
        start_tick=10, end_tick=80,
        story_potential_score=0.85,
        usable_as=("film_scene",),
    )
    opp = from_thread(t)
    assert opp.thread_id == "T01"
    assert opp.score == 0.85
    assert opp.rank == "strong"
    assert opp.creative_uses == ("film_scene",)
    assert opp.moment_count == 3


# ============ Markdown output ============

def test_markdown_renders_with_thread_cards(tmp_path):
    out_md, out_json = _build_real(tmp_path)
    md = out_md.read_text(encoding="utf-8")
    assert "# WITNESS Narrative Opportunities" in md
    assert "peter_scarcity_baseline" in md
    # Each thread should be referenced
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    for opp in payload["opportunities"]:
        assert opp["thread_id"] in md


def test_markdown_includes_logline_and_evidence(tmp_path):
    out_md, _ = _build_real(tmp_path)
    md = out_md.read_text(encoding="utf-8")
    assert "### Logline" in md
    assert "### Evidence" in md
    assert "### Unresolved Question" in md


def test_markdown_lists_creative_uses_when_present(tmp_path):
    out_md, out_json = _build_real(tmp_path)
    md = out_md.read_text(encoding="utf-8")
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    if any(o["creative_uses"] for o in payload["opportunities"]):
        assert "creative uses" in md


# ============ JSON output ============

def test_json_schema_version(tmp_path):
    _, out_json = _build_real(tmp_path)
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "narrative_opportunities_v1"


def test_json_summary_counts_consistent(tmp_path):
    _, out_json = _build_real(tmp_path)
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    s = payload["summary"]
    actual_strong = sum(1 for o in payload["opportunities"] if o["rank"] == "strong")
    actual_usable = sum(1 for o in payload["opportunities"] if o["rank"] == "usable")
    actual_weak = sum(1 for o in payload["opportunities"] if o["rank"] == "weak")
    actual_hold = sum(1 for o in payload["opportunities"] if o["rank"] == "hold")
    assert s["strong_opportunities"] == actual_strong
    assert s["usable_threads"] == actual_usable
    assert s["weak_threads"] == actual_weak
    assert s["hold_threads"] == actual_hold
    assert s["threads_total"] == len(payload["opportunities"])


def test_json_opportunities_sorted_by_score_desc(tmp_path):
    _, out_json = _build_real(tmp_path)
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    scores = [o["score"] for o in payload["opportunities"]]
    assert scores == sorted(scores, reverse=True)


def test_json_each_opportunity_has_required_fields(tmp_path):
    _, out_json = _build_real(tmp_path)
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    required = {
        "thread_id", "title", "logline", "core_conflict", "arc_direction",
        "unresolved_question", "creative_uses", "score", "rank",
        "main_agents", "groups", "start_tick", "end_tick", "moment_count",
    }
    for opp in payload["opportunities"]:
        missing = required - set(opp.keys())
        assert not missing, f"opportunity missing fields {missing}: {opp}"


def test_export_no_hardcoded_hero():
    src = (ROOT / "scripts" / "narrative" / "export_narrative_opportunities.py").read_text(encoding="utf-8")
    src2 = (ROOT / "engine" / "observer" / "narrative_opportunity.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden hero '{forbidden}' in export script"
        assert forbidden not in src2, f"forbidden hero '{forbidden}' in opportunity model"


def test_pipeline_end_to_end_passes_plan_success_criteria(tmp_path):
    """Plan §17 success criteria pass-check."""
    _, out_json = _build_real(tmp_path)
    payload = json.loads(out_json.read_text(encoding="utf-8"))

    # Criterion 1: 여러 개의 Story Thread가 나오는가?
    assert payload["summary"]["threads_total"] >= 2

    # Criterion 6: 창작자가 영화/소설/게임/방송 중 어디에 쓸 수 있을지 판단 가능한가?
    if payload["summary"]["strong_opportunities"] >= 1 \
            or payload["summary"]["usable_threads"] >= 1:
        # at least one of those should have creative_uses
        with_uses = [o for o in payload["opportunities"]
                     if o["creative_uses"] and o["rank"] in ("strong", "usable")]
        assert len(with_uses) >= 1
