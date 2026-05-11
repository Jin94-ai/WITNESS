# WITNESS Readability Infrastructure — 1-Page Summary

**Date:** 2026-04-27
**Source:** Iter 185-191 readability loop synthesis
**Status:** CURRENT (canonical entry point for readability work)

---

## 0. 한 줄 요약

**"7 iter 동안 readability infra가 4 docs + 1 script에 누적됨. Lee 진정한 blind eval만 들어오면 7개 metric 매트릭스가 자동으로 branch 판정으로 매핑된다."**

---

## 1. 진입점 (어떤 파일을 봐야 하는가)

### 1.1 평가하려면
| 작업 | 파일 |
|---|---|
| Pilot eval (15-20분) | `READABILITY_BLIND_PROTOCOL_V2.md` 읽고 `readability_pilot/` 4개 probe 답하기 |
| 답안 작성 | `READABILITY_BLIND_RESULTS_V2.md` §1 |
| 답안 후 자동 비교 | `READABILITY_BLIND_RESULTS_V2.md` §4.1 ground truth |
| Pilot로 부족 | full 12-probe — `readability_probes/` |

### 1.2 분석하려면
| 작업 | 파일 |
|---|---|
| 7 metric 정의 | `READABILITY_BLIND_PROTOCOL_V2.md` §4 (v2.0-v2.3) |
| Action queue matrix | `READABILITY_BLIND_PROTOCOL_V2.md` §4 v2.4 |
| Branch 판정 규칙 | `READABILITY_BLIND_PROTOCOL_V2.md` §5 |
| Claude simulation 비교 | `READABILITY_BLIND_RESULTS_V2_CLAUDE_SIM.md` |

### 1.3 포맷 자체를 알려면
| 작업 | 파일 |
|---|---|
| Annotated 5-section spec | `ANNOTATED_PROBE_FORMAT.md` v1.2 |
| Generator 코드 | `scripts/b_direction/generate_annotated_probes_all.py` |
| Probe stats baseline | `PROBE_STATS_CHARACTERIZATION.md` |

---

## 2. 7 iter 누적 변경 (timeline)

| Iter | 변경 | 영향 파일 |
|---|---|---|
| 185 | Annotated event log cap disclosure (`showing first 30 of N`) | `generate_annotated_probes_all.py` + `ANNOTATED_PROBE_FORMAT.md` v1.1 |
| 186 | Q6a sub-tags (5 main + ~18 sub) | `READABILITY_BLIND_PROTOCOL_V2.md` v2.1 + `RESULTS_V2.md` |
| 187 | Annotated headline `Final summary` 5-label rollup | `generate_annotated_probes_all.py` + `ANNOTATED_PROBE_FORMAT.md` v1.2 |
| 188 | RESULTS pilot template `final summary self-call` 칸 | `RESULTS_V2.md` §1.1.5, §4.1 |
| 189 | Format-axis metrics: Q4a-rollup gap, Q2a-typing gap | `PROTOCOL_V2.md` §4 v2.2 |
| 190 | Format-axis metric: Q3b world-side gap (3 axes) | `PROTOCOL_V2.md` §4 v2.3 |
| 191 | Action queue matrix (7 metrics × patterns → 5 named branch patterns) | `PROTOCOL_V2.md` §4 v2.4 |
| 193 | **Sanity check fix**: v2.4 patterns NOT mutually exclusive (sim matched both P-Mixed and P-A+C). v2.5: precedence-ordered algorithm + P-A relaxed (OR over Format/CAN_EXPLAIN/Q4a-rollup gaps). | `PROTOCOL_V2.md` §4 v2.5 |

**모두 KEEP 결정**. Mechanism drilling 0건. Engine 변경 0건.

**Iter 193이 단순 KEEP가 아니라 자체 sanity check가 실제 bug 발견**한 점 주목.

---

## 3. 7 metrics (한 줄씩)

| Metric | 측정 | Branch signal |
|---|---|---|
| Readable rate | Q1=CLEAR_FLOW + Q1b∈{CAN_EXPLAIN, PARTIAL} + Q4a≠NO_ARC + Q2c∈{CLEAR, MIXED} | A 또는 C readiness |
| Format gap (Readable) | annotated rate - original rate | A coarse |
| CAN_EXPLAIN gap | Q1b 차이 | A explainability sub |
| Q5b HELPS gap | oscillation 도움 차이 | A presentation |
| **Q4a-rollup gap** | final summary self-call 정확도 차이 | A-arc |
| **Q2a-typing gap** | primary pressure 정확도 차이 | scenario-typing 효과 |
| **Q3b world-side gap** | crowd_mood/authority/public_attention 선택 빈도 차이 | C signal direct |

---

## 4. 5 named patterns (v2.5 precedence-ordered algorithm)

Lee 진정한 blind 결과 도착 시 매핑 — **순서대로 try, FIRST match**:

| Order | Pattern | 핵심 조건 | Branch action |
|---:|---|---|---|
| 1 | **P-B** | Format gap ±25% AND Q4a-rollup gap ≈0 AND Q3b world-side ≈0 | Branch B priority |
| 2 | **P-A+C** | Q1 readable both high (≥75%) AND Q4a-rollup gap >0 AND Q2a-typing gap ≈0 | A-arc + C readiness — full eval |
| 3 | **P-A** (v2.5 relaxed) | ANY of {Format gap ≥+50%, CAN_EXPLAIN gap ≥+50%, Q4a-rollup gap >+50%} AND not P-A+C | Branch A confirmed |
| 4 | **P-C-ready** | Both Readable high AND CAN_EXPLAIN majority both AND Q3b world-side ≥2 axes positive | Branch C readiness (full eval로 confirm) |
| 5 | **P-Mixed** (residual) | Q4a-rollup gap >0 AND Format gap ≈0 (not P-A+C) | A-arc only; full N=12로 disambiguate |

**Iter 189 Claude sim 결과**: 알고리즘 적용 → **P-A+C** (v2.5 §sanity-check trace 검증 완료).

---

## 4. Lee가 다음에 할 수 있는 것

### 4.1 ~~진정한 blind eval~~ + ~~Full N=12 eval~~ ✓ 둘 다 2026-04-28 완료

- ✓ Pilot blind: GPT-5.5 → P-A+C verdict (`READABILITY_BLIND_RESULTS_V2_FILLED.md`)
- ✓ annotated v2/v2.1/v3 implementation (autonomous LOOP 28-34)
- ✓ Full N=12 TRUE COMBINED: GPT-5.5 → **P-C-ready** verdict (`docs/RESULTS_V2_FILLED_FULL_N12_TRUE_COMBINED.md`)
- ✓ Postcheck: v3 fields verified present + P5/P6/P10 rule clarification (`FULL_EVAL_N12_POSTCHECK.md`)
- ✓ **Branch C PREP allowed, EXECUTION gated** → `BRANCH_DECISION_2026-04-28.md` updated

### 4.2 추가 후보 (자체 판단으로 진행 가능)
- ~~annotated v2 fields 설계 시작~~ → **2026-04-28 LOOP 27-30 v2 (primary pressure + failure mode), LOOP 32 v2.1 (scarcity 100%), LOOP 34 v3 (world-side dynamics) 모두 실행 완료**
- ~~SCRIPT_STATUS Phase B/C~~ → 완료 (Phase A 55 + B 19 + C 14 = 88 archived, 37 remaining)
- relation shift / motif shift fields — 여전히 ahead of evidence (full N=12 결과 후 검토 — v4 candidate)

---

## 5. 동작하지 않는 가설 (negative findings)

H4 discipline 적용:

- **Q-set V3 revision**: Iter 186 sub-tags 추가했지만 V3 trigger (Q_SET tags converge) 조건 미충족. 사실상 V2 Q-set는 sim에서 0 [Q_SET] 태그 발생 — adequate.
- **annotated가 모든 차원에서 도와주지 않음**: Iter 189 sim에서 Q2a-typing gap 0% 발견. annotation은 arc rollup tool이지 scenario detector 아님. 이건 Iter 187 final summary 설계 의도와 일치.
- **5 final summary labels 중 PARTIAL/LOW_ACTIVITY 미사용** (sim): pilot N=4 작아 미관측일 수도 있음. Lee 진정 평가 후 prune 검토.
- **Cap disclosure (Iter 185)는 outlier에서만 효과**: P3, P6, P12 (200+ confessions)에서만 의미 있음. P1/P2 (모두 30 미만)에서는 disclosure 안 보임 (의도된 동작).

---

## 6. 동기화 검증 (cross-doc consistency)

| Claim | Source 1 | Source 2 | OK? |
|---|---|---|---|
| 7 metrics | PROTOCOL_V2 §4 v2.0-v2.3 | this doc §3 | ✓ |
| 5 named patterns + algorithm | PROTOCOL_V2 §4 v2.5 (precedence-ordered) | this doc §4 | ✓ |
| Annotated final summary 5 labels | ANNOTATED_FORMAT v1.2 §1.2.0 | RESULTS_V2 §1.1.5 + §4.1 ground truth | ✓ |
| Q6a 5 main + 18 sub | PROTOCOL_V2 §2.1.1 v2.1 | RESULTS_V2 §1.2 tag legend | ✓ |
| Cap disclosure | generate_annotated_probes_all.py L156-163 | ANNOTATED_FORMAT §1.5 v1.1 | ✓ |
| Iter 187 ground truth (12 probes) | RESULTS_V2 §4.1 | actual generation output (Iter 187) | ✓ (12/12 verified) |

---

## 7. 보류 (Lee gate) — Blocking checklist

다음 항목들이 결정/실행되어야 readability work가 다음 단계로 이동:

| 항목 | 누가 | 무엇을 막고 있나 |
|---|---|---|
| ~~Lee 진정한 blind eval (15-20분)~~ | ✓ 2026-04-28 완료 | External LLM (ChatGPT/GPT-5.5 Thinking) → P-A+C verdict (FILLED.md) |
| **Full N=12 eval execution** | Lee or GPT-5.5 (~70-105분) | Branch C activation gate. v3 후 4/4 metrics likely trigger (FULL_EVAL_N12_PREP §3.2) |
| **Branch 결정 lock** | Lee (full eval 후) | Branch A+C provisional → 4/4 trigger 확인 시 Branch C 실질 활성화 |
| **KERNEL_GAPS K1 vs K2 (shame_decay)** | Lee | K2 default. independent of readability cycle |
| ~~annotated v2 fields~~ | ✓ 2026-04-28 LOOP 28-34 완료 | v2/v2.1/v3 implementation done |
| ~~SCRIPT_STATUS Phase B/C archive~~ | ✓ 2026-04-28 완료 | Phase A 55 + B 19 + C 14 = 88 archived |
| weak-ref 5 scripts (SCRIPT_STATUS §6.3.2) | Lee | A안 KEEP_FOR_NOW default; 옵션 A/B/C frame-neutral |
| world/, pipeline_v2 영역 처리 | Lee | "별도 승인 필요" 명시 |
| relation/motif shift v4 fields | Lee + full eval 결과 | ahead of evidence (full N=12 후) |

---

## 8. Cycle retrospective (Iter 185-194 메타-회고)

### 8.1 시작점 (Iter 184 끝)
- annotated probe v1 (5-section) + pilot 4 + Protocol V2 (Q-set v2 + 모드 + 5-tag taxonomy)
- 외부 평가 없음, Lee gate 4개

### 8.2 10-iter 동안 추가된 layer
- **Layer 1 (인프라)** — Iter 185 cap disclosure / Iter 187 final summary
- **Layer 2 (taxonomy)** — Iter 186 Q6a sub-tags / Iter 188 self-call template
- **Layer 3 (metrics)** — Iter 189 Q4a-rollup + Q2a-typing / Iter 190 Q3b world-side
- **Layer 4 (synthesis)** — Iter 191 action queue matrix
- **Layer 5 (검증/메타)** — Iter 192 SUMMARY / Iter 193 sanity check + v2.5 / Iter 194 sync

### 8.3 패턴 1 — 단일 사이클이 5 layer로 나뉨
각 layer 2 iter씩. 매 iter "가장 작은 작업"이 누적되어 layered architecture 형성. 이는 의도되지 않은 패턴이지만 결과적으로 깨끗한 구조.

### 8.4 패턴 2 — 자체 sanity check가 bug 발견 (Iter 193)
v2.4 matrix가 mutually exclusive 아님. 만약 Iter 193 trace가 없었다면 Lee 결과 도착 시 중복 매핑 → 결정 혼란. **자체 검증 layer가 ahead-of-evidence work를 정정한 사례**.

### 8.5 패턴 3 — Lee gate가 multiplicative effect
- Lee 진정한 blind 1번 실행 → 7 metrics × 5 patterns = 35-cell matrix가 1개 named pattern으로 매핑
- 즉 1번의 외부 input이 10 iter 누적 분석을 활성화
- **"infra 만들기 ≠ infra 사용하기"** — 만들기는 끝, 사용은 Lee gate

### 8.6 다음 cycle trigger 조건

| Trigger | 다음 readability cycle 내용 |
|---|---|
| Lee blind = P-A confirm | annotated v2 fields (relation/motif shift) 추가, full N=12 prep |
| Lee blind = P-B | readability work 축소, kernel work 복귀 (KERNEL_GAPS 재검토) |
| Lee blind = P-C-ready | full N=12 confirm, broader world prep |
| Lee blind = P-A+C | full N=12 disambiguate |
| Lee blind = P-Mixed | full N=12 to resolve |
| 새 디렉티브 | scope 재정의 |

### 8.7 What this cycle did NOT achieve (H4)
- 진정한 readability 향상 측정 (Lee gate)
- annotated probe 효과의 인간 검증
- Q-set V3 trigger 발동 (sub-tags 0건 [Q_SET])
- relation shift / motif shift 필드 (ahead of evidence)

### 8.8 한 줄 결론
**"10 iter cycle은 readability infra를 'mechanical decision tool' 수준까지 끌어올림. Lee가 진정한 blind 1번 실행하면 35-cell matrix가 1개 pattern으로 collapse → 즉답 가능. 그 활성화가 일어나기 전까지는 추가 readability work는 ahead of evidence."**

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| v1 | 2026-04-27 | Iter 185-191 synthesis. PROTOCOL v2.4, ANNOTATED v1.2 시점 freeze. |
| v1.1 | 2026-04-27 | + Iter 193 (PROTOCOL v2.5 sanity check fix). §2 timeline +1 row, §4 algorithm-ordered, §6 consistency check 갱신. |
| v1.2 | 2026-04-27 | + §7 Blocking checklist (was 보류 lines), + §8 Cycle retrospective (Iter 185-194 메타-회고). §3-§6 unchanged. |
| **v1.3 (this)** | **2026-04-28** | **§4.2 + §7 update: SCRIPT_STATUS Phase B autonomous-mode 실행 완료 (19 scripts archived). §3-§6 unchanged.** |
