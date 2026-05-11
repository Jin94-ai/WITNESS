# WITNESS — 5-Minute Demo Script (Text-first, Portfolio Variant)

> **2026-05-06 update**: 이 5분 데모는 Reporting Layer (text brief) 중심이다.
> Narrative Mining Engine이 추가된 이후, 5분 데모의 §A frame은 다음 한 줄로
> 갱신해야 한다:
>
> > "WITNESS는 압력 기반 다중 에이전트 시뮬레이션을 구동한 뒤 *여러 서사
> > 후보(Story Thread)를 채굴*하는 시스템이다."
>
> §C 카드 walkthrough 후, [NARRATIVE_OPPORTUNITIES.md](NARRATIVE_OPPORTUNITIES.md)와
> [narrative_mining_console.html](narrative_mining_console.html)을
> 30초 분량으로 추가하면 *brief에서 thread로 이어지는 layer 진화*가 보인다.

> **Use this for portfolio walkthroughs.** A more verbal-delivery-tuned
> variant exists at [docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md](../demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md).
> This portfolio variant assumes the reader is reading silently with
> the artifacts open, not listening to a verbal pitch.

---

## How to use this document

- Open the artifacts referenced in §A–§E in tabs.
- Read the corresponding script section while the reader skims.
- Each section is ≤ 1 minute. Total ≤ 5.
- If you have only 90 seconds: do §A and §C.

---

## §A — The one-line frame (0:00–0:30)

> WITNESS is an observer system for simulated multi-agent worlds. Given a
> simulation run, it detects meaningful event candidates and produces
> evidence-backed reports with explicit provenance — what was directly
> observed versus what the system interpreted.

**Open**: [WITNESS_OBSERVER_BRIEF_SAMPLE.md](WITNESS_OBSERVER_BRIEF_SAMPLE.md)

The reader sees a structured Markdown brief with candidate cards and
provenance blocks. Every fact has a class label.

**Anchor message**: traceability is the product, not story.

---

## §B — The pipeline (0:30–1:30)

> Three layers feed one user-facing artifact:

```
Simulated world
  ↓ (engine — 2,026 fast tests, deterministic per seed)
Per-tick agent / group / event / world state
  ↓ (observer — additive, no engine modification)
Candidates + signals + lens scoring + curation
  ↓
Evidence-backed Observer Brief    ← the deliverable
```

**Open**: [WITNESS_CASE_STUDY_TEXT_FIRST.md §2 System Architecture](WITNESS_CASE_STUDY_TEXT_FIRST.md#2-system-architecture)

The reader sees the four-layer diagram with layer 4 (Visual) marked
*frozen*. This is the moment to mention the pivot:

> The visual layer was attempted and frozen after a traceability audit
> found 27.9% staged-only content. Rest of demo explains how that audit
> became the foundation for the text artifact you're looking at.

---

## §C — The candidate card walkthrough (1:30–3:00)

**Open**: [WITNESS_OBSERVER_BRIEF_SAMPLE.md → Candidate sample 1 (`C01_t15`)](WITNESS_OBSERVER_BRIEF_SAMPLE.md)

Walk the reader through these blocks **in order**:

1. **Active events at tick 15** (source-derived):
   `guard_approaches`, `discussion_emitted`, `public_denial`,
   `visible_withdrawal`. These are direct readouts. The engine fired
   these. Not paraphrased.

2. **World snapshot** (source-derived): `crowd_mood: agitated`,
   `authority_vigilance: 0.250`. Same — direct readouts.

3. **Group state** (source-derived): L1 transitions to `partial`
   mode with tension `0.539`; L2 / L3 stay `low_activity` at `0.100`.
   The cohort split is right there in the data.

4. **Why story_ready** (source-inferred):
   "Surfaced by authority_vigilance_spike, cohort_split,
   agent_state_shift." This is *interpretation*. Three signals exceeded
   thresholds. The rule is reproducible, but it's the system making a
   judgment, not raw fact.

5. **Provenance audit** at the bottom of the card:
   - source-derived
   - source-inferred
   - not used (visual staging fields explicitly excluded)

The reader can audit any line.

---

## §D — The pivot story (3:00–4:00)

**Open**: [WITNESS_VISUAL_EXPERIMENT_APPENDIX.md](WITNESS_VISUAL_EXPERIMENT_APPENDIX.md)

Hit only the table-of-contents level here:

> Five visual sub-tracks attempted. Pixel World, Scene Director, Event
> Playback, World Flow Observer (data IR), and a polished viewer over
> that IR. The audit caught the problem before the visual shipped:
> Event Playback was 27.9% staged-only.

**Pivot punchline**:

> The visual track did not produce a shipping visual. It produced an
> audit instrument. That instrument now scores every block of the text
> brief. The vocabulary you saw in §C — *source_derived /
> source_inferred / not_used* — was invented to score the visual; it
> turned out to score text more usefully than visuals.

---

## §E — The system-level claim + close (4:00–5:00)

**Open**: [WITNESS_CASE_STUDY_TEXT_FIRST.md §6 The Visual Pivot](WITNESS_CASE_STUDY_TEXT_FIRST.md#6-the-visual-pivot--what-was-learned)
or stay on the brief.

> Across the project I learned that the most defensible portfolio asset
> here isn't a polished demo — it's the audit methodology. Every visible
> claim in the brief is one of three classes. The same audit method
> drove the visual freeze decision. It's transferable to any agent /
> simulation / RAG system that mixes raw output and interpretation.

**Three open items** (close with):

1. Per-field provenance ledger — already shipped at
   [WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)
   (160 rows: 59.4% source_derived, 25.0% source_inferred, 15.6%
   not_used).
2. This portfolio package — case study + sample brief + visual appendix
   + resume bullets — *what you are reading now*.
3. Engine Event Log Adapter — the gate for any visual revival; deferred
   until after this portfolio cycle.

**Close**: the artifact you are looking at *is* the system's main output
as of today.

---

## What NOT to say (forbidden framings)

- "WITNESS is a story generator." — wrong, it's an observer system.
- "The visual experiment was a failure." — wrong, it produced an audit
  instrument and a freeze decision; both are deliverables.
- "I want to ship the pixel-art version next." — wrong, deferred until
  the engine emits a true event log.
- "This is a portfolio about pivoting away from a doomed feature." —
  wrong, this is a portfolio about *substituting a more defensible
  artifact on the same value claim*.
- "The text brief is just a placeholder until visual is ready." —
  wrong, the brief is the system's primary output.

---

## Pace notes

| Section | Target time | Where to spend |
|---|---|---|
| §A frame | 0:30 | Don't over-explain. Let the brief speak. |
| §B pipeline | 1:00 | Spend on layer 4 frozen, not layers 1-3 |
| §C card | 1:30 | **Most important**. The audit value is concrete here. |
| §D pivot | 1:00 | Stay factual. Don't over-narrate the visual fail. |
| §E close | 1:00 | The portfolio package is the close, not a teaser. |

If running short, drop §B (pipeline) before §C or §E.

---

## Backup answers (if asked)

- *"How many tests?"* → 2,026 fast suite + 72 visual + 19 report + 18 narrative.
- *"Show me the builder code"* → [scripts/report/build_observer_brief.py](../../scripts/report/build_observer_brief.py)
- *"Show me the audit"* → [docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md](../visual/WORLD_FLOW_TRACEABILITY_AUDIT.md)
- *"Why peter_scarcity?"* → A canonical scenario with three documented
  inflection points (t15 / t25 / t142). Same engine runs other scenarios
  (Van Gogh / Talleyrand) without code changes.
- *"What's deterministic about the run?"* → Seed 0; same observer dump
  every time; the brief is regenerated from that dump.
- *"What if I want to see the simulation visually?"* → [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md §8](../visual/VISUAL_TRACK_FREEZE_DECISION.md)
  explains the prerequisite.

---

## Cross-reference

- **Brief sample**: [WITNESS_OBSERVER_BRIEF_SAMPLE.md](WITNESS_OBSERVER_BRIEF_SAMPLE.md)
- **Case study**: [WITNESS_CASE_STUDY_TEXT_FIRST.md](WITNESS_CASE_STUDY_TEXT_FIRST.md)
- **Visual appendix**: [WITNESS_VISUAL_EXPERIMENT_APPENDIX.md](WITNESS_VISUAL_EXPERIMENT_APPENDIX.md)
- **Resume bullets**: [WITNESS_RESUME_BULLETS_FINAL.md](WITNESS_RESUME_BULLETS_FINAL.md)
- **Verbal-delivery variant**: [docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md](../demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md)
