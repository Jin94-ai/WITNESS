# WITNESS — Observer Brief (Portfolio Sample)

> **2026-05-06 update**: 이 abridged brief는 Reporting Layer (Phase 11) 산출물이다.
> 현재 메인 deliverable은 한 단계 위의 **Narrative Mining Engine** —
> [NARRATIVE_OPPORTUNITIES.md](NARRATIVE_OPPORTUNITIES.md) +
> [narrative_mining_console.html](narrative_mining_console.html).
> 이 brief는 narrative mining의 *입력 surface*다. 둘 다 자체적으로 portfolio
> 자료로 유효함.

> **For external readers**. This is a curated, abridged version of the full
> Observer Brief at [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md).
> Two candidates are shown; the full run produced five `story_ready` candidates.

---

## What this is

WITNESS is a multi-agent simulation observer. Given a 200-tick run of a
12-agent / 3-group scenario, it:

1. Detects event candidates from world-state changes (signals + lens scoring).
2. Classifies each candidate's confidence and relevance.
3. Emits a **structured text report** — *this document* — with per-block
   provenance: which fields are direct simulation readouts, which are
   bounded interpretations, which are not used.

Every claim below traces to a single observer field or a reproducible
scoring rule. There is no narrative voice; there is no hand-authored
visualization.

---

## Run context

| Field | Value |
|---|---|
| Run | `peter_scarcity_baseline` |
| Ticks | 200 |
| Agents | 12 (in 3 groups: L1, L2, L3) |
| Seed | 0 (deterministic) |
| Candidates surfaced | 8 total — 5 `story_ready`, 3 `low_activity_hold` |
| Source | [`data/visual/dot_observer_data.json`](../../data/visual/dot_observer_data.json) |

---

## Candidate sample 1 — `C01_t15` (authority pressure)

**One-line**: A `story_ready` candidate at tick 15, surfaced via three
co-occurring signals: `authority_vigilance_spike`, `cohort_split`,
`agent_state_shift`. Strongest lens: `person`. Salience score: 3.

### Source-derived (raw observer fields at tick 15)

- **World**: `crowd_mood: agitated`, `authority_vigilance: 0.250`,
  `blame_concentration: 0.280`, `public_suspicion: 0.150`.
- **Groups**: L1 transitioned to `partial` mode with tension `0.539`;
  L2 and L3 remain `low_activity` at tension `0.100`.
- **Active events**: `guard_approaches`, `discussion_emitted`,
  `public_denial`, `visible_withdrawal` (and a second `discussion_emitted`).
- **Focal agents** (sample): `agent_03` (state `fragmenting`, fear 8.73),
  `agent_05` (state `fragmenting`, fear ~9.0).
  These two are the cohort-split focal agents; the other 10 agents remain
  `calm`.

### Source-inferred (system interpretation rules)

- **Rationale**: "Surfaced by authority_vigilance_spike, cohort_split,
  agent_state_shift." (verbatim system output)
- **Strongest lens**: `person`. The lens scorer assigned the highest
  weight to per-agent state changes over group or world dynamics.
- **Dominant pressure**: `none_clear`. No single pressure type dominates
  the signal mix at this tick.

### Why this matters

The candidate marks the simulation's first cohort-split moment under
authority pressure — a specific configuration of three co-firing signals
that the observer policy treats as a `story_ready` candidate.

### Provenance audit

- Every world / group / agent value above is a direct observer-state
  readout at tick 15.
- The `rationale` / `strongest_lens` / `dominant_pressure` / `salience`
  fields are reproducible scoring rule outputs over the source signals.
- No visual staging fields (positions for cutscene, walking frames,
  speech bubbles) are used.

---

## Candidate sample 2 — `C02_t25` (saturation split)

**One-line**: `story_ready` at tick 25, salience 3, strongest lens
`person`. Eight active events span the window: `public_confession`,
`forgiveness_emitted`, `visible_grief` (×2), `public_denial`,
`discussion_emitted`, plus two more.

### Source-derived

- **World**: `crowd_mood` continues `agitated`; `blame_concentration`
  trending higher.
- **Groups**: L1 still in `partial`; L2/L3 still `low_activity`.
- **Focal agents**: a wider spread now — multiple agents have shifted to
  `tense` or `fragmenting` since C01.
- **Active events** include both confession-class events
  (`public_confession`, `forgiveness_emitted`) and grief-class events
  (`visible_grief` ×2). The simulation has produced a moment with
  competing emotional dynamics in the same tick window.

### Source-inferred

- Rationale: surfaced by signals describing rising tension distribution
  combined with focused emotional events on specific agents.
- The candidate is a *saturation* event: many low-level signals
  combining into a high-salience moment, rather than a single sharp
  spike.

### Provenance audit

Same vocabulary as C01: every world/group/agent block is direct readout;
rationale and lens are scoring outputs; visual staging excluded.

---

## What the full brief includes (and this sample omits)

The full brief at `docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md`
adds:

- 3 more `story_ready` candidates (`P03_t66_agent_08`, `C03_t142`,
  `C05_t147`) with the same level of evidence detail.
- A cross-candidate provenance table (one row per candidate, showing
  source-derived vs source-inferred field counts).
- An Observer Judgment section explaining the threshold rules.
- A Limitations section listing what the brief explicitly cannot claim.
- A pointer to the [Phase 12 Provenance Table](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)
  with **160 field-row** ledger across all candidates (59.4% source_derived,
  25.0% source_inferred, 15.6% not_used / visual-only).

---

## Honesty disclosures

- **State labels** (`calm`, `agitated`, `tense`, `fragmenting`,
  `withdrawn`) are dominant-state classifiers in the engine, not
  psychological assertions about the agent. They reflect the engine's
  internal classifier, which is itself a scoring rule, not ground truth.
- **`use_mode: story_ready`** does not mean "this is a story". It means
  the curation policy is willing to surface this candidate in a brief.
  Curation thresholds are configurable.
- **No visual** of any kind is rendered in the brief. An earlier visual
  track existed and is now [frozen](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
  because its audit found 27.9% staged-only content (PEP / VT-B). The
  audit method that surfaced that figure is what now scores this brief.

---

## Cross-reference

- **Full brief**: [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- **Field-level provenance**: [docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)
- **Case study**: [WITNESS_CASE_STUDY_TEXT_FIRST.md](WITNESS_CASE_STUDY_TEXT_FIRST.md)
- **Visual experiment appendix**: [WITNESS_VISUAL_EXPERIMENT_APPENDIX.md](WITNESS_VISUAL_EXPERIMENT_APPENDIX.md)
- **Builder source**: [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
