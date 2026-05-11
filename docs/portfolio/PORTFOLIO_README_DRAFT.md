# WITNESS — Agent-based World Simulation Explorer

> **DRAFT**: 본 README는 *외부용 초안*. 루트 `README.md`에는 별도 directive 시 적용.

> Multi-agent simulation + visual observer for browsing emergent story candidates.

---

## Project Title

**WITNESS** — *Agent-based World Simulation Explorer*

---

## One-liner

> A simulation engine that models historical figures as multi-agent systems, paired with a dot-based visual explorer that surfaces story-worthy moments through automated curation.

---

## Problem

Multi-agent simulations produce rich behavior (cohort dynamics, configuration-driven outcomes, emergent events), but interpreting them is hard:

- **Reading text logs** is slow when 200 ticks × 12 agents × 3 groups change every step.
- **Statistical summaries** average over the dynamics that matter.
- **Cherry-picking interesting runs** by hand doesn't scale.
- **Single-seed validation** misleads about how sensitive the system is to configuration.

We need a way to *see the world flow*, *spot moments worth investigation*, and *compare how the same configuration leads to different outcomes across seeds* — without auto-judging story quality.

---

## Solution

WITNESS is a 4-layer system:

1. **Simulation Engine** — agent state, hazard-driven events, trigger pipeline. 2,640+ unit tests, no domain hardcoding.
2. **Observer Layer** — captures snapshots and detects salient moments through 8 tag types (cohort split, saturation lock, agent state shift, etc.).
3. **Candidate Pipeline** — extracts story-worthy moments and curates them into 3 use modes (suitable for narrative review / observation only / low-activity hold).
4. **Visual Explorer** — single self-contained HTML (vanilla JS + SVG, zero external dependencies) that visualizes the simulation as dots/zones, lets you scrub timeline, and surfaces curated candidates with side panels showing the rationale for each.

The cross-seed view shows **configuration sensitivity directly**: same configuration + different seed = different outcome distribution (REC 3 / PARTIAL 1 / SAT 1 in our canonical example).

---

## Demo

### Quick start

```bash
# Generate visualization data (one-time)
python scripts/visual/export_dot_observer_data.py
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple \
    --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py \
    --anchor peter_scarcity_triple --seeds 0 1 2 3 4 \
    --output data/visual/dot_observer_cross_seed_triple.json
python scripts/visual/export_dot_observer_data.py \
    --anchor vangogh_sacred_baseline \
    --output data/visual/dot_observer_data_vangogh.json

# Serve (HTTP server required, no build step)
python -m http.server 8000

# Open in browser
http://localhost:8000/visual/explorer.html
```

### 5-minute demo flow

| Time | Screen | Message |
|---|---|---|
| 0:00–0:30 | Intro | "Agent-based world simulation explorer" |
| 0:30–2:00 | **Single-run replay** | Timeline salience markers, candidate panel, click-to-jump |
| 2:00–3:30 | **Cross-seed comparison** | 5 seeds → REC 3 / PARTIAL 1 / SAT 1 distribution |
| 3:30–4:40 | **Different scenario family** | "Quiet flow" — system doesn't auto-judge dynamics |
| 4:40–5:00 | Wrap | 3-layer role: Visual / Packet / Story |

---

## Key Features

### 1. Hazard-driven multi-agent simulation engine
- Agent state (drives, beliefs, fear/hope/shame, etc.)
- Trigger pipeline (events emerge from state accumulation)
- Hazard rate Poisson process (`P(event) = 1 - exp(-h·dt)`)
- Strict architectural constraints: no person hardcoding in engine layer
- 2,640+ unit tests passing

### 2. Visual observer with timeline scrubbing
- 200-tick replay of 12 agents × 3 groups as SVG dots and zones
- Color encoding: agent state → dot color, group mode → zone color, salience → marker color
- Timeline marker hierarchy: low (dim yellow) / mid (orange) / high (red bold)
- Play / Pause / ◀ / ▶ / Slider / click-to-jump / keyboard arrow keys

### 3. Cross-seed configuration sensitivity view
- Small multiples (5 seeds × 200 ticks) on a single screen
- Outcome distribution banner (REC / PARTIAL / SAT)
- Per-seed candidate counts, salience timing, group trajectory
- Directly visualizes "same config → different outcomes" property

### 4. Curated candidate panel with packet side panel
- Auto-extracted story-worthy moments grouped into 3 use modes
- 3-bucket filter (toggle each on/off)
- Click candidate → tick jump (single-run) + range overlay + packet panel update
- Packet shows: rationale + signals + classification + location + related candidates

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Simulation Engine                       │
│  (multi-agent state, hazard, trigger, action, environment) │
│  → 2,640+ unit tests, no domain hardcoding                 │
└──────────────────────────┬─────────────────────────────────┘
                           │ snapshots
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    Observer Snapshot Layer                 │
│  (per-tick world / group / agent state, 8 salience tags)   │
└──────────────────────────┬─────────────────────────────────┘
                           │ candidates
                           ▼
┌────────────────────────────────────────────────────────────┐
│             Candidate Extraction / Curation                │
│   (4 extractors → 3-bucket curation: suitable for review / │
│    observation only / low-activity hold)                   │
└──────────────────────────┬─────────────────────────────────┘
                           │ JSON (schema v1 + cross_seed_v1)
                           ▼
┌────────────────────────────────────────────────────────────┐
│                     Visual Explorer                        │
│   (anchor selector + view toggle + canvas + timeline)      │
└──────────────────────────┬─────────────────────────────────┘
                           │ click
                           ▼
┌────────────────────────────────────────────────────────────┐
│           Packet / Story Side Panel                        │
│   (rationale + signals + classification + lens summary)    │
└────────────────────────────────────────────────────────────┘
```

→ Each layer can freeze independently; later layers add capability without modifying earlier layers (additive layer pattern).

---

## Tech Stack

### Backend
- **Python 3.11+**
- **Pydantic** (schema validation)
- **NumPy / SciPy** (statistical analysis)
- **pytest** (2,640+ tests, 3-tier execution: fast / domain / full)
- **Ruff + mypy** (linting + type checking, 0 errors)

### Visualization
- **Vanilla JS + SVG** (zero external dependencies)
- **Self-contained HTML** (HTTP server only — no build step, no React)

### Optional / supporting
- **SALib** (sensitivity analysis)
- **UMAP / HDBSCAN** (clustering — research mode)

### CI / dev
- GitHub Actions (test + coverage)
- Schema versioning (data export contracts: v1, cross_seed_v1)

---

## Validation / Tests

- **2,640+ fast unit tests** (~13 min full suite)
- **97%+ coverage** on critical modules (time_axis, slow_recovery, inhibitor)
- **Configuration sensitivity validation**: 3/3 scenario groups show ≥3 distinct outcome classes within scenario
- **Cross-scenario universality**: Same engine code runs Peter, Van Gogh, and Talleyrand scenarios with content-only differences (no engine modification)
- **Anti-bias engineering**: 8-rule self-evaluation framework documented in `docs/HARNESS.md`

---

## What I Built

### Engine (Python)
- 4-layer architecture (Engine + World + Story Output + Observer)
- 35+ engine modules with strict architectural rules
- Hazard-driven event system with deterministic seed control
- Pattern-Oriented Modeling (POM) validation framework

### Visualization (Vanilla JS + SVG)
- Self-contained Visual Explorer (~700 lines, 0 external deps)
- 4 view modes (single-run / cross-seed / candidate panel / packet panel)
- Color-encoded state/mode/salience system
- Cross-seed small multiples with outcome banner

### Documentation
- 4-layer architecture spec
- Self-evaluation framework (8 rules: null hypothesis, alternative explanations, falsification paths, etc.)
- Schema versioning (v1 + cross_seed_v1)
- 5-minute internal demo package (script + cheat sheet + limitations + checklist)

### Process
- Phase-based development (7 phases from MVP to fork decision)
- Each phase: success/failure criteria + stop rule + validation
- Self-correcting loop pattern (autonomous iterations with explicit forbidden lists)

---

## Limitations

- **Single-seed bias** in some validation runs (validation evidence in cross-seed view only)
- **Sacred dynamics** (one scenario family) is harder to surface salience for — encoding is tuned for external-pressure dynamics
- **Story panel placeholder** — narrative renderer is intentionally frozen (separate CLI tool exists for story generation)
- **Internal scope only** — UI is minimal, mobile / responsive untested
- **Cross-seed limited to single anchor** in current data

→ Detailed limitations documented in `docs/demo/KNOWN_LIMITATIONS_V1.md`.

---

## Next Steps

**Short-term** (1–2 weeks):
- Stabilize Visual Explorer v0.2
- Capture demo GIF / screenshots
- Refine portfolio-facing documentation
- Plan v0.2 roadmap

**Mid-term** (1–3 months, separate decision):
- Multi-anchor cross-seed expansion
- Cross-scenario validation (Van Gogh cross-seed)
- Visual encoding tuning for "quiet" dynamics

**Long-term** (separate fork decision):
- Option 1: Visual Explorer as observable world engine
- Option 2: Story / IP asset development (renderer restart)
- Option 3: Simulation research / paper validation
- Option 4: Playable prototype (intervention / what-if)

---

## License & Attribution

(TBD — to be decided before public release)

---

**Status**: v0.1 frozen. Visual Explorer v0.2 demo-ready. Internal use only.

**Repository**: (to be decided — private vs public, branch strategy)
