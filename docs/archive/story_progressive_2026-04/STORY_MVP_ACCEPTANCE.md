# Story Output MVP Acceptance Check

**Date**: 2026-04-28
**Phase**: NEXT_STEPS Stage 3 (Step 7-8)
**Source**:
- `STORY_OUTPUT_SPEC.md` §7 acceptance criteria
- `STORY_SET_BASELINE_REVIEW.md` (Phase 6 review)
- `STORY_FAILURE_MODES.md` (failure 분류)
- `STORY_RENDERER_REVISION_1.md` (1차 개선)
**Verdict**: **PASS** (5/6 PASS, 1 MARGINAL)

---

## 1. 6 Acceptance Criteria 평가 (NEXT_STEPS §3)

### Criterion 1: 12개 중 9개 이상에서 이야기 흐름이 보이는가

**PASS** — 12/12. 모든 probe에서 5단 구조 (도입 / 압력 / 반응 / 귀결 / 사후) 명확히 식별 가능.

**근거**: Revision 1 후 모든 probe가 `_opening` → `_initial_tension` + `_pressure_arc` → `_group_response` + cohort_detail → `_turning_point` + `_outcome` → `_aftereffect` 순으로 5단 구조 완성.

### Criterion 2: recovery / saturation / mixed 차이가 글에서 느껴지는가

**PASS** — 분명한 톤 차이 확인.

| outcome | 대표 문장 |
|---|---|
| RECOVERY_DOMINATED | "사람들은 다시 일어섰다. 자리에 따라 빠르고 더딤은 달랐지만, 무거움은 빠져나갔다." |
| SATURATION_DOMINATED | "사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다." |
| MIXED | "한쪽은 회복했고, 다른 쪽은 굳었다. 같은 사건이 사람들에게 다른 모양을 남겼다." |
| PARTIAL | "사람들은 어딘가에서 멈춰 있었다. 회복도 무너짐도 분명하지 않았다." |

P4/P5 (RECOVERY) vs P9/P12 (SATURATION) vs P6/P8/P11 (MIXED) 직접 읽어 봤을 때 분명히 다른 결.

### Criterion 3: crowd / authority / public attention 중 최소 2개가 텍스트에서 보이는가

**PASS** — 4개 축 모두 surface.

| Axis | Text 표현 |
|---|---|
| crowd_blame | "비난은 한 방향으로 모였다" / "사람들의 눈은 노동자들에게로" / blame_band 4단계 |
| authority_vigilance | "권위의 시선은 끝까지 느슨해지지 않았다" / "한참을 머물렀다가 천천히 옅어졌다" (D-2 pattern 분기) |
| public_suspicion | "의심이 거리 위로 짙게 깔렸다" / "성전 바깥에서는 의심이, 안에서는 기도가" |
| top_blame_target | "노동자들에게로" (scarcity) / "거리의 사람들에게로" (accusation) |

### Criterion 4: 출력이 보고서가 아니라 이야기처럼 읽히는가

**PASS** — 보고서 말투 0건 검증.

`audit_report.py`-style scan 결과:
- "trajectory", "probe", "final summary": 0건 (forbidden_phrases SPEC §6)
- "이 시뮬레이션", "데이터에 따르면": 0건
- raw IDs (P6, A1, L1, agent_NN): 0건
- 숫자 (peak X, final Y): 0건

문체는 3인칭 관찰자 시점 + 의미 번역 ("crowd_blame_peak 1.5" → "비난은 한 방향으로 모였다").

### Criterion 5: probe별 차이가 결과물에도 살아 있는가

**PASS (Revision 1 후 강화됨)**.

**시나리오 분기**: scarcity ("곡식이 비어 가는 계절") vs accusation ("공기는 이미 무거웠다") vs sacred ("성전 바깥뜰") — 도입 분명히 다름.

**Outcome 분기**: RECOVERY/SATURATION/MIXED/PARTIAL 4종 다른 톤.

**Top blame target**: scarcity (노동자) / accusation (거리의 사람들) / sacred (제자) 분기.

**Location semantic (D-1)**: P6 vs P9 vs P12 — "곡물 창고", "빈민가", "시장" 다른 자리에서 saturation 묘사.

**Blame band (B-1)**: P3 (weak) vs P9 (weak) vs hypothetical strong → 다른 문장.

### Criterion 6: 템플릿 반복 냄새가 심하지 않은가

**MARGINAL** (이번 cycle의 유일한 약점).

**증상**:
- P4 == P5 (sacred RECOVERY) 100% 동일 텍스트.
- P8 vs P11 (둘 다 MIXED accusation) 거의 동일 (cohort_outcomes도 동일하면 같은 출력).

**원인**: 같은 IR atom 결과 → 같은 templates. annotated probe 자체가 같은 의미적 압축을 만들 때 텍스트 차이를 만들 근거가 없음.

**경감 요인**:
- 시나리오 (3) × outcome (5) × blame_band (4) × authority_pattern (4) × cohort split 패턴 (multi) → 이론상 변주 공간 큼.
- 12 baseline 중 P4=P5 외 다른 동일 페어는 없음 (각자 cohort 수, blame band 등 다름).

**판정**: 같은 IR 입력에 같은 템플릿 출력은 deterministic. 6 기준 중 유일한 marginal. 후속 loop C에서 micro-variation으로 해결 가능 (Phase 3 plan).

---

## 2. MVP 종합 판정

| Criterion | Result |
|---|---|
| C1 — 12/12 이야기 흐름 | PASS |
| C2 — outcome 구분 | PASS |
| C3 — world-side 2+ 축 surface | PASS (4축 모두 surface) |
| C4 — 이야기처럼 읽힘 | PASS (forbidden 0건) |
| C5 — probe별 차이 | PASS (Revision 1 후 강화) |
| C6 — 반복 냄새 | MARGINAL (P4=P5 동일) |

**5/6 PASS + 1 MARGINAL**.

**MVP 통과 기준**: 4개 이상 만족.

→ **VERDICT: PASS**.

---

## 3. PASS 후속 (NEXT_STEPS Stage 4.9)

Stage 4 directive: "PASS 시 `STORY_RENDERER_PHASE2_PLAN.md` 작성 → 다음 단계로".

Phase 2 plan은 NEXT_STEPS §3 Phase 3 (Story Renderer 확장) 기반:
- Step 6: 요약형 / 서사형 분기 고도화
- Step 7: variation 강화 (loop C — P4=P5 같은 동일-IR 케이스 처리)
- Step 8: world-side rendering 강화

`STORY_RENDERER_PHASE2_PLAN.md` 별도 doc.

---

## 4. 보존된 강점 (Phase 2에서 망가뜨리지 말 것)

1. 3단계 분리 (extract / IR / render) 유지 — 디버깅 가능성 핵심
2. Template-guided rendering — LLM 자유 생성 도입 금지 (NEXT_STEPS §5)
3. forbidden phrases 0건 (raw ID, 숫자, 메타) — spec §6 보존
4. 시나리오/outcome 분기 — 현재 패턴 보존
5. 5단 구조 — 도입/압력/반응/귀결/사후 유지

---

## 5. 한계 + 후속 처리

- P4=P5 동일 출력 → loop C variation
- Narrative 길이 일부 미달 (1000자 미만 11/12) → loop A 읽힘 개선
- Trace-level 정보 미사용 (key_events_sample 추출 후 미반영) → loop D event timing rhythm

→ Phase 2 plan에서 우선순위로 다룸.
