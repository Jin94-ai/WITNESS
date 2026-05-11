# RESULTS_V2_FILLED_FULL_N12_TRUE_COMBINED

**Status:** TRUE combined consolidation from uploaded P1-P12 originals + P1-P12 annotated supplements.  
**Date:** 2026-04-28

**Important scope note:** This is **not a pure blind eval**. It is a post-eval consolidation that uses both raw event logs and annotated supplements. Raw self-call is preserved separately to show where annotation resolved ambiguity.

## 0. Input set

- Originals: `P1(1).txt` through `P12(1).txt`
- Annotated supplements: `P1_ANNOTATED.txt` through `P12_ANNOTATED.txt`
- Consolidation rule: use raw logs for raw self-call / readability friction; use annotated supplements for cohort rollup, final label, and cross-check.

## 1. Per-probe Q1, Q1b, Q2

| Probe | Scenario inferred | Format used | Q1 | Q1b | Q2a | Q2b | Q2c |
|---|---|---|---|---|---|---|---|
| P1 | scarcity | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR |
| P2 | scarcity | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR |
| P3 | accusation | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | fear | CLEAR |
| P4 | sacred | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR |
| P5 | sacred | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR |
| P6 | scarcity | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR |
| P7 | sacred | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR |
| P8 | accusation | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | fear | CLEAR |
| P9 | scarcity | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR |
| P10 | accusation | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | fear | CLEAR |
| P11 | accusation | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation | fear | CLEAR |
| P12 | sacred | original+annotated | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR |

## 2. Per-probe Q3, Q4, Q5, Score

| Probe | Q3a | Q3b (multi) | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|
| P1 | COHORT_SHIFT | group_alignment, crowd_mood, authority, public_attention | MIXED | MODERATE | WEAK_RHYTHM | HELPS | Readable |
| P2 | COHORT_SHIFT | group_alignment, crowd_mood, authority, public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P3 | RESTRUCTURE | group_alignment, crowd_mood, authority, public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P4 | COHORT_SHIFT | interpersonal, group_alignment, crowd_mood, public_attention | RECOVERY | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P5 | COHORT_SHIFT | interpersonal, group_alignment, crowd_mood, public_attention | RECOVERY | MODERATE | CLEAR_CYCLE | HELPS | Readable |
| P6 | RESTRUCTURE | group_alignment, crowd_mood, authority, public_attention | MIXED | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P7 | COHORT_SHIFT | interpersonal, group_alignment, crowd_mood, public_attention | MIXED | MODERATE | WEAK_RHYTHM | HELPS | Readable |
| P8 | RESTRUCTURE | group_alignment, crowd_mood, authority, public_attention | MIXED | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P9 | COHORT_SHIFT | group_alignment, crowd_mood, authority, public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P10 | RESTRUCTURE | group_alignment, crowd_mood, authority, public_attention | RECOVERY | MODERATE | CLEAR_CYCLE | HELPS | Readable |
| P11 | RESTRUCTURE | group_alignment, crowd_mood, authority, public_attention | MIXED | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P12 | COHORT_SHIFT | interpersonal, group_alignment, crowd_mood, public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |

## 3. Final summary self-call comparison

| Probe | Raw self-call from original | Annotated / GT label | Match? | Note |
|---|---|---|---|---|
| P1 | PARTIAL | PARTIAL | yes | merchant scarcity pressure; partial recovery with residual shame |
| P2 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes | merchant/laborer cluster saturates despite many confessions |
| P3 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes | two accusations and public denial field produce stuck saturation |
| P4 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes | sacred setup plus late confession/recovery is legible |
| P5 | PARTIAL | RECOVERY_DOMINATED | no | raw snapshot suggests partial residue; annotated rollup resolves as recovery |
| P6 | SATURATION_DOMINATED | MIXED | no | raw looks saturation-heavy; annotated reveals recovery + saturation cohort split |
| P7 | PARTIAL | PARTIAL | yes | high residual shame without full saturation; partial arc |
| P8 | MIXED | MIXED | yes | some cohorts recover while accused/outside actors stay high |
| P9 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes | laborer/enforcer/crowd cluster saturates by t=200 |
| P10 | MIXED | RECOVERY_DOMINATED | no | raw suggests residual stuck agents; annotated rollup classifies dominant recovery with partial residue |
| P11 | MIXED | MIXED | yes | explicit recovery cohort plus saturation cohort |
| P12 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes | spiritual_wanderer accusation generates stuck sacred-shame cohort |

## 4. Q6a confusion notes, tagged

- P1: [FORMAT:DENSITY] raw log is repetitive but partial arc is recoverable from final snapshot; annotated cohort rollup makes the partial label clear.
- P2: [FORMAT:DENSITY] raw confessions are numerous; saturation is clear only after checking final snapshot.
- P3: [STRUCTURE:RECOVERY] many confessions do not imply recovery; saturation requires final-state check.
- P4: [FORMAT:GROUPING] annotated grouping makes late recovery readable; raw log is sparse enough but takes more effort.
- P5: [SCOPE:TRAJECTORY] raw final snapshot appears more partial than annotated recovery label; needs generator/source consistency check.
- P6: [SCOPE:RELATION] raw view hides cohort split; annotated reveals mixed recovery+saturation.
- P7: [STRUCTURE:RECOVERY] partial state is legible, but Q4a lacks a direct PARTIAL option; forced into MIXED.
- P8: [FORMAT:DENSITY] raw accusation case is readable but long; annotated cohort split reduces effort.
- P9: [STRUCTURE:MECHANISM] saturation is clear; causal difference from P1/P2 needs scenario/variant metadata after eval.
- P10: [SCOPE:TRAJECTORY] raw residual saturation conflicts with dominant recovery label; needs rule clarification for RECOVERY_DOMINATED when partial residue exists.
- P11: [FORMAT:HEADLINE] annotated headline correctly exposes mixed divergence.
- P12: [STRUCTURE:WORLD_SIDE] saturation is clear; world-side authority/public dynamics are still mostly inferred, not explicitly surfaced in headline.

## 5. Aggregates

- Readable rate, combined 12: **12/12 = 100%**
- Readable rate, original-only interpretability: **12/12 readable**, but with higher ambiguity on P5, P6, P10.
- Readable rate, annotated supplements: **12/12 readable**.
- Format effect: annotation does not merely improve readability; it materially improves **arc rollup confidence**.
- Raw self-call accuracy vs annotated/GT label: **9/12 = 75.0%**
- Annotated label match by definition/check: **12/12 = 100.0%**
- Q4a-rollup lift, annotated vs raw self-call: **+25.0 pp**
- Q2a typing, combined: **12/12 = 100.0%**
- Q2a typing improvement source: role/cast/location signatures are sufficient in combined view; strict blind improvement still needs isolated evaluator if required.
- Q3b world-side axes selected:
  - crowd_mood: **12/12**
  - authority: **8/12**
  - public_attention: **12/12**
- Q6a tag distribution: [FORMAT]=4, [STRUCTURE]=4, [SCOPE]=3, [Q_SET]=0, [OTHER]=0

## 6. Branch verdict

**Verdict:** `P-C-ready, with Branch A presentation sub-signal retained`.

Rationale:

1. Combined readability is 12/12.
2. Annotated supplements resolve arc rollup errors in P5/P6/P10.
3. Scenario typing is clear in combined view.
4. World-side dynamics are inferable across all probes, but uploaded annotated headlines still mainly expose `Crowd blame total`; authority/public-attention fields are not explicitly surfaced in the provided annotated files.

**Operational interpretation:** Branch C may be prepared, but broad world-side work should not start until Lee gives a separate directive and the annotation-field mismatch is checked.

## 7. Critical discrepancies to inspect before locking this as canonical

| Probe | Issue | Why it matters | Action |
|---|---|---|---|
| P5 | raw final snapshot looks PARTIAL, annotated says RECOVERY_DOMINATED | could be rollup rule or source mismatch | inspect generator + GT source |
| P6 | raw looks saturation-heavy, annotated says MIXED | cohort split not visible enough in raw | keep annotation; verify cohort mapping |
| P10 | raw has stuck high-shame agents, annotated says RECOVERY_DOMINATED | need rule for recovery-dominated despite partial residue | clarify final-summary rule |
| all annotated | no explicit `public_suspicion` / `authority_vigilance` fields visible | dashboard expected v3 world-side fields, but files show crowd blame only | update annotated format or generator output |

## 8. Bottom line

The combined evidence supports moving to **Branch C preparation**, not unrestricted Branch C execution. The next gate is not another readability pass; it is a consistency check on annotated field output and a Lee directive for broader world work.
