# Phase 1.4 — Environment responsiveness 진단

SimulationConfig 자체는 environment 필드 미노출. 엔진 내부에서 EnvironmentState를 쓰는 지점과 Peter의 반응 여부 확인.

- engine/simulation/world.py에서 'environment' 등장 횟수: **14**
- 주요 등장 위치:
  - `environment = self._config.environment.model_copy(deep=True)`

- **Peter behavior_profile의 state_multipliers 중 `env.` 경로 참조: 0**

## 실측 비교 (seed=0, 30 tick)

- Base run peter actions (31): `['follow_closely', 'follow_closely', 'follow_closely', 'follow_closely', 'watch_quietly', 'follow_closely', 'discuss_with_disciples', 'follow_closely', 'follow_closely', 'follow_closely']...`

## 결론

- **Peter behavior_profile은 environment를 직접 참조하지 않음.** 즉 Phase 2E environment 다양화는 **현 구조에서 Peter 행동에 영향을 주지 못함.**
- Phase 2E는 Option B (건너뜀) 권고.