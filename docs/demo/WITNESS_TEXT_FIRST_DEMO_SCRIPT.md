# WITNESS — Text-first 5-minute Demo Script

**Audience**: AI product / simulation / agent-system role interviews; portfolio reviews.
**Length**: 5 minutes verbal, ~3 minutes if hands-on.
**Goal**: Convey that WITNESS is *an observer system that detects event candidates from a multi-agent world and produces evidence-backed reports with provenance* — not a story generator, not a pixel game.

> Use this script alongside [WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md) on screen. Walk through the brief; do not improvise.

---

## 0:00 — 0:30 — One-line frame

> "WITNESS is an observer system for simulated multi-agent worlds. Given a
> simulation run, it detects meaningful event candidates and produces
> evidence-backed reports with explicit provenance — what was directly
> observed versus what the system interpreted."

Show the brief title on screen: `WITNESS Observer Brief — peter_scarcity_baseline`.

**Anchor message** (first impression): traceability is the product.

---

## 0:30 — 1:30 — Pipeline in one breath

> "There are three layers under the hood, but the user-facing artifact is
> just this report. The pipeline is:"

```
Simulated world
  ↓ (engine)
Agent / Group / Event / State changes per tick
  ↓ (observer)
Candidate extraction + signal/lens scoring
  ↓ (curation)
Evidence-backed Observer Brief
```

Point at section §2 of the brief — *Run Context* — to ground this in real fields:
- 200 ticks, 12 agents, 3 groups, seed 0
- 8 candidates surfaced, 5 of them `story_ready`

> "Every claim downstream traces back to one of these run-level facts."

---

## 1:30 — 3:00 — The candidate card walkthrough

Open §4 of the brief — `C01_t15 — tick 15`.

> "This is what the system surfaced at tick 15. Let me show you why I trust
> this candidate."

Walk through, in order:

1. **Active events at tick** (source-derived):
   `guard_approaches`, `discussion_emitted`, `public_denial`, `visible_withdrawal`
   > "These are direct readouts from the simulation. The engine fired these.
   > I am not paraphrasing."

2. **World snapshot** (source-derived):
   `crowd_mood: agitated`, `authority_vigilance: 0.250`
   > "Same — direct field readouts."

3. **Group state** — L1 transitioning to `partial`, tension 0.579 vs 0.100 elsewhere
   > "Mode and tension are observer fields. The system did not invent this."

4. **Why story_ready** (source-inferred):
   `Surfaced by authority_vigilance_spike, cohort_split, agent_state_shift`
   > "This is *interpretation*. Three signals exceeded their thresholds. The
   > rule is reproducible from the same observer data — but it is the system
   > making a judgment, not raw fact. The provenance section flags this."

5. **Provenance** block at the bottom:
   > "Source-derived, source-inferred, not used. The reader can audit which
   > kind of claim each line is."

---

## 3:00 — 4:00 — The visual pivot story

Open §7 of the brief — *Visual Experiment Note*.

> "I originally tried to ship this as a pixel-art viewer. Three sub-tracks
> over five weeks — pixel world, scene director, event playback, and a
> world-flow viewer."

> "The traceability audit caught a problem before I shipped: the cutscene
> playback was 27.9% staged-only — meaning that more than a quarter of what
> the user would have seen was hand-authored, not engine-derived. So I built
> a stricter audit, drove that ratio to zero, and shipped a 100%
> source-backed long-form viewer."

> "But that viewer failed a 5-second usability test — *'a few dots moving
> around but I cannot tell what is happening.'* The medium itself wasn't
> ready: the engine doesn't yet emit a visual-ready event log."

> "So the deliverable became this report instead."

Show [VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
briefly — tables of per-track verdicts. Don't read it; just establish that
the decision is documented.

**Anchor message** (the punchline): *I would rather ship a true text artifact
than a polished but partially fabricated visual.*

---

## 4:00 — 4:30 — The system-level claim

> "Across the project I learned that the most defensible portfolio asset
> here isn't a polished demo — it's the audit methodology. Every visible
> claim in the brief is one of three classes:
>
> - source-derived (raw observer field at the candidate's tick)
> - source-inferred (bounded rule applied to source signals)
> - not used (visual staging fields explicitly excluded)
>
> The same audit method drove the visual freeze decision. It's transferable
> to any agent / simulation / RAG system that mixes raw output and
> interpretation."

---

## 4:30 — 5:00 — Close + next steps

> "Three things are pending after this brief:
>
> 1. A per-field *Provenance Table* (Phase 12) — finer-grained than the
>    candidate-level table you see in §5.
> 2. A portfolio case study packaging this pivot story for external
>    review (Phase 13).
> 3. An Engine Event Log Adapter (Phase 14, deferred) — the prerequisite
>    for any future visual revival.
>
> The artifact you're looking at is the system's main output as of today."

Close on the brief's **§9 Next Steps** block, on screen.

---

## Backup slides (if asked)

- *"Show me the code that produces the brief"* → [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
- *"Show me the audit"* → [docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md](../visual/WORLD_FLOW_TRACEABILITY_AUDIT.md)
- *"Show me the visual experiment"* → [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
- *"Show me the engine"* → [DESIGN.md §4 (engine architecture)](../../DESIGN.md), then `engine/person/`, `engine/world/` highlights
- *"How many tests?"* → 2,026 engine fast suite + 72 visual + 19 brief + 18 narrative tests

---

## What NOT to say

The following framings are *out of scope* for this demo and explicitly
contradict the project reset plan. Avoid them:

- "WITNESS is a story generator." (no — it is an observer system)
- "The visual experiment was a failure." (no — it produced an audit
  methodology and a freeze decision; that *is* a deliverable)
- "I want to ship the pixel-art version next." (no — Phase 14 is deferred
  until the engine event log exists)
- "This is a portfolio about pivoting away from a doomed feature."
  (no — this is a portfolio about *substituting a more defensible artifact*
  on the same value claim)
- "The text brief is just a placeholder until the visual is ready."
  (no — the brief is the system's primary output, full stop)

---

## Pace notes

- Spend the most time on **§3 (1:30–3:00)** — the candidate card walkthrough.
  This is where the audit value is most concretely visible.
- Skim **§4 (3:00–4:00)** — the pivot story is necessary but easy to
  over-narrate. Stay factual.
- The 5-second hook is **§0** + the visible brief title. If the audience is
  hostile-skim, that is what they will remember.

---

*Companion artifacts:*
- *Brief itself*: [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- *Freeze decision*: [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
- *Builder*: [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
- *Plan*: [docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](../WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)
