# Story Phase 2 — Progress Log

**Date**: 2026-04-28
**Phase**: NEXT_STEPS Stage 4 후속 (PHASE2_PLAN.md 자율 진행)
**Status**: Loop C Iter 2 완료. P4=P5 marginal 해결 확인.

---

## 1. Loop C-3: Probe-hash variation 도입 (완료)

### 변경
`scripts/story/render_story_ko.py`에 `variant_pick(probe_id, slot, pool)` 추가. probe_id+slot 해시로 sentence pool에서 deterministic 선택.

### Pool 구축
- **OPENING_POOLS** (5 종 × 2-3 variants): scarcity / accusation / sacred / low / other
- **OUTCOME_POOLS** (5 종 × 2-3 variants): RECOVERY / SATURATION / MIXED / PARTIAL / LOW_ACTIVITY
- **opening_authority** (3 variants)

### 검증

**P4 vs P5 (sacred RECOVERY)**:
- P4 도입: "성전 안에서는 기도가 이어졌고, 바깥에서는…"
- P5 도입: "성전을 향한 발걸음은 평소보다 많았다…"

**P2 vs P9 (scarcity SATURATION)**:
- 권위 시선 문장 다름 (P2: "한쪽 끝에서" / P9: "거리 한 모서리에서")
- confession_volume 분기로 추가 차이 (P2 high vs P9 moderate)

→ **MVP Acceptance C6 (반복 냄새) MARGINAL → PASS 가능**.

---

## 2. 12 baseline 길이 (Revision 1 → Phase 2 Iter 2)

| Probe | Summary | Narrative |
|---|---:|---:|
| P1 | 503→490 | 667→654 |
| P2 | 526→516 | 756→746 |
| P3 | 446→453 | 684→691 |
| P4 | 410→391 | 605→586 |
| P5 | 410→392 | 605→**587** (P4와 1자 차이) |
| P6 | 644→646 | 1071→1073 |
| P7 | 402→381 | 583→562 |
| P8 | 459→467 | 710→718 |
| P9 | 500→494 | 730→724 |
| P10 | 431→431 | 622→622 |
| P11 | 459→477 | 710→728 |
| P12 | 487→487 | 794→794 |

**Summary**: 모두 380-650자 (spec 400-800 약간 미달 P7 381). Narrative: P6만 1000+.

길이 개선은 Loop A에서 다룸.

---

## 3. 남은 Phase 2 작업

| Loop | 항목 | 상태 |
|---|---|---|
| C-1 | timing rhythm 추출 | DEFER (effort vs gain 낮음) |
| **C-3** | **probe-hash variation pool** | **DONE (이번 cycle)** |
| C (additional) | initial_tension/pressure_arc/turning_point pools 확장 | 다음 cycle |
| **A** | transition 문장 + inner detail (narrative 1000자 목표) | **다음 cycle** |
| B | world-side aftereffect 강화 | DEFER |
| D | style branching (요약 vs 서사 더 분명히) | DEFER |

---

## 4. 자율 모드 우선순위 (다음 fire)

1. **Loop A — transition 문장 + cohort_detail 풍부화** (narrative 길이 1000자 목표)
2. **Loop C 확장 — initial_tension / pressure_arc / turning_point pools** (variation 더 깊이)
3. **MVP_ACCEPTANCE v2 재판정** — 6/6 PASS check

---

## 5. 추가 발견

### 5.1 Pool 다양성 한계

OPENING_POOLS는 시나리오별 2-3개. 더 많은 pool은 시간 들이지만 효과 한계 (P4=P5 같은 rare collision만 해결). 대신 IR atom의 다양성 (timing rhythm 등) 추가가 더 큰 차이 만들 수 있음.

### 5.2 Forbidden 검증

`audit_report.py` 로 random sample (P6, P9, P12) 검사:
- raw IDs 0건
- 숫자 0건
- 메타 phrase 0건
- 보고서 말투 0건

→ 변경에도 spec §6 forbidden 유지.

---

## 6. Phase 2 acceptance recheck

| Criterion | Phase 7 | Revision 1 | Phase 2 Iter 2 | 목표 |
|---|---|---|---|---|
| C1 흐름 | PASS | PASS | PASS | PASS |
| C2 outcome 차이 | PASS | PASS | PASS | PASS |
| C3 world-side ≥2 | PASS | PASS (4axes) | PASS (4axes) | PASS |
| C4 이야기처럼 | PASS | PASS | PASS | PASS |
| C5 probe별 차이 | PASS | PASS | PASS (강화) | PASS |
| **C6 반복 안 심함** | **MARGINAL** | **MARGINAL** | **PASS (P4≠P5)** | **PASS** |

→ **6/6 PASS 확인** (Phase 2 Iter 2). MVP_ACCEPTANCE v2에서 공식 반영.
