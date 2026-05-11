# Pipeline v2 -- Phase A (Forced Action Sampling) 보고

> **Spec**: [WITNESS_SPIKE_6_LEARNABLE_DATA.md](../../WITNESS_SPIKE_6_LEARNABLE_DATA.md) Phase A (§2)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/DATA_PIPELINE_v2_PHASE_A.md` 통과 요구

## Lee의 원래 지시 (verbatim -- H5)

> "C:\Users\이진석\Desktop\Witness\WITNESS_SPIKE_6_LEARNABLE_DATA.md파일을 읽어보고 구현해서 학습할 수 있는 데이터를 만들어내보자"

## 내가 실행한 scope

- 스펙 Phase A (Forced Action Sampling) 구현 + quick sanity training
- Phase B-F는 본 세션 범위 밖

## 축소한 지점

- Lee 지시는 "학습할 수 있는 데이터" 전체. Spec §9가 "한 세션에 Phase A-F 전부 시도 금지"로 단계 분리 명시 → 나는 Phase A로 좁혔음
- Voluntary 6 action에만 집중 (canonical-event 9 action은 Phase A 범위 밖이라 자체 판단으로 남김)
- Lee 재확인 요청: 이 축소가 타당한지

---

## Spec / Rule 인용 (H3)

### Rule #6 verbatim (CLAUDE.md line 18)

> *"(v2.0) engine/ public interface 보존: world/는 engine/을 import만 한다. public API 시그니처를 깨지 않는 generic 확장만 허용"*

- **문구상 금지**: engine/ 내부 파일의 public API 시그니처 변경
- **문구상 금지 아님**: scripts/ 에서 engine 객체에 policy 주입, SimulationWorld 사용

### Spec §0.3 verbatim (WITNESS_SPIKE_6_LEARNABLE_DATA.md line 64)

> *"Rule #6 해석 명확화: engine 수정 금지이지만 scripts/ 에서 SimulationWorld state를 직접 patching하는 것은 허용. 이전 파이프라인에서 이를 회피해서 initial-state로 근사한 결과 rare action 실패. 이번에는 허용되는 범위 내에서 '난폭한 확충' (Gemini 지적) 가능."*

이번 구현은 spec §0.3의 **허용된** 범위 (forced policy를 SimulationWorld에 주입). engine/ 코드 0 수정 확인.

### Spec §5.2.1 Linear separability 기준

> *"기준: 0.6 이상이면 '학습 가능한 데이터', 0.6 미만이면 '데이터에 분리 가능한 구조 없음'"*

---

## 수치 결과

### Phase A 생성 데이터

| 지표 | 값 | null hypothesis | 기각 증거 |
|---|---:|---|---|
| 총 샘플 수 | 1,800 | — | — |
| Action 수 | 6 (voluntary) | — | — |
| 각 action 확보 | 300 | — | 거부 0 (100% 성공률) |
| 분포 균등성 | 완벽 (300/class) | — | — |
| Linear 5-fold CV acc | **0.880 ± 0.007** | "sampler가 action과 무관한 일관 state를 뽑아 임의 분리 가능" | forced policy가 weight-mask이므로 action은 정확히 target이지만 state는 zone에서 uniform sample. 무관하면 acc ≈ 1/6 ≈ 17%. 88% 관찰은 **state에 action-특이 signal 존재** 증거. |
| Random Forest feat importance top-5 | grief / hope / love / confusion / fear | "uniform random feature = uniform importance" | uniform이면 importance ≈ 1/12 ≈ 0.083. grief=0.24로 3배 초과 → importance 불균등 실존 |

### MLP sanity training (Phase A 내부 — Phase F 아님)

1800 samples × stratified train 1440 / val 360, MLP(12→32→32→6), 50 epoch lr=1e-2 early stop patience 10:

| 지표 | 값 |
|---|---:|
| Val acc (best) | 0.944 |
| Majority baseline | 0.167 (1/6) |
| 초과분 | **+77.7 %p** |

Per-class F1 (val):

| Action | F1 | Precision | Recall |
|---|---:|---:|---:|
| weep | 1.000 | 1.000 | 1.000 |
| withdraw_in_fear | 1.000 | 1.000 | 1.000 |
| pray | 0.984 | 0.968 | 1.000 |
| follow_closely | 0.881 | 0.980 | 0.800 |
| assert_loyalty | 0.877 | 0.814 | 0.950 |
| discuss_with_disciples | 0.857 | 0.864 | 0.850 |

### 수치 해석 제약 (H1)

- **이 수치가 의미하는 것**: Phase A가 만든 forced dataset은 linear classifier로 88% 분리 가능 + MLP로 94% 학습 가능 == spec §5.2.1의 "학습 가능한 데이터" 문턱 통과.
- **이 수치가 의미하지 않는 것**:
  - 이 모델을 실제 Peter 시뮬레이션에 주입 시 engine과 일관된 행동을 한다는 보장 없음 (simulation-in-the-loop 검증 미실시)
  - 이 MLP는 **6 voluntary action만** 예측 가능. 전체 15 action (canonical 9 포함) 분류는 아직 불가
  - Phase A의 MLP가 실제 engine과 bit-identical하게 선택한다는 증명 아님 — forced dataset은 forced 결과이고, rule-based 자연 선택과 분포가 다를 수 있음
- **falsification criterion**:
  - 이 데이터가 정말 학습 가능하다면, **동일 state에 대해 동일 action이 나와야** (consistency >= 0.7). 이번 측정에는 consistency test 미포함 → 다음 세션 Phase D 대상.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **Forced MLP vs rule-based engine divergence 미측정**. 이 모델을 SimulationWorld에 주입하면 엄청 다른 trajectory를 만들 수 있음. KL divergence vs rule-based 같은 behavior fidelity metric이 spec §7.2.2에 있는데 이번에 측정 안 했음.
- [ ] **Canonical event 9 action 0 샘플**. deny, draw_sword, flee, fall_asleep, stay_awake, stay_hiding, follow_at_distance, run_to_tomb, confess — 이들은 event가 발동해야 등장. ForcingPolicy로 event option에도 강제 가능한지 미검증. 이번 Phase A scope 밖이었음.
- [ ] **Overfitting 가능성**. MLP train acc 0.947 vs val 0.944 — 거의 일치. 하지만 1800 sample × 12 feature × 6 class에서 MLP 1637 파라미터가 table lookup처럼 외웠을 수도 있음. consistency test + unseen state generalization test 미실시.
- [ ] **Forced state가 engine의 자연 상태와 다른 분포일 가능성**. zone에서 uniform 샘플 → 실제 simulation에서 fear=9+hope=1+love=1 같은 combination이 자연스럽게 등장하는가? 만약 거의 등장 안 하면 학습된 모델이 "실제 Peter가 마주칠 state"에서는 여전히 majority 반환할 수 있음.
- [ ] **Preconditions 100% pass → 거부 0**은 zone 정의가 precondition을 포함하게 짰기 때문. 더 극단 zone (precondition 경계 넘어)에서는 거부 발생할 수 있지만 검증 안 했음.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도 / 불가능 |
|---|---|---|
| Canonical event 9 action forced sampling | event-triggered action은 event 발동 조건이 별도. spec §2.2.1가 voluntary 예시만 명시, Phase B 이후 작업으로 위임 | 미시도 (시간/scope 이유) |
| Simulation-in-the-loop behavior fidelity (spec §7.2.2 KL) | Phase F 작업. 여기는 Phase A sanity만 | 미시도 |
| Consistency test (동일 state → 동일 action) | Spec §5.2.2. Phase D 소관 | 미시도 |
| Zone 경계 sweep (precondition 경계선 실험) | 거부 0이었으므로 급하지 않음. 추후 지루성 검사 가치 있을 수 있음 | 미시도 |
| Rule-based weight distribution과 forced distribution 직접 비교 | 구현 가능하지만 이번은 "학습 가능한지"에 집중 | 미시도 |

5개 나열 — H2 만족.

## Alternate interpretations (H4)

- **내 해석**: Phase A가 만든 데이터는 "학습 가능한 데이터"의 spec §5.2.1 문턱을 통과. MLP가 94% val acc에 도달한 건 **data가 실제로 signal 갖고 있음** 증거.
- **대안 해석 1**: **ForcingPolicy가 만든 데이터는 토톨로지(tautology)다**. 우리가 "이 zone의 state이면 이 action을 강제했다" → MLP가 그 매핑을 학습. 즉 engine의 자연 behavior가 아니라 내가 선언한 매핑을 학습한 것. rule-based engine과 비교 없이는 "학습했다"는 말이 공허할 수 있음.
- **대안 해석 2**: zone 정의가 이미 action별로 분리 가능한 공간을 **인위적으로** 잘랐으므로 separability 0.88은 **spec 따른 결과**이지 engine의 학습 가능성 증명은 아님. 극단 케이스: 각 action을 one-hot feature로 라벨하면 linear acc 1.0이 나오겠지만 학습이 아님.
- **대안 해석 3**: 이 데이터로 학습한 MLP를 실제 시뮬레이션에 넣으면 engine과 거의 같은 선택을 할 것이다 (rule-based weight formula와 zone boundary가 일치하므로). 그렇다면 "새로운 것을 학습"했다기보다 "rule을 복제"했을 뿐. 좋은 copying이지만 "천변만화"는 아님.

**내 bias 고백**: 나는 "대안 해석 1+3"이 부분적으로 맞다고 생각하며 "내 해석"보다 덜 강한 claim이 정직하다. 즉 "이 데이터는 학습 가능하지만, 학습 대상이 engine이 아니라 spec 작성자의 zone 정의"일 가능성이 높다. Phase D consistency + Phase F simulation-in-the-loop에서 검증 필요.

---

## Lee에게 판단 요청 (H6)

Phase B-F 진행에 관한 4 선택지 (equal weight):

| 선택지 | 장점 | 단점 | trade-off |
|---|---|---|---|
| **A** Phase B (Event context feature) | event-triggered action 9개 해결 단서 | Rule #6 범위 확장 검토 필요 (recent_event_id tracking은 engine 참조 필요) | 기술적으로 복잡 |
| **B** Phase D (Separability check) | 데이터 품질을 수치로 재검증. 내 대안 해석 1+3을 검증 | 수치 통과해도 Phase F 안 하면 최종 증명 아님 | 낮은 비용, 낮은 최종 가치 |
| **C** Canonical event 9 forced sampling | voluntary 6만 있으면 전체 15 action 학습 불가. 이거 해야 "완전" | ForcingPolicy가 event option에서도 작동하는지 별도 검증 필요 | 중간 비용, 높은 가치 |
| **D** Phase F만 바로 (기존 6821 + 1800 merge 후 재학습) | 전체 그림 빨리 확인 | Phase B-C 건너뜀으로 "왜 좋아졌는지" 분리 불가 | 높은 위험 |

**내 bias 고백**:
- 나는 **C**에 기우는데 이유는 voluntary 6만으론 15 action 전체 분류 불가능하고, Phase A에서 확인된 forced-sampling 메커니즘이 event-option에도 동일하게 작동할 가능성이 높기 때문
- 하지만 이 bias는 "양적 확장"을 우선하는 경향으로, spec §0의 "양이 아니라 학습 가능성"과 긴장할 수 있음
- 이 bias가 Lee 결정을 편향시킬 수 있음 — Lee가 B(separability 재검증)를 선호한다면 내가 overclaim 하지 않도록 그쪽이 안전

---

## HARNESS 자가감사 (H7)

1. **[H1]** 이 수치를 trivial로 설명 가능? 기각?
   → **부분 기각**. "88% linear = engine signal" 해석은 1+3 대안에서 반박됨. "94% MLP = 학습" 해석은 overfitting 가능성 남음. 완전 기각 아님.
2. **[H2]** 시도 안 한 대안 3개 이상?
   → **5개 나열**
3. **[H3]** 인용한 Rule/spec verbatim?
   → **Rule #6 + Spec §0.3 + §5.2.1 verbatim 인용 완료**
4. **[H4]** "What could still be wrong" 작성?
   → **5개 작성**
5. **[H5]** Lee 원래 지시 verbatim 보존?
   → **yes**
6. **[H6]** 선택지 equal weight + bias confession?
   → **4 선택지 제시 + C bias 고백**
7. **이 보고서가 좋은 소식만 전달하고 있지 않은가?**
   → **대안 해석 섹션이 내 해석을 부분적으로 기각**. MLP overfit 가능성, tautology 가능성, rule copying 가능성 전부 명시. Lee가 반박 가능한 지점 다수.

---

## 산출물

```
scripts/data_pipeline/
  forced_sampling.py                 (신규, 260 lines)
  _common.py                         (run_peter_with_policy helper 추가)

data/person/pipeline_v2/
  forced/
    X.npy                            (1800, 12) float32
    meta.json                        (actions, per-action attempts/rejected)
```

변경 없음:
- engine/ 0 수정
- content/ 0 수정
- 기존 1081 engine + 216 타겟 tests green 유지
- ruff/mypy clean

---

## 세션 로그

### Session 1 (2026-04-22) -- Phase A

**초기 실패 기록**: 첫 구현에서 `max_tick=1` + `extract_samples`로 0 샘플. 원인: `extract_samples`는 `tick < max_tick` 인 tick만 (state, action) 페어링. action은 tick=1에 기록되지만 tick=1은 `range(len(ticks) - 1)`에서 제외됨. 수정: action_records를 직접 읽고 snapshot[1]을 state로 페어링.

이 초기 실패가 있어서 spec §1 진단 "forced action은 weight-mask로 100% 달성"이 구현 레벨에서 "sample 추출 방법"과 별개 문제임을 재확인. Phase 1 진단은 메커니즘만 확인, 추출 logic은 별도.

**성공 후 결과**: 1800 샘플, 거부 0, 1.76s (50/action) → 8.4s (300/action).

---

**다음 세션 시작 시 확인**: 이 보고의 "Lee에게 판단 요청" 섹션에서 B/C/A/D 중 선택. 없으면 C (canonical event 확장) 기본 선택.
