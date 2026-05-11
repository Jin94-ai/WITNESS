# Peter / Judas Contrast Bench (Step G)

**작성:** 2026-04-23
**원칙 (Rule #21 영구):** Judas는 튜닝 대상 아님. **일반화 실패 진단 자료** 로만 사용.
**본 문서 용도:** Persona Engine 이 같은 엔진 위에서 profile 만으로 두 인물을 구분하는가를 측정.

---

## 0. 측정 조건

- 엔진: Persona Engine 전환 후 (Step C 완료)
- Peter: `content/peter/v3/profile.json`
- Judas: `content/judas/v3/profile.json`
- 동일 RNG seed (0), 30 ticks
- 각자의 canonical_events.json 기반 (서로 다른 event schedule)

---

## 1. Motif 분포 비교

| Motif | Peter (30 tick) | Judas (30 tick) | 차이 |
|---|---:|---:|---|
| observe_wait | 0 | **23** | Judas 극단 지배 |
| remain_present | **22** | 7 | Peter 지배 |
| conceal | 4 | 0 | Peter only |
| grieve | 2 | 0 | Peter only |
| confront | 1 | 0 | Peter only |
| seek_repair | 1 | 0 | Peter only |
| withdraw | 0 | 0 | - |
| confess | 0 | 0 | - |

**해석:**
- **Peter 다양 motif 활성**: 정상적 passion week 인물. 사건에 따라 remain_present → conceal → grieve → seek_repair 이동.
- **Judas 단조로운 observe_wait**: 25-30 tick 동안 계산/대기 상태 지속. profile의 `observe_wait_tendency=1.3` + `primary_focus_attachment=0.7` + 적극 motif 낮음 (confront=0.6, confess=0.7, seek_repair=0.4) 결합.

**현재 엔진이 못 설명하는 차이:**
- Judas는 `covert_bargain`, `identification_signal`, `return_token` 같은 **은밀 행동**에 대한 motif가 없음. `observe_wait`는 대기이지 계획적 행위 아님.
- `scheme / calculate / betray_covertly` 같은 **"은밀 의도적 계산"** motif가 추가될 필요 있음. 단 현재는 8 motif 제약 유지.

---

## 2. Action 분포 비교

| Action | Peter | Judas | 차이 |
|---|---:|---:|---|
| discuss_with_disciples | 6 | **16** | Judas 절반 이상 |
| follow_closely | **9** | 7 | Peter 우세 |
| stay_awake | 7 | 4 | - |
| follow_at_distance | **3** | 0 | Peter only |
| pray | 2 | 0 | Peter only |
| watch_quietly | 0 | **3** | Judas only |
| assert_loyalty | 1 | 0 | Peter only |
| withdraw_in_fear | 1 | 0 | Peter only |
| confess | 1 | 0 | Peter only |

**해석:**
- Peter: 9 distinct actions. Passion context에 반응.
- Judas: 4 distinct actions. discuss_with_disciples 16회 — 대기/논의 지배.
- Canonical 행동 (deny, weep) 은 둘 다 0회 — Peter v1 B2 튜닝 없앤 결과. Genericity 유지.

---

## 3. 핵심 Tick 에서의 비교

### Peter (accusation / turning point 시점)

| Tick | Event | Motif | Action |
|---:|---|---|---|
| 17 | public_accusation | **conceal** | follow_at_distance |
| 18 | public_accusation | **conceal** | withdraw_in_fear |
| 19 | public_accusation | **conceal** | follow_at_distance |
| 20 | eye_contact+public_accusation | **conceal** | follow_at_distance |
| 21 | (post-accusation) | remain_present | follow_closely |
| 28 | restoration_moment | remain_present | follow_closely |

**Peter 정경과 비교:**
- canonical: 17/18/19 deny, 20 weep, 28 confess
- actual: 17-20 conceal motif → follow_at_distance (not deny)
- 이유: conceal motif의 action prior 에서 deny=0.45 / follow_at_distance=0.20. RNG에서 deny 대신 follow_at_distance가 뽑힘. 3회 반복이라 확률상 한 번은 deny 예상되는데 결과가 전부 follow_at_distance는 RNG seed 영향.
- **B2 retune이 있을 때 deny 3회 재현했던 것이 motif 층 도입 후 깨짐.** 이는 예상된 결과. Lee 원칙: *"Peter 점수가 올라도 genericity가 깨졌으면 후퇴다"*. 지금은 Peter 개별 fit 감소했으나 genericity 증가.

### Judas (betrayal / remorse 시점)

| Tick | Event | Motif | Action |
|---:|---|---|---|
| 3 | covert_bargain | observe_wait | discuss_with_disciples |
| 5 | sacred_meal | observe_wait | discuss_with_disciples |
| 7 | betrayal_witnessed | observe_wait | watch_quietly |
| 8 | ally_departure | observe_wait | discuss_with_disciples |
| 12 | guard_approaches | observe_wait | discuss_with_disciples |
| 13 | identification_signal | observe_wait | stay_awake |
| 20 | remorse_trigger | remain_present | follow_closely |
| 22 | return_token | observe_wait | discuss_with_disciples |

**Judas 정경과 비교:**
- canonical (run_judas_v3): 3 discuss, 7 withdraw_in_fear (betrayal exposed), 13 assert_loyalty (kiss), 20 weep, 22 confess
- actual: observe_wait 지배, 특수 행동 부재
- **원인**: `identification_signal` event → scene_response 에서 assert_loyalty expected 이나 observe_wait의 action prior에는 assert_loyalty 낮음. `remorse_trigger` → 정경은 weep/flee 이나 motif 가 remain_present로 수렴.

**Judas 누락된 구조:**
- "계산된 배신" motif가 없음 (observe_wait는 수동적)
- Judas 고유 절망 (despair) motif도 없음

---

## 4. Peter profile vs Judas profile 파라미터 대비

| 파라미터 | Peter | Judas | Ratio (P/J) | 의미 |
|---|---:|---:|---:|---|
| **Pressure sensitivity** | | | | |
| social_threat | 1.2 | 0.8 | 1.5× | Peter 공개 현장에 민감 |
| loyalty_pull | 1.3 | 0.7 | 1.86× | Peter primary_focus 수난에 민감 |
| sacred_salience | 1.4 | 0.8 | 1.75× | Peter 경외 강함 |
| isolation_pressure | 0.9 | 1.2 | 0.75× | Judas 이미 심리적 고립 |
| **Motif tendency** | | | | |
| seek_repair | 1.4 | 0.4 | **3.5×** | 가장 큰 차이 |
| confess | 1.1 | 0.7 | 1.57× | Peter 공개 confess 가능 |
| confront | 1.3 | 0.6 | 2.17× | Peter 정면 대응 (칼 뽑음) |
| conceal | 1.2 | 1.3 | 0.92× | 둘 다 높음 (각자 다른 방식) |
| observe_wait | 0.8 | 1.3 | 0.62× | Judas 계산/대기 |
| **Recovery bias** | | | | |
| guilt_decay_rate | 0.8 | 0.5 | 1.6× | Judas guilt 훨씬 길게 지속 |
| trust_restoration_bias | 1.2 | 0.5 | 2.4× | Peter 재결속, Judas 복원 없음 |
| **Relation bias** | | | | |
| primary_focus_attachment_strength | 1.4 | 0.7 | 2× | Peter 강한 결속, Judas 이탈 |
| authority_reactivity | 0.9 | 1.2 | 0.75× | Judas 권력 측 접근 (대제사장) |

---

## 5. 공통 / 차이 / 공백 (3종 분류)

### 5.1 공통 motif 패턴 (generic human 공유)

- 둘 다 **remain_present** 기본 상태
- 둘 다 초반 평시 `follow_closely` / `discuss_with_disciples` 우세
- 둘 다 canonical event 반응 능력 있음 (conceal Peter / observe_wait Judas)

### 5.2 Peter 우세 motif

- `conceal`, `grieve`, `confront`, `seek_repair` 모두 Peter only 활성 (30 tick)
- 이유: Peter는 사건에 **능동 반응**. 사건 → motif → action 연쇄 밝게 움직임

### 5.3 Judas 우세 motif

- `observe_wait` (23회 vs Peter 0회)
- 이유: Judas profile의 observe_wait 증폭 + 다른 motif 감쇄 + primary_focus 이탈 → "사건 앞에서 적극 대응 안 함"

### 5.4 현재 엔진이 못 설명하는 차이

**가장 큰 공백 3가지:**

1. **"계획/계산된 행동"**: Judas의 silver 합의는 covert_bargain event로 발생하나, 엔진 내 motif가 그것을 매개하지 못함. observe_wait는 수동. 필요한 motif (현 8개 초과 금지 제약 하에서):
   - 대안 1: `observe_wait` 안에 "계산적 대기" submode
   - 대안 2: profile에 `scheming_bias` 같은 파라미터 추가 (motif에 영향)
   - 대안 3: 새 motif `scheme` 추가 (9개, Lee 12 제약 내)

2. **"절망 / 극단 회피"**: Judas 후회 → 자기 파괴. 현재 motif `grieve` 가 cover 하나 action prior에 self-harm 없음. action vocab 확장도 스펙 금지.

3. **"은밀한 이탈"**: Judas 식탁 떠남 (tick 8 ally_departure) → withdraw_in_fear 기대했으나 observe_wait 지배. withdraw motif activation 조건에 "명시적 떠남 의도" 없음.

---

## 6. 성공 / 부족 평가

### 6.1 Lee 완료 조건 대비

| 완료 조건 | 상태 |
|---|---|
| (1) Peter 정책에서 direct action boost → motif boost 대체 | ✓ `_decide_action` 3-stage 구조, 모든 boost 삭제 |
| (2) target-aware 관계 구조 generic role 기반 | **부분** (profile에 generic 이름 사용, 그러나 `ActiveState.default_targets` 는 아직 구 이름 — 추후 Step D 완성) |
| (3) Peter / Judas 같은 profile schema 기술 | ✓ 둘 다 `content/<name>/v3/profile.json` |
| (4) 인물 = shared engine + profile | ✓ PersonV3Loop 이 profile만 바꿔 둘 실행 |
| (5) 새 인물 추가 = profile + scenario binding | ✓ engine 코드 수정 불필요 (DEFAULT_PROFILE로 baseline human 즉시 생성 가능) |

### 6.2 완료 **아님**

- `ActiveState.default_targets` 는 아직 `primary_figure` / `peers` / `twelve_disciples` / `broader_followers` 남아 있음. Step D 부분 구현.
- faith_stage_tag도 Christian-specific 언어 유지.
- Peter canonical fit 은 B2 retune보다 낮음 (deny 0회, confess 1회). genericity와 canonical fit 사이 trade-off.
- 8 motif가 Judas의 "계획적 배신" 을 잘 cover 못함. Lee §4 금지: 12개 초과 금지 → 이 공백은 의도적 허용.

---

## 7. 의미

Persona Engine 전환의 목적은 **"Peter를 더 맞추는 것이 아니라 일반화 구조를 만드는 것"** 이었다.

- ✓ 같은 엔진 위에서 Peter/Judas가 **완전히 다른 motif 분포** 생성 (profile 파라미터만으로)
- ✓ `_decide_action` 에 Peter-specific 하드코딩 0 (B2 retune 완전 제거)
- ✓ 새 인물 추가 시 코드 수정 불필요 (profile + content만)
- ✗ 현재 rubric 기준 Peter canonical fit 이 B2 retune보다 낮음 (예상된 trade-off)
- ✗ Judas-specific motif 공백 존재 (8-motif 제약 하에서 부분 cover 만 가능)

**최종 판정:** Lee 4대 원칙 준수 + 완료 조건 5개 중 4개 완전, 1개 부분. 방향 성공, 세부 추가 작업 남음.

---

## 8. 후속 작업 제안 (Lee 결정용)

| 작업 | 효과 | Lee 원칙 위반 여부 |
|---|---|---|
| Step D 완결 (default_targets를 generic role로) | Rule #1 강화 | 위반 없음 |
| faith_stage_tag → content function | Rule #1 강화 | 위반 없음 |
| Judas scheme motif 추가 검토 | Judas 표현 개선 | 12개 제약 내 허용 |
| Judas canonical fit 개선 (profile 조정) | contrast bench 정밀화 | **Rule #21 위반 우려** — Judas 튜닝 대상 아님. 금지. |
| 3번째 scenario (Talleyrand) profile 추가 | engine 범용성 추가 검증 | 위반 없음 |

내 bias: **Step D 완결 + 3번째 scenario 검증** 이 자연스러운 다음 단계.

---

**End of Step G.**
