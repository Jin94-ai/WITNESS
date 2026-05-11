# WITNESS — Portfolio Repack Plan

**Date**: 2026-04-30
**Source**: Lee directive (포트폴리오 재포장, 코드 0 변경)
**Scope**: 외부(채용/리뷰어) 설명용 재포장 plan. 내부 → 외부 용어 변환, 적합 직무 식별.

---

## 0. 한 줄 요약

> **WITNESS는 텍스트 이야기 생성기가 아니라, 다중 에이전트와 집단/사건/세계 상태가 시간에 따라 변화하는 시뮬레이션을 도트 기반 Visual Explorer로 관찰하고, 그 안에서 story candidate를 탐색하는 Agent-based World Simulation Explorer다.**

→ 한 줄 / 30초 / 3분 설명은 §1-§3.

---

## 1. 한 줄 설명

> *"Agent-based world simulation explorer with dot-based visualization for browsing emergent story candidates."*

(한국어): *"다중 에이전트 시뮬레이션이 만들어내는 이야기 후보를 도트 기반 visualization으로 탐색하는 도구."*

---

## 2. 30초 설명

> *"WITNESS is an agent-based world simulation tool that runs historical-figure scenarios (Peter, Van Gogh, Talleyrand) as multi-agent systems. The Visual Explorer visualizes 200 ticks × 12 agents × 3 groups as dots and zones, lets you compare how the same configuration produces different outcomes across seeds, and surfaces story-worthy moments through a curated candidate panel. Built with vanilla JS + SVG (zero external dependencies), tested with 2,640+ unit tests, and informed by self-evaluation framework for anti-bias engineering."*

핵심 keywords: *agent-based simulation, configuration sensitivity, dot visualization, story candidate curation, anti-bias engineering, zero dependencies*.

---

## 3. 3분 설명

> *"WITNESS started as an attempt to model historical figures as multi-agent systems — for example, modeling Peter's denial in the passion narrative as emergent from agent state accumulation, hazard-driven events, and crowd dynamics. Over many iterations the project evolved through multiple layers:*
>
> *1. **Engine layer** — agent state, hazard, trigger, action APIs with 2,640+ tests and strict architectural constraints (no person hardcoding).*
>
> *2. **Story output layer** — template-guided narrative renderer that converts simulation traces to readable text.*
>
> *3. **Observer layer** — captures snapshots and detects salient moments through 8 tag types (cohort split, saturation lock, agent state shift, etc.).*
>
> *4. **Candidate pipeline** — extracts story-worthy moments from snapshots and curates them into 3 buckets (suitable for narrative review, low-activity candidates kept for inspection, observation-only).*
>
> *5. **Visual Explorer** — single HTML entry that visualizes simulation as dots and zones, with timeline scrubbing, salience markers, candidate filter, and side panels showing the rationale for each candidate. Cross-seed view shows how the same configuration leads to different outcomes (REC 3 / PARTIAL 1 / SAT 1) — directly visualizing configuration sensitivity.*
>
> *Throughout, the project applied anti-bias engineering principles: don't auto-judge story quality, don't claim sensitivity ratios from single-seed runs, document falsification paths explicitly. The result is an internal exploration tool, not a public product — but the architecture and the visualization-for-validation pattern are portable to other domains: game AI, simulation research, or interactive analytics."*

---

## 4. 핵심 기능 4개

| # | 기능 | 외부 설명 |
|---|---|---|
| 1 | **Agent-based simulation engine** | Hazard-driven events, trigger pipeline, multi-agent state evolution. 2,640+ unit tests. |
| 2 | **Visual Observer with timeline scrubbing** | 200-tick replay of 12 agents × 3 groups as SVG dots and zones. Salience markers (low/mid/high), play/pause/timeline-click. |
| 3 | **Cross-seed configuration sensitivity view** | Small multiples comparing 5 seeds — same config produces different outcomes. Directly visualizes configuration sensitivity. |
| 4 | **Curated candidate panel with packet side panel** | Auto-extracted story-worthy moments grouped into 3 use modes; click jumps to tick + shows rationale + signals. |

---

## 5. 보여줄 데모 화면 3개

### 화면 1 — Single-run replay (1.5분)
- Anchor: peter_scarcity_baseline (default)
- Timeline의 5 high-salience marker → click → tick jump
- Candidate panel filter (3-bucket toggle)
- Selected packet panel (rationale + signals)

### 화면 2 — Cross-seed comparison (1.5분)
- Anchor toggle → peter_scarcity_triple
- Cross-seed view → outcome banner (REC 3 / PARTIAL 1 / SAT 1)
- 5 seed rows side-by-side
- Click seed → candidate panel updates

### 화면 3 — Different scenario family (1분)
- Anchor toggle → vangogh_sacred_baseline
- "Quiet flow" 시각적 대비 (timeline yellow only, all candidates low-activity)
- 메시지: *"system does not auto-judge — different dynamics get different classification"*

---

## 6. 기술 스택 (외부 표현)

### Backend
- **Python 3.11+** (engine, simulation runtime)
- **Pydantic** (data validation)
- **NumPy / SciPy** (statistical analysis)
- **pytest** (2,640+ tests)
- **Ruff + mypy** (linting + type checking)

### Visualization
- **Vanilla JS + SVG** (zero external dependencies)
- **Self-contained HTML** (HTTP server only — no build step)

### Optional / supporting
- **SALib** (sensitivity analysis)
- **UMAP / HDBSCAN** (clustering — research mode)

### CI / dev
- GitHub Actions (test + coverage)
- Schema versioning (data export contracts)

---

## 7. 포트폴리오에서 강조할 역량

### Engineering rigor
- 2,640+ tests with strict architectural constraints (no domain hardcoding in engine layer)
- Test-driven schema versioning
- Type checking + linting in CI

### System design
- 4-layer architecture (Engine / Story Output / Observer / Visual)
- Additive layer pattern (new layer doesn't break existing layers)
- Self-contained components (no external dependencies)

### Quantitative thinking
- Configuration sensitivity validation (cross-seed evidence)
- Anti-bias engineering (single-seed conditioning warnings, falsification paths)
- Statistical rigor (5+ seed ensemble for sensitivity claims)

### Visualization design
- Dot-based encoding (color = state, size = intensity, stroke = salience)
- Small multiples for cross-seed comparison
- Timeline marker hierarchy (3-level salience)

### Self-evaluation framework
- Designed pattern for autonomous self-correction (8 anti-bias rules)
- Documentation pattern: *what could still be wrong / what I did NOT try / alternate interpretations*

---

## 8. 감춰야 할 내부 용어 / 문서

### 내부 용어 (포트폴리오에서 reframe 필수)
- "Lee directive" → "design specification"
- "HARNESS" → "self-evaluation framework"
- "forbidden_now" → "scope constraints"
- "Branch C" → "configuration sensitivity validation"
- "Case A / Case BP-A / Case F-A" → "validation result"
- "관찰기 ≠ 평가기" → "observer-not-evaluator design principle"
- "story_ready" → "candidate suitable for narrative review"
- "low_activity_hold" → "low-activity candidate kept for inspection"
- "observation_only" → "candidate kept for observation, not narrative use"

### 비공개 유지 권장 (internal-only)
- `progress.md` — 일자별 작업 log (개인 작업 패턴 노출)
- `lessons.md` — 자기반성 / 메타 분석
- `docs/CLAUDE.md` HARNESS section verbatim (외부에는 reframe된 버전만)
- `docs/archive/lee_directives_2026-04-30/` — 19 historical directive
- `docs/archive/working_notes_*/` — working notes
- `docs/research/PAPER_DRAFT_V06.md` working draft (peer review 전)

### 공개 OK
- `engine/`, `scripts/`, `visual/`, `examples/`, `content/`, `tests/` 코드
- `README.md` (정리된 외부용으로 변경 — *별도 LOOP에서 작업*)
- `DESIGN.md` 4-layer architecture diagram
- 2,640+ tests stats
- `data/visual/*.json` (canonical run data)
- `visual/explorer.html` (live demo)

---

## 9. 공개 가능 / 비공개 유지 항목

### 공개 가능 (포트폴리오 직접 사용)
- ✅ 4-layer architecture diagram
- ✅ Visual Explorer screenshot/GIF
- ✅ Cross-seed outcome distribution figure
- ✅ Test count + CI badge
- ✅ Tech stack 표
- ✅ "Configuration sensitivity within scenarios" key finding (rephrased)
- ✅ Engine code 일부 (engine/observer/, engine/core/)

### 비공개 유지
- ❌ `progress.md` / `lessons.md` (작업 chronology)
- ❌ Lee directive verbatim
- ❌ HARNESS H1-H8 verbatim (reframed version만 공개)
- ❌ 내부 working notes (archive)
- ❌ Paper working draft (peer review 전)
- ❌ Branch C 18 probes raw data (validation 자료)

---

## 10. 예상 타임라인 (재포장)

본 plan은 *plan only*. 실제 작업은 *별도 directive 시*:

| 단계 | 작업 | 시간 |
|---|---|---|
| **Now** (이번 LOOP) | Repack plan + 6 doc 초안 작성 | ~2시간 |
| Next (별도 directive) | README 외부용 작성 | ~1시간 |
| Next | Architecture diagram (PNG/SVG) | ~30분 |
| Next | Screenshot 3 + GIF 3 | ~1시간 |
| Next | GitHub repo 정리 (.gitignore / commit hygiene) | ~30분 |
| **Total** | | ~5시간 (분산) |

---

## 11. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ 본 plan은 doc only |
| Lee §"루트 README 바로 수정 금지" | ✅ draft만 작성 (별도 LOOP에서 적용) |
| Lee §"public release 작업 금지" | ✅ plan + draft만 |
| Lee §"새 기능 구현 금지" | ✅ |
| Lee §"내부 로그 삭제하지 말 것" | ✅ progress / lessons 보존 |
| Lee §"archive 정리하지 말 것" | ✅ |

---

## 12. 한 줄 요약

> **Portfolio Repack Plan = 7 doc 작성 (이번 LOOP에서). 한 줄/30초/3분 설명, 4 핵심 기능, 3 데모 화면, 기술 스택, 강조 역량, 감춰야 할 내부 용어, 공개 가능 항목 모두 정의. 코드 0 변경. 루트 README는 별도 LOOP에서 적용.**

---

**Versioning**: v1 (this plan) — 2026-04-30 portfolio 재포장 시작.
