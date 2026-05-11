# WITNESS — Portfolio Asset Checklist

> External-facing asset preparation. Code 0 변경. 본 doc은 *checklist only* — 실제 asset 캡처는 별도 directive 시.

---

## 0. Asset categories

1. Screenshots (3 필요)
2. GIFs (3 필요)
3. Architecture diagram (1 필요, README용)
4. Statistics / numbers
5. Code path references
6. Public release pre-check

---

## 1. Screenshots (3)

### Screenshot 1 — Single-run replay
- **Source**: `http://localhost:8000/visual/explorer.html` (Peter baseline, default state)
- **Target tick**: 15 (or 142 — both have score-3 markers)
- **What's visible**: SVG canvas with 12 dots + 3 zones, timeline-bar with 5 red markers visible, candidate panel with story_ready filter on
- **Filename**: `screenshot_01_single_run_replay.png`
- **Purpose**: Cover image / "what does it look like" first impression
- **Caption**: *"Single-run replay: 200 ticks of agent state, with timeline markers showing high-salience moments."*

### Screenshot 2 — Cross-seed comparison
- **Source**: `http://localhost:8000/visual/explorer.html` (peter_scarcity_triple, cross-seed view)
- **What's visible**: Outcome banner ("REC 3 · PARTIAL 1 · SAT 1"), 5 horizontal seed rows with mini-timelines + outcome tags
- **Filename**: `screenshot_02_cross_seed_comparison.png`
- **Purpose**: "Configuration sensitivity" key claim visualization
- **Caption**: *"Cross-seed view: same configuration produces different outcome distributions across 5 seeds."*

### Screenshot 3 — Different scenario family
- **Source**: `http://localhost:8000/visual/explorer.html` (vangogh_sacred_baseline)
- **What's visible**: Timeline mostly dim yellow (no red/orange markers), all 6 candidates gray
- **Filename**: `screenshot_03_different_dynamics.png`
- **Purpose**: "System honestly shows when dynamics differ" message
- **Caption**: *"Different scenario family: sacred dynamics produce 'quiet flow' — the system categorizes them as low-activity rather than auto-tuning to fake salience."*

---

## 2. GIFs (3)

### GIF 1 — Timeline scrubbing (~5 sec loop)
- **Action**: Drag timeline slider from tick 0 to 199
- **Source**: explorer.html (Peter baseline)
- **What's visible**: Dots and zones change color/size as tick advances, score-3 markers visible on timeline
- **Filename**: `gif_01_timeline_scrub.gif`
- **Size target**: < 2 MB
- **Purpose**: "World flow visualization in motion"

### GIF 2 — Candidate click → tick jump + range overlay (~3 sec loop)
- **Action**: Click candidate `C03_t142` in right panel
- **What's visible**: Tick cursor jumps to 142, blue rectangle overlay appears on timeline, packet panel updates with rationale + signals
- **Filename**: `gif_02_candidate_to_packet.gif`
- **Size target**: < 1.5 MB
- **Purpose**: "Curated candidate workflow"

### GIF 3 — Cross-seed view + seed click (~5 sec loop)
- **Action**: Click seed 0 row, then seed 3 row
- **What's visible**: Selected seed highlight + side panel updates with that seed's candidate count
- **Filename**: `gif_03_cross_seed_compare.gif`
- **Size target**: < 2 MB
- **Purpose**: "Configuration sensitivity in action"

---

## 3. Architecture diagram (1, README용)

### Diagram — 4-layer pipeline
- **Format**: SVG (preferred) or PNG (1200px wide minimum)
- **Source**: `docs/portfolio/ARCHITECTURE_FOR_PORTFOLIO.md` §1 layer diagram (현재 ASCII, 그래픽으로 변환)
- **Filename**: `architecture_4_layer.png` 또는 `.svg`
- **Boxes**:
  1. Simulation Engine (multi-agent state + hazard + trigger)
  2. Observer Snapshot Layer (8 salience tags)
  3. Candidate Extraction / Curation (3 use modes)
  4. Visual Explorer (vanilla JS + SVG)
- **Side block**: Packet / Story side panel
- **Arrows**: snapshots → candidates → JSON → click
- **Style**: Clean, monochrome or 2-color, no decorative elements
- **Caption (when used in README)**: *"WITNESS 4-layer architecture: each layer is additive (later layers don't modify earlier ones)."*

---

## 4. Statistics / numbers (README용)

### Key metrics to highlight
- ✅ **2,640+ unit tests** (`pytest -m 'not slow and not archived'`)
- ✅ **97%+ coverage** on critical modules
- ✅ **0 external dependencies** in visualization layer
- ✅ **4 layers, ~40 modules**
- ✅ **3 scenarios, 1 engine** (Peter, Van Gogh, Talleyrand — same engine code)
- ✅ **5 seeds × 200 ticks** cross-seed visualization
- ✅ **8 salience tag types** + **3 candidate use modes**

### Performance numbers (engine)
- Peter: ~1,001 ticks/sec, ~2.3 MB memory
- Van Gogh: ~1,267 ticks/sec, ~1.7 MB memory

### Test execution
- Fast suite: ~30s
- Full suite: ~13 min
- 3-tier execution: fast / domain / full

---

## 5. Key code paths (for code review)

### Entry points
- `engine/observer/` — Observer snapshot + candidate extraction
- `engine/observer/candidate_curation.py` — 3-bucket curation pipeline
- `scripts/observer/candidate_packet.py` — packet builder (6-field format)
- `scripts/visual/export_dot_observer_data.py` — JSON exporter (schema v1)
- `scripts/visual/export_cross_seed_visual_data.py` — cross-seed exporter (schema cross_seed_v1)
- `visual/explorer.html` — single-entry visual explorer (~700 lines)

### Architecture rules
- `CLAUDE.md` — architectural constraints (no domain hardcoding in engine layer)
- `docs/HARNESS.md` — 8-rule self-evaluation framework

### Validation
- `tests/test_observer/` — 212 Observer + Pipeline + Curation tests
- `tests/test_engine/` — engine-level tests
- `engine/observer/candidate_curation.py` 22 tests

---

## 6. Public release pre-check

### Files to hide / redact before public release

#### Sensitive (must hide)
- ❌ `progress.md` — daily work log (personal patterns)
- ❌ `lessons.md` — meta-analysis (internal flavor)
- ❌ Lee directive verbatim references — reframe to "design specs"
- ❌ `docs/archive/lee_directives_2026-04-30/` — original directive files
- ❌ HARNESS H1-H8 verbatim (only reframed version OK)

#### Sensitive (review carefully)
- ⚠️ `docs/research/PAPER_DRAFT_V06.md` — working draft (peer review 전 risky)
- ⚠️ `docs/CLAUDE.md` HARNESS section — reframe before public
- ⚠️ Branch C 18 probes raw data — proprietary if external IP

#### Safe to release
- ✅ `engine/`, `scripts/`, `visual/`, `examples/`, `content/`, `tests/` source code
- ✅ `README.md` (after applying portfolio README draft)
- ✅ `DESIGN.md` (4-layer architecture)
- ✅ Visual data: `data/visual/*.json` (canonical run snapshots)
- ✅ Documentation: `docs/portfolio/*` (this folder)
- ✅ Test stats / CI badges

### .gitignore additions for public repo
```
# Internal logs
progress.md
lessons.md

# Archived directives
docs/archive/lee_directives_2026-04-30/
docs/archive/working_notes_*/

# Working drafts
docs/research/PAPER_DRAFT_V06.md
docs/archive/REVIEW_RESPONSE_V1_2.md

# Generated visualization data (regenerate via scripts/)
data/visual/*.json

# IDE / OS
.vscode/
.idea/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
```

### Pre-release checklist
- [ ] Apply PORTFOLIO_README_DRAFT to root `README.md`
- [ ] Reframe CLAUDE.md HARNESS section (or remove from public branch)
- [ ] Review all `*Lee*` references — reframe or remove
- [ ] Generate 3 screenshots (above)
- [ ] Generate 3 GIFs (above)
- [ ] Generate architecture diagram (above)
- [ ] Update `.gitignore` (above)
- [ ] Test fresh clone + setup (1 user, no prior context)
- [ ] Verify 5-min demo runs end-to-end on fresh clone
- [ ] LICENSE file (TBD — MIT / Apache 2 / BSD recommendation)
- [ ] Citation file (CFF) if academic

### Branch strategy options
- **Option A**: Single public branch with internal logs gitignored
- **Option B**: Separate `public` branch (clean history, internal logs deleted)
- **Option C**: Keep private, share via specific URL / temporary access

→ **Decision pending** (별도 directive 시).

---

## 7. Asset capture workflow

### Once Lee approves the asset capture phase

1. Run data export commands (3 lines from `INTERNAL_DEMO_PACKAGE_V1.md` §3.2)
2. Start HTTP server
3. Open `explorer.html` in browser (Chrome / Firefox)
4. Use OS screenshot tool (or Snipping Tool / cmd+shift+4) for static screenshots
5. Use **OBS Studio** or **ScreenToGif** for GIFs (target: 5-10 sec, 10-15 fps)
6. Crop / resize to consistent dimensions
7. Place in `docs/portfolio/assets/` (folder to be created)
8. Reference from `PORTFOLIO_README_DRAFT.md` (after applying)

### Quality criteria
- Screenshots: 1920×1080 or higher, PNG format
- GIFs: < 2 MB each, smooth playback
- Architecture: SVG preferred, PNG fallback at 1200px width

---

## 8. Asset budget estimate

| Asset | Estimated time |
|---|---|
| 3 screenshots | ~30 min |
| 3 GIFs | ~45 min (capture + crop + optimize) |
| Architecture diagram | ~30 min (Excalidraw / Figma) |
| README polish + asset linkage | ~30 min |
| `.gitignore` + branch decision | ~15 min |
| Pre-release checklist verification | ~30 min |
| **Total** | **~3 hours** |

→ All asset capture is *별도 directive*. 현 LOOP에서는 *checklist only*.

---

## 9. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 작업 금지" | ✅ checklist만, capture 안 함 |
| Lee §"새 기능 구현 금지" | ✅ |
| Lee §"내부 로그 삭제하지 말 것" | ✅ progress / lessons 보존 |
| Lee §"archive 정리하지 말 것" | ✅ |

---

## 10. 한 줄 요약

> **Asset checklist = 3 screenshots + 3 GIFs + 1 architecture diagram + statistics 표 + code paths + public release pre-check. 모두 capture는 별도 directive 시. 본 doc은 *checklist only*.**

---

**Versioning**: v1 (this checklist) — 2026-04-30 portfolio repack.
