# WITNESS — Architecture (Portfolio Version)

> External-facing architecture description. Internal terms reframed for general technical audience.

---

## 0. System overview (one paragraph)

WITNESS is a 4-layer agent-based simulation system. Each layer transforms a stream of data from the previous layer: simulation produces snapshots, snapshots get tagged for salience, salient moments become curated candidates, and candidates feed into a visual explorer. The architecture is *additive* — each new layer extends capability without modifying earlier layers.

---

## 1. Layer diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 — Simulation Engine                                    │
│  ─────────────────────────                                      │
│  • Multi-agent state evolution                                  │
│  • Hazard-driven events: P(event) = 1 - exp(-h·dt)              │
│  • Trigger pipeline (events emerge from accumulated state)      │
│  • Architectural constraint: no domain hardcoding in engine     │
│  • 2,640+ unit tests, ruff + mypy clean                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ snapshots (per-tick state)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2 — Observer Snapshot Layer                              │
│  ────────────────────────────────                               │
│  • Captures world / group / agent state per tick                │
│  • Detects 8 salience tag types (e.g., cohort split,            │
│    saturation lock, agent state shift)                          │
│  • Replay cursor + bookmark for navigation                      │
│  • 4 lenses: World / Person / Group / Event                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ candidates (story-worthy moments)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3 — Candidate Extraction / Curation                      │
│  ──────────────────────────────────────                         │
│  • 4 extractors: top-mixed, world-heavy, person-arc,            │
│    event-ripple                                                 │
│  • Curation pipeline: temporal diversity + near-duplicate       │
│    reduction + 3-bucket classification                          │
│  • 3 use modes (no quality verdict, only categorization):       │
│    - candidate suitable for narrative review                    │
│    - candidate kept for observation                             │
│    - low-activity candidate kept for inspection                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ JSON (schema v1, cross_seed_v1)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4 — Visual Explorer                                      │
│  ────────────────────────                                       │
│  • Single self-contained HTML (vanilla JS + SVG, 0 deps)        │
│  • Anchor selector + view toggle (single-run / cross-seed)      │
│  • Timeline scrubbing with salience markers                     │
│  • Candidate filter (3-bucket toggle)                           │
│  • Packet side panel (rationale, signals, classification)       │
└────────────────────────────┬────────────────────────────────────┘
                             │ click
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Side panel — Packet / Story                                    │
│  ────────────────────────                                       │
│  • Packet: why this candidate was surfaced                      │
│  • Story: 3-lens narration (person / event / world)             │
│    — separate CLI tool, not integrated in default demo          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Data flow (single tick)

```
World step (t)
   │
   ├──> WorldSnapshot (mood, blame, suspicion, vigilance, ...)
   │
   ├──> for each group: GroupSnapshot (mode, tension, member_count)
   │
   └──> for each agent: AgentSnapshot (state, fear, hope, shame, delta)

Aggregate snapshot at t = combination of above
   │
   ▼
Salience detector(t) → list of tags (0~8)
   │
   ▼
If tag count >= threshold → candidate
   │
   ▼
Curation pipeline:
   1. Near-duplicate reduce (group adjacent similar candidates)
   2. Use-mode classification (3 buckets)
   3. Temporal diversity (greedy by salience score, min tick gap)
   │
   ▼
CuratedSet (story_ready / observation_only / low_activity_hold)
   │
   ▼
Export to JSON (schema v1)
   │
   ▼
Visual Explorer renders:
   • Dot/zone canvas at current tick
   • Timeline marker (score 1/2/3 visual hierarchy)
   • Candidate panel filtered by use mode
   • Packet panel on candidate click
```

---

## 3. Cross-seed extension (Layer 4 alternative)

```
For seed in [0, 1, 2, 3, 4]:
   ├── Run simulation → snapshots
   ├── Extract candidates → curation
   └── Aggregate per-seed summary

Combine into cross_seed_v1 JSON
   │
   ▼
Cross-seed Visual (small multiples)
   • Outcome distribution banner (REC 3 / PARTIAL 1 / SAT 1)
   • 5 rows = 5 seeds, each with mini-timeline
   • Click row → side panel updates with seed details
```

→ Directly visualizes **configuration sensitivity**: same configuration produces different outcome distributions across seeds.

---

## 4. Architectural principles

### 4.1 Additive layer pattern
Each new layer reads from the previous layer's output (snapshots, candidates, etc.) and produces a new output type. New layers don't modify earlier layers. This means:
- Engine layer can freeze without blocking visualization improvements
- Visualization can iterate (V0 → V1 → V2 → Explorer) without engine churn
- Schema versioning (v1, cross_seed_v1) enforces data contracts

### 4.2 Observer-not-evaluator design principle
The system does *not* automatically judge story quality. Instead:
- Candidates are *categorized* (3 use modes) rather than *ranked*
- Curation pipeline does mechanical operations (deduplication, temporal diversity) rather than quality scoring
- Final judgment is left to a human reviewer
- Side panel shows *why* each candidate was surfaced, not *whether* it's good

### 4.3 Configuration sensitivity validation
Single-seed runs are insufficient to claim sensitivity ratios. Cross-seed view is the canonical way to *show* how configuration sensitivity manifests. The 8th rule of the self-evaluation framework explicitly warns about single-seed conditioning bias.

### 4.4 Self-evaluation framework
8 rules applied across the project to reduce confirmation bias:
1. Don't claim positive findings without specifying a falsifying observation
2. List alternatives before attributing failure to external causes
3. Cite specifications verbatim and check intent
4. Document "what could still be wrong" in every report
5. Preserve the original instruction verbatim before scope reduction
6. Present options frame-neutrally to the decision maker
7. Audit reports for forbidden positive-only language
8. Use 5+ seed ensemble for sensitivity claims (not single-seed)

---

## 5. Tech stack details

### 5.1 Engine (Python)
- **Pydantic** for schema validation (strict types)
- **dataclasses** for fast intermediate data structures
- **pytest** with 3-tier execution (fast / domain / full)
- **ruff + mypy** in CI (0 errors required)

### 5.2 Visualization (Frontend)
- **Vanilla JS + SVG** (no React, no D3, no build step)
- **fetch() + JSON** for data loading (HTTP server required, no `file://`)
- **CSS opacity hierarchy** for salience marker tier (low/mid/high)
- **Color encoding system**:
  - Agent state → dot fill color
  - Group mode → zone fill color
  - Salience score → timeline marker color
  - World mood → background tint

### 5.3 Schema versioning
- `v1` — single-run snapshot stream (200 ticks × N agents × M groups)
- `cross_seed_v1` — multi-seed aggregate (sparse trajectory + outcome label per seed)
- Both schemas append-only (additions OK, deletions = major bump)

---

## 6. Module map (for code reviewers)

| Path | Role |
|---|---|
| `engine/core/` | Agent state, hazard, trigger, action, environment |
| `engine/rules/` | State transition rules (physical, emotional, social, temporal) |
| `engine/simulation/` | Simulation runtime, batch execution, statistics, POM validation |
| `engine/observer/` | Snapshot schema, recorder, salience detector, candidate extractor, curation |
| `engine/world/` | Multi-agent crowd dynamics, spatial layer, information layer |
| `scripts/observer/` | Observer report generation, candidate packet builder |
| `scripts/visual/` | Visual data export (JSON for HTML) |
| `visual/` | Self-contained HTML explorers |
| `content/` | Scenario data (Peter, Van Gogh, Talleyrand — all use same engine) |
| `tests/` | 2,640+ unit tests |

---

## 7. Performance characteristics

- **Engine throughput**: ~1,000-1,300 ticks/sec per scenario (Peter ~1,001, Van Gogh ~1,267)
- **Memory**: ~2 MB per Peter run, ~1.7 MB per Van Gogh run
- **Visual render**: 200 ticks × 12 agents at 10 fps replay (no frame drops on desktop)
- **JSON export size**: 824 KB single-run, 275 KB cross-seed (5 seeds, sparse)
- **Test suite**: ~13 min full, ~30s fast / domain test subsets

---

## 8. CI / dev workflow

- **GitHub Actions**: ruff + mypy + pytest on push
- **Branch strategy**: TBD (currently single-branch development)
- **Schema migration**: append-only; deletion requires major version bump
- **Documentation**: Markdown in `docs/`, `INDEX.md` master navigation

---

## 9. What's *not* in this architecture

To set expectations for reviewers:

- ❌ No machine learning (no PyTorch / sklearn for classification)
- ❌ No live multiplayer (single-seed deterministic per run)
- ❌ No 3D / animation (2D SVG only)
- ❌ No React / Vue / Angular (vanilla JS by design)
- ❌ No mobile / responsive (desktop only)
- ❌ No public API / SaaS (internal exploration tool)
- ❌ No automated story quality scoring (observer-not-evaluator principle)

---

## 10. One-paragraph summary (for portfolio bullets)

> *"WITNESS is a 4-layer agent-based simulation system. The engine (2,640+ tests, no domain hardcoding) produces snapshots, the observer layer detects salient moments through 8 tag types, the candidate pipeline curates story-worthy moments into 3 use modes, and the visual explorer (vanilla JS + SVG, zero dependencies) renders the simulation as dots/zones with timeline scrubbing and a side panel showing the rationale for each candidate. The cross-seed view directly visualizes configuration sensitivity. Built with strict architectural principles: additive layers, observer-not-evaluator, schema versioning, and an 8-rule self-evaluation framework for anti-bias engineering."*

---

**Versioning**: v1 (this architecture doc) — 2026-04-30 portfolio repack.
