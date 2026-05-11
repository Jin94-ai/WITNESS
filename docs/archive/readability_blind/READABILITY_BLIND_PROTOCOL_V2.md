# WITNESS Readability Blind Protocol V2

**Date:** 2026-04-26
**Iteration:** Iter 178 (Step A3)
**Supersedes:** `READABILITY_BLIND_PROTOCOL.md` (v1)
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step A3

---

## 0. What's new in V2

V2 keeps the v1 Q-set (Q1, Q1b, Q2a-c, Q3a-b, Q4a-b, Q5a-b, Q6a-b) and adds:

1. **Pilot mode (N=4)** -- low-threshold eval per Step A2 (15-20 min vs 1-2 h)
2. **Format axis** -- explicit original vs annotated tracking (per Step A1)
3. **Format-by-Q aggregation rules** -- separate readable rates by format
4. **Pilot-specific branch decision rules** -- adjusted for N=4 noise
5. **Q6a structured taxonomy** -- confusion notes can be tagged for thematic analysis

The Q-set itself is unchanged from v1 (which already incorporated the
WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md improvements).

---

## 1. Modes

### 1.1 Pilot mode (N=4)
- **Materials**: `docs/b_direction/readability_pilot/PILOT_{1-4}_*.txt`
- **Time budget**: 15-20 min total (3-5 min/probe)
- **Format split**: 2 original + 2 annotated
- **Use case**: lower-threshold first read, signal-only verdict

### 1.2 Full mode (N=12)
- **Materials**: `docs/b_direction/readability_probes/P{1-12}.txt`
- **Time budget**: 1-2 hours
- **Format**: all original (or all annotated, or hybrid 6+6 -- evaluator's choice)
- **Use case**: definitive verdict; pilot has insufficient signal

### 1.3 Hybrid mode
- 6 originals + 6 annotated from full set, format-balanced
- **Time budget**: 1-2 hours
- **Use case**: directly compare format efficacy at full N

---

## 2. Question set (unchanged from v1)

See `READABILITY_BLIND_PROTOCOL.md` §3 for full definitions. Summary:

| Q | Topic | Options |
|---|---|---|
| Q1 | Flow vs noise | RANDOM / FLOW_HINT / CLEAR_FLOW |
| Q1b | Readability confidence | CAN_EXPLAIN / PARTIAL_EXPLAIN / CANNOT_EXPLAIN |
| Q2a | Primary pressure | shame / fear / sacred / scarcity / accusation / grief / none |
| Q2b | Secondary pressure | (same) or none_secondary |
| Q2c | Pressure clarity | CLEAR / MIXED_BUT_READABLE / VAGUE / UNREADABLE |
| Q3a | Relation/group level | NONE / LOCAL_SHIFT / COHORT_SHIFT / RESTRUCTURE |
| Q3b | What changed most (multi) | interpersonal / group_alignment / crowd_mood / authority / public_attention |
| Q4a | Primary arc | NO_ARC / FLAT / ESCALATION / RECOVERY / MIXED / CYCLIC |
| Q4b | Arc strength | WEAK / MODERATE / STRONG |
| Q5a | Oscillation type | NO_OSC / MEANINGLESS_NOISE / WEAK_RHYTHM / CLEAR_CYCLE |
| Q5b | Narrative contribution | HELPS / NEUTRAL / HURTS |
| Q6a | Confusion notes | semi-required, structured taxonomy below |
| Q6b | Design feedback | free text |

### 2.1 Q6a structured taxonomy (NEW in V2)

In V2, Q6a accepts categorical tags in addition to free text. Tag each
confusion note with one or more:

| Tag | Meaning | Branch-relevance |
|---|---|---|
| `[FORMAT]` | Probe formatting / presentation issue | Branch A (presentation work) |
| `[STRUCTURE]` | Kernel mechanism not detectable | Branch B (simplification) |
| `[Q_SET]` | Question itself is unclear | Q-set revision (V3) |
| `[SCOPE]` | Probe lacks information needed | Probe redesign |
| `[OTHER]` | Doesn't fit above | Free text |

### 2.1.1 Sub-categories (Iter 186 v2.1 refinement)

Each main tag MAY take an optional sub-tag for finer mechanical aggregation.
Sub-tags are NOT required; evaluator can keep just the main tag.

#### `[FORMAT]` sub-tags
- `[FORMAT:LENGTH]` — too long / too short
- `[FORMAT:DENSITY]` — events too dense or sparse to follow
- `[FORMAT:ANONYMIZATION]` — role/location label confusing
- `[FORMAT:GROUPING]` — tick window or cohort grouping unhelpful
- `[FORMAT:HEADLINE]` — headline summary missing or wrong field
- `[FORMAT:CAP]` — cap disclosure unclear (if applicable, v1.1 annotated)

#### `[STRUCTURE]` sub-tags
- `[STRUCTURE:MECHANISM]` — kernel mechanism not detectable
- `[STRUCTURE:AGENCY]` — who is doing what is unclear
- `[STRUCTURE:CAUSALITY]` — event chain doesn't connect
- `[STRUCTURE:WORLD_SIDE]` — crowd/authority/public dynamics not surfacing
- `[STRUCTURE:RECOVERY]` — recovery vs saturation arc not legible

#### `[Q_SET]` sub-tags
- `[Q_SET:AMBIGUOUS]` — question wording unclear
- `[Q_SET:MISSING_OPTION]` — needed answer option absent
- `[Q_SET:OVERLAP]` — two questions ask the same thing
- `[Q_SET:WRONG_LEVEL]` — question asks wrong granularity (per-agent vs cohort)

#### `[SCOPE]` sub-tags
- `[SCOPE:HIDDEN_DATA]` — kernel did more than probe shows (e.g., cap)
- `[SCOPE:TRAJECTORY]` — per-agent shame trajectory missing
- `[SCOPE:RELATION]` — relationship/trust evolution missing
- `[SCOPE:TIMING]` — event timing/duration not visible

#### `[OTHER]`
- Free text. If pattern repeats, escalate to new sub-tag in next revision.

Example with sub-tags:
```
Q6a:
- [FORMAT:DENSITY] event log too dense between t=20-50, hard to follow
- [STRUCTURE:WORLD_SIDE] no signal that authority is acting on crowd
- [SCOPE:HIDDEN_DATA] cap disclosure says 200 confessions but only 30 shown
- [Q_SET:OVERLAP] Q4a and Q5a both ask about cyclic patterns
```

### 2.1.2 Why sub-tags

Main tags give branch direction (FORMAT → A, STRUCTURE → B). Sub-tags
give **action direction**:
- `[FORMAT:DENSITY]` → format revision target = event log layout
- `[FORMAT:HEADLINE]` → format revision target = headline fields
- `[STRUCTURE:WORLD_SIDE]` → kernel addition target = world-side process
- `[SCOPE:HIDDEN_DATA]` → presentation target = uncap or summarize

Without sub-tags, "FORMAT majority" tells us to do something but not what.

Aggregation now multi-level:
- Main: `% [FORMAT] vs % [STRUCTURE]` → branch hint (V2 §5)
- Sub: top-3 sub-tags within each main → action queue

This allows mechanical aggregation: % FORMAT vs % STRUCTURE → branch hint.
Sub-tag distribution → which formatting/structure improvement is highest leverage.

---

## 3. Per-probe scoring (unchanged from v1)

| Classification | Conditions |
|---|---|
| **Readable** | Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN} AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE} |
| **Partially readable** | Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN) OR Q2c=VAGUE |
| **Unreadable** | Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE |

---

## 4. Format-axis aggregation (NEW in V2)

When pilot or hybrid mode is used, separate readable rates by format:

| Metric | Formula | What it isolates |
|---|---|---|
| Readable rate (original) | (readable count among original) / (total original) | Baseline format legibility |
| Readable rate (annotated) | (readable count among annotated) / (total annotated) | Annotated format legibility |
| Format gap | annotated rate - original rate | Coarse format effect on Q1 readable |
| CAN_EXPLAIN gap | (CAN_EXPLAIN count annotated) / N - (CAN_EXPLAIN count original) / N | Q1b confidence improvement |
| Q5b HELPS rate gap | (HELPS count annotated) / N - (HELPS count original) / N | Oscillation reading benefit |
| **Q4a-rollup gap** (v2.2) | (final summary self-call accuracy on annotated, with label visible) - (on original, vs ground truth) | Whether annotated's `Final summary` line resolves cohort rollup ambiguity |
| **Q2a-typing gap** (v2.2) | (Q2a primary pressure correct on annotated) / N - (on original) / N | Whether annotated format helps scenario-type detection (orthogonal to Q4a-rollup) |
| **Q3b world-side gap** (NEW v2.3) | (count of {crowd_mood, authority_presence, public_attention} selected on annotated) / N - (on original) / N | Whether annotated format helps detect world-side process. Direct Branch C signal (per §5.2). |

### Interpretation (extended v2.2)

The `Q4a-rollup gap` and `Q2a-typing gap` are **orthogonal axes**:
- `Q4a-rollup gap` measures **arc-shape inference** (recovery vs saturation vs mixed)
- `Q2a-typing gap` measures **scenario-type inference** (accusation vs scarcity vs sacred)

Annotated headline (v1.2) currently surfaces Q4a-rollup explicitly via
`Final summary` line. It does NOT surface scenario type — the cohort
labels stay agnostic to whether shame came from accusation / scarcity / sacred.

Empirical signal from Iter 189 Claude simulation (with mechanism-knowledge
caveat): Q4a-rollup gap = +50%, Q2a-typing gap = 0% (annotated did not
help scenario typing).

If Lee's true blind shows similar pattern, this **isolates which dimension
of readability annotation actually solved**:
- `Q4a-rollup gap > 0, Q2a-typing gap ≈ 0` → annotation = arc rollup tool only
- `Both > 0` → annotation surfaces scenario type too (label leak risk)
- `Both ≈ 0` → annotation didn't help; structure is bottleneck (Branch B signal)

### v2.3 extension: Q3b world-side gap (direct Branch C signal)

Protocol V2 §5.2 Branch C requires `Q3b world-side picked frequently`. The
v2.3 metric measures whether annotated format **surfaces world-side process
better than original**. Three world-side options:
- `crowd_mood`
- `authority_presence`
- `public_attention`

Annotated v1.2 surfaces only `crowd_blame_total` in headline. authority/
public_attention are NOT in headline. So expected:
- `Q3b world-side gap` from `crowd_mood` axis: **>0** (annotated wins via crowd_blame)
- `Q3b world-side gap` from `authority/public_attention` axes: **≈0** (neither format surfaces)

If Lee true blind confirms this asymmetry, future format extension target
is clear: add authority/public_attention to annotated headline.

Branch C readiness check: Q3b world-side gap meaningfully positive AND
Q1 readable rate high on both formats.

### v2.4 Action queue matrix (Iter 191 synthesis)

7 format-axis metrics map to branch / action signals:

| Metric | Pattern | Reading | Branch implication / action |
|---|---|---|---|
| **Readable rate (both)** | both ≥ 75% | both formats legible | Branch C readiness signal |
| | both ≤ 25% | both formats illegible | Branch B priority |
| | annotated > original | format helps | Branch A signal (coarse) |
| **Format gap** (Readable) | ≥ +50% | strong format effect | Branch A confirmed |
| | +25%~+50% | moderate format effect | Branch A candidate |
| | ±25% | format-neutral | structure is bottleneck (Branch B hint) |
| | ≤ -25% | annotation hurts | rollback annotated; revisit format design |
| **CAN_EXPLAIN gap** (Q1b) | ≥ +50% | annotation surfaces explainability | A-explainability sub-action |
| | ≈ 0 | structure is explainable both ways | C-readiness sub-signal |
| **Q5b HELPS gap** | > 0 | annotation makes oscillation readable | A-presentation action |
| | ≈ 0 or < 0 | oscillation neutral / hurts regardless | Q5 indicator non-critical |
| **Q4a-rollup gap** | > +50% | arc rollup needs explicit label | A-arc action: keep `Final summary` |
| | ≈ 0 | arc readable from raw probe | C-readiness sub-signal |
| **Q2a-typing gap** | > 0 | annotation surfaces scenario type | label leak risk + future format extension |
| | ≈ 0 | annotation orthogonal to scenario type | annotation = arc tool only (Iter 187 design intent) |
| **Q3b crowd_mood gap** | > 0 | crowd_blame_total surfaces | annotated v1.2 designed for this; expected |
| | ≈ 0 | crowd dynamics not perceived from headline | revisit crowd-state field in headline |
| **Q3b authority_presence gap** | > 0 | annotation surfaces authority | UNEXPECTED — investigate (annotation doesn't have this field) |
| | ≈ 0 | authority not surfaced | next format extension target |
| **Q3b public_attention gap** | > 0 | annotation surfaces public attention | same as authority — UNEXPECTED |
| | ≈ 0 | not surfaced | next format extension target |

#### Action queue derived from above

After Lee's true blind eval, walk down the matrix and collect implied
actions. Common patterns:

**Pattern P-A (Branch A confirmed) — v2.5 relaxed**:
- ANY of:
  - Format gap (Readable) ≥ +50%
  - CAN_EXPLAIN gap ≥ +50%
  - Q4a-rollup gap > +50%
- AND NOT P-A+C (see precedence below)
- → Branch A confirmed (some annotation dimension dominantly helps)

**Pattern P-B (Branch B signal)**:
- Format gap (Readable) ±25%
- Q4a-rollup gap ≈ 0
- All Q3b world-side ≈ 0
- → Structure unclear regardless of format; revisit kernel mechanisms

**Pattern P-C-ready (Branch C readiness)**:
- Both Readable rates high (≥75%)
- Q1b CAN_EXPLAIN majority on both
- Q3b world-side >0 on multiple axes
- Mixed-arc maintained (Q4a varied across probes)
- → Run full N=12 to confirm

**Pattern P-Mixed (residual catch-all)**:
- Q4a-rollup gap >0 BUT Q1 readable rate gap ≈ 0
- AND NOT P-A+C (see precedence)
- → Annotation helps a sub-dimension only; Branch A-arc but not full A
- → Run full N=12 to disambiguate

**Pattern P-A+C (Iter 189 sim's read) — most specific**:
- Q1 readable both formats high (≥75%)
- Q4a-rollup gap >0
- Q2a-typing gap ≈ 0 (annotation orthogonal to scenario typing)
- → Branch A on arc + Branch C readiness; full eval needed for confirm

### v2.5 Decision algorithm (precedence-ordered)

Patterns are NOT mutually exclusive on raw conditions (Iter 193 sanity check
revealed sim results match both P-Mixed and P-A+C). Apply in this order;
take FIRST match:

1. **P-B** — clear Branch B signal (early-out if structure issue)
2. **P-A+C** — most specific (Q1 readable both + arc gap + scenario orthogonal)
3. **P-A** — Branch A confirmed via any single dimension
4. **P-C-ready** — both formats readable + world-side detected
5. **P-Mixed** — residual (annotation helps a sub-dimension only)

### v2.5 Sanity check trace — Iter 189 Claude sim

| Metric | sim value |
|---|---|
| Readable rate (original) | 100% (2/2) |
| Readable rate (annotated) | 100% (2/2) |
| Format gap (Readable) | 0% |
| CAN_EXPLAIN gap | +100% |
| Q5b HELPS gap | 0% |
| Q4a-rollup gap | +50% |
| Q2a-typing gap | 0% |
| Q3b world-side gap | not measured |

Apply algorithm:
1. P-B? Format gap ±25% YES, but Q4a-rollup gap = +50% (NOT ≈0) → **NO**
2. P-A+C? Q1 readable both high (100%, 100%) YES, Q4a-rollup gap > 0 YES, Q2a-typing gap ≈0 YES → **MATCH**
3. (skip — first match wins)

**Sim result classifies as P-A+C** (consistent with Iter 189 sim's own claim).

This matrix is **provisional** — adjustments expected after Lee's first
true blind. v2.6 may consolidate or split patterns based on actual data.


| Format gap | Reading |
|---|---|
| ≥ +50% (annotated 2/2 vs original 0/2) | Strong format effect; annotation helps |
| +25% to +50% | Moderate format effect |
| ±25% | Format-neutral; structure is the bottleneck |
| ≤ -25% | Annotation hurts (e.g., leaks ground truth misleadingly) |

---

## 5. Branch decision rules

### 5.1 Pilot mode (N=4)

Pilot is hint-grade due to N=4 noise. Do not finalize branch on pilot alone.

| Pattern | Action |
|---|---|
| Annotated 2/2 readable, original ≤1/2 readable | Branch A confirmed (format works); skip full eval optional |
| Both formats 2/2 readable | Branch C ready (both formats work); confirm with full eval |
| Both formats ≤1/2 readable | Branch B priority (structure issue); pivot to simplification |
| Mixed (annotated 2/2, original 2/2) ambiguous | Run full N=12 eval to resolve |

### 5.2 Full mode (N=12)

Same as v1 §10 thresholds:

| Branch | Conditions (all required) |
|---|---|
| **Branch A** | Readable ≥ 8/12 AND CAN_EXPLAIN majority AND Q6a [FORMAT] dominates |
| **Branch B** | Readable ≤ 3/12 AND Q1=RANDOM frequent AND Q6a [STRUCTURE] dominates |
| **Branch A+B** | Readable 4-7/12 AND Q6a mixed FORMAT/STRUCTURE |
| **Branch C** | Readable high AND Q3b shows world-side perception (crowd_mood / authority / public_attention) AND mixed-arc maintained |

### 5.3 Hybrid mode (N=12, 6+6)

Combines §5.1 format-axis analysis with §5.2 thresholds. Most informative
mode if time permits.

---

## 6. Probe materials

### Pilot
| File | Source | Format |
|---|---|---|
| `readability_pilot/PILOT_1_original.txt` | P10 (accusation baseline) | original |
| `readability_pilot/PILOT_2_original.txt` | P9 (scarcity baseline) | original |
| `readability_pilot/PILOT_3_annotated.txt` | P4 (sacred baseline) | annotated |
| `readability_pilot/PILOT_4_annotated.txt` | P3 (accusation p2a_off) | annotated |

### Full (12 probes)
- Original: `readability_probes/P{1-12}.txt`
- Annotated supplement: `readability_probes_annotated/P{1-12}_ANNOTATED.txt`

Ground truth (held separately): `READABILITY_BLIND_GROUND_TRUTH.md`

---

## 7. Workflow

### 7.1 Pilot workflow
1. Read this protocol (V2)
2. Open `readability_pilot/PILOT_{1-4}_*.txt` in order
3. Answer Q1-Q6 per probe (3-5 min each)
4. Fill `READABILITY_BLIND_RESULTS_V2.md` (pilot section)
5. Apply §5.1 pilot decision rule
6. Decide: skip full eval / run full eval / revise format

### 7.2 Full workflow
1. Read this protocol (V2)
2. Decide format: original / annotated / hybrid
3. Open chosen probe set
4. Answer Q1-Q6 per probe (5-10 min each)
5. Fill `READABILITY_BLIND_RESULTS_V2.md` (full section)
6. Apply §5.2 (or §5.3 if hybrid) decision rule

---

## 8. Who can do what (unchanged from v1)

Claude can:
- Generate probe text (existing scripts)
- Pre-populate ground truth
- Aggregate categorical answers into verdict after evaluator returns

Claude **cannot**:
- Act as the blind evaluator (has full mechanism knowledge)
- Interpret Q-set answers without human input
- Decide branch unilaterally (Lee retains gate)

---

## 9. What's NOT in V2 (deferred)

Per H4 negative findings discipline:

- **Multi-evaluator design**: V2 is single-evaluator. Inter-rater agreement
  not measured. If multiple evaluators are available, run independently and
  compute Cohen's kappa post-hoc.
- **Quantitative confusion analysis**: Q6a tagging is manual. No automated
  tag extraction or clustering.
- **Time-tracking enforcement**: pilot 15-20 min target is honor system.
  Actual time logging is recommended but not required.
- **Q-set V3 revisions**: V2 keeps v1 Q-set. If pilot Q6a [Q_SET] tags
  cluster on specific questions, V3 will revise those questions.

---

## 10. Versioning

| Version | Date | Change |
|---|---|---|
| v1 (Iter 161) | 2026-04-26 | Q-set v2 adopted, format-neutral |
| v2 (Iter 178) | 2026-04-26 | Pilot mode + format-axis + Q6a taxonomy (5 main tags) |
| v2.1 (Iter 186) | 2026-04-27 | Q6a sub-tags (~18 sub-categories under 5 main). |
| v2.2 (Iter 189) | 2026-04-27 | §4 format-axis + 2 metrics: Q4a-rollup gap, Q2a-typing gap. |
| v2.3 (Iter 190) | 2026-04-27 | §4 + Q3b world-side gap (Branch C signal direct). |
| v2.4 (Iter 191) | 2026-04-27 | §4 Action queue matrix — 7 metrics × patterns → branch action implications. 5 named patterns. |
| **v2.5 (Iter 193)** | **2026-04-27** | **§4 sanity check fix: patterns NOT mutually exclusive on raw conditions. v2.5 adds (a) precedence-ordered decision algorithm, (b) P-A relaxed to OR over Format/CAN_EXPLAIN/Q4a-rollup gaps, (c) sim trace verification (P-A+C match confirmed).** |
| v3 (post Step C) | TBD | Will revise Q-set if pilot Q6a [Q_SET:*] sub-tags converge on specific question |
