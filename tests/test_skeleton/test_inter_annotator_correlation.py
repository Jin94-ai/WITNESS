"""Tests for inter-annotator correlation (Plan §7.2 + ANNOTATION_GUIDE §3.4).

Per `docs/witness_narrative_mode_plan.md` §7.2:
    "어노테이션 신뢰도 (LLM 간 일치도, 사람과의 일치도)"

Per `docs/annotation/ANNOTATION_GUIDE.md` §3.4:
    "kappa ≥ 0.6 또는 r ≥ 0.7 → 신뢰 가능"

연속값 features에는 Pearson r이 적합 (kappa는 categorical용).
"""
from __future__ import annotations

import pytest


ANNOTATION_FEATURES = (
    "conflict_intensity_peak",
    "revelation_density",
    "coincidence_frequency",
    "relationship_polarization",
    "new_conflict_introduction_rate",
    "dangling_thread_generation",
    "cliffhanger_intensity",
)


def _make_annotation(annotator_id: str, features: dict[str, float]) -> dict:
    """Make a minimal annotation dict for testing."""
    return {
        "schema_version": "annotation_v1",
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": annotator_id,
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": features,
        "confidence": 0.7,
    }


# ============================================================================
# 1. _pearson_r helper
# ============================================================================

def test_pearson_r_perfect_positive():
    from scripts.annotation.prompt_templates import _pearson_r
    r = _pearson_r([0.1, 0.5, 0.9], [0.2, 0.6, 1.0])
    assert abs(r - 1.0) < 1e-6


def test_pearson_r_perfect_negative():
    from scripts.annotation.prompt_templates import _pearson_r
    r = _pearson_r([0.1, 0.5, 0.9], [0.9, 0.5, 0.1])
    assert abs(r - (-1.0)) < 1e-6


def test_pearson_r_uncorrelated_zero():
    from scripts.annotation.prompt_templates import _pearson_r
    # 같은 값 반복 (분산 0) → r = 0
    r = _pearson_r([0.5, 0.5, 0.5], [0.1, 0.7, 0.3])
    assert r == 0.0


def test_pearson_r_short_input():
    from scripts.annotation.prompt_templates import _pearson_r
    assert _pearson_r([0.5], [0.5]) == 0.0
    assert _pearson_r([], []) == 0.0


def test_pearson_r_mismatched_lengths():
    from scripts.annotation.prompt_templates import _pearson_r
    assert _pearson_r([0.1, 0.2], [0.5]) == 0.0


# ============================================================================
# 2. inter_annotator_correlation
# ============================================================================

def test_correlation_perfect_agreement_returns_one():
    """3 annotators agree perfectly across 3 episodes → r = 1.0 per feature."""
    from scripts.annotation.prompt_templates import inter_annotator_correlation

    eps = []
    for ep_no, base in enumerate([0.2, 0.5, 0.8], start=1):
        feats = {f: base for f in ANNOTATION_FEATURES}
        eps.append([
            _make_annotation("claude", feats),
            _make_annotation("gpt", feats),
            _make_annotation("gemini", feats),
        ])
    result = inter_annotator_correlation(eps)
    for f in ANNOTATION_FEATURES:
        assert f in result
        # 모두 같은 값 → r = 1.0 (완벽 일치)
        assert abs(result[f] - 1.0) < 1e-6, (
            f"feature {f}: expected r=1.0, got {result[f]}"
        )


def test_correlation_perfect_disagreement_returns_negative():
    """Annotator pair with opposite ratings → r < 0."""
    from scripts.annotation.prompt_templates import inter_annotator_correlation

    eps = []
    for ep_no, (a_val, b_val) in enumerate(
        [(0.2, 0.8), (0.5, 0.5), (0.8, 0.2)], start=1,
    ):
        eps.append([
            _make_annotation("claude", {f: a_val for f in ANNOTATION_FEATURES}),
            _make_annotation("gpt", {f: b_val for f in ANNOTATION_FEATURES}),
        ])
    result = inter_annotator_correlation(eps)
    for f in ANNOTATION_FEATURES:
        assert result[f] < 0, f"feature {f}: expected negative r, got {result[f]}"


def test_correlation_handles_partial_agreement():
    """Partial agreement → 0 < r < 1."""
    from scripts.annotation.prompt_templates import inter_annotator_correlation

    # claude: 0.2, 0.5, 0.8
    # gpt:    0.3, 0.5, 0.7  (high correlation but not perfect)
    eps = [
        [_make_annotation("claude", {f: a for f in ANNOTATION_FEATURES}),
         _make_annotation("gpt", {f: b for f in ANNOTATION_FEATURES})]
        for a, b in [(0.2, 0.3), (0.5, 0.5), (0.8, 0.7)]
    ]
    result = inter_annotator_correlation(eps)
    for f in ANNOTATION_FEATURES:
        assert 0.5 < result[f] < 1.0


def test_correlation_empty_input():
    from scripts.annotation.prompt_templates import inter_annotator_correlation
    result = inter_annotator_correlation([])
    for f in ANNOTATION_FEATURES:
        assert result[f] == 0.0


def test_correlation_single_annotator_returns_zero():
    """Cannot measure inter-annotator agreement with 1 annotator."""
    from scripts.annotation.prompt_templates import inter_annotator_correlation
    eps = [
        [_make_annotation("claude", {f: 0.5 for f in ANNOTATION_FEATURES})]
        for _ in range(3)
    ]
    result = inter_annotator_correlation(eps)
    for f in ANNOTATION_FEATURES:
        assert result[f] == 0.0


def test_correlation_per_feature_independent():
    """Different features can have different correlations."""
    from scripts.annotation.prompt_templates import inter_annotator_correlation

    # claude vs gpt:
    # - revelation_density agrees perfectly
    # - cliffhanger_intensity disagrees
    eps = []
    for ep_no, (rd_a, rd_b, ci_a, ci_b) in enumerate([
        (0.2, 0.2, 0.2, 0.8),
        (0.5, 0.5, 0.5, 0.5),
        (0.8, 0.8, 0.8, 0.2),
    ], start=1):
        feats_a = {f: 0.5 for f in ANNOTATION_FEATURES}
        feats_a["revelation_density"] = rd_a
        feats_a["cliffhanger_intensity"] = ci_a
        feats_b = {f: 0.5 for f in ANNOTATION_FEATURES}
        feats_b["revelation_density"] = rd_b
        feats_b["cliffhanger_intensity"] = ci_b
        eps.append([
            _make_annotation("claude", feats_a),
            _make_annotation("gpt", feats_b),
        ])

    result = inter_annotator_correlation(eps)
    # revelation_density: perfect agreement
    assert abs(result["revelation_density"] - 1.0) < 1e-6
    # cliffhanger_intensity: perfect disagreement
    assert abs(result["cliffhanger_intensity"] - (-1.0)) < 1e-6
    # 다른 features: 모두 0.5라 분산 0 → r = 0
    assert result["coincidence_frequency"] == 0.0


# ============================================================================
# 3. reliability_grade (Plan §3.4 thresholds)
# ============================================================================

def test_reliability_grade_thresholds():
    from scripts.annotation.prompt_templates import reliability_grade
    assert reliability_grade(0.95) == "reliable"
    assert reliability_grade(0.7) == "reliable"
    assert reliability_grade(0.69) == "marginal"
    assert reliability_grade(0.5) == "marginal"
    assert reliability_grade(0.49) == "low_reliability"
    assert reliability_grade(0.0) == "low_reliability"
    assert reliability_grade(-0.5) == "low_reliability"
