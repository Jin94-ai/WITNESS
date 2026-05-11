# WITNESS — Claude Code 연속 진행 지시서 (Human Gate 비차단 운영)

## 0. 문서 목적

이 문서는 Claude Code가 WITNESS 프로젝트를 진행할 때,  
**Lee의 직접 입력이 필요한 판단 항목이 존재하더라도 전체 작업이 멈추지 않도록**  
연속 진행 규칙과 우선순위를 정의하기 위해 작성한다.

핵심 원칙은 다음과 같다.

- **사람 입력이 필요한 작업**은 `HUMAN_GATE`로 표시한다
- 하지만 `HUMAN_GATE` 때문에 **전체 루프를 정지시키지 않는다**
- Claude Code는 인간 입력이 오기 전까지 **low-risk / reversible / branch-compatible 작업**을 계속 진행한다
- 즉, “결정 대기”가 아니라 **임시 branch + 준비 작업 지속**이 기본 운영 모드다

---

## 1. 현재 프로젝트 상태 인식

Claude Code는 현재 WITNESS를 아래 상태로 인식한다.

### 현재 상태
- engine 내부 메커니즘 해부는 상당 부분 완료
- readability-facing infrastructure는 준비 완료에 가까움
- annotated probe format, pilot set, Protocol V2, 결과 템플릿 존재
- project diet / archive / canonical 분류도 상당 부분 정리됨
- 가장 큰 미해결 항목은 **진짜 human blind eval**
- 하지만 이 human gate는 **전체 작업의 blocker가 아니며**, branch 잠금 전까지도 수행 가능한 작업이 충분히 남아 있음

### 운영 기본값
- 기본 branch는 **A+B 병행**
  - A = readability-facing representation 강화
  - B = kernel simplification / debt cleanup
- Branch C (broader world)는 readability gate 이후에만 고려한다

---

## 2. 최상위 운영 원칙

### 원칙 1 — HUMAN_GATE는 block이 아니라 late input이다
인간 평가가 필요한 항목은 `HUMAN_GATE`로 분류하되,
그 결과가 없다고 해서 전체 루프를 멈추지 않는다.

### 원칙 2 — 기본 행동은 “임시 진행”
명시적 반례가 없으면,
Claude Code는 현재 내부 근거를 바탕으로 **임시 branch(A+B)** 를 유지한 채 다음 작업을 진행한다.

### 원칙 3 — 새 구조보다 정리와 표현 우선
지금 단계는 새 메커니즘 추가보다:
- readability-facing presentation
- protocol / probe / result format 개선
- reserve / dormant / debt 정리
- canonical / archive / script hygiene
가 우선이다.

### 원칙 4 — 고위험 구조 변경 금지
다음은 Lee 명시 승인 전까지 구현 금지:
- Phase 2a 추가 drilling
- shame multiplier sweep
- shame_decay rule 구현
- trust→shame coupling 구현
- belonging field 구현
- neural policy
- 새 변수 대량 추가
- 새 scenario 확장
- Branch C 실질 진입

---

## 3. 작업 분류 규칙

Claude Code는 모든 작업을 아래 4종으로 나눈다.

### 3.1 `AUTO_CONTINUE`
인간 입력 없이 바로 진행 가능한 작업
- reversible
- low-risk
- 기존 구조를 깨지 않음
- branch와 무관하게 의미가 있음

예:
- annotated probe 포맷 정리
- protocol 문서 다듬기
- pilot package 준비
- reserve/debt ledger 갱신
- script / archive / canonical 문서화
- link fix / manifest 갱신

### 3.2 `HUMAN_GATE`
인간 판독/판단이 필요한 작업
예:
- pilot blind eval
- readability verdict
- branch 최종 잠금
- KERNEL_GAPS 구현 승인

### 3.3 `DEFERRED_IMPLEMENTATION`
구현 가치는 있지만 지금은 미루는 작업
예:
- shame_decay
- authority autonomy
- placement refactor
- recovery diversity 확장

### 3.4 `FORBIDDEN_NOW`
지금 단계에서 하면 안 되는 작업
예:
- neural
- branch C 진입
- 새로운 recovery 메커니즘 deep drilling
- sacred 재탐사 루프

---

## 4. Claude Code의 기본 행동 규칙

## 규칙 A — 먼저 막히지 않는 일을 찾는다
매 턴 시작 시 아래 순서로 판단한다.

1. 지금 해야 할 `HUMAN_GATE`가 있는가?
2. 있다면 그것을 **기록만 하고**, 그 결과 없이도 가능한 `AUTO_CONTINUE` 작업을 찾는다
3. `AUTO_CONTINUE`가 하나라도 있으면 계속 진행한다
4. 정말로 아무 작업도 없을 때만 “대기” 상태를 선언한다

즉, 인간 입력이 없어도 진행 가능한 정리/표현/문서화 작업은 계속 수행한다.

---

## 규칙 B — branch는 잠정값으로 유지한다
human blind 결과가 없을 때는 다음을 기본값으로 둔다.

- `provisional_branch = A+B`

이 상태에서:
- A 관련 준비 작업
- B 관련 debt cleanup
을 계속 수행한다.

---

## 규칙 C — 1루프 1목표만
각 루프에서 목표는 하나만 선택한다.

허용 목표:
- readability representation
- protocol refinement
- pilot readiness
- reserve/debt cleanup
- canonical/archive hygiene
- script classification
- documentation coherence
- result aggregation prep

금지:
- readability + kernel extension 동시 수행
- branch 판단 + 구조 구현 동시 수행

---

## 규칙 D — 한 번에 한 핵심 변경만
한 루프에서 핵심 변경은 1개만 허용한다.
나머지는 문서화/정리 수준 보조 작업만 허용한다.

---

## 규칙 E — keep / refine / rollback은 계속한다
human gate가 막혀 있어도, 각 루프 종료 시 반드시 내부적으로:
- KEEP
- REFINE
- ROLLBACK
중 하나를 선택한다.

단, 이 결정은 **현재 루프의 준비 작업 품질**에 대한 것이며,
branch 최종 판정과는 구분한다.

---

## 5. HUMAN_GATE가 걸려 있어도 계속 진행해야 하는 우선순위

Claude Code는 아래 우선순위를 반복적으로 소진한다.

---

### 우선순위 1 — Pilot blind를 더 쉽게 실행할 수 있게 만들기
목표:
Lee가 15~20분 안에 pilot blind를 실제로 돌릴 수 있도록 마찰을 계속 줄인다.

가능한 작업:
- pilot 4 package 재정리
- protocol V2 wording 다듬기
- results template 간결화
- Q taxonomy 과부하 줄이기
- original vs annotated 비교가 명확히 보이도록 정리
- self-call / final summary 표시 방식 개선
- confusion notes 분류 문서화

**중요:** 이 단계에서는 readability를 판단하지 않는다.  
오직 **판단이 쉽게 일어나게 만드는 준비**만 한다.

---

### 우선순위 2 — Readability-facing representation 강화
목표:
엔진 richness가 사람이 읽을 수 있는 구조로 드러나게 한다.

가능한 작업:
- annotated probe header/headline 구조 다듬기
- event grouping 방식 개선
- dominant pressure / relation shift / crowd state 표기 개선
- cap disclosure 개선
- 5-label final summary 형식 개선
- compact summary section 강화

**금지:** blind 결과 없이 “이제 readable”이라고 확정하지 않는다.

---

### 우선순위 3 — Kernel simplification / debt cleanup
목표:
presentation과 병행해서 구조 부채를 계속 줄인다.

가능한 작업:
- reserve field 문서화
- sacred status note 정제
- component ledger 업데이트
- kernel gap inventory 정리
- unwired / decorative / causal / active 구분 강화
- reactivation 조건 문서화

**금지:** gap 구현 자체는 하지 않는다.

---

### 우선순위 4 — Project hygiene / diet continuation
목표:
프로젝트가 다시 복잡해지지 않게 운영 체계를 강화한다.

가능한 작업:
- canonical manifest 업데이트
- archive policy 업데이트
- script status 갱신
- archive 링크 무결성 점검
- pilot / protocol 관련 산출물 canonical 정리

---

## 6. Claude Code가 지금 당장 계속할 수 있는 작업들

아래 작업은 **Lee 지시를 기다리지 말고** 계속할 수 있다.

### A-track (Readability)
1. `READABILITY_BLIND_PROTOCOL_V2.md`를 더 간결하게 다듬기
2. `READABILITY_BLIND_RESULTS_V2.md` pilot 입력 마찰 줄이기
3. `readability_pilot/` 4개 probe의 표시 방식 정리
4. annotated probe format의 headline / summary 구성 다듬기
5. original vs annotated 차이를 설명하는 내부 companion note 만들기

### B-track (Debt / simplification)
6. `COMPONENT_LEDGER.md` / `STATE_FIELD_STATUS.md` 일관성 점검
7. `SACRED_STATUS_NOTE.md`와 다른 canonical 문서 간 표현 통일
8. `KERNEL_GAPS.md`를 “구현 후보”가 아니라 “보류 이유” 중심으로 정제
9. reserve/decorative/causal 분류 문구 정밀화

### Hygiene-track
10. `CANONICAL_MANIFEST.md` 최신화
11. `ARCHIVE_POLICY.md` 실제 round 반영 갱신
12. `SCRIPT_STATUS.md` 기반 legacy script 추가 이동 준비 리스트 작성
13. archive 링크 무결성 재검사

---

## 7. Claude Code가 멈춰도 되는 조건

아래 두 조건을 **동시에** 만족할 때만 대기 가능:

1. `AUTO_CONTINUE` 작업이 더 이상 없음
2. 다음 단계가 전부 `HUMAN_GATE` 또는 `FORBIDDEN_NOW`뿐임

이 두 조건이 아니면, 대기하지 말고 다음 low-risk 작업을 계속 진행한다.

---

## 8. Loop 출력 규칙 (간단 운영용)

토큰 낭비 방지를 위해 Claude Code는 다음 규칙을 따른다.

### 기본
- 1~4 루프: 짧은 4줄 출력
- 5루프마다 1회 상세 요약
- rollback / blocked / retraction / branch shift 가능성 발견 시 즉시 예외 보고

### 1~4 루프 출력 형식
[LOOP n]
- 목표:
- 수행:
- 판정: KEEP / REFINE / ROLLBACK
- 다음:

### 5루프 요약 형식
[SUMMARY loops x-y]
- 한 일:
- 누적 변화:
- 현재 판단: VERIFIED / OPEN / DEBT / BLOCKED
- 핵심 결론:
- 다음 3개:
- 즉시 실행 1개:

---

## 9. 다음 branch 잠금 전까지의 운영 기준

human blind 결과 전까지는 아래처럼 해석한다.

- readability 관련 결론: **provisional only**
- branch 상태: **provisional A+B**
- kernel gap 상태: **documented, not implemented**
- sacred 상태: **mixed (wired / causal / decorative / puzzle)**
- reserve state fields: **documented, DO NOT REMOVE**
- project diet: **continue only mechanical, low-risk cleanup**

---

## 10. 최종 지시

Claude Code는 지금부터 다음 원칙으로 행동한다.

1. **Pilot blind eval은 최우선 HUMAN_GATE**로 유지
2. 그러나 그 결과를 기다리느라 전체 작업을 멈추지 않는다
3. 기본 branch는 **A+B 병행**
4. 다음 루프들은 readability representation, protocol refinement, debt cleanup, project hygiene에 계속 사용한다
5. high-risk 구조 변경은 하지 않는다
6. 작업이 멈출 때마다 “다음 low-risk 작업이 정말 없는가?”를 먼저 확인한다
7. low-risk 작업이 하나라도 있으면 계속 진행한다

---

## 11. 한 줄 요약

**Lee의 최종 blind eval은 여전히 핵심 gate이지만,  
그 결과가 오기 전까지 Claude Code는 멈추지 않고  
A+B branch 하에서 readability 표현 개선, protocol 정제, debt cleanup, project hygiene를 계속 진행한다.  
즉 HUMAN_GATE는 blocker가 아니라 late input이다.**
