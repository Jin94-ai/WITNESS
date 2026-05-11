# WITNESS — 다음 진행 실행 지시서 (Pilot Blind Eval 중심)

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트의 다음 진행을 멈춤 없이 이어가기 위해,  
Lee가 직접 판단해야 하는 항목들과 그 이후 자동으로 이어질 후속 작업을 **실행 순서 기준**으로 정리한 지시서다.

핵심은 다음 한 줄이다.

> **지금 가장 중요한 다음 작업은 Pilot 4-probe blind eval 실행이며,  
> 그 결과로 Branch A / B / C / A+B를 잠그고 이후 작업을 자동 진행할 수 있게 만드는 것이다.**

---

## 1. 현재 상태 요약

현재 프로젝트는 다음 상태에 있다.

- readability-facing infrastructure는 사실상 준비 완료
- pilot 4-probe 세트 존재
- Protocol V2 존재
- 결과 템플릿 존재
- self-call / Q6a taxonomy / format-axis tracking 등 보조 인프라도 추가됨
- 현재 가장 큰 blocker는 **실제 evaluator 입력 부재**
- 이 blocker가 해소되면 branch 판단과 다음 작업이 거의 자동으로 이어질 수 있음

즉 지금은 새 메커니즘 탐색보다 **pilot blind eval 실행**이 우선이다.

---

## 2. 최우선 작업 — Pilot 4-probe blind eval 실행

### 목표
4개 pilot probe를 실제로 blind reading 해서,
- readability가 실제로 있는지
- original vs annotated 차이가 있는지
- Q-set이 evaluator 입장에서 usable한지
를 확인한다.

### 예상 시간
- **15~20분**

### 읽을 파일
- `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md`
- `docs/b_direction/readability_pilot/` 안의 4 probes

### 답안 작성 위치
- `docs/b_direction/READABILITY_BLIND_RESULTS_V2.md`
  - **§1 pilot 부분**

---

## 3. Pilot eval에서 반드시 채워야 할 항목

### 3.1 Per-probe table
각 probe마다 아래를 기록한다.

- Q1
- Q1b
- Q2a
- Q2b
- Q2c
- Q3a
- Q3b
- Q4a
- Q4b
- Q5a
- Q5b

### 3.2 Final summary self-call
- `§1.1.5 final summary self-call`
- 각 probe에 대해 **5-label 중 하나**를 직접 적는다
- annotated label을 먼저 보지 말 것

### 3.3 Q6a confusion notes
- main tag
- 필요 시 sub-tag

### 3.4 Pilot verdict
- A
- B
- C
- A+B
- inconclusive

중 하나를 적는다.

---

## 4. Pilot eval 이후 자동으로 할 수 있는 것

pilot 결과가 들어오면 아래는 거의 자동으로 처리 가능하다.

### 4.1 Ground truth 비교
- `§4.1 ground truth table`
- self-call 정확도 측정
- original vs annotated 구분 성능 확인

### 4.2 Format-axis 효과 확인
- annotated 2개가 original 2개보다 읽히는지 비교
- readability improvement가 실제인지 확인

### 4.3 Q-set usability 점검
- Q6a 5 tags + sub-tags가 evaluator에게 과부하인지
- self-call 칸이 실제로 도움 되는지
- Protocol V2의 mode/format-axis 확장이 실용적인지 확인

---

## 5. Branch 결정 규칙

pilot 결과가 오면 아래 규칙으로 1차 branch 판단을 한다.

| Pattern | Branch |
|---|---|
| Annotated 2/2 + Original ≤ 1/2 | **A** |
| Both 2/2 | **C ready** (단, full eval로 confirm) |
| Both ≤ 1/2 | **B priority** |
| Mixed | **run full N=12** |

### 해석
- **A**: presentation 쪽이 실제 병목이었음
- **B**: kernel simplification / 구조 재정리가 더 필요
- **C ready**: broader world 가능성 있음, 단 full eval 필요
- **Mixed**: pilot만으로는 부족하므로 12개 full blind로 확대

---

## 6. Pilot 이후 후속 작업 순서

### Branch A일 경우
1. annotated probe format 확정
2. Protocol V2 유지
3. Full N=12 blind eval 준비
4. readability-facing representation 개선 지속
5. Branch B debt cleanup은 최소 유지

### Branch B일 경우
1. readability-facing 작업은 축소
2. kernel simplification 우선
3. sacred / reserve / recovery diversity gap 재검토
4. KERNEL_GAPS에서 높은 가치 항목 재평가

### Branch C ready일 경우
1. full N=12 blind eval로 confirm
2. confirm되면 broader world 준비
3. 단, Branch B debt cleanup은 최소 유지

### Mixed일 경우
1. full N=12 blind eval 진행
2. pilot 결과와 full 결과 비교
3. original vs annotated 차이가 시나리오별인지 일반적인지 확인

---

## 7. KERNEL_GAPS 관련 Lee gate

Pilot 이후에 판단해야 할 별도 항목이다.

### 현재 가장 큰 결정
- **Gap 1: shame_decay rule 추가 (K1 vs K2)**

### 원칙
- Pilot blind eval 전에는 구현하지 않는다
- Pilot 결과가 readability bottleneck인지 structural bottleneck인지 보여준 뒤 결정한다

### 권고
현재는 **K2 (defer)** 쪽을 기본값으로 둔다.  
즉, readability 결과를 보기 전까지는 gap 구현을 미룬다.

### 기타 gap
- trust→shame coupling
- belonging field
- placement template refactor
- authority autonomy

이 항목들도 지금은 구현보다 **보류 + 문서화 유지**가 맞다.

---

## 8. 다이어트 / 정리 관련 후속 작업

Pilot과 별개로 low-risk하게 진행 가능한 것들이다.

### 이미 분류 완료된 것
- `scripts/b_direction §6.1` leaf scripts archive 후보
- `scripts/b_direction §6.2` Iter 91-119 standalone
- `scripts/b_direction §6.3` one-off 일부
- `probe_runs/*.json` 후보

### 원칙
Pilot blind eval이 끝나기 전까지는
- mechanical archive만
- import 의존성 없는 것만
- 구조 판단을 바꾸지 않는 것만
진행한다.

즉, 다이어트는 branch 판단을 방해하지 않는 선에서만 계속한다.

---

## 9. Iter 185-188 readability infrastructure 추가분 평가 포인트

Pilot을 돌릴 때 아래 4개도 같이 평가한다.

### 9.1 Annotated event log cap disclosure
- “showing first 30 of N” 표기가 evaluator에게 실제로 도움이 되는가

### 9.2 Q6a sub-tags
- 세부 분류가 유용한가
- evaluator 부담이 너무 커지지는 않는가

### 9.3 Annotated headline final summary
- 현재 5 labels가 충분한가
- `NUANCED`, `OUTLIER` 같은 추가가 필요한가

### 9.4 Self-call template
- evaluator 입장에서 유의미한가
- 그냥 부담만 늘리는가

즉 Pilot은 readability만 보는 게 아니라,
**Iter 185-188에서 추가된 infra가 실제로 유용한지도 같이 점검하는 자리**다.

---

## 10. 지금 바로 할 일 (실행 순서)

### Step 1
`READABILITY_BLIND_PROTOCOL_V2.md` 읽기

### Step 2
`readability_pilot/` 4개 probe blind reading

### Step 3
`READABILITY_BLIND_RESULTS_V2.md` pilot 부분 채우기

### Step 4
pilot verdict 기록

### Step 5
ground truth와 self-call 비교

### Step 6
branch 1차 판정
- A / B / C ready / Mixed

### Step 7
그 branch에 맞는 다음 작업 자동 진행

---

## 11. 한 줄 요약

**지금 다음으로 해야 할 가장 중요한 일은  
Pilot 4-probe blind eval을 직접 실행하는 것이다.  
이 한 번의 평가로 readability infra 효과, original vs annotated 차이, Q-set usability, 그리고 Branch A/B/C 방향이 거의 동시에 정리된다.**
