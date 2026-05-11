# WITNESS Observer Brief — peter_scarcity_baseline

> **System**: WITNESS multi-agent simulation observer — detects event candidates
> from world-state changes and produces evidence-backed reports with provenance.

> **What this brief is**: a textual, source-traceable description of the
> candidates that this run surfaced. Every claim below is either a raw observer
> field or a bounded interpretation rule applied to source signals. There is no
> visual staging, hand-authored cutscene, or narrative embellishment.

---

## 1. Executive Summary

- Run produced **8 candidates** total
  (**5 story_ready**, 3 low_activity_hold).
- This brief covers **5 candidates** matching modes: `story_ready`.
- Strongest individual candidate by salience: `C01_t15`.
- Run-level world mood traces from initial `calm` through `agitated`/`tense` and back, with three notable inflection points around ticks 15, 25, and 142.

---

## 2. Run Context

| Field | Value |
|---|---|
| run_label | `peter_scarcity_baseline` |
| schema_version | `v1` |
| n_ticks | 200 |
| seed | 0 |
| agent_count | 12 |
| group_count | 3 |
| candidate source | `data/visual/dot_observer_data.json` |
| modes included | `story_ready` |
| lens set | person / group / event / world (per candidate `strongest_lens`) |

---

## 3. Timeline of Notable Events

- **t15** — `C01_t15` (lens `person`, salience 3): `guard_approaches`, `discussion_emitted`, `public_denial`, `visible_withdrawal`, `discussion_emitted`
- **t25** — `C02_t25` (lens `person`, salience 3): `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `visible_withdrawal`, `visible_withdrawal`, `public_denial`, `discussion_emitted`
- **t66** — `P03_t66_agent_08` (lens `person`, salience 2): `visible_grief`, `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `discussion_emitted`
- **t142** — `C03_t142` (lens `person`, salience 3): `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `visible_grief`, `visible_grief`, `public_denial`, `visible_grief`
- **t147** — `C05_t147` (lens `person`, salience 3): `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `visible_grief`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`

---

## 4. Candidate Cards

### C01_t15 — tick 15 (range 13–17)

**One-line**: `story_ready` candidate surfaced via `authority_vigilance_spike`, `cohort_split`, `agent_state_shift` on lens `person` (salience 3).

**What happened (source-derived)**
- 12 agents in scope at tick 15
- Active events: `guard_approaches`, `discussion_emitted`, `public_denial`, `visible_withdrawal`, `discussion_emitted`
- World mood across window: `agitated` → `agitated` → `agitated` → `agitated` → `agitated`

**World snapshot at tick**
- crowd_mood: **agitated**
- blame_concentration: 0.280
- public_suspicion: 0.150
- authority_vigilance: 0.250

**Group state at tick**
| group | mode | tension | members |
|---|---|---|---|
| L2 | low_activity | 0.100 | 4 |
| L3 | low_activity | 0.100 | 4 |
| L1 | partial | 0.539 | 4 |

**Focal agent state at tick**
| agent | group | state | fear | hope | salient |
|---|---|---|---|---|---|
| agent_01 | L2 | calm | 1.30 | 4.00 | · |
| agent_02 | L3 | calm | 1.30 | 4.00 | · |
| agent_03 | L1 | fragmenting | 8.73 | 4.00 | ★ |
| agent_04 | L2 | calm | 1.30 | 4.00 | · |
| agent_05 | L3 | fragmenting | 8.30 | 4.00 | ★ |
| agent_06 | L1 | calm | 1.30 | 4.00 | · |

_(+6 more agents — full list in candidate metadata)_

**Why story_ready (source-inferred)**
- Rationale: Surfaced by authority_vigilance_spike, cohort_split, agent_state_shift
- Strongest lens: `person` (candidate_type `person`)
- Dominant pressure: `none_clear`
- Salience score: 3

**Provenance**
- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, world / group / agent state at the candidate tick (raw observer fields)
- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, `salience_score`, `dominant_pressure`, `use_mode` (interpretation rules over the source signals — bounded but not raw)
- Not used: _synthetic guard movement_, _tile-grid positions_, _walking-frame timeline_, _hand-authored cutscene cues_, _speech-bubble staging_

**Caveat**: this card describes a candidate as observed by the system. It is not a finished narrative. State labels (`calm`, `agitated`, etc.) are dominant-state classifiers, not psychological claims about the agent.

---

### C02_t25 — tick 25 (range 23–27)

**One-line**: `story_ready` candidate surfaced via `cohort_split`, `saturation_lock`, `agent_state_shift` on lens `person` (salience 3).

**What happened (source-derived)**
- 12 agents in scope at tick 25
- Active events: `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `visible_withdrawal`, `visible_withdrawal`, `public_denial`, `discussion_emitted`
- World mood across window: `agitated` → `calm` → `calm` → `calm` → `calm`

**World snapshot at tick**
- crowd_mood: **calm**
- blame_concentration: 0.030
- public_suspicion: 0.015
- authority_vigilance: 0.250

**Group state at tick**
| group | mode | tension | members |
|---|---|---|---|
| L2 | low_activity | 0.089 | 4 |
| L3 | low_activity | 0.040 | 4 |
| L1 | saturation | 0.748 | 4 |

**Focal agent state at tick**
| agent | group | state | fear | hope | salient |
|---|---|---|---|---|---|
| agent_01 | L2 | calm | 0.50 | 4.00 | · |
| agent_02 | L3 | calm | 0.50 | 4.00 | · |
| agent_03 | L1 | fragmenting | 9.09 | 4.00 | ★ |
| agent_04 | L2 | calm | 0.00 | 4.00 | · |
| agent_05 | L3 | fragmenting | 9.09 | 4.00 | ★ |
| agent_06 | L1 | calm | 0.50 | 4.00 | · |

_(+6 more agents — full list in candidate metadata)_

**Why story_ready (source-inferred)**
- Rationale: Surfaced by cohort_split, saturation_lock, agent_state_shift
- Strongest lens: `person` (candidate_type `person`)
- Dominant pressure: `none_clear`
- Salience score: 3

**Provenance**
- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, world / group / agent state at the candidate tick (raw observer fields)
- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, `salience_score`, `dominant_pressure`, `use_mode` (interpretation rules over the source signals — bounded but not raw)
- Not used: _synthetic guard movement_, _tile-grid positions_, _walking-frame timeline_, _hand-authored cutscene cues_, _speech-bubble staging_

**Caveat**: this card describes a candidate as observed by the system. It is not a finished narrative. State labels (`calm`, `agitated`, etc.) are dominant-state classifiers, not psychological claims about the agent.

---

### P03_t66_agent_08 — tick 66 (range 64–68)

**One-line**: `story_ready` candidate surfaced via `cohort_split`, `agent_state_shift` on lens `person` (salience 2).

**What happened (source-derived)**
- 1 agents in scope at tick 66
- Active events: `visible_grief`, `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `discussion_emitted`
- World mood across window: `calm` → `calm` → `calm` → `tense` → `calm`

**World snapshot at tick**
- crowd_mood: **calm**
- blame_concentration: 0.000
- public_suspicion: 0.000
- authority_vigilance: 0.250

**Group state at tick**
| group | mode | tension | members |
|---|---|---|---|
| L2 | low_activity | 0.075 | 4 |
| L3 | low_activity | 0.000 | 4 |
| L1 | partial | 0.545 | 4 |

**Focal agent state at tick**
| agent | group | state | fear | hope | salient |
|---|---|---|---|---|---|
| agent_08 | L3 | agitated | 7.15 | 4.00 | ★ |

**Why story_ready (source-inferred)**
- Rationale: Surfaced by cohort_split, agent_state_shift
- Strongest lens: `person` (candidate_type `person`)
- Dominant pressure: `none_clear`
- Salience score: 2

**Provenance**
- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, world / group / agent state at the candidate tick (raw observer fields)
- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, `salience_score`, `dominant_pressure`, `use_mode` (interpretation rules over the source signals — bounded but not raw)
- Not used: _synthetic guard movement_, _tile-grid positions_, _walking-frame timeline_, _hand-authored cutscene cues_, _speech-bubble staging_

**Caveat**: this card describes a candidate as observed by the system. It is not a finished narrative. State labels (`calm`, `agitated`, etc.) are dominant-state classifiers, not psychological claims about the agent.

---

### C03_t142 — tick 142 (range 140–144)

**One-line**: `story_ready` candidate surfaced via `cohort_split`, `saturation_lock`, `agent_state_shift` on lens `person` (salience 3).

**What happened (source-derived)**
- 12 agents in scope at tick 142
- Active events: `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `visible_grief`, `visible_grief`, `public_denial`, `visible_grief`
- World mood across window: `agitated` → `agitated` → `tense` → `tense` → `calm`

**World snapshot at tick**
- crowd_mood: **agitated**
- blame_concentration: 0.357
- public_suspicion: 0.150
- authority_vigilance: 0.250

**Group state at tick**
| group | mode | tension | members |
|---|---|---|---|
| L2 | low_activity | 0.075 | 4 |
| L3 | low_activity | 0.000 | 4 |
| L1 | saturation | 0.970 | 4 |

**Focal agent state at tick**
| agent | group | state | fear | hope | salient |
|---|---|---|---|---|---|
| agent_01 | L2 | calm | 0.00 | 4.00 | · |
| agent_02 | L3 | calm | 0.00 | 4.00 | · |
| agent_03 | L1 | fragmenting | 8.99 | 4.00 | ★ |
| agent_04 | L2 | calm | 0.00 | 4.00 | · |
| agent_05 | L3 | fragmenting | 7.98 | 4.00 | ★ |
| agent_06 | L1 | calm | 0.00 | 4.00 | · |

_(+6 more agents — full list in candidate metadata)_

**Why story_ready (source-inferred)**
- Rationale: Surfaced by cohort_split, saturation_lock, agent_state_shift
- Strongest lens: `person` (candidate_type `person`)
- Dominant pressure: `accusation`
- Salience score: 3

**Provenance**
- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, world / group / agent state at the candidate tick (raw observer fields)
- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, `salience_score`, `dominant_pressure`, `use_mode` (interpretation rules over the source signals — bounded but not raw)
- Not used: _synthetic guard movement_, _tile-grid positions_, _walking-frame timeline_, _hand-authored cutscene cues_, _speech-bubble staging_

**Caveat**: this card describes a candidate as observed by the system. It is not a finished narrative. State labels (`calm`, `agitated`, etc.) are dominant-state classifiers, not psychological claims about the agent.

---

### C05_t147 — tick 147 (range 145–149)

**One-line**: `story_ready` candidate surfaced via `cohort_split`, `saturation_lock`, `agent_state_shift` on lens `person` (salience 3).

**What happened (source-derived)**
- 12 agents in scope at tick 147
- Active events: `public_confession`, `forgiveness_emitted`, `discussion_emitted`, `public_confession`, `forgiveness_emitted`, `visible_grief`, `public_confession`, `forgiveness_emitted`, `discussion_emitted`
- World mood across window: `calm` → `calm` → `calm` → `calm` → `calm`

**World snapshot at tick**
- crowd_mood: **calm**
- blame_concentration: 0.000
- public_suspicion: 0.000
- authority_vigilance: 0.250

**Group state at tick**
| group | mode | tension | members |
|---|---|---|---|
| L2 | low_activity | 0.075 | 4 |
| L3 | low_activity | 0.000 | 4 |
| L1 | saturation | 0.794 | 4 |

**Focal agent state at tick**
| agent | group | state | fear | hope | salient |
|---|---|---|---|---|---|
| agent_01 | L2 | calm | 0.00 | 4.00 | · |
| agent_02 | L3 | calm | 0.00 | 4.00 | · |
| agent_03 | L1 | fragmenting | 7.74 | 4.00 | ★ |
| agent_04 | L2 | calm | 0.00 | 4.00 | · |
| agent_05 | L3 | fragmenting | 6.73 | 4.00 | ★ |
| agent_06 | L1 | calm | 0.00 | 4.00 | · |

_(+6 more agents — full list in candidate metadata)_

**Why story_ready (source-inferred)**
- Rationale: Surfaced by cohort_split, saturation_lock, agent_state_shift
- Strongest lens: `person` (candidate_type `person`)
- Dominant pressure: `none_clear`
- Salience score: 3

**Provenance**
- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, world / group / agent state at the candidate tick (raw observer fields)
- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, `salience_score`, `dominant_pressure`, `use_mode` (interpretation rules over the source signals — bounded but not raw)
- Not used: _synthetic guard movement_, _tile-grid positions_, _walking-frame timeline_, _hand-authored cutscene cues_, _speech-bubble staging_

**Caveat**: this card describes a candidate as observed by the system. It is not a finished narrative. State labels (`calm`, `agitated`, etc.) are dominant-state classifiers, not psychological claims about the agent.

---

## 5. Provenance Table

| Candidate | Tick | Use mode | Lens | Agents | Events | Source-derived | Source-inferred |
|---|---|---|---|---|---|---|---|
| `C01_t15` | 15 | `story_ready` | `person` | 12 | 5 | world+group+agents at t15 | `authority_vigilance_spike`, `cohort_split`, `agent_state_shift` |
| `C02_t25` | 25 | `story_ready` | `person` | 12 | 8 | world+group+agents at t25 | `cohort_split`, `saturation_lock`, `agent_state_shift` |
| `P03_t66_agent_08` | 66 | `story_ready` | `person` | 1 | 6 | world+group+agents at t66 | `cohort_split`, `agent_state_shift` |
| `C03_t142` | 142 | `story_ready` | `person` | 12 | 7 | world+group+agents at t142 | `cohort_split`, `saturation_lock`, `agent_state_shift` |
| `C05_t147` | 147 | `story_ready` | `person` | 12 | 9 | world+group+agents at t147 | `cohort_split`, `saturation_lock`, `agent_state_shift` |

**Reading the table**:
- *Source-derived* lists raw observer fields used at the candidate's tick — these
  are not interpretations; they are direct readouts of simulation state.
- *Source-inferred* lists fields produced by bounded rules over source signals
  (signal detection, lens scoring, salience). These are reproducible from the
  same observer data but represent system-level interpretation.
- Fields not listed (e.g. visual staging, cutscene staging, tile coordinates)
  are intentionally **not used** in this brief.

---

## 6. Observer Judgment

- The system classifies a candidate as `story_ready` when one or more
  signals exceed their lens-specific threshold within a tick window
  AND the dominant_pressure is non-trivial AND salience_score ≥ 2.
- `low_activity_hold` candidates are recorded for completeness but are
  not promoted to the brief body unless explicitly requested.
- The strongest lens per candidate is selected by signal weight, not by
  narrative preference.

---

## 7. Visual Experiment Note

WITNESS originally explored pixel-based visualizations
(Pixel World Static → Pixel Scene Director → Pixel Event Playback →
World Flow Observer). The traceability audit (WVT) showed that visual
playback contained **27.9% staged-only** elements (hand-authored cutscene
staging that was not directly source-derived). A subsequent World Flow
Observer (WFO) achieved **100% source-backed** but the resulting viewer
proved hard to read at the 5-second test on its own.

The decision was therefore to:

- **Freeze** the visual track (PSD / PEP / WFO) as an experiment record,
  not as the portfolio's main artifact.
- **Pivot to text-first Observer Brief** — this document — which preserves
  source traceability without depending on visual presentation literacy.

See `docs/visual/VISUAL_TRACK_FREEZE_DECISION.md` for the full freeze
rationale and per-track verdict.

---

## 8. Limitations

- The engine does not yet emit a *visual-ready* event log; per-agent action
  granularity below the tick level is unavailable. Visual playback that
  attempts this will need an Engine Event Log Adapter first.
- Candidate selection thresholds are fixed for this run; sensitivity to
  threshold choice has not been swept here (Phase 12 scope).
- Provenance class assignment is field-level, not value-level: a single
  field's content may be partially raw and partially smoothed by the engine.
- The brief depends on `data/visual/dot_observer_data.json`. If the schema
  version changes, the builder must be re-validated.

---

## 9. Next Steps

1. **Phase 12** — Provenance Table strengthening (per-field source ledger).
2. **Phase 13** — Portfolio Package v1 (case study + 5-min demo + resume bullets).
3. **Phase 14** (deferred) — Engine Event Log Adapter design notes for any
   future visual revival.

---

*Generated by* `scripts/report/build_observer_brief.py` *from* `peter_scarcity_baseline` *observer data.*
