# WITNESS v2.0 — Spike 6: 신경망 전환의 시작

**생성 배경:**
Spike 1-5에서 구축한 규칙 기반 세계는 "발견"의 원리적 한계에 도달했다.
규칙 기반 엔진에서 나타나는 인과는 Lee가 손으로 배선한 것의 재생일 뿐,
진짜 emergent가 아니다. 이 한계를 돌파하기 위해 신경망 학습으로 전환한다.

**선행 조건:**
Spike 5 Part 1/2 완료. 1176+ fast tests green. ABSOLUTE RULES #1-10 준수.
Person Engine v1.0 Stage 2 계획 (PyTorch drive encoder) 미착수 상태.

**폐기:**
`WITNESS_ROADMAP_SPIKE6_TO_8.md` (Discovery Target 중심 로드맵)는 폐기.
방향이 빗나가 있었음.

---

## 0. 이 Spike의 본질

### 0.1 왜 신경망인가

Lee의 원래 비전 한 문장:

> *"신경망 학습을 통해 천변만화하는 세상을 시뮬레이터로써 구축하고 싶다."*

"천변만화"는 규칙 기반으로 불가능하다. 규칙 기반에서는:

- `if x > threshold: action_A` → Lee가 선언한 연결
- `weight=0.15 between rumour and jesus_movement` → Lee가 선언한 가중치
- `Judas → betray → arrest chain` → Lee가 선언한 배선

이런 엔진에서 "Judas 제거 → 예수운동 62% 붕괴"는 **발견이 아니라 재생**이다.
아무도 그 연결을 몰랐던 상태에서 알아낸 것이 아니고, 처음부터 Lee가
설계한 연결이 실행된 것일 뿐이다.

신경망은 다르다:
- 규칙이 없는 상황에서 **보간된 확률 분포**로 행동
- Lee도 예측 못 한 조합 → **진짜 emergent**
- 훈련 데이터에서 **스스로 패턴을 추출**

**규칙 기반 세계는 버리는 게 아니다.** 신경망 훈련을 위한 **데이터 생성기**로
역할이 전환된다. 지금까지의 Spike 1-5는 "하드코딩된 배선"이 아니라
"학습 대상 분포"로 재해석된다.

### 0.2 이 Spike가 안 하는 것

❌ 세계를 더 두껍게 만들기 (agent 추가, 경제 확장 등)
❌ 실험 프레임워크 확장 (noisy intervention, metric invariance 등)
❌ Discovery Target 정의
❌ 외부 리뷰 패킷 작성
❌ 논문 관련 작업

**이 Spike는 오직 "규칙 기반 Peter → 신경망 Peter 전환"의 첫 걸음에 집중한다.**
다른 agent(Jesus, Judas, Pilate 등)는 건드리지 않는다. 세계의 다른 레이어도
건드리지 않는다.

### 0.3 왜 Peter부터인가

1. **Separability 1.93** — 이미 측정된 값, 학습 feasibility 확보
2. **가장 풍부한 기존 자산** — Person Engine 1003 tests, 4 content packs 중
   Peter가 가장 성숙
3. **50일 분량의 규칙 기반 데이터 생성 가능** — 즉시 훈련 데이터 확보
4. **실패해도 scope 제한** — Peter만 실패하고 다른 agent는 규칙 기반 유지

Talleyrand separability 0.05는 여전히 deferred. 다른 agent는 Spike 7+에서
Peter 성공 후 점진 전환.

---

## 1. ABSOLUTE RULES 변경

### Rule #10 현상 유지

> 세계 확장 Spike에서는 counterfactual 실험을 추가하지 않는다.

이 Spike는 세계 확장이 아니라 **기존 Peter의 작동 방식 전환**이므로 Rule #10
영향권 밖. 단, **새 intervention JSON 추가는 여전히 금지** (Spike 8+의 몫).

### Rule #11 신설 (이 Spike부터 적용)

> **신경망 전환 시 규칙 기반 fallback을 제거하지 않는다.**
> 학습된 모델과 규칙 기반 모델이 동일 인터페이스로 공존 가능해야 하며,
> 전환은 **선택적**이어야 한다. 학습 실패 시 규칙 기반으로 즉시 되돌릴 수 있어야 한다.

이유: 학습이 실패하거나 불안정할 때 기존 1176+ tests가 전부 깨지면 복구 불가.
이중 경로(dual-path)를 유지하는 것이 Lee의 안전장치.

---

## 2. Spike 6의 영역 (구체적 선언 회피)

**이 섹션은 의도적으로 구체적 목록을 만들지 않는다.**

지엽적 목록(5개 action 정의, 10개 test 케이스 등)을 박는 순간
"하드코딩 보완"이 반복된다. 대신 **방향만 선언**하고, 세부는 Claude Code와
Lee의 판단에 맡긴다.

### 2.1 방향

**규칙 기반 Peter의 행동 선택을 학습된 모델로 대체한다.**

Peter는 현재 `if-else` 형태의 규칙으로 action을 선택하고 있다. 이를
신경망이 학습한 분포에서 샘플링하도록 전환한다. 다른 측면(state 업데이트,
context 해석, visible_signal 등)은 건드리지 않는다.

### 2.2 무엇이 "완료"인가

**Lee가 판단한다.** 수치 기준 없음.

Claude Code가 구현을 완료했다고 보고하면, Lee가 돌려보고:
- *"Peter가 이전과 다르게, 그러나 자연스럽게 행동하는가?"* — Lee 판단
- *"예측 못 한 상황에서도 말이 되는 선택을 하는가?"* — Lee 판단
- *"이제 Peter가 살아 움직이는가?"* — Lee 판단

Lee가 *"아직 얇다"* 고 느끼면 Spike 6이 끝난 게 아니다. Lee가 *"됐다"*
고 느낄 때까지 반복.

### 2.3 불확실성 허용 범위

**이 Spike는 실패 가능성을 허용한다.**

- 학습이 수렴 안 할 수 있음
- 학습된 Peter가 규칙 기반보다 이상하게 행동할 수 있음
- Stage 2 PyTorch 전환이 RTX 2070 SUPER에서 예상보다 오래 걸릴 수 있음

실패 시: Rule #11에 따라 규칙 기반으로 rollback, 원인 분석, 재시도.
실패 자체가 학습 자산. 논문적 성과가 없어도 OK.

---

## 3. Claude Code의 자율 판단 영역

Claude Code는 다음을 **스스로 결정**한다. Lee에게 매번 묻지 말 것:

- 신경망 아키텍처 선택 (MLP? Transformer? 작은 것부터 시작)
- 훈련 데이터 생성 방식 (규칙 기반 시뮬레이션 몇 seed? 몇 일?)
- Loss function 설계 (behavior cloning? RL?)
- Hyperparameter (learning rate, batch size, epochs)
- PyTorch 버전, CUDA 설정, device 관리
- 학습된 모델과 규칙 기반 모델의 인터페이스 통합 방식
- 테스트 작성 방식 (학습 모델 자체 테스트는 어떻게?)

**단, 다음은 Lee 판단 필요:**

1. **학습 시도가 3회 연속 실패(수렴 안 함 / loss explosion / device error)** 했을 때
2. **아키텍처/전략 변경이 필요한 근본적 설계 판단**을 해야 할 때
3. **기존 1176+ tests 중 5개 이상이 깨지는데 원인이 구조적**일 때
4. **Peter separability 1.93 측정이 현 코드베이스에서 불가능**할 때
5. **훈련 데이터 생성을 위해 Person Engine 구조를 수정**해야 할 때
   (Rule #6 위반 여부 판단)

---

## 4. 산출물 (최소 요구사항)

### 4.1 코드

```
engine/peter/
  neural/
    __init__.py
    model.py              # Peter behavior 학습 모델
    trainer.py            # 훈련 루프
    dataset.py            # 규칙 기반 → 훈련 데이터 변환
    inference.py          # 학습된 모델 사용 시 인터페이스
  behavior_selector.py    # 기존 규칙 기반 + 신규 신경망 dual-path
```

구체적 파일 구조는 Claude Code 재량. 위는 예시.

### 4.2 문서

```
docs/person/STAGE2_PETER_PROGRESS.md    (신규)
```

내용:
- 매 세션마다 진행 기록 (통상 "현재 판단 / 실행한 일 / 나온 결과 / 다음 액션")
- 실패한 시도도 기록 (성공만 기록하지 말 것)
- Lee가 중간에 보고 방향 조정 가능하도록 구조화

**생성 금지:**
- `docs/world/SPIKE_6_REVIEW.md` — 외부 리뷰 패킷 작성 금지
- `paper_data/` 업데이트 금지
- `docs/world/WORLD_SPIKE_6_*.md` — 이건 world 작업이 아님

### 4.3 테스트

**신규 테스트는 최소화.** 기존 1176+ tests 유지가 더 중요.

추가할 만한 테스트:
- `tests/test_person/test_peter_neural_dual_path.py` — 학습 / 규칙 경로 둘 다 작동
- `tests/test_person/test_peter_neural_fallback.py` — Rule #11 준수 확인

**금지:**
- 학습된 모델의 "정답" 테스트 (behavior가 규칙 기반과 동일한지 확인하는 류)
- Cohen's d / p-value 계산
- 성능 벤치마크 테스트

---

## 5. 진행 순서 (권장, 강제 아님)

Claude Code가 다음 순서를 따를 필요는 없음. 하지만 참고용:

**Phase A — 기반 구축:**
규칙 기반 Peter의 behavior selection 지점을 분리. PyTorch 환경 확인.
Peter separability 1.93 재측정 (현 코드에서 가능한지 확인).

**Phase B — 훈련 데이터 생성:**
규칙 기반 Peter를 N seeds × M days 돌려서 (state, action) 쌍 수집.
N, M은 Claude Code 판단.

**Phase C — 모델 훈련:**
작은 모델부터. 수렴 확인. 성능 비교는 Lee 판단.

**Phase D — 통합:**
학습 모델을 Peter behavior selector에 dual-path로 연결. Rule #11 준수.
기존 tests 유지 확인.

**Phase E — Lee 검토:**
Lee가 돌려보고 "됐다" / "아직" 판단.

---

## 6. 피해야 할 함정 (이번 대화에서 확인된 것들)

### 6.1 지엽적 목록 만들기

이전 Spike 5에서 "5 actions, 6 locations, 3 economy layers" 같은
지엽적 목록을 박았다. 이번 Spike에서는 금지. **방향만 제시하고 세부는 재량.**

### 6.2 "발견 메시지" 먼저 정하기

ChatGPT 지적을 오해해서 "Discovery Target부터"로 갔던 방향은 폐기. 세계가
신경망으로 살아난 뒤에야 "무엇을 발견할 수 있는지"가 의미를 가진다. 지금은
아니다.

### 6.3 완료 조건을 수치로 박기

"Peter separability가 X 이상" / "action 예측 accuracy Y% 이상" 같은 수치 목표
금지. 수치 목표를 박는 순간 Claude Code가 그 수치에 맞춰 하드코딩 최적화를
한다. **완료는 Lee의 감각 판단.**

### 6.4 다른 Spike로 가지치기

학습된 Peter가 작동하면 "이제 Judas도" / "이제 Jesus도" 가지치기 유혹이 생김.
**이 Spike는 Peter만.** 다른 agent는 Spike 7+의 몫.

### 6.5 ChatGPT 지적을 이 Spike에 끌어오기

ChatGPT의 5개 지적(causal variation test, noisy intervention, metric
invariance, Jesus dominance, aggregation semantics)은 전부 **규칙 기반 세계
위에서의 보완**이다. 신경망 전환 후에는 대부분 의미가 달라진다. **이 Spike에
끌어오지 말 것.**

---

## 7. 세션 관리

Spike 5 Part 1+2가 32 루프 + 보완 6 루프였음. Stage 2 전환은:

- **PyTorch 환경 확인 + 데이터 생성:** 1 세션
- **모델 훈련 + 수렴 확인:** 1-2 세션 (실패 시 더)
- **Dual-path 통합 + Lee 검토:** 1 세션

**한 세션에 전부 시도 금지.** 각 Phase 완료 후 Lee 확인.

세션 간 context 유지를 위해 `STAGE2_PETER_PROGRESS.md` 매 세션 업데이트 필수.

---

## 8. 실패 시나리오 대응

### 8.1 학습이 수렴 안 할 때

- 3회 시도 후 Lee에게 보고
- 규칙 기반 rollback (Rule #11)
- 원인 분석 (데이터 부족? 아키텍처? Feature engineering?)
- 필요 시 Peter 대신 더 쉬운 agent로 전환 검토

### 8.2 학습된 Peter가 이상하게 행동할 때

- Lee가 "이상함"을 판단
- Claude Code는 기술적 진단만 (loss 수렴 여부, validation metric 등)
- 행동의 "자연스러움"은 Lee 판단 영역

### 8.3 PyTorch 환경 이슈 (CUDA, device, 메모리)

- RTX 2070 SUPER 8GB 기준으로 설계
- OOM 발생 시 batch size 축소 먼저 시도
- 모델 크기 축소는 Lee 보고 후 결정

### 8.4 Person Engine 수정이 불가피할 때

- Rule #6 위반 여부 Lee 확인 필요
- 가능하면 `engine/peter/neural/` 하위에서 해결
- Person Engine 루트 수정은 최후 수단

---

## 9. 이 Spike의 전체 정신

**Lee가 원하는 것:**
> *"신경망 학습을 통해 천변만화하는 세상을 시뮬레이터로써 일단 구축"*

**Claude Code가 하지 말아야 할 것:**
- 세계를 더 구체적으로 만들기
- 발견 메시지 정하기
- 실험 프레임워크 확장하기
- 수치 완료 기준 박기

**Claude Code가 해야 할 것:**
- Peter 하나를 규칙 기반에서 신경망 기반으로 전환
- Lee가 "이제 Peter가 살아 움직이네"라고 느낄 때까지
- 실패해도 괜찮음, 배우는 과정

**Lee가 하는 것:**
- 중간중간 돌려보고 감각 판단
- "됐다" / "아직" 피드백
- 구조적 결정이 필요한 지점에서만 개입

---

## 10. 한 줄 요약

**"Peter 한 명을 신경망으로 살아 움직이게 한다. 다른 건 건드리지 않는다.
완료는 Lee가 느낌으로 판단한다."**

---

## 부록 — Lee에게

이 파일은 의도적으로 구체적 목록을 피했다. 이전 대화에서 반복된 패턴
(지엽적 목록 → 하드코딩 최적화 → "발견" 착시)을 끊기 위함이다.

만약 이 파일이 너무 추상적이라 Claude Code가 진행을 못 한다면, 그건
Claude Code의 한계이고 Lee가 그 지점에서 개입해주면 된다. 추상성은 버그가
아니라 feature다.

Rule #10, #11을 명시적으로 유지한 건 규칙 기반 세계가 갑자기 사라지는 걸
막기 위함이다. Stage 2 전환은 대체가 아니라 **공존의 시작**이다. 신경망이
안정화되면 규칙 기반 의존도가 자연스럽게 줄어들고, 그게 "천변만화"의 첫
감각일 것이다.
