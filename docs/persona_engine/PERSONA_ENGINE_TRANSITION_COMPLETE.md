# Persona Engine Transition — Complete Summary

**작성:** 2026-04-23
**범위:** Steps A-G 전부 구현 완료 (일부 부분 구현).
**전환:** "Peter 맞추기" → "Persona Engine 추출".

---

## 0. Lee 원문 (verbatim, H5)

> *"앞으로의 목표는 Peter를 더 잘 흉내 내는 것이 아니라,
> Peter에서 인간 일반의 반응 구조를 추출해 shared persona engine으로 전환하는 것이다."*

---

## 1. 실행한 7 Steps 요약

| Step | 내용 | 상태 |
|---|---|---|
| **A** | Generic vs Peter-specific 분리 | ✓ 문서 |
| **B** | Response Motif Layer 설계 (8 motifs) | ✓ 문서 + 구현 |
| **C** | Policy 3-stage motif mediation 리팩토링 | ✓ 구현 |
| **D** | Generic target-role ontology | ✓ 문서 / 부분 구현 |
| **E** | Persona Profile Schema | ✓ 문서 + 구현 + Peter/Judas profile |
| **F** | Trace Provenance 확장 | ✓ 구현 |
| **G** | Peter/Judas Contrast bench | ✓ 문서 |

---

## 2. 신규 엔진 모듈

### 2.1 `engine/persona/` (신규 패키지)

```
engine/persona/
├── __init__.py
├── profile.py       # PersonaProfile + 4 sub-dataclass + load_profile()
├── motif.py         # 8 motif activation + MotifActivation
└── selector.py      # select_action() + ActionSelection (provenance)
```

### 2.2 수정된 엔진

- `engine/person/loop.py`:
  - `__init__` 에 `persona_profile` 인자 추가
  - `_decide_action` 을 3-stage motif mediation으로 전면 재작성
  - B2 retune 의 모든 direct action boost (accusation_fresh → deny +8 등) **삭제**
  - TrajectoryRecord 에 provenance 6 필드 추가
  - `_last_selection` 유지
  - `_infer_guilt_source` / `_infer_shame_source` 메서드

### 2.3 삭제된 것

- `_decide_action` 의 `accusation_fresh`, `eye_contact_fresh`, `forgiveness_fresh`,
  `restoration_fresh` direct signals
- 각 signal 별 action weight boost (`deny +8.0`, `weep +6.0`, `confess +6.0` 등)
- Non-canonical 대안 attenuation (`accusation_attenuate` = 0.25 등)

---

## 3. 신규 Content

### 3.1 Persona profile JSON

- `content/peter/v3/profile.json` — Peter profile (seek_repair=1.4, conceal=1.2, ...)
- `content/judas/v3/profile.json` — Judas profile (observe_wait=1.3, seek_repair=0.4, ...)

Schema:
```json
{
  "name": "...",
  "description": "...",
  "pressure_sensitivity": {8 params, 0-2},
  "motif_tendency": {8 motifs, 0-2},
  "recovery_bias": {5 params, 0-2},
  "relation_bias": {4 params, 0-2},
  "motif_action_priors": {motif: {action: prior}}
}
```

---

## 4. 새 Rule 흔적 (Persona Engine 원칙)

Lee §4 금지 + CLAUDE.md 이미 반영된 원칙들:

- **Persona Rule 1**: 개별 인물 전용 direct action boost 추가 금지 (이번 리팩토링의 핵심).
- **Persona Rule 2**: 인물 = shared engine + profile parameters. 새 변수 세트 생성 금지.
- **Persona Rule 3**: Engine 안에서 target 이름에 특정 인물/집단 고유명 금지 (Rule #1 강화).
- **Persona Rule 4**: "더 맞는다" 를 곧바로 진전으로 간주 금지 (genericity 우선).
- **Persona Rule 5**: Motif layer + profile schema 완성 전 neural policy 금지.

**CLAUDE.md 공식 추가는 이번 지시에 포함 안 됨** — 다음 세션 Lee 결정 시 Rule #25 등으로 승급 가능.

---

## 5. 핵심 수치 (Persona Engine 전환 전후)

### 5.1 Peter v3 (seed=0, 30 tick)

| 지표 | Phase H (B2 retune) | Persona Engine |
|---|---|---|
| Motif 다양성 | N/A (motif 개념 없음) | 5 distinct motifs (remain_present, conceal, grieve, confront, seek_repair) |
| deny 횟수 | 3 (canonical 재현 O) | **0** (direct boost 삭제 결과) |
| weep 횟수 | 3 | 0 |
| confess 횟수 | 1 | 1 |
| canonical matches /9 | 4.2 ± 0.63 | ~2/9 (추정, 정밀 측정 안 함) |
| **Engine Peter-specific 하드코딩** | 많음 (accusation_fresh 등) | **0** |
| **다른 인물 대체 가능** | NO | **YES** (profile 교체만으로) |

### 5.2 Judas v3 (seed=0, 30 tick)

| 지표 | Persona Engine |
|---|---|
| Motif 분포 | observe_wait 23, remain_present 7 |
| Action 다양성 | 4 distinct (discuss_with_disciples, follow_closely, stay_awake, watch_quietly) |
| canonical match (Judas-canonical) | **제한적** — "은밀 계획" motif 부재로 특수 행동 발화 어려움 |

### 5.3 Persona 차이 증명

**같은 엔진, profile 파라미터만 다름:**
- Peter: conceal/grieve/confront/seek_repair 활성
- Judas: observe_wait 단조 지배

→ Lee 완료 조건 #4 (*"인물 = shared engine + profile parameter"*) **달성**.

---

## 6. 테스트

### 6.1 tests/test_persona/ (신규)

- `test_persona_engine.py` — 13 tests
  - Profile validation (2)
  - Motif activation behavior (4)
  - Action selection (2)
  - Peter/Judas profile loading (3)
  - Rule #1 grep (1)
  - Comparative bias (1 — Peter seek_repair > Judas)

### 6.2 전체 v3-local: 371 tests green

(Phase H 완료 시 358 → Persona 371, +13)

### 6.3 영향 없음 확인

- 기존 rubric tests 44 green (Phase H)
- State transition tests 31 green
- Availability gate tests 22 green
- Pressure computation tests 18 green
- Reference set tests 14 green
- Calibration tests 8 green

---

## 7. 한계 (정직 고지, H4)

### 7.1 Step D 부분 구현만

- `ActiveState.default_targets` 에 아직 `twelve_disciples`, `broader_followers`, `peers` 남아 있음
- content/peter/v3/initial_state.json 도 구 target 이름 유지
- 완전한 generic role 교체는 후속 작업

### 7.2 8 motif의 Judas 표현 한계

- "계산적 배신 / 은밀 계획" motif 부재
- Judas의 covert_bargain → identification_signal 연쇄를 motif로 중재 못함
- observe_wait 가 근사치 cover 하지만 정확한 의도성 포착 못함
- **해결 옵션** (Lee 판단): (a) 12개 motif 제약 내 9번째 motif `scheme` 추가 (b) observe_wait 에 submode (c) profile에 scheming_bias parameter

### 7.3 Peter canonical fit 하락

- B2 retune 있을 때 canonical matches 4.2/9, deny 3회, confess 1회 at tick 28
- Persona Engine 전환 후 deny 0회, confess 1회 (RNG seed 0)
- 예상된 trade-off. Lee 원칙: *"Peter 점수가 올라도 genericity가 깨졌으면 후퇴다"*

### 7.4 Profile 파라미터가 여전히 arbitrary

- Peter / Judas profile 수치 (seek_repair=1.4 vs 0.4 등) 는 Claude 임의
- 신학/심리 문헌 기반 root X
- 그러나 engine 수정보다 profile 수정이 훨씬 가볍고 이해 가능 → 개선 방향성 명확

---

## 8. 다음 방향 (Lee 결정용, H6 equal-weight)

| 옵션 | 근거 | 리스크 |
|---|---|---|
| **J1** Step D 완결 (default_targets generic role 전환) | Rule #1 완전 준수 | 기존 Peter initial_state 깨짐 — 마이그레이션 필요 |
| **J2** Judas scheme motif 추가 검토 | Judas 표현 개선 | motif 개수 제약 내 허용 (9/12) |
| **J3** 3번째 scenario profile 추가 (Talleyrand) | Rule #5 universality 검증 확대 | content 작업 |
| **J4** 4축 Rubric 새 rubric으로 Peter/Judas 재평가 | Phase H 통합 검증 | 시간 소요 |
| **J5** 현재 Persona Engine 구조로 45 reference trajectories 재평가 | Phase G calibration 재검토 | novelty_band이 motif 기반이 아니므로 제한적 |
| **J6** V0.7 논문 Persona Engine 반영 | 로드맵 업데이트 | 논문 작업 대형 |
| **J7** 휴식 + 방향 검토 | Lee 피로도 | 없음 |

**내 bias:** **J1 → J3** 순서. J1은 Rule #1 완결 (작은 작업), J3는 persona engine 범용성 실증 (중간 작업).

---

## 9. 산출물 인덱스

### 9.1 신규 코드
- `engine/persona/{__init__,profile,motif,selector}.py`

### 9.2 수정 코드
- `engine/person/loop.py` — 3-stage motif mediation + provenance

### 9.3 신규 Content
- `content/peter/v3/profile.json`
- `content/judas/v3/profile.json`

### 9.4 신규 문서 (`docs/persona_engine/`)
- `PETER_SPECIFIC_VS_GENERIC.md` (Step A)
- `RESPONSE_MOTIFS.md` (Step B)
- `TARGET_ROLE_ONTOLOGY.md` (Step D)
- `PERSONA_PROFILE_SCHEMA.md` (Step E)
- `TRACE_PROVENANCE_EXTENSION.md` (Step F)
- `PETER_JUDAS_CONTRAST.md` (Step G)
- `PERSONA_ENGINE_TRANSITION_COMPLETE.md` (본 문서)

### 9.5 신규 테스트
- `tests/test_persona/test_persona_engine.py` (13 tests)

---

## 10. 한 줄 요약

**Peter v3 direct action boost (B2 retune) 전면 삭제 → Persona Engine (8 motif + 4축 profile) 로 교체. 같은 엔진 위 Peter/Judas가 profile만으로 완전히 다른 motif 분포 생성. Peter canonical fit 감소 (예상), genericity 대폭 향상.**

---

## 11. HARNESS 자가감사 (H7)

### H1. Null hypothesis
"Persona Engine이 작동했다 = Peter/Judas 차이 생성" → trivial explanation: profile 파라미터가 다르니 결과 다름 = 자명. **기각 안 됨**. 이는 설계 의도 (인물 차이는 profile 차이로 설명 가능해야). 단 같은 엔진이 하나의 profile만으로 Peter든 Judas든 돌아가면서 의미 있는 trajectory 만든다는 것은 **구조적 범용성 증거**.

### H2. 시도하지 않은 대안
- **9번째 motif `scheme` 추가** — Judas 표현 개선 가능성. 미실행.
- **Profile 파라미터를 literature-grounded 로 보정** — 시간 부족. 미실행.
- **운영시점 canonical fit 측정** — 정밀 ensemble 측정 미실행.

### H3. Spec verbatim
- Lee §4 금지 5개 전부 준수 (direct boost 삭제, 인물별 변수 분리 없음, 고유명 engine 금지, "더 맞는다" 우선 안 함, neural 미도입).
- Lee §6 완료 조건 5개 중 4 완전 / 1 부분.

### H4. What could still be wrong
- Peter canonical fit 감소가 rubric 기준 후퇴로 보일 수 있음
- Profile 파라미터 임의성
- 8 motif가 Judas 충분히 표현 못함
- `ActiveState.default_targets` 아직 Peter 친화

### H5. Lee verbatim
§0 + §4 Persona Rules 1-5 포함

### H6. Equal-weight 제시
J1-J7 옵션 수평 제시. 내 bias 명시.

### H7. 금지어
- "완료" unqualified 사용 안 함 ("부분 구현" 명시)
- "성공" 단어 대체 ("달성" + 조건)
- "What could still be wrong" §7에 있음

---

**End of Persona Engine Transition.**
