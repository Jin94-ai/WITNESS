# WITNESS — 루프 종료 후 정리 및 다음 단계 작업지시서

## 0. 문서 목적

이 문서는 WITNESS B-direction WORLD_FLOW_LOOP를 충분히 반복한 이후,  
추가 iteration을 바로 진행하지 않고 **정리(freeze + audit + decision)** 단계로 전환하기 위한 작업지시서다.

현재 상태의 핵심 판단은 다음과 같다.

- 루프는 충분히 많이 돌았다
- 추가 반복보다 해석 피로와 미세 회로 집착 위험이 커졌다
- 지금 필요한 것은 더 많은 iteration이 아니라 **무엇이 확실한지 / 무엇이 불확실한지 / 무엇을 버릴지**를 정리하는 것
- 정리 완료 후에야 다음 단계(확장, 혼합 시나리오, readability-facing phase, broader world phase 등)로 넘어갈 수 있다

---

## 1. 현재 상태에 대한 판단

### 1.1 현재 시점의 핵심 문제
지금은 다음 문제가 동시에 존재한다.

1. **구조는 많이 발전했지만 해석 안정성은 아직 완전히 수렴하지 않음**
2. **특정 메커니즘(예: Phase 2a / shame / confess feedback)에 대한 drilling 비중이 너무 커짐**
3. **engine-internal metric과 mechanism explanation이 앞서고, external readability는 뒤처짐**
4. **decoupled state / dormant event / inert field 정리가 아직 완전히 끝나지 않음**
5. **다음 루프를 계속 돌릴 경우 “새 발견”보다 “더 정교한 설명 과잉”이 나올 위험이 큼**

### 1.2 따라서 지금 해야 할 일
지금은 다음을 해야 한다.

- 현재 kernel을 **freeze**
- 현재까지의 결과를 **확실한 것 / 불확실한 것 / 제거 후보**로 분리
- external readability blind를 수행
- inert / reserve audit 수행
- mixed-arc 최소 probe 수행
- 그 결과를 바탕으로 다음 단계 진입 여부를 결정

---

## 2. 절대 원칙

### 원칙 1 — 당분간 새 iteration 금지
정리 단계가 끝나기 전까지 Iter 90+ 스타일의 추가 루프를 금지한다.

### 원칙 2 — Phase 2a 추가 drilling 금지
다음과 같은 작업은 정리 단계 동안 금지한다.

- shame multiplier 세밀 스윕
- Phase 2a 내부 추가 미세 튜닝
- confess feedback 추가 drilling
- single-seed 기반 fine adjustment

### 원칙 3 — 새 구조 대량 추가 금지
정리 단계 동안 다음을 금지한다.

- 새 레이어 대량 추가
- 새 변수 대량 추가
- neural policy probe 시작
- 새 scenario 대량 추가
- universality 주장 강화

### 원칙 4 — 정리와 검증을 분리
이번 단계의 목표는 구조 성능 개선이 아니라 **구조 상태 정리와 다음 단계 전환 판단**이다.

---

## 3. 정리 단계에서 해야 할 일

# Step A — Kernel Freeze

## 목표
현재 구조를 하나의 기준점으로 고정한다.  
무엇이 최근 패치인지, 무엇이 현재 기본 구조인지 흐려지는 것을 막는다.

## 작업
1. 현재 kernel snapshot 고정
2. active toggles / default toggles 기록
3. 현재 실험에 사용되는 scenario 목록 기록
4. 현재 probe / metric / label 정의 기록
5. 현재 component ledger 버전 고정

## 산출물
- `docs/b_direction/FREEZE_STATE.md`
- `data/b_direction/freeze_snapshot/`
- `docs/b_direction/FREEZE_COMPONENTS.md`

## 포함해야 할 항목
- active scenario list
- active world processes
- active motif classes
- active role priors
- active feedback loops
- known dormant / decoupled components

---

# Step B — “확실한 것 / 불확실한 것 / 제거 후보” 분리

## 목표
현재까지 나온 발견을 계층화한다.  
이 단계가 없으면 다음 단계에서 다시 해석 혼선이 반복된다.

## 분류 체계

### B-1. 확실한 것 (Verified)
반복 실험, cross-seed, code inspection, instrumentation까지 통과한 것

예시 형식:
- claim
- evidence type
- scope
- caveat

### B-2. 불확실한 것 (Open / unresolved)
부분 증거만 있거나, external readability / mixed-arc / cast combinatorics 등으로 아직 미완인 것

### B-3. 제거 후보 (Remove / reserve / dormant)
반복적으로 inert, decoupled, dormant로 보이는 것

## 작업
모든 현재 claim을 아래 셋 중 하나로 분류한다.

- VERIFIED
- OPEN
- REMOVE_CANDIDATE / RESERVE

## 산출물
- `docs/b_direction/CLAIM_STATUS_MATRIX.md`

## 문서 형식 예시
| Claim | Status | Evidence | Scope | Caveat |
|---|---|---|---|---|
| Phase 2a는 현재 3/3 시나리오 recovery 핵심 채널 | VERIFIED | code + N=5 + 3 scenarios | current kernel only | diversity는 미검증 |
| readability exists | OPEN | 없음 | n/a | human blind 필요 |
| authority_vigilance field | REMOVE_CANDIDATE | inert audit | current kernel | empirical removal 필요 |

---

# Step C — External Readability Blind

## 목표
현재 엔진이 만들어내는 흐름이 외부에서도 “읽히는 세계”인지 확인한다.

## 배경
현재까지의 검증은 대부분 engine-internal metric과 mechanism-level explanation이었다.  
B-direction의 다음 단계로 가려면 **외부 판독 가능성**이 필요하다.

## 작업
1. story probe 12~20개 선정
2. scenario / seed / metric / label 숨김
3. 외부 평가자 또는 최소 Lee blind reading 수행
4. 아래 질문으로 평가

## 질문 세트
1. 이 probe는 랜덤 로그처럼 보이나, 어떤 흐름이 느껴지나?
2. 어떤 압력(예: shame, fear, sacred, scarcity)이 중심처럼 보이나?
3. 관계 변화나 군중/권위 변화가 느껴지나?
4. recovery 또는 escalation arc가 읽히나?
5. oscillation이 의미 있는 반복처럼 보이나, 그냥 흔들림처럼 보이나?

## 결과 기록 형식
- readable / partially readable / unreadable
- dominant perceived pressure
- perceived arc label
- confusion notes

## 산출물
- `docs/b_direction/READABILITY_BLIND_PROTOCOL.md`
- `docs/b_direction/READABILITY_BLIND_RESULTS.md`

## 주의
- 내부 metric을 읽힌 뒤 판정하지 말 것
- 먼저 읽고, 나중에 ground truth 대조할 것

---

# Step D — Inert / Reserve Audit

## 목표
현재 ontology / event / field / state 중 실제로 구조에 기여하지 않는 요소를 정리한다.

## 배경
지금은 decoupled states, dormant events, inert field가 누적되어 있을 가능성이 크다.  
정리 없이 다음 단계로 가면 설계 부채만 늘어난다.

## 작업 대상

### D-1. state fields
예:
- moral_injury
- identity_shift
- trust_scar
- event_trauma
- breach_count
- awe 등 현재 suspect 대상 전체

### D-2. events
- registered but no consumer
- produced but practically irrelevant
- one-shot decorative event

### D-3. fields / layers
- authority_vigilance
- narrative-field suspects
- climate variants
- other low-effect components

## 테스트 형식
각 대상마다 최소 아래 4개를 본다.

1. high injection
2. zero clamp
3. remove
4. downstream motif / event / long-horizon effect 확인

## 분류 결과
- KERNEL
- SUPPORT
- RESERVE
- DORMANT
- REMOVE

## 산출물
- `docs/b_direction/INERT_RESERVE_AUDIT.md`
- `docs/b_direction/COMPONENT_LEDGER.md` 업데이트

---

# Step E — Mixed-Arc Minimal Probe

## 목표
현재 kernel이 단일 crisis/recovery 회로에만 강한지, 혼합 압력장에서 버티는지 확인한다.

## 배경
지금까지는 각각 비교적 분리된 scenario에서 메커니즘을 확인한 성격이 강하다.  
진짜 세계는 압력장이 겹친다.

## 이번 단계의 mixed-arc 목표
새 발견을 만드는 것이 아니라, **현재 kernel이 섞인 조건에서도 읽히는가**를 보는 것이다.

## 최소 probe 2개
1. accusation + sacred overlap
2. scarcity + private grief overlap

## 확인 항목
- 한 pressure family가 다른 pressure를 완전히 죽이는가
- mixed arc가 전혀 안 나오고 single-loop collapse로 가는가
- relation / world memory가 교차 반응하는가
- readability가 오히려 나아지는가 / 나빠지는가

## 산출물
- `docs/b_direction/MIXED_ARC_PROBE.md`

---

## 4. 정리 단계에서 하지 말아야 할 것

### 금지 1
Iter 90+ 스타일의 새로운 미세 반복 즉시 재개

### 금지 2
Phase 2a / shame / confess feedback 미세 조정

### 금지 3
새 변수 / 새 레이어 추가

### 금지 4
Neural policy probe 시작

### 금지 5
“이제 universality 됐다” 류 주장

### 금지 6
single seed 기반 큰 결론

---

## 5. 정리 완료 기준

아래 6개가 충족되어야 정리 단계 완료로 본다.

### 조건 1
현재 kernel snapshot이 freeze 상태로 기록되었다

### 조건 2
모든 주요 claim이 VERIFIED / OPEN / REMOVE_CANDIDATE로 분류되었다

### 조건 3
external readability blind가 최소 1회 수행되었다

### 조건 4
inert / reserve audit가 완료되어 component ledger가 업데이트되었다

### 조건 5
mixed-arc minimal probe 2개가 수행되었다

### 조건 6
다음 단계 진입 여부를 결정할 수 있을 정도로 “확실한 것 / 불확실한 것 / 버릴 것”이 분명해졌다

---

## 6. 정리 끝난 뒤 다음 단계에서 해야 할 것

정리 단계가 끝났다고 바로 expansion으로 가는 것은 아니다.  
정리 결과에 따라 다음 단계는 분기된다.

---

# Branch A — Readability-facing Phase

## 진입 조건
- external readability blind에서 최소한 일부 probe가 readable / partially readable
- mixed-arc에서도 arc-like 흐름이 감지됨
- current kernel이 완전히 단일 회복 회로에만 갇혀 있지 않음

## 다음 작업
1. story probe format 표준화
2. readability rubric 초안 작성
3. agent-level motif 흐름 → human-readable narrative field 매핑
4. oscillation을 narrative arc로 읽을 수 있는지 점검
5. 외부 독자 추가 blind reading

## 목표
“잘 도는 엔진”에서 “읽히는 세계”로 넘어가기

---

# Branch B — Kernel Simplification Phase

## 진입 조건
- readability 낮음
- mixed-arc에서 collapse가 많음
- inert / reserve component가 다수 확인됨
- recovery가 지나치게 단일 회로 의존

## 다음 작업
1. inert field 제거
2. reserve field late-binding 전환
3. Phase 2a 외 보조 recovery path 최소 1~2개 탐색
4. role prior / shame / confess feedback dependence 재축소
5. 구조 단순화 후 다시 micro-world probe

## 목표
복잡한 엔진이 아니라 **더 단단한 최소 kernel** 만들기

---

# Branch C — Broader World Phase

## 진입 조건
- readability가 일정 수준 확보
- mixed-arc에서 world memory / relation / pressure 교차 반응이 확인됨
- kernel simplification 필요성이 상대적으로 낮음

## 다음 작업
1. cast combinatorial test
2. role cluster 확대
3. world-side process 다양화
   - rumor
   - crowd
   - institution
   - resource / scarcity
4. 500+ tick ultra-long horizon
5. scenario 다양성 재평가

## 목표
micro-world에서 broader world-facing engine으로 확장

---

## 7. 다음 단계 결정 규칙

정리 단계가 끝나면 아래 셋 중 하나를 선택한다.

### 선택 1 — Continue toward readability
읽히는 흐름이 일정 수준 확인되면 Branch A로 간다.

### 선택 2 — Simplify before expanding
복잡도 대비 읽힘이 낮고 inert 구조물이 많으면 Branch B로 간다.

### 선택 3 — Expand world-side diversity
현재 kernel이 충분히 단단하고 mixed-arc도 버티면 Branch C로 간다.

---

## 8. 우선순위

### 정리 단계 우선순위
1. Kernel Freeze
2. Claim Status Matrix
3. External Readability Blind
4. Inert / Reserve Audit
5. Mixed-Arc Minimal Probe
6. Branch Decision

### Branch 진입 우선순위
- Readability가 보이면 A
- 복잡도와 구조 부채가 크면 B
- kernel이 단단하고 mixed-arc도 유지되면 C

---

## 9. 한 줄 요약

**지금은 더 루프를 돌릴 때가 아니라,  
현재 kernel을 freeze하고, 무엇이 확실하고 무엇이 불확실하며 무엇을 버릴지 정리한 뒤,  
readability / simplification / broader world 중 다음 단계로 분기해야 하는 시점이다.**
         