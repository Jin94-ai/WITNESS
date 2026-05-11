# V3 Phase G — Sanity Check Summaries (9 trajectories)

**Generated:** 2026-04-23
**Evaluator source:** `data\reference\evaluation_results_calibrated.json`
**Thresholds:** rep=28.30, noise=29.00, copy=23.50, char_min=0.843

Lee 검토 항목 (각 trajectory):
- (a) 이건 정말 {category}처럼 보인다 → OK
- (b) 어색하다 / 왜 이 category 인가 → Flag (GPT 품질 이슈)
- (c) Rubric 판정이 이상하다 → Flag (rubric 이슈)

---

## Section 1 — Canonical-like (3 samples)

### Trajectory: **can_03**

- **Category:** canonical_like
- **Rubric scores:**
  character_composite: 0.667
  canon_valid:         True
  canon_soft_drift:    27.50
  causal_smoothness:   0.848
  novelty_band:        meaningful
  novelty_drift:       27.50
  discovery_class:     canonical_reproduction

- **Action summary at key ticks:**
  ```
  T 5: watch_quietly | T 7: assert_loyalty | T10: pray | T12: discuss_with_disciples | T13: follow_closely | T17: deny | T18: watch_quietly | T19: deny | T20: deny | T21: weep | T22: follow_at_distance | T28: discuss_with_disciples
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 3.7  grief= 0.0  guilt= 1.7  loyalty_pf= 8.6  hope= 8.1
    T19: fear= 5.0  grief= 0.0  guilt= 3.3  loyalty_pf= 8.3  hope= 8.0
    T20: fear= 6.3  grief= 0.0  guilt= 5.0  loyalty_pf= 8.0  hope= 8.0
    T21: fear= 5.5  grief= 3.0  guilt= 7.1  loyalty_pf= 8.0  hope= 7.9
    T28: fear= 4.9  grief= 4.0  guilt= 5.5  loyalty_pf= 8.0  hope= 9.9
  ```

- **Trajectory-level reading:**
  deny 2회 (T17=deny, T18=watch_quietly, T19=deny). tick 21에서 통곡 ✓. T28 복귀 없음 (=discuss_with_disciples).

---

### Trajectory: **can_08**

- **Category:** canonical_like
- **Rubric scores:**
  character_composite: 0.667
  canon_valid:         True
  canon_soft_drift:    26.50
  causal_smoothness:   0.837
  novelty_band:        meaningful
  novelty_drift:       26.50
  discovery_class:     canonical_reproduction

- **Action summary at key ticks:**
  ```
  T 5: accept_washing | T 7: pray | T10: fall_asleep | T12: pray | T13: draw_sword | T17: deny | T18: discuss_with_disciples | T19: deny | T20: deny | T21: weep | T22: follow_at_distance | T28: confess
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 4.2  grief= 0.0  guilt= 1.7  loyalty_pf= 8.6  hope= 8.4
    T19: fear= 4.8  grief= 0.0  guilt= 3.3  loyalty_pf= 8.3  hope= 8.3
    T20: fear= 6.1  grief= 0.0  guilt= 5.0  loyalty_pf= 8.0  hope= 8.3
    T21: fear= 5.3  grief= 3.0  guilt= 7.1  loyalty_pf= 8.0  hope= 8.3
    T28: fear= 5.3  grief= 4.0  guilt= 5.5  loyalty_pf= 8.0  hope=10.0
  ```

- **Trajectory-level reading:**
  deny 2회 (T17=deny, T18=discuss_with_disciples, T19=deny). tick 21에서 통곡 ✓. tick 28 confess (복귀) ✓.

---

### Trajectory: **can_12**

- **Category:** canonical_like
- **Rubric scores:**
  character_composite: 0.771
  canon_valid:         True
  canon_soft_drift:    28.00
  causal_smoothness:   0.851
  novelty_band:        meaningful
  novelty_drift:       28.00
  discovery_class:     canonical_reproduction

- **Action summary at key ticks:**
  ```
  T 5: watch_quietly | T 7: assert_loyalty | T10: assert_loyalty | T12: discuss_with_disciples | T13: draw_sword | T17: deny | T18: follow_at_distance | T19: deny | T20: deny | T21: weep | T22: follow_at_distance | T28: discuss_with_disciples
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 5.2  grief= 0.0  guilt= 1.7  loyalty_pf= 8.6  hope= 8.9
    T19: fear= 6.6  grief= 0.0  guilt= 3.3  loyalty_pf= 8.3  hope= 8.9
    T20: fear= 7.9  grief= 0.0  guilt= 5.0  loyalty_pf= 8.0  hope= 8.8
    T21: fear= 7.1  grief= 3.0  guilt= 7.1  loyalty_pf= 8.0  hope= 8.8
    T28: fear= 6.5  grief= 4.0  guilt= 5.5  loyalty_pf= 8.0  hope=10.0
  ```

- **Trajectory-level reading:**
  deny 2회 (T17=deny, T18=follow_at_distance, T19=deny). tick 21에서 통곡 ✓. T28 복귀 없음 (=discuss_with_disciples).

---


## Section 2 — Plausible alternative (3 samples)

### Trajectory: **alt_02**

- **Category:** plausible_alternative
- **Rubric scores:**
  character_composite: 0.914
  canon_valid:         True
  canon_soft_drift:    29.00
  causal_smoothness:   0.870
  novelty_band:        meaningful
  novelty_drift:       29.00
  discovery_class:     character_consistent_novel

- **Action summary at key ticks:**
  ```
  T 5: accept_washing | T 7: follow_closely | T10: pray | T12: follow_closely | T13: follow_closely | T17: join_crowd | T18: follow_closely | T19: watch_quietly | T20: stay_hiding | T21: watch_quietly | T22: follow_at_distance | T28: pray
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 3.3  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 8.3
    T19: fear= 4.4  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 8.2
    T20: fear= 6.3  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 8.2
    T21: fear= 5.7  grief= 1.8  guilt= 2.2  loyalty_pf= 8.9  hope= 8.2
    T28: fear= 6.1  grief= 0.5  guilt= 0.7  loyalty_pf= 8.9  hope=10.0
  ```

- **Trajectory-level reading:**
  deny 없음 — 대체: T17=join_crowd, T18=follow_closely, T19=watch_quietly. 통곡 없음 (T20=stay_hiding, T21=watch_quietly). T28 복귀 없음 (=pray).

---

### Trajectory: **alt_07**

- **Category:** plausible_alternative
- **Rubric scores:**
  character_composite: 0.879
  canon_valid:         True
  canon_soft_drift:    27.00
  causal_smoothness:   0.865
  novelty_band:        meaningful
  novelty_drift:       27.00
  discovery_class:     canonical_reproduction

- **Action summary at key ticks:**
  ```
  T 5: accept_washing | T 7: follow_closely | T10: confess | T12: pray | T13: assert_loyalty | T17: deny | T18: pray | T19: stay_hiding | T20: confess | T21: pray | T22: watch_quietly | T28: confess
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 3.2  grief= 0.0  guilt= 1.7  loyalty_pf= 8.6  hope= 9.2
    T19: fear= 4.9  grief= 0.0  guilt= 1.6  loyalty_pf= 8.6  hope= 9.6
    T20: fear= 6.6  grief= 0.0  guilt= 1.6  loyalty_pf= 8.6  hope= 9.9
    T21: fear= 5.8  grief= 1.8  guilt= 3.7  loyalty_pf= 8.6  hope=10.0
    T28: fear= 6.3  grief= 0.5  guilt= 2.1  loyalty_pf= 8.6  hope=10.0
  ```

- **Trajectory-level reading:**
  deny 1회만 (T17=deny, T18=pray, T19=stay_hiding). 통곡 없음 (T20=confess, T21=pray). tick 28 confess (복귀) ✓.

---

### Trajectory: **alt_13**

- **Category:** plausible_alternative
- **Rubric scores:**
  character_composite: 0.700
  canon_valid:         True
  canon_soft_drift:    34.00
  causal_smoothness:   0.864
  novelty_band:        noise
  novelty_drift:       34.00
  discovery_class:     not_discovery_noise

- **Action summary at key ticks:**
  ```
  T 5: accept_washing | T 7: pray | T10: confess | T12: confess | T13: assert_loyalty | T17: watch_quietly | T18: assert_loyalty | T19: deny | T20: weep | T21: withdraw_in_fear | T22: watch_quietly | T28: follow_closely
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 4.3  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 9.8
    T19: fear= 5.1  grief= 0.0  guilt= 1.7  loyalty_pf= 8.6  hope= 9.7
    T20: fear= 6.7  grief= 1.2  guilt= 1.6  loyalty_pf= 8.6  hope= 9.7
    T21: fear= 6.2  grief= 3.0  guilt= 3.8  loyalty_pf= 8.6  hope= 9.7
    T28: fear= 6.0  grief= 1.6  guilt= 2.2  loyalty_pf= 8.6  hope=10.0
  ```

- **Trajectory-level reading:**
  deny 1회만 (T17=watch_quietly, T18=assert_loyalty, T19=deny). tick 20에서 통곡 ✓. T28 복귀 없음 (=follow_closely).

---


## Section 3 — Obvious noise (3 samples, one per level)

### Trajectory: **noi_03**

- **Category:** obvious_noise (Level 1)
- **Rubric scores:**
  character_composite: 0.709
  canon_valid:         True
  canon_soft_drift:    29.00
  causal_smoothness:   0.879
  novelty_band:        meaningful
  novelty_drift:       29.00
  discovery_class:     canon_compatible_alternative

- **Action summary at key ticks:**
  ```
  T 5: watch_quietly | T 7: join_crowd | T10: join_crowd | T12: join_crowd | T13: join_crowd | T17: discuss_with_disciples | T18: discuss_with_disciples | T19: watch_quietly | T20: join_crowd | T21: pray | T22: stay_on_boat | T28: watch_quietly
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 1.9  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 6.5
    T19: fear= 3.0  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 6.4
    T20: fear= 4.3  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 6.4
    T21: fear= 3.5  grief= 1.8  guilt= 2.2  loyalty_pf= 8.9  hope= 6.8
    T28: fear= 1.7  grief= 0.5  guilt= 0.7  loyalty_pf= 8.9  hope= 8.8
  ```

- **Trajectory-level reading:**
  deny 없음 — 대체: T17=discuss_with_disciples, T18=discuss_with_disciples, T19=watch_quietly. 통곡 없음 (T20=join_crowd, T21=pray). T28 복귀 없음 (=watch_quietly).

---

### Trajectory: **noi_08**

- **Category:** obvious_noise (Level 2)
- **Rubric scores:**
  character_composite: 0.943
  canon_valid:         True
  canon_soft_drift:    30.00
  causal_smoothness:   0.868
  novelty_band:        noise
  novelty_drift:       30.00
  discovery_class:     not_discovery_noise

- **Action summary at key ticks:**
  ```
  T 5: fall_asleep | T 7: withdraw_in_fear | T10: fall_asleep | T12: withdraw_in_fear | T13: stay_hiding | T17: fall_asleep | T18: withdraw_in_fear | T19: stay_on_boat | T20: stay_on_boat | T21: join_crowd | T22: stay_hiding | T28: run_to_tomb
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 7.2  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.3
    T19: fear= 9.1  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.2
    T20: fear=10.0  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.2
    T21: fear= 8.8  grief= 1.8  guilt= 2.2  loyalty_pf= 8.9  hope= 7.2
    T28: fear= 8.8  grief= 0.5  guilt= 0.7  loyalty_pf= 8.9  hope= 9.2
  ```

- **Trajectory-level reading:**
  deny 없음 — 대체: T17=fall_asleep, T18=withdraw_in_fear, T19=stay_on_boat. 통곡 없음 (T20=stay_on_boat, T21=join_crowd). T28 복귀 없음 (=run_to_tomb).

---

### Trajectory: **noi_13**

- **Category:** obvious_noise (Level 3)
- **Rubric scores:**
  character_composite: 0.807
  canon_valid:         True
  canon_soft_drift:    29.00
  causal_smoothness:   0.842
  novelty_band:        meaningful
  novelty_drift:       29.00
  discovery_class:     canon_compatible_alternative

- **Action summary at key ticks:**
  ```
  T 5: jump_into_sea | T 7: run_to_tomb | T10: stay_on_boat | T12: jump_into_sea | T13: run_to_tomb | T17: jump_into_sea | T18: jump_into_sea | T19: run_to_tomb | T20: stay_on_boat | T21: draw_sword | T22: jump_into_sea | T28: stay_on_boat
  ```

- **State at canonical decision points:**
  ```
    T17: fear= 3.1  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.1
    T19: fear= 3.8  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.1
    T20: fear= 5.6  grief= 0.0  guilt= 0.0  loyalty_pf= 8.9  hope= 7.0
    T21: fear= 5.7  grief= 1.8  guilt= 2.2  loyalty_pf= 8.9  hope= 7.0
    T28: fear= 5.1  grief= 0.5  guilt= 0.7  loyalty_pf= 8.9  hope= 9.0
  ```

- **Trajectory-level reading:**
  deny 없음 — 대체: T17=jump_into_sea, T18=jump_into_sea, T19=run_to_tomb. 통곡 없음 (T20=stay_on_boat, T21=draw_sword). T28 복귀 없음 (=stay_on_boat).

---


## Summary table

| trajectory | category | drift | char | class |
|---|---|---:|---:|---|
| can_03 | canonical_like | 27.5 | 0.67 | canonical_reproduction |
| can_08 | canonical_like | 26.5 | 0.67 | canonical_reproduction |
| can_12 | canonical_like | 28.0 | 0.77 | canonical_reproduction |
| alt_02 | plausible_alternative | 29.0 | 0.91 | character_consistent_novel |
| alt_07 | plausible_alternative | 27.0 | 0.88 | canonical_reproduction |
| alt_13 | plausible_alternative | 34.0 | 0.70 | not_discovery_noise |
| noi_03 | obvious_noise L1 | 29.0 | 0.71 | canon_compatible_alternative |
| noi_08 | obvious_noise L2 | 30.0 | 0.94 | not_discovery_noise |
| noi_13 | obvious_noise L3 | 29.0 | 0.81 | canon_compatible_alternative |

## Phase G 상태 (for Lee 판단)

- **Step G1:** Reference loader + schema 검증 완료 (14 tests green).
- **Step G2:** 45 trajectories rubric 평가. Default threshold로 **45/45 NOT_DISCOVERY_NOISE**.
- **Step G3:** 분포 리포트 작성 (`V3_REFERENCE_DISTRIBUTION_REPORT.md`).

  - **Canonical drift median: 25.00** (range 22.5-28.5)
  - **Alternative drift median: 29.50** (range 27-35.5)
  - **Noise drift median: 29.00** (range 29-30)
  - canonical vs noise: **NO OVERLAP** (분리 가능)
  - **Character composite가 backwards**: canonical=0.67 (최저), alt=0.88, noise=0.81

- **Step G4:** Percentile-based calibration:
  - reproduction_threshold = canonical.drift P90 = **28.30**
  - noise_threshold = noise.drift P10 = **29.00**
  - character_min = alt.character P25 = **0.843**
  - copy_threshold = canonical.novelty_drift P10 = **23.50**

  Confusion matrix (target in parens):
  | actual | canonical% | alternative% | noise% |
  |---|---:|---:|---:|
  | canonical | **87%** (>80 ✓) | 13% (<15 ✓) | 0% (<5 ✓) |
  | alternative | 13% (<10 ✗) | **33%** (>70 ✗) | 53% (<20 ✗) |
  | noise | 0% (<5 ✓) | 67% (<10 ✗) | **33%** (>85 ✗) |

  **Target partially met (canonical only).** Alternative/noise classification failed.

- **Step G5:** Variable-specific recovery profile.
  - fear: HL=4.5, floor=0.0 (fast decay)
  - confusion: HL=7.0, floor=0.0
  - grief: HL=13.0, floor=0.15 (long tail)
  - guilt: HL=11.0, floor=0.10 (long tail)
  - shame: HL=6.0, floor=0.05
  - anger: HL=6.0, floor=0.0
  - awe: HL=10.0, floor=0.0

  Peter 100-tick: guilt 0.11 (floor), shame 0.05 (floor), others → 0 ✓

- **Tests:** 348 v3-local green (+ 14 reference + 8 calibration).

## Case 판정 (spec §7.1)

**Case β (Rubric 재설계 필요) 신호 뚜렷:**
1. Alternative/noise 분포 중첩 심함 (P10 vs P90 gap = 29.0 - 28.3 = 0.7)
2. Character composite가 canonical에서 최저 — rubric 작동 방향 반대
3. Causal smoothness 세 category 모두 0.85-0.88 — 구분력 없음
4. Confusion matrix 3 행 중 1 행만 target 달성

Phase H (rubric 재설계) 후보:
- 축 재정의 (character critic 로직 점검)
- Canon soft_drift 계산법 재검토 (현재 edit distance가 너무 블런트)
- Novelty critic를 canon에서 독립 (현재 novelty_drift == canon_soft_drift)