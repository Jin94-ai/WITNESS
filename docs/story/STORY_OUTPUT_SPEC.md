# WITNESS — Story Output Spec (MVP)

**Date**: 2026-04-28
**Source directive**: `docs/WITNESS_STORY_OUTPUT_MVP_PLAN.md` (Lee).
**Status**: Phase 1 (spec lock) — implementation phases 2-6 follow.

---

## 1. 목적

WITNESS annotated probe를 입력으로 받아 **사람이 읽을 수 있는 한국어 이야기 텍스트**를 생성하는 story output layer 사양.

엔진/구조 분석을 더 하지 않는다. 현재 출력에서 **읽힘**을 만든다.

---

## 2. 출력 종류 (2종)

### Type 1 — 요약형 (`{probe_id}_summary_ko.txt`)
| 항목 | 값 |
|---|---|
| 길이 | 400~800자 |
| 형식 | 4~6 짧은 문단 또는 연속 문단 |
| 시점 | 3인칭 관찰자 |
| 문체 | 건조한 서사형 (기록체) |
| 목적 | 빠른 흐름 파악, baseline evaluation |

### Type 2 — 서사형 (`{probe_id}_narrative_ko.txt`)
| 항목 | 값 |
|---|---|
| 길이 | 1000~1800자 |
| 형식 | 5단 구조 기반 짧은 서사 (도입/압력 상승/반응 분기/귀결/사후 세계) |
| 시점 | 3인칭 관찰자 |
| 문체 | 감정 서사형 (감정/긴장/회복 흐름 약간 드러냄, 과문장 금지) |
| 목적 | 읽힘 검증, showcase |

---

## 3. 입력 스키마 (annotated probe required fields)

`docs/b_direction/readability_probes/P{n}_ANNOTATED.txt`에서 추출:

### Required
- `probe_id` (header parse)
- `final_summary` ∈ {LOW_ACTIVITY, RECOVERY_DOMINATED, SATURATION_DOMINATED, MIXED, PARTIAL}
- `primary_pressure` ∈ {scarcity, accusation, sacred, shame, fear, grief, none, mixed, none_clear}
- `failure_mode` (optional, only on saturation; e.g. shame_cap, repeat_retrigger)
- `cohort_outcomes`: list of {location, agents_count, arc, peak, final}
- `accusations_count` (e.g. "Accusations: N fired")
- `confessions_count` (Recovery actions)
- `forgiveness_count`
- `crowd_blame_peak`, `crowd_blame_final`
- `public_suspicion_peak`, `public_suspicion_final`
- `authority_vigilance_peak`, `authority_vigilance_final`

### v4 (optional)
- `top_blame_target` (role + peak)

### Recommended
- `roles_present` (Agents 행 parse)
- `locations_present` (Locations 행)
- `key_events_first_30` (Event log section, first 30 lines)

---

## 4. 중간 서사 스키마 (Narrative IR)

`data/story/narrative_ir/{probe_id}.json`:

```json
{
  "probe_id": "P6",
  "title_hint": "string (옵션)",
  "world_opening": "string — 세계 초기 상태/공기/배경 압력",
  "initial_tension": "string — 첫 긴장 (accusation/sacred sign/scarcity pressure)",
  "pressure_arc": "string — 압력 상승 패턴 (crowd/authority/suspicion/blame)",
  "group_response": "string — 인물/집단 반응 (denial/confession/withdraw/split)",
  "turning_point": "string — 회복/포화/혼합을 가르는 지점",
  "outcome": "string — 최종 arc",
  "world_aftereffect": "string — 사후 세계 (suspicion residue/blame persistence/authority)",
  "dominant_mode": "string — recovery_dominated/saturation_dominated/mixed/partial/low_activity",
  "notes": ["array — 추가 메타정보"]
}
```

각 필드는 빈 string 가능 (low_activity 시 turning_point 빌 수 있음).

---

## 5. 한국어 출력 규칙

### 반드시 지킬 것
- 보고서 말투 금지 — "이 trajectory에서는", "이 probe에서", "최종 결과는"
- 표 해설체 금지
- 지나친 수식 금지
- 사건 간 연결 없는 병렬 문장 금지
- 기계적 반복 금지

### 허용
- 3인칭 관찰자 시점
- 의미 번역 (수치 → 의미)
- 압력과 반응의 인과 표현
- 집단/세계 단위 묘사

### 피해야 할 것
- 지나친 문학적 과장
- 근거 없는 심리 추정
- 엔진에 없는 내용 (예: 인물 이름 창작, 새 사건 추가)
- 메타 설명 ("이 이야기는…", "위 사건은…")

### 의미 번역 예시
| 수치 | 번역 (X) | 번역 (O) |
|---|---|---|
| crowd_blame_peak 8.2 | "비난이 8.2 정점 도달" | "비난이 빠르게 한곳으로 모였다" |
| authority_vigilance 0.42 | "권위 감시 0.42" | "권위의 시선은 끝까지 느슨해지지 않았다" |
| confessions 142 | "고백 142회" | "고백은 멈추지 않고 이어졌다" |
| public_suspicion peak 0.87 | "의심 0.87" | "의심이 거리 위로 짙게 깔렸다" |

---

## 6. 금지어 (renderer가 출력하지 말 것)

- "trajectory", "probe", "final summary", "annotated"
- "이 시뮬레이션", "이 결과", "이 사례에서는"
- "데이터에 따르면"
- 숫자 그대로 (peak X, final Y, t=N, agent_id)
- agent_NN, A1/A2 같은 raw ID
- L1/L2 같은 raw location ID — "한 자리", "다른 곳", "거리", "광장" 등으로 의미 번역

---

## 7. Acceptance Criteria

### 통과 (4/6 이상)
1. 12개 중 9개 이상에서 이야기 흐름 식별 가능
2. recovery / saturation / mixed 구분이 글로 느껴짐
3. crowd / authority / public attention 중 최소 2개가 서사 속에서 보임
4. 문서 요약이 아니라 서사처럼 읽힘
5. probe별 차이가 텍스트에서도 드러남
6. 같은 템플릿 반복 냄새가 심하지 않음

### 실패 (2개 이상이면 renderer 재설계)
1. 글이 보고서처럼만 읽힘
2. world-side observable이 거의 안 보임
3. 사건 간 연결이 약함
4. 너무 많은 수치 번역 실패
5. 모든 story가 비슷한 문체/구조로만 나옴
6. saturation과 recovery 차이가 안 느껴짐

---

## 8. 구현 산출물 위치

| Phase | 산출물 | 위치 |
|---|---|---|
| 2 | extract script | `scripts/story/extract_story_features.py` |
| 2 | extracted JSON | `data/story/story_features/{probe_id}.json` |
| 3 | IR builder | `scripts/story/build_narrative_ir.py` |
| 3 | IR JSON | `data/story/narrative_ir/{probe_id}.json` |
| 4 | renderer | `scripts/story/render_story_ko.py` |
| 5 | story 텍스트 | `docs/story/generated/{probe_id}_summary_ko.txt`, `..._narrative_ko.txt` |
| 6 | review doc | `docs/story/STORY_SET_BASELINE_REVIEW.md` |

---

## 9. Forbidden_now (이번 MVP에서 하지 않을 것)

- engine touch (Rule #6)
- 새 scenario 추가
- broader world execution
- neural story generation / LLM 호출
- 길고 복잡한 문체 실험
- 인터랙티브 / 선택지

이 MVP는 **template-guided rendering**. 복잡 생성기는 후속 loop 작업.

---

## 10. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | MVP_PLAN.md 기반 spec lock. Phase 1 완료. |
