# Pipeline v2 -- Phase A Extension (Event actions) + Fidelity Check

> **Spec**: [WITNESS_SPIKE_6_LEARNABLE_DATA.md](../../WITNESS_SPIKE_6_LEARNABLE_DATA.md)
> **Previous**: [DATA_PIPELINE_v2_PHASE_A.md](DATA_PIPELINE_v2_PHASE_A.md)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/DATA_PIPELINE_v2_PHASE_A_EXT.md`

## Lee의 원래 지시 (verbatim -- H5)

> "C:\Users\이진석\Desktop\Witness\WITNESS_SPIKE_6_LEARNABLE_DATA.md파일을 읽어보고 구현해서 학습할 수 있는 데이터를 만들어내보자"

## 내가 실행한 scope

- Phase A에서 **voluntary 6 action**만 커버 → 이번 세션에서 **canonical-event 15 action 확장**
- 합쳐서 21-action forced dataset (6300 samples) 구축
- MLP 학습 + **simulation-in-the-loop fidelity 측정** (이전 보고서의 alternate interpretation 1+3 직접 검증)

## 축소한 지점

- Lee 명시 선택(A/B/C/D) 없었음. 이전 보고서에서 내가 고백한 **bias C (canonical event)** 그대로 진행
- 이 bias 진행이 Lee 의도와 다를 수 있음 -- Phase B (event context feature) 또는 Phase D (separability 재검증)를 Lee가 원했다면 이번 세션 방향이 어긋남

---

## Spec / Rule 인용 (H3)

### Spec §0.3 verbatim

> *"Rule #6 해석 명확화: engine 수정 금지이지만 scripts/ 에서 SimulationWorld state를 직접 patching하는 것은 허용."*

이번 확장은 `decide_action(options, policy=ForcingPolicy)`를 직접 호출. Simulation loop 없이 순수 (state, action) 페어 생성. `scripts/` 수준 작업이므로 Rule #6 문구 안.

### Spec §5.2.1 Linear separability 기준

> *"기준: 0.6 이상이면 '학습 가능한 데이터', 0.6 미만이면 '데이터에 분리 가능한 구조 없음'"*

---

## 수치 결과

### Event-action forced sampling (신규 모듈)

| 지표 | 값 |
|---|---:|
| 샘플 수 | 4,500 |
| Action 수 | 15 (canonical-event) |
| 각 action 확보 | 300 (거부 0) |
| 실행 시간 | 1.7s |

### 통합 v3 dataset (voluntary 6 + event 15 = 21-action)

| 지표 | 값 | null hypothesis | 기각 증거 |
|---|---:|---|---|
| 총 샘플 | 6,300 | — | — |
| Linear 5-fold CV acc | **0.803** | "21 랜덤 class = 4.8% acc" | +75.5%p → 기각 (zone-내) |
| RandomForest 5-fold CV | **0.979** | — | — |
| MLP val_acc (80 epoch) | **0.888** | majority 1/21 = 4.8% | +84%p (zone-내) |
| Macro F1 | **0.875** | — | — |
| F1 ≥ 0.5 class | **21/21** | — | 1회차에서 F1=0이었던 4개 action (weep, fall_asleep, follow_at_distance, run_to_tomb) 전부 구제 |

### ⚠ Simulation-in-the-loop fidelity check (**중심 결과**)

**이것이 이전 보고서 §Alternate interpretations의 tautology risk를 직접 검증한 결과**:

v3 MLP에 **자연 Peter trajectory state** (10 seeds × 200 tick canonical run에서 수집한 307개 실제 state)를 입력해 예측. engine의 실제 action과 매치율 측정:

| 지표 | 값 |
|---|---:|
| **MLP vs engine match rate** | **0.042 (13/307)** |
| Majority predictor baseline | 0.52 (follow_closely 160/307) |

**MLP가 4.2% 매치**. Random 21-class predictor (4.8%) 수준. Majority predictor보다 **12배 나쁨**.

Per-class match 분포:

| Action | match / total | rate |
|---|---:|---:|
| weep | 6 / 6 | 100% |
| discuss_with_disciples | 6 / 34 | 17.6% |
| withdraw_in_fear | 1 / 18 | 5.6% |
| follow_closely | 0 / 160 | 0.0% |
| pray | 0 / 30 | 0.0% |
| deny | 0 / 30 | 0.0% |
| (그 외 6 action) | 전부 0 | — |

### 수치 해석 제약 (H1)

- **이 수치가 의미하는 것**:
  - Zone-내 val_acc 0.888은 **forced dataset 내부 일반화 능력** 측정
  - Fidelity 0.042는 **engine behavior 재현 능력** 측정 -- 서로 다른 것을 잰 두 수치
- **이 수치가 의미하지 않는 것**:
  - val_acc 0.888이 "Peter가 engine처럼 행동하는 모델"을 의미하지 **않음**
  - "21/21 F1 ≥ 0.5"가 "실제 Peter 시뮬레이션 품질 개선"을 의미하지 **않음**
- **실증된 null hypothesis**:
  - 이전 보고서 §Alternate interpretations 1+3 ("tautology" / "rule copying")이 **부분적으로 참**임이 확인됨
  - MLP는 zone 정의 자체를 학습. zone 정의가 engine의 자연 state 분포와 겹치지 않으므로 engine과 divergent
- **weep 100% match + discuss 17%는 부분 신호**: 일부 zone 정의는 자연 분포와 겹치지만 대부분은 아님

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **Zone 정의가 단순히 "틀렸다"** -- engine의 실제 weight_formula이 만드는 natural 분포와 일치하지 않음. weight_formula 역분석으로 engine이 실제로 각 action을 선택하는 state 분포를 먼저 뽑은 뒤 그 분포에 맞춰 sample해야 했음. 내가 "어디서 이 action이 자연스러운가"를 추측으로 정함.
- [ ] **forced_event는 simulation loop 없이 decide_action 직접 호출**이라 rule_engine 적용 없음. Phase A는 1-tick simulation을 거쳤으나 Phase A ext는 더 인위적. 두 샘플 세트가 동질적이지 않음.
- [ ] **Fidelity 자체도 편향된 지표일 수 있음**. engine이 자연 follow_closely 160/307을 내는 이유는 majority base_weight 때문. MLP가 자연 state에서 다른 action을 선택한다면 "engine보다 다양하게 행동"하는 것이지 반드시 나쁜 것은 아님. 어느 쪽이 옳은지는 Lee 판단 영역.
- [ ] **v3 model은 저장됐지만 실제 배포 검증 안 함**. `SimulationWorld(policies={"peter": NeuralDecisionPolicy(v3)})`로 돌려서 Peter의 trajectory가 어떻게 바뀌는지 관찰 안 됨.
- [ ] **21-class separability 0.803도 overfitting일 수 있음**. CV지만 zone이 action별로 분리된 공간에서 sample했으므로 cross-validation조차 zone 경계 학습 반복. 진정한 held-out은 natural state인데 거기서는 4.2%.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| Engine weight_formula 역분석으로 자연 state 분포 뽑기 | 시간. 한 세션에 Phase A-F 전부 금지 원칙 따라 다음 세션 이후 | 미시도 |
| forced_event에도 1-tick simulation 적용 (Phase A와 동질화) | event는 특정 tick에만 발동. event_scheduler 조작 없이는 어려움 | 미시도 |
| MLP로 실제 Peter simulation 돌려보기 (v3 체크포인트 배포 실험) | spec Phase F 영역. 이번 scope 밖 | 미시도 |
| Engine match rate 대신 KL divergence (behavior fidelity metric) | 계산 복잡. 우선 match rate만 측정 | 미시도 |
| Phase B (event context feature) 선행 -- temporal 정보 추가로 event action 구분 강화 | 이번 C bias에 밀려 | 미시도 |
| Boundary zone을 data-driven으로 생성 (baseline harvest에서 각 action 자연 발생 state 평균 + variance) | 아이디어 뒤늦게 떠오름 | 미시도 |

## Alternate interpretations (H4)

- **내 해석**: Phase A ext의 val_acc 0.888은 "학습 가능성" 측면에서 성공, fidelity 0.042는 "engine fidelity" 측면에서 실패. 두 해석을 동시에 유지해야 함.
- **대안 해석 1**: **Fidelity 0.042가 결정적 기각**. val_acc 0.888은 tautology 증명일 뿐 "학습 가능한 데이터"는 **여전히 만들지 못함**. Phase A ext 전체가 잘못된 접근.
- **대안 해석 2**: **Fidelity가 낮아도 괜찮을 수 있음**. Spec §0.1 "같은 상태에서 다른 행동 = noise, 다른 상태에서 다른 행동 = 학습 가능". Forced dataset은 후자 구조를 가짐. Engine fidelity는 "engine 복제" 목표일 때만 중요하며 spec §12 "천변만화"는 engine 복제가 아닐 수 있음.
- **대안 해석 3**: Zone 정의 자체가 **나의 이론 (weight_formula 읽고 추측)**의 테스트. 4.2%는 "내 이론이 engine을 정확히 예측 못 함"을 의미. Engine의 실제 분포에서 zone을 data-driven으로 다시 뽑으면 fidelity 개선 가능. 즉 Phase A ext의 실패가 아니라 내 zone 설계의 실패.

**내 bias 고백**: 나는 **대안 해석 1**에 기우는데 그 이유는 패턴 1-7 교훈상 "val_acc 개선 → 본질 개선" 착각을 반복하지 않기 위함. 하지만 이 bias가 대안 해석 2를 과소평가할 수 있음 (Lee의 "천변만화" 의도가 engine 복제가 아니라 더 광범위한 행동 공간 학습일 수 있음).

---

## Lee에게 판단 요청 (H6)

이번 세션 fidelity 4.2% 발견 이후 선택지:

| 선택지 | 장점 | 단점 | trade-off |
|---|---|---|---|
| **A** 대안 해석 1 수용 → Phase A ext 폐기, 자연 state-driven zone으로 재설계 | Fidelity 회복 목표. engine 재현 능력 복귀. | Phase A의 1800 + ext의 4500 작업 폐기. 시간 손실. |
| **B** 대안 해석 2 수용 → fidelity 낮아도 OK로 보고 Phase F 진행 | "천변만화" 해석 수용. Lee가 실제로 MLP Peter를 돌려보고 판단. | Lee 판단 전까지 방향 불확실. |
| **C** Phase B (event context feature) 우선 → temporal/event 정보 추가로 fidelity 개선 시도 | 근본 원인 중 하나 (12-feature aliasing) 해결 | 새 feature가 fidelity 회복할지 불확실 |
| **D** Data-driven zone 재설계 → baseline harvest에서 각 action의 실제 state 분포 학습 후 거기서 sample | 대안 해석 3에 따라 zone 문제 직접 해결. 가장 logical. | Phase A 설계 전부 재작업 |

**내 bias 고백**:
- 나는 **D** (data-driven zone 재설계)에 기울었음. 근거: 대안 해석 3이 가장 실행 가능한 경로. 일부 자산 (1800 voluntary 샘플은 zone이 weep/withdraw에서 자연 분포와 겹침이 확인됨) 재활용 가능.
- 하지만 이 bias는 "양적 iteration을 반복"하는 경향. Lee가 B(fidelity 무시, simulation 실제 돌려보기)를 선호한다면 더 빠른 답 가능.
- "안전한 default"를 내 맘대로 정하지 않음 -- 4 선택지 모두 유효.

---

## HARNESS 자가감사 (H7)

1. **[H1]** 이 수치를 trivial로 설명 가능? 기각?
   → **부분만 기각**. val_acc 0.888 = tautology 가능성 실증됨 (fidelity 4.2%). zone-내 학습 가능성은 확인, engine 재현 가능성은 **실증 실패**.
2. **[H2]** 시도 안 한 대안 3개 이상?
   → **6개 나열**
3. **[H3]** 인용한 Rule/spec verbatim?
   → **Spec §0.3 + §5.2.1 verbatim 인용**
4. **[H4]** "What could still be wrong" 작성?
   → **5개 작성**
5. **[H5]** Lee 원래 지시 verbatim 보존?
   → **yes** (응답 상단)
6. **[H6]** 선택지 equal weight + bias confession?
   → **4 선택지 + D bias 고백**
7. **이 보고서가 좋은 소식만 전달하고 있지 않은가?**
   → **Fidelity 4.2%가 주 결과로 전면 배치**. val_acc 0.888 단독 해석 금지 명시. 이전 보고서의 tautology risk가 실증됐음을 Lee가 볼 수 있도록.

---

## 산출물

```
scripts/data_pipeline/
  forced_events.py                   (신규, 230 lines)

data/person/pipeline_v2/
  forced_events/
    X.npy                            (4500, 12)
    meta.json
  forced_merged/                     (voluntary + event 통합)
    dataset.npz                      (X 6300×12, y 6300)
    meta.json                        (action_vocab 21)

content/peter/trained/
  peter_bc_v3.pt                     (21-action MLP 가중치, 저장됨)
  peter_bc_v3.feature_config.json
```

변경 없음:
- engine/ 0 수정 (Rule #6 준수)
- content/ 0 수정 (trained/ 하위 신규 파일만)
- 21 engine + 216 타겟 tests green 유지
- ruff clean

---

## 세션 로그

### Session 2 (2026-04-22) -- Phase A ext

**Phase A ext 성공**: 4500 samples, 15 action 전부 300 확보, 거부 0. 메커니즘 `decide_action(options, policy=ForcingPolicy)` 직접 호출로 100% 작동 (smoke에서 denial event로 20/20 검증).

**통합 학습 결과 양가적**:
- Zone-내 지표 모두 좋음 (Linear 0.803 / RF 0.979 / MLP 0.888 / 21/21 F1≥0.5)
- Simulation-in-the-loop fidelity **4.2%**

**가장 중요한 발견**: 이전 보고서의 alternate interpretation 1+3 (tautology / rule copying)이 실제로 실증됨. MLP는 내가 정의한 zone을 학습했지만 engine의 자연 state 분포와 zone이 일치하지 않음.

**이것이 HARNESS를 실제로 쓴 결과**: fidelity check를 "성공 보고" 다음 자리에 넣지 않고 주 결과로 배치. 1회차 실수 (val_acc를 "진짜 학습" 근거로 쓴 것) 반복 회피.
