# Anchor 2 Visual Validation — peter_scarcity_triple

**Date**: 2026-04-30
**Source**: `ANCHOR_2_VISUAL_VALIDATION_PLAN.md` 실행
**Anchor 1 (baseline)**: `peter_scarcity_baseline` seed=0 200 ticks (V0-V2 검증 기준)
**Anchor 2 (validation)**: `peter_scarcity_triple` seed=0 200 ticks (3 accusations cell)
**Verdict**: **Case A-2 — V2 기능은 완전 작동 (regression 0), 데이터 발산이 제한적 (single-seed limitation)**

---

## 0. 산출물

### 코드 변경
- `scripts/visual/export_dot_observer_data.py`: argparse 추가 (`--anchor`, `--seed`, `--n-ticks`, `--output`)
- `visual/dot_observer_replay.html`: query param `?data=<path>` 지원, 동적 subtitle (anchor info 표시)

### 데이터 생성
- `data/visual/dot_observer_data_triple.json` (823.7 KB) — `peter_scarcity_triple` seed=0 200 ticks

### Schema 변경 0
- 두 JSON 모두 `schema_version: v1`
- top-level fields 동일: `meta / ticks / candidates / salience_marks`
- tick fields 동일: `tick / world / groups / agents / active_events`
- HTML은 *기존 베이스라인*도 그대로 로드 (default fallback)

---

## 1. 사용 방법 (Anchor 2 visual replay)

```bash
# Anchor 2 데이터 export
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple \
    --output data/visual/dot_observer_data_triple.json

# HTTP server
python -m http.server 8000

# 브라우저
# Anchor 1 (default):
#   http://localhost:8000/visual/dot_observer_replay.html
# Anchor 2:
#   http://localhost:8000/visual/dot_observer_replay.html?data=../data/visual/dot_observer_data_triple.json
```

---

## 2. 가설별 검증 (H1-H5)

### H1. Salience marker noise가 anchor 2에서 어떻게 변하는가
**결과**: **거의 동일** (V2-1 mitigation 그대로 작동, 분포는 비슷).

| 분포 | baseline | triple |
|---|---|---|
| 총 marks | 197 | 197 |
| score-1 (yellow, opacity 0.18) | 145 (74%) | **158 (80%)** |
| score-2 (orange) | 47 | 34 |
| score-3 (red) | 5 | 5 |
| score-3 ticks | 15, 25, 142, 146, 147 | **동일** |

- score-3 5개가 정확히 같은 tick에 발생 → V2-1 mitigation 효과 anchor 2에서도 유지
- score-1이 약간 늘어남 (145→158, +9%) — 약간 더 noisy하지만 여전히 score-3 식별 가능
- → **V2-1 generalize OK**

### H2. Agent dynamism이 다른가
**결과**: **동일** — 4/12 dynamic (33%, 변화 없음).

| | baseline | triple |
|---|---|---|
| Dynamic agents (≥3 distinct states) | 4/12 | **4/12** |

- 시나리오 B의 "boring agent 67%" 약점이 *anchor 특성에 한정되지 않음*
- 두 anchor 모두 *4명만* dynamic
- → 시나리오 B 약점이 *V2 설계 결함*에 더 가까운 evidence (HARNESS H4 alternate interpretation falsify)
- 다만 단일 anchor family (둘 다 scarcity)이므로 cross-scenario generalization은 여전히 미검증

### H3. Candidate distribution이 다른가
**결과**: **분포는 동일, focal agent 1명 다름**.

| | baseline | triple |
|---|---|---|
| Total candidates | 8 | 8 |
| story_ready | 5 | **5** |
| observation_only | 0 | **0** |
| low_activity_hold | 3 | **3** |

| Candidate ID | baseline | triple |
|---|---|---|
| C01_t15 | ✓ | ✓ |
| C02_t25 | ✓ | ✓ |
| Person | P03_t66_agent_08 | **P02_t69_agent_05** |
| C03_t142 | ✓ | ✓ |
| C05_t147 | ✓ | ✓ |
| W03_t20 | ✓ | ✓ |
| E02_t102 | ✓ | ✓ |
| E03_t112 | ✓ | ✓ |

- 7/8 candidate ID 동일
- 1개 차이: person candidate가 `agent_08` (tick 66) → `agent_05` (tick 69)로 변경
- observation_only가 *여전히 0개* — V2-3 filter의 3rd bucket이 두 anchor 모두에서 비어있음
- → curation rule 자체가 *너무 strict*한 가능성 (별도 directive 시 threshold 검토)

### H4. Group split / tension이 더 잘 보이는가
**결과**: **약간 약함**.

| | baseline | triple |
|---|---|---|
| Group mode 변화 횟수 | 12 | **12** (동일) |
| Max tension | 1.00 | 0.97 |
| Avg tension | 0.183 | **0.144** (-21%) |

- mode 변화 횟수 동일 (L1만 활성, L2/L3 정적은 그대로)
- triple이 *약간 lower tension* — counterintuitive (selector notes "더 많은 accusation → 더 많은 recovery"와 일관)
- → group split visual은 anchor 2에서도 약함 (baseline과 비슷한 정도)

### H5. V2 features가 anchor 2에서 깨지지 않는가
**결과**: **모두 깨지지 않음 (regression 0)**.

| Feature | anchor 2 작동 |
|---|:---:|
| V2-1 marker noise opacity 차등 | ✅ score-3 5개 즉시 식별 가능 |
| V2-2 selected agent follow | ✅ panel auto-refresh 작동 (단, 4/12 boring agent 비율 동일) |
| V2-3 candidate filter | ✅ 5/0/3 toggle 작동, count 정확 |
| V2-4 candidate range overlay | ✅ tick_range 파란 overlay 정상 표시 |
| HTML query param `?data=` | ✅ triple JSON 즉시 로드, subtitle 갱신 |

---

## 3. 데이터 발산 통계

### 두 anchor 사이의 차이 (seed=0)

| 측정 | 값 |
|---|---|
| Differing ticks (event 또는 blame >0.05 차이) | **59/200** (29.5%) |
| Total active events: baseline / triple | 830 / **846** (+16, +2%) |
| Tension avg: baseline / triple | 0.183 / **0.144** (-21%) |
| 추가 accusation 발생 ticks (triple only) | tick 40, tick 100 (+2 accusations) |

### 핵심 관찰
- triple은 baseline + 2 extra accusations (tick 40 + tick 100)
- 그러나 *visual 시각적 차이는 미미*함 (group mode 변화는 동일, candidate 분포 거의 동일)
- 이유: `peter_scarcity_triple`은 *cross-seed* nonmonotonic finding (REC 3 / SAT 2 across 5 seeds)
- *seed=0 단일*에서는 baseline과 trajectory가 거의 동일

---

## 4. 시나리오 A/B/C 재검증 (anchor 2)

### 시나리오 A — World-first browsing
- **시작**: timeline-bar에 score-3 marker 5개 (tick 15, 25, 142, 146, 147 — baseline과 동일)
- **클릭 동작**: 정상 작동
- **panel 검토**: World @ tick + Salience tags + Active candidates 모두 갱신
- **차이**: tick 100에 *baseline에는 없던 public_accusation* 발생 (Active events panel에서 visible)
- **판정**: ✅ 작동 OK. 미세 차이는 panel 검토 시 visible.

### 시나리오 B — Agent-follow browsing
- **시작**: 4/12 dynamic agent — baseline과 동일 비율
- **focal agent 후보 변경**: candidate가 `agent_08`(baseline) → `agent_05`(triple) → 사용자가 *다른 agent*를 따라가게 됨
- **V2-2 panel auto-refresh**: 정상 작동
- **약점 그대로**: boring agent 비율 동일
- **판정**: △ 부분 작동. agent 식별 hint 부재 약점이 anchor 2에서도 동일.

### 시나리오 C — Candidate-first browsing
- **filter button**: 5 / 0 / 3 (baseline과 동일 분포)
- **5 카드 클릭 순회**: 정상 작동, range overlay 표시
- **observation_only가 여전히 0**: filter button 사용 가치 제한
- **판정**: ✅ 작동 OK, 다만 observation_only bucket이 비어있어 3-bucket 필터의 *2-bucket으로 사용*되는 셈.

### 시나리오 종합

| 시나리오 | baseline | triple |
|---|---|---|
| A. World-first | ✅ 강함 | **✅ 강함 (동일)** |
| B. Agent-follow | △ 부분 | **△ 부분 (동일)** |
| C. Candidate-first | ✅ 강함 | **✅ 강함 (동일)** |

→ V2 사용 흐름은 anchor 2에서도 baseline과 동일하게 작동.

---

## 5. HARNESS 적용

### What I did NOT try
- **Cross-seed visual** (seed 0~4 동시 비교): 가장 큰 누락. peter_scarcity_triple의 *진짜 차이*는 seed별 outcome 분포 (REC 3 / SAT 2). 단일-seed 시각화는 이 nonmonotonicity를 못 잡음.
- **vangogh_sacred_baseline (다른 scenario family) 검증**: cross-scenario generalization은 미검증
- **scarcity_high_density 검증**: cohort split 강도가 다른 anchor

### What could still be wrong
- "anchor 2 = peter_scarcity_triple"이 *충분한 차별점*을 제공한다는 가정 자체가 틀릴 수 있음
- 실제로는 두 anchor가 *같은 generator family + 동일 baseline parameters*를 공유 → seed=0 trajectory 거의 같음
- 진정한 generalization 검증은 *cross-scenario* (peter vs vangogh) 또는 *cross-seed* (5-seed ensemble visualization)이 필요

### Alternate interpretations
- (a) V2가 anchor-agnostic하게 작동 → Case A-1
- (b) Anchor 2가 baseline과 너무 유사해서 *진짜 generalization 검증 안 됨* → Case A-2 (이번 결과)
- (c) V2 자체가 약함 → Case B/C (해당 안 됨, V2 features 모두 작동)

→ HARNESS H8 일관: *single-seed conditioning이 sensitivity claim을 왜곡* — 이번에는 *single-seed identity가 anchor difference를 가림*.

---

## 6. 분기 판정

### Case A-1 vs A-2 vs B vs C

**Case A-1 (anchor 2도 잘 작동, V2 multi-anchor MVP)**:
- ✅ V2 features 모두 작동
- ✅ schema integrity 유지
- ❌ 그러나 *진정한 anchor difference*가 visual에 반영되지 않음 — anchor 2 데이터가 baseline과 너무 유사

**Case A-2 (일부 약하지만 핵심 작동) — 이번 결과**:
- ✅ V2 4 features 모두 작동, regression 0
- ✅ 5/8 시나리오 검증 통과 (A 강함, C 강함, B 부분)
- △ 데이터 발산이 제한적 (29.5% ticks 다름, 그러나 *visual 차이는 미미*)
- → encoding 자체 문제는 아님. *cross-seed visualization*이 필요할 수 있음 (별도 plan).

**Case B (anchor 2에서 의미 약함, encoding 재검토)**:
- 적용 안 됨 — V2 features 모두 작동, encoding 자체는 OK

**Case C (anchor 2에서 실패, visual 중단)**:
- 적용 안 됨 — visual은 작동, 단지 *데이터*가 baseline과 유사

### 결정: **Case A-2 — V2 generalize 부분 확인**

근거:
1. V2 4 features 모두 anchor 2에서 작동 (technical generalize ✅)
2. 시나리오 A + C 강한 도움 동일 (use-case generalize ✅)
3. 데이터 차이 (29.5%) 존재하지만 *visual에서 보이는 차이는 미미*
4. 핵심 약점 (시나리오 B boring agent 비율)이 anchor 2에서도 동일 → *V2 설계 한계*에 더 가까움 (HARNESS H4 alternate falsify)

---

## 7. 다음 단계 (Case A-2 후속)

### 본 review에서 권고하는 후속 (별도 directive 시)

1. **Cross-seed visualization** (가장 큰 잠재 가치):
   - 5 seeds를 timeline 위에 layered로 표시 (각 seed가 다른 색)
   - peter_scarcity_triple의 nonmonotonic 발견을 *visual로* 보여줄 수 있음
   - 작업 단가: 큼 (~3-4시간), 별도 directive 필요

2. **Cross-scenario validation** (vangogh_sacred):
   - 정말 다른 metric system에서 V2 작동 검증
   - 작업 단가: 중간 (~1-2시간), 별도 directive 필요

3. **시나리오 B agent identification hint** (V2 약점 직접 해결):
   - dot에 "trajectory dynamism" badge (export 단계 계산)
   - 작업 단가: 작음 (~30분), 별도 directive 필요

### 본 review에서 *하지 않은* 것
- 새 lens / 새 metric / 새 bucket 추가 (Lee directive 금지)
- V3 panel 통합 (별도 directive 필요)
- visual polish (Lee directive 금지)
- schema 변경 (Lee directive 금지)

---

## 8. 한 줄 요약

> **peter_scarcity_triple anchor 2에서 V2 4 features 모두 작동, schema integrity 유지, 시나리오 A/C 강함 + B 부분 — Case A-2 (V2 generalize 부분 확인). 데이터 발산은 29.5% ticks 차이 있지만 *visual 차이*는 미미 (single-seed limitation). 진정한 anchor difference를 보려면 cross-seed visualization 필요 — 별도 directive 시 후속.**

---

## 9. ABSOLUTE 원칙 준수

- Rule #1: visual 코드에 person hardcoding 없음 (anchor_id parameter only) ✅
- Rule #6: 기존 Observer + Pipeline + Curation API 무수정 ✅
- Schema v1 무수정 ✅
- 새 lens / metric / bucket 추가 0 ✅
- React / 3D / 캐릭터 / animation 미수행 ✅
- story renderer 재개 0 ✅
- new scenario 생성 0 ✅
- player intervention 0 ✅
- visual polish 0 ✅

---

**Versioning**: v1 (this validation) — 2026-04-30 Anchor 2 visual validation 완료. Case A-2.
