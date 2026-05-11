"""LLM prompt templates for Narrative Mode annotation (Phase 2 prep).

Per `docs/witness_narrative_mode_plan.md` §5.3 + `docs/annotation/ANNOTATION_GUIDE.md`.

이 모듈은 *프롬프트 정의*만 한다. 네트워크 호출 0. 실제 LLM API 호출은
별도 스크립트 (scripts/annotation/run_annotation.py — Phase 2 본격 시작 시
구현)에서 이 템플릿을 사용한다.

설계 원칙:
    - Plan §5.5 "사용 전 출처별 ToS 확인" — 이 모듈은 어노테이션 *전에*
      거치는 prep stage이므로 호출 자체가 없다.
    - JSON-only 응답 강제 (자유 텍스트 금지).
    - 0.0 ~ 1.0 scale + anchor 점수를 ANNOTATION_GUIDE.md §2 verbatim 인용.
    - evidence_quote는 줄거리 *원문* 인용 — LLM이 새로 만들어내면 안 됨.
"""
from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 7 features (Plan §2.3)
# ---------------------------------------------------------------------------

ANNOTATION_FEATURES: tuple[str, ...] = (
    "conflict_intensity_peak",
    "revelation_density",
    "coincidence_frequency",
    "relationship_polarization",
    "new_conflict_introduction_rate",
    "dangling_thread_generation",
    "cliffhanger_intensity",
)


# Phase 2.5 (2026-05-09): conflict_amplification_rate, resolution_to_dangling_ratio
# 두 feature는 회차 단위 측정 불가능으로 판단되어 deprecated. 새 이름 매핑.
DEPRECATED_FEATURE_RENAMES: dict[str, str] = {
    "conflict_amplification_rate": "conflict_intensity_peak",
    "resolution_to_dangling_ratio": "dangling_thread_generation",
}

# 0~5 레벨 / 5로 정규화되는 features. 이들은 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 중
# 하나여야 (또는 작은 epsilon 안에서) — 자유 0.0-1.0 float가 아님.
LEVELED_FEATURES: tuple[str, ...] = (
    "conflict_intensity_peak",
    "dangling_thread_generation",
)
LEVELED_FEATURE_MAX_LEVEL: int = 5
LEVELED_FEATURE_TOLERANCE: float = 0.05  # 0.2 단위에 ±0.05 허용 (annotator 변동)


# ---------------------------------------------------------------------------
# Anchor scores (per ANNOTATION_GUIDE.md §2.1-§2.7)
#
# 모든 feature는 0.0~1.0 float로 저장되지만, 두 features
# (conflict_intensity_peak, dangling_thread_generation)는 0~5 정수 레벨에서
# 어노테이트한 후 level/5로 정규화한다 (0.0, 0.2, 0.4, 0.6, 0.8, 1.0).
# ---------------------------------------------------------------------------

_FEATURE_ANCHORS: dict[str, str] = {
    "conflict_intensity_peak": (
        "(0~5 레벨 / 5로 정규화) "
        "0=갈등 거의 없음 / 1=약한 긴장·암시 / 2=명확한 갈등 / "
        "3=여러 인물·관계로 확산 / 4=공개 충돌·폭로·파탄 직전 / "
        "5=회차 중심이 강한 충돌·폭로·파국"
    ),
    "revelation_density": (
        "0.0=폭로 0건 / 0.2=1건 작은 / 0.5=1건 큰 또는 2-3건 중간 / "
        "0.8=2건 이상 큰 폭로 / 1.0=3건 이상 큰 폭로"
    ),
    "coincidence_frequency": (
        "0.0=우연 0건 / 0.3=1건 작은 / 0.5=1건 결정적 / "
        "0.8=2건 이상 결정적 / 1.0=3건 이상 결정적"
    ),
    "relationship_polarization": (
        "0.0=모든 관계 그라데이션 / 0.3=일부 극단 / 0.5=절반 극단 / "
        "0.8=거의 전부 극단 / 1.0=모든 주요 관계 극단, 중간 0"
    ),
    "new_conflict_introduction_rate": (
        "0.0=새 갈등 0 / 0.3=1건 / 0.5=2건 / 0.8=3건 이상 / 1.0=4건 이상"
    ),
    "dangling_thread_generation": (
        "(0~5 레벨 / 5로 정규화) "
        "0=미해결 0건 / 1=약한 암시 1개 / 2=분명한 미해결 1건 / "
        "3=미해결 갈등 2건 이상 / 4=주요 관계·비밀이 다음 회차로 강하게 넘어감 / "
        "5=회차 말미가 거의 클리프행어 중심"
    ),
    "cliffhanger_intensity": (
        "0.0=깔끔히 끝남 / 0.3=약한 미해결 / 0.5=중간 / "
        "0.8=강한 cliffhanger / 1.0=극단적 cliffhanger"
    ),
}


def normalize_level_to_unit(level: int, max_level: int = 5) -> float:
    """0~max_level 정수 레벨을 0.0~1.0 float로 정규화.

    Phase 2.5 도입: conflict_intensity_peak / dangling_thread_generation가
    0-5 레벨로 정의되었으나 저장 형식은 0.0-1.0 통일.
    """
    if max_level <= 0:
        return 0.0
    return max(0.0, min(1.0, level / max_level))


def is_valid_leveled_value(value: float) -> bool:
    """0.0, 0.2, 0.4, 0.6, 0.8, 1.0 중 하나에 ±LEVELED_FEATURE_TOLERANCE 안인가."""
    if not 0.0 <= value <= 1.0:
        return False
    valid_levels = [n / LEVELED_FEATURE_MAX_LEVEL for n in range(LEVELED_FEATURE_MAX_LEVEL + 1)]
    return any(abs(value - v) <= LEVELED_FEATURE_TOLERANCE for v in valid_levels)


def rename_deprecated_features(features: dict) -> dict:
    """기존 feature 이름을 새 이름으로 변환. 기존 어노테이션 마이그레이션용."""
    out: dict = {}
    for k, v in features.items():
        out[DEPRECATED_FEATURE_RENAMES.get(k, k)] = v
    return out


def migrate_deprecated_annotation(d: dict) -> dict:
    """Phase 2.5 cycle 6: 기존 v1 어노테이션의 features + evidence_quotes
    feature 필드를 새 이름으로 마이그레이션. 다른 필드는 그대로 보존.

    매핑:
        conflict_amplification_rate → conflict_intensity_peak
        resolution_to_dangling_ratio → dangling_thread_generation

    원본 dict는 수정하지 않음 (shallow copy).
    """
    out = dict(d)
    feats = d.get("features")
    if isinstance(feats, dict):
        out["features"] = rename_deprecated_features(feats)
    quotes = d.get("evidence_quotes")
    if isinstance(quotes, list):
        new_quotes = []
        for q in quotes:
            if isinstance(q, dict) and "feature" in q:
                fname = q["feature"]
                new_q = dict(q)
                new_q["feature"] = DEPRECATED_FEATURE_RENAMES.get(fname, fname)
                new_quotes.append(new_q)
            else:
                new_quotes.append(q)
        out["evidence_quotes"] = new_quotes
    return out


# ---------------------------------------------------------------------------
# System prompt (LLM-agnostic; per-LLM 변형은 별도)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_KO = """당신은 한국어 회차별 줄거리에서 *Narrative Mode 정량 특성*을 추출하는 어노테이터입니다.

규칙:
1. 응답은 JSON only. 자유 텍스트 답변 금지.
2. 모든 점수는 0.0 ~ 1.0 사이 실수.
3. evidence_quote는 *줄거리 원문에서 직접 인용*. 새로 만들어내면 안 됨.
4. 줄거리가 모호하면 confidence를 낮추세요 (0.0 ~ 1.0).
5. 영어가 아닌 *한국어 줄거리*임을 인지하세요.
"""


def build_user_prompt_ko(synopsis_text_ko: str, episode_no: int, title_ko: str) -> str:
    """LLM에 보낼 user prompt (한국어). LLM-agnostic."""
    feature_lines = "\n".join(
        f"  - **{name}**: {_FEATURE_ANCHORS[name]}"
        for name in ANNOTATION_FEATURES
    )
    schema_example = """{
  "schema_version": "annotation_v1",
  "title_id": "...",
  "episode_no": 0,
  "annotator_id": "<your model name>",
  "annotated_at_iso": "<ISO-8601 UTC>",
  "features": {
    "conflict_intensity_peak": 0.0,
    "revelation_density": 0.0,
    "coincidence_frequency": 0.0,
    "relationship_polarization": 0.0,
    "new_conflict_introduction_rate": 0.0,
    "dangling_thread_generation": 0.0,
    "cliffhanger_intensity": 0.0
  },
  "evidence_quotes": [
    {"feature": "<feature name>", "quote_ko": "<줄거리 원문 인용>"}
  ],
  "confidence": 0.0,
  "notes": []
}"""
    return f"""# 회차 줄거리 어노테이션

작품: **{title_ko}** / 회차 #{episode_no}

## 줄거리 (한국어)

{synopsis_text_ko}

## 측정할 7 features (각 0.0 ~ 1.0)

{feature_lines}

## 출력 형식 (JSON only)

```json
{schema_example}
```

위 형식 그대로 JSON만 출력. 추가 설명 / 자유 텍스트 금지.
"""


# ---------------------------------------------------------------------------
# Annotation result schema (validation only — synthesis logic is separate)
# ---------------------------------------------------------------------------

ANNOTATION_SCHEMA_VERSION = "annotation_v1"

REQUIRED_ANNOTATION_FIELDS: tuple[str, ...] = (
    "schema_version", "title_id", "episode_no", "annotator_id",
    "annotated_at_iso", "features", "confidence",
)

REQUIRED_ANNOTATION_FEATURES: tuple[str, ...] = ANNOTATION_FEATURES


def validate_annotation_dict(d: dict, *, strict_levels: bool = False) -> list[str]:
    """Return list of validation errors (empty == valid).

    Phase 2.5 (Cycle 4): strict_levels=True 일 때 conflict_intensity_peak /
    dangling_thread_generation 가 0/0.2/0.4/0.6/0.8/1.0 (±0.05) 중 하나여야.
    기본은 backward-compatible (0.0-1.0 자유 float).
    """
    errs: list[str] = []
    for f in REQUIRED_ANNOTATION_FIELDS:
        if f not in d:
            errs.append(f"missing field: {f}")
    if d.get("schema_version") and d["schema_version"] != ANNOTATION_SCHEMA_VERSION:
        errs.append(
            f"schema_version mismatch: got {d['schema_version']!r}, "
            f"expected {ANNOTATION_SCHEMA_VERSION!r}"
        )
    features = d.get("features", {})
    if not isinstance(features, dict):
        errs.append("features must be a dict")
    else:
        for fname in REQUIRED_ANNOTATION_FEATURES:
            if fname not in features:
                errs.append(f"missing feature: {fname}")
                continue
            v = features[fname]
            if not isinstance(v, (int, float)):
                errs.append(f"feature {fname} must be numeric, got {type(v).__name__}")
                continue
            fv = float(v)
            if not (0.0 <= fv <= 1.0):
                errs.append(f"feature {fname} out of range [0.0, 1.0]: {v}")
                continue
            if (strict_levels and fname in LEVELED_FEATURES
                    and not is_valid_leveled_value(fv)):
                errs.append(
                    f"feature {fname} is leveled (0~{LEVELED_FEATURE_MAX_LEVEL}); "
                    f"value {v} not within {LEVELED_FEATURE_TOLERANCE} of any "
                    "valid level (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)"
                )
    conf = d.get("confidence", -1)
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        errs.append(f"confidence must be in [0.0, 1.0], got {conf!r}")
    return errs


# ---------------------------------------------------------------------------
# Evidence quote validator — LLM 환각 검사
#
# Per `docs/annotation/ANNOTATION_GUIDE.md` §3.2:
#     "evidence_quote는 줄거리 원문에서 직접 인용 — LLM이 새로 만들어내면 안 됨."
#
# 이 검증기는 어노테이션의 evidence_quotes 각 quote_ko가 *원본 줄거리* 안에
# substring으로 실제 등장하는지 검사한다. 매칭 안 되면 LLM 환각으로 의심.
#
# 비교 옵션:
#   strict_substring: 원문에 그대로 등장 (기본)
#   normalized:       공백 정규화 후 (앞뒤 공백 / 연속 공백 차이는 허용)
# ---------------------------------------------------------------------------

import re as _re_evidence


def _normalize_for_match(text: str) -> str:
    """공백 정규화: 연속 공백 → 단일 공백, 앞뒤 trim."""
    return _re_evidence.sub(r"\s+", " ", text or "").strip()


def validate_evidence_quotes(
    annotation: dict,
    synopsis_text: str,
    *,
    strategy: str = "normalized",
) -> list[str]:
    """LLM이 만든 evidence quote가 원본 줄거리에 실제 있는지 검사.

    Args:
        annotation: validate_annotation_dict가 통과한 annotation dict.
        synopsis_text: 원본 회차 줄거리 (synopsis_text_ko).
        strategy: 'strict_substring' 또는 'normalized'.

    Returns:
        Empty list if all quotes verified. Otherwise list of error messages
        — 각 환각 의심 quote에 대한 진단.
    """
    errs: list[str] = []
    quotes = annotation.get("evidence_quotes", [])
    if not isinstance(quotes, list):
        errs.append("evidence_quotes must be a list")
        return errs

    if strategy == "normalized":
        haystack = _normalize_for_match(synopsis_text)
    else:
        haystack = synopsis_text or ""

    for i, q in enumerate(quotes):
        if not isinstance(q, dict):
            errs.append(f"evidence_quotes[{i}] must be a dict")
            continue
        qtext = q.get("quote_ko", "")
        if not qtext:
            errs.append(f"evidence_quotes[{i}].quote_ko is empty")
            continue
        needle = (
            _normalize_for_match(qtext) if strategy == "normalized" else qtext
        )
        if needle not in haystack:
            feat = q.get("feature", "?")
            errs.append(
                f"evidence_quotes[{i}] (feature={feat!r}) not found in synopsis "
                f"(possible LLM hallucination): {qtext!r}"
            )
    return errs


def hallucination_rate(
    annotation: dict, synopsis_text: str,
) -> float:
    """Fraction of evidence quotes that are NOT verifiable in the synopsis.

    0.0 = all quotes verified, 1.0 = all hallucinated. Useful as a
    secondary confidence signal.
    """
    quotes = annotation.get("evidence_quotes", [])
    if not quotes:
        return 0.0
    errs = validate_evidence_quotes(annotation, synopsis_text)
    # 위 errs 중 'not found'만 카운트 (다른 schema 에러는 제외)
    halluc = sum(1 for e in errs if "not found in synopsis" in e)
    return halluc / max(1, len(quotes))


# ---------------------------------------------------------------------------
# Inter-annotator correlation — LLM 간 일치도 (Plan §7.2 + ANNOTATION_GUIDE §3.4)
#
# 여러 어노테이터의 결과가 *같은 회차*에서 얼마나 상관 있는지 측정. 어노테이션
# 가이드의 신뢰도 지표 (kappa / Pearson)에서 *연속값 features*에 적합한
# Pearson r을 사용 (kappa는 categorical용).
#
# Plan §3.4: "kappa ≥ 0.6 또는 r ≥ 0.7 → 신뢰 가능"
# ---------------------------------------------------------------------------

import math as _math


def _pearson_r(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation coefficient. NaN-safe (returns 0.0 for degenerate)."""
    n = len(xs)
    if n != len(ys) or n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = _math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = _math.sqrt(sum((y - my) ** 2 for y in ys))
    den = sx * sy
    if den == 0:
        return 0.0
    return num / den


def inter_annotator_correlation(
    annotations_per_episode: list[list[dict]],
) -> dict[str, float]:
    """Compute average pairwise Pearson r across annotators, per feature.

    Args:
        annotations_per_episode: List where each element is a list of K
            annotations from K different annotators *for the same episode*.
            Multiple episodes can be passed — each episode's annotations
            contribute one paired-vector per (annotator-i, annotator-j).

    Returns:
        dict mapping feature_name → average Pearson r across all annotator
        pairs and episodes. Returns 0.0 for features where no valid pair
        exists.

    Example:
        >>> # 3 episodes × 3 annotators
        >>> result = inter_annotator_correlation([
        ...     [a1_ep1, a2_ep1, a3_ep1],
        ...     [a1_ep2, a2_ep2, a3_ep2],
        ...     [a1_ep3, a2_ep3, a3_ep3],
        ... ])
        >>> # result["revelation_density"] = mean r across (a1,a2), (a1,a3), (a2,a3)
        >>> #                                  pairs and 3 episodes
    """
    out: dict[str, float] = {}

    # For each annotator pair, collect (feat_value_i, feat_value_j) across
    # episodes, then compute r per feature.
    if not annotations_per_episode:
        return {f: 0.0 for f in ANNOTATION_FEATURES}

    n_annotators = len(annotations_per_episode[0])
    if n_annotators < 2:
        return {f: 0.0 for f in ANNOTATION_FEATURES}

    for feature in ANNOTATION_FEATURES:
        rs: list[float] = []
        for i in range(n_annotators):
            for j in range(i + 1, n_annotators):
                xs: list[float] = []
                ys: list[float] = []
                for ep_anns in annotations_per_episode:
                    if len(ep_anns) <= max(i, j):
                        continue
                    fi = ep_anns[i].get("features", {}).get(feature)
                    fj = ep_anns[j].get("features", {}).get(feature)
                    if isinstance(fi, (int, float)) and isinstance(fj, (int, float)):
                        xs.append(float(fi))
                        ys.append(float(fj))
                if len(xs) >= 2:
                    rs.append(_pearson_r(xs, ys))
        out[feature] = sum(rs) / len(rs) if rs else 0.0

    return out


def reliability_grade(correlation: float) -> str:
    """Plan §3.4 기준: r ≥ 0.7 → 신뢰 가능, 그 외 → 가이드 개선 필요."""
    if correlation >= 0.7:
        return "reliable"
    if correlation >= 0.5:
        return "marginal"
    return "low_reliability"


# ---------------------------------------------------------------------------
# Synthesis (multi-AI → single result, no network)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SynthesizedAnnotation:
    title_id: str
    episode_no: int
    features: dict[str, float]
    confidence: float
    contributing_annotators: tuple[str, ...]
    evidence_quotes: tuple[dict, ...]


def synthesize_annotations(annotations: list[dict]) -> SynthesizedAnnotation:
    """Combine multiple LLM annotations into one (per ANNOTATION_GUIDE §3.5).

    - features: arithmetic mean across annotators
    - confidence: 1 - variance proxy (if all agree, confidence high)
    - evidence_quotes: union (preserved with source annotator_id)
    """
    if not annotations:
        raise ValueError("synthesize_annotations: empty list")
    title_id = annotations[0].get("title_id", "")
    episode_no = int(annotations[0].get("episode_no", 0))

    feature_values: dict[str, list[float]] = {f: [] for f in ANNOTATION_FEATURES}
    quotes: list[dict] = []
    annotators: list[str] = []
    for a in annotations:
        annotators.append(a.get("annotator_id", "?"))
        feats = a.get("features", {})
        for f in ANNOTATION_FEATURES:
            v = feats.get(f)
            if isinstance(v, (int, float)):
                feature_values[f].append(float(v))
        for q in a.get("evidence_quotes", []):
            quotes.append({**q, "source_annotator_id": a.get("annotator_id", "?")})

    means: dict[str, float] = {}
    spreads: list[float] = []
    for f, vs in feature_values.items():
        if vs:
            mean = sum(vs) / len(vs)
            means[f] = round(mean, 4)
            if len(vs) > 1:
                # max - min as a simple spread proxy
                spreads.append(max(vs) - min(vs))
        else:
            means[f] = 0.0

    # confidence: 1 - average spread (clamped). Low spread → high confidence.
    if spreads:
        avg_spread = sum(spreads) / len(spreads)
        confidence = max(0.0, min(1.0, 1.0 - avg_spread))
    else:
        confidence = 0.0  # only one annotator → cannot estimate inter-annotator agreement

    return SynthesizedAnnotation(
        title_id=title_id,
        episode_no=episode_no,
        features=means,
        confidence=round(confidence, 4),
        contributing_annotators=tuple(annotators),
        evidence_quotes=tuple(quotes),
    )
