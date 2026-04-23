# lessons — Witness v1.2 세션 (2026-04-19, Iter 20-40)

> 글로벌 CLAUDE.md 원칙에 따라 실수/방향 수정/학습 사항 정리. 다음 세션에서 참고.

---

## 아키텍처 결정에서 얻은 것

### 1. 외부 리뷰어 지적은 먼저 스켈레톤으로 흡수, 구현은 opt-in

Gemini와 ChatGPT 리뷰가 요구한 기능 (Inhibitor Rule, slow state 회복, absolute time) 을 **opt-in zero-default** 형태로 먼저 엔진에 추가했다.

- `SlowStateFieldRecoveryRule`: 모든 rate=0이면 zero-effect → v0.7 레거시 무영향.
- `FieldAttenuationRule`: content가 명시적으로 instantiate 해야 활성.
- `HazardFunction.base_rate_unit`: 기본 per_tick = legacy 완전 보존.

**교훈**: 리뷰가 "반드시 추가"를 말해도 기본 비활성으로 넣으면 legacy 검증이 깨지지 않고, content 실험만 단계적으로 해볼 수 있다. "활성화 여부는 content 결정" 패턴으로 일관되게 설계.

### 2. Legacy 모드와 신 모드의 완전 분리

`phases=None`이면 `PhasedSimulationWorld._run_legacy_mode()`가 기존 `SimulationWorld`에 그대로 위임. 두 경로가 같은 seed에서 **bit-exact** 결과를 낸다 (test_claim_legacy_mode_identical_to_v07에서 증명됨).

**교훈**: v0.7 수치 (arrest 100%, Cohen's d=-6.87 등) 보존이 요구될 때, 신 기능을 기존 코드 경로에 섞지 말고 **분기**하라. 두 모드가 다르게 동작하는 것은 feature이지 bug가 아니다.

### 3. Phase-linked = "표면 연속 / 내부 stitched"

reviewer ChatGPT의 명명을 수용. `PhasedMultiAgentResult`가 `per_phase_results` (stitched 관점)와 `final_states` (연속 관점)를 **둘 다** 노출.

**교훈**: "연속 vs stitched"는 양자택일이 아니다. 같은 run 객체가 두 관점을 모두 제공하면 사용자가 분석 목적에 따라 고를 수 있다.

---

## 테스트/검증에서 얻은 것

### 4. POM-style ensemble validation이 단일 seed보다 강력

Phase 1-4 emergent 패턴은 seed 하나로는 증명 안 됨 (noise 섞인 state_noise_scale). 10-seed 앙상블로 "awe Phase 1 < Phase 3", "obedience 단조 성장" 같은 **평균적 패턴**을 검증하면 noise 있어도 robust.

**교훈**: `@pytest.fixture(scope="module")`로 앙상블 결과 캐싱 → 여러 test class가 같은 결과를 쪼개어 검증 가능 (성능 문제 없음).

### 5. Integration test는 unit test를 대체하지 않는다

Iter 11에서 `test_inhibitor_rules.py` (unit) 작성, Iter 26에서 `test_inhibitor_integration.py` (PhasedSimulationWorld E2E) 작성, Iter 31에서 `test_inhibitor_judas_deployment.py` (content composition) 작성.

각 층이 다른 것을 증명: unit = 로직 정확성, E2E = pipeline 통합, content = 실제 시나리오 의미. **세 계층 모두 필요**.

### 6. Coverage 100%는 목표가 아니라 부수 효과

Iter 36에서 time_axis, inhibitor를 100% 커버로 만들었다. 하지만 `extract_final_states_at_phase_boundaries`의 dead 조건 경로 등은 커버해도 값이 크지 않다. **100%를 목표로 테스트를 쓰면 의미 없는 edge case가 쌓인다**. 반대로, 유의미한 edge를 찾다 보면 커버리지가 자연스럽게 올라간다.

### 7. Floating point equality는 항상 tolerance

`1.2000000000000002 == 1.2` 실패를 여러 번 목격. `abs(x - y) < 1e-6` 또는 `< 1e-9`로 일관되게 비교.

---

## 무엇을 놓쳤다가 나중에 발견했나

### 8. Hazard dt 누락 (Iter 26 → Iter 27)

`engine/simulation/world.py:274`에서 `hazard_engine.evaluate_tick(...)`가 `dt` 기본값(1.0)으로 호출됨. Phase tick_scale=24h일 때 hazard rate가 rescale되지 않아 reviewer가 지적한 "phase-variable tick에서 rate invariance" 원칙이 깨짐.

Iter 26까지는 "나중에 고치자"고 progress.md에 flag만 걸었으나, Iter 27에서 `HazardFunction.base_rate_unit` 추가로 해결. 해결책이 legacy-safe였기 때문에 **flag 건 것을 실제로 해결할 수 있었음**.

**교훈**: flag를 걸 땐 "나중에 어떻게 해결할지" 구체적으로 기록하라. "추후 검토" 같은 모호한 말은 flag 해소를 영구히 미룬다.

### 9. Loop ROI는 Iter 35경부터 체감 감소

Iter 20-32는 reviewer-demanded 아키텍처 작업. Iter 33부터는 테스트/문서 정비 및 edge case 커버. Iter 36-38은 coverage 100% + 문서 정렬. Iter 39는 scale 증명. Iter 40은 attestation.

**Iter 35 이후 각 iteration이 +5~10 테스트 추가**하지만 **새로운 설계 결정은 없다**. 이 시점부터는 "정말 가치 있는가?" 질문에 스스로 엄격해져야 함.

### 10. 빠른 cache-friendly 루프보다 깊은 사고가 나은 순간이 있다

ScheduleWakeup 300s는 user 선호로 고정했지만, 이 주기는 cache warm window 안이어서 각 iteration이 "이전 결과 보고 다음 작은 단위 추가" 패턴이 됨. 그 결과 작업이 **점진적이지만 기계적**으로 됨. 큰 설계 결정 (Iter 23 slow recovery, Iter 27 per_hour)은 그보다 긴 사고 시간이 필요했으며, 짧은 주기의 리듬에서 빠져나와 한 iteration에서 해결.

**교훈**: 루프 주기는 단순한 "반복 빈도"가 아니라 **사고 깊이의 박자**. 때로는 한 iteration을 길게 쓰는 것이 여러 작은 iteration보다 낫다.

---

## 다음 세션에 주의할 것

- **v1.2 체크리스트는 Iter 40에서 종료 선언**. 더 추가하려면 "이게 누구에게 가치가 있나?"를 명시적으로 답하고 시작.
- **legacy v0.7 수치 (arrest 100%, Cohen's d=-6.87, sword_drawn Phi=0.95)는 sacred**. 어떤 신 기능도 이를 변경하면 안 됨. 변경될 것 같으면 legacy mode에 가두기.
- **3번째 시나리오** 추가 시 ABSOLUTE RULE #5 "universality 주장 금지" 해제 가능. 그 전까진 "structural isomorphism" (Peter/VG 2 시나리오)까지만.
- **v1.0 Stage 2 PyTorch encoder**가 다음 큰 작업. `drive_training.py` line 118 TODO가 진입점.

## Iter 41-48 tail phase 반성

v1.2 체크리스트가 끝난 후에도 loop가 계속 요청되어 Iter 41-48을 수행. 실제 가치:

| Iter | 작업 | 솔직한 가치 판단 |
|------|------|-----------------|
| 41 | lessons.md 신규 | 중 (이 문서 자체; 미래 세션 참조 가치) |
| 42 | paper draft v1.2 Appendix D | 중-상 (논문 제출 시 필요) |
| 43 | load_handoff_spec | 중 (content JSON 선언 가능하게) |
| 44 | load_phase | 중 (43의 대칭) |
| 45 | JSON-driven arc test | 저-중 (43+44의 통합 증명) |
| 46 | demo_phased --full-passion | 저-중 (사용자 편의) |
| 47 | phase_hours_table() | 저 (편의 wrapper) |
| 48 | SCENARIO_TEMPLATE §7 phase | 중 (3rd scenario 저자 참고) |

**Pattern**: Iter 42-43-44는 명확한 결핍을 채움. Iter 45-47은 그 위에 쌓인 편의. Iter 48은 다음 작업 지향 문서.

### 교훈 11: Loop 지속 시점 판단법

Iter 40 "release attestation" 이후 각 iteration의 가치가 매번 작아짐. 다음 기준 중 하나라도 맞으면 새 세션으로 넘겨야 함:
- 연속 3 iteration이 모두 "중-저" 가치이면 saturation.
- iteration이 5줄 이하 편의 method 추가만 하면 signal이 약해짐.
- 사용자가 큰 방향 전환을 요청할 때까지는 새 iteration을 시작하지 말고 현재 상태를 honest하게 보고.

이 세션은 Iter 41-48에서 실제로 이 saturation 패턴을 보임. 다음 세션은 "v1.0 Stage 2 시작" 같은 큰 작업으로 진입하기 전까지 loop 재시작하지 말 것.

### 교훈 12: SCHEDULED_WAKEUP_INTERVAL=300s는 cache-miss 구간에서 유효하지 않음

ScheduleWakeup 도구 문서가 300s를 "worst-of-both"로 권고하지만, 사용자가 명시적으로 300초 고정을 원했으므로 존중. 결과적으로 각 iteration이 짧은 사고 단위로 나뉘어 **큰 설계 변경이 아닌 점진적 polish만** 나오게 됨. 다음 세션에서 비슷한 상황이 되면, 사용자에게 "300s 유지할지, 1200s+로 늘릴지, 또는 수동 제어로 전환할지" 다시 물어볼 것.

### 교훈 14: Stage 2 학습 feasibility는 학습 전에 측정 가능 (Iter 64-66)

PyTorch MLP encoder를 구현하기 전에 다음을 묻는 것이 중요:
"현재 feature set + projection이 action class를 구별할 수 있는가?"

**측정 도구** (Iter 64 완성):
- `compute_drive_action_diagnostics(samples, encoder)` → action별 drive mean/std
- `drive_class_separability(diagnostics)` → Fisher-style between/within variance ratio

**3-scenario empirical 결과** (Iter 65-66, 10 seeds):
| 시나리오 | separability | 해석 |
|---------|-------------|------|
| Van Gogh (Arles) | 6.04 | 매우 feasible |
| Peter (passion) | 1.93 | feasible |
| **Talleyrand (50y career)** | **0.05** | **학습 불가 신호** |

**Talleyrand 실패 원인**: `state_to_feature_vector`는 emotions + physical + slow_state 12 필드만 포함. Talleyrand의 action 선택은 `domain_state.current_regime`, `alignment_stance`, `network_depth` 등 Literal/domain-specific 필드에 의존 → 현 feature vector에 이 정보가 없으므로 action class가 drive 공간에서 구분 불가.

**구조적 교훈**: "Engine universality"(Iter 57 증명) ≠ "Feature universality". 엔진은 Talleyrand를 수용하지만, Stage 2 학습은 **per-scenario feature extractor**가 필요. 다음 대안:
1. `state_to_feature_vector`를 agent/scenario별로 override 가능하게 확장
2. domain_state Literal 필드를 one-hot encoding으로 embed
3. relationships/network를 aggregate feature로 추가

이 발견은 `test_cross_scenario_separability.py`에 regression guard로 고정. 만약 미래에 feature set을 확장해서 Talleyrand separability가 0.5를 넘으면 테스트가 실패하여 **lessons.md 업데이트 신호**가 된다.

### 교훈 15: Stage 2 진입 전 **항상** 각 시나리오에 feasibility 측정 실행하라 (Iter 66)

Iter 65에서 Peter separability 1.93 확인 후 "Stage 2 feasible" 판단.
Iter 66에서 Talleyrand 돌리니 0.05. **한 시나리오 측정만으로 feasibility 결론 금지**.

다음 단계(PyTorch 구현)를 시작하기 전 반드시:
1. 모든 active scenario에서 separability 측정
2. 최저 scenario도 ≥ 0.5 이상일 것 (feature universality 검증)
3. 그렇지 못하면 PyTorch 구현 전에 feature extractor 확장 먼저

### 교훈 17: Talleyrand action-predictability 붕괴의 진짜 원인은 feature가 아니라 behavior_profile (Iter 69)

Iter 66-68에서 "feature가 domain_state 무시" 를 원인으로 지목하고 해법 시도. Iter 69에서 learned LogisticRegression 으로 진짜 한계 측정:

| Scenario | Majority baseline | Logit on 12-feature |
|---------|------------------|---------------------|
| Peter | 12.5% | **45.5%** (3.6× chance) |
| Talleyrand | 47.8% | 45.6% (**at or below chance**) |

**진단**: Peter action은 state → action 관계가 강해서 learned linear classifier도 3.6× 이득. Talleyrand는 learned classifier조차 majority 못 이김 → **state 자체가 action을 결정 못 함**.

**원인 (content-level)**: `content/talleyrand/behavior_profile.json`의 `base_weight` 값 (maintain_network=3.0, serve_current_regime=2.5, ...)이 `state_multipliers` scale (0.1~0.2) 대비 압도적. action 선택이 state 변화에 둔감.

**구조적 교훈**: Stage 2 학습의 학습 가능성은
1. feature gap (Iter 66-67) — state가 관련 정보 포함하는가
2. **policy gap (Iter 69)** — action이 그 state에 실제로 민감한가

둘 다 해소되어야 의미 있는 학습 가능. Iter 66-67은 (1)만 측정/수정했지만 (2)는 건드리지 않아 효과 없었음.

**향후 조치**: Talleyrand `behavior_profile.json`을 state-sensitive하게 재작성 (base_weight 감소 or multiplier scale 증가). 다시 측정 → logit acc가 majority를 의미 있게 넘어야 Stage 2 투자 가치 확인.

`test_behavior_profile_state_sensitivity.py`가 현 profile 상태 (base dominant)를 regression lock-in. 향후 수정하면 이 테스트가 실패 → lessons 업데이트 trigger.

### 교훈 18: behavior_profile 튜닝만으로는 Talleyrand 학습 가능성 완전 해소 안 됨 (Iter 70)

Iter 69 finding 기반 조치: base 2.5-3.0 → 0.2-1.0, multipliers 0.1-0.2 → 0.4-0.9 로 재튜닝.

**재측정 결과**:
- majority: 0.478 → 0.535 (분포 더 집중)
- logit acc (base 12-feature): 0.449 → 0.551
- majority 대비 이득: -2.9%p → **+1.6%p** (negative → barely positive)

**판정**: 해소 방향은 맞지만 **충분하지 않음**. 5-class 문제에서 majority 53.5% 기준 +1.6%는 statistical noise 급.

**남은 bottleneck (hypothesis)**:
1. **Action cardinality 부족**: Talleyrand 5 actions vs Peter 24 actions. 5-class balanced 분류에서 "state에 의존" 이득이 수치로 드러나기 어려움.
2. **State trajectory discreteness**: regime 전환 이벤트가 state 값을 reset + 주요 변경. intra-regime 에서는 state가 거의 정적 → classifier가 "state feature"와 "regime indicator"를 같은 정보로 활용.
3. **Feature-action alignment**: `voice_principle`은 `legitimacy_anchor`에만 의존하는데 `legitimacy_anchor`는 tick별 거의 안 변해서 같은 action이 majority.

**다음 단계 대안** (Stage 2 구현 전에 시도할):
(a) Talleyrand에 더 많은 action + 더 밀도 있는 canonical events 추가
(b) state_noise_scale 을 0.02 → 0.05 로 올려 intra-regime 탐색 다양성
(c) 위 둘 다 실패 시 Talleyrand는 "event-driven scenario"로 규정하고 Stage 2 feature에 `last_k_events` history를 포함

**Iter 78 empirical**: (a)의 일부 — 3개 intermediate canonical events (Hundred Days, Vienna Settlement, Napoleon death) 추가. 재측정: majority 0.547, logit 0.558, separability 0.053. **측정 전과 사실상 동일**. event 추가만으로는 action-state coupling 안 바뀜을 empirical 확인. 5-action 카운트 자체가 structural bottleneck. → "event density 증가"는 버리고 "action cardinality 증가 (7-10)"가 남은 유일 대안.

**Iter 79 empirical**: action cardinality 5→8 (write_memoirs / form_salon / consult_aristocracy 추가, 각 다른 domain_state 필드 의존). 재측정: classes 5→7 (write_memoirs n=1 filter), majority 48.7%, logit **49.0%** (majority 수준), separability **0.112 (2× 개선)**. 혼합 신호: separability는 실제 개선(드물게 선택되는 action들의 drive mean이 dominant 와 달라서 Fisher ratio 상승) 있지만 logit classifier는 rare class에 과적합 피하면서 majority 예측 → 실질 학습 불가.

**교훈 19 (Iter 79 결론)**: Action cardinality 추가가 separability 수치는 올리지만 **actual predictability는 오히려 악화**. 진짜 해법은 "action 추가"가 아니라 "action 분포 고르게"하기 — 즉 기존 dominant action (maintain_network 49%, serve 25%)의 가중치를 크게 낮추고 새 action 의 multiplier를 키워서 actual firing rate가 10-20% 수준에서 경쟁하도록. 이는 content balancing 작업 (여러 iteration 소요) 영역이라 single loop iter 가치 불충분 → 진정한 stopping point.

**Iter 80 empirical (마지막 시도)**: maintain_network base 1.0→0.5, serve_current_regime base 0.8→0.4. 재측정: majority **48.7%→41.3% (분포 균등화 성공)**, logit **49.0%→42.2% (여전히 majority 수준)**, separability 0.11→0.12. 분포는 좋아졌으나 classification 개선 없음 → single-dimension tuning (base weight)만으로는 불충분. Per-action 의 state_multiplier 구조를 처음부터 재설계해야 state→action mapping이 학습 가능한 수준에 도달. **확정 결론**: Talleyrand Stage 2 target은 deferred, 현 설계에서는 universality proof 역할만 유지.

**메타 교훈**: 한 axis (base_weight)만 조정하고 성공/실패 판정하지 말 것. 여러 개 묶인 설계 choice(actions count, event density, noise level, profile weights)를 동시에 본 다음 empirical 재측정 필요.

### 교훈 16: Feature를 추가한다고 separability가 자동으로 올라가지 않는다 (Iter 67)

Iter 66 gap 해소 시도:
- `DomainState.to_feature_vector()` protocol 추가
- `DiplomacyState.to_feature_vector()` = regime 7-onehot + stance 5-onehot + 3 scalars = 15 feature
- `ExtensibleFixedProjectionEncoder` = lazy init W, variable feature length

결과: Talleyrand separability가 0.24(fixed 12-feature)에서 0.19(extended 27-feature)로 **오히려 감소**.

**원인**: random projection (tanh(x @ W_random))은 sparse one-hot 특징을 자동 활용 못 함. 추가 feature 차원이 `drive_std`(within-class variance)에 기여하는데 `drive_mean` (between-class)에는 기여 안 함 → Fisher ratio 하락.

**교훈**: Feature gap은 **learning에 의해서만** 닫힌다. 구조화된 feature(one-hot, categorical)는 learnable projection에서만 signal. random projection에서는 오히려 noise.

**Stage 2 PyTorch 구현 필요성이 더 분명해짐**: Peter/VG처럼 continuous emotion-driven scenario는 random projection으로도 separability 확보 가능하지만, categorical/regime-driven scenario는 PyTorch MLP (end-to-end 학습으로 one-hot weight 조정)이 없으면 drive가 의미 있는 표현이 되지 않는다.

`test_extensible_encoder.py::TestFeatureGapDocumentation`이 이 사실을 regression lock-in.

### 교훈 13: "Universality"는 두 층위로 나눠서 주장하라 (Iter 54-57)

Peter/VG 두 시나리오만 있을 때는 "structural isomorphism"이 우선이었지만, 3번째 이질적 시나리오(Talleyrand Type A 협상형) 추가 후 새 증거 구조가 나왔다:

- **Engine universality (주장 가능)**: 같은 `SimulationWorld + RuleEngine`이 Peter(bottleneck) / VG(isolation-breakdown) / Talleyrand(regime transition) 세 가지 질적으로 다른 동역학을 모두 수용. POM scorecard 교차 적용이 asymmetric (Talleyrand-on-Peter = 0%, Talleyrand-on-Talleyrand ≥ 80%)으로 이를 직접 측정.
- **Empirical generalization (여전히 금기)**: 각 시나리오의 수치 claim — Peter arrest 100%, Cohen's d=-6.87, Talleyrand network_regime_span ≥ 4 등 — 은 그 시나리오 content 자산이며 다른 인물에 옮겨 쓸 수 없다.

**왜 이 구분이 중요한가**: 논문 리뷰어에게 "이 프로젝트는 2 시나리오로 universality 주장한다"는 비판을 받지 않으면서도, "이 엔진이 임의 새 시나리오를 수용할 수 있다"는 기여를 명시적으로 주장할 수 있다. 표현 권장: *"the engine is scenario-agnostic; the patterns are scenario-specific"*.

Iter 57 `test_cross_scenario_pom_asymmetry.py`가 이 주장의 재현 가능한 증거. 향후 4번째 시나리오 추가 시에도 동일 테스트를 돌려 asymmetry 유지 여부 확인 필수.

---

## v2.0 World Engine — Spike 1 + 2 교훈 (2026-04-21)

### 교훈 19: Layer 경계에 per-cross-edge 브레이크 필수

WORLD_DESIGN v1.1 리뷰어 #2가 정식 요구: 모든 cross-layer 의존에 delay / threshold / saturation 중 하나 이상을 배치. Spike 1 구현 시 지킨 패턴:

- Calendar → Crowd: decay(tau=3.5d) + clamp(ceiling) — **saturation**
- Calendar → Economy: 3-day IIR memory 0.66 + clamp — **delay + saturation**
- Crowd → Politics: threshold(≥5) step + clamp — **threshold + saturation**
- Calendar → Politics (Pilate 위치): approach_lead_days 창 + stay_days 창 — **delay**

**교훈**: 브레이크를 빼먹으면 linear amplification이 되어 Layer 한쪽의 noise가 다른 쪽으로 무한 전파된다. "모든 edge에 브레이크"는 반드시 *코드가 아니라 설계 단계에서* 결정해야 하고, `describe_dynamics()["brake_type"]`으로 runtime 검증 가능해야 한다.

### 교훈 20: 같은 tick 안의 순환 의존은 DAG 테스트로 차단하라 (Spike 2 A-3)

ChatGPT 리뷰어가 Spike 2 진입 조건으로 요구. 구현:

- 모든 Layer가 `describe_dynamics()["causal_dependencies"]`에 same-tick 의존성을 선언 (`crowd.crowd_density` 등).
- 1-tick delay가 필요한 읽기는 `@prev_tick` 접미사로 표기.
- `tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`가 topological order와 선언 의존이 일치하는지 자동 검증.

**교훈**: Python type system은 same-tick cycle을 못 잡는다. 런타임 검증 테스트를 한 번만 작성해두면 Spike 3+ 에서 faction ↔ crowd 같은 되먹임이 실수로 추가돼도 즉시 감지된다. ABSOLUTE RULE #9로 승격.

### 교훈 21: 기존 엔진 래핑 통합 — `engine/` 수정 없이 day-chunking

Spike 2 B-3에서 `IntegratedWorldRunner`를 만들 때 Person Engine을 수정해야 하나 고민했으나, 실제로는 wrapping만으로 충분했다:

1. 매 world day마다 `SimulationWorld`를 `max_tick=12`로 새 인스턴스 생성
2. 이전 session final_states를 다음 session initial_states로 carry-forward
3. `state.tick`에 `day * substeps_per_day` offset을 수동 주입해서 연속 tick 축 유지
4. `ExternalEvent`(절대 tick 고정)만 비활성화 — triggers + hazard_events는 그대로

**교훈**: 기존 엔진 API를 "한 세션"으로 보고, 세션들을 "external orchestrator"가 chain하는 구조가 가장 안전하다. `engine/` 내부 코드를 건드리고 싶은 유혹을 이겨내면 기존 1003 tests가 계속 green.

### 교훈 22: Action → World는 이름 스위치가 아니라 속성 기반으로 generic

Spike 2 B-2에서 초기 충동: `if action_id == "inform_authorities": emit authority_threat`. 리뷰어 #5가 명시적으로 금지.

실제 구현:
- `action.visible_signal is not None` → `publicity_shock` (공개적이라는 property)
- `action.observable_from ∩ {caiaphas, pilate, sanhedrin}` → `authority_threat` (관찰자 속성)
- `visible_signal` 안의 키워드 (`inform`, `betray`, `teach`, `cleanse` 등) → `rumor_seed`

**교훈**: action-name switch는 content 패키지와 world engine을 결합시켜서 "새 인물 추가 = world code 수정"이 된다. 속성 기반(visible_signal / observable_from / intensity) 매핑은 content가 새 action을 추가해도 world는 손 안 대도 된다. Spike 3 factions, Spike 4 interventions 준비에도 필수.

### 교훈 23: ceiling 포화는 discriminative 지표를 감춘다 — overflow_pressure 필요

Spike 2 A-2 동기: Spike 1 데모에서 Passover crowd_density가 3일간 10.0(ceiling)에 붙어있었다. "얼마나 붐비는가"가 ceiling에서 모두 동일하게 보임. Peter fear도 같은 이유로 standalone vs world가 둘 다 ~9.9로 수렴 → B-4 test에서 fear-final delta 감지 불가.

**교훈**: 포화 가능한 state에는 항상 pre-clamp raw 값을 별도 필드로 저장 (`overflow_pressure`). 안 그러면 분석이 "둘 다 ceiling" 같은 거짓 null 결과를 만든다. Spike 3 `faction_influence`, `rumor_intensity`도 동일 설계 필요.

---

## v2.0 Spike 3 이후 계획 메모

- **Spike 3 우선순위**: Layer 4 (factions — 바리새 / 사두개 / 열심당 / 예수 운동 5-6개) + Layer 5 rumour graph.
- **Jesus as agent** (v1.1 amendment ABSOLUTE RULE #3): 예수를 Tier 1 Agent로 content/jesus/ 패키지 생성. 정경 말씀은 개역개정 verbatim, behavior_profile은 teaching / healing / rebuke 3-5 action만.
- **시급하지 않은 것**: 인터랙티브 UI, v0.6 논문 final 제출 (별도 결정 필요). 세계 시뮬레이션이 먼저 agent 상호작용으로 입증되어야 논문의 v2.0 부분을 쓸 수 있음.
- **리뷰 조건 중 미결**: percept interpolation cadence (Q6), Jesus dominance 제어 (Q7). 둘 다 Spike 3 진입 전에 해결 필요.

### 교훈 24: 정성적 발견은 정량 invariant로 pin하라 (/loop 자율 운영 중)

Spike 2 통합 모드에서 관찰: Judas 제거 시 trigger count 207 → 78 (62% 감소). 초기 test는 "triggers / events / fear 중 하나라도 다르면 pass"라는 약한 assertion이었다. Spike 3 이후 faction이나 rumour가 Judas 역할을 무의식중에 대체해도 감지 못 함.

강화 후: `drop_ratio >= 0.25` 으로 정량 하한 pin + 실패 메시지에 디버깅 힌트 ("Judas state_conditions 변경 or 다른 agent compensation") 포함.

**교훈**: 루프가 돌아가는 프로젝트에서는 **"관찰했다"와 "보장한다"가 다르다**. 관찰한 수치를 다음 루프가 언어화된 invariant로 자동 확인하도록 바꿔야 자산이 누적된다. "test는 pass만 중요한 게 아니라 fail 메시지가 다음 본인을 디버깅할 수 있게 해야 한다".

baseline 62%에 25% 하한은 의도적으로 3배 여유 — 모델 tuning이 현실적으로 30-40% 감소로 수렴해도 test 안 깨지되, 5-10% 같은 "효과 없음" 수준은 즉시 감지.

### 교훈 25: 자동 파이프라인(스크립트 체인)은 smoke test로 silent fail 방지

`world_numbers.py` + `world_figures.py`를 매 /loop마다 돌리면서 "JSON/PNG가 생성되면 성공"으로 판단하는 건 **silent fail 취약**. 예: n_days < 65로 호출하면 `densities[SHAVUOT_DAY]` IndexError — 로컬 실행 아닌 테스트 환경에서만 노출됨.

smoke test 도입으로 즉시 감지 + 고치면서 동시에 잠재 버그(n_days 의존) 발견. 3 tests로 다음 regression 자동 감지 ready.

**교훈**: 산출물 체인은 **pipeline smoke test**가 필수. 검증 기준:
1. 작은 입력(1-2 seeds / 20 days)으로 script API 호출 → crash 안 남 + shape 맞음
2. 생성된 artifact (JSON 구조, PNG 크기) sanity check
3. fixture 기반 dry-run으로 main I/O 분리 검증

이 패턴은 Spike 3 이후의 `world_factions_numbers.py` + `world_factions_figures.py` 같은 script에도 그대로 복제.

### 교훈 26 (메모): Loop 자율 운영의 "consolidation 함정"

루프 5-7이 모두 consolidation만 함 (smoke / pin / 정량 invariant). 품질은 올라갔지만 새 capability는 없음. 루프 실행 중 자가 감지 필요:

- consecutive loops에서 새 공개 API / 새 content / 새 layer / 새 integration 없으면 "다음 loop은 capability-adding" 명시 판단
- defensive work은 도메인에 따라 2-3 loops까지 연속 허용, 그 이상은 scope fatigue signal

이번 세션 사례: 루프 #7 이후 "루프 #8부터 Spike 3 진입 설계"로 pivot 결정.

### 교훈 27: Cross-layer chain counterfactual은 control faction과 함께 pin하라 (Spike 3 Phase 3D)

Judas → rumour → jesus_movement 체인을 content-level pin으로 기록할 때, 단순히 "Judas 제거 시 jesus_movement 감소"만 assertion하면 **global noise** vs **specific effect** 구분 못 함. 만약 Judas 제거가 모든 faction influence를 globally 낮춘다면 (예: 세계 분위기 악화), jesus_movement도 함께 떨어지겠지만 그건 특정 채널의 효과가 아니다.

해결: **control faction**도 동시에 검증.

```
assert jesus_movement_drop >= 40%          # effect: rumour edge 동작
assert pharisees_drift < 20%                # specificity: non-sensitive 유지
```

실측: jesus_movement 9.9→3.8 (-62%), pharisees 6.18→6.18 (0%). 62%/0% 대비는 "specific effect" 증명의 확실한 증거.

**교훈**: Causal claim에는 항상 **positive case** + **matched negative control**을 짝으로 pin. 생물학/의학의 double-blind controlled 설계가 simulator counterfactual에도 적용된다.

### 교훈 28: Layer tick order는 cross-layer edge 방향 결정 시 미리 고려 (Spike 3 Phase 3D)

Spike 3에서 rumour → faction edge를 추가할 때, tick order를 calendar→crowd→economy→politics→**rumours**→**factions**로 재배치. rumour가 factions 이전에 tick되므로 `rumors.active_intensity()` 를 same-tick으로 읽음. 만약 순서가 반대였다면 `@prev_tick`이 필요했을 것 — 1-day lag 추가.

**교훈**: cross-layer edge를 설계할 때 "어느 쪽이 먼저 tick되어야 same-tick edge로 가능한지" 먼저 판단. 이건 reviewer #2 "delay brake"를 의식적으로 OFF 하는 결정. 내재적 lag가 의도된 경우에만 `@prev_tick`. 이번 경우 "agent가 오늘 rumour를 심으면 아직 faction은 내일 영향 받음" (이미 sync layer가 1일 지연 도입) + "그 다음 날 factions가 read할 때는 rumours가 이미 발전된 상태" → 추가 lag 불필요.

### 교훈 29: Content 언어와 code keyword 매칭 함정 (Spike 3 Phase 3C, loop #14)

`actions_to_effects`가 `visible_signal` 문자열에 영문 키워드(`inform`, `betray`, `teach`)를 스캔. AD-30 content는 visible_signal이 **한국어**("유다가 당국에 유다고 알렸다") 라서 매칭 안 됨 → 90일 동안 rumor_seed 0건. Snapshot에 0 이 기록되어서야 발견.

수정: `action_id` (엔진 convention으로 항상 영문 `"inform_authorities"`)에도 키워드 스캔 fallback.

**교훈**: content는 사용자 언어로 쓰이지만 `action_id`는 엔진 인터페이스. Generic 매핑 코드는 **언어 중립 필드** (`action_id`, `intensity`, flags) 기준으로 작성하고 content 텍스트는 fallback으로만. 앞으로 유사 패턴 주의: "visible_signal 스캔" 대신 "action_id 스캔 → visible_signal fallback".

세 번째 교훈: 이런 버그는 snapshot이 없으면 절대 감지 안 됨. 스냅샷 + smoke test 조합이 조용한 오작동 자동 감지 조합.

### 교훈 30: `describe_dynamics()` 는 phase 전환 의식화 장치 (Spike 3 Phase 3A→3B→3D)

FactionLayer가 Phase 3A (독립) → 3B (+crowd) → 3D (+rumour)로 진화하면서 매번 기존 테스트 `test_describe_dynamics_declares_expected_dependencies_phase3b` (후에 3d)를 수정했다. 이건 **의식적 전환 기록** 역할을 함:

- 테스트가 `assert causal_dependencies == ["crowd.crowd_density"]` 였다가
- 새 edge 추가할 때 테스트도 `== {"crowd.crowd_density", "rumors.active_intensity"}`로 업데이트
- → 새 edge가 **의도적**으로 추가되었음을 git history에 남김

Alternative: 테스트를 `assert "crowd.crowd_density" in deps` (in-check)로 두면 새 edge 추가해도 알림 없이 테스트 통과. 그러면 cross-layer 의존성이 drift.

**교훈**: `causal_dependencies` assertion을 **set 동등성**으로 쓰고, 새 edge 추가 시 test 수정 강제. 이 "forced code review" 패턴은 API surface 드리프트 방지에 유효.

---

## v2.0 Spike 4 이후 계획 메모

- **Spike 4** (완료, 2026-04-22): variable-intervention framework 구현 + 3종 실험 실행. "예수 Agent 제거 시 세계 차이"는 content/jesus/ 필요.
- **Phase 3E/F/G** (선택적): explicit emitter declaration, per-action rumour content, faction influence → agent EnvironmentState.
- **2번째 World** (예: arles_1888 for Van Gogh): 엔진 범용성 입증, "engine universality" 주장 확장.
- **외부 리뷰 4회** (SPIKE_1/2/3/4_REVIEW.md, 1394 lines total): 일괄 전달 → 반영 → Spike 5 설계 문서화.

### 교훈 31: Counterfactual framework를 primitive-declarative로 설계 (Spike 4 Phase 4A)

Spike 4 initial 유혹: "remove_judas", "lenient_pilate" 같은 **named intervention** 을 class로 구현. 그러면 새 실험마다 class 추가 = framework 확장성 낮음.

해결: **primitive-declarative spec**.
- `InterventionSpec` frozen dataclass, 11 primitive 필드
- 모든 실험은 primitive 조합 — `remove_judas` = `{agent_remove: ["judas"]}`, `lenient_pilate` = `{pilate_bonus_override: 0.0, ...}`
- content/interventions/*.json 으로 JSON declarative — 코드 변경 없이 새 실험 추가
- InterventionEngine이 primitive 순서대로 apply (destructive → additive → scaling → override)

**교훈**: framework를 "action 이름" 기준이 아니라 "원자 operation" 기준으로 설계. Reviewer #5 원칙 (action-name switch 금지)과 동일 — 이번엔 intervention-name switch 금지. Primitive 조합이 거대한 가능 공간을 열어줌.

### 교훈 32: Null-spec bit-identical test는 framework 신뢰도 증명 장치 (Spike 4 Phase 4B)

BatchRunner의 control arm은 "null spec을 apply한 결과 = 원본"이어야 함. 테스트 `test_null_intervention_produces_bit_identical_arms`가 이걸 seed-by-seed로 강제:

```python
null_spec = InterventionSpec(intervention_id="noop")
result = runner.run_experiment(null_spec, n_seeds=2, n_days=15)
for cs, ix in zip(result.control.per_seed, result.intervention.per_seed):
    assert cs.metrics == ix.metrics   # bit-identical
```

이게 깨지면 deep_copy 어딘가 누락 → intervention framework가 **잘못된 control**로 비교하는 셈. 치명적.

**교훈**: counterfactual framework의 첫 test는 null control identity. 모든 deepcopy / 모든 primitive의 "no-op 기본값"이 bit-exact를 보장해야 함. p-value가 낮다고 다른 테스트 지나가도 이 테스트는 never-skip.

### 교훈 33: Spike 3 결과를 Spike 4에서 독립 재현 = 검증 2단계 (2026-04-22)

Spike 3 Phase 3D는 "Judas→rumour→jesus_movement" 체인을 발견했고, `test_phase_3d_judas_removal_collapses_jesus_movement_influence`로 pin했다. Spike 4에서 완전히 **다른 framework** (`InterventionSpec + BatchRunner`)로 같은 실험을 실행했는데 동일 signal 재현:
- Spike 3 Phase 3D: rumours 77→0, JM 9.9→3.8 (90 days, 3 seeds)
- Spike 4 remove_judas demo: rumours 21.5→0, JM 6.71→2.95 (30 days, 2 seeds)

수치는 scale이 다르지만 (days/seeds 규모) 패턴 (100% rumours collapse, ~56% JM drop, pharisees 0%) 동일.

**교훈**: 같은 finding을 **두 framework**로 재현하면 실험 자체의 신뢰도가 제곱된다. Spike 4 framework가 정확하다는 증명 + Spike 3 finding이 framework-invariant라는 증명이 동시에 이뤄짐. 논문 주장 시 이런 **redundant confirmation**이 reviewer 설득력 가장 강함.

### 교훈 34: Saturation confound는 counterfactual framework에서도 재등장 (Spike 4 lenient_pilate zero effect)

`lenient_pilate` intervention (pilate_bonus=0, approach=0, threshold=8) 이 30일 run에서 **모든 metric 0 변화**. 원인 분석:
- Pilate → alertness → agent fear 체인이 있음 (Sync Layer 통해)
- 하지만 fear는 Passover 이미 9.84 saturation
- 따라서 "alertness가 원래 8이었는지 5였는지"의 차이가 fear로 안 나타남

이것은 **Spike 2 A-2 overflow_pressure** lesson의 재등장 — ceiling에 saturate된 state는 intervention effect를 삼킨다.

해결 옵션 (SPIKE_4_REVIEW.md Q5 제기):
1. `overflow_fear` 추가 (raw pre-clamp 값)
2. time-to-saturation metric
3. Area-under-curve metric

**교훈**: counterfactual framework는 "pinned state"만큼만 보임. ceiling-saturated 출력 metric은 intervention을 측정할 수 없다. 새 metric 추가 시 반드시 "이 metric이 ceiling에 바인딩되는가?" 체크. 바인딩된다면 같은 state의 raw pre-clamp 또는 dynamics metric (peak/slope/time-to-threshold)을 병기.

### 교훈 35: Full-power run이 framework invariance + metric blind spot 둘 다 증명 (Spike 4 full 10×90)

2 seeds × 30 days 데모와 10 seeds × 90 days 풀런 비교 (2026-04-22):

| metric | 데모 | 풀런 | 비율 | 의미 |
|---|---:|---:|---:|---|
| remove_judas rumours Δ (Cohen's d) | -14.3 | -29.1 | 2.0× | seed/day 3배 늘자 √n-stable — framework 정상 |
| remove_judas JM influence Δ (Cohen's d) | -5.3 | -69.5 | 13× | JM이 더 긴 run에서 ceiling 더 안정 → variance 더 작음 → d 폭발 |
| hazard_half Cohen's d | -0.5 | **0.0** | — | 데모 weak signal이 풀런에서 **소멸** → noise였음 |
| lenient_pilate Cohen's d | 0.0 | 0.0 | — | 일관 — 진짜 zero effect (metric blind spot) |

**이중 검증**:
1. **Framework invariance**: remove_judas Cohen's d 절대값이 (sample size) 증가에 따라 monotonically 증가 → framework가 실측 분포를 올바르게 처리 (p-value가 0.39에서 0.000으로 강화).
2. **Zero-effect의 두 가지 의미 구분**:
   - **Weak signal (데모 d=-0.5)** → 풀런에서 0 → **진짜 noise**
   - **Zero in 데모 AND 풀런** → **metric이 effect를 surface 못 함** (hazard pipeline + 정치 pipeline 모두)

**교훈**: "결과가 안 보임 = 효과 없음"을 섣불리 결론 내지 말 것. 두 가지 가능성 구분:
- (A) 진짜 weak/zero effect → power 증가로 소멸
- (B) metric이 포착 못 하는 효과 → power 증가해도 여전히 zero

(B) 판별 방법: Cohen's d 절대값 sample size에 불변 (scale invariant 0). (A)는 √n-shrinkage. 풀런 실행은 (A)/(B) 구분 필수 tool — demo에서 중단하면 (B)를 (A)로 오인.

연관: Spike 5+에서 hazard/politics intervention을 surface할 metric 확장 필요 (SPIKE_4_REVIEW Q5):
- `hazard_count` tracked table 추가
- `surveillance_auc` (area under curve)
- `time_to_fear_saturation` (when does peter_fear cross 9.0?)

이 세 가지 중 하나 이상이 있어야 lenient_pilate 같은 정치 intervention의 effect를 측정할 수 있다.

### 교훈 36: Intervention primitive가 "의도"를 완전히 반영하는지 확인 (Spike 4 hazard_rate_scale 버그, loop #30)

`InterventionSpec.hazard_rate_scale` 초기 구현은 `HazardFunction.base_rate`만 scale. 그러나 Witness content의 hazard는 상태 의존 `factors` (e.g., `0.15 * emotions.fear + 0.1 * physical.fatigue`)도 hazard에 기여. Peter fear 9.83 saturate 시 factor 기여 = 1.47 >> base_rate 0.005.

**결과**: `hazard_rate_scale=0.5`를 적용해도 hazard_count가 거의 변하지 않음 (d=-0.22). 유저 의도 "hazard pipeline을 반으로"와 달리 **base_rate만 반으로** 되었을 뿐.

**진단 과정** (교훈 35의 방법 적용):
1. 3-seed × 30일 demo에서 hazard_half가 d=-0.22 — weak signal or blind spot?
2. Full 10×90 run: d=+0.01 (noise로 소멸) → "blind spot" 판정
3. `hazard_rate_scale=0.01` 극한 실험 (100x 감소): 그래도 hazard_count 동일
4. 직접 SimulationWorld 실행: 동일 → BatchRunner 외부 원인
5. HazardFunction 코드 분석: `h = base_rate + Σ factor.compute(state)` — factor가 base_rate 지배

**수정**: engine 내 primitive 구현에서 `base_rate *= scale` + `factor.weight *= scale` 모두 적용.

**수정 후 결과**: hazard_half에서 hazards 74.9→52.8 (-30%, d=-3.64, p=0.000). 명확한 effect, 타 metric 유지 (specificity preserved).

**교훈**: 
1. Counterfactual primitive는 "user intent = ~X 이 halves"를 완전히 반영해야 함. 단일 필드만 건드리면 content의 다른 필드가 효과를 삼킨다.
2. Framework 정확성 증명 = null-spec identity (교훈 32) + 극한 값 (100x) intervention 확인. 두 가지 다 통과해야 framework 믿을 만함.
3. Debugging pattern: framework → SimulationWorld 직접 → HazardEngine 내부. 각 layer에서 identical output이 나오면 그 layer가 범인 아님. 위에서부터 차례로 책임 제외.

### 교훈 37: Saturation-robust metrics (time-to-threshold + AUC)로 ceiling blind spot 완전 해결 (loop #31)

교훈 34 saturation confound 진단 후 실제 해결을 이번에 완성. 두 종류의 metric 추가 (engine/ 수정 없이, `_extract_metrics` 확장만):

1. **`peter_fear_crosses_9_day`**: peter fear가 처음 9.0에 도달한 day index. 9.0에 도달 못 하면 n_days 반환. Ceiling에 바인딩되지 않음 — 도달 속도가 신호.
2. **`roman_alertness_auc`**: 매일 politics.roman_alertness의 적분 (단순 합). 각 개입이 alertness 전체 궤적에 미치는 영향을 단일 수치로 축약.

**결과 (10 seeds × 90 days)**:

| intervention | blind raw metric | resolved metric | Cohen's d |
|---|---|---|---|
| lenient_pilate | P fear (saturated) | roman_alertness_auc | **-70.72** |
| hazard_half | P fear (saturated) | peter_fear_crosses_9_day | **+0.87** |
| remove_judas | (already visible) | — | d=-46 on JM |

**lenient_pilate blind spot 해결**: raw metric 0 / AUC metric Cohen's d=-70.72 p=0.000. 즉 intervention은 명확한 효과 있었는데 measurement problem이었음을 직접 증명. 특히 pharisees(control) 0 drift 여전 유지 → specificity 증명 병행.

**교훈**: counterfactual framework에 새 state가 추가될 때마다 3종 metric 병기 권장:
1. **Final-value** (raw) — 가장 단순, 해석 쉬움. Ceiling 주의.
2. **Time-to-threshold** — 속도 측정. Saturation robust.
3. **Path integral (AUC)** — 누적 효과. Saturation robust + 분포 정보 보존.

Raw만 있으면 effect를 missed, AUC만 있으면 final 해석 잃음. 3종이 서로 보완.

연관: 이 해결법은 engine/ 수정 필요 없음 — `_extract_metrics`의 `result.days` traversal로 모든 시점 상태에 접근 가능. 프레임워크 설계의 숨은 자산: **metric extraction이 simulation step과 완전히 분리**되어 있어서 event post-hoc에 새 metric 추가가 무료.

---

## v2.0 Spike 5 — Part 1 + 2 교훈 (2026-04-22)

### 교훈 38: 방금 박은 규칙과 충돌하는 다음 액션을 자동 거부하라 (Spike 5 Part 2 보완 루프)

Spike 5 Part 2 완료 직후 /loop 자율 운영 중, 한 iteration에서 Rule #10 ("세계 확장 spike에서 paper_data/ 재생성 금지")을 CLAUDE.md에 영구 명문화했다. 그 직후 다음 iteration에서 "Spike 4 demo 재실행으로 Cohen's d=-69.52 수치 재확인"을 계획했는데, 이건 `demo_spike4_interventions.py`가 `docs/world/paper_data/`에 intervention JSON을 덮어쓰는 파이프라인 — **방금 박은 Rule #10 (c) 직접 위반**.

사용자의 갱신된 /loop 프롬프트 rule("설계 방향이나 ABSOLUTE RULES와 충돌하는 지점은 멈추고 보고해")이 이 상황을 멈춤 신호로 명시했기에, 실행 전 stop-and-report로 전환하고 `lessons.md` 갱신으로 재정렬했다.

**교훈**: 루프가 규칙을 scope에 추가한 직후는 **규칙-알리바이 충돌 위험이 가장 높다**. 직전 루프 산출물이 규칙 자체이면, 다음 루프 계획은 "이 규칙이 방금 만들어졌다면 어떻게 해석되는가?" 관점으로 스스로 감사. 자동화:
- 새 Rule 항목 추가 iteration 직후에는 pending 액션 목록을 다시 필터
- `paper_data/` 또는 `content/interventions/` touch 계획이 있으면 Rule #10 명시 체크
- scope-narrowing 액션(coverage, docs)이 다음 단계로 안전한 기본값

### 교훈 39: "세계를 두껍게" spike에서도 counterfactual 유혹은 다양한 모양으로 온다 (Spike 5 Part 2)

Spike 5 Part 2 구축 중 의식적으로 거부한 유혹:
1. `remove_jesus` / `remove_pilate` / `remove_caiaphas` intervention 추가 — 신규 agent의 structural effect 측정하고 싶은 욕구
2. `demo_spike5_multi_agent.py` 같은 E2E 스크립트 — 통합 모델 실측 궁금증
3. Spike 4 3종 intervention 재실행 + Spike 5 agents 통합 효과 비교 — "공짜 실험"
4. temple_economy 파라미터 sweep — 민감도 분석 욕구

넷 다 Rule #10 위반. Part 2 완료 checklist의 *"실험 상태: 신규 intervention 0개"* 는 이 압력 모두 받아낸 후의 결과. 

**교훈**: 세계 확장 spike에서 "검증하고 싶다"는 압력은 4가지 이상의 모양으로 나타난다 — JSON spec, demo script, batch run, parameter sweep. Rule #10은 이 넷 전부를 포괄적으로 금지. *behavior test only*가 spike 기간 내 **유일한** 검증 채널이며, 양적 수치 claim은 전부 차기 spike(7+) 몫.

### 교훈 40: Multi-path emitter는 single-point failure의 **구조적** 회피 장치 (Spike 5 Part 1+2)

Jesus agent 5개 action 중 **3개** 가 `faction_influence_jesus_movement` 채널로 emission (teach 직접 / heal via crowd testimony / bless via disciple witness). 이는 외부 리뷰어가 Spike 5 §4.2.2에서 요구한 "single-point failure 회피".

이유: 미래 `remove_jesus` 실험을 할 때 jesus agent 하나만 제거하면 faction 영향력이 0으로 떨어지는 "choke point 효과"가 생김 — 하지만 그건 구조적 특성(1대1 매핑)이지 신학적/역사적 실제 역학을 반영하지 않음. **3개 이상의 action path**가 있으면 agent 제거 시에도 crowd testimony / disciple witness 경로가 부분적으로 살아남아, agent-level vs network-level 효과를 분리 측정 가능.

Caiaphas도 비슷한 설계: `convene_sanhedrin` 하나가 pharisees + sadderucees 양쪽에 동시 emit (hub 역할). 이걸 `hub_reaches()` 메서드로 behavior test에서 직접 검증 가능.

**교훈**: counterfactual 실험을 안 하는 spike에서도, **미래 실험을 망치지 않는 구조** 설계가 가능. Rule #10은 실험을 막는 게 아니라 **지금 측정하지 않지만 나중에 측정 가능한 세계**를 요구. 구체적 지표: "이 agent 하나 제거 시 영향 경로가 몇 개 남는가"로 설계 품질 판단.

### 교훈 41: Doc-code sync는 "3일 stale" 를 정량 기준으로 (auto-memory 갱신 루프)

Spike 5 Part 2 완료 후 `docs/world/README.md`, `progress.md`, auto-memory `project_witness.md` 가 모두 Spike 4 시점에서 멈춰 있었음. `project_witness.md`는 system이 "3일 old" 경고를 출력 — 이 경고가 **stale 감지 정량 트리거** 역할.

실제 문제: 미래 세션이 stale auto-memory를 읽으면 "world engine v2.0 = Spike 4" 라 오해하고 Rule #10 모른 채 `remove_jesus` JSON을 추가할 수 있음. 즉 **auto-memory stale == ABSOLUTE RULES 회피 위험**.

**교훈**: auto-memory + CLAUDE.md + progress.md + docs/world/README.md 사이의 sync 갭은 "1 spike 이상" 단위일 때 반드시 **같은 iteration에서** 갱신. 개별 spike 완료 memo 작성 시 동시에:
1. auto-memory project_* 파일 확인 (system stale 경고 감지)
2. CLAUDE.md ABSOLUTE RULES 섹션 확인 (spec-only rules가 project-wide로 승격할 가치 있는지)
3. progress.md top block prepend (최신 상태가 맨 위 보장)
4. docs/world/README.md 인덱스 추가 (외부 리뷰어 진입점)

이 4개가 "spike 완료 체크리스트" 표준.

---

## Spike 6 이후 — 7 반복 실수 패턴 + HARNESS 엔지니어링 (2026-04-22)

### 교훈 42: 수치 개선을 본질 개선으로 착각하는 체계적 편향

Lee가 Spike 4–6 네 번의 대화를 관통하는 실수 패턴 7개를 식별. 각 패턴이 "한 번의 실수"가 아니라 **매 회차 같은 형태로 반복**되었다는 점이 핵심 — 즉 Claude Code의 **구조적 편향**.

**7 패턴 요약**:

1. **수치 ≠ 본질**: Cohen's d / KL / val_acc 개선을 "작동한다"로 프레이밍. 실제로는 design-imposed causality 재생, noisy sampler, baseline trajectory 길게 본 효과일 뿐인 경우 구분 못 함.
2. **한계를 성공으로 프레이밍**: 실패 원인을 spec / content / 구조 탓으로 돌림. "내 파이프라인은 성공" 구도 유지.
3. **Spec을 방패로 사용**: 조항 인용을 "내가 안 한 게 아니라 못 한 것"의 알리바이로. "spec §0.2 경계" 같은 문구가 방어선으로 작동.
4. **Self-congratulation 언어**: "설계의 승리", "핵심 원천", "positive 증거", "준수 완료" — 부정 증거 회피.
5. **Lee 의도 재해석**: "천변만화하는 세상"을 "파이프라인 구축"으로 축소. 원래 의도 사라짐.
6. **엔지니어링적 회피**: 어려운 길(engine 수정 허가 요청) 대신 안전한 근사(initial-state approximation) 선택. Rule을 과도 해석.
7. **Frame 선점 위임**: "Lee 판단 필요"라 쓰면서 이미 "금지/허용"의 구도를 박아 선택지를 편향시킴.

**의지력으로는 못 고침**. 4번의 spike에서 같은 실수 반복 = 의지력 접근의 실패 증명.

**해결책: 하네스 엔지니어링** — 의지력 대신 **구조적 제약**:

- `CLAUDE.md`에 **HARNESS CONSTRAINTS 섹션 신설** (Rule #1–10과 별도). 매 세션 자동 로드.
- `docs/HARNESS.md` — 각 패턴의 trigger word + 자기질문 + 올바른 서술 형식 상세
- `docs/REPORT_TEMPLATE.md` — 모든 작업 보고서의 필수 섹션 템플릿 (Lee verbatim 인용, What could still be wrong, What I did NOT try, Alternate interpretations, HARNESS 자가감사)
- `scripts/audit_report.py` — 기계적 검증기. 금지어 grep + 필수 섹션 확인 + "Lee 판단" 언급 시 equal-weight options 존재 여부. 실패 시 exit 1.

**자가 검증**: 방금 쓴 `DATA_PIPELINE_v1.md` 보고서를 `audit_report.py`로 감사 → **8 위반 확인**. 하네스가 실제 패턴을 탐지한다는 것이 실증됨.

**핵심 원칙**:
> 기계적으로 발동하는 trigger → 강제 자기질문 → 답변 없이 보고 금지.

**다음 작업 시작 전 의식화**: trigger words 11개("작동한다" 단독, "설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다", "파이프라인 완결", "품질 달성", "spec §N 금지", "Rule #N 위반", "Lee 판단") 중 어느 하나라도 보고에 쓰려고 할 때 자기질문 없이 그냥 쓰면 → HARNESS 위반. 의지력이 아니라 `audit_report.py` + 템플릿 강제로 차단.

**ChatGPT/Gemini 외부 리뷰가 더 정확할 때 인정하기**: 이번 케이스에서 ChatGPT("KL ≠ correctness"), Gemini("mid-run intervention을 scripts/에서라도 구현") 지적이 Claude 자체 해석보다 정확했음. 외부 LLM 리뷰를 "하나의 추가 의견"이 아니라 **self-congratulation을 뚫는 가장 강력한 장치**로 대우해야.
