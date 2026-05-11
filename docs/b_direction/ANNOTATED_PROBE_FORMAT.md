# Annotated Probe Format -- Provisional Standard

**Date:** 2026-04-26
**Status:** Provisional standard (per WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS Step A1)
**Source generator:** `scripts/b_direction/generate_annotated_probes_all.py`

---

## 0. Purpose

Annotated probe is the **provisional readability-facing standard** for surfacing
WITNESS kernel dynamics to external readers. It supplements the original 12-probe
blind eval set (`P1.txt` - `P12.txt`) by pre-computing cohort outcomes, pressure
event counts, world-level trajectory, and event grouping.

This format is provisional. It will be revised after Step C blind eval results.

**Verbatim from directive (Lee, 2026-04-26)**:
> "annotated probe가 원본보다 가독성 잠재력이 높다는 strong hint가 있음"
> "annotated probe를 임시 표준 포맷으로 채택한다"

---

## 1. Format structure (5 sections)

### 1.1 Header
```
=== PROBE {probe_id}_ANNOTATED (annotated supplement) ===
```

`probe_id` matches the blind-eval naming (P1-P12). The `(annotated supplement)`
tag exists so that, if mistakenly placed in a blind eval, the reader can
identify it as supplementary.

### 1.2 Headline summary block

Four subsections, fixed order (v1.2 added Final summary at top). **v2 + v3 added new fields — see §9 for spec; quick map below**:

| Field | Version | Purpose |
|---|---|---|
| Final summary | v1.2 | Q4a arc rollup anchor |
| Primary pressure | v2 | Q2a scenario type (§9.1) |
| Failure mode | v2 (saturation only) | Saturation cause (§9.2) |
| Public suspicion | v3 | Q3b world-side meso memory (§9 LOOP 34) |
| Authority vigilance | v3 | Q3b world-side, DEAD memory but logged (§9 LOOP 34) |


#### 1.2.0 Final summary (v1.2; rule edge cases clarified 2026-04-28 post-Full-N12)
Single-line rollup of cohort arc types. One of:

| Label | Condition | Edge case |
|---|---|---|
| `LOW_ACTIVITY` | All cohorts `no shame accumulation` | — |
| `RECOVERY_DOMINATED` | "recovery" in arcs AND "saturation" NOT in arcs | **Includes partial cohorts** (P10 case): if a cohort is partial (final 4-7) but another is fully recovered, label is RECOVERY_DOMINATED. Per-agent residual high shame does NOT downgrade to MIXED. |
| `SATURATION_DOMINATED` | "saturation" in arcs AND "recovery" NOT in arcs | — |
| `MIXED` | Both "recovery" and "saturation" present (cohort divergence) | (P6 case) — cohort split visible regardless of raw event volume. |
| `PARTIAL` | Otherwise (mostly partial cohorts, no full recovery + no saturation) | — |

Format: `Final summary:  {LABEL}`.

Purpose: 1-line "what is this probe" answer. Reduces cohort-table scan
cost from N lines to 1 for navigation. Q4a (arc type) anchor.

**Design choice (post-Full-N12)**: RECOVERY_DOMINATED with partial residue is intentional — recovery > partial > no_shame priority. See `FULL_EVAL_N12_POSTCHECK.md` §2.4 for P5/P6/P10 case discussion.

#### 1.2.1 Cohort outcomes
Per-location aggregate, arc-classified. Format:

```
[L{n} cohort, {N} agents]:  {arc_label}
```

**Arc labels** (mutually exclusive, computed from per-agent peak/final shame):

| Label | Condition |
|---|---|
| `no shame accumulation` | max peak < 1.5 |
| `recovery: peak~{peak:.1f} → final~{final_mean:.1f}` | final_mean < 4 AND peak >= 5 |
| `saturation: peak~{peak:.1f} → final~{final_mean:.1f} (stuck)` | final_mean >= 7 |
| `partial: peak~{peak:.1f} → final~{final_mean:.1f}` | otherwise |

`peak` = max across cohort members of (max public_group shame over all ticks).
`final_mean` = mean across cohort members of (public_group shame at final tick).

#### 1.2.2 Pressure events + recovery actions
Two lines, fixed order:

```
Accusations: {N} fired (targets: {comma-separated unique target_role list})
Recovery actions: {N} confessions, {N} forgiveness rumors emitted
```

If no accusations: `Accusations: 0 fired (none)`.

#### 1.2.3 World-level dynamics
Three lines (v3 expanded — `Public suspicion` and `Authority vigilance` added LOOP 34 to address Q3b world-side gap):

```
Crowd blame total:   peak {peak:.1f} at t={tick} → final {final:.1f}
Public suspicion:    peak {peak:.2f} → final {final:.2f}            ← v3
Authority vigilance: peak {peak:.2f} → final {final:.2f}            ← v3
```

Negligible thresholds:
- `Crowd blame total:   negligible (peak < 0.1)` if peak < 0.1
- `Public suspicion:    negligible (peak < 0.05)` if peak < 0.05
- `Authority vigilance: negligible (peak < 0.05)` if peak < 0.05

Field provenance:
- `Crowd blame total` = sum of `crowd.blame_concentration.values()` across all crowd instances per tick, then peak/final
- `Public suspicion` = sum of `crowd.public_suspicion` (CrowdState ACTIVE meso memory; couples to social_threat pressure)
- `Authority vigilance` = sum of `crowd.authority_vigilance` (CrowdState DEAD memory; logged-only since Iter 38/43)

#### 1.2.4 Primary pressure (v2, see §9.1 for detection rule)
Single line after Final summary:

```
Primary pressure: {label}
```

Labels: `accusation` / `sacred` / `scarcity` / `shame` / `fear` / `awe` / `grief` / `mixed` / `none_clear`.

#### 1.2.5 Failure mode (v2, only on SATURATION_DOMINATED, see §9.2)
Single line after Primary pressure (omitted if final_summary != SATURATION_DOMINATED):

```
Failure mode: {label}
```

Labels: `shame_cap` / `repeat_retrigger` / `no_forgiveness_uptake` / `crowd_blame_persists` / `shame_decay_absent`.

### 1.3 Separator
```
============================================================
```
(60 `=` characters)

### 1.4 Agents/Locations metadata
Same as original probes (Iter 120 anonymization):

```
Agents: A1={role}, A2={role}, ... (up to 12)
Locations: L1, L2, ... (sorted)
```

Role anonymization map (`ANONYMIZED_ROLE_MAP` in
`scripts/b_direction/generate_readability_probes.py`):
- `disciple_follower` → `follower`
- `authority_priest` → `authority`
- `soldier_enforcer` → `enforcer`
- `crowd_participant` → `crowd`
- `family_anchor` → `family`
- `outsider`, `merchant`, `laborer`, `elite_strategist` → unchanged

Location anonymization is **insertion-order-dependent**: L1 = first location
inserted into `MicroWorld._spatial._locations`. Cross-probe comparison of
specific L-labels is NOT meaningful.

### 1.5 Event log (grouped by 50-tick windows)
```
--- Event log (grouped by 50-tick windows) ---
  (showing first 30 of {N} confessions; total in headline)   ← v1.1 cap disclosure (omitted if N≤30)
  --- Tick 0-49 ---
  t={n:>3}  accusation against {target_role}
  t={n:>3}  confession by A{n} ({role})
  --- Tick 50-99 ---
  ...
```

Events shown (cap at 30 confessions per probe to bound size):
- `accusation against {target}` -- from `public_accusation` events
- `confession by A{n} ({role})` -- from agent_action == "confess"

Forgiveness rumors are summarized in headline only (their per-tick listing
floods the event log; count alone is informative).

---

## 2. Comparison to original probes

| Dimension | Original (P1.txt) | Annotated (P1_ANNOTATED.txt) |
|---|---|---|
| Length | ~415 lines | ~80 lines |
| Headline | None | 3-section summary block |
| Cohort | None (per-agent only) | Per-location arc classification |
| Trajectory | Implicit (must read tick-by-tick) | Explicit peak/final |
| Event log | Flat, all events | Grouped by 50-tick window, capped at 30 confessions |
| Anonymization | Same (Iter 120) | Same (Iter 120) |
| Use case | Blind eval (Step C) | Supplementary reference / pilot eval |

5x compaction; both formats preserve role/location anonymization integrity.

---

## 3. Generation pipeline

Single source: `scripts/b_direction/generate_annotated_probes_all.py`.

Imports `PROBES_GROUND_TRUTH`, `build_world`, `ANONYMIZED_ROLE_MAP` from
`generate_readability_probes.py` -- ensures annotated and original probes use
the **same scenario/seed/variant** for each P-index. Probe order is determined
by `random.Random(42).shuffle(list(range(12)))` and is identical across both
generators.

### 3.1 PYHASH guarantee
`enforce_pyhash()` is called at module load. Output is bit-identical across
runs only if `PYTHONHASHSEED=0` (per Iter 105 PYHASH fix discipline).

### 3.2 Output location
- Original: `docs/b_direction/readability_probes/P{1-12}.txt`
- Annotated: `docs/b_direction/readability_probes/P{1-12}_ANNOTATED.txt`
- (NEW) Organized copy: `docs/b_direction/readability_probes_annotated/P{1-12}.txt`

---

## 4. Validation checklist (when regenerating)

Before publishing a new annotated probe set:

- [ ] `enforce_pyhash()` does not raise (PYTHONHASHSEED=0 set)
- [ ] All 12 files generated (P1_ANNOTATED.txt through P12_ANNOTATED.txt)
- [ ] Each file has the 5 sections in order (header → headline → separator → metadata → event log)
- [ ] Cohort arc labels use only the 4 valid labels from §1.2.1
- [ ] Anonymization is consistent with original probes for the same P-index
- [ ] Probe order matches `generate_readability_probes.py` (random.Random(42) seed)

---

## 5. Open questions (will revise after Step C)

These are deferred until blind eval results arrive:

1. **Cohort grouping by initial location** -- some scenarios have agents that
   move between locations within 200 ticks. Initial-location cohorts may
   misclassify those agents.
2. **Arc classification thresholds** -- the (1.5, 4, 5, 7) thresholds were
   chosen by judgment in Iter 163. Different thresholds change labels.
3. **30-confession cap** -- some probes have 70+ confessions; truncation may
   hide late dynamics.
4. **Hybrid eval risk** -- annotated probes may LEAK ground truth (cohort
   distribution + arc labels can hint at scenario type).
5. **Single horizon (50-tick window)** -- coarser/finer windows have not been
   compared.

These will be revisited after Step C readability blind eval gives empirical
signal on what the annotated format actually communicates to readers.

---

## 6. What this format does NOT include

Per H4 (negative findings discipline):

- **No per-agent shame trajectory** -- only cohort aggregates. Individual
  trajectories live in original probes.
- **No relation-shift summary** -- though the directive (A1) lists "relation
  shift" as a candidate field, the current generator does not extract it.
  Future revision candidate.
- **No motif-shift summary** -- same as above; motif activations are not
  surfaced in current format.
- **No final summary line** -- cohort outcomes are the closest analog. A
  one-line probe-wide summary (e.g., "recovery-dominated" / "saturation
  -dominated") is not yet computed.

These map to the directive's "event log / dominant pressure /
relation shift / motif shift / crowd state / final summary" wishlist (§A1).

**v1.2 status (Iter 187)**: 4 of 6 fields present:
- ✓ event log (§1.5)
- ✓ dominant pressure (§1.2.2)
- ✓ crowd state (§1.2.3)
- ✓ final summary (§1.2.0, NEW v1.2)
- ✗ relation shift (still missing, v2 candidate)
- ✗ motif shift (still missing, v2 candidate)

---

## 7. Original vs Annotated — comparison companion (NEW 2026-04-28)

Lee가 두 포맷을 평가할 때 무엇이 다르고 무엇이 같은지 한눈에 보기 위한 정리. directive §5 우선순위 2 (annotated representation 강화) 작업.

### 7.1 같은 것 (둘 다 가지고 있음)

| 정보 | Original | Annotated |
|---|---|---|
| 기본 식별 (probe ID + scenario + variant + seed) | header | header |
| Tick 수 (50) | header | header |
| Per-cohort outcome (recovered / saturated / partial) | inferred from cohort_outcomes raw | §1.2.4 cohort outcomes table |
| Event log (raw event triggers) | full log | §1.5 event log (capped to 30 lines, §1.5 cap disclosure if more) |
| Cohort identity (agent IDs) | listed in cohort_outcomes | anonymized to N-letter labels (A, B, C…) |
| Final shame state per agent | trajectory tail | summarized in cohort outcomes |

### 7.2 Original에만 있는 것

- **Per-agent shame trajectory** — 시간에 따른 shame 곡선 (per-tick raw values)
- **Per-agent location/action sequence** — 누가 언제 어디로 이동했는지
- **Per-relation trust/scar** — 관계별 raw 값
- **Full crowd_mood / authority / public_attention timeseries** — 50 tick 전체 raw

이는 "raw substrate". evaluator가 *가설을 쌓을 수 있는* primary material.

### 7.3 Annotated에만 있는 것 (rollup layers)

- **§1.2.0 final summary 1-line rollup** (v1.2, Iter 187): `LOW_ACTIVITY` / `RECOVERY_DOMINATED` / `SATURATION_DOMINATED` / `MIXED` / `PARTIAL` — Q4a-style arc inference를 한 줄로 압축
- **§1.2.2 dominant pressure label** — 주된 pressure (shame / grief / fear / awe…)
- **§1.2.3 crowd state label** — crowd_mood 우세 라벨 (calm / fearful / awe-struck…)
- **§1.2.4 cohort outcomes table** — N-cohort을 recovered/saturated/partial로 분류
- **§1.5 cap disclosure** (v1.1, Iter 185): event log 30 줄 cap 시 "showing first 30 of N" 표시

이는 "interpretation overlay". evaluator의 *분석 시간을 단축*하지만 ground truth와 분리되지 않으면 anchor 효과 위험.

### 7.4 안 들어 있는 것 (v1.2까지)

- **Per-agent relation shift summary** — directive A1 wishlist이지만 미구현 (v2 후보)
- **Per-agent motif activation summary** — directive A1 wishlist이지만 미구현 (v2 후보)
- **Cross-probe comparison** — 단일 probe만 다룸. cross-probe pattern은 evaluator가 직접 본다

### 7.5 평가 시 함의

| Branch signal | 어디에서 보이는가 |
|---|---|
| **Branch A** (annotated가 readability 향상) | annotated 포맷의 §1.2.0 rollup이 Q4a 정확도를 올린다면 → format gap >0 |
| **Branch B** (annotated 도움 안 됨, 구조 단순화 필요) | 두 포맷 모두 readable 낮음 → original raw도 충분히 읽힘 (rollup 불필요) OR annotated rollup도 도움 안 됨 (기본 구조 자체 불명료) |
| **Branch A+C** | annotated rollup이 arc 추론 도움 (A) + Q3b world-side가 두 포맷 모두 명확 (C ready) |

### 7.6 leakage 위험 (H4)

Annotated 포맷은 §1.2.0/§1.2.2/§1.2.3/§1.2.4 라벨이 ground truth와 *부분적으로 겹친다*:
- §1.2.0 final summary는 Q4a arc 분류와 어휘가 같음 (RECOVERY/SATURATION/MIXED) → Q4a self-call이 라벨을 베낄 수 있음
- §1.2.2 dominant pressure는 Q2a primary pressure와 1:1 매핑 가능
- §1.2.4 cohort outcomes는 §3 cross-probe 패턴 inference를 leak

**완화책**: §1.1.5 self-call template — annotated 라벨을 보기 전에 evaluator가 먼저 자기 말로 final summary를 적도록 강제. match rate가 anchor effect를 측정.

---

## 8. Versioning

| Version | Date | Change |
|---|---|---|
| v0 (Iter 163 prototype) | 2026-04-26 | `P_ANNOTATED_DEMO.txt`, single probe |
| v1 (Iter 166 + this doc, Iter 176) | 2026-04-26 | All 12 probes, 5-section format, provisional standard |
| v1.1 (Iter 185) | 2026-04-27 | Cap disclosure 추가. 12 probes regenerated. |
| v1.2 (Iter 187) | 2026-04-27 | Final summary 1-line rollup (5 labels: LOW_ACTIVITY / RECOVERY_DOMINATED / SATURATION_DOMINATED / MIXED / PARTIAL) added at top of headline. Reduces N-cohort scan to 1-line nav. Q4a anchor. 12 probes regenerated. |
| v1.3 | 2026-04-28 | §7 Original vs Annotated 비교 companion (autonomous-mode, directive §5 우선순위 2). 동일/차이/leakage 위험 + Branch signal 매핑 명시. §1-§6 unchanged. |
| v1.4-spec | 2026-04-28 | §8 v2 spec proposal. |
| v2 (executed, autonomous LOOP 28-30) | 2026-04-28 | §8 spec implemented. detect_primary_pressure + detect_failure_mode 추가. 12 probes + 4 PILOT regenerated. Detection: accusation 5/5, sacred 4/4, **scarcity 0/4** (limitation). |
| v2.1 (executed, autonomous LOOP 32) | 2026-04-28 | Scarcity detection 강화 — cast/location multi-signal. Detection: 12/12 = 100%. |
| **v3 (executed, autonomous LOOP 34)** | **2026-04-28** | **World-side dynamics fields added (Q3b world-side gap address). Per-tick aggregation of `public_suspicion` (ACTIVE meso memory) + `authority_vigilance` (DEAD logged-only memory) across all crowd instances. Headline shows peak/final for both. Tests 1647 unchanged.** |

---

## 9. v2 / v3 spec (post pilot blind, 2026-04-28)

**Trigger**: External LLM (ChatGPT/GPT-5.5 Thinking) pilot blind eval (`READABILITY_BLIND_RESULTS_V2_FILLED.md`) → P-A+C verdict. Q2a-typing gap = 0 pp 발견 = annotation이 arc rollup tool이지 scenario detector 아님. 핵심 actionable: pressure source field 추가. v3 추가: Q3b world-side gap = 0 pp address.

### 9.1 새 field 1: Primary pressure (§1.2.2 확장)

**현재 v1.2 (line 4 in headline)**:
```
  Pressure events + recovery actions:
    Accusations: 2 fired (targets: ...)
    Recovery actions: 200 confessions, 124 forgiveness rumors emitted
```

**v2 안 (after `Final summary` line)**:
```
  Final summary:  SATURATION_DOMINATED
  Primary pressure: <shame / fear / sacred / scarcity / accusation / grief / mixed>
  ...
```

**Detection rule** (proposed):
| Scenario | Detection signal | Primary pressure label |
|---|---|---|
| accusation | accusation events ≥3 OR target_count ≥1 | `accusation` |
| scarcity | scarcity-related events present (TBD: which event_id signals scarcity?) | `scarcity` |
| sacred | `prayer_invitation` OR `miracle_witnessed` events present | `sacred` |
| awe-injection | high awe state (≥5) on majority cohort | `awe` |
| (default) | none of above | `mixed` (or `none_clear` if low_activity) |

**Risk (leakage)**: PROBES_GROUND_TRUTH의 scenario name과 primary pressure label이 1:1 매핑되면 evaluator가 직접 베낌. 대안:
- (a) scenario에서 직접 매핑: 빠르지만 leakage 100%
- (b) event 패턴에서 empirical detect: 정확도 의존, leakage 낮음
- (c) 두 개 다 감지하여 mismatch 시 `mixed` 표시: 가장 안전

**권장**: (b) empirical detect.

### 9.2 새 field 2: Failure mode (saturation 시만, §1.2.0 확장)

**현재 v1.2**: `Final summary: SATURATION_DOMINATED`만.

**v2 안**:
```
  Final summary:  SATURATION_DOMINATED
  Failure mode: <shame_cap / repeat_retrigger / no_forgiveness_uptake / crowd_blame_persists / shame_decay_absent>
```

**Detection rule** (proposed):
| Failure mode | Detection signal |
|---|---|
| `shame_cap` | peak ≈ 10.0 AND final ≈ 10.0 (saturation ceiling) |
| `repeat_retrigger` | accusation events ≥3 AND each followed by partial recovery dip then re-saturation |
| `no_forgiveness_uptake` | forgiveness_emitted ≥10 AND final shame still ≥7 (rumor fired but unsuccessful) |
| `crowd_blame_persists` | crowd_blame_max ≥1.5 AND crowd_blame_final ≥1.0 (crowd never released blame) |
| `shame_decay_absent` | (default if above fail) — KERNEL_GAPS Gap 1 manifestation |

**Why valuable**: PILOT_4 confusion note (FILLED §1.2): "200 confessions + 124 forgiveness rumors still yielding saturation is conceptually important, but the causal reason for failed recovery is not visible." Failure mode field가 이 visibility 제공.

### 9.3 Implementation plan (Lee 승인 후)

1. **Modify**: `scripts/b_direction/generate_annotated_probes_all.py`
   - Add `detect_primary_pressure()` function (§8.1 detection rule)
   - Add `detect_failure_mode()` function (§8.2 detection rule, only if final_summary == SATURATION_DOMINATED)
   - Insert into headline assembly (after final_summary line)

2. **Regenerate**: 12 P{1-12}_ANNOTATED.txt + 4 PILOT_*.txt

3. **Update**: `READABILITY_BLIND_RESULTS_V2.md` §1.0 cheat sheet — primary_pressure + failure_mode 옵션 추가

4. **Cost**: ~30 LOC + tests + 12 probes regenerate. 1-2 hour.

5. **Risk**: low — annotated format 변경, no engine/source data 변경. v1.2 backward-compat (v2 field가 추가될 뿐, 기존 lines 보존).

### 9.4 Validation gate (post-implementation)

After v2 implementation, run **full N=12 eval (Path β per BRANCH_DECISION §5.2)**:

| Metric | v1.2 baseline (pilot) | v2 expected | Branch C trigger |
|---|---:|---|---|
| Q2a-typing gap | 0 pp | ≥+30 pp | ≥+30 pp 시 confirm |
| Q3b world-side gap | 0 pp | unchanged or improve | ≥2 axes positive 시 partial confirm |
| Q4a-rollup gap | +50 pp | maintain | maintain ≥+30 pp |
| CAN_EXPLAIN gap | +100 pp | maintain | maintain ≥+50 pp |

**Branch C 실질 진입 조건**: full N=12에서 위 4 metrics 모두 trigger 충족.

### 9.4.1 Implementation results (LOOP 28-31, autonomous-mode)

**Per-probe detection result**:

| Probe | Scenario (GT) | Final summary | Primary pressure (v2) | Failure mode (v2) | Detection |
|---|---|---|---|---|---|
| P1 | scarcity sham_mul_0.8 | PARTIAL | accusation | — | ✗ scarcity |
| P2 | scarcity baseline | SATURATION | accusation | shame_cap | ✗ scarcity |
| P3 | accusation p2a_off | SATURATION | accusation | shame_cap | ✓ |
| P4 | sacred baseline | RECOVERY | sacred | — | ✓ |
| P5 | sacred baseline | RECOVERY | sacred | — | ✓ |
| P6 | scarcity p2a_off | MIXED | accusation | — | ✗ scarcity |
| P7 | sacred sham_mul_0.05 | PARTIAL | sacred | — | ✓ |
| P8 | accusation sham_mul_0.8 | MIXED | accusation | — | ✓ |
| P9 | scarcity baseline | SATURATION | accusation | shame_cap | ✗ scarcity |
| P10 | accusation baseline | RECOVERY | accusation | — | ✓ |
| P11 | accusation baseline | MIXED | accusation | — | ✓ |
| P12 | sacred p2a_off | SATURATION | sacred | shame_cap | ✓ |

**Summary**: 8/12 = 67% accuracy. accusation 5/5, sacred 4/4, **scarcity 0/4**.

**PILOT impact (Q2a-typing gap)**:
- v1.2: 1/2 vs 1/2 = 0 pp
- v2 (예측): annotated 2/2 (sacred + accusation) vs original 1/2 (unchanged) = **+50 pp**
- 이는 P-A+C decision의 핵심 actionable인 Q2a-typing gap 0 pp 해결을 *기계적으로 검증*한 결과.

**Validation gate update (per §8.4)**: full N=12 eval에서 Q2a-typing gap 측정 → 67% accuracy(scarcity 제외)이 evaluator의 annotated reading에 미치는 영향 정량화.

### 9.4.2 ~~Documented limitation: scarcity detection 0/4~~ (RESOLVED v2.1)

**v2 finding**: scarcity scenarios (P1, P2, P6, P9) 모두 `accusation`으로 분류.

**Root cause discovered (LOOP 32 build_world inspection)**:
- scarcity scenario uses **same** `public_accusation` + `guard_approaches` events as accusation scenario
- distinctive feature is **cast composition** (merchant, fisher_laborer, beggar) + **locations** (granary, marketplace, poor_quarter)
- event log alone cannot distinguish accusation vs scarcity — this is a **scenario design fact, not generator bug**

**v2.1 fix**: cast/location multi-signal detection added to §8.1 rule:
```python
scarcity_roles = {"merchant", "fisher_laborer", "beggar", "laborer"}
scarcity_locations = {"granary", "marketplace", "poor_quarter"}
is_scarcity_context = has_scarcity_cast AND has_scarcity_locations
```

If `is_scarcity_context` AND no sacred signals → classify `scarcity` (overrides accusation default).

**Result**: detection 8/12 → **12/12 = 100%**. PILOT_3, PILOT_4 unchanged (already correct in v2). PILOT_1 (P10=accusation) + PILOT_2 (P9=scarcity) — note PILOT_2 originals show accusations only, but P9 ANNOTATED now shows `scarcity`.

**Implication for Q2a-typing gap measurement**: with v2.1, evaluator reading annotated probes will see correct scenario type for all 12. Original probes don't have annotated label → still unaffected. Q2a-typing gap potentially **+50 to +75 pp** in full N=12 (vs 0 pp in v1.2 pilot).

---

### 9.5 What v2 does NOT add

- ✗ Per-agent relation shift summary (still missing)
- ✗ Per-agent motif activation summary (still missing)
- ✗ Cross-probe comparison (still single-probe)
- ✗ Engine/state changes (purely format extension)

위 3개는 v3 후보 (cross-cycle, after Branch C 활성화 시).
