# NEXT_ACTIONS_AFTER_FULL_N12_TRUE_COMBINED

**Date:** 2026-04-28  
**Basis:** `RESULTS_V2_FILLED_FULL_N12_TRUE_COMBINED.md` using uploaded originals + annotated supplements.

## 0. Decision summary

| Decision | Status | Rationale |
|---|---|---|
| Treat previous provisional result as superseded | **YES** | TRUE combined file now uses uploaded P1-P12 originals + annotations. |
| Branch C readiness | **YES, prepare** | Combined readability 12/12, scenario typing 12/12, arc labels available 12/12. |
| Branch C execution | **NO, not yet** | Broader world work still requires Lee directive; annotated world-side fields need verification. |
| Need another full readability pass | **NO by default** | Current combined evidence is enough for product direction. Only rerun if strict blind evidence is required. |
| Engine/kernel changes | **NO** | Do not mix readability/format validation with engine behavior changes. |

## 1. Immediate file actions

1. Mark `RESULTS_V2_FILLED_FULL_N12.md` as provisional/superseded.
2. Promote `RESULTS_V2_FILLED_FULL_N12_TRUE_COMBINED.md` as the active full-N12 consolidation.
3. Add this next-actions file beside it in `docs/b_direction/`.
4. Update `LEE_DASHBOARD_2026-04-28.md` with one line: “TRUE combined full N=12 completed; Branch C prep allowed, execution gated.”

## 2. Required verification before canonical lock

### 2.1 Annotated v3 field mismatch

The dashboard/package expected v3 world-side fields such as `public_suspicion` and `authority_vigilance`, but the uploaded annotated files visibly expose only `Crowd blame total` under world-level dynamics.

**Action:** inspect `generate_annotated_probes_all.py` or regenerated annotated outputs. Confirm whether the files are true v3 or an older v1.2/v2-style supplement.

**Decision rule:**

- If generator contains v3 fields but files omit them → regenerate annotated P1-P12.
- If generator does not contain v3 fields → implement output fields before claiming Q3b world-side gap is solved by annotation.

### 2.2 P5/P6/P10 rollup discrepancies

Raw self-call disagreed with annotated label on P5, P6, and P10. These are not failures; they are useful format-signal cases. But they should be checked before final canonical wording.

| Probe | Check | Expected resolution |
|---|---|---|
| P5 | raw final high A1 shame vs annotated RECOVERY_DOMINATED | clarify cohort aggregation / selected snapshot mismatch |
| P6 | raw saturation-heavy view vs annotated MIXED | verify L2/L3 cohort mapping |
| P10 | residual stuck agents vs RECOVERY_DOMINATED | clarify whether recovery-dominated allows partial residue |

## 3. Branch C preparation plan

Proceed only with **preparation**, not broad implementation.

### Allowed now

- Draft Branch C design scope.
- Define world-side observables: `crowd_mood`, `authority_vigilance`, `public_attention/public_suspicion`.
- Write acceptance tests for annotated output fields.
- Prepare a small world-side spec doc.

### Still blocked until Lee directive

- Changing engine behavior.
- Starting top-level `world/` refactor.
- Touching `docs/world/`, `data/person/pipeline_v2/`, or `data/person/abc_snapshots/`.
- Archiving probe raw data.

## 4. Recommended next MD files to create/update

| Priority | File | Action |
|---|---|---|
| P0 | `docs/b_direction/READABILITY_INFRA_SUMMARY.md` | add TRUE combined result and current gate |
| P0 | `docs/b_direction/BRANCH_DECISION_2026-04-28.md` | update verdict: P-C-ready prep, execution gated |
| P1 | `docs/b_direction/ANNOTATED_PROBE_FORMAT.md` | verify/add world-side fields explicitly |
| P1 | `docs/b_direction/FULL_EVAL_N12_POSTCHECK.md` | record P5/P6/P10 discrepancy audit |
| P2 | `docs/LEE_DASHBOARD_2026-04-28.md` | add final status line |

## 5. Go / no-go rule

**Go for Branch C prep** when:

- TRUE combined result is saved.
- Annotated field mismatch is acknowledged.
- Lee agrees that prep does not equal execution.

**No-go for Branch C execution** until:

- Lee gives explicit directive.
- v3 annotated fields are verified or regenerated.
- P5/P6/P10 discrepancy note is resolved or accepted as format-signal evidence.

## 6. Final recommendation

Move forward with **Branch C preparation** and **annotation field verification**. Do not spend more cycles on another readability eval unless strict blind evidence is specifically required.
