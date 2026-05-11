# Witness 프로젝트 다이어트 분석 리포트

**Date:** 2026-04-26
**Status (2026-04-28):** **COMPLETE / REFERENCE** — 모든 분석 항목이 ACTIONS + POSTCHECK + autonomous-mode (LOOP 1-13)에서 실행됨. doc은 historical record로 보존.
**Original status:** 분석만 (실제 삭제 없음 — Lee 승인 후 실행)
**Total project size:** 146 MB → ~50 MB (Phase 1+2 + autonomous Phase A+B+C 후)

---

## 1. 전체 용량 요약

| 영역 | 용량 | git-tracked? |
|---|---:|:---:|
| `data/` | **59 MB** | NO (gitignored) |
| `.mypy_cache/` | **47 MB** | NO (gitignored) |
| `tests/` | 6.6 MB | YES |
| `docs/` | 6.4 MB | partial |
| `__pycache__/` (모든 위치 합) | **6.7 MB** | NO (gitignored) |
| `scripts/` | 2.3 MB | partial |
| `engine/` | 2.0 MB | YES (core) |
| `world/` (top-level legacy) | 689 KB | YES |
| `output/` | 628 KB | NO (gitignored) |
| `content/` | 603 KB | YES |
| `.pytest_cache/` | 171 KB | NO |
| `.ruff_cache/` | 72 KB | NO |

**최대 다이어트 가능 영역**: 데이터 (59M) + 캐시 (54M) + 일부 docs (4M b_direction 미커밋) ≈ **~120MB**

---

## 2. 가장 큰 폴더 Top 20

| Rank | Path | Size | Tracked | Note |
|---:|---|---:|:---:|---|
| 1 | `data/person/` | 56 MB | NO | 4개 1000-trajectory jsonl + pipeline outputs |
| 2 | `.mypy_cache/` | 47 MB | NO | mypy 캐시 (재생성 가능) |
| 3 | `data/reference/` | 3.4 MB | NO | reference trajectories + evaluation results |
| 4 | `tests/test_engine/` | 4.8 MB | YES | 핵심 테스트 |
| 5 | `docs/b_direction/` | 4 MB | **NO** | 67 ITER 문서 + 212 probe_runs (전부 미커밋) |
| 6 | `data/person/pipeline_v1/` | 2.4 MB | NO | pipeline v1 outputs |
| 7 | `scripts/b_direction/` | 1.6 MB | **NO** | 125 py files (전부 미커밋) |
| 8 | `data/person/pipeline_v2/` | 1.7 MB | NO | pipeline v2 outputs |
| 9 | `docs/person/` | 1.1 MB | partial | paper_data PNG + iter docs |
| 10 | `tests/test_world/` | 845 KB | YES | world test suite |
| 11 | `docs/person/paper_data/` | 709 KB | YES (일부) | 8 PNG 논문 figures |
| 12 | `world/` (top-level) | 689 KB | YES | v2.0 Spike 1A 레거시 (engine/world와 별도) |
| 13 | `output/` | 628 KB | NO | demo trace + figures |
| 14 | `docs/world/` | 480 KB | YES (일부) | spike review docs + paper_data |
| 15 | `docs/specs/` | 300 KB | YES | 16 spec docs |
| 16 | `docs/b_direction/readability_probes/` | 288 KB | NO | 12 original + 12 annotated probes |
| 17 | `scripts/data_pipeline/` | 222 KB | YES | data pipeline scripts |
| 18 | `tests/test_world_process/` | 189 KB | YES | active tests |
| 19 | `tests/test_rubric/` | 182 KB | YES | active tests |
| 20 | `docs/research/` | 128 KB | YES | research history |

---

## 3. 가장 큰 파일 Top 50 (>500KB)

| Rank | Path | Size | Tracked | Note |
|---:|---|---:|:---:|---|
| 1 | `data/person/trajectory_1000_v4_final.jsonl` | 14 MB | NO | latest v4 |
| 2 | `data/person/trajectory_1000_v3_varied.jsonl` | 13 MB | NO | v3 |
| 3 | `data/person/trajectory_1000_v2.jsonl` | 13 MB | NO | v2 |
| 4 | `data/person/trajectory_1000.jsonl` | 13 MB | NO | v1 |
| 5 | `data/reference/witness_trajectories_45_v2.json` | 1.7 MB | NO | reference v2 |
| 6 | `data/reference/witness_trajectories_45.json` | 1.7 MB | NO | reference v1 |
| 7 | `data/person/pipeline_v1/baseline/X.npy` | 1.1 MB | NO | training feature matrix |
| 8 | (각 LOOP_ITER_* doc) | ~8KB each × 85 | NO | b_direction probe iter logs |
| 9 | (각 *.json probe) | ~12KB each × 122 | NO | b_direction probe results |
| 10 | `output/trace_demo.jsonl` | 220 KB | NO | demo trace (regen-able) |

**4개 trajectory_1000*.jsonl = 53 MB**. v1, v2, v3, v4 4개 버전 모두 보존 중.
정상이라면 v4_final만 유지하고 v1-v3은 삭제 후보.

---

## 4. 분류표 (KEEP_CORE / KEEP_REFERENCE / ARCHIVE / DELETE / UNSURE)

### 4.1 KEEP_CORE (핵심, 절대 건드리지 말 것)

| Path | Reason |
|---|---|
| `engine/` | 핵심 엔진 코드 (KERNEL classification per COMPONENT_LEDGER) |
| `content/` | Content packs (peter, judas, vangogh, ...) — 콘텐츠 정경 |
| `tests/` | 모든 테스트 (572 fast + 98 slow + 33 archived = 703 total) |
| `examples/` | demo.py, demo_v07.py, demo_phased.py — runnable demos |
| `benchmarks/bench_simulation.py` | 성능 벤치마크 |
| `scripts/data_pipeline/`, `scripts/v3_measurement/` | active pipeline |
| `scripts/{paper_numbers, world_figures, baseline_comparison, hazard_scaling, paper_figures}.py` | 논문 figure 생성 |
| `docs/HARNESS.md`, `docs/ODD_PROTOCOL.md`, `docs/REPORT_TEMPLATE.md` | 행동 강령/방법론 |
| `docs/specs/` | 16 spec docs (DESIGN_LATENT_DRIVE, TRACE_SCHEMA, V3 redesign...) |
| `docs/research/` | RESEARCH.md, PAPER_DRAFT_V06, ITERATION_CLASSIFICATION |
| `docs/persona_engine/`, `docs/world_engine/` | persona + world 엔진 spec |
| `CLAUDE.md`, `DESIGN.md`, `README.md`, `lessons.md`, `progress.md` | 루트 핵심 |
| `.gitignore`, 설정 파일 | 빌드/lint/test 인프라 |

### 4.2 KEEP_REFERENCE (참고용 보존)

| Path | Size | Reason |
|---|---:|---|
| `data/person/trajectory_1000_v4_final.jsonl` | 14 MB | 최신 dataset (v4) |
| `data/reference/witness_trajectories_45_v2.json` | 1.7 MB | reference v2 (latest) |
| `data/reference/evaluation_results.json` | 56 KB | rubric 비교 소스 |
| `data/reference/distribution_analysis.json` | 20 KB | 분석 baseline |
| `data/reference/calibrated_thresholds.json` | 4 KB | calibration |
| `docs/person/paper_data/` (PNG 8개) | 709 KB | 논문 figure 자산 |
| `docs/world/paper_data/` | 측정 outputs | spike 검증 figures |
| `docs/person/v3_measurement/` (5 files) | 56 KB | v3 측정 산출물 |
| `docs/b_direction/COMPONENT_LEDGER.md`, `STATE_FIELD_STATUS.md`, `KERNEL_GAPS.md`, `SACRED_STATUS_NOTE.md`, `WITNESS_INTERNAL_BRANCH_CYCLE_COMPLETE.md` | ~80 KB | 현재 cycle 산출물 — canonical |
| `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md`, `RESULTS_V2.md`, `READABILITY_PILOT_4.md`, `ANNOTATED_PROBE_FORMAT.md` | ~40 KB | 현재 V2 protocol |
| `docs/b_direction/readability_probes_annotated/` | 56 KB | annotated 12 probes (현재 표준) |
| `docs/b_direction/readability_pilot/` | 48 KB | pilot 4 probes |
| `docs/b_direction/BRANCH_B_C_SUMMARY.md`, `ITER_INDEX.md`, `INERT_RESERVE_AUDIT.md`, `READABILITY_BLIND_PROTOCOL.md` (v1), `READABILITY_BLIND_RESULTS.md` (v1), `READABILITY_BLIND_GROUND_TRUTH.md` | ~120 KB | 현재 활용 reference |
| `docs/b_direction/PROBE_STATS_CHARACTERIZATION.md` | 16 KB | post-cycle 분석 (Iter 184) |
| `docs/archive/` | 32 KB | 이미 archive됨 |

### 4.3 ARCHIVE_CANDIDATE (압축/외부 보관)

| Path | Size | Reason | Risk |
|---|---:|---|:---:|
| `data/person/trajectory_1000.jsonl` | 13 MB | v1 dataset, v4가 최신. 결과 재현 위해서만 필요 | low |
| `data/person/trajectory_1000_v2.jsonl` | 13 MB | v2 dataset, superseded by v4 | low |
| `data/person/trajectory_1000_v3_varied.jsonl` | 13 MB | v3 dataset, superseded by v4 | low |
| `data/reference/witness_trajectories_45.json` | 1.7 MB | reference v1, v2가 최신 | low |
| `data/reference/evaluation_results_calibrated.json` | 32 KB | calibrated 변형 (calibrated_thresholds.json + evaluation_results.json로 재생성 가능) | low |
| `data/reference/evaluation_results_v2.json` | 8 KB | superseded variant | low |
| `data/person/pipeline_v1/` | 2.4 MB | pipeline v1 outputs (v2가 최신) | medium (재학습 시 비교용 가능) |
| `docs/b_direction/probe_runs/LOOP_ITER_1.md` ~ `LOOP_ITER_88.md` | 770 KB (85 files) | Iter 1-88 로그 — 핵심 인사이트는 ITER_119_FINAL_CONSOLIDATION.md + FINDINGS_SUMMARY 시리즈에 흡수됨 | medium |
| `docs/b_direction/probe_runs/*.json` (122 files) | 1.5 MB | iter별 raw probe 결과. 일부는 ITER_*.md에서 인용됨 | medium |
| `docs/b_direction/FINDINGS_SUMMARY_ITER_1_32.md`, `_1_43.md`, `_1_48.md` | 48 KB | 작은 범위 summary들. `FINDINGS_SUMMARY_ITER_1_63.md`로 superseded | low |
| `docs/b_direction/ITER_91_*.md` ~ `ITER_119_*.md` (29 files) | ~280 KB | Iter 91-119 (PYHASH bug pre-cleanup era). ITER_111_CONSOLIDATION + ITER_119_FINAL_CONSOLIDATION에 정리됨 | medium |

**제안**: `archive/` 폴더로 이동하거나 `.tar.gz`로 압축 후 외부 백업.

### 4.4 DELETE_CANDIDATE (삭제 후보)

| Path | Size | Reason | Risk |
|---|---:|---|:---:|
| `.mypy_cache/` | 47 MB | mypy 실행 시 자동 재생성. .gitignore 처리됨 | low |
| 모든 `__pycache__/` (subdir 포함) | 6.7 MB | 파이썬 import 시 자동 재생성. .gitignore 처리됨 | low |
| `.pytest_cache/` | 171 KB | pytest 실행 시 재생성 | low |
| `.ruff_cache/` | 72 KB | ruff 실행 시 재생성 | low |
| `docs/b_direction/P_ANNOTATED_DEMO.txt` | 8 KB | Iter 163 prototype, P{1-12}_ANNOTATED.txt로 superseded | low |
| `output/trace_demo.jsonl` | 220 KB | demo 출력, `examples/demo_v07.py` 재실행으로 재생성 | low |
| 423 stray `*.pyc` | (포함됨 in __pycache__) | __pycache__ 삭제와 함께 정리 | low |

### 4.5 UNSURE (사람이 판단 필요)

| Path | Size | Question |
|---|---:|---|
| `world/` (top-level, 689 KB) | 689 KB | v2.0 Spike 1A 레거시. `from world.` import 56 files (대부분 tests/test_world + scripts/demo_world_*). 활성 사용 중인지, archive로 격하 가능한지 Lee 판단 필요 |
| `docs/world/` (480 KB) | 480 KB | 위 world/ 폴더의 spike review 문서들. world/가 active이면 KEEP, 아니면 archive |
| `docs/b_direction/probe_runs/` 전체 (2.4 MB) | 2.4 MB | 일괄 archive 또는 선별 보존? |
| `data/person/abc_snapshots/` | 372 KB | ABC calibration snapshots — 재현 시 필요한지 |
| `scripts/b_direction/run_iter*.py` (Iter 91-119 era, 28 files) | ~150 KB | PYHASH-pre era scripts. 재실행 가치 미정 |
| `scripts/b_direction/run_loop_iter*.py` (45 files) | ~250 KB | Iter 1-88 era. 일부는 INDEX 기준 superseded |
| `docs/b_direction/WORLD_BUILDING_PROGRESS.md` vs `_v2.md` | 32 KB | v1 vs v2 둘 다 16KB. 동일 주제 — v1 archive 가능? |
| 5 `BATCH_*_REPORT.md` (40 KB) | 40 KB | Iter 1-88 이전 batch reports. Pre-PYHASH era |

---

## 5. .gitignore 추가 제안

현재 `.gitignore`는 표준 패턴 + `data/*` + `output/` 처리 됨. 추가 권장:

```gitignore
# 다이어트 분석 (Iter 184 발견)

# 로컬 work-in-progress B-direction (전체 미커밋 상태)
# 만약 정리 후 보존 원하지 않으면 추가 (현재는 미적용 권장):
# docs/b_direction/probe_runs/

# pipeline outputs (재현 가능)
data/person/pipeline_v*/
data/person/abc_snapshots/

# 측정 산출물 중 superseded
data/person/trajectory_1000.jsonl       # v1
data/person/trajectory_1000_v2.jsonl    # v2
data/person/trajectory_1000_v3_*.jsonl  # v3

# Reference variants (latest만 유지)
data/reference/witness_trajectories_45.json    # v1 (v2가 latest)
data/reference/evaluation_results_calibrated.json
data/reference/evaluation_results_v2.json
```

**주의**: 위 trajectory_1000_v{1,2,3} 패턴은 `data/*`로 이미 ignored. 다만 stale 파일이 disk에 잔존 → archive 또는 삭제 후 빈 자리 .gitkeep만.

---

## 6. 두 가지 다이어트 안

### 6.1 보수적 다이어트 (low-risk only) — 약 56 MB 절감

| Action | Path | Size |
|---|---|---:|
| Delete (재생성) | `.mypy_cache/` | 47 MB |
| Delete (재생성) | 모든 `__pycache__/` | 6.7 MB |
| Delete (재생성) | `.pytest_cache/` | 171 KB |
| Delete (재생성) | `.ruff_cache/` | 72 KB |
| Delete | `docs/b_direction/P_ANNOTATED_DEMO.txt` | 8 KB |
| Delete (재생성 가능) | `output/trace_demo.jsonl` | 220 KB |
| Delete | 423 stray `*.pyc` | (in pycache) |

**보수적 안 절감**: ~54 MB
**리스크**: 거의 0 (모두 .gitignore 처리됨, 재실행으로 재생성)
**복구**: `pytest`, `mypy`, `ruff`, `examples/demo_v07.py` 재실행

### 6.2 1차 다이어트안 (보수 + ARCHIVE) — 약 105-110 MB 절감

보수적 안 + 다음 archive 작업:

| Action | Path | Size |
|---|---|---:|
| Move to archive | `data/person/trajectory_1000.jsonl` (v1) | 13 MB |
| Move to archive | `data/person/trajectory_1000_v2.jsonl` | 13 MB |
| Move to archive | `data/person/trajectory_1000_v3_varied.jsonl` | 13 MB |
| Move to archive | `data/reference/witness_trajectories_45.json` (v1) | 1.7 MB |
| Move to archive | `data/person/pipeline_v1/` | 2.4 MB |
| Move to archive | `docs/b_direction/probe_runs/LOOP_ITER_*.md` (85 files) | 770 KB |
| Move to archive | `docs/b_direction/probe_runs/*.json` (Iter ≤ 88) | ~700 KB (선별) |
| Move to archive | `docs/b_direction/FINDINGS_SUMMARY_ITER_1_{32,43,48}.md` | 48 KB |
| Move to archive | `docs/b_direction/ITER_91_*.md` ~ `ITER_119_*.md` (PYHASH-pre era) | ~280 KB |
| Move to archive | `docs/b_direction/WORLD_BUILDING_PROGRESS.md` (v1 only) | 16 KB |
| Move to archive | `docs/b_direction/BATCH_*_REPORT.md` (5 files) | 40 KB |

**1차 안 절감**: ~54 MB (cache) + ~46 MB (archive) = **~100 MB**
**리스크**: medium — archive 파일들은 일부 ITER_INDEX.md에서 참조됨 (broken link 발생 가능)
**복구**: archive/ 폴더에서 복원

**Archive 위치 제안**:
```
archive/
├── data_legacy/           # trajectory v1-v3, reference v1
│   ├── trajectory_1000.jsonl
│   ├── trajectory_1000_v2.jsonl
│   ├── trajectory_1000_v3_varied.jsonl
│   ├── witness_trajectories_45.json
│   └── pipeline_v1/
└── b_direction_legacy/    # PYHASH-pre era + iter 1-88 logs
    ├── ITER_91_to_119/
    ├── probe_runs_iter_1_88/
    └── findings_summaries_partial/
```

또는 외부 백업 (`Witness_archive_2026-04-26.tar.gz`).

### 6.3 적극적 다이어트안 (high-risk, NOT recommended without Lee 명시 승인)

| Action | Path | Size | Concern |
|---|---|---:|---|
| Delete | top-level `world/` 폴더 | 689 KB | v2.0 spike 레거시 — tests/test_world에서 import. **삭제 시 56 files 영향** |
| Delete | `docs/world/` | 480 KB | 위와 짝. 삭제 전 Spike 5 paper_data 보존 필요 |
| Delete | `data/person/pipeline_v2/` | 1.7 MB | v3가 최신이지만 비교용 가능 |
| Delete | 모든 ITER_91-119 docs (29 files) | 280 KB | INDEX 참조 깨짐 |

**적극 안 추가 절감**: ~3 MB
**리스크**: HIGH — 코드/문서 의존성 끊김 가능
**권장**: NOT recommended without explicit Lee 검토

---

## 7. ITER 문서 / Probe 결과 / Scripts 분류

### 7.1 ITER 문서 (총 67 in docs/b_direction)

**현재 커널 이해에 꼭 필요한 것 (canonical)**:
- `ITER_INDEX.md` (navigation)
- `ITER_124_SCALE_TIERS_CANONICAL.md` (scale-tier table)
- `ITER_119_FINAL_CONSOLIDATION.md` (PYHASH-post baseline)
- `ITER_111_CONSOLIDATION.md` (mid-cycle synthesis)
- `ITER_124_SCALE_TIERS_CANONICAL.md`
- `ITER_135_RUMOR_MECHANISM_CORRECTED.md` (mechanism correction)
- `ITER_167_DIRECTIVE_CYCLE_SYNTHESIS.md` (presentation > mechanism)
- `ITER_176_*` ~ `ITER_184_*` (현재 cycle, 9 docs)

**역사적 기록 (archive 후보)**:
- `ITER_91-119` PYHASH-pre era: 19 files (ITER_INDEX 명시: "specific quantitative claims partially retracted")
- Iter 1-88 era는 LOOP_ITER_*.md로 probe_runs/에 있음

### 7.2 Probe runs (총 212 files)

| 분류 | 개수 | 크기 | 처리 |
|---|---:|---:|---|
| LOOP_ITER_*.md (1-88) | 85 | 770 KB | archive (FINDINGS_SUMMARY로 흡수됨) |
| BATCH_*_REPORT.md | 5 | 40 KB | archive (pre-PYHASH era) |
| *.json probe outputs | 122 | 1.5 MB | 선별 archive — 재현 가능한 것만 |

### 7.3 Scripts 분류 (scripts/b_direction/, 125 files)

| 분류 | 예시 | 처리 |
|---|---|---|
| **active** (현재 cycle) | `generate_annotated_probes_all.py`, `generate_readability_probes.py`, `_pyhash_guard.py` | KEEP |
| **active probe scripts** | `run_world_autonomy_probe.py`, `run_iter161_*.py` ~ `run_iter165_*.py` | KEEP |
| **legacy** | `run_loop_iter1-88_*.py` (45 files) | archive 후보 |
| **one-off experimental** | `run_iter91-119_*.py` (28 files PYHASH-pre era), `run_iter120-160_*.py` (활용도 낮음) | archive 후보 |

**참고**: `scripts/b_direction/`은 전체가 git 미추적이므로 archive 무게 부담 없음.

### 7.4 Docs 분류 (docs/b_direction/)

| Canonical (현재 활용) | Superseded (archive) | Duplicated (정리) |
|---|---|---|
| COMPONENT_LEDGER.md (v1.1) | INERT_RESERVE_AUDIT.md (Iter 89, partial stale) | WORLD_BUILDING_PROGRESS.md vs _v2.md |
| STATE_FIELD_STATUS.md | FINDINGS_SUMMARY_ITER_1_32, _1_43, _1_48 (subsumed) | (없음, 대부분 unique) |
| KERNEL_GAPS.md | ITER_91-119 era detail docs | |
| SACRED_STATUS_NOTE.md | ITER_107_AUX_RETRACTION 완료 후 retracted aux work docs | |
| READABILITY_BLIND_PROTOCOL_V2.md | _PROTOCOL.md (v1, V2가 supersede) | |
| READABILITY_BLIND_RESULTS_V2.md | _RESULTS.md (v1) | |
| ANNOTATED_PROBE_FORMAT.md | (없음, 신규) | |
| READABILITY_PILOT_4.md | (없음, 신규) | |
| BRANCH_B_C_SUMMARY.md | POST_FREEZE_BRANCH_DECISION.md (이전 framing) | |
| ITER_INDEX.md | ITER_91-119 docs를 가리킴 — partial broken if archive | |

---

## 8. 예상 절감 용량 총합

| 시나리오 | 절감 | 위험 |
|---|---:|:---:|
| 보수적 다이어트 (cache only) | **~54 MB** | 0 |
| 1차 다이어트안 (보수 + archive) | **~100 MB** | medium |
| 적극적 (1차 + 의존성 깨질 위험) | ~103 MB | HIGH |

**현재 146 MB → 보수적 후 92 MB → 1차 후 46 MB**

---

## 9. 권장 실행 순서 (Lee 승인 시)

### Phase 1: 즉시 가능 (보수적, 위험 0)
```bash
# 캐시 정리 (재생성 가능)
find . -name "__pycache__" -type d -exec rm -rf {} +
rm -rf .mypy_cache .pytest_cache .ruff_cache
find . -name "*.pyc" -delete
rm output/trace_demo.jsonl
rm docs/b_direction/P_ANNOTATED_DEMO.txt
```

### Phase 2: archive 디렉토리 생성 + 이동 (1차 안)
```bash
mkdir -p archive/data_legacy
mkdir -p archive/b_direction_legacy/{iter_91_to_119,probe_runs_1_88,findings_summaries_partial}

# trajectory + reference 구버전
mv data/person/trajectory_1000.jsonl archive/data_legacy/
mv data/person/trajectory_1000_v2.jsonl archive/data_legacy/
mv data/person/trajectory_1000_v3_varied.jsonl archive/data_legacy/
mv data/reference/witness_trajectories_45.json archive/data_legacy/
mv data/person/pipeline_v1 archive/data_legacy/

# B-direction legacy docs
mv docs/b_direction/probe_runs/LOOP_ITER_*.md archive/b_direction_legacy/probe_runs_1_88/
mv docs/b_direction/probe_runs/BATCH_*_REPORT.md archive/b_direction_legacy/probe_runs_1_88/
mv docs/b_direction/FINDINGS_SUMMARY_ITER_1_{32,43,48}.md archive/b_direction_legacy/findings_summaries_partial/
mv docs/b_direction/WORLD_BUILDING_PROGRESS.md archive/b_direction_legacy/
# ITER_91-119 docs (선별)
```

### Phase 3: ITER_INDEX 업데이트 (broken link 수정)
- archive 후 `ITER_INDEX.md`에 "archived" 표시 + path 갱신

### Phase 4: .gitignore 추가
- `data/person/pipeline_v*/` 명시
- `data/person/abc_snapshots/` 명시 (이미 `data/*` 처리되지만 명시 권장)

---

## 10. 핵심 발견 (요약)

1. **B-direction 작업 전체 미커밋**: `docs/b_direction/` (4 MB, 67 ITER docs + 212 probe_runs files) + `scripts/b_direction/` (1.6 MB, 125 py files) — 모두 git untracked. 정리에 git 위험 없음.

2. **데이터 영역이 가장 큰 절감 잠재력**: 4개 trajectory_1000*.jsonl만으로 53 MB. 모두 gitignored 상태.

3. **mypy_cache 47 MB**: 단일 최대 캐시. 즉시 삭제 가능, 위험 0.

4. **ITER 91-119 PYHASH-pre era docs**: ITER_INDEX.md에 "partially retracted" 명시되어 있어 archive 적격. 하지만 `ITER_INDEX.md` link 깨짐 주의.

5. **top-level `world/` 폴더 (v2.0 Spike 1A)**: `engine/world/`와 별도. `tests/test_world/` + `scripts/demo_world_*.py`에서 사용 중. **삭제 금지** (UNSURE 분류).

6. **5 FINDINGS_SUMMARY docs는 superseded chain**: ITER_1_32 ⊂ ITER_1_43 ⊂ ITER_1_48 ⊂ ITER_1_63. 처음 3개 archive 가능.

7. **stray *.pyc 423개**: __pycache__ 외부에 있는 .pyc — Python 일반적 위치 외 잔존. 함께 정리.

---

## 11. 다이어트 후 예상 구조

```
Witness/  (146 MB → 46 MB after 1차)
├── engine/                     2.0 MB (KEEP)
├── content/                    603 KB (KEEP)
├── tests/                      6.6 MB (KEEP)
├── scripts/                    2.3 MB (KEEP active, archive legacy)
├── examples/                   64 KB (KEEP)
├── benchmarks/                 12 KB (KEEP)
├── world/                      689 KB (UNSURE — Lee 판단)
├── docs/                       ~3 MB (after archive)
│   ├── (root *.md)             KEEP
│   ├── specs/                  KEEP
│   ├── research/               KEEP
│   ├── persona_engine/         KEEP
│   ├── world_engine/           KEEP
│   ├── b_direction/            ~1 MB (canonical only)
│   │   ├── COMPONENT_LEDGER.md, STATE_FIELD_STATUS.md, ...
│   │   ├── readability_probes_annotated/
│   │   ├── readability_pilot/
│   │   └── (current cycle docs Iter 176-184)
│   └── archive/                KEEP (already archive)
├── data/                       ~16 MB (v4 + reference v2 + abc_snapshots)
│   ├── person/trajectory_1000_v4_final.jsonl
│   ├── reference/witness_trajectories_45_v2.json
│   └── README.md
├── output/                     0 (gitignored, dynamic)
└── archive/                    ~46 MB (legacy data + ITER 91-119 + probe_runs 1-88)
```

---

## 12. 주의사항

- **현재 워킹 트리에 untracked 파일 50개 + 변경 16개 있음**. 다이어트 전 `git status` 확인 + 필요시 commit/stash.
- `world/` 와 `engine/world/` 는 다른 폴더 — 혼동 주의.
- `archive/` 폴더는 git에 추가할지 ignore할지 결정 필요. `archive/` 내용이 정말 "역사적"이면 한 번 commit 후 `archive/*` ignore 권장.
- ITER_INDEX.md broken link는 archive 후 수정 필요 (또는 INDEX_OBSOLETE.md로 rename + 새 INDEX_CURRENT.md 작성).

---

**최종 권장**: Phase 1 (보수적, 54 MB 절감) → Lee 검토 → Phase 2 (archive, 추가 ~46 MB 절감). Phase 3 적극안은 Lee 명시 승인 시에만.
