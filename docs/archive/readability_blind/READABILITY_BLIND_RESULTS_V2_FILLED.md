# WITNESS Readability Blind Results V2 — FILLED

**Status:** FILLED — pilot blind-style evaluation  
**Protocol:** `READABILITY_BLIND_PROTOCOL_V2.md`  
**Q-set:** v2

---

## 0. Mode used

- [x] Pilot (N=4)
- [ ] Full (N=12, all original)
- [ ] Full (N=12, all annotated)
- [ ] Hybrid (N=12, 6 original + 6 annotated)

**Evaluator:** ChatGPT / GPT-5.5 Thinking  
**Date:** 2026-04-28  
**Total time spent:** ~20 minutes

---

## 1. Pilot results (N=4)

### 1.1 Per-probe table

| Probe | Format | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PILOT_1 | original | CLEAR_FLOW | PARTIAL_EXPLAIN | accusation | fear | MIXED_BUT_READABLE | COHORT_SHIFT | group_alignment; crowd_mood | MIXED | STRONG | WEAK_RHYTHM | HELPS | Readable |
| PILOT_2 | original | CLEAR_FLOW | PARTIAL_EXPLAIN | accusation | grief | MIXED_BUT_READABLE | COHORT_SHIFT | group_alignment; crowd_mood | ESCALATION | STRONG | WEAK_RHYTHM | NEUTRAL | Readable |
| PILOT_3 | annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | sacred | CLEAR | COHORT_SHIFT | group_alignment; crowd_mood | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| PILOT_4 | annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | fear | CLEAR | COHORT_SHIFT | group_alignment; crowd_mood | ESCALATION | STRONG | WEAK_RHYTHM | NEUTRAL | Readable |

---

### 1.1.5 Final summary self-call

| Probe | Format | Your final summary | Annotated label | Match? |
|---|---|---|---|---|
| PILOT_1 | original | MIXED | (not shown — original) | n/a; vs GT = no |
| PILOT_2 | original | SATURATION_DOMINATED | (not shown — original) | n/a; vs GT = yes |
| PILOT_3 | annotated | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| PILOT_4 | annotated | SATURATION_DOMINATED | SATURATION_DOMINATED | yes |

Note: for PILOT_3/4, self-call was made from cohort outcomes and event pattern before using the explicit `Final summary` line as the answer key.

---

### 1.2 Q6a — confusion notes, structured + free

#### PILOT_1 (original)
- [FORMAT:DENSITY] The event stream is readable only after jumping to state snapshots; the raw denial/confession sequence is too dense to infer arc confidently.
- [STRUCTURE:RECOVERY] Recovery vs saturation is ambiguous: some agents visibly recover while A4/A10 remain high at final state, so the cohort-level rollup is not obvious.
- [SCOPE:TRAJECTORY] Per-cohort trajectory is missing; final shame states are available, but cohort rollup must be inferred manually.

#### PILOT_2 (original)
- [FORMAT:DENSITY] Many repeated denials/confessions/grief events obscure the main scenario pressure.
- [STRUCTURE:MECHANISM] The visible log reads like accusation/shame, while the actual scarcity mechanism is not surfaced in event labels.
- [SCOPE:TRAJECTORY] The late return to high shame is visible in snapshots, but the cause of relapse/saturation is underexplained.

#### PILOT_3 (annotated)
- [FORMAT:HEADLINE] The headline makes arc rollup easy, but scenario typing still leans toward visible accusation rather than sacred pressure.
- [SCOPE:HIDDEN_DATA] Only first 30 of 35 confessions are shown; acceptable here, but the cap should remain explicit.

#### PILOT_4 (annotated)
- [FORMAT:CAP] “First 30 of 200 confessions” is useful disclosure, but it means the event log cannot independently verify saturation dynamics.
- [STRUCTURE:RECOVERY] 200 confessions plus 124 forgiveness rumors still yielding saturation is conceptually important, but the causal reason for failed recovery is not visible.

---

### 1.3 Q6b — design feedback

- **PILOT_1:** Add a compact cohort rollup table even for original format: peak shame, final shame, recovered/stuck count per location/cohort. Raw logs alone create false MIXED reading.
- **PILOT_2:** Surface scarcity pressure explicitly somewhere in the log or header. Without it, Q2a is almost forced into accusation because the only clear pressure event is `public_accusation`.
- **PILOT_3:** Annotated format works for arc readability. To avoid scenario-typing failure, add a pressure-source field that distinguishes sacred/fear/scarcity/accusation from event trigger labels.
- **PILOT_4:** Add a “why recovery failed” field: e.g., shame cap, repeated re-trigger, lack of forgiveness uptake, crowd blame persistence. Otherwise 200 confessions + saturation feels contradictory.

---

### 1.4 Pilot aggregates

#### Format-axis

- **Readable rate (original):** 2 / 2 = 100%
- **Readable rate (annotated):** 2 / 2 = 100%
- **Format gap:** 0 percentage points
- **CAN_EXPLAIN gap:** +100 percentage points  
  - original: 0 / 2 CAN_EXPLAIN
  - annotated: 2 / 2 CAN_EXPLAIN
- **Q5b HELPS rate gap:** 0 percentage points  
  - original: 1 / 2 HELPS
  - annotated: 1 / 2 HELPS

#### Q6a tag distribution

Counting each listed Q6a bullet once by main tag:

- **[FORMAT] count:** 5
- **[STRUCTURE] count:** 3
- **[Q_SET] count:** 0
- **[SCOPE] count:** 3
- **[OTHER] count:** 0

Interpretation: main issue is still presentation/format, but there is a real structure/scope problem around pressure source and recovery failure mechanism.

#### Final summary self-call

Ground truth mapping:

- PILOT_1 = P10 = accusation baseline = RECOVERY_DOMINATED
- PILOT_2 = P9 = scarcity baseline s=0 = SATURATION_DOMINATED
- PILOT_3 = P4 = sacred baseline s=0 = RECOVERY_DOMINATED
- PILOT_4 = P3 = accusation p2a_off = SATURATION_DOMINATED

Results:

- **Original self-call accuracy:** 1 / 2
  - PILOT_1: self-call MIXED vs GT RECOVERY_DOMINATED = wrong
  - PILOT_2: self-call SATURATION_DOMINATED vs GT SATURATION_DOMINATED = correct
- **Annotated match rate:** 2 / 2
  - PILOT_3: RECOVERY_DOMINATED = match
  - PILOT_4: SATURATION_DOMINATED = match
- **Comparison:** annotated match > original self-call. Annotation helps Q4a-style arc rollup.

#### Format-axis metrics v2.2

- **Q4a-rollup gap:** 2/2 - 1/2 = **+50 percentage points**
  - Reading: annotation helps arc rollup, especially by preventing PILOT_1-style MIXED misread.
- **Q2a primary pressure accuracy:**
  - Original: 1 / 2
    - PILOT_1 accusation = correct
    - PILOT_2 accusation vs scarcity = wrong
  - Annotated: 1 / 2
    - PILOT_3 accusation vs sacred = wrong
    - PILOT_4 accusation = correct
- **Q2a-typing gap:** 1/2 - 1/2 = **0 percentage points**
  - Reading: annotation helps arc rollup, not scenario-type detection.

#### Format-axis metric v2.3 — Q3b world-side gap

Selected world-side options counted from `{crowd_mood, authority, public_attention}`.

- **Annotated count:** 2
  - PILOT_3: crowd_mood
  - PILOT_4: crowd_mood
- **Original count:** 2
  - PILOT_1: crowd_mood
  - PILOT_2: crowd_mood
- **Gap:** 0

Per-axis breakdown:

- **crowd_mood gap:** 2/2 - 2/2 = 0
- **authority gap:** 0/2 - 0/2 = 0
- **public_attention gap:** 0/2 - 0/2 = 0

Branch C readiness from this metric alone: weak. Crowd mood is visible, but authority/public_attention are not meaningfully surfaced.

---

### 1.5 Pilot branch decision

| Pattern | Match? |
|---|---|
| Annotated 2/2 + original ≤1/2 → Branch A | no |
| Both 2/2 → Branch C ready | yes, but only weakly |
| Both ≤1/2 → Branch B priority | no |
| Mixed → run full eval | yes, because Q4 rollup improves while Q2 typing does not |

**Pilot verdict:** **A+C / inconclusive — run full**

More precise read:

- **Branch A signal:** strong for explainability and arc rollup. Annotated format made the result immediately explainable.
- **Branch C signal:** both formats are technically readable, but world-side detection is mostly limited to `crowd_mood`; authority/public_attention are not surfaced enough.
- **Branch B signal:** not dominant, but there is a structure/scope issue around hidden pressure source and failed recovery causality.

Recommended next step: run full N=12, preferably hybrid or all annotated plus pressure-source field, because pilot says readability is not the main blocker anymore; scenario typing and world-side mechanism visibility are.

---

### 1.6 Pilot time tracking

| Phase | Target | Actual |
|---|---:|---:|
| Reading | 12-16 min | ~15 min |
| Writing answers | 3-4 min | ~5 min |
| Total | 15-20 min | ~20 min |

---

## 4.1 Ground truth comparison — self-check

| Pilot | Actual scenario | Final summary GT | Q2a self-call | Q2a correct? | Final summary self-call | Final summary correct? |
|---|---|---|---|---|---|---|
| PILOT_1 | P10 = accusation baseline | RECOVERY_DOMINATED | accusation | yes | MIXED | no |
| PILOT_2 | P9 = scarcity baseline s=0 | SATURATION_DOMINATED | accusation | no | SATURATION_DOMINATED | yes |
| PILOT_3 | P4 = sacred baseline s=0 | RECOVERY_DOMINATED | accusation | no | RECOVERY_DOMINATED | yes |
| PILOT_4 | P3 = accusation p2a_off | SATURATION_DOMINATED | accusation | yes | SATURATION_DOMINATED | yes |

Aggregate:

- **Q2a primary pressure accuracy:** 2 / 4
- **Final summary self-call accuracy:** 3 / 4
- **Key failure mode:** pressure source is under-specified. Event trigger labels over-attract the evaluator toward `accusation`, even when hidden scenario type is scarcity/sacred.
