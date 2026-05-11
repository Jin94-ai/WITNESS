# Kernel Gaps -- Future Extension Candidates (NOT Implementation)

**Date:** 2026-04-26
**Iteration:** Iter 182 (Step B4 of new directive, final step)
**Status:** RECORD ONLY -- no implementation in this iter or this cycle
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step B4

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "B4. recovery diversity gap 메모화
> 현재 spatial disengagement 실험이 막힌 이유가 shame_decay gap이라는 점을,
> 즉시 구현이 아니라 future kernel extension candidate로 기록한다.
> 주의: 이 단계에선 구현하지 않는다.
> 산출물: docs/b_direction/KERNEL_GAPS.md"

**Implementation discipline**: this document records gaps. It does NOT
modify engine code. Per directive §6 forbidden list, shame_decay
implementation is explicitly prohibited at this stage.

---

## 1. Why this document exists

The current WITNESS kernel has **one** active recovery channel: Phase 2a
forgiveness rumor (Iter 31 design, Iter 66 confirmed sole load-bearing).
Adding "recovery diversity" — Lee's directive priority 4 — requires either
new kernel mechanisms OR creative repurposing of existing mechanisms.

This document records the **specific kernel gap blocking 5/6 recovery
family candidates**, plus other identified gaps, as future extension
candidates. The point is to ensure that when Lee revisits the question
"why was recovery diversity blocked?", the answer is one click away.

---

## 2. Gap 1: No shame_decay rule

### 2.1 The gap (verbatim from Iter 161)

> "shame has no passive decay rule. Once it reaches saturation (10.0),
> it stays there indefinitely unless an ACTIVE mechanism reduces it
> (currently only Phase 2a forgiveness rumor)."

### 2.2 What this blocks

| Recovery family candidate | Mechanism needed | Currently exists? |
|---|---|---|
| trust-driven stabilization | trust state + decay coupling to shame | NO |
| belonging-driven calming | belonging state + decay coupling | NO |
| authority withdrawal de-escalation | authority_reach decay + shame coupling | partial (auth_reach exists; no decay-shame coupling) |
| spatial disengagement | shame decay when away from event | **NO** (Iter 161 verified) |
| scarcity easing recovery | scarcity state + decay coupling | NO |
| ritual / sacred grounding | already exists for awe-baseline cast (Iter 95, 113) | **YES (conditionally)** |

**5 of 6 candidates blocked.** Only sacred ritual exists, and that is
itself partly decorative (per `SACRED_STATUS_NOTE.md`).

### 2.3 Empirical evidence (Iter 161)
| Variant | Pre-saturation peak | Post-relocation final | Recovery rate |
|---|---|---|---|
| V0 control (no relocate) | 10.0 | 10.0 | 0/5 |
| V1 relocate at t=80 | 10.0 | **10.0** | **0/5** |

Relocation from high-pressure to low-pressure location does NOT reduce
already-accumulated shame. The 10.0 ceiling is sticky.

### 2.4 Implementation cost (if revisited)

Per Iter 161 §4:
- ~10 lines code in `engine/world/micro_world/world.py`
- Configurable via `MicroWorldConfig.shame_decay_enabled` toggle (default OFF)
- New probe ~50 lines
- N=15 + per-agent peak/final audit per Iter 105-119 discipline

### 2.5 Risk (Option K1 vs K2 from Iter 167)

**K1 (implement)**:
- Pro: unlocks 5+ recovery family experiments
- Con: phantom mechanism risk per Iter 105-119 lessons (e.g., aux block
  was decorative when shipped, took Iter 92-108 to find out)
- Con: breaks "0 engine changes in 65+ iters" boundary

**K2 (defer)**:
- Pro: maintains discipline; current Phase 2a recovery model is empirically validated
- Con: recovery diversity remains structural ceiling
- Con: branch criteria for "broader world" (Branch C) include "auxiliary
  recovery exists" which would never be satisfied

### 2.6 My lean (per Iter 167 synthesis)
**K2 (defer)** -- Iter 165 showed kernel is already richly coupled (7/10 meso
pairs strongly cross-correlated). Adding more mechanisms risks over-engineering.
But this is a judgment call; final decision is Lee's.

### 2.7 Why deferred (보류 이유, primary framing)

1. **Phantom mechanism risk** — Iter 92-108 lessons: aux block was decorative when shipped; shame_decay added speculatively could repeat the pattern. Empirical "5/6 blocked" finding does not by itself argue *for* implementation; it argues for *clarity that Lee judges*.
2. **Phase 2a recovery is empirically validated** — 89+ iters of stable behavior under sole-channel recovery. Adding decay perturbs this baseline.
3. **K2 (defer) was selected at Iter 167** — Iter 165 meso coupling 7/10 strong pairs already saturate the kernel coupling space. More mechanisms = over-engineering risk.
4. **Engine-change boundary** — "0 engine changes in 65+ iters" discipline broken on first kernel addition. Cost includes loss of provenance line.

### 2.8 Status
**LOCKED 2026-04-28**: K2 보류 (Lee decision). Not implemented. shame_decay rule는 future kernel extension candidate로 유지하되, 이번 cycle 또는 Branch C 활성화 시점에서 재검토 안 함. Lee 별도 directive 필요.

---

## 3. Gap 2: No trust → shame coupling

### 3.1 The gap
Trust state exists in `AgentState.relationships[*].trust` (per-relation
0-10 scale). It is updated by relationship events but does NOT couple to
shame in any direction.

### 3.2 What this blocks
- Trust-driven stabilization recovery family (Iter 161 candidate 1)
- Belonging recovery (often modeled as average trust)

### 3.3 Implementation cost
- ~5 lines in shame update path (e.g., shame -= 0.1 * dt if avg_trust > 7)
- Or: new SlowStateFieldRecoveryRule field for trust-coupled decay
- (SlowStateFieldRecoveryRule already has `trust_scar` recovery gated
  by avg_trust ≥ threshold, but that's for trust_scar field, not shame)

### 3.4 Why deferred
1. **Coupling direction unclear** — does avg_trust raise (calming) or lower (vigilance loss) the shame floor? Iter 161-167 yielded no empirical signal.
2. **trust_scar already coupled** — `SlowStateFieldRecoveryRule` couples trust to `trust_scar` recovery. Adding a *second* trust coupling for shame risks double-counting.
3. **Sub-gap of Gap 1** — without shame_decay (Gap 1), trust→shame coupling has nothing to push against (shame stays at 10.0).

### 3.5 Status
**RECORD ONLY**. Not implemented. Sub-gap of Gap 1.

---

## 4. Gap 3: No belonging state field

### 4.1 The gap
"Belonging" is a candidate state field per Iter 161 directive priority 4
("belonging-driven calming"). But no `belonging` field exists in
`AgentState` or `SlowState`.

### 4.2 What this blocks
- Belonging-driven recovery
- Authority-withdrawal arc (would need authority + belonging interaction)

### 4.3 Implementation cost
- Add `belonging: float` to SlowState (Pydantic schema change)
- Add update rule (when does belonging rise/fall?)
- Add coupling to shame (or other emotion) for the recovery effect
- ~30 LOC total + tests + content updates

### 4.4 Why deferred
1. **Directive §6 explicit forbid** — "새 변수 대량 추가는 여전히 금지". Single-field add still violates spirit.
2. **No empirical demand** — current scenarios produce coherent recovery without belonging. Adding it is *ahead of evidence* (worst class per Iter 105-119 retraction lessons).
3. **High decorative risk** — without a strong update rule + coupling, belonging becomes another aux/decorative slot.
4. **Highest cost / highest risk** — ~30 LOC + content + tests + new schema migration. Worst risk-cost ratio of all 6 gaps.

### 4.5 Status
**RECORD ONLY**. Strongest deferral case among the 6.

---

## 5. Gap 4: Phase 2a is sole load-bearing recovery

### 5.1 The gap (Iter 66 finding)
Phase 2a forgiveness rumor is the **only** mechanism that produces recovery
across 3/3 tested scenarios (accusation, scarcity, sacred). Ablating it
produces identical saturation collapse in all three. This is a robustness
question, not a gap per se — but it is a single point of failure.

### 5.2 What this means
- If Phase 2a has a bug or parameter drift, ALL recovery dynamics break
- No redundancy or alternative pathway
- Branch C ("broader world") prerequisites include "auxiliary recovery
  channel(s) exist" — currently fails

### 5.3 Implementation cost (if alternative recovery added)
Depends on which alternative. Cheapest (per Iter 161): shame_decay rule
(Gap 1).

### 5.4 Why deferred
1. **Not a bug, an architectural choice** — Iter 31 design explicitly chose single-channel forgiveness. "Sole-channel" framing as a *gap* is interpretation, not fact (H4 alternate: "robustness by design").
2. **No alternative validated** — adding alternatives means implementing Gap 1/2/3, all of which have their own deferral reasons.
3. **Branch C gate** — only matters if/when Branch C ("broader world") is activated. Currently Branch C is `FORBIDDEN_NOW` per continuous-execution directive §6.

### 5.5 Status
**RECORD ONLY**. Architectural observation, conditional on Branch C gate.

---

## 6. Gap 5: Population grammar placement template

### 6.1 The gap (Iter 160 finding, per Iter 167 §4 priority order)
"Population grammar placement" was identified as a directive priority 5 gap
in earlier work. Currently agent placement is ad-hoc per scenario builder
(e.g., `build_accusation_cast` hardcodes initial_placements).

A "placement template" would let scenarios declare population structure
(cast composition + location distribution + relation graph) without
duplicating builder logic.

### 6.2 What this blocks
- Cross-scenario population variation experiments
- Branch C's "cast composition variation" criterion
- Fast iteration on scenario design

### 6.3 Implementation cost
- New schema for placement templates (~50 LOC)
- Refactor 3 builders to use templates (~100 LOC)
- Migration risk: existing scenarios might shift slightly under refactor

### 6.4 Why deferred
1. **Engine refactor risk** — touching 3 builders during readability cycle risks regressing existing scenarios. Builder hardcoding is *legible*; template is *abstract*.
2. **Migration drift** — Iter 161 baseline uses current builders. Refactor + re-run = retest entire chain.
3. **Branch C only** — value emerges with cross-scenario population variation experiments, which are Branch C scope.

### 6.5 Status
**RECORD ONLY**. Engine refactor; not in current directive scope.

---

## 7. Gap 6: Authority autonomy

### 7.1 The gap (Iter 164 finding)
World autonomy probe (Iter 164) found 4/4 signals show world processes
operate autonomously without seed events EXCEPT authority. Authority
actions are event-triggered, not autonomously generated.

### 7.2 What this blocks
- Branch C "world-side process partly readable externally" criterion
  is partly satisfied (3/4) but authority gap reduces evidence
- Fully-autonomous world simulation

### 7.3 Implementation cost
- New rule: authority generates actions based on
  blame_concentration / public_suspicion / shame_climate thresholds
- ~20 LOC + tests + parameter tuning

### 7.4 Why deferred
1. **Directive §6 ambiguity** — "autonomous-generation of actions" arguably counts as 새 메커니즘 drilling. Defer to Lee on classification.
2. **Iter 164 finding may be by design** — authority responding to events (not autonomously generating) is internally consistent. H4 alternate: "this is feature, not gap."
3. **3/4 already satisfied** — world autonomy probe shows 3/4 signals autonomous. Gap is partial, not load-bearing for current claims.

### 7.5 Status
**RECORD ONLY**. Engine addition; classification ambiguous. Defer to Lee.

---

## 8. Summary table of gaps

| Gap | Blocks | Cost (LOC) | Risk | Lee gate |
|---|---|---:|---|---|
| 1. No shame_decay rule | 5/6 recovery families | ~10 + tests | phantom mechanism | YES (K1/K2) |
| 2. No trust→shame coupling | trust-driven recovery | ~5 | low | YES |
| 3. No belonging field | belonging recovery | ~30 + content | new variable, decorative risk | YES |
| 4. Sole-channel recovery | Branch C robustness | depends | architectural | YES |
| 5. Placement template | cross-scenario variation | ~150 (refactor) | migration | YES |
| 6. Authority autonomy | full world autonomy | ~20 | autonomous-gen ambiguity | YES |

**All 6 gaps require Lee gate.** None are implemented in this iter or this
directive cycle.

---

## 8.5 보류 사유 한 줄 요약 (deferral-reason centric, 2026-04-28 refine)

| Gap | Primary deferral reason | Secondary |
|---|---|---|
| 1. shame_decay | Phantom mechanism risk (Iter 92-108 lessons) | K2 chosen at Iter 167; engine-change boundary |
| 2. trust→shame | Coupling direction unclear; sub-gap of Gap 1 | trust_scar already coupled (avoid double-count) |
| 3. belonging | Directive §6 explicit forbid + ahead of evidence | Highest decorative risk + worst risk-cost ratio |
| 4. sole-channel | Architectural choice by design (Iter 31), not bug | H4 alternate: "robustness, not gap" |
| 5. placement template | Engine refactor during readability cycle = regression risk | Branch C only |
| 6. authority autonomy | Directive §6 ambiguity (drilling vs not?) | H4 alternate: "feature, not gap" |

**Common thread**: 5 of 6 deferrals trace back to Iter 105-119 retraction lessons (phantom mechanism / decorative addition) + directive §6 forbidden list. The 6th (Gap 5) is migration-risk during active cycle.

---

## 9. Decision rules for future revisit

When Lee revisits these gaps (post-Step C eval or new directive):

### 9.1 Implement shame_decay (K1) IF
- Step C readability blind shows readable ≤ 3/12 (Branch B strong)
- AND Q6a [STRUCTURE] confusion notes mention "no recovery without forgiveness"
- AND aux mechanism (Iter 92-108 retracted) lessons are actively considered
  to avoid phantom mechanism repeat

### 9.2 Implement trust→shame coupling IF
- Branch C ready (readable + world legible) AND Lee wants population-grammar
  experiments
- AND avg_trust threshold + decay rate are validated empirically before
  shipping

### 9.3 Implement belonging field IF
- Branch C confirmed AND scenario design needs belonging-driven arcs
- This is the riskiest addition (new field, no current evidence of need)

### 9.4 Refactor placement template IF
- Branch C confirmed AND cross-scenario variation experiments are queued

### 9.5 Add authority autonomy IF
- Branch C "broader world" confirmed AND Iter 164 finding is not satisfactory
- Risk: autonomous-generation may itself be classified as "새 메커니즘"

### 9.6 Default: do nothing
**If Step C is unclear or new directive is minor, defer all 6 gaps.** The
kernel as it stands has been validated through 89+ iters. Adding mechanisms
is high-risk per Iter 105-119 lessons.

---

## 10. What could still be wrong (H4)

### 10.1 Gap 1 (shame_decay) might be misdiagnosed
Iter 161 tested ONE relocation timing (t=80). Earlier relocation (e.g., t=15
before saturation) might allow shame to drift naturally even without a
decay rule, via interaction with crowd state changes (reduced ambient
pressure as agents leave).

The "no decay rule" claim is based on grep + observation, not exhaustive
code search. A subtle decay path might exist somewhere (e.g., pressure
update setting shame to weighted average of current shame + new pressure,
where new pressure = 0 effectively decays).

### 10.2 Gap 4 (sole-channel) is robust by design, not a bug
Iter 66 confirmed Phase 2a is sole load-bearing across 3 scenarios. This
is **architectural choice** per Iter 31 design, not an oversight. Treating
it as a "gap" assumes diversity is desirable. Lee's directive priority 4
endorses this assumption, but it's not self-evident.

### 10.3 Gap 6 (authority autonomy) might be intentional
Iter 164 found authority is event-triggered. This may be by design —
authorities respond to events, not act autonomously. Re-classifying as a
"gap" assumes autonomous behavior is desired.

### 10.4 Implementation cost estimates are rough
"~10 LOC" or "~30 LOC" are eyeball estimates. Real implementation often
balloons due to test coverage, content migration, edge cases. Treat costs
as lower bounds.

### 10.5 Order of gaps may matter
Implementing Gap 1 (shame_decay) might invalidate the Iter 113 -26.7%
sacred ablation finding (if shame can passively decay, late miracle's
effect changes). Cross-impact analysis not done.

---

## 11. What I did NOT try (H2)

- **Implement any gap**: explicit directive prohibition (§6, B4 caution)
- **Cross-impact analysis** between gaps (e.g., does Gap 1 invalidate Gap 6?)
- **Empirical validation** of "no decay rule" claim (would need targeted
  grep + injection test)
- **Cost estimate refinement**: actual LOC counts via prototype branches
- **Prioritization scoring**: which gap has highest leverage if Lee picks
  one

이유:
- Step B4 scope: "기록"이지 implementation이 아님
- 디렉티브 §6 forbidden: shame_decay 즉시 구현 금지
- B4 caution verbatim: "이 단계에선 구현하지 않는다"

---

## 12. Alternate interpretations (H4)

- **"Gap" = bug to fix**: 그러면 즉시 구현 정당화 가능. 디렉티브와 대치.
- **"Gap" = architectural observation**: 그러면 기록만 충분. 내 해석.
- **"Future candidate" = next iter implementation**: 그러면 K1 자동 채택.
  내 해석은 "future ≠ next"; Lee 결정 후 implementation.
- **"Recovery diversity" = 6 candidates 모두 구현**: 그러면 5+ 새 mechanism
  추가. §6 명시적 금지. 거부.

---

## 13. References

- `docs/b_direction/ITER_161_RECOVERY_FAMILY_GAP.md` — primary evidence
  (spatial disengagement -- shame_decay gap finding)
- `docs/b_direction/ITER_167_DIRECTIVE_CYCLE_SYNTHESIS.md` §3.4 — K1 vs K2
  decision framing
- `docs/b_direction/SACRED_STATUS_NOTE.md` §7 — sacred ritual recovery
  family status
- `docs/b_direction/STATE_FIELD_STATUS.md` — current state field inventory
  (no belonging field; trust as relation field)
- `docs/b_direction/COMPONENT_LEDGER.md` §11 — RESERVE state fields
- `engine/world/micro_world/world.py` — Phase 2a implementation (current
  sole recovery channel)
- `engine/rules/slow_recovery.py` — UNWIRED rule for slow_state recovery

---

## 14. Decision: this is a record, not a plan

**This document is the directive's intended output.** It records 6 gaps
as future kernel extension candidates without implementing any of them.
When Lee or future-self asks "why was recovery diversity blocked at
Iter 181?", the answer is in §2-§7. When Lee asks "should we implement
shame_decay now?", the answer is in §9 (decision rules).

The cycle (Iter 176-182, 7 steps of new directive) closes here.
