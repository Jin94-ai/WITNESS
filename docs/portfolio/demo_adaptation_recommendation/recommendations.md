# Phase 3.1 §22.3 Target C — Adaptation Recommendation

## Non-Claims (Phase 3.05 review §3)

- 이 recommendation은 *truth claim*이 아닌 **adaptation candidate**다.
- 학습 0 / 외부 fetch 0 / raw text 사용 0.
- 모든 threshold는 `uncalibrated_phase3_placeholder` (Phase 5+ 실측 보정 전).
- Rule #14 — rubric/recommendation은 학습 loss로 사용되지 않음.

> **📐 Prep mode (rulebook-only)** — 현재 score는 *실제 annotation 기반 추천이 아니라* rulebook compatibility (seed의 conflict_axis / dominant_pressures가 장르 rulebook과 호환되는 정도)다. Phase 3.0 pilot 데이터가 들어와야 annotation component가 추가되어 *data-backed* recommendation이 된다.

---

## 메타

- **schema**: `adaptation_recommendation_v1`
- **source skeleton**: `peter_scarcity_baseline` (skeleton_output_v1)
- **profiles**: korean_morning_melodrama, japanese_quiet_drama
- **top_k**: 3
- **model**: weighted_rule_score (trained=False, data_source=rulebook_only)
- **audit**: raw_text_used=False / evidence_preserved=True
- **calibration**: `uncalibrated_phase3_placeholder`

---

## 1순위 장르 분포 (seed별 top-1 빈도)

- `korean_morning_melodrama`: 4 seeds

## Seed별 Ranked Recommendations

### S01

- **1순위**: `korean_morning_melodrama` — score 1.000 (strong_fit (rulebook-only))
- **이유**: conflict_axis:loyalty_vs_survival + pressure:authority_vigilance
- **mode**: `rulebook_only`
- **대안 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only)) — conflict_axis:loyalty_vs_survival + pressure:authority_vigilance

### S02

- **1순위**: `korean_morning_melodrama` — score 1.000 (strong_fit (rulebook-only))
- **이유**: conflict_axis:uncertainty_vs_commitment + pressure:confusion
- **mode**: `rulebook_only`
- **대안 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only)) — conflict_axis:uncertainty_vs_commitment + pressure:confusion

### S03

- **1순위**: `korean_morning_melodrama` — score 1.000 (strong_fit (rulebook-only))
- **이유**: conflict_axis:uncertainty_vs_commitment + pressure:confusion
- **mode**: `rulebook_only`
- **대안 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only)) — conflict_axis:uncertainty_vs_commitment + pressure:confusion

### S04

- **1순위**: `korean_morning_melodrama` — score 1.000 (strong_fit (rulebook-only))
- **이유**: conflict_axis:uncertainty_vs_commitment + pressure:confusion
- **mode**: `rulebook_only`
- **대안 후보**:
  - `japanese_quiet_drama`: 1.000 (strong_fit (rulebook-only)) — conflict_axis:uncertainty_vs_commitment + pressure:confusion

---

## 재현 명령

```bash
python scripts/narrative/run_adaptation_recommendation.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \
    --output data/narrative/phase3_1_demo/adaptation_recommendation.json \
    --top-k 3
```

```bash
python scripts/narrative/build_adaptation_recommendation_demo.py \
    --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \
    --output docs/portfolio/demo_adaptation_recommendation
```
