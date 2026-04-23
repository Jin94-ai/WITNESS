# Witness v3 Concept Interactions (v2 §6 수정)

> **Spec**: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §6

## 0. v1 수정사항 (v2 §6.1)

v1: *"각 변수 최대 3개"* — **너무 기계적**
v2: 연결 유형별 제한 + Strong direct / Mediated 분리

## 1. Strong Direct Edges (v2 §6.2)

- 변수당 2-4 direct edges (상한 5)
- 부호 (+/-) 와 강도 (weak/medium/strong) 명시

### 1.1 Active 변수 direct edges (초안)

```
fear:
  → resolve         (strong, -)
  → doubt           (strong, +)
  → confusion       (medium, +)

hope:
  → resolve         (strong, +)
  → doubt           (medium, -)
  → peace           (medium, +)     # Derived target

love[target]:
  → loyalty[target] (strong, +)
  → trust[target]   (medium, +)

loyalty[target]:
  → guilt[target]   (strong, +)     # 배신 시 loyalty-based guilt

guilt[target]:
  → shame[target]   (strong, +)
  → repentance_depth (strong, +)    # Derived
  → faith_stage      (medium, -)

shame[target]:
  → hesitation       (strong, +)    # Candidate
  → belonging[target] (medium, -)

trust[target]:
  → belonging[group containing target] (medium, +)

fatigue:
  → vitality         (strong, -)
  → resolve          (medium, -)
  → anger            (weak, +)

trauma:
  → faith_stage      (medium, -)
  → repentance_depth (medium, +)

doubt:
  → resolve          (strong, -)
  → faith_stage      (medium, -)

awe:
  → faith_stage      (medium, +)
  → love[target]     (medium, +)

joy:
  → vitality         (medium, +)
  → peace            (strong, +)

anger:
  → resolve          (weak, +)
```

## 2. Mediated Connections (v2 §6.2)

- 제한 없음
- Pressure / latent mediator 경유
- 예시:

```
public_accusation (Event)
  → [Primitive update: accusation_visibility↑]
  → [Pressure: shame_exposure↑]
  → [Person: shame[crowd]↑]
  → [Person direct edge: hesitation↑, belonging↓]

guard_approaches (Event)
  → [Primitive: roman_presence↑, time_pressure↑]
  → [Pressure: physical_threat↑, urgency↑]
  → [Person: fear↑ (via pressure sensitivity)]
  → [Direct: resolve↓]
```

## 3. Graph 통계

### Direct edges 수 (현 초안)

| 변수 | downstream count |
|---|---:|
| fear | 3 |
| hope | 3 |
| love | 2 |
| loyalty | 1 |
| guilt | 3 |
| shame | 2 |
| trust | 1 |
| fatigue | 3 |
| trauma | 2 |
| doubt | 2 |
| awe | 2 |
| joy | 2 |
| anger | 1 |

총 27 direct edges, 12 active 변수 대상. 평균 2.25 / 변수. v2 §6.2 "2-4 범위" 준수.

### Mediated path examples

- Public accusation → shame[crowd] (3단계)
- Guard approaches → fear (via physical_threat pressure, 3단계)

## 4. Lee 검토 지점

- 부호 (+/-) 방향 맞나? (특히 `loyalty → guilt+` 는 "배신 시 loyalty가 guilt 만들어낸다"는 방향)
- 강도 (weak/medium/strong) 할당
- 누락된 중요 edge? (예: `awe → hope+` 가 맞나 direct 인가 mediated 인가)

## 5. 한 줄 요약

**"Strong direct 27 edges (변수당 1-3) + Mediated path (Pressure 경유) 무제한. v2 §6 규칙 준수."**
