# Branch C — Scope and Criteria

**Date:** 2026-04-28
**Status:** PREP scope locked; EXECUTION gated by separate Lee directive
**Source directive:** `docs/WITNESS_BRANCH_C_PREP_MASTER_PLAN.md`
**Companion docs:**
- `BRANCH_C_PREP_SPEC.md` (initial prep spec, this doc supersedes for scope/criteria)
- `WORLD_SIDE_OBSERVABLES.md` (NEW Task 2)
- `ANNOTATED_OUTPUT_ACCEPTANCE_TEST.md` (NEW Task 3)
- `BRANCH_C_DESIGN_DRAFT.md` (NEW Task 4)

---

## 1. First Branch C use case (locked)

**수직 확장 only** — 4th scenario 추가 안 함.

Concrete: 현재 3 scenarios (accusation / scarcity / sacred) 안에서:

1. **Scenario depth expansion** — world-side observables를 더 분명히 surface
2. **Population variation within current scenarios** — cast composition + location placement variation, cohort split 가시화

→ "Branch C 첫 실행은 *현재 세계를 더 세계답게 만드는 확장*."

## 2. Broader world definition (locked)

**현 프로젝트 문맥에서 broader world**:

> 현재 3 scenarios 안에서, 사람의 내적 변화뿐 아니라 crowd / authority / public attention / blame concentration / memory residue 같은 world-side observables가 **독립적인 축으로** 읽히고 비교될 수 있는 상태.

수평 확장 ("더 많은 이야기") **아님**. 수직 확장 ("더 많은 세계 차원의 관측 가능성").

## 3. Completion criterion (target-based, NOT open-ended)

Branch C PREP 1차 완료는 다음 5 항목이 모두 문서로 고정될 때:

| Criterion | 내용 | 산출물 |
|---|---|---|
| **A** World-side observables 명시 | 7 observables 목록 + source field + 가시화 방식 | `WORLD_SIDE_OBSERVABLES.md` |
| **B** Annotated output acceptance | 필수/optional 필드 + readability 유지 조건 | `ANNOTATED_OUTPUT_ACCEPTANCE_TEST.md` |
| **C** First use case 범위 고정 | 6 후보 중 무엇을 first slice로 | `BRANCH_C_DESIGN_DRAFT.md` |
| **D** 금지선 명시 | 이번 PREP에서 하지 않을 것 | this doc §4 |
| **E** Scope 1 doc | 위를 entry point로 통합 | this doc |

→ E (this doc) 완성 시 Branch C PREP 1차 종료. EXECUTION은 별도 directive.

## 4. Forbidden_now (locked)

이 PREP 단계에서 다음은 **금지**:

| 항목 | 사유 |
|---|---|
| engine code 변경 | ABSOLUTE Rule #6 + master plan §8 |
| `shame_decay` 구현 | KERNEL_GAPS K2 LOCKED |
| `trust → shame` coupling | KERNEL_GAPS sub-gap |
| `belonging` field 추가 | directive §6 forbidden + ahead of evidence |
| `authority autonomy` 구현 | engine 변경 |
| broader world execution | Lee 별도 directive 필요 |
| new scenario 추가 (4th) | master plan §3: 수직 확장 only |
| `world/` legacy refactor | freeze 유지 (§5) |
| Branch C 완료 선언 (autonomous) | Lee가 명시적으로 "execution start" 줄 때까지 |

## 5. world/ legacy 처리 (locked)

**Stay frozen.**

- `world/` (top-level Spike 1A): freeze
- `docs/world/`: freeze
- `data/person/pipeline_v2/`: freeze
- `data/person/abc_snapshots/`: freeze

Branch C PREP는 `engine/world/` (current canonical) 위에서만 작업.

## 6. Immediate next actions (autonomous-allowed)

per master plan §7:

| Task | 산출물 | Status |
|---|---|---|
| 1 | this doc (BRANCH_C_SCOPE_AND_CRITERIA) | ✓ writing |
| 2 | `WORLD_SIDE_OBSERVABLES.md` | LOOP 56 next |
| 3 | `ANNOTATED_OUTPUT_ACCEPTANCE_TEST.md` | LOOP 57 next |
| 4 | `BRANCH_C_DESIGN_DRAFT.md` | LOOP 58 next |

PREP 완료 후 다음 질문 (master plan §10):
- 첫 execution slice 6 candidate 중 어느 것?
- Validation 무엇으로?
- Engine touch 생기는가?

→ 위 3 질문은 별도 Lee directive 필요.

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Per master plan Task 1; supersedes BRANCH_C_PREP_SPEC.md for scope/criteria. |
