# Witness v3 Pressure Calculations (Layer C)

> **Spec**: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §2.3
> **Code**: [engine/world/pressure.py](../engine/world/pressure.py)

## 0. 핵심 원칙

- **Rule #16**: 3 Layer 분리 (Primitive / Event / Pressure)
- **v2 §2.4 옵션 C**: Pressure는 Derived, 별도 저장 X, 매 tick 계산
- **v2 §16 함정 11**: Pressure를 Active로 등록 금지

## 1. 8 Pressure 계산식

입력:
- `p`: `PrimitiveState` (Layer A)
- `s`: `ActiveState` (person)
- `recent_accusation`: 최근 tick event intensity (0-1, caller 제공)
- `personal_faith_activation`: default = `s.hope / 10`

출력 범위: 각 pressure 0-10 (primitive product 0-1 × 10).

```
social_threat      = 10 × crowd_density × accusation_visibility × authority_presence
physical_threat    = 10 × roman_presence × volatility
shame_exposure     = 10 × (public_visibility × prior_failure_salience + recent_accusation × 0.15)
loyalty_pull       = 10 × primary_figure_presence × proximity_of_suffering
uncertainty        = 10 × information_gap × decision_stakes
urgency            = 10 × time_pressure × decision_criticality
isolation_pressure = 10 × (1 - group_cohesion) × (1 - ally_proximity)
sacred_salience    = 10 × religious_context × personal_faith_activation
```

## 2. 속성

- **Monotone**: 입력 primitive가 증가하면 관련 pressure도 단조 증가 (음의 효과는 isolation 계산의 `1 - x` 부분).
- **Clamped**: 모든 pressure [0, 10] 클램프.
- **Deterministic**: 같은 (primitive, state) → 같은 pressure.
- **Stateless**: pressure 자체는 저장 안 함. tick별 재계산.

## 3. recent_accusation 의 특별 처리

`shame_exposure` 만 최근 event 의 delta 를 boost. Caller (simulation loop) 가 매 tick 경계에서 최근 accusation event intensity 를 `PressureLayer.set_recent_accusation()` 으로 전달.

이유: public_visibility / prior_failure_salience 는 Primitive (slow) 이지만 accusation은 Event (fast). Pressure가 둘을 혼합.

## 4. Lee 검토 지점

- 곱셈적 공식의 위험: 두 인수 중 하나가 0이면 전체 0. 예: `roman_presence=0` 이면 `volatility=10` 이어도 `physical_threat=0`. 이게 맞는지?
- `sacred_salience` 의 `personal_faith_activation = hope/10` 기본값. 다른 변수 (belonging to religious group 등) 포함해야 하는지?
- Scale: primitive가 0-1 → pressure 0-10. 다른 scale 선호?

## 5. 한 줄 요약

**"8 pressure = primitive 곱셈 × 10. Shame만 recent-event boost. Stateless, per-tick 재계산. Rule #16 준수 Derived only."**
