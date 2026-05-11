# WITNESS Rubric Evaluation Report (Phase 3.05)

> Generated: 2026-05-11T12:53:49
> Tool: `scripts/rubric/run_rubric.py`
> Trajectory length: 3 records

## Non-Claims

이 보고서는 신학적/문학적 *진실*을 증명하지 않는다. 
생성된 trajectory가 (1) canon-compatible, (2) causally explainable, 
(3) trait-consistent, (4) non-copy/non-noise인지 *분류*한다.
최종 label은 **discovery candidate class**로 해석.

---

## Discovery Classification

**discovery_class**: `invalid_canon_violation`

### Justification

- Step 2: 2 hard violation(s) → INVALID_CANON_VIOLATION

---

## 6 Sub-Reports (axis별 독립)

### Character (review §2.3 minimum gate)
- relation_stability: 1.000
- identity_retention: 1.000
- recovery_plausibility: 1.000
- composite (display only): 1.000
- **passed_minimum_signature**: `True`
- weak_axes: 없음

### Causal (review §2.5 gate)
- explained_transition_ratio: 1.000
- unexplained_jumps: 0
- smoothness_score: 0.775
- **passed_causal_gate**: `True`

### Novelty (review §2.4 structured difference)
- novelty_band: `meaningful`
- structured_deviation: 0.250
- changed_axes: ['action_diversity']
- interpretation: 구조적으로 다른 trajectory — discovery 후보 가능 (변화 axis: action_diversity)

### Canon (review §2.6 hard/soft 분리)
- is_canon_valid (hard_pass): `False`
- hard_violations: 2건
- soft_drift: 6.000
- soft_compatibility_score: 0.400
- is_canon_reproducing: `False`

### Scene Response
- fit_rate: 0.500

### Context Break
- break_rate: 0.000
- is_context_coherent: `True`

---

## Calibration Status

모든 critic threshold는 **uncalibrated_phase3_placeholder** — Phase 5+ 실측 trajectory로 보정 필요.

## Rule #14 Compliance

- Rubric은 evaluation-only (학습 loss 사용 0)
- scalar 합산 0 (4 critic report independent 유지)
- final label은 candidate class — truth claim 아님