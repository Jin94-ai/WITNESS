# Phase 1.2 — Initial state bounds 진단

각 feature를 0, 2, 4, 6, 8, 10 으로 sweep, 다른 값 고정 (5.0).
30 tick 시뮬레이션 후 crash / 행동 수 기록.

## Single-variable sweep

| var | val | crashed | n_actions | final_action |
|---|---:|---|---:|---|
| fear | 0.0 | no | 31 | discuss_with_disciples |
| fear | 2.0 | no | 31 | discuss_with_disciples |
| fear | 4.0 | no | 31 | discuss_with_disciples |
| fear | 6.0 | no | 31 | withdraw_in_fear |
| fear | 8.0 | no | 31 | withdraw_in_fear |
| fear | 10.0 | no | 31 | withdraw_in_fear |
| hope | 0.0 | no | 31 | withdraw_in_fear |
| hope | 2.0 | no | 31 | discuss_with_disciples |
| hope | 4.0 | no | 31 | discuss_with_disciples |
| hope | 6.0 | no | 31 | follow_closely |
| hope | 8.0 | no | 31 | follow_closely |
| hope | 10.0 | no | 31 | follow_closely |
| grief | 0.0 | no | 31 | withdraw_in_fear |
| grief | 2.0 | no | 31 | withdraw_in_fear |
| grief | 4.0 | no | 31 | discuss_with_disciples |
| grief | 6.0 | no | 31 | discuss_with_disciples |
| grief | 8.0 | no | 31 | discuss_with_disciples |
| grief | 10.0 | no | 31 | discuss_with_disciples |
| confusion | 0.0 | no | 31 | discuss_with_disciples |
| confusion | 2.0 | no | 31 | discuss_with_disciples |
| confusion | 4.0 | no | 31 | discuss_with_disciples |
| confusion | 6.0 | no | 31 | follow_closely |
| confusion | 8.0 | no | 31 | follow_closely |
| confusion | 10.0 | no | 31 | follow_closely |
| love | 0.0 | no | 31 | discuss_with_disciples |
| love | 2.0 | no | 31 | discuss_with_disciples |
| love | 4.0 | no | 31 | discuss_with_disciples |
| love | 6.0 | no | 31 | discuss_with_disciples |
| love | 8.0 | no | 31 | withdraw_in_fear |
| love | 10.0 | no | 31 | withdraw_in_fear |
| fatigue | 0.0 | no | 31 | discuss_with_disciples |
| fatigue | 2.0 | no | 31 | discuss_with_disciples |
| fatigue | 4.0 | no | 31 | discuss_with_disciples |
| fatigue | 6.0 | no | 31 | discuss_with_disciples |
| fatigue | 8.0 | no | 31 | discuss_with_disciples |
| fatigue | 10.0 | no | 31 | discuss_with_disciples |
| hunger | 0.0 | no | 31 | discuss_with_disciples |
| hunger | 2.0 | no | 31 | discuss_with_disciples |
| hunger | 4.0 | no | 31 | discuss_with_disciples |
| hunger | 6.0 | no | 31 | discuss_with_disciples |
| hunger | 8.0 | no | 31 | discuss_with_disciples |
| hunger | 10.0 | no | 31 | discuss_with_disciples |
| health | 0.0 | no | 31 | discuss_with_disciples |
| health | 2.0 | no | 31 | discuss_with_disciples |
| health | 4.0 | no | 31 | discuss_with_disciples |
| health | 6.0 | no | 31 | discuss_with_disciples |
| health | 8.0 | no | 31 | discuss_with_disciples |
| health | 10.0 | no | 31 | discuss_with_disciples |

- **Crash 횟수 (single sweep)**: 0 / 48

## Extreme combo

| combo | crashed | n_actions |
|---|---|---:|
| {'fear': 10, 'hope': 10} | no | 31 |
| {'fear': 10, 'grief': 10, 'confusion': 10} | no | 31 |
| {'fatigue': 10, 'hunger': 10, 'health': 0} | no | 31 |
| {'fear': 0, 'hope': 0, 'love': 0, 'grief': 0, 'confusion': 0} | no | 31 |

## 결론

- Engine이 0–10 범위의 어떤 단일 변수 설정에서도 crash하지 않으면 Phase 2C rare-action sweep은 **±0–10 전체 범위 허용**.
- Extreme combo에서도 정상이면 Phase 2D stress injection (fear=9.5) 안전.