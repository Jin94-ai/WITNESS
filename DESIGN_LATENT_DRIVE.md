# v1.0 Latent Drive Bottleneck — Design Sketch

> ChatGPT 5차 리뷰 "E안" 기반. Trajectory VAE 아닌 **predictive bottleneck latent drive model**.
>
> Symbolic event engine은 유지, 그 위에 학습된 latent drive layer 추가.

---

## 1. 아키텍처 개요

```
┌─────────────────────────────────────────────────────────┐
│                  INPUT (per tick, per agent)             │
├─────────────────────────────────────────────────────────┤
│ • current state (physical, emotions, slow_state)         │
│ • relationships (trust, love, awe, understanding)        │
│ • environment context                                     │
│ • recent action history (last k ticks)                   │
│ • recent observed events                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
            ┌─────────────────────────┐
            │   LATENT DRIVE LAYER    │
            │                         │
            │   drive ∈ R^d           │
            │   (d ≈ 3~8 차원)        │
            │                         │
            │   이름: 학습 후 해석     │
            │   (attachment, shame,   │
            │    calling, resentment, │
            │    self-preservation…)  │
            └──────────┬──────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌─────────┐  ┌──────────┐  ┌──────────────┐
    │ Action  │  │ Trigger  │  │ Slow-state   │
    │ Policy  │  │ Suscept. │  │ Update       │
    │         │  │          │  │              │
    │ π(a|s,d)│  │ T(ε|s,d) │  │ slow ←       │
    └─────────┘  └──────────┘  │ f(slow,d)    │
                                └──────────────┘
                       │
                       ▼
            ┌─────────────────────────┐
            │  SYMBOLIC EVENT ENGINE  │
            │  (현행 유지 — v0.5)      │
            │  • Trigger system       │
            │  • Hazard engine        │
            │  • Rule application     │
            └─────────────────────────┘
```

---

## 2. 차원 명세

### 2.1 Latent drive dim = d (3~8 권장)

**초기 권장**: d=5

| 축 후보 | 의미 | Peter 관련 | VG 관련 |
|--------|------|-----------|---------|
| d[0] | attachment / belonging | 제자 공동체 소속 | Gauguin/Theo 연결 |
| d[1] | self_preservation / safety | 체포 공포 | 정신 붕괴 공포 |
| d[2] | shame / moral_injury | 부인 후 수치 | 귀 자해 후 수치 |
| d[3] | calling / meaning_pursuit | 사도적 사명 | 예술적 비전 |
| d[4] | resentment / bitterness | 유다 측면 | Gauguin 측면 |

**주의**: 이 이름은 **사후 해석용 가이드**. 학습 시에는 순서 없는 latent vector만.

### 2.2 입력 차원

| 항목 | 차원 | 비고 |
|------|------|------|
| 현 상태 (physical+emotion+slow_state) | ~12 | fear/hope/grief/fatigue/hunger/health/confusion/love + slow (4~5) |
| 관계 (per target) | 4 × N_relations | trust/love/awe/understanding |
| Domain state | 3~6 | scenario별 |
| Environment | ~5 | surveillance, crowd_pressure 등 |
| Recent action history | k=10 × action_dim | k 이전 행동 one-hot |
| **총 입력 차원** | **~50-80** | agent별 |

### 2.3 출력

**Action policy π(a|s, d)**:
- d 차원 latent + state → action probability distribution over behavior primitives
- 기존 behavior_profile weights 대체

**Trigger susceptibility T(ε|s, d)**:
- d → trigger threshold 조정 (fixed threshold 대체)
- 예: d[shame] 높음 → "withdraw" action이 "inform_authorities" trigger로 이어지는 민감도 상승

**Slow-state update**:
- d → slow_state (moral_injury, identity_shift, trust_scar) 변화율
- 기존 rule 기반 slow update를 drive-modulated로

---

## 3. 학습 방식

### 3.1 Predictive bottleneck (핵심 구조)

```
Encoder(state + history) → d (latent)
Decoder(d, state) → next_action, next_event_type, next_state

Loss = α * action_prediction_loss
     + β * event_prediction_loss
     + γ * state_continuity_loss
     + δ * trigger_susceptibility_loss
     + λ * KL(d || prior)  // regularization
```

### 3.2 학습 데이터

**Phase 1 (v1.0 초기)**: 현 symbolic simulator가 생성한 trajectory N=10,000+
- (state_t, action_t, event_t, state_{t+1}) tuples
- Peter 시나리오 전용

**Phase 2**: VG 시나리오 추가 → cross-scenario transfer 테스트

**Phase 3 (v1.3)**: 실제 historical 기록 (성경, 반 고흐 편지)을 expert trajectory로 → preference mixture inference

### 3.3 Loss 설계 주의

**피해야 할 함정** (ChatGPT 리뷰):
- "역사적 정답과의 매칭" 을 단일 reward로 쓰면 memorization
- "POM all-pass" 를 reward로 쓰면 현재 규칙에 과적합

**추천 loss 조합**:
1. **Action/Event 예측 정확도** (supervised, trajectory가 expert)
2. **Slow state continuity** (비가역성 보존)
3. **KL divergence** (latent drive 분포 regularization)
4. **POM는 validation only** (training loss 아님)

---

## 4. 기존 엔진과의 통합

### 4.1 변경 사항

| 구성 요소 | v0.5 | v1.0 |
|-----------|------|------|
| `AgentState` | emotion, physical, slow, domain | + `drive: np.ndarray[d]` 필드 |
| `behavior_profile.json` | action weights (hardcoded) | **deprecated** → π(a|s,d)로 대체 |
| `Trigger.state_conditions` | fixed thresholds | **modulated** by drive susceptibility |
| `Rule.apply()` | state → state' | drive가 update 강도 조절 |
| `SimulationWorld.tick()` | 기존 loop | + latent drive update step 삽입 |

### 4.2 새 구성 요소

```python
# engine/core/latent_drive.py (새 파일)
class LatentDriveModel:
    """Predictive bottleneck drive model."""

    def encode(self, state: AgentState, history: list[ActionRecord]) -> np.ndarray:
        """state + history → latent drive vector d."""

    def action_policy(self, state: AgentState, drive: np.ndarray) -> dict[str, float]:
        """drive-modulated action weights."""

    def trigger_susceptibility(
        self, state: AgentState, drive: np.ndarray, trigger: Trigger
    ) -> float:
        """drive → trigger threshold multiplier."""

    def slow_state_update(
        self, slow: SlowState, drive: np.ndarray
    ) -> SlowState:
        """drive-modulated slow state evolution."""
```

### 4.3 학습 파이프라인

```python
# engine/simulation/drive_training.py (새 파일)
def collect_trajectories(n_runs: int) -> list[Trajectory]:
    """현 simulator로 trajectory 수집."""

def train_drive_model(trajectories: list[Trajectory], d: int = 5) -> LatentDriveModel:
    """predictive bottleneck 학습."""

def validate_drive_model(model: LatentDriveModel) -> ValidationReport:
    """기존 POM/counterfactual/checkpoint로 검증."""
```

---

## 5. 검증 전략 (v0.5 framework 재사용)

### 5.1 필수 통과 기준

학습된 모델도 v0.5의 검증 프레임워크를 통과해야 한다:

| 검증 | 기준 | 이유 |
|------|------|------|
| POM all_pass rate | >= 40% (n=40) | 인물 구조 보존 |
| Counterfactual (Judas removal) | spontaneous 0% | 인과 비대칭 보존 |
| Event-relative checkpoint | >= 70% match | emergent timing 유지 |
| Explanation faithfulness | Spearman ρ >= 0.8 | 설명 일관성 |
| Peter triple_denial rate | >= 80% | 정경 사건 emergence |
| Linear trajectory R² | >= 0.95 | 기본 dynamics 유지 |

### 5.2 새 검증 (drive 모델 특화)

| 검증 | 목적 |
|------|------|
| Drive latent dim 의미 해석 | 각 d[i] 축의 상관 state 변수 (attachment = relationships.love?) |
| Drive trajectory smoothness | d(t)가 state보다 더 매끄러운지 (bottleneck 효과) |
| Cross-scenario drive transfer | Peter-trained 모델을 VG에 적용 시 성능 |
| Drive ablation | d[i] = 0으로 고정 시 행동 변화 (각 축 역할) |

---

## 6. Trace 로깅 (v1.0 필수)

[TRACE_SCHEMA.md](TRACE_SCHEMA.md) 스펙 따름. 특히:

```json
{
  "tick": 152,
  "agent": "judas",
  "latent_drive": [0.9, 0.8, 0.3, 0.6, 0.4],
  "action_weights": {"withdraw": 0.43, "inform": 0.32, ...},
  "drive_attribution": {
    "withdraw": {"d[safety]": 0.2, "d[shame]": 0.8},
    "inform": {"d[resentment]": 0.5, "d[self_preservation]": 0.4}
  }
}
```

---

## 7. 구현 단계 (v1.0 세부)

### Stage 1 (월 1-1.5): 인프라
- [ ] `LatentDriveModel` 스켈레톤 클래스
- [ ] `AgentState.drive` 필드 추가 (backward compatible)
- [ ] Trajectory logging 확장 (현 state_snapshots + action_histories 기반)
- [ ] PyTorch/JAX 중 택일 (MLP 수준이라 torch 권장)

### Stage 2 (월 1.5-2.5): 모델 학습
- [ ] 10,000 trajectory 수집 (Peter + VG + Talleyrand 멀티 시나리오)
- [ ] MLP encoder (state → d) + decoder heads
- [ ] Predictive loss 구현
- [ ] 학습 + hyperparameter search (d=3,5,8)

**Stage 2 진입 전 feasibility 증거 (v1.2 Iter 65-70 종합)**:

| Scenario | Random Projection separability | Learned logistic acc vs majority | Stage 2 target? |
|----------|-------------------------------|----------------------------------|-----------------|
| Van Gogh | 6.04 | (high) | **YES** — emotion-driven, learnable |
| Peter | 1.93 | 45.5% vs 12.5% (**3.6×**) | **YES** — state→action 강한 coupling |
| Talleyrand | 0.05-0.07 | 55.1% vs 53.5% (**+1.6%p**) | **Deferred** (Iter 71 결정) |

**Iter 71 결정 (scope 분리)**:
- Talleyrand는 **"engine universality" 증거** 역할 (Iter 57 POM 교차 적용 비대칭성 증명 완료) — 엔진이 이질적 시나리오 타입 수용함을 증명.
- Stage 2 PyTorch 학습의 direct target은 **아님**. 이유 (Iter 69-70 empirical):
  1. 5개 action에 majority class 53.5% → 학습 이득 statistical noise 급
  2. regime 전환 canonical events가 state를 discrete step으로 reset → intra-regime state 변화 작아 classifier signal 약함
  3. behavior_profile 재튜닝(Iter 70)으로 base_weight dominance 해소했지만 한계 도달
- 재튜닝으로 Talleyrand를 Stage 2 target으로 만들려면 content 확장 필요 (7-10 actions + intermediate canonical events). **v1.2.1 이후 작업**으로 분리.

- `engine.simulation.training_samples.drive_class_separability` 로 측정 가능 (Iter 64).
- Peter/VG 같은 **continuous emotion-driven** 시나리오는 12-feature random projection 만으로도 action class 분리 → Stage 2 MLP 학습이 수렴할 여지 확인.
- Talleyrand 같은 **categorical regime-driven** 시나리오는 12-feature 로는 분리 불가 (`state_to_feature_vector` 가 `domain_state` 를 무시).
- feature set 확장 (`DomainState.to_feature_vector` + `state_to_feature_vector_extended`, Iter 67)을 해도 random projection 하에서는 개선 미미 — **learnable weights** 가 필수.

**함의**: Stage 2 PyTorch 구현은 "선택"이 아니라 "시나리오 일반성 확보의 필요조건". Peter/VG 에만 만족하는 모델은 universality 주장 불가.

**Stage 2 학습에 반드시 포함해야 할 feature block**:
1. Base 12: emotions + physical + slow_state (`state_to_feature_vector`)
2. Domain-specific one-hot + scalars (`DomainState.to_feature_vector`; DiplomacyState 예시 = regime 7 + stance 5 + 3 scalars)
3. (선택) 최근 k tick action history (one-hot 시퀀스)

### Stage 3 (월 2.5-3.5): 통합
- [ ] `SimulationWorld` 에 drive update step 삽입
- [ ] `behavior_profile` 대체 (JSON → learned π)
- [ ] Trigger susceptibility 모듈
- [ ] 기존 tests 호환성 유지

### Stage 4 (월 3.5-4): 검증
- [ ] 5.1 필수 통과 기준 테스트
- [ ] 5.2 drive-특화 검증
- [ ] Peter trajectory 재현성 확인
- [ ] Publication-ready 결과 생성

---

## 8. 주요 결정 사항 (미확정)

### 8.1 Framework
- PyTorch (유연, 생태계) vs JAX (빠름, functional)
- **권장**: PyTorch (MLP 수준, 학습 복잡도 낮음, 디버깅 용이)

### 8.2 Drive dim d
- d=3: 해석 쉬움, 표현력 낮음
- d=5: balanced
- d=8: 표현력 높음, overfitting 위험
- **권장**: d=5 초기, ablation으로 최적화

### 8.3 학습 vs 추론 경계
- 학습: offline batch (trajectory 수집 → 모델 업데이트)
- 추론: online (매 tick drive encode → action sample)
- **운영**: 학습된 모델 deploy, 필요시 재학습

### 8.4 Loss weighting
- α (action prediction), β (event prediction), γ (state continuity), δ, λ
- 초기 값: α=1.0, β=1.0, γ=0.5, δ=0.3, λ=0.01
- Validation loss로 ablation

---

## 9. 위험 및 완화

| 위험 | 완화 |
|------|------|
| 학습 모델이 current rules 과적합 | Cross-scenario (VG) 테스트, 3번째 시나리오 추가 |
| Drive latent 해석 불가 | Ablation + 상관 분석 with known state variables |
| POM 기준 실패 | Loss에 POM-aligned term 추가 (단 validation만 강제 아님) |
| 기존 test 호환성 깨짐 | backward compatible drive=None 경로 유지 |
| Overfitting to trajectory 분포 | Regularization KL(d || prior) + 데이터 augmentation |
| 계산 비용 증가 | MLP 수준 유지, 추론 <10ms 목표 |

---

## 10. 성공 기준 (v1.0 완료 = Pass when)

1. ✅ 기존 v0.5 POM/counterfactual/checkpoint 모두 통과
2. ✅ Judas disill r (Spearman) 재현 (유사 값)
3. ✅ Behavioral signal 보존 (withdraw rate leading indicator 유지)
4. ✅ Cross-scenario transfer 부분 성공 (VG POM >= 50% of Peter-trained baseline)
5. ✅ Drive latent 해석 가능 (최소 3축 의미 부여)
6. ✅ Trace schema v1.0 로깅 완료

---

**Next**: 이 스케치 기반으로 [PAPER_OUTLINE_V05.md](PAPER_OUTLINE_V05.md) 마감 후 Stage 1 착수.
