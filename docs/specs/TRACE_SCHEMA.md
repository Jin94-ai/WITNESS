# Render-Ready Trace Schema (v1.0 → v2.0 연결)

> ChatGPT 5차 리뷰: "UI는 나중, 하지만 서사로 변환 가능한 추적 구조는 지금부터."
>
> v1.0 Latent Drive 모델이 남겨야 할 로그 구조 정의. v2.0 Narrative Witness Layer가 이 로그를 읽어 1인칭 목격 경험을 렌더링.

---

## 1. 설계 원칙

### 1.1 플레이어 = 목격자 (Witness)
- 플레이어는 전지적 시점 아님 (God-view 거부)
- **정보 비대칭성** (Gemini 5차 리뷰): agent의 모든 수치를 보는 게 아니라 **관찰 가능한 행동 신호**만
- 예: 유다 disill=10.0 수치 안 보임 → "유다가 점점 무리에서 떨어진다"로 관찰

### 1.2 Bifurcation 기록 우선
- Witness 정체성은 "무엇이 갈라지는 순간이었는가"
- 이벤트가 왜/언제 갈라졌는지가 trace의 중심

### 1.3 Latent drive는 사후 해석 가능 형태로
- drive state는 내부적으로 기록하되, 렌더러가 이름을 선택
- 예: `drive[2]=0.7` → "attachment 축이 높다"

---

## 2. Trace 스키마 (JSONL 한 줄 = 한 event)

### 2.1 필수 엔트리

```json
{
  "tick": 152,
  "type": "trigger_fired",
  "event_id": "arrest_trigger",
  "cause": {
    "state_conditions_satisfied": [
      {"agent": "judas", "field": "disillusionment", "value": 8.2, "threshold": 8.0},
      {"agent": "caiaphas", "field": "threat", "value": 7.5, "threshold": 7.0}
    ],
    "action_preceding": {"agent": "judas", "action": "betray", "tick": 151},
    "latent_drive_snapshot": {
      "judas": [0.9, 0.8, 0.3, 0.6, 0.4],
      "peter": [0.5, 0.3, 0.7, 0.8, 0.2]
    }
  },
  "counterfactual_candidates": [
    {"if_remove": "judas", "expected_outcome": "deadline-only"},
    {"if_threshold_+20pct": "expected_outcome": "arrest@~220"}
  ]
}
```

### 2.2 Action entry

```json
{
  "tick": 148,
  "type": "action_taken",
  "agent": "judas",
  "action": "withdraw",
  "observable_from": ["peter", "caiaphas"],
  "visible_signal": "유다가 무리에서 떨어져 앉았다",
  "internal_state_change": {
    "drive[shame]": "+0.05",
    "emotion[grief]": "+0.3"
  },
  "weight_breakdown": {
    "base": 1.5,
    "drive_safety_contribution": 0.8,
    "drive_shame_contribution": 1.2,
    "selected_probability": 0.43
  }
}
```

### 2.3 Belief entry (v1.1 relational extension)

```json
{
  "tick": 150,
  "type": "belief_update",
  "observer": "peter",
  "target": "judas",
  "trigger": "observed withdraw x3",
  "belief_change": {
    "estimated_drive[loyalty]": "0.7 → 0.4",
    "trust": "4.0 → 3.2"
  }
}
```

### 2.4 Bifurcation entry (핵심)

```json
{
  "tick": 100,
  "type": "bifurcation_point",
  "description": "Decision window — 이 이후 경로가 갈라지기 시작",
  "observable_signal": "judas.withdraw 빈도 급증",
  "branch_distribution": {
    "early_arrest": 0.55,
    "mid_arrest": 0.45,
    "late_arrest": 0.00
  },
  "critical_drives": ["shame", "self_preservation"]
}
```

### 2.5 Canonical alignment entry

```json
{
  "tick": 210,
  "type": "canonical_match",
  "canonical_event": "peter_first_denial",
  "simulated_match": {
    "action": "deny",
    "match_type": "event-relative",
    "relative_offset": [5, 30],
    "actual_offset": 12,
    "match": true
  }
}
```

---

## 3. Render-Ready 변환 규칙

### 3.1 플레이어 시점 필터
렌더러가 trace 읽을 때:
1. `observable_from` 에 플레이어 시점 agent 포함 여부 체크
2. 포함되면 `visible_signal` 텍스트로 변환
3. `internal_state_change` 는 **렌더 안 함** (목격자는 내면 못 봄)
4. 단, 플레이어 자신의 `internal_state_change` 는 1인칭 내레이션으로 변환

### 3.2 Bifurcation의 서사적 강조
- `bifurcation_point` entry 감지 → 플레이어에게 긴장감 유발 장면
- `observable_signal` 을 서사 트리거로 사용
- 예: "유다가 또 조용히 자리를 뜨는 모습을 지켜보았다"

### 3.3 Counterfactual의 서사적 활용 (선택)
- 게임 후반부 "만약 ~이었다면" 회고 장면
- `counterfactual_candidates` entry에서 추출

---

## 4. 현 엔진에서 지금 추가해야 할 로깅

v0.7 Stage 1 구현 완료. 아래 표는 현재 상태:

| 항목 | 구현 위치 | 상태 |
|------|----------|------|
| tick, action, agent | `ActionRecord` | ✅ |
| trigger state conditions | `TriggerEngine.fired + snapshot_conditions()` | ✅ `state_conditions_satisfied` 포함 |
| action weight breakdown | `WeightFormula.compute_weight_breakdown()` → `ActionRecord.weight_breakdown` | ✅ |
| observable_from / visible_signal | `ActionRecord.observable_from`, `.visible_signal` | ✅ |
| canonical_match | `checkpoint_results` → `emit_canonical_matches` | ✅ |
| bifurcation_point | `engine/simulation/bifurcation.py` | ✅ decision window + plateau |
| latent_drive_snapshot | `AgentState.drive_state` (None-safe) + `IdentityEncoder` | ✅ Stage 1 plumbing (Stage 2에서 학습된 값) |
| belief_update | `AgentState.beliefs` + `emit_belief_updates` | ✅ §2.3 end-to-end |

`engine/rendering/trace_emitter.py` 가 위 entries를 통합 TraceEvent JSONL 스트림으로 방출.
`engine/rendering/player_view.py` 가 §3.1 정보 비대칭성 필터 적용.

---

## 5. 구현 우선순위 (v0.7 시점)

1. ✅ **완료** (v0.7): `observable_from` + `visible_signal` + `weight_breakdown` 로깅, `trigger.snapshot_conditions()`, `bifurcation.detect_bifurcation()`, `trace_emitter`, `player_view`, `belief_update` entry 구조
2. **v1.0 Stage 2**: `latent_drive_snapshot` 에 학습된 drive 값 채우기 (현재는 IdentityEncoder fallback)
3. **v1.1**: `belief_update` Bayesian update 구현 (현재는 skeleton heuristic + demo_v07 예시)
4. **v2.0**: 렌더러가 trace 소비 → 플레이어 경험

---

## 6. 플레이어 경험 예시 (최종 목표)

```
[tick 100]
당신은 베드로의 눈으로 본다.
유다가 또 무리에서 떨어져 앉았다.
무언가 변하고 있다는 느낌이 든다.

[tick 148 — 플레이어가 베드로 시점일 때]
유다가 말없이 일어났다. 어디로 가는지 묻지 못했다.
(내면: 두려움이 차오른다.)

[tick 152]
갑작스러운 발소리. 군인들이 왔다.
(당신의 칼이 흔들렸다. 뽑을 것인가.)

[선택 없음 — baseline simulation]
당신의 손이 칼자루를 잡았다. 어느 순간 뽑고 있었다.
```

이 경험의 기술적 뒷받침:
- `action_taken` {tick 148, judas, withdraw, observable_from: [peter]} → "말없이 일어났다"
- `trigger_fired` {tick 152, arrest_trigger} → "군인들이 왔다"
- `action_taken` {tick 152, peter, draw_sword} → "칼을 뽑고 있었다"

---

**이 문서는 v1.0 설계의 가드레일이다.** 학습 모델을 짤 때 이 trace 구조를 남길 수 있는 방향으로 설계해야 v2.0 목격자 경험이 가능해진다.
