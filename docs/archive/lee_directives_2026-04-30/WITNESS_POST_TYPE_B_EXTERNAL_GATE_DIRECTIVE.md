# WITNESS — 다음 작업 지시서 (외부 판독 게이트 이후 분기 운영)

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트가  
**Type B directive cycle을 완전히 종료한 뒤**  
다음 단계에서 무엇을 해야 하는지 정리한 실행 지시서다.

현재 상태의 핵심은 다음과 같다.

> **자율적으로 할 수 있고 의미 있는 내부 작업은 모두 소진되었다.  
> 이제 다음 진전은 외부 판독 결과를 받아서 분기하는 방식으로만 나온다.**

따라서 이 문서는:
1. 지금 상태를 고정하고
2. Lee가 해야 할 입력을 정리하고
3. 외부 판독 결과별 분기 행동을 미리 정의하고
4. Claude Code가 새 지시 없이도 재개 가능한 조건을 명확히 하는 데 목적이 있다.

---

## 1. 현재 상태 고정

### 1.1 완료된 것
다음은 모두 완료된 것으로 본다.

- Type B directive cycle 완료
- 4 Steps 즉시 구현 완료
- 4 marginal polish 완료
- Story Output MVP 구축 및 검증 완료
- J-Alpha / J-Beta 자율 진행 가능한 부분 완료
- forbidden_now 7 항목 유지
- 자율 모드 4 phase 모두 종료
- saturation 명시 및 자가질문 5회 연속 No 확인

### 1.2 현재 결론
현재 국면은 다음처럼 정의한다.

- **내부 자율 작업 = 종료**
- **다음 단계 = 외부 판독 / 인간 평가 입력**
- **Claude Code는 새로운 지시 또는 외부 판독 결과 없이는 추가 substantive work를 하지 않는다**

즉 지금은 “다음 할 일 찾기” 단계가 아니라,
**게이트 입력을 받아 다음 분기를 고르는 단계**다.

---

## 2. 지금 필요한 외부 입력

외부 입력은 2개만 남아 있다.

## 2.1 Lee Gate 1 v2 — Renderer Human Diagnosis
### 파일
- `docs/creative/RENDERER_DIAGNOSIS_GATE1_V2.md`

### Lee가 해야 할 일
renderer sample 5개를 읽고 아래를 입력한다.

- 좋은 sample / 나쁜 sample 구분
- 어디가 creative output으로 약한지
- 가장 먼저 고쳐야 할 항목 3개

### 목적
- renderer quality에 대한 인간 기준 ground truth 확보
- style profile 확장 이전에 core weakness를 명확히 하기 위함

---

## 2.2 Branch C GPT-5.5 Send
### 파일
- `BRANCH_C_18_PROBES_BLIND_PACKAGE.md`

### Lee가 해야 할 일
- package를 GPT-5.5에 직접 paste/send
- 결과 응답을 가져온다

### 목적
- Branch C를 더 파지 않고 외부 판독을 먼저 받는다
- engine touch 전 외부 reading 확보
- current Branch C claim의 외부 해석 확인

---

## 3. 지금 당장 하지 말아야 할 것

아래는 외부 판독 결과가 오기 전까지 계속 금지다.

- density-aware sentence pool 구현
- 70+ trajectory labeling
- style profile 추가 확장
- drama / webtoon / game IP mode 확장
- Van Gogh real annotated probe generator
- Branch C S6 engine touch
- Branch C S1 slice 추가
- research deepening 재개
- paper 확장 작업
- 새 자율 루프 생성

즉, **현재 상태에서 추가 제작/확장은 금지**다.

---

## 4. 외부 판독 결과별 자동 분기

외부 판독이 들어오면, Claude Code는 아래 분기 규칙에 따라 즉시 재개한다.

---

## 경우 A — Gate 1 v2 결과가 명확함
### 의미
Lee의 renderer diagnosis가 충분히 구체적이고,
우선 개선 3개가 명확히 정해진 상태.

### 다음 행동
1. `docs/creative/RENDERER_CYCLE_2_PLAN.md` 작성
2. 우선 개선 3개 중 상위 2개만 선택
3. renderer core 수정
4. before / after 비교 sample 생성
5. `docs/creative/RENDERER_CYCLE_2_REVIEW.md` 작성

### 목표
- style profile 확장 전에 renderer 핵심 약점 개선
- “creative output으로서 약한 이유”를 직접 수정

### 주의
- 문체 확장보다 **core readability / vividness / non-report quality**가 먼저
- style branching은 아직 금지

---

## 경우 B — GPT-5.5 응답이 강하게 긍정적
### 의미
외부 판독이 Branch C current claim과 creative variation 가치에 강한 지지를 준 상태.

### 다음 행동
1. Branch C claim 잠금 문서 작성
   - `docs/b_direction/BRANCH_C_LOCK_DECISION.md`
2. creative track 자산화 강화
   - variation demo 정리
   - selector result showcase 정리
   - story pack 정리
3. `docs/creative/CREATIVE_ASSET_PACK_PLAN.md` 작성
4. J-Beta 확장 후보 재검토
   - 단, 70+ labeling은 즉시 시작하지 않고 우선순위 재평가부터

### 목표
- Branch C를 더 실험하는 대신 현재 결과를 자산으로 굳히기
- creative IP track에서 바로 보여줄 수 있는 결과물 체계 강화

### 주의
- 긍정 응답이 와도 engine touch는 별도 지시 없이 하지 않는다
- “strong positive”를 “즉시 확장 허가”로 해석하지 않는다

---

## 경우 C — GPT-5.5 응답이 애매함
### 의미
외부 판독이 current claim을 부정하지는 않지만 강하게 지지하지도 않는 상태.

### 다음 행동
1. Branch C는 hold 상태 유지
2. research deepening 재개하지 않음
3. creative output 중심으로만 계속
4. renderer 진단 쪽이 있으면 renderer cycle 우선
5. Branch C 관련은 “추가 주장”이 아니라 “현재 자산 정리” 수준만 유지

### 목표
- 애매한 외부 판독을 이유로 다시 research loop에 빠지지 않기
- 결과물 중심 트랙 유지

### 주의
- 이 경우엔 Branch C를 더 파지 않는다
- GPT 응답을 해석하려고 새로운 slice 실험 금지

---

## 경우 D — renderer 평가가 매우 부정적
### 의미
Lee가 직접 보기에 creative output으로서 현재 renderer가 약하고,
핵심 문제가 style 이전의 구조적 표현 문제에 있다는 상태.

### 다음 행동
1. style/profile 확장 전면 중단
2. `docs/creative/RENDERER_CORE_REPAIR_PLAN.md` 작성
3. core weakness 2개만 선택
   - 예: report-like tone
   - 예: variation collapse
   - 예: world-side invisibility
4. renderer repair cycle 실행
5. variation demo 일부 재생성 후 재평가

### 목표
- creative output의 바닥 품질 확보
- style 실험 전에 core renderer repair

### 주의
- 이 경우 aesthetic tuning보다 core representation repair가 먼저
- selector, taxonomy, labeling 확장은 추가 금지

---

## 5. Claude Code 재개 규칙

외부 판독 결과가 도착하면 Claude Code는 아래 원칙으로 움직인다.

### 5.1 공통 원칙
- 한 번에 한 분기만 처리
- 결과를 과대해석하지 않음
- 기존 forbidden_now는 유지
- engine touch / 새 slice / research 재개는 별도 directive 없이는 금지

### 5.2 문서 우선
각 분기마다 먼저 plan 문서를 쓴 뒤 구현한다.
즉,
- 결과 수신
- 분기 판정
- 실행 계획 문서 작성
- 실제 작업
순서로 간다.

### 5.3 자율 가능 범위
외부 판독이 들어온 뒤에는 다음 정도는 자율 진행 가능하다.
- renderer cycle 2 plan 작성
- Branch C lock 문서 작성
- creative asset pack plan 작성
- before/after 비교 샘플 생성
- variation review 업데이트

단, 새로운 설계 축을 여는 일은 금지다.

---

## 6. Lee가 지금 하면 되는 것

### 우선순위 1
`RENDERER_DIAGNOSIS_GATE1_V2.md`에 sample 5개 평가 입력

### 우선순위 2
`BRANCH_C_18_PROBES_BLIND_PACKAGE.md`를 GPT-5.5에 보내고 응답 가져오기

### 우선순위 3
그 결과를 Claude Code에 다시 전달

즉 Lee의 현재 역할은:
- 추가 방향 고민이 아니라
- **게이트 입력 2개를 넣는 것**이다.

---

## 7. 다음 단계의 실제 우선순위

외부 입력 전 기준으로 우선순위는 아래처럼 고정한다.

1. **Lee Gate 1 v2 직접 평가**
2. **Branch C GPT-5.5 send**
3. 결과 수신
4. 분기 실행
5. 그 이후에야 renderer/style/creative asset 논의

---

## 8. 중단 조건

Claude Code는 아래 상태에서는 더 이상 새 작업을 만들어내지 않는다.

- 외부 판독 결과가 없음
- 새 directive 없음
- forbidden_now 내부에서 marginal value만 남음

즉, 지금은 정말로 **의미 있는 자율 작업 0건 상태**로 본다.

---

## 9. 최종 한 줄 요약

**현재 자율 작업 사이클은 완전히 종료되었다.  
이제 다음 진전은 오직 두 개의 외부 입력 —  
(1) Lee의 renderer human diagnosis,  
(2) Branch C GPT-5.5 외부 판독 — 에 의해 결정된다.  
결과가 들어오면 Claude Code는 경우 A/B/C/D 중 하나로 즉시 분기해서 재개하고,  
그 전까지는 새로운 내부 확장 작업을 하지 않는다.**
