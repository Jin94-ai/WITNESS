# Phase 1.6 — Counterfactual branching 진단

## Deep-copy 안전성

- `copy.deepcopy(AgentState)` 동작: OK (cloned.emotions.fear=4.005142239437186)
- 원본과 clone이 서로 다른 객체: True

## Branch divergence (현재 가능한 방식 — 다른 seed로 재실행)

| seed | 마지막 action |
|---:|---|
| 0 | follow_closely |
| 1 | pray |
| 2 | pray |
| 3 | follow_closely |
| 4 | discuss_with_disciples |

- 5 seed에서 관찰된 distinct final actions: **3** (`{'follow_closely', 'discuss_with_disciples', 'pray'}`)

## Mid-run branching 가능성

- 현재 `SimulationWorld.run(seed)` 는 처음부터 재시작만 지원.
- **Mid-run branching** (tick k의 state에서 여러 branch) 은 SimulationWorld에 `resume(from_state, from_tick, seed)` API 신설 필요.
- 이는 engine/ 수정이므로 Lee 확인 대상 (Rule #6).

## 결론

- Deep-copy 자체는 안전. State 격리 가능.
- Seed 재실행을 통한 초기 branching은 가능하지만 *mid-trajectory*가 아닌 *initial-state* branching. Phase 2B 구현 시 처음부터 perturbed state로 새 run을 시작하는 방식으로 근사 가능.
- 엔진에 `resume_from_state` API를 추가하지 않는 한 "동일 궤적의 tick k부터 분기" 는 불가능.