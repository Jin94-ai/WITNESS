# Full N=12 Eval Package — GPT-5.5 Single Evaluator

**Status**: Ready to send (post Lee decision lock 2026-04-28).
**Evaluator**: GPT-5.5 Thinking (per Lee decision, consistent with pilot eval)
**Mode**: Hybrid 6 original + 6 annotated (v3 fields), scenario-balanced
**Time budget**: ~70-105 min reading + 10-15 min writing

---

## 1. Evaluator instructions (paste this as system message to GPT-5.5)

```
You are an external readability evaluator for the WITNESS project. Your task is to read 12 simulation probes and answer a structured Q-set per probe, then produce aggregates and a Branch verdict.

Hidden context: Each probe is one 50-tick slice of a multi-agent simulation. You will read 6 in "original" (raw event log) format and 6 in "annotated" (v3 with summary header) format. The scenario type, seed, and variant are hidden — you must infer them from the data.

Rules:
1. Treat this as blind: do not search prior context for ground truth.
2. For each probe, fill all 12 columns of the per-probe table.
3. For annotated probes: BEFORE writing your final summary self-call, infer it from cohort outcomes (do NOT copy the visible "Final summary" label until your self-call is locked). Note: this is treated as a *label-intuition check* in post-eval analysis, not true blind.
4. For original probes: write a final summary self-call from raw event log (true blind arc inference).
4. Q6a confusion notes: tag each note with [FORMAT] / [STRUCTURE] / [Q_SET] / [SCOPE] / [OTHER] before free text.
5. Submit aggregates (§1.4 + §2.5) AFTER all 12 per-probe answers.
6. Final Branch verdict per protocol §5.2.

Q-set definitions, options, and scoring rule: see PROTOCOL §2 + §3 (provided below).

When done, output the filled RESULTS template (§2) and the Branch verdict.
```

---

## 2. Materials (ordered for evaluator delivery)

### 2.1 Protocol summary (paste as evaluator reference)

**Q-set V2 (verbatim from PROTOCOL_V2 §2)**:

| Q | Topic | Options |
|---|---|---|
| Q1 | Flow vs noise | RANDOM / FLOW_HINT / CLEAR_FLOW |
| Q1b | Readability confidence | CAN_EXPLAIN / PARTIAL_EXPLAIN / CANNOT_EXPLAIN |
| Q2a | Primary pressure | shame / fear / sacred / scarcity / accusation / grief / none |
| Q2b | Secondary pressure | (same as Q2a) / none_secondary |
| Q2c | Pressure clarity | CLEAR / MIXED_BUT_READABLE / VAGUE / UNREADABLE |
| Q3a | Relation/group level | NONE / LOCAL_SHIFT / COHORT_SHIFT / RESTRUCTURE |
| Q3b | What changed most (multi) | interpersonal / group_alignment / crowd_mood / authority / public_attention |
| Q4a | Primary arc | NO_ARC / FLAT / ESCALATION / RECOVERY / MIXED / CYCLIC |
| Q4b | Arc strength | WEAK / MODERATE / STRONG |
| Q5a | Oscillation type | NO_OSC / MEANINGLESS_NOISE / WEAK_RHYTHM / CLEAR_CYCLE |
| Q5b | Narrative contribution | HELPS / NEUTRAL / HURTS |

**Score rule (verbatim from PROTOCOL_V2 §3)**:
- **Readable**: Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN} AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}
- **Partially readable**: Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN) OR Q2c=VAGUE
- **Unreadable**: Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE

**Final summary 5 labels** (used in annotated headline + self-call): `LOW_ACTIVITY` / `RECOVERY_DOMINATED` / `SATURATION_DOMINATED` / `MIXED` / `PARTIAL`

### 2.2 Probe assignment (scenario-balanced 6+6 hybrid split)

| Half | Probes | Scenarios |
|---|---|---|
| Original | P1, P5, P8, P9, P10, P12 | 2 scarcity / 2 sacred / 2 accusation |
| Annotated v3 | P2, P3, P4, P6, P7, P11 | 2 scarcity / 2 sacred / 2 accusation |

**Source files** (provide to GPT-5.5):

```
ORIGINALS (raw event log, ~415 lines each):
  docs/b_direction/readability_probes/P1.txt
  docs/b_direction/readability_probes/P5.txt
  docs/b_direction/readability_probes/P8.txt
  docs/b_direction/readability_probes/P9.txt
  docs/b_direction/readability_probes/P10.txt
  docs/b_direction/readability_probes/P12.txt

ANNOTATED v3 (5-section + headline, ~100 lines each):
  docs/b_direction/readability_probes/P2_ANNOTATED.txt
  docs/b_direction/readability_probes/P3_ANNOTATED.txt
  docs/b_direction/readability_probes/P4_ANNOTATED.txt
  docs/b_direction/readability_probes/P6_ANNOTATED.txt
  docs/b_direction/readability_probes/P7_ANNOTATED.txt
  docs/b_direction/readability_probes/P11_ANNOTATED.txt
```

### 2.3 Reading order (interleaved to minimize order bias)

```
P1 (orig) → P2 (annot) → P3 (annot) → P4 (annot) → P5 (orig) → P6 (annot)
→ P7 (annot) → P8 (orig) → P9 (orig) → P10 (orig) → P11 (annot) → P12 (orig)
```

### 2.4 Answer template (paste as response format)

```markdown
# Full N=12 Results — GPT-5.5

## §2.1 Per-probe Q1, Q1b, Q2

| Probe | Format | Q1 | Q1b | Q2a | Q2b | Q2c |
|---|---|---|---|---|---|---|
| P1 | original | ? | ? | ? | ? | ? |
| P2 | annotated | ? | ? | ? | ? | ? |
| ...
| P12 | original | ? | ? | ? | ? | ? |

## §2.2 Per-probe Q3, Q4, Q5, Score

| Probe | Q3a | Q3b (multi) | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|
| P1 | ? | ? | ? | ? | ? | ? | ? |
| ...

## §2.3 Final summary self-call — ALL probes (Lee correction 2026-04-28)

**Required for both formats**:
- Original probes: self-call = blind arc inference (no label visible)
- Annotated probes: self-call = label-intuition check (label is visible at file top; treat self-call as "does the label feel intuitive given the cohort/event data?", NOT as true blind)

This is needed to compute Q4a-rollup gap = (annotated match rate) − (original self-call accuracy vs GT).

| Probe | Format | Self-call | Headline label (annotated only) | GT after reveal | Match self-call vs GT? |
|---|---|---|---|---|---|
| P1 | original | ? | n/a | ? | ? |
| P2 | annotated | ? | ? | ? | ? |
| P3 | annotated | ? | ? | ? | ? |
| P4 | annotated | ? | ? | ? | ? |
| P5 | original | ? | n/a | ? | ? |
| P6 | annotated | ? | ? | ? | ? |
| P7 | annotated | ? | ? | ? | ? |
| P8 | original | ? | n/a | ? | ? |
| P9 | original | ? | n/a | ? | ? |
| P10 | original | ? | n/a | ? | ? |
| P11 | annotated | ? | ? | ? | ? |
| P12 | original | ? | n/a | ? | ? |

**Interpretation note** (per Lee 2026-04-28):
- `original self-call accuracy` = N(original Match=yes) / 6
- `annotated match rate` = N(annotated Match=yes) / 6 — but this is *label-intuition*, not blind
- `Q4a-rollup gap` = annotated match rate − original self-call accuracy (positive = annotation helps arc rollup)

## §2.4 Q6a confusion notes per probe (tagged)

P1: [TAG] note
P2: [TAG] note
...

## §2.5 Aggregates

- Readable rate (originals 6): N/6
- Readable rate (annotated 6): N/6
- Format gap: ? pp
- CAN_EXPLAIN gap: ? pp
- Q4a-rollup gap: ? pp (annotated match rate − original self-call accuracy)
- Q2a-typing gap: ? pp (annotated Q2a correct − original Q2a correct, after revealing GT)
- Q3b world-side gap (per axis):
  - crowd_mood: ?
  - authority: ?
  - public_attention: ?
- Q6a tag distribution: [FORMAT]: N, [STRUCTURE]: N, [Q_SET]: N, [SCOPE]: N, [OTHER]: N

## §2.6 Branch verdict

Pattern matched (per PROTOCOL_V2 §4 v2.5 precedence-ordered):
- [ ] P-B (Format gap ±25% AND Q4a-rollup ≈0 AND Q3b ≈0)
- [ ] P-A+C (Q1 readable both ≥75% AND Q4a-rollup >0 AND Q2a-typing ≈0)
- [ ] P-A (any of: Format/CAN_EXPLAIN/Q4a-rollup ≥+50% AND not P-A+C)
- [ ] P-C-ready (both readable high AND CAN_EXPLAIN majority both AND Q3b ≥2 axes positive)
- [ ] P-Mixed (Q4a-rollup>0 AND Format≈0, residual)

Verdict: [pattern label]

## §3 Cross-probe observations (free text)
```

---

## 3. Ground truth (DO NOT share with GPT-5.5)

For post-eval comparison only. Source: `READABILITY_BLIND_GROUND_TRUTH.md`.

| Probe | Scenario | Variant | Final summary GT |
|---|---|---|---|
| P1 | scarcity | sham_mul_0.8 | PARTIAL |
| P2 | scarcity | baseline s=2 | SATURATION_DOMINATED |
| P3 | accusation | p2a_off | SATURATION_DOMINATED |
| P4 | sacred | baseline s=0 | RECOVERY_DOMINATED |
| P5 | sacred | baseline s=1 | RECOVERY_DOMINATED |
| P6 | scarcity | p2a_off | MIXED |
| P7 | sacred | sham_mul_0.05 | PARTIAL |
| P8 | accusation | sham_mul_0.8 | MIXED |
| P9 | scarcity | baseline s=0 | SATURATION_DOMINATED |
| P10 | accusation | baseline | RECOVERY_DOMINATED |
| P11 | accusation | baseline s=3 | MIXED |
| P12 | sacred | p2a_off | SATURATION_DOMINATED |

---

## 4. Branch C activation criteria (post-eval check)

After GPT-5.5 returns answers, compute 7 metrics and check 4/4 trigger:

| Metric | Trigger threshold |
|---|---|
| Readable rate (both formats) | ≥80% |
| CAN_EXPLAIN gap | ≥+50 pp |
| Q4a-rollup gap | ≥+30 pp |
| **Q2a-typing gap** | **≥+30 pp** (v2.1 fix expected to deliver +50 pp) |
| **Q3b world-side gap** | **≥2 axes positive** (v3 fix expected with public_suspicion + authority_vigilance) |

**4/4 trigger → Branch C 실질 활성화 가능** (currently FORBIDDEN_NOW until confirm).

---

## 5. Post-eval next actions

| If verdict... | Then... |
|---|---|
| **P-A+C confirmed (4/4 trigger)** | Branch C 실질 활성화 — broader world prep (별도 directive 필요) |
| **P-A+C 유지 (3/4 trigger)** | Identify gap → v4 spec (annotated relation/motif shift) |
| **P-A only (Q3b 못 함)** | Branch A confirmed; Branch C는 v4+ 필요 |
| **P-B (Format gap ±25 + Q4a-rollup ≈0)** | Unexpected reversal; review structure 단순화 |
| **P-Mixed** | additional N=N+12 또는 v4 design |

---

## 6. Versioning

| Version | Date | Note |
|---|---|---|
| v1 | 2026-04-28 | Initial package post Lee decision lock. |
| **v1.1 (this)** | **2026-04-28** | **Lee correction (post-GPT review): §2.3 self-call expanded to all 12 probes (was annotated-only). Original = blind arc inference, annotated = label-intuition check. Q4a-rollup gap formula now computable. Execution approved.** |
