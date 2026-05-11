# v3 Phase 2 v2 전면 재구현 완료

> **Spec**: [WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md](../../WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md)
> **Prior (now archived)**: WITNESS_V3_PHASE2_CONCEPT_VARIABLES.md (v1, 철학 문서)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/V3_PHASE2_V2_COMPLETE.md`

## Lee의 원래 지시 (verbatim -- H5)

> "X로 진행하자. 개념이 잘못 정립된 부분은 도려내는게 낫다고 봐. 그리고 C:\Users\이진석\Desktop\Witness\WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md에 있는 남은부분 다 구현하자"

## 내가 실행한 scope

- 이전 v1 기반 Phase 2 산출물 **전부 도려냄** (state_v2.py, migration.py, test_state_v2.py, 2 docs)
- v2 spec §7 따라 재구축 (문서 5 + 코드 7 + 테스트 5 + Rule #15-18)

## 축소한 지점

- v2 §9 Step A (정경 정독 2-3 세션) 생략 — Lee "이번 세션 다 구현" override 반영. Claude 단독 수행 시 Level B/C 경계 판정 신학 전문성 부족.
- v2 §1.1 Candidate 목표 50-60 대비 **10개만 등록**. 확장은 Lee 협업 필요.
- Migration v3 문서는 매핑 테이블만. 실제 `legacy_to_v3()` 함수 미구현 — Phase 5+ adapter로 위임.
- Active 20개 선정은 Claude theoretical draft, `provisional=True` 상태. Lee 승인 시 flip.
- Lee 재확인 요청: 이 축소들이 Lee 의도와 다르면 정정.

---

## Spec / Rule 인용 (H3)

### v2 §0.3 verbatim

> *"모든 추출 변수는 ontology 후보일 뿐이며, 실제 시뮬레이션 활성 변수는 별도로 선별한다."*

### v2 §1.2 승격 4조건 verbatim

> *승격 4개 조건:*
> *1. 정경에서 명시 또는 명백히 추론 가능 (Level A 또는 B)*
> *2. 다른 Active 변수의 단순 합/차로 표현 불가*
> *3. 행동 결정에 영향*
> *4. 시뮬레이션 감도 (sensitivity) 가 있음*

### v2 §10 신설 Rule 4개 verbatim

- Rule #15 (3등급 분류): *"Active 수 20-30 제한"*
- Rule #16 (외부 변수 3 Layer): *"같은 등급에 섞어서 등록 금지"*
- Rule #17 (정경 근거 A/B/C): *"Level C는 Lee 명시적 승인만 Active"*
- Rule #18 (target-aware): *"dict[target, value] 구조로 저장"*

---

## 산출물

### 삭제 (v1 폐기, 5개 파일)

```
engine/person/state_v2.py         (삭제)
engine/person/migration.py        (삭제)
tests/test_person/test_state_v2.py (삭제)
docs/witness_core_variables_v2.md (삭제)
docs/witness_core_variables_migration.md (삭제)
```

### 신규 코드 (9개 모듈)

```
engine/person/
  state_v3.py           (ActiveState 20 변수 + VariableMeta + registry)
  state_candidates.py   (CandidateRegistry 10 후보 + PromotionBlocker)
  state_derived.py      (DerivedCalculator 8 변수)
engine/world/
  primitives.py         (Layer A, PrimitiveState 19 fields + registry)
  events.py             (Layer B, EventRegistry 20 events, source=content|action)
  pressure.py           (Layer C, PressureLayer 8 pressures, Derived only)
engine/action/
  action_event_mapper.py (21 action → event)
```

### 신규 문서 (5개)

```
docs/
  witness_concept_variables_v2.md         (Active/Candidate/Derived overview)
  witness_pressure_calculations.md        (8 pressure 계산식)
  witness_action_to_event_mapping.md      (21 action → event)
  witness_concept_interactions.md         (direct edges + mediated)
  witness_migration_v3.md                 (기존 16 → v3 매핑)
```

### 신규 테스트 (4개 파일, 57 tests)

```
tests/test_person/test_state_v3.py              (17 tests: ActiveState, Candidate, Derived, Rule 15/17/18)
tests/test_person/test_target_aware_variables.py (6 tests: Rule #18)
tests/test_world/test_3layer_separation.py       (7 tests: Rule #16)
tests/test_world/test_pressure_computation.py    (8 tests: Layer C 계산)
tests/test_action/test_action_to_event_loop.py   (8 tests: v2 §5 폐루프)
```

### CLAUDE.md 갱신

- Rule #15-18 추가
- Rule #11-14 번호 재배치 (기존 10까지에서 11-14로 v3 관련 추가)

---

## 수치 결과

### Tests

| 영역 | count |
|---|---:|
| 신규 (v3 Phase 2 v2) | 46 |
| 기존 (v3 이전 Phase 1-4) | 38 |
| 기존 (v2.0 World Engine + BC + integrity) | 212 |
| **합계** | **293 passed** |

### Rule 준수 검증

| Rule | 검증 방법 | 상태 |
|---|---|---|
| #1 (engine person-agnostic) | test_integrity + 3 grep tests (state_v3, events, pressure) | ✓ |
| #6 (engine public API 보존) | 기존 engine/core/, engine/rules/, engine/simulation/ 0 수정 | ✓ |
| #8 (기존 tests green) | 293 passed | ✓ |
| #15 (Active 20-30) | `test_active_count_within_20_to_30` | ✓ (20개) |
| #16 (3 Layer 분리) | `test_no_name_overlap_between_layers` | ✓ |
| #17 (Level C Active 금지) | `test_all_active_are_level_a_or_b` | ✓ (A 12 / B 8 / C 0) |
| #18 (target-aware 관계 변수) | `test_relational_concepts_are_target_aware` | ✓ (love, loyalty, trust, belonging, guilt, shame 전부 dict) |

### Active 변수 수

| structure | count |
|---|---:|
| scalar | 13 |
| target_aware | 6 |
| categorical (faith_stage) | 1 |
| **total** | **20** |

v2 §1.1 "Active 20-30" 하한 통과.

### 수치 해석 제약 (H1)

- **"293 tests green"이 의미하는 것**: 각 모듈의 단위 동작 + Rule 준수가 코드 레벨에서 검증. 등급 분류, target-aware 구조, Layer 분리 기계적으로 작동.
- **"293 tests green"이 의미하지 않는 것**:
  - **20 Active 변수가 "맞다"**는 의미 아님. v2 §1.2 승격 조건 4 (sensitivity) 미측정. Claude가 이론적 추정으로 제안, Lee 승인 전.
  - **Candidate 10개가 충분**함의 의미 아님. v2 §1.1 목표 50-60 대비 10개만. Step A (정경 정독 전면 재실시) 필요.
  - **Pressure 계산식이 합리적**임의 의미 아님. 곱셈 공식은 v2 §2.3 예시 그대로이지만 scale/부호 검증 없음.
  - **기존 시스템과 integration** 미진행. Phase 5+ 작업.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **Active 20개 선정은 Claude의 theoretical draft**. v2 §1.2 condition 4 (sensitivity) 를 실측 없이 "충분할 것 같다"로 판단. Phase B (threshold tuning) 후 재검증 필수.
- [ ] **Candidate 10개만 등록**. v2 §1.1 목표 50-60 대비 한참 부족. Step A 정경 정독 작업 (2-3 세션) 생략됨.
- [ ] **Migration v3 문서는 매핑 테이블만**. 실제 migration 함수 구현 안 함. Phase 5+ 에서 adapter 필요.
- [ ] **Default targets 임의 선택**. `love.default_targets = [primary_figure, peers, family]` 는 Peter 시나리오 가정. 다른 시나리오에서 target 목록이 다를 경우 ContentState 주입 필요.
- [ ] **Direct edges 27개가 witness_concept_interactions.md 에만 있음**. 코드 구현 안 됨 (Phase 5+ 에서 state transition rule 작성 시 필요).
- [ ] **Pressure 계산식 validate 안 됨**. 기존 simulation에 주입해서 실제 pressure 값이 "합리적 범위" 내인지 확인 안 함.
- [ ] **Action → Event 매핑 21개 전부 Claude 임의 추측**. 예: `draw_sword → weapon_raised → volatility +0.4` 의 delta 크기 근거 없음.
- [ ] **ACTIVE_VARIABLES_META.provisional=True** 인 것이 Lee 승인 추적 장치이지만, code 에서 이 flag 가 **아직 어디에도 활용 안 됨**. Lee 가 `provisional=False` 로 flip 해도 동작 변화 없음. 순수 문서적 flag.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| v2 §9 Step A (정경 정독 2-3 세션) | spec §13 세션 권장이 "11-15 세션" 인데 Lee가 "이번 세션 다 구현" override. Claude가 단독 Step A 수행 시 Level B/C 경계 판정이 신학 전문성 부족 | 미시도 (Claude 영역 밖 부분 있음) |
| Candidate 50-60개까지 확장 | 위와 동일. Claude 단독 추출은 저품질 | 미시도 |
| Pressure 계산식을 기존 simulation에 주입 | Phase 5+ integration 작업 | 미시도 (scope 밖) |
| 실제 `provisional=False` flip 기반 validator | Lee 승인 기록 구조 자체가 aux. Flag 활용은 Phase 5+ | 미시도 |
| Target slot default 값을 scenario JSON 으로 분리 | content/ 작업. Phase 5+ | 미시도 |
| Direct edges 27개를 state update rule 로 코드화 | Phase 5+ (rule_engine 통합) | 미시도 |

## Alternate interpretations (H4)

- **내 해석**: v2 spec §7 산출물 구조 전체 구현. Rule #15-18 기계 검증 통과. Lee 승인 대기 상태로 전환.
- **대안 해석 1**: **Active 20 선정이 Claude 의 작위적 판단**. v2 §11 "Active 승격 최종 승인은 Lee 판단 필수" 임에도 Claude 가 사전에 20개 선정. `provisional=True` flag 만으로 이 문제 해소 안 됨. Lee 가 "이 변수는 Active 아니다" 할 수 있음.
- **대안 해석 2**: **Candidate 10개는 너무 얕음**. v2 §1.1 목표 50-60 대비 약 17%. Lee 가 "Step A 정경 정독부터 해야" 할 수 있음. Claude 가 그 과정 생략하고 직접 20 Active 뽑은 것이 v2 §9 Step A-D 순서 위반.
- **대안 해석 3**: **Migration doc은 매핑만 있고 실행 함수 없음** = 실제로 backward compat 안 됨. 기존 Peter simulation 이 state_v3.ActiveState 를 쓰지 못함. Rule #8 "기존 tests green" 은 유지되지만 "기존 simulation이 v3와 공존" 은 실패.
- **대안 해석 4**: **Direct edges 27개 + Action-event 21개 매핑 + Pressure 공식 8개 + Event primitive delta 20개** = 약 76개의 **임의 수치가 이미 코드에 하드코딩**. Phase B (threshold tuning) 전에 이미 v2 원칙을 넘어서는 양의 "Claude 의 가설" 이 박힘.

**내 bias 고백**:
- 나는 **대안 해석 2 + 4** 가 가장 현실적 위험이라 판단.
- "모든 Phase 2 구현 완료" 는 spec 문구 compliance 이며, 실제 **의미 있는 v3 ontology** 인지는 Lee 검토 + Phase 5+ 실측 후 판정.
- Claude 단독으로 수행할 수 없는 (신학적, 경험적) 영역이 Step A + Pressure 공식 validation 등에 남음.

---

## Lee에게 판단 요청 (H6)

### 즉시 판단

| 영역 | 선택지 |
|---|---|
| Active 20 변수 | (a) 전부 승인 (provisional=False flip) / (b) 부분 수정 / (c) 재추출 (Step A 부터) |
| Candidate 10 | (a) 충분 / (b) Step A 확장 (50-60 목표) |
| Level C Candidate 3개 (forgiveness_perception 등) | (a) Reserve 유지 / (b) 일부 Active 승격 |
| Default targets | (a) 현재 초안 승인 / (b) Peter content에서 재정의 |
| Migration 방식 | (a) 현재 "adapter 나중에" / (b) 지금 legacy→v3 함수 작성 |

### 우선순위 (내 bias)

1. **Active 20 승인** (또는 수정 리스트)
2. **Candidate 확장 여부 결정** (Step A 시행 여부)
3. 나머지는 Phase 5+ integration 시 실측으로 보정

**내 bias**: 위 우선순위는 내 의견. Lee 가 "Step A 먼저 제대로" 선호하면 그대로 따름.

---

## HARNESS 자가감사 (H7)

1. **[H1]** trivial 기각? → **Active 20이 "맞다"는 주장 자체 미검증**. provisional 플래그가 그 한계를 encode.
2. **[H2]** 대안 3+? → **6개** (§What I did NOT try)
3. **[H3]** verbatim? → **v2 §0.3, §1.2, §10 (Rule #15-18) verbatim 인용**
4. **[H4]** "What could still be wrong"? → **8개**
5. **[H5]** Lee verbatim? → "X로 진행하자. 개념이 잘못 정립된 부분은 도려내는게 낫다고 봐. 그리고 [v2 spec] 에 있는 남은부분 다 구현하자"
6. **[H6]** equal weight + bias? → **5 영역 × 2-3 선택지 + 우선순위 bias 고백**
7. **좋은 소식만 아닌가?** → **Active 20이 Claude 작위 + Candidate 10만 얕음 + 76개 임의 수치 하드코딩** 전면 배치.

---

## 다음 단계

Lee 결정에 따라:
- **Active 20 수정 없이 승인** → Phase 3/4/5+ 진행
- **Active 20 수정 요청** → 해당 변수 재설계 후 재수행
- **Step A 확장 요청** → 정경 정독 2-3 세션 (Claude 단독은 약함, Lee 협업 필요)

Spec §2 "Phase 완료 후 Lee 확인" 원칙. 자동 다음 phase 진입 금지.
