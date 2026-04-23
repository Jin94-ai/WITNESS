# Pipeline v2 -- Full Spec Implementation Report (Phases A-F)

> **Spec**: [WITNESS_SPIKE_6_LEARNABLE_DATA.md](../../WITNESS_SPIKE_6_LEARNABLE_DATA.md)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/DATA_PIPELINE_v2_FULL_SPEC_COMPLETE.md`

## Lee의 원래 지시 (verbatim -- H5)

> "페이즈 전부 구현부터 하자"

## 내가 실행한 scope

Spec §9 세션 분리 권장은 Lee의 "전부 구현" 명시 지시로 override. 6 Phase 전부 한 세션 내 구현 + 통합 학습 + 평가.

## 축소한 지점

- 없음. Phase A/B/C/D/E/F 전부 구현.
- 단 Phase E는 spec §6.3 "선택적"에 따라 **구현만** 하고 데이터셋에 적용은 안 함 (Phase D FAIL 후 Lee 판단).
- Phase A는 data-driven 방식으로 **재설계**하여 구현 (v2/v3 비교 실증 반영).

---

## Spec / Rule 인용 (H3)

### Spec §3.2 verbatim

> *extended_features = [fear, hope, ..., trust_scar, recent_event_id, time_since_event, hazard_proximity]*

→ Phase B 구현 (15-dim).

### Spec §4.2 verbatim

> *baseline: ≤ 50% / forced sampling (Phase A): ≥ 50%*

→ Phase C: natural 36% / forced 64% (cap 통과).

### Spec §4.4 verbatim

> *data/person/pipeline_v2/ balanced_for_training/ / raw_natural/*

→ 이중 저장 구현.

### Spec §5.2.1 verbatim

> *기준: 0.6 이상이면 '학습 가능한 데이터'*

→ Phase D 측정: 0.509 (FAIL).

### Spec §5.2.2 verbatim

> *평균 consistency > 0.7 이면 학습 가능*

→ Phase D 측정: 0.439 (FAIL).

### Spec §6.3 verbatim

> *Phase A-D만으로 separability test 통과 시 Phase E 생략 가능. 과도하게 noise 추가하면 오히려 학습 방해. Lee 판단으로 진행 여부 결정.*

→ Phase E 구현만, 적용은 Lee 판단.

### Spec §7.2.2 verbatim

> *1회차 KL 1.44 대비 개선 여부*

→ v4 KL 1.066 (**개선**).

### Spec §7.2.3 verbatim

> *F1=0이었던 4개 action (weep, fall_asleep, follow_at_distance, run_to_tomb)이 F1 > 0 으로 바뀌었는가*

→ weep 0.82, fall_asleep 0.62, follow_at_distance 0.61, run_to_tomb n=2로 통계 부족.

---

## 수치 결과

### Phase별 산출물

| Phase | 산출물 | 상태 |
|---|---|---|
| A (재설계) | `data_driven_zones.py` + `zones.json` (13 actions from 916 natural samples, k_std=1.2) | 구현 완료 |
| B | `extended_features.py` (EVENT_VOCAB 32항, state_to_extended_feature_vector 15-dim) | 구현 완료 |
| C | `build_final_v2_dataset.py` (raw_natural 4524, forced_data_driven 3600, balanced_for_training 5621 with natural 36%) | 구현 완료, ratio 통과 |
| D | `separability_check.py` + `docs/person/diagnostics/separability_v2.md` | 구현 완료, **측정 FAIL** |
| E | `boundary_noise.py` (near_sigma=0.8 / far_sigma=0.2, threshold=3.0) | 구현만, 적용 없음 |
| F | `phase_f_train_eval.py` + `peter_bc_v4.pt` + `stage2_v4_evaluation.json` | 구현 완료, v4 저장 |

### v4 (Phase A-F full) 결과

| 지표 | 값 | null hypothesis | 기각 증거 |
|---|---:|---|---|
| Val accuracy | 0.541 | majority 0.107 → acc ≤ 0.11 | +43%p |
| NLL | 1.030 | log(15)=2.71 uniform | 62% below uniform |
| Macro F1 | 0.487 | random 0.067 | — |
| F1 ≥ 0.5 count | 8/15 | — | flee 0.99 / deny 0.94 / weep 0.82 / stay_hiding 0.79 / draw_sword 0.70 / fall_asleep 0.62 / follow_at_distance 0.61 / stay_awake 0.58 |
| F1 = 0 count | 2/15 | — | confess n=2, run_to_tomb n=2 (support 통계 부족) |

### Fidelity 비교 (자연 trajectory 10 seeds × 200 tick)

| Metric | v2 | v3 | **v4** |
|---|---:|---:|---:|
| Overall match | 0.394 | 0.042 | **0.280** |
| Voluntary match | 0.300 | 0.051 | 0.156 |
| Event match | 0.880 | 0.000 | **0.920** |
| Voluntary KL mean | 1.396 | 10.522 | **1.066** |

**v4**:
- Spec §7.2.2 KL target < 1.44 **통과**
- Event match 0.92로 v2 대비 개선
- Voluntary match는 v2 대비 **역행** (0.30 → 0.16)

### Phase D (FAIL 상세)

| Metric | Value | Target | Pass |
|---|---:|---:|:---:|
| Linear 5-fold CV acc | 0.509 ± 0.082 | ≥ 0.6 | ✗ |
| In-cluster consistency mean | 0.439 | > 0.7 | ✗ |
| Consistency range | [0.21, 0.98] | — | — |

Spec §5.3 처방:
- Linear < 0.6 → "Phase A 재실행, target state 재설계"
- Consistency < 0.7 → "Phase B (event context feature) 강화"

이 처방은 모두 **이미 수행한 작업** (data-driven zone + event feature 추가). 즉 spec의 처방 그대로 해도 동일 데이터에서는 더 개선할 여지 없음.

### 수치 해석 제약 (H1)

- **v4가 "학습 가능한 데이터"라고 주장 가능**: KL 1.066 + macro F1 0.487 + 8/15 F1 ≥ 0.5 + rare action 3/4 구제. 하지만 spec §5.2 기계 기준은 FAIL.
- **"Spec 기준 통과"가 아니라 "부분 개선"**: Phase D FAIL은 데이터 자체의 구조적 한계 시사. Spec의 기계 기준 자체가 이 content/engine 조합에서는 과도할 수 있음.
- **Voluntary match 역행**은 경고 신호: extended feature가 voluntary에서 placeholder(event_id='voluntary')라 noise로 작용했을 수 있음.
- **Rare action 구제는 진짜 개선**: 1회차 F1=0이었던 4개 중 3개가 F1 > 0.6 도달. 이는 data-driven zone + event feature의 실질 기여.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **Phase D FAIL의 진짜 원인 불확실**. 데이터가 진짜 학습 불가 구조인가, 아니면 feature 해상도 부족인가? domain_state를 주입해보지 않아 확신 못 함. 해보지 않은 이유: spec §0.2 명시 금지.
- [ ] **Voluntary match 0.156은 모델이 voluntary를 잘못 학습한 증거**. event feature가 voluntary 상황에서 placeholder라는 구조적 결함. Event-aware + 12-dim fallback으로 split 학습했어야 할 가능성.
- [ ] **Phase E 미적용 상태**. D FAIL 후 spec §6.3은 "Lee 판단"이라 적용 보류. 적용했다면 consistency 개선 가능성 있으나 val accuracy 악화 위험도 있음.
- [ ] **run_to_tomb/confess F1=0은 support=2라 fair metric 아님**. 학습 실패가 아니라 val split에서 아예 한두 개만 배정됐을 가능성. training support는 100 이상일 것.
- [ ] **15-action vocab이 Phase A ext의 21보다 작음**. data-driven zone에서 stay_hiding n=86만 있어 forced는 없음, confess n=11 forced 없음. Scene-01/05/15 actions (join_crowd 등 6개)는 자연 발생 0이라 아예 zone 추출 안 됨.
- [ ] **Fidelity 측정의 편향**. natural trajectory 307 samples는 같은 10 seeds × 200 tick에서 반복 추출. 다른 seed 범위에서는 결과 다를 수 있음.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| Phase E (boundary noise) 실제 적용 | spec §6.3 "Lee 판단". 기계적으로 D FAIL이지만 적용 전/후 val_acc 비교 안 함 | 미시도 (Lee 판단 대기) |
| domain_state 주입 (Literal categorical features) | spec §0.2 명시 금지 | 금지 |
| Class-weighted CE loss | spec §0.2 명시 금지 | 금지 |
| Mode splitting (voluntary model + event model 분리 학습) | 복잡도. 기본 단일 MLP로 Phase F 완료 | 미시도 |
| v4 MLP를 실제 simulation에 주입 (behavior 관찰) | 별도 Lee 판단 영역 | 미시도 |
| Extended feature를 continuous embedding으로 re-design | event_id를 scalar norm으로 encode, 더 나은 방법 있을 가능성 | 미시도 |

## Alternate interpretations (H4)

- **내 해석**: Phase 전부 구현 완료. v4는 Spec §7.2.2 KL 목표는 달성, spec §5.2 separability 기계 목표는 FAIL. Mixed result.
- **대안 해석 1**: **Phase D FAIL은 근본적 데이터 한계 신호**. spec §0.2가 금지한 feature 확장 없이는 이 기준선을 못 넘을 가능성. 그러면 Phase E, Phase F 재조정 모두 한계.
- **대안 해석 2**: **spec §5.2의 "target 0.6"이 15-action 문제에는 비현실적**. 6-voluntary만 놓고 보면 pipeline v1 baseline이 linear 0.3에도 못 미쳤음. 기준 자체가 "더 나은 데이터"의 조건이지 "지금 학습 가능"의 조건은 아닐 수 있음. Lee 감각 판단 기준 (spec §5.4) 에서는 v4가 의미 있는 개선.
- **대안 해석 3**: **Voluntary match 역행이 결정적**. v2가 0.30이었는데 v4가 0.16이면 extended feature 추가가 역효과. Phase B 전체 철회 검토 필요. Event match 개선 (0.88 → 0.92)은 미미.
- **대안 해석 4**: **v2 대비 v4의 순 개선은 rare action 구제만**. Spec 기준 통과 아니어도 Lee의 "pray, assert_loyalty, weep를 학습할 수 있나"라는 초기 걱정은 부분 해소. weep 0 → 0.82가 증거.

**내 bias 고백**:
- 나는 **대안 해석 2 + 4**에 기울었음. v4가 "spec 기준 FAIL이지만 실질 개선"이라는 프레임.
- 하지만 이 프레임 자체가 **패턴 1 재발 위험** ("수치를 편한 해석으로 돌림"). Phase D 처방이 명확히 FAIL인데 "기준이 비현실적"이라 돌리는 것은 정당화 방어.
- 정직한 선택지: (a) Phase D 기준을 인정하고 Phase A/B 근본 재설계, (b) "spec 기준 FAIL이지만 voluntary KL + rare action 구제"를 partial 성과로 인정하고 Phase F 결과 유지.

---

## Lee에게 판단 요청 (H6)

Phase 전부 구현 완료 시점의 선택지:

| 선택지 | 내용 | Trade-off |
|---|---|---|
| A | Phase E 적용 → 재학습 → D 재측정 | spec §6.3 "과도한 noise는 학습 방해" 위험 |
| B | Phase B 철회 (voluntary match 역행 근거) → 12-dim MLP 재학습 | rare action 구제 일부 손실 가능 |
| C | v4 그대로 "부분 개선"으로 수용 → Spike 6 종료 | spec §5.2 FAIL 상태 영구 기록 |
| D | spec §0.2 해제 (domain_state 주입) → Phase B 개선 재학습 | spec 경계 넘음, Lee 명시 허가 필요 |
| E | v4 MLP를 실제 simulation에 주입 → "천변만화" 여부 Lee 감각 판단 | fidelity 0.28 상태로 trajectory 비정상 가능성 |

**내 bias 고백**:
- **C 또는 E**로 기울었음. C는 honestly "부분 개선"으로 매듭, E는 Lee 감각 판단으로 결정.
- 이 bias가 패턴 7 (frame 선점) 가능성 — Lee 결정을 "끝내거나 / 시뮬레이션 보거나"로 좁힘.
- 모든 선택지 유효.

---

## HARNESS 자가감사 (H7)

1. **[H1]** trivial 기각? → **부분 기각**. 수치 개선이 있지만 spec 기계 기준은 FAIL.
2. **[H2]** 대안 3+? → **6개**
3. **[H3]** verbatim? → **Spec §3.2, §4.2, §4.4, §5.2.1, §5.2.2, §6.3, §7.2.2, §7.2.3 모두 verbatim 인용**
4. **[H4]** "What could still be wrong"? → **6개**
5. **[H5]** Lee verbatim? → **"페이즈 전부 구현부터 하자"**
6. **[H6]** equal weight + bias? → **5 선택지 + C/E bias 고백 + 패턴 7 위험 명시**
7. **좋은 소식만 아닌가?** → Phase D FAIL, Voluntary match 역행, 2개 F1=0 class 전부 명시. 내 Phase A ext bias 틀렸음을 이미 이전 세션에서 실증. v4도 "부분 개선"일 뿐 "천변만화" 아님.

---

## 산출물 (통합)

```
scripts/data_pipeline/
  extended_features.py                 (Phase B)
  data_driven_zones.py                 (Phase A 재설계)
  build_final_v2_dataset.py            (Phase C 통합)
  phase_f_train_eval.py                (Phase F)
  separability_check.py                (Phase D)
  boundary_noise.py                    (Phase E 구현만)
  (기존) forced_sampling.py, forced_events.py, fidelity_check.py

data/person/pipeline_v2/
  zones.json                           (data-driven zones from 30 seeds)
  raw_natural/                         (4524 samples, 15-dim)
  forced_data_driven/                  (3600 samples, 15-dim)
  balanced_for_training/               (5621 samples, natural ratio 36%)
  event_vocab.json                     (32 event vocabulary)

content/peter/trained/
  peter_bc_v4.pt                       (15-dim MLP)
  peter_bc_v4.feature_config.json

docs/person/
  diagnostics/separability_v2.md       (Phase D report)
  diagnostics/separability_v2.json
  stage2_v4_evaluation.json            (Phase F metrics)
  DATA_PIPELINE_v2_FULL_SPEC_COMPLETE.md (이 파일)
```

변경 없음:
- engine/ 0 수정 (Rule #6)
- content/ 기존 0 수정 (trained/ 하위 신규만)
- 기존 21 targeted tests green 유지
- ruff clean (line-length만 9개 warning, 기능 영향 없음)

---

## 세션 로그

### Session 5 (2026-04-22) -- Phase 전부 구현

**Lee 지시**: "페이즈 전부 구현부터 하자" — 스펙 §9 세션 분리 권장을 명시적 override. 한 세션에 A-F 구현.

**의존성 재배열**: B → A(재설계) → C → F → D → E 순서. B가 feature dim을 바꾸므로 A 재설계 선행 조건. F는 Phase B+A+C 통합 학습. D는 F 결과 평가. E는 D FAIL에 따라 구현만.

**가장 중요한 발견**: Phase D FAIL (Linear 0.509, Consistency 0.439). Spec §5.3 처방이 이미 수행한 작업이므로 동일 content/engine에서는 spec의 기계 기준 통과 어려움. Lee 감각 판단 (spec §5.4)이 실질 기준.

**Voluntary match 역행** (v2 0.30 → v4 0.16)은 경고 신호. Extended feature가 voluntary 상황에서 placeholder라 noise로 작용한 가능성. Phase B 재검토 필요성 기록.

**HARNESS 적용**: H4 banned phrase list 사용 안 함. Phase D FAIL을 숨기지 않고 전면 기록. Voluntary match 역행을 긍정적 결과 뒤에 숨기지 않음.
