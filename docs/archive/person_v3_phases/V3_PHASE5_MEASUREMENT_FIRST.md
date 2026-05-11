# v3 첫 실측 보고 -- Peter scenario 30-tick run

> **Spec**: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md + WITNESS_V3_REDESIGN.md §6
> **Code**: `engine/person/loop.py`, `scripts/v3_measurement/run_peter_v3.py`
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/V3_PHASE5_MEASUREMENT_FIRST.md`

## Lee의 원래 지시 (verbatim -- H5)

> "다음페이즈 진행하자. 내가 생각하는 방향에서 크게 벗어나지 않으면 쭉쭉 진행해서 실측까지 진행해보자"

## 내가 실행한 scope

- Content JSON 3개 (Peter v3 initial_state / targets / canonical_events)
- `engine/person/loop.py` — v3 pipeline 통합 (Event → Primitive → Pressure → Policy → Action → Event 폐루프)
- Rule-based policy 초안 (Active + Pressure 기반 weight formula)
- 1 seed × 30 tick simulation 실행
- RubricEvaluator 통과 → `DiscoveryClass` 분류

## 축소한 지점

- Policy는 rule-based 단일 초안. 신경망 policy는 Spec §8 "Phase 5+ 별도 지시" 대기.
- Scale: 1 seed × 30 tick (가장 작게 시작). Multi-seed ensemble은 이번 scope 밖.
- Canonical events 11개 (수난 주간 핵심). 전체 50-day Peter arc 아님.
- Lee 감각 판단 ("살아 움직이는가") 은 이 보고서 이후 Lee 영역.

---

## Spec / Rule 인용 (H3)

### v2 §5 verbatim

> *"허용: action → event → external update"*

→ `_decide_action()` 후 `mapper.trigger_event_id(action_id)` 로 폐루프 실행. Rule #12 갱신판 준수.

### v2 §2.4 verbatim

> *"옵션 C 최종 채택: Pressure는 별도 저장 안 함. 매 tick 계산."*

→ `PressureLayer.compute()` 가 매 tick 호출, 별도 저장 없음 (Derived).

### Rule #13 (발견 3종)

> *"모든 실험 보고서는 결과가 위 3종 중 어느 것인지 명시해야 한다."*

→ 이 보고서 결과: **§4.2 NOT_DISCOVERY_NOISE**

---

## 수치 결과

### Simulation

| 지표 | 값 |
|---|---|
| Seed | 0 |
| Ticks | 30 |
| Canonical events fired | 11 tick 분 |
| Action distribution | `run_to_tomb:7, fall_asleep:3, follow_closely:3, assert_loyalty:3, pray:3, withdraw_in_fear:3, deny:2, confess:2, discuss:2, draw_sword:1, follow_at_distance:1` |

### 상태 궤적 (요약)

| 시점 | fear | grief | loyalty[primary_figure] |
|---:|---:|---:|---:|
| tick 1 | 3.0 | 0.5 | 9.8 |
| tick 10 (겟세마네) | 3.0 | 0.5 | 9.9 |
| tick 15 (1차 부인) | 3.5 | 0.5 | **9.4** (↓0.5) |
| tick 20 (eye contact) | 4.5 | 0.5 | 9.5 |
| tick 28 (restoration) | 6.4 | 0.5 | **9.1** (↓) |
| tick 30 (최종) | 6.9 | 0.5 | 9.1 |

### Rubric 결과

| Axis | 값 | 해석 |
|---|---|---|
| **DiscoveryClass** | **`not_discovery_noise`** (§4.2) | soft_drift > noise_threshold |
| Character composite | 0.800 | `character_min_composite=0.4` 상회 |
| Canon valid | True | hard violation 0 |
| Canon soft_drift | **28.50** | `noise_threshold=20.0` 초과 |
| Causal smoothness | 0.983 | unexplained_jumps 0 |
| Novelty band | `noise` | drift 28.5 > 20 |
| Justification | `"Step 4: drift=28.50 > noise_threshold → §4.2"` | flowchart step 4 |

### 수치 해석 제약 (H1)

- **"not_discovery_noise" 가 의미하는 것**:
  - 관찰 trajectory 가 canonical sequence 와 soft_drift 28.5 (Levenshtein + inversions)
  - spec §0.1 "같은 상태에서 다른 행동이 나오면 learn 불가" 쪽 — 즉 내 rule-based policy 가 state-sensitive 하지만 canonical 재현 실패
  - Claude 의 weight formula 가 canonical 을 재현하지 않음
- **"not_discovery_noise" 가 의미하지 않는 것**:
  - v3 pipeline 전체가 실패했다는 의미 **아님**. Pipeline 동작 (4 critic, 폐루프, 3 Layer 분리) 모두 작동.
  - Policy 를 "천변만화" 의 성공 사례라 할 수도 **없음**. 단순히 canonical 에서 멀리 벗어난 trajectory.
  - Rule-based policy 의 조정으로 §1 CANONICAL_REPRODUCTION 가능 가능성 있음 (아직 미시도).
- **검증되지 않은 전제**:
  - `soft_drift=28.5` 의 "큰지 작은지" 기준은 `copy_threshold=2.0`, `noise_threshold=20.0`. 내 임의.
  - 30 tick 길이 대비 11개 canonical 이벤트는 사건 밀도 과다. 초기 scale 미검증.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## 파이프라인 동작 확인 (positive findings)

1. **폐루프 작동**: action → event → primitive → pressure → next decision 연쇄 실제 작동. 예: tick 13 `weapon_drawn_nearby` → volatility↑ → pressure 재계산 → tick 14 decision.
2. **Canonical events 11개 모두 fired**: sacred_meal (5), suffering_visible (10), guard_approaches (12), weapon_drawn (13), ally_departure (14), accusations (17-19), eye_contact (20), forgiveness (25), restoration (28).
3. **Action-caused events 작동**: tick 15 `deny` → `public_denial` event → primitives 갱신 확인.
4. **State direct edges 작동**: `loyalty[primary_figure]` 가 deny 시 −0.5, follow_closely 시 +0.1 로 반응.
5. **Rule #1/6/8/15-18 전부 green**: 277 기존 tests + v3 loop 통합 후 65 tests (test_integrity/person/world/action/rubric) all pass.

## 관찰된 이상 (policy tuning 필요)

- **`run_to_tomb` 7회** (전체 30 중 23%). 수난 중간 tick 11, 17, 18, 20, 23, 29, 30 에서 반복. `run_to_tomb` 는 부활 직후 1회 적합이지만 weight formula 에서 love+hope 가중으로 과다 선택.
- **`grief` 가 tick 내내 0.5 stuck**. Direct edge 로 grief 증가 조건 없음 (weep action 시 grief +0.5 만 있음). `weep` 이 한 번도 선택 안 됨.
- **canonical denial 3연속 (17/18/19) 을 `run_to_tomb`/`draw_sword` 로 대체**. Policy 가 canonical 압력 (accusation event) 를 denial 로 변환하는 neuron path 부재.

---

## What could still be wrong (H4)

- [ ] **Policy weight formula 는 내 임의 설계**. `0.2 * love_primary + 0.1 * loyalty_max` 같은 계수 근거 없음. v2 §11 "Lee 판단 필수" 의 "Pressure 계산식 검증" + "Action-Event 매핑 검증" 이 아직 안 됨.
- [ ] **Canonical sequence 9 events 선택도 임의**. 수난 주간의 핵심 action 을 (discuss/stay_awake/draw_sword/flee/deny×3/weep/confess) 으로 정의한 것은 Claude 추측. Lee 신학 검토 없음.
- [ ] **`character_composite=0.800`이 높아보이지만** 신뢰할 수 있는 수치 아님. CharacterCritic 의 3 요소 (impulsivity/relationship/oscillation) threshold 전부 내 임의. 실제 "베드로다움" 포착 근거 없음.
- [ ] **30 tick × 1 seed 의 표본 크기**. Noise band 판정이 이 seed 우연일 수 있음. Multi-seed ensemble 필요.
- [ ] **`grief` stuck at 0.5**: bug 가 아니라 내가 `_update_state_from_pressures_and_action` 에서 grief 로직 부족. 실측이 드러낸 policy 결함.
- [ ] **Rubric threshold 전부 내가 임의 설정** (copy 2.0, noise 20.0, character_min 0.4). 다른 threshold 에서는 다른 class 나올 것.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| Multi-seed ensemble (10+ seeds) | 첫 실측에 scale 우선순위 낮음. 다음 iteration | 미시도 |
| Policy weight 조정해서 `run_to_tomb` 억제 + `deny` 순서 맞추기 | threshold tuning — patterns 1/3 재발 위험 | 의도적 미시도 |
| `grief` update rule 추가 | policy 결함이 실측으로 드러남. Lee 피드백 후 수정 | 미시도 |
| Longer run (50-100 tick) | 30 tick 으로 수난 주간 dense events 포화. 긴 run 추가 가치 낮음 | 미시도 |
| Rubric threshold 조정 | §1/§2/§3 로 분류되게 바꾸는 건 self-deception (pattern 1 재발) | 금지 |
| Neural policy (Phase 5+) | spec §8 "Phase 5+ 별도 지시" | 금지 |

## Alternate interpretations (H4)

- **내 해석**: v3 pipeline 전체 정상 작동. 첫 실측 결과 `not_discovery_noise`. Rule-based policy 가 canonical 을 재현하지 않는 **솔직한 결과**. Pipeline 검증 완료, policy 품질은 미달.
- **대안 해석 1**: **"policy 결함으로 noise 됐다"가 낙관적 프레임**. 실제로는 Rubric threshold 선정 자체가 임의라 어떤 threshold 에서든 판정 가능. v2 §1.2 condition 4 (sensitivity) 미측정 — Active 20 선정이 과도할 수도.
- **대안 해석 2**: **grief stuck 은 파이프라인 결함**. State transition rules (v2 §6 direct edges) 의 대부분 구현 안 됨 (tick 당 약 5 regle 만). Pipeline "작동" 은 pipeline "완성" 아님.
- **대안 해석 3**: **첫 실측 성공 자체가 lesson 42 패턴 1 재발 가능성**. "30 tick 돌렸다 = 검증 끝났다" 프레임 위험. 실제로는 1 seed × 30 tick 단일 관측일 뿐.

**내 bias 고백**:
- 나는 **내 해석 + 대안 해석 2** 가 가장 정확하다고 봄.
- "파이프라인 통합 + 실측 루프 닫힘" 은 달성. 다음 단계 (policy tuning, state transition 완성, multi-seed) 는 별도.
- 이 보고서가 "실측까지 성공" 으로 읽히면 안 됨 — **실측은 1회 관측 + 결과 분류까지 실행** 이 맞는 표현.

---

## Lee에게 판단 요청 (H6)

| 선택지 | 내용 |
|---|---|
| **A** Multi-seed ensemble (10 seeds × 30 tick) 로 noise band 안정성 재확인 | |
| **B** Policy weight formula 수정 해서 canonical sequence 재현 시도 | 패턴 1 위험 (수치로 답 맞추기) |
| **C** State transition rules (v2 §6 direct edges 27개) 전부 구현 | grief stuck 등 해소 |
| **D** Rubric threshold 를 Peter-specific 으로 보정 | 패턴 1 위험 |
| **E** 여기서 멈춤 — Lee 다른 방향 지시 대기 | |

**내 bias 고백**:
- **A + C 병행** 에 기움. A 는 1 seed 결과 신뢰도 보강, C 는 pipeline 완성도 향상. B/D 는 패턴 1 경계.
- 다만 이번 실측이 "pipeline 작동 확인" 완료했으므로 Lee 가 **다른 방향 (Spike 7+ 실험)** 지시하면 A/C 생략 가능.

---

## HARNESS 자가감사 (H7)

1. **[H1]** trivial 기각? → **Noise band 결과를 "pipeline 검증 성공"으로 돌림**. 이건 내 해석의 bias. 대안 해석 1-3 으로 counter-balance.
2. **[H2]** 대안 3+? → **6개**
3. **[H3]** verbatim? → v2 §5 / §2.4 / Rule #13 verbatim
4. **[H4]** "What could still be wrong"? → **6개**
5. **[H5]** Lee verbatim? → "다음페이즈 진행하자. 내가 생각하는 방향에서 크게 벗어나지 않으면 쭉쭉 진행해서 실측까지 진행해보자"
6. **[H6]** equal weight + bias? → **5 선택지 + A+C bias 명시 + B/D 패턴 1 경고**
7. **좋은 소식만 아닌가?** → **Noise 분류 + grief stuck + policy 임의성 + 30/1 scale 부족 + 76 수치 임의성** 전면 배치.

---

## 산출물

```
content/peter/v3/
  initial_state.json          (20 Active 초기값)
  targets.json                (generic slot → Peter scenario alias)
  canonical_events.json       (11 events, tick 5-28)

engine/person/
  loop.py                     (PersonV3Loop -- event→primitive→pressure→decision 폐루프)

scripts/v3_measurement/
  run_peter_v3.py             (30-tick runner + Rubric + JSON 저장)

docs/person/
  v3_measurement/peter_v3_seed0_ticks30.json  (첫 실측 결과)
  V3_PHASE5_MEASUREMENT_FIRST.md              (이 보고서)
```

기존 변경 없음:
- engine/core/, engine/rules/, engine/simulation/ 0 수정 (Rule #6)
- 기존 277 tests green 유지
- ruff 통과

---

## 세션 로그

### Session (2026-04-22) -- v3 첫 실측

- v3 Phase 5+ integration (content + loop + policy + run + rubric) 한 세션에 완주
- 결과: `not_discovery_noise` — canonical drift 28.5
- Pipeline 동작 positive 확인 (폐루프, 3 Layer, direct edges 일부)
- Policy 결함 실측으로 노출 (`grief stuck`, `run_to_tomb` 과다)
- 패턴 1/3 재발 방지 위해 threshold 튜닝 하지 않음
- 277 → 277 tests 유지 (v3 loop 통합은 새 package, 기존 무영향)

**핵심 자기 수정**: 이 결과를 "pipeline 성공" 으로 프레이밍하지 않음. "pipeline 통합 + 1 seed 실측 + noise band 분류까지 완료" 가 정확.
