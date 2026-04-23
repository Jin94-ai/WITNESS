# Phase 1.5 — Forced action feasibility 진단

현재 구조에서 '이 tick에 이 action을 강제 실행' 가능한지 확인.

- Peter action 수: 6
- action_ids:
  - `follow_closely`
  - `pray`
  - `discuss_with_disciples`
  - `assert_loyalty`
  - `withdraw_in_fear`
  - `weep`

## 메커니즘 테스트 (20회 decide_action with weight-mask policy)

- Target action: `pray`
- Forced ratio: **100%** (100%면 완전 강제 가능)

## 결론

- **Forced action은 DecisionPolicy weight-mask로 100% 달성 가능.** 별도 engine 수정 불필요. ChatGPT의 'forced action rollouts' 전략 적용 가능.
- Phase 2에서 `{action_id: 100.0, others: 0.0}` 형태의 `ForcingPolicy`를 주입한 뒤 N tick rollout → rare action 주변 state 분포 수집 가능.