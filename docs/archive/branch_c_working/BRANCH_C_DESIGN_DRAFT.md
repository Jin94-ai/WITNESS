# Branch C Design Draft

**Date:** 2026-04-28
**Source directive:** `docs/WITNESS_BRANCH_C_PREP_MASTER_PLAN.md` §7 Task 4
**Status:** PREP draft — execution requires separate Lee directive
**Companion:**
- `BRANCH_C_SCOPE_AND_CRITERIA.md` (Task 1)
- `WORLD_SIDE_OBSERVABLES.md` (Task 2)
- `ANNOTATED_OUTPUT_ACCEPTANCE_TEST.md` (Task 3)

---

## 1. What this PREP cycle does

| Action | Status |
|---|---|
| Branch C scope + criteria 확정 | ✓ Task 1 |
| World-side observables 7 명세 | ✓ Task 2 |
| Annotated acceptance criteria 6 fields + 5 questions | ✓ Task 3 |
| First execution slice 후보 6 정리 (이 doc) | ✓ Task 4 |
| Validation script `validate_annotated_v3.py` | ✓ LOOP 51 |
| Engine 변경 | ✗ forbidden |
| Implementation | ✗ deferred |

## 2. What this PREP cycle does NOT do

| Action | Reason |
|---|---|
| Engine code modification | ABSOLUTE Rule #6 + master plan §8 |
| New scenario (4th) | master plan §3: 수직 확장 only |
| `world/` legacy refactor | master plan §6 freeze |
| v4 annotated field implementation | ahead of evidence (lessons L7) |
| Engine kernel touch (shame_decay, belonging, authority autonomy) | KERNEL_GAPS LOCKED |
| Branch C 완료 선언 (autonomous) | Lee directive needed |

## 3. First execution slice — 6 candidates

per `BRANCH_C_PREP_SPEC.md` §6.1 + master plan §10:

| # | Slice | What it does | Engine touch? | Validation |
|---|---|---|---|---|
| **S1** | accusation depth expansion | accusation scenario에서 cast composition variation N=15 + per-cohort world-side trace | NO (probe regen only) | Q3b accusation에서 5/5 axes positive 도달? |
| **S2** | scarcity depth expansion | scarcity에서 location placement variation + authority_vigilance 추적 강화 | NO (probe regen only) | Q3b authority axis가 scarcity에서만 강한 시그널 — cross-scenario coverage 정량화 |
| **S3** | sacred depth expansion | sacred에서 awe + miracle frequency variation | NO (probe regen only) | Q3b sacred에서 새 axis 발견 가능? |
| **S4** | cast composition variation (cross-scenario) | 모든 3 scenarios에서 cast size = {6, 8, 10, 12} 비교 | NO (probe regen only) | cohort_divergence가 cast size에 따라 변하는가? |
| **S5** | placement variation (cross-scenario) | 모든 3 scenarios에서 initial_placements permute | NO (probe regen only) | location-based readability 차이? |
| **S6** | authority observability pass | authority_vigilance를 *coupled*로 만드는 minimal kernel change (Iter 38 ablation 반대 방향) | **YES (engine touch)** | authority가 dynamics에 영향 주는지 직접 검증 |

→ **S1-S5는 engine 변경 없음**. **S6만 engine touch** (forbidden_now per §2).

### 3.1 Recommended first slice

**Claude bias**: **S5 (placement variation) → S4 (cast variation) → S1/S2/S3 (per-scenario depth)**.

이유:
- S5: 가장 mechanical (initial_placements 변경만), low risk, immediate Q3b world-side measurement
- S4: cast variation은 builder cast list 변경. medium risk (cast composition은 PROBES_GROUND_TRUTH semantic 변경 가능)
- S1/S2/S3: scenario-specific deepening, after S4/S5 baseline

**S6 (authority autonomy)** = engine kernel change → **별도 Lee directive 필요**.

## 4. Target outputs (per slice S5 example, if approved)

if S5 (placement variation) is selected:

| Output | Form |
|---|---|
| Probe set extension | P1-P12 (current) + P13-P24 (placement variations) |
| Generator script | `generate_placement_variations.py` (NEW, ~50 LOC) |
| Comparison doc | `BRANCH_C_S5_PLACEMENT_RESULTS.md` (NEW post-execution) |
| Validation | `validate_annotated_v3.py` 확장 (P13-P24 포함) |
| Re-eval | optional (Lee 결정) — N=24 hybrid eval |

## 5. Validation questions (per slice)

각 slice 실행 후 다음 질문 답해야 함:

1. **Readability 유지?** (combined readable rate ≥90%)
2. **World-side observables 증가?** (Q3b axes positive 평균 증가)
3. **Cohort split 더 명확?** (cohort_divergence ratio change)
4. **Public attention / authority signal 분리?** (per-scenario surfacing)
5. **Engine touch 발생?** (NO 권장, YES 시 별도 directive)

## 6. PREP 완료 시점

이 doc 작성 = master plan §7 Task 4 완료. Task 1-4 모두 완료 시 Branch C PREP 1차 종료.

**Status**: 4/4 tasks 완료 (LOOP 55-58).

→ **Branch C PREP 1차 완료**. EXECUTION은 다음 Lee directive에서 first slice 선택 후.

## 7. Execution gate conditions

다음 모두 충족 시 execution 시작 가능:

| Condition | Status |
|---|---|
| Lee가 first slice 선택 (S1-S5 중) | ⏸ pending |
| Lee가 engine touch 가부 명시 (S6 거부 / 부분 허용 / 별도 directive) | ⏸ pending |
| Validation questions 5개 답할 plan 존재 | ✓ this doc §5 |
| forbidden_now list 위반 없음 | ✓ this doc §2 |

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Per master plan Task 4; 6 slice candidates + S5 recommended + execution gate 4 conditions. |
