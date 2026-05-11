# WITNESS Provenance Table — peter_scarcity_baseline

> **Companion to**: [WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
> **Phase**: 12 — per-field provenance ledger.
> **Schema**: `provenance_table_v1`.

This document is a **flat field-level ledger**: every field reported on a
candidate (or actively excluded from this brief) gets a row stating its
provenance class and confidence. The brief itself is structured for
readability; this table is structured for verification.

## How to read

- **class** is one of:
  - `source_derived` — a direct readout from observer state.
  - `source_inferred` — a bounded rule applied over source signals.
  - `not_used` — a field that *would* have come from the visual layer
    and is intentionally excluded from this text-first brief.
- **confidence** is qualitative:
  - `high` — direct field readout, no aggregation.
  - `medium` — aggregation over a window or small set.
  - `low` — single classifier output gated by a policy threshold.
- **source** points to the ledger's origin. `observer.ticks[t].…` indexes
  by tick value via the safe lookup in `build_observer_brief.get_tick`.

The aggregate at the bottom counts field rows across all candidates in
this run. `source_derived` should dominate; `not_used` is a positive
signal that the brief is honestly excluding visual-only fields rather
than silently omitting them.

---

## Field-class aggregate (all candidates included)

- Total field rows: **160**
- `source_derived`: **95** (59.4%)
- `source_inferred`: **40** (25.0%)
- `not_used`: **25** (15.6%)


---

## C01_t15 — tick 15 (`story_ready`)

| field | class | confidence | source | value | note |
|---|---|---|---|---|---|
| `candidate_id` | `source_derived` | high | observer.candidates[i].candidate_id | C01_t15 | stable identifier; not interpreted |
| `tick` | `source_derived` | high | observer.candidates[i].tick | 15 | anchor tick of the candidate |
| `tick_range` | `source_derived` | high | observer.candidates[i].tick_range | 13, 17 | [lo, hi] window the candidate spans |
| `agents_involved` | `source_derived` | high | observer.candidates[i].agents_involved | agent_01, agent_02, agent_03, agent_04, agent_05, agent_06, agent_07, agent_08 (+4) | stable agent IDs; ordering is observer-imposed |
| `events_involved` | `source_derived` | high | observer.candidates[i].events_involved | guard_approaches, discussion_emitted, public_denial, visible_withdrawal, discussion_emitted | active_events seen across the tick range |
| `rationale` | `source_inferred` | medium | observer scoring rules over signals | Surfaced by authority_vigilance_spike, cohort_split, agent_state_shift | free-text label of which signals fired |
| `signals` | `source_inferred` | high | observer signal detector outputs | authority_vigilance_spike, cohort_split, agent_state_shift | set of signal names that crossed thresholds |
| `candidate_type` | `source_inferred` | medium | observer lens scorer | person | person \| group \| event \| world (matches strongest_lens) |
| `strongest_lens` | `source_inferred` | medium | observer lens scorer | person | lens with maximum signal weight at this tick range |
| `salience_score` | `source_inferred` | medium | observer salience aggregator | 3 | integer score from signal weights |
| `dominant_pressure` | `source_inferred` | low | observer pressure classifier | none_clear | may be 'none_clear' if no single pressure dominates |
| `use_mode` | `source_inferred` | medium | curation policy thresholds | story_ready | story_ready \| observation_only \| low_activity_hold |
| `related_candidate_ids` | `source_inferred` | high | observer relation linker | [] | IDs of other candidates linked by shared signal |
| `world.crowd_mood` | `source_derived` | high | observer.ticks[t].world.crowd_mood | agitated | categorical mood at the candidate tick |
| `world.blame_concentration` | `source_derived` | high | observer.ticks[t].world.blame_concentration | 0.280 |  |
| `world.public_suspicion` | `source_derived` | high | observer.ticks[t].world.public_suspicion | 0.150 |  |
| `world.authority_vigilance` | `source_derived` | high | observer.ticks[t].world.authority_vigilance | 0.250 |  |
| `groups[].dominant_mode` | `source_derived` | high | observer.ticks[t].groups[i].dominant_mode | L2=low_activity; L3=low_activity; L1=partial |  |
| `groups[].tension` | `source_derived` | high | observer.ticks[t].groups[i].tension | L2=0.100; L3=0.100; L1=0.539 |  |
| `groups[].member_count` | `source_derived` | high | observer.ticks[t].groups[i].member_count | L2=4; L3=4; L1=4 |  |
| `agents[].dominant_state` | `source_derived` | high | observer.ticks[t].agents[i].dominant_state | agent_01=calm; agent_02=calm; agent_03=fragmenting; …(+9) |  |
| `agents[].fear` | `source_derived` | high | observer.ticks[t].agents[i].fear | agent_01=1.300; agent_02=1.300; agent_03=8.730; …(+9) |  |
| `agents[].hope` | `source_derived` | high | observer.ticks[t].agents[i].hope | agent_01=4.000; agent_02=4.000; agent_03=4.000; …(+9) |  |
| `agents[].shame_self` | `source_derived` | high | observer.ticks[t].agents[i].shame_self | agent_01=1.000; agent_02=1.000; agent_03=5.450; …(+9) |  |
| `agents[].salient` | `source_derived` | high | observer.ticks[t].agents[i].salient | agent_01=False; agent_02=False; agent_03=True; …(+9) |  |
| `agents[].x` | `source_derived` | high | observer.ticks[t].agents[i].x | agent_01=455; agent_02=305; agent_03=155; …(+9) | engine canvas-space coordinate; not a tile |
| `agents[].y` | `source_derived` | high | observer.ticks[t].agents[i].y | agent_01=135; agent_02=335; agent_03=135; …(+9) |  |
| `synthetic_guard_movement` | `not_used` | low | (visual staging — frozen) | (excluded) | would require Engine Event Log Adapter |
| `walking_frame_timeline` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `speech_bubble_staging` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `tile_grid_position` | `not_used` | low | (visual staging — frozen) | (excluded) | viewer maps to canvas coords, not tiles |
| `hand_authored_cutscene_cues` | `not_used` | low | (visual staging — frozen) | (excluded) |  |

---

## C02_t25 — tick 25 (`story_ready`)

| field | class | confidence | source | value | note |
|---|---|---|---|---|---|
| `candidate_id` | `source_derived` | high | observer.candidates[i].candidate_id | C02_t25 | stable identifier; not interpreted |
| `tick` | `source_derived` | high | observer.candidates[i].tick | 25 | anchor tick of the candidate |
| `tick_range` | `source_derived` | high | observer.candidates[i].tick_range | 23, 27 | [lo, hi] window the candidate spans |
| `agents_involved` | `source_derived` | high | observer.candidates[i].agents_involved | agent_01, agent_02, agent_03, agent_04, agent_05, agent_06, agent_07, agent_08 (+4) | stable agent IDs; ordering is observer-imposed |
| `events_involved` | `source_derived` | high | observer.candidates[i].events_involved | discussion_emitted, public_confession, forgiveness_emitted, discussion_emitted, visible_withdrawal, visible_withdrawal, public_denial, discussion_emitted | active_events seen across the tick range |
| `rationale` | `source_inferred` | medium | observer scoring rules over signals | Surfaced by cohort_split, saturation_lock, agent_state_shift | free-text label of which signals fired |
| `signals` | `source_inferred` | high | observer signal detector outputs | cohort_split, saturation_lock, agent_state_shift | set of signal names that crossed thresholds |
| `candidate_type` | `source_inferred` | medium | observer lens scorer | person | person \| group \| event \| world (matches strongest_lens) |
| `strongest_lens` | `source_inferred` | medium | observer lens scorer | person | lens with maximum signal weight at this tick range |
| `salience_score` | `source_inferred` | medium | observer salience aggregator | 3 | integer score from signal weights |
| `dominant_pressure` | `source_inferred` | low | observer pressure classifier | none_clear | may be 'none_clear' if no single pressure dominates |
| `use_mode` | `source_inferred` | medium | curation policy thresholds | story_ready | story_ready \| observation_only \| low_activity_hold |
| `related_candidate_ids` | `source_inferred` | high | observer relation linker | [] | IDs of other candidates linked by shared signal |
| `world.crowd_mood` | `source_derived` | high | observer.ticks[t].world.crowd_mood | calm | categorical mood at the candidate tick |
| `world.blame_concentration` | `source_derived` | high | observer.ticks[t].world.blame_concentration | 0.030 |  |
| `world.public_suspicion` | `source_derived` | high | observer.ticks[t].world.public_suspicion | 0.015 |  |
| `world.authority_vigilance` | `source_derived` | high | observer.ticks[t].world.authority_vigilance | 0.250 |  |
| `groups[].dominant_mode` | `source_derived` | high | observer.ticks[t].groups[i].dominant_mode | L2=low_activity; L3=low_activity; L1=saturation |  |
| `groups[].tension` | `source_derived` | high | observer.ticks[t].groups[i].tension | L2=0.089; L3=0.040; L1=0.748 |  |
| `groups[].member_count` | `source_derived` | high | observer.ticks[t].groups[i].member_count | L2=4; L3=4; L1=4 |  |
| `agents[].dominant_state` | `source_derived` | high | observer.ticks[t].agents[i].dominant_state | agent_01=calm; agent_02=calm; agent_03=fragmenting; …(+9) |  |
| `agents[].fear` | `source_derived` | high | observer.ticks[t].agents[i].fear | agent_01=0.500; agent_02=0.500; agent_03=9.090; …(+9) |  |
| `agents[].hope` | `source_derived` | high | observer.ticks[t].agents[i].hope | agent_01=4.000; agent_02=4.000; agent_03=4.000; …(+9) |  |
| `agents[].shame_self` | `source_derived` | high | observer.ticks[t].agents[i].shame_self | agent_01=1.000; agent_02=1.000; agent_03=6.190; …(+9) |  |
| `agents[].salient` | `source_derived` | high | observer.ticks[t].agents[i].salient | agent_01=False; agent_02=False; agent_03=True; …(+9) |  |
| `agents[].x` | `source_derived` | high | observer.ticks[t].agents[i].x | agent_01=455; agent_02=305; agent_03=155; …(+9) | engine canvas-space coordinate; not a tile |
| `agents[].y` | `source_derived` | high | observer.ticks[t].agents[i].y | agent_01=135; agent_02=335; agent_03=135; …(+9) |  |
| `synthetic_guard_movement` | `not_used` | low | (visual staging — frozen) | (excluded) | would require Engine Event Log Adapter |
| `walking_frame_timeline` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `speech_bubble_staging` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `tile_grid_position` | `not_used` | low | (visual staging — frozen) | (excluded) | viewer maps to canvas coords, not tiles |
| `hand_authored_cutscene_cues` | `not_used` | low | (visual staging — frozen) | (excluded) |  |

---

## P03_t66_agent_08 — tick 66 (`story_ready`)

| field | class | confidence | source | value | note |
|---|---|---|---|---|---|
| `candidate_id` | `source_derived` | high | observer.candidates[i].candidate_id | P03_t66_agent_08 | stable identifier; not interpreted |
| `tick` | `source_derived` | high | observer.candidates[i].tick | 66 | anchor tick of the candidate |
| `tick_range` | `source_derived` | high | observer.candidates[i].tick_range | 64, 68 | [lo, hi] window the candidate spans |
| `agents_involved` | `source_derived` | high | observer.candidates[i].agents_involved | agent_08 | stable agent IDs; ordering is observer-imposed |
| `events_involved` | `source_derived` | high | observer.candidates[i].events_involved | visible_grief, discussion_emitted, public_confession, forgiveness_emitted, discussion_emitted, discussion_emitted | active_events seen across the tick range |
| `rationale` | `source_inferred` | medium | observer scoring rules over signals | Surfaced by cohort_split, agent_state_shift | free-text label of which signals fired |
| `signals` | `source_inferred` | high | observer signal detector outputs | cohort_split, agent_state_shift | set of signal names that crossed thresholds |
| `candidate_type` | `source_inferred` | medium | observer lens scorer | person | person \| group \| event \| world (matches strongest_lens) |
| `strongest_lens` | `source_inferred` | medium | observer lens scorer | person | lens with maximum signal weight at this tick range |
| `salience_score` | `source_inferred` | medium | observer salience aggregator | 2 | integer score from signal weights |
| `dominant_pressure` | `source_inferred` | low | observer pressure classifier | none_clear | may be 'none_clear' if no single pressure dominates |
| `use_mode` | `source_inferred` | medium | curation policy thresholds | story_ready | story_ready \| observation_only \| low_activity_hold |
| `related_candidate_ids` | `source_inferred` | high | observer relation linker | P01_t68_agent_03, P02_t68_agent_05 | IDs of other candidates linked by shared signal |
| `world.crowd_mood` | `source_derived` | high | observer.ticks[t].world.crowd_mood | calm | categorical mood at the candidate tick |
| `world.blame_concentration` | `source_derived` | high | observer.ticks[t].world.blame_concentration | 0.000 |  |
| `world.public_suspicion` | `source_derived` | high | observer.ticks[t].world.public_suspicion | 0.000 |  |
| `world.authority_vigilance` | `source_derived` | high | observer.ticks[t].world.authority_vigilance | 0.250 |  |
| `groups[].dominant_mode` | `source_derived` | high | observer.ticks[t].groups[i].dominant_mode | L2=low_activity; L3=low_activity; L1=partial |  |
| `groups[].tension` | `source_derived` | high | observer.ticks[t].groups[i].tension | L2=0.075; L3=0.000; L1=0.545 |  |
| `groups[].member_count` | `source_derived` | high | observer.ticks[t].groups[i].member_count | L2=4; L3=4; L1=4 |  |
| `agents[].dominant_state` | `source_derived` | high | observer.ticks[t].agents[i].dominant_state | agent_08=agitated |  |
| `agents[].fear` | `source_derived` | high | observer.ticks[t].agents[i].fear | agent_08=7.150 |  |
| `agents[].hope` | `source_derived` | high | observer.ticks[t].agents[i].hope | agent_08=4.000 |  |
| `agents[].shame_self` | `source_derived` | high | observer.ticks[t].agents[i].shame_self | agent_08=3.910 |  |
| `agents[].salient` | `source_derived` | high | observer.ticks[t].agents[i].salient | agent_08=True |  |
| `agents[].x` | `source_derived` | high | observer.ticks[t].agents[i].x | agent_08=365 | engine canvas-space coordinate; not a tile |
| `agents[].y` | `source_derived` | high | observer.ticks[t].agents[i].y | agent_08=335 |  |
| `synthetic_guard_movement` | `not_used` | low | (visual staging — frozen) | (excluded) | would require Engine Event Log Adapter |
| `walking_frame_timeline` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `speech_bubble_staging` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `tile_grid_position` | `not_used` | low | (visual staging — frozen) | (excluded) | viewer maps to canvas coords, not tiles |
| `hand_authored_cutscene_cues` | `not_used` | low | (visual staging — frozen) | (excluded) |  |

---

## C03_t142 — tick 142 (`story_ready`)

| field | class | confidence | source | value | note |
|---|---|---|---|---|---|
| `candidate_id` | `source_derived` | high | observer.candidates[i].candidate_id | C03_t142 | stable identifier; not interpreted |
| `tick` | `source_derived` | high | observer.candidates[i].tick | 142 | anchor tick of the candidate |
| `tick_range` | `source_derived` | high | observer.candidates[i].tick_range | 140, 144 | [lo, hi] window the candidate spans |
| `agents_involved` | `source_derived` | high | observer.candidates[i].agents_involved | agent_01, agent_02, agent_03, agent_04, agent_05, agent_06, agent_07, agent_08 (+4) | stable agent IDs; ordering is observer-imposed |
| `events_involved` | `source_derived` | high | observer.candidates[i].events_involved | public_confession, forgiveness_emitted, discussion_emitted, visible_grief, visible_grief, public_denial, visible_grief | active_events seen across the tick range |
| `rationale` | `source_inferred` | medium | observer scoring rules over signals | Surfaced by cohort_split, saturation_lock, agent_state_shift | free-text label of which signals fired |
| `signals` | `source_inferred` | high | observer signal detector outputs | cohort_split, saturation_lock, agent_state_shift | set of signal names that crossed thresholds |
| `candidate_type` | `source_inferred` | medium | observer lens scorer | person | person \| group \| event \| world (matches strongest_lens) |
| `strongest_lens` | `source_inferred` | medium | observer lens scorer | person | lens with maximum signal weight at this tick range |
| `salience_score` | `source_inferred` | medium | observer salience aggregator | 3 | integer score from signal weights |
| `dominant_pressure` | `source_inferred` | low | observer pressure classifier | accusation | may be 'none_clear' if no single pressure dominates |
| `use_mode` | `source_inferred` | medium | curation policy thresholds | story_ready | story_ready \| observation_only \| low_activity_hold |
| `related_candidate_ids` | `source_inferred` | high | observer relation linker | [] | IDs of other candidates linked by shared signal |
| `world.crowd_mood` | `source_derived` | high | observer.ticks[t].world.crowd_mood | agitated | categorical mood at the candidate tick |
| `world.blame_concentration` | `source_derived` | high | observer.ticks[t].world.blame_concentration | 0.357 |  |
| `world.public_suspicion` | `source_derived` | high | observer.ticks[t].world.public_suspicion | 0.150 |  |
| `world.authority_vigilance` | `source_derived` | high | observer.ticks[t].world.authority_vigilance | 0.250 |  |
| `groups[].dominant_mode` | `source_derived` | high | observer.ticks[t].groups[i].dominant_mode | L2=low_activity; L3=low_activity; L1=saturation |  |
| `groups[].tension` | `source_derived` | high | observer.ticks[t].groups[i].tension | L2=0.075; L3=0.000; L1=0.970 |  |
| `groups[].member_count` | `source_derived` | high | observer.ticks[t].groups[i].member_count | L2=4; L3=4; L1=4 |  |
| `agents[].dominant_state` | `source_derived` | high | observer.ticks[t].agents[i].dominant_state | agent_01=calm; agent_02=calm; agent_03=fragmenting; …(+9) |  |
| `agents[].fear` | `source_derived` | high | observer.ticks[t].agents[i].fear | agent_01=0.000; agent_02=0.000; agent_03=8.990; …(+9) |  |
| `agents[].hope` | `source_derived` | high | observer.ticks[t].agents[i].hope | agent_01=4.000; agent_02=4.000; agent_03=4.000; …(+9) |  |
| `agents[].shame_self` | `source_derived` | high | observer.ticks[t].agents[i].shame_self | agent_01=1.000; agent_02=0.000; agent_03=10.000; …(+9) |  |
| `agents[].salient` | `source_derived` | high | observer.ticks[t].agents[i].salient | agent_01=False; agent_02=False; agent_03=True; …(+9) |  |
| `agents[].x` | `source_derived` | high | observer.ticks[t].agents[i].x | agent_01=455; agent_02=305; agent_03=155; …(+9) | engine canvas-space coordinate; not a tile |
| `agents[].y` | `source_derived` | high | observer.ticks[t].agents[i].y | agent_01=135; agent_02=335; agent_03=135; …(+9) |  |
| `synthetic_guard_movement` | `not_used` | low | (visual staging — frozen) | (excluded) | would require Engine Event Log Adapter |
| `walking_frame_timeline` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `speech_bubble_staging` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `tile_grid_position` | `not_used` | low | (visual staging — frozen) | (excluded) | viewer maps to canvas coords, not tiles |
| `hand_authored_cutscene_cues` | `not_used` | low | (visual staging — frozen) | (excluded) |  |

---

## C05_t147 — tick 147 (`story_ready`)

| field | class | confidence | source | value | note |
|---|---|---|---|---|---|
| `candidate_id` | `source_derived` | high | observer.candidates[i].candidate_id | C05_t147 | stable identifier; not interpreted |
| `tick` | `source_derived` | high | observer.candidates[i].tick | 147 | anchor tick of the candidate |
| `tick_range` | `source_derived` | high | observer.candidates[i].tick_range | 145, 149 | [lo, hi] window the candidate spans |
| `agents_involved` | `source_derived` | high | observer.candidates[i].agents_involved | agent_01, agent_02, agent_03, agent_04, agent_05, agent_06, agent_07, agent_08 (+4) | stable agent IDs; ordering is observer-imposed |
| `events_involved` | `source_derived` | high | observer.candidates[i].events_involved | public_confession, forgiveness_emitted, discussion_emitted, public_confession, forgiveness_emitted, visible_grief, public_confession, forgiveness_emitted (+1) | active_events seen across the tick range |
| `rationale` | `source_inferred` | medium | observer scoring rules over signals | Surfaced by cohort_split, saturation_lock, agent_state_shift | free-text label of which signals fired |
| `signals` | `source_inferred` | high | observer signal detector outputs | cohort_split, saturation_lock, agent_state_shift | set of signal names that crossed thresholds |
| `candidate_type` | `source_inferred` | medium | observer lens scorer | person | person \| group \| event \| world (matches strongest_lens) |
| `strongest_lens` | `source_inferred` | medium | observer lens scorer | person | lens with maximum signal weight at this tick range |
| `salience_score` | `source_inferred` | medium | observer salience aggregator | 3 | integer score from signal weights |
| `dominant_pressure` | `source_inferred` | low | observer pressure classifier | none_clear | may be 'none_clear' if no single pressure dominates |
| `use_mode` | `source_inferred` | medium | curation policy thresholds | story_ready | story_ready \| observation_only \| low_activity_hold |
| `related_candidate_ids` | `source_inferred` | high | observer relation linker | C04_t146 | IDs of other candidates linked by shared signal |
| `world.crowd_mood` | `source_derived` | high | observer.ticks[t].world.crowd_mood | calm | categorical mood at the candidate tick |
| `world.blame_concentration` | `source_derived` | high | observer.ticks[t].world.blame_concentration | 0.000 |  |
| `world.public_suspicion` | `source_derived` | high | observer.ticks[t].world.public_suspicion | 0.000 |  |
| `world.authority_vigilance` | `source_derived` | high | observer.ticks[t].world.authority_vigilance | 0.250 |  |
| `groups[].dominant_mode` | `source_derived` | high | observer.ticks[t].groups[i].dominant_mode | L2=low_activity; L3=low_activity; L1=saturation |  |
| `groups[].tension` | `source_derived` | high | observer.ticks[t].groups[i].tension | L2=0.075; L3=0.000; L1=0.794 |  |
| `groups[].member_count` | `source_derived` | high | observer.ticks[t].groups[i].member_count | L2=4; L3=4; L1=4 |  |
| `agents[].dominant_state` | `source_derived` | high | observer.ticks[t].agents[i].dominant_state | agent_01=calm; agent_02=calm; agent_03=fragmenting; …(+9) |  |
| `agents[].fear` | `source_derived` | high | observer.ticks[t].agents[i].fear | agent_01=0.000; agent_02=0.000; agent_03=7.740; …(+9) |  |
| `agents[].hope` | `source_derived` | high | observer.ticks[t].agents[i].hope | agent_01=4.000; agent_02=4.000; agent_03=4.000; …(+9) |  |
| `agents[].shame_self` | `source_derived` | high | observer.ticks[t].agents[i].shame_self | agent_01=1.000; agent_02=0.000; agent_03=6.790; …(+9) |  |
| `agents[].salient` | `source_derived` | high | observer.ticks[t].agents[i].salient | agent_01=False; agent_02=False; agent_03=True; …(+9) |  |
| `agents[].x` | `source_derived` | high | observer.ticks[t].agents[i].x | agent_01=455; agent_02=305; agent_03=155; …(+9) | engine canvas-space coordinate; not a tile |
| `agents[].y` | `source_derived` | high | observer.ticks[t].agents[i].y | agent_01=135; agent_02=335; agent_03=135; …(+9) |  |
| `synthetic_guard_movement` | `not_used` | low | (visual staging — frozen) | (excluded) | would require Engine Event Log Adapter |
| `walking_frame_timeline` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `speech_bubble_staging` | `not_used` | low | (visual staging — frozen) | (excluded) |  |
| `tile_grid_position` | `not_used` | low | (visual staging — frozen) | (excluded) | viewer maps to canvas coords, not tiles |
| `hand_authored_cutscene_cues` | `not_used` | low | (visual staging — frozen) | (excluded) |  |

---

## Field-class aggregate (all candidates included)

- Total field rows: **160**
- `source_derived`: **95** (59.4%)
- `source_inferred`: **40** (25.0%)
- `not_used`: **25** (15.6%)
