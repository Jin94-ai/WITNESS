# Witness v3 Migration (v2 §8 수정)

> **Spec**: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §8
>
> **기존 v1 migration.py 폐기.** v2 §8 원칙으로 재작성.

## 0. ChatGPT 핵심 지적 (v2 §8.3)

> *"마이그레이션은 단순 rename이 아니라 관찰 가능한 개념으로의 환원 원칙이 더 분명해야 한다."*

각 기존 변수마다: **"이 변수가 일상적으로 명명 가능한 개념인가?"**
- Yes → 신규 변수로 매핑
- No → 분해하거나 폐기

## 1. 기존 16 → v3 매핑 (v2 §8.2)

### 1.1 유지 (Active, Level A, 9개)

| 기존 | v3 신규 | 변경 |
|---|---|---|
| `emotions.fear` | `fear` | 동일 |
| `emotions.hope` | `hope` | 동일 |
| `emotions.grief` | `grief` | 동일 |
| `emotions.confusion` | `confusion` | 동일 |
| `emotions.love` (scalar) | `love[target]` (dict) | **target-aware 변환** (Rule #18) |
| `physical.fatigue` | `fatigue` | 동일 |
| `physical.hunger` | `hunger` | 동일 |
| `physical.health` | `vitality` | 재명명 (더 일상적 개념) |

### 1.2 재정의 / 분해 (4개)

| 기존 | v3 신규 |
|---|---|
| `slow_state.moral_injury` | **분해**: `shame[target]` + `guilt[wronged_party]` (Rule #18) |
| `slow_state.identity_shift` | **재정의**: `doubt` + `confusion` 조합으로 충분 — 별도 변수 폐기 |
| `slow_state.event_trauma` | `trauma` (단일 변수 유지) |
| `slow_state.trust_scar` | **반전**: `trust[target]` 의 음수 방향 — `trust` dict로 흡수 |

### 1.3 거의 폐기 (3개 -- Candidate 로 이동 또는 삭제)

| 기존 | 처분 | 이유 |
|---|---|---|
| `FaithJourney.fear_layers` | **폐기** | v2 §8.2 "Lee 의도 어긋남" |
| `FaithJourney.obedience_maturity` | **폐기** | "일상 명명 가능 개념" 기준 미달 |
| `FaithJourney.communal_role` | 외부 변수 (`group_role`) 로 이동 검토 | 개인 변수 아닌 사회적 역할 |

### 1.4 통합 (1개)

| 기존 | v3 신규 |
|---|---|
| `FaithJourney.jesus_understanding` (Literal) | `understanding_level` (Candidate) + `faith_stage` (Active) 로 분리 표현 |

## 2. 결과 요약

- **기존 16 → v3 13개 일부 재사용 + 7개 신규 Active**
- Rule #18 target-aware 변환: 1개 (love)
- 분해: 1개 (moral_injury → 2개)
- 재명명: 1개 (health → vitality)
- 폐기: 3개 (fear_layers, obedience_maturity, communal_role)

## 3. 코드 migration

**v1의 migration.py 폐기**. 현재 Phase 2 v2 구현은 **state_v3.ActiveState** 가 **legacy AgentState 와 완전 독립**. 기존 시뮬레이션은 AgentState 그대로 사용. v3 새 pipeline (Phase 5+) 에서 ActiveState 채택.

이것이 **backward compat 전략**: 기존 engine/core/state.py 는 건드리지 않음 (Rule #6 준수).

v3 구조를 기존 시뮬레이션에 연결할 때 (Phase 5+) 별도 adapter 작성:
```python
# Phase 5+ 에서 필요 시 작성
def legacy_to_v3(legacy: AgentState) -> ActiveState:
    ...
```

하지만 v2 §8.3 명시: **단순 rename 아닌 개념 환원**. 위 매핑의 대부분은 1:1 아닌 의미적 전환.

## 4. Lee 판단 필수 (v2 §11 "마이그레이션 폐기 변수")

- `fear_layers` 폐기 최종 승인
- `obedience_maturity` 폐기 최종 승인
- `communal_role` 외부 변수 이동 vs 폐기
- `health → vitality` 재명명 (의미 동일한가)
- `love` target-aware 변환 시 기존 scalar value 어떻게 initialize

## 5. 한 줄 요약

**"기존 16 → v3 Active 13개 매핑 (유지 8 + 분해 2 + 재명명 1 + 통합 2). 폐기 3. target-aware 변환 1. 자동 migration 함수 대신 Phase 5+ adapter로 처리."**
