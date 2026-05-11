# WITNESS — Engine Event Log Adapter / World Flow Observer v0 Plan

Date: 2026-05-02  
Status: Planning directive  
Previous visual status: PEP frozen with VT-B  
Next track: Engine Event Log Adapter → World Flow Observer v0

---

## 0. Decision

PEP candidate expansion is suspended.

The current Pixel Event Playback track proved that short cutscene playback is technically possible, and WVT showed that the current PEP is not a pure mock. However, VT-B also exposed the core gap:

```text
source-backed: 72.1%
staged-only:   27.9%
C03 source-backed: 53.3%
```

The next phase should not create more hand-staged cutscenes. The next phase must prove that visual output can be derived from actual engine/observer world flow with a smaller provenance gap.

Working decision:

```text
PEP remains frozen as a partially-staged prototype.
Next step: Engine Event Log Adapter / World Flow Observer v0.
```

---

## 1. Why PEP Expansion Stops Here

PEP succeeded at:

- Canvas-based pixel actor playback
- Short event timeline rendering
- Speech, emote, facing, movement, pose changes
- Korean Observer Mode + Trace Mode
- Provenance classification through WVT
- Partial source-backed visual mapping

PEP did not prove:

- Persistent world flow
- Actual engine-state-driven movement
- Deterministic conversion from source world state to visual event stream
- Spatial continuity across ticks
- Low-staging visual generation
- A user-visible sense that “the world is running”

The main issue is not sprite detail, timing cleanup, or UI copy. The issue is traceability and continuity.

Current PEP is best understood as:

```text
Observer candidate → partially source-backed staged cutscene
```

The desired direction is:

```text
Engine run / observer tick sequence → world-flow event IR → visual observer
```

---

## 2. Goal of This Phase

Build a data-first adapter that converts actual engine/observer output into a visual intermediate representation for world flow.

This phase is not primarily an HTML/rendering phase.

Primary goal:

```text
Prove that visual world flow can be derived from real engine/observer data with explicit provenance.
```

Secondary goal:

```text
Reduce staged-only visual decisions below the PEP VT-B baseline.
```

---

## 3. Scope

### In Scope

- Use existing anchor only: `peter_scarcity_baseline`
- Use existing engine/observer outputs
- Build a world-flow visual IR
- Track persistent actor state across a tick range
- Preserve source provenance per visual event
- Audit source-derived / source-inferred / staged-only ratios
- Produce a traceability report
- Optionally create a minimal non-polished viewer later, only after data audit passes

### Out of Scope

- PEP candidate expansion
- New scenario
- New anchor
- New engine metric
- Story renderer revival
- Full replay UI
- Timeline scrub
- Player intervention
- Pathfinding
- Playable game mechanics
- Phaser / React / PixiJS
- External assets
- Visual polish-first work

---

## 4. Proposed Track Name

Recommended name:

```text
World Flow Observer v0
```

Supporting implementation component:

```text
Engine Event Log Adapter
```

Use both names with this distinction:

- **Engine Event Log Adapter**: data conversion layer
- **World Flow Observer**: eventual visual observer experience

---

## 5. Inputs

Potential input sources:

```text
data/visual/dot_observer_data.json
data/visual/event_playbacks.json
data/visual/visual_traceability_report.json
observer snapshots
candidate packets
per-tick event summaries
agent state deltas
anchor metadata
```

Primary source should be the existing observer output, not hand-authored playback templates.

The adapter should inspect what is actually available before inventing a schema.

Minimum input audit:

1. What tick-level events exist?
2. Which agents are present per tick?
3. Which events are tied to agents?
4. Which states change over time?
5. Which candidate signals can be mapped to visual actions?
6. Are there usable positions, locations, or group memberships?
7. Which visual requirements cannot be source-derived?

---

## 6. Output IR: `world_flow_events_v1`

The new output should not be another candidate cutscene file.

It should represent a short tick sequence with persistent actor state.

Proposed file:

```text
data/visual/world_flow_events.json
```

Schema draft:

```json
{
  "meta": {
    "schema_version": "world_flow_events_v1",
    "anchor_id": "peter_scarcity_baseline",
    "source_file": "data/visual/dot_observer_data.json",
    "tick_range": [0, 160],
    "mode": "focused_world_flow",
    "created_by": "scripts/visual/build_world_flow_events.py"
  },
  "actors": [
    {
      "id": "agent_03",
      "source_kind": "engine_agent",
      "initial_state": "anxious",
      "initial_location": "L1",
      "visual_role_hint": "focal_candidate",
      "provenance": {
        "class": "source_derived",
        "reason": "agent exists in observer source"
      }
    }
  ],
  "ticks": [
    {
      "tick": 15,
      "world_events": [
        {
          "id": "wf_t15_e01",
          "type": "authority_pressure",
          "agents": ["agent_09", "agent_03"],
          "source_events": ["authority_vigilance_spike", "agent_state_shift"],
          "visual_actions": [
            {
              "type": "face",
              "actor": "agent_09",
              "target": "guard",
              "provenance": {
                "class": "source_inferred",
                "source": "authority_vigilance_spike",
                "mapping": "authority pressure implies focal faces authority"
              }
            }
          ],
          "provenance": {
            "class": "source_derived",
            "source_tick": 15,
            "source_candidate": "C01_t15"
          }
        }
      ]
    }
  ]
}
```

---

## 7. Persistent Actor State Model

PEP currently restarts each candidate as a separate cutscene. WFO must preserve actor continuity.

Minimum actor state fields:

```json
{
  "actor_id": "agent_09",
  "tick": 15,
  "location": "L1",
  "visual_x": 8,
  "visual_y": 6,
  "facing": "right",
  "mood": "anxious",
  "role": "focal",
  "last_event": "authority_pressure",
  "visibility": "visible"
}
```

Important distinction:

- `location` should be source-derived where possible.
- `visual_x`, `visual_y` may be staged initially, but must be labeled.
- State transitions must prefer source events or state deltas.
- If movement is invented for readability, mark it as `staged_only` or `source_inferred`.

---

## 8. Provenance Classes

Keep the existing WVT classes, but apply them more strictly.

### `source_derived`

Directly supported by source data.

Examples:

- agent exists in source
- candidate tick exists
- source event exists
- source agent is named in candidate/event
- state change exists in observer packet

### `source_inferred`

Reasonable mapping from source signal to visual action.

Examples:

- `cohort_split` → actors separate spatially
- `public_confession` → speech bubble
- `forgiveness_emitted` → supporter turns toward focal
- `agent_state_shift` → emote or pose change

### `staged_only`

Not supported by source; introduced only for visual readability.

Examples:

- arbitrary crowd placement
- decorative props
- non-source movement
- synthetic timing gap
- invented group composition

Rule:

```text
Every visual action must declare its provenance class.
```

---

## 9. Target Metrics

PEP WVT baseline:

```text
source-backed: 72.1%
staged-only:   27.9%
```

WFO v0 target:

```text
source-backed >= 80%
staged-only   <= 20%
```

Stretch target:

```text
source_derived >= 45%
staged-only    <= 15%
```

Per-scene/per-segment warning threshold:

```text
Any segment below 60% source-backed must be flagged.
```

Do not hide weak segments. The audit should expose them.

---

## 10. Adapter Responsibilities

Script:

```text
scripts/visual/build_world_flow_events.py
```

Responsibilities:

1. Load existing observer/candidate data.
2. Select a focused tick range.
3. Extract candidate-related world events.
4. Build persistent actor list.
5. Build tick-sequenced visual events.
6. Assign provenance to every visual action.
7. Minimize staged-only decisions.
8. Emit `world_flow_events_v1`.

The adapter is not allowed to:

- invent new engine metrics
- modify source observer data
- introduce new scenario logic
- create story prose
- create freeform visual events without provenance

---

## 11. Tick Range Strategy

Avoid full replay.

Recommended initial tick range:

```text
C01_t15 through C03_t142 coverage window
```

Possible first pass:

```text
tick_range: [10, 150]
selected_ticks: [15, 25, 66, 142, 147]
```

But do not add extra candidates unless source data supports them clearly.

Better first implementation:

```text
Use 3 known candidate windows only:
- C01_t15: [13, 17]
- C02_t25: [23, 27]
- C03_t142: [140, 144]

Then connect them through persistent actor state summaries, not continuous animation.
```

This keeps the task tractable while proving continuity.

---

## 12. World Flow vs PEP

| Dimension | PEP | WFO v0 |
|---|---|---|
| Unit | candidate cutscene | tick sequence / event sequence |
| Actor state | reset per scene | persistent across sequence |
| Position | template-authored | source-derived or explicitly staged |
| Provenance | added after WVT | required by design |
| Goal | readability of one event | evidence of world flow |
| UI | playback viewer | observer/audit first |
| Success | user understands short scene | user trusts visual came from engine/observer |

---

## 13. Audit Script

Script:

```text
scripts/visual/audit_world_flow_traceability.py
```

Outputs:

```text
data/visual/world_flow_traceability_report.json
docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md
```

Audit should report:

- total visual actions
- source_derived count/rate
- source_inferred count/rate
- staged_only count/rate
- source-backed rate
- per-tick and per-candidate ratios
- lowest-confidence mappings
- unbacked actor placements
- synthetic actors
- source events not visualized
- visual actions with weak source support

---

## 14. Validation Rules

Script may be integrated into existing validator or separate:

```text
scripts/visual/validate_world_flow_events.py
```

Minimum validation:

1. schema version is `world_flow_events_v1`
2. actor ids are unique
3. all visual action actors exist
4. ticks are non-decreasing
5. provenance exists on every visual action
6. provenance class is one of `source_derived`, `source_inferred`, `staged_only`
7. no staged-only visual action lacks a reason
8. source-backed rate computed
9. staged-only ratio computed
10. warnings generated for low-traceability segments

---

## 15. Optional Viewer Direction

Do not start with viewer polish.

If data/audit passes, create a minimal viewer later:

```text
visual/world_flow_observer.html
```

Viewer principles:

- Korean Observer Mode by default
- Trace Mode available separately
- Internal terms hidden from default user view
- No timeline scrub
- No player control
- No pathfinding
- No full world map
- No Phaser/React/PixiJS
- Canvas primitive only

Default Korean UI should say things like:

```text
세계 관찰: 베드로 결핍 시나리오
현재 구간: 압박 → 분열 → 고백
관찰된 변화: 두 인물이 경비병 압박 이후 물러남
근거 보기: Trace Mode
```

Not:

```text
anchor_id
candidate_id
schema_version
playback_id
actors/events count
```

---

## 16. Korean Observer Mode vs Trace Mode

Split the experience into two modes.

### Korean Observer Mode

Audience: human reviewer / portfolio viewer  
Goal: intuitive observation

Shows:

- Korean event title
- simple situation sentence
- actor names or labels
- visible world state changes
- short observation log

Hides:

- candidate id
- schema fields
- event counts
- internal classifier names
- source classes unless requested

### Trace Mode

Audience: developer / audit reviewer  
Goal: prove source linkage

Shows:

- candidate id
- source tick
- source events/signals
- visual action mapping
- provenance class
- source-backed ratio
- staged-only warnings

Rule:

```text
Do not mix Observer Mode and Trace Mode in the same panel.
```

The previous UI problem came from mixing user-facing observation and developer debug metadata.

---

## 17. Case Criteria

Use WFO-A/B/C, not PEP-A/B/C.

### WFO-A — Strong Traceable World Flow

Conditions:

- source-backed >= 80%
- staged-only <= 20%
- persistent actor state works across selected tick windows
- source-derived events drive the majority of visual actions
- Korean Observer Mode can explain the flow without internal metadata
- Trace Mode proves the mapping clearly

Next:

```text
Create minimal world_flow_observer.html or expand tick coverage.
```

### WFO-B — Partial Traceable Flow

Conditions:

- source-backed >= 60%
- staged-only <= 35%
- key events are source-backed
- spatial continuity remains partly staged
- enough evidence to continue, but not enough for portfolio claim

Next:

```text
Improve adapter / add source extraction / reduce staged-only mappings.
```

### WFO-C — Visual Still Mostly Staged

Conditions:

- source-backed < 60%, or staged-only > 35%
- key visual actions cannot be tied to source data
- adapter mostly reconstructs another staged cutscene system

Next:

```text
Freeze pixel visual track. Move to storyboard/comic or portfolio-only explanation.
```

---

## 18. Implementation Order

### Step 1 — Source Availability Audit

Create a short inventory of source fields available in current observer output.

Output:

```text
docs/visual/WORLD_FLOW_SOURCE_INVENTORY.md
```

Questions:

- What per-tick data exists?
- What per-agent data exists?
- What events are named?
- Are locations stable?
- Are relationships explicit or inferred?
- What is impossible to derive?

### Step 2 — Schema Draft

Create:

```text
docs/visual/WORLD_FLOW_OBSERVER_SPEC.md
```

Include:

- `world_flow_events_v1`
- actor state model
- event/action model
- provenance model
- validation rules

### Step 3 — Adapter Implementation

Create:

```text
scripts/visual/build_world_flow_events.py
```

Output:

```text
data/visual/world_flow_events.json
```

### Step 4 — Traceability Audit

Create:

```text
scripts/visual/audit_world_flow_traceability.py
```

Outputs:

```text
data/visual/world_flow_traceability_report.json
docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md
```

### Step 5 — Tests

Create:

```text
tests/test_visual/test_world_flow_events.py
```

Test:

- schema validity
- actor references
- provenance required
- source-backed ratio calculation
- staged-only threshold warnings
- persistent actor state continuity

### Step 6 — Decision

Record WFO-A/B/C in:

```text
docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md
```

Do not build a viewer until the audit justifies it.

---

## 19. Hard Constraints

Do not modify:

```text
visual/explorer.html
visual/pixel_world_static.html
visual/pixel_scene.html
engine/
scripts/observer/
examples/
```

Do not introduce:

```text
new anchor
new scenario
new engine metric
story renderer
full replay UI
timeline scrub
pathfinding
player intervention
playable loop
React
Phaser
PixiJS
external assets
```

Do not expand:

```text
PEP candidates
PEP animations
PEP visual polish
```

Until WFO traceability is resolved.

---

## 20. What Success Looks Like

A good result is not a prettier animation.

A good result is a report that can honestly say:

```text
This visual event exists because this source event existed.
This actor is visible because this agent was involved.
This reaction is inferred from this signal.
This movement is staged, and here is why.
The total staged-only ratio is below threshold.
```

The final claim should be:

```text
WITNESS visual output is not just a hand-authored mock.
It is a traceable translation layer from engine/observer world flow into human-readable visual events.
```

---

## 21. Recommended Immediate Directive

Use this as the next execution prompt:

```text
WITNESS Visual Track — Start Engine Event Log Adapter / World Flow Observer v0.

Context:
PEP is frozen with VT-B. It is 72.1% source-backed but still 27.9% staged-only. Candidate expansion is forbidden. The next task is to prove that visual world flow can be derived from actual engine/observer output, not hand-authored cutscene templates.

Tasks:
1. Inspect existing observer/visual source data and write docs/visual/WORLD_FLOW_SOURCE_INVENTORY.md.
2. Draft docs/visual/WORLD_FLOW_OBSERVER_SPEC.md for world_flow_events_v1.
3. Implement scripts/visual/build_world_flow_events.py.
4. Generate data/visual/world_flow_events.json.
5. Implement scripts/visual/audit_world_flow_traceability.py.
6. Generate data/visual/world_flow_traceability_report.json and docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md.
7. Add tests/test_visual/test_world_flow_events.py.
8. Decide WFO-A/B/C.

Rules:
- Do not build a new viewer unless the audit passes WFO-A or strong WFO-B.
- Do not expand PEP candidates.
- Do not add new animation or visual polish.
- Do not modify engine/observer/explorer/pixel_world_static/pixel_scene.
- Do not add new anchor, scenario, or engine metric.
- Every visual action must have provenance: source_derived / source_inferred / staged_only.
- Report staged-only ratio honestly.
```
