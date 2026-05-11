# WITNESS — 스토리 출력 MVP 다음 작업 지시서

## 0. 문서 목적

이 문서는 현재 WITNESS에서  
**“한글로 이야기가 몇 줄 나오는 것”을 확인한 직후**  
다음으로 무엇을 해야 하는지, 그리고 그 다음 단계까지 어떻게 이어질지를 정리한 실행 지시서다.

핵심 목표는 다음과 같다.

> **한두 개 예시 출력에서 멈추지 않고,  
> baseline 12개 전체를 한국어 스토리로 생성한 뒤  
> 결과물로서 성립하는지 검증하고,  
> renderer를 개선 가능한 상태로 만들 것.**

즉 지금부터의 목표는:
- “스토리가 나온다”가 아니라
- **“스토리 출력 MVP가 성립한다”**로 전환하는 것이다.

---

## 1. 현재 상태

현재까지는 다음을 확인했다.

- annotated probe 기반 3단계 파이프라인이 동작한다
- extraction → Narrative IR → Korean rendering 구조가 성립한다
- P9 같은 개별 예시에서는 한국어 서사 문장이 실제로 생성된다
- 현재 출력은 template-guided 이므로 추적 가능하고 디버깅 가능하다

하지만 아직 아래는 미검증이다.

- 이 출력이 12개 baseline 전체에서도 성립하는가
- recovery / saturation / mixed가 글에서 실제로 구분되는가
- world-side observables가 텍스트에서 충분히 보이는가
- probe마다 차이가 살아 있는가
- 출력이 보고서가 아니라 이야기처럼 읽히는가
- 반복/기계적 템플릿 냄새가 심하지 않은가

따라서 다음 단계는  
**개별 성공 사례 확인 → baseline set 검증**으로 넘어가는 것이다.

---

## 2. 지금 바로 해야 할 일

## Step 1 — 12개 baseline 전체 story 생성
가장 먼저 해야 할 일은 baseline 12개 전체를 한글 story로 뽑는 것이다.

### 목표
- `P1` ~ `P12` 전체에 대해
  - 요약형 story
  - 서사형 story
를 생성한다.

### 산출물
- `docs/story/generated/P1_summary_ko.txt`
- `docs/story/generated/P1_narrative_ko.txt`
- ...
- `docs/story/generated/P12_summary_ko.txt`
- `docs/story/generated/P12_narrative_ko.txt`

### 원칙
- 아직 style branching을 늘리지 않는다
- 기본 2종(요약형 / 서사형)만 생성한다
- 엔진/annotated 내용을 벗어난 창작 금지
- 수치 직역 금지, 의미 번역 유지

---

## Step 2 — Story Set Baseline Review 작성
12개를 뽑은 뒤, 바로 감으로만 보지 말고 review 문서를 작성한다.

### 추천 파일
- `docs/story/STORY_SET_BASELINE_REVIEW.md`

### 최소 포함 항목
각 probe마다 아래를 기록한다.

1. 이야기 흐름이 보이는가
2. primary pressure가 글에서 느껴지는가
3. recovery / saturation / mixed가 맞게 읽히는가
4. crowd / authority / public attention 등 world-side가 보이는가
5. 문체가 보고서처럼 느껴지는가 / 이야기처럼 느껴지는가
6. 다른 probe와 차별성이 있는가
7. 가장 어색한 문장 또는 구간은 어디인가

### 목적
- 잘 된 것보다 **어디서 망하는지**를 찾기 위함
- 다음 수정이 Step 1/2/3 중 어디 문제인지 구분하기 위함

---

## Step 3 — 실패 유형 분류
리뷰를 바탕으로 실패 유형을 분류한다.

### 실패 유형 A — Extraction 문제
예:
- final_summary 잘못 읽음
- event count 잘못 추출
- top blame target 누락

→ `extract_story_features.py` 수정 대상

### 실패 유형 B — Narrative IR 문제
예:
- saturation인데 recovery처럼 묘사됨
- blame이 약한데 strong으로 분류됨
- world_aftereffect가 지나치게 약하거나 과장됨

→ `build_narrative_ir.py` 수정 대상

### 실패 유형 C — Renderer 문제
예:
- 문장이 어색함
- 너무 반복적임
- 문단 연결이 딱딱함
- 한국어 조사가 부자연스러움

→ `render_story_ko.py` 수정 대상

### 실패 유형 D — Surface gap 문제
예:
- world-side observable이 거의 안 느껴짐
- authority / public_attention이 텍스트에서 사라짐
- cohort split이 충분히 서사화되지 않음

→ annotated field 또는 Narrative IR 확장 후보

### 산출물
- `docs/story/STORY_FAILURE_MODES.md`

---

## Step 4 — Renderer 1차 개선
12개 baseline review와 failure mode 분류가 끝나면  
그 다음은 engine 변경이 아니라 **renderer 1회 개선**이다.

### 우선 개선 항목
1. 반복 문장 줄이기
2. saturation / recovery / mixed 구분 문장 강화
3. world-side observable 문장 강화
4. 문단 연결 자연화
5. 숫자 의미 번역 안정화
6. probe 간 문체/전개 차이 조금 더 확보

### 주의
- 새 메커니즘 추가 금지
- 새 scenario 추가 금지
- Branch C execution 금지
- LLM 자유생성 도입 금지

### 산출물
- `render_story_ko.py` v1.1
- `docs/story/STORY_RENDERER_REVISION_1.md`

---

## 3. 이 다음 지시사항 (현재 4단계 이후)

지금 단계가 끝나면 다음은 아래 순서로 간다.

---

## Phase 2 — Story Output MVP 판정

### Step 5 — MVP Acceptance Check
review와 renderer 1차 개선 후, 아래 기준으로 MVP 통과 여부를 본다.

### MVP 통과 기준
다음 중 4개 이상 만족:

1. 12개 중 9개 이상에서 이야기 흐름이 보인다
2. recovery / saturation / mixed 차이가 글에서 느껴진다
3. crowd / authority / public attention 중 최소 2개가 텍스트에서 보인다
4. 출력이 보고서가 아니라 이야기처럼 읽힌다
5. probe별 차이가 결과물에도 살아 있다
6. 템플릿 반복 냄새가 심하지 않다

### 산출물
- `docs/story/STORY_MVP_ACCEPTANCE.md`

### 판정 결과
- PASS → 다음 단계로
- FAIL → renderer 2차 개선으로

---

## Phase 3 — Story Renderer 확장

MVP가 통과하면 그때부터 확장한다.

### Step 6 — 요약형 / 서사형 분기 고도화
현재 2종을 유지하되, 구조를 더 선명하게 한다.

- 요약형: 압축, 빠른 파악
- 서사형: 이야기 감각 강화

### Step 7 — variation 강화
- 같은 템플릿 반복 줄이기
- pressure type별 opening 분기 강화
- outcome type별 ending 분기 강화
- role / target / world-state별 문장 변주 강화

### Step 8 — world-side rendering 강화
이 단계에서 특히 강화할 것:
- crowd mood
- authority vigilance
- public attention
- blame concentration
- public suspicion
- residue 표현

### 산출물
- `docs/story/STORY_RENDERER_PHASE2_PLAN.md`

---

## Phase 4 — Branch C와 연결

스토리 출력 MVP가 안정화되면, 그다음부터 Branch C는 아래 기준으로만 연다.

> **이 변화가 story output quality를 실제로 개선하는가?**

즉 Branch C는 더 이상 추상적 확장이 아니라  
**더 나은 한글 이야기 출력을 위한 세계 확장**으로 본다.

### 이후 Branch C가 건드릴 수 있는 것
- world-side observables가 더 선명히 보이게 하는 surface 개선
- cast composition variation이 story 차이를 더 잘 만들게 하는 설계
- authority / public attention / blame residue를 story에 더 잘 드러내는 지원

### 아직 금지
- shame_decay 구현
- authority autonomy 구현
- new scenario 추가
- world/ legacy 재검토
- broader world execution
- 자유 생성 기반 LLM story writing

---

## 4. Claude Code용 실행 순서

Claude Code는 아래 순서대로 진행한다.

### Stage 1
1. baseline 12개 story 전체 생성
2. `STORY_SET_BASELINE_REVIEW.md` 작성
3. `STORY_FAILURE_MODES.md` 작성

### Stage 2
4. `render_story_ko.py` 1차 개선
5. 개선 후 baseline 일부 재생성
6. `STORY_RENDERER_REVISION_1.md` 작성

### Stage 3
7. `STORY_MVP_ACCEPTANCE.md` 작성
8. PASS/FAIL 판정

### Stage 4
9. PASS 시 `STORY_RENDERER_PHASE2_PLAN.md` 작성
10. FAIL 시 renderer 2차 개선 계획으로 이동

---

## 5. 지금 하지 말아야 할 것

- Branch C execution
- authority autonomy engine touch
- shame_decay 구현
- 새로운 scenario 추가
- world/ legacy 재검토
- 논문/리서치 문서 확장 우선
- 템플릿 개선 전에 style만 늘리기
- LLM 자유 생성으로 우회하기

지금은 **결과물 baseline 검증 + renderer 개선**이 중심이다.

---

## 6. 최종 한 줄 요약

**지금 해야 할 일은 baseline 12개 전체를 한국어 스토리로 생성하고,  
그 결과물이 실제로 이야기로 성립하는지 리뷰한 뒤,  
실패 유형을 분류하고 renderer를 1회 개선하는 것이다.  
그 다음에야 Story Output MVP 통과 여부를 판정하고,  
이후 확장을 Branch C와 연결한다.**
