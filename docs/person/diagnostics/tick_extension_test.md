# Phase 1.3 — Tick extension 진단

seed=0, canonical_events + behavior_profile 정상 load.

| max_tick | crashed | n_actions | final_tick | final fear | final hope | final fatigue |
|---:|---|---:|---:|---:|---:|---:|
| 50 | no | 51 | 50 | 4.63 | 8.81 | 3.00 |
| 100 | no | 101 | 100 | 9.69 | 7.74 | 3.00 |
| 200 | no | 212 | 200 | 9.40 | 0.93 | 10.00 |
| 500 | no | 516 | 500 | 9.37 | 8.43 | 10.00 |

## 긴 궤적 attractor 관찰

- 500 tick까지 완주: True
- 500 tick 마지막 state fear/hope: 9.37 / 8.43
- saturation vs oscillation 구분은 snapshot 궤적 추가 분석 필요.