# Witness v3.0 -- 기존 실험 Rubric 재평가

> **Spec**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) §6.5
> **Rubric**: [engine/rubric/](../engine/rubric/)
>
> Spec §6.5 verbatim: *"이전 '발견' 주장들을 rubric으로 재평가"*

## 1. 재평가 대상 3건

Spike 4/5/6 에서 "발견" 또는 유사 주장이 있었던 건.

| ID | 주장 | 출처 |
|---|---|---|
| E1 | Spike 4 "Judas 제거 Cohen's d -46" | docs/world/SPIKE_4_REVIEW.md |
| E2 | Spike 5 Part 1 "multi-path 3경로 구조" | docs/world/WORLD_SPIKE_5_PART1_PROGRESS.md |
| E3 | Spike 6 BC "20-34% divergence" | docs/person/STAGE2_PETER_PROGRESS.md Session 5 |

## 2. E1 재평가 -- Judas 제거 Cohen's d -46

### Rubric 적용 시뮬레이션

flowchart step-by-step:

1. **Step 1: is_all_hardcoded?**
   - Arrest event 는 canonical_events.json 에 있음. Precondition은 `judas.betrayal_readiness ≥ threshold`.
   - Judas가 없으면 precondition 자체가 발동 안 됨 → arrest 안 일어남.
   - **Hardcoded firing 은 아님** (precondition state-sensitive). step pass.

2. **Step 2: hard violation?**
   - 정경과 모순 없음. Judas 없으면 arrest 없음 = 정경 일관.
   - **No hard violation.** step pass.

3. **Step 3: canonical reproduction?**
   - Arrest 가 **없는** 상태 (Judas 제거 arm). Canon에는 Judas 있고 arrest 있음.
   - 원래 canon은 arrest 있으므로, arrest=0 trajectory는 canon drift 큼.
   - **is_canon_reproducing = False** (arrest 있어야 canon reproduction).

4. **Step 4: noise?**
   - Control vs Judas-removed 의 drift 차이는 **결정론적** (Cohen's d -46 이 우연 아님).
   - 통계적으로 noise 아님.

5. **Step 5/6: character-consistent?**
   - Judas 제거 시 Peter 행동 변화 (arrest 없음)는 Peter 자체의 변화 아님.
   - 이 판정은 Peter가 여전히 베드로답게 행동하는가의 문제이지 Judas 구조의 문제 아님.
   - **결론: Judas 제거 자체는 "Peter 행동 발견" 아님**. 구조적 counterfactual.

### 최종 분류: **§4.3 NOT_DISCOVERY_HARDCODED 근사 (구조 재생)**

Judas 제거 실험은 **엔진 설계에 이미 내장된 causal chain** 을 확인한 것. "Judas → arrest" 관계는 content의 `canonical_events.json` + `trigger` 설정으로 Lee가 선언. 그것이 재현됐을 뿐.

**단**: spike 4 원본 보고는 이것을 "발견" 이라 프레이밍했음. Rule #13 소급 적용 시 이 명명은 철회 권장. **causal 재생**으로 재분류.

### Justification
- engine setup이 "Judas는 arrest의 trigger" 라는 causal 가정을 이미 포함
- 신경망 학습 없음. 규칙 기반 counterfactual simulation.
- Cohen's d=-46은 **효과 크기**이지 **발견 여부** 판정 아님

---

## 3. E2 재평가 -- multi-path 3경로 구조

### 주장 내용
Spike 5 Part 1에서 Jesus agent가 `faction_influence_jesus_movement` 채널로 3개 action path (teach/heal/bless)로 emit.

### Rubric 적용
1. **Step 1: hardcoded?** -- 네. `JesusAgent._ACTION_EMITTERS` 가 content에 선언된 매핑. engine이 그대로 실행.
2. **Step 2-6: irrelevant** -- trajectory 기반 측정 아님. Engine 설계 패턴 관찰.

### 최종 분류: **§4.1 규칙 보간에도 해당 안 됨 -- "구조 설계"이지 "발견" 아님**

`multi_path emitter` 는 단순히 Claude가 engine/agents/jesus.py 에 하드코딩한 **설계 패턴**. Trajectory에서 관찰된 "emergent" 현상 아님. Rule #13의 3종 어느 것에도 해당 안 함.

**Session log (DATA_PIPELINE_v2_V2_VS_V3_COMPARISON §이전 bias 철회) 에서 이미 인정**:
> "Spike 5 '3경로 구조'는 구조 심었을 뿐 검증 안 됨" (교훈 42 패턴 1)

### Justification
- Engine 코드의 deterministic 매핑 = 규칙
- 관찰된 trajectory에서 귀납적으로 발견된 게 아님
- "∼와 맞춰 설계한 것을 발견이라 명명"은 Rule #13 위반

---

## 4. E3 재평가 -- BC "20-34% divergence"

### 주장 내용
Spike 6 Phase E에서 v3 BC MLP와 규칙 기반 sampler의 action choice가 4 seeds 간 19.6%-34.3% 차이.

### Rubric 적용
1. **Step 1: hardcoded?** -- 아님. MLP 샘플링.
2. **Step 2: hard violation?** -- engine의 `policy=None` fallback이 vocab 침범 차단.
3. **Step 3: canonical reproduction?**
   - Fidelity 측정 (DATA_PIPELINE_v2_V2_VS_V3_COMPARISON) 에서 **overall match 0.042**.
   - Canon drift 매우 큼. **is_canon_reproducing = False**.
4. **Step 4: noise?**
   - Voluntary KL mean **10.5** (거의 무관 분포).
   - Val accuracy = val majority baseline (0.682).
   - **novelty_critic 기본 noise_threshold=15.0**에 가까운 drift. 
   - **결론**: noise band 또는 경계 근처.
5. **Step 5/6**: character composite 낮음 (voluntary 자체 흉내 못 냄).

### 최종 분류: **§4.2 NOT_DISCOVERY_NOISE**

### Justification
- 동일 state에서 다른 action이 나오는 것이 noise 조건 (discovery_definitions §4.2)
- KL 10.5는 분포가 **거의 무관** (KL 0 = 동일, 5+ = 매우 다름)
- Val accuracy 가 majority baseline 수준 = 모델이 majority로 수렴

Session 4 (fidelity split) 에서 이미 실증:
> "MLP 가 학습한 것은 training set 분포의 lookup table" (교훈 42 패턴 1 차단 시도)

**이 재평가는 해당 실증을 Rule #13 언어로 공식 분류.** v4 (full spec) 에서는 rubric 재적용 시 voluntary match 0.16 + event match 0.92 → mixed 결과이지만 voluntary 여전히 drift large.

---

## 5. 종합

| 실험 | v3 rubric 분류 | 소급 평가 |
|---|---|---|
| E1 Judas 제거 | §4.3 근사 (구조 재생) | Spike 4 "Cohen's d -46" 프레이밍 일부 철회 권장 |
| E2 multi-path 구조 | §4.1 규칙 설계 (발견 아님) | Lessons 교훈 42 패턴 1 이미 철회 |
| E3 BC divergence | §4.2 NOT_DISCOVERY_NOISE | Session 3-4 실증으로 재확인 |

**3건 모두 v3 Rule #13 관점에서 "발견" 아님**. 이 결과는:

1. Spike 4/5/6 이 무의미했다는 뜻 **아님** -- 각각 엔진 범용성 / 구조 설계 / BC 파이프라인 검증이라는 자체 가치 존재
2. 그러나 **"발견"이라는 단어로 프레이밍한 것이 부정확**했음 -- Rule #13 적용으로 분류 정교화

## 6. 향후 실험 체크리스트 (§8 재확인)

모든 후속 실험 보고는:
- [ ] 결과 trajectory 에 §1/§2/§3/§4 분류 레이블 명시
- [ ] `RubricEvaluator.evaluate()` 로 자동 판정 또는 수동 flowchart 답변
- [ ] "발견" 단어 사용 시 분류 레이블과 함께만

## 7. 한 줄 요약

**"E1은 엔진 구조 재생, E2는 코드 설계 패턴, E3는 noise band 근사. 어느 것도 v3 Rule #13의 §1/§2/§3 '발견' 아님. 하지만 각 실험은 다른 가치 (framework validation, structural insurance, BC feasibility 측정) 가 있었다."**
