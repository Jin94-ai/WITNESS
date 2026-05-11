# Witness Canonical Manifest

**Date:** 2026-04-27 (v1) / 2026-04-30 (v2 — Phase 1-7 완료 후 갱신)
**Purpose:** "이 프로젝트를 이해하려면 무엇을 먼저 봐야 하는가" — 다이어트 후 길찾기
**Source:** 이전: `docs/WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md` (archive). v2: Phase 1-7 정리 결과.

> 📂 **빠른 전체 nav**: [docs/INDEX.md](INDEX.md) (master index, 모든 카테고리) | [docs/SUMMARY_PHASES_1_TO_7.md](SUMMARY_PHASES_1_TO_7.md) (Phase 1-7 누적 결과)

---

## 0. 사용법

이 문서는 두 가지 용도다.

1. **새 사람이 프로젝트 들어왔을 때**: §1-§4 순서로 읽으면 30분 안에 전체 그림 파악
2. **다이어트 / 정리 작업 시**: 여기 명시된 항목은 **canonical**, 즉 archive 금지

`canonical`이라는 표시는 "현재 기준으로 살아있는 진실"을 뜻한다.
`legacy / archive / superseded`는 역사적 기록.

---

## 1. 시작 — 프로젝트 정체성과 행동 강령

이 5개 파일을 먼저 읽는다. 30분 이하.

| 파일 | 역할 |
|---|---|
| [README.md](../README.md) | 프로젝트 소개 + 빠른 실행 |
| [CLAUDE.md](../CLAUDE.md) | AI 작업 시 행동 강령 (HARNESS H1-H8 포함) |
| [DESIGN.md](../DESIGN.md) | 4-layer 아키텍처 + v0.7 설계 |
| [docs/HARNESS.md](HARNESS.md) | H1-H7 anti-bias engineering 상세 |
| [docs/ODD_PROTOCOL.md](ODD_PROTOCOL.md) | ODD (Overview-Design-Details) 방법론 |

---

## 2. 엔진 코드 — KEEP_CORE

수정 시 항상 ablation + 검증 필요.

### 2.1 핵심 엔진
- [engine/core/](../engine/core/) — AgentState, ExternalEvent, Hazard, Trigger, Action, Environment
- [engine/rules/](../engine/rules/) — 상태 전이 규칙
- [engine/simulation/](../engine/simulation/) — SimulationWorld, Runner, batch, statistics, POM, calibration
- [engine/persona/](../engine/persona/) — motif, profile, selector
- [engine/population/](../engine/population/) — role_cluster, transitions
- [engine/world/](../engine/world/) — micro_world, crowd_dynamics, spatial, information
- [engine/rendering/](../engine/rendering/) — narrator, scripture, trace_emitter
- [engine/io/](../engine/io/) — loader, trajectory
- [engine/rubric/](../engine/rubric/) — rubric_evaluator, critic chain
- [engine/person/](../engine/person/) — PersonV3Loop (legacy v3 pipeline)
- [engine/policies/](../engine/policies/) — policy + neural

### 2.2 콘텐츠 (Biography Packs)
- [content/peter/](../content/peter/) — 베드로
- [content/judas/](../content/judas/), [content/caiaphas/](../content/caiaphas/), [content/crowd/](../content/crowd/) — 베드로 시나리오 동반
- [content/vangogh/](../content/vangogh/), [content/gauguin/](../content/gauguin/), [content/theo/](../content/theo/) — 반 고흐
- [content/talleyrand/](../content/talleyrand/) — 정치
- [content/jesus/](../content/jesus/), [content/interventions/](../content/interventions/) — canonical interventions
- [content/shared/](../content/shared/) — 정경 말씀, triggers
- [content/worlds/](../content/worlds/) — 세계 설정

### 2.3 별도 영역 (보류 중, 건드리지 않음)
- [world/](../world/) — top-level v2.0 Spike 1A (689 KB, tests/test_world에서 import 중)

---

## 3. 테스트 — 모두 KEEP

- [tests/test_engine/](../tests/test_engine/) — 핵심 엔진 테스트
- [tests/test_person/](../tests/test_person/) — Peter v3 시나리오
- [tests/test_peter/](../tests/test_peter/) — Peter integration
- [tests/test_world/](../tests/test_world/) — world v2.0 Spike
- [tests/test_world_process/](../tests/test_world_process/) — 무인물 검증
- [tests/test_rubric/](../tests/test_rubric/) — rubric critics
- [tests/test_persona/](../tests/test_persona/), [test_population/](../tests/test_population/), [test_action/](../tests/test_action/), [test_talleyrand/](../tests/test_talleyrand/), [test_vangogh/](../tests/test_vangogh/)

테스트 수집: `pytest --collect-only` → 1647 tests collected.

---

## 4. 문서 — canonical만 (archive 영역 별도)

### 4.1 Spec / 설계 (KEEP)
- [docs/specs/](specs/) — 16 spec docs
  - DESIGN_LATENT_DRIVE, TRACE_SCHEMA, V3_REDESIGN, V3_PHASE2_*, WORLD_DESIGN, WORLD_SPIKE_2/5, WITNESS_SPIKE_6_*, SCENARIO_TEMPLATE
- [docs/research/](research/) — 연구 history
  - RESEARCH.md, PAPER_DRAFT_V06, PAPER_OUTLINE_V05, ITERATION_CLASSIFICATION, PROJECT_DIRECTION_v2
- [docs/persona_engine/](persona_engine/) — persona spec (9 docs)
- [docs/world_engine/](world_engine/) — world engine reframe (4 docs)

### 4.2 B-direction canonical (현재 cycle)
다이어트 후 보존된 핵심 산출물:

#### 현재 직접 활용 (Iter 176-184 cycle)
- [docs/b_direction/COMPONENT_LEDGER.md](b_direction/COMPONENT_LEDGER.md) — v1.1
- [docs/b_direction/STATE_FIELD_STATUS.md](b_direction/STATE_FIELD_STATUS.md)
- [docs/b_direction/KERNEL_GAPS.md](b_direction/KERNEL_GAPS.md)
- [docs/b_direction/SACRED_STATUS_NOTE.md](b_direction/SACRED_STATUS_NOTE.md)
- [docs/b_direction/WITNESS_INTERNAL_BRANCH_CYCLE_COMPLETE.md](b_direction/WITNESS_INTERNAL_BRANCH_CYCLE_COMPLETE.md)
- [docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md](b_direction/READABILITY_BLIND_PROTOCOL_V2.md)
- [docs/b_direction/READABILITY_BLIND_RESULTS_V2.md](b_direction/READABILITY_BLIND_RESULTS_V2.md)
- [docs/b_direction/READABILITY_PILOT_4.md](b_direction/READABILITY_PILOT_4.md)
- [docs/b_direction/ANNOTATED_PROBE_FORMAT.md](b_direction/ANNOTATED_PROBE_FORMAT.md)
- [docs/b_direction/PROBE_STATS_CHARACTERIZATION.md](b_direction/PROBE_STATS_CHARACTERIZATION.md)
- [docs/b_direction/SCRIPT_STATUS.md](b_direction/SCRIPT_STATUS.md) ← 이번 작업
- [docs/b_direction/READABILITY_INFRA_SUMMARY.md](b_direction/READABILITY_INFRA_SUMMARY.md) — Iter 185-191 readability infra 1-page navigation

#### Cycle 이전 reference (현재도 활용)
- [docs/b_direction/ITER_INDEX.md](b_direction/ITER_INDEX.md) — 50+ Iter 색인
- [docs/b_direction/BRANCH_B_C_SUMMARY.md](b_direction/BRANCH_B_C_SUMMARY.md)
- [docs/b_direction/INERT_RESERVE_AUDIT.md](b_direction/INERT_RESERVE_AUDIT.md) — Iter 89, partial stale
- [docs/b_direction/READABILITY_BLIND_PROTOCOL.md](b_direction/READABILITY_BLIND_PROTOCOL.md) — v1
- [docs/b_direction/READABILITY_BLIND_RESULTS.md](b_direction/READABILITY_BLIND_RESULTS.md) — v1
- [docs/b_direction/READABILITY_BLIND_GROUND_TRUTH.md](b_direction/READABILITY_BLIND_GROUND_TRUTH.md)
- [docs/b_direction/ITER_124_SCALE_TIERS_CANONICAL.md](b_direction/ITER_124_SCALE_TIERS_CANONICAL.md)
- [docs/b_direction/ITER_135_RUMOR_MECHANISM_CORRECTED.md](b_direction/ITER_135_RUMOR_MECHANISM_CORRECTED.md)
- [docs/b_direction/ITER_167_DIRECTIVE_CYCLE_SYNTHESIS.md](b_direction/ITER_167_DIRECTIVE_CYCLE_SYNTHESIS.md)
- [docs/b_direction/FINDINGS_SUMMARY_ITER_1_63.md](b_direction/FINDINGS_SUMMARY_ITER_1_63.md) — latest in 1-63 chain
- [docs/b_direction/FINDINGS_SUMMARY_ITER_64_74.md](b_direction/FINDINGS_SUMMARY_ITER_64_74.md)
- [docs/b_direction/FINDINGS_SUMMARY_ITER_75_86.md](b_direction/FINDINGS_SUMMARY_ITER_75_86.md)
- [docs/b_direction/WORLD_BUILDING_PROGRESS_v2.md](b_direction/WORLD_BUILDING_PROGRESS_v2.md)
- [docs/b_direction/WORLD_MEMORY.md](b_direction/WORLD_MEMORY.md)
- [docs/b_direction/POST_FREEZE_BRANCH_DECISION.md](b_direction/POST_FREEZE_BRANCH_DECISION.md)
- [docs/b_direction/WORLD_PROCESSES.md](b_direction/WORLD_PROCESSES.md)
- ITER_120-160 era docs (~10 files): KEEP as recent

#### Iter retrospectives (Iter 176-184)
- ITER_176_STEP_A1_FORMAT_STANDARDIZATION.md
- ITER_177_STEP_A2_PILOT_4.md
- ITER_178_STEP_A3_PROTOCOL_V2.md
- ITER_179_STEP_B1_LEDGER_UPDATE.md
- ITER_180_STEP_B2_FIELD_DOCSTRINGS.md
- ITER_181_STEP_B3_SACRED_NOTE.md
- ITER_182_STEP_B4_KERNEL_GAPS.md

### 4.3 Probes (현재 표준)
- [docs/b_direction/readability_probes/](b_direction/readability_probes/) — P1-P12 original + ANNOTATED
- [docs/b_direction/readability_probes_annotated/](b_direction/readability_probes_annotated/) — 정리본
- [docs/b_direction/readability_pilot/](b_direction/readability_pilot/) — PILOT_1-4 (4-probe pilot)
- [docs/b_direction/probe_runs/](b_direction/probe_runs/) — 122 JSON outputs (legacy raw, but kept until §3.3 archive round)

### 4.4 Person engine (Peter v3)
- [docs/person/](person/) — V3 phase docs (12 files), DATA_PIPELINE_v2 spec
- [docs/person/diagnostics/](person/diagnostics/) — separability, environment_responsiveness, etc.
- [docs/person/v3_measurement/](person/v3_measurement/) — rubric 측정 산출물 (5 files)
- [docs/person/paper_data/](person/paper_data/) — 8 PNG figures (논문 자산)

### 4.5 World engine (v2.0 Spike)
- [docs/world/](world/) — Spike 1-5 review docs + paper_data

### 4.6 Top-level docs (root *.md)
- README.md, CLAUDE.md, DESIGN.md, lessons.md, progress.md
- WITNESS_IMPROVEMENTS_AND_UPDATED_LOOP.md (active loop directive)
- WITNESS_NEXT_STEPS_WEAKNESSES_AND_IMPROVEMENTS.md
- WITNESS_POST_LOOP_FREEZE_AND_NEXT_STEPS.md
- WITNESS_V3_PHASE_G_CALIBRATION.md
- WITNESS_WORLD_BUILDING_ELEMENTS_AND_SCALE.md
- WITNESS_WORLD_FLOW_LOOP.md

### 4.7 Diet 관리 docs (이번 작업 산출물)
- [docs/PROJECT_DIET_ANALYSIS.md](PROJECT_DIET_ANALYSIS.md)
- [docs/WITNESS_PROJECT_DIET_ACTIONS.md](WITNESS_PROJECT_DIET_ACTIONS.md)
- [docs/WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md](WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md)
- [docs/CANONICAL_MANIFEST.md](CANONICAL_MANIFEST.md) — this doc
- [docs/ARCHIVE_POLICY.md](ARCHIVE_POLICY.md) — operational rules

---

## 5. Scripts — active만

### 5.1 데이터/논문 파이프라인 (KEEP)
- [scripts/data_pipeline/](../scripts/data_pipeline/) — baseline_harvest, build_final_dataset, fidelity_check, separability, etc.
- [scripts/v3_measurement/](../scripts/v3_measurement/) — run_peter_v3, run_judas_v3, run_vangogh_v3, calibrate_thresholds, generate_sanity_check
- [scripts/paper_numbers.py](../scripts/paper_numbers.py), [paper_figures.py](../scripts/paper_figures.py), [world_numbers.py](../scripts/world_figures.py), [baseline_comparison.py](../scripts/baseline_comparison.py), [hazard_scaling.py](../scripts/hazard_scaling.py), [counterfactual_baseline.py](../scripts/counterfactual_baseline.py), [chain_detection_v2.py](../scripts/chain_detection_v2.py), [svm_comparison.py](../scripts/svm_comparison.py), [demo_spike6_peter_neural.py](../scripts/demo_spike6_peter_neural.py)

### 5.2 B-direction (분류 완료, Phase A+B+C 실행됨)
**Active building blocks + current cycle (19개)**: SCRIPT_STATUS.md §3, §4 참조.
**Legacy keep (8개)**: SCRIPT_STATUS.md §5 참조.
**Archive candidates**: SCRIPT_STATUS.md §6 참조.
- Phase A 실행 (v1.1, 2026-04-27): 55 leaf `run_loop_iter*.py` → `archive/b_direction_legacy/scripts_iter_1_88/`
- Phase B 실행 (v1.2, 2026-04-28): 19 of §6.2 → `archive/b_direction_legacy/scripts_iter_91_119/` (UNSURE 3 preserved)
- Phase C 실행 (v1.3, 2026-04-28): 14 of §6.3.1 ARCHIVE_CANDIDATE → `archive/b_direction_legacy/scripts_phase_c_oneoffs/` (7 KEEP_CANDIDATE preserved)
- 현재 scripts/b_direction count: 37 (from 125)

### 5.3 Examples + Benchmarks (KEEP)
- [examples/demo.py](../examples/demo.py), [demo_v07.py](../examples/demo_v07.py), [demo_phased.py](../examples/demo_phased.py)
- [benchmarks/bench_simulation.py](../benchmarks/bench_simulation.py)

### 5.4 World demos (보류 — Phase 3)
- `scripts/demo_world_*.py`, `scripts/demo_spike4_interventions.py`, `scripts/world_numbers.py`, `scripts/world_figures.py`

---

## 6. 데이터 — latest만 working area에

### 6.1 Working area (KEEP)
- [data/person/trajectory_1000_v4_final.jsonl](../data/person/trajectory_1000_v4_final.jsonl) — latest dataset (14 MB)
- [data/reference/witness_trajectories_45_v2.json](../data/reference/witness_trajectories_45_v2.json) — reference v2 (1.7 MB)
- [data/reference/evaluation_results.json](../data/reference/evaluation_results.json) — rubric 비교 baseline
- [data/reference/distribution_analysis.json](../data/reference/distribution_analysis.json)
- [data/reference/calibrated_thresholds.json](../data/reference/calibrated_thresholds.json)
- [data/person/pipeline_v2/](../data/person/pipeline_v2/) — pipeline outputs (보류 중)
- [data/person/abc_snapshots/](../data/person/abc_snapshots/) — ABC calibration (보류 중)
- [data/README.md](../data/README.md)

### 6.2 Archive (외부 보관 가능)
- archive/data_legacy/trajectory_1000.jsonl (v1)
- archive/data_legacy/trajectory_1000_v2.jsonl (v2)
- archive/data_legacy/trajectory_1000_v3_varied.jsonl (v3)
- archive/data_legacy/witness_trajectories_45.json (reference v1)
- archive/data_legacy/pipeline_v1/

---

## 7. 외부에서 보는 archive

`archive/` 안의 파일도 가끔 필요. canonical 문서가 인용하는 archive 파일:

| Canonical doc | References (archive) |
|---|---|
| (former) ITER_INDEX.md | now in `docs/archive/iter_logs/ITER_INDEX.md` |
| SACRED_STATUS_NOTE.md §12 | ITER_95, ITER_108, ITER_113 (path refs, archived 2026-04-27) |
| (former) WORLD_BUILDING_PROGRESS_v2.md | now in `docs/archive/branch_c_working/` (table mentions only) |
| BRANCH_C_FIRST_EVIDENCE_SUMMARY.md | references S2/S3/S4/S5 results in `docs/archive/branch_c_working/` |
| LEE_GATE_2026-04-28_BRANCH_C.md | references files in `docs/archive/working_notes_2026-04/` |

archive/README.md + `docs/archive/{root_2026-04, iter_logs, branch_c_working, readability_blind, full_eval_n12, working_notes_2026-04}/`: 위치 + 복구 방법.

---

## 8. 길찾기 (Cheat Sheet)

| 질문 | 답 |
|---|---|
| 이 프로젝트 어떤 거야? | README.md + DESIGN.md |
| 어떻게 작업하면 돼? | CLAUDE.md (행동 강령, H1-H8 포함) |
| 베드로 시뮬은 어디? | content/peter/ + tests/test_peter/ |
| 현재 핵심 결정 근거는? | b_direction/COMPONENT_LEDGER.md, KERNEL_GAPS.md, SACRED_STATUS_NOTE.md |
| Branch C 1차 evidence? | docs/SESSION_SUMMARY_2026-04-28_BRANCH_C_AUTONOMOUS.md → b_direction/BRANCH_C_FIRST_EVIDENCE_SUMMARY.md (v4.4) |
| Lee 결정 대기? | b_direction/LEE_GATE_2026-04-28_BRANCH_C.md (5 옵션) |
| 외부 평가 준비됐나? | b_direction/BRANCH_C_18_PROBES_BLIND_PACKAGE.md (seed=0 disclosure 추가 필요) |
| 89+ iter 역사? | docs/archive/iter_logs/ITER_INDEX.md (archived 2026-04-28) |
| 이전 round (FULL_EVAL_N12 등)? | docs/archive/full_eval_n12/, docs/archive/readability_blind/ |
| 데이터 어디? | data/person/trajectory_1000_v4_final.jsonl + data/reference/*_v2.json |
| 논문 figure? | docs/person/paper_data/ + docs/world/paper_data/ |
| 논문 working draft? | docs/research/PAPER_DRAFT_V06.md (Appendix G = Branch C 1차 evidence) |
| Scripts 분류? | b_direction/SCRIPT_STATUS.md |
| Archive 정책? | docs/ARCHIVE_POLICY.md + archive/ subdirectory list (LOOP 82) |

---

## 9. Versioning

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-27 | 초기 manifest -- 이번 다이어트 (Phase 1+2+ITER_91-119 archive) 후 |
| v1.1 | 2026-04-28 | autonomous-mode: §5.2 Phase B (19 scripts) 실행 반영. archive/README.md v1.3 참조. |
| v1.2 (this) | 2026-04-28 | post-Branch C autonomous session cleanup: 루트 6 WITNESS_*.md → archive/root_2026-04/, ITER_*.md 40개 → archive/iter_logs/, Branch C working 18개 → archive/branch_c_working/, working notes 13개 → archive/working_notes_2026-04/. Active files: 226 → 133 (-41%). HARNESS H8 추가 반영. |
| **v1.2 (current)** | **2026-04-28** | **autonomous-mode LOOP 9: §5.2 Phase C (14 scripts) 실행 반영. archive/README.md v1.4. scripts/b_direction 37 (from 125, -88 cumulative).** |
