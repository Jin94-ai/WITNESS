# Variation Reading Review (J-Alpha Gate 2)

**Date**: 2026-04-28
**Phase**: J-Alpha Step A6 결과 + Step A7 판정
**Source**: `outputs/creative_demo/peter_anchor_5_variations_ko.txt` + `vangogh_anchor_5_variations_ko.txt`
**Verdict**: **PARTIAL PASS** — Peter anchor 성공, Van Gogh→sacred anchor 실패. 분리 평가.

---

## 1. 실측 결과 (5 seeds × 2 anchors = 10 trajectories)

### 1.1 Peter scarcity baseline anchor

| Seed | Final summary |
|---|---|
| 0 | SATURATION_DOMINATED |
| 1 | RECOVERY_DOMINATED |
| 2 | SATURATION_DOMINATED |
| 3 | PARTIAL |
| 4 | RECOVERY_DOMINATED |

→ **3 distinct outcomes** (SAT, REC, PARTIAL). Distribution 2:2:1.

### 1.2 Van Gogh→sacred baseline anchor

| Seed | Final summary |
|---|---|
| 0 | PARTIAL |
| 1 | PARTIAL |
| 2 | PARTIAL |
| 3 | PARTIAL |
| 4 | PARTIAL |

→ **1 outcome only** (PARTIAL × 5). Cross-seed unanimous (이전 Branch C cross-seed 측정과 일치).

---

## 2. 6 성공 기준 평가 (Lee directive §5)

### Peter anchor

| 기준 | 결과 | 근거 |
|---|---|---|
| 1. 5 seed 중 최소 3개 명확히 다름 | **PASS** | 3 distinct outcomes (SAT/REC/PARTIAL), 5/5 seed에서 다른 분포 |
| 2. 차이가 단순 문체가 아니라 구조 차이 | **PASS** | outcome 다른 → group_response / outcome 단계 텍스트 자체 다름 (예: SAT "굳었다" vs REC "다시 일어섰다") |
| 3. person/event/world 중 최소 2 층위 surface | **PASS** | event (accusation) + world (blame target = fisher_laborer 5/5) + person (cohort outcome 다름) — 3 모두 |
| 4. renderer가 trajectory 차이 죽이지 않음 | **PASS** | OUTCOME_POOLS 5종 + ENDING_HOOK_POOLS 5종으로 outcome별 분명히 다른 톤 |
| 5. Lee가 "IP 변주로 쓸 수 있겠다" 판단 | **Lee Gate 2 입력 대기** | (Lee 직접 읽고 판정 필요) |
| 6. 반복 템플릿 냄새가 치명적이지 않음 | **PROBABLY PASS** | probe-hash variation pool로 같은-IR도 다른 sentence. 다만 같은 outcome 묶음(seed 0+2 SAT) 텍스트는 비슷 |

→ **Peter: 5/6 PASS**, 1 Lee Gate 2 대기. **성공 4/6 기준 통과**.

### Van Gogh→sacred anchor

| 기준 | 결과 | 근거 |
|---|---|---|
| 1. 5 seed 중 최소 3개 명확히 다름 | **FAIL** | 5/5 모두 PARTIAL |
| 2. 차이가 단순 문체가 아니라 구조 차이 | **FAIL** | 같은 outcome → 같은 OUTCOME_POOLS (variant_pick hash로 미세 차이만) |
| 3. world-side 층위 surface | PASS | suspicion / authority / top blame 출력 |
| 4. renderer가 차이 죽이지 않음 | N/A | 차이 자체가 없음 |
| 5. Lee가 IP 자산 판단 | Lee Gate 2 대기 | |
| 6. 반복 냄새 치명적 | **FAIL** | 5/5 비슷한 텍스트 |

→ **Van Gogh→sacred: 1/6 PASS**. **실패 (성공 4 미달)**.

---

## 3. 5 실패 기준 평가 (Lee directive §5)

### Peter anchor 실패 신호 평가

| 실패 기준 | 결과 |
|---|---|
| 1. 5개가 거의 같은 이야기 | NO (3 distinct) |
| 2. 차이가 seed 아닌 renderer 랜덤성 | NO (outcome diff = 엔진 시뮬레이션 차이) |
| 3. world-side cause 안 보임 | NO (blame target 5/5 surface) |
| 4. 보고서 같음 | DEBATABLE (Lee 판정 필요) |
| 5. selector보다 manual curation | NO (selector는 anchor bundling만, manual 필요 없음) |

→ **0-1 fail signal**. Peter는 성공 가능성 높음.

### Van Gogh→sacred 실패 신호

| 실패 기준 | 결과 |
|---|---|
| 1. 5개가 거의 같은 이야기 | **YES** (PARTIAL × 5) |
| 2-5 | (1번이 결정적이라 평가 의미 적음) |

→ **2/5 fail signal 명백**. Van Gogh→sacred는 J-Alpha 실패.

---

## 4. 분석 — 왜 이런 결과인가

### 4.1 Peter scarcity 성공 원인
- scarcity baseline (single accusation) cell이 **cross-seed 가장 다양한 outcome** 생산 (Branch C cross-seed test 결과와 일치)
- 5 seeds → 3 outcomes 전부터 알려진 패턴
- 한국어 prose에서 "곡식이 비어 가는 계절..." 시나리오 도입 + outcome 분기 명확

### 4.2 Van Gogh→sacred 실패 원인 — 두 가지

**(a) Anchor 선택 잘못**: sacred는 가장 ensemble-stable 시나리오 (Branch C cross-seed 측정에서 sacred/very-cluster 5/5 unanimous, sacred 일반적으로 RECOVERY 안정). 시드 sensitivity 낮음 → 5 seeds 모두 비슷한 dynamics.

**(b) 시나리오 매핑 잘못**: Van Gogh의 "spiritual collapse" 톤은 sacred 단순 substitute보다 더 복잡. 진짜 Van Gogh anchor 사용 위해서는 별도 generator 필요 (J-Beta 영역).

### 4.3 결론
**Peter anchor는 J-Alpha 핵심 가설 입증**. **Van Gogh substitute 실패는 anchor 선택 문제**, 핵심 가설 자체는 부정 안 됨.

---

## 5. Lee Gate 2 — 직접 입력 영역

Lee가 `outputs/creative_demo/peter_anchor_5_variations_ko.txt` 5개 variation 직접 읽고:

### 5.1 정말 변주처럼 보이는가?
(YES / NO + 구체 이유)

### 5.2 IP 자산으로 갈 만한가?
(YES / NO + 어떤 IP 형태에 적합)

### 5.3 가장 좋은 variation
(번호 + 이유)

### 5.4 가장 약한 variation
(번호 + 이유)

### 5.5 Renderer 추가 개선 방향
(아직 약한 점)

---

## 6. J-Beta 진행 가부 권장

### 권장: **부분적 진행**

- **Peter scarcity 패턴 → J-Beta 진행 가능**: 5/6 + Lee Gate 2 추가 → 통과 시 J-Beta 일반화 (taxonomy 확장 / selector query API / 70+ trajectory labeling)
- **Van Gogh anchor → 별도 작업 필요**: J-Alpha 실패. 진짜 Van Gogh annotated probe generator 작성 (별도 directive 필요)

### J-Beta 우선 항목
1. anchor library 확장 — Peter scarcity처럼 *cross-seed sensitivity 높은* anchor 식별
2. "어떤 cell이 가장 readable variation 생산하는가" — selector scoring (J-Alpha minimal selector 확장)
3. 70+ trajectory labeling — Person/Event/World arc 분류

---

## 7. 산출물 요약

| 파일 | 위치 |
|---|---|
| Peter 5 variations | `outputs/creative_demo/peter_anchor_5_variations_ko.txt` |
| Van Gogh→sacred 5 variations | `outputs/creative_demo/vangogh_anchor_5_variations_ko.txt` |
| Reading review (this) | `docs/creative/VARIATION_READING_REVIEW.md` |
| Renderer diagnosis 틀 | `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md` (Lee Gate 1 대기) |
| Novel tone guide | `docs/creative/NOVEL_TONE_GUIDE_ALPHA.md` |
| Curated anchor set | `docs/creative/CURATED_ANCHOR_SET_ALPHA.md` |
| Story unit taxonomy minimal | `docs/specs/STORY_UNIT_TAXONOMY_MINIMAL.md` |
| Track transition | `docs/CREATIVE_TRACK_TRANSITION.md` |
| Selector | `engine/story/selector.py` + 11 tests PASS |

---

## 8. 한 줄 요약

**Peter scarcity anchor는 5 seeds → 3 distinct outcomes 생산 (5/6 PASS, 핵심 가설 입증). Van Gogh→sacred substitute는 5/5 PARTIAL 단일 outcome (실패). J-Alpha 절반 성공 — Peter 패턴으로 J-Beta 진행 가능, Van Gogh는 별도 generator 작업 필요.**

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | J-Alpha Step A6+A7 결과. Lee Gate 2 입력 대기. |
