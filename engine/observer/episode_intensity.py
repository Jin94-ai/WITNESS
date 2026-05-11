"""Episode Intensity Score v1 — Phase 3.1 §22.2 Target B.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.2.

Goal:
    Annotation feature vector (per episode) → genre_intensity_score per genre.

    예: korean_melodrama_intensity: 0.78, quiet_drama_intensity: 0.34

원칙:
    - 학습 0 / fine-tuning 0
    - feature_weights는 GenreProfile에서 그대로 사용 (선형 결합)
    - KEEP feature만 사용 (옵션, kept_features 지정 시 필터)
    - 여러 annotator의 score는 산술 평균 후 weight 적용
    - intensity_score 0.0-1.0, fit_label = strong/moderate/weak/no_fit
    - raw text 사용 0 (annotation feature scores만)

입력:
    - feature_matrix rows (record_id, annotator_id, feature, score) — long form
    - List[GenreProfile]
    - kept_features (optional) — None이면 profile.feature_weights.keys() 전부 사용

출력 schema (episode_intensity_v1):
    {
      "schema_version": "episode_intensity_v1",
      "n_records": 10,
      "n_genres": 1,
      "kept_features_used": ["silence_or_avoidance", ...],
      "intensity_records": [
        {
          "record_id": "km_titleA_ep001",
          "genre_id": "korean_morning_melodrama",
          "intensity_score": 0.78,
          "fit_label": "strong_fit",
          "feature_contributions": {
            "silence_or_avoidance": 0.30,
            "cliffhanger_strength": 0.18,
            ...
          },
          "n_annotators_used": 2,
          "feature_means": {...}
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
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from engine.observer.flesh_baseline import _normalize_to_unit, fit_label_for_score
from engine.observer.genre_profile import GenreProfile


EPISODE_INTENSITY_VERSION = "episode_intensity_v1"


# ---------------------------------------------------------------------------
# Aggregation: long-form rows → {record → {feature → mean}}
# ---------------------------------------------------------------------------

def aggregate_features_by_record(
    rows: Iterable[dict],
    *,
    kept_features: Iterable[str] | None = None,
) -> dict[str, tuple[dict[str, float], int]]:
    """Long-form rows → {record_id: ({feature: mean_score}, n_annotators)}.

    rows 항목: {"record_id", "annotator_id", "feature", "score"}.

    kept_features이 주어지면 해당 feature만 통계.
    """
    keep = set(kept_features) if kept_features is not None else None

    bucket: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    annotators: dict[str, set[str]] = defaultdict(set)

    for r in rows:
        rid = r.get("record_id", "")
        feat = r.get("feature", "")
        ann = r.get("annotator_id", "")
        try:
            score = float(r.get("score"))
        except (TypeError, ValueError):
            continue
        if keep is not None and feat not in keep:
            continue
        if not rid or not feat:
            continue
        bucket[rid][feat].append(score)
        annotators[rid].add(ann)

    out: dict[str, tuple[dict[str, float], int]] = {}
    for rid, fmap in bucket.items():
        means = {f: sum(vs) / len(vs) for f, vs in fmap.items() if vs}
        out[rid] = (means, len(annotators[rid]))
    return out


# ---------------------------------------------------------------------------
# Intensity record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EpisodeIntensityRecord:
    """단일 (episode, genre) intensity 결과."""
    record_id: str
    genre_id: str
    intensity_score: float
    fit_label: str
    feature_contributions: dict[str, float]
    feature_means: dict[str, float]
    n_annotators_used: int

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "genre_id": self.genre_id,
            "intensity_score": round(self.intensity_score, 4),
            "fit_label": self.fit_label,
            "feature_contributions": {
                k: round(v, 4) for k, v in self.feature_contributions.items()
            },
            "feature_means": {
                k: round(v, 4) for k, v in self.feature_means.items()
            },
            "n_annotators_used": self.n_annotators_used,
        }


def compute_episode_intensity(
    record_id: str,
    feature_means: dict[str, float],
    n_annotators: int,
    profile: GenreProfile,
) -> EpisodeIntensityRecord:
    """Per-record × profile → EpisodeIntensityRecord.

    intensity_score = sum(profile.feature_weights[f] * normalize(feature_means[f]))
    feature_means에 없는 feature는 contribution 0.
    """
    breakdown: dict[str, float] = {}
    score = 0.0
    for fname, weight in profile.feature_weights.items():
        raw = feature_means.get(fname)
        if raw is None:
            breakdown[fname] = 0.0
            continue
        norm = _normalize_to_unit(float(raw))
        contribution = norm * float(weight)
        breakdown[fname] = contribution
        score += contribution

    score = max(0.0, min(1.0, score))
    return EpisodeIntensityRecord(
        record_id=record_id,
        genre_id=profile.genre_id,
        intensity_score=score,
        fit_label=fit_label_for_score(score),
        feature_contributions=breakdown,
        feature_means=dict(feature_means),
        n_annotators_used=n_annotators,
    )


# ---------------------------------------------------------------------------
# Top-level output
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EpisodeIntensityOutput:
    """Phase 3.1 §22.2 episode_intensity_v1 결과."""
    schema_version: str
    n_records: int
    n_genres: int
    kept_features_used: tuple[str, ...]
    intensity_records: tuple[EpisodeIntensityRecord, ...]
    model_type: str = "weighted_rule_score"
    model_trained: bool = False
    model_data_source: str = "phase3_pilot"
    audit_raw_text_used: bool = False
    audit_evidence_preserved: bool = True

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "n_records": self.n_records,
            "n_genres": self.n_genres,
            "kept_features_used": list(self.kept_features_used),
            "intensity_records": [r.to_dict() for r in self.intensity_records],
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


def run_episode_intensity(
    rows: Iterable[dict],
    profiles: list[GenreProfile],
    *,
    kept_features: Iterable[str] | None = None,
) -> EpisodeIntensityOutput:
    """Long-form rows + profiles → EpisodeIntensityOutput.

    kept_features이 주어지면 해당 feature만 평균/적용. 없으면 profile.feature_weights
    keys 합집합 사용.
    """
    if kept_features is None:
        union: set[str] = set()
        for p in profiles:
            union.update(p.feature_weights.keys())
        keep_list = sorted(union)
    else:
        keep_list = sorted(kept_features)

    aggregated = aggregate_features_by_record(rows, kept_features=keep_list)

    records: list[EpisodeIntensityRecord] = []
    for record_id in sorted(aggregated.keys()):
        means, n_ann = aggregated[record_id]
        for profile in profiles:
            records.append(
                compute_episode_intensity(record_id, means, n_ann, profile),
            )

    data_source = profiles[0].data_source if profiles else "rulebook_only"
    return EpisodeIntensityOutput(
        schema_version=EPISODE_INTENSITY_VERSION,
        n_records=len(aggregated),
        n_genres=len(profiles),
        kept_features_used=tuple(keep_list),
        intensity_records=tuple(records),
        model_type="weighted_rule_score",
        model_trained=False,
        model_data_source=data_source,
        audit_raw_text_used=False,
        audit_evidence_preserved=True,
    )
