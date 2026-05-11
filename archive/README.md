# Witness Archive

**Created:** 2026-04-27
**Created via:** `docs/WITNESS_PROJECT_DIET_ACTIONS.md` Phase 2 execution
**Last updated:** 2026-05-09 (root cleanup, post Narrative Mode Refactor Phase 0/1/2)

---

## 0. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-04-27 | initial — `data_legacy/` + `b_direction_legacy/` |
| 2026-05-09 | root cleanup: `output/` (PNG bench 산출물) + `outputs/creative_demo/` 5-variation txts 이동 |

---

## 1. 왜 archive 했는가

WITNESS 프로젝트가 146 MB까지 부푼 상태에서 **legacy / superseded /
재생성 가능** 산출물을 작업 영역 밖으로 빼서 다음을 달성:

- 작업 폴더 navigability 향상
- 현재 canonical 산출물과 historical 산출물 명확히 구분
- 디스크 압박 시 archive를 외부 저장소로 옮기기 쉬운 구조

**삭제하지 않은 이유**: 일부 항목은 ITER_INDEX.md에서 참조되거나, 비교/재현
용도로 여전히 가치가 있을 수 있다.

---

## 2. 무엇이 들어 있는가

### 2.1 `data_legacy/` (~43 MB)

| Path | Source | Why archived |
|---|---|---|
| `trajectory_1000.jsonl` | `data/person/` | v1, superseded by v4_final |
| `trajectory_1000_v2.jsonl` | `data/person/` | v2, superseded by v4_final |
| `trajectory_1000_v3_varied.jsonl` | `data/person/` | v3, superseded by v4_final |
| `witness_trajectories_45.json` | `data/reference/` | reference v1, superseded by v2 |
| `pipeline_v1/` | `data/person/pipeline_v1/` | pipeline v1 outputs (재학습 가능) |

**Canonical 유지 (data/ 안에 그대로)**:
- `data/person/trajectory_1000_v4_final.jsonl`
- `data/reference/witness_trajectories_45_v2.json`
- `data/reference/evaluation_results.json`, `distribution_analysis.json`, `calibrated_thresholds.json`

### 2.3 `output_legacy/` (PNG benchmark + diagnostic 산출, 2026-05-09 추가)

| Path | Source | Why archived |
|---|---|---|
| `bench_baseline.json` | `output/` | benchmarks/bench_simulation.py 산출 — *재생성 가능*, 현재 활성 메인 표면(portfolio demo)에서 미사용 |
| `cross_persona_posterior.png` 등 8 PNG | `output/` | 옛 분석 시각화 (Branch B/C 분석기 산출). 현재 portfolio demo 외부 |

루트의 `output/` 디렉토리는 비워졌고 제거됨.

### 2.4 `outputs_legacy/creative_demo/` (한국어 5-variation 산출, 2026-05-09 추가)

| Path | Source | Why archived |
|---|---|---|
| `peter_scarcity_*_5_variations_ko.txt` (4개) | `outputs/creative_demo/` | `scripts/story/generate_anchor_variations.py`로 재생성 가능 |
| `vangogh_sacred_baseline_5_variations_ko.txt` | 동일 | 재생성 가능 |
| `scarcity_trilogy_*.txt` (2개) | 동일 | trilogy 산출, 재생성 가능 |

루트의 `outputs/` 디렉토리는 제거됨. 재실행 시 `generate_anchor_variations.py`가 `outputs/creative_demo/` 자동 생성.

### 2.2 `b_direction_legacy/` (~1.7 MB after v1.3)

| Path | Count | Source | Why archived |
|---|---:|---|---|
| `probe_runs_1_88/LOOP_ITER_*.md` | 85 | `docs/b_direction/probe_runs/` | Iter 1-88 logs, FINDINGS_SUMMARY로 흡수됨 |
| `probe_runs_1_88/BATCH_*.md` | 5 | `docs/b_direction/probe_runs/` | pre-PYHASH era batch reports |
| `findings_summaries_partial/FINDINGS_SUMMARY_ITER_1_{32,43,48}.md` | 3 | `docs/b_direction/` | superseded by FINDINGS_SUMMARY_ITER_1_63 |
| `WORLD_BUILDING_PROGRESS.md` | 1 | `docs/b_direction/` | v1 (WORLD_BUILDING_PROGRESS_v2.md가 latest) |
| `iter_91_to_119/ITER_*.md` | 27 | `docs/b_direction/` | PYHASH-pre/transition era. ITER_INDEX + SACRED_STATUS_NOTE link 갱신됨 |
| `scripts_iter_1_88/run_loop_iter*.py` | 55 | `scripts/b_direction/` | Phase A: leaf loop_iter scripts (no imports). 5 building blocks (iter1, 2, 22, 23, 45) preserved. |
| `scripts_iter_91_119/run_iter*.py` | 19 | `scripts/b_direction/` | Phase B (v1.3): §6.2 standalone scripts (Iter 91-119 era). UNSURE 3 (iter113, iter118, iter134) preserved per SCRIPT_STATUS §7. |
| **`scripts_phase_c_oneoffs/run_*.py`** | **14** | **`scripts/b_direction/`** | **Phase C (v1.4): §6.3.1 ARCHIVE_CANDIDATE one-offs (audit, cast, counterfactual, iter135-142, long_horizon, loose_gate, mixed_arc_authority, p1_revalidate, per_cohort). 7 KEEP_CANDIDATE preserved (canonical doc reference).** |

---

## 3. 현재 canonical 문서 (archive 아님)

`docs/b_direction/`에 남아 있는 다음 문서들이 **현재 기준 canonical**:

### 현재 cycle 산출물 (Iter 176-184)
- `COMPONENT_LEDGER.md` (v1.1)
- `STATE_FIELD_STATUS.md`
- `KERNEL_GAPS.md`
- `SACRED_STATUS_NOTE.md`
- `WITNESS_INTERNAL_BRANCH_CYCLE_COMPLETE.md`
- `READABILITY_BLIND_PROTOCOL_V2.md`
- `READABILITY_BLIND_RESULTS_V2.md`
- `READABILITY_PILOT_4.md`
- `ANNOTATED_PROBE_FORMAT.md`
- `PROBE_STATS_CHARACTERIZATION.md`
- ITER_176-184 회고 문서

### Cycle 이전 reference (현재도 활용)
- `ITER_INDEX.md` (archive link 갱신 완료 v1.1)
- `BRANCH_B_C_SUMMARY.md`
- `INERT_RESERVE_AUDIT.md` (Iter 89, partial stale)
- `READABILITY_BLIND_PROTOCOL.md` (v1, V2가 supersede 했지만 reference)
- `READABILITY_BLIND_RESULTS.md` (v1)
- `READABILITY_BLIND_GROUND_TRUTH.md`
- `ITER_124_SCALE_TIERS_CANONICAL.md` (Iter 120+ era — KEEP)
- `ITER_135_RUMOR_MECHANISM_CORRECTED.md` (Iter 120+ era — KEEP)
- `ITER_167_DIRECTIVE_CYCLE_SYNTHESIS.md` (Iter 167 — KEEP)
- `FINDINGS_SUMMARY_ITER_1_63.md` (latest in Iter 1-63 chain)
- `FINDINGS_SUMMARY_ITER_64_74.md`
- `FINDINGS_SUMMARY_ITER_75_86.md`
- `WORLD_BUILDING_PROGRESS_v2.md` (v2 latest)
- `WORLD_MEMORY.md`, `WORLD_PROCESSES.md`, `POST_FREEZE_BRANCH_DECISION.md`
- `SCRIPT_STATUS.md` (NEW — 2026-04-27)

**참고**: ITER_111_CONSOLIDATION + ITER_119_FINAL_CONSOLIDATION은 v1.1에서
archive로 이동. ITER_INDEX link 갱신 완료.

### Probes (현재 표준)
- `readability_probes/` (12 original + 12 annotated, P{1-12}.txt + P{1-12}_ANNOTATED.txt)
- `readability_probes_annotated/` (정리본 12개)
- `readability_pilot/` (4 pilot probes)

---

## 4. 복구 방법

### 데이터 복구
```bash
# Restore individual file
mv archive/data_legacy/trajectory_1000.jsonl data/person/

# Restore all data_legacy
mv archive/data_legacy/* data/person/  # WARNING: 일부는 data/reference/로
```

### B-direction 문서 복구
```bash
# Restore one
mv archive/b_direction_legacy/probe_runs_1_88/LOOP_ITER_1.md docs/b_direction/probe_runs/

# Restore findings summaries
mv archive/b_direction_legacy/findings_summaries_partial/*.md docs/b_direction/
```

---

## 5. 보류 (FROZEN 2026-04-28 per Lee decision)

다음은 **별도 directive 없이는 건드리지 않음** (Lee 명시 lock):

- `world/` (top-level legacy v2.0 Spike 1A) — **FREEZE**
- `docs/world/` — **FREEZE**
- `data/person/pipeline_v2/` — **FREEZE**
- `data/person/abc_snapshots/` — **FREEZE**
- `docs/b_direction/probe_runs/*.json` (122 files) — **보류 LOCKED**
- `scripts/b_direction/` 7 KEEP_CANDIDATE (weak-ref 5 + strong-ref 2) — **KEEP LOCKED**
- SCRIPT_STATUS §7 UNSURE 3 (iter113, iter118, iter134) — **KEEP LOCKED**

**완료 (v1.3 round, autonomous-mode 2026-04-28)**:
- ✓ Phase B: 19 of §6.2 scripts → `scripts_iter_91_119/`
- ✓ SCRIPT_STATUS.md v1.2 업데이트 (Phase B execution log §11)
- ✓ Building-block import 검증 통과

**완료 (v1.4 round, autonomous-mode LOOP 9 2026-04-28)**:
- ✓ Phase C: 14 of §6.3.1 ARCHIVE_CANDIDATE → `scripts_phase_c_oneoffs/`
- ✓ SCRIPT_STATUS.md v1.3 업데이트 (Phase C execution log §12)
- ✓ Building-block import + 1647 tests collection 검증 통과
- ✓ scripts/b_direction count: 51 → 37

---

## 6. archive 위치 운영 정책

### Git 처리 (현재 적용됨)
`.gitignore`에 다음 추가됨 (2026-04-27):
```gitignore
archive/*
!archive/README.md
!archive/.gitkeep
```

archive 내용은 **로컬-only**. README만 git tracked.

### 외부 백업 권장
disk 압박 또는 cleanup 추가 진행 시 `archive/`를 외부로 이동:

```bash
tar -czf Witness_archive_2026-04-27.tar.gz archive/
# upload to external storage, then:
rm -rf archive/
```

---

## 7. Versioning

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-27 | 초기 archive — Phase 1 cache + Phase 2 data_legacy + b_direction obvious superseded |
| v1.1 | 2026-04-27 | + ITER_91-119 docs (27 files) + canonical link 갱신 + .gitignore 적용 + CANONICAL_MANIFEST + ARCHIVE_POLICY + SCRIPT_STATUS 작성 |
| v1.2 | 2026-04-27 | + Phase A: 55 leaf `run_loop_iter*.py` archived (Iter 1-88, 5 building blocks preserved). Pilot blind sim (claude-bias) executed; results in `RESULTS_V2_CLAUDE_SIM.md`. |
| v1.3 | 2026-04-28 | + Phase B: 19 of §6.2 scripts archived under autonomous-mode directive (`scripts_iter_91_119/`). UNSURE 3 (iter113, iter118, iter134) preserved per SCRIPT_STATUS §7. SCRIPT_STATUS.md v1.2 with execution log. |
| **v1.4 (current)** | **2026-04-28** | **+ Phase C: 14 of §6.3.1 ARCHIVE_CANDIDATE (`scripts_phase_c_oneoffs/`). 7 KEEP_CANDIDATE preserved (5 weak-ref to WORLD_BUILDING_PROGRESS_v2 + 2 strong-ref). scripts/b_direction count: 51 → 37. SCRIPT_STATUS.md v1.3 with §12 execution log.** |
| v1.5 (planned) | TBD | Lee 검토 후 weak-ref 5개 추가 archive 또는 보류 / probe_runs json archive (122 files, ARCHIVE_POLICY §1.2 next round). |
| v2 (planned) | TBD | world/ legacy 평가 (Lee 별도 승인) |

---

## 8. Companion docs

- [docs/CANONICAL_MANIFEST.md](../docs/CANONICAL_MANIFEST.md) — 길찾기, "무엇이 canonical인가"
- [docs/ARCHIVE_POLICY.md](../docs/ARCHIVE_POLICY.md) — 운영 규칙, "다음 archive round 어떻게"
- [docs/b_direction/SCRIPT_STATUS.md](../docs/b_direction/SCRIPT_STATUS.md) — scripts/b_direction 분류표
- [docs/PROJECT_DIET_ANALYSIS.md](../docs/PROJECT_DIET_ANALYSIS.md) — 초기 분석
- [docs/WITNESS_PROJECT_DIET_ACTIONS.md](../docs/WITNESS_PROJECT_DIET_ACTIONS.md) — Phase 1+2 실행 지시서
- [docs/WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md](../docs/WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md) — 후속 평가 + 다음 단계 지시서
