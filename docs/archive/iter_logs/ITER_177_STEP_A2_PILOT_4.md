# Iter 177 -- Step A2: Readability Pilot 4-Probe Set

**Date:** 2026-04-26
**Iteration:** Iter 177 (Step 2/7 of new directive)
**Severity:** LOW -- pilot eval material prep
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step A2

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "A2. Step C를 12개 full run 전, 4개 pilot blind로 축소 실행 가능한 형태로 준비
> 인간 평가가 늦어질 수 있으므로, full blind 전에 pilot 4개 세트를 먼저 뽑아놓는다.
> 구성: 원본 2개, annotated 2개, scenario/seed balanced
> 목적: 원본 vs annotated readability 차이를 작게라도 검증할 수 있게 만들기
>       인간이 1~2시간 대신 15~20분 안에 반응할 수 있도록 문턱 낮추기
> 산출물: docs/b_direction/READABILITY_PILOT_4.md, docs/b_direction/readability_pilot/"

---

## 1. What I did

### 1.1 4-probe selection
Computed P-to-scenario mapping using `random.Random(42)` shuffle (matches
existing generator). Selected 4 probes for pilot:

| Pilot | Source | Scenario | Seed | Variant | Format |
|---|---|---|---|---|---|
| PILOT_1 | P10 | accusation | 0 | baseline | original |
| PILOT_2 | P9 | scarcity | 0 | baseline | original |
| PILOT_3 | P4 | sacred | 0 | baseline | annotated |
| PILOT_4 | P3 | accusation | 0 | p2a_off | annotated |

### 1.2 Files created
- `docs/b_direction/readability_pilot/PILOT_{1-4}_{original,annotated}.txt`
  (renamed headers to PILOT_N for clean blind presentation)
- `docs/b_direction/READABILITY_PILOT_4.md` (guide doc with selection
  rationale, ground truth (collapsed), results template, branch decision rule)

---

## 2. Selection rationale

| Axis | Coverage |
|---|---|
| Scenarios | 3 of 3 (accusation x2, scarcity x1, sacred x1) |
| Variants | 3 baselines + 1 p2a_off (recovery-blocked) |
| Seeds | All seed=0 (cleanest comparison; seed variance is not pilot's axis) |
| Format split | 2 original + 2 annotated |

### Cross-axis comparisons enabled
- Format on accusation: PILOT_1 vs PILOT_4
- Format across scenarios: PILOT_1+2 (originals) vs PILOT_3+4 (annotated)
- Mechanism axis within annotated: PILOT_3 (sacred baseline) vs PILOT_4
  (accusation p2a_off)

### What I avoided
- **Within-scenario format pair**: e.g., showing the same (accusation, seed=0,
  baseline) probe in both formats. This was deliberately avoided because seeing
  the same data twice would contaminate the second read. If needed, expand to
  a 6-probe pilot with the same-data pair.
- **Multi-seed coverage**: only seed=0. P11 (accusation seed=3), P2 (scarcity
  seed=2) excluded.
- **Sham_mul variants**: P1, P7 excluded.

---

## 3. Branch decision rule embedded in pilot doc

| Pilot outcome | Action |
|---|---|
| Annotated >> original (e.g., 3-4 readable / 1 readable) | Branch A confirmed |
| Annotated ≈ original | Branch B simplification priority (format doesn't help) |
| Both unreadable | Branch B strong, recovery diversification revisit |
| Both readable | Branch C ready, world-side legible externally |

These thresholds at N=4 are noisy (1 probe shift can flip verdict). Treat as
hint, not final answer. Pilot serves to **lower the threshold for human
evaluation**, not to substitute for it.

---

## 4. Lee가 원한 것 / 내가 한 것 대비 (H5)

| Lee 요구 | 내가 한 것 | Status |
|---|---|---|
| 원본 2개 | PILOT_1 (P10), PILOT_2 (P9) | DONE |
| annotated 2개 | PILOT_3 (P4), PILOT_4 (P3) | DONE |
| scenario/seed balanced | 3 시나리오 + 1 variant 커버; seed=0 통일 | PARTIAL (seed 통일은 의도적, balanced와 다름) |
| 1-2 hour → 15-20 min | 4 probes × 3-5 min = 12-20 min target | DONE |
| 산출물 doc | READABILITY_PILOT_4.md (273 lines) | DONE |
| 산출물 디렉토리 | readability_pilot/ + 4 files | DONE |

**축소 해석한 부분 (Lee 재확인 요청)**: "scenario/seed balanced"의 "balanced"
의미가 모호. 두 가지 해석:
1. **Scenario 균형 (내 해석)**: 3 시나리오를 골고루 커버. seed는 통일.
2. **Seed 균형도 포함**: scenario × seed 격자에서 균형.

해석 1로 진행한 이유: N=4에서 scenario 3개와 seed 다양성을 모두 커버하면
신호가 분산됨. 시나리오 균형이 우선이고, seed 다양성은 full 12-probe eval에서
다룬다.

---

## 5. What could still be wrong (H4)

### 5.1 Probe selection bias
- 내가 (assistant) 4개 probe를 선택. 다른 선택 (예: P11+P2 포함)이 다른 신호 줄 수 있음.
- §2 rationale은 defensible 하지만 unique 하지 않음.

### 5.2 Format axis 격리 부족
- PILOT_1 (original baseline) vs PILOT_4 (annotated p2a_off) 은 scenario는
  같지만 variant가 다름. 순수 format 비교가 아니라 format×variant 혼합.
- 순수 format 비교는 within-(scenario,seed,variant) 쌍이어야 가능. §1.2.1 §What I avoided 참조.

### 5.3 Header rename 부작용
- PILOT_N 헤더로 변경하면서 source P-index가 보이지 않음. evaluator가 후속
  분석에서 원본 P 파일을 찾을 때 추가 매핑 필요. 가이드 doc §3에 매핑 보존.

### 5.4 Annotated probe ground-truth leak
- annotated probes는 cohort 라벨 (recovery / saturation / partial / no shame)
  포함. evaluator가 라벨에서 시나리오 추론 가능 (예: scarcity baseline은
  cohort outcome 패턴이 sacred와 다름).
- 이는 annotated format의 의도된 trade-off. blind 순수성을 약간 양보하고
  presentation efficacy를 측정.

### 5.5 N=4 통계 신호
- N=4에서 1 probe shift가 verdict를 뒤집음. §3 rule은 hint 수준.
- "Annotated >> original" 기준 (3-4 vs ≤1) 은 boundary 명확하지만 inter-rater
  variance를 측정하지 못함.

---

## 6. What I did NOT try (H2)

- 6-probe pilot (within-scenario format pair 포함)
- Multi-evaluator pilot 설계 (inter-rater agreement 측정)
- 자동 readability scoring (heuristic 기반 baseline 측정)
- Pilot results auto-comparison 도구 (지금은 manual 비교)
- Q-set v2 적용 (Step A3에서 분리)

이유:
- N=4 scope 유지 (디렉티브 §A2)
- 한 iter에 1 step 원칙 (디렉티브 §7 순서)

---

## 7. Alternate interpretations (H4)

- **"balanced" = scenario × seed 격자 균형**: 그러면 PILOT 세트 재구성 필요.
  현재 4 slot에서는 어쩔 수 없이 부분 커버.
- **"15-20 min"은 reading time만**: 그러면 답안 작성 시간 추가. 가이드 doc은
  reading 12-16 min + writing 3-4 min으로 분배.
- **"pilot blind" = 정답 절대 비공개**: §3 ground truth 표시 (collapsed)도
  부적절할 수 있음. 현재는 collapsed details 태그로 의도적 hide.

---

## 8. 진행 상황

| Step | 상태 |
|---|---|
| A1: annotated probe 포맷 표준화 | DONE (Iter 176) |
| **A2: readability pilot 4 세트 준비** | **DONE (이번 iter)** |
| A3: Readability Blind Protocol V2 + Results V2 | NEXT (Iter 178) |
| B1: component ledger 업데이트 (5 RESERVE) | PENDING |
| B2: breach_count + unwired field 문서화 | PENDING |
| B3: SACRED_STATUS_NOTE.md | PENDING |
| B4: KERNEL_GAPS.md | PENDING |

---

## 9. 결론

**산출물**:
- `docs/b_direction/READABILITY_PILOT_4.md` (273 lines)
- `docs/b_direction/readability_pilot/PILOT_{1-4}_{original,annotated}.txt`

**Pilot 효과**: 기존 12-probe blind eval (1-2 시간) → 4-probe pilot (15-20 분).
Format axis 부분 격리 + 3 시나리오 + 1 structural variant 커버. N=4 신호는
hint 수준이며, full 12-probe eval를 대체하지 않고 보완.

**No engine changes**, no generator changes. 순수 probe 선택 + 가이드 작성.

다음 iter (Step A3)에서 Q-set v2를 반영한 Readability Blind Protocol V2 +
Results V2 템플릿을 생성할 예정. 기존 V1 protocol에 이미 v2 Q-set이 일부
반영되어 있으므로, V2는 protocol 명시화 + pilot adaptation에 집중.
