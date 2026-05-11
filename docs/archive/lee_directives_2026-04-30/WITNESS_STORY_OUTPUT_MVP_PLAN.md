# WITNESS — 한글 스토리 출력 구현 상세 계획서

## 0. 문서 목적

이 문서는 WITNESS 프로젝트의 다음 1차 목표를  
**“엔진 검증”에서 “실제로 읽을 수 있는 한글 스토리 결과물 생성”**으로 전환하기 위한 상세 구현 계획서다.

핵심 목표는 간단하다.

> **현재 WITNESS가 만들어내는 trajectory / probe / annotated output을 바탕으로,  
> 사람이 실제로 읽을 수 있는 한국어 이야기 텍스트를 안정적으로 생성한다.**

이 문서는 다음을 정의한다.

1. 왜 지금 스토리 출력이 1차 목표인지
2. 출력 MVP의 범위
3. 스토리 생성 파이프라인
4. 입력 스키마 / 중간 서사 스키마 / 출력 형식
5. 구현 순서
6. 평가 기준
7. 반복 개선 루프
8. 지금 하지 말아야 할 것

---

## 1. 왜 지금 스토리 출력이 우선인가

지금까지 WITNESS는 다음을 상당 부분 확보했다.

- 세계 커널이 흐른다는 구조적 증거
- readability infra
- annotated probe format
- branch 판단 체계
- canonical / archive / script hygiene
- world-side observables의 초안

하지만 아직 부족한 건  
**“이 엔진이 낳는 결과를 사람이 한국어로 읽을 수 있는가”**다.

현재 상태에서는:
- 분석 문서
- probe
- annotated summary
- world-side observable
이 많지만,

사용자가 실제로 원하는 건:
- 로그가 아니라 이야기
- 표가 아니라 서사
- 구조 설명이 아니라 읽히는 결과물

이다.

따라서 지금부터의 1차 목표는 다음으로 재정의한다.

## 새 1차 목표
**WITNESS의 현재 출력들을 바탕으로,  
짧고 읽히는 한국어 스토리 텍스트를 생성하는 story output layer를 구현한다.**

---

## 2. 목표 범위 (MVP)

이번 계획서에서 말하는 MVP는 “완성형 문학 작품”이 아니다.  
목표는 다음 수준이다.

### MVP 정의
- 1 trajectory / 1 probe / 1 annotated probe를 입력으로 받아
- 1개의 한국어 이야기 텍스트를 생성한다
- 사람이 읽었을 때
  - 사건 흐름이 보이고
  - 압력이 느껴지고
  - 인물/집단 반응이 보이며
  - 회복 / 포화 / 혼합 중 무엇인지 감이 온다

즉, **보고서가 아니라 이야기처럼 읽히는 것**이 기준이다.

### 이번 단계에서 하지 않는 것
- 완전 자유 생성 소설
- 수천 자 장편
- 인물별 화자 전환
- 실시간 인터랙티브 선택지
- 새로운 엔진 메커니즘 구현
- 더 넓은 세계 execution
- neural policy
- 스타일 과도 최적화

---

## 3. 전체 구현 전략

전체 파이프라인은 아래 3단계로 본다.

## 단계 A — World Output Extraction
엔진/annotated probe에서 스토리 생성에 필요한 핵심 정보만 추출

## 단계 B — Narrative Intermediate Representation
추출된 정보를 서사 구조로 재배열
(도입 / 전개 / 분기 / 귀결 / 해설)

## 단계 C — Korean Story Rendering
중간 서사 구조를 한국어 텍스트로 렌더링

핵심 원칙:
- 엔진 output을 바로 자연어로 바꾸지 않는다
- **중간 서사 스키마**를 반드시 둔다
- 그래야 개선이 가능하고, story 품질 문제를 구조적으로 진단할 수 있다

---

## 4. Story Output MVP의 출력 형식

이번 MVP는 2종류만 지원한다.

### Output Type 1 — 요약형
- 길이: 400~800자
- 목적: 빠르게 읽고 흐름 파악
- 형식: 4~6문단 또는 짧은 연속 문단
- 사용처: baseline evaluation, bulk generation

### Output Type 2 — 서사형
- 길이: 1000~1800자
- 목적: 이야기처럼 읽히는지 확인
- 형식: 5단 구조 기반 짧은 서사
- 사용처: 대표 trajectory/probe showcase

### 이번 단계에서 문체는 2개만 허용
1. **건조한 서사형**
   - 과장 없음
   - 기록체에 가까움
   - 사건과 압력이 잘 보이게

2. **감정 서사형**
   - 감정/긴장/회복 흐름을 조금 더 드러냄
   - 단, 과문장 금지
   - 설명보다 장면 중심

### 기본 시점
- **3인칭 관찰자 시점**

이유:
- 세계 전체 흐름도 다뤄야 하고
- 특정 인물 1인칭에 갇히면 world-side observable이 약해진다

---

## 5. 입력 소스 우선순위

스토리 출력은 아래 입력을 우선순위로 사용한다.

### 1순위 — Annotated probe
가장 적합하다. 이유:
- final summary 있음
- primary pressure 있음
- failure mode 있음
- cohort outcome 있음
- world-level dynamics 있음
- event grouping 있음

### 2순위 — Original probe
annotated가 없을 때 fallback

### 3순위 — trajectory JSON / simulation trace
추가 renderer 단계에서 직접 쓰기 위한 source
단, MVP는 annotated 중심이 더 빠르다

### 4순위 — world-side derived summary
필요 시 generator가 계산해서 덧붙이는 보조 정보

---

## 6. 입력 스키마 (Story Extraction Layer)

Story renderer는 annotated probe에서 최소 아래 필드를 읽는다.

### Required fields
- probe_id
- final_summary
- primary_pressure
- failure_mode (optional on non-saturation)
- cohort_outcomes
- accusation_count
- confession_count
- forgiveness_count
- crowd_blame_total
- public_suspicion
- authority_vigilance
- key events (grouped)
- roles present
- locations present

### Recommended additional fields
- top_blame_target
- cohort divergence marker
- event density class
- recovery action dominance
- denial density
- world-memory residue summary

### Extraction 결과 예시
```json
{
  "probe_id": "P6",
  "final_summary": "MIXED",
  "primary_pressure": "scarcity",
  "failure_mode": null,
  "cohort_outcomes": [
    {"location": "L1", "agents": 4, "arc": "recovery"},
    {"location": "L2", "agents": 3, "arc": "saturation"}
  ],
  "event_counts": {
    "accusations": 1,
    "confessions": 142,
    "forgiveness": 142,
    "denials": 447
  },
  "world": {
    "crowd_blame_peak": 8.2,
    "crowd_blame_final": 4.9,
    "public_suspicion_peak": 0.87,
    "authority_vigilance_peak": 0.42
  },
  "key_events": [
    "초기 accusation 발생",
    "denial 반복",
    "confession 누적",
    "cohort split 발생"
  ]
}
```

---

## 7. 중간 서사 스키마 (Narrative IR)

이 단계가 핵심이다.

엔진 출력 → 바로 한국어로 가지 않고, 먼저 아래 구조로 변환한다.

## Narrative IR 구조
```json
{
  "title_hint": "",
  "world_opening": "",
  "initial_tension": "",
  "pressure_arc": "",
  "group_response": "",
  "turning_point": "",
  "outcome": "",
  "world_aftereffect": "",
  "dominant_mode": "",
  "notes": []
}
```

### 필드 설명

#### 7.1 world_opening
- 세계의 시작 상태
- 사건 전 공기
- 어떤 종류의 압력이 깔려 있었는지

#### 7.2 initial_tension
- 첫 accusation / sacred sign / scarcity pressure
- 이야기의 첫 긴장

#### 7.3 pressure_arc
- 압력이 어떻게 커졌는지
- crowd / authority / suspicion / blame가 어떻게 움직였는지

#### 7.4 group_response
- 인물/코호트가 어떻게 반응했는지
- 누가 버티고 누가 무너지고 누가 흔들렸는지

#### 7.5 turning_point
- recovery / saturation / mixed를 가르는 지점
- confession cascade, denial lock, split, easing 등

#### 7.6 outcome
- 최종 arc
- recovery / saturation / mixed / partial / low_activity

#### 7.7 world_aftereffect
- 사건 이후 세계 상태
- suspicion residue, blame persistence, authority vigilance, mood 변화

#### 7.8 dominant_mode
- recovery_dominated
- saturation_dominated
- mixed
- partial
- low_activity

---

## 8. Story Renderer 설계

Renderer는 Narrative IR를 받아 한글 문장으로 풀어낸다.

### 8.1 MVP renderer 방식
처음에는 복잡한 생성기보다 **template-guided rendering**이 맞다.

이유:
- 출력 품질 문제를 진단하기 쉽다
- weird generation을 줄인다
- annotated field와 직접 연결 가능하다

### 8.2 문단 구조
기본 5문단 구조:

1. **도입**
   - 배경 / 공기 / 초기 긴장

2. **압력 상승**
   - 사건 / 비난 / scarcity / sacred / fear

3. **반응 분기**
   - denial / confession / withdrawal / staying / split

4. **귀결**
   - 회복 / 포화 / 혼합

5. **사후 세계**
   - crowd / authority / public attention / residue

### 8.3 렌더링 원칙
- 숫자를 그대로 나열하지 않는다
- 하지만 숫자에 해당하는 의미는 번역한다
- “peak 8.2” 대신 “비난은 빠르게 한곳으로 모였다”
- “authority_vigilance 0.42” 대신 “권위의 시선은 끝까지 느슨해지지 않았다”
- “confessions 142” 대신 “고백은 멈추지 않고 이어졌다”

---

## 9. 한국어 출력 규칙

### 반드시 지킬 것
- 보고서 말투 금지
- 표 해설체 금지
- “이 trajectory에서는” 같은 표현 금지
- 지나친 수식 금지
- 사건 간 연결 없는 병렬 문장 금지
- 기계적 반복 금지

### 허용
- 관찰자 시점
- 의미 번역
- 압력과 반응의 인과 표현
- 집단/세계 단위 묘사

### 피해야 할 것
- 지나친 문학적 과장
- 근거 없는 심리 추정
- 엔진에 없는 내용을 지어내기
- 세계 바깥의 평가 문장
- 메타 설명

---

## 10. MVP 구현 순서

## Phase 1 — Story Spec 고정
산출물:
- `docs/story/STORY_OUTPUT_SPEC.md`

포함:
- output types
- style options
- forbidden phrases
- acceptance criteria

---

## Phase 2 — Extraction Layer 구현
산출물:
- `scripts/story/extract_story_features.py`

역할:
- annotated probe 읽기
- required fields 추출
- JSON intermediate 저장

출력:
- `data/story/story_features/{probe_id}.json`

---

## Phase 3 — Narrative IR builder 구현
산출물:
- `scripts/story/build_narrative_ir.py`

역할:
- extracted features → narrative IR 변환

출력:
- `data/story/narrative_ir/{probe_id}.json`

---

## Phase 4 — Korean Renderer 구현
산출물:
- `scripts/story/render_story_ko.py`

역할:
- narrative IR → 한글 스토리 텍스트

출력:
- `docs/story/generated/{probe_id}_summary_ko.txt`
- `docs/story/generated/{probe_id}_narrative_ko.txt`

---

## Phase 5 — 12개 baseline story 생성
산출물:
- `docs/story/generated/` 전체 세트
- `docs/story/STORY_SET_BASELINE_REVIEW.md`

역할:
- 12개 baseline probes에 대해 한글 story 생성
- 각 story의 읽힘 점검

---

## Phase 6 — 읽힘 평가
평가 축:
- 흐름이 느껴지는가
- world-side가 보이는가
- 보고서가 아니라 이야기처럼 읽히는가
- recovery/saturation/mixed 차이가 느껴지는가
- 과하게 설명적이지 않은가

산출물:
- `docs/story/STORY_READABILITY_REVIEW.md`

---

## 11. 평가 기준 (Acceptance Criteria)

### 11.1 MVP acceptance
다음 중 4개 이상 만족하면 MVP 통과:

1. 12개 중 9개 이상에서 이야기 흐름이 식별 가능
2. recovery / saturation / mixed 구분이 글로 느껴짐
3. crowd / authority / public attention 중 최소 2개가 서사 속에서 보임
4. 문서 요약이 아니라 서사처럼 읽힘
5. probe별 차이가 텍스트에서도 드러남
6. 같은 템플릿 반복 냄새가 심하지 않음

### 11.2 실패 신호
다음 중 2개 이상이면 renderer 재설계 필요:

1. 글이 보고서처럼만 읽힘
2. world-side observable이 거의 안 보임
3. 사건 간 연결이 약함
4. 너무 많은 수치 번역 실패
5. 모든 story가 비슷한 문체/구조로만 나옴
6. saturation과 recovery 차이가 안 느껴짐

---

## 12. 반복 개선 루프

Story 구현 이후에는 아래 루프로 간다.

### Loop A — 읽힘 개선
- 문장 구조
- 문단 구성
- 장면 연결
- 압력 표현

### Loop B — world-side 강화
- crowd / authority / public attention 더 잘 보이게
- world residue 표현 개선

### Loop C — variation 확보
- 같은 템플릿 반복 완화
- probe별 개성 증가

### Loop D — style branching
- 요약형 vs 서사형
- 건조형 vs 감정형

중요:
이 루프도 **결과물 우선**이다.  
새 엔진보다 story output 개선이 먼저다.

---

## 13. 지금 하지 말아야 할 것

- authority autonomy 구현
- shame_decay 구현
- broader world execution
- 새로운 scenario 추가
- world/ legacy 재검토
- neural story generation
- 길고 복잡한 문체 실험
- output 평가 전에 format만 계속 만지기

지금은 “엔진 확장”보다 **story renderer MVP**가 우선이다.

---

## 14. Claude Code용 작업 지시 순서

Claude Code는 다음 순서로 진행한다.

### Step 1
`docs/story/STORY_OUTPUT_SPEC.md` 작성

### Step 2
`extract_story_features.py` 구현

### Step 3
`build_narrative_ir.py` 구현

### Step 4
`render_story_ko.py` 구현

### Step 5
12 baseline probe에 대해 한글 story 생성

### Step 6
`STORY_SET_BASELINE_REVIEW.md` 작성

### Step 7
review 결과 바탕으로 renderer 1회 개선

---

## 15. 최종 한 줄 요약

**지금 WITNESS의 다음 1차 목표는 더 많은 구조 분석이 아니라,  
현재 엔진 출력에서 실제로 읽을 수 있는 한글 이야기 텍스트를 생성하는 것이다.  
이를 위해 annotated probe를 입력으로 쓰고,  
중간 서사 스키마를 거쳐 한국어 story renderer를 만드는 MVP를 먼저 구현한다.**
