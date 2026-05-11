# Full N=12 Eval Prep — Path β post-v2.1

**Date:** 2026-04-28
**Trigger:** BRANCH_DECISION_2026-04-28.md §5.2 — Path β recommended (v2 first, then N=12)
**v2.1 status:** 12/12 detection accuracy (LOOP 32 complete)
**Purpose:** Set up full N=12 eval to confirm Branch A+C → Branch C activation

---

## 1. Why full N=12 now

Pilot (N=4) gave **P-A+C** verdict but with caveats:
- Q4a-rollup gap +50 pp ✓ (annotation helps arc)
- Q2a-typing gap 0 pp ✗ (annotation doesn't help scenario type)
- Q3b world-side gap 0 pp ✗ (only crowd_mood visible)

v2.1 fixes scenario type detection at the **probe level** (12/12 = 100%). Now the question is:
1. Does v2.1 annotated header *actually help evaluator* answer Q2a correctly?
2. Does v2.1 affect Q4a-rollup gap (already strong)?
3. Does Q3b world-side gap need v3 work (authority/public_attention surfacing)?

**Full N=12 eval is the validation gate for Branch C activation** (BRANCH_DECISION §8.4).

---

## 2. Eval mode + materials

### 2.1 Recommended mode: Hybrid (6 original + 6 annotated, format-balanced)

**Reason**: directly compare format efficacy at full N. With 6/6 split:
- Statistical power for Q2a-typing gap (0 pp pilot → ?)
- Statistical power for Q3b world-side gap
- format gap visible per-probe

**Alternative**: All-12-annotated (lower threshold, but no format comparison).

### 2.2 Probe assignment for hybrid mode

Format-balanced (3 accusation, 2 sacred, 1 scarcity in each half; or scenario-balanced):

| Half | Probes | Format |
|---|---|---|
| Original | P2, P5, P8, P10, P11, P12 | original (P{n}.txt) |
| Annotated | P1, P3, P4, P6, P7, P9 | annotated v2.1 (P{n}_ANNOTATED.txt) |

**Scenario coverage in originals**: P2 scarcity, P5 sacred, P8 accusation, P10 accusation, P11 accusation, P12 sacred (4 acc/2 scar/2 sac for original mix; rebalance below)

Rebalanced split for scenario-balanced ground truth coverage (2 each scenario per format):

| Half | Probes | Scenarios covered |
|---|---|---|
| Original | P1 (scarcity), P5 (sacred), P8 (accusation), P9 (scarcity), P10 (accusation), P12 (sacred) | 2 sca / 2 sac / 2 acc |
| Annotated | P2 (scarcity), P3 (accusation), P4 (sacred), P6 (scarcity), P7 (sacred), P11 (accusation) | 2 sca / 2 sac / 2 acc |

→ This split allows format gap measurement on 6 vs 6 with same scenario distribution.

### 2.3 Files needed by evaluator

| File | Purpose |
|---|---|
| `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md` §0-§3 | Protocol overview + Q-set + score rule |
| `docs/b_direction/readability_probes/P{1,5,8,9,10,12}.txt` | 6 originals |
| `docs/b_direction/readability_probes/P{2,3,4,6,7,11}_ANNOTATED.txt` | 6 annotateds (v2.1) |
| `docs/b_direction/READABILITY_BLIND_RESULTS_V2.md` §1.0 cheat sheet + §2 template | Quick-fill + full table |

### 2.4 Time budget

- Reading: ~60-90 min (12 probes × 5-7 min/probe; annotated ~3 min, original ~7 min)
- Writing: ~10-15 min
- **Total: 70-105 min**

Note: pilot was 15-20 min for 4 probes = ~4 min/probe avg. Full N=12 scales linearly.

---

## 3. Pre-filled answer key (Claude predictions)

For self-check + comparison after evaluator answers:

### 3.1 v3 annotated headers (visible to evaluator on annotated probes)

Updated 2026-04-28 LOOP 34: added Public suspicion + Authority vigilance world-side fields.

| Probe | Final summary | Primary pressure | Failure mode | Public susp. (peak/final) | Authority vig. (peak/final) |
|---|---|---|---|---|---|
| P1 | PARTIAL | scarcity | — | 0.24/0.03 | 0.25/0.25 |
| P2 | SATURATION_DOMINATED | scarcity | shame_cap | 0.24/0.01 | 0.25/0.25 |
| P3 | SATURATION_DOMINATED | accusation | shame_cap | 0.22/0.16 | negligible |
| P4 | RECOVERY_DOMINATED | sacred | — | 0.06/0.00 | negligible |
| P5 | RECOVERY_DOMINATED | sacred | — | 0.06/0.00 | negligible |
| P6 | MIXED | scarcity | — | 0.43/0.31 | 0.25/0.25 |
| P7 | PARTIAL | sacred | — | 0.08/0.03 | negligible |
| P8 | MIXED | accusation | — | 0.22/0.00 | negligible |
| P9 | SATURATION_DOMINATED | scarcity | shame_cap | 0.24/0.03 | 0.25/0.25 |
| P10 | RECOVERY_DOMINATED | accusation | — | 0.22/0.00 | negligible |
| P11 | MIXED | accusation | — | 0.18/0.03 | negligible |
| P12 | SATURATION_DOMINATED | sacred | shame_cap | 0.39/0.31 | negligible |

**Detection accuracy** (per `READABILITY_BLIND_GROUND_TRUTH.md`):
- Primary pressure: 12/12 = 100% (v2.1)
- Final summary: 12/12 (computed from cohort arc rollup)
- Public suspicion: traced live (CrowdState ACTIVE memory)
- Authority vigilance: traced live (CrowdState DEAD memory, logged-only)

**v3 patterns observed**:
- Authority vigilance > 0 ONLY in scarcity scenarios (P1, P2, P6, P9) — `guard_approaches` event in scarcity build_world emits authority_vigilance accumulation. accusation/sacred scenarios show negligible.
- Public suspicion peaks correlate with cohort saturation (P6, P12 highest at 0.39-0.43)
- World-side detection now distinguishable across scenarios → Q3b world-side gap should improve

### 3.2 Expected evaluator answers

For Branch C activation, target metrics:

| Metric | v1.2 pilot | v2.1 expected | v3 expected (LOOP 34+) | Branch C trigger |
|---|---:|---|---|---|
| Readable rate (original) | 100% (2/2) | ~100% | ~100% | ≥80% ✓ |
| Readable rate (annotated) | 100% (2/2) | ~100% | ~100% | ≥80% ✓ |
| Format gap | 0 pp | ~0 pp | ~0 pp | within ±25% ✓ |
| CAN_EXPLAIN gap | +100 pp | maintain | maintain | ≥+50 pp ✓ |
| Q4a-rollup gap | +50 pp | maintain | maintain | ≥+30 pp ✓ |
| **Q2a-typing gap** | **0 pp** | **+50 pp** | **+50 pp** | **≥+30 pp ✓** |
| **Q3b world-side gap** | **0 pp** | **0 pp** | **+30 to +50 pp expected** | **≥2 axes positive** |

**v2.1 only**: 3/4 trigger conditions. Q3b world-side blocked by single-axis (crowd_mood only).

**v3 (LOOP 34)**: 3 axes available (crowd_mood + public_suspicion + authority_vigilance). Q3b world-side gap likely positive on ≥2 axes for hybrid pair (annotated has v3 fields, original does not). Branch C trigger condition likely met.

**Updated Branch C activation prediction**: 4/4 metrics likely trigger after v3.

---

## 4. Q3b world-side gap — open work (Branch C blocker)

### 4.1 Current state

Annotated v2.1 surfaces:
- Cohort outcomes (per-location)
- Pressure events count + targets
- Crowd blame total (max + final)

Does NOT surface:
- Authority presence (authority_reach state)
- Public attention (public_attention state)
- Group alignment trajectory

### 4.2 v3 spec proposal (LOOP 34+ candidate)

Add to annotated headline:
```
World-level dynamics:
  Crowd blame total:    peak X at t=Y → final Z
  Authority reach:      peak X at t=Y → final Z      ← NEW v3
  Public attention:     peak X at t=Y → final Z      ← NEW v3
```

**Implementation**: requires checking if MicroWorld exposes these as observable state. If yes, mechanical addition. If no, need engine cooperation (likely already in `crowd_state` or `world_event` summaries).

### 4.3 Decision: v3 work as Branch C precondition

Per `WITNESS_CLAUDE_CODE_CONTINUOUS_EXECUTION_DIRECTIVE.md`: Branch C **실질 진입은 forbidden_now**. But v3 spec design + implementation is *infra extension*, not "Branch C entry". Allowable per directive §3.1 if:
- low-risk
- reversible
- branch와 무관 (annotated header field 추가는 mechanical)

**Default**: continue v3 work in autonomous mode if MicroWorld state allows trivial extraction.

---

## 5. Eval execution plan

### 5.1 Step 1 (5 min): evaluator orientation

Evaluator (GPT-5.5 Thinking 또는 Lee 본인) reads:
- PROTOCOL_V2 §0-§3
- RESULTS_V2 §1.0 cheat sheet (옵션 + quick rules)

### 5.2 Step 2 (60-90 min): read 12 probes + answer

**Order**: format-interleaved to minimize order bias:
P1(annotated) → P2(original) → P3(annotated) → P4(annotated) → P5(original) → P6(annotated) → P7(annotated) → P8(original) → P9(annotated, but P9 is original per §2.2 split) ...

Actually use the §2.2 split:
- Originals: P1, P5, P8, P9, P10, P12
- Annotateds: P2, P3, P4, P6, P7, P11

Interleave: P1(o) → P2(a) → P3(a) → P4(a) → P5(o) → P6(a) → P7(a) → P8(o) → P9(o) → P10(o) → P11(a) → P12(o)

Wait — split says P1 is original. Adjusting: P1(o) P2(a) P3(a) P4(a) P5(o) P6(a) P7(a) P8(o) P9(o) P10(o) P11(a) P12(o).

For each probe:
1. Read (3-7 min depending on format)
2. Fill RESULTS_V2 §2.1 + §2.2 row
3. Q6a confusion notes if any
4. Q6b free-text feedback per probe (§2.4)

### 5.3 Step 3 (10-15 min): aggregates + ground truth comparison

- Compute §2.5 aggregates (counts, gaps)
- Compare §4 ground truth → Q2a accuracy + final summary self-call accuracy
- §2.7 full branch decision (Branch A / B / A+B / C)

### 5.4 Step 4 (5 min): final verdict

Apply PROTOCOL_V2 §4 v2.5 precedence-ordered algorithm to N=12 metrics → confirm Branch decision.

If 3/4 metrics trigger Branch C → **Branch C partial activation** (still gated on Q3b world-side gap).

If 4/4 metrics trigger → **Branch C full activation**.

---

## 6. What this eval will NOT determine

Per H4 (negative findings discipline):

- ❌ KERNEL_GAPS K1 vs K2 (shame_decay) — independent of readability
- ❌ Engine architectural decisions
- ❌ probe v3 fields beyond what's in v2.1
- ❌ Cross-scenario kernel coupling (Iter 165 territory)

This eval is **purely about Branch A vs C signal strength** post-v2.1 detection fix.

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Initial prep doc post-v2.1 detection. Path β. |
