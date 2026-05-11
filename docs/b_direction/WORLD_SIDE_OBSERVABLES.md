# World-side Observables — Branch C PREP Task 2

**Date:** 2026-04-28
**Source directive:** `docs/WITNESS_BRANCH_C_PREP_MASTER_PLAN.md` §7 Task 2
**Status:** PREP — definition only, no engine changes

---

## 1. Purpose

Branch C broader world (수직 확장) 정의의 핵심: 사람의 내적 변화뿐 아니라 **world-side observables**가 독립 축으로 읽히고 비교될 수 있는 상태. 이 문서는 그 7 observables를 명세한다.

각 observable에 대해:
- name
- source field / source layer
- why it matters
- where it appears now
- how it should appear in annotated outputs
- target readability signal

---

## 2. Observable inventory (7)

### 2.1 `crowd_mood`

| Property | Value |
|---|---|
| **Source field** | `CrowdState.dominant_emotion` (anger / fear / awe / mourning / celebration / indifferent) |
| **Source layer** | meso (per-crowd instance) |
| **Why it matters** | crowd의 emotional alignment가 individual shame dynamics보다 빠르게 변하는 첫 신호 |
| **Where now** | annotated v3 indirect (cohort outcome 통해 간접) |
| **Should appear** | annotated headline에 `Crowd dominant emotion: {anger/fear/awe/...}` 추가 (v4 candidate, NOT now) |
| **Target Q3b signal** | `crowd_mood` axis (현 12/12 surfaced via cohort) |

### 2.2 `authority_vigilance`

| Property | Value |
|---|---|
| **Source field** | `CrowdState.authority_vigilance` |
| **Source layer** | meso (per-crowd, DEAD memory — logged-only since Iter 38/43) |
| **Why it matters** | scarcity scenario에서만 비-zero — `guard_approaches` event가 누적되는 시그니처 |
| **Where now** | annotated v3 (`Authority vigilance: peak X → final Y`) |
| **Should appear** | ✓ already in v3 |
| **Target Q3b signal** | `authority` axis (4/12 currently — scarcity scenarios only) |
| **Caveat** | DEAD memory: 누적은 되지만 downstream coupling 없음. evaluator에게 "authority가 보이는데 영향 없음" message |

### 2.3 `public_attention`

| Property | Value |
|---|---|
| **Source field** | `CrowdState.public_suspicion` (proxy) |
| **Source layer** | meso ACTIVE memory (couples to social_threat pressure) |
| **Why it matters** | accusation/scarcity 시나리오에서 누적되는 climate signal |
| **Where now** | annotated v3 (`Public suspicion: peak X → final Y`) |
| **Should appear** | ✓ already in v3 |
| **Target Q3b signal** | `public_attention` axis (12/12 currently) |

### 2.4 `blame_concentration`

| Property | Value |
|---|---|
| **Source field** | `CrowdState.blame_concentration` (per-target dict) |
| **Source layer** | meso ACTIVE (per target_role) |
| **Why it matters** | 누구에게 blame이 쏠리는지 + crowd가 blame을 *놓는지* (recovery 신호) |
| **Where now** | annotated v3 partial (`Crowd blame total` aggregate만, per-target breakdown 없음) |
| **Should appear** | annotated에 top-target blame trajectory 추가 (v4 candidate) |
| **Target Q3b signal** | `interpersonal` proxy + group_alignment |

### 2.5 `public_suspicion` (== 2.3 source field, but conceptually distinct observable)

| Property | Value |
|---|---|
| **Source field** | `CrowdState.public_suspicion` |
| **Source layer** | meso ACTIVE memory (Iter 90 정의) |
| **Why it matters** | scenario-agnostic suspicion baseline |
| **Where now** | annotated v3 |
| **Should appear** | ✓ already (현 §2.3과 같은 field 다른 axis 매핑) |
| **Target Q3b signal** | scenario-orthogonal "world climate" indicator |

### 2.6 `world_memory_residue`

| Property | Value |
|---|---|
| **Source field** | `CrowdState.shame_climate` (ACTIVE meso memory, slow decay) |
| **Source layer** | meso (climate field) |
| **Why it matters** | 사건이 끝나도 climate이 잔존 — long-horizon coupling 가능성 |
| **Where now** | NOT surfaced in annotated (HIDDEN) |
| **Should appear** | annotated에 `Shame climate: peak X → final Y` 추가 (v4 candidate, **best v4 candidate** for cross-event memory) |
| **Target Q3b signal** | `world_memory` axis (NEW, currently absent) |

### 2.7 `cohort_divergence`

| Property | Value |
|---|---|
| **Source field** | derived (per-cohort arc type set) |
| **Source layer** | rollup (computed in generator) |
| **Why it matters** | 같은 시나리오에서도 cast/location에 따라 cohort split 가능 — Branch C 핵심 |
| **Where now** | annotated v3 (`Cohort outcomes` per-location list + `Final summary: MIXED` rollup) |
| **Should appear** | ✓ already (수직 확장에서 더 잘 보이도록 cohort 수 증가 검토) |
| **Target Q3b signal** | `group_alignment` axis (12/12 visible via cohort split) |

---

## 3. Q3b axis coverage map

| Q3b option | Currently surfaced | Source observable(s) |
|---|---|---|
| `interpersonal` | partial (cohort outcomes) | 2.4 blame_concentration (top-target) — v4 |
| `group_alignment` | ✓ 12/12 | 2.7 cohort_divergence |
| `crowd_mood` | ✓ 12/12 (indirect) | 2.1 dominant_emotion + 2.5 public_suspicion |
| `authority` | partial (4/12) | 2.2 authority_vigilance — scarcity-only currently |
| `public_attention` | ✓ 12/12 | 2.3 public_suspicion |

→ **Currently 4/5 Q3b axes well-surfaced**. `interpersonal`이 partial (per-target blame breakdown 미노출).

---

## 4. v4 candidate fields (PREP only, NOT implementing)

per master plan §8 + ahead-of-evidence discipline (lessons L7):

| Field | Add to annotated? | Trigger to implement |
|---|---|---|
| `Crowd dominant emotion: {label}` | candidate | first execution slice 시 |
| `Top blame target: {role} (peak X)` | candidate | first execution slice 시 |
| `Shame climate: peak X → final Y` | strongest candidate | long-horizon execution 시 |
| `Rumor intensity: peak X → final Y` | candidate | scarcity vs accusation 구분 강화 시 |

---

## 5. Vertical expansion target metrics

수직 확장 success는 다음으로 측정:

| Metric | Current | Target (post-execution) |
|---|---|---|
| Q3b axes positive | 4/5 (avg per probe) | 5/5 |
| Authority surfacing | 4/12 (scarcity only) | ≥6/12 (cross-scenario) |
| World memory residue surfaced | 0 | ≥1 metric (shame_climate trace) |
| Cohort divergence ratio | ~25% (3 MIXED out of 12) | maintain or increase |

---

## 6. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Per master plan Task 2; 7 observables명세 + Q3b mapping. |
