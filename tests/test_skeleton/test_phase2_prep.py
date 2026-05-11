"""Tests for Phase 2 prep: LLM prompt templates, contract drift guard, RFC template.

Per `docs/witness_narrative_mode_plan.md`:
    - Phase 2 prep: prompt templates that match ANNOTATION_GUIDE.md
    - Contract drift: SkeletonOutput / UniversalStorySeed 필드 freeze
    - RFC template: contract 변경 governance
"""
from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# 1. LLM prompt templates (Phase 2)
# ============================================================================

def test_prompt_templates_module_imports():
    from scripts.annotation.prompt_templates import (
        ANNOTATION_FEATURES,
        SYSTEM_PROMPT_KO,
        build_user_prompt_ko,
        validate_annotation_dict,
        synthesize_annotations,
        ANNOTATION_SCHEMA_VERSION,
    )
    assert ANNOTATION_SCHEMA_VERSION.startswith("annotation_v")
    assert len(ANNOTATION_FEATURES) == 7


def test_prompt_features_match_annotation_guide():
    """7 features in prompt module must match ANNOTATION_GUIDE.md verbatim."""
    from scripts.annotation.prompt_templates import ANNOTATION_FEATURES
    guide = (ROOT / "docs/annotation/ANNOTATION_GUIDE.md").read_text(encoding="utf-8")
    for feature in ANNOTATION_FEATURES:
        assert feature in guide, f"feature {feature!r} in module but not in ANNOTATION_GUIDE.md"


def test_user_prompt_includes_synopsis_and_features():
    from scripts.annotation.prompt_templates import (
        build_user_prompt_ko, ANNOTATION_FEATURES,
    )
    prompt = build_user_prompt_ko("회차 줄거리 예시.", episode_no=5, title_ko="테스트작품")
    assert "테스트작품" in prompt
    assert "5" in prompt or "#5" in prompt
    assert "회차 줄거리 예시" in prompt
    for feature in ANNOTATION_FEATURES:
        assert feature in prompt
    # JSON-only enforcement
    assert "JSON only" in prompt or "JSON" in prompt


def test_validate_annotation_dict_catches_out_of_range():
    from scripts.annotation.prompt_templates import (
        validate_annotation_dict, ANNOTATION_SCHEMA_VERSION,
    )
    bad = {
        "schema_version": ANNOTATION_SCHEMA_VERSION,
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "test",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {
            "conflict_intensity_peak": 1.5,  # out of range
            "revelation_density": 0.5,
            "coincidence_frequency": 0.2,
            "relationship_polarization": 0.7,
            "new_conflict_introduction_rate": 0.3,
            "dangling_thread_generation": 0.4,
            "cliffhanger_intensity": 0.8,
        },
        "confidence": 0.9,
    }
    errs = validate_annotation_dict(bad)
    assert any("out of range" in e for e in errs)


def test_validate_annotation_accepts_valid_record():
    from scripts.annotation.prompt_templates import (
        validate_annotation_dict, ANNOTATION_SCHEMA_VERSION, ANNOTATION_FEATURES,
    )
    good = {
        "schema_version": ANNOTATION_SCHEMA_VERSION,
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "claude",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {f: 0.5 for f in ANNOTATION_FEATURES},
        "confidence": 0.7,
    }
    assert validate_annotation_dict(good) == []


def test_synthesize_annotations_averages_features():
    from scripts.annotation.prompt_templates import (
        synthesize_annotations, ANNOTATION_FEATURES,
    )
    a1 = {
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "claude",
        "features": {f: 0.4 for f in ANNOTATION_FEATURES},
        "evidence_quotes": [{"feature": "revelation_density", "quote_ko": "A"}],
    }
    a2 = {
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "gpt",
        "features": {f: 0.6 for f in ANNOTATION_FEATURES},
        "evidence_quotes": [{"feature": "revelation_density", "quote_ko": "B"}],
    }
    syn = synthesize_annotations([a1, a2])
    assert syn.title_id == "x"
    assert syn.episode_no == 1
    for f in ANNOTATION_FEATURES:
        assert syn.features[f] == 0.5  # mean of 0.4, 0.6
    # confidence: 1 - (0.6 - 0.4) = 0.8
    assert 0.79 <= syn.confidence <= 0.81
    # quotes union
    assert len(syn.evidence_quotes) == 2
    assert all("source_annotator_id" in q for q in syn.evidence_quotes)


def test_synthesize_empty_raises():
    from scripts.annotation.prompt_templates import synthesize_annotations
    with pytest.raises(ValueError):
        synthesize_annotations([])


# ============================================================================
# 2. Contract drift guard (Phase 0 freeze enforcement)
# ============================================================================

EXPECTED_SKELETON_OUTPUT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "seeds",
    "flow",
    "evidence_ledger",
    "anchor_metadata",
    "audit_trail",
)

EXPECTED_UNIVERSAL_SEED_FIELDS: tuple[str, ...] = (
    "seed_id",
    "conflict_axis_id",
    "main_role",
    "main_archetype",
    "dominant_pressures",
    "dominant_desires",
    "supporting_archetypes",
    "supporting_roles",
    "pressure_pattern",
    "change_pattern",
    "arc_direction",
    "relationship_function",
    "flow_role",
    "turning_points_count",
    "confidence_label",
    "audit_status",
    "evidence_count",
    "notes",
)


def test_skeleton_output_field_set_matches_frozen_contract():
    """**FROZEN**. 변경 시 RFC 의무 (docs/plans/RFC_TEMPLATE.md)."""
    from engine.observer.skeleton_output import SkeletonOutput
    actual = tuple(f.name for f in fields(SkeletonOutput))
    assert actual == EXPECTED_SKELETON_OUTPUT_FIELDS, (
        f"SkeletonOutput field set drifted! Expected {EXPECTED_SKELETON_OUTPUT_FIELDS}, "
        f"got {actual}. If intended, write an RFC per docs/plans/RFC_TEMPLATE.md "
        f"and update EXPECTED_SKELETON_OUTPUT_FIELDS in this test."
    )


def test_universal_story_seed_field_set_matches_frozen_contract():
    """**FROZEN**. 변경 시 RFC 의무."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    actual = tuple(f.name for f in fields(UniversalStorySeed))
    assert actual == EXPECTED_UNIVERSAL_SEED_FIELDS, (
        f"UniversalStorySeed field set drifted! Expected {EXPECTED_UNIVERSAL_SEED_FIELDS}, "
        f"got {actual}. RFC required per docs/plans/RFC_TEMPLATE.md."
    )


# ============================================================================
# 2.5 Phase 2.5 §F — Strengthened Drift Guard
#
# Field name만이 아니라 type annotation / default / frozen 여부 / mutability /
# schema_version까지 검사한다 (Plan §F.4).
# ============================================================================

def test_universal_story_seed_dataclass_is_frozen():
    """Phase 2.5 §F: frozen dataclass 해제 시 fail."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    assert UniversalStorySeed.__dataclass_params__.frozen is True, (
        "UniversalStorySeed must remain frozen (Plan §F)"
    )


def test_skeleton_output_dataclass_is_frozen():
    """Phase 2.5 §F: SkeletonOutput frozen dataclass 해제 시 fail."""
    from engine.observer.skeleton_output import SkeletonOutput
    assert SkeletonOutput.__dataclass_params__.frozen is True


def test_universal_story_seed_collection_fields_are_tuple_typed():
    """Phase 2.5 §F: tuple/list mutability drift 감지.
    immutable 컬렉션 필드는 tuple[...] 타입으로 선언되어야."""
    from typing import get_type_hints
    from engine.observer.universal_story_seed import UniversalStorySeed
    hints = get_type_hints(UniversalStorySeed)
    immutable_fields = (
        "dominant_pressures", "dominant_desires",
        "supporting_archetypes", "supporting_roles", "notes",
    )
    for fname in immutable_fields:
        annotation = hints.get(fname)
        assert annotation is not None, f"missing type hint for {fname}"
        # tuple[str, ...] 또는 typing.Tuple[str, ...]
        origin = getattr(annotation, "__origin__", None)
        assert origin is tuple, (
            f"{fname} must be typed as tuple[str, ...] (got {annotation!r}). "
            "Phase 2.5 §F: list typing is mutability drift."
        )


def test_universal_story_seed_scalar_field_types():
    """Phase 2.5 §F: scalar field 타입 drift 감지."""
    from typing import get_type_hints
    from engine.observer.universal_story_seed import UniversalStorySeed
    hints = get_type_hints(UniversalStorySeed)
    scalar_str_fields = (
        "seed_id", "conflict_axis_id", "main_role", "main_archetype",
        "change_pattern", "arc_direction", "relationship_function", "flow_role",
        "confidence_label", "audit_status",
    )
    for fname in scalar_str_fields:
        assert hints.get(fname) is str, (
            f"{fname} must be str (got {hints.get(fname)!r})"
        )
    assert hints.get("evidence_count") is int
    assert hints.get("turning_points_count") is int


def test_universal_story_seed_default_values_stable():
    """Phase 2.5 §F: default 값이 변경되면 fail (옵셔널 필드 묵시적 의미 변화 방지)."""
    from dataclasses import fields, MISSING
    from engine.observer.universal_story_seed import UniversalStorySeed

    expected_defaults: dict[str, object] = {
        "main_archetype": "",
        "dominant_pressures": (),
        "dominant_desires": (),
        "supporting_archetypes": (),
        "supporting_roles": (),
        "change_pattern": "",
        "arc_direction": "",
        "relationship_function": "",
        "flow_role": "",
        "turning_points_count": 0,
        "confidence_label": "",
        "audit_status": "pass",
        "evidence_count": 0,
        "notes": (),
    }
    actual_defaults = {f.name: f.default for f in fields(UniversalStorySeed)
                       if f.default is not MISSING}
    for fname, expected in expected_defaults.items():
        assert actual_defaults.get(fname) == expected, (
            f"default drift: {fname} expected={expected!r} "
            f"got={actual_defaults.get(fname)!r}"
        )


def test_universal_story_seed_default_factory_for_dict():
    """Phase 2.5 §F: pressure_pattern은 default_factory=dict이어야 (mutable default 방지)."""
    from dataclasses import fields, MISSING
    from engine.observer.universal_story_seed import UniversalStorySeed
    for f in fields(UniversalStorySeed):
        if f.name == "pressure_pattern":
            assert f.default_factory is dict, (
                f"pressure_pattern must use default_factory=dict, got {f.default_factory!r}"
            )
            assert f.default is MISSING, (
                "pressure_pattern must not have a literal default (use default_factory)"
            )
            return
    pytest.fail("pressure_pattern field not found")


def test_skeleton_output_schema_version_is_v1_family():
    """Phase 2.5 §F: SkeletonOutput.schema_version drift 감지."""
    from engine.observer.skeleton_output import (
        SkeletonOutput, SKELETON_OUTPUT_VERSION,
    )
    assert SKELETON_OUTPUT_VERSION.startswith("skeleton_output_v1"), (
        f"SkeletonOutput schema_version drifted: {SKELETON_OUTPUT_VERSION}"
    )
    out = SkeletonOutput()
    assert out.schema_version == SKELETON_OUTPUT_VERSION


def test_audit_trail_v1_1_has_unmapped_pressure_phrases_field():
    """Phase 2.5 §D.4: AuditTrail v1.1는 unmapped pressure phrase 추적."""
    from engine.observer.skeleton_output import AuditTrail
    at = AuditTrail()
    assert hasattr(at, "unmapped_pressure_phrases")
    assert hasattr(at, "missing_pressure_seeds")
    assert hasattr(at, "unknown_axis_count")


def test_life_story_flow_v1_1_has_flow_roles_field():
    """Phase 2.5 §E: LifeStoryFlow v1.1는 flow_roles dict 포함."""
    from engine.observer.skeleton_output import LifeStoryFlow
    lf = LifeStoryFlow()
    assert hasattr(lf, "flow_roles")
    assert isinstance(lf.flow_roles, dict)


# ============================================================================
# 2.6 Phase 2.5 follow-up — Sub-dataclass drift guard (Cycle 4)
#
# SkeletonOutput sub-dataclasses (EvidenceLedger / AuditTrail / LifeStoryFlow /
# AnchorMetadata) 도 contract — 변경 시 RFC 의무. 필드 이름 + frozen + 핵심
# 타입까지 검사한다.
# ============================================================================

EXPECTED_EVIDENCE_LEDGER_FIELDS: tuple[str, ...] = (
    "schema_version", "total_signals", "signals_per_seed",
    "audit_pass_count", "audit_fail_count", "audit_risky_count",
    "forbidden_token_violations", "notes",
)

EXPECTED_AUDIT_TRAIL_FIELDS: tuple[str, ...] = (
    "schema_version", "stages_passed",
    "forbidden_event_additions", "forbidden_dialogue_generation",
    "forbidden_slugline_use",
    "unmapped_pressure_phrases", "missing_pressure_seeds", "unknown_axis_count",
    "notes",
)

EXPECTED_LIFE_STORY_FLOW_FIELDS: tuple[str, ...] = (
    "schema_version", "ordering", "ordered_seed_ids", "flow_roles",
)

EXPECTED_ANCHOR_METADATA_FIELDS: tuple[str, ...] = (
    "anchor_id", "display_name_overrides", "role_label_overrides",
    "description_ko",
)


def test_evidence_ledger_field_set_matches_contract():
    from engine.observer.skeleton_output import EvidenceLedger
    actual = tuple(f.name for f in fields(EvidenceLedger))
    assert actual == EXPECTED_EVIDENCE_LEDGER_FIELDS, (
        f"EvidenceLedger drifted: expected {EXPECTED_EVIDENCE_LEDGER_FIELDS}, "
        f"got {actual}. RFC required."
    )


def test_audit_trail_field_set_matches_contract():
    from engine.observer.skeleton_output import AuditTrail
    actual = tuple(f.name for f in fields(AuditTrail))
    assert actual == EXPECTED_AUDIT_TRAIL_FIELDS, (
        f"AuditTrail drifted: expected {EXPECTED_AUDIT_TRAIL_FIELDS}, got {actual}. "
        "RFC required."
    )


def test_life_story_flow_field_set_matches_contract():
    from engine.observer.skeleton_output import LifeStoryFlow
    actual = tuple(f.name for f in fields(LifeStoryFlow))
    assert actual == EXPECTED_LIFE_STORY_FLOW_FIELDS, (
        f"LifeStoryFlow drifted: expected {EXPECTED_LIFE_STORY_FLOW_FIELDS}, "
        f"got {actual}. RFC required."
    )


def test_anchor_metadata_field_set_matches_contract():
    from engine.observer.skeleton_output import AnchorMetadata
    actual = tuple(f.name for f in fields(AnchorMetadata))
    assert actual == EXPECTED_ANCHOR_METADATA_FIELDS, (
        f"AnchorMetadata drifted: expected {EXPECTED_ANCHOR_METADATA_FIELDS}, "
        f"got {actual}. RFC required."
    )


def test_sub_dataclasses_are_frozen():
    """모든 SkeletonOutput sub-dataclass는 frozen이어야."""
    from engine.observer.skeleton_output import (
        EvidenceLedger, AuditTrail, LifeStoryFlow, AnchorMetadata,
    )
    for cls in (EvidenceLedger, AuditTrail, LifeStoryFlow, AnchorMetadata):
        assert cls.__dataclass_params__.frozen is True, (
            f"{cls.__name__} must be frozen"
        )


def test_audit_trail_v1_1_immutable_collections_use_tuple():
    """AuditTrail v1.1 신규 컬렉션 필드는 tuple 타입이어야."""
    from typing import get_type_hints
    from engine.observer.skeleton_output import AuditTrail
    hints = get_type_hints(AuditTrail)
    immutable_fields = (
        "stages_passed", "unmapped_pressure_phrases",
        "missing_pressure_seeds", "notes",
    )
    for fname in immutable_fields:
        annotation = hints.get(fname)
        origin = getattr(annotation, "__origin__", None)
        assert origin is tuple, (
            f"AuditTrail.{fname} must be tuple[str, ...] (got {annotation!r})"
        )


def test_life_story_flow_ordered_seed_ids_is_tuple():
    from typing import get_type_hints
    from engine.observer.skeleton_output import LifeStoryFlow
    hints = get_type_hints(LifeStoryFlow)
    annotation = hints.get("ordered_seed_ids")
    origin = getattr(annotation, "__origin__", None)
    assert origin is tuple, (
        f"LifeStoryFlow.ordered_seed_ids must be tuple[str, ...] (got {annotation!r})"
    )


def test_evidence_ledger_immutable_collections_use_tuple():
    from typing import get_type_hints
    from engine.observer.skeleton_output import EvidenceLedger
    hints = get_type_hints(EvidenceLedger)
    annotation = hints.get("notes")
    origin = getattr(annotation, "__origin__", None)
    assert origin is tuple, (
        f"EvidenceLedger.notes must be tuple[str, ...] (got {annotation!r})"
    )


def test_sub_dataclass_schema_versions_consistent():
    """Sub-dataclass schema_version은 v1.x family이어야 (drift catch)."""
    from engine.observer.skeleton_output import (
        EvidenceLedger, AuditTrail, LifeStoryFlow,
    )
    assert EvidenceLedger().schema_version.startswith("evidence_ledger_v1")
    assert AuditTrail().schema_version.startswith("audit_trail_v1")
    assert LifeStoryFlow().schema_version.startswith("life_story_flow_v1")


# ============================================================================
# 2.7 Phase 2.5 — Leveled feature validation (opt-in)
# ============================================================================

def test_is_valid_leveled_value_accepts_levels():
    from scripts.annotation.prompt_templates import is_valid_leveled_value
    for level in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        assert is_valid_leveled_value(level), level


def test_is_valid_leveled_value_within_tolerance():
    from scripts.annotation.prompt_templates import is_valid_leveled_value
    # ±0.05 tolerance
    assert is_valid_leveled_value(0.21)
    assert is_valid_leveled_value(0.84)
    assert not is_valid_leveled_value(0.5)   # 0.4와 0.6에서 0.1 거리 — out
    assert not is_valid_leveled_value(0.3)
    assert not is_valid_leveled_value(0.7)


def test_is_valid_leveled_value_rejects_out_of_range():
    from scripts.annotation.prompt_templates import is_valid_leveled_value
    assert not is_valid_leveled_value(-0.1)
    assert not is_valid_leveled_value(1.1)


def test_normalize_level_to_unit():
    from scripts.annotation.prompt_templates import normalize_level_to_unit
    assert normalize_level_to_unit(0) == 0.0
    assert normalize_level_to_unit(3) == 0.6
    assert normalize_level_to_unit(5) == 1.0
    # clamp
    assert normalize_level_to_unit(7) == 1.0
    assert normalize_level_to_unit(-1) == 0.0


def test_validate_strict_levels_rejects_off_level_for_leveled_features():
    """opt-in strict_levels=True 모드는 0.5 같은 off-level 거부."""
    from scripts.annotation.prompt_templates import (
        validate_annotation_dict, ANNOTATION_FEATURES, ANNOTATION_SCHEMA_VERSION,
    )
    bad = {
        "schema_version": ANNOTATION_SCHEMA_VERSION,
        "title_id": "x", "episode_no": 1, "annotator_id": "test",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {f: 0.5 for f in ANNOTATION_FEATURES},
        "confidence": 0.7,
    }
    errs_default = validate_annotation_dict(bad)  # 기본 — 0.5 통과
    leveled_errs_default = [e for e in errs_default if "leveled" in e]
    assert leveled_errs_default == []

    errs_strict = validate_annotation_dict(bad, strict_levels=True)
    leveled_errs_strict = [e for e in errs_strict if "leveled" in e]
    # conflict_intensity_peak + dangling_thread_generation 두 개 모두 fail
    assert len(leveled_errs_strict) == 2


def test_validate_strict_levels_accepts_clean_levels():
    """conflict_intensity_peak=0.6, dangling_thread_generation=0.4 같은 valid level은
    strict 통과."""
    from scripts.annotation.prompt_templates import (
        validate_annotation_dict, ANNOTATION_SCHEMA_VERSION,
    )
    good = {
        "schema_version": ANNOTATION_SCHEMA_VERSION,
        "title_id": "x", "episode_no": 1, "annotator_id": "test",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {
            "conflict_intensity_peak": 0.6,
            "revelation_density": 0.5,
            "coincidence_frequency": 0.3,
            "relationship_polarization": 0.7,
            "new_conflict_introduction_rate": 0.4,
            "dangling_thread_generation": 0.4,
            "cliffhanger_intensity": 0.5,
        },
        "confidence": 0.8,
    }
    errs = validate_annotation_dict(good, strict_levels=True)
    assert errs == [], errs


def test_rename_deprecated_features_migrates_old_names():
    """기존 어노테이션 (v1)에서 새 이름으로 자동 마이그레이션."""
    from scripts.annotation.prompt_templates import rename_deprecated_features
    old = {
        "conflict_amplification_rate": 0.4,
        "resolution_to_dangling_ratio": 0.6,
        "revelation_density": 0.3,
    }
    new = rename_deprecated_features(old)
    assert "conflict_intensity_peak" in new
    assert "dangling_thread_generation" in new
    assert "conflict_amplification_rate" not in new
    assert new["revelation_density"] == 0.3


def test_skeleton_output_schema_version_is_v1():
    from engine.observer.skeleton_output import (
        SkeletonOutput, SKELETON_OUTPUT_VERSION,
    )
    assert SKELETON_OUTPUT_VERSION == "skeleton_output_v1"
    out = SkeletonOutput()
    assert out.schema_version == "skeleton_output_v1"


def test_universal_seed_schema_version_is_v1_1():
    """Phase 2.5 RFC-0001: universal_story_seed_v1 → v1_1 (additive)."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(seed_id="X", conflict_axis_id="unknown",
                                main_role="main")
    d = seed.to_dict()
    assert d["schema_version"] == "universal_story_seed_v1_1"


def test_taxonomy_schema_versions_are_v1_family():
    """Phase 2.5 (2026-05-09): schema bumped to v1_1 for additive fields
    (colliding_desires/pressures, status, valid_for_training).
    Drift guard allows v1.x family, blocks v2."""
    for fname in ("pressure_taxonomy", "desire_taxonomy", "conflict_axes"):
        p = ROOT / "content" / "universal" / f"{fname}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        sv = d["_meta"]["schema_version"]
        assert sv.startswith("universal_taxonomy_v1"), (
            f"{fname}.json schema_version drifted (must be v1.x family): {sv}"
        )


# ============================================================================
# 3. RFC template
# ============================================================================

def test_rfc_template_exists_and_covers_required_sections():
    p = ROOT / "docs" / "plans" / "RFC_TEMPLATE.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for required in (
        "RFC ID",
        "동기",
        "제안",
        "schema_version",
        "마이그레이션",
        "영향",
        "대안",
        "승인 체크리스트",
    ):
        assert required in text, f"RFC_TEMPLATE.md missing section: {required}"


def test_rfc_template_references_skeleton_output_and_universal_seed():
    p = ROOT / "docs" / "plans" / "RFC_TEMPLATE.md"
    text = p.read_text(encoding="utf-8")
    assert "SkeletonOutput" in text
    assert "UniversalStorySeed" in text


# ============================================================================
# 4. PLAN_11_AUDIT updated with Narrative Mode Refactor
# ============================================================================

def test_plan_11_audit_has_phase0_and_phase1_sections():
    p = ROOT / "docs" / "portfolio" / "demo" / "PLAN_11_AUDIT.md"
    text = p.read_text(encoding="utf-8")
    assert "Phase 0" in text or "P0-1" in text
    assert "Phase 1" in text or "P1-1" in text
    assert "Phase 2" in text or "P2-1" in text
    # contract freeze 명시
    assert "FROZEN" in text or "RFC" in text
