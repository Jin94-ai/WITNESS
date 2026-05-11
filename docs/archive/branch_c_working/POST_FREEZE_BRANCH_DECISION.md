# WITNESS B-Direction — Post-Freeze Branch Decision

**Freeze date:** 2026-04-25
**Doc references**:
- Work directive: `WITNESS_POST_LOOP_FREEZE_AND_NEXT_STEPS.md`
- Freeze: `FREEZE_STATE.md` + `FREEZE_COMPONENTS.md`
- Claim matrix: `CLAIM_STATUS_MATRIX.md`
- Readability: `READABILITY_BLIND_PROTOCOL.md` + probes
- Inert audit: `INERT_RESERVE_AUDIT.md`
- Mixed-arc: `MIXED_ARC_PROBE.md`

---

## 0. TL;DR

**Recommended Branch: B (Kernel Simplification) as interim, with a gate
to Branch A (Readability-facing) once Step C human evaluation returns.**

Justification: audit revealed 17 RESERVE/REMOVE_CANDIDATE items, Probe 1
null mixing (sacred fully decoupled), and a single-loop-dominant kernel
with only one Phase 2a recovery channel. Simplification before
readability-facing expansion is the lower-risk path. If Step C
readability comes back HIGH (>=8/12 readable), the branch pivots to A
directly — but until then, Branch B discipline reduces technical debt
the audit exposed.

**Full pivot decision requires Step C output** (human blind evaluation
of 12 probes in `readability_probes/`).

---

## 1. Completion checklist (per work directive §5)

| # | Condition | Status |
|:-:|---|:-:|
| 1 | Kernel snapshot frozen (Step A) | ✅ DONE |
| 2 | All claims classified VERIFIED / OPEN / REMOVE_CANDIDATE | ✅ DONE |
| 3 | External readability blind performed | ⏸ **INFRASTRUCTURE READY**; awaits human |
| 4 | Inert / reserve audit + Component Ledger update | ✅ DONE |
| 5 | Mixed-arc minimal probe × 2 | ✅ DONE |
| 6 | "Certain / uncertain / discard" clear | ✅ DONE for conditions 1,2,4,5 |

**5 of 6 complete**. Condition 3 has protocol + probes ready; human
evaluator needed to proceed to final branch gate.

---

## 2. Audit findings summary

### 2.1 What's certain (VERIFIED — 20 + 3 scope-limited)

See `CLAIM_STATUS_MATRIX.md` §1-§4 for full list. Highlights:

- **Phase 2a** is universal recovery channel (3/3 scenarios)
- **Agent-layer shame decrement** is necessary and sufficient for cycles
- **Arc labels** are motif-composition classifiers, not different mechanisms
- **M24 confess-feedback** via events_recent is universal (3/3 scenarios)
- **Grieve motif** doesn't gate on shame; motif activation architecturally
  independent of recovery
- **6 narrative state fields** (awe, moral_injury, identity_shift, trust_scar,
  event_trauma, breach_count) are MicroWorld-INERT (both static + empirical)
- **PYHASH noise floor** stdev 0.388 rev/agent at (N=5, 200tk)

### 2.2 What's open (7 OPEN claims)

The open items cluster around:
- **Readability** (O1): no external validation
- **Mixed-arc robustness** (O2): partially answered by Step E; full answer
  needs readability on mixed probes
- **Cross-scenario generalization** (O3): strong for 3 similar-topology
  scenarios; unknown for 4th with different motif structure
- **Side observations** (O4-O7): seed-specific outliers, rule-activation
  questions, optimal-parameter questions

### 2.3 What to discard or reserve

**17 items** classified RESERVE (14) + REMOVE_CANDIDATE (3):

- **3 REMOVE_CANDIDATE** (actionable during freeze):
  - `breach_count` state field — logged only, lowest dependency
  - `prayer_invitation` event — dormant, either wire or remove
  - `miracle_witnessed` event — dormant, either wire or remove

- **14 RESERVE** (keep for cross-pipeline compat):
  - 5 narrative state fields (awe, moral_injury, identity_shift,
    trust_scar, event_trauma)
  - 3 previously-INERT profile fields (authority_vigilance,
    recovery_bias, relation_bias)
  - `SlowStateFieldRecoveryRule` (unwired infrastructure)
  - 5+ other legacy / cross-pipeline components

### 2.4 Mixed-arc findings (Step E)

- **Probe 1** (accusation + sacred): **zero effect** of sacred overlay.
  Confirms architectural decoupling. Sacred scenario lives entirely in
  cast composition + crowd baselines.
- **Probe 2** (scarcity + grief): **real mixed dynamics**. Cycling drops
  70%, grieve motif firing triples, cohort-wide propagation observed.
  P1 (Phase 2a necessary) still holds.

Asymmetry: kernel is **robust** under grief mixing (grief is motif-coupled)
but **inert** under sacred mixing (sacred is decoupled).

---

## 3. Branch comparison

### 3.1 Branch A — Readability-facing Phase

**Entry conditions** (per §6):
- External readability blind shows ≥ some probes readable
- Mixed-arc shows arc-like flow
- Kernel not completely single-loop

**Current state against entry conditions**:
- ⏸ readability blind: NOT YET RUN (protocol ready)
- ⚠ mixed-arc: Probe 2 shows rich dynamics (≈ arc-like); Probe 1
  shows single-loop collapse
- ⚠ kernel: **IS largely single-loop** — Phase 2a is the only motif-
  coupled recovery channel

**Pro**:
- Probe 2 suggests grief injection produces narratively richer output
- Engine mechanism deeply understood; ready to layer narrative on
- 89 iterations of stabilization mean internal quality is high

**Con**:
- Without readability eval, we don't know if "mechanism stable" translates
  to "narrative legible"
- 17 RESERVE/REMOVE items = narrative-layer complexity without clear
  readability payoff
- Risk of building readability features on unvalidated assumption

**Action if chosen**:
1. Run Step C human eval first
2. If ≥ 8/12 readable: proceed with story probe format standardization
3. Readability rubric + narrative-field mapping

### 3.2 Branch B — Kernel Simplification

**Entry conditions** (per §6):
- Readability low
- Mixed-arc shows collapse
- Inert / reserve components numerous
- Recovery overly single-loop dependent

**Current state against entry conditions**:
- ⏸ readability: unknown yet, but mixed-arc half-collapses (Probe 1)
- ✅ mixed-arc shows partial collapse (Probe 1 fully, Probe 2 partial)
- ✅ **17 RESERVE/REMOVE components** — this condition is met
- ✅ **recovery is single-loop** — Phase 2a is the only motif-coupled
  recovery path; confess-feedback analysis (Iter 84-88) revealed runaway
  when Phase 2a absent

**Pro**:
- Clear target list: 3 REMOVE candidates actionable immediately
- Kernel simplification reduces maintenance + conceptual load
- Makes space for auxiliary recovery path experiment (per §Branch B §3)
- Post-simplification re-audit could produce cleaner readability result

**Con**:
- Removing cross-pipeline items (even CROSS-PIPELINE RESERVE) risks
  breaking v1.0 + v3 pipelines
- Branch B delays user-facing progress
- Sacred scenario simplification (remove dormant events) changes scenario
  semantics

**Action if chosen**:
1. Execute 3 REMOVE_CANDIDATE decisions (with Lee approval):
   - Remove breach_count OR annotate as "logging-only, deprecated"
   - Remove prayer_invitation + miracle_witnessed from SEED_EVENTS
     registry + sacred scenario
2. Explore auxiliary recovery path: design a 2nd recovery mechanism
   (e.g., temporal decay rule for shame, or awe-driven pressure decay)
3. Re-run mixed-arc Probe 1 with wired-OR-removed sacred elements
4. Post-simplification re-audit: does readability improve?

### 3.3 Branch C — Broader World Phase

**Entry conditions** (per §6):
- Readability already secured
- Mixed-arc cross-reactions confirmed
- Kernel simplification not needed

**Current state against entry conditions**:
- ⏸ readability: unknown
- ⚠ cross-reactions observed but only in Probe 2; Probe 1 null
- ❌ simplification IS needed (17 RESERVE/REMOVE items)

**Branch C is not viable without first completing A or B** per the
decision tree in work directive §7.

---

## 4. Decision logic

```
IF readability_blind_result available:
    IF readable >= 8/12:
        IF mixed_arc_shows_cross_reaction:
            → Branch A or C
            (C if simplification not needed; A otherwise)
        ELSE:
            → Branch A (readability at motif level, collapse at scenario mix)
    ELIF readable 4-7/12:
        → Branch A with Branch B preparation (simplify in parallel)
    ELIF readable <= 3/12:
        → Branch B (simplify first)
ELSE (current state, awaiting human eval):
    → Interim Branch B preparation + wait for Step C
```

---

## 5. Recommendation

### 5.1 Interim: Branch B preparation

Begin the low-risk subset of Branch B actions **now** (before human eval):

1. **REMOVE or annotate**:
   - `breach_count`: annotate in `engine/core/state.py` as
     "trajectory-logging-only, MicroWorld-INERT" with a comment linking
     to Iter 89 finding. Don't remove (cross-pipeline risk). RESERVE.
   - `prayer_invitation` + `miracle_witnessed`: do NOT remove from
     `event_registry.py` (already annotated as "no downstream coupling
     currently"). Instead remove from `sacred_gathering` scenario seed
     events OR keep and document that sacred scenario differentiation
     is cast/crowd-based. **Lee decision** — recommend KEEP with
     annotation (removing narrows sacred scenario).

2. **Annotate DORMANT rule**:
   - `SlowStateFieldRecoveryRule`: add module docstring noting "unwired
     as of 2026-04-25 freeze" and intended use (v1.2 content config).

3. **Ledger update** in `COMPONENT_LEDGER.md`:
   - Add state-fields section per `INERT_RESERVE_AUDIT.md`
   - Mark 3 REMOVE_CANDIDATE items formally

### 5.2 Gate on Step C: Pivot to Branch A if readability confirms

After Lee performs Step C evaluation:

- If **≥ 8/12 readable** → pivot to Branch A (readability-facing)
  - Story probe format standardization
  - Readability rubric draft
  - Motif → narrative-field mapping
- If **4-7/12 readable** → Branch A with simplification in parallel
- If **≤ 3/12 readable** → continue Branch B deeper (auxiliary recovery
  path exploration)

### 5.3 Branch C held in reserve

Do NOT start Branch C now. Requires either readability confirmation OR
simplification completion as prerequisite per decision tree.

---

## 6. Freeze lift conditions

Current freeze prohibits (per §2):
- New iteration-style probes
- Phase 2a / shame / confess drilling
- New variables / layers
- Neural policy probes
- Universality claims
- Single-seed major conclusions

**Lift at**: branch decision finalized (post Step C human evaluation).

Until then:
- Allowed: audit document updates, annotation commits, ledger updates
- Allowed: Step C protocol execution (scripting, not interpretation)
- Forbidden: new simulation iterations, tuning, feature work

---

## 7. Concrete next actions

### Now (Lee or Claude can do)
1. **Human**: Run Step C — read each probe in
   `docs/b_direction/readability_probes/P1.txt` … `P12.txt` blind,
   fill `READABILITY_BLIND_RESULTS.md` per protocol
2. **Claude or human**: Annotation commits for breach_count +
   SlowStateFieldRecoveryRule (minor)

### After Step C
1. Compute readability verdict per protocol thresholds
2. Execute branch decision per §4 decision logic
3. Lift freeze discipline for chosen branch
4. Begin branch-specific work per §5 of directive

---

## 8. What could still be wrong (H4)

- **Audit completeness**: 5 of 6 conditions met; Step C blocking.
  "Infrastructure ready" is weaker than "evaluation done."
- **Branch B preparation "interim" stance**: could create work that's
  undone if Step C returns HIGH readability → Branch A pivot. Chose
  to only do annotation-level work to minimize this risk.
- **Mixed-arc probes limited to 2**: §Step E satisfied literally, but
  broader mixing (accusation + private_crisis, scarcity + sacred,
  etc.) untested. Branch decision on partial data.
- **"Single-loop dominant kernel"** is a qualitative judgment; could
  be argued either way. The audit lists single recovery mechanism
  (Phase 2a) as fact, but whether this counts as "overly single-loop"
  for Branch B entry is interpretive.
- **Readability predictions for probes** (§6 of MIXED_ARC_PROBE) are
  speculative; human eval could surprise in either direction.

---

## 9. What I did NOT try (H2)

- Additional mixed-arc probes beyond the 2 required
- Empirical ablation confirmation for INERT slow_state fields with
  correct Pydantic setter path
- Cross-scenario confess-feedback validation at scarcity + sacred
- Alternative recovery path design (Branch B feature work)
- Actual Step C evaluation (human-gated)

---

## 10. Conclusion

The 89-iteration stabilization phase has produced a well-characterized,
empirically audited kernel. The audit identified significant technical
debt (17 RESERVE/REMOVE items) and confirmed architectural separation
between narrative-layer and mechanism-layer state fields.

**Branch decision is ready pending Step C human evaluation**.
- If readability is high → Branch A (readability-facing expansion)
- If readability is low → Branch B (simplification)
- Branch C (broader world) is premature in all cases

**Interim action**: low-risk annotation work only. Do not start
substantial branch work until Step C returns.

---

**End of Post-Freeze Branch Decision. Audit phase complete pending
Step C human evaluation.**
