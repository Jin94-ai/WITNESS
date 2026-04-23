# Spike 1 Review Packet — World Engine v2.0

> **Audience**: external LLM reviewers (Gemini, ChatGPT, etc.).
> **Ask**: §6 has 8 targeted questions. Please answer those + flag any
> design or methodological risks you see. No knowledge of prior Witness
> work is assumed; §1 gives the minimum-viable context.
> **Scope under review**: Spike 1A + 1B + 1C + 1D of the World Engine
> (Layer 1 calendar, Layer 2 economy, Layer 3 politics, Layer 5 crowd,
> Sync Layer bridge). Person Engine (v0.5–v1.2) is stable upstream and is
> summarised only as context for the coupling design.

---

## §1. Project identity in one page

### 1.1 What Witness is now

Two engines sharing the same `engine/` + `content/` Python code but
producing **separate record streams**:

| | **Person Engine** (v0.5–v1.2, stable) | **World Engine** (v2.0, Spike 1 just landed) |
|---|---|---|
| Question | "What shaped this individual's life?" | "What shaped the world this individual was embedded in?" |
| Unit of analysis | Agent (Peter, Van Gogh, Talleyrand, ...) | City / region (Jerusalem AD 30) |
| Core dynamic | Agent-based, hazard-driven, ensemble | Multi-layer social/environmental dynamics |
| Tick | 2h per tick (event-dense) to 24h per tick (event-sparse) | 1 day per tick (variable `dt_days` supported) |
| Sync | Single-scale | Sync Layer bridges N person-substeps per world day |
| Existing results | 1003 tests, 7-layer validation, 3 scenarios (Peter/VG/Talleyrand) | 62 world tests, 4 layers + sync skeleton |
| Paper status | Working draft [PAPER_DRAFT_V06.md](../../PAPER_DRAFT_V06.md), 413 lines | n/a — out-of-scope for Spike 1 |

### 1.2 Why two engines

The Person Engine answered "is this individual's counterfactual
structure discoverable from a simulator's self-reported causal chain?"
(verdict: yes; Judas removal → arrest rate 100%→0%, Cohen's *d* −6.87).

But it cannot answer "what if Rome had been more conciliatory?" or
"what if Passover had been a month later?" because the entire world
outside the protagonists is a *constant background*. The World Engine
makes the world its own **dynamical system** whose variables can be
intervened on. Spike 1 is the minimum demonstration that the engine
can keep the world alive without any agents at all.

### 1.3 Five ABSOLUTE RULES carried forward

1. Engine/content separation — no hard-coded person references in
   `engine/` (verified by a CI grep).
2. Canonical scripture preserved verbatim (Korean revised — 개역개정).
3. Jesus — *originally* non-agent; **v2.0 amendment**: promoted to an
   agent with a special behaviour profile so "what if Jesus was
   removed?" is representable. Canonical texts remain verbatim.
4. No LLM in the simulation loop. LLMs assist design + post-hoc
   analysis + external review only (this document is one such use).
5. No universality claim until a third structurally distinct scenario
   exists (Peter + VG = structural isomorphism only; Talleyrand is the
   third, negotiator-type scenario — partial universality claim
   permitted for "the engine is scenario-agnostic", **not** for "the
   patterns generalise").

---

## §2. Spike 1 scope under review

The spike was built in four sub-pieces each with its own test suite.

### 2.1 Spike 1A — Layer 1 calendar + Layer 5 crowd

- Hebrew calendar: Nisan 1 start, Passover at day 13 (Nisan 14),
  Unleavened Bread days 14–20, Firstfruits day 15, Shavuot day 64
  (Sivan 6, = Firstfruits + 49 per Lev 23:15-16).
- Shabbat recurrence: `(day_index - shabbat_anchor) % 7 == 0`.
- Pilgrim-influx target: superposition of two asymmetric Gaussians
  peaked at Passover (amplitude 10) and Shavuot (amplitude 4).
- Crowd density:

      density(t+1) = clamp(
          baseline
          + (density(t) - baseline) * exp(-dt/tau)      # decay
          + pilgrim_influx(t) * inflow_weight * dt      # drive
          + N(0, sigma*dt)                               # noise
      , baseline, ceiling)

- **Success criteria (pytest)**: Passover peak ≥ 3× baseline,
  post-Passover decline, Shavuot second peak, Shabbat cadence exact 7d,
  100-seed flatline rate < 10%. All passing; observed Passover peak
  10× baseline (ceiling), Shavuot peak 4.5×.

### 2.2 Spike 1B — Layer 2 economy

- Single variable: `staple_price`.
- Update (two-step cascade) ::

      demand_3d(t+1) = memory*demand_3d(t) + (1-memory)*pilgrim_influx(t)
      price(t+1)    = clamp(
          floor
          + (price(t) - floor) * exp(-dt/price_tau)     # mean reversion
          + demand_3d(t+1) * demand_weight * dt         # delayed demand shock
          + N(0, sigma*dt)
      , floor, ceiling)

- `memory = 0.66` gives a 3-day IIR brake so price does not spike on the
  same day the first pilgrims arrive (reviewer #2 delay requirement).
- Observed: price peak 3.8 at day ~15 (lags the crowd peak by ~2 days);
  decays to floor 1.3 by day 30.

### 2.3 Spike 1C — Layer 3 politics

- Two state variables: `roman_alertness` (0..10) and
  `pilate_location` ∈ {caesarea, jerusalem}.
- Location is calendar-driven (delay brake): Pilate approaches
  Jerusalem `approach_lead_days` before Passover, stays through
  Firstfruits + `approach_stay_days` after, also appears for Shavuot.
- Alertness update ::

      boost         = threshold_step * dt    if crowd ≥ threshold else 0
      location_bias = pilate_bonus * dt      if in_jerusalem      else 0
      alertness(t+1) = clamp(
          floor
          + (alertness(t) - floor)*exp(-dt/tau)
          + boost                     # threshold brake on crowd coupling
          + location_bias
          + N(0, sigma*dt)
      , floor, ceiling)

- Threshold brake prevents linear amplification of every small crowd
  movement; only crowd ≥ 5 (half of ceiling) trips the boost.
- Observed: alertness peak 8.7 at Passover, Jerusalem 20/90 days.

### 2.4 Spike 1D — Sync Layer bridge

**No agents yet.** The Sync Layer is the skeleton that Spike 2 will use
to splice the existing Person Engine into a 12-substep-per-day loop:

- `AgentPercept`: local, partial view exposed to an agent per substep
  (crowd density, economic stress 0..1, perceived authority 0..1,
  days-to-Passover, active feast name, Shabbat flag). Reviewer #5
  required "local percept, not global state", which this honours.
- `WorldEffect`: one emission from one agent substep; `channel_id` +
  `value`. Channels are declared in `WorldConfig.effect_channels` with
  aggregation mode `sum`, `mean`, `max`, or `threshold`.
- `SyncLayer.drain_aggregated()` collapses per-channel buffers into a
  single `dict[str, float]` and hands it to the next world tick via
  `LayerContext.aggregated_effects`. Spike 1 always drains empty.

---

## §3. Architecture snapshot

### 3.1 Layer tick order

```
LayerContext(dt_days=1.0, rng_seed, world_snapshot, aggregated_effects)
     │
     ▼
Layer 1  calendar   → day_index, feast, shabbat, pilgrim_influx_target
     │
     ▼  (reads Layer 1 from this tick's fresh snapshot)
Layer 5  crowd      → crowd_density(t+1)
     │
     ▼  (reads Layer 1)
Layer 2  economy    → staple_price(t+1), demand_3d avg
     │
     ▼  (reads Layer 1 + Layer 5)
Layer 3  politics   → roman_alertness(t+1), pilate_location
     │
     ▼
RunawayDetector.observe(samples, deltas)
     │
     ▼
WorldState(t+1)
```

### 3.2 Folder structure

```
witness/
├── engine/               # Person Engine (unchanged in v2.0)
├── world/                # World Engine v2.0
│   ├── core/             # Layer protocol, WorldState, WorldConfig, WorldEffect
│   ├── environment/      # CalendarLayer (Layer 1)
│   ├── social/           # CrowdLayer (Layer 5)
│   ├── economy/          # EconomyLayer (Layer 2)
│   ├── politics/         # PoliticsLayer (Layer 3)
│   └── simulation/       # WorldTick, RunawayDetector, SyncLayer
├── content/
│   ├── {peter,judas,...}/    # Person-Engine agent packs (shared)
│   ├── shared/               # Scripture + shared triggers
│   └── worlds/
│       └── jerusalem_ad30/   # World-pack for Spike 1
├── tests/
│   ├── test_engine/      # 959 Person-Engine tests
│   ├── test_peter/       # 44 Peter-specific tests
│   └── test_world/       # 62 World-Engine tests (Spike 1)
├── scripts/              # Person-Engine paper scripts + demo_world_*
├── docs/
│   ├── person/paper_data/    # Person-Engine paper artifacts
│   ├── world/SPIKE_1_REVIEW.md  # <- this document
│   ├── prompts/              # Session prompts
│   └── archive/              # Historical one-offs
└── data/
    ├── person/              # Person-Engine runtime data
    │   ├── abc_snapshots/       # pyABC SQLite DBs
    │   ├── trajectory_*.jsonl   # run-level datasets
    │   └── {culture,geography,traditions}/
    └── world/               # (empty placeholder for v2.0 data)
```

Hard rule: **no file under `engine/` was modified** for Spike 1. World
Engine imports from `engine/` but never reaches into it.

### 3.3 Reviewer-principle compliance

The 8 external-review principles from
[WORLD_SPIKE_1A.md](../prompts/WORLD_SPIKE_1A.md) were applied to every
new layer:

| # | Principle | Spike 1 application |
|---|-----------|---------------------|
| 1 | Explicit update equations | Every layer has `describe_dynamics()` returning its equation + time constants |
| 2 | Cross-layer brakes (delay / threshold / saturation) | crowd: decay+clamp; economy: 3-day IIR+clamp; politics: threshold+delay+clamp |
| 3 | Numerical success criteria | 5 `test_success_criteria.py` checks (incl. 100-seed flatline) |
| 4 | Variable `dt_days` | Threaded through `LayerContext`; all per-day rates multiplied by `dt_days` |
| 5 | WorldEffect aggregation interface | 4 modes implemented and tested — awaiting Spike 2 agents |
| 6 | Runaway detection | `RunawayDetector` observes clamps + per-day delta limits |
| 7 | Causal-consistency tests | `test_world_tick.py::test_causal_consistency_influx_monotonically_raises_density` + matching tests per layer |
| 8 | Strict Spike-A scope | No Layer 4 (factions), no rumours, no agent integration |

---

## §4. What this spike intentionally does NOT do

The scope was held deliberately narrow. Out of scope for Spike 1:

- Layer 4 factions (Pharisees, Zealots, Jesus movement) — Spike 3.
- Rumour propagation graphs — Spike 3.
- Person-Engine integration — Spike 2. The Sync Layer is a *skeleton*.
- Variable-intervention experiments ("what if Pilate was lenient?") —
  Spike 4. `world/intervention/` is an empty namespace.
- Any claim about matching historical Jerusalem to the simulated world.
  Spike 1 is internal-consistency only.

---

## §5. Current numerical behaviour (seed 0, 90 days)

Single-seed summary from `scripts/demo_world_full.py`:

| Day | Hebrew date | Feast | Crowd | Price | Alert | Pilate |
|-----|-------------|-------|-------|-------|-------|--------|
|  0  | Nisan 1    | –                 |  1.0 |  1.0 |  2.0 | caesarea |
|  9  | Nisan 10   | –                 |  5.7 |  1.2 |  4.3 | **jerusalem** (approach) |
| 13  | Nisan 14   | passover          | 10.0 |  3.5 |  8.7 | jerusalem |
| 15  | Nisan 16   | firstfruits       | 10.0 |  3.8 | ~10  | jerusalem |
| 20  | Nisan 21   | unleavened_bread  |  5.2 |  3.2 |  7.1 | jerusalem |
| 30  | Iyyar 1    | –                 |  1.3 |  1.3 |  4.1 | caesarea |
| 64  | Sivan 6    | shavuot           |  4.5 |  1.8 |  3.8 | jerusalem |
| 90  | –          | –                 |  1.0 |  1.0 |  2.1 | caesarea |

Aggregate over seed 0:
- 12 Shabbats at days 7, 14, 21, ..., 84 (every 7 days, anchor Nisan 15).
- Runaway warnings: 5 (3 crowd-ceiling hits + 2 alertness-ceiling hits
  around Passover — expected, not pathological).
- 100-seed flatline rate < 10% criterion: 0 flatlines observed.

---

## §6. Questions for the reviewer

Please answer any / all of these; flag additional concerns as §7.

### Q1. Layer tick order & fixed-point safety

Current order is calendar → crowd → economy → politics, each layer
reading only layers already updated in this tick. There is no circular
dependency in Spike 1, so a single forward pass is fine. But in Spike 3
we plan to add faction → crowd → faction influence loops. Is the
single-pass order enough, or should we introduce fixed-point iteration
with explicit delay buffers from the outset?

### Q2. Crowd-ceiling saturation

Passover crowd density saturates at the ceiling (10×) for ~3 days. We
read this as "Jerusalem fills up; any further pilgrim arrivals are
indistinguishable from peak". Is clamping + logging enough, or should
we expose overflow as a distinct state variable (e.g., `overflow_pressure`)
that Spike 2 agents could react to (sleeping outside, leaving early)?

### Q3. 3-day IIR on demand

The economy layer uses `memory=0.66` (roughly 3-day IIR) as the only
brake between pilgrim arrival and price response. Is that realistic for
a grain market at AD-30 technology? Would you prefer (a) a longer IIR,
(b) a piecewise-linear supply response, or (c) both? Does the current
formulation have a hidden equilibrium problem we missed?

### Q4. Pilate location model

Pilate's location is a step function with a 4-day pre-Passover
approach and 10-day post-feast stay plus a 2-day envelope around
Shavuot. This is the only non-scalar discrete signal in Spike 1. Is
this a reasonable abstraction, or does it unfairly reduce the governor
to a calendar function when the historical record also has him react
to specific incidents (Tacitus, Josephus Ant. 18, Philo Legatio 38)?
What would be the minimal next step — a second state that depends on
alertness reaching a sub-threshold?

### Q5. Threshold brake on crowd → alertness

`crowd ≥ 5` triggers an `alertness += 1.5 * dt` step. Below 5, only
decay + location bias apply. We chose a hard threshold because reviewer
#2 asked for one brake per cross-layer edge and because step functions
keep telemetry simple. But a soft threshold (sigmoid, logistic) would
be more physically plausible. Is the hardness causing any analyzable
pathologies we have not noticed? Would a soft transition make
counterfactual experiments (Spike 4) harder or easier to interpret?

### Q6. Sync Layer skeleton vs. eventual spec

`SyncLayer.make_percept()` currently returns 8 fields normalised to
unit intervals. Spike 2 will feed these into Person-Engine
`EnvironmentState.surveillance` and `crowd_pressure`. Two risks we see:
(a) the percept is too coarse — an agent cannot tell "elite soldier
patrolled my street today" from "alertness is high city-wide"; (b) the
percept update cadence is once per world day while person-tick is 2
hours, so agents might stale-read the world by up to ~23 hours. Is one
of these risks dominant? How would you structure the percept-update
cadence without reintroducing O(world-ticks × person-substeps) work?

### Q7. ABSOLUTE RULE #3 change (Jesus as agent)

v1.1 amendments promote Jesus from "non-agent canonical event" to
"agent with a special behaviour profile" so that
`intervention/remove_jesus` becomes expressible in Spike 4.
Theologically the user has decided this is acceptable; methodologically
we are still wary: a single special agent whose `influence` scalar
dominates the system can make the world's outcome fragile to one
parameter. Should we constrain the Jesus agent in specific ways (e.g.,
action set restricted to teaching / healing / specific scripture
citations) so the agent adds *measurable influence* without
overwhelming the model?

### Q8. Runtime data separation

The repo now separates Person-Engine records (`docs/person/`,
`data/person/`) from World-Engine records (`docs/world/`, `data/world/`)
so that artifacts from one engine never contaminate the other. Scripts
writing paper numbers still write into `docs/person/paper_data/`, not
`docs/world/`. Is this split meaningful or is it performative
book-keeping? Would you prefer a single shared `data/` plus per-artifact
provenance tags?

---

## §7. Known risks we have flagged

For the reviewer: please add to this list.

| Risk | Mitigation so far |
|------|-------------------|
| Spike 2 integration pressure may push us to modify `engine/` | Sync Layer design is agent-read-only from the world's side; the agent → world direction goes through `WorldEffect` values, not engine API changes |
| "World ticks once a day, agent ticks every 2 h" sync scheme is untested with feedback loops | Spike 1 aggregates empty; Spike 2 will surface timing issues in controlled tests |
| Canonical scripture constraint vs. Jesus-as-agent | Tests in Spike 2 will assert that all Jesus utterances match the canonical scripture store byte-for-byte |
| Jerusalem AD-30 is the only world content — risk of over-fitting the engine to it | Spike 1B/C/D parameter values are isolated in `content/worlds/jerusalem_ad30/world_config.json`; adding a second world (arles_1888) should require no code change |
| Parameter sprawl (tau, weight, sigma × 4 layers) | Every parameter lives in the content-pack JSON; `describe_dynamics()` on each layer echoes it back; no hidden constants in code paths |

---

## §8. How to run & verify

From repo root:

```bash
# 90-day 4-layer demo with full output.
python scripts/demo_world_full.py --seed 0

# Calendar-only + crowd-only legacy demo.
python scripts/demo_world_spike1a.py --seed 0

# All world tests (62 tests; fast).
pytest tests/test_world/ -q

# Slow success criterion (100-seed flatline check).
pytest tests/test_world/ -m slow -q

# Full repo suite (1064 fast tests; proves Spike 1 did not break the
# Person Engine).
pytest -m "not slow and not archived" -q
```

All paths are POSIX; on Windows the same commands run under `bash` /
`pwsh` provided Python 3.11+ and `pyproject.toml` deps are installed.

---

## §9. Output format we would prefer

```
## §6 answers
Q1. …
Q2. …
…
Q8. …

## §7 additions
- Additional risk: …
- Suggested mitigation: …

## Overall judgement
Spike 1 is ready to proceed to Spike 2: YES / NO / CONDITIONAL
Conditions (if any): …
```

Thanks for the critical read.
