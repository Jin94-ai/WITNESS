# WITNESS Rubric Evaluation Report (Phase 3.05)

> Generated: 2026-05-11T12:53:49
> Tool: `scripts/rubric/run_rubric.py`
> Trajectory length: 5 records

## Non-Claims

이 보고서는 신학적/문학적 *진실*을 증명하지 않는다. 
생성된 trajectory가 (1) canon-compatible, (2) causally explainable, 
(3) trait-consistent, (4) non-copy/non-noise인지 *분류*한다.
최종 label은 **discovery candidate class**로 해석.

---

## Discovery Classification

**discovery_class**: `canon_compatible_character_drift`

### Justification

- Step 8: canon-compatible, drift=5.00, novelty=meaningful, character[weak_axes=['identity_retention']], scene_fit=1.00 (min 0.5) → §2 CANON_COMPATIBLE_CHARACTER_DRIFT

---

## 6 Sub-Reports (axis별 독립)

### Character (review §2.3 minimum gate)
- relation_stability: 1.000
- identity_retention: 0.375
- recovery_plausibility: 1.000
- composite (display only): 0.792
- **passed_minimum_signature**: `False`
- weak_axes: ['identity_retention']

### Causal (review §2.5 gate)
- explained_transition_ratio: 1.000
- unexplained_jumps: 0
- smoothness_score: 1.000
- **passed_causal_gate**: `True`

### Novelty (review §2.4 structured difference)
- novelty_band: `meaningful`
- structured_deviation: 0.250
- changed_axes: 없음
- interpretation: 구조적으로 다른 trajectory — discovery 후보 가능

### Canon (review §2.6 hard/soft 분리)
- is_canon_valid (hard_pass): `True`
- hard_violations: 0건
- soft_drift: 5.000
- soft_compatibility_score: 0.500
- is_canon_reproducing: `False`

### Scene Response
- fit_rate: 1.000

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