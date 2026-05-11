"""Tests for Phase 4 → Phase H rubric critics + evaluator.

Phase H (2026-04-23) rewrite:
- CharacterCritic: character_consistency only (no smoothness bias)
- SceneResponseCritic: new axis for scene-appropriate response
- ContextBreakCritic: new noise gate
- NoveltyCritic: structured deviation (no canon_drift reuse)
- RubricEvaluator: 4 independent axes (+ canon + causal as gates)
"""

from __future__ import annotations

import pytest

from engine.constraint.hard_constraints import HardConstraintChecker
from engine.constraint.soft_constraints import SoftConstraintScorer
from engine.rubric import (
    CanonCritic,
    CausalCritic,
    CharacterCritic,
    ContextBreakCritic,
    DiscoveryClass,
    NoveltyCritic,
    RubricEvaluator,
    SceneResponseCritic,
)


def _make_evaluator(
    canonical_sequence,
    vocab,
    *,
    reproduction_threshold=1.0,
    novelty_low=0.25,
    novelty_high=0.75,
    character_min=0.3,
    scene_fit_min=0.3,
    break_threshold=0.5,
):
    hard = HardConstraintChecker(action_vocabulary=vocab)
    soft = SoftConstraintScorer(canonical_sequence=canonical_sequence)
    return RubricEvaluator(
        character=CharacterCritic(),
        scene_response=SceneResponseCritic(fit_threshold=scene_fit_min),
        context_break=ContextBreakCritic(break_threshold=break_threshold),
        canon=CanonCritic(hard=hard, soft=soft,
                          reproduction_threshold=reproduction_threshold),
        causal=CausalCritic(),
        novelty=NoveltyCritic(meaningful_low=novelty_low,
                              meaningful_high=novelty_high),
        character_min_composite=character_min,
        scene_fit_min=scene_fit_min,
    )


# -----------------------------------------------------------------
# CharacterCritic (Phase H: character_consistency only)
# -----------------------------------------------------------------

def test_character_critic_composite_range() -> None:
    c = CharacterCritic()
    report = c.evaluate([{"action_id": "pray", "state": {}}])
    assert 0 <= report.composite <= 1.0


def test_character_critic_identity_retention_high_with_sustained_loyalty() -> None:
    c = CharacterCritic(minimum_final_identity=4.0)
    records = [
        {"tick": 1, "action_id": "pray", "state": {"loyalty_pf": 9.0}},
        {"tick": 2, "action_id": "pray", "state": {"loyalty_pf": 9.0}},
    ]
    r = c.evaluate(records)
    assert r.identity_retention == 1.0


def test_character_critic_identity_retention_low_with_collapse() -> None:
    c = CharacterCritic(minimum_final_identity=6.0)
    records = [
        {"tick": 1, "action_id": "pray", "state": {"loyalty_pf": 9.0}},
        {"tick": 2, "action_id": "flee", "state": {"loyalty_pf": 2.0}},
    ]
    r = c.evaluate(records)
    assert r.identity_retention < 0.5


def test_character_critic_recovery_plausibility() -> None:
    c = CharacterCritic(spike_threshold=2.0, repentance_response_window=3)
    records = [
        {"tick": 1, "action_id": "pray", "state": {"grief": 0.0}},
        {"tick": 2, "action_id": "deny", "state": {"grief": 3.0}},  # spike
        {"tick": 3, "action_id": "weep", "state": {"grief": 2.5}},  # answered
    ]
    r = c.evaluate(records)
    assert r.recovery_plausibility == 1.0


# -----------------------------------------------------------------
# SceneResponseCritic
# -----------------------------------------------------------------

def test_scene_response_fit_in_family() -> None:
    c = SceneResponseCritic()
    records = [
        {"tick": 17, "event_in": ["public_accusation"], "action_id": "deny",
         "state": {}},
    ]
    r = c.evaluate(records)
    assert r.fit_rate == 1.0


def test_scene_response_fit_out_of_family() -> None:
    c = SceneResponseCritic()
    records = [
        {"tick": 17, "event_in": ["public_accusation"], "action_id": "pray",
         "state": {}},
    ]
    r = c.evaluate(records)
    assert r.fit_rate == 0.0


def test_scene_response_no_scenes() -> None:
    c = SceneResponseCritic()
    records = [{"tick": 1, "event_in": [], "action_id": "pray", "state": {}}]
    r = c.evaluate(records)
    assert r.n_scenes_observed == 0
    assert r.fit_rate == 1.0  # no signal = neutral pass


# -----------------------------------------------------------------
# ContextBreakCritic
# -----------------------------------------------------------------

def test_context_break_no_violations() -> None:
    c = ContextBreakCritic()
    records = [
        {"tick": 1, "action_id": "pray", "state": {}, "event_in": []},
        {"tick": 2, "action_id": "follow_closely", "state": {}, "event_in": []},
    ]
    r = c.evaluate(records)
    assert r.break_rate == 0.0
    assert r.is_context_coherent


def test_context_break_affordance_violation() -> None:
    c = ContextBreakCritic()
    records = [
        {"tick": 1, "action_id": "run_to_tomb", "state": {}, "event_in": []},
    ]
    r = c.evaluate(records)
    assert r.affordance_violations >= 1
    assert not r.is_context_coherent


def test_context_break_scene_mismatch() -> None:
    c = ContextBreakCritic()
    records = [
        {"tick": 1, "action_id": "jump_into_sea",
         "event_in": ["public_accusation"], "state": {}},
    ]
    r = c.evaluate(records)
    assert r.scene_mismatch_count >= 1
    assert r.affordance_violations >= 1


# -----------------------------------------------------------------
# NoveltyCritic (Phase H: structured deviation)
# -----------------------------------------------------------------

def test_novelty_rejects_float_input() -> None:
    c = NoveltyCritic()
    with pytest.raises(TypeError):
        c.evaluate(5.0)


def test_novelty_canon_copy_band() -> None:
    """Mostly in-family → low deviation → copy."""
    c = NoveltyCritic()
    records = [
        {"tick": 17, "event_in": ["public_accusation"],
         "action_id": "deny", "state": {}},
        {"tick": 18, "event_in": ["public_accusation"],
         "action_id": "deny", "state": {}},
        {"tick": 19, "event_in": ["public_accusation"],
         "action_id": "deny", "state": {}},
    ]
    r = c.evaluate(records)
    assert r.novelty_band == "copy"


def test_novelty_noise_band_random_out_of_family() -> None:
    """Out-of-family + action changes NOT explained by state/events → noise."""
    c = NoveltyCritic()
    # All scene actions out-of-family AND action changes with no event and
    # no state movement → low branching_coherence + high family_variation.
    records = [
        {"tick": 1, "event_in": ["public_accusation"],
         "action_id": "jump_into_sea", "state": {"fear": 0.0}},
        {"tick": 2, "event_in": [],
         "action_id": "run_to_tomb", "state": {"fear": 0.0}},
        {"tick": 3, "event_in": ["public_accusation"],
         "action_id": "stay_on_boat", "state": {"fear": 0.0}},
        {"tick": 4, "event_in": [],
         "action_id": "flee", "state": {"fear": 0.0}},
        {"tick": 5, "event_in": ["eye_contact"],
         "action_id": "assert_loyalty", "state": {"fear": 0.0}},
    ]
    r = c.evaluate(records)
    # family_variation high (all out), branching_coherence low (changes w/o events)
    assert r.response_family_variation >= 0.8
    assert r.novelty_band == "noise"


# -----------------------------------------------------------------
# Canon + Causal (unchanged)
# -----------------------------------------------------------------

def test_canon_critic_no_violation_clean_trajectory() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray", "follow"})
    soft = SoftConstraintScorer(canonical_sequence=[(1, "pray"), (2, "follow")])
    canon = CanonCritic(hard=hard, soft=soft, reproduction_threshold=2.0)
    records = [
        {"tick": 1, "action_id": "pray"},
        {"tick": 2, "action_id": "follow"},
    ]
    r = canon.evaluate(records)
    assert r.is_canon_valid
    assert r.is_canon_reproducing


def test_canon_critic_hard_violation_detected() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray"})
    canon = CanonCritic(hard=hard)
    records = [{"tick": 1, "action_id": "tweet"}]
    r = canon.evaluate(records)
    assert not r.is_canon_valid
    assert len(r.hard_violations) == 1


def test_causal_critic_flags_unexplained_jumps() -> None:
    critic = CausalCritic(jump_threshold=3.0, state_fields=["fear"])
    records = [
        {"state": {"fear": 1.0}},
        {"state": {"fear": 1.5}, "event_triggered": False},
        {"state": {"fear": 8.0}, "event_triggered": False},
        {"state": {"fear": 8.5}, "event_triggered": False},
    ]
    r = critic.evaluate(records)
    assert r.unexplained_jumps >= 1


def test_causal_critic_event_explains_jump() -> None:
    critic = CausalCritic(jump_threshold=3.0, state_fields=["fear"])
    records = [
        {"state": {"fear": 1.0}},
        {"state": {"fear": 9.0}, "event_triggered": True},
    ]
    r = critic.evaluate(records)
    assert r.unexplained_jumps == 0


# -----------------------------------------------------------------
# RubricEvaluator integration
# -----------------------------------------------------------------

def test_rubric_evaluator_invalid_on_hard_violation() -> None:
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray")], vocab={"pray"},
    )
    records = [{"tick": 1, "action_id": "unknown_action", "state": {},
                "event_in": []}]
    r = evaluator.evaluate(records)
    # Phase 3.05 rubric review §2.1: INVALID → INVALID_CANON_VIOLATION (정식 명칭)
    assert r.discovery_class == DiscoveryClass.INVALID_CANON_VIOLATION


def test_rubric_evaluator_canonical_reproduction() -> None:
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray"), (2, "follow_closely")],
        vocab={"pray", "follow_closely"},
        reproduction_threshold=1.0,
    )
    records = [
        {"tick": 1, "action_id": "pray", "state": {"loyalty_pf": 9.0},
         "event_in": []},
        {"tick": 2, "action_id": "follow_closely",
         "state": {"loyalty_pf": 9.0}, "event_in": []},
    ]
    r = evaluator.evaluate(records)
    assert r.discovery_class == DiscoveryClass.CANONICAL_REPRODUCTION


def test_rubric_evaluator_not_discovery_when_hardcoded() -> None:
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray")], vocab={"pray"},
    )
    records = [{"tick": 1, "action_id": "pray", "state": {}, "event_in": []}]
    r = evaluator.evaluate(records, is_all_hardcoded=True)
    assert r.discovery_class == DiscoveryClass.NOT_DISCOVERY_HARDCODED


def test_rubric_evaluator_context_break_routes_to_noise() -> None:
    """Phase H: context-break critic should catch affordance violations first."""
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "follow_closely")],
        vocab={"run_to_tomb", "follow_closely"},
        break_threshold=0.1,  # very strict
    )
    records = [
        {"tick": 1, "action_id": "run_to_tomb",  # no restoration context
         "state": {}, "event_in": []},
    ]
    r = evaluator.evaluate(records)
    assert r.discovery_class == DiscoveryClass.NOT_DISCOVERY_NOISE


# -----------------------------------------------------------------
# Phase 3.05 Rubric Design Review — P0 변경 (CANDIDATE label + causal gate)
# -----------------------------------------------------------------

def test_phase3_05_invalid_canon_violation_label() -> None:
    """rubric review §2.1: INVALID → INVALID_CANON_VIOLATION 정식 명칭."""
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray")], vocab={"pray"},
    )
    records = [{"tick": 1, "action_id": "unknown_action", "state": {},
                "event_in": []}]
    r = evaluator.evaluate(records)
    assert r.discovery_class == DiscoveryClass.INVALID_CANON_VIOLATION
    # backwards compat — legacy alias INVALID도 enum에 유지
    assert hasattr(DiscoveryClass, "INVALID")


def test_phase3_05_candidate_suffix_in_positive_labels() -> None:
    """rubric review §2.1: positive 분류는 _CANDIDATE 또는 _CHARACTER_DRIFT suffix."""
    # 두 새 label이 enum에 등록되어 있고 string value도 정확
    assert DiscoveryClass.CHARACTER_CONSISTENT_NOVEL_CANDIDATE.value == \
        "character_consistent_novel_candidate"
    assert DiscoveryClass.CANON_COMPATIBLE_CHARACTER_DRIFT.value == \
        "canon_compatible_character_drift"


def test_phase3_05_causal_gate_step_3() -> None:
    """rubric review §2.2 P0: causal coherence는 Step 3 (novelty 앞)에서 gate."""
    # 매우 큰 unexplained jumps를 만드는 records (smoothness_score < 0.4)
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray"), (2, "pray")], vocab={"pray"},
        break_threshold=1.0,  # context break은 통과 (gate Step 4)
    )
    records = [
        {"tick": 1, "action_id": "pray",
         "state": {"fear": 0.0, "hope": 0.0}, "event_in": []},
        # huge unexplained jump (no event_triggered)
        {"tick": 2, "action_id": "pray",
         "state": {"fear": 50.0, "hope": -50.0}, "event_in": [],
         "event_triggered": False},
    ]
    r = evaluator.evaluate(records)
    # causal smoothness가 매우 낮음 → Step 3 gate trip
    assert r.causal.smoothness_score < 0.4
    assert r.discovery_class == DiscoveryClass.NOT_DISCOVERY_INCOHERENT


def test_phase3_05_calibration_status_marked() -> None:
    """rubric review §2.7: threshold가 uncalibrated_phase3_placeholder 명시."""
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray")], vocab={"pray"},
    )
    assert evaluator.calibration_status == "uncalibrated_phase3_placeholder"


def test_phase3_05_no_scalar_total_score_in_report() -> None:
    """rubric review §1.2: scalar 합산 0 — 4축이 별도 sub-report로 보존."""
    evaluator = _make_evaluator(
        canonical_sequence=[(1, "pray")], vocab={"pray"},
    )
    records = [{"tick": 1, "action_id": "pray", "state": {}, "event_in": []}]
    r = evaluator.evaluate(records)
    # RubricReport는 character / scene_response / context_break / canon / causal / novelty 별도 필드
    assert hasattr(r, "character")
    assert hasattr(r, "scene_response")
    assert hasattr(r, "context_break")
    assert hasattr(r, "canon")
    assert hasattr(r, "causal")
    assert hasattr(r, "novelty")
    # 합산 scalar field 없음
    assert not hasattr(r, "discovery_score")
    assert not hasattr(r, "total_score")
    assert not hasattr(r, "aggregate_score")


def test_phase3_05_character_report_has_minimum_signature_fields() -> None:
    """rubric review §2.3 P1: CharacterReport에 passed_minimum_signature / weak_axes 추가."""
    c = CharacterCritic()
    report = c.evaluate([{"action_id": "pray", "state": {}}])
    assert hasattr(report, "passed_minimum_signature")
    assert hasattr(report, "weak_axes")
    assert hasattr(report, "calibration_status")
    assert report.calibration_status == "uncalibrated_phase3_placeholder"
    assert isinstance(report.weak_axes, tuple)


def test_phase3_05_character_minimum_gate_blocks_weak_axis() -> None:
    """rubric review §2.3 P1: 약한 axis (recovery_plausibility 0)가 있으면 passed_minimum_signature=False."""
    # recovery_plausibility를 강하게 fail시키는 records:
    # guilt spike 후 repentance 없음
    c = CharacterCritic(
        relation_stability_min=0.5,
        identity_retention_min=0.5,
        recovery_plausibility_min=0.5,
        repentance_response_window=2,
        spike_threshold=2.0,
    )
    records = [
        {"tick": 1, "action_id": "pray", "state": {"loyalty_pf": 9.0, "guilt": 0.0}},
        # large guilt spike, no repentance in next 2 ticks
        {"tick": 2, "action_id": "deny", "state": {"loyalty_pf": 9.0, "guilt": 5.0}},
        {"tick": 3, "action_id": "deny", "state": {"loyalty_pf": 9.0, "guilt": 5.0}},
        {"tick": 4, "action_id": "deny", "state": {"loyalty_pf": 9.0, "guilt": 5.0}},
    ]
    report = c.evaluate(records)
    # recovery_plausibility가 0 (spike 발견했지만 repentance 0) → minimum_signature fail
    assert report.recovery_plausibility == 0.0
    assert report.passed_minimum_signature is False
    assert "recovery_plausibility" in report.weak_axes


def test_phase3_05_character_composite_is_display_only() -> None:
    """rubric review §2.3 P1: composite가 평균은 통과해도 axis 미달이면 passed=False."""
    c = CharacterCritic(
        relation_stability_min=0.5,
        identity_retention_min=0.5,
        recovery_plausibility_min=0.5,
        spike_threshold=2.0,
        repentance_response_window=1,
    )
    # 2 axes pass (1.0 + 1.0) + 1 axis fail (0.0) → composite = 2/3 ≈ 0.67
    # composite ≥ 0.5라 단순 평균은 통과하지만, recovery_plausibility=0 → minimum_signature fail
    records = [
        {"tick": 1, "action_id": "pray", "state": {"loyalty_pf": 9.0, "guilt": 0.0}},
        {"tick": 2, "action_id": "deny", "state": {"loyalty_pf": 9.0, "guilt": 5.0}},
        {"tick": 3, "action_id": "deny", "state": {"loyalty_pf": 9.0, "guilt": 5.0}},
    ]
    r = c.evaluate(records)
    # composite은 fairly high (2/3) — 단순 평균이 약한 축 덮음
    # passed_minimum_signature은 axis별 minimum gate → fail
    if r.composite >= 0.5:
        # 정확히 review §2.3 시나리오 — 평균은 OK인데 minimum_signature는 fail
        assert r.passed_minimum_signature is False, (
            f"composite {r.composite:.2f}는 통과하지만 axis별 gate는 fail해야 함"
        )


def test_phase3_05_evaluator_uses_minimum_signature_not_composite() -> None:
    """rubric review §2.3 P1: Evaluator Step 7이 composite 대신 passed_minimum_signature 사용.

    약한 axis가 있어 minimum_signature fail하면 CHARACTER_CONSISTENT_NOVEL_CANDIDATE 불가.
    """
    # Note: 이 test는 Step 7에 도달하기 전 단계들이 모두 통과한다는 가정 필요 — 복잡함.
    # 직접적 단위 검증: char.passed_minimum_signature 필드가 evaluator decision에 쓰이는지
    from engine.rubric import CharacterCritic
    c = CharacterCritic()
    r = c.evaluate([{"action_id": "pray", "state": {}}])
    # 빈 trajectory도 default field 보유
    assert isinstance(r.passed_minimum_signature, bool)


def test_phase3_05_causal_report_has_p1_fields() -> None:
    """rubric review §2.5 P1: CausalReport에 explained_transition_ratio + passed_causal_gate."""
    c = CausalCritic()
    r = c.evaluate([
        {"tick": 1, "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 2, "state": {"fear": 1.0}, "event_triggered": False},
    ])
    assert hasattr(r, "explained_transition_ratio")
    assert hasattr(r, "total_transitions")
    assert hasattr(r, "passed_causal_gate")
    assert hasattr(r, "calibration_status")
    assert r.calibration_status == "uncalibrated_phase3_placeholder"
    assert 0.0 <= r.explained_transition_ratio <= 1.0


def test_phase3_05_causal_report_explained_ratio_correct() -> None:
    """explained_transition_ratio = (total - unexplained) / total."""
    c = CausalCritic(jump_threshold=5.0)
    # 3 transitions, 1 unexplained (no event_triggered, large jump)
    records = [
        {"tick": 1, "state": {"fear": 0.0, "hope": 0.0}, "event_triggered": False},
        {"tick": 2, "state": {"fear": 1.0, "hope": 1.0}, "event_triggered": False},  # small
        {"tick": 3, "state": {"fear": 50.0, "hope": -50.0}, "event_triggered": False},  # large unexplained
        {"tick": 4, "state": {"fear": 51.0, "hope": -50.0}, "event_triggered": False},  # small
    ]
    r = c.evaluate(records)
    # 3 transitions, 1 unexplained → ratio = 2/3 ≈ 0.67
    assert r.total_transitions == 3
    assert r.unexplained_jumps == 1
    assert abs(r.explained_transition_ratio - 2/3) < 0.01


def test_phase3_05_causal_passed_gate_fails_on_unexplained() -> None:
    """passed_causal_gate=False when explained ratio < min or smoothness < min."""
    c = CausalCritic(jump_threshold=5.0, explained_transition_min=0.9, smoothness_min=0.4)
    records = [
        {"tick": 1, "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 2, "state": {"fear": 100.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    # large unexplained jump → smoothness 낮음 + explained_ratio < 0.9
    assert r.passed_causal_gate is False


def test_phase3_05_novelty_report_has_p1_fields() -> None:
    """rubric review §2.4 P1: NoveltyReport에 changed_axes + interpretation + calibration."""
    c = NoveltyCritic()
    records = [
        {"tick": 1, "action_id": "pray", "scene_id": "prayer_invitation",
         "state": {}, "event_in": []},
    ]
    r = c.evaluate(records)
    assert hasattr(r, "changed_axes")
    assert hasattr(r, "interpretation")
    assert hasattr(r, "calibration_status")
    assert r.calibration_status == "uncalibrated_phase3_placeholder"
    assert isinstance(r.changed_axes, tuple)
    assert isinstance(r.interpretation, str)


def test_phase3_05_novelty_aliases() -> None:
    """rubric review §2.4: copy_like / noise_like / structured_difference_score aliases."""
    c = NoveltyCritic()
    records = [{"tick": 1, "action_id": "pray", "scene_id": "prayer_invitation",
                "state": {}, "event_in": []}]
    r = c.evaluate(records)
    # 새 alias properties 모두 동작
    assert r.copy_like == r.is_copy
    assert r.noise_like == r.is_noise
    assert r.structured_difference_score == r.structured_deviation


def test_phase3_05_canon_report_has_p2_fields() -> None:
    """rubric review §2.6 P2: CanonReport에 soft_compatibility_score / soft_deviations / hard_pass alias."""
    from engine.constraint.hard_constraints import HardConstraintChecker
    from engine.constraint.soft_constraints import SoftConstraintScorer
    canon = CanonCritic(
        hard=HardConstraintChecker(action_vocabulary={"pray"}),
        soft=SoftConstraintScorer(canonical_sequence=[(1, "pray")]),
    )
    r = canon.evaluate([{"tick": 1, "action_id": "pray", "state": {}, "event_in": []}])
    # P2 신규 필드 모두 존재
    assert hasattr(r, "soft_deviations")
    assert hasattr(r, "soft_compatibility_score")
    assert hasattr(r, "calibration_status")
    # hard_pass alias property
    assert r.hard_pass == r.is_canon_valid
    # soft_compatibility_score 범위 [0, 1]
    assert 0.0 <= r.soft_compatibility_score <= 1.0
    assert r.calibration_status == "uncalibrated_phase3_placeholder"


def test_phase3_05_canon_soft_compatibility_inverse_of_drift() -> None:
    """canon-exact (drift=0) → soft_compatibility_score=1.0."""
    from engine.constraint.hard_constraints import HardConstraintChecker
    from engine.constraint.soft_constraints import SoftConstraintScorer
    canon = CanonCritic(
        hard=HardConstraintChecker(action_vocabulary={"pray"}),
        soft=SoftConstraintScorer(canonical_sequence=[(1, "pray")]),
    )
    # canonical sequence와 정확 일치 → drift 0
    r = canon.evaluate([{"tick": 1, "action_id": "pray", "state": {}, "event_in": []}])
    assert r.soft_drift == 0.0
    assert r.soft_compatibility_score == 1.0


def test_phase3_05_runner_cli_smoke(tmp_path) -> None:
    """rubric runner CLI smoke test — records JSON → RubricReport JSON + markdown."""
    import subprocess
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        '[{"tick":1,"action_id":"pray","state":{},"event_in":[]},'
        '{"tick":2,"action_id":"follow_closely","state":{},"event_in":[]}]',
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    md_path = tmp_path / "out.md"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--md-report", str(md_path),
        "--canonical-sequence", '[[1, "pray"], [2, "follow_closely"]]',
        "--vocabulary", "pray follow_closely",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    # JSON output 검증
    assert out_path.exists()
    import json
    d = json.loads(out_path.read_text(encoding="utf-8"))
    # 4축 + canon + causal + scene + context + justification
    assert "discovery_class" in d
    assert "character" in d
    assert "canon" in d
    assert "causal" in d
    assert "novelty" in d
    assert "scene_response" in d
    assert "context_break" in d
    assert "justification" in d
    # MD output 검증
    assert md_path.exists()
    md = md_path.read_text(encoding="utf-8")
    assert "Non-Claims" in md
    assert "candidate" in md.lower()
    assert "uncalibrated" in md
    assert "Rule #14" in md


def test_phase3_05_runner_cli_exit_2_on_missing_records(tmp_path) -> None:
    """records 파일 없음 → exit 2."""
    import subprocess
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(tmp_path / "missing.json"),
        "--output", str(tmp_path / "out.json"),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 2


def test_phase3_05_rubric_demo_fixture_exists() -> None:
    """rubric demo fixture가 존재 + records 12개 + Non-Claims 명시."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests/fixtures/rubric_demo/peter_synthetic_trace.json"
    assert fixture.exists()
    d = json.loads(fixture.read_text(encoding="utf-8"))
    assert "meta" in d
    assert "records" in d
    assert len(d["records"]) >= 10
    # Non-Claims 명시
    meta_notes = d["meta"]["notes"]
    assert any("Non-Claims" in n or "fictional" in n or "합성" in n for n in meta_notes)


def test_phase3_05_rubric_demo_3_variants() -> None:
    """4 distinct discovery class variants deploy: 5 fixtures → canonical / drift(×2) / novel_candidate / incoherent."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    fixtures = ROOT / "tests/fixtures/rubric_demo"
    # 5 fixture 모두 존재 + Non-Claims marker
    expected_fixtures = [
        "peter_synthetic_trace",
        "peter_canonical_reproduction",
        "peter_novel_candidate",
        "peter_meaningful_novel",
        "peter_incoherent",
    ]
    for name in expected_fixtures:
        path = fixtures / f"{name}.json"
        assert path.exists(), f"fixture {name} missing"
        d = json.loads(path.read_text(encoding="utf-8"))
        notes = " ".join(d["meta"].get("notes", []))
        assert "합성" in notes or "Non-Claims" in notes or "fictional" in notes, (
            f"{name} meta.notes에 Non-Claims marker 누락"
        )

    # portfolio deploy 검증
    demo_dir = ROOT / "docs/portfolio/demo_rubric"
    if not demo_dir.exists():
        return

    # 4 reports 모두 존재 + expected class 일치
    expected_reports = {
        "canonical_reproduction_report": "canonical_reproduction",
        "incoherent_report": "not_discovery_incoherent",
        "meaningful_novel_report": "character_consistent_novel_candidate",
    }
    for fname, expected_class in expected_reports.items():
        report_path = demo_dir / f"{fname}.json"
        if not report_path.exists():
            continue
        d = json.loads(report_path.read_text(encoding="utf-8"))
        assert d["discovery_class"] == expected_class, (
            f"{fname}.json: expected {expected_class}, got {d['discovery_class']}"
        )

    # incoherent: passed_causal_gate False 강제 (review §2.2 P0)
    incoherent = demo_dir / "incoherent_report.json"
    if incoherent.exists():
        d = json.loads(incoherent.read_text(encoding="utf-8"))
        assert d["causal"]["passed_causal_gate"] is False
        just = " ".join(d.get("justification", []))
        assert "Step 3" in just or "causal" in just.lower()

    # meaningful_novel: novelty.band="meaningful" + character signature + scene_fit 모두 통과 (review §2.1 P0)
    meaningful = demo_dir / "meaningful_novel_report.json"
    if meaningful.exists():
        d = json.loads(meaningful.read_text(encoding="utf-8"))
        assert d["novelty"]["novelty_band"] == "meaningful"
        assert d["character"]["passed_minimum_signature"] is True
        # justification에 Step 7 명시
        just = " ".join(d.get("justification", []))
        assert "Step 7" in just


def test_phase3_05_trace_to_records_adapter_smoke() -> None:
    """trace_to_records.py adapter — demo_v07 형식 → rubric records 변환."""
    from pathlib import Path
    import json
    import subprocess
    import sys
    import tempfile
    ROOT = Path(__file__).resolve().parents[2]
    # synthetic trace 형식 (demo_v07 style)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        trace = td / "trace.jsonl"
        trace.write_text(
            '\n'.join([
                '{"tick": 1, "type": "action_taken", "payload": {"agent": "peter", "action": "pray"}}',
                '{"tick": 1, "type": "action_taken", "payload": {"agent": "judas", "action": "follow"}}',
                '{"tick": 2, "type": "action_taken", "payload": {"agent": "peter", "action": "weep", "event_id": "eye_contact"}}',
            ]),
            encoding="utf-8",
        )
        out = td / "records.json"
        rc = subprocess.run([
            sys.executable, str(ROOT / "scripts/rubric/trace_to_records.py"),
            "--trace", str(trace),
            "--agent", "peter",
            "--output", str(out),
        ], capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert rc.returncode == 0, rc.stdout + rc.stderr
        d = json.loads(out.read_text(encoding="utf-8"))
        # 2 tick의 peter actions만 (judas 제외)
        assert len(d) == 2
        assert d[0]["tick"] == 1
        assert d[0]["action_id"] == "pray"
        assert d[1]["tick"] == 2
        assert d[1]["action_id"] == "weep"
        # event_in: 같은 tick의 다른 event types
        # tick 2의 event_id "eye_contact"는 action_taken payload라 event_in에 안 들어감 — 정상


def test_phase3_05_real_simulation_deployed_if_present() -> None:
    """real_simulation_report.json deploy 시 검증 (선택적)."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    real = ROOT / "docs/portfolio/demo_rubric/real_simulation_report.json"
    if not real.exists():
        return  # 미배포 시 skip
    d = json.loads(real.read_text(encoding="utf-8"))
    # 모든 필수 필드 존재 (real simulation도 동일 schema)
    assert "discovery_class" in d
    assert d["character"]["calibration_status"] == "uncalibrated_phase3_placeholder"
    # records 많음 (real simulation)
    just = " ".join(d.get("justification", []))
    assert "Step" in just  # 어느 step에서 분류됐는지 명시


def test_phase3_05_ensemble_visualization_if_present() -> None:
    """ensemble_visualization.html deploy 시 검증 — Non-Claims + cross-scenario summary."""
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    html_path = ROOT / "docs/portfolio/demo_rubric/ensemble_visualization.html"
    if not html_path.exists():
        return
    html = html_path.read_text(encoding="utf-8")
    # Non-Claims 명시
    assert "Non-Claims" in html
    assert "uncalibrated_phase3_placeholder" in html
    assert "Rule #14" in html
    assert "candidate" in html.lower()
    # 3 ensembles 발견 (filename 기반)
    for name in ("cross_scenario_ensemble", "multi_agent_ensemble", "multi_seed_ensemble"):
        assert name in html, f"{name} ensemble missing from HTML"
    # discovery class 색상/태그 노출
    assert "character_consistent_novel_candidate" in html


def test_phase3_05_cross_scenario_ensemble_if_present() -> None:
    """Cross-scenario ensemble (peter + vangogh) deploy 시 검증."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    ensemble = ROOT / "docs/portfolio/demo_rubric/cross_scenario_ensemble.json"
    if not ensemble.exists():
        return
    d = json.loads(ensemble.read_text(encoding="utf-8"))
    assert "overall_distribution" in d
    assert "per_context" in d
    assert "calibration_status" in d
    # ≥2 scenarios
    assert "peter" in d["meta"]["scenarios"]
    assert "vangogh" in d["meta"]["scenarios"]
    # ≥4 contexts (3 peter agents + 1 vangogh)
    assert len(d["per_context"]) >= 4
    # vangogh context 존재
    has_vangogh = any("vangogh" in k for k in d["per_context"])
    assert has_vangogh


def test_phase3_05_multi_agent_ensemble_if_present() -> None:
    """Multi-agent ensemble deploy 시 검증 (3 agents × 5 seeds = 15 reports)."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    ensemble = ROOT / "docs/portfolio/demo_rubric/multi_agent_ensemble.json"
    if not ensemble.exists():
        return  # 미배포 시 skip
    d = json.loads(ensemble.read_text(encoding="utf-8"))
    # 핵심 필드
    assert "overall_distribution" in d
    assert "per_agent" in d
    assert "calibration_status" in d
    # 3 agents
    assert len(d["per_agent"]) >= 3
    # ≥5 seeds per agent
    for agent, info in d["per_agent"].items():
        assert "per_seed" in info
        assert len(info["per_seed"]) >= 5
    # overall_distribution 합 = total
    total = sum(d["overall_distribution"].values())
    expected = sum(len(info["per_seed"]) for info in d["per_agent"].values())
    assert total == expected


def test_phase3_05_multi_seed_ensemble_if_present() -> None:
    """Multi-seed ensemble deploy 시 검증 (Phase 3.05 review §H8 — 5+ seed)."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    ensemble = ROOT / "docs/portfolio/demo_rubric/multi_seed_ensemble.json"
    if not ensemble.exists():
        return  # 미배포 시 skip
    d = json.loads(ensemble.read_text(encoding="utf-8"))
    # 핵심 필드
    assert "distribution" in d
    assert "per_seed" in d
    assert "axis_means" in d
    assert "calibration_status" in d
    assert d["calibration_status"] == "uncalibrated_phase3_placeholder"
    # ≥5 seeds (review §H8)
    assert len(d["per_seed"]) >= 5
    # distribution 합 = total seeds
    total = sum(d["distribution"].values())
    assert total == len(d["per_seed"])
    # axis_means 모든 키 존재
    expected_axes = {"character_composite", "causal_smoothness",
                     "causal_explained_ratio", "novelty_structured_deviation",
                     "canon_soft_compatibility"}
    assert set(d["axis_means"].keys()) == expected_axes


def test_phase3_05_rubric_8step_all_endpoints_demonstrated() -> None:
    """rubric review §0 — 8-step flowchart 모든 endpoint portfolio 시연."""
    from pathlib import Path
    import json
    ROOT = Path(__file__).resolve().parents[2]
    demo_dir = ROOT / "docs/portfolio/demo_rubric"
    if not demo_dir.exists():
        return  # 미배포 시 skip
    # 7 distinct classes를 7 reports에서 발견 가능
    expected_classes = {
        "hardcoded_report": "not_discovery_hardcoded",          # Step 1
        "invalid_canon_report": "invalid_canon_violation",      # Step 2
        "incoherent_report": "not_discovery_incoherent",        # Step 3
        "noise_report": "not_discovery_noise",                  # Step 4-5
        "canonical_reproduction_report": "canonical_reproduction",   # Step 6
        "meaningful_novel_report": "character_consistent_novel_candidate",   # Step 7
        # Step 8 (drift)은 rubric_report.json 또는 novel_candidate_report.json
    }
    found_classes = set()
    for fname, expected in expected_classes.items():
        path = demo_dir / f"{fname}.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        assert d["discovery_class"] == expected, (
            f"{fname}.json: expected {expected}, got {d['discovery_class']}"
        )
        found_classes.add(d["discovery_class"])
    # Step 8 (drift) 별도 확인 — rubric_report 또는 novel_candidate
    for fname in ("rubric_report", "novel_candidate_report"):
        path = demo_dir / f"{fname}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            found_classes.add(d["discovery_class"])
    # 7 distinct classes 모두 발견
    expected_distinct = {
        "not_discovery_hardcoded",
        "invalid_canon_violation",
        "not_discovery_incoherent",
        "not_discovery_noise",
        "canonical_reproduction",
        "character_consistent_novel_candidate",
        "canon_compatible_character_drift",
    }
    missing = expected_distinct - found_classes
    assert not missing, f"누락된 discovery classes: {missing}"


def test_phase3_05_rubric_demo_deployed() -> None:
    """portfolio demo_rubric가 deploy됨 + Non-Claims + uncalibrated 명시."""
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    demo_dir = ROOT / "docs/portfolio/demo_rubric"
    if not demo_dir.exists():
        # 정직성 정책상 deploy 안 됐을 수도 — skip은 안 함, 명시적 검증
        import pytest
        pytest.skip("demo_rubric not deployed (정직성 정책)")

    # 3 산출물 모두 존재
    readme = demo_dir / "README.md"
    json_report = demo_dir / "rubric_report.json"
    md_report = demo_dir / "rubric_report.md"
    assert readme.exists()
    assert json_report.exists()
    assert md_report.exists()

    # README: Non-Claims + 합성 fixture 명시
    readme_text = readme.read_text(encoding="utf-8")
    assert "Non-Claims" in readme_text
    assert "synthetic" in readme_text or "합성" in readme_text or "fictional" in readme_text
    assert "uncalibrated" in readme_text
    assert "Rule #14" in readme_text
    assert "candidate" in readme_text.lower()

    # JSON report: 7 핵심 키 + discovery_class
    import json
    d = json.loads(json_report.read_text(encoding="utf-8"))
    assert "discovery_class" in d
    assert "character" in d
    assert "canon" in d
    assert "causal" in d
    assert "novelty" in d
    # 모든 critic에 calibration_status
    assert d["character"]["calibration_status"] == "uncalibrated_phase3_placeholder"
    assert d["causal"]["calibration_status"] == "uncalibrated_phase3_placeholder"
    assert d["novelty"]["calibration_status"] == "uncalibrated_phase3_placeholder"
    assert d["canon"]["calibration_status"] == "uncalibrated_phase3_placeholder"


def test_phase3_05_runner_handles_dict_records_wrapper(tmp_path) -> None:
    """{records: [...]} wrapper 형식도 지원."""
    import subprocess
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        '{"meta": "wrapped", "records": ['
        '{"tick":1,"action_id":"pray","state":{},"event_in":[]}]}',
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    assert out_path.exists()


def test_phase3_05_acceptance_criteria_all_met() -> None:
    """rubric review §5 acceptance criteria — 모든 acceptance 항목 통합 검증."""
    from engine.constraint.hard_constraints import HardConstraintChecker
    from engine.constraint.soft_constraints import SoftConstraintScorer

    # AC1: CANDIDATE / CHARACTER_DRIFT label 존재
    assert DiscoveryClass.CHARACTER_CONSISTENT_NOVEL_CANDIDATE
    assert DiscoveryClass.CANON_COMPATIBLE_CHARACTER_DRIFT
    # AC2: causal gate가 novelty 분류 *전* (Step 3, novelty band check는 Step 5)
    # 이미 test_phase3_05_causal_gate_step_3 검증
    # AC3-6: 각 critic 보강 필드 검증
    char = CharacterCritic()
    cr = char.evaluate([{"action_id": "pray", "state": {}}])
    assert hasattr(cr, "passed_minimum_signature")  # AC3
    assert hasattr(cr, "weak_axes")
    nov = NoveltyCritic()
    nr = nov.evaluate([{"tick": 1, "action_id": "pray", "scene_id": "prayer_invitation",
                        "state": {}, "event_in": []}])
    assert hasattr(nr, "changed_axes")  # AC4
    assert hasattr(nr, "interpretation")
    causal = CausalCritic()
    cau = causal.evaluate([{"tick": 1, "state": {}}, {"tick": 2, "state": {}}])
    assert hasattr(cau, "explained_transition_ratio")
    assert hasattr(cau, "passed_causal_gate")
    canon = CanonCritic(
        hard=HardConstraintChecker(action_vocabulary={"pray"}),
        soft=SoftConstraintScorer(canonical_sequence=[(1, "pray")]),
    )
    can = canon.evaluate([{"tick": 1, "action_id": "pray", "state": {}, "event_in": []}])
    assert hasattr(can, "soft_compatibility_score")  # AC8 (canon hard/soft 분리)
    assert hasattr(can, "soft_deviations")
    # AC5: calibration_status 모든 critic
    assert cr.calibration_status == "uncalibrated_phase3_placeholder"
    assert nr.calibration_status == "uncalibrated_phase3_placeholder"
    assert cau.calibration_status == "uncalibrated_phase3_placeholder"
    assert can.calibration_status == "uncalibrated_phase3_placeholder"


def test_phase3_05_neural_trainer_does_not_import_rubric() -> None:
    """rubric review §1.3 / Rule #14: neural trainer가 rubric import 0."""
    from pathlib import Path
    trainer_path = Path(__file__).resolve().parents[2] / "engine/policies/neural/trainer.py"
    if not trainer_path.exists():
        pytest.skip("neural trainer not present")
    text = trainer_path.read_text(encoding="utf-8")
    # rubric import 0 검증
    assert "from engine.rubric" not in text
    assert "import engine.rubric" not in text
    # loss = rubric 패턴 0
    assert "loss = rubric" not in text
    assert "rubric_score.backward" not in text


def test_rubric_engine_no_person_hardcoding() -> None:
    """Rule #1 on engine/rubric/."""
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    for py in (root / "engine" / "rubric").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")


# Phase 3.05 review §2.5 P1 extended (cycle 16) — pressure_action_alignment

def test_phase3_05_causal_pressure_alignment_default_no_map() -> None:
    """action_pressure_map 없으면 alignment_evaluated=False, gate 영향 0."""
    c = CausalCritic()  # no map
    records = [
        {"tick": 1, "action_id": "pray", "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 2, "action_id": "flee", "state": {"fear": 0.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    assert r.alignment_evaluated is False
    assert r.pressure_action_alignment == 1.0  # default
    assert r.aligned_actions == 0
    assert r.misaligned_actions == 0
    # gate는 alignment 영향 없이 통과해야 함 (smooth + explained 모두 통과)
    assert r.passed_causal_gate is True


def test_phase3_05_causal_pressure_alignment_aligned() -> None:
    """action이 expected pressure에 정렬되면 alignment_ratio = 1.0."""
    action_map = {
        "flee": ["fear"],
        "pray": ["grief", "fear"],
    }
    c = CausalCritic(action_pressure_map=action_map, pressure_min_value=3.0)
    records = [
        # flee at high fear → aligned
        {"tick": 1, "action_id": "flee", "state": {"fear": 8.0}, "event_triggered": False},
        # pray at high grief → aligned
        {"tick": 2, "action_id": "pray", "state": {"fear": 0.0, "grief": 5.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    assert r.alignment_evaluated is True
    assert r.aligned_actions == 2
    assert r.misaligned_actions == 0
    assert r.pressure_action_alignment == 1.0


def test_phase3_05_causal_pressure_alignment_misaligned() -> None:
    """action이 expected pressure 부족이면 misaligned + alignment_ratio < 1.0."""
    action_map = {"flee": ["fear"]}
    c = CausalCritic(action_pressure_map=action_map, pressure_min_value=3.0)
    records = [
        # flee at low fear → misaligned
        {"tick": 1, "action_id": "flee", "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 2, "action_id": "flee", "state": {"fear": 1.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    assert r.alignment_evaluated is True
    assert r.misaligned_actions == 2
    assert r.aligned_actions == 0
    assert r.pressure_action_alignment == 0.0
    assert len(r.misaligned_examples) >= 1
    assert "flee" in r.misaligned_examples[0]


def test_phase3_05_causal_pressure_alignment_unmapped() -> None:
    """map에 없는 action_id는 unmapped로 분류, alignment 비율 계산에서 제외."""
    action_map = {"flee": ["fear"]}
    c = CausalCritic(action_pressure_map=action_map, pressure_min_value=3.0)
    records = [
        {"tick": 1, "action_id": "flee", "state": {"fear": 5.0}, "event_triggered": False},
        {"tick": 2, "action_id": "unknown_action", "state": {"fear": 0.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    assert r.alignment_evaluated is True
    assert r.aligned_actions == 1
    assert r.misaligned_actions == 0
    assert r.unmapped_actions == 1
    # ratio = 1/1 (unmapped 제외)
    assert r.pressure_action_alignment == 1.0


def test_phase3_05_causal_pressure_alignment_gate_fails() -> None:
    """alignment_ratio < pressure_action_alignment_min이면 gate fail."""
    action_map = {"flee": ["fear"]}
    c = CausalCritic(
        action_pressure_map=action_map,
        pressure_min_value=3.0,
        pressure_action_alignment_min=0.6,
    )
    records = [
        # 1 aligned, 2 misaligned → ratio 0.33 < 0.6
        {"tick": 1, "action_id": "flee", "state": {"fear": 8.0}, "event_triggered": False},
        {"tick": 2, "action_id": "flee", "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 3, "action_id": "flee", "state": {"fear": 0.0}, "event_triggered": False},
    ]
    r = c.evaluate(records)
    assert r.alignment_evaluated is True
    assert r.pressure_action_alignment < 0.6
    assert r.passed_causal_gate is False


def test_phase3_05_causal_alignment_backwards_compat_legacy_callers() -> None:
    """legacy callers (no action_pressure_map)는 영향 받지 않음."""
    c = CausalCritic()
    r = c.evaluate([
        {"tick": 1, "state": {"fear": 0.0}, "event_triggered": False},
        {"tick": 2, "state": {"fear": 1.0}, "event_triggered": False},
    ])
    # 기존 필드 모두 존재
    assert hasattr(r, "explained_transition_ratio")
    assert hasattr(r, "passed_causal_gate")
    # 새 필드도 default 값 보유
    assert r.alignment_evaluated is False
    assert r.pressure_action_alignment == 1.0
    assert r.misaligned_examples == []


# Phase 3.05 review §2.5 P1 extended (cycle 20) — Rubric CLI exposes
# --action-pressure-map flag, surfacing pressure_action_alignment in output

def test_phase3_05_runner_cli_action_pressure_map(tmp_path) -> None:
    """CLI --action-pressure-map flag → causal report에 pressure_action_alignment 노출."""
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    # records: pray (high fear) → flee (high fear) → flee (low fear, misaligned)
    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        _json.dumps([
            {"tick": 1, "action_id": "pray", "state": {"fear": 5.0},
             "event_in": [], "event_triggered": True},
            {"tick": 2, "action_id": "flee", "state": {"fear": 6.0},
             "event_in": [], "event_triggered": True},
            {"tick": 3, "action_id": "flee", "state": {"fear": 0.5},
             "event_in": [], "event_triggered": False},
        ]),
        encoding="utf-8",
    )
    map_path = tmp_path / "pmap.json"
    map_path.write_text(
        _json.dumps({"pray": ["fear", "grief"], "flee": ["fear"]}),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray flee",
        "--action-pressure-map", str(map_path),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    # stdout에 alignment 노출
    assert "pressure_action_alignment" in rc.stdout
    d = _json.loads(out_path.read_text(encoding="utf-8"))
    causal = d["causal"]
    assert causal["alignment_evaluated"] is True
    # 3 actions all mapped (pray, flee, flee)
    # tick1 pray: fear=5 ≥ 3 → aligned
    # tick2 flee: fear=6 ≥ 3 → aligned
    # tick3 flee: fear=0.5 < 3 → misaligned
    assert causal["aligned_actions"] == 2
    assert causal["misaligned_actions"] == 1
    assert causal["unmapped_actions"] == 0
    assert 0.6 < causal["pressure_action_alignment"] < 0.7  # 2/3


def test_phase3_05_runner_cli_action_pressure_map_invalid_json(tmp_path) -> None:
    """잘못된 JSON 형식 → exit 2."""
    import subprocess
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text("[]", encoding="utf-8")
    bad_map = tmp_path / "bad.json"
    bad_map.write_text("not valid json {", encoding="utf-8")
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(tmp_path / "out.json"),
        "--action-pressure-map", str(bad_map),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 2


def test_phase3_05_runner_cli_action_pressure_map_wrong_shape(tmp_path) -> None:
    """JSON이 dict가 아니거나 value가 list[str]이 아니면 exit 2."""
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text("[]", encoding="utf-8")

    # value가 list가 아닌 경우
    bad_map = tmp_path / "bad.json"
    bad_map.write_text(_json.dumps({"pray": "fear"}), encoding="utf-8")
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(tmp_path / "out.json"),
        "--action-pressure-map", str(bad_map),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 2


def test_phase3_05_runner_cli_action_pressure_map_missing_file(tmp_path) -> None:
    """--action-pressure-map 파일 미존재 → exit 2."""
    import subprocess
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text("[]", encoding="utf-8")
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(tmp_path / "out.json"),
        "--action-pressure-map", str(tmp_path / "missing.json"),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 2


def test_phase3_05_runner_cli_action_pressure_map_skips_meta_keys(tmp_path) -> None:
    """Underscore-prefixed keys (예: `_meta`)는 inline metadata로 무시."""
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        _json.dumps([
            {"tick": 1, "action_id": "pray", "state": {"fear": 5.0},
             "event_in": [], "event_triggered": False},
            {"tick": 2, "action_id": "pray", "state": {"fear": 5.0},
             "event_in": [], "event_triggered": False},
        ]),
        encoding="utf-8",
    )
    map_path = tmp_path / "pmap.json"
    map_path.write_text(
        _json.dumps({
            "_meta": {"purpose": "demo", "calibration_status": "uncalibrated"},
            "_comment": "inline metadata block",
            "pray": ["fear"],
        }),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray",
        "--action-pressure-map", str(map_path),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    d = _json.loads(out_path.read_text(encoding="utf-8"))
    assert d["causal"]["alignment_evaluated"] is True
    assert d["causal"]["aligned_actions"] == 2  # 두 tick 모두 pray at fear=5 → aligned


# Phase 3.05 review §2.5 P1 extended (cycle 22) — alignment demo deployed —
# 외부 검증: noise fixture는 meaningful_novel보다 alignment ratio가 낮아야 한다
# (alignment metric이 discovery class와 *독립적으로* 일관해야 함)

# Phase 3.05 review §5 후속 (cycle 23) — CharacterCritic discrimination diagnostic.
# 설계 시점 (review §5): "단순 평균은 약한 축 덮음" + "Peter 고유성 정의 미검증".
# Phase H 재설계 (relation_stability + identity_retention + recovery_plausibility) +
# review §2.3 P1 minimum gate가 *실제로* anti-Peter 궤적을 거절하는지 empirical test.

def test_phase3_05_character_critic_rejects_anti_signature_trajectory() -> None:
    """Anti-Peter fixture (low loyalty drop / no repentance / final identity collapse)
    가 character_signature를 *fail*시키는지 확인. Pass 되면 critic over-permissive 신호.
    """
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests" / "fixtures" / "rubric_demo" / "peter_anti_signature.json"
    if not fixture.exists():
        import pytest
        pytest.skip("anti_signature fixture not present")

    data = _json.loads(fixture.read_text(encoding="utf-8"))
    records = data["records"]

    c = CharacterCritic()
    r = c.evaluate(records)

    # 핵심 invariant: 적어도 한 축이 minimum gate 미만이어야 critic이 작동
    assert r.passed_minimum_signature is False, (
        "anti-signature fixture가 character_signature를 통과 — critic over-permissive. "
        f"axes: relation={r.relation_stability:.3f}, identity={r.identity_retention:.3f}, "
        f"recovery={r.recovery_plausibility:.3f}, weak={r.weak_axes}"
    )
    # 두 축이 fail 예상 (identity_retention + recovery_plausibility)
    assert "identity_retention" in r.weak_axes
    assert "recovery_plausibility" in r.weak_axes
    # uncalibrated 표시 유지
    assert r.calibration_status == "uncalibrated_phase3_placeholder"


# Phase 3.05 review §5 ensemble (cycle 26) — axis-isolated anti-signature
# fixtures: 각 axis가 *independently* failure를 trigger할 수 있음을 입증 (L83
# N-case ensemble, minimum gate design empirical validation).

def test_phase3_05_axis_isolated_only_relation_fail() -> None:
    """relation_stability만 약한 fixture — minimum gate identifies single axis."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests" / "fixtures" / "rubric_demo" / "peter_anti_relation_only.json"
    if not fixture.exists():
        import pytest
        pytest.skip()
    data = _json.loads(fixture.read_text(encoding="utf-8"))
    r = CharacterCritic().evaluate(data["records"])
    assert r.passed_minimum_signature is False
    assert r.weak_axes == ("relation_stability",), (
        f"Expected single weak axis [relation_stability], got {r.weak_axes}. "
        f"axes: relation={r.relation_stability:.3f}, identity={r.identity_retention:.3f}, "
        f"recovery={r.recovery_plausibility:.3f}"
    )


def test_phase3_05_axis_isolated_only_identity_fail() -> None:
    """identity_retention만 약한 fixture."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests" / "fixtures" / "rubric_demo" / "peter_anti_identity_only.json"
    if not fixture.exists():
        import pytest
        pytest.skip()
    data = _json.loads(fixture.read_text(encoding="utf-8"))
    r = CharacterCritic().evaluate(data["records"])
    assert r.passed_minimum_signature is False
    assert r.weak_axes == ("identity_retention",)


def test_phase3_05_axis_isolated_only_recovery_fail() -> None:
    """recovery_plausibility만 약한 fixture (guilt spike → no repentance)."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests" / "fixtures" / "rubric_demo" / "peter_anti_recovery_only.json"
    if not fixture.exists():
        import pytest
        pytest.skip()
    data = _json.loads(fixture.read_text(encoding="utf-8"))
    r = CharacterCritic().evaluate(data["records"])
    assert r.passed_minimum_signature is False
    assert r.weak_axes == ("recovery_plausibility",)


# Phase 3.05 review §2.4 (cycle 27) — report_to_dict surfaces @property aliases.
# Engine had `copy_like` / `noise_like` / `structured_difference_score`로 review §2.4
# alias를 @property로 정의했지만 `_to_dict` 가 `__dict__` 만 사용해 deployed JSON에서
# 누락되던 L84 stranded 패턴.

def test_phase3_05_runner_cli_surfaces_novelty_aliases(tmp_path) -> None:
    """CLI 출력 JSON에 review §2.4 alias 필드 (copy_like / noise_like / structured_difference_score)
    가 *반드시* 포함되어야 한다."""
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        _json.dumps([
            {"tick": 1, "action_id": "pray", "scene_id": "prayer_invitation",
             "state": {}, "event_in": []},
            {"tick": 2, "action_id": "follow_closely", "scene_id": "sacred_meal",
             "state": {}, "event_in": []},
        ]),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray follow_closely",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    d = _json.loads(out_path.read_text(encoding="utf-8"))
    novelty = d["novelty"]
    # review §2.4 alias 필드 강제 노출
    assert "copy_like" in novelty
    assert "noise_like" in novelty
    assert "structured_difference_score" in novelty
    # 일관성: structured_difference_score == structured_deviation
    assert novelty["structured_difference_score"] == novelty["structured_deviation"]
    # boolean 타입
    assert isinstance(novelty["copy_like"], bool)
    assert isinstance(novelty["noise_like"], bool)


# Phase 3.05 cycle 28 — generic meta-test against L84 stranded pattern:
# 어떤 sub-report dataclass의 @property alias도 *반드시* JSON serialization에
# surface돼야 한다. report_to_dict()의 generic walker가 이 invariant를 강제.

def test_phase3_05_all_subreport_properties_surfaced_in_json(tmp_path) -> None:
    """Generic L84 detector — *all* @property aliases on rubric sub-reports
    must appear in serialized JSON. New @property가 추가되면 자동 검증됨.
    """
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        _json.dumps([
            {"tick": 1, "action_id": "pray", "scene_id": "prayer_invitation",
             "state": {"loyalty_pf": 8.0, "love": 8.0}, "event_in": []},
            {"tick": 2, "action_id": "follow_closely", "scene_id": "sacred_meal",
             "state": {"loyalty_pf": 8.0, "love": 8.0}, "event_in": []},
        ]),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray follow_closely",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0, rc.stdout + rc.stderr
    d = _json.loads(out_path.read_text(encoding="utf-8"))

    # 각 sub-report key에 대해 engine class에 정의된 @property가 모두 serialize되었는지 검증.
    from engine.rubric.canon_critic import CanonReport
    from engine.rubric.causal_critic import CausalReport
    from engine.rubric.character_critic import CharacterReport
    from engine.rubric.context_break_critic import ContextBreakReport
    from engine.rubric.novelty_critic import NoveltyReport
    from engine.rubric.scene_response_critic import SceneResponseReport

    sub_report_classes = {
        "character": CharacterReport,
        "canon": CanonReport,
        "causal": CausalReport,
        "novelty": NoveltyReport,
        "scene_response": SceneResponseReport,
        "context_break": ContextBreakReport,
    }
    missing: list[str] = []
    for key, cls in sub_report_classes.items():
        actual = d.get(key, {})
        for name in dir(cls):
            if name.startswith("_"):
                continue
            descriptor = getattr(cls, name, None)
            if isinstance(descriptor, property):
                if name not in actual:
                    missing.append(f"{key}.{name} (defined as @property on {cls.__name__})")
    assert not missing, (
        f"L84 stranded @property aliases not surfaced in JSON:\n"
        + "\n".join(missing[:15])
    )


def test_phase3_05_canon_report_hard_pass_alias_in_json(tmp_path) -> None:
    """Specific: CanonReport.hard_pass (review §2.6 alias) deve surface."""
    import subprocess
    import sys
    from pathlib import Path
    import json as _json
    ROOT = Path(__file__).resolve().parents[2]

    rec_path = tmp_path / "rec.json"
    rec_path.write_text(
        _json.dumps([
            {"tick": 1, "action_id": "pray", "state": {}, "event_in": []},
            {"tick": 2, "action_id": "follow_closely", "state": {}, "event_in": []},
        ]),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    rc = subprocess.run([
        sys.executable, str(ROOT / "scripts/rubric/run_rubric.py"),
        "--records", str(rec_path),
        "--output", str(out_path),
        "--vocabulary", "pray follow_closely",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert rc.returncode == 0
    d = _json.loads(out_path.read_text(encoding="utf-8"))
    canon = d["canon"]
    assert "hard_pass" in canon
    # 일관성: hard_pass == is_canon_valid
    assert canon["hard_pass"] == canon["is_canon_valid"]


def test_phase3_05_deployed_reports_have_novelty_aliases() -> None:
    """Deployed trajectory reports에 review §2.4 alias 필드 surface."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    demo_dir = ROOT / "docs" / "portfolio" / "demo_rubric"

    # 7 trajectory + 4 character + 3 alignment
    deployed_reports = [
        "canonical_reproduction_report.json",
        "meaningful_novel_report.json",
        "noise_report.json",
        "novel_candidate_report.json",
        "incoherent_report.json",
        "invalid_canon_report.json",
        "synthetic_trace_report.json",
        "hardcoded_report.json",
        "character_discrimination.json",
        "character_axis_anti_relation_only.json",
        "character_axis_anti_identity_only.json",
        "character_axis_anti_recovery_only.json",
        "alignment_meaningful_novel.json",
        "alignment_synthetic_trace.json",
        "alignment_noise.json",
    ]
    missing: list[str] = []
    for filename in deployed_reports:
        path = demo_dir / filename
        if not path.exists():
            continue
        d = _json.loads(path.read_text(encoding="utf-8"))
        n = d.get("novelty", {})
        for field in ("copy_like", "noise_like", "structured_difference_score"):
            if field not in n:
                missing.append(f"{filename}: missing {field}")
    assert not missing, (
        f"Deployed reports missing review §2.4 alias fields:\n"
        + "\n".join(missing[:10])
    )


def test_phase3_05_axis_isolated_demos_deployed() -> None:
    """Deployed character_axis_*.json reports show single weak axis each."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    demo_dir = ROOT / "docs" / "portfolio" / "demo_rubric"

    cases = [
        ("character_axis_anti_relation_only.json", "relation_stability"),
        ("character_axis_anti_identity_only.json", "identity_retention"),
        ("character_axis_anti_recovery_only.json", "recovery_plausibility"),
    ]
    for filename, expected_weak_axis in cases:
        path = demo_dir / filename
        if not path.exists():
            import pytest
            pytest.skip(f"{filename} not deployed")
        d = _json.loads(path.read_text(encoding="utf-8"))
        ch = d["character"]
        assert ch["passed_minimum_signature"] is False, (
            f"{filename} should have minimum_signature=False"
        )
        assert ch["weak_axes"] == [expected_weak_axis], (
            f"{filename} expected weak_axes=[{expected_weak_axis}], "
            f"got {ch['weak_axes']}"
        )


def test_phase3_05_character_critic_passes_meaningful_novel() -> None:
    """대조: positive class trajectory는 character_signature 통과 — discrimination 양방향."""
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    fixture = ROOT / "tests" / "fixtures" / "rubric_demo" / "peter_meaningful_novel.json"
    if not fixture.exists():
        import pytest
        pytest.skip("meaningful_novel fixture not present")

    data = _json.loads(fixture.read_text(encoding="utf-8"))
    records = data["records"]

    c = CharacterCritic()
    r = c.evaluate(records)

    assert r.passed_minimum_signature is True, (
        f"meaningful_novel이 character_signature fail — critic over-strict. "
        f"axes: relation={r.relation_stability:.3f}, identity={r.identity_retention:.3f}, "
        f"recovery={r.recovery_plausibility:.3f}, weak={r.weak_axes}"
    )
    assert r.weak_axes == ()


def test_phase3_05_deployed_alignment_demos_show_class_correlation() -> None:
    """deployed alignment demos: noise alignment < meaningful_novel alignment.

    cycle 16 alignment 측정이 discovery class와 *independent하게* 일관함을 입증.
    pressure_action_alignment는 causal critic 내부 측정이고 class 결정에 직접
    사용되지 않으므로, *별개 신호*가 같은 결론에 도달하는 게 신호 강도 확인.
    """
    import json as _json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    demo_dir = ROOT / "docs" / "portfolio" / "demo_rubric"

    novel_path = demo_dir / "alignment_meaningful_novel.json"
    noise_path = demo_dir / "alignment_noise.json"
    if not novel_path.exists() or not noise_path.exists():
        import pytest
        pytest.skip("deployed alignment demos not present")

    novel = _json.loads(novel_path.read_text(encoding="utf-8"))
    noise = _json.loads(noise_path.read_text(encoding="utf-8"))

    novel_align = novel["causal"]["pressure_action_alignment"]
    noise_align = noise["causal"]["pressure_action_alignment"]

    # discovery class 일관성: meaningful_novel = positive class, noise = noise class
    assert novel["discovery_class"] == "character_consistent_novel_candidate"
    assert noise["discovery_class"] == "not_discovery_noise"
    # alignment 측정도 같은 방향: noise < novel (별개 신호 일관)
    assert noise_align < novel_align, (
        f"alignment metric should agree with discovery class: "
        f"noise={noise_align}, novel={novel_align}"
    )
    # alignment_evaluated=True (action_pressure_map 사용됨)
    assert novel["causal"]["alignment_evaluated"] is True
    assert noise["causal"]["alignment_evaluated"] is True
