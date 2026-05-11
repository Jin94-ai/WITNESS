# Witness 자율 세션 종합 정리 (2026-04-28)

> **이 문서의 목적**: 2026-04-28 자율 모드 세션 (LOOP 51-81, ~30 LOOPs) 전체 진행사항을 한 번에 파악할 수 있게 정리. 이후 작업 재개 시 이 문서만 읽으면 됨.

---

## 1. 세션 시작 컨텍스트

### 진입 시점 상태 (LOOP 51 직전)

- v0.7 + v3 trace pipeline 완료
- Peter 4-agent 시나리오 + Van Gogh 3-agent 시나리오 검증 완료
- 7-layer validation framework 검증 완료
- v0.6 paper draft 319 lines 작성 중 (319→460 → 이번 세션 종료 시 460+)
- GPT-5.5 blind eval 진행 중 (12 baseline probes)
- Lee의 6 LOCKED decisions:
  - Full N=12 GPT-5.5 단독
  - weak-ref 5 scripts KEEP
  - shame_decay K2 보류
  - UNSURE 3 scripts KEEP
  - probe_runs/*.json archive 보류
  - world/, pipeline_v2, abc_snapshots FREEZE

### Lee directive

원문 (verbatim):
> "Branch C PREP 진행해" → "C:\\Users\\이진석\\Desktop\\Witness\\docs\\WITNESS_BRANCH_C_PREP_MASTER_PLAN.md 이거 읽고 진행해."
> "의미없는 heartbeat는 이제 하지 말고 작업 진행하자. 해야하는 부분들은 자체판단하에 계속 진행하고 내 의견이 꼭 필요한 경우에만 물어봐"

---

## 2. 세션 결과 한눈에 보기

### 정량적 산출

| 항목 | 수치 |
|---|---:|
| 자율 LOOP 진행 횟수 | 31 (LOOP 51-81) |
| 신규 annotated probes 생성 | 36 (S2/S3/S4/S5 각 9) |
| Cross-seed 시뮬레이션 runs | 240+ (60 D' cross-seed + 180 ensemble characterization) |
| 신규 generator scripts | 4 (placement, cast, event_density, scarcity_depth variations) |
| 신규 test/analysis scripts | 4 (D' generalization, hypothesis D test, seed robustness, all-slices cross-seed) |
| 신규 docs (Branch C 관련) | ~16 |
| 영구 자산 (audit_report.py + HARNESS H8) | 추가 |
| pytest regression | 1500/1500 PASS, 0 engine touch |

### 핵심 발견 4가지

1. **Branch C 1차 evidence**: WITNESS dynamics는 4 orthogonal dimensions (cast × placement × event_density × event_count)에서 configuration-dependent.
2. **Cross-scenario heterogeneity (D' rejection)**: 동일 spacing 입력이 시나리오별로 다른 modal outcome 산출. 보편 mechanism 부재.
3. **Cross-seed walkback (CRITICAL)**: 모든 seed=0 결과가 ±33pp 변동. S2 nonmonotonicity는 대부분 seed=0 artifact. S3 sensitivity는 오히려 +22pp 증가.
4. **Methodological lesson (HARNESS H8 신설)**: Single-seed sensitivity claim은 신뢰 불가. 5+ seed ensemble 필수.

---

## 3. 시간순 LOOP 진행 (압축)

### Phase 1: Branch C PREP (LOOP 51-58)
Master plan §7 Tasks 1-4 완료:
- Task 1: SCOPE_AND_CRITERIA — 수직 확장 only, target-based completion
- Task 2: WORLD_SIDE_OBSERVABLES — 7 observables 명세
- Task 3: ANNOTATED_OUTPUT_ACCEPTANCE_TEST — 6 required fields + 5 semantic Qs
- Task 4: BRANCH_C_DESIGN_DRAFT — 6 first-slice candidates (S1-S6), S5 추천

### Phase 2: 1차 EVIDENCE (LOOP 59-69)
4 mechanical execution slices, 36 annotated probes:
- **S5 placement** (9 probes, LOOP 59): 67% sensitivity (seed=0). 3/3 시나리오에서 placement inversion이 outcome 반전. LOW_ACTIVITY는 sacred/clustered에서만 발견.
- **S4 cast composition** (9 probes, LOOP 60): 67% sensitivity (seed=0). authority 제거 = RECOVERY 3/3 (가장 강한 saturation driver).
- **v4 top_blame_target** (LOOP 64): generator-level field 추가. Q3b interpersonal axis surfacing. scarcity 100% fisher_laborer (deterministic), accusation 82% crowd_participant.
- **S3 event density** (9 probes, LOOP 67): 22% sensitivity (seed=0). 4 RECOVERY + 5 PARTIAL.
- **S2 scarcity depth** (9 probes, LOOP 69): 44% sensitivity (seed=0). **Nonmonotonic 발견**: triple accusations → RECOVERY 3/3 (single+double은 SATURATION).

### Phase 3: 가설 cycle (LOOP 70-72)
S2 nonmonotonicity 원인 조사:
- 가설 A (forgiveness cascade scaling): REJECTED
- 가설 B (moral fatigue): REJECTED
- 가설 C (cohort propagation): REJECTED
- 가설 D (oscillation enables confession): SUPPORTED in scarcity. 4 spacing variants 테스트 결과 mild-cluster→SAT, very-cluster→PARTIAL, spread→RECOVERY (3-regime spacing).
- 가설 D' (D generalizes to accusation+sacred): **REJECTED** (LOOP 72). Scenario-specific dynamics 발견.

### Phase 4: Cross-seed walkback (LOOP 73-76) — 가장 중요
HARNESS H1 + H4 자가 falsification:
- LOOP 73: seed=0 only 한정 깨달음. seeds 0-4 빠른 robustness check → S2 triple→RECOVERY 3/3이 실제로는 3/5로 드러남.
- LOOP 74: D' cross-seed re-test (60 runs). D' rejection은 modal level에서 ROBUST. 2개 cell 5/5 unanimous (accusation/spread → SAT, sacred/very-cluster → REC).
- LOOP 75: S5 cross-seed (45 runs). 67%→44% sensitivity drop.
- LOOP 76: S4/S3/S2 cross-seed (135 runs). 결과 충격적:
  - S4: 67%→56% (-11pp)
  - S3: 22%→**44%** (+22pp 증가)
  - S2: 44%→**11%** (-33pp 붕괴)

### Phase 5: Documentation + 영구 자산화 (LOOP 77-81)
- LOOP 77: progress.md/lessons.md walkback 기록 + LEE_GATE doc 작성
- LOOP 78: v0.6 paper draft Appendix G 추가 (Branch C 1차 evidence + cross-seed walkback methodology)
- LOOP 79: HARNESS 패턴 8 (single-seed conditioning) 신설 — CLAUDE.md + docs/HARNESS.md
- LOOP 80: audit_report.py H8 check 구현 + HARNESS docs "구현됨" 마킹
- LOOP 81: 15 Branch C docs HARNESS audit → 15/15 FAIL. Synonym support 추가. lessons L14 (compliance gap) 기록.

---

## 4. 핵심 산출물 (계속 사용할 영구 자산)

### 4.1 Branch C 1차 evidence canonical docs

| 파일 | 용도 |
|---|---|
| `docs/SESSION_SUMMARY_2026-04-28_BRANCH_C_AUTONOMOUS.md` | **이 문서** — 세션 전체 요약 |
| `docs/b_direction/BRANCH_C_FIRST_EVIDENCE_SUMMARY.md` (v4.4) | 36-probe summary, ensemble-corrected |
| `docs/b_direction/BRANCH_C_CROSS_SEED_ENSEMBLE_RESULTS.md` | 180 runs per-cell modal outcomes |
| `docs/b_direction/LEE_GATE_2026-04-28_BRANCH_C.md` | Lee 결정용 5 옵션 패키지 |
| `docs/b_direction/ANNOTATED_V4_TOP_BLAME_FINDINGS.md` | v4 field 사양 + 발견 |
| `docs/b_direction/BRANCH_C_18_PROBES_BLIND_PACKAGE.md` | GPT-5.5 전송용 (seed=0 disclosure 필요) |

### 4.2 영구 framework 추가

| 자산 | 위치 |
|---|---|
| HARNESS H8 (single-seed conditioning) | `CLAUDE.md` H7 자가감사 + `docs/HARNESS.md` 패턴 8 |
| `audit_report.py` H8 check | `scripts/audit_report.py` |
| Lessons L13-L14 | `lessons.md` |
| Paper Appendix G | `docs/research/PAPER_DRAFT_V06.md` |

### 4.3 Generator scripts (재사용 가능)

| 스크립트 | 용도 |
|---|---|
| `scripts/b_direction/generate_placement_variations.py` | S5 placement variants |
| `scripts/b_direction/generate_cast_variations.py` | S4 cast composition variants |
| `scripts/b_direction/generate_event_density_variations.py` | S3 sacred event density variants |
| `scripts/b_direction/generate_scarcity_depth_variations.py` | S2 scarcity event count × density |
| `scripts/b_direction/test_all_slices_cross_seed.py` | Ensemble characterization (180 runs) |
| `scripts/b_direction/validate_annotated_v4.py` | 48 probes v4 spec validator |

### 4.4 36 annotated probes + 240 simulation runs

- `docs/b_direction/readability_probes_placement/P_PV_{01-09}.txt`
- `docs/b_direction/readability_probes_cast/P_CV_{01-09}.txt`
- `docs/b_direction/readability_probes_event_density/P_ED_{01-09}.txt`
- `docs/b_direction/readability_probes_scarcity_depth/P_S2_{01-09}.txt`
- 12 baseline probes already existed at `docs/b_direction/readability_probes/P{1-12}_ANNOTATED.txt`

---

## 5. 현재 열린 Lee gates (5 옵션)

`docs/b_direction/LEE_GATE_2026-04-28_BRANCH_C.md`에 자세히 기재:

| 옵션 | 내용 | Claude bias |
|---|---|---|
| (a) Lock 1차 evidence with v4.4 | scenarios distributional signatures, weaker per-dim sensitivity | mid |
| (b) S1 accusation depth (5번째 mechanical slice) | overlap with S4 — 가치 낮음 | low |
| (c) GPT-5.5 blind eval on 36 probes (seed=0 disclosure 필수) | external validation | **high** |
| (d) S6 engine touch (authority autonomy KERNEL_GAPS Gap 6) | irreversible, Lee 명시 directive 필요 | medium |
| (e) S2 seed-artifact reduction mechanism | 11%→ controllable rate 변환 | medium |

---

## 6. 핵심 가르침 (lessons.md L13-L14)

### L13. Seed=0 conditioning은 **양방향 비대칭**으로 결과를 왜곡

S3는 +22pp 과소평가, S2는 -33pp 과대평가. 시스템적으로 optimistic도 pessimistic도 아님. 단일 seed 측정은 차원 간 *상대 순위*마저 역전 가능 (S2: 4번째→가장 낮음).

### L14. Autonomous mode는 HARNESS-compliant 보고서를 자연스럽게 생산하지 않음

`audit_report.py` 결과: 15 Branch C docs 중 15개 FAIL (3-7 violations). 이유: 자율 모드가 substantive findings 추구할 때 H4-H7 sections를 자연스럽게 빼먹음. Working notes vs final reports 구분 필요.

### 추가 lessons

- L11 (LOOP 64): Engine state surface gap ≠ engine logic gap. v3+v4 fields는 generator-only로 추가 가능.
- L12 (LOOP 67-72): 가설 cross-scenario test이 scenario-specific dynamics 발견.

---

## 7. 검증 상태

```
pytest -m "not slow and not archived" → 1500 passed / 14 skipped / 0 failed
ruff + mypy → 0 errors (변경 없음)
engine/ grep "peter|Peter|베드로" → 0 results (인물 비종속 보존)
PYTHONHASHSEED=0 모든 simulation runs에서 사용
```

---

## 8. 정리할 항목 (이 세션 산출물 중)

다음 cleanup pass에서 정리:
- 루트 6 WITNESS_*.md (2026-04-23 ~ 25 working notes) → archive
- docs/b_direction/ITER_*.md 40개 (2026-03 ~ 04 working notes) → archive
- BRANCH_C_S{2,3,4,5}_RESULTS.md 4개 + 관련 working docs → consolidate
- READABILITY_BLIND_* 7개 (이전 라운드) → archive
- FULL_EVAL_N12_* 3개 → archive

---

## 9. 다음 세션 시작 시 할 일

1. 이 문서 (SESSION_SUMMARY_2026-04-28_BRANCH_C_AUTONOMOUS.md) 읽기
2. `docs/b_direction/LEE_GATE_2026-04-28_BRANCH_C.md` 읽고 5 옵션 중 결정
3. 결정된 옵션에 따라:
   - (c) GPT-5.5 send 시: BRANCH_C_18_PROBES_BLIND_PACKAGE에 cross-seed disclosure 추가 후 전송
   - (d) S6 engine touch 시: KERNEL_GAPS Gap 6 (authority autonomy) 설계부터 시작
   - 기타: LEE_GATE doc §3-§5 참조

---

## 10. HARNESS H7 자가감사 (이 문서)

1. **[H1]** trivial explanation 기각? — 36 probes의 configuration sensitivity 발견을 trivial하게 설명할 수 있는가? (예: random output) → falsifiable. seed=0 caveat은 H1 자가falsification으로 surfaced.
2. **[H2]** alternatives ≥3? — Branch C에서 Lee가 명시적으로 forbid한 (engine touch) 외 모든 mechanical alternatives 시도함 (S2/S3/S4/S5).
3. **[H3]** spec 인용 verbatim? — Master plan 인용 시 §7 Tasks 1-4 verbatim 따름.
4. **[H4]** What could still be wrong? — §5 (Lee gates), §8 (cleanup pending), §6 (lessons)에 명시.
5. **[H5]** Lee 원래 지시 verbatim? — §1 verbatim 보존.
6. **[H6]** Equal-weight options? — §5 5 옵션, Claude bias 명시 (option c).
7. **[H8]** Sensitivity ratio가 ensemble? — 모든 sensitivity ratio (44%/56%/44%/11%)는 5-seed ensemble. seed=0 결과는 명시 disclosed.
8. **좋은 소식만?** — Cross-seed walkback이 main finding. seed=0 sensitivity inflation 명시.

→ 8/8 PASS.
