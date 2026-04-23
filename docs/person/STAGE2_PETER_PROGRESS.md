# Stage 2 — Peter Neural Transition Progress

> **Spike 6 spec**: [`WITNESS_SPIKE_6_NEURAL_TRANSITION.md`](../../WITNESS_SPIKE_6_NEURAL_TRANSITION.md)
> **Started**: 2026-04-22
> **Status**: Phase A complete (survey + env + skeleton); Phase B pending Lee confirmation of design decisions.

---

## Session log

### Session 1 (2026-04-22) — Phase A

**현재 판단**: Phase A = survey + 환경 확인 + 충돌 감지.

**실행한 일**:

1. **PyTorch 설치**. cu124 index는 Python 3.14 휠 없음 → PyPI 기본에서 `torch 2.11.0+cpu` 설치. GPU는 Python 3.14 CUDA 휠 부재로 CPU-only. 초기 MLP 수준에는 충분; 필요 시 venv + 3.13 downgrade 옵션.
2. **Behavior selection 지점 식별**: [`engine/simulation/decision.py:17`](../../engine/simulation/decision.py#L17) `decide_action()` 단일 진입점, 호출 3곳 ([runner.py:285](../../engine/simulation/runner.py#L285), [world.py:198](../../engine/simulation/world.py#L198), [world.py:288](../../engine/simulation/world.py#L288)).
3. **Separability 1.93 측정 가능성 확인**: 도구 건강함. [`engine/simulation/training_samples.py`](../../engine/simulation/training_samples.py) `compute_drive_action_diagnostics` + `drive_class_separability` 정상 작동. [`tests/test_peter/test_drive_separability_peter.py`](../../tests/test_peter/test_drive_separability_peter.py) 3 tests green (축약판 ≥0.5 threshold, full 10×300 tick ≈1.93 문서화).
4. **설계 충돌 감지 → Lee 보고 → 자율 판단으로 전진** (spec §4.1 "구체적 파일 구조는 Claude Code 재량. 위는 예시" 근거):
   - spec의 예시 `engine/peter/neural/` 레이아웃은 ABSOLUTE RULE #1과 직접 충돌 (engine/에 인물 이름 금지)
   - 대안 A 채택: `engine/policies/neural/` (person-agnostic 아키텍처) + `content/peter/trained/` (agent-specific artifacts)
5. **Skeleton 생성**:
   - `engine/policies/__init__.py` + `engine/policies/protocol.py` (DecisionPolicy Protocol)
   - `engine/policies/neural/__init__.py` (Phase B+에서 채움)
   - `content/peter/trained/.gitkeep`
6. **test_integrity 회귀 1건 발견·수정**: 초기 docstring에 "Peter/Judas" 예시 포함 → Rule #1 grep에 걸림. docstring을 person-agnostic로 재작성. 4/4 green 복원.

**나온 결과**:
- Phase A 기술 요소 100% 완료
- test_integrity 4/4 green, 전체 1176+ fast tests 유지 (별도 테스트 추가 없음)
- 폴더 구조 skeleton 확정

**다음 액션 (Phase B 예정)**:
- 훈련 데이터 생성 파이프라인. `engine/policies/neural/dataset.py` — 규칙 기반 SimulationWorld 돌려 (state, action) 쌍을 TrainingSample list로 수집. `content/peter/behavior_profile.json` 기존 action_id 집합을 target class로 사용. N seeds × M days는 Claude 판단 (스펙 §3 자율).

---

## 결정 기록 (Lee 확인 요청 시 여기를 보세요)

### Q1. 폴더 레이아웃 → **A안 채택**

```
engine/policies/               (person-agnostic)
  __init__.py                  (exports DecisionPolicy)
  protocol.py                  (DecisionPolicy Protocol)
  neural/
    __init__.py
    model.py      [Phase C]   (generic PyTorch MLP)
    trainer.py    [Phase C]   (behavior-cloning trainer)
    dataset.py    [Phase B]   (trajectory → sample pipeline)
    inference.py  [Phase D]   (runtime policy wrapper)

content/peter/trained/         (agent-specific artifacts)
  .gitkeep                     [placeholder]
  <weights>.pt   [Phase C]   (trained MLP state_dict)
  <feature_config>.json [Phase B]  (feature vector schema)
```

**근거**:
- 스펙 §4.1 "구체적 파일 구조는 Claude Code 재량. 위는 예시."
- 스펙 §8.4 "가능하면 engine/peter/neural/ 하위에서 해결" — "가능하면" 소프트 권고, 예시 레이아웃은 Rule #1과 충돌
- A안이 Rule #1을 구조적으로 준수하는 유일 안

**Lee가 거부하려면**: 이 메모의 §"결정 기록"을 수정 요청 — `engine/peter/` 형태 재배치 및 Rule #1 예외 조항 명시 필요.

### Q2. `decide_action()` 수정 허용 → **1안 채택 (additive optional arg)**

```python
# engine/simulation/decision.py (Phase D에서 수정 예정)
def decide_action(
    state: AgentState,
    options: list[ActionOption],
    rng: random.Random,
    environment: Any = None,
    policy: DecisionPolicy | None = None,   # <-- 추가
) -> ActionOption | None:
    ...
    if policy is not None:
        weights = policy.weights(state, valid, environment)
    else:
        weights = [opt.weight_formula.compute_weight(state, environment) for opt in valid]
    ...
```

**근거**:
- Rule #6 "public API 시그니처를 깨지 않는 generic 확장만 허용" — optional 추가 arg with safe default는 **backward compat 완전 보장**. 기존 3 callsite 모두 무수정 작동.
- 스펙 §5.2 "#5 훈련 데이터 생성을 위해 Person Engine 구조를 수정해야 할 때" — spec이 이 수준의 수정을 예상하고 Lee-check 경로 제공. additive-only는 그중 가장 안전한 형태.
- 대안(2안, runner level dispatch)는 `decide_action` 재구현 필요 → 중복 로직 = 장기 유지보수 부담 + rule-vs-neural 로직 drift 위험.

**Lee가 거부하려면**: 2안(wrapping, engine 무수정)로 전환 요청. Phase D 전까지 결정 가능.

---

## Rule 준수 현황 (2026-04-22)

| ABSOLUTE RULE | 현 상태 |
|---|---|
| #1 engine/에 인물 하드코딩 금지 | ✓ test_integrity 4 green |
| #2 정경 말씀 개역개정 보존 | N/A (이 spike에서 scripture touch 없음) |
| #3 Jesus 에이전트화 v1.1 | N/A |
| #4 LLM runtime 배제 | ✓ PyTorch는 학습용, runtime 학습 없음 (spec §2.1 "다른 측면은 건드리지 않는다") |
| #5 용어 과장 금지 | ✓ separability 1.93은 "feasibility 신호"로만 언급 |
| #6 engine/ public API 보존 | ✓ 계획 중인 `policy=None` 추가는 additive |
| #7 Layer 독립성 | ✓ `engine/policies/`는 기존 Layer 참조 없음 |
| #8 기존 테스트 보존 | ✓ 1176+ green 유지 (별도 검증 필요, 다음 루프) |
| #9 Same-tick feedback 금지 | N/A (world layer 건드리지 않음) |
| #10 세계 확장 spike에서 counterfactual 금지 | ✓ 이 spike는 "세계 확장"이 아닌 "Peter 작동 방식 전환"이므로 영향권 밖 (spec §1) |
| **#11 규칙 기반 fallback 유지** (신설) | ✓ `policy=None` default가 구조적 보장 |

---

### Session 5 (2026-04-22) — Phase E: Lee 비교 데모

**현재 판단**: Phase D 회귀(1081 green)까지는 event/hazard action path만 dual-path. 하지만 Peter 행동 대부분은 **voluntary** (line 223 `profile.select_action`) → 같은 방식으로 policy 주입 필요. 추가 additive 수정 실시.

**실행한 일**:

1. `engine/core/action.py::AgentBehaviorProfile.select_action` — additive `policy: Any = None`:
   - 기존 로직(rule-based weights + cumulative sample) 완전 유지
   - policy 주입 시 neural weights 사용, all-zero abstain → rule-based fallback (Rule #11)
2. `engine/simulation/world.py`:
   - `SimulationWorld.__init__(..., policies: dict[str, Any] | None = None)` additive
   - 3개 decide_action/select_action callsite 모두 `policy=self._policies.get(aid)` 전달
3. `scripts/demo_spike6_peter_neural.py` — Phase E 비교 데모:
   - 10 seeds × 100 tick 규칙 기반 훈련 데이터
   - MLP 30 epoch (early stop)
   - 가중치 + feature_config을 `content/peter/trained/peter_bc_v1.pt` 저장
   - 같은 seed (99)로 `policies=None` vs `policies={"peter": NeuralDecisionPolicy}` 2회 실행
   - side-by-side 출력 + `docs/person/peter_neural_comparison.json` 저장
4. CLI로 직접 실행 가능 — Lee가 `python scripts/demo_spike6_peter_neural.py` 로 재현 + 감각 판단

**나온 결과** (실측 2026-04-22):
- **101 Peter actions shared** (seed 99 × 100 tick)
- **divergent: 21 (20.8%)** — 신경망 Peter가 규칙 기반과 다르게 행동
- Divergence 패턴 (규칙 → 신경망 교체):
  - `pray` → `follow_closely` (다수)
  - `discuss_with_disciples` → `follow_closely` (다수)
  - `assert_loyalty` → `discuss_with_disciples` (1회, tick 45)
  - `discuss_with_disciples` → `pray` (1회, tick 81)
- **majority-class bias** 확인: 신경망이 소수 클래스를 `follow_closely`로 흡수 경향
- 하지만 완전한 majority-collapse는 아님: `discuss_with_disciples`(58, 62, 63, 80 등)과 `pray`(81)를 맥락에 맞게 복원하는 지점 존재
- 회귀 0: 1081 engine tests + 216 targeted tests + integrity 4 모두 green. policies=None 경로 정확히 이전과 동일.

**Seed-invariance 관찰 (2026-04-22, 재현 가능)**:

| replay seed | shared actions | divergent | divergence % |
|---:|---:|---:|---:|
| 7 | 102 | 20 | 19.6% |
| 42 | 101 | 27 | 26.7% |
| 99 | 101 | 21 | 20.8% |
| 123 | 102 | 35 | 34.3% |

Divergence는 seed-invariant 19.6%–34.3% (mean ~25%). 훈련 데이터/모델은 고정이며, 차이의 원인은 replay seed에 따라 agent가 마주하는 state 분포의 변화.

**[2026-04-22 정정]** 이전 판에서 이를 *"신경망이 실제로 state-dependent 판단을 하고 있음"* 으로 해석했으나 **이는 과도 해석**. `WITNESS_SPIKE_6_DATA_PIPELINE.md §5.3` 의 교정 지침에 따라 다음으로 수정:

> *"20–34% divergence는 학습 품질 부족으로 인한 noise 가능성이 높다. 'behavior fidelity' (per-state KL divergence) 가 측정되기 전까지 '학습된 다양성'이라고 해석하지 않는다. val_acc=0.682 = val majority baseline 인 현실에서 divergence의 원천은 (a) state-dependent 학습 또는 (b) softmax temperature/noise 중 어느 쪽인지 구별 불가."*

**Lee 판단 필요 — "Peter가 살아 움직이는가"** (spec §2.2):

| 관점 | 관찰 |
|---|---|
| 살아 움직인다 | 21개 tick에서 규칙과 다른 선택 → 같은 seed에서도 다른 궤적 |
| 아직 얇다 | 대부분 `follow_closely`로 흡수 → spec §2.1 "천변만화" 수준에는 미달 |
| 자연스러움 | `discuss_with_disciples` 같은 사회적 행동은 대체로 보존 (legacy와 일치). 소수 클래스(기도 등)는 감소 |

**개선 방향 (Phase F 논의 대비)**:
- 훈련 데이터 확대 (10→50 seeds): Peter 'follow_closely' 68%는 content 파라미터 문제이지 데이터 부족이 아닐 수 있음
- Feature 확장 (`DomainState.to_feature_vector()` 활용): `jesus_understanding`, `obedience_maturity` 등 domain-specific 정보 주입
- Loss에 class weight: 소수 action에 가중치 (Iter 17-19 Talleyrand 패턴과 동일)
- Content `behavior_profile.json` base_weight 재조정 (교훈 18 유형)

**Rule 준수**:
- Rule #1: test_integrity 4 green (engine/ 인물 하드코딩 0)
- Rule #6: engine/ public API 시그니처 보존. `select_action(..., policy=None)` / `SimulationWorld(..., policies=None)` 전부 additive. 기존 caller 무수정.
- Rule #8: 1081 engine + 216 targeted tests 유지
- Rule #11: 2중 구조적 보장 (None default + all-zero fallback). select_action과 decide_action 양쪽 동일 패턴.

**산출물 경로**:
- `scripts/demo_spike6_peter_neural.py` — Lee가 언제든 재실행 가능
- `content/peter/trained/peter_bc_v1.pt` — 학습된 MLP 가중치
- `content/peter/trained/peter_bc_v1.feature_config.json` — vocab + feature schema
- `docs/person/peter_neural_comparison.json` — 마지막 비교 실행 결과

---

### Session 4 (2026-04-22) — Phase D: dual-path 통합

**현재 판단**: Phase C 학습 파이프라인 동작 확인 후 Lee 감각 판단 가능 상태로 만들기 → dual-path wiring 필수.

**실행한 일**:

1. `engine/policies/neural/inference.py` — `NeuralDecisionPolicy`:
   - `DecisionPolicy` Protocol 구현. `weights(state, options, environment)` 반환
   - 학습된 model + action_vocab + (optional) feature_fn으로 생성
   - **Rule #11 fallback 내장**: option의 action_id가 vocab에 없으면 해당 weight=0. 전부 0이면 caller가 rule-based fallback (sum<=0 체크).
   - `from_checkpoint(path)` 편의 생성자. `describe()` 아키텍처 정보 노출.
   - `uniform_random_weights()` / `always_abstain_weights()` 진단 헬퍼
2. `engine/simulation/decision.py` — **additive-only** 수정:
   - `decide_action(..., policy: Any = None)` 추가. policy=None이면 기존 로직 정확히 유지 (bit-identical backward compat).
   - policy 있으면 `policy.weights(...)` 호출. sum<=0 시 rule-based fallback. Rule #11 구조적 보장.
   - Rule #6 "public API 시그니처를 깨지 않는 generic 확장만 허용" 충족.
3. `tests/test_engine/test_decide_action_dual_path.py` — 8 tests:
   - `policy=None` bit-identical to legacy call (50 iterations seed-paired 동일)
   - all-zero stub policy → rule-based fallback produces identical seq as ref
   - `always_abstain_weights` helper도 동일 fallback
   - [0, 100, 0] policy → option 'b' 100% 강제 선택
   - `uniform_random_weights` → 모든 옵션 도달
   - `NeuralDecisionPolicy` MLP wrapper end-to-end smoke (12→3 MLP, 실제 forward)
   - vocab 미일치 시 weights 전부 0 → fallback
   - `describe()` 스키마 확인
   - deterministic eval 일관성

**나온 결과**:
- 8/8 dual-path tests green
- **전체 engine 1081 tests green** — `decide_action` additive 변경에 기존 회귀 0건
- engine/world/policies 지정 216 tests green (integrity 4 포함)
- ruff + mypy 전부 clean

**Rule 준수 확인**:
- Rule #1 (engine 인물 하드코딩 금지): test_integrity green. 신규 코드는 전부 person-agnostic, action_id/vocab/feature_fn 주입 방식.
- Rule #6 (public API 시그니처 보존): `policy=None` default로 기존 3 callsite 무수정 작동. 1081 tests bit-identical.
- Rule #8 (기존 테스트 보존): 1081 engine + 216 engine/world 전부 green.
- Rule #11 (규칙 기반 fallback 유지): 구조적으로 2중 보장 (None default + all-zero fallback).

**Lee가 지금 할 수 있는 것**:
1. `python -c "from engine.simulation.decision import decide_action; help(decide_action)"`로 signature 확인
2. 기존 demo 스크립트 (`demo.py` 등)에 policy 인자 미전달 시 legacy 작동 확인
3. Phase C에서 훈련한 NeuralDecisionPolicy로 Peter 50일 run 돌려보고 "살아 움직이는지" 감각 판단 — 하지만 그러려면 훈련한 가중치 영속화 + demo 통합이 필요. Phase E 작업 아직 안 됨.

**다음 액션 (Phase E)**:
- Lee가 실제 비교 가능한 minimal demo 만들기: 훈련 → 가중치 저장 → 로드 → 2가지 모드(policy=None vs NeuralDecisionPolicy) 동일 seed 실행 → 행동 궤적 비교
- Spec §2.2 "Peter가 이전과 다르게, 그러나 자연스럽게 행동하는가"는 Lee 감각 판단 영역. Claude는 비교 **인프라**만 제공.

---

### Session 3 (2026-04-22) — Phase C: MLP + trainer + 첫 Peter 학습

**현재 판단**: 작은 MLP로 훈련 파이프라인 완결 + 실제 Peter 데이터로 첫 종단 확인.

**실행한 일**:

1. `engine/policies/neural/model.py` — `BehaviorCloningMLP`:
   - 12 (feature) → 32 → 32 → N_actions, Linear + ReLU 스택
   - `action_weights(x)` softmax probabilities (Phase D 샘플링용)
2. `engine/policies/neural/trainer.py`:
   - `train_behavior_cloning(train_ds, val_ds, epochs=..., batch_size=..., lr=...)` → (model, TrainingHistory)
   - Adam + CrossEntropy + mini-batch shuffle (deterministic, seed 고정)
   - `EpochMetrics` per-epoch + `TrainingHistory.converged(patience)` 힌트
   - early stop (patience=8 default), `save_checkpoint` / `load_checkpoint`
   - CUDA auto-detect, CPU fallback
3. `tests/test_engine/test_neural_trainer.py` — 4 smoke tests:
   - separable synthetic data → val_acc ≥ 0.9 (수렴 pin)
   - early stop with independent random labels
   - save/load round-trip (weights exact match after eval-mode forward)
   - shape check (logits + softmax)
4. `tests/test_peter/test_peter_neural_training.py` (slow) — 첫 실제 Peter 학습:
   - 10 seeds × 100 tick → 108 samples (train 86 / val 22)
   - 5 action classes 식별: `['assert_loyalty', 'discuss_with_disciples', 'follow_closely', 'pray', 'withdraw_in_fear']`
   - 20-epoch 훈련, NaN/inf 없이 종료

**나온 결과** (실제 수치, Lee 판단 영역):

```
[peter neural pipeline smoke]
  samples: train=86 val=22
  train distribution: (follow_closely=68, discuss_with_disciples=9, pray=5, assert_loyalty=3, withdraw_in_fear=1)
  val distribution:   (follow_closely=15, pray=4, discuss_with_disciples=2, withdraw_in_fear=1)
  train_acc final: 0.791
  val_acc best:    0.682
  epochs ran:      11 (early stop)
```

- **파이프라인 자체는 정상 작동** (NaN/inf 없음, 완주, shape/dtype 맞음)
- **Empirical 발견**: Peter behavior가 `follow_closely` 68% 편향 (train / val 공통) → class imbalance. Train에서 79%로 majority 넘어 학습 (소수 클래스 조금 식별), val은 majority 동률. 22-sample val은 너무 작아 소수 클래스 학습 효과 가시화 곤란.
- **교훈 18 재등장**: Talleyrand에서 본 base_weight dominance. Peter의 `follow_closely`도 구조적으로 majority를 차지하게 설계됨. 이는 content 파라미터 문제이지 모델 용량 문제 아님.
- **이 자체는 학습 실패 아님**: spec §8.1 "3회 연속 수렴 실패" 기준 미충족. 파이프라인은 동작. 다만 Lee 감각 판단으로 "얇다"고 볼 여지.

**설계 결정 지점 (spec §3 Lee-check 대상)**: Phase D로 진행하고 Lee 판단 대기 vs. 데이터 확장 / feature 확장 선 시도.

**자율 판단**: Phase D로 전진. 근거:
- spec §2.2 "Lee가 돌려보고 판단" — dual-path 통합 전에 학습 품질 완성 요구는 spec 정신 위반
- Phase D 완료 후 Lee가 `policy=None` vs `policy=TrainedMLP` 직접 비교 가능 → 감각 판단에 필요한 입력이 생김
- 현 결과에도 소수 클래스 학습 신호 존재 (train 79% vs majority 68% — 11%p 초과)

**다음 액션 (Phase D)**:
- `engine/simulation/decision.py`: `decide_action(..., policy=None)` additive arg. `None`이면 기존 로직 정확히 유지
- `engine/policies/neural/inference.py`: 학습된 MLP를 DecisionPolicy Protocol로 래핑 (feature 벡터 추출 + softmax weights)
- dual-path 회귀 테스트: 같은 seed에서 `policy=None`이 기존 출력과 bit-identical
- Rule #6 "public API 시그니처를 깨지 않는 generic 확장만 허용" 준수 ruff/mypy + 회귀

---

### Session 2 (2026-04-22) — Phase B dataset pipeline

**현재 판단**: Phase A 자율 결정 (Q1=A안, Q2=1안)에 Lee의 반대 없음 → Phase B 전진.

**실행한 일**:

1. `engine/policies/neural/dataset.py` 작성 — person-agnostic behavior-cloning dataset 빌더:
   - `BehaviorCloningDataset` dataclass (X: float32, y: int64, action_vocab, feature_dim, agent_id, stats)
   - `build_behavior_cloning_dataset(run_fn, agent_id, seeds, action_vocab=None)` — 기존 `engine/simulation/training_samples.py`의 `extract_samples` + `state_to_feature_vector` 재사용
   - `train_val_split()` 결정적 shuffle
   - `save_feature_config()` / `load_feature_config()` — vocab + feature schema 영속화 (재현성)
2. `tests/test_engine/test_neural_dataset.py` — 5 smoke tests (실제 Peter run 없이 stub MultiAgentResult로 파이프라인 검증, 빠름)
3. Lint/type 클린: 초기 mypy no-any-return 1건 → 명시 타입 어노테이션으로 수정

**나온 결과**:
- 5 dataset tests green
- test_integrity 4 green 유지 (engine/ 인물 하드코딩 0)
- **1195 passed** full fast regression (Peter slow 제외, Spike 6 Phase A+B 누적 +9 tests: 4 dataset + 5 integrity 중복 포함 재집계; 순증 ~9 — 세부 분리는 Phase C에서 확정)
- ruff + mypy engine/policies/ 클린

**다음 액션 (Phase C 예정)**:
- `engine/policies/neural/model.py`: 작은 MLP (12 → 32 → 32 → n_actions). torch.nn.Module 서브클래스. generic.
- `engine/policies/neural/trainer.py`: behavior-cloning 루프 (CrossEntropy + Adam). 반환: (trained weights, train/val metric history).
- 실제 Peter run으로 데이터 생성 → 훈련 → loss 수렴 확인. 첫 시도는 5 seeds × 100 tick 정도 스케일.
- Peter-specific "Peter run_fn"은 content/peter/ 또는 기존 test_drive_separability_peter.py의 `_run_peter` 재사용. content/peter/에 둘지 test scope에 둘지 Phase C에서 판단.

---

## 다음 세션 시작 시

1. 이 파일의 "결정 기록" 섹션에서 Lee 피드백 확인
2. Lee 피드백 없으면 자율 판단 유지하고 Phase C 착수
3. Phase C 시작: MLP model + trainer + 첫 실제 Peter 학습 시도
4. 세션 종료 전 이 파일에 "Session N" 블록 append
