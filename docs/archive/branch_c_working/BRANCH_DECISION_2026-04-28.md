# Branch Decision — 2026-04-28 (post-pilot blind eval)

**Date:** 2026-04-28
**Trigger:** External LLM (ChatGPT/GPT-5.5 Thinking) pilot blind evaluation completed
**Eval source:** `READABILITY_BLIND_RESULTS_V2_FILLED.md`
**Algorithm:** PROTOCOL_V2 §4 v2.5 precedence-ordered matching
**Initial Verdict (post-pilot):** P-A+C → Branch A+C, run full N=12
**Updated Verdict (post-Full N=12 TRUE COMBINED, 2026-04-28):** **P-C-ready, with Branch A presentation sub-signal retained — Branch C PREP allowed, EXECUTION gated**

See `FULL_EVAL_N12_POSTCHECK.md` for verification + P5/P6/P10 rule clarification.

---

## 1. Why this doc

Per `WITNESS_CLAUDE_CODE_CONTINUOUS_EXECUTION_DIRECTIVE.md`: pilot blind eval was the single decisive HUMAN_GATE for Branch lock. The eval has now arrived. This doc traces the algorithm + locks the provisional A+B branch into a **Branch A+C with full eval gate**.

---

## 2. Pilot eval results (verbatim from FILLED §1.4)

### 2.1 7 format-axis metrics

| Metric | Value | Interpretation |
|---|---:|---|
| Readable rate (original) | **2/2 = 100%** | Both PILOT_1, PILOT_2 readable raw |
| Readable rate (annotated) | **2/2 = 100%** | Both PILOT_3, PILOT_4 readable annotated |
| **Format gap** | **0 pp** | structure self-readable both formats |
| **CAN_EXPLAIN gap** | **+100 pp** | original 0/2, annotated 2/2 |
| Q5b HELPS rate gap | 0 pp | oscillation reading neutral both |
| **Q4a-rollup gap** | **+50 pp** | annotation match 2/2 vs original self-call 1/2 |
| **Q2a-typing gap** | **0 pp** | scenario type accuracy 1/2 both formats |
| **Q3b world-side gap** | **0 pp** | crowd_mood only on both |

### 2.2 Critical findings (FILLED §1.5, §4.1)

- **Q2a primary pressure accuracy: 2/4** — pressure source under-specified
- **Final summary self-call: 3/4** — annotated 2/2 match, original 1/2 (PILOT_1 MIXED misread)
- **Failure mode**: "event trigger labels over-attract evaluator toward `accusation`, even when hidden scenario type is scarcity/sacred"

---

## 3. 5-pattern precedence-ordered match (PROTOCOL_V2 §4 v2.5)

순서대로 try, FIRST match가 결정.

### 3.1 P-B test (Order 1)
**Conditions**: Format gap ±25% AND Q4a-rollup gap ≈0 AND Q3b world-side ≈0

| Condition | Met? |
|---|---|
| Format gap ±25% (0 pp) | ✓ within range |
| Q4a-rollup gap ≈ 0 | ✗ **+50 pp not near zero** |
| Q3b world-side ≈ 0 | ✓ |

→ **NOT P-B**. Q4a-rollup gap이 0이 아님.

### 3.2 P-A+C test (Order 2)
**Conditions**: Q1 readable both high (≥75%) AND Q4a-rollup gap >0 AND Q2a-typing gap ≈0

| Condition | Met? |
|---|---|
| Q1 readable both ≥75% | ✓ both 100% |
| Q4a-rollup gap > 0 | ✓ +50 pp |
| Q2a-typing gap ≈ 0 | ✓ 0 pp |

→ **MATCH: P-A+C** ✓

### 3.3 Stop. Precedence-ordered → first match wins.

P-A, P-C-ready, P-Mixed 검사 불필요 (P-A+C가 이미 매칭).

**Cross-check (FILLED §1.5)**: GPT-5.5 자체 verdict = "A+C / inconclusive — run full". 알고리즘 매핑과 일치 ✓.

---

## 4. Branch decision

**Locked: Branch A+C with full eval gate.**

### 4.1 What this means

- **Branch A confirmed (partial)**: annotated format이 Q4a arc rollup에 명확 도움 (+50 pp Q4a-rollup gap, +100 pp CAN_EXPLAIN gap).
- **Branch C readiness (partial)**: 두 format 모두 readable이지만 world-side detection은 `crowd_mood`만 보임. authority/public_attention 부재.
- **결정 신호 부족 영역**: Q2a-typing (scenario detection)이 0 — annotation이 *arc rollup tool이지 scenario detector 아님*. v2 fields 필요.

### 4.2 Provisional A+B → A+C 변경

| Element | Before (provisional A+B) | After (Branch A+C) |
|---|---|---|
| Branch A | annotated representation 강화 후보 | confirmed (arc rollup 효과 입증) |
| Branch B | kernel debt cleanup 병행 | de-prioritized (Format gap 0, structure readable) |
| Branch C | broader world readiness 후보 | partial signal — full N=12 confirm 필요 |

**Note**: Branch B로의 직접 회귀 (kernel 단순화)는 *not warranted*. structure 자체는 양쪽 모두 readable. Branch B 우선 신호 없음.

---

## 5. Required next steps (Branch A+C action queue)

### 5.1 Branch A: annotated v2 design (high priority)

GPT-5.5 발견의 actionable: **"event trigger labels over-attract toward accusation"**. 해결책 = annotated header에 **explicit pressure-source field** 추가.

**제안 v2 field** (per PILOT_2 + PILOT_3 confusion notes):

```
[Annotated headline summary]
  Final summary: <RECOVERY_DOMINATED / SATURATION_DOMINATED / ...>
  Primary pressure: <shame / fear / sacred / scarcity / accusation / grief>  ← NEW v2
  Failure mode: <none / shame_cap / repeat_retrigger / no_forgiveness_uptake / crowd_blame_persists>  ← NEW v2 (only on saturation)
  ...
```

이 두 field가 추가되면:
- Q2a-typing gap > 0 가능 (scenario detector 역할)
- Q4 saturation 원인 visibility (PILOT_4의 "200 confessions + saturation 모순감" 해결)

**Cost**: `scripts/b_direction/generate_annotated_probes_all.py` 확장. ~30 LOC, no engine change.

**Risk**: Low. annotated format 변경, source data 변경 없음.

### 5.2 Branch C readiness: full N=12 eval

12 probes 모두 답하면:
- Q3b world-side per-axis 통계 (현재 N=4 → N=12로 statistical power 증가)
- authority/public_attention surface 여부 확정
- Q2a-typing gap이 v2 field 추가 후 어떻게 변하는지 비교

**Two paths**:
- Path α: 현재 v1.2 annotated로 N=12 first → v2 field 추가 후 비교
- Path β: v2 field 먼저 추가 후 N=12 → before/after 비교 가능

**권장**: Path β. Lee/GPT-5.5의 핵심 발견 (Q2a-typing 0 pp)를 직접 측정 가능.

### 5.3 Cycle 종료 조건

Full N=12 eval에서:
- Q1 readable ≥10/12 + Q2a-typing gap >+30 pp + Q3b world-side ≥2 axes positive → **Branch C 실질 활성화 가능**
- 위 조건 미충족 → annotated v3 또는 cycle 추가 반복

---

## 6. What this does NOT change (FORBIDDEN_NOW 유지)

Per `WITNESS_CLAUDE_CODE_CONTINUOUS_EXECUTION_DIRECTIVE.md` §6:

- ⛔ Phase 2a 추가 drilling
- ⛔ shame_decay rule 구현 (K1 vs K2 → K2 default 유지)
- ⛔ trust→shame coupling
- ⛔ belonging field
- ⛔ neural policy
- ⛔ 새 scenario 확장
- ⛔ **Branch C 실질 진입** (full N=12 eval은 evidence collection이고 진입 아님)

**Branch A+C 결정 = "Branch C readiness 신호 발견" + "full eval로 confirm 필요"**. 실질 진입은 confirm 후.

---

## 7. Open items for Lee — **ALL LOCKED 2026-04-28**

| # | 항목 | **Lee 결정** |
|---|---|---|
| 1 | Path α vs Path β | **Path β executed (LOOP 28-34)** |
| 2 | Full N=12 evaluator | **GPT-5.5 단독** (FULL_EVAL_N12_GPT5_PACKAGE.md ready) |
| 3 | annotated v2 spec | **Implemented v2/v2.1/v3** |
| 4 | KERNEL_GAPS K1 vs K2 | **K2 보류** (LOCKED) |
| 5 | weak-ref 5 scripts | **KEEP** (LOCKED, SCRIPT_STATUS §6.3.2 옵션 A) |
| 6 | UNSURE 3 scripts | **KEEP** (LOCKED) |
| 7 | probe_runs/*.json archive | **보류** (LOCKED) |
| 8 | world/, pipeline_v2 영역 | **FREEZE — 별도 directive 필요** (LOCKED) |

---

## 8. Algorithm trace (verifiable)

```
Input: pilot results from FILLED §1.4
  Q1 readable: 100% / 100%
  Format gap: 0 pp
  CAN_EXPLAIN gap: +100 pp
  Q4a-rollup gap: +50 pp
  Q2a-typing gap: 0 pp
  Q3b world-side gap: 0 pp

Step 1: try P-B
  format ±25%? YES (0 pp)
  Q4a-rollup ≈0? NO (+50 pp)
  → P-B FAIL

Step 2: try P-A+C
  Q1 readable both ≥75%? YES (100%)
  Q4a-rollup > 0? YES (+50 pp)
  Q2a-typing ≈ 0? YES (0 pp)
  → P-A+C MATCH

Stop. First match wins.

Verdict: P-A+C
Action: Branch A+C, full N=12 eval gate
```

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Initial decision doc post-pilot blind. P-A+C verdict locked. |
