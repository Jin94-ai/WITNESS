"""Tests for Episode Outline (Story Assembly Layer)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.episode_outline import (
    EpisodeAct, EpisodeOutline, SupportingArc,
    build_episode_outline, render_episode_outline_md,
    resolve_korean_josa, _has_final_consonant, pick_postposition,
)
from engine.observer.identity_resolver import IdentityResolver
from engine.observer.moment_extractor import extract_moments
from engine.observer.pressure_summary import build_pressure_summary
from engine.observer.scene_brief import build_scene_brief
from engine.observer.story_candidate_builder import build_story_candidates
from engine.observer.story_seed_card import build_seed_card
from engine.observer.story_viability import score_candidate
from engine.observer.thread_builder import build_story_threads, link_moments
from engine.observer.treatment import build_treatment

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/visual/dot_observer_data.json"


def _full_inputs():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    candidates = build_story_candidates(threads, moments, identity)
    pressure = build_pressure_summary(obs, identity_resolver=identity)
    seeds = []
    for c in candidates:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        seeds.append(build_seed_card(c, b, sc))
    return candidates, seeds, pressure


# ============ Korean josa resolver ============

def test_josa_resolves_no_consonant():
    # "Reader" 끝이 영어 → 받침 없음 → 는/가/를
    assert resolve_korean_josa("Reader은(는) 간다") == "Reader는 간다"
    assert resolve_korean_josa("Reader이(가) 본다") == "Reader가 본다"
    assert resolve_korean_josa("Reader을(를) 만든다") == "Reader를 만든다"


def test_josa_resolves_with_consonant():
    # "분위기" 끝 '기'는 받침 없음, "압력" 끝 '력'은 받침 있음
    assert resolve_korean_josa("압력이(가) 쌓인다") == "압력이 쌓인다"
    assert resolve_korean_josa("압력을(를) 받는다") == "압력을 받는다"
    assert resolve_korean_josa("분위기가 변한다") == "분위기가 변한다"  # already correct


def test_josa_handles_mixed_text():
    text = "Reader은(는) 자리에 남지만, 압력은(는) 계속된다."
    out = resolve_korean_josa(text)
    assert "Reader는" in out
    assert "압력은" in out
    assert "은(는)" not in out


def test_has_final_consonant_basics():
    assert _has_final_consonant("학")    # 학 has 받침 ㄱ
    assert not _has_final_consonant("가")  # 가 has no 받침
    assert not _has_final_consonant("Reader")  # english → no 한글 받침
    assert not _has_final_consonant("")    # empty


def test_pick_postposition():
    assert pick_postposition("Reader", "은", "는") == "Reader는"
    assert pick_postposition("학생", "은", "는") == "학생은"
    assert pick_postposition("학교", "을", "를") == "학교를"


# ============ Dataclasses ============

def test_supporting_arc_to_dict():
    sa = SupportingArc(seed_id="S02", name="Andrew", role_label="결정을 미루는 사람",
                        one_line="결정 없이 표류한다.")
    d = sa.to_dict()
    assert d["seed_id"] == "S02"
    assert d["role_label"] == "결정을 미루는 사람"


def test_episode_act_to_dict():
    a = EpisodeAct(label="Act 1 — Setup", plain_label="1막 — 시작",
                    summary="시작 단계.")
    d = a.to_dict()
    assert d["plain_label"] == "1막 — 시작"


# ============ End-to-end build_episode_outline ============

def test_build_episode_outline_uses_s01_as_main():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    # main_character는 S01의 main agent
    assert outline.main_character == seeds[0].main_character


def test_episode_outline_has_3_acts():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    assert outline.act_1.summary
    assert outline.act_2.summary
    assert outline.act_3.summary


def test_episode_outline_supporting_arcs_match_count():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    # supporting = candidates 1..end (except main)
    assert len(outline.supporting_arcs) == len(candidates) - 1


def test_episode_outline_supporting_arcs_have_distinct_roles():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    # plan: roles should differ — Andrew/James/John shouldn't all be same
    if len(outline.supporting_arcs) >= 2:
        roles = {s.role_label for s in outline.supporting_arcs}
        # 최소 2개의 distinct role
        assert len(roles) >= 2, (
            f"supporting roles too uniform: {[s.role_label for s in outline.supporting_arcs]}"
        )


def test_episode_outline_serializable_with_korean_josa_resolved():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    d = outline.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    # No "은(는)" / "이(가)" / "을(를)" remain in serialized output
    for marker in ("은(는)", "이(가)", "을(를)", "과(와)"):
        assert marker not in s, (
            f"unresolved josa marker {marker!r} in to_dict output"
        )


def test_episode_outline_no_internal_terms_in_main_text():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    text = " ".join([
        outline.title, outline.logline, outline.main_arc,
        outline.act_1.summary, outline.act_2.summary, outline.act_3.summary,
        outline.end_hook, outline.why_this_feels_like_a_story,
        *(s.role_label for s in outline.supporting_arcs),
        *(s.one_line for s in outline.supporting_arcs),
    ])
    forbidden = (
        "tick", "source_derived", "source_inferred", "co-occurrence",
        "authority_vigilance", "public_suspicion", "blame_concentration",
        "MomentLink", "StoryThread", "viable_with_gaps", "strong_viable",
        "loyalty_vs_survival", "uncertainty_vs_commitment",
    )
    for f in forbidden:
        assert f not in text, f"plan §forbidden term '{f}' in episode outline"


def test_episode_outline_no_dialogue_or_fabricated_action():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    text = " ".join([
        outline.act_1.summary, outline.act_2.summary, outline.act_3.summary,
        outline.why_this_feels_like_a_story,
    ])
    # Plan §10.2 forbidden
    forbidden = (
        '"', '"', '"',
        "EXT.", "INT.", "FADE IN",
        "배신했다", "고백했다", "도망쳤다", "체포했다",
        "rooster crowed", "denied him",
    )
    for f in forbidden:
        assert f not in text, f"forbidden token {f!r} in episode outline"


def test_episode_outline_evidence_summary_includes_seed_count():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure,
                                      audit_pass_count=4, audit_fail_count=0)
    assert str(len(seeds)) in outline.evidence_summary
    assert "감사 통과: 4" in outline.evidence_summary
    assert "실패: 0" in outline.evidence_summary


def test_episode_outline_md_renders():
    candidates, seeds, pressure = _full_inputs()
    outline = build_episode_outline(candidates, seeds, pressure)
    md = render_episode_outline_md(outline, "peter_scarcity_baseline")
    assert outline.title in md
    # logline is josa-resolved in MD; verify resolved form (not raw template)
    resolved_logline = resolve_korean_josa(outline.logline)
    assert resolved_logline in md
    # No josa markers in MD
    assert "은(는)" not in md
    assert "이(가)" not in md


def test_episode_outline_module_no_hardcoded_hero():
    src = (ROOT / "engine/observer/episode_outline.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Reader", "베드로", "Judas", "Caiaphas", "vangogh"):
        assert forbidden not in src, f"hero '{forbidden}' in episode_outline source"


def test_build_episode_outline_raises_on_empty():
    with pytest.raises(ValueError):
        # empty candidates / seeds
        from engine.observer.pressure_summary import PressureSummary
        ps = PressureSummary(
            total_ticks=0, dominant_world_pressure="", peak_pressure_tick=0,
            pressure_phases=(), top_agent_pressures=(),
            plain_language_summary="",
        )
        build_episode_outline([], [], ps)


# ============ Integration with NarrativeEvidence (data-driven body) ============

def _evidence_for_seed(seed: int):
    from engine.observer.data_narrative import extract_narrative_evidence
    p = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
    if not p.exists():
        pytest.skip(f"observer dump for seed {seed} missing")
    obs = json.loads(p.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    cands = build_story_candidates(threads, moments, identity)
    pressure = build_pressure_summary(obs, identity_resolver=identity)
    seeds_local = []
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        seeds_local.append(build_seed_card(c, b, sc))
    main_ev = None
    if cands and cands[0].main_characters:
        main_ev = extract_narrative_evidence(
            obs, cands[0].main_characters[0], identity_resolver=identity,
        )
    return cands, seeds_local, pressure, main_ev


def test_episode_outline_with_evidence_changes_logline():
    """evidence를 주면 logline이 lookup-fallback과 *달라야* 한다."""
    cands, seeds, pressure, ev = _evidence_for_seed(0)
    if not ev:
        pytest.skip("no evidence available")
    out_lookup = build_episode_outline(cands, seeds, pressure)
    out_evidence = build_episode_outline(cands, seeds, pressure, evidence=ev)
    assert out_lookup.logline != out_evidence.logline, (
        "logline must differ when evidence is supplied"
    )
    # evidence-driven은 *수치*를 인용해야 함
    assert str(ev.total_ticks) in out_evidence.logline


def test_episode_outline_two_seeds_yield_different_acts():
    """다른 seed의 evidence를 주면 Act 본문이 *다르게* 나와야 한다."""
    c0, s0, p0, ev0 = _evidence_for_seed(0)
    c3, s3, p3, ev3 = _evidence_for_seed(3)
    if not (ev0 and ev3):
        pytest.skip("evidence missing for one of the seeds")
    out0 = build_episode_outline(c0, s0, p0, evidence=ev0)
    out3 = build_episode_outline(c3, s3, p3, evidence=ev3)
    # Act 본문 셋 중 적어도 하나는 달라야 한다
    differences = sum([
        out0.act_1.summary != out3.act_1.summary,
        out0.act_2.summary != out3.act_2.summary,
        out0.act_3.summary != out3.act_3.summary,
    ])
    assert differences >= 1, (
        f"all three act summaries identical across seeds: {out0.act_1.summary}"
    )


def test_episode_outline_supporting_evidence_changes_one_lines():
    """supporting_evidence를 주면 supporting arc one-line이 *수치 인용*으로 바뀐다."""
    from engine.observer.data_narrative import extract_narrative_evidence
    p = ROOT / "data/visual/dot_observer_data_seed0.json"
    if not p.exists():
        pytest.skip("observer dump missing")
    obs = json.loads(p.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    cands = build_story_candidates(threads, moments, identity)
    pressure = build_pressure_summary(obs, identity_resolver=identity)
    seeds_local = []
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        seeds_local.append(build_seed_card(c, b, sc))
    sup_ev = {}
    for c in cands[1:]:
        if c.main_characters:
            sup_ev[c.story_candidate_id] = extract_narrative_evidence(
                obs, c.main_characters[0], identity_resolver=identity,
            )
    out_no_sup = build_episode_outline(cands, seeds_local, pressure)
    out_sup = build_episode_outline(
        cands, seeds_local, pressure, supporting_evidence=sup_ev,
    )
    # 적어도 한 supporting arc의 one_line이 달라야.
    # Iter 22-26 후: supporting one_line은 *수치 0* + 정성 표현 ("오래"/"꾸준히"/
    # "잠시") 사용. directive §2 — 메인/보조 surface에 수치 노출 금지.
    if out_sup.supporting_arcs:
        any_diff = False
        qualitative_words = ("오래", "꾸준히", "잠시", "다른 속도")
        for s_no, s_yes in zip(out_no_sup.supporting_arcs, out_sup.supporting_arcs):
            if s_no.one_line != s_yes.one_line:
                any_diff = True
                # 정성 표현이 들어가거나 (evidence 매핑 hit) fallback 표현 사용
                assert any(q in s_yes.one_line for q in qualitative_words), (
                    f"supporting one_line lacks qualitative descriptor: "
                    f"{s_yes.one_line!r}"
                )
        assert any_diff, "supporting_evidence had no effect on any one_line"


def test_seed_card_with_evidence_changes_premise():
    """build_seed_card에 evidence를 주면 plain_premise가 수치 인용으로 바뀐다."""
    from engine.observer.data_narrative import extract_narrative_evidence
    cands, seeds_lookup, pressure, ev = _evidence_for_seed(0)
    if not ev:
        pytest.skip("no evidence")
    c0 = cands[0]
    b = build_scene_brief(c0)
    t = build_treatment(c0, b)
    sc = score_candidate(c0, b, t)
    card_no = build_seed_card(c0, b, sc)
    card_ev = build_seed_card(c0, b, sc, evidence=ev)
    assert card_no.plain_premise != card_ev.plain_premise
    assert str(ev.total_ticks) in card_ev.plain_premise
