"""Adaptation Recommendation v1 — Phase 3.1 §22.3 Target C (No-ML).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.3.

목표:
    SkeletonOutput seed에 대해 *어떤 genre로 각색하면 좋은지* 추천. Phase 3.1
    No-ML baseline — `flesh_baseline.recommend_seed`의 (seed × profile) 점수를
    *seed별로 grouping + ranking + top-K*해 spec §22.3 schema 형태로 출력.

입력:
    - SkeletonOutput v1.1
    - List[GenreProfile]
    - annotation_features_by_seed (선택, Phase 3.0 KEEP feature 평균 등)

출력 schema (§22.3 spec):
    {
      "schema_version": "adaptation_recommendation_v1",
      "source_skeleton_id": "...",
      "recommendations": [
        {
          "source_seed_id": "S01",
          "recommended_modes": [
            {
              "genre_id": "korean_morning_melodrama",
              "score": 0.78,
              "fit_label": "strong_fit",
              "reason": "silence_or_avoidance + relationship_pressure high",
              "mode": "rulebook_only" or "annotation_blended",
            },
            ...
          ]
        }
      ],
      "model": {...},
      "audit": {...},
    }

원칙 (Phase 3.05 정직성):
    - score_breakdown은 *항상* `recommend_seed`에서 채워짐 (rulebook_only 모드도 명시)
    - `mode` 필드로 rulebook-only / annotation_blended 노출
    - 학습 0 / 외부 fetch 0 / raw text 사용 0 (audit_raw_text_used=False)
    - Phase 3.05 review §3 Non-Claims — recommendation은 *후보*이지 truth claim 아님

Target A/B/C 매핑:
    - Target A (Genre Mode Classification): flesh_baseline.run_flesh_baseline (flat list)
    - Target B (Genre Intensity Score):     episode_intensity.score_episode
    - Target C (Adaptation Recommendation): adaptation_recommendation.run_adaptation_recommendation
      ← *이 모듈* (Target A를 seed별 그룹화 + top-K로 재구성)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from engine.observer.flesh_baseline import (
    FleshRecommendation,
    recommend_seed,
)

if TYPE_CHECKING:
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.skeleton_output import SkeletonOutput


ADAPTATION_RECOMMENDATION_VERSION = "adaptation_recommendation_v1"


@dataclass(frozen=True)
class RecommendedMode:
    """단일 (genre × seed) 추천 (top-K 리스트 항목)."""
    genre_id: str
    score: float
    fit_label: str
    reason: str
    mode: str  # "rulebook_only" or "annotation_blended"
    reason_features: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "genre_id": self.genre_id,
            "score": round(self.score, 4),
            "fit_label": self.fit_label,
            "reason": self.reason,
            "mode": self.mode,
            "reason_features": list(self.reason_features),
        }


@dataclass(frozen=True)
class SeedAdaptationRecommendation:
    """단일 seed에 대한 grouped + ranked 추천 (§22.3 spec 형태)."""
    source_seed_id: str
    recommended_modes: tuple[RecommendedMode, ...]

    def to_dict(self) -> dict:
        return {
            "source_seed_id": self.source_seed_id,
            "recommended_modes": [m.to_dict() for m in self.recommended_modes],
        }


@dataclass(frozen=True)
class AdaptationRecommendationOutput:
    """Phase 3.1 §22.3 Target C output (adaptation_recommendation_v1)."""
    schema_version: str
    source_skeleton_id: str
    source_skeleton_version: str
    genre_profiles_used: tuple[str, ...]
    recommendations: tuple[SeedAdaptationRecommendation, ...]
    top_k: int = 3
    model_type: str = "weighted_rule_score"
    model_trained: bool = False
    model_data_source: str = "phase3_pilot"
    audit_raw_text_used: bool = False
    audit_evidence_preserved: bool = True
    calibration_status: str = "uncalibrated_phase3_placeholder"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "source_skeleton_id": self.source_skeleton_id,
            "source_skeleton_version": self.source_skeleton_version,
            "genre_profiles_used": list(self.genre_profiles_used),
            "top_k": self.top_k,
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
            "calibration_status": self.calibration_status,
        }


def _build_reason_string(rec: FleshRecommendation) -> str:
    """reason_features 튜플 → 짧은 자연어 reason 문자열.

    §22.3 spec example: "silence_or_avoidance + relationship_pressure high"
    """
    if not rec.reason_features:
        return "no_specific_signal"
    # 처음 두 요소만 — UI noise 줄이기 위해
    head = list(rec.reason_features[:3])
    return " + ".join(head)


def run_adaptation_recommendation(
    skeleton: SkeletonOutput,
    profiles: list[GenreProfile],
    *,
    skeleton_id: str = "",
    annotation_features_by_seed: dict[str, dict[str, float]] | None = None,
    top_k: int = 3,
    min_score: float = 0.0,
) -> AdaptationRecommendationOutput:
    """SkeletonOutput × profiles → seed별 ranked recommendations (§22.3 spec).

    Args:
        skeleton: UniversalStorySeed v1.1 컨테이너
        profiles: 점수화할 GenreProfile 목록
        skeleton_id: optional override
        annotation_features_by_seed: {seed_id → {feature: score}} — Phase 3.0 결과
        top_k: seed당 추천 모드 수 (default 3)
        min_score: 이 점수 이하 모드는 제외 (default 0.0 = 모두 포함)

    Returns:
        AdaptationRecommendationOutput — schema_version="adaptation_recommendation_v1"
    """
    annotation_features_by_seed = annotation_features_by_seed or {}

    seed_recommendations: list[SeedAdaptationRecommendation] = []
    for seed in skeleton.seeds:
        ann_features = annotation_features_by_seed.get(seed.seed_id)
        # seed × all profiles → flat list of FleshRecommendation
        seed_modes: list[RecommendedMode] = []
        for profile in profiles:
            rec = recommend_seed(seed, profile, annotation_features=ann_features)
            if rec.score < min_score:
                continue
            mode = rec.score_breakdown.get("mode", "rulebook_only")
            seed_modes.append(
                RecommendedMode(
                    genre_id=rec.genre_id,
                    score=rec.score,
                    fit_label=rec.fit_label,
                    reason=_build_reason_string(rec),
                    mode=mode,
                    reason_features=rec.reason_features,
                ),
            )
        # rank by score descending, take top-K
        seed_modes.sort(key=lambda m: m.score, reverse=True)
        ranked = tuple(seed_modes[:top_k])
        seed_recommendations.append(
            SeedAdaptationRecommendation(
                source_seed_id=seed.seed_id,
                recommended_modes=ranked,
            ),
        )

    return AdaptationRecommendationOutput(
        schema_version=ADAPTATION_RECOMMENDATION_VERSION,
        source_skeleton_id=skeleton_id or (
            skeleton.anchor_metadata.anchor_id if skeleton.anchor_metadata else ""
        ),
        source_skeleton_version=skeleton.schema_version,
        genre_profiles_used=tuple(p.genre_id for p in profiles),
        recommendations=tuple(seed_recommendations),
        top_k=top_k,
        model_type="weighted_rule_score",
        model_trained=False,
        model_data_source=(
            profiles[0].data_source if profiles else "rulebook_only"
        ),
        audit_raw_text_used=False,
        audit_evidence_preserved=True,
        calibration_status="uncalibrated_phase3_placeholder",
    )
