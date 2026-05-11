# WITNESS — Visual Experiment Appendix

> **2026-05-06 update**: 이 appendix는 *visual freeze 시점의 기록*이다. 그
> freeze 결정 자체가 다음 layer로 이어졌다 — **Narrative Mining Engine**
> ([NARRATIVE_OPPORTUNITIES.md](NARRATIVE_OPPORTUNITIES.md) + [console](narrative_mining_console.html)).
> Visual에서 발명된 audit instrument (provenance class)가 narrative mining의
> 모든 출력에도 그대로 적용된다.

> **For external readers**. This appendix narrates the visual track that
> WITNESS attempted before pivoting to text-first. The track is preserved
> as an experiment record, not as the project's main artifact. The freeze
> decision is in [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md).

---

## Why this appendix exists

The visual track produced no shipping deliverable. It produced something
arguably more transferable: an **audit methodology** that now backs the
project's text-first brief.

This appendix:

1. Lists the five visual sub-tracks attempted, in chronological order.
2. Identifies what each attempt failed at, *specifically* (not "it was
   ugly" — the actual failure mode).
3. Names the artifact that survived — the provenance class vocabulary —
   and points to where it now lives.

This is a *write-up of an honest negative result*, not a postmortem of a
disaster. The pivot was driven by a measurement, not by frustration.

---

## Track-by-track

### 1. Pixel World Static (S1, S2)

**Goal**: Render the engine's world state as a 25×16 tile grid with 12
agent sprites and 3 zone walls, so a viewer could "see" the simulation
at a glance.

**Result**: PW-S1-B (test grid) → PW-S2-C (still dashboard after
vocabulary patch).

**Failure mode**: Adding more *vocabulary* (sprite variants, prop tiles,
zone-color floors, soft walls) did not fix the *composition* problem.
Viewers read the screen as a debug dashboard, not as a populated world.

**Lesson kept**: L46 — vocabulary patches do not fix composition gaps.
Composition is about sight lines, character placement, distance
relationships, and event prominence. Asset polish can't substitute.

### 2. Pixel Scene Director Static (PSD)

**Goal**: Insert a *Director* layer between the observer and the viewer.
Translate per-tick observer state into focal agents, role assignments,
layout, action beats, and visual cues. Render *one well-composed scene*
per candidate, not a populated world.

**Result**: PW-SC-B. Better than the pixel world (the scene was
recognizable as a scene). But the medium itself — a static image — could
not communicate the *flow* between scenes.

**Failure mode**: A static frame conveys position; it cannot convey the
sequence by which agents arrived at that position, or the chain of
reactions that follows. Static media is a wrong medium for emergent
dynamics.

**Lesson kept**: L47 — observer→viewer needs a Director translation
layer; L49 — medium pivot. *Cutscene* is a more appropriate medium than
static for emergent dynamics; *text* is most appropriate of all.

### 3. Pixel Event Playback (PEP)

**Goal**: Animated cutscenes — 10–12 second windows where agent sprites
walk, face, speak, emote, change pose. Implemented as a hand-authored
timeline per candidate, with crowd reaction frames.

**Result**: VT-B (Visual Traceability), 72.1% source-backed / **27.9%
staged-only**. The PEP cutscenes communicated more interaction than any
static could. But the audit revealed that more than a quarter of the
visible content was hand-authored timeline staging — not directly
derived from the engine state.

**Failure mode**: To produce a *legible* cutscene, the timeline had to
fill in gaps the engine doesn't expose: walking direction, speech
timing, crowd reaction order. Each fill-in is interpretation. Each
interpretation passes a tipping point where the visual is no longer
describing the simulation; it's describing the designer's reading of it.

**Lesson kept**: L48 — visual cues should be *shadows of action* (cause →
effect), not floating icons; L52 — the real visual problem is provenance
gap, not aesthetic gap.

### 4. World Flow Observer (WFO v0)

**Goal**: A *data-first* IR — `world_flow_events_v1` — that emits visual
actions only when they can be derived from observer per-tick deltas or
from bounded inference rules. Hard ban on hand-staging.

**Result**: WFO-A. **100% source-backed**, 0% staged. The IR shipped as
JSON; the audit confirmed zero hand-authored content.

**Failure mode**: None at the data layer. The audit was clean.

**Lesson kept**: L53 — data-first IR beats UI-first cutscene at staging
ratio reduction. *Designing the IR for honesty* removes the polish
temptation that produced PEP's 27.9%.

### 5. WFO Polished Viewer (v1)

**Goal**: Render the WFO IR as a 200-tick continuous-flow viewer with
state cross-fade, group breathing, mood tint, and an 8-glyph emote
vocabulary. Quiet observation tone. 60-second default playback.

**Result**: Built. Verified 0 staged actions, all source-backed.

**Failure mode**: 5-second usability test fail. The reviewer's verbatim
reaction: *"a few dots moving around but I cannot tell what is
happening."* The polished viewer subtracted so aggressively in pursuit
of "quiet tone" that the simulation's behavior was no longer perceptible.

**Lesson kept**: L54 — polish must flow data → presentation, never the
reverse. Subtle ≠ legible. A viewer that hides its own signal in service
of tone fails its first job.

---

## What survived the freeze

### The audit vocabulary

The provenance class vocabulary used to score visual fields —
`source_derived`, `source_inferred`, `staged_only` — was *invented*
during the visual track. PEP's audit produced **WVT-B (72.1% / 27.9%)**;
WFO's audit produced **WFO-A (100% / 0%)**.

The same vocabulary now stamps every block of the text-first brief:

```
visual track          →  text-first brief
-------------------       --------------------
source_derived            source_derived
source_inferred           source_inferred
staged_only               not_used   (renamed: visual-only fields are
                                       explicitly excluded, not staged)
```

### The audit script

`scripts/visual/audit_world_flow_traceability.py` runs against any
WFO-format IR and produces a Markdown audit report. The script was the
instrument that forced the staged-only number to be measurable rather
than aesthetic.

### The traceability standard

A specific decision rule emerged from the audit:

> *No surface ships unless its source-backed ratio is ≥ 80% and its
> hand-authored ratio is ≤ 20%. The text-first brief targets ≥ 95% / ≤ 5%
> on the same vocabulary.*

This is now the project's release gate.

---

## Why the pivot is not retreat

A simpler narrative would be: *"I tried five visual approaches; they all
failed; I gave up and wrote text instead."*

The actual story is different:

1. The visual track produced a tool that scores honesty.
2. The tool revealed that the engine wasn't yet emitting a visual-ready
   event log.
3. Scoring the candidate text representations with the same tool showed
   that the text could be ≥95% source-backed *without staging* — because
   text doesn't need sub-tick action granularity to be legible.
4. The right surface for the project's current engine state is text.
   Visual returns when (and only when) the engine emits a true event log.

The pivot was therefore *driven by the audit vocabulary the visual track
itself produced*. That is a much stronger portfolio claim than either a
shipped visual or a quiet retreat: the project produced an instrument
that decided its own deliverable.

---

## Files by status

### Frozen (do not modify)

- [visual/pixel_world_static.html](../../visual/pixel_world_static.html) — PW-S2-C
- [visual/pixel_scene.html](../../visual/pixel_scene.html) — PW-SC-B
- [visual/pixel_event_playback.html](../../visual/pixel_event_playback.html) — VT-B
- [visual/world_flow_observer.html](../../visual/world_flow_observer.html) — freeze v1

### Active (audit / regression)

- [scripts/visual/audit_world_flow_traceability.py](../../scripts/visual/audit_world_flow_traceability.py) — instrument
- [tests/test_visual/](../../tests/test_visual/) — 72 tests (regression guard, do not extend)

### Active (text-first, derives from this experience)

- [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
- [scripts/report/build_provenance_table.py](../../scripts/report/build_provenance_table.py)
- [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- [docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)
- [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)

---

## Cross-reference

- Full freeze decision: [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
- Lessons cluster (visual track): [lessons.md L46–L55](../../lessons.md)
- Audit reports: [docs/visual/VISUAL_TRACEABILITY_AUDIT.md](../visual/VISUAL_TRACEABILITY_AUDIT.md), [docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md](../visual/WORLD_FLOW_TRACEABILITY_AUDIT.md)
- Project reset plan: [docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](../WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)
