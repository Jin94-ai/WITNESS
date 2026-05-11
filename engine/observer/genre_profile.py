"""GenreProfile v1 — Phase 3.1 ML/Flesh Baseline 산출물.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §26.

GenreProfile는 *데이터에서 검증된 feature weights + compatibility*를 정리한
genre 별 프로파일이다. Phase 3.0 reliability report의 KEEP feature를 사용해
구축된다. Phase 3.1 weighted score baseline (`flesh_baseline.py`)이 이 프로파일을
입력으로 받아 SkeletonOutput seed가 어떤 장르 flesh에 잘 맞는지 점수화한다.

Schema:
    {
      "schema_version": "genre_profile_v1",
      "genre_id": "korean_morning_melodrama",
      "feature_weights": {
        "conflict_intensity_peak": 0.25,
        "dangling_thread_generation": 0.25,
        "relationship_pressure": 0.20,
        "hidden_information_pressure": 0.15,
        "cliffhanger_strength": 0.15
      },
      "compatible_conflict_axes": [...],
      "compatible_pressures": [...],
      "data_source": "phase3_pilot",
      "n_records_basis": 10
    }

원칙:
    - feature_weights sum = 1.0 (또는 1.0에 가깝게 정규화)
    - 모든 feature는 Phase 3.0 reliability report에서 KEEP 판정된 것
    - rulebook의 conflict_amplifiers + pressure_mappings에서 compatibility 추론
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


GENRE_PROFILE_VERSION = "genre_profile_v1"


@dataclass(frozen=True)
class GenreProfile:
    """Phase 3.1 §26 GenreProfile v1."""
    schema_version: str
    genre_id: str
    feature_weights: dict[str, float]
    compatible_conflict_axes: tuple[str, ...]
    compatible_pressures: tuple[str, ...]
    data_source: str = "phase3_pilot"   # "phase3_pilot" | "rulebook_only" | "manual"
    n_records_basis: int = 0            # 프로파일을 만든 데이터 수
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "genre_id": self.genre_id,
            "feature_weights": dict(self.feature_weights),
            "compatible_conflict_axes": list(self.compatible_conflict_axes),
            "compatible_pressures": list(self.compatible_pressures),
            "data_source": self.data_source,
            "n_records_basis": self.n_records_basis,
            "notes": list(self.notes),
        }

    @staticmethod
    def from_dict(d: dict) -> "GenreProfile":
        return GenreProfile(
            schema_version=d.get("schema_version", GENRE_PROFILE_VERSION),
            genre_id=d["genre_id"],
            feature_weights=dict(d.get("feature_weights", {})),
            compatible_conflict_axes=tuple(d.get("compatible_conflict_axes", [])),
            compatible_pressures=tuple(d.get("compatible_pressures", [])),
            data_source=d.get("data_source", "phase3_pilot"),
            n_records_basis=int(d.get("n_records_basis", 0)),
            notes=tuple(d.get("notes", [])),
        )


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """가중치 합을 1.0으로 정규화."""
    total = sum(weights.values())
    if total <= 0:
        return dict(weights)
    return {k: round(v / total, 4) for k, v in weights.items()}


def build_profile_from_rulebook(
    *,
    genre_id: str,
    rulebook,                    # GenreRulebook
    keep_features: list[str],
    feature_weights: dict[str, float] | None = None,
    n_records_basis: int = 0,
    data_source: str = "phase3_pilot",
) -> GenreProfile:
    """Rulebook + KEEP feature → GenreProfile.

    rulebook에서 다음을 추출:
        - compatible_conflict_axes: amplifier.applies_to union
        - compatible_pressures: pressure_mappings.keys()
    """
    # KEEP feature 외의 weight는 0으로
    if feature_weights is None:
        # uniform 분포 over KEEP features
        if not keep_features:
            weights: dict[str, float] = {}
        else:
            equal_w = 1.0 / len(keep_features)
            weights = {f: equal_w for f in keep_features}
    else:
        # KEEP feature만 유지
        weights = {
            f: float(w) for f, w in feature_weights.items() if f in keep_features
        }
        weights = normalize_weights(weights)

    # rulebook에서 compatible axes / pressures
    axes = []
    seen_axes = set()
    for amp in rulebook.conflict_amplifiers:
        for ax in amp.applies_to:
            if ax not in seen_axes:
                seen_axes.add(ax)
                axes.append(ax)
    pressures = list(rulebook.pressure_mappings.keys())

    return GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id=genre_id,
        feature_weights=weights,
        compatible_conflict_axes=tuple(axes),
        compatible_pressures=tuple(pressures),
        data_source=data_source,
        n_records_basis=n_records_basis,
        notes=(),
    )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def save_profiles(profiles: list[GenreProfile], path: Path) -> None:
    """Profile list를 JSON으로 저장 (data/annotation/phase3_pilot/genre_profiles.json)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "genre_profiles_index_v1",
        "profiles": [p.to_dict() for p in profiles],
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8",
    )


def load_profiles(path: Path) -> list[GenreProfile]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [GenreProfile.from_dict(d) for d in raw]
    if isinstance(raw, dict) and "profiles" in raw:
        return [GenreProfile.from_dict(d) for d in raw["profiles"]]
    return []
