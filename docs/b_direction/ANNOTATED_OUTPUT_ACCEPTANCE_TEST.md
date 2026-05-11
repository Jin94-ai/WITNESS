# Annotated Output Acceptance Test — Branch C PREP Task 3

**Date:** 2026-04-28
**Source directive:** `docs/WITNESS_BRANCH_C_PREP_MASTER_PLAN.md` §7 Task 3
**Status:** PREP — acceptance criteria definition (no implementation changes)
**Companion:**
- `WORLD_SIDE_OBSERVABLES.md` (Task 2)
- `ANNOTATED_PROBE_FORMAT.md` §1 + §9 (current spec)

---

## 1. Purpose

Branch C 수직 확장 시 annotated output이 *어떤 조건* 하에 유효한지 acceptance criteria 정의. 즉 "annotated가 Branch C에서도 계속 도구로 작동하려면 무엇을 만족해야 하는가."

NOT a pytest-style automated test list. Acceptance **questions** + **rules**.

---

## 2. Required fields (필수)

annotated probe가 valid Branch C input이 되려면 다음 fields **필수**:

| Field | Section | Why required |
|---|---|---|
| `Final summary: {LABEL}` | §1.2.0 | Q4a arc rollup anchor; eval evaluator 가장 자주 봄 |
| `Primary pressure: {label}` | §1.2.4 (v2) | Q2a scenario typing — pilot 0% → v2.1 100% |
| `Cohort outcomes:` per-location list | §1.2.1 | Q3a relation/group level + cohort divergence visibility |
| `Public suspicion: peak/final` | §1.2.3 (v3) | Q3b `public_attention` axis |
| `Authority vigilance: peak/final` | §1.2.3 (v3) | Q3b `authority` axis (DEAD memory caveat 명시) |
| `Crowd blame total: peak/final` | §1.2.3 | Q3b `interpersonal/group_alignment` proxy |

→ **6 required fields**. validate_annotated_v3.py에서 5개 (header_v3 + final_summary + primary_pressure + crowd_blame + public_suspicion + authority_vigilance) 이미 검증.

## 3. Optional fields (조건부)

| Field | Section | When shown |
|---|---|---|
| `Failure mode: {label}` | §1.2.5 (v2) | Only when `Final summary == SATURATION_DOMINATED` |
| Event log cap disclosure | §1.5 (v1.1) | Only when confessions > 30 |

## 4. v4 candidate fields (NOT in current acceptance)

per `WORLD_SIDE_OBSERVABLES.md` §4:

- `Crowd dominant emotion: {label}` — defer to first execution slice
- `Top blame target: {role}` — defer
- `Shame climate: peak/final` — strongest v4 candidate (long-horizon)
- `Rumor intensity: peak/final` — defer

→ **NOT required**. 추가 시 acceptance test 갱신 필요.

## 5. Acceptance questions (semantic, not just pattern match)

Annotated output이 Branch C 목적에 맞는지 5 질문으로 검증:

### Q1: Final summary가 유지되는가?
- 5 labels (LOW_ACTIVITY / RECOVERY_DOMINATED / SATURATION_DOMINATED / MIXED / PARTIAL) 안에서 분류되는가?
- Cohort arc rollup rule이 unambiguous한가?
- (Edge case: P5/P10 RECOVERY_DOMINATED with partial residue — `ANNOTATED_PROBE_FORMAT.md` §1.2.0 design choice 명시됨)

**Pass**: 12/12 probes 모두 5 labels 중 하나 + rule consistent (verified LOOP 50).

### Q2: Primary pressure가 실제로 scenario typing에 도움 되는가?
- v2.1 detection 100% 달성
- evaluator가 raw event log만 보고 답할 때보다 annotated headline 보고 답할 때 정확도 향상
- pilot에서: original Q2a 1/2 → annotated 1/2 (label 베끼기 방지 후) → v2.1 implementation 후 12/12 ground truth match

**Pass**: 12/12 ground truth match (validate_annotated_v3.py).
**Caveat**: GPT TRUE COMBINED는 Q2a 12/12 correct였으나 *combined view*; strict blind에서는 미측정.

### Q3: Failure mode가 saturation 이해를 돕는가?
- SATURATION_DOMINATED probes (P2, P3, P9, P12)에서 Failure mode가 *왜* saturation이 발생했는지 설명
- evaluator confusion (PILOT_4 "200 confessions + saturation contradiction")을 해결

**Pass**: 4/4 saturated probes 모두 `shame_cap` 표시. PILOT_4 confusion 해결 (FILLED §1.2 "this resolves PILOT_4").

### Q4: Authority / public_attention / crowd_mood가 동시에 surface되어도 과부하가 아닌가?
- v3 추가 후 annotated headline은 ~10 lines (이전 ~7) → 여전히 <12 line scan
- evaluator 답변 시간 변화: pilot 15-20분 → full N=12 70-105분 (probe당 5-9분, 정상 범위)
- Q6a [FORMAT] 태그 빈도: pilot 5 → full 4 (감소, 부담 증가 신호 없음)

**Pass**: 부담 증가 신호 없음.

### Q5: Readability를 해치지 않으면서 world-side observables가 드러나는가?
- Combined readable rate 12/12 = 100%
- Q3b world-side axes positive: 4/5 (interpersonal만 partial)
- Format gap 0 pp (annotated가 original보다 크게 어렵지 않음)

**Pass**: 부담 없이 +world-side 신호 추가.

---

## 6. Acceptance gate for v4 fields (post-Branch C execution)

v4 fields (§4) 추가 시 위 5 질문 모두 **다시 통과**해야 함. 기준:

| Acceptance metric | Threshold |
|---|---|
| Q1 final summary 유지 | 100% (변동 없어야) |
| Q2 primary pressure accuracy | maintain ≥95% |
| Q3 failure mode coverage | ≥90% saturated probes |
| Q4 cognitive load (annotated lines) | ≤15 lines headline |
| Q5 combined readable rate | maintain ≥90% |

→ 위 thresholds 위반 시 v4 field rollback.

---

## 7. Implementation status

- ✓ validate_annotated_v3.py (LOOP 51) — pattern + GT match 자동화
- ⏸ semantic Q1-Q5 acceptance — manual review (Lee + GPT-5.5 결과 검토)
- ⏸ v4 acceptance gate — Branch C execution 시점에 활성화

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Per master plan Task 3; 6 required + 2 optional + 4 v4 candidate fields + 5 semantic acceptance questions. |
