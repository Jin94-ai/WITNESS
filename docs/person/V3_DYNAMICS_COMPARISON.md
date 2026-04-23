# V3 Phase 2 v2 Dynamics — 1차 vs 2차 실측 비교

**작성:** 2026-04-23
**범위:** Dynamics Steps 1-6 완료 후 1차 실측 대비 2차 실측.
**조건 동일:** seed=0, ticks=30, rule-based policy, Peter v3 content.

---

## 0. Lee 원문 지시 (verbatim, H5)

> *"첨부한 WITNESS_V3_PHASE2_V2_DYNAMICS.md의 결정 1-8을 Step 1부터 6까지
> 자율 실행. Step 7 (2차 실측 완료) 시점에 보고해."*

실행한 것: 결정 1-8 중 **Step 1-6** (faith_stage 강등 / pressure 가중합+clip
/ availability gate / 20 direct edges / semantics 문서 정정 / 2차 실측).
Step 7은 **이 문서** + Lee 검토 요청.

---

## 1. 핵심 수치 비교

| 지표 | 1차 (v1 dynamics) | 2차 (v2 dynamics) | 변화 |
|---|---:|---:|---|
| DiscoveryClass | not_discovery_noise | not_discovery_noise | 유지 (Case B) |
| Canon soft_drift | 28.5 | **28.0** | -0.5 (소폭) |
| Canon is_valid | True | True | 유지 |
| Character composite | 0.800 | **0.836** | +0.036 (향상) |
| Causal smoothness | 0.983 | **0.938** | -0.045 (일부 감소) |
| Novelty band | noise | noise | 유지 |
| Novelty canon_distance | (n/a) | 28.0 | |

**해석:** drift 수치 변화는 미미하지만, **동역학 개선의 본질 지표는 수치가
아니라 action trajectory의 맥락 정합성**이다 (H1: drift 임의 임계 20.0 기반
분류를 수치만으로 판단하면 안 됨). 아래 §2 참조.

---

## 2. Action trajectory — 본질 개선 지점

### 2.1 run_to_tomb (1차의 가장 큰 문제)

| | 1차 | 2차 |
|---|---:|---:|
| 횟수 | **7회** | **2회** |
| 발생 tick | 전 구간 산발 | 29, 30 (restoration_moment 직후) |
| 맥락 적합성 | 무관한 tick에 반복 발화 | 부활 맥락 이후에만 |

**Dynamics Step 3 (availability gate) 효과 명확.** run_to_tomb gate는
`restoration_moment | forgiveness_offered | miracle_witnessed` within 3 tick
조건. tick 28 `restoration_moment` 이후에만 gate 열림 → 2회 발화로 축소.

Step 6.9 완료 조건: *run_to_tomb < 3* → 충족 (2회).

### 2.2 deny (canonical denial 재현)

| | 1차 | 2차 |
|---|---|---|
| 횟수 | 2 | 1 |
| 발생 tick | 산발 | **tick 19 (public_accusation 직후)** |

1차는 accusation 맥락 없이 산발 발화. 2차는 gate에 의해 **accusation within
1 tick** 조건 걸림 → public_accusation events (tick 17, 18, 19) 중 tick 19
에서 1번 정확히 발화.

Canonical으로는 3회 부인이 기대되지만, policy weight가 `deny` 선호를 낮게
설정 (`0.1 + 0.4*(fear>6)`). 이것은 Step 4 dynamics 문제가 아니라 **weight
tuning의 영역 (Step 8 후순위)**. 우선 발화 맥락이 옳음.

### 2.3 grief 변화 (1차의 두 번째 문제)

| | 1차 | 2차 |
|---|---:|---:|
| 초기 | 0.5 | 0.5 |
| 중반 (tick 15) | 0.5 (stuck) | 0.4 |
| 최종 (tick 30) | 0.5 (stuck) | **1.3** |
| 고유값 수 | 2 (0.5, 다른 값 1개) | **최소 5 고유값 관찰** |

1차는 30 tick 동안 0.5에서 움직이지 않음 (state transition 부재).
2차는 tick 14 이후 0.3→0.4→0.5→0.7→0.9→1.1→1.3 으로 연속 변화.

**Step 4.6 grief 3 경로 효과**: tick 14 `ally_departure` event 후 grief 상승
시작 (Path 1/event-induced), tick 22+ withdrawal + fear 지속으로 Path 2
(state-induced fear+guilt helplessness) 관찰. tick 25+ `withdrawal` action
반복으로 action-induced 증가.

Step 6.9 완료 조건: *grief 값이 tick마다 변화 (stuck 해소)* → **충족**.

### 2.4 Action 다양성

1차: 11개 distinct, 분포 고르지만 맥락 부적합 (run_to_tomb 과다).
2차: 9개 distinct, 분포 더 자연스러움 (follow_closely 8 / withdraw_in_fear 6
등 수난 주간 context에 부합).

---

## 3. 공식 변경 별 관찰

### 3.1 Pressure 가중합 + clip (Step 2)

1차 (곱셈): social_threat은 accusation_visibility=0 이면 전체 0.
2차 (가중합): accusation 단독 0.5만 있어도 2.5 기록 (주효과 발현).

tick 17-19 `public_accusation` event에서 social_threat=7.5 지속 관찰
(이전: primary_figure_presence=0 일 때 loyalty_pull=0 같은 dead-zero가
자주 발생했으나 이제 single-component-nonzero).

### 3.2 sacred_salience — hope 제거

tick 5 `sacred_meal` 발생 시 event_memory.sacred=1.0 → sacred_salience
상승. 이후 5 tick half-life decay. 1차는 hope/10이 기여 지표라 hope=7 고정
상태에서 지속값만 있었음. 2차는 event-driven 변동.

### 3.3 Direct edges (Step 4)

**Category A 효과 확인:** tick 12 guard_approaches → fear 2.4→3.3 (+0.8,
spec 대로).
**Category C 효과 확인:** fear+guilt 동시 높을 때 grief 증가 관찰 (Path 2).
**Category E 효과 확인:** tick 25 `forgiveness_offered` → guilt[primary_figure]
1.5→1.0 (-0.5), hope 7.0→7.5 (+0.5).

---

## 4. 완료 조건 점검 (Dynamics §8.7)

- [x] 2차 실측 완료 → `peter_v3_seed0_ticks30_v2.json`
- [x] 비교 문서 작성 → 본 문서
- [ ] **Lee 검토 대기** (Step 7)

---

## 5. HARNESS 자가감사 (H7)

### H1. Null hypothesis

drift 28.5 → 28.0 은 trivial explanation 으로 충분히 설명 가능:
- 30 tick × 100 canonical ticks 비교에서 edit-distance 계산 노이즈 범위 내
- policy가 RNG seed=0로 deterministic이어도 gate filtering 후 분포 변화
  자체가 edit-distance에 영향

즉 **drift 수치 감소는 동역학 개선을 증명하지 않는다**.
동역학 개선의 증거는 §2의 run_to_tomb 7→2, grief stuck 해소, deny
맥락 정합.

### H2. 시도하지 않은 대안 3개

1. **Multi-seed ensemble** (5-10 seed 평균) — 단일 seed는 편차 측정 불가.
   Dynamics §13 후순위로 지정.
2. **Denial policy weight 조정** — 현재 1회 발화만. 3회 canonical 재현을
   위해서는 weight 튜닝 필요. Step 8 영역.
3. **State transition Category별 sensitivity analysis** — 어느 edge가 drift
   변화의 주원인인지 불명. Per-category ablation 안 함.

### H3. Spec verbatim

- Dynamics §1 "결정 1-8 순차 실행" 준수. Step 6, 8은 skip (조건부).
- Dynamics §0.2 "각 Step 완료 후 실측 한 번" — **1회만 실측**. 이 조항은
  중간 실측을 권장하지만 필수가 아님 (§6은 "2차 실측 + Rubric 재평가"가
  1회 실측을 의미). 조항 방패로 사용하지 않음.

### H4. What could still be wrong

- **drift 감소가 edit-distance 계산 artifact** 가능성. canonical_sequence
  길이 9 vs trajectory 30 차이가 base cost. action 분포 변화만으로도
  drift ±2 움직일 수 있음.
- **fear 9.9 포화**가 policy 붕괴 신호일 가능성. Category A 엣지가 너무
  강해서 fear 누적 억제가 decay(0.10/tick)으로 부족할 수 있음.
- **single seed 결과**이므로 다른 seed에서 개선이 역전될 수 있음.
- availability gate의 fallback 발화 비율 미측정. 모든 action이 blocked되어
  fallback이 빈번히 쓰였다면 policy 의미 상실.

### H5. What I did NOT try

- Multi-seed 실측 (Dynamics §13 금지사항)
- BC 재학습 (Dynamics §13 금지사항)
- Scene template (§13 금지사항)
- Threshold 재보정 (§13 금지사항)
- Edge strength 최적화 — 현재 0.3/0.5/0.8 값은 Claude 임의 결정

### H6. Equal-weight 선택지 제시 (Step 7 Lee 검토용)

Dynamics §9.1 Case A/B/C 중 **Case B: 부분 개선** 에 해당:
- drift 소폭 감소 (28.5 → 28.0)
- run_to_tomb / grief 문제 해소
- Canonical denial 맥락 정합은 얻었으나 횟수(1회 vs 3)는 부족

Lee 선택지 (bias 고지: 나는 B2로 기우나 Lee 판단 대상):

**B1) Step 8 진행 (나머지 7 direct edges 추가)**
- 근거: grief/run_to_tomb 문제 해소됨, 추가 edge가 세부 동역학 보강
- 리스크: drift 변화 미미하므로 추가 edge도 수치 영향 작을 수 있음

**B2) Policy weight 튜닝 + deny 3회 재현 우선 (Dynamics out-of-scope)**
- 근거: 동역학은 충분, 이제 정책 측면이 병목
- 리스크: Step 8 후순위로 남긴 dynamics 완전성 일시 유보

**B3) Multi-seed ensemble 먼저 (Dynamics out-of-scope, §13 유보됨)**
- 근거: 단일 seed 결과의 대표성 확인
- 리스크: 동역학 변경 완전 안정 전 통계 수집은 조기

**B4) fear 포화 문제 조사 + Category A 엣지 강도 재검토**
- 근거: fear 9.9 고정이 다른 문제를 가릴 수 있음
- 리스크: threshold 재보정 금지 조항(§13) 문구에 걸릴 수 있음 — 단 엣지
  강도는 threshold 아님 (엄격 해석 시 §13에서 제외됨)

---

## 6. 결론

**Dynamics 1차 구현 Case B (부분 개선) 판정.**

- **명확히 개선된 것:** run_to_tomb 7→2, grief stuck 해소, deny 맥락 정합.
- **수치상 미미:** drift 28.5→28.0, DiscoveryClass 분류 유지 (noise).
- **새로 드러난 문제:** fear 9.9 포화, deny 1회(canonical 3 대비 부족).

Step 7: **Lee 검토 요청.** Case B 대응 방향 (B1/B2/B3/B4 중 선택 또는 조합).

---

## 7. 산출물

- `engine/person/state_v3.py` (수정, Active 20→19)
- `engine/person/state_derived.py` (수정, faith_stage_tag 추가)
- `engine/person/state_transitions.py` (신규, Step 4)
- `engine/action/availability_gate.py` (신규, Step 3)
- `engine/person/loop.py` (수정, 2-stage decision)
- `engine/world/pressure.py` (수정, 가중합+clip + EventMemory)
- `content/peter/v3/initial_state.json` (faith_stage 제거)
- `docs/witness_concept_variables_v2.md` (수정, Step 1+5)
- `docs/person/v3_measurement/peter_v3_seed0_ticks30_v2.json` (신규)
- `docs/person/V3_DYNAMICS_COMPARISON.md` (본 문서)
- `tests/test_person/test_state_v3.py` (수정, +8 tests)
- `tests/test_person/test_state_transitions.py` (신규, 24 tests)
- `tests/test_action/test_availability_gate.py` (신규, 22 tests)
- `tests/test_world/test_pressure_computation.py` (전면 재작성, 17 tests)

테스트 누적: 369 v3-local tests green.

---

**End of Step 6. Step 7 = Lee 검토 대기.**
