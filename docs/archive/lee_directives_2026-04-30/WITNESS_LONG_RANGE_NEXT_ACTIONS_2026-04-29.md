# WITNESS Long-Range Next Actions — after Renderer Gate 1 v2 + Branch C 18-Probe Bundle

**Date:** 2026-04-29  
**Prepared as:** Lee decision + long-range execution roadmap  
**Inputs:**
- `RENDERER_DIAGNOSIS_GATE1_V2_BUNDLE.md`
- `BRANCH_C_18_PROBES_SEND_BUNDLE.md`
- prior Full N=12 combined result

---

## 0. Executive decision

지금 WITNESS는 두 개의 gate 앞에 있다.

1. **Renderer Gate** — WITNESS가 creative output으로 읽히는가?
2. **Branch C External Gate** — configuration variation이 outcome divergence를 만든다는 주장이 외부 판독에서도 보이는가?

내 결정은 다음과 같다.

> **Branch C 18-probe external eval은 즉시 진행한다.**  
> **Renderer는 Cycle 2를 거친 뒤 creative asset pack으로 넘어간다.**  
> **Branch C가 통과해도 renderer v2가 개선되기 전까지는 public-facing narrative 확장은 보류한다.**

---

## 1. 현재 상태 판단

### 1.1 Branch C 쪽

현재 준비된 18-probe bundle은 외부 평가용으로 충분히 정리되어 있다.

강점:

- 18개 모두 annotated v3 format
- probe ID는 P_NEW_01~18로 익명화
- scenario / cast / placement를 blind infer하도록 설계
- single-seed 한계와 ±33pp bias disclosure가 명시되어 있음
- GPT-5.5에 보낼 §A와 Lee private note §B가 분리되어 있음
- post-eval PASS 기준 5개가 명확함

따라서 이 bundle은 **그대로 GPT-5.5 새 채팅에 보낼 수 있다.**

주의:

- §B는 절대 보내지 않는다.
- 응답 raw는 `BRANCH_C_GPT55_RESPONSE_RAW.md`로 저장한다.
- 통과 여부는 감으로 보지 말고 B.3의 5개 기준으로 판정한다.

---

### 1.2 Renderer 쪽

Renderer Gate 1 v2는 **부분 통과**다.

- P6 MIXED scarcity: 좋음
- Trilogy modal: 좋음
- P9 SAT scarcity: flat/report-like
- P10 REC accusation: scenario tone 약함
- P_PV_09 LOW_ACTIVITY: fail

즉, renderer는 “구조를 문장으로 옮기는 능력”은 있지만, 아직 outcome별 / scenario별 문학적 호흡이 충분히 분리되지 않았다.

Renderer는 바로 확장하지 말고 **Cycle 2 patch**가 필요하다.

---

## 2. 즉시 진행 — Day 0

### 2.1 Branch C 18-probe eval 발송

실행:

1. `BRANCH_C_18_PROBES_SEND_BUNDLE.md` 열기
2. §A 전체를 GPT-5.5 새 채팅에 paste
3. §B는 보내지 않음
4. 응답 raw text 저장

저장 파일:

```text
BRANCH_C_GPT55_RESPONSE_RAW.md
```

그다음 분석 파일:

```text
BRANCH_C_EXTERNAL_EVAL_ANALYSIS.md
```

분석해야 할 기준:

| Criterion | PASS condition |
|---|---|
| Within-scenario divergence detected | ≥2 distinct outcomes in ≥2 of 3 scenario groups |
| Configuration sensitivity verdict | STRONG or MODERATE |
| Q2a typing accuracy vs GT | ≥15/18 |
| Final summary self-call vs GT | ≥12/18 |
| Q3b world-side axes positive | ≥3 of 5 axes selected on majority of probes |

판정:

- 4~5 PASS: Branch C external validation 성공
- 2~3 PASS: Branch C hold, 추가 evidence 필요
- 0~1 PASS: Branch C claim 약함, 구조/format 재검토

---

### 2.2 Renderer Cycle 2 계획 파일 작성

생성 파일:

```text
docs/creative/RENDERER_CYCLE_2_PLAN.md
```

필수 포함:

1. stock phrase 제거
2. outcome별 rhythm 분리
3. LOW_ACTIVITY 전용 branch
4. before/after 비교 기준
5. Gate 1 v3 재평가 양식

---

## 3. Short term — Day 1~3

### 3.1 Renderer Cycle 2 patch

구현 우선순위:

#### Patch A — phrase de-template

목표:

- 반복 phrase pool 제거 또는 확장
- 같은 위치에 같은 문장이 반복되지 않게 함
- conclusion / transition / authority motif 문장을 outcome별로 분기

수정 대상 예시:

```text
그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.
며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다.
권위의 시선도 거두어지지 않았다.
```

#### Patch B — outcome rhythm control

Outcome별 문장 호흡:

| Outcome | 문장 리듬 |
|---|---|
| RECOVERY_DOMINATED | 점점 열리는 호흡, 문장 길이 증가 |
| SATURATION_DOMINATED | 짧고 닫히는 문장, 제자리 반복 |
| MIXED | 두 공간/두 집단 대비, 교차 구조 |
| PARTIAL | 회복과 잔류의 불완전한 균형 |
| LOW_ACTIVITY | 부재의 긴장, 미발화된 사건 |

#### Patch C — LOW_ACTIVITY renderer branch

LOW_ACTIVITY는 “짧은 이야기”가 아니라 “사건이 되지 못한 징후”로 처리한다.

구성:

1. 작은 징후
2. 확산되지 않는 소문
3. 반응하지 않는 사람들
4. 감시하지만 개입하지 않는 authority
5. 아무 일도 일어나지 않았기 때문에 남는 불편함

---

### 3.2 5 sample 재생성

재생성 대상:

1. P6 MIXED scarcity
2. Scarcity Trilogy modal 3-act
3. P9 SAT scarcity
4. P10 REC accusation
5. P_PV_09 LOW_ACTIVITY

저장:

```text
docs/creative/renderer_gate1_v3_samples.md
```

---

### 3.3 Gate 1 v3 평가

평가 기준:

| Metric | Target |
|---|---|
| good | ≥3/5 |
| bad | 0/5 |
| report-like | ≤1/5 |
| flat | ≤1/5 |
| LOW_ACTIVITY | at least salvageable |

통과 조건:

- 최소 3/5 good
- LOW_ACTIVITY가 bad에서 벗어남
- P9 SAT이 report-like에서 벗어남
- P10 REC accusation이 scenario tone을 가짐

---

## 4. Mid term — Week 1

### 4.1 Branch C 결과에 따른 분기

#### Case B — Strong positive, 4~5 PASS

생성:

```text
docs/b_direction/BRANCH_C_LOCK_DECISION.md
```

내용:

- 외부 판독에서 within-scenario divergence가 보였는가
- Q2a typing이 충분히 맞았는가
- final summary self-call이 GT와 충분히 맞았는가
- world-side axes가 읽혔는가
- single-seed limitation을 어떻게 제한적으로 해석할 것인가

결정:

> Branch C locked as validated direction, but magnitude claims remain cross-seed-qualified.

다음:

- creative asset pack 준비
- configuration dynamics explainer 작성
- public-facing narrative는 renderer v3 통과 후 진행

#### Case C — Ambiguous, 2~3 PASS

생성:

```text
docs/b_direction/BRANCH_C_HOLD_AND_RETEST_PLAN.md
```

다음 작업:

- 18-probe bundle을 5-seed modal basis로 재구성
- single-seed bias를 줄인 새 blind set 생성
- Q3b world-side가 약하면 headline field 보강

결정:

> Branch C remains promising but not locked.

#### Case D — Weak, 0~1 PASS

생성:

```text
docs/b_direction/BRANCH_C_NEGATIVE_RESULT_REVIEW.md
```

다음 작업:

- configuration claim 축소
- world-side mechanism 재검토
- renderer보다 structure diagnosis 우선

결정:

> Do not expand Branch C. Return to mechanism or measurement review.

---

### 4.2 Renderer 결과에 따른 분기

#### Renderer v3 PASS

조건:

- 3/5 good 이상
- bad 0
- LOW_ACTIVITY salvage 이상

다음:

```text
docs/creative/WITNESS_CREATIVE_ASSET_PACK_PLAN.md
```

포함:

- 3 scenario trilogy
- outcome contrast samples
- configuration-sensitive narrative pairs
- before/after diagrams
- short-form blog/video scripts

#### Renderer v3 PARTIAL

다음:

```text
docs/creative/RENDERER_CYCLE_3_PLAN.md
```

Cycle 3는 style polish가 아니라:

- scene-level agency
- named motif continuity
- local action beats
- narrator distance control

#### Renderer v3 FAIL

다음:

```text
docs/creative/RENDERER_CORE_REPAIR_PLAN.md
```

이 경우 creative 확장은 중지.

---

## 5. Strategic roadmap — Weeks 2~4

### 5.1 If Branch C PASS + Renderer PASS

이 경우 WITNESS는 다음 단계로 간다.

#### Product direction

```text
WITNESS = configuration-sensitive social narrative simulator
```

산출물:

1. **Branch C explainer**
   - 같은 scenario라도 cast/placement에 따라 outcome이 달라짐
   - 단일 사건이 아니라 구조가 결말을 만든다는 메시지

2. **Creative asset pack v1**
   - scarcity trilogy
   - accusation divergence pair
   - sacred low-activity vs recovery contrast

3. **Public demo narrative**
   - “같은 사건, 다른 자리, 다른 결말”
   - 3분 영상/블로그/슬라이드로 전환 가능

4. **Technical appendix**
   - 18-probe external eval
   - N=12 true combined result
   - cross-seed limitation note

---

### 5.2 If Branch C PASS + Renderer PARTIAL/FAIL

이 경우 방향은 검증됐지만 표현이 부족한 상태다.

결정:

> Science/structure validated, creative release delayed.

다음:

- renderer repair 우선
- public-facing creative는 보류
- 내부 technical doc만 정리

산출물:

```text
docs/b_direction/BRANCH_C_VALIDATED_RENDERER_HOLD.md
docs/creative/RENDERER_REPAIR_BACKLOG.md
```

---

### 5.3 If Branch C AMBIGUOUS + Renderer PASS

이 경우 문학적 출력은 좋아졌지만 claim이 약한 상태다.

결정:

> Creative artifact possible, but Branch C scientific claim must be softened.

표현:

- “configuration-dependent dynamics”라고 강하게 말하지 않음
- “configuration-sensitive possibilities” 정도로 낮춤
- 외부 공개 시 실험적 narrative engine으로 소개

---

### 5.4 If Branch C FAIL + Renderer FAIL

중단.

결정:

> Do not expand. Return to core mechanism review.

작업:

- kernel mechanism audit
- Q-set review
- annotated format 목적 재정의
- renderer 폐기 또는 재설계

---

## 6. Long term — Month 1~2

### 6.1 World expansion 조건

`world/`, `docs/world/`, `data/person/*`는 아직 열지 않는다.

열 수 있는 조건:

1. Branch C external validation 4/5 PASS
2. Renderer v3 3/5 good 이상
3. Creative asset pack v1 설계 완료
4. Lee가 별도 directive 부여

그 전까지는 world expansion 금지.

---

### 6.2 Public-facing formats

Branch C와 Renderer가 모두 통과하면 다음 포맷으로 확장한다.

#### Blog

주제:

- 같은 사건이 왜 다른 결말을 낳는가
- 사회적 감정은 개인이 아니라 배치에서 발생한다
- WITNESS는 이야기인가, 시뮬레이션인가

#### YouTube

가능한 제목:

- 같은 비난, 다른 결말
- 사람은 같아도 자리가 바뀌면 이야기가 바뀐다
- AI로 사회적 감정의 흐름을 시뮬레이션해봤다

#### Demo deck

구성:

1. 문제 제기
2. simulation setup
3. 3 scenarios
4. 18-probe divergence
5. narrative renderer output
6. limitation
7. next experiment

---

## 7. File creation checklist

### Immediate files

- [ ] `BRANCH_C_GPT55_RESPONSE_RAW.md`
- [ ] `BRANCH_C_EXTERNAL_EVAL_ANALYSIS.md`
- [ ] `docs/creative/RENDERER_CYCLE_2_PLAN.md`

### After renderer patch

- [ ] `docs/creative/renderer_gate1_v3_samples.md`
- [ ] `docs/creative/RENDERER_GATE1_V3_RESULTS.md`

### If Branch C passes

- [ ] `docs/b_direction/BRANCH_C_LOCK_DECISION.md`
- [ ] `docs/b_direction/BRANCH_C_EXTERNAL_VALIDATION_SUMMARY.md`

### If renderer passes

- [ ] `docs/creative/WITNESS_CREATIVE_ASSET_PACK_PLAN.md`
- [ ] `docs/creative/WITNESS_CREATIVE_ASSET_PACK_V1.md`

### If both pass

- [ ] `docs/WITNESS_PUBLIC_DEMO_PLAN.md`
- [ ] `docs/WITNESS_ONE_PAGE_POSITIONING.md`
- [ ] `docs/WITNESS_LIMITATIONS_AND_CLAIMS.md`

---

## 8. Final operating principle

앞으로의 기준은 하나다.

> **Branch C는 구조의 검증이고, renderer는 전달의 검증이다. 둘 중 하나만 통과해도 부족하다.**

따라서 다음 순서는:

1. Branch C 18-probe external eval 실행
2. Renderer Cycle 2 patch
3. Renderer Gate 1 v3 재평가
4. Branch C PASS 여부 확정
5. 둘 다 통과할 때만 creative asset pack / public demo로 이동

---

## 9. Lee final call

**나는 지금 Branch C 검증을 멈추지 않는다.**  
**하지만 renderer는 아직 공개용이 아니라고 본다.**

그래서 결정은 다음과 같다.

```text
Branch C external eval: GO
Renderer creative expansion: HOLD
Renderer Cycle 2: GO
World expansion: HOLD until separate directive
Public asset pack: HOLD until Branch C + Renderer both pass
```
