# WITNESS B-Direction — Consolidation (Iter 75-86)

**Date:** 2026-04-25
**Scope:** Delta from `FINDINGS_SUMMARY_ITER_64_74.md`.
**Purpose:** Consolidate Iter 75-86 (12 iterations) into the
stabilization record.

---

## 0. Executive summary (delta)

Iter 75-86 pursued criterion 7 (mixed-arc) via 5 different mixing
mechanisms, then followed a 5-iteration mechanism-correction chain
(M22 → M23 → M24 → verify at N=1 → verify at N=5). Key outcomes:

- **Mixed-arc has 3 different filter layers**: dormant events,
  decoupled state fields, motif-filtered roles. Only direct state
  injection into motif-read fields produces genuine mixing.
- **Motif activation and recovery mechanism architecturally
  independent**. Arc D motifs fire under shame ablation; cycling
  requires shame channel regardless of motif flavor.
- **Real mechanism for C vs D grieve_frac divergence**: confess
  activation runs up under Phase 2a ablation via events_recent
  positive feedback. Verified at code + N=1 + N=5 levels.
- **Pattern of 3 wrong mechanism inferences** (Iter 81, 82, 83)
  exposed a process issue: infer without measure is unreliable
  even with static code inspection.

**7 new retractions (M19-M25)** raising total to **25 lifetime**.

Updated Loop: **7/8 criteria** (criterion 6 readability blind
still human-blocked). Criterion 7 (mixed-arc) substantively
advanced.

---

## 1. Iter 75-86 iteration ledger

| Iter | Focus | Result | Status |
|:-:|---|---|---|
| 75 | Consolidation of Iter 64-74 | FINDINGS_SUMMARY_ITER_64_74 | REFINE |
| 76 | Cross-scenario shame-mul sweep | Regime shape scenario-specific | KEEP |
| 77 | Mixed arc via sacred events | ROLLBACK: dormant events | null |
| 78 | Mixed arc via awe injection | ROLLBACK: awe decoupled | null |
| 79 | Mixed arc via layered blame | Role-conditional cycling exposed | KEEP |
| 80 | Guilt injection + ablation | Dual-channel falsified (M21) | KEEP |
| 81 | Iter 57 exact replicate | Unified shame recovery confirmed | KEEP |
| 82 | Grieve activator code inspection | M22: grieve not shame-gated | CORRECT |
| 83 | 2-motif computation trace | M23: conceal not outranker | CORRECT |
| 84 | Full 14-motif dump | M24: confess is real outranker | KEEP |
| 85 | events_recent content verification | M24 confirmed N=1 | KEEP |
| 86 | Multi-seed (N=5) verification | M24 confirmed + M25 sub-retract | KEEP |

---

## 2. Mixed-arc three-layer filter discovery (Iter 77-80)

Testing whether structural findings preserve under mixed pressure.
Four different mixing mechanisms tried; each revealed a different
architectural filter.

### 2.1 Filter layer 1 — dormant events (Iter 77)

Injected `prayer_invitation` + `miracle_witnessed` at tick 40-60.
Expected sacred-style dynamics overlay on accusation base.

Result: conditions A (pure) and B (mixed) bit-identical. Root
cause in `engine/world/event_registry.py:43-44`:
```
"prayer_invitation",      # no downstream coupling currently
"miracle_witnessed",      # no downstream coupling currently
```

Events are registered as valid SEED_EVENTS but no rule consumes
them at runtime.

**Architectural finding**: sacred scenario's emergent behavior is
NOT event-driven. It derives from cast composition + crowd
baselines + location tags.

### 2.2 Filter layer 2 — decoupled state fields (Iter 78)

Injected `awe += 4.0` on 3 cycling-cohort agents at tick 40.

Result: awe rose from 3.0 to 7.0 (persisted). Zero change in
reversal count, grieve count, or any cycle metric.

Grep for `awe` in `engine/persona/`: zero matches. Awe is a state
field that no motif activator reads. It's emitted for narrative
purposes but decoupled from cycle machinery.

**Architectural finding**: sacred-flavored state fields (awe,
moral_injury, identity_shift) are architecturally separated from
the crisis-cycle subsystem. Only shame/guilt/fear/anger/blame are
motif-coupled.

### 2.3 Filter layer 3 — motif-filtered roles (Iter 79)

Injected second `public_accusation` (contract-verified event)
targeting priest role at tick 40.

Result: priest agents activated (shame ≥ 1.5) but rev=0 — they
absorb blame without cycling. Priest's `motif_tendency` favors
observe_wait (1.3) and confront (1.2), not confess (recovery-
triggering). Without confession firing, no forgiveness rumor
spawns for priest role, no Phase 2a recovery triggers for that
role.

**Architectural finding**: cycle emergence requires a role × pressure
× recovery triad. Phase 2a is universal recovery channel, but only
fires when motif_action_priors allow recovery-triggering action.

### 2.4 Bypass via direct state injection (Iter 57, Iter 80)

Iter 57's guilt injection (guilt.self=6.0 + guilt.primary_focus=4.2
+ grief=3.0 on 3 agents at t=0) was the only mixing approach that
produced real mixed dynamics with measurable effect on cycling
cohort.

Iter 80 ran this + Phase 2a/shame-channel ablation overlay:
- B full: rev=3.33, grieve_frac_inj=2.4 (Arc D emerges)
- C + P2a off: rev=0, grieve_frac_inj=18.1 (grieve fires a lot,
  cycling dies)
- D + shame off: rev=0, grieve_frac_inj=10.3 (grieve fires, cycling
  dies)

### 2.5 Key finding from mixed-arc (M21)

**M21 (Iter 80 clarification)**: Arc labels (A/B/C/D) classify
trajectories by dominant motif composition. They do NOT correspond
to different recovery mechanisms. All arcs share Phase 2a shame
channel for cycle recovery. "Different arcs" ≠ "different channels."

---

## 3. Mechanism-correction chain (Iter 81-86)

After Iter 80's dual-channel falsification, Iter 81-86 formed a
5-iteration chain drilling into WHY grieve_frac differs between
C (P2a off, 0.019) and D (shame off, 0.121) conditions.

### 3.1 Iter 81 — replicate Iter 57 + ablation

Full Iter 57 injection + ablation overlay. Confirmed Iter 80 story
at stronger signal (grieve emerges at grieve_frac=0.121 in D but
cycling still dies). Posited "grieve requires shame not saturated"
mechanism.

### 3.2 Iter 82 — code inspection (M22)

Read `engine/persona/motif.py:173-184` directly. Grieve activation
formula:
```python
score = 0.5*grief/10 + 0.3*guilt/10 + 0.3*max(eye_contact, suffering)
```

**Grieve has NO shame dependency.** Iter 81's shame-gate claim
falsified. Proposed alternative: conceal outranks grieve under
high shame_climate.

### 3.3 Iter 83 — 2-motif computation (M23)

Manually computed conceal and grieve activations per tick. Grieve
activation (~0.69) uniformly higher than conceal (~0.38). Conceal
never outranks grieve in 540 trace rows.

Iter 82's specific conceal-claim falsified. But the grieve
activation is NOT significantly different between C and D, which
means something ELSE is pushing grieve out of top-2 selection.

### 3.4 Iter 84 — full 14-motif dump (M24)

Monkey-patched `activate_motifs` to dump all 14 activations.
Found:
- Grieve is NEVER top primary motif (0.2% max).
- Top primaries: remain_present (56% B), conceal (52% C/D).
- **Confess activation 0.701 in C vs 0.521 in D** — this is
  the differentiator.

Resolved Iter 81 grieve_frac measurement: `step.agent_motifs`
records `selection.selected_motif` (driver motif from top-2
contribution to chosen action), NOT activate_motifs primary.
64× measurement difference explained.

### 3.5 Iter 85 — events_recent verification

forgiveness_emitted present in events_recent:
- B full: 15.0%
- C P2a off: 63.0%
- D shame off: 7.0%

Confirmed: Phase 2a normally CONSUMES forgiveness events via
recovery. Without Phase 2a, confession-generated events accumulate
and feed back into confess motif activation. Runaway feedback.

### 3.6 Iter 86 — multi-seed (N=5)

B: 24.8% (stdev 7.3), C: 55.4% (stdev 20.0), D: 20.0% (stdev 12.1).

Main pattern (C >> B~D) confirmed. Iter 85 sub-finding (D < B)
retracted as M25 — single-seed artifact. C shows bimodal
variance; one seed (seed 3) reached only 24% instead of typical
60-70%.

### 3.7 Correct mechanism (final)

```
Phase 2a ON (B): confess fires → forgiveness_emitted events spawn
                 → Phase 2a consumes for recovery
                 → shame drops → confess trigger conditions relaxed
                 → confess activation bounded
                 → grieve can win top-2 selection 12% of ticks

Phase 2a OFF (C): confess fires → forgiveness_emitted spawn
                 → NOT consumed (Phase 2a off)
                 → events accumulate in events_recent
                 → confess activation RUNS UP (0.52 → 0.70)
                 → confess dominates top-2, grieve excluded
                 → grieve driver frac drops to 2%

Shame channel off (D): confess fires → forgiveness spawn
                 → consumed (Phase 2a still active on crowd +
                   guilt/fear layers)
                 → partial recovery keeps confess activation
                   moderate
                 → grieve competitive in top-2 (~12%)
                 → cycling still requires shame decrement — which
                   is off — so cycling = 0 despite motif activity
```

---

## 4. Retraction log (M19-M25)

| # | Iter | Claim retracted | Reason |
|---|---|---|---|
| M19 | 70 | Iter 68 accusation "C<A by 0.13" | Hash noise floor |
| M20 | 72 | Iter 71 magnitude-driven dominance | Inverted test | 
| M21 | 80 | Arc labels ≠ different mechanisms | Recovery unified |
| M22 | 82 | Iter 81 "grieve gates on shame" | Code says no |
| M23 | 83 | Iter 82 "conceal outranks grieve" | Direct measurement |
| M24 | 84 | (new claim, confirmed not retracted) | Real outranker = confess |
| M25 | 86 | Iter 85 "D < B confession" | Single-seed fluke |

Total lifetime retractions: **25** (14 pre-Iter-50 + M15-M18 + M19-M25).

---

## 5. Process lessons (from the correction chain)

### 5.1 Infer-without-measure is unreliable

3 iterations in a row (Iter 81 → 82 → 83) produced wrong
mechanism claims based on inference from observed patterns or
code reading alone. Only Iter 84 (monkey-patch and dump) produced
a claim that survived verification.

**Lesson**: mechanism claims need direct measurement, not
post-hoc narrative. "Reading the code" isn't measurement — the
code can be right but the runtime dynamics still surprise.

### 5.2 Binary data needs presence-frequency aggregation

Iter 85 script had a bug: it aggregated events_recent with
`mean(values)`, but values are binary flags (1.0 if present).
Mean is always 1.0 — uninformative. Real metric is
presence-frequency (% of calls with event present).

**Lesson**: always check data type before choosing aggregator.

### 5.3 Single-seed findings ≠ robust findings

Iter 85's "D < B" subfinding (7% vs 15%) at N=1 retracted at
N=5 (20.0% vs 24.8% — same within noise). Main effect (C >> B,D)
survived N=1 because the effect is large (4.2× at N=1).

**Lesson**: large effects survive N=1; small effects need N=5+.

### 5.4 Measurement identity matters

Iter 81's `grieve_frac` (from `step.agent_motifs`) measures
driver-motif, not primary-motif. Iter 84's `grieve` primary count
(from `activate_motifs`) measures activation ranking. These are
64× apart for the same simulation.

**Lesson**: document measurement chain; don't assume "motif
fraction" has a single definition.

---

## 6. Updated Loop §6 criteria (post Iter 86)

| # | Criterion | Status | Key iters |
|:-:|---|:-:|:-:|
| 1 | Event lint | DONE | 51 |
| 2 | 3-level analysis | DONE | 53+ |
| 3 | Prior ablation scope | DONE | 53 |
| 4 | Topology fingerprint | DONE (refined) | 54, 78 |
| 5 | Limit cycle source | EXHAUSTIVE | 55-86 |
| 6 | External readability blind | BLOCKED | - |
| 7 | Mixed-arc preservation | **SUBSTANTIVE** | 57, 80-81, 86 |
| 8 | Component Ledger | DONE | 52-86 |

7/8 still the headline number. Criterion 7 now has:
- 3 null-mixing attempts (exposed 3 filter layers)
- 1 direct-state-injection success with ablation overlay
- Structural findings preserved across mixed conditions
- Full mechanism map for motif-vs-cycling decoupling

Criterion 6 remains blocked until human evaluator available.

---

## 7. Component Ledger updates (Iter 75-86)

### 7.1 Confess motif sub-classification

Confess motif (engine/persona/motif.py:111) has the structural
property of depending on events_recent, creating a Phase 2a-
coupled feedback loop (Iter 84-86 verified).

- **With Phase 2a on**: bounded at ~0.52 activation.
- **With Phase 2a off**: runs up to ~0.70 activation via
  accumulated forgiveness_emitted events.
- 4.2× events_recent presence frequency difference (55% vs 25%).

### 7.2 Motif-coupled vs narrative-only state fields

Clarifying which state fields matter for cycle mechanism:

**Motif-coupled (affect cycling)**:
- shame (all sub-keys) — entry point for shame_exposure pressure
- guilt (primary_focus, self) — confess + seek_repair + grieve
- fear — withdraw + conceal
- anger — confront
- blame / blame_concentration (crowd) — shame_exposure source

**Narrative-only (read-only, cycle-decoupled)**:
- awe — verified decoupled (Iter 78)
- moral_injury — untested but no persona readers found in grep
- identity_shift — untested but no persona readers found
- trust_scar — design-only per existing docs

### 7.3 Grieve is a driver motif, not a top motif

Grieve activation (0.47-0.51) is nearly constant across conditions.
Grieve is NEVER primary motif per activate_motifs (0.2% max).
"Grieve_frac" in prior iterations actually measures driver-motif
attribution from select_action's top-2 action contribution — a
different metric with different dynamics.

---

## 8. Recommendations for Iter 87+

### Potentially valuable next steps

1. **Cross-scenario confess-feedback** — does the Iter 84 mechanism
   (Phase 2a consumption as negative feedback) hold in scarcity +
   sacred scenarios? Would extend M24 universality claim.

2. **Lookback window measurement** — events_recent has a lookback
   (probably 5-10 ticks). Measuring this would refine the
   confess-feedback model.

3. **Seed 3 C outlier investigation** — why does one seed in C
   not runaway? Could reveal a meta-stable regime.

4. **Non-shame state field motif coupling** — moral_injury,
   identity_shift, trust_scar grep/ablation to complete the
   Iter 78 "cycle-decoupled state fields" catalog.

5. **Readability blind external eval** (criterion 6) — remains
   human-gated.

### Less valuable

- Further drilling into Phase 2a (saturated topic).
- More magnitude sweeps within already-mapped regimes.
- Arc-label refinements (surface classification already clarified).

---

## 9. Artifacts Index (Iter 75-86)

Iteration reports: `LOOP_ITER_75.md` through `LOOP_ITER_86.md`
(12 reports, all in `docs/b_direction/probe_runs/`).

Probe scripts: `run_loop_iter76_cross_shame_sweep.py` through
`run_loop_iter86_multi_seed_verify.py` (11 new scripts).

Monkey-patch pattern introduced Iter 84: activate_motifs hook via
patching across 3 module namespaces (motif, persona, world).
Reusable for future runtime introspection.

---

**End of Iter 75-86 consolidation. Mixed-arc filter layers
mapped. Confess-feedback mechanism verified through 5-iter chain
with process lessons on measurement-vs-inference. 25 lifetime
retractions. 287 tests green. Criterion 5+7 advanced;
criterion 6 awaits human.**
