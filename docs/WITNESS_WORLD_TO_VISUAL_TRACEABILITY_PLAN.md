# WITNESS — World-to-Visual Traceability Plan

Date: 2026-05-02  
Track: Visual / Pixel Event Playback  
Status: Planning document for provenance-first verification

---

## 0. Executive Decision

현재 Pixel Event Playback(PEP)은 **움직이는 도트 cutscene prototype**으로는 의미가 있다. 하지만 아직 WITNESS의 핵심 주장인 아래 체인을 증명하지 못한다.

```text
Engine simulation
→ Observer output
→ Candidate selection
→ Visual translation
→ Human-readable playback
```

따라서 다음 단계는 candidate 확장, UI polish, animation 추가가 아니다.

**다음 단계는 World-to-Visual Traceability Pass다.**

목표는 단순하다.

> 실제 엔진/observer를 돌려 나온 결과가 어떤 근거로 현재 visual playback이 되었는지, scene 단위와 timeline event 단위로 증명 가능하게 만든다.

현재 의심:

```text
Claude Code가 엔진 세계를 실제로 시각화한 것이 아니라,
그럴듯한 도트 영상을 hand-authored template으로 만든 것일 수 있다.
```

이 의심은 정당하다. 따라서 visual track은 이제 **예쁘게 보이기**보다 **연동 증명**을 우선한다.

---

## 1. Current Diagnosis

### 1.1 PEP가 현재 증명한 것

PEP는 다음을 증명했다.

- Canvas primitive로 도트 캐릭터를 그릴 수 있다.
- actor spawn / move / face / speech / emote / pose_change / crowd_react timeline을 재생할 수 있다.
- candidate 1개를 짧은 cutscene으로 변환할 수 있다.
- static PSD보다 상호작용 감각이 개선되었다.
- schema validation과 unit tests로 JSON/timeline의 구조적 오류를 막을 수 있다.

### 1.2 PEP가 아직 증명하지 못한 것

아직 다음은 증명하지 못했다.

- actor 위치가 실제 simulation state에서 왔는가?
- actor 감정/상태가 실제 observer output과 연결되는가?
- speech/emote/pose_change가 실제 event 또는 signal에서 derive되었는가?
- guard, crowd, supporter 같은 visual role이 source data에서 설명 가능한가?
- timeline event의 순서가 실제 tick 흐름과 대응되는가?
- visual playback이 “그럴듯한 mock”인지 “world data translation”인지 구분 가능한가?

### 1.3 현재 가장 큰 리스크

현재 visual은 다음 구조에 가깝다.

```text
Observer candidate metadata
→ hand-authored playback template
→ staged pixel cutscene
```

WITNESS가 보여줘야 할 구조는 다음이다.

```text
Engine run output
→ observer packet / candidate packet
→ source events / agent states / signals
→ traceable visual mapping
→ playback
```

즉, 지금의 문제는 animation quality가 아니라 **provenance gap**이다.

---

## 2. Guiding Principle

이번 단계의 원칙:

```text
Visual은 더 그럴듯해지기 전에, 먼저 더 추적 가능해야 한다.
```

각 visual event는 반드시 아래 셋 중 하나로 분류되어야 한다.

| Mapping class | 의미 | 허용 여부 |
|---|---|---|
| `source_derived` | source event/signal/agent state에서 직접 도출 | 적극 허용 |
| `source_inferred` | source signal을 바탕으로 연출상 추론 | 허용, 단 근거 명시 |
| `staged_only` | 화면 이해를 위해 임의 배치/연출 | MVP에서는 제한 허용, 비율 공개 |

핵심은 `staged_only`를 없애는 것이 아니라, **숨기지 않는 것**이다.

---

## 3. New Workstream Name

작업명:

```text
World-to-Visual Traceability Pass
```

약칭:

```text
WVT Pass
```

산출물 명명:

- `VISUAL_TRACEABILITY_AUDIT.md`
- `visual_traceability_report.json`
- `traceability_case`: `VT-A / VT-B / VT-C`

---

## 4. Scope

### 4.1 대상 anchor

```text
peter_scarcity_baseline only
```

### 4.2 대상 candidate

기존 PEP 3개만 유지한다.

```text
C01_t15 — authority_pressure
C02_t25 — saturation_split
C03_t142 — confession_cluster
```

### 4.3 금지

이번 단계에서는 visual 확장 금지.

- candidate 5~7개 확장 금지
- 새 anchor 금지
- 새 scenario 금지
- 새 engine metric 금지
- 새 timeline event type 금지
- 새 animation 추가 금지
- Phaser / React / PixiJS 도입 금지
- 외부 asset 금지
- story renderer 재개 금지
- timeline scrub 금지
- full replay 금지
- player intervention 금지
- pathfinding 금지

---

## 5. Target Architecture

현재 구조:

```text
data/visual/dot_observer_data.json
→ scripts/visual/build_event_playbacks.py
→ data/visual/event_playbacks.json
→ visual/pixel_event_playback.html
```

개선 후 구조:

```text
Engine / Observer outputs
→ dot_observer_data.json
→ candidate source packet extraction
→ event_playbacks.json + source_trace
→ visual_traceability_report.json
→ pixel_event_playback.html
   - Korean Observer Mode
   - Trace Mode
```

핵심은 `event_playbacks.json`이 단순 playback script가 아니라, **source-provenance 포함 IR**이 되는 것이다.

---

## 6. Required Data Model Change

### 6.1 Playback-level `source_trace`

각 playback에 `source_trace`를 추가한다.

```json
{
  "source_trace": {
    "anchor_id": "peter_scarcity_baseline",
    "source_file": "data/visual/dot_observer_data.json",
    "candidate_id": "C03_t142",
    "tick": 142,
    "tick_range": [140, 144],
    "candidate_use_mode": "story_ready",
    "strongest_lens": "person",
    "salience_score": 3,
    "source_events": [
      "public_confession",
      "forgiveness_emitted"
    ],
    "source_signals": [
      "cohort_split",
      "saturation_lock",
      "agent_state_shift"
    ],
    "source_agents": ["agent_09", "agent_03"],
    "mapping_mode": "partially_staged",
    "traceability_note": "Confession and forgiveness events are source-derived; positions and crowd staging are inferred."
  }
}
```

### 6.2 Timeline event-level `source`

각 timeline event에 source mapping을 추가한다.

예시 — source-derived:

```json
{
  "t": 1500,
  "type": "speech",
  "actor": "agent_03",
  "text": "I did.",
  "duration": 1600,
  "source": {
    "class": "source_derived",
    "kind": "observer_event",
    "source_event": "public_confession",
    "mapping": "public_confession -> speech bubble",
    "confidence": "high"
  }
}
```

예시 — source-inferred:

```json
{
  "t": 3100,
  "type": "emote",
  "actor": "agent_05",
  "emote": "grief",
  "duration": 1800,
  "source": {
    "class": "source_inferred",
    "kind": "agent_state_shift",
    "source_signal": "agent_state_shift",
    "mapping": "fragmenting/grief state -> grief emote",
    "confidence": "medium"
  }
}
```

예시 — staged-only:

```json
{
  "t": 0,
  "type": "spawn",
  "actor": "agent_06",
  "source": {
    "class": "staged_only",
    "kind": "visual_composition",
    "mapping": "supporting witness placed for scene readability",
    "confidence": "low",
    "reason": "No direct source position used; staged to preserve focused tile composition."
  }
}
```

---

## 7. New Files to Add

### 7.1 `scripts/visual/audit_visual_traceability.py`

Purpose:

- Read `data/visual/event_playbacks.json`
- Check every playback has `source_trace`
- Check every timeline event has `source`
- Count source mapping classes
- Detect unsupported or suspicious mappings
- Generate Markdown + JSON report

Output:

```text
docs/visual/VISUAL_TRACEABILITY_AUDIT.md
data/visual/visual_traceability_report.json
```

### 7.2 `data/visual/visual_traceability_report.json`

Machine-readable summary.

Example:

```json
{
  "schema": "visual_traceability_report_v1",
  "anchor_id": "peter_scarcity_baseline",
  "playback_count": 3,
  "summary": {
    "timeline_events_total": 46,
    "source_derived": 14,
    "source_inferred": 20,
    "staged_only": 12,
    "derived_ratio": 0.30,
    "derived_or_inferred_ratio": 0.74
  },
  "case": "VT-B",
  "playbacks": [...]
}
```

### 7.3 `docs/visual/VISUAL_TRACEABILITY_AUDIT.md`

Human-readable audit.

Must include:

- summary table
- per-playback source chain
- per-timeline mapping table
- staged-only event list
- risk assessment
- VT-A/B/C case decision

---

## 8. Existing Files to Modify

### 8.1 `scripts/visual/build_event_playbacks.py`

Modify template output to add:

- playback-level `source_trace`
- event-level `source`

Important:

- Do not add new candidate.
- Do not add new event type.
- Do not change visual staging yet unless required for source clarity.
- Preserve current PEP readability cleanup timelines.

### 8.2 `data/visual/event_playbacks.json`

Regenerate after adding source metadata.

Expected changes:

- schema remains `event_playback_v1`
- new optional fields added:
  - `source_trace`
  - timeline event `source`

### 8.3 `scripts/visual/validate_event_playbacks.py`

Extend validation:

- require `source_trace`
- require event-level `source`
- validate `source.class in {source_derived, source_inferred, staged_only}`
- validate confidence in `{high, medium, low}`
- validate source-derived events name known source events/signals
- warn or fail if `staged_only` ratio too high

Suggested thresholds:

```text
VT-A threshold:
  source_derived + source_inferred >= 80%
  staged_only <= 20%

VT-B threshold:
  source_derived + source_inferred >= 55%
  staged_only <= 45%

VT-C:
  source_derived + source_inferred < 55%
  or missing source mappings
```

### 8.4 `tests/test_visual/test_event_playbacks.py`

Add tests:

- every playback has `source_trace`
- every timeline event has `source`
- mapping class is valid
- confidence is valid
- staged-only ratio below chosen maximum
- source-derived events reference known candidate source event/signal
- audit script exits 0

### 8.5 `visual/pixel_event_playback.html`

Add two modes:

```text
Observer Mode
Trace Mode
```

Do not mix them.

#### Observer Mode

User-facing Korean UI.

Hide internal terms:

- `candidate_id`
- `tick`
- `anchor`
- `playback_id`
- `events`
- `actors`
- `schema`

Show instead:

```text
제목: 경비병의 압박
상황: 경비병이 다가오자 두 인물이 물러난다.
관찰: 주변 인물들이 경비병 쪽으로 시선을 돌린다.
```

#### Trace Mode

Developer-facing audit panel.

Show:

```text
source candidate: C01_t15
source tick: 15
source signals: authority_vigilance_spike, cohort_split, agent_state_shift
mapping mode: partially_staged
source-derived: N
source-inferred: N
staged-only: N
```

Optional:

- timeline event list with source class
- color labels for mapping class
- current active event source mapping while playback runs

Do not add timeline scrub.

---

## 9. Korean Observer Mode Text Plan

### 9.1 C01 — authority_pressure

```text
제목: 경비병의 압박
상황: 경비병이 다가오자 두 인물이 뒤로 물러난다.
관찰: 주변 인물들이 경비병 쪽으로 시선을 돌린다.
```

### 9.2 C02 — saturation_split

```text
제목: 갈라지는 무리
상황: 한 인물의 고백 이후, 맞은편 인물이 무너지고 거리를 둔다.
관찰: 왼쪽 무리와 오른쪽 무리의 반응이 갈라진다.
```

### 9.3 C03 — confession_cluster

```text
제목: 공개 고백
상황: 중앙 인물이 앞으로 나와 말하고, 곁의 인물이 무릎을 꿇는다.
관찰: 주변 인물들이 중앙을 바라보고 일부가 가까이 다가온다.
```

These texts are **observer labels**, not story renderer prose.

Do not generate narrative paragraphs.

---

## 10. Traceability Case Decision

Replace PEP-A/B/C for this pass with VT-A/B/C.

### VT-A — Traceable visual translation

Conditions:

- every playback has complete `source_trace`
- every timeline event has source mapping
- source-derived + source-inferred ratio >= 80%
- staged-only ratio <= 20%
- each core beat is source-derived or source-inferred
- visual can be defended as a translation of engine/observer results

Decision after VT-A:

```text
Proceed to limited World Flow Prototype design.
```

### VT-B — Partially traceable, staged prototype

Conditions:

- source_trace exists
- timeline mappings exist
- core events are connected to source
- but many positions/moves/crowd reactions remain staged-only
- visual is useful but not yet proof of world simulation

Decision after VT-B:

```text
Freeze PEP as staged prototype.
Do not expand candidates.
Design source-derived World Flow Prototype.
```

### VT-C — Visual mock

Conditions:

- source mapping missing or mostly staged-only
- core beats cannot be tied to source events/signals
- candidate data only used as labels
- video is essentially handcrafted mock

Decision after VT-C:

```text
Stop PEP track.
Write failure memo.
Fork to new visual approach based on direct engine event logs.
```

---

## 11. What Counts as “Real Engine Linkage”

### Weak linkage

```text
candidate_id/tick만 가져오고 나머지는 사람이 연출
```

This is not enough.

### Medium linkage

```text
source event/signal/agent role을 가져오고,
visual position/timing은 scene director가 추론
```

This is acceptable for prototype if disclosed.

### Strong linkage

```text
engine/observer output contains event participants, state transitions, location, and tick range;
visual derives actor roles, timing, and action from those fields.
```

This is the target.

---

## 12. Core Questions the Audit Must Answer

For each playback:

1. Which engine/observer output produced this candidate?
2. Which source events or signals justify the visual beat?
3. Which agents are actually present in source data?
4. Which visual roles are source-derived vs assigned by staging?
5. Which timeline actions are backed by source data?
6. Which timeline actions are inferred?
7. Which timeline actions are purely staged?
8. What percentage of the playback is source-backed?
9. Would the same source data consistently produce the same visual playback?
10. If the source candidate changes, would the visual change accordingly?

If these cannot be answered, the visual track is not yet trustworthy.

---

## 13. Implementation Order

### Step 1 — Inspect source candidate data

Open `data/visual/dot_observer_data.json` and identify for C01/C02/C03:

- candidate id
- tick / tick range
- use mode
- strongest lens
- salience score
- focal event
- source events at tick
- source signals
- source agent ids
- any available location/state/role hints

Write a small helper if needed:

```text
scripts/visual/inspect_candidate_sources.py
```

Optional, but useful.

### Step 2 — Add source_trace to builder

Modify `build_event_playbacks.py` so each template includes `source_trace` extracted from candidate/tick data where possible.

### Step 3 — Add source mapping to each timeline event

Every event must have `source`.

Initial mapping can be conservative:

- spawn: usually `staged_only` unless actor presence is source-derived
- speech: usually `source_derived` if tied to confession/discussion/denial
- emote: `source_derived` or `source_inferred` if tied to state/event
- move: usually `source_inferred` or `staged_only`
- face/crowd_react: usually `source_inferred`
- pose_change: `source_inferred` unless direct event/state supports it

### Step 4 — Extend validator

Add source validation rules.

### Step 5 — Add tests

Lock the rules in unit tests.

### Step 6 — Generate audit report

Create `audit_visual_traceability.py`.

Output both JSON and Markdown.

### Step 7 — Add UI mode separation

Modify `pixel_event_playback.html`:

- default: Korean Observer Mode
- toggle: Trace Mode

Observer Mode should feel like a viewer.
Trace Mode should feel like a provenance debugger.

### Step 8 — Decide VT case

Record in:

```text
docs/visual/VISUAL_TRACEABILITY_AUDIT.md
```

---

## 14. Review Document Template

`docs/visual/VISUAL_TRACEABILITY_AUDIT.md` should include:

```md
# Visual Traceability Audit

## 0. Summary

Case: VT-A / VT-B / VT-C

## 1. Scope

Anchor:
Candidates:
Files:

## 2. Traceability Summary

| Playback | Events | Source-derived | Source-inferred | Staged-only | Case |
|---|---:|---:|---:|---:|---|

## 3. Playback Audits

### 3.1 C01_t15 — authority_pressure

Source candidate:
Source tick:
Source events:
Source signals:
Source agents:

| t | visual event | actor | source class | source basis | confidence |
|---:|---|---|---|---|---|

Assessment:

### 3.2 C02_t25 — saturation_split
...

### 3.3 C03_t142 — confession_cluster
...

## 4. Staged-only Risk

## 5. What the Visual Currently Proves

## 6. What the Visual Does Not Yet Prove

## 7. Decision

## 8. Next Action
```

---

## 15. Expected Honest Outcome

Most likely result for current PEP:

```text
VT-B
```

Reason:

- candidate/tick/event labels likely trace back to observer output
- core beats can be justified
- but positions, exact moves, speech text, and crowd staging are likely mostly inferred/staged

This is acceptable if recorded honestly.

The target is not to force VT-A.  
The target is to know the truth.

---

## 16. After Traceability Pass

### If VT-A

Proceed to **World Flow Prototype design**.

Possible next direction:

```text
Pixel World Flow Observer
- one location
- 30-60 seconds
- several source-derived event beats
- persistent actor positions/state
- Korean observer UI
```

### If VT-B

Freeze PEP as partial staged prototype.

Then design a more source-derived visual architecture:

```text
Engine Event Log Adapter
→ World Flow Timeline
→ Persistent Actor State
→ Pixel World Flow Observer
```

No candidate expansion yet.

### If VT-C

Stop PEP.

Write failure memo:

```text
PEP was a useful animation prototype but not a trustworthy world visualization.
```

Then fork to direct engine event log visualization.

---

## 17. Final Directive Prompt

```text
WITNESS Visual track next phase: World-to-Visual Traceability Pass.

Do not expand PEP candidates.
Do not polish animation.
Do not add new visual effects.
Do not introduce Phaser/React/PixiJS.

The current question is trustworthiness:
Does pixel_event_playback.html actually visualize engine/observer output,
or is it mainly a hand-authored cutscene mock?

Tasks:
1. Inspect source candidate data for C01_t15, C02_t25, C03_t142.
2. Add playback-level source_trace to event_playbacks.json via build_event_playbacks.py.
3. Add timeline event-level source mapping to every event.
4. Classify each visual event as source_derived / source_inferred / staged_only.
5. Extend validate_event_playbacks.py to require source mappings.
6. Add unit tests for source_trace and mapping validity.
7. Create scripts/visual/audit_visual_traceability.py.
8. Generate data/visual/visual_traceability_report.json.
9. Generate docs/visual/VISUAL_TRACEABILITY_AUDIT.md.
10. Add Korean Observer Mode and Trace Mode separation to pixel_event_playback.html.
11. Decide VT-A / VT-B / VT-C honestly.

Success is not making the video prettier.
Success is knowing exactly how much of the video is grounded in the actual WITNESS world output.
```

---

## 18. One-Line Summary

> PEP는 움직임을 증명했다. 이제 WITNESS는 그 움직임이 실제 세계 결과에서 온 것인지 증명해야 한다.
