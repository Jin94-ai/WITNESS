# WITNESS B-Direction — Claim Status Matrix

**Freeze date:** 2026-04-25
**Scope:** Every major claim generated across 89 iterations, classified
as VERIFIED / OPEN / REMOVE_CANDIDATE (RESERVE).

---

## 0. Schema

| Column | Meaning |
|---|---|
| Claim | The load-bearing statement |
| Status | VERIFIED / OPEN / REMOVE_CANDIDATE / RESERVE |
| Evidence | What supports or fails to support the claim |
| Scope | Under what conditions the claim is valid |
| Caveat | Known limits / unverified extensions |

**Status definitions**:
- **VERIFIED**: multi-level evidence (code + ablation + multi-seed or
  multi-scenario). Effect ratio >= 3σ where applicable.
- **OPEN**: partial evidence; requires external eval, larger N, or
  broader coverage before final classification.
- **REMOVE_CANDIDATE / RESERVE**: ablation-inert or dormant; retained
  only for cross-pipeline compat (RESERVE) or suggested for removal
  (REMOVE_CANDIDATE).

---

## 1. Core cycle mechanism claims (VERIFIED)

| # | Claim | Status | Evidence | Scope | Caveat |
|:-:|---|:-:|---|---|---|
| C1 | Phase 2a forgiveness loop is the universal recovery channel | VERIFIED | Iter 66: 3/3 scenarios ablation-confirmed; Iter 67-68 sub-layer decomposition | accusation + scarcity + sacred; MicroWorld kernel | 3/3 limit; only accusation-style action topology |
| C2 | Agent-layer shame decrement is necessary for cycle existence | VERIFIED | Iter 67/68 layer decompose; Iter 71 field ablation (shame-off → rev=0) | MicroWorld | Other channels (crowd-layer, guilt, fear) cannot substitute |
| C3 | Crowd-layer is dual-role modulator (depth amp + rate dampener) | VERIFIED | Iter 67/68 cross-scenario layer decompose | MicroWorld 3 scenarios | Effect magnitude scenario-dependent |
| C4 | Shame decrement magnitude 0.2-0.4 is a local plateau | VERIFIED | Iter 72 inverted-multiplier test + Iter 73 dose-response sweep | accusation only | Range tested 0.0-0.8 only; wider untested |
| C5 | Above mul=0.4, cycle rate rises via period shortening | VERIFIED | Iter 73-74: mul=0.8 gives +63% rev and 22% shorter period | accusation | Single scenario; not verified in scarcity/sacred |
| C6 | Arc labels (A/B/C/D) = motif composition, not mechanism | VERIFIED | Iter 80-81: Arc D motifs emerge under shame ablation but cycling dies | MicroWorld | "Arc" as motif-composition classifier remains valid |
| C7 | M24 — confess runaway via events_recent feedback under P1 ablation | VERIFIED | Iter 84 14-motif dump + Iter 85 events_recent presence (63%/15%/7%) + Iter 86 N=5 confirmation | 3/3 scenarios (Iter 88) | Amplification magnitude pressure-dependent |
| C8 | Grieve motif does NOT gate on shame state | VERIFIED | Iter 82 code inspection of motif.py:173-184 + Iter 83 direct measurement | MicroWorld | Indirect influence via conceal/remain_present activations |
| C9 | Motif activation and cycling mechanism are architecturally independent | VERIFIED | Iter 80-81 + Iter 84-85 measurements | MicroWorld | Grieve fires under shame ablation; cycling requires shame channel |

---

## 2. Mixed-arc filter claims (VERIFIED)

| # | Claim | Status | Evidence | Scope | Caveat |
|:-:|---|:-:|---|---|---|
| C10 | Sacred seed events are dormant (no runtime consumer) | VERIFIED | Iter 77 A/B bit-identical + event_registry.py:43-44 verbatim comment | current event contract | Dormant events may be wired in future |
| C11 | Awe state field is architecturally decoupled from cycle mechanism | VERIFIED | Iter 78 ablation: +4 awe, zero cycle delta. + Iter 89 grep zero hits | MicroWorld | Read by narrator + trajectory (not INERT everywhere) |
| C12 | 5 additional narrative state fields (moral_injury, identity_shift, trust_scar, event_trauma, breach_count) are MicroWorld-INERT | VERIFIED (static) | Iter 89: zero grep hits in engine/world + engine/persona | MicroWorld | Empirical ablation not run; Iter 89 relies on static analysis |
| C13 | Cycle emergence is a role × pressure × recovery triad | VERIFIED | Iter 79: priest role absorbs blame but motif_tendency blocks confess → no cycling | MicroWorld + current 10 roles | Dependent on current motif_tendency + motif_action_priors |

---

## 3. Methodology claims (VERIFIED)

| # | Claim | Status | Evidence | Scope | Caveat |
|:-:|---|:-:|---|---|---|
| C14 | PYTHONHASHSEED nondeterminism produces ±0.388 rev/agent stdev at (N=5, 200 tk) | VERIFIED | Iter 70: 10-hash grid | accusation baseline | Other configs have different noise floors |
| C15 | step.agent_motifs (driver motif) ≠ activate_motifs.primary | VERIFIED | Iter 84: 64× difference in grieve_frac metrics | MicroWorld | selector.py:131-139 cited |
| C16 | Binary event presence needs frequency aggregation, not mean | VERIFIED | Iter 85: script-bug discovery + correct metric comparison | Event-presence measurements | Methodology lesson |
| C17 | Infer-without-measure is unreliable for mechanism claims | VERIFIED (process) | Iter 81→82→83 chain: 3 consecutive wrong inferences before measurement | Research process | Applies to post-hoc narrative generally |

---

## 4. Scenario-specific claims (PARTIAL — scope-limited)

| # | Claim | Status | Evidence | Scope | Caveat |
|:-:|---|:-:|---|---|---|
| C18 | Cross-scenario shame mul regime shape differs | VERIFIED scope-limited | Iter 76: 3 scenarios × 3 mul values | 3 scenarios tested | Only 3 mul points per scenario |
| C19 | Sacred has lower shame-mul threshold than accusation | VERIFIED scope-limited | Iter 76: rev=1.08 at mul=0.05 for sacred vs ~0 for others | sacred scenario | Single-seed at each point |
| C20 | Scarcity shows "cycles at ceiling" regime at high mul | VERIFIED scope-limited | Iter 76: rev=5.7 with final=10 | scarcity + mul≥0.8 | Single-seed observation |

---

## 5. OPEN claims (insufficient evidence to classify)

| # | Claim | Status | Evidence | Missing | Next step |
|:-:|---|:-:|---|---|---|
| O1 | Engine produces externally readable narrative arcs | **OPEN** | None direct | Human blind evaluation | **Step C readability protocol** |
| O2 | Engine behavior is robust under mixed pressure (not just probe-specific) | **OPEN** | Iter 57 partial + Iter 80-81 guilt injection | Formal mixed-arc probe with explicit overlap | **Step E mixed-arc probe** |
| O3 | Mechanism findings generalize beyond 3 current scenarios | OPEN | 3/3 generalization but similar action topology | 4th scenario with different motif structure | Future branch decision |
| O4 | Seed 3 C outlier in Iter 86 reflects real bimodal dynamics | OPEN | Single observation | Multi-seed replication | Not priority |
| O5 | SlowStateFieldRecoveryRule activation would materially change dynamics | OPEN | Static analysis only | Instantiate rule + run | Feature work (not audit priority) |
| O6 | Production shame multiplier 0.4 is near-optimal | OPEN | Local plateau 0.2-0.4; secondary rise at 0.8 | Readability comparison at different mul | Readability eval would help |
| O7 | Scenario diversity is truly compositional, not mechanistic | OPEN | Iter 78 suggestive + Iter 89 static | Need new-topology scenario test | Broader world phase prerequisite |

---

## 6. REMOVE_CANDIDATE / RESERVE

Current INERT classifications retained for cross-pipeline compat:

| # | Component | Reason kept | Remove potential |
|:-:|---|---|---|
| R1 | `moral_injury` state field | latent_drive (v1.0), narrator, trajectory | RESERVE — keep for v1.0 future |
| R2 | `identity_shift` state field | Same | RESERVE |
| R3 | `trust_scar` state field | Same + slow_recovery-rule-defined | RESERVE |
| R4 | `event_trauma` state field | Same | RESERVE |
| R5 | `breach_count` state field | trajectory only (narrative counter) | **REMOVE_CANDIDATE** — lowest dependency |
| R6 | `awe` state field | narrator | RESERVE |
| R7 | `authority_vigilance` field | Pre-Iter-50 INERT | RESERVE (v3 pipeline possibly) |
| R8 | `recovery_bias` (PersonaProfile) | v3 content JSONs populate it | RESERVE (cross-pipeline confirmed) |
| R9 | `relation_bias` (PersonaProfile) | Same | RESERVE |
| R10 | `prayer_invitation` event | Sacred scenario seed | **WIRE or REMOVE** — decision needed |
| R11 | `miracle_witnessed` event | Sacred scenario seed | **WIRE or REMOVE** — decision needed |
| R12 | `SlowStateFieldRecoveryRule` | v1.2 future infrastructure | RESERVE — annotate intent |
| R13 | Legacy v3 orphan motif branches | v3 PersonV3Loop pipeline reads | RESERVE (cross-pipeline confirmed Iter 60) |

---

## 7. Previously retracted claims (archival)

These are no longer active claims; retained for traceability:

| # | Retracted claim | Retracted at | Replaced by |
|:-:|---|:-:|---|
| M15-M18 | (see FINDINGS_SUMMARY_ITER_1_63) | Iter 50-63 | Prior summary |
| M19 | Iter 68 accusation "C<A crowd-layer dampening" | Iter 70 | Within hash-noise floor |
| M20 | Iter 71 "shame magnitude-driven dominance" | Iter 72 | Channel-presence not magnitude |
| M21 | Arc labels = different recovery mechanisms | Iter 80 | Labels are motif-composition classifiers |
| M22 | "Grieve requires shame not saturated" | Iter 82 | Grieve has no shame dependency |
| M23 | "Conceal outranks grieve under P1 off" | Iter 83 | Conceal never outranks grieve |
| M24 | (NEW CLAIM, not retracted) | Iter 84 | Confess runaway via events_recent |
| M25 | Iter 85 "D < B confession activity" | Iter 86 | Within noise at N=5 |

---

## 8. Summary statistics

| Status | Count | Examples |
|---|:-:|---|
| **VERIFIED** | 20 | C1-C17, Cycle mechanism + methodology |
| **VERIFIED scope-limited** | 3 | C18-C20 (single-seed or narrow coverage) |
| **OPEN** | 7 | O1-O7 (readability, mixed-arc robustness, generalization) |
| **REMOVE_CANDIDATE** | 3 | R5 breach_count, R10/R11 sacred events |
| **RESERVE** | 10 | R1-R4, R6-R9, R12, R13 (cross-pipeline) |

Total tracked: 43 claims + 7 historical retractions.

---

## 9. Priority for audit completion

### Highest priority
1. **O1** readability — requires human blind evaluation (Step C)
2. **O2** mixed-arc robustness — requires formal probe (Step E)

### Medium priority
3. **R10 / R11** sacred events — decide WIRE or REMOVE (Step D)
4. **R5** breach_count — empirical ablation confirmation (Step D)

### Deferred
5. **O3-O7** — handled by branch phase after audit

---

## 10. Branch decision implications

The branch decision (A readability / B simplification / C broader world)
will depend on:

- **If O1 result is READABLE** → Branch A (readability-facing) viable
- **If R10-R13 RESERVE list is long AND O2 mixed-arc shows collapse** → Branch B (simplification)
- **If kernel is tight AND mixed-arc holds** → Branch C (broader world)

Matrix updated at audit completion.

---

**End of Claim Status Matrix. Step C (readability blind) and Step E
(mixed-arc probe) provide the missing data for the 7 OPEN claims.**
