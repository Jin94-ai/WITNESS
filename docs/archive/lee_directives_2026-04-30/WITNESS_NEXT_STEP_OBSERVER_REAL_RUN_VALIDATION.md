# WITNESS — 다음 진행사항 (Observer Layer 이후)

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트 상태를 기준으로,  
**지금 당장 크게 수정할 부분이 없다는 전제 아래**  
다음으로 무엇을 해야 하는지 바로 실행 가능한 형태로 정리한 작업 계획서다.

현재 판단은 다음과 같다.

> **Observer Layer 자체는 방향상 잘 구현되었고,  
> 지금 필요한 건 새 기능 추가가 아니라  
> 실제 시뮬레이션 run에 붙여서 “전지적 관찰자처럼 세계를 볼 수 있는지” 검증하는 것이다.**

따라서 다음 단계의 핵심은  
**Observer Layer real-run validation** 이다.

---

## 1. 현재 상태 요약

현재까지 확보된 것은 다음과 같다.

### 1.1 Engine / Integrity
- 전체 테스트 1763 PASS / 0 FAIL
- pre-existing fail 해소 완료
- engine integrity violations 0
- selector hardcoding 문제 해결 (`engine/story/selector.py` → `scripts/story/selector.py` 이동)

### 1.2 Story Output
- 3-stage pipeline 존재
- story output MVP 검증 완료
- renderer는 Cycle 7에서 freeze
- creative variation demo와 anchor library 존재

### 1.3 Branch C
- external eval bundle 준비 완료
- 아직 외부 응답은 대기 중
- 구조 검증은 외부 판독 단계로 넘어간 상태

### 1.4 Observer Layer
- O1~O7 구현 완료
- 17 files / ~2700+ lines / 144 tests
- snapshot / lens / replay / compare / narrative summary까지 존재
- 원칙: **observer = 관찰기, not 평가기**

즉 현재 프로젝트는:
- 엔진 있음
- 이야기 출력 있음
- 관찰 레이어 있음
- 이제 남은 건 **실제 흐르는 세계에 붙여 가치가 있는지 확인하는 단계**다.

---

## 2. 지금 큰 수정이 필요하지 않은 이유

다음 이유로, 지금은 Observer Layer 자체를 크게 뜯어고칠 시점이 아니다.

### 2.1 기능 골격은 이미 충분함
observer layer는 최소한의 핵심 기능을 이미 갖췄다.

- snapshot recording
- multi-view observation
- replay / jump
- compare views
- narrative summary

즉 기능 결핍 상태가 아니다.

### 2.2 테스트와 정합성이 확보됨
이 상태에서 더 확장하거나 정교화하면,
지금 얻은 안정성을 깨뜨릴 위험이 있다.

### 2.3 현재 병목은 “기능 부족”이 아니라 “실제 가치 검증”
지금 가장 중요한 질문은:
> **이 observer layer가 실제 simulation run에 붙었을 때  
> 정말로 전지적 관찰자처럼 세계를 볼 수 있게 해 주는가?**

즉 문제는 설계가 아니라 **실사용 검증**이다.

---

## 3. 다음 핵심 목표

## 다음 1차 목표
**Observer Layer를 실제 simulation run에 연결하여,  
World View / Person View / Event View / Compare View가  
실제로 읽을 가치가 있는 관찰 결과를 주는지 검증한다.**

이 목표는 story renderer를 더 고치거나,  
새 scenario를 열거나,  
새 learned model을 붙이기 전에 반드시 끝내야 한다.

---

## 4. 다음 단계 — Real Run Observer Validation

## 4.1 목표
하나의 canonical run을 선택해서,
observer layer가 실제 세계 흐름을 충분히 잘 드러내는지 검증한다.

### 검증 질문
1. 세계 전체 흐름(world view)이 실제로 읽히는가?
2. 특정 인물(person view)의 arc를 따라갈 수 있는가?
3. 특정 사건(event view)의 ripple이 보이는가?
4. salience detector가 중요한 순간을 제대로 잡는가?
5. replay / jump가 관찰 도구로 쓸 만한가?
6. compare view가 variation 차이를 실제로 보여주는가?

---

## 4.2 추천 대상 run
처음부터 여러 run으로 가지 않는다.

### 우선 1개 run만 선택
**Peter scarcity baseline canonical run**을 1순위로 추천한다.

이유:
- 기존 story / creative / variation 자산과 연결됨
- scarcity는 world-side pressure가 비교적 선명함
- observer view에서 crowd / blame / suspicion / split을 보기 좋음

### 필요 시 2순위
- accusation canonical run

단, 첫 단계는 1개로 충분하다.

---

## 4.3 검증할 View set
다음 4개 view를 반드시 뽑는다.

### A. World View
- 현재 세계 phase
- crowd mood
- blame concentration
- public suspicion
- authority vigilance
- dominant tension

### B. Person View
- 특정 인물 1명
- 추천: Peter
- 최근 20~40 ticks 상태 변화
- pressure exposure
- turning point

### C. Event View
- 핵심 사건 1개
- 추천: accusation 혹은 scarcity spike
- event 발생 → 전파 → 잔향

### D. Compare View
- 같은 anchor의 다른 seed 2~3개 비교
- 같은 scenario 안에서 결과 차이가 observer layer에서도 보이는지 확인

---

## 4.4 Salience validation
Observer Layer의 핵심은 “무엇을 봐야 하는가”를 알려주는 것이다.

그래서 다음 항목을 꼭 점검한다.

- top 5 salient moments가 납득 가능한가
- 실제로 중요한 순간이 빠지지 않는가
- noise가 너무 많이 올라오지 않는가
- low-activity but meaningful moment를 잡을 수 있는가

### 주의
salience quality 평가를 “좋은 이야기냐”로 보면 안 된다.
기준은 오직:
- 관찰 가치가 있는가
- world change가 있는가
- turning point로 보이는가

---

## 4.5 Replay / Jump validation
다음 동작이 실제로 유용한지 확인한다.

- 특정 tick jump
- 특정 event start jump
- turning point bookmark jump
- 최근 N ticks replay
- before/after 비교

### 목표
이 기능이 story debug뿐 아니라,
실제로 **세계 관찰 도구**로도 쓸 수 있어야 한다.

---

## 5. 산출물

다음 단계의 산출물은 아래처럼 정리한다.

### 5.1 Validation 문서
- `docs/observer/REAL_RUN_VALIDATION.md`

포함:
- 사용한 canonical run
- 선택 이유
- 검증한 4개 view
- salience 결과
- replay/jump 체감
- observer layer의 강점 / 약점
- 다음 수정 필요 여부

---

### 5.2 Demo 샘플
- `examples/demo_observer.py` real-run mode 호출 예시
- World View sample
- Person View sample
- Event View sample
- Compare View sample

---

### 5.3 Review 요약
- `docs/observer/REAL_RUN_REVIEW_SUMMARY.md`

포함:
- keep
- weak
- missing
- not useful
- next action

---

## 6. 성공 기준

다음 중 4개 이상 만족하면 Observer MVP는 실사용 가능으로 본다.

1. World View가 실제로 세계 전체 흐름을 이해하게 해 준다
2. Person View에서 인물 arc가 납득 가능하게 보인다
3. Event View에서 사건 ripple이 읽힌다
4. Compare View가 variation 차이를 보여준다
5. Salience top moments가 의미 있다
6. Replay / Jump가 실제 탐색 도구로 쓸 만하다

---

## 7. 실패 기준

다음 중 2개 이상이면 Observer Layer 보완이 필요하다.

1. World View가 단순 로그 요약처럼만 보인다
2. Person View가 renderer 서사보다 정보가 약하다
3. Event View가 사건 전파를 못 보여준다
4. salience가 noise를 너무 많이 뽑는다
5. compare가 차이를 거의 못 보여준다
6. replay / jump가 있으나 실제로 쓸 이유가 없다

---

## 8. 이 단계 이후 분기

## 경우 A — Real-run validation이 좋음
다음 단계는:
- Observer MVP freeze 검토
- Story + Observer 통합 활용
- curated observation pack 혹은 explorer 방향 검토

## 경우 B — 일부 약함
다음 단계는:
- observer core는 유지
- weak area만 국소 patch
- 다시 1 run 재검증

## 경우 C — 전반적으로 약함
다음 단계는:
- observer narrative summary 축소
- salience / compare / replay 중 병목 재설계
- UI나 새 기능 추가 금지

---

## 9. 지금 하지 말아야 할 것

다음은 지금 하지 않는다.

- observer GUI/dashboard 제작
- observer view 종류 추가 확장
- narrator 스타일 늘리기
- quality verdict 자동화
- Talleyrand 3rd scenario
- v1.0 PyTorch encoder
- Branch C 실험 추가
- renderer 추가 cycle
- public-facing polished browser

즉 지금은 **새 기능 추가보다 검증 우선**이다.

---

## 10. Claude Code용 작업 순서

### Step 1
`docs/observer/REAL_RUN_VALIDATION.md` 초안 작성

### Step 2
canonical run 1개 선정
- 기본값: Peter scarcity baseline

### Step 3
동일 run에 대해 다음 4개 출력 생성
- world view
- person view
- event view
- compare view

### Step 4
salience / replay / jump 검증

### Step 5
`docs/observer/REAL_RUN_REVIEW_SUMMARY.md` 작성

### Step 6
성공 / 실패 기준으로 다음 분기 결정

---

## 11. 최종 한 줄 요약

**지금 Observer Layer는 크게 손댈 단계가 아니라,  
실제 simulation run에 붙여서 전지적 관찰자처럼 세계를 볼 수 있는지 검증하는 단계다.  
따라서 다음 최선의 작업은 새 기능 추가가 아니라  
Peter scarcity baseline 같은 canonical real run 하나를 골라  
World / Person / Event / Compare view를 실제로 검증하는 것이다.**
