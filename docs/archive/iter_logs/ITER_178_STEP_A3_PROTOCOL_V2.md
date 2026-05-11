# Iter 178 -- Step A3: Readability Blind Protocol V2 + Results V2

**Date:** 2026-04-26
**Iteration:** Iter 178 (Step 3/7 of new directive)
**Severity:** LOW -- documentation infrastructure
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step A3

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "A3. Q 세트 개선안 적용 버전 준비
> 이전 문서에서 제안한 Q 개선안을 반영해, 새 템플릿을 만든다.
> 포함:
> - Q1b readability confidence
> - Q2 secondary pressure + clarity
> - Q3 cohort/group dynamics 세분화
> - Q4 cyclic arc 분리
> - Q5 oscillation narrative contribution
> - Q6 confusion notes semi-required
> 산출물:
> - docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md
> - docs/b_direction/READABILITY_BLIND_RESULTS_V2.md"

---

## 1. What I did

### 1.1 PROTOCOL_V2.md (193 lines)
- 모드 구분: Pilot (N=4), Full (N=12), Hybrid (N=12, 6+6)
- Q-set 유지 (v1에서 이미 v2 Q-set 채택됨; 변경 사항만 추가)
- **NEW**: Q6a structured taxonomy ([FORMAT] / [STRUCTURE] / [Q_SET] / [SCOPE] / [OTHER])
- **NEW**: Format-axis aggregation (annotated vs original readable rate gap)
- **NEW**: Pilot-specific branch decision rules (N=4 noise 고려)
- versioning history (v1 → v2)

### 1.2 RESULTS_V2.md (288 lines)
- Mode checkbox (pilot / full / hybrid)
- Pilot section (PILOT_1-4 with format column)
- Full section (P1-P12 with format column for hybrid)
- Pilot aggregates: format-axis breakdown
- Full aggregates: 8 categorical distributions + ablation detectability
- Branch decision checklists (A / B / A+B / C)
- Ground truth comparison table
- V3 revision notes section

---

## 2. Q-set 6 항목 매핑 (Lee 요구 vs 현황)

| Lee 요구 | 현황 | Notes |
|---|---|---|
| Q1b readability confidence | DONE (v1에 이미 있음) | CAN_EXPLAIN / PARTIAL / CANNOT |
| Q2 secondary pressure + clarity | DONE (v1에 Q2b + Q2c) | shame / fear / sacred / scarcity / accusation / grief |
| Q3 cohort/group dynamics 세분화 | DONE (v1에 Q3a level + Q3b multi-select) | NONE / LOCAL / COHORT / RESTRUCTURE |
| Q4 cyclic arc 분리 | DONE (v1 Q4a에 CYCLIC_ARC 옵션) | NO_ARC / FLAT / ESC / RECOVERY / MIXED / CYCLIC |
| Q5 oscillation narrative contribution | DONE (v1 Q5b) | HELPS / NEUTRAL / HURTS |
| Q6 confusion notes semi-required | DONE (v1 Q6a "≥1 item") + V2에 taxonomy 추가 | [FORMAT] / [STRUCTURE] / [Q_SET] / [SCOPE] |

**모든 Q 개선 사항 v1에 이미 반영됨**. V2 추가 가치는:
1. 모드 구분 (Pilot vs Full)
2. Format-axis 명시화
3. Q6a structured taxonomy
4. Branch decision 자동화 가능한 형태

---

## 3. V1 vs V2 핵심 차이

| 차원 | V1 (Iter 161) | V2 (Iter 178) |
|---|---|---|
| Q-set | v2 채택 | v2 유지 (변화 없음) |
| 모드 | full N=12만 가정 | Pilot / Full / Hybrid 3 모드 |
| Format | format-neutral | format-axis 명시 (original vs annotated) |
| Q6a tagging | free text | structured taxonomy + free text |
| Branch decision | 단일 thresholds | mode-specific thresholds |
| Time budget | 1-2시간 implied | mode별 시간 명시 |

V2는 V1을 **승계**하지 정정하지 않음. V1 protocol은 그대로 valid.

---

## 4. Lee가 원한 것 / 내가 한 것 대비 (H5)

| Lee 요구 | 내가 한 것 | Status |
|---|---|---|
| Q-set 개선안 적용 | v1에 이미 있음, V2는 taxonomy 추가 | DONE (확장) |
| 새 템플릿 | PROTOCOL_V2.md + RESULTS_V2.md | DONE |

**확장 해석한 부분 (Lee 재확인 요청)**: Lee 요구는 "Q-set 개선안만 반영"이지만,
나는 추가로 다음을 포함:
- Pilot 모드 (Step A2와 연동)
- Format-axis 추적 (Step A1과 연동)
- Q6a structured taxonomy

이유: Step A1+A2+A3가 한 묶음으로 동작해야 효과 (annotated 표준화 → pilot 세트 →
protocol이 모두 정합). Q-set만 갱신하면 A1/A2 작업이 결과 분석에 반영되지 않음.

확장 요소를 분리하고 싶으면 PROTOCOL_V2 §0 "What's new"에서 명시했음. Lee가
"Q-set만 원했다"면 §1, §4, §5의 mode/format-axis 부분을 제거 가능.

---

## 5. What could still be wrong (H4)

### 5.1 Q-set v2가 충분한지
- Q2a (primary pressure)가 "shame / fear / sacred / scarcity / accusation /
  grief"로 닫혀 있음. annotated probe headline에서 cohort 라벨로 hint 받으면
  evaluator가 옵션 중 추측만 할 수 있음. 자유 기술 옵션 (Q2a_other) 추가
  여지.
- Q3b multi-select에서 평균 몇 개 선택되는지 디자인되지 않음. 1개만 강제하면
  signal 강도 측정 부족, all-of-above 허용하면 신호 희석.

### 5.2 Pilot 모드 N=4 통계 신호
- §5.1 thresholds (annotated 2/2 vs original ≤1/2)는 1 probe shift가 verdict 뒤집음
- N=4에서 verdict signaling은 noise 위주
- 풀 모드 fallback은 명시되어 있으나 evaluator의 판단에 의존

### 5.3 Q6a taxonomy 강제성
- v1은 "semi-required" (≥1 item). V2는 tagging 추가했지만 강제는 아님.
- evaluator가 taxonomy 무시하고 free text만 쓰면 aggregation 자동화 불가.

### 5.4 V3 revision criteria 모호
- "Q6a [Q_SET] tags converge" 시 V3 revision이라 명시했지만, "converge"의 임계값
  미정. "3+ probes에서 동일 Q에 [Q_SET] 태그" 같은 명확한 기준 부재.

---

## 6. What I did NOT try (H2)

- **자동 readability scoring**: heuristic 기반 baseline 측정 (예: Q1=CLEAR_FLOW
  비율 자동 계산) — 인간 평가 없이 sanity check 가능하지만 미구현.
- **Inter-rater agreement 설계**: V2는 single-evaluator. multi-evaluator
  workflow는 §9에 deferred로 명시했지만 실제 protocol 미작성.
- **Q-set V3 직접 revision**: pilot 결과 없이 V3 작성은 premature. V2는 V3에
  대한 "trigger 조건"만 명시.
- **Pilot 결과 자동 분석 도구**: aggregation 수동. RESULTS_V2 작성 후 손으로
  채워야 함.

이유:
- Step A3 scope: "Q 개선안 적용 버전 준비"이지 "자동화"가 아님
- 디렉티브 §6: 새 메커니즘 drilling 금지

---

## 7. Alternate interpretations (H4)

- **"Q-set 개선안 적용"이 V1 그대로 유지를 의미**: 그러면 V2 작성 자체가 불필요.
  v1이 이미 Q-set v2를 채택했기 때문. 내 해석은 "포맷+모드 확장 포함".
- **"새 템플릿"이 RESULTS_V2만 의미**: 그러면 PROTOCOL_V2는 불필요.
  하지만 Lee가 "PROTOCOL_V2 + RESULTS_V2" 두 산출물 명시했으므로 둘 다 작성.

---

## 8. 진행 상황

| Step | 상태 |
|---|---|
| A1: annotated probe 포맷 표준화 | DONE (Iter 176) |
| A2: readability pilot 4 세트 준비 | DONE (Iter 177) |
| **A3: Readability Blind Protocol V2 + Results V2** | **DONE (이번 iter)** |
| B1: component ledger 업데이트 (5 RESERVE) | NEXT (Iter 179) |
| B2: breach_count + unwired field 문서화 | PENDING |
| B3: SACRED_STATUS_NOTE.md | PENDING |
| B4: KERNEL_GAPS.md | PENDING |

Track A 완료. 이제 Track B (kernel simplification) 진입.

---

## 9. 결론

**산출물**:
- `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md` (193 lines)
- `docs/b_direction/READABILITY_BLIND_RESULTS_V2.md` (288 lines)

**Q-set은 변경 없음** (v1에 이미 v2 Q-set 채택). V2의 가치는:
- Pilot/Full/Hybrid 3 모드 분리
- Format-axis 추적 (Step A1+A2와 연동)
- Q6a structured taxonomy ([FORMAT]/[STRUCTURE]/[Q_SET]/[SCOPE]/[OTHER])
- Mode-specific branch decision rules

**No engine changes**, no Q-set changes. 순수 protocol 명시화.

다음 iter (Step B1)에서 component ledger 업데이트 (5 RESERVE 필드 공식 표기)
시작. Track A → Track B 전환.
