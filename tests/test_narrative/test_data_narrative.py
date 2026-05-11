"""Unit tests for data_narrative — NarrativeEvidence extractor + renderers.

핵심 검증:
    1. extractor가 observer dump에서 의미있는 수치를 뽑는다 (peaks / cooc / transitions)
    2. 다른 seed가 다른 NarrativeEvidence를 만든다
    3. 자연어 변환기가 한국어 plain language를 만든다 (내부 용어 누설 0)
    4. josa placeholder가 결과 텍스트에 leak되지 않게 처리되어야 함 (사용자가 본문에서 보면 안 됨)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.data_narrative import (
    NarrativeEvidence,
    PressurePeak,
    StateTransition,
    evidence_to_act_summary,
    evidence_to_logline,
    evidence_to_premise,
    evidence_to_scene_image,
    evidence_to_why,
    evidence_to_why_interesting,
    extract_narrative_evidence,
)
from engine.observer.episode_outline import resolve_korean_josa
from engine.observer.identity_resolver import IdentityResolver

ROOT = Path(__file__).resolve().parents[2]


def _load_observer(seed: int) -> dict:
    p = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
    if not p.exists():
        pytest.skip(f"observer dump for seed {seed} missing")
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Extractor tests
# ---------------------------------------------------------------------------

def test_extract_evidence_basic_shape():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    assert ev.total_ticks == len(obs["ticks"])
    assert ev.main_agent_id  # resolved
    assert ev.main_agent_name == "Peter"
    # peter_scarcity_baseline에서는 fear가 분명히 발생하므로 적어도 1 peak
    assert len(ev.main_agent_pressure_peaks) >= 1


def test_extract_evidence_pressure_peak_has_sustained_count():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    for p in ev.main_agent_pressure_peaks:
        assert p.sustained_ticks > 0
        assert p.peak_value > 0
        assert p.peak_tick >= 0


def test_extract_evidence_state_transitions_ordered():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    # transitions의 tick은 비감소
    ticks = [t.transition_tick for t in ev.main_agent_state_transitions]
    assert ticks == sorted(ticks)
    # plain_from / plain_to는 한국어
    for t in ev.main_agent_state_transitions:
        assert t.plain_from
        assert t.plain_to


def test_extract_evidence_co_occurrences_have_distinct_pressures():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    for c in ev.world_co_occurrences:
        assert c.pressure_a != c.pressure_b
        assert c.plain_a
        assert c.plain_b


# ---------------------------------------------------------------------------
# Seed diversity (the critical test)
# ---------------------------------------------------------------------------

def test_different_seeds_produce_different_evidence_numbers():
    """다른 seed → 다른 observer dump → 다른 NarrativeEvidence."""
    obs0 = _load_observer(0)
    obs3 = _load_observer(3)
    if obs0 == obs3:
        pytest.skip("seeds produce identical dumps (unexpected)")
    r0 = IdentityResolver.from_observer(obs0)
    r3 = IdentityResolver.from_observer(obs3)
    ev0 = extract_narrative_evidence(obs0, "Peter", r0)
    ev3 = extract_narrative_evidence(obs3, "Peter", r3)
    # 숫자 중 적어도 하나는 달라야 한다
    diffs = []
    if ev0.crowd_tense_ticks != ev3.crowd_tense_ticks:
        diffs.append("crowd_tense_ticks")
    if ev0.main_agent_action_count_early != ev3.main_agent_action_count_early:
        diffs.append("action_early")
    if ev0.main_agent_action_count_late != ev3.main_agent_action_count_late:
        diffs.append("action_late")
    if len(ev0.main_agent_pressure_peaks) != len(ev3.main_agent_pressure_peaks):
        diffs.append("peak_count")
    elif (ev0.main_agent_pressure_peaks and ev3.main_agent_pressure_peaks
          and ev0.main_agent_pressure_peaks[0].sustained_ticks
          != ev3.main_agent_pressure_peaks[0].sustained_ticks):
        diffs.append("peak_sustained")
    assert diffs, f"two seeds yielded identical evidence numbers (ev0={ev0}, ev3={ev3})"


def test_different_seeds_produce_different_logline_text():
    """seed 0 vs seed 3 logline 본문은 *다른 숫자*를 인용하므로 텍스트가 달라야."""
    obs0 = _load_observer(0)
    obs3 = _load_observer(3)
    r0 = IdentityResolver.from_observer(obs0)
    r3 = IdentityResolver.from_observer(obs3)
    ev0 = extract_narrative_evidence(obs0, "Peter", r0)
    ev3 = extract_narrative_evidence(obs3, "Peter", r3)
    log0 = resolve_korean_josa(evidence_to_logline(ev0))
    log3 = resolve_korean_josa(evidence_to_logline(ev3))
    assert log0 != log3, (
        "data-driven logline must differ across seeds; "
        f"got identical text:\n{log0}"
    )


def test_different_seeds_produce_different_premise_text():
    obs0 = _load_observer(0)
    obs3 = _load_observer(3)
    r0 = IdentityResolver.from_observer(obs0)
    r3 = IdentityResolver.from_observer(obs3)
    ev0 = extract_narrative_evidence(obs0, "Peter", r0)
    ev3 = extract_narrative_evidence(obs3, "Peter", r3)
    p0 = resolve_korean_josa(evidence_to_premise(ev0))
    p3 = resolve_korean_josa(evidence_to_premise(ev3))
    assert p0 != p3, "premise must differ across seeds"


def test_different_seeds_produce_different_why_text():
    obs0 = _load_observer(0)
    obs3 = _load_observer(3)
    r0 = IdentityResolver.from_observer(obs0)
    r3 = IdentityResolver.from_observer(obs3)
    ev0 = extract_narrative_evidence(obs0, "Peter", r0)
    ev3 = extract_narrative_evidence(obs3, "Peter", r3)
    w0 = resolve_korean_josa(evidence_to_why(ev0))
    w3 = resolve_korean_josa(evidence_to_why(ev3))
    assert w0 != w3, "why_this_feels_like_a_story must differ across seeds"


# ---------------------------------------------------------------------------
# Forbidden tokens / Korean surface
# ---------------------------------------------------------------------------

_FORBIDDEN_INTERNAL_TOKENS = (
    "tick ",
    "source_derived", "source_inferred",
    "co-occurrence",
    "authority_vigilance", "public_suspicion", "blame_concentration",
    "MomentLink", "StoryThread", "viable_with_gaps", "strong_viable",
    "loyalty_vs_survival", "uncertainty_vs_commitment",
)


def _all_text(ev: NarrativeEvidence) -> str:
    pieces = [
        evidence_to_logline(ev),
        evidence_to_premise(ev),
        evidence_to_scene_image(ev),
        evidence_to_why(ev),
        evidence_to_why_interesting(ev),
        evidence_to_act_summary(ev, 0),
        evidence_to_act_summary(ev, 1),
        evidence_to_act_summary(ev, 2),
    ]
    return resolve_korean_josa(" / ".join(pieces))


def test_renderer_outputs_have_no_internal_tokens():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    text = _all_text(ev)
    for tok in _FORBIDDEN_INTERNAL_TOKENS:
        assert tok not in text, f"internal token {tok!r} leaked: {text}"


def test_renderer_outputs_have_no_unresolved_josa_markers():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    text = _all_text(ev)
    for marker in ("은(는)", "이(가)", "을(를)", "과(와)", "으로(로)"):
        assert marker not in text, (
            f"unresolved josa marker {marker!r} in renderer output: {text}"
        )


def test_renderer_outputs_have_no_dialogue_quotes():
    """Plan §10.2 — 대사 / 따옴표 동사 금지."""
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    text = _all_text(ev)
    forbidden_dialogue_verbs = ("said", "asked", "shouted", "screamed",
                                 "외쳤다", "물었다")
    for v in forbidden_dialogue_verbs:
        assert v not in text


def test_evidence_to_dict_roundtrip():
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    d = ev.to_dict()
    # JSON-serializable
    s = json.dumps(d, ensure_ascii=False)
    assert "main_agent_pressure_peaks" in d
    assert "world_co_occurrences" in d
    assert json.loads(s)["total_ticks"] == ev.total_ticks


def test_renderer_quotes_observed_numbers():
    """Logline / why가 observer에서 *실제로* 나온 숫자를 인용한다."""
    obs = _load_observer(0)
    resolver = IdentityResolver.from_observer(obs)
    ev = extract_narrative_evidence(obs, "Peter", resolver)
    log = resolve_korean_josa(evidence_to_logline(ev))
    # total_ticks 200이 본문에 나타나야 (실제 데이터 연결 증거)
    assert str(ev.total_ticks) in log
    # 적어도 한 peak의 sustained_ticks가 본문에 나타남
    if ev.main_agent_pressure_peaks:
        first = ev.main_agent_pressure_peaks[0]
        assert str(first.sustained_ticks) in log
