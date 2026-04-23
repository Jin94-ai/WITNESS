# Phase 1.1 — 기존 108 샘플 분포 진단

**생성**: 2026-04-22, `scripts/data_pipeline/phase1_diagnostics.py`

- 총 샘플: 108
- Action vocab: ['assert_loyalty', 'discuss_with_disciples', 'follow_closely', 'pray', 'withdraw_in_fear']
- Feature dim: 12

## Action 분포 (class imbalance)

| action | count | % |
|---|---:|---:|
| assert_loyalty | 3 | 2.8% |
| discuss_with_disciples | 11 | 10.2% |
| follow_closely | 83 | 76.9% |
| pray | 9 | 8.3% |
| withdraw_in_fear | 2 | 1.9% |

## Feature statistics (전체 샘플)

| feature | min | max | mean | std | unique |
|---|---:|---:|---:|---:|---:|
| emotions.fear | 1.59 | 9.94 | 5.02 | 2.06 | 108 |
| emotions.hope | 7.65 | 9.93 | 8.92 | 0.63 | 104 |
| emotions.grief | 0.00 | 1.07 | 0.55 | 0.28 | 108 |
| emotions.confusion | 3.19 | 7.78 | 4.93 | 0.83 | 108 |
| emotions.love | 6.07 | 8.86 | 6.94 | 0.81 | 108 |
| physical.fatigue | 3.00 | 3.00 | 3.00 | 0.00 | 1 |
| physical.hunger | 0.00 | 2.00 | 1.65 | 0.76 | 2 |
| physical.health | 8.00 | 8.00 | 8.00 | 0.00 | 1 |
| slow_state.moral_injury | 0.00 | 0.00 | 0.00 | 0.00 | 1 |
| slow_state.identity_shift | 0.00 | 0.00 | 0.00 | 0.00 | 1 |
| slow_state.event_trauma | 0.00 | 0.00 | 0.00 | 0.00 | 1 |
| slow_state.trust_scar | 0.00 | 0.60 | 0.04 | 0.10 | 3 |

## 해석 — 얼마나 좁은 공간인가

- **Volume ratio** (per-feature range product / full [0,10]^12): 3.11e-15
- 1.0에 가까울수록 넓은 공간 커버. 현재 값은 실측 공간이 얼마나 좁은지의 지표.

## Action별 state mean (decision boundary 위치)

| action | fear | hope | grief | confusion | love | fatigue | hunger | health | moral_injury | identity_shift | event_trauma | trust_scar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| assert_loyalty | 3.89 | 9.27 | 0.53 | 4.86 | 7.27 | 3.00 | 1.33 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| discuss_with_disciples | 4.92 | 8.94 | 0.57 | 4.80 | 7.25 | 3.00 | 1.45 | 8.00 | 0.00 | 0.00 | 0.00 | 0.07 |
| follow_closely | 4.92 | 8.92 | 0.56 | 4.93 | 6.86 | 3.00 | 1.71 | 8.00 | 0.00 | 0.00 | 0.00 | 0.03 |
| pray | 5.79 | 9.00 | 0.49 | 5.19 | 7.01 | 3.00 | 1.56 | 8.00 | 0.00 | 0.00 | 0.00 | 0.04 |
| withdraw_in_fear | 8.04 | 8.09 | 0.18 | 4.69 | 7.53 | 3.00 | 1.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.20 |