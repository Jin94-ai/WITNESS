"""Tests for genre_adapter (Phase 2.75 §6 + §7)."""
from __future__ import annotations

import pytest

from engine.observer.genre_adapter import (
    GENRE_ADAPTED_OUTPUT_VERSION,
    GenreAdaptedOutput,
    GenreAdaptedSeed,
    adapt_skeleton_to_genre,
)
from engine.observer.genre_rulebook import load_rulebook
from engine.observer.skeleton_output import (
    AnchorMetadata, AuditTrail, EvidenceLedger, LifeStoryFlow, SkeletonOutput,
)
from engine.observer.universal_story_seed import UniversalStorySeed


def _make_clean_skeleton() -> SkeletonOutput:
    """Phase 2.5 §4.1 입력 조건을 만족하는 minimal skeleton."""
    s1 = UniversalStorySeed(
        seed_id="S01",
        conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist",
        main_archetype="loyal_under_pressure",
        dominant_pressures=("authority_vigilance", "fear"),
        dominant_desires=("loyalty", "survival"),
        supporting_archetypes=("uncertain_actor", "watcher"),
        supporting_roles=("supporting_actor", "witness"),
        change_pattern="stay_present_then_withdraw",
        arc_direction="visibility_to_silence",
        relationship_function="group_presence_without_action",
        flow_role="main_arc",
        turning_points_count=3,
        evidence_count=21,
    )
    s2 = UniversalStorySeed(
        seed_id="S02",
        conflict_axis_id="uncertainty_vs_commitment",
        main_role="supporting_actor",
        main_archetype="uncertain_actor",
        dominant_pressures=("confusion",),
        dominant_desires=("commitment",),
        supporting_archetypes=("watcher",),
        supporting_roles=("witness",),
        change_pattern="delay_under_pressure",
        arc_direction="uncertainty_to_withdrawal",
        relationship_function="contrast_to_main_arc",
        flow_role="supporting_uncertainty",
        turning_points_count=2,
        evidence_count=9,
    )
    s3 = UniversalStorySeed(
        seed_id="S03",
        conflict_axis_id="control_vs_exposure",
        main_role="witness",
        main_archetype="watcher",
        dominant_pressures=("public_suspicion",),
        dominant_desires=("control",),
        supporting_archetypes=("loyal_under_pressure",),
        supporting_roles=("protagonist",),
        change_pattern="observe_without_intervening",
        arc_direction="presence_to_distance",
        relationship_function="witness_function",
        flow_role="witness_arc",
        turning_points_count=2,
        evidence_count=8,
    )
    s4 = UniversalStorySeed(
        seed_id="S04",
        conflict_axis_id="identity_vs_failure",
        main_role="delayed_actor",
        main_archetype="late_responder",
        dominant_pressures=("confusion", "shame_self"),
        dominant_desires=("identity_preservation",),
        supporting_archetypes=("uncertain_actor",),
        supporting_roles=("supporting_actor",),
        change_pattern="delayed_action",
        arc_direction="silence_to_response",
        relationship_function="delayed_echo",
        flow_role="delayed_response_arc",
        turning_points_count=1,
        evidence_count=4,
    )
    flow = LifeStoryFlow(
        ordering="evidence_derived",
        ordered_seed_ids=("S01", "S03", "S02", "S04"),
        flow_roles={
            "S01": "main_arc",
            "S02": "supporting_uncertainty",
            "S03": "witness_arc",
            "S04": "delayed_response_arc",
        },
    )
    return SkeletonOutput(
        seeds=(s1, s2, s3, s4),
        flow=flow,
        evidence_ledger=EvidenceLedger(total_signals=42, audit_pass_count=4),
        anchor_metadata=AnchorMetadata(anchor_id="peter_scarcity_baseline"),
        audit_trail=AuditTrail(
            stages_passed=("moments", "candidates", "audit"),
        ),
    )


# ---------------------------------------------------------------------------
# 1. adapt_skeleton_to_genre — happy path
# ---------------------------------------------------------------------------

def test_adapt_produces_genre_output_v1():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    assert isinstance(out, GenreAdaptedOutput)
    assert out.schema_version == GENRE_ADAPTED_OUTPUT_VERSION
    assert out.schema_version.startswith("genre_adapted_output_v1")
    assert out.genre_id == "korean_morning_melodrama"
    assert out.source_skeleton_version.startswith("skeleton_output_v")
    assert len(out.adapted_seeds) == 4


def test_adapted_seeds_preserve_source_seed_ids():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    source_ids = [s.source_seed_id for s in out.adapted_seeds]
    assert source_ids == ["S01", "S02", "S03", "S04"]


def test_adapted_seeds_preserve_conflict_axis():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    sk = _make_clean_skeleton()
    by_id = {s.seed_id: s for s in sk.seeds}
    for adapted in out.adapted_seeds:
        original = by_id[adapted.source_seed_id]
        assert adapted.source_conflict_axis_id == original.conflict_axis_id


def test_adapted_seeds_preserve_pressures_and_desires():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    sk = _make_clean_skeleton()
    by_id = {s.seed_id: s for s in sk.seeds}
    for adapted in out.adapted_seeds:
        original = by_id[adapted.source_seed_id]
        assert adapted.source_pressures == original.dominant_pressures
        assert adapted.source_desires == original.dominant_desires


def test_adapted_seeds_have_structure_only_transformation_level():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    for s in out.adapted_seeds:
        assert s.transformation_level == "structure_only"
        assert s.evidence_preserved is True
        assert s.forbidden_added is False


def test_adapted_seed_genre_role_uses_rulebook():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    # S01: protagonist → "버티는 사람" / "숨기는 사람"
    s01 = next(s for s in out.adapted_seeds if s.source_seed_id == "S01")
    assert s01.genre_role in ("버티는 사람", "숨기는 사람")
    # S03: witness → "알아차리지만 말하지 않는 사람"
    s03 = next(s for s in out.adapted_seeds if s.source_seed_id == "S03")
    assert s03.genre_role == "알아차리지만 말하지 않는 사람"


def test_adapted_seed_genre_pressure_uses_rulebook():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    s01 = next(s for s in out.adapted_seeds if s.source_seed_id == "S01")
    # authority_vigilance → "가족/권위자의 시선"
    assert "가족/권위자의 시선" in s01.genre_pressure


def test_adapted_flow_orders_seeds_per_skeleton():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    assert out.adapted_flow.source_ordered_seed_ids == ("S01", "S03", "S02", "S04")


def test_adapted_flow_preserves_evidence_summary():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    summary = out.adapted_flow.evidence_summary
    assert summary["source_seed_count"] == 4
    assert "loyalty_vs_survival" in summary["preserved_conflict_axes"]
    assert "authority_vigilance" in summary["preserved_pressures"]
    assert "loyalty" in summary["preserved_desires"]


def test_adapted_flow_outline_uses_episode_rhythm():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    outline = out.adapted_flow.adapted_outline_ko
    assert len(outline) == len(rb.episode_rhythm)
    # 첫 라인은 첫 rhythm 단계로 시작
    assert outline[0].startswith("1. ") and rb.episode_rhythm[0] in outline[0]


def test_adapted_flow_cliffhanger_uses_priority_pattern():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    # main seed S01 has loyalty_vs_survival → silence_read_as_betrayal
    assert "침묵을 배신으로 해석" in out.adapted_flow.cliffhanger_ko


def test_adapted_output_to_dict_roundtrip():
    rb = load_rulebook("korean_morning_melodrama")
    out = adapt_skeleton_to_genre(_make_clean_skeleton(), rb)
    d = out.to_dict()
    assert d["schema_version"] == GENRE_ADAPTED_OUTPUT_VERSION
    assert d["genre_id"] == "korean_morning_melodrama"
    assert isinstance(d["adapted_seeds"], list)
    assert len(d["adapted_seeds"]) == 4
    # to_dict가 자체 직렬화 가능
    import json
    s = json.dumps(d, ensure_ascii=False)
    assert "korean_morning_melodrama" in s


# ---------------------------------------------------------------------------
# 2. Input gate (Plan §4.1)
# ---------------------------------------------------------------------------

def test_adapt_rejects_skeleton_without_flow():
    from dataclasses import replace
    rb = load_rulebook("korean_morning_melodrama")
    sk = _make_clean_skeleton()
    sk_no_flow = SkeletonOutput(
        schema_version=sk.schema_version,
        seeds=sk.seeds,
        flow=None,
        evidence_ledger=sk.evidence_ledger,
        anchor_metadata=sk.anchor_metadata,
        audit_trail=sk.audit_trail,
    )
    with pytest.raises(ValueError, match="flow"):
        adapt_skeleton_to_genre(sk_no_flow, rb)


def test_adapt_rejects_skeleton_with_unknown_axis_count():
    rb = load_rulebook("korean_morning_melodrama")
    sk = _make_clean_skeleton()
    bad_audit = AuditTrail(
        stages_passed=sk.audit_trail.stages_passed,
        unknown_axis_count=1,
    )
    sk_unknown = SkeletonOutput(
        schema_version=sk.schema_version,
        seeds=sk.seeds, flow=sk.flow,
        evidence_ledger=sk.evidence_ledger,
        anchor_metadata=sk.anchor_metadata,
        audit_trail=bad_audit,
    )
    with pytest.raises(ValueError, match="unknown_axis_count"):
        adapt_skeleton_to_genre(sk_unknown, rb)


def test_adapt_rejects_skeleton_with_forbidden_event_additions():
    rb = load_rulebook("korean_morning_melodrama")
    sk = _make_clean_skeleton()
    bad_audit = AuditTrail(
        stages_passed=sk.audit_trail.stages_passed,
        forbidden_event_additions=1,
    )
    sk_bad = SkeletonOutput(
        schema_version=sk.schema_version,
        seeds=sk.seeds, flow=sk.flow,
        evidence_ledger=sk.evidence_ledger,
        anchor_metadata=sk.anchor_metadata,
        audit_trail=bad_audit,
    )
    with pytest.raises(ValueError, match="forbidden_event_additions"):
        adapt_skeleton_to_genre(sk_bad, rb)
