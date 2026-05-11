# WITNESS — Demo Guide (Portfolio Version)

> External-facing demo guide for portfolio reviewers / interviewers.

---

## 0. Goal

Run a **5-minute live demo** that shows:
1. The system actually works (not vaporware)
2. The architecture choices were deliberate (not random)
3. The visualization-for-validation pattern is reusable beyond this domain

---

## 1. Run the demo (3 steps)

### Step 1 — Generate visualization data (one-time, ~1 min)
```bash
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
```

### Step 2 — Start HTTP server
```bash
python -m http.server 8000
```

### Step 3 — Open browser
```
http://localhost:8000/visual/explorer.html
```

→ No build step. No npm install. No external dependencies.

---

## 2. Demo screen 1 — Single-run replay (1.5 min)

### What's on screen
- 800×500 SVG canvas with 12 agent dots + 3 group zones
- Timeline bar (200 ticks) below canvas
- Right panel: Candidates list (filterable) + Selected packet (rationale + signals)

### What to show
1. **Default state**: Anchor = `peter_scarcity_baseline`, View = Single-run.
2. **Point at timeline**: "5 red bold markers — these are the high-salience moments."
3. **Click first red marker (tick 15)**: Black cursor jumps. Dots and zones change color/size.
4. **Click candidate `C03_t142` in right panel**:
   - Tick jumps to 142
   - Blue rectangle overlay appears on timeline (the candidate's tick range)
   - Right panel "Selected packet" shows: ID, location, classification, why surfaced, signals
5. **Click filter buttons**: "story_ready" toggle off → only observation/low-activity candidates shown.

### What to explain to reviewer

> *"Everything you see here is auto-extracted by the curation pipeline. The system doesn't auto-judge story quality — it categorizes candidates into 3 use modes and lets a human reviewer decide. The packet on the right shows why each candidate was surfaced (which signals fired). The visualization gives you 'where to look', and the packet gives you 'why it matters' — they're complementary."*

### Key takeaway for reviewer

✅ *Visualization lets you scan 200 ticks in seconds. Text alone would take minutes.*

---

## 3. Demo screen 2 — Cross-seed comparison (1.5 min)

### Setup
1. Anchor dropdown → `peter_scarcity_triple`
2. View toggle → `Cross-seed`

### What's on screen
- Outcome banner at top: `Outcomes: REC 3 · PARTIAL 1 · SAT 1`
- 5 horizontal rows (one per seed), each with mini-timeline + outcome tag
- Right panel shows selected seed's candidates

### What to show
1. **Read the banner**: "REC 3 / PARTIAL 1 / SAT 1 — same configuration, 5 different seeds, 3 different outcome classes."
2. **Compare row colors**: "Green ending = recovery, red ending = saturation, gray = partial. The lane color directly shows each seed's destiny."
3. **Click seed 3 row**: Outcome = SAT. Right panel shows that seed's candidate distribution.
4. **Compare to seed 0 (REC)**: Same config, completely different trajectory.

### What to explain to reviewer

> *"This is configuration sensitivity, visualized directly. Single-seed runs would have given you one outcome and you'd think the system is deterministic. The cross-seed view forces you to see the distribution. The 8th rule of our self-evaluation framework explicitly warns about single-seed conditioning — this view is the practice of that rule."*

### Key takeaway for reviewer

✅ *Anti-bias engineering: visualization that prevents single-seed bias is built into the design.*

---

## 4. Demo screen 3 — Different scenario family (1 min)

### Setup
- Anchor dropdown → `vangogh_sacred_baseline`
- View defaults to Single-run (cross-seed disabled — different anchor doesn't have cross-seed data)

### What's on screen
- Same canvas + timeline structure as screen 1
- BUT: timeline is mostly dim yellow (no red/orange high-salience markers)
- Group zones are nearly static
- All 6 candidates in the panel are gray (low-activity)

### What to show
1. **Compare to screen 1**: "Peter scenario had 5 red markers. This one has 0. Different scenario family, different dynamics."
2. **Point at gray candidates**: "All 6 are classified as 'low-activity candidates kept for inspection'. The system doesn't auto-judge — it just tells you the dynamics are different."
3. **Read the side panel for one candidate**: Sacred-specific events (miracle, prayer) appear in active events, even though salience markers don't fire.

### What to explain to reviewer

> *"The 8 salience tags in our system are tuned for external-pressure dynamics (cohort split, saturation lock, etc.). Sacred dynamics are internal/contemplative — they don't trigger those tags. Rather than auto-tuning the system to force salience markers, we leave the dynamics as-is and let the categorization show the difference. This is the observer-not-evaluator design principle in action."*

### Key takeaway for reviewer

✅ *System honestly shows when its tooling is mismatched to the domain — it doesn't fake importance to look good.*

---

## 5. Wrap (1 min)

### 3-layer recap
> *"Three layers, three roles:*
> *• Visual = where to look (timeline markers, lane colors, candidate filter)*
> *• Packet = why it matters (rationale, signals, classification)*
> *• Story = how it reads (separate CLI tool, not integrated by design)"*

### One-line summary
> *"Visualization for validation: dots and zones aren't decoration, they're the mechanism for spotting configuration-sensitive emergent behavior in agent-based simulations."*

---

## 6. 5-minute demo time budget

| Time | Activity | Cumulative |
|---|---|---|
| 0:00 – 0:30 | Intro (one-line + URL) | 0:30 |
| 0:30 – 2:00 | Screen 1: Single-run replay | 2:00 |
| 2:00 – 3:30 | Screen 2: Cross-seed comparison | 3:30 |
| 3:30 – 4:40 | Screen 3: Different scenario family | 4:40 |
| 4:40 – 5:00 | Wrap (3-layer recap + one-liner) | 5:00 |

---

## 7. Anticipated reviewer questions

### Q. "Why dots? Why not real characters / icons?"
> *"Dots scale better. With 12 agents updating every tick, you need a representation that doesn't draw attention away from the dynamics. Color + size + stroke encoding gives you state, intensity, and salience without the cognitive cost of 'who is this character'. The point is the system, not the avatar."*

### Q. "Why no React?"
> *"Three reasons: (1) zero build step — `python -m http.server` is the only requirement, (2) no dependency footprint — the entire visualization is one HTML file, (3) the demo runs offline once data is exported. For an internal exploration tool, framework overhead would be a liability."*

### Q. "How would this scale to 1000 agents?"
> *"It wouldn't, in the current implementation — SVG renders 12 dots cleanly but 1000 would need Canvas. The architecture is layered, though, so swapping the visual layer without touching engine/observer/curation is straightforward. Cross-seed at 1000 agents would also need data export trimming (current export is 824 KB for 12 agents)."*

### Q. "What's the engine actually doing?"
> *"Hazard-driven Poisson process: P(event) = 1 - exp(-h·dt). Agent state accumulates fear, hope, shame, etc. Triggers fire when accumulated state crosses thresholds. Events propagate through agent interactions and crowd dynamics. The trace gets snapshotted per tick, salience-tagged, and curated into candidates."*

### Q. "How is this different from a game?"
> *"No player. No goal state. No win/lose. The 'observer-not-evaluator' principle means the system surfaces moments that are *salient by signal* — it doesn't pre-classify them as good or bad story material. The visual explorer is for *exploration*, not *gameplay*. (Future work could add intervention / what-if, but that's a separate fork decision.)"*

### Q. "What about mobile?"
> *"Desktop only. Visual layer assumes 1280×800+ window. Responsive design is on the v0.2 backlog but not in current scope."*

### Q. "How do I know the validation is real?"
> *"2,640+ unit tests in `tests/`. Run `pytest -m 'not slow and not archived'` for the fast suite (~13 min). Cross-scenario validation: same engine code runs Peter, Van Gogh, and Talleyrand scenarios with content-only differences. Phase 3.05 Rubric directive (29 cycle) adds 124+ rubric tests + doc-reality automation (130 internal links auto-verified)."*

---

## 8. Live demo cheat sheet

### Critical anchor + tick + candidate IDs
- **Peter baseline**: high-salience ticks at 15, 25, 142, 146, 147; 5 story_ready candidates
- **Peter triple cross-seed**: outcome banner "REC 3 · PARTIAL 1 · SAT 1"; click seed 3 (SAT — quietest one)
- **Van Gogh sacred**: 0 high-salience markers; all 6 candidates gray (low-activity)

### Don't say
- "Story generator" → say *"world simulation explorer"*
- "AI" → say *"agent-based simulation"* (no ML in this layer)
- "Game" → say *"interactive visualization"*
- "Validates" → say *"surfaces"* or *"shows"*

### Do say
- "Configuration sensitivity"
- "Anti-bias engineering"
- "Observer-not-evaluator"
- "Additive layer architecture"
- "Zero external dependencies"

---

## 9. Compressed 90-second elevator version

If reviewer has only 90 seconds:

1. **0:00–0:15**: Open `explorer.html`. *"Agent-based simulation explorer."*
2. **0:15–0:45**: Point at timeline 5 red markers + click one. *"Salience-tagged moments, surfaced automatically."*
3. **0:45–1:15**: Toggle to cross-seed view. *"Same config, 5 seeds, 3 outcomes — configuration sensitivity directly visible."*
4. **1:15–1:30**: Wrap. *"Visualization for validation, observer-not-evaluator principle, zero deps."*

---

## 10. After the demo

### Recommended follow-up reading order
1. `docs/portfolio/ARCHITECTURE_FOR_PORTFOLIO.md` — deeper architecture
2. `docs/portfolio/PORTFOLIO_README_DRAFT.md` — full project README
3. `docs/HARNESS.md` — self-evaluation framework details (advanced)
4. `engine/observer/` source — code review entry point

### What to skip (until specifically asked)
- `progress.md` — internal work log (chronological, not curated)
- `lessons.md` — meta-analysis (advanced, internal-flavored)
- `docs/archive/` — historical artifacts

---

**Versioning**: v1 (this guide) — 2026-04-30 portfolio repack.
