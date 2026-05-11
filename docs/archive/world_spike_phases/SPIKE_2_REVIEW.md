# Spike 2 Review Packet — Person × World Integration

> **Audience**: external LLM reviewers (Gemini, ChatGPT, etc.) — same venue as
> [SPIKE_1_REVIEW.md](SPIKE_1_REVIEW.md).
> **Ask**: §5 has 7 targeted questions. Please answer those + flag any
> integration or methodological risks you see.
> **Scope under review**: Spike 2 Phase A (three reviewer-requested
> conditions) + Phase B (Person Engine plugged into World Engine via the
> Sync Layer). Spike 1 is already shipped and covered in SPIKE_1_REVIEW.md;
> this document covers only what changed or was built on top.

---

## §1. Context in one page

### 1.1 What Spike 2 delivers

Two half-deliverables:

**Phase A — conditions ChatGPT set as prerequisites for Spike 2.**
- A-1 · Sync aggregation semantics verified. Every declared
  `effect_channel` (sum / mean / max / threshold) is actually applied at
  `SyncLayer.drain_aggregated()`. 12 channel tests pin all four modes.
- A-2 · `overflow_pressure` added to `CrowdState`. When pilgrim demand
  would push density past the ceiling, the *pre-clamp excess* is retained
  in a separate field so downstream consumers (Spike 2 agent percepts,
  future faction pressure) can distinguish "city at capacity" from
  "city overfull". 6 new tests.
- A-3 · Same-tick feedback prohibition. WORLD_DESIGN.md now codifies
  ABSOLUTE RULE #9: a Layer may only read from layers already updated
  this tick or from a previous tick (marked `@prev_tick`). 5 new DAG
  tests automate the check.

**Phase B — Person Engine integrated into the World Engine.**
- B-1 · `SyncLayer.world_to_environment` — translates a `WorldState`
  snapshot into a Person-Engine `EnvironmentState` (5 fields, unit-scaled).
- B-2 · `SyncLayer.actions_to_effects` — converts substep action records
  into `WorldEffect` values using *action attributes* (`visible_signal`,
  `observable_from`), never action-name switches.
- B-3 · `IntegratedWorldRunner` — daily loop:
  `world_tick → env mapping → 12 person substeps → effect aggregation →
  next day`.
- B-4 · 6 integration tests (90-day completion, Peter fear materially
  differs, endogenous events still fire, upstream effects emitted,
  Judas-removed alters outcome, env reflects world).
- B-5 · [scripts/demo_world_integrated.py](../../scripts/demo_world_integrated.py)
  — per-day world state + agent actions + emitted effects in one view.

### 1.2 Key constraints honoured

- **`engine/` untouched** — `world/simulation/integrated_runner.py`
  wraps `SimulationWorld` as a one-session building block; `engine/`
  code path is unchanged.
- **1003 Person-Engine tests green** throughout (now 1084 with 81 world
  tests).
- **No action-name switches** — per-action dispatch would bake content
  into engine code; we use generic action attributes instead.

---

## §2. Architecture delta

### 2.1 The integrated loop

```
agent_states[t0]  env[t0]=default  world_state[t0]
          │               │              │
          ▼               │              ▼
    SimulationWorld (12 substeps)        │
    max_tick=12, environment=env[t0]     │
    triggers + hazard_events active      │
    canonical ExternalEvents DISABLED    │
          │                              │
          ▼                              │
    action_histories[t0]                 │
          │                              │
          ▼                              │
    actions_to_effects()                 │
          │                              │
          ▼                              │
    aggregated_effects_out[t0] ──────────┤
                                         │
                                         ▼
                                   WorldTick.tick(
                                       world_state,
                                       aggregated=aggregated_effects_out[t0]
                                   )
                                         │
                                         ▼
                                   world_state[t1]
                                         │
                                         ▼
                                   sync.world_to_environment
                                         │
                                         ▼
                                     env[t1]
                                         │
          ┌──────────────────────────────┘
          ▼
    SimulationWorld (next 12 substeps) …
```

Each `SimulationWorld` session runs only `max_tick=12` ticks but carries
`state.tick` forward by `day * 12` to give triggers / hazards a
continuous absolute-tick axis.

### 2.2 What the integrated runner DOES NOT handle

- `ExternalEvent` / `CanonicalIntervention` with absolute-tick anchors —
  disabled by default. The Peter canonical timeline (scene_08_arrest at
  tick 152, 3 denials, etc.) is a Person-Engine-only construct. In the
  integrated run the arrest still fires, but via triggers / hazard events,
  not the fixed-tick canonical event.
- Multiple worlds in parallel — runner state is single-world-single-run.
- Variable-time substeps — `substeps_per_day` is fixed at 12.

---

## §3. Empirical behaviour (seed 0, 4 agents, 90 days)

From [demo_world_integrated.py](../../scripts/demo_world_integrated.py):

- Passover (day 13): crowd=10.0 (ceiling), price=3.5, alert=8.7,
  Pilate in Jerusalem, Peter fear 8.5 → 9.9.
- Unleavened Bread (day 14–20): crowd stays at ceiling, alert saturates
  at 10, Judas disillusionment rises 7 → 10.
- Day 20–22: Judas begins emitting `inform_authorities` / `betray`
  actions; aggregated `authority_threat` spikes to 10 (channel SUM).
- Post-feast (day 23–30): crowd decays to 1.3, alert decays to 4,
  Pilate returns to Caesarea on day 24.
- Shavuot (day 64): secondary peak crowd=4.5, all other values lifted
  compared to the quiet mid-window.

Aggregated across 90 days:
- 31 triggers + 21 hazard events fired (endogenous dynamics preserved).
- 25/25 of the verbose-printed days show non-zero WorldEffect —
  upstream causation is routinely present, not rare.
- Judas-removed counterfactual: trigger count and Peter's fear final
  both diverge from the full-agent run.

---

## §4. Known coupling pathologies & mitigations

| Issue | Symptom | Current mitigation | Proposed Spike 3 fix |
|-------|---------|-------------------|----------------------|
| Ceiling saturation hides world effects | Peter fear saturates at ~9.9 in both standalone and integrated; final-value comparisons look null | A-2 `overflow_pressure` added for crowd; fear comparison uses mid-run snapshot | Add overflow-style raw-value fields to *every* saturating state (fear, hope, alertness) |
| `authority_threat` channel sums to 10+ per day | Channel aggregation `sum` accumulates every Judas betrayal without bound | Nothing in Spike 2 — reviewer may suggest normalisation | Introduce a `bounded_sum` aggregation or per-agent contribution cap |
| Canonical ExternalEvent disabled | Integrated run cannot reproduce fixed-tick canonical results | Triggers + hazard events still fire; V3 trigger_arrest metric (from counterfactual experiment) is the discriminative one anyway | If Spike 3 needs canonical events, schedule them against `world_day_index` instead of absolute tick |
| Per-session `state.tick` reset | Risk of trigger or hazard state desync across sessions | Runner rewrites `state.tick = day * 12` before each session | Future work: refactor engine to accept an explicit `tick_offset` parameter (would require engine public-API extension) |

---

## §5. Questions for the reviewer

### Q1. Session-chunking vs. single-pass

`IntegratedWorldRunner` creates a fresh `SimulationWorld` instance every
day (90 × 12-tick sessions). The alternative would be a monolithic
1080-tick `SimulationWorld` with a custom rule that injects world state
each tick boundary. We chose session-chunking because it keeps the
`engine/` code path untouched. Trade-offs we see:

- chunking: `SimulationWorld.__init__` cost × 90; hazard Poisson probs
  reset per session (but with identical per-tick rate).
- monolithic: needs `engine/` extension for an injection hook; simpler
  data flow, more fragile.

Is chunking a real performance / correctness issue in your view, or a
fine compromise?

### Q2. Tick-offset via state.tick write

We carry `state.tick = day * 12` into every session so triggers /
cooldowns see a monotone axis. `SimulationWorld` internally iterates
`for tick in range(1, max_tick + 1)` and overwrites `state.tick = tick`
at the top of each loop — so our write only matters for pre-session
setup (e.g., cooldown initial checks). Is there a correctness hole here
we missed? Does the per-session tick reset break a Person-Engine
invariant we can't see from outside?

### Q3. Action → effect via attributes

The agent → world direction uses two generic action attributes:
`visible_signal is not None` for public intensity, and
`observable_from ∩ {caiaphas, pilate, sanhedrin}` for authority threat.
Rumour seeding is keyword-scan on `visible_signal` text (`inform`,
`betray`, `teach`, etc.).

Two risks we see:
(a) the keyword list is fragile — new content can accidentally fire
    `rumor_seed` or silently skip it.
(b) `observable_from` conflates "visible to that observer" with "affects
    that observer's authority" — they are not the same thing.

How would you redesign the action → effect contract to be both generic
AND misuse-resistant? Should the content pack declare explicit
`world_effect_emitters` on each action?

### Q4. Effect aggregation semantics

Three channels are declared in
[content/worlds/jerusalem_ad30/world_config.json](../../content/worlds/jerusalem_ad30/world_config.json):

- `publicity_shock` — MAX
- `authority_threat` — SUM
- `rumor_seed` — THRESHOLD (0.5)

With 4 agents × 12 substeps × 90 days, SUM on `authority_threat`
routinely hits double-digit totals per day. Is SUM the right choice, or
should we switch to MEAN and let the downstream Layer decide whether to
multiply by a density factor? The reviewer-spike1 answer to Q8 (runtime
data separation) didn't touch aggregation specifically; we'd welcome
your view.

### Q5. Saturation-induced null results

The standalone-vs-integrated fear comparison *passed* our test only
because we compared a mid-run snapshot. Had we compared final fear
only, the test would have missed the world effect entirely (both
saturate at ceiling). This is generalisable: any state with a
hard ceiling + monotone drive produces indistinguishable long-run
outcomes across experimental conditions.

Should we:
(a) add `overflow_pressure`-style raw fields to every saturating state,
(b) measure *time-to-saturation* instead of final value,
(c) redesign the scoring to use area-under-curve,
(d) something else?

### Q6. Conditional canonical events

Canonical ExternalEvents are off in integrated mode because they are
tick-anchored. This is probably wrong in the long run — the Passion
week is historically anchored to Passover, which *does* exist in the
World Engine calendar. A day-index-anchored re-expression could route
around the issue: "scene_08_arrest fires when
`calendar.active_feast == 'passover' AND judas.disillusionment > X`".

Is that the right direction? Who owns the Passover mapping — the
content pack (hard-coded day_index) or the calendar layer (named
feast window) or the sync layer (translation)?

### Q7. Jesus-as-Agent prep

[docs/prompts/WORLD_SPIKE_3.md](../prompts/WORLD_SPIKE_3.md) sketches
Spike 3. One open design question: Jesus is explicitly promoted to
Agent for Spike 3 under the v1.1 amendment to ABSOLUTE RULE #3. This
violates the original Person-Engine constraint "canonical events
only". What is the minimal set of guardrails you'd recommend so that
Jesus-as-Agent does *not* absorb all the causal variance?

Concrete candidates:
- Action set restricted to 5–8 scripture-cited actions.
- Jesus Agent cannot *receive* rumour seeds, only emit them.
- Jesus Agent's `influence` bias caps at the same ceiling as other
  Tier-1 agents.
- Per-day acted-on influence bounded, not summed.

Which of these is essential vs. over-engineering?

---

## §6. How to verify

```bash
# Integrated 90-day run with verbose output.
python scripts/demo_world_integrated.py --seed 0 --days 25 --verbose-days 6

# All world tests (81 tests).
pytest tests/test_world/ -q

# Phase A only (3 conditions).
pytest tests/test_world/test_overflow_pressure.py \
       tests/test_world/test_layer_dag.py -q

# Phase B integration (6 tests).
pytest tests/test_world/test_integrated_runner.py -q

# Full repo (1084 fast tests, proves Person-Engine unaffected).
pytest -m "not slow and not archived" -q
```

All paths are POSIX; on Windows the same commands run under bash / pwsh.

---

## §7. Output format we would prefer

```
## §5 answers
Q1. …
Q2. …
…
Q7. …

## §4 table additions
- New issue: …
  - Symptom: …
  - Proposed mitigation: …

## Overall judgement
Spike 2 is ready to proceed to Spike 3: YES / NO / CONDITIONAL
Conditions (if any): …
```

Thanks for the critical read.
