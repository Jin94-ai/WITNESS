# Phase 4 §6.5 — 이전 "발견" 주장의 Rubric 재평가

**작성:** 2026-04-23
**범위:** WITNESS_V3_REDESIGN.md §6.5 "이전 발견 주장들을 rubric으로 재평가"
**대상:** Spike 4 (Judas 제거 실험), Spike 6 (BC 결과)

---

## 0. 왜 이 재평가인가

Rule #13 (v3 REDESIGN §1.3) 에 따라 "발견"은 3종으로 분할 + 3종 "비발견":

- **CANONICAL_REPRODUCTION** — 정경 시퀀스 재현
- **CANON_COMPATIBLE_ALTERNATIVE** — 정경 불위반 + 다른 경로
- **CHARACTER_CONSISTENT_NOVEL** — 성격 일관 + 경로 신규

- **NOT_DISCOVERY_HARDCODED** — 직접 주입된 결과
- **NOT_DISCOVERY_INTERPOLATION** — 학습 데이터 내삽
- **NOT_DISCOVERY_NOISE** — 무작위 변이

이전 "positive 증거" 라 주장된 결과들이 어디에 해당하는가?

---

## 1. Spike 4: Judas 제거 실험

### 1.1 원 주장

*"Judas를 제거하면 체포 이벤트 확률이 100%에서 0%로 떨어진다. Cohen's d =
-6.87, permutation p<0.001. 이는 Judas가 구조적으로 필수 노드임을 증명."*

### 1.2 Rubric 재평가

**쟁점:** 이것이 Rule #13 "발견"의 어느 category인가?

| 후보 class | 적합성 | 이유 |
|---|---|---|
| CANONICAL_REPRODUCTION | **N/A** | 재현이 아니라 *제거* 실험. 비정경 궤적 |
| CANON_COMPATIBLE_ALTERNATIVE | **X** | 정경은 체포 발생. 체포 0% = 정경 충돌 |
| CHARACTER_CONSISTENT_NOVEL | **X** | 인물 성격의 trajectory 아니라 *설계 조작* |
| NOT_DISCOVERY_HARDCODED | **X** | 체포 확률은 hazard에서 emerg, 직접 코딩 아님 |
| NOT_DISCOVERY_INTERPOLATION | **X** | 훈련 데이터 사용 안 함 (rule-based) |
| NOT_DISCOVERY_NOISE | **X** | d=-6.87 은 비무작위 |

**결론:** Rule #13 category에 **해당하지 않음**. 이것은:

> **Methodological counterfactual** (방법론적 반사실 실험). Discovery가 아니라
> model의 **구조 분석**. Rule #13의 대상은 "trajectory 자체의 class" 이나,
> Judas 제거는 trajectory 생성 조건의 *조작*.

### 1.3 교정된 해석 (H1)

**과거 주장:** "Judas 구조적 필수성 증명."
**정직한 해석:** "우리가 만든 모델 내에서 Judas 노드가 체포 이벤트의 유일한
trigger이다. 다른 모델에서는 다른 답이 나올 수 있다."

Trivial explanation: 체포 이벤트는 Judas-linked trigger로 *우리가 코딩했다*.
제거하면 trigger 사라짐 → 체포 0%는 필연. Cohen's d=-6.87 은 "우리 코드가
자기 코드를 따른다"는 확인.

**Null hypothesis (H1):** "모델 내 Judas 제거 시 체포 0% 는 모델의 hardcoded
의존성 때문" — **기각하지 못함**.

**재분류:** NOT_DISCOVERY_HARDCODED의 **조건부 형태** — trigger 의존성은
코드로 정의되므로, 제거 시 효과는 코드 정의에 따른 결과.

---

## 2. Spike 6: BC (Behavioral Cloning) 결과

### 2.1 원 주장

Spike 6에서 BC 모델이 Peter trajectory를 학습하여 **"positive 증거"**로
간주됨. Lee의 7-패턴 자기반성에서 이 용어가 구체적으로 지적되어 HARNESS H1이
도입됨.

### 2.2 Rubric 재평가

| 후보 class | 적합성 |
|---|---|
| CANONICAL_REPRODUCTION | **부분** — BC가 canonical trajectory 를 재현했다면 맞지만, "발견" 아님 |
| CANON_COMPATIBLE_ALTERNATIVE | **X** — BC는 학습 데이터에 의존, 정경과 별개 |
| CHARACTER_CONSISTENT_NOVEL | **X** — BC는 novel 아님 |
| **NOT_DISCOVERY_INTERPOLATION** | **O** — BC는 훈련 데이터 내삽 |
| NOT_DISCOVERY_HARDCODED | 조건부 — 학습 데이터가 hardcoded canonical이면 |
| NOT_DISCOVERY_NOISE | X — 학습은 noise 아님 |

**결론:** **NOT_DISCOVERY_INTERPOLATION** 확정.

### 2.3 교정된 해석 (H1)

**과거 주장:** "BC 모델이 Peter 행동을 학습했다 = positive 증거."
**정직한 해석:** "BC 모델은 훈련 데이터를 interpolate. 훈련 데이터가 Peter
trajectory 이므로 BC 출력이 Peter trajectory와 유사한 것은 **정의상 성립**.
새로운 정보 없음."

Trivial explanation: BC는 $L_{train} = -\log p(\text{action} | \text{state})$
를 최소화. 훈련 데이터에 맞추도록 설계된 함수가 훈련 데이터에 맞음은 학습의
정의.

**Null hypothesis (H1):** "BC 출력이 Peter와 유사함은 훈련 목적 자체" —
**기각하지 못함**.

**재분류:** **NOT_DISCOVERY_INTERPOLATION** (confirmed)

---

## 3. v3 Phase 2 v2 현재 실측도 재평가

### 3.1 Peter seed=0 ticks=30 (B2 + Cat F + primitive decay 적용)

| 지표 | 값 |
|---|---|
| canon_valid | True |
| canon_soft_drift | 25.30 (10-seed mean, σ=1.16) |
| character_composite | 0.949 (10-seed mean, σ=0.022) |
| novelty_band | **noise (10/10 seeds)** |
| DiscoveryClass | **NOT_DISCOVERY_NOISE (10/10)** |

**분류:** **NOT_DISCOVERY_NOISE** in all 10 seeds.

**재분류 근거:** drift > noise_threshold (20.0 임의). `character_consistent_novel`
가 되려면 drift < noise_threshold + 다른 조건. 현재 미달.

**단 threshold 20.0 자체가 arbitrary** (§Dynamics §13 금지 영역). 수치 조작 없이
자연스러운 class 획득은 future work.

### 3.2 Judas seed=0 ticks=30 (engine universality test)

| 지표 | 값 |
|---|---|
| canon_valid | True |
| canon_soft_drift | 32.00 |
| character_composite | 0.879 |
| novelty_band | noise |
| DiscoveryClass | **NOT_DISCOVERY_NOISE** |

**분류:** NOT_DISCOVERY_NOISE.

**핵심 발견:** drift 32 > Peter's 25.30 → Policy + edges가 Peter-tuned.
Judas-specific retune 없이는 동급 수준 불가.

→ CLAUDE.md Rule #5 의 *"engine is scenario-agnostic; patterns are
scenario-specific"* 원칙 **실증 확인**. 같은 engine, 다른 content, 다른 drift.

---

## 4. 요약: 지금까지 Witness 프로젝트의 "발견" Ledger

| 실험 | 원 주장 | Rubric 재분류 | 정직한 해석 |
|---|---|---|---|
| Spike 4 Judas 제거 | "구조적 필수성 증명" | methodological counterfactual (Rule #13 범위 밖) | 모델 내 하드코딩 trigger 의존성 |
| Spike 6 BC | "positive 증거" | NOT_DISCOVERY_INTERPOLATION | 훈련 데이터 interpolation |
| v3 Peter (current) | (no discovery claim) | NOT_DISCOVERY_NOISE | drift > arbitrary threshold |
| v3 Judas (current) | (no discovery claim) | NOT_DISCOVERY_NOISE | policy Peter-tuned confirmed |
| POM Peter all-pass 47.5% | "패턴 재현 성공" | 별개 validation framework | Rubric 적용 대상 아님 |
| Counterfactual d=-6.87 | "causal evidence" | methodological 범위 | 위와 동 |

**현재까지 Witness가 얻은 Rule #13 범주의 실제 "발견" 건수: 0.**

(이것은 프로젝트 실패 신호가 **아님**. Rule #13 은 매우 엄격하며, 진정한
NOVEL trajectory는 drift-novelty balance가 어려움. 현재 phase의 중요한
산물은 "**분류 도구 자체의 완성**" 이다.)

---

## 5. HARNESS 자가감사

### H1. Null hypothesis

- Spike 4: "trigger 의존성은 코드 정의로 필연" → 기각 못함 → HARDCODED 조건부
- Spike 6: "BC = 훈련 데이터 interpolation" → 기각 못함 → INTERPOLATION
- v3 현재: "drift > 20은 structural 특성 (10/10 seeds 일관)" → 기각 못함 → NOISE

### H4. What could still be wrong

- Rule #13의 **threshold 자체**가 임의 (noise 20.0, copy 2.0, reproduction 3.0)
- "noise" 분류는 threshold 변경 시 뒤집힘
- Peter 현재 drift 25.30 이 다른 threshold (예: 30) 에서는 CHARACTER_CONSISTENT_NOVEL
- 따라서 **현재 분류는 현재 threshold 하에서만 유효**

### H7. 금지어 체크

- "Positive evidence" (Spike 6) — **이 문서에서 공식 철회**
- "Discovery" (Spike 4) — 조건부 철회 (methodological counterfactual로 재명명)
- "Structural necessity" → "hardcoded trigger dependency" 로 교정

---

## 6. 결론

**Phase 4 §6.5 완료.**

- 이전 주장 2개 (Spike 4, 6) 모두 Rule #13 재분류
- 현재 실측도 Rule #13 분류 (Peter/Judas 모두 NOT_DISCOVERY_NOISE)
- **진정한 "discovery" 1건도 아직 없음** (Ledger §4)
- 이 사실 자체가 Rubric 도구의 엄격성을 보여주는 positive 결과

**다음 실제 "discovery" 후보 조건:**
- drift < noise_threshold (20.0 기본)
- canon_valid = True (hard 위반 없음)
- character_composite > 0.4
- 훈련 데이터 없는 rule-based 생성

현재 distance to reach: drift 25.30 → 20. 정책 fitting 없이는 어려움.

Alternative: threshold 자체를 **sample distribution 기반으로 재정의** (후순위,
§13 threshold 보정 영역).

---

**End of retrospective rubric classification.**
