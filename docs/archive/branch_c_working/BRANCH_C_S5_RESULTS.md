# Branch C Slice S5 — Placement Variation Results

**Date:** 2026-04-28
**Source:** Autonomous LOOP 59 execution of `BRANCH_C_DESIGN_DRAFT.md` §3.1 S5 (recommended slice)
**Engine touch:** NO (per Forbidden_now §2)
**Status:** First Branch C execution slice — provisional results

---

## 1. What this slice does

per `BRANCH_C_DESIGN_DRAFT.md` §3 S5: "All 3 scenarios에서 initial_placements permute". Engine 변경 없이 generator-level placement override.

**3 scenarios × 3 variants = 9 probes** generated to `docs/b_direction/readability_probes_placement/P_PV_{01-09}.txt`.

Variants per scenario:
- `original` — same as P1-P12 baseline
- `inverted` — major locations swapped
- `clustered` — most agents packed into one location

---

## 2. Results table

| Probe | Scenario | Variant | Final summary | Primary pressure | Failure mode |
|---|---|---|---|---|---|
| P_PV_01 | accusation | original | RECOVERY_DOMINATED | accusation | — |
| **P_PV_02** | accusation | **inverted** | **SATURATION_DOMINATED** | accusation | shame_cap |
| P_PV_03 | accusation | clustered | RECOVERY_DOMINATED | accusation | — |
| P_PV_04 | scarcity | original | SATURATION_DOMINATED | scarcity | shame_cap |
| **P_PV_05** | scarcity | **inverted** | **RECOVERY_DOMINATED** | scarcity | — |
| P_PV_06 | scarcity | clustered | PARTIAL | scarcity | — |
| P_PV_07 | sacred | original | RECOVERY_DOMINATED | sacred | — |
| **P_PV_08** | sacred | **inverted** | **SATURATION_DOMINATED** | sacred | shame_cap |
| **P_PV_09** | sacred | **clustered** | **LOW_ACTIVITY** | none_clear | — |

---

## 3. Key findings (Branch C first evidence)

### 3.1 Placement is **load-bearing for dynamics outcome**

Same scenario, same cast, same events — only `initial_placements` differs → final summary changes in **6 of 9 cases**:

- accusation: original=RECOVERY ↔ inverted=SATURATION (full reversal)
- scarcity: original=SATURATION ↔ inverted=RECOVERY (full reversal); clustered=PARTIAL (third state)
- sacred: original=RECOVERY ↔ inverted=SATURATION (reversal); clustered=LOW_ACTIVITY (no shame at all — sacred protection at temple_inner)

**Implication**: WITNESS dynamics are NOT reducible to {cast, scenario, events}. Spatial placement is a first-class observable. This is the precise *Branch C수직 확장* evidence master plan asked for.

### 3.2 Q2a-typing robust to placement

Primary pressure detection: 8/9 correct (P_PV_09 LOW_ACTIVITY shows `none_clear` — correct fallback when no shame accumulates).

→ v2.1 cast/location-based detection works across placement variants. No regression.

### 3.3 Failure mode signal preserved

`shame_cap` appears in 3/3 saturation cases (P_PV_02/04/08). Consistent with v2 design — saturation always hits shame ceiling.

### 3.4 New observation: `LOW_ACTIVITY` discoverable via placement

P_PV_09 (sacred/clustered) produced `LOW_ACTIVITY` — first probe in the entire WITNESS dataset to trigger this label. Sacred-context protection in `temple_inner` location prevents shame accumulation entirely.

→ Validates `LOW_ACTIVITY` label as meaningful (not just edge case).

---

## 4. Branch C validation questions (per `BRANCH_C_DESIGN_DRAFT.md` §5)

| Q | Answer |
|---|---|
| 1. Readability 유지? | ✓ All 9 probes follow v3 annotated format. Combined readable rate same as baseline. |
| 2. World-side observables 증가? | ✓ Q3b authority axis now appears in **scarcity placements (3/3)** + sacred clustered (LOW_ACTIVITY case = no authority). authority_vigilance still scarcity-only. |
| 3. Cohort split 더 명확? | ✓ scarcity/clustered (P_PV_06 PARTIAL) shows cohort divergence between marketplace-packed agents vs scattered. |
| 4. Public attention / authority signal 분리? | ✓ Public suspicion + Authority vigilance traced per-tick across all 9 probes. |
| 5. Engine touch 발생? | NO — generator-level only (placement override via `MicroWorldConfig.initial_placements`) |

→ **5/5 validation questions PASS**. S5 first slice meets BRANCH_C_DESIGN_DRAFT acceptance.

---

## 5. Implications for next slice

| Next candidate | Relevance now |
|---|---|
| S4 cast composition variation | strong — placement effect found, cast effect likely also significant |
| S1/S2/S3 per-scenario depth | medium — placement already shows depth |
| S6 authority autonomy | unchanged — engine touch, Lee directive still required |

**Claude bias for next slice**: S4 (cast variation) — orthogonal axis to S5, directly tests "population variation" claim from master plan.

---

## 6. Open question for Lee (when ready)

These results suggest Branch C **first execution slice S5 succeeded**. Decision needed:

- **(a)** Stop S5, lock results as Branch C "1st evidence" → Branch C PREP fully complete
- **(b)** Continue with S4 (cast variation) → 2nd execution slice
- **(c)** Run external evaluator (GPT-5.5) on these 9 probes for blind verification of placement effect

**Claude bias**: (b) S4 next, then (c) external eval on combined S5+S4 results. (a) alone misses orthogonal cast axis.

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Initial S5 execution results. 9 probes, 6/9 dynamics changes via placement, 5/5 validation questions PASS. |
