"""Flesh Baseline v1 — Phase 3.1 weighted score (No-ML).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22 + §23.1 + §27.

목표:
    SkeletonOutput seed가 어떤 genre flesh와 잘 맞는지 *설명 가능한 weighted
    score*로 점수화. ML 모델 없음 — 모든 logic이 코드 + GenreProfile JSON으로
    설명 가능.

입력:
    - SkeletonOutput v1.1 (seeds + dominant_pressures + dominant_desires + flow_role 등)
    - List[GenreProfile] (Phase 3.1 build_genre_profiles.py로 생성)

출력 schema (§27 flesh_baseline_output_v1):
    {
      "schema_version": "flesh_baseline_output_v1",
      "source_skeleton_id": "...",
      "genre_profiles_used": ["korean_morning_melodrama"],
      "recommendations": [
        {
          "source_seed_id": "S01",
          "genre_id": "korean_morning_melodrama",
          "score": 0.78,
          "fit_label": "strong_fit",
          "reason_features": [...],
          "recommended_adapter": "rulebook_v2_8"
        }
      ],
      "model": {
        "type": "weighted_rule_score",
        "trained": false,
        "data_source": "phase3_pilot"
      },
      "audit": {
        "raw_text_used": false,
        "evidence_preserved": true
      }
    }

원칙:
    - score는 0.0-1.0 범위
    - reason_features는 설명 가능한 *원본 feature/skeleton 필드*만 인용
    - 대사 / 본문 생성 0
    - GenreProfile.feature_weights를 그대로 사용 (선형 결합)
    - skeleton에 annotation feature가 없으면 *compatibility-only score* fallback
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from engine.observer.genre_profile import GenreProfile
from engine.observer.skeleton_output import SkeletonOutput
from engine.observer.universal_story_seed import UniversalStorySeed


FLESH_BASELINE_OUTPUT_VERSION = "flesh_baseline_output_v1"


# ---------------------------------------------------------------------------
# Recommendation dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FleshRecommendation:
    """Phase 3.1 §27 recommendations 항목."""
    source_seed_id: str
    genre_id: str
    score: float
    fit_label: str                # "strong_fit" | "moderate_fit" | "weak_fit" | "no_fit"
    reason_features: tuple[str, ...]
    recommended_adapter: str = "rulebook_v2_8"
    # Phase 3.05: typed loosely (dict[str, object]) — None / nested dict / mode str 허용
    score_breakdown: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source_seed_id": self.source_seed_id,
            "genre_id": self.genre_id,
            "score": round(self.score, 4),
            "fit_label": self.fit_label,
            "reason_features": list(self.reason_features),
            "recommended_adapter": self.recommended_adapter,
            "score_breakdown": _serialize_breakdown(self.score_breakdown),
        }


def _serialize_breakdown(bd: dict) -> dict:
    """Phase 3.05 — score_breakdown JSON 직렬화 (None / nested dict / str 모두 허용)."""
    out: dict = {}
    for k, v in bd.items():
        if v is None:
            out[k] = None
        elif isinstance(v, (int, float)):
            out[k] = round(float(v), 4)
        elif isinstance(v, dict):
            out[k] = {kk: round(float(vv), 4) for kk, vv in v.items()}
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------

def _normalize_to_unit(score: float, max_level: int = 5) -> float:
    """0-5 level → 0.0-1.0. 또는 0.0-1.0 그대로."""
    if score <= 1.0:
        return max(0.0, min(1.0, score))
    return max(0.0, min(1.0, score / max_level))


def compute_compatibility_score(
    seed: UniversalStorySeed, profile: GenreProfile,
) -> tuple[float, list[str]]:
    """Skeleton seed의 conflict_axis / pressures와 profile compatibility.

    Returns:
        (score, reason_features) — score 0.0-1.0, 작은 reason 목록.
        Phase 3.05: detail이 필요하면 `compute_compatibility_detail` 사용.
    """
    score, reasons, _ = compute_compatibility_detail(seed, profile)
    return score, reasons


def compute_compatibility_detail(
    seed: UniversalStorySeed, profile: GenreProfile,
) -> tuple[float, list[str], dict[str, float]]:
    """Phase 3.05 — score_breakdown 정직성을 위해 axis_match / pressure_overlap 분리.

    Returns:
        (score, reason_features, components) — components: {
            "axis_match": 0.0 or 0.5,
            "pressure_overlap": 0.0-0.5 (Jaccard-like ratio × 0.5),
        }
    """
    reasons: list[str] = []
    components: dict[str, float] = {"axis_match": 0.0, "pressure_overlap": 0.0}

    # conflict_axis 매칭 (가장 강한 신호)
    if seed.conflict_axis_id in profile.compatible_conflict_axes:
        components["axis_match"] = 0.5
        reasons.append(f"conflict_axis:{seed.conflict_axis_id}")

    # dominant_pressures 매칭 — Jaccard-like 비율
    seed_pressures = set(seed.dominant_pressures or ())
    profile_pressures = set(profile.compatible_pressures or ())
    if seed_pressures and profile_pressures:
        overlap = seed_pressures & profile_pressures
        if overlap:
            ratio = len(overlap) / len(seed_pressures)
            components["pressure_overlap"] = round(0.5 * ratio, 4)
            for p in sorted(overlap):
                reasons.append(f"pressure:{p}")

    score = min(components["axis_match"] + components["pressure_overlap"], 1.0)
    return score, reasons, components


def compute_annotation_score(
    annotation_features: dict[str, float],
    profile: GenreProfile,
) -> tuple[float, list[str], dict[str, float]]:
    """Annotation feature × profile.feature_weights 선형 결합.

    각 feature score는 0-5 (또는 0.0-1.0)으로 받아 normalize 후 weight 곱셈.

    Returns:
        (score, reason_features, breakdown)
    """
    if not profile.feature_weights:
        return 0.0, [], {}

    breakdown: dict[str, float] = {}
    contributions: list[tuple[str, float]] = []
    for fname, weight in profile.feature_weights.items():
        raw = annotation_features.get(fname)
        if raw is None:
            breakdown[fname] = 0.0
            continue
        norm = _normalize_to_unit(float(raw))
        contribution = norm * weight
        breakdown[fname] = round(contribution, 4)
        contributions.append((fname, contribution))

    score = sum(breakdown.values())
    score = max(0.0, min(1.0, score))

    # reason_features = top-3 contributors
    contributions.sort(key=lambda x: -x[1])
    reasons = [f"feature:{name}" for name, _ in contributions[:3] if _ > 0]
    return score, reasons, breakdown


def fit_label_for_score(score: float) -> str:
    """§27 fit_label 매핑."""
    if score >= 0.7:
        return "strong_fit"
    if score >= 0.5:
        return "moderate_fit"
    if score >= 0.25:
        return "weak_fit"
    return "no_fit"


def recommend_seed(
    seed: UniversalStorySeed,
    profile: GenreProfile,
    annotation_features: dict[str, float] | None = None,
) -> FleshRecommendation:
    """단일 seed × profile → Recommendation.

    annotation_features (Phase 3.0 KEEP feature 평균 등)가 있으면 weighted score
    + compatibility 결합 (50/50). 없으면 compatibility-only (rulebook_only mode).

    Phase 3.05 — score_breakdown은 *항상* 채워진다 (정직성):
        {
            "axis_match": 0.0 or 0.5,
            "pressure_overlap": 0.0-0.5,
            "compatibility_score": 0.0-1.0,
            "annotation_score": 0.0-1.0 or None (rulebook_only),
            "annotation_components": {feature: contribution} or {} (rulebook_only),
            "final_score": 0.0-1.0,
            "mode": "rulebook_only" or "annotation_blended",
        }
    """
    compat_score, compat_reasons, compat_components = compute_compatibility_detail(
        seed, profile,
    )

    breakdown: dict = {
        "axis_match": compat_components["axis_match"],
        "pressure_overlap": compat_components["pressure_overlap"],
        "compatibility_score": round(compat_score, 4),
    }

    if annotation_features:
        ann_score, ann_reasons, ann_breakdown = compute_annotation_score(
            annotation_features, profile,
        )
        score = 0.5 * compat_score + 0.5 * ann_score
        reasons = ann_reasons + compat_reasons
        breakdown["annotation_score"] = round(ann_score, 4)
        breakdown["annotation_components"] = ann_breakdown
        breakdown["final_score"] = round(score, 4)
        breakdown["mode"] = "annotation_blended"
    else:
        score = compat_score
        reasons = compat_reasons
        breakdown["annotation_score"] = None
        breakdown["annotation_components"] = {}
        breakdown["final_score"] = round(score, 4)
        breakdown["mode"] = "rulebook_only"

    return FleshRecommendation(
        source_seed_id=seed.seed_id,
        genre_id=profile.genre_id,
        score=score,
        fit_label=fit_label_for_score(score),
        reason_features=tuple(reasons),
        recommended_adapter="rulebook_v2_8",
        score_breakdown=breakdown,
    )


# ---------------------------------------------------------------------------
# Top-level baseline runner
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FleshBaselineOutput:
    """Phase 3.1 §27 flesh_baseline_output_v1."""
    schema_version: str
    source_skeleton_id: str
    source_skeleton_version: str
    genre_profiles_used: tuple[str, ...]
    recommendations: tuple[FleshRecommendation, ...]
    model_type: str = "weighted_rule_score"
    model_trained: bool = False
    model_data_source: str = "phase3_pilot"
    audit_raw_text_used: bool = False
    audit_evidence_preserved: bool = True

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "source_skeleton_id": self.source_skeleton_id,
            "source_skeleton_version": self.source_skeleton_version,
            "genre_profiles_used": list(self.genre_profiles_used),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "model": {
                "type": self.model_type,
                "trained": self.model_trained,
                "data_source": self.model_data_source,
            },
            "audit": {
                "raw_text_used": self.audit_raw_text_used,
                "evidence_preserved": self.audit_evidence_preserved,
            },
        }


def run_flesh_baseline(
    skeleton: SkeletonOutput,
    profiles: list[GenreProfile],
    *,
    skeleton_id: str = "",
    annotation_features_by_seed: dict[str, dict[str, float]] | None = None,
) -> FleshBaselineOutput:
    """SkeletonOutput × profiles → recommendation list.

    annotation_features_by_seed: {seed_id → {feature_name → score}}.
    None이면 compatibility-only.
    """
    annotation_features_by_seed = annotation_features_by_seed or {}

    recommendations: list[FleshRecommendation] = []
    for seed in skeleton.seeds:
        ann_features = annotation_features_by_seed.get(seed.seed_id)
        for profile in profiles:
            rec = recommend_seed(seed, profile, annotation_features=ann_features)
            recommendations.append(rec)

    return FleshBaselineOutput(
        schema_version=FLESH_BASELINE_OUTPUT_VERSION,
        source_skeleton_id=skeleton_id or (
            skeleton.anchor_metadata.anchor_id if skeleton.anchor_metadata else ""
        ),
        source_skeleton_version=skeleton.schema_version,
        genre_profiles_used=tuple(p.genre_id for p in profiles),
        recommendations=tuple(recommendations),
        model_type="weighted_rule_score",
        model_trained=False,
        model_data_source=(
            profiles[0].data_source if profiles else "rulebook_only"
        ),
        audit_raw_text_used=False,
        audit_evidence_preserved=True,
    )
