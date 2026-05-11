# WITNESS Story Viability Report — peter_scarcity_baseline

> Stage A-F output (Story Viability Validation Plan).
>
> *What this answers*: Can each StoryCandidate be converted into a Scene
> Brief and a 1-page Treatment without inventing events / dialogue /
> locations? And does the result feel like a usable creator-facing seed?
>
> *What this does not do*: write the story. No prose, no dialogue, no
> screenplay. The forbidden surface is enforced by Stage F audit.

## 1. Summary

| Candidate | Score | Grade | Brief audit | Treatment audit | Overall |
|---|---:|---|---|---|---|
| `S01` `Loyalty Strained by Survival Pressure` | 100.0 | `strong_viable` | `pass` | `pass` | `pass` |
| `S02` `Uncertainty Lingers Without Commitment` | 73.0 | `viable_with_gaps` | `pass` | `pass` | `pass` |
| `S03` `Uncertainty Lingers Without Commitment` | 77.5 | `viable_with_gaps` | `pass` | `pass` | `pass` |
| `S04` `Uncertainty Lingers Without Commitment` | 77.5 | `viable_with_gaps` | `pass` | `pass` | `pass` |

## 2. Strongest Candidate

**`S01` — Loyalty Strained by Survival Pressure** (score 100.0, grade `strong_viable`).

- Premise: *Peter tries to stay present as fear and public pressure slowly turn loyalty into silence.*
- Audit: `pass` (0 violations, 0 risky phrases)
- Top scoring factors: character_clarity=1.00, conflict_clarity=1.00, pressure_accumulation=1.00

## 3. Candidate-by-Candidate Review

### S01 — Loyalty Strained by Survival Pressure

- **Score**: 100.0  /  **Grade**: `strong_viable`
- **Brief completeness**: `complete`  · missing: (none)
- **Treatment completeness**: `complete`  · missing: (none)
- **Audit**: brief=`pass`, treatment=`pass`, overall=`pass`
- **Violations**: (none)
- **Risky phrases**: (none)
- **Score notes**:
  - (none)
- **Recommended use**: see scene brief at [SCENE_BRIEFS.md#s01](SCENE_BRIEFS.md) and treatment at [ONE_PAGE_TREATMENTS.md#s01](ONE_PAGE_TREATMENTS.md)

### S02 — Uncertainty Lingers Without Commitment

- **Score**: 73.0  /  **Grade**: `viable_with_gaps`
- **Brief completeness**: `scene_brief_incomplete`  · missing: external_pressure
- **Treatment completeness**: `complete`  · missing: (none)
- **Audit**: brief=`pass`, treatment=`pass`, overall=`pass`
- **Violations**: (none)
- **Risky phrases**: (none)
- **Score notes**:
  - scene brief missing fields: external_pressure
- **Recommended use**: see scene brief at [SCENE_BRIEFS.md#s02](SCENE_BRIEFS.md) and treatment at [ONE_PAGE_TREATMENTS.md#s02](ONE_PAGE_TREATMENTS.md)

### S03 — Uncertainty Lingers Without Commitment

- **Score**: 77.5  /  **Grade**: `viable_with_gaps`
- **Brief completeness**: `scene_brief_incomplete`  · missing: external_pressure
- **Treatment completeness**: `complete`  · missing: (none)
- **Audit**: brief=`pass`, treatment=`pass`, overall=`pass`
- **Violations**: (none)
- **Risky phrases**: (none)
- **Score notes**:
  - scene brief missing fields: external_pressure
- **Recommended use**: see scene brief at [SCENE_BRIEFS.md#s03](SCENE_BRIEFS.md) and treatment at [ONE_PAGE_TREATMENTS.md#s03](ONE_PAGE_TREATMENTS.md)

### S04 — Uncertainty Lingers Without Commitment

- **Score**: 77.5  /  **Grade**: `viable_with_gaps`
- **Brief completeness**: `scene_brief_incomplete`  · missing: external_pressure
- **Treatment completeness**: `complete`  · missing: (none)
- **Audit**: brief=`pass`, treatment=`pass`, overall=`pass`
- **Violations**: (none)
- **Risky phrases**: (none)
- **Score notes**:
  - scene brief missing fields: external_pressure
- **Recommended use**: see scene brief at [SCENE_BRIEFS.md#s04](SCENE_BRIEFS.md) and treatment at [ONE_PAGE_TREATMENTS.md#s04](ONE_PAGE_TREATMENTS.md)

## 4. Stage E — Human Pick Test (manual)

This stage is *not automated*. Per plan §9, ask 3+ reviewers:

1. Could you actually write a scene / episode / quest from this? (1–5)
2. Which candidate would you pick first?
3. Why that one?
4. What information is missing?
5. Which sentence reads as data, not story?
6. Where do you see forced "story-ification"?
7. Best medium for this candidate? film / novel / game / none

**Pass criteria** (per candidate):
- avg of question 1 ≥ 0.70 of 5 (i.e. ≥ 3.5/5)
- selection_rate ≥ 1/3
- no major over-inference complaint

Use the strongest candidate above as the *first* show item.

## 5. Evidence Audit Result

- Total candidates: 4
- audit_fail: 0
- risky (no fail): 0
- pass: 4

## 6. Decision

**SHIP** — at least one strong_viable or two viable_with_gaps, zero audit_fail.

## 7. Honesty disclosures

- This report scores *viability* (could you write a scene?), not narrative quality.
- All sentences are deterministic templates over source-derived candidate fields.
- Stage F audit is keyword-based — it catches obvious dialogue/screenplay markers and a finite list of risky verbs. A new violation pattern requires updating `engine/observer/story_audit.py`.
- Cross-seed robustness factor only fires when `cross_seed_story_patterns.json` is present.
- Human Pick Test is *required* for the top-line claim ("yes, this is usable"). Without it, the score is system self-assessment only.

---

*Generated by* `scripts/narrative/build_story_viability_report.py`.
