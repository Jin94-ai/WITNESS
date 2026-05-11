# WITNESS — 다음 진행사항 작업지시서
## 초점: 잘 나온 점보다 잘 안 나온 점, 해석 리스크, 개선안 중심

작성 목적:
- 최근 WORLD_FLOW_LOOP Iter 1-18 결과를 기준으로, 현재 구조의 **약점**과 **다음 단계의 개선 실험**을 명확히 정리한다.
- 이번 문서는 성과 요약 문서가 아니다.
- 핵심 목표는 다음 1~2 사이클 동안 **무엇을 의심해야 하는지**, **무엇을 검증해야 하는지**, **무엇을 하지 말아야 하는지**를 고정하는 것이다.

---

# 0. 현재 상태에 대한 냉정한 진단

현재 결과는 다음을 보여준다.

- role-cluster 기반 generative world engine이 3 시나리오에서 C_propagating flow에 도달했다.
- conditional role invariance라는 강한 패턴이 관측되었다.
- Iter 7에서 role-conditional motif_action_priors가 주요 구조적 병목으로 드러났다.
- Iter 6의 measurement refinement가 false positive keep을 걷어냈다.

하지만 이것만으로 다음을 주장할 수는 없다.

- universality 달성
- narrative-generative world 달성
- 사람에게 읽히는 서사 생성 입증
- role identity의 보편 법칙 발견
- 현재 구조가 최종 kernel이라는 결론

즉 현재 상태는:

**"핵심 계층 병목을 찾은 상태"이지, "최종 세계 엔진을 확보한 상태"는 아니다.**

---

# 1. 현재 가장 큰 약점

## 1.1 JS 중심 해석 과의존 위험

현재 conditional invariance의 주된 근거는 JS divergence 계열 측정이다.
이건 분명 유용하지만, 다음 한계를 갖는다.

### 문제
- JS는 분포 차이를 잘 보여주지만, **왜** 차이가 났는지는 직접 설명하지 않는다.
- 특정 action 1~2개의 support shift만 커도 JS가 크게 움직일 수 있다.
- motif occupancy 변화, relation 재배열, event composition 차이와 분리해서 보면 오해할 수 있다.
- 현재 관측된 conditional invariance가 "구조적 invariance"인지, "action prior 효과의 직접 반영"인지 JS만으로는 확정하기 어렵다.

### 개선 방향
다음부터 JS는 단독 핵심 지표로 쓰지 말고 반드시 아래를 같이 본다.

- top action family shift
- motif occupancy shift
- relation delta signature
- event exposure asymmetry
- role별 confusion matrix
- per-seed distribution shape

### 작업
- JS 보조 설명 지표 5종 추가
- `distribution_analysis` 결과에 JS 단독 결론 금지
- 각 결과 섹션에 "JS alone cannot determine mechanism" 명시

---

## 1.2 conditional invariance가 self-fulfilling일 가능성

현재 strongest finding은 다음이다.

> role identity는 motif_tendency가 아니라 motif_action_priors에 산다.

이건 매우 중요하다. 하지만 동시에 다음 의심을 반드시 열어둬야 한다.

### 문제
- role-conditioned priors를 강하게 넣었으니, role invariance가 더 잘 나오는 건 일정 부분 자명할 수 있다.
- 즉 현재 finding이 "진짜 구조 발견"인지, "설계자가 넣은 bias의 직접 반영"인지 추가 실험이 필요하다.
- 특히 pressure와 prior의 상호작용이 충분히 보이지 않으면, 이것은 world-reactive identity가 아니라 prior-dominant identity일 수 있다.

### 개선 방향
반드시 prior strength와 pressure strength를 교차 실험한다.

### 작업
다음 4조건 ablation 수행:
- no role priors
- weak role priors
- current role priors
- strong role priors

그리고 각 조건에서 다음 측정:
- C_propagating 도달률
- conditional invariance score
- action family diversity
- motif occupancy stability
- readability proxy

추가로 pressure sweep 수행:
- blame pressure low / medium / high
- authority pressure low / medium / high
- rumor pressure low / medium / high

목표:
- prior만으로 결과가 고정되는지
- pressure가 role expression을 적절히 휘게 하는지
확인한다.

---

## 1.3 C_propagating에 멈춰 있고 D_narrative-generative는 미검증

현재 반복 루프는 C_propagating 도달을 충분히 보여준다.
하지만 그다음 단계인 D_narrative-generative는 아직 아니다.

### 문제
- propagation이 있다고 해서 arc가 있는 것은 아니다.
- layer 간 전파가 있다고 해서 readable world라는 뜻은 아니다.
- statistical separation이 있다고 해서 story-like dynamics가 있다는 뜻은 아니다.
- 현재 caveat로 남겨둔 arc family reproducibility와 external readability는 여전히 공백이다.

### 개선 방향
다음 단계는 propagation 자체를 더 늘리는 것이 아니라, propagation이 **arc-like structure**를 낳는지 확인해야 한다.

### 작업
새 평가축 추가 후보:
- propagation depth
- persistence length
- delayed consequence count
- relation restructuring magnitude
- motif transition coherence
- arc family recurrence

이 축들은 당장 정량 완성까지는 필요 없지만, 적어도 trace 상에서 manual/semiauto 판정이 가능해야 한다.

---

## 1.4 3 시나리오 다양성의 구조적 증명 부족

"3 시나리오 transfer 성공"은 좋은 신호다. 하지만 다음 질문은 아직 답이 없다.

### 문제
- 시나리오가 진짜 구조적으로 다른가?
- 아니면 표면 서사만 다르고 내부 pressure topology는 유사한가?
- 현재 conditional invariance가 사실상 같은 종류의 pressure landscape에서만 통하는 것은 아닌가?

### 개선 방향
시나리오 다양성을 "content가 다름"이 아니라 "구조가 다름"으로 보여줘야 한다.

### 작업
각 시나리오별 다음 프로파일 비교:
- dominant pressures over time
- event family composition
- authority / rumor / crowd contribution ratio
- relation reconfiguration signature
- motif activation fingerprint

목표:
- 3 scenario가 진짜 다른 world dynamics를 갖는지 확인
- 현재 finding이 single topology artifact인지 배제

---

## 1.5 readability 미검증

현재 결과는 내부 엔진 관점에서 매우 의미 있다.
하지만 외부 독자가 봤을 때 "이게 진짜 흐름처럼 읽히는가"는 별개다.

### 문제
- 내부 metric이 좋다고 해서 사람이 봐도 arc가 보이는 건 아니다.
- statistical separation은 있는데, 실제 trace는 여전히 랜덤 로그처럼 보일 수 있다.
- 현재 프로젝트의 장기 목표가 생성 원리라 해도, 최소한 인간이 읽을 수 있는 구조 신호는 있어야 한다.

### 개선 방향
blind readability check를 도입한다.

### 작업
story probe 10개 정도를 뽑아 라벨을 숨기고 다음 질문으로 점검:
- 이 흐름은 random log처럼 보이는가?
- 어떤 pressure가 핵심이었는가?
- 관계 변화가 읽히는가?
- 동일 인물/집단의 방향성이 읽히는가?
- arc 비슷한 곡선이 느껴지는가?

평가자는:
- Lee 본인
- 가능하면 외부 1~2인
- 가능하면 trajectory category를 모르는 상태

---

## 1.6 dead / over-dominant layer audit 미완료

반복 루프는 성공적으로 돌아갔지만, 여전히 어떤 레이어는 과대기여 또는 무기여 상태일 수 있다.

### 문제
- rumor layer가 이번엔 살아났지만 계속 핵심인지 모른다.
- authority layer가 특정 조건에서만 반응할 수도 있다.
- crowd는 proxy 수준에 머물렀을 수 있다.
- memory layer는 실제로 후속 가능성 지형을 바꾸는지 더 확인이 필요하다.
- role transition mechanism은 처음에는 breakthrough로 기대됐지만 실제론 counter_div 0.0이었다.

### 개선 방향
최종 기여도 감사표를 만들어야 한다.

### 작업
각 kernel/layer/process를 아래로 분류:
- indispensable kernel
- supporting but insufficient
- neutral / low effect
- misleading / false-positive source

현재 provisional 분류:
- indispensable: role-conditioned motif_action_priors, action→rumor amplification
- supporting: world memory, climate sensitivity, role transition
- audit needed: crowd proxy, authority vigilance, shame_climate persistence

---

# 2. 다음 단계에서 하지 말아야 할 것

## 금지 1 — universality 선언
아직 3 시나리오 성공은 universality가 아니다.

## 금지 2 — 바로 대규모 population 확장
지금은 기여 구조와 계층 병목을 더 단단히 해야 한다.

## 금지 3 — neural policy 도입
현재 구조적 finding을 rule-based kernel 차원에서 먼저 고정해야 한다.

## 금지 4 — 새 변수 / 새 레이어 대량 추가
현재 병목은 변수 부족보다 계층 결정권 문제다.

## 금지 5 — readability를 무시하고 수치만 쫓기
내부 metric overfit 위험이 크다.

## 금지 6 — prior 강화만으로 결과를 밀어붙이기
prior-dominant world가 되면 world-reactive generative engine이 아니다.

---

# 3. 다음 진행사항 — 우선순위 작업지시

---

## Step 1 — Role Prior Ablation Matrix 수행 (최우선)

### 목적
Iter 7 finding이 진짜 구조 병목인지 확인한다.

### 실험 조건
다음 4조건을 동일한 micro-world benchmark에 적용:
- no role priors
- weak role priors
- current role priors
- strong role priors

### 측정 지표
- C_propagating 도달률
- conditional invariance score
- action family diversity
- motif occupancy stability
- rumor amplification persistence
- readability proxy

### 기대하는 해석
- no priors에서 흐름 붕괴 → prior 필요성 확인
- current에서 최적, strong에서 과도 경직 → sweet spot 확인
- strong에서도 pressure responsiveness 유지되면 robust
- strong에서 pressure responsiveness 사라지면 prior over-dominance 신호

### 산출물
- `docs/world_flow/ROLE_PRIOR_ABLATION.md`
- 결과 요약 테이블
- 각 조건별 대표 story probe 2개

---

## Step 2 — Pressure × Prior Interaction Sweep

### 목적
role identity가 pressure에 의해 적절히 휘는지 확인한다.

### sweep 대상
- blame pressure: low / medium / high
- authority pressure: low / medium / high
- rumor pressure: low / medium / high

가능하면 3×3×3 전수보다 우선 blame/authority 축부터 시작.

### 측정
- action family shift
- motif shift
- relation delta
- invariance 유지 여부
- scenario별 JS, but JS alone 금지

### 핵심 질문
- pressure가 role expression을 실제로 재구성하는가?
- 아니면 priors가 결과를 거의 고정하는가?

### 산출물
- interaction heatmap
- role별 response surface 요약
- `docs/world_flow/PRESSURE_PRIOR_INTERACTION.md`

---

## Step 3 — Scenario Diversity Structural Audit

### 목적
3 scenario transfer가 실제 구조적 다양성을 의미하는지 확인한다.

### 해야 할 것
각 시나리오에 대해 다음 5가지 fingerprint 산출:
- dominant pressures over time
- event family composition
- rumor/authority/crowd contribution ratio
- relation restructuring signature
- motif activation fingerprint

### 판정 기준
아래 중 하나면 문제:
- 세 시나리오가 거의 같은 pressure topology를 가짐
- motif activation fingerprint가 사실상 동일
- contribution ratio가 거의 같음

### 목표
"content가 다르다"가 아니라
"world dynamics topology가 다르다"를 보여줘야 한다.

### 산출물
- `docs/world_flow/SCENARIO_DIVERSITY_AUDIT.md`
- topology similarity matrix

---

## Step 4 — Readability Blind Check

### 목적
내부 지표와 인간이 읽는 흐름 사이의 간극을 확인한다.

### 절차
- story probe 10개 선정
- label, metric, scenario 정보 가리고 제시
- 다음 질문으로 평가

#### 질문
1. 이 흐름은 random log처럼 보이는가?
2. 어떤 pressure 또는 갈등축이 중심처럼 보이는가?
3. 관계 변화가 실제로 읽히는가?
4. 사건이 누적되어 다음 장면 가능성을 바꾸는가?
5. arc-like curve가 보이는가?

### 결과 해석
- 내부 metric high인데 readability low → metric overfit 위험
- readability high인데 metric low → evaluator 구조 수정 필요

### 산출물
- `docs/world_flow/READABILITY_BLIND_CHECK.md`
- human notes raw appendix

---

## Step 5 — Flow Quality Metric v2 설계

### 목적
C_propagating 내부 품질을 더 잘 본다.

### 추가할 축 후보
- propagation depth
- persistence length
- delayed consequence count
- relation restructuring magnitude
- motif transition coherence
- arc family recurrence

### 주의
한 번에 모두 자동화하려 하지 말 것.
우선 manual/semiauto 판정 가능하게 정의하고, 그 뒤 자동화한다.

### 산출물
- `docs/world_flow/FLOW_QUALITY_V2.md`

---

## Step 6 — Layer Contribution Audit

### 목적
이번까지 살아남은 구조 중 정말 필수인 것과 아닌 것을 구분한다.

### 분류 카테고리
- indispensable kernel
- supporting but insufficient
- low-effect / optional
- misleading / false-positive source

### 꼭 포함할 항목
- role transition mechanism
- action→rumor amplification
- world memory
- climate sensitivity
- role priors
- crowd proxy
- authority vigilance
- shame_climate
- memory persistence

### 산출물
- `docs/world_flow/LAYER_CONTRIBUTION_AUDIT.md`

---

# 4. 실험 설계 원칙

## 원칙 1
한 번에 하나의 구조 가설만 강하게 건드릴 것.

## 원칙 2
"좋아 보인다"가 아니라 반드시 benchmark scenario에서 비교할 것.

## 원칙 3
모든 keep는 다음 질문을 통과해야 한다.
- 이 변경 없이는 어떤 현상이 사라지는가?
- 이 변경으로 어떤 리스크가 새로 생기는가?
- 이 변경은 다른 시나리오에서도 유지되는가?

## 원칙 4
결과가 좋게 나와도 magnitude는 정직하게 보정할 것.
Iter 14 → Iter 15 correction 같은 태도를 유지.

## 원칙 5
읽히지 않는 세계는 통계적으로 좋아도 보류할 것.

---

# 5. keep / rollback / refine 결정 규칙

## Keep
- effect가 재현됨
- 측정 artifact 가능성이 낮음
- 다른 시나리오에서도 유지됨
- readability와 구조 해석이 크게 충돌하지 않음

## Rollback
- effect가 특정 metric 하나에만 의존
- 다른 지표/사람 판독과 충돌
- pressure responsiveness를 죽임
- role prior over-dominance를 유발

## Refine
- 방향은 맞으나 과도하거나 약함
- scenario별 편차가 큼
- 일부 지표에서는 좋고 일부에선 악화

---

# 6. 이번 단계의 완료 기준

아래가 충족되면 이번 단계는 완료로 본다.

1. role prior finding이 ablation으로 잠김
2. pressure × prior 상호작용이 확인됨
3. 3 scenario가 구조적으로 다른 topology를 가진다는 증거가 나옴
4. readability blind check 결과가 확보됨
5. C_propagating 내부 품질을 보는 v2 metric 초안이 생김
6. kernel / support / dead layer 분류표가 완성됨

---

# 7. 이번 단계의 가장 중요한 질문

이번 단계에서 계속 붙잡아야 할 질문은 하나다.

> **"지금 관측된 conditional invariance가 정말 world-reactive generative identity의 증거인가, 아니면 role-conditioned prior의 직접 반영인가?"**

이 질문에 더 강하게 답하기 전에는:
- universality
- narrative-generative
- larger population
- neural transition
을 서두르지 않는다.

---

# 8. 한 줄 요약

**다음 단계의 목표는 성과 확대가 아니라, 이번 finding의 약점을 찌르고도 살아남는지 확인하는 것이다. 핵심은 role priors의 구조적 발견을 ablation·interaction·readability·layer audit로 잠그는 것.**
