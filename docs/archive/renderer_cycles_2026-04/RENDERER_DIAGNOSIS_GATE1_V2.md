# Renderer Diagnosis — Gate 1 v2 (Lee 직접 평가)

**Date**: 2026-04-28
**Phase**: NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md §4 최우선 1 / §5 Step 1-2
**Source directive**: `docs/WITNESS_NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md`
**Predecessor**: `RENDERER_DIAGNOSIS_ALPHA.md` v1 (자율 fill, Claude bias) — 이 doc은 Lee 직접 평가용 v2.

---

## 0. Lee 기입 방법

각 sample의 narrative 결과를 직접 읽고 (`docs/story/generated/...`):

1. 한 줄 총평 (한 문장만 — 너무 길게 쓰지 말 것)
2. 분류 5종 중 해당 칸에 표시 (X / O / -)
3. 우선 개선 3 체크 (renderer cycle 2에서 작업할 항목)

**중요**: 자율 v1 진단 결과 (Claude bias)는 §5 참고. 그러나 Lee 입력은 **자율 v1과 독립적으로** 진행 — Lee 직관 우선.

---

## 1. 5 Sample (good 2 + 애매 2 + 나쁜 1)

### Sample 1 (good, expected) — P6 MIXED scarcity
**Why this**: 가장 풍부 (1253자). cohort split (빈민가 vs 곡물 창고) + location semantic 분명.
**File**: `docs/story/generated/P6_narrative_ko.txt`

### Sample 2 (good, expected) — Trilogy modal (3-act)
**Why this**: scarcity Trilogy nonmonotonic IP narrative beat. anchor signature lines + 3-act structure.
**File**: `outputs/creative_demo/scarcity_trilogy_modal.txt` (3 acts in 1 file)

### Sample 3 (애매, expected) — P9 SATURATION scarcity
**Why this**: 톤은 정확하지만 "굳었다 / 머물렀다" 표현 반복. 자율 v1에서 "보고서 톤" 약점 식별.
**File**: `docs/story/generated/P9_narrative_ko.txt`

### Sample 4 (애매, expected) — P10 RECOVERY accusation
**Why this**: cross-scenario REC differentiation 후 sacred와 분리됐지만, 여전히 hook 부재 가능.
**File**: `docs/story/generated/P10_narrative_ko.txt`

### Sample 5 (나쁜, expected) — P_PV_09 LOW_ACTIVITY
**Why this**: 가장 짧음 (529자). LOW_ACTIVITY 자체가 dry하지만 narrative depth 부족.
**File**: `docs/story/generated/P_PV_09_narrative_ko.txt`

빠른 실행: `python examples/demo_story.py --highlights` (6 cases 중 5/6 일치).

---

## 2. Lee 평가 표 (직접 기입)

| # | Sample | 한 줄 총평 | good | awkward | flat | report-like | bad |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | P6 MIXED scarcity | | | | | | |
| 2 | Trilogy modal 3-act | | | | | | |
| 3 | P9 SAT scarcity | | | | | | |
| 4 | P10 REC accusation | | | | | | |
| 5 | P_PV_09 LOW_ACTIVITY | | | | | | |

**분류 가이드**:
- **good** = creative output으로 그대로 쓸 만함
- **awkward** = 어딘가 어색 (조사/어미/표현 어색)
- **flat** = 평이함, 기복 없음 (drama tension 부재)
- **report-like** = 보고서 톤 (관찰자 시점이 너무 dry)
- **bad** = creative output으로 무리

---

## 3. Lee 직접 입력 — 우선 개선 3 (renderer cycle 2에서 작업)

5 sample 읽고 *가장 약한 점 3개*만 골라 적기 (priority order):

### 우선 개선 1
- **항목**:
- **현재 문제 예시 (sample # 또는 phrase)**:
- **목표 (어떤 톤으로 가야 하는가)**:

### 우선 개선 2
- **항목**:
- **현재 문제 예시**:
- **목표**:

### 우선 개선 3
- **항목**:
- **현재 문제 예시**:
- **목표**:

---

## 4. Lee 종합 평가

### 4.1 전체 출력 quality 한 줄
(예: "5/5 모두 acceptable" / "3/5 약함, 2개는 좋음" / "전체적으로 보고서 톤")

### 4.2 가장 좋은 sample (Lee 직관)
(번호 + 짧은 이유)

### 4.3 가장 나쁜 sample (Lee 직관)
(번호 + 짧은 이유)

### 4.4 Creative output으로서의 전반적 가치
(예: "novel anchor로 쓸 만함" / "더 다듬어야 함" / "core 톤은 잡혔으나 hook 부족")

### 4.5 다음 단계 권장
- (A) renderer cycle 2 진행 (우선 개선 3 적용)
- (B) style profile 확장 검토
- (C) 더 다듬을 게 아니라 새 quality dimension 추가
- (D) 현재 quality 만족 → J-Beta 다른 작업으로 넘어감

---

## 5. 자율 v1 진단 결과 (Claude bias) — 참고용

이미 작성된 `RENDERER_DIAGNOSIS_ALPHA.md` v1 자율 진단 요약:

| Sample | Claude bias 판정 | 약점 카테고리 |
|---|---|---|
| P9 (SAT) | 애매 | 보고서 톤 + 템플릿 냄새 |
| P4 (REC sacred) | 좋다 | (cross-scenario differentiation 후) |
| P6 (MIXED) | 좋다 | cohort split 풍부 |
| P10 (REC accusation) | 애매 | cross-scenario REC tone collapse |
| P_PV_09 (LOW_ACTIVITY) | 애매 | 짧고 dry, narrative depth 부족 |
| Trilogy modal | 좋다 (한계) | anchor signature 후 강화됐지만 cross-anchor SAT modal 비슷 |

자율 v1이 골라낸 우선 개선 3 (이미 적용됨):
1. ✅ Scarcity opening pool 3→5
2. ✅ Cross-scenario REC differentiation
3. ✅ Anchor signature lines for trilogy

→ Lee Gate 1 v2 결과는 *자율 v1 이후* 추가로 잡힌 약점 식별. 자율이 못 본 것이 핵심.

---

## 6. 다음 단계 (Lee 입력 후)

Lee 입력 채워지면 자동:

1. 우선 개선 3 항목을 → `docs/creative/RENDERER_CYCLE_2_PLAN.md`로 이전
2. 각 항목별 implementation 계획 작성
3. renderer patch 적용
4. 5 sample 재생성 + before/after 비교
5. Lee Gate 1 v3 (개선 효과 확인)

NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md §7 예상 흐름:
- 경우 A (명확함) → renderer cycle 2 진행
- 경우 D (매우 부정적) → renderer core 수정 먼저

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (자율) | 2026-04-28 | `RENDERER_DIAGNOSIS_ALPHA.md` Claude bias fill |
| **v2 (Lee)** | TBD | **이 doc — Lee 직접 입력 대기** |
| v3 (post-cycle 2) | TBD | renderer cycle 2 후 효과 측정 |
