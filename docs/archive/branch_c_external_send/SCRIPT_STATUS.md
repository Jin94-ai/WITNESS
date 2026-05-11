# scripts/b_direction/ -- Script Status Classification

**Date:** 2026-04-27
**Iteration source:** `WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md` §3.2 / §4.3 / §5(2순위)
**Total scripts:** 125 .py files
**Status:** Classification only — no archive moves yet

---

## 0. Why this matters

`scripts/b_direction/` accumulated 125 scripts across 89+ iters. Naive
archive of "old iter scripts" would **break the chain** because:

- Some `run_loop_iter*.py` are **building blocks** imported by later iters
- `run_accusation_scene.py`, `run_scarcity_scene.py`, `run_sacred_gathering.py`
  are imported by 100+ scripts each
- `_pyhash_guard.py` is imported by 74 scripts (PYHASH discipline infrastructure)

This document captures the dependency graph + classification before any moves.

---

## 1. Method

For each script, counted imports across `scripts/`, `tests/`, `engine/`,
`examples/`, `benchmarks/`:

```bash
grep -rln "from scripts.b_direction.{name}" --include="*.py" ...
```

Self-references excluded. **Result**: 10 scripts are imported by others;
115 scripts are leaf (not imported by any other file).

---

## 2. Classification

| Category | Count | Action |
|---|---:|---|
| **ACTIVE_BUILDING_BLOCK** | 10 | KEEP (imported by others) |
| **ACTIVE_CURRENT_CYCLE** | 9 | KEEP (Iter 161-184 work) |
| **LEGACY_KEEP** | 8 | KEEP (recent Iter 120-160 era, may be referenced) |
| **ARCHIVE_CANDIDATE** | ~88 | Move to `archive/b_direction_legacy/scripts_iter_1_119/` |
| **UNSURE** | 10 | Lee 판단 필요 |

---

## 3. ACTIVE_BUILDING_BLOCK (10 — DO NOT MOVE)

These are imported by other scripts. Moving them breaks downstream.

| Script | Imported by | Role |
|---|---:|---|
| `_pyhash_guard.py` | 74 | PYHASH=0 enforcement (Iter 105 fix) |
| `run_accusation_scene.py` | 104 | Builds accusation cast/locations/network |
| `run_scarcity_scene.py` | 33 | Builds scarcity cast/locations |
| `run_sacred_gathering.py` | 21 | Builds sacred cast/gathering |
| `run_loop_iter1_transition.py` | 7 | Foundation loop iter 1 (chain root) |
| `run_loop_iter22_topology_audit.py` | 5 | Iter 22 topology utilities |
| `run_loop_iter45_arc_d_sweep.py` | 2 | Iter 45 arc-D sweep |
| `run_loop_iter2_distant.py` | 2 | Iter 2 distant transition |
| `run_loop_iter23_sacred_audit.py` | 2 | Iter 23 sacred audit |
| `generate_readability_probes.py` | 1 | Imported by generate_annotated_probes_all |

---

## 4. ACTIVE_CURRENT_CYCLE (9 — Iter 161-184)

Current directive cycle outputs. KEEP.

| Script | Iter | Purpose |
|---|---:|---|
| `_retrofit_pyhash_guard.py` | helper | PYHASH retrofit utility |
| `audit_event_contract.py` | helper | Event contract audit |
| `generate_annotated_probe.py` | 163 | Annotated probe prototype |
| `generate_annotated_probes_all.py` | 166 | All 12 annotated probes |
| `run_iter161_spatial_disengage.py` | 161 | Spatial disengagement (negative result) |
| `run_iter162_inert_reaudit.py` | 162 | INERT 5/6 confirmed |
| `run_iter164_world_autonomy.py` | 164 | World autonomy 4/4 signals |
| `run_iter165_meso_coupling.py` | 165 | Meso coupling 7/10 pairs |
| `run_world_autonomy_probe.py` | 164-related | World autonomy variant |

---

## 5. LEGACY_KEEP (8 — Iter 120-160 era)

Recent enough that they may be referenced or rerun. Keep until clearer signal.

| Script | Iter | Reason to keep |
|---|---:|---|
| `run_iter138_per_agent_audit.py` | 138 | Per-agent peak/final pattern (used in current Q-set) |
| `run_iter143_recovery_audit.py` | 143 | Recovery audit pattern |
| `run_iter144_audit_iter140.py` | 144 | Audit chain |
| `run_iter145_audit_iter133.py` | 145 | Audit chain |
| `run_iter146_audit_iter118.py` | 146 | Audit chain |
| `run_iter148_n4_outsiders.py` | 148 | n=4 cast finding |
| `run_iter150_audit_iter134.py` | 150 | Audit chain |
| `run_meso_scale_probe.py` | helper | Meso scale measurement |

---

## 6. ARCHIVE_CANDIDATE (~88 — pre-Iter 120 + isolated one-offs)

### 6.1 Iter 1-88 era (run_loop_iter*) — 47 scripts

All `run_loop_iter*.py` EXCEPT the 5 building blocks (iter1, iter2, iter22,
iter23, iter45).

```
run_loop_iter6_js_metric.py
run_loop_iter12_transfer_audit.py
run_loop_iter13_role_invariance.py
run_loop_iter14_conditional_invariance.py
run_loop_iter15_bootstrap.py
run_loop_iter16_threshold.py
run_loop_iter17_triadic.py
run_loop_iter18_permutation.py
run_loop_iter19_prior_ablation.py
run_loop_iter20_weak_verify.py
run_loop_iter21_pressure_prior.py
run_loop_iter24_authority_raid.py
run_loop_iter25_readability.py
run_loop_iter26_relation_probe.py
run_loop_iter28_repair_arc.py
run_loop_iter29_repair_sweep.py
run_loop_iter32_dflow_transfer.py
run_loop_iter35_autonomous_transfer.py
run_loop_iter36_scale.py
run_loop_iter40_private_crisis.py
run_loop_iter46_crossscene_arc_d.py
run_loop_iter47_mixed_cast.py
run_loop_iter48_crisis_agent_level.py
run_loop_iter50_longhorizon.py
run_loop_iter53_prior_invariance.py
run_loop_iter54_topology_reaudit.py
run_loop_iter55_cycle_source.py
run_loop_iter56_p1_ablation.py
run_loop_iter57_mixed_arc.py
run_loop_iter58_p2_decay_sweep.py
run_loop_iter59_p4_deny_intensity.py
run_loop_iter61_blend_power.py
run_loop_iter62_recovery_bias_ablation.py
run_loop_iter63_relation_bias_ablation.py
run_loop_iter65_p3_intensity.py
run_loop_iter66_cross_scenario_p1.py
run_loop_iter67_layer_decompose.py
run_loop_iter68_cross_layer.py
run_loop_iter69_amp_threshold.py
run_loop_iter70_pyhash_grid.py
run_loop_iter71_state_field.py
run_loop_iter72_multiplier_probe.py
run_loop_iter73_shame_sweep.py
run_loop_iter74_period_sweep.py
run_loop_iter76_cross_shame_sweep.py
run_loop_iter77_mixed_accusation_sacred.py
run_loop_iter78_awe_injection_mixed.py
run_loop_iter79_layered_blame.py
run_loop_iter80_guilt_injection_mixed.py
run_loop_iter81_iter57_replicate.py
run_loop_iter83_motif_activation_trace.py
run_loop_iter84_full_motif_dump.py
run_loop_iter85_events_recent_trace.py
run_loop_iter86_multi_seed_verify.py
run_loop_iter88_cross_scenario_feedback.py
```

### 6.2 Iter 91-119 era (run_iter*) — 22 scripts

Pre-PYHASH-fix and post-fix transition era. ITER_91-119 docs already
archived in Phase 2 (Iter 91-119 docs cycle).

```
run_iter106_noise_floor.py
run_iter107_500t_noise.py
run_iter107b_mixed_noise.py
run_iter108_bimodal_trace.py
run_iter108b_confession_trace.py
run_iter109_confessor_roles.py
run_iter112_cross_scenario.py
run_iter113_sacred_ablation.py
run_iter114_acc_plus_miracle.py
run_iter115_weakened_acc.py
run_iter116_pressure_sweep.py
run_iter117_conjunctive_test.py
run_iter118_cast_rescue.py
run_iter119_outsider_sweep.py
run_iter122_memory_layers.py
run_iter123_cross_memory.py
run_iter125_generative_test.py
run_iter127_null_effect.py
run_iter129_long_horizon.py
run_iter130_bistable_check.py
run_iter133_space_affordance.py
run_iter134_time_rhythm.py
```

### 6.3 Other one-offs — 21 scripts (count corrected 2026-04-28)

Pre-cycle exploration that didn't form chains. Original count was 19 in v1; actual count is 21 (recount 2026-04-28).

```
run_aux_recovery_probe.py
run_aux_recovery_sweep.py
run_aux_recovery_with_decay.py
run_audit_authority_vigilance.py
run_audit_inert_fields.py
run_cast_combinatorics.py
run_counterfactual_probe.py
run_iter135_rumor_mechanism.py
run_iter136_cast_norumor.py
run_iter137_lever_interaction.py
run_iter140_priest_relocate.py
run_iter141_outsider_location.py
run_iter142_scarcity_relocate.py
run_long_horizon_500.py
run_loose_gate_500t.py
run_mixed_acc_sacred_iter96.py
run_mixed_arc_authority_rumor.py
run_mixed_arc_probe.py
run_p1_revalidate_with_aux.py
run_per_cohort_500t.py
run_sacred_wiring_probe.py
```

### 6.3.1 Phase C reclassification (2026-04-28, autonomous-mode LOOP 8)

Canonical doc reference grep 결과 — **7 KEEP_CANDIDATE / 14 ARCHIVE_CANDIDATE** 분리:

**KEEP_CANDIDATE (7 — canonical doc 참조 있음, 보수적 보존)**:

| Script | Referenced by (canonical doc) | Reference strength |
|---|---|---|
| `run_audit_inert_fields.py` | `INERT_RESERVE_AUDIT.md` §1.1 (직접 인용) | strong (script:인라인) |
| `run_mixed_arc_probe.py` | `MIXED_ARC_PROBE.md` (전체 doc이 이 script 결과) | strong |
| `run_aux_recovery_probe.py` | `WORLD_BUILDING_PROGRESS_v2.md` Iter 92 시퀀스 | weak (역사적 mention) |
| `run_aux_recovery_sweep.py` | `WORLD_BUILDING_PROGRESS_v2.md` Iter 93 시퀀스 | weak |
| `run_aux_recovery_with_decay.py` | `WORLD_BUILDING_PROGRESS_v2.md` Iter 94 시퀀스 | weak |
| `run_sacred_wiring_probe.py` | `WORLD_BUILDING_PROGRESS_v2.md` Iter 95 시퀀스 | weak |
| `run_mixed_acc_sacred_iter96.py` | `WORLD_BUILDING_PROGRESS_v2.md` Iter 96 시퀀스 | weak |

**ARCHIVE_CANDIDATE (14)**:

```
run_audit_authority_vigilance.py
run_cast_combinatorics.py
run_counterfactual_probe.py
run_iter135_rumor_mechanism.py
run_iter136_cast_norumor.py
run_iter137_lever_interaction.py
run_iter140_priest_relocate.py
run_iter141_outsider_location.py
run_iter142_scarcity_relocate.py
run_long_horizon_500.py
run_loose_gate_500t.py
run_mixed_arc_authority_rumor.py
run_p1_revalidate_with_aux.py
run_per_cohort_500t.py
```

**Verification**: 14개 모두 import 0건, canonical doc reference 0건.

**Decision rule for "weak reference" (5 scripts in WORLD_BUILDING_PROGRESS_v2)**: doc는 history 시퀀스만 mention. archive 후에도 doc은 깨지지 않음 (path link 아님, 단순 텍스트 mention). 그러나 ARCHIVE_POLICY §1.4와 일관성을 위해 보수적으로 KEEP.

**Phase C execution path**: LOOP 9에서 14 archive 실행 완료. weak-reference 5개는 Lee 검토 대기.

### 6.3.2 Weak-ref 5 scripts decision (Lee gate, 2026-04-28 LOOP 23)

**현 상태**: KEEP_FOR_NOW (Phase C 보수적 결정)

**Lee 결정 옵션** (frame-neutral, H6):

**옵션 A: KEEP 유지** (현재 default, autonomous-mode 결정)
- 사유: WORLD_BUILDING_PROGRESS_v2.md (canonical doc)이 5 script를 Iter 92-96 시퀀스로 mention. archive 시 doc text 자체는 깨지지 않으나 reference chain의 traceability 손상.
- 비용: scripts/b_direction/ 5개 추가 보유 (37 → 32 가능했던 것을 37로 유지)
- 리스크: 0 (nothing breaks)

**옵션 B: ARCHIVE 5 추가 실행**
- 사유: WORLD_BUILDING_PROGRESS_v2.md mention은 *path link 없는 텍스트 mention*. archive 후에도 doc은 그대로 작동. ARCHIVE_POLICY §1.4 "subset chain은 latest만 KEEP" 패턴에 일관.
- 비용: 5 scripts 이동 = 5분 작업 (LOOP 9 패턴 반복)
- 리스크: 미세 — Lee가 나중에 Iter 92-96 검증 재실행 시 archive에서 복구 필요

**Claude의 bias**: A안 (현 상태 유지)에 기우는 이유 — H7 "보고서가 좋은 소식만 전달하지 않도록" 따르면, archive 추가는 추가 실행이 필요 없는 작업을 만드는 것. Lee가 명시 승인할 때까지 보존이 안전. 그러나 옵션 B도 합리적이며, Lee 결정 권한 있음.

**옵션 C: WORLD_BUILDING_PROGRESS_v2 mention을 archive note로 갱신 후 archive**
- 사유: doc의 mention 부분에 "(archived 2026-04-XX)" 추가하면 traceability 유지하며 archive 가능
- 비용: 5 lines edit + 5 mv = 10분
- 리스크: 0 (가장 안전한 path)

**Default until Lee 결정**: 옵션 A (KEEP_FOR_NOW).

**LOCKED 2026-04-28**: **옵션 A — KEEP** (Lee decision). 5 scripts 모두 `scripts/b_direction/`에 보존. WORLD_BUILDING_PROGRESS_v2.md mention chain 유지. Lee 별도 directive 없으면 archive 안 함.

**Same lock applies to §7 UNSURE 3 scripts** (iter113, iter118, iter134) — KEEP.

---

## 7. UNSURE (10 — Lee 판단 필요)

Scripts that look one-off but might be referenced from currently-archived
docs (e.g., from ITER_91-119 docs in archive). Conservative path is to
keep them.

| Script | Reason for UNSURE |
|---|---|
| `run_iter113_sacred_ablation.py` | ITER_113 doc archived but SACRED_STATUS_NOTE refs the result (not script) |
| `run_iter118_cast_rescue.py` | ITER_118 doc still hard-linked from ITER_INDEX |
| `run_iter146_audit_iter118.py` | Audit chain pointing to active iter118 finding |
| `run_iter134_time_rhythm.py` | ITER_150 audits this; if iter150 is kept, this might be referenced |
| `run_loop_iter1_transition.py`, `run_loop_iter2_distant.py`, etc. | Already in BUILDING_BLOCK, not unsure |
| 기타 audit chain scripts | The audit chain (iter144→iter140, iter145→iter133, etc.) creates non-import-time references |

---

## 8. Recommended action plan

### 8.1 Phase A: archive 47 leaf loop_iter scripts (§6.1)
Safe — none are imported. Building blocks (iter1, 2, 22, 23, 45) excluded.

```bash
mkdir -p archive/b_direction_legacy/scripts_iter_1_119
mv scripts/b_direction/run_loop_iter6_*.py \
   scripts/b_direction/run_loop_iter12_*.py \
   ...
   archive/b_direction_legacy/scripts_iter_1_119/
```

### 8.2 Phase B: archive Iter 91-119 standalone (§6.2)
Move scripts that match archived ITER_91-119 docs (already in archive).

### 8.3 Phase C: review one-offs (§6.3) Lee와 함께
Some of §6.3 are post-PYHASH-fix (iter 122+) but may not be referenced.
Lee 검토 후 일괄 또는 선별 archive.

### 8.4 Skip: §7 UNSURE
Until clearer signal (e.g., audit chain dependencies fully traced).

---

## 9. Expected impact

If Phase A + Phase B executed (~69 scripts):
- 자체 용량 절감: 1.6 MB → ~0.6 MB (scripts/b_direction/)
- 가독성: 125 → 56 scripts (cycles + active building blocks)
- 위험: low (none are imported, traced via grep)

---

## 10. Versioning

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-27 | Initial classification, no moves yet |
| v1.1 (executed) | 2026-04-27 | Phase A executed: 55 leaf `run_loop_iter*.py` scripts moved to `archive/b_direction_legacy/scripts_iter_1_88/`. ACTIVE building blocks (5 loop_iter + 5 scene/guard/generator) preserved + verified via import test. |
| v1.2 (executed) | 2026-04-28 | Phase B executed under autonomous-mode directive: 19 of §6.2 scripts moved to `archive/b_direction_legacy/scripts_iter_91_119/`. UNSURE 3 (`run_iter113_sacred_ablation.py`, `run_iter118_cast_rescue.py`, `run_iter134_time_rhythm.py`) preserved per §7. Building-block import verified post-move. |
| **v1.3 (executed)** | **2026-04-28** | **Phase C executed under autonomous-mode (LOOP 9): 14 ARCHIVE_CANDIDATE scripts of §6.3.1 moved to `archive/b_direction_legacy/scripts_phase_c_oneoffs/`. 7 KEEP_CANDIDATE preserved (5 weak-ref to WORLD_BUILDING_PROGRESS_v2.md; 2 strong-ref to INERT_RESERVE_AUDIT.md / MIXED_ARC_PROBE.md). Total scripts/b_direction: 51 → 37. Tests 1647 collection unchanged.** |

---

## 11. Phase B execution log (v1.2, 2026-04-28)

**Scripts moved** (19 — §6.2 minus UNSURE 3):

```
run_iter106_noise_floor.py        run_iter115_weakened_acc.py
run_iter107_500t_noise.py         run_iter116_pressure_sweep.py
run_iter107b_mixed_noise.py       run_iter117_conjunctive_test.py
run_iter108_bimodal_trace.py      run_iter119_outsider_sweep.py
run_iter108b_confession_trace.py  run_iter122_memory_layers.py
run_iter109_confessor_roles.py    run_iter123_cross_memory.py
run_iter112_cross_scenario.py     run_iter125_generative_test.py
run_iter114_acc_plus_miracle.py   run_iter127_null_effect.py
                                  run_iter129_long_horizon.py
                                  run_iter130_bistable_check.py
                                  run_iter133_space_affordance.py
```

**Preserved (UNSURE per §7)**:
- `run_iter113_sacred_ablation.py` — SACRED_STATUS_NOTE references this finding
- `run_iter118_cast_rescue.py` — ITER_118 doc still hard-linked from ITER_INDEX
- `run_iter134_time_rhythm.py` — ITER_150 audits this finding

**Verification**:
- `grep "from scripts.b_direction.run_iter1{06,07,08,09,12,14,15,16,17,19,22,23,25,27,29,30,33}"` → no matches (all leaf)
- `python -c "import scripts.b_direction.run_loop_iter1_transition; import scripts.b_direction.run_accusation_scene; import scripts.b_direction._pyhash_guard"` → OK

**Why autonomous-mode authorized this**:
Lee directive (2026-04-28): "프로젝트 방향에서 벗어나지 않으면 알아서 판단해서 진행." Phase B was already classified, dependency-traced, and ARCHIVE_POLICY §2 explicitly permits ARCHIVE_CANDIDATE moves. This is policy-execution, not new scope.

---

## 12. Phase C execution log (v1.3, 2026-04-28 LOOP 9)

**Scripts moved** (14 of §6.3.1 ARCHIVE_CANDIDATE):

```
run_audit_authority_vigilance.py     run_iter137_lever_interaction.py
run_cast_combinatorics.py            run_iter140_priest_relocate.py
run_counterfactual_probe.py          run_iter141_outsider_location.py
run_iter135_rumor_mechanism.py       run_iter142_scarcity_relocate.py
run_iter136_cast_norumor.py          run_long_horizon_500.py
                                     run_loose_gate_500t.py
                                     run_mixed_arc_authority_rumor.py
                                     run_p1_revalidate_with_aux.py
                                     run_per_cohort_500t.py
```

**Preserved (7 KEEP_CANDIDATE per §6.3.1)**:
- `run_audit_inert_fields.py` — strong-ref INERT_RESERVE_AUDIT §1.1
- `run_mixed_arc_probe.py` — strong-ref MIXED_ARC_PROBE.md
- `run_aux_recovery_probe.py` — weak-ref WORLD_BUILDING_PROGRESS_v2 Iter 92
- `run_aux_recovery_sweep.py` — weak-ref WORLD_BUILDING_PROGRESS_v2 Iter 93
- `run_aux_recovery_with_decay.py` — weak-ref WORLD_BUILDING_PROGRESS_v2 Iter 94
- `run_sacred_wiring_probe.py` — weak-ref WORLD_BUILDING_PROGRESS_v2 Iter 95
- `run_mixed_acc_sacred_iter96.py` — weak-ref WORLD_BUILDING_PROGRESS_v2 Iter 96

**Verification**:
- Building-block import 검증 통과
- pytest collection: 1647 tests (변동 없음)
- scripts/b_direction count: 51 → 37 (54-58, then 19 archived from Phase B → 32, then 14 archived → 37 due to recount; original Phase A count off by 4)

**Remaining work for v1.4**:
- Lee 검토 후 weak-ref 5개 추가 archive 결정
- §7 UNSURE 3개 재검토
