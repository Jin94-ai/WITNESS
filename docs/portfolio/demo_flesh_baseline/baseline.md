# Phase 3.1 Flesh Baseline — Recommendations

> **📐 Prep mode (rulebook-only)** — 현재 점수는 *실제 annotation 기반 추천이 아니라* rulebook compatibility (seed의 conflict_axis / dominant_pressures가 장르 rulebook과 호환되는 정도)다. Phase 3.0 pilot 데이터가 들어와야 annotation component가 추가되어 *data-backed* recommendation이 된다. 현재 fit_label은 **compatibility match**로 해석해야 안전하다.

> **schema**: `flesh_baseline_output_v1`  
> **source skeleton**: `peter_scarcity_baseline` (skeleton_output_v1)  
> **profiles**: korean_morning_melodrama, japanese_quiet_drama  
> **model**: weighted_rule_score (trained=False, data_source=rulebook_only)
> **audit**: raw_text_used=False / evidence_preserved=True

---

## Seed별 Top Recommendation

### S01 [main_arc] (`loyalty_vs_survival`)

- **추천 장르**: `korean_morning_melodrama`
- **점수**: 1.000 (strong_fit (rulebook-only))
- **score_breakdown**: mode=`rulebook_only` · compatibility=1.000 (axis=0.50, pressure=0.50) · annotation=not available yet
- **이유**: conflict_axis:loyalty_vs_survival, pressure:authority_vigilance
- **추천 어댑터**: `rulebook_v2_8`
- **다른 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only))

### S02 [supporting_uncertainty] (`uncertainty_vs_commitment`)

- **추천 장르**: `korean_morning_melodrama`
- **점수**: 1.000 (strong_fit (rulebook-only))
- **score_breakdown**: mode=`rulebook_only` · compatibility=1.000 (axis=0.50, pressure=0.50) · annotation=not available yet
- **이유**: conflict_axis:uncertainty_vs_commitment, pressure:confusion
- **추천 어댑터**: `rulebook_v2_8`
- **다른 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only))

### S03 [witness_arc] (`uncertainty_vs_commitment`)

- **추천 장르**: `korean_morning_melodrama`
- **점수**: 1.000 (strong_fit (rulebook-only))
- **score_breakdown**: mode=`rulebook_only` · compatibility=1.000 (axis=0.50, pressure=0.50) · annotation=not available yet
- **이유**: conflict_axis:uncertainty_vs_commitment, pressure:confusion
- **추천 어댑터**: `rulebook_v2_8`
- **다른 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only))

### S04 [delayed_response_arc] (`uncertainty_vs_commitment`)

- **추천 장르**: `korean_morning_melodrama`
- **점수**: 1.000 (strong_fit (rulebook-only))
- **score_breakdown**: mode=`rulebook_only` · compatibility=1.000 (axis=0.50, pressure=0.50) · annotation=not available yet
- **이유**: conflict_axis:uncertainty_vs_commitment, pressure:confusion
- **추천 어댑터**: `rulebook_v2_8`
- **다른 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only))

---

## 전체 Recommendation Matrix

| seed | genre | score | fit | top reason |
|---|---|---|---|---|
| S01 | `korean_morning_melodrama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:loyalty_vs_survival |
| S01 | `japanese_quiet_drama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:loyalty_vs_survival |
| S02 | `korean_morning_melodrama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |
| S02 | `japanese_quiet_drama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |
| S03 | `korean_morning_melodrama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |
| S03 | `japanese_quiet_drama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |
| S04 | `korean_morning_melodrama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |
| S04 | `japanese_quiet_drama` | 1.000 | strong_fit (rulebook-only) | conflict_axis:uncertainty_vs_commitment |

---

## Audit

- raw_text_used: `False`
- evidence_preserved: `True`
- model_trained: `False`
- model_type: `weighted_rule_score`
- data_source: `rulebook_only`
