# WITNESS — 내부 자가평가 기반 다음 작업 진행 규칙 및 실행 지시서

## 0. 문서 목적

이 문서는 WITNESS 프로젝트가 외부 인간 결정(예: Step C 판독, branch 선택)을 오래 기다리며 정지 상태에 들어가지 않도록,  
현재까지 확보한 내부 근거와 산출물을 바탕으로 **프로젝트 내부에서 자체적으로 다음 작업을 결정하고 진행할 수 있는 규칙**을 정리하기 위해 작성한다.

핵심 목적은 세 가지다.

1. **결정 대기 상태를 줄인다**
2. **내부 근거로 다음 작업을 자동 분기한다**
3. **루프 포화 이후에도 “작은 다음 단계”를 끊기지 않고 수행한다**

이 문서는 “사람이 최종 판정자”라는 원칙을 없애는 문서가 아니다.  
다만, 인간 판정이 늦어질 때 프로젝트가 멈추지 않도록 **내부 추정 branch**와 **자동 진행 규칙**을 둔다.

---

## 1. 현재 상태 진단

현재 WITNESS는 다음 상태에 있다.

- kernel은 상당 부분 정리되었음
- mechanism drilling은 포화에 가까움
- branch 결정의 핵심 blocker는 readability blind
- Iter 168-175는 heartbeat only로 사실상 정지 상태
- annotated probe가 원본보다 가독성 잠재력이 높다는 strong hint가 있음
- 동시에 reserve / decoupled / single-loop recovery 문제는 완전히 끝나지 않았음

즉 현재 문제는 구조 부족이라기보다 **결정 지연**이다.

따라서 다음 원칙을 채택한다.

> 외부 인간 판독이 없더라도, 내부 근거가 일정 수준 이상이면 **임시 branch**를 정하고 작은 다음 작업을 자동 진행한다.

---

## 2. 기본 운영 원칙

### 원칙 1 — 정지보다 임시 분기가 낫다
명시적 반증이 없는 한, 프로젝트는 “대기”보다 “작은 범위의 임시 branch 진행”을 우선한다.

### 원칙 2 — 인간 gate는 유지하되 blocker로 두지 않는다
Readability blind는 여전히 중요하지만, 그 결과가 오기 전에도 내부 근거로 **provisional branch**를 정할 수 있다.

### 원칙 3 — 큰 결정 대신 작은 진행
다음 단계는 “완전한 Branch A/C 확정” 같은 큰 결정보다,
- 1주 단위
- reversible
- low-risk
한 작업으로 쪼개어 진행한다.

### 원칙 4 — 새 메커니즘 drilling 금지 유지
아직도 다음은 구조 탐사보다 전환 단계다.
따라서:
- Phase 2a 추가 drilling
- shame multiplier 미세 스윕
- neural policy
- 새 변수 대량 추가
는 여전히 금지한다.

---

## 3. 내부 자가평가 기반 branch 판정 규칙

이 섹션은 외부 readability blind가 없더라도, 내부에서 임시 branch를 선택하는 기준이다.

---

### Branch A — Readability-facing (임시 진입 조건)

다음 5개 중 3개 이상이면 **임시 Branch A** 진입:

1. annotated probe가 원본보다 구조를 더 잘 드러낸다는 정성적 근거가 있음
2. kernel은 충분히 풍부하다는 내부 결론이 있음
3. world autonomy / meso coupling / mixed dynamics가 이미 검증됨
4. 최근 새 mechanism 발견보다 presentation bottleneck 지적이 반복됨
5. heartbeat-only 원인이 “무엇을 더 만들지 모름”이 아니라 “외부 판독 대기”임

### 현재 WITNESS 판정
이 조건은 이미 충족한다.  
따라서 **임시 Branch A 진입 가능**으로 본다.

---

### Branch B — Kernel Simplification (병행 유지 조건)

다음 5개 중 2개 이상이면 **Branch B 병행 유지**:

1. reserve / dormant / decoupled components가 아직 남아 있음
2. sacred 계열 일부가 decorative / zero-effect suspect 상태
3. recovery가 여전히 single-loop 의존
4. readability가 좋아도 structure debt가 남아 있을 가능성이 큼
5. small simplification 작업이 저위험으로 남아 있음

### 현재 WITNESS 판정
이 조건도 충족한다.  
따라서 **Branch B 병행 유지 필요**로 본다.

---

### Branch C — Broader World (보류 조건)

다음 4개가 모두 충족되기 전까지 Branch C는 유예:

1. readability blind 실제 결과 확보
2. annotated probe가 인간에게도 readable하다는 증거 확보
3. world-side process 3개 이상이 외부에서도 감지 가능
4. mixed-arc collapse가 제한적임

### 현재 WITNESS 판정
아직 보류.  
따라서 **Branch C는 준비만 하고 진입하지 않는다.**

---

## 4. 현재 최종 내부 branch 결정

현재 시점의 내부 자가판정은 다음과 같다.

## 결론
**임시 Branch A + Branch B 병행**을 기본 운영 상태로 채택한다.

즉:
- A: readability-facing presentation / probe 인프라 강화
- B: kernel simplification 잔여 작업 정리

을 동시에 진행한다.

### 왜 이 조합인가
- A만 가기엔 reserve / decoupled debt가 남아 있음
- B만 가기엔 실제 병목이 presentation일 가능성이 높음
- C로 가기엔 human readability gate가 아직 없음

따라서 가장 현실적인 선택은 **A+B 병행**이다.

---

## 5. 지금부터 자동 진행할 다음 작업

아래 작업은 외부 결정 대기 없이 바로 진행 가능하다.

---

# Track A — Readability-facing 진행

## A1. Annotated probe를 공식 포맷으로 승격
현재 prototype / 12개 생성 결과를 바탕으로, annotated probe를 임시 표준 포맷으로 채택한다.

### 해야 할 일
- 원본 probe와 annotated probe 차이점 문서화
- annotated probe 필드 정의 고정
- event log / dominant pressure / relation shift / motif shift / crowd state / final summary의 최소 표준 정리

### 산출물
- `docs/b_direction/ANNOTATED_PROBE_FORMAT.md`
- `docs/b_direction/readability_probes_annotated/` 정리본

---

## A2. Step C를 12개 full run 전, 4개 pilot blind로 축소 실행 가능한 형태로 준비
인간 평가가 늦어질 수 있으므로, full blind 전에 **pilot 4개 세트**를 먼저 뽑아놓는다.

### 구성
- 원본 2개
- annotated 2개
- scenario/seed balanced

### 목적
- 원본 vs annotated readability 차이를 작게라도 검증할 수 있게 만들기
- 인간이 1~2시간 대신 15~20분 안에 반응할 수 있도록 문턱 낮추기

### 산출물
- `docs/b_direction/READABILITY_PILOT_4.md`
- `docs/b_direction/readability_pilot/`

---

## A3. Q 세트 개선안 적용 버전 준비
이전 문서에서 제안한 Q 개선안을 반영해, 새 템플릿을 만든다.

포함:
- Q1b readability confidence
- Q2 secondary pressure + clarity
- Q3 cohort/group dynamics 세분화
- Q4 cyclic arc 분리
- Q5 oscillation narrative contribution
- Q6 confusion notes semi-required

### 산출물
- `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md`
- `docs/b_direction/READABILITY_BLIND_RESULTS_V2.md`

---

# Track B — Kernel Simplification 진행

## B1. Reserve / dormant 공식 표기
현재 남은 reserve / remove 후보를 component ledger에 공식 반영한다.

### 해야 할 일
- 5 reserve 항목 확정 표기
- 각 항목의 현재 상태, 제거 여부 아님, future reactivation 조건 한 줄씩 기록
- unwired / doc-only / decorative 여부 표시

### 산출물
- `docs/b_direction/COMPONENT_LEDGER.md` 업데이트
- `docs/b_direction/STATE_FIELD_STATUS.md`

---

## B2. breach_count / unwired field 문서화
낮은 리스크로 즉시 가능한 작업.

### 해야 할 일
- breach_count annotation
- SlowStateFieldRecoveryRule docstring 업데이트
- narrative-field 상태 기록

### 목표
실제 동역학에 안 쓰이는 것과 향후 후보를 명확히 분리

---

## B3. sacred decorative suspicion 문서화
sacred가 지금 genuinely active world process가 아니라 decorative suspect라는 점을 공식적으로 기록한다.

### 이유
나중에 sacred를 다시 손댈 때 “왜 지금은 보류인지”를 잊지 않도록 하기 위함

### 산출물
- `docs/b_direction/SACRED_STATUS_NOTE.md`

---

## B4. recovery diversity gap 메모화
현재 spatial disengagement 실험이 막힌 이유가 shame_decay gap이라는 점을, 즉시 구현이 아니라 **future kernel extension candidate**로 기록한다.

### 주의
이 단계에선 구현하지 않는다.

### 산출물
- `docs/b_direction/KERNEL_GAPS.md`

---

## 6. 지금 자동 진행하면 안 되는 것

다음 항목은 내부 자가판단으로도 아직 진행 금지다.

### 금지
- Phase 2a 추가 drilling
- shame multiplier 미세 실험
- shame_decay 즉시 구현
- neural probe
- 새 변수 대량 추가
- 새 named scenario 확장
- universality claims
- Branch C 실질 진입

이유:
현재 목적은 새로운 기계 내부 발견이 아니라,
**표현 검증 + debt 정리 + 다음 분기 준비**이기 때문이다.

---

## 7. 내부 진행 순서

외부 입력이 없어도 아래 순서대로 진행한다.

### Step 1
A1 — annotated probe 포맷 표준화

### Step 2
A2 — readability pilot 4개 세트 준비

### Step 3
A3 — Readability Blind Protocol V2 템플릿 생성

### Step 4
B1 — reserve / dormant ledger 업데이트

### Step 5
B2 — breach_count / unwired field 문서화

### Step 6
B3 — sacred status note 작성

### Step 7
B4 — kernel gaps note 작성

이 7개는 모두 **low-risk, reversible, branch-compatible** 작업이다.

---

## 8. 인간 평가가 들어오면 어떻게 할 것인가

Step C 결과가 오면 아래 규칙을 즉시 적용한다.

### 결과 1 — readable ≥ 8/12
- Branch A 강화
- Branch B는 debt cleanup만 유지
- Branch C 준비 단계 진입 가능

### 결과 2 — readable 4~7/12
- A+B 병행 유지
- probe formatting 개선 반복
- 구조 simplification 일부 계속

### 결과 3 — readable ≤ 3/12
- Branch B 강화
- A는 probe redesign 수준으로 축소
- kernel simplification / recovery diversity / decorative removal 쪽으로 복귀

---

## 9. 지금 상태를 한 문장으로 정의

지금 WITNESS는  
**새 메커니즘을 더 캐는 단계가 아니라, 이미 확보한 world kernel이 외부에서 읽히도록 만드는 단계**에 있다.

따라서 외부 인간 결정이 없더라도,  
내부적으로는 **A+B 병행**을 기본값으로 정하고 다음 준비 작업을 자동 진행하는 것이 맞다.

---

## 10. 한 줄 요약

**지금은 결정 대기 때문에 멈추는 대신,  
내부 근거로 임시 Branch A+B를 채택하고  
annotated probe 표준화 + readability pilot 준비 + reserve/debt 정리를 자동으로 진행한다.  
즉 다음 단계는 “새 발견”이 아니라 “읽히는 세계로 넘어가기 위한 표현 인프라와 구조 정리”다.**
