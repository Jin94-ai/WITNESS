# Phase D -- Separability Test Report

**생성**: `scripts/data_pipeline/separability_check.py`
**Dataset**: balanced_for_training (n=5621, classes=15, feature_dim=15)

## Spec §5.2.1 -- Linear Separability Test

| Metric | Value | Target | Pass |
|---|---:|---:|:---:|
| 5-fold CV acc (LogReg) | 0.509 ± 0.082 | >= 0.6 | ✗ |

## Spec §5.2.2 -- Consistency Test

KMeans(k=30) 클러스터 내 동일 action 비율.

| Metric | Value | Target | Pass |
|---|---:|---:|:---:|
| Mean in-cluster consistency | 0.439 | > 0.7 | ✗ |
| Min | 0.210 | - | - |
| Max | 0.977 | - | - |

## Spec §5.2.3 -- Feature Importance

### Global feature importance (RandomForest)

| Feature | Importance |
|---|---:|
| fear | 0.126 |
| love | 0.120 |
| grief | 0.104 |
| trust_scar | 0.097 |
| hope | 0.086 |
| confusion | 0.081 |
| identity_shift | 0.067 |
| fatigue | 0.063 |
| moral_injury | 0.054 |
| hunger | 0.048 |
| recent_event_id | 0.038 |
| time_since_event | 0.033 |
| hazard_proximity | 0.032 |
| event_trauma | 0.028 |
| health | 0.021 |

### Per-action top-3 distinguishing features

(action별 state 평균과 전체 state 평균의 차이. 큰 값일수록 해당 action을 구분짓는 feature.)

| action | top 1 | top 2 | top 3 |
|---|---|---|---|
| assert_loyalty | fear (0.78) | hunger (0.76) | fatigue (0.73) |
| confess | love (1.46) | hazard_proximity (1.40) | event_trauma (0.96) |
| deny | love (1.44) | fear (0.73) | fatigue (0.70) |
| discuss_with_disciples | fatigue (0.57) | hunger (0.48) | fear (0.37) |
| draw_sword | moral_injury (1.04) | grief (1.04) | identity_shift (1.04) |
| fall_asleep | identity_shift (1.05) | moral_injury (1.04) | grief (1.03) |
| flee | grief (1.04) | moral_injury (1.04) | recent_event_id (0.81) |
| follow_at_distance | moral_injury (1.04) | grief (1.04) | identity_shift (1.03) |
| follow_closely | fatigue (0.76) | hunger (0.76) | fear (0.72) |
| pray | fatigue (0.54) | hunger (0.46) | moral_injury (0.41) |
| run_to_tomb | hazard_proximity (1.40) | grief (1.32) | love (1.18) |
| stay_awake | identity_shift (1.05) | moral_injury (1.04) | grief (1.03) |
| stay_hiding | trust_scar (1.59) | hazard_proximity (1.40) | grief (1.29) |
| weep | grief (1.32) | identity_shift (1.28) | moral_injury (1.26) |
| withdraw_in_fear | identity_shift (0.54) | hope (0.52) | moral_injury (0.52) |

## Overall Phase D Result

- Linear separability: FAIL
- Consistency: FAIL
- **Phase D FAIL**

## Spec §5.3 -- 실패 처방

- Linear acc < 0.6 → Phase A 재실행, target state 재설계
- Consistency < 0.7 → Phase B (event context feature) 강화