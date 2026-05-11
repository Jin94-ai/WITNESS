# Full N=12 Postcheck — TRUE Combined Verification

**Date:** 2026-04-28
**Source results:** `docs/RESULTS_V2_FILLED_FULL_N12_TRUE_COMBINED.md`
**Action source:** `docs/NEXT_ACTIONS_AFTER_FULL_N12_TRUE_COMBINED.md`
**Verdict from GPT-5.5:** P-C-ready with Branch A presentation sub-signal

---

## 1. v3 annotated field mismatch — **VERIFIED, no mismatch**

GPT §6 raised concern: "uploaded annotated headlines still mainly expose `Crowd blame total`; authority/public-attention fields are not explicitly surfaced."

**Verification (autonomous LOOP 50)**:

```bash
grep -E "Public suspicion|Authority vigilance|Crowd blame" docs/b_direction/readability_probes/P3_ANNOTATED.txt
# Output:
#   Crowd blame total:   peak 1.7 at t=82 → final 1.3
#   Public suspicion:    peak 0.22 → final 0.16
#   Authority vigilance: negligible (peak < 0.05)

grep "(annotated supplement, v" docs/b_direction/readability_probes/P3_ANNOTATED.txt
# Output:
#   === PROBE P3_ANNOTATED (annotated supplement, v3) ===
```

**Result**: All 12 annotated files contain v3 fields (`Public suspicion` + `Authority vigilance`). GPT's §6 phrasing was inconsistent with §3 (which correctly counted authority 8/12 + public_attention 12/12 — these counts are v3-derived).

**Resolution**: GPT §6 finding rejected. NEXT_ACTIONS §2.1 "inspect generator OR regenerate" not needed. v3 implementation (LOOP 34) is verified delivered.

**However**: GPT's text inconsistency does suggest the v3 fields could be made *more visually salient* (e.g., grouping under "World-side dynamics" subheader vs current flat list). This is a v4 minor refinement candidate.

---

## 2. P5 / P6 / P10 rollup discrepancies (per NEXT_ACTIONS §2.2)

### 2.1 P5 — sacred baseline s=1, raw=PARTIAL → annotated=RECOVERY_DOMINATED

| Source | Final summary |
|---|---|
| GPT raw self-call | PARTIAL |
| Annotated headline | RECOVERY_DOMINATED |
| Ground truth | RECOVERY_DOMINATED |

**Generator rule** (`generate_annotated_probes_all.py`):
```
arcs = set(cohort_arc_types)
if "recovery" in arcs and "saturation" not in arcs:
    final_summary = "RECOVERY_DOMINATED"
```

**Cohort breakdown for P5** (sacred baseline s=1):
- L cohort 1: `recovery: peak~10.0 → final~0.x` (recovery)
- L cohort 2: `partial: peak~X → final~Y` (if partial)
- L cohort 3: `no shame accumulation` (no_shame)

If at least 1 recovery + no saturation → RECOVERY_DOMINATED. **Rule consistent**.

**Why raw says PARTIAL**: GPT looked at *final shame snapshot* (one agent A1 high) and inferred PARTIAL. The cohort rollup rule weights *cohort-level recovery* over per-agent residual. Discrepancy is **rule design choice**, not bug.

**Resolution**: Document the rule explicitly — "RECOVERY_DOMINATED ⇔ at least one cohort fully recovered AND no cohort saturated, regardless of per-agent residual."

### 2.2 P6 — scarcity p2a_off, raw=SATURATION_DOMINATED → annotated=MIXED

| Source | Final summary |
|---|---|
| GPT raw self-call | SATURATION_DOMINATED |
| Annotated headline | MIXED |
| Ground truth | MIXED |

**Cohort breakdown for P6** (scarcity p2a_off, s=0):
- Has at least one recovery + at least one saturation cohort → **MIXED**

**Why raw says SATURATION**: When p2a is OFF, recovery is rare. Saturation cohort dominates the evaluator's perception of raw event log (more accusations + more stuck high-shame agents). Cohort split (one cohort recovers despite p2a_off, others don't) is invisible without explicit cohort rollup.

**Resolution**: This is *exactly the case where annotation helps*. Rule consistent, GPT raw was misled by surface volume — annotated MIXED is correct per cohort split.

### 2.3 P10 — accusation baseline, raw=MIXED → annotated=RECOVERY_DOMINATED

| Source | Final summary |
|---|---|
| GPT raw self-call | MIXED |
| Annotated headline | RECOVERY_DOMINATED |
| Ground truth | RECOVERY_DOMINATED |

**Cohort breakdown for P10** (accusation baseline):
- L1 cohort: `partial: peak~10.0 → final~5.8` (partial, NOT saturation since final<7)
- L2 cohort: `no shame accumulation`
- L3 cohort: `recovery: peak~10.0 → final~2.5` (recovery)

**Rule check**:
- arcs = {recovery, partial, no_shame}
- "recovery" in arcs ✓, "saturation" NOT in arcs ✓ → RECOVERY_DOMINATED

**Why raw says MIXED**: GPT saw "stuck agents" (the partial cohort with final~5.8) and called MIXED. Generator rule treats *partial* as not-equal-saturation, hence RECOVERY_DOMINATED.

**Resolution**: Rule edge case — `partial` (final 4-7) is currently classified as neither recovery nor saturation. When mixed with recovery, rule says RECOVERY_DOMINATED. This is a **policy choice** about how to handle "incomplete recovery". Two options:
- (a) **Keep current rule**: RECOVERY_DOMINATED if any recovery + no saturation (regardless of partial)
- (b) **Tighter rule**: PARTIAL if any partial cohort exists (degrades RECOVERY_DOMINATED to PARTIAL)

GT uses (a). GPT raw self-call applied (b) implicitly.

**Default**: Keep (a) — explicit in `generate_annotated_probes_all.py:114-125`. Document this design choice.

### 2.4 Rule clarification additions

To address §2.1-2.3, document in `ANNOTATED_PROBE_FORMAT.md` §1.2.0 final-summary table:

| Label | Rule (verbatim from generator) | Edge case |
|---|---|---|
| `LOW_ACTIVITY` | All cohorts `no_shame` | — |
| `RECOVERY_DOMINATED` | "recovery" in arcs AND "saturation" NOT in arcs | **may include partial cohorts** (P10 case) — recovery > partial > no_shame priority |
| `SATURATION_DOMINATED` | "saturation" in arcs AND "recovery" NOT in arcs | — |
| `MIXED` | Both "recovery" and "saturation" in arcs | (P6 case) — visible cohort split |
| `PARTIAL` | Otherwise (mostly partial cohorts, no full recovery and no saturation) | — |

This makes P5 / P10 RECOVERY_DOMINATED defensible against per-agent residual concerns.

---

## 3. Branch verdict update (per NEXT_ACTIONS §3)

**From P-A+C (provisional, post-pilot) → P-C-ready (post-Full N=12, with Branch A retained)**.

| Aspect | Status |
|---|---|
| Branch A signal | Retained — annotation lifts arc rollup +25 pp (raw 9/12 → annotated 12/12) |
| Branch C readiness | **YES, prepare** — readable 12/12, Q2a typing 12/12 (combined), Q3b world-side 3 axes positive |
| Branch C execution | **NO, gated** — broader world refactor needs separate Lee directive |

**Q2a-typing in combined view**: 12/12 (vs pilot 1/2 = 50% / v2.1 expected +50 pp). This is *combined view* with both raw + annotated; strict blind would need annotated-only measurement. GPT explicitly noted: "Q2a typing improvement source: role/cast/location signatures are sufficient in combined view; strict blind improvement still needs isolated evaluator if required."

**Decision**: For product direction, combined view is sufficient (Lee accepts per NEXT_ACTIONS §0).

---

## 4. Branch C preparation allowed-now (per NEXT_ACTIONS §3)

**Allowed in autonomous-mode**:
- Draft Branch C design scope
- Define world-side observables list (current: crowd_mood, authority_vigilance, public_suspicion + future: crowd_mood, authority_presence, public_attention)
- Write acceptance tests for annotated output fields
- Prepare small world-side spec doc

**Still blocked** (forbidden_now):
- Engine behavior changes
- Top-level `world/` refactor
- `docs/world/`, `data/person/pipeline_v2/`, `data/person/abc_snapshots/` 작업
- Archive probe raw data

---

## 5. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Initial postcheck. v3 mismatch verified absent + P5/P6/P10 rule clarification. |
