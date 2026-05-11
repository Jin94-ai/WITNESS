# Rubric Demo — 4-Axis Discovery Candidate Classifier

> ⚠️ **Fixture Stress-Test Disclaimer (per directive 2026-05-11 §6)**
>
> **This is a rubric stress-test surface using controlled fixtures, not a claim of validated real-world discovery.**
>
> 이 데모는 통제 fixture 기반 rubric stress-test이며, 실제 데이터 기반 discovery 검증 결과가 아니다.
>
> 모든 trajectory가 *합성(synthetic) / fictional*이며, ensemble 수치 (cross_scenario 19/20 / multi_agent 14/15 / multi_seed 4/5)는 rubric 엔진이 *통제된 입력*에 대해 어떻게 분류하는지를 보여주는 **stress-test 결과**다. 실제 영화·드라마·사료 데이터에 대한 validation은 *Phase 3.0 Mini Pilot* 이후에만 가능하다.

> **Phase 3.05 Rubric Design Review** (`docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md`) 결과물.
> **Generated**: 2026-05-11 (cycle: Rubric runner CLI deployment)
> **Source**: `tests/fixtures/rubric_demo/peter_synthetic_trace.json` (**합성/fictional**)
> **Tool**: `scripts/rubric/run_rubric.py`

---

## Non-Claims (review §3)

이 demo는 *결과물 시연*만을 목적으로 한다. 다음을 **증명하지 않는다**:

- 신학적 정답 / 진실 — Rubric output이 *truth claim*이 아님
- 문학적 완성도 / 의미 — Rubric은 *분류 도구*이지 평가자가 아님
- 베드로의 실제 trajectory — 사용된 trace는 **합성 (synthetic)** fixture

이 demo가 보여주는 것:
1. 4-Axis Rubric이 *실제 trajectory를 받아 분류*할 수 있다
2. 분류 결과는 4개 독립 critic의 sub-report로 보존됨 (scalar 합산 0)
3. 최종 label은 **discovery candidate class** (truth claim 아님)
4. 모든 threshold는 `uncalibrated_phase3_placeholder` (Phase 5+ 실측 보정 필요)

---

## 결과 요약 — 4 trajectory variants → 3 distinct discovery classes

### 8-variants 매트릭스 — 모든 endpoint 시연

| Trajectory | discovery_class | Step | 핵심 관찰 |
|---|---|---|---|
| `peter_canonical_reproduction` (+ `--is-all-hardcoded`) | **not_discovery_hardcoded** ✅ | **1** | hardcoded firing 가정 시 즉시 분류 |
| `peter_invalid_canon` (3 ticks, vocab 밖 action) | **invalid_canon_violation** ✅ | **2** | `fly_away`, `summon_angel` 등 vocab 위반 (review §2.1 정식 명칭) |
| `peter_incoherent` (5 ticks) | **not_discovery_incoherent** ✅ | **3** | unexplained jumps (fear 1→50) — review §2.2 P0 |
| `peter_noise` (4 ticks) | **not_discovery_noise** ✅ | **4** | action ↔ scene affordance 불일치 (draw_sword at sacred_meal 등) |
| `peter_canonical_reproduction` (10 ticks) | **canonical_reproduction** ✅ | **6** | 정경 sequence 정확 reproduce |
| `peter_meaningful_novel` (10 ticks) | **character_consistent_novel_candidate** ✨ | **7** | review §2.1 P0 *positive* CANDIDATE |
| `peter_synthetic_trace` (12 ticks) | **canon_compatible_character_drift** | **8** | canon ✓, novelty copy band |
| `peter_novel_candidate` (9 ticks) | **canon_compatible_character_drift** | **8** | 동상 |

### 시연된 7 distinct discovery classes — *8-step flowchart 모든 endpoint*:

| # | Class | Step | 의미 |
|---|---|---|---|
| 1 | `not_discovery_hardcoded` | 1 | hardcoded event firing — discovery 아님 |
| 2 | `invalid_canon_violation` | 2 | hard constraint 위반 — 즉시 INVALID |
| 3 | `not_discovery_incoherent` | 3 | causal gate fail (review §2.2 P0) |
| 4 | `not_discovery_noise` | 4-5 | context_break high 또는 novelty noise |
| 5 | `canonical_reproduction` | 6 | 정경 충실 재생 |
| 6 | **`character_consistent_novel_candidate`** ✨ | 7 | **review §2.1 P0 positive CANDIDATE** |
| 7 | `canon_compatible_character_drift` | 8 | canon valid + character ✓이지만 full novel tier 미달 |

→ Rubric의 *8-step flowchart 모든 endpoint*가 portfolio에 실제 시연됨. discovery class 7개 모두 *진짜 실행 결과*.

### 보너스: Real Simulation e2e (`real_simulation_report.json`)

기존 8 fixtures는 *합성 trajectory*다. 다음은 **진짜 simulation 결과** — `examples/demo_v07.py`로 실제 시뮬레이션 실행 후 rubric 적용:

```bash
# 1. demo_v07로 실제 simulation 실행 → trace JSONL (971 events)
python examples/demo_v07.py --player peter --seed 0 --output output/peter_trace.jsonl

# 2. trace → rubric records 변환 (adapter)
python scripts/rubric/trace_to_records.py \
    --trace output/peter_trace.jsonl \
    --agent peter \
    --output output/peter_records.json   # 250 peter records

# 3. rubric 실행
python scripts/rubric/run_rubric.py \
    --records output/peter_records.json \
    --output docs/portfolio/demo_rubric/real_simulation_report.json \
    --md-report docs/portfolio/demo_rubric/real_simulation_report.md \
    --vocabulary "assert_loyalty deny discuss_with_disciples draw_sword follow_closely pray stay_awake stay_hiding weep withdraw_in_fear fall_asleep flee follow_at_distance confess"
```

**결과** (real simulation, 250 ticks):
- discovery_class: **not_discovery_noise**
- canon_valid: True / causal_gate: True / character_signature: True
- context_break critic trip (real simulation actions가 scene affordance와 완벽 매칭 안 됨)

→ Rubric이 *진짜 simulation 결과*에도 적용 가능 + **과대평가 회피** (real simulation도 noise 분류 가능). e2e pipeline 작동 입증.

### Multi-seed Ensemble (`multi_seed_ensemble.json`) — review §H8 5+ seed 원칙

Single seed claim은 위험 (variance risk). Phase 3.05 review §H8 (HARNESS H8) — *5+ seed ensemble 필수*. peter seed=0~4 simulation → rubric:

**Discovery class distribution (5 seeds)**:

| Class | Count | Ratio |
|---|---|---|
| `character_consistent_novel_candidate` ✨ | **4/5** | **80%** |
| `not_discovery_noise` | 1/5 | 20% |

**Per-axis average (5 seeds)**:

| Axis | Mean | 해석 |
|---|---|---|
| character.composite | 1.000 | character signature 강 (always pass) |
| causal.smoothness | 1.000 | real simulation은 인과적으로 smooth |
| causal.explained_ratio | 1.000 | unexplained jumps 0 |
| novelty.structured_deviation | 0.722 | meaningful band 상단 (noise boundary 0.75 근접) |
| canon.soft_compatibility | 0.000 | real simulation은 정경 sequence와 다른 행동 |

**해석**: 
- 4/5 seed에서 *Phase 3.05 review §2.1 P0 positive class* (`character_consistent_novel_candidate`) 도달
- 1/5 seed에서 noise — *seed sensitivity 명시* (single seed claim 회피)
- character/causal는 strong (real simulation pipeline 정합성)
- novelty boundary 근접 → 약간의 perturbation이 noise로 trip 가능

→ Real simulation에서도 **80% character_consistent_novel_candidate** + 20% sensitivity. *5 seed ensemble*이 *single seed*보다 정직한 claim.

### Multi-Agent Ensemble (`multi_agent_ensemble.json`) — 3 agents × 5 seeds = 15 reports

같은 simulation에서 *3 agents* (peter / judas / caiaphas) 각각 분류:

**Per-agent distribution**:

| Agent | character_consistent_novel_candidate | not_discovery_noise |
|---|---|---|
| **peter** | 4/5 (80%) | 1/5 (20%) |
| **judas** | 5/5 (100%) | 0 |
| **caiaphas** | 5/5 (100%) | 0 |

**Overall** (15 reports): **character_consistent_novel_candidate 14/15 (93%) + not_discovery_noise 1/15 (7%)**

**해석**:
- Witness simulation의 3개 핵심 agent 모두 *Phase 3.05 review §2.1 P0 positive class*에 거의 일관 도달
- judas + caiaphas: 100% positive (5/5)
- peter: 80% positive (1/5 sensitivity)
- *engine의 cross-agent 재현성* 입증 — 같은 simulation에서 다른 agent도 character signature + novelty + causal coherence 통과
- agent-specific vocabulary 필수: peter `pray/deny/weep/...` / judas `follow/question/withdraw/betray` / caiaphas `observe/order_arrest/order_surveillance`

### Cross-Scenario Ensemble (`cross_scenario_ensemble.json`) — 4 agent contexts × 5 seeds = 20 reports

**Peter scenario** (passion narrative, 3 agents) + **Vangogh scenario** (creative drive, 1 agent):

| Scenario/Agent | character_consistent_novel_candidate | not_discovery_noise |
|---|---|---|
| peter/peter | 4/5 (80%) | 1/5 (20%) |
| peter/judas | **5/5 (100%)** | 0 |
| peter/caiaphas | **5/5 (100%)** | 0 |
| **vangogh/vangogh** | **5/5 (100%)** | 0 |

**Overall (20 reports)**: **19/20 (95%) character_consistent_novel_candidate** + 1/20 (5%) noise.

**해석 — engine generality 입증**:
- Witness engine이 *전혀 다른 두 scenario* (passion narrative ↔ creative drive)에서 거의 일관된 character_consistent_novel_candidate 도달
- Vangogh actions (`paint_feverishly`, `despair`, `self_harm`, ...) 도 character signature + causal + novelty meaningful 통과
- *engine 코드 변경 0*으로 다른 scenario에서 작동 — content-engine 분리 원칙 (`engine/` is person-agnostic, `content/{peter,vangogh}/` is scenario-specific) 입증
- 95% positive ratio + 5% sensitivity → *honest cross-scenario claim* 가능

### Character Discrimination Diagnostic (review §5 후속 — cycle 23)

**review §5 비판 대상**: 기존 Character Critic 3 요소 (impulsivity / relationship / oscillation)이 *"즉각반응형 인물 일반성"*을 측정해 약한 critic이라는 우려. Phase H 재설계 (relation_stability + identity_retention + recovery_plausibility) 이후 이 우려가 *empirically* 해소됐는지 검증:

**Anti-signature fixture** ([peter_anti_signature.json](../../../tests/fixtures/rubric_demo/peter_anti_signature.json)) — 의도적으로 character signature *3축 모두 약하게* 구성:
- relation_stability: loyalty_pf가 deny action 없이 9 → 3 (unexplained drop)
- identity_retention: 최종 loyalty 1.0 << minimum 4.0
- recovery_plausibility: guilt spike (0→5) 후 7 ticks repentance-family action 0건

**Deploy 결과** ([`character_discrimination.json`](character_discrimination.json) / [`.md`](character_discrimination.md)):

| Axis | Score | Gate (uncalibrated) | 판정 |
|---|---|---|---|
| relation_stability | 0.500 | ≥ 0.5 | at threshold |
| identity_retention | 0.250 | ≥ 0.5 | **fail** |
| recovery_plausibility | 0.000 | ≥ 0.3 | **fail** |
| composite | 0.250 | — | display only |
| **passed_minimum_signature** | **False** | — | discrimination 작동 ✅ |

→ `weak_axes = [identity_retention, recovery_plausibility]` — 자동 검증 가능.

**대조**: `peter_meaningful_novel` (positive class)은 동일 critic에서 `passed_minimum_signature=True`로 통과. 양방향 discrimination 확인.

자동 검증: `tests/test_rubric/test_rubric.py::test_phase3_05_character_critic_rejects_anti_signature_trajectory` + `test_phase3_05_character_critic_passes_meaningful_novel`.

#### Axis-isolated ensemble (cycle 26) — minimum gate per-axis 입증

cycle 23 fixture는 *3축이 동시에* 약한 케이스. **각 axis가 독립적으로** failure를 trigger할 수 있는지 (minimum gate design 입증) N-case ensemble로 검증:

| Fixture | weak_axes | 다른 2축 |
|---|---|---|
| `peter_anti_relation_only` → `character_axis_anti_relation_only.{json,md}` | `[relation_stability]` (drops=3/5, rate=0.6) | identity=1.0 / recovery=1.0 (pass) |
| `peter_anti_identity_only` → `character_axis_anti_identity_only.{json,md}` | `[identity_retention]` (final loyalty 1.5 < 4.0) | relation=1.0 / recovery=1.0 (pass) |
| `peter_anti_recovery_only` → `character_axis_anti_recovery_only.{json,md}` | `[recovery_plausibility]` (guilt 0→5 spike + 0 repentance in window) | relation=1.0 / identity=1.0 (pass) |

→ **3 axis 모두 독립적으로** `passed_minimum_signature=False`를 trigger 가능. composite 단순 평균이라면 한 축 fail이 다른 축 pass에 묻혀버리는 review §2.3 우려를 minimum gate가 *empirically* 해소.

자동 검증: `test_phase3_05_axis_isolated_only_{relation,identity,recovery}_fail` + `test_phase3_05_axis_isolated_demos_deployed`.

---

### Alignment Demos (review §2.5 P1 extended — cycle 16/20/22)

`CausalCritic`이 *optional* `action_pressure_map`을 받으면 *pressure-action alignment*를 측정한다. cycle 16 engine → cycle 20 CLI → cycle 22 demo의 3단계 L82 evolution 결과.

Peter passion vocabulary map: [`tests/fixtures/rubric_demo/peter_action_pressure_map.json`](../../../tests/fixtures/rubric_demo/peter_action_pressure_map.json) (`_meta` block에 calibration_status 명시).

3 fixture를 동일 map으로 평가한 결과:

| Fixture | discovery_class | pressure_action_alignment | aligned / misaligned | 해석 |
|---|---|---|---|---|
| `peter_meaningful_novel` → `alignment_meaningful_novel.json/md` | character_consistent_novel_candidate ✨ | **1.000** | 10 / 0 | 모든 action이 적절한 압력에서 자연스럽게 설명됨 |
| `peter_synthetic_trace` → `alignment_synthetic_trace.json/md` | canon_compatible_character_drift | **1.000** | 12 / 0 | 모든 action이 정렬, 단지 novelty band가 copy band |
| `peter_noise` → `alignment_noise.json/md` | not_discovery_noise | **0.750** | 3 / 1 | 1개 action이 압력 elevated 없이 발생 — alignment 약함 |

**핵심 관찰** — `pressure_action_alignment`은 `discovery_class` 결정에 *직접* 사용되지 않는다 (현재 default `pressure_action_alignment_min`은 evaluator gate에 강제 적용 안 됨). 그럼에도 alignment 측정값이 *별개 신호*로서 discovery class와 일관 — noise (0.750) < meaningful_novel (1.000). 두 신호의 *독립적 합의*가 cycle 16 측정 신뢰도를 높인다.

재생성 명령:
```bash
python scripts/rubric/run_rubric.py \
    --records tests/fixtures/rubric_demo/peter_meaningful_novel.json \
    --output docs/portfolio/demo_rubric/alignment_meaningful_novel.json \
    --md-report docs/portfolio/demo_rubric/alignment_meaningful_novel.md \
    --vocabulary "follow_closely discuss_with_disciples pray fall_asleep draw_sword flee follow_at_distance deny weep withdraw_in_fear confess run_to_tomb stay_awake assert_loyalty stay_hiding" \
    --reproduction-threshold 3.0 \
    --action-pressure-map tests/fixtures/rubric_demo/peter_action_pressure_map.json
```

---

### Ensemble Visualization (`ensemble_visualization.html`) — Result-11

3 ensembles를 한 페이지로 통합한 self-contained HTML (10.9 KB, 외부 CDN 0):

- **Header**: Non-Claims banner (review §3) + Rule #14 명시
- **3 ensemble cards** (cross_scenario / multi_agent / multi_seed):
  - Headline: `positive_pct%` character_consistent_novel_candidate
  - Overall distribution bar (discovery_class별 색상 — positive=green / canonical=blue / drift=amber / noise=red / incoherent=purple / invalid=dark red / hardcoded=gray)
  - Axis means (5-seed average)
  - Per-context / per-agent / per-seed breakdown table
- **Discovery class 의미** details (8-step flowchart + class별 설명)
- **Result 11단계 진화** details

생성/재생성 명령:
```bash
python scripts/rubric/build_ensemble_html.py \
    --ensembles docs/portfolio/demo_rubric/cross_scenario_ensemble.json \
                docs/portfolio/demo_rubric/multi_agent_ensemble.json \
                docs/portfolio/demo_rubric/multi_seed_ensemble.json \
    --output docs/portfolio/demo_rubric/ensemble_visualization.html
```

→ portfolio 진입 시 *한 visual asset*으로 ensemble 결과 한눈에 확인. Non-Claims + uncalibrated 명시 visual layer 강화 (Phase 3.05 정직성 4 layer 패턴).

---

## 4-variants flowchart 시연 (review §2.2 P0 입증)

Rubric의 *flowchart 순서* (Step 1-8)가 trajectory별로 어떻게 작동하는지:

```text
Step 1: hardcoded?           → (모두 not hardcoded)
Step 2: hard violation?      → (모두 canon valid)
Step 3: causal smoothness?   → peter_incoherent FAIL → NOT_DISCOVERY_INCOHERENT (review §2.2 P0)
Step 4: context_break rate?  → (4 fixture 모두 PASS, event_in 정렬 후)
Step 5: novelty.band noise?  → (모두 not noise)
Step 6: canon reproducing?   → peter_canonical_reproduction PASS → CANONICAL_REPRODUCTION
Step 7: novelty meaningful + character + scene? → (3 fixture 모두 미달)
Step 8: fallback             → synthetic + novel_candidate → CANON_COMPATIBLE_CHARACTER_DRIFT
```

→ Rubric의 P0 신규 *causal gate* (Step 3)와 *CANDIDATE labels* (Step 7+8)이 portfolio deployed artifact로 *실제 작동* 입증됨.

---

## 기본 demo 상세 (Trajectory 1)

### 분류 justification

```text
Step 4: context_break.rate=0.250 (afford=2, scene=0, motive=1) → §4.2 NOISE
```

→ Rubric은 이 trajectory를 **NOT_DISCOVERY_NOISE**로 분류. 이유:
- canon hard violations 0 (정경 위반 아님)
- causal gate 통과 (인과 설명 가능)
- character signature 통과 (베드로-like trait)
- 그러나 **context_break rate가 임계 초과** — 몇 개 action이 scene affordance와 안 맞음

**해석**: 이 trajectory는 *정경 위반은 아니지만 context coherence가 약함* → discovery 후보 자격 미달.

### Sub-report 상세

| Axis | 핵심 지표 | 값 | 판정 |
|---|---|---|---|
| **Character** | passed_minimum_signature / composite | True / 1.000 | ✓ pass |
| **Canon** | hard_violations / soft_drift / soft_compat | 0 / 7.0 / 0.30 | ✓ hard pass, soft drift |
| **Causal** | explained_transition_ratio / smoothness | 0.909 / high | ✓ gate pass |
| **Novelty** | band / structured_deviation / changed_axes | copy / 0.000 / [action_diversity] | copy band |
| **Scene Response** | fit_rate | (medium) | partial |
| **Context Break** | break_rate / is_coherent | 0.250 / False | ✗ noise gate |

---

## 사용 절차 (재현 가능)

```bash
python scripts/rubric/run_rubric.py \
    --records tests/fixtures/rubric_demo/peter_synthetic_trace.json \
    --output docs/portfolio/demo_rubric/rubric_report.json \
    --md-report docs/portfolio/demo_rubric/rubric_report.md \
    --canonical-sequence '[[1, "follow_closely"], [3, "pray"], [4, "fall_asleep"], [5, "draw_sword"], [8, "deny"], [9, "weep"], [12, "confess"]]' \
    --vocabulary "follow_closely discuss_with_disciples pray fall_asleep draw_sword flee follow_at_distance deny weep withdraw_in_fear confess run_to_tomb stay_awake assert_loyalty stay_hiding" \
    --reproduction-threshold 3.0
```

---

## Calibration Status

```yaml
character_critic:
  relation_stability_min: 0.5
  identity_retention_min: 0.5
  recovery_plausibility_min: 0.3
  calibration_status: uncalibrated_phase3_placeholder

causal_critic:
  explained_transition_min: 0.7
  smoothness_min: 0.4
  calibration_status: uncalibrated_phase3_placeholder

canon_critic:
  reproduction_threshold: 3.0  (this run)
  soft_drift_max: 10.0
  calibration_status: uncalibrated_phase3_placeholder

novelty_critic:
  meaningful_low / meaningful_high: 기본값
  calibration_status: uncalibrated_phase3_placeholder

rubric_evaluator:
  character_min_composite: 0.5
  scene_fit_min: 0.5
  causal_smoothness_min: 0.4
  calibration_status: uncalibrated_phase3_placeholder
```

**모든 threshold는 placeholder.** 실제 Peter trajectory ensemble을 수집한 후 calibration phase (Phase 5+)에서 보정.

---

## Rule #14 Compliance

이 demo는 다음 원칙을 준수한다:

- Rubric은 **evaluation-only** — 학습 loss로 사용되지 않음
- Neural trainer가 `from engine.rubric` import 0건 (test로 강제 검증)
- Scalar 합산 0 — discovery class는 4 critic의 *flowchart* 결과이지 단일 점수 아님
- Final label은 **CANDIDATE class** (review §2.1) — 정식 명칭에 _CANDIDATE / _CHARACTER_DRIFT suffix

---

## 관련 문서

- [docs/witness_rubric_design.md](../../witness_rubric_design.md) — 4-Axis Candidate Classifier 설계 + Acceptance §7
- [docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](../../WITNESS_V3_RUBRIC_DESIGN_REVIEW.md) — review (Phase 3.05) + directive draft
- `scripts/rubric/run_rubric.py` — CLI 진입점 (records → RubricReport JSON + markdown)
- `scripts/rubric/trace_to_records.py` — demo_v07 trace JSONL → rubric records (Result-7 e2e adapter)
- `scripts/rubric/build_ensemble_html.py` — 3 ensemble JSON → self-contained HTML (Result-11 visualization)
- `tests/test_rubric/test_rubric.py` — 100 tests collected (Phase 3.05 P0/P1/P2 + Result-1~11 cycle coverage)
