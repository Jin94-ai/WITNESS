# Witness "발견(Discovery)" 정의 — v3.0 기준점

> **출처**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) Phase 1 산출물.
>
> **Rule #13 정의**: *"발견(discovery)은 3종으로 분할하여 명시한다. 모든 실험 보고서는 결과가 위 3종 중 어느 것인지 명시해야 한다. '발견'이라는 단어를 분류 없이 사용 금지."*
>
> **이 문서는 v3.0 모든 후속 Phase의 기준점이다.** Phase 2/3/4에서 이 3종 구분을 참조한다. 경계 해석에 이견이 생기면 이 문서가 권위를 가진다 (Lee가 직접 수정하지 않는 한).

---

## 0. 왜 이 문서가 필요한가

Spike 1–6을 관통한 반복 실수 (lessons.md 교훈 42, 패턴 1):

> *"수치가 개선되면 '작동한다' 로 기록. 그 수치가 무엇을 의미하는지 반문하지 않음."*

"발견" 이라는 단어를 분류 없이 쓰면 다음 3종이 섞여 Lee가 결과를 해석할 수 없다:

- (a) **엔진이 정경대로 재생**한 것을 "발견했다" 고 오인
- (b) **규칙 보간**으로 생긴 중간값을 "발견" 이라 주장
- (c) **noise / random variation** 을 "다양성의 증거" 로 해석

Rule #13은 이 혼동을 차단. 이 문서는 Rule #13을 실제로 적용 가능한 **측정 기준**으로 환원한다. 추상 서술 금지 (spec §3.3).

---

## 1. Canonical Reproduction (정경 재생)

### 1.1 정의

**기존 정경에 명시된 인물·사건·행동을, 시뮬레이션이 자발적으로 생성한 경우.**

- 정경 = 개역개정 복음서 본문 (베드로 scope 기준)
- 자발적 = 정경을 hardcode로 주입하지 않았는데 시뮬레이션이 그 사건을 재현
- 재현의 대상은 **행동 자체** (예: 3회 부인) 또는 **순서** (예: 체포 → 부인 → 통곡) 중 하나 이상

### 1.2 측정 방법

**측정 기준 3가지** (하나라도 미달 시 Canonical reproduction 주장 금지):

1. **Action-level match**: 정경이 지정한 action_id가 해당 canonical event tick ±3 window 안에 발생. 측정 도구: `engine/simulation/checkpoint.py`의 `hindcast_check`.
2. **Order preservation**: 정경이 A→B→C 순서로 지정한 사건들이 시뮬레이션 trajectory에서 동일 순서 발생. 측정: event_id 시퀀스 비교.
3. **Spontaneity**: 해당 action이 `canonical_events.json`에 hardcode 되어 있지 않거나, 있더라도 precondition이 state-sensitive해서 **시뮬레이션이 state를 만들어야 fire** 하는 경우. Hardcode force-fire는 자발 아님.

### 1.3 예시 — 무엇이 Canonical reproduction인가

✓ **Canonical reproduction 예시**:
- Seed=42 run에서 tick 163-170에 `deny` 3회 발생. `canonical_events.json`의 denial 이벤트는 `peter_fear ≥ 6` state precondition이 있고, 해당 seed에서 이 조건이 자연스럽게 충족되어 event가 발동한 경우.

✗ **Canonical reproduction 아님 (hardcode 재생)**:
- `canonical_events.json`이 tick 163에 `force: true` 플래그로 `deny`를 강제한 경우. 이건 엔진 출력이지 "발견" 아님.

### 1.4 해당 measurement가 측정하지 않는 것

- **정경에 없는 새 행동** — §3 "Character-consistent novel trajectory" 영역
- **정경에 없지만 모순 안 되는 행동** — §2 "Canon-compatible alternative" 영역
- 엔진이 정경을 단순히 "실행"했는지 여부 — §1.2 criterion 3이 이를 걸러냄

---

## 2. Canon-Compatible Alternative (정경 양립 대안)

### 2.1 정의

**정경에 명시되지 않은 시공간·행동이지만, 정경과 모순되지 않는 경우.**

- 정경은 베드로의 50일을 전부 명시하지 않음 (공백 많음)
- 정경 공백기에 발생한 plausible 행동을 **"정경과 양립한다"** 고 판정 가능
- 핵심: **정경을 침범하지 않는 행동**

### 2.2 측정 방법

Phase 4 Canon Critic (`engine/rubric/canon_critic.py`)이 수행할 hard-constraint 검사 3종:

1. **Anachronism check (시대착오 금지)**:
   - action_id 또는 state transition이 AD 30 Palestine 맥락 밖이 아닌가?
   - 구현: vocabulary allowlist (기존 action_id ∪ canonical content)에 포함된 것만 허용. 신규 action은 content 승인 절차 통과 필요.

2. **Canonical contradiction check (직접 모순 금지)**:
   - 정경이 A 라고 명시한 tick에서 ¬A 발생했는가?
   - 구현: `canonical_events.json`의 "fixed_action" 플래그가 있는 tick에서의 state mismatch 검사.

3. **Theological violation check (신성모독 금지)**:
   - Scripture 재작성 금지 (Rule #2)
   - 예수 Agent의 visible_signal이 개역개정 원문에서 이탈 금지 (Rule #2)

### 2.3 예시 — 무엇이 Canon-compatible alternative인가

✓ **Canon-compatible 예시**:
- 정경에 없는 "tick 77 (수요일 오후)"에 `discuss_with_disciples` 행동 발생. 수요일 오후 베드로의 행동은 정경에 명시 없음. `discuss_with_disciples`는 당시 제자 공동체에서 plausible 행동.

✗ **Canon-compatible 아님 (직접 모순)**:
- 정경 tick 163에 `deny`가 예정되어 있는데 시뮬레이션이 `confess`를 선택. Hard constraint 위반 (Canonical contradiction).

✗ **Canon-compatible 아님 (시대착오)**:
- 베드로가 "coffee 마신다" 같은 action_id 생성 (AD 30 Palestine에 coffee 없음).

### 2.4 해당 measurement가 측정하지 않는 것

- **정경과 일치하는가** — §1 Canonical reproduction 영역
- **인물답게 plausible한가** — §3 Character-consistent 영역 (character critic이 별도 측정)

---

## 3. Character-Consistent Novel Trajectory (캐릭터 일관성 있는 새 경로)

### 3.1 정의

**Canon-compatible (§2) 이면서, 추가로 '베드로답다'고 판정되는 새 trajectory.**

- "베드로답다" = §2를 넘어 **인물 고유의 특성** 보존
- 예: 충동성, 즉각 반응, 두려움-용기 왕복, 예수에 대한 강한 애착
- Canon-compatible이지만 character-inconsistent인 경우 존재 (§2 통과 §3 실패)

### 3.2 측정 방법

Phase 4 Character Critic (`engine/rubric/character_critic.py`)이 수행할 3종 검사:

1. **Impulsivity pattern match**:
   - 베드로 특유의 "즉각 반응 → 후회" 패턴 빈도
   - 구현: 연속 tick 내에서 `[action_A → state_shift → action_B]` sequence 중 "상반된 방향으로 급변"하는 패턴 계수. Baseline (canonical 베드로 trajectory)과 비교.

2. **Relationship-specific response check**:
   - 예수 관련 event → 사랑/두려움/실패의 조합 반응 빈도
   - 적대자 관련 event → 방어적/공격적 반응 빈도
   - 구현: event_id category × action_id category 교차표 비교.

3. **Fear-courage oscillation**:
   - 베드로 특유의 두려움↔용기 왕복. 단조 증가 / 단조 감소가 아닌 oscillation 빈도.
   - 구현: `fear_death` 또는 `fear_isolation` 변수(Phase 2 기준)의 sign change 빈도를 baseline 대비 측정.

### 3.3 예시

✓ **Character-consistent novel trajectory 예시**:
- 정경에 없는 tick 110에 `draw_sword` 후 3 tick 내 `withdraw_in_fear`로 급전환. 베드로의 충동성 + 두려움 패턴 match.

✗ **Canon-compatible but character-inconsistent (§2만 통과, §3 실패)**:
- 정경에 없는 tick 110에 베드로가 "수시간 동안 조용히 기다림". Canon 양립 가능하지만 베드로 특유의 즉각성 부재.

✗ **Novel이지만 canon-incompatible (§2 실패, §3 무의미)**:
- 베드로가 Pilate에게 직접 말 걺. 정경 모순이므로 §3 평가 이전에 §2에서 탈락.

### 3.4 해당 measurement가 측정하지 않는 것

- **인과 설명 가능성** — Phase 4 Causal Critic 영역
- **Novelty 정량** — Phase 4 Novelty Critic 영역

---

## 4. 혼동 방지 — "발견"으로 오해되는 것들

### 4.1 규칙 보간 (Rule interpolation)

**정의**: 엔진의 기존 weight_formula 가 linear combination으로 생성한 중간 상태.

예: `follow_closely.weight = 4.0 + 0.15×love - 0.1×fear`. state (love=8, fear=3)에서 weight=5.0 나옴. 이건 **규칙이 지정한 linear combination**. 새로운 현상 아님.

**판정 기준**: `trajectory[t]`의 action weight을 `weight_formula.compute_weight_breakdown(state, env)` 로 계산했을 때, **모든 term이 규칙에 이미 선언된 것**이면 interpolation. 발견 아님.

### 4.2 Noise / Random variation

**정의**: 동일한 분포에서 나온 다른 샘플.

예: seed=42 vs seed=43 run이 다른 trajectory를 만듦. 두 trajectory의 차이가 engine의 `rng.random()` 호출 결과 차이에서 유래.

**판정 기준**: N개 seed로 ensemble 돌려서 action distribution 측정. 개별 trajectory의 "다름" 이 ensemble mean ± N×std 안에 있으면 noise. 발견 아님.

이 기준은 Spike 6 BC 보고서의 "divergence 20-34%" 를 noise로 분류하기 위한 것. lessons.md 교훈 42 패턴 1 재발 차단.

### 4.3 하드코딩된 사건의 실행 (Hardcoded event firing)

**정의**: `canonical_events.json` 또는 `hazard_events.json`이 특정 tick에 특정 action을 강제 발동하는 경우, 엔진이 그것을 실행한 결과.

예: `scene_09_denial_1`이 "tick 163 ± 3에 `deny` 옵션 제공". 시뮬레이션이 이걸 실행해서 tick 163에 `deny`가 나옴.

**판정 기준**: §1.2 criterion 3 (spontaneity) 실패. Canonical event의 precondition이 state-sensitive이고 실제 state가 그 조건을 자연 충족한 경우만 §1 Canonical reproduction 로 인정.

### 4.4 BC 모델의 흉내 (BC mimicry)

**추가 항목** — Spike 6 경험에서 도출된 새 혼동 요소.

**정의**: Behavior Cloning 신경망이 training set 에 있었던 state-action pair를 val-time에 그대로 재생.

예: v2 MLP 가 `fear=5, hope=8, love=7` state에서 `follow_closely` 를 예측. training set에 같은 분포의 state-action pair가 있었음. 신경망이 학습한 것은 **training set 분포의 lookup table**.

**판정 기준**: Neural model의 val-set 예측이 training set의 nearest-neighbor action과 몇 % 일치하는가. 80%+ 일치하면 mimicry. 발견 아님.

이 기준은 Phase 5+ 에서 신경망이 재도입될 때 적용.

---

## 5. 분류 flowchart (실무용)

실험 trajectory에 대해 아래 순서로 분류:

```
1. Hardcoded event firing 이었나?  →  §4.3  (발견 아님)
       ↓ No
2. Hard constraint (§2.2) 위반?     →  §4.x Invalid (발견 아님, 엔진 버그 가능성)
       ↓ No
3. Canon에 명시?                     →  §1 Canonical reproduction
       ↓ No
4. Rule interpolation / noise?       →  §4.1 / §4.2  (발견 아님)
       ↓ No
5. Canon 양립?                       →  §2 Canon-compatible alternative
       ↓ Yes
6. Character-consistent?             →  §3 Character-consistent novel
       ↓ No
                                     →  §2에서 멈춤 (canon 양립이지만 character drift)
```

이 flowchart를 Phase 4 rubric_evaluator.py에 구현 (spec §6.2). 각 실험 보고서는 이 flowchart를 통과한 분류 레이블을 반드시 기록.

---

## 6. 기존 실험 재분류 (Phase 4에서 수행 예정)

현재 Witness에 기록된 "발견" 주장 3개를 이 3종 분류로 재평가 대기:

| 기존 주장 | 후보 분류 | Phase 4에서 측정 |
|---|---|---|
| Spike 4 "Judas 제거 Cohen's d -46" | §1 Canonical reproduction (정경 상 Judas 없으면 arrest 일어나지 않음)의 *재생*일 가능성 높음 | Canon critic + hindcast_check |
| Spike 5 Part 1 "multi-path 3경로 구조" | §4.1 규칙 보간 (구조는 심었고 작동은 했으나 신경망 판단 아님) | 구조 자체가 규칙이므로 §1–3 해당 없음. 기각 후보 |
| Spike 6 BC "20-34% divergence" | §4.2 Noise 가능성 높음 (val_acc=majority 기반 random sampler 수준) | 이미 세션 4 fidelity 측정에서 noise 실증 |

이 재분류는 **Phase 4에서 수행**. 이번 Phase 1 산출물은 정의 문서만.

---

## 7. Rule #13 준수 검증 체크리스트

모든 후속 실험 보고서가 다음을 포함해야 함:

- [ ] 결과 trajectory 각각에 §1 / §2 / §3 / §4 중 분류 레이블 명시
- [ ] 분류 근거로 §5 flowchart의 step별 답변 (y/n)
- [ ] "발견" 단어 사용 시 해당 분류 레이블과 함께만 사용 ("Canon-compatible alternative 를 발견했다" / "Character-consistent novel trajectory 발견")
- [ ] §4.1–4.4 가능성 명시적 검토 (4개 모두 기각 후에만 §1–3 주장)

이 체크리스트 미준수 보고서는 Rule #13 위반. `scripts/audit_report.py` 확장해서 자동 검증 예정 (Phase 4에서 구현).

---

## 8. 기존 Rule과의 관계

| Rule | 이 문서와의 관계 |
|---|---|
| Rule #5 (용어 과장 금지) | §4.1–4.4 는 Rule #5를 구체화 — "phase transition"처럼 "발견" 도 오용 금기 |
| Rule #13 (발견 3종 분할) | 이 문서가 Rule #13의 구체 정의 |
| Rule #14 (학습 reward ≠ 평가 rubric) | Phase 4 rubric 측정이 이 정의 위에서 작동 |
| HARNESS H1 (수치 개선 = 본질 개선 착각) | §4.1–4.4 가 H1의 null hypothesis 가이드 |

---

## 9. Phase 1 완료 체크리스트 (spec §3.3)

- [x] `docs/witness_discovery_definitions.md` 작성
- [x] 3종 발견 각각에 측정 방법 명시 (§1.2 / §2.2 / §3.2)
- [x] 추상 서술 금지 — 각 측정은 구현 가능한 도구/벡터/파일 경로 명시
- [x] 혼동 방지 항목 §4에 4종 (spec 요구 3 + 추가 1)
- [x] 분류 flowchart §5 (Phase 4 rubric_evaluator 구현 대상)
- [ ] Lee 확인: "앞으로 실험 결과를 이 3종으로 분류 가능" 판단 ← **대기**
- [x] 코드 변경 0 (spec §3.4 준수)

---

## 10. 한 줄 요약

**"'발견' 은 Canonical reproduction / Canon-compatible alternative / Character-consistent novel trajectory 중 하나이며, 각각 측정 도구가 다르다. Rule interpolation / noise / hardcoded firing / BC mimicry 는 발견 아니다."**
