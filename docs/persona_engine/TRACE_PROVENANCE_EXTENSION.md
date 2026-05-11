# Trace Provenance Extension (Step F)

**작성:** 2026-04-23
**목적:** 변수 수 늘리지 않고 해석 가능성 향상. "왜 이 행동이 나왔는가" 추적.

---

## 0. 저장 대상 (각 tick)

**선언적 정보** (엔진이 내린 결정의 근거):
- `selected_motif` — 최종 선택 motif (primary or driver)
- `motif_activations` — 전체 8 motif activation [0, 1] dict
- `blocked_actions` — availability gate에 의해 필터된 actions
- `dominant_pressure` — 가장 높은 pressure 이름
- `guilt_source` — 최근 guilt 유발 event 범주 (social_accusation / peer_failure / vicarious_guilt / exposure)
- `shame_source` — 최근 shame 유발 event 범주 (public_exposure / intimate_exposure / peer_failure)

---

## 1. TrajectoryRecord 확장 (engine/person/loop.py)

```python
@dataclass
class TrajectoryRecord:
    # 기존
    tick: int
    action_id: str
    state: dict
    pressures: dict
    derived: dict
    fired_events: list[str]
    event_category: str
    action_kind: str
    fear_like: float
    # Step F 확장
    selected_motif: str | None = None
    motif_activations: dict[str, float] | None = None
    blocked_actions: list[str] | None = None
    dominant_pressure: str | None = None
    guilt_source: str | None = None
    shame_source: str | None = None
```

---

## 2. 채우는 방식

**selected_motif / motif_activations / blocked_actions:**
- `_decide_action` 이 `ActionSelection` 객체를 `self._last_selection`에 저장
- tick 기록 시 그 값 copy

**dominant_pressure:**
- `max(pressure_dict, key=pressure_dict.get)`

**guilt_source / shame_source:**
- `_infer_guilt_source(fired_events)` — event id → category 매핑
- `_SHAME_SOURCE_EVENTS` / `_GUILT_SOURCE_EVENTS` 테이블

매핑 (engine/person/loop.py):
```python
_GUILT_SOURCE_EVENTS = {
    "public_accusation": "social_accusation",
    "crowd_mockery": "social_accusation",
    "betrayal_witnessed": "peer_failure",
    "eye_contact": "exposure",
    "primary_figure_suffering_visible": "vicarious_guilt",
}
_SHAME_SOURCE_EVENTS = {
    "public_accusation": "public_exposure",
    "crowd_mockery": "public_exposure",
    "eye_contact": "intimate_exposure",
    "betrayal_witnessed": "peer_failure",
}
```

---

## 3. 사후 분석 예시

원래 질문: *"Peter가 tick 19에 왜 follow_at_distance를 했는가?"*

Provenance 로 답:
```
tick 19: action=follow_at_distance
  selected_motif=conceal
  motif_activations={conceal: 0.78, withdraw: 0.42, remain_present: 0.31, ...}
  blocked_actions=[run_to_tomb, draw_sword]
  dominant_pressure=social_threat (9.2)
  shame_source=public_exposure
  guilt_source=None
```

해석:
- 지배 동기: 사회적 수치 노출 → conceal 활성
- 대안: run_to_tomb (restoration context 없음 — gated out), draw_sword (threat 지나감)
- 선택: conceal family 에서 확률적 draw → follow_at_distance

---

## 4. Rubric과의 연계

Provenance 는 rubric critic이 판단 근거를 검증하는데 사용:

- **character_consistency**: 핵심 장면 후 motif 전환이 인물 profile 에 맞는가 (e.g., Peter는 grieve → seek_repair 전환 기대)
- **context_break**: scene event 와 selected_motif 가 일치하는가 (accusation scene에 remain_present motif = 이상)
- **novelty branching_coherence**: action 변화가 motif 변화로 설명되는가

---

## 5. v0.7 trace schema와의 호환

`engine/rendering/trace_emitter.py` 의 기존 TRACE_SCHEMA (§2) 는 rendering용.
Step F Provenance 는 TrajectoryRecord-수준 (analysis-oriented). Rendering 에
노출하지 않음 (플레이어에게 "selected_motif: conceal" 같은 내부 상태
보여주면 서사 정보 비대칭성 깨짐).

Analysis pipeline만 이 필드 읽음.

---

## 6. 구현 체크리스트

- [x] TrajectoryRecord 6 신규 필드 추가
- [x] PersonV3Loop `_last_selection` 유지
- [x] `_infer_guilt_source` / `_infer_shame_source` 메서드
- [x] tick 기록 시 provenance 기입
- [ ] (후속) 기존 rubric critics에서 provenance 활용 (선택)
- [ ] (후속) `demo_v07.py` analysis 블록에 provenance summary 출력 (선택)

---

## 7. 예상 출력 예시 (Peter tick 17 conceal)

```json
{
  "tick": 17,
  "action_id": "follow_at_distance",
  "selected_motif": "conceal",
  "motif_activations": {
    "conceal": 0.83,
    "withdraw": 0.47,
    "remain_present": 0.28,
    "confess": 0.00,
    "grieve": 0.05,
    "confront": 0.12,
    "seek_repair": 0.00,
    "observe_wait": 0.35
  },
  "blocked_actions": ["run_to_tomb", "jump_into_sea"],
  "dominant_pressure": "social_threat",
  "guilt_source": "social_accusation",
  "shame_source": "public_exposure",
  "fired_events": ["public_accusation", "ally_arrival"]
}
```

---

**End of Step F.**
