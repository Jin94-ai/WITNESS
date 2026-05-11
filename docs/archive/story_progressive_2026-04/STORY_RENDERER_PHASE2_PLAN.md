# Story Renderer Phase 2 Plan

**Date**: 2026-04-28
**Phase**: NEXT_STEPS Stage 4.9 (PASS 후속)
**Source**:
- MVP PASS verdict (`STORY_MVP_ACCEPTANCE.md` 5/6 + 1 MARGINAL)
- NEXT_STEPS §3 Phase 3 (Story Renderer 확장)
**Status**: Plan only. 구현 시점은 별도 directive 또는 자율 진행.

---

## 1. Phase 2 목표

> MVP에서 "성립한다"가 확인됐으니, **probe별 개성과 깊이**를 늘린다.

지금까지 갖춘 것:
- 3단계 파이프라인 (extract / IR / render) 견고
- 5단 구조 (도입/압력/반응/귀결/사후) 안정
- 시나리오 분기 + outcome 분기 + 4 world-side axes surface
- 한국어 조사/복수 자동 처리
- forbidden phrases 0건

부족한 것 (MVP_ACCEPTANCE §5):
- 같은 IR → 같은 출력 (P4=P5)
- Narrative 길이 일부 미달
- key_events_sample 미사용

---

## 2. 우선순위 (3 Loops)

### Loop C — Variation 강화 (HIGHEST priority)

**목표**: 같은 IR 결과여도 다른 텍스트 변주.

**접근**:
1. **Trace-level micro-features 도입**: key_events_sample (추출 후 미사용)에서 timing rhythm 추출 (early-burst / sustained / late-burst). IR atom 추가.
2. **Cohort detail 강화**: cohort agent 수, agent 종류 (`agents=A1=merchant, A2=family, ...`)를 IR에 통과 → renderer에서 cohort 묘사에 변주 가능.
3. **Sentence template pool**: 같은 의미 atom에 대해 2-3개 후보 문장. seed-deterministic 선택 (probe_id hash 기반).
4. **Opening 변주**: scenario별 도입을 2-3개 변주 (현재 1개).

**위치**:
- `extract_story_features.py`: timing rhythm 추출 추가
- `build_narrative_ir.py`: pressure_arc atom에 `event_timing_pattern` 추가
- `render_story_ko.py`: sentence pool + variation selector

**예상 효과**: P4 vs P5 텍스트 차이 발생 (probe_id 다름). 같은 시나리오/outcome 페어 미세 구분 가능.

### Loop A — 읽힘 개선 (MEDIUM)

**목표**: Narrative 길이 spec 목표 (1000-1800자) 도달, 문단 연결 자연화.

**접근**:
1. **Stage 2-3 사이 transition 문장**: 압력 상승 → 반응 분기 transition ("그러나 사람들의 반응은 한 결이 아니었다").
2. **5단 각 stage의 inner detail 추가**: cohort_detail이 짧음 (1-2문장). 2-3개 비유적 묘사 추가.
3. **시간/공간 묘사**: "어느 시각", "거리 끝" 같은 시공간 표지가 균등하게 분포되도록.

**위치**: `render_story_ko.py` 5단 각 함수 + `render_narrative` 결합부.

**예상 효과**: Narrative 평균 700자 → 1000자대.

### Loop B — World-side rendering 강화 (LOW)

**목표**: world-side observable이 지금보다 더 분명히 surface.

**접근**:
1. **public_suspicion peak 강도 분기**: 현재 `suspicion_strong: bool`만. peak 값 4단계 → 다른 문장.
2. **blame_residue + suspicion_residue 결합 묘사**: 둘 다 strong 시 별도 문장.
3. **shame_residue_ratio 활용** (B-3 도입했지만 아직 미사용): saturation cohort 비율 → "거의 모든 자리가" / "한두 자리만"

**위치**: `build_world_aftereffect` + `_aftereffect` renderer.

**예상 효과**: Aftereffect 단락 더 풍부.

### Loop D — Style branching (DEFER)

NEXT_STEPS §3 Step 6 (요약형/서사형 분기 고도화)는 MVP가 통과한 만큼 신규 기능. 우선 Loop C/A/B 후 검토.

---

## 3. 구현 순서 권장

| Iter | 작업 | 산출물 |
|---|---|---|
| Iter 1 | Loop C-1: timing rhythm 추출 + IR atom | extract + IR 패치 |
| Iter 2 | Loop C-3: sentence pool + probe-hash variation | renderer 패치 |
| Iter 3 | 12 baseline 재생성 + variation 검증 (P4 vs P5 차이 확인) | 새 generated/ 출력 |
| Iter 4 | Loop A: transition + inner detail | renderer 패치 |
| Iter 5 | 12 재생성 + length spec 100% 도달 검증 | output |
| Iter 6 | Loop B: aftereffect 강화 | IR + renderer |
| Iter 7 | 12 재생성 + acceptance re-check (이번엔 6/6 목표) | `STORY_MVP_ACCEPTANCE_v2.md` |
| Iter 8 | (선택) 새 baseline probe 셋 (S2/S3/S4/S5 archive에서) 활용 | 새 set generation |

---

## 4. 엄격 금지 (NEXT_STEPS §5 + §3 Phase 4)

- engine touch (Rule #6)
- LLM 자유 생성
- 새 scenario 추가
- shame_decay / authority autonomy 구현
- world/ legacy 재검토
- broader world execution

Branch C는 "**story output quality를 실제로 개선하는가**" 기준으로만 열림 (NEXT_STEPS §3 Phase 4).

---

## 5. Phase 2 acceptance 기준 (Phase 2 후 재판정)

목표: **6/6 PASS** (현재 5/6 + 1 MARGINAL).

| Criterion | 현재 | Phase 2 목표 |
|---|---|---|
| C1 | PASS | 유지 |
| C2 | PASS | 유지 |
| C3 | PASS | 강화 (4 axes 모두 더 분명히) |
| C4 | PASS | 유지 |
| C5 | PASS | 강화 (per-probe 차이 더 깊게) |
| C6 | MARGINAL | **PASS 목표 — Loop C variation으로 해결** |

---

## 6. Branch C와의 연결 (Phase 4 — far future)

NEXT_STEPS §3 Phase 4: Phase 2 안정화 후 Branch C가 다시 열린다면 **story output quality 개선 기준**으로만.

가능한 Branch C 재오픈 조건:
- annotated probe field 부족 발견 시 (예: D-3 event timing이 unrendered → annotated v5에 timing rhythm field 추가 검토)
- cast composition variation이 story 차이를 더 잘 만들도록 generator 수정 가치 발견 시

이는 Phase 2 끝난 후 별도 directive가 필요한 영역.

---

## 7. 한 줄 요약

**Phase 2의 목표는 "성립한다 (5/6)" → "다 만족한다 (6/6)" 전환. 핵심은 Loop C variation — 같은 IR이어도 다른 텍스트가 나오게.**
