# WITNESS Rubric Evaluation Report (Phase 3.05)

> Generated: 2026-05-11T12:53:48
> Tool: `scripts/rubric/run_rubric.py`
> Trajectory length: 10 records

## Non-Claims

이 보고서는 신학적/문학적 *진실*을 증명하지 않는다. 
생성된 trajectory가 (1) canon-compatible, (2) causally explainable, 
(3) trait-consistent, (4) non-copy/non-noise인지 *분류*한다.
최종 label은 **discovery candidate class**로 해석.

---

## Discovery Classification

**discovery_class**: `canonical_reproduction`

### Justification

- Step 6: soft_drift=0.00 ≤ reproduction_threshold → §1 CANONICAL_REPRODUCTION

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
- smoothness_score: 0.472
- **passed_causal_gate**: `True`

### Novelty (review §2.4 structured difference)
- novelty_band: `copy`
- structured_deviation: 0.000
- changed_axes: ['action_diversity']
- interpretation: 정경 복사에 가까움 — meaningful difference 없음 (변화 axis: action_diversity)

### Canon (review §2.6 hard/soft 분리)
- is_canon_valid (hard_pass): `True`
- hard_violations: 0건
- soft_drift: 0.000
- soft_compatibility_score: 1.000
- is_canon_reproducing: `True`

### Scene Response
- fit_rate: 1.000

### Context Break
- break_rate: 0.100
- is_context_coherent: `True`

---

## Calibration Status

모든 critic threshold는 **uncalibrated_phase3_placeholder** — Phase 5+ 실측 trajectory로 보정 필요.

## Rule #14 Compliance

- Rubric은 evaluation-only (학습 loss 사용 0)
- scalar 합산 0 (4 critic report independent 유지)
- final label은 candidate class — truth claim 아님