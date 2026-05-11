# WITNESS — Case Study (Text-first Pivot)

> **Update (2026-05-06 후속)**: 이 케이스 스터디는 *text-first pivot 시점의 기록*이다.
> 현재 메인 deliverable은 한 단계 더 진화한 **Narrative Mining Engine**:
> [docs/portfolio/NARRATIVE_OPPORTUNITIES.md](NARRATIVE_OPPORTUNITIES.md) +
> [narrative_mining_console.html](narrative_mining_console.html). Text-first brief는
> narrative mining의 *입력 surface*로 통합됐다. 자세한 trajectory:
> [WITNESS_NARRATIVE_MINING_PLAN.md](../WITNESS_NARRATIVE_MINING_PLAN.md).

**One-line**: A multi-agent simulation observer that *audits its own output*
and substituted a polished but partially fabricated visual deliverable with
an evidence-backed text brief — which then became the input layer for a
Narrative Mining Engine that surfaces multiple story threads from a single run.

**Status**: Phase 11–13 (text-first pivot) shipped; Narrative Mining Engine Phase 1–5 shipped.
**Date**: 2026-05-06

---

## 1. Problem

Multi-agent simulations of human social behavior produce a flood of
per-tick state — agent emotion vectors, group modes, world-level pressure
fields, discrete events. Most consumers of this output (researchers,
product reviewers, portfolio readers) cannot read tick-level data directly.
The natural impulse is to render it visually.

**The trap**: any visual representation that looks like *people doing
things in a place* requires more granularity than the engine actually
emits — sub-tick movement, target attention, walking direction, speech
timing. Producing those visuals at all means *staging* them by hand. Which
means the visual no longer represents the simulation; it represents the
designer's interpretation of what the simulation should look like.

This case study describes how that trap was identified, measured, and
exited — and what shipped instead.

---

## 2. System Architecture

WITNESS has four layers; the project reset froze layer 4 and made layer 3
the user-facing surface.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Visual (frozen)                                    │
│  pixel world / scene director / event playback / world flow │
│  — preserved as experiment record only                      │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Reporting (active)                  ← user-facing  │
│  Observer Brief / Provenance Table / Demo / Case Study      │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Observation (active)                               │
│  candidate extraction / signal-lens scoring / curation      │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Engine (active)                                    │
│  agent dynamics / group state / world pressure / events     │
└─────────────────────────────────────────────────────────────┘
```

**Layer 1 — Engine.** Tick-stepped multi-agent simulation. ~12 agents in
3 groups under a configurable scarcity / authority pressure scenario.
2,026 engine fast tests passing; behavior is deterministic per seed.

**Layer 2 — Observation.** A non-evaluating observer reads each tick and
produces candidates: tick range, agents involved, active events, signals
that crossed thresholds, lens classification (person / group / event /
world), salience score. The observer is *additive* — it never modifies
engine output, only labels it.

**Layer 3 — Reporting (this layer is the deliverable).** The Observer
Brief renders candidates as Markdown cards with a per-field provenance
class:

- `source_derived` — raw observer field at the candidate's tick.
- `source_inferred` — bounded rule applied to source signals.
- `not_used` — visual staging fields explicitly excluded.

**Layer 4 — Visual (frozen).** Five sub-tracks attempted; all frozen.
See [VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md).

---

## 3. The Observer Layer (substance)

The observer is what the project actually built well. Its job:

1. Read the engine's per-tick state.
2. Detect signals (e.g. `authority_vigilance_spike`, `cohort_split`,
   `agent_state_shift`) by comparing fields against thresholds and deltas.
3. Group adjacent signal-rich ticks into a **candidate** with a
   `tick_range` and the agents/events involved.
4. Score the candidate by lens (which lens explains the most variance:
   the agent's psychology, the group's dynamics, the discrete event,
   or the world-level pressure?).
5. Classify use mode: `story_ready` (system willing to talk about it),
   `observation_only`, or `low_activity_hold` (recorded but suppressed).

For the `peter_scarcity_baseline` run (200 ticks, seed 0):

| | count |
|---|---|
| total candidates | 8 |
| `story_ready` | 5 |
| `low_activity_hold` | 3 |

Three of the `story_ready` candidates anchor the brief: **C01_t15**
(authority pressure), **C02_t25** (saturation split), **C03_t142**
(confession cluster). Two more (`P03_t66_agent_08`, `C05_t147`) are
included as additional evidence.

---

## 4. Candidate Extraction (the audit-ready part)

For each candidate, the brief reports:

| Block | Provenance class | Source |
|---|---|---|
| `tick`, `tick_range` | source_derived | observer.candidates[i] |
| `agents_involved`, `events_involved` | source_derived | observer.candidates[i] |
| World snapshot at tick | source_derived | observer.ticks[t].world |
| Group state at tick | source_derived | observer.ticks[t].groups |
| Focal agent state at tick | source_derived | observer.ticks[t].agents |
| Active events at tick | source_derived | observer.ticks[t].active_events |
| Mood across tick range | source_derived | observer.ticks[lo..hi].world.crowd_mood |
| `rationale`, `signals`, `strongest_lens` | source_inferred | observer scoring rules |
| `salience_score`, `dominant_pressure` | source_inferred | observer scoring rules |
| `use_mode` | source_inferred | curation thresholds |
| Visual staging (positions, walking frames) | **not_used** | (explicitly excluded) |

The reader can audit any single line of the brief by tracing it to one of
those sources.

---

## 5. Evidence-backed Brief (the deliverable)

[`docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md`](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)

Key properties:

- **Generated**, not hand-written. The builder is
  [`scripts/report/build_observer_brief.py`](../../scripts/report/build_observer_brief.py).
  Re-running it on a different observer dump produces an analogous brief.
- **Fields, not prose.** The brief is structured tables and short
  declarative sentences. There is no narrative voice claiming what
  characters "felt".
- **Provenance per block.** Each candidate card ends with a `Provenance`
  block listing which fields are source-derived, which are source-inferred,
  and which are not used.
- **Explicit limitations.** Section 8 of the brief lists what the brief
  cannot claim — sub-tick action granularity, threshold sensitivity sweep,
  value-level provenance.

**This is what gets shown in the 5-minute demo.** Not a viewer.

---

## 6. The Visual Pivot — what was learned

### 6.1 The five tracks

| Track | Verdict | Insight kept |
|---|---|---|
| Pixel World Static (S1) | PW-S1-B (test grid) | Vocabulary alone doesn't fix composition — L46 |
| Pixel World Static (S2 patch) | PW-S2-C (still dashboard) | Same lesson, second confirmation |
| Pixel Scene Director Static | PW-SC-B (static medium ceiling) | A "Director" translation layer is needed between observer and viewer — L47 |
| Pixel Event Playback | VT-B (72.1% / 27.9% staged) | Cutscenes communicate interaction better than statics, but cost staging budget |
| World Flow Observer (WFO v0) | WFO-A (100% source-backed, viewer-less) | Data-first IR can hit zero-staged when designed for it — L53 |
| WFO Polished Viewer (v1) | freeze (5-second test fail) | Polish ≠ subtle. Subtle viewers can hide the very signal they're conveying — L54 |

### 6.2 The audit method (the actual portfolio asset)

The provenance class vocabulary used by the brief — `source_derived` /
`source_inferred` / `staged_only` (visual) / `not_used` (text) — was
*invented* during the visual track to score per-event and per-action
honesty. PEP's audit produced **WVT-B** (72.1% / 27.9%); WFO's audit
produced **WFO-A** (100% / 0%).

That same audit vocabulary is what now stamps every block of the brief.

The visual track did not produce a shipped visual; it produced a measuring
instrument.

### 6.3 The pivot decision

Three converging signals forced the freeze:

1. PEP's 27.9% staged ratio — past the audit's WFO-A threshold.
2. WFO Polished Viewer's 5-second-test fail despite 0% staged.
3. Honest assessment: the engine doesn't yet emit a visual-ready event log,
   and any visual that pretends otherwise is staged by definition.

Rather than ship a polished-but-staged visual, the project owner decided
to ship a structured text brief with the same audit class on every line.

---

## 7. Results

| Surface | Status | Provenance integrity |
|---|---|---|
| Observer Brief (Phase 11) | shipping | Every block class-tagged |
| Visual Track (Phase 4–10) | frozen | Audit reports retained |
| Engine fast suite | 2,026 passing | Deterministic per seed |
| Visual unit tests | 72 passing | Regression guard, not extended |
| Brief builder | runs in <1s | Re-runnable on any observer dump |

---

## 8. Lessons

Concrete lessons from this case study (recorded in [lessons.md](../../lessons.md)):

- **L46** — vocabulary patch ≠ composition fix
- **L47** — observer→viewer needs a translation layer (Director), not direct rendering
- **L48** — visual cues should be *shadows of action*, not floating icons
- **L49** — medium pivot: static images cannot communicate flow regardless of polish
- **L52** — the real visual problem is provenance gap, not aesthetic gap
- **L53** — data-first IR beats UI-first cutscene at staging-ratio reduction
- **L54** — polish must flow data → presentation, never the reverse

These together describe a single trajectory: *what visual could not deliver
is exactly what text-first delivers without effort.*

---

## 9. Next Step

1. **Phase 12** — Per-field provenance table (machine-readable + Markdown).
   The current brief's table is candidate-level; Phase 12 produces a
   row-per-field table with explicit class assignment.
2. **Phase 13** — Portfolio Package v1: this case study + the brief
   + the demo script + resume bullets + interview cards.
3. **Phase 14 (deferred)** — Engine Event Log Adapter design notes.
   This is the prerequisite for any future visual revival.

---

## Cross-reference

- Plan: [docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](../WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)
- Brief: [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- Demo script: [docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md](../demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md)
- Visual freeze: [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
- Audit: [docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md](../visual/WORLD_FLOW_TRACEABILITY_AUDIT.md)
- Builder: [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
