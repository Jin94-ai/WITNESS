# Witness v3.0 Pressure Field -- Design

> **Spec**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) §5
> **Code**: `engine/pressure/` + `engine/constraint/`

## 1. 4층 월드 구조 (spec §5.2)

```
Layer A: World Facts         (기존 Spike 1-5 layer 6개 재분류)
Layer B: Event Objects       (짧은 수명 사건, 기존 canonical_events 재해석)
Layer C: Pressure Field      ← v3.0 신규 (engine/pressure/)
Layer D: Constraint          ← v3.0 신규 (engine/constraint/)
```

## 2. 흐름

```
Tick t:
  1. Layer A (World Facts) 기존대로 update
  2. Layer B (Event Objects) 발동 이벤트 감지
  3. Layer C (Pressure Field):
     - PressureField.tick(incoming=[...], decay=PressureDecay) → 현재 압력
  4. (Person module reads Layer A+C) → chooses action
  5. Layer D (Constraint): 
     - HardConstraintChecker → 액션이 canon 위반이면 reject
     - SoftConstraintScorer → drift 점수 기록
```

**핵심: 압력은 '어떤 행동을 해야 하는가'를 지정하지 않는다** (Rule #12). 사람 모듈이 압력을 읽고 자기 정책으로 결정.

## 3. 8 Pressure Variables (spec §5.3)

| variable | 의미 | 예상 source |
|---|---|---|
| `social_threat` | 사회적 위협 | 군중 적대, 공개 고발 |
| `physical_threat` | 물리 위협 | 경비병 접근, 무기 |
| `shame_exposure` | 공개 수치 | 공개 노출 + 과거 실패 |
| `loyalty_pull` | 결속의 끌어당김 | 주된 결속 대상의 고난 |
| `uncertainty` | 정보 공백 | 숨겨진 정보, 높은 위험 |
| `urgency` | 긴급성 | 시간 압박, 결정 임박 |
| `isolation_pressure` | 고립감 | 동료 이탈, 버림받은 느낌 |
| `sacred_salience` | 거룩함 현출성 | 종교 맥락 + 신앙 활성화 |

## 4. 계산 방식 (예시, spec §5.3)

```
social_threat    = crowd_density × accusation_visibility
physical_threat  = roman_presence × volatility
shame_exposure   = public_visibility × prior_failure_salience
loyalty_pull     = memory_of_primary_figure × proximity_of_suffering
uncertainty      = information_gap × stakes
urgency          = time_pressure × decision_criticality
isolation        = group_absence × perceived_abandonment
sacred_salience  = religious_context × personal_faith_activation
```

**이 계산은 두 가지 소스**:
1. Layer A World Facts (crowd_density, roman_presence, religious_context 등)
2. Event Object 감지 시 테이블 look-up (`engine/pressure/event_pressure_map.py`)

## 5. Decay (spec §5.5)

**핵심 통찰**:
> 중요한 건 이벤트 발생 그 순간보다 몇 턴 동안 잔향을 남기느냐다.

`engine/pressure/decay.py::PressureDecay` 가 per-variable exponential half-life:

```python
decay_factor = 0.5 ** (dt / half_life)
```

Half-life 값은 `docs/witness_event_pressure_table.md §3` 참조.

## 6. Constraint Layer (Layer D, spec §5.2)

### 6.1 Hard Constraints (binary)

`engine/constraint/hard_constraints.py::HardConstraintChecker`:

- **Anachronism**: action_id must be in scenario's vocabulary
- **Canonical contradiction**: fixed_actions at specific ticks must not be overridden
- **Theological violation**: sacred figure's visible_signal must include guards (Rule #2)

위반 시 `ConstraintViolation` 기록. 이 기록은:
- 실험 trajectory 분석 시 사용
- Phase 4 Canon Critic의 입력

### 6.2 Soft Constraints (score)

`engine/constraint/soft_constraints.py::SoftConstraintScorer`:

- 관찰된 action 시퀀스와 canonical reference의 Levenshtein distance
- + 순서 침범(inversions) penalty

0 = canon-identical, 큰 값 = canon drift. Phase 4 Novelty Critic 의 입력.

## 7. 기존 Spike 1-5 월드와의 통합

**충돌 회피 (spec §5.6)**:

- 기존 6 Layer (Calendar, Crowd, Economy, Politics, Factions, Rumours) 는 **Layer A 하위로 재분류**
- Pressure Field Layer C 는 **위에 새로 올라가는 층** -- 기존 코드를 수정하지 않음
- 기존 1176+ tests green 유지

## 8. Rule #12 준수 증명

`engine/pressure/` 전체 코드 **어디에도 `agent.action = X` 같은 할당 없음**. `PressureField.tick()` 반환은 `PressureVector` (숫자 8개). 액션 선택은 downstream person module 책임.

Test `test_pressure_modules_no_person_hardcoding` 이 Rule #1 + Rule #12 정신을 grep-level 로 검증.

## 9. 한 줄 요약

**"Pressure Field는 8개 숫자 (social/physical/shame/loyalty/uncertainty/urgency/isolation/sacred) 를 매 tick 생성. 이벤트 테이블에서 delta 읽고 decay 적용. 행동은 절대 지정하지 않음 (Rule #12)."**
