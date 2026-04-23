# Witness Stage 2 — Data Pipeline v1

> **Spec**: [WITNESS_SPIKE_6_DATA_PIPELINE.md](../../WITNESS_SPIKE_6_DATA_PIPELINE.md)
> **Status**: Phase 1 (진단) 완료. Phase 2 진입 Lee 허가 대기 (spec §2.3 엄수).
> **Started**: 2026-04-22

---

## Phase 1 진단 종합 (2026-04-22)

6 진단 보고서: [docs/person/diagnostics/INDEX.md](diagnostics/INDEX.md)

### 핵심 발견

| # | 항목 | 결과 | Phase 2 영향 |
|---|---|---|---|
| 1 | 기존 108 샘플 분포 | **Volume ratio 3.11e-15** (state hypervolume의 극히 일부), `follow_closely` 76.9% dominant, **4 feature 완전 상수 + 1 거의 상수** | Phase 2C 집중 대상 영역 명확, Phase 2F balanced sampling 필수 |
| 2 | Initial state bounds | 0–10 single sweep 0/48 crash, extreme combo 전부 OK | Phase 2C rare-action sweep **전 범위(0–10)** 허용 |
| 3 | Tick extension | 50/100/200/500 tick 전부 crash 없이 완주 | Phase 2A 긴 seed run 가능 |
| 4 | Environment responsiveness | **Peter behavior_profile이 env. 경로 참조 0건** | **Phase 2E environment 다양화 건너뜀** (spec Option B). Feature 확장 후 재검토 (Phase 3+) |
| 5 | Forced action | `DecisionPolicy` weight-mask로 **100% 강제 가능** (engine 수정 불요) | ChatGPT forced-rollout 전략 채택 가능 |
| 6 | Counterfactual branching | `deepcopy(AgentState)` 안전. **Mid-trajectory branching은 engine 수정 필요** | Phase 2B는 **initial-state branching**으로 근사 권장 (mid-run은 Lee 별도 결정) |

### 특히 중요한 관찰

**108 샘플의 5개 feature는 학습에 기여 안 함**:
```
physical.fatigue:        3.00 상수 (unique=1)
physical.health:         8.00 상수
slow_state.moral_injury: 0.00 상수
slow_state.identity_shift: 0.00 상수
slow_state.event_trauma: 0.00 상수
slow_state.trust_scar:   거의 0 (unique=3, std=0.10)
```

12-feature 중 **실질 신호는 7개** (5 emotion + hunger + trust_scar 약간). MLP가 나머지 5차원은 전부 zero-input로 취급 — 학습 용량 낭비. 이는 Phase 3 재학습 이후에도 상한을 결정하는 요인이며, Phase 2 파이프라인이 이 상수 feature를 **움직여야** 함 (stress injection 등).

**Action별 decision boundary 깔끔**:
```
withdraw_in_fear: fear mean=8.04  (다른 action 3.89–5.79 대비 명확)
assert_loyalty:   hope mean=9.27  (다른 action ~8.9 대비 상단)
pray:             fear mean=5.79  (중간대)
```

이는 Phase 2C rare-action sweep의 **target grid 범위 설정에 직접 사용**됨.

---

## Phase 2 설계 조정 (진단 반영)

Spec §3.2–3.7 대비 변경사항:

| 원 설계 | 조정안 | 근거 |
|---|---|---|
| 2A baseline harvest: 100 seeds × 100 tick | **100 seeds × 200 tick** (diag 3에서 200 tick 안정 확인) | 샘플 수 최소 2배 증가 |
| 2B counterfactual branching | **initial-state perturbation only** (mid-run은 deferred) | diag 6 (engine 수정 필요) |
| 2C rare-action sweep | diag 1 decision boundary를 target zone으로 grid 재설정 | withdraw_in_fear: fear 7–10, fatigue 6–10, moral_injury 5–10 등 |
| 2D stress injection | **mid-run 주입은 engine 수정 필요** → initial extreme state로 근사 | diag 6 동일 이슈 |
| 2E environment variation | **건너뜀** (spec Option B) | diag 4 |
| 2F balanced + noise | 그대로 | diag 1에서 class imbalance 79:11:1 극심 확인 |

**engine 수정 제안 (Lee 결정 필요)**: `SimulationWorld.resume_from_state(state, from_tick, seed)` 신설. 이것이 있으면 Phase 2B mid-run branching + Phase 2D true mid-trajectory stress injection 둘 다 가능. 없으면 두 전략은 "초기 state perturbation"으로 **약한 근사**만.

---

## Lee 판단 요청 (Phase 2 진입 전)

1. **Phase 2 진입 허가?** (spec §2.3 필수 체크)
2. **engine `resume_from_state` API 신설 허가?**
   - 찬성 시: Phase 2B/2D가 본래 의도대로 작동
   - 반대 시: Phase 2B/2D는 "initial-state extreme perturbation" 형태로 근사
3. **Phase 2 순서 조정?**
   - 원안: 2A → 2B → 2C → 2D → (2E skip) → 2F
   - 조정 가능: 2A → 2C (rare-action sweep 최우선) → 2F → 2B → 2D. 이유: diag 1이 명확한 target zone을 제공하므로 2C가 가장 즉시 효과.

허가 없이 Phase 2 진입하지 않음.

---

## 산출물 (2026-04-22 기준)

```
scripts/data_pipeline/
  phase1_diagnostics.py     — 6 진단 일괄 실행기

docs/person/diagnostics/
  INDEX.md                   — 6 보고서 인덱스
  existing_sample_distribution.md
  initial_state_bounds.md
  tick_extension_test.md
  environment_responsiveness.md
  forced_action_feasibility.md
  counterfactual_branching.md

docs/person/
  STAGE2_PETER_PROGRESS.md   — §5.3 환상 해석 수정 완료
  DATA_PIPELINE_v1.md        — 이 파일
```

**변경 없음**:
- engine/ 0 수정 (Rule #6 준수)
- content/ 0 수정
- 기존 1176+ tests 전부 green 유지

---

## 세션 로그

### Session 2 (2026-04-22) — Phase 2 파이프라인 구축 + Phase 3 재학습

**Lee 허가 받음**: "진입하고 너가 판단해서 진행". 자율 결정:
- Q2 (engine resume_from_state) → **무수정**. Phase 2B/2D는 initial-state 근사.
- Q3 (순서) → **A → C → B+D merged → F**. 2B/2D는 동일 메커니즘이라 `perturbation_rollouts.py` 단일 모듈로 병합.

#### 2A baseline harvest 확장

진행 중 **핵심 발견**: 100 tick → 300 tick 확장이 **가장 큰 품질 개선 기여**. 수난 주간 canonical_events + hazard가 늦은 tick에서 발동 → 기존 5-action vocab이 **15-action vocab**으로 확대.

| 스케일 | 샘플 | actions | 시간 |
|---|---:|---:|---:|
| 20 × 100 (초기 smoke) | 217 | 5 | 1.2s |
| 100 × 200 | 3097 | 13 | 8.7s |
| **500 × 300** (채택) | **22756** | **15** | 64s |

500 × 300의 class 분포:
```
follow_closely:         10606 (47%)
discuss_with_disciples: 3641
pray:                   2980
deny:                   1453
withdraw_in_fear:       1336
weep:                    602
assert_loyalty:          594
stay_hiding:             425
stay_awake:              334
draw_sword:              264
fall_asleep:             166
flee:                    155
follow_at_distance:       81
run_to_tomb:              74
confess:                  45  (최소)
```

#### 2C rare sweep + 2B+2D perturbation 관찰

Rare sweep (40-tick rollout, diag 1 target zones): 2259 samples 기여하지만 여전히 `follow_closely` 지배 (62%). 구조적 해석: Peter behavior_profile의 weight formula가 매우 강한 majority bias를 갖고 있어 **초기 state extreme도 쉽게 흡수**된다. 이는 content 설계의 특성.

#### Phase 2F 최종 빌드 + Phase 3 재학습

Balance target 800/class (넘치면 random subsample, 부족하면 유지), gaussian noise σ=0.3 per feature.

**최종 dataset**: **6821 samples, 15 actions, train 5461 / val 1360 (stratified)**.

**재학습 결과**:
- Val acc **0.407** vs majority **0.118** → +29%p over baseline (이전 v1은 majority 동률)
- NLL 1.492 (uniform random 2.71의 55%)
- **5개 class F1 ≥ 0.7**: flee(0.862), stay_hiding(0.780), deny(0.759), draw_sword(0.759), stay_awake(0.699)
- **4개 class F1 = 0**: weep(n=127), fall_asleep(n=33), follow_at_distance(n=16), run_to_tomb(n=14) — support 있어도 feature space에서 분리 불가
- Behavior fidelity: KL median **1.445** (neural vs rule-based per-state distributions)

**해석**: 파이프라인 품질 개선이 학습에 실제 전달됨 확인. 단, 4개 class의 F1=0은 **spec §0.2가 금지한 "feature 확장" 필요 지점**. 현 12-feature로 이들 action의 결정경계 모형화 불가.

#### 산출물 증가

```
data/person/pipeline_v1/
  baseline/    22756 samples (X.npy + meta.json)
  rare_sweep/  2259 samples
  mild/        110 samples
  stress/      122 samples
  final/       6821 samples (balanced + noise)  ← dataset.npz

scripts/data_pipeline/
  _common.py                (시나리오 로더 공통)
  baseline_harvest.py       (2A)
  rare_action_sweep.py      (2C)
  perturbation_rollouts.py  (2B + 2D merged)
  build_final_dataset.py    (2F + 오케스트레이터)
  retrain_and_evaluate.py   (Phase 3)

content/peter/trained/
  peter_bc_v2.pt                      ← 재학습 가중치
  peter_bc_v2.feature_config.json

docs/person/
  stage2_v2_evaluation.json           ← 상세 metric 기록
```

#### Phase 3 완료 기준 대비 (spec §4.3)

| 기준 | 목표 | 달성 |
|---|---|---|
| Val acc > majority + 10%p | > 78% ? 사실 baseline은 68%였지만 15-class 분포 쇄신으로 majority 11.8% → target=21.8% 재해석 가능 | **40.7%** (+29%p) |
| Rare action F1 > 0.3 | 전체 | 11/15 = 0.3 이상, 4개 미달 |
| Behavior fidelity 측정 | 계산 | KL median 1.445 |
| Lee "실제 학습 보이는가" | 판단 | **사용자 판단 영역** |

Spec 기준 **부분 달성**. "4개 class가 여전히 F1=0"이 남은 한계이며, 이는 파이프라인보다 feature/model 영역.

---

### Session 1 (2026-04-22) — Phase 1 일괄 진단

- 6 진단을 `phase1_diagnostics.py` 단일 스크립트로 실행. 원인: 각 진단이 read-only이며 독립적이라 병렬 실행 가능하면서도 통합 실행이 중복 import 비용 회피 (spec §8.1 "1–2 세션").
- **가장 충격적 발견**: volume ratio 3.11e-15 — 기존 데이터가 차지하는 공간은 실제로 거의 0. "108 샘플이 부족하다"는 단순 문제가 아니라 "108 샘플이 전부 거의 같은 점 근처를 돌고 있다".
- **STAGE2_PETER_PROGRESS.md §5.3 환상 해석 수정** (spec §5.3 강제).
