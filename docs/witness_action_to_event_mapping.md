# Witness v3 Action → Event Mapping (v2 §5)

> **Spec**: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §5
> **Code**: [engine/action/action_event_mapper.py](../engine/action/action_event_mapper.py)

## 0. v2 §5 핵심

- **금지**: `person_state → external_state` 직접 (텔레파시 금지)
- **허용**: `action → event → external update` (폐루프)

## 1. 매핑 테이블 (21 actions → events)

### 1.1 BC vocab 15개 (spike 6 peter_bc_v1/v2)

| action_id | → event_id | 효과 |
|---|---|---|
| `deny` | `public_denial` | accusation_visibility↑, public_visibility↑ |
| `confess` | `public_declaration` | authority_presence↑, public_visibility↑ |
| `weep` | `visible_distress` | public_visibility↓ (숨어서) |
| `pray` | `prayer_invitation` | religious_context↑ |
| `withdraw_in_fear` | `withdrawal` | ally_proximity↓, public_visibility↓ |
| `follow_closely` | `ally_arrival` | ally_proximity↑ |
| `follow_at_distance` | `withdrawal` | (same as withdraw) |
| `draw_sword` | `weapon_raised` | volatility↑, decision_criticality↑ |
| `flee` | `withdrawal` | |
| `stay_awake` | `ally_arrival` | |
| `fall_asleep` | `ally_departure` | ally_proximity↓ |
| `stay_hiding` | `withdrawal` | |
| `run_to_tomb` | `ally_arrival` | |
| `assert_loyalty` | `public_declaration` | |
| `discuss_with_disciples` | `ally_arrival` | |

### 1.2 Canonical-event actions 6개 (scene option)

| action_id | → event_id |
|---|---|
| `join_crowd` | `public_declaration` |
| `watch_quietly` | `withdrawal` |
| `resist_washing` | `public_declaration` |
| `accept_washing` | `ally_arrival` |
| `jump_into_sea` | `public_declaration` |
| `stay_on_boat` | `withdrawal` |

## 2. 폐루프 데이터 흐름 (v2 §5.3)

```
Person State (ActiveState)
    ↓  [decision]
action_id
    ↓  [ActionEventMapper.trigger_event_id]
event_id
    ↓  [EventRegistry.apply_to_primitives]
PrimitiveState (Layer A) 갱신
    ↓  [next tick]
PressureLayer.compute(primitives, person_state)
    ↓  [PressureVector]
Next decision
```

## 3. 검증 (tests)

- `tests/test_action/test_action_to_event_loop.py::test_action_to_event_to_primitive_loop` -- 전체 폐루프 end-to-end
- `tests/test_action/test_action_to_event_loop.py::test_withdrawal_action_reduces_visibility` -- 특정 action의 effect 검증

## 4. Lee 검토 지점

- 21 action이 전부 생각한 effect를 가지는지 (내 임의 매핑)
- 한 action이 여러 event를 trigger해야 하는 경우? (현재 1:1 매핑)
- Event의 primitive_updates delta 크기 (±0.2 ~ ±0.5 임의)

## 5. 한 줄 요약

**"21 action 전부 event로 매핑. Event가 Primitive 갱신. 다음 tick에서 Pressure 재계산. v2 §5 폐루프 엔드투엔드 작동."**
