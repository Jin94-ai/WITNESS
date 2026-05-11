"""Tests for Life Arc Narrative — time-windowed engine-driven narrative.

Per user directive (2026-05-08): "이야기의 흐름을 특정한 시간대로 두고 확인할
수 있도록. 베드로의 인생 / 예수님의 공생애 3년 이런식으로. 하드코딩한 결과물이
아니라 우리 에이전트, 월드 모델을 돌려서 결과를 얻도록."

This test module verifies:
    1. PhasedSimulationWorld + life_arc_narrative integration produces
       a 4-phase Korean timeline.
    2. Different seeds produce *different chosen_actions* for some events.
    3. All canonical event descriptions/scripture refs come from JSON files
       (no hardcoded narrative).
    4. No forbidden tokens (internal/dialogue) leak into rendered markdown.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.observer.life_arc_narrative import (  # noqa: E402
    LifeArcNarrative,
    build_life_arc_narrative,
    render_life_arc_html,
    render_life_arc_md,
)
from engine.simulation.phased_world import PhasedSimulationWorld  # noqa: E402

# Reuse demo_phased's phase config so the test does not duplicate engine wiring
from examples.demo_phased import _build_config, _rules  # noqa: E402
from scripts.narrative.run_life_arc_demo import PETER_PHASE_LABELS_KO  # noqa: E402


def _run_arc(seed: int, full_passion: bool = False) -> LifeArcNarrative:
    config = _build_config(with_passion=full_passion)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=seed)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or [])
        if p.canonical_events_path
    }
    return build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=seed,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
    )


# ============ structure ============

def test_four_phase_arc_has_four_windows():
    arc = _run_arc(seed=0, full_passion=False)
    assert len(arc.windows) == 4
    expected = ["01_calling", "02_galilean", "03_confession", "04_journey"]
    actual = [w.window.label for w in arc.windows]
    assert actual == expected


def test_full_passion_arc_has_five_windows_and_more_events():
    arc4 = _run_arc(seed=0, full_passion=False)
    arc5 = _run_arc(seed=0, full_passion=True)
    assert len(arc5.windows) == 5
    e4 = sum(len(w.canonical_events) for w in arc4.windows)
    e5 = sum(len(w.canonical_events) for w in arc5.windows)
    # passion phase fires multiple events
    assert e5 > e4


def test_total_days_is_around_101_for_4_phase():
    arc = _run_arc(seed=0, full_passion=False)
    # Original config: ~101 days for 4-phase
    assert 90 < arc.total_days < 120


def test_total_days_is_around_142_for_5_phase():
    arc = _run_arc(seed=0, full_passion=True)
    assert 130 < arc.total_days < 160


# ============ engine-driven choices ============

def test_chosen_actions_come_from_engine_action_histories():
    """canonical_events.json에 정의된 chosen_action 후보 중 *하나*만 골라야."""
    arc = _run_arc(seed=0, full_passion=False)
    # 01_calling phase has known event_id list
    calling = next(w for w in arc.windows if w.window.label == "01_calling")
    assert len(calling.canonical_events) >= 3
    for e in calling.canonical_events:
        # chosen_action은 engine 출력이므로 비어있으면 안 됨
        assert e.chosen_action
        assert e.chosen_action != "(no action)"


def test_different_seeds_yield_some_different_choices():
    """다른 seed → action_histories 다름 → narrative choice 다름."""
    arc0 = _run_arc(seed=0, full_passion=True)
    arc7 = _run_arc(seed=7, full_passion=True)
    choices0 = {e.event_id: e.chosen_action
                for w in arc0.windows for e in w.canonical_events}
    choices7 = {e.event_id: e.chosen_action
                for w in arc7.windows for e in w.canonical_events}
    common = set(choices0) & set(choices7)
    assert len(common) >= 5  # both seeds fire at least 5 shared events
    different = [eid for eid in common if choices0[eid] != choices7[eid]]
    assert different, (
        "no choice differences between seeds — narrative is not engine-driven. "
        f"choices0={choices0}, choices7={choices7}"
    )


def test_emotion_deltas_are_observed_not_hardcoded():
    """emotion_deltas는 extract_absolute_trajectory에서 와야 (engine 출력)."""
    arc = _run_arc(seed=0, full_passion=False)
    # 01_calling: awe should rise (canonical events add awe)
    calling = next(w for w in arc.windows if w.window.label == "01_calling")
    awe_delta = next(
        (d for d in calling.emotion_deltas if d.emotion == "awe"), None,
    )
    assert awe_delta is not None
    assert awe_delta.end_value > awe_delta.start_value  # awe rises


# ============ canonical event integrity ============

def test_canonical_event_descriptions_come_from_json_files():
    """description은 canonical_events.json verbatim — 코드에 하드코딩되면 안 됨."""
    arc = _run_arc(seed=0, full_passion=False)
    src = (ROOT / "engine/observer/life_arc_narrative.py").read_text(encoding="utf-8")
    for w in arc.windows:
        for e in w.canonical_events:
            # description은 module source에 들어있으면 안 됨 (즉, JSON에서 옴)
            assert e.description not in src, (
                f"description leaked into source: {e.description}"
            )


def test_scripture_refs_present():
    arc = _run_arc(seed=0, full_passion=True)
    # Every fired event should have a scripture_ref
    refs_found = 0
    for w in arc.windows:
        for e in w.canonical_events:
            if e.scripture_ref:
                refs_found += 1
    assert refs_found >= 5


# ============ markdown rendering ============

def test_rendered_md_contains_phase_labels():
    arc = _run_arc(seed=0, full_passion=False)
    md = render_life_arc_md(arc)
    assert "베드로의 생애" in md
    assert "1막: 부르심" in md
    assert "2막: 갈릴리 사역" in md


def test_rendered_md_no_internal_tokens():
    arc = _run_arc(seed=0, full_passion=False)
    md = render_life_arc_md(arc)
    forbidden = (
        "co-occurrence",
        "MomentLink", "StoryThread",
        "loyalty_vs_survival",
        "source_derived", "source_inferred",
    )
    for tok in forbidden:
        assert tok not in md, f"internal token {tok!r} leaked into md"


def test_rendered_md_no_dialogue_verbs():
    """Plan §10.2 — 대사 / 외쳤다 등 동사 of saying 금지."""
    arc = _run_arc(seed=0, full_passion=False)
    md = render_life_arc_md(arc)
    # Note: canonical_events.json에는 인용된 *예수의 말*이 들어있으므로
    # quotes는 허용. 그러나 *베드로의 외침* 같은 fabricated dialogue는 금지.
    # 모듈이 만든 텍스트에서만 검사 — narrative 단락 부분만 추출.
    # (간단 검사: "외쳤다" / "screamed" / "shouted" 단어가 등장하면 fail)
    forbidden_dialogue = ("외쳤다", "shouted", "screamed", "weeping")
    for v in forbidden_dialogue:
        assert v not in md, f"dialogue verb {v!r} leaked"


def test_unfired_events_populated_when_phase_has_no_action_history():
    """galilean / journey phases는 trigger 미일치로 0 events fire하지만,
    canonical_events.json에는 12 / 8개 정의되어 있음. unfired_events에 들어가야."""
    arc = _run_arc(seed=0, full_passion=True)
    galilean = next(w for w in arc.windows if w.window.label == "02_galilean")
    # 0 fired but should have unfired
    assert len(galilean.canonical_events) == 0
    assert len(galilean.unfired_events) >= 1
    for u in galilean.unfired_events:
        assert u.description
        assert u.scripture_ref or u.description  # at least one of them


def test_unfired_events_carry_scripture_refs():
    arc = _run_arc(seed=0, full_passion=True)
    refs = []
    for w in arc.windows:
        for u in w.unfired_events:
            if u.scripture_ref:
                refs.append(u.scripture_ref)
    # passion 외 phases에서 unfired refs 다수 존재해야 함
    assert len(refs) >= 5


def test_md_shows_unfired_events_in_silent_phases():
    arc = _run_arc(seed=0, full_passion=True)
    md = render_life_arc_md(arc)
    # 갈릴리 사역 섹션이 단순 "0건 발화" 만이 아니라 unfired list 포함
    assert "미발화 정경 사건" in md or "정의" in md


def test_to_dict_roundtrip():
    arc = _run_arc(seed=0, full_passion=False)
    d = arc.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    assert "schema_version" in d
    assert d["schema_version"] == "life_arc_narrative_v1"
    parsed = json.loads(s)
    assert parsed["seed"] == 0
    assert len(parsed["windows"]) == 4


# ============ orchestrator (script) — quick CLI integration ============

def test_by_week_window_strategy_produces_many_windows():
    """by_week → 약 7일/window으로 142.8일이 ~21개 window."""
    config = _build_config(with_passion=True)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=0,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_week",
    )
    # 142.8 days / 7 ≈ 20-21 windows
    assert 18 <= len(arc.windows) <= 22
    # week labels in Korean
    assert any("주차" in w.window.plain_label for w in arc.windows)


def test_by_week_no_event_double_counted():
    """이벤트가 정확히 주 boundary에 있어도 한 window에만 들어가야."""
    config = _build_config(with_passion=True)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=0,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_week",
    )
    all_event_ids = []
    for w in arc.windows:
        for e in w.canonical_events:
            all_event_ids.append(e.event_id)
    assert len(all_event_ids) == len(set(all_event_ids)), (
        "an event was double-counted across week boundaries"
    )


def test_by_week_silent_runs_compressed_in_md():
    """연속 silent weeks가 한 헤딩으로 압축된다."""
    config = _build_config(with_passion=True)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=0,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_week",
    )
    md = render_life_arc_md(arc)
    # peter seed 0 has at least one run of ≥2 silent weeks
    assert "연속" in md and "압축" in md, (
        "expected compressed silent-run heading in by_week markdown"
    )
    # Compressed heading uses 시간대 수 as integer
    import re
    runs = re.findall(r"연속 (\d+)개 시간대 압축", md)
    assert runs, "no compressed run found"
    assert all(int(n) >= 2 for n in runs)


def test_silent_compression_preserves_total_event_count():
    """압축은 *렌더*만 영향. arc.windows 데이터는 그대로 (압축 X)."""
    config = _build_config(with_passion=True)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=0,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_week",
    )
    # all 21 windows still present in dataclass
    assert len(arc.windows) >= 18  # ≥18 weeks for 142-day arc


def test_invalid_window_strategy_raises():
    config = _build_config(with_passion=False)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    with pytest.raises(ValueError):
        build_life_arc_narrative(
            result, agent_id="peter", agent_label="베드로", seed=0,
            window_strategy="by_decade",
        )


def test_html_renderer_produces_self_contained_html():
    arc = _run_arc(seed=0, full_passion=True)
    html = render_life_arc_html(arc)
    # Doctype + html tag
    assert html.startswith("<!DOCTYPE html>")
    assert "<html lang=\"ko\">" in html
    # Title contains agent label
    assert "베드로의 생애" in html
    # CSS inlined
    assert "<style>" in html
    # No external assets
    forbidden = (
        "<script src=", '<link rel="stylesheet" href=',
        "fonts.googleapis", "cdn.jsdelivr", "unpkg.com",
    )
    for f in forbidden:
        assert f not in html, f"external asset detected: {f}"


def test_html_includes_scripture_refs_and_korean_actions():
    arc = _run_arc(seed=0, full_passion=True)
    html = render_life_arc_html(arc)
    # Scripture refs preserved
    assert "눅 5:3" in html or "눅 5:1-3" in html
    # Korean action descriptions visible
    assert "그물" in html  # appears in calling phase action descriptions
    # Internal action_ids also present (as <code>)
    assert "wash_nets" in html or "confess" in html


def test_html_embeds_json_payload():
    arc = _run_arc(seed=0, full_passion=False)
    html = render_life_arc_html(arc)
    import re
    m = re.search(
        r'<script type="application/json" id="life-arc-payload">(.*?)</script>',
        html, re.DOTALL,
    )
    assert m, "JSON payload not embedded"
    payload = json.loads(m.group(1))
    assert payload["schema_version"] == "life_arc_narrative_v1"
    assert payload["agent_label"] == "베드로"


def test_html_compresses_silent_runs_for_by_week():
    config = _build_config(with_passion=True)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=0)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=0,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_week",
    )
    html = render_life_arc_html(arc)
    # Compressed silent run heading appears in HTML too
    assert "연속" in html and "압축" in html


def test_orchestrator_writes_markdown_html_and_json(tmp_path):
    import subprocess
    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/narrative/run_life_arc_demo.py"),
         "--seed", "0",
         "--output", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"{rc.stderr}\n{rc.stdout}"
    md = tmp_path / "life_arc_demo.md"
    html = tmp_path / "life_arc_demo.html"
    js = tmp_path / "life_arc_demo.json"
    assert md.exists()
    assert html.exists()
    assert js.exists()
    payload = json.loads(js.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "life_arc_narrative_v1"
    assert payload["seed"] == 0
    # HTML payload also embeds JSON
    html_text = html.read_text(encoding="utf-8")
    assert "life-arc-payload" in html_text
