# WITNESS — Creative IP 트랙 개선 반영 작업 지시서

## 0. 문서 목적

이 문서는 기존 `WITNESS — Creative IP 트랙 전환 기획안`의 큰 방향은 유지하되,  
범위를 줄이고 결과물 중심으로 재배치한 **개선 실행 지시서**다.

핵심 수정은 하나다.

> **Phase J를 그대로 크게 시작하지 말고,  
> 먼저 J-Alpha에서 “같은 anchor의 5개 변주가 실제로 서로 다른 한글 이야기로 읽히는가”를 증명한다.  
> 그 다음에야 J-Beta에서 taxonomy / selector / labeling을 확장한다.**

즉, 이번 문서의 목적은:
- 방향은 유지
- 범위는 축소
- 결과물은 앞당기기
- 구조 일반화는 나중으로 미루기

이다. 기존 Creative IP 전환의 핵심 방향인
**“소설/웹소설 + 다영역 IP 자산 생성기”**
라는 정체성은 그대로 유지한다. 다만 실행 순서를 바꾼다. fileciteturn11file0

---

## 1. 유지되는 핵심 방향

다음 판단은 그대로 유지한다.

### 1.1 프로젝트 정체성
- 연구 트랙 중심이 아니라 **Creative IP 트랙 우선**
- 산출물 중심은 paper가 아니라 **한글 이야기 텍스트**
- cross-seed variation은 statistical weakness가 아니라 **운명 변주 자산**으로 해석

이 방향 전환 자체는 유효하다. 기존 기획안의 핵심 방향은 맞다. fileciteturn11file0

### 1.2 4-layer 구조
다음 4-layer 구조도 유지한다.

- Layer 1: World Simulation
- Layer 2: Story Unit Taxonomy
- Layer 3: Story Selector / Framer
- Layer 4: Style-aware Renderer

이 구조는 프로젝트를 디버깅 가능하게 유지하는 데 유리하므로 폐기하지 않는다. fileciteturn11file0

### 1.3 1차 타겟
- 첫 IP 타겟은 **소설 / 웹소설**
- 드라마 / 웹툰 / 게임 등은 후순위

이 우선순위도 그대로 유지한다. fileciteturn11file0

---

## 2. 기존 기획안의 문제점

기존 기획안은 방향은 좋지만, 실행 범위가 너무 크다.

### 2.1 범위 과대
기존 J1-J8에는 다음이 한 번에 들어 있다.

- Rule 추가
- renderer 진단
- taxonomy 문서화
- 70+ trajectory 라벨링
- selector 구현
- renderer 개선
- 통합 데모

이건 자율 진행 기준으로는 한 번에 너무 크다. 특히
**70+ trajectory 라벨링**
은 결과물보다 분류 체계를 먼저 키우게 만들 위험이 있다. fileciteturn11file0

### 2.2 결과물 지연 위험
Creative 트랙 전환의 핵심은
“문서”가 아니라
**실제로 읽히는 결과물**
인데, 기존 기획은 taxonomy / selector / labeling이 앞서고 결과물이 뒤로 밀릴 수 있다. fileciteturn11file0

### 2.3 J2 병목
기존 기획은 J2에서 Lee가 renderer 샘플 5개를 보고 좋고 나쁨을 판단해야 한다고 했는데,  
이 판단이 없으면 J6 renderer 개선도 흔들린다.

즉 J2를 늦게 두면 전체가 다시 멈출 가능성이 있다. fileciteturn11file0

### 2.4 Selector 비대화 위험
기존 기획안도 경고했듯, selector가 과하게 정교해지면
“또 다른 rubric”
이 된다. 이건 Creative 트랙의 목적에 맞지 않는다. fileciteturn11file0

---

## 3. 개선 핵심 — Phase J를 J-Alpha / J-Beta로 분리

## 결론
Phase J를 두 단계로 쪼갠다.

### J-Alpha
**목표: 작은 curated set에서 creative track의 핵심 가설을 증명**

질문:
> **같은 anchor의 5개 seed가 실제로 서로 다른 한국어 이야기로 읽히는가?**

이걸 먼저 증명한다.

### J-Beta
**목표: J-Alpha가 성공했을 때 taxonomy / selector / labeling을 확장**

즉:
- 먼저 작은 데모
- 그다음 일반화

순서로 바꾼다.

---

## 4. J-Alpha — 1차 증명 단계

## 4.1 J-Alpha의 목적

다음 한 문장을 증명하는 것이 목적이다.

> **“같은 세계 조건에서 출발한 5개의 seed가,  
> 사람이 읽었을 때 서로 다른 운명/아크를 가진 한국어 이야기 5편으로 읽힌다.”**

이게 되면:
- cross-seed variation을 IP 자산으로 볼 수 있고
- selector의 존재 이유가 생기고
- renderer 개선 방향도 분명해진다

이게 안 되면, Creative IP 전환은 아직 이르다.

---

## 4.2 J-Alpha의 범위

기존 J4의 70+ trajectory 전체 라벨링은 하지 않는다.

### 이번 단계에서 사용할 curated set
최대 **10~15 trajectories**만 사용한다.

구성 추천:
- Peter anchor 1개 × 5 seeds
- Van Gogh anchor 1개 × 5 seeds
- 필요하면 Branch C anchor 1개 × 3~5 seeds는 보조

즉 J-Alpha는
**“많이 다루기”가 아니라 “작게 증명하기”**
가 목표다.

---

## 4.3 J-Alpha 핵심 산출물

반드시 나와야 하는 산출물은 3개다.

### A. Anchor Variation Story Pack
예:
- `outputs/creative_demo/peter_anchor_5_variations_ko.txt`
- `outputs/creative_demo/vangogh_anchor_5_variations_ko.txt`

각 파일에는 같은 anchor에서 나온 5개 seed story가 들어간다.

### B. Variation Reading Review
예:
- `docs/creative/VARIATION_READING_REVIEW.md`

질문:
- 정말 서로 다른 이야기로 읽히는가
- 차이가 단순 문체 차이가 아니라 구조 차이로 읽히는가
- world-side cause가 보이는가
- “같은 출발에서 다른 결말”이 느껴지는가

### C. Renderer Diagnosis + Fix Note
예:
- `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md`

좋은 샘플 / 나쁜 샘플 / 반복 표현 / 문제 카테고리 기록

---

## 4.4 J-Alpha에서 반드시 먼저 해야 할 일

### Step A1 — Renderer 샘플 진단 (최우선)
기존 J2를 앞으로 당긴다.

Lee가 현재 renderer 출력 5개를 보고:
- 좋다
- 애매하다
- 나쁘다
를 표시해야 한다.

이건 aesthetic 취향 질문이 아니라,
**Creative ground truth 확보**
다.

#### 산출물
- `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md`

#### 분류 항목 예시
- 문장이 너무 보고서 같다
- 감정/장면 전환이 약하다
- world-side가 잘 안 드러난다
- 사건은 있는데 이야기처럼 안 읽힌다
- 같은 템플릿 냄새가 강하다

이 진단 없이는 J-Alpha가 의미 없이 돌아간다.

---

### Step A2 — Minimal Story Unit 정의
full taxonomy를 만들지 않는다.
먼저 3개만 정의한다.

- Person Arc
- Event Arc
- World Arc

Time-slice는 모드가 아니라 slicing parameter로만 둔다.

#### 목적
지금은 4-layer 중 Layer 2를 “최소 동작” 수준으로만 세운다.
완전 taxonomy 문서는 J-Beta로 미룬다.

#### 산출물
- `docs/specs/STORY_UNIT_TAXONOMY_MINIMAL.md`

---

### Step A3 — Curated Anchor Set 확정
다음만 확정한다.

- Peter anchor 1개
- Van Gogh anchor 1개
- 각 5 seeds

필요하면 보조 anchor 1개 추가.
하지만 최대 15 trajectories를 넘기지 않는다.

#### 산출물
- `docs/creative/CURATED_ANCHOR_SET_ALPHA.md`

포함:
- anchor 이름
- 사용 seeds
- 왜 이 anchor를 선택했는지
- 기대하는 arc 차이

---

### Step A4 — Minimal Selector
full selector API를 만들지 않는다.
J-Alpha에서는 다음 2개만 있으면 충분하다.

1. 같은 anchor의 5개 seed를 묶어서 가져오기
2. 현재 curated set에서 “가장 읽을 가치 있는” anchor를 고르기

즉 J-Alpha selector는 검색기가 아니라
**anchor variation bundler**
수준으로 제한한다.

#### 산출물
- `engine/story/selector.py` (minimal)
- `tests/test_story/test_selector_alpha.py`

---

### Step A5 — 소설/웹소설 톤 renderer 개선
기존 J6를 유지하되, 목표를 낮춘다.

목표:
- 완벽한 문체 금지
- **같은 anchor 5개가 서로 다르게 읽히는 것**이 핵심
- “읽을 만하다” 수준이면 통과

우선 개선 항목은 **최대 3개만** 고른다.
예:
1. 보고서 같은 문장 줄이기
2. 압력 상승 문장 강화
3. ending 차별화

#### 산출물
- `engine/story/renderer.py` 또는 기존 위치 개선
- `docs/creative/NOVEL_TONE_GUIDE_ALPHA.md`
- before / after 비교 예시

---

### Step A6 — 5 Variation Demo 생성
J-Alpha의 핵심 증명 단계.

각 anchor에 대해 5개 variation story를 출력한다.

#### 필수 질문
- 5개가 서로 다른 이야기인가
- 차이가 엔진 차이에서 오는가
- renderer가 그 차이를 죽이지 않았는가
- IP 자산처럼 보이는가

#### 산출물
- `outputs/creative_demo/peter_anchor_5_variations_ko.txt`
- `outputs/creative_demo/vangogh_anchor_5_variations_ko.txt`
- `docs/creative/VARIATION_READING_REVIEW.md`

---

## 5. J-Alpha의 성공 / 실패 기준

## 성공 기준
다음 중 4개 이상 만족하면 성공으로 본다.

1. 같은 anchor의 5개 seed가 최소 3개 이상 명확히 다르게 읽힌다
2. 차이가 단순 문체가 아니라 구조 차이로 보인다
3. person / event / world 중 최소 2개 층위가 읽힌다
4. renderer가 trajectory 차이를 죽이지 않는다
5. Lee가 “이건 IP 변주로 쓸 수 있겠다”고 판단한다
6. 반복 템플릿 냄새가 치명적이지 않다

## 실패 기준
다음 중 2개 이상이면 J-Beta로 가지 않는다.

1. 5개가 거의 같은 이야기로 읽힌다
2. 차이가 seed가 아니라 renderer 랜덤성처럼 느껴진다
3. world-side cause가 안 보인다
4. 문장이 너무 보고서 같아서 creative output으로 보기 어렵다
5. selector보다 manual curation이 더 낫게 느껴진다

---

## 6. J-Beta — 확장 단계 (J-Alpha 성공 시에만)

J-Alpha가 성공했을 때만 간다.

### J-Beta에서 하는 것
- full `STORY_UNIT_TAXONOMY.md`
- 70+ trajectory 라벨링
- selector query API 확장
- cross-seed anchor library 구축
- style profile 확장
- IP mode 확장 (drama/webtoon/game는 아직 후순위)

### J-Beta에서 추가할 것
- get_variations(anchor)
- get_top_arcs(arc_type)
- get_ip_candidates(target="webnovel")
- labels.json / selector_index.json

즉 J-Beta는
**작은 증명이 먹힌 뒤의 일반화**
다.

---

## 7. 기존 Phase J와의 매핑

기존 기획안의 Step을 그대로 폐기하지 않고 재배치한다.

| 기존 | 개선 후 |
|---|---|
| J1 트랙 전환 공식화 | 유지 |
| J2 renderer 진단 | **J-Alpha Step A1로 승격** |
| J3 taxonomy 문서화 | **minimal만 먼저** |
| J4 70+ 라벨링 | **J-Beta로 연기** |
| J5 selector 1차 구현 | **minimal selector만 J-Alpha** |
| J6 renderer 개선 | J-Alpha에서 축소 실행 |
| J7 통합 데모 | **5-variation demo로 축소** |
| J8 Lee 검토 | 유지 |

즉:
- J1 유지
- J2를 앞으로
- J3/J5/J6/J7은 축소
- J4는 뒤로
- J8은 그대로

---

## 8. 지금 당장 Claude Code가 할 일

### Step 1
`docs/CREATIVE_TRACK_TRANSITION.md` 작성  
기존 기획안 요약 + J-Alpha / J-Beta 구조 반영

### Step 2
`docs/creative/RENDERER_DIAGNOSIS_ALPHA.md` 초안 틀 작성  
Lee가 샘플 평가를 바로 적을 수 있게

### Step 3
`docs/specs/STORY_UNIT_TAXONOMY_MINIMAL.md` 작성  
Person / Event / World 3개만

### Step 4
`docs/creative/CURATED_ANCHOR_SET_ALPHA.md` 작성  
Peter 1 anchor + Van Gogh 1 anchor 선정

### Step 5
minimal selector 구현  
anchor 5개 variation 묶기만 우선

### Step 6
renderer 1차 개선  
우선 개선 3개만

### Step 7
5-variation demo 생성  
Peter / Van Gogh 각 1세트

### Step 8
`docs/creative/VARIATION_READING_REVIEW.md` 작성  
성공 / 실패 판정

---

## 9. 지금 하지 말아야 할 것

- 70+ trajectory 전체 라벨링
- selector 점수 체계 과도 정교화
- IP 형태 추가 확장
- drama/game/webtoon 톤 작업
- research 트랙 재개
- paper 통합 작업
- Branch C 추가 slice 실행
- engine touch (authority autonomy 등)
- world/ legacy 재검토

지금은 **creative track의 최소 증명**이 먼저다.

---

## 10. Lee 입력이 필요한 지점

J-Alpha에서 Lee 입력은 2번만 받는다.

### Gate 1 — Renderer 진단
샘플 5개 보고:
- 좋다 / 나쁘다
- 어떤 점이 creative output으로 약한지
판단

### Gate 2 — Variation Demo 판정
Peter / Van Gogh 5-variation demo를 읽고:
- 실제로 변주처럼 보이는가
- IP 자산으로 갈 만한가
판정

기존 계획처럼 J2 + J8 두 번만 입력받되,
J2를 앞으로 당겨서 병목을 앞에서 해결한다. fileciteturn11file0

---

## 11. 최종 한 줄 요약

**Creative IP 트랙 전환 방향은 유지하되,  
Phase J를 그대로 크게 시작하지 말고 J-Alpha에서 먼저  
“같은 anchor의 5개 seed가 실제로 서로 다른 한글 이야기로 읽히는가”를 증명한다.  
그 다음에야 J-Beta에서 taxonomy / selector / labeling을 일반화한다.  
즉 지금 가장 중요한 건 70개를 다루는 것이 아니라,  
Peter와 Van Gogh의 5-variation demo가 정말 읽히는지 먼저 보여주는 것이다.**
