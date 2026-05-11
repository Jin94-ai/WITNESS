# World Observer Layer — Canonical Spec

**Status**: Phase O1 implementation in progress (2026-04-30)
**Source**: `docs/WITNESS_WORLD_OBSERVER_LAYER_SPEC.md` (Lee directive 2026-04-30)
**용도**: World Observer Layer의 canonical 사양. 구현 동기화 기준.

---

## 0. 한 줄 정의

**시뮬레이션이 생성하는 상태 변화를 tick 단위 snapshot stream으로 구조화하고, 다양한 관찰 렌즈 (Person / Group / Event / World) + zoom level + salience detector로 조회 가능하게 하는 계층.**

해석기 아님. *관찰기 / 탐색기*.

---

## 1. ABSOLUTE 원칙 (구현 시 준수)

### Rule #1 — engine/ no person hardcoding
- `engine/observer/` 안에 person name (peter / vangogh / etc.) 하드코딩 금지
- pytest `test_no_person_hardcoding_in_engine` PASS 유지

### Rule #6 — engine/ public API preservation
- 기존 SimulationWorld 인터페이스 변경 금지
- Observer는 *additive layer* — 기존 simulation 결과를 받아서 처리

### 관찰기 원칙 (Lee directive §6)
- **원칙 1**: 시스템은 관측 태그까지만 만든다. 평가/판정 금지
- **원칙 2**: 여러 렌즈 제공, 하나를 정답으로 고정 안 함
- **원칙 3**: 해석보다 *탐색 가능성* 우선

---

## 2. 아키텍처

```
Pressure/Event Input
    ↓
Simulation Engine (existing)
    ↓
World Snapshot Stream  ← Observer Layer가 받는 입력
    ↓
World Observer Layer
    ├─ Snapshot Recorder (engine/observer/recorder.py)
    ├─ Snapshot Schema (engine/observer/snapshot_schema.py)
    ├─ Observer Core API (engine/observer/core.py)
    │   ├─ get_world_view(tick)
    │   ├─ get_person_view(agent_id, tick)
    │   ├─ get_group_view(group_id, tick)
    │   └─ get_event_view(event_id)
    ├─ Salience Detector (engine/observer/salience.py)
    ├─ Replay / Jump (engine/observer/replay.py)
    └─ Multi-lens Compare (scripts/observer/compare_views.py)
    ↓
Text Reports (scripts/observer/observer_report.py)
```

---

## 3. Snapshot Schema (Phase O1)

### 3.1 Pydantic 모델 계층

```python
class WorldSnapshot(BaseModel):
    """World-level state at one tick."""
    crowd_mood: str  # "calm" / "tense" / "agitated" / "fragmenting"
    blame_concentration: float  # 0.0-1.0
    public_suspicion: float  # 0.0-1.0
    authority_vigilance: float  # 0.0-1.0
    scarcity_pressure: float  # 0.0-1.0

class GroupSnapshot(BaseModel):
    """Cohort/location/role-based state."""
    id: str
    dominant_mode: str  # "saturation" / "recovery" / "mixed" / "low_activity"
    tension: float  # 0.0-1.0
    member_count: int

class AgentSnapshot(BaseModel):
    """One agent's state at one tick (dynamic — engine state schema 변화 흡수)."""
    id: str
    role: str  # generic role tag (no person name)
    fear: float
    hope: float
    shame_self: float
    delta: list[str]  # ["fear_up", "shame_self_down", ...]

class Snapshot(BaseModel):
    """One tick's complete observation."""
    tick: int
    active_events: list[str]
    world: WorldSnapshot
    groups: list[GroupSnapshot]
    agents: list[AgentSnapshot]
    salience_hints: list[str]
```

### 3.2 Schema 진화 원칙

- **MVP (Phase O1)**: 위 4 schema 만으로 시작. 추가 fields는 *optional* + default
- **확장**: 새 field 추가 시 Pydantic Optional + backward compat
- **engine state schema 동기화**: AgentState (engine/core/state.py)의 PhysicalState/EmotionalState/SocialState 일부를 AgentSnapshot에 mirror. 단, observer schema는 *engine schema의 subset* (snapshot은 light view)

---

## 4. Observer Core API (Phase O2)

### 4.1 Observer 클래스

```python
class Observer:
    """Observation lens API — read-only view over snapshot stream."""

    def __init__(self, snapshots: list[Snapshot]):
        """Initialize with pre-recorded snapshot stream."""

    def get_world_view(self, tick: int) -> WorldSnapshot:
        """World-level state at one tick."""

    def get_person_view(self, agent_id: str, tick: int) -> AgentSnapshot:
        """One agent's state at one tick."""

    def get_group_view(self, group_id: str, tick: int) -> GroupSnapshot:
        """One group's state at one tick."""

    def get_event_view(self, event_id: str) -> dict:
        """Event ripple — all ticks where event was active + affected agents."""

    def get_salience_window(self, tick_from: int, tick_to: int) -> list[str]:
        """Top salient moments in window."""

    def list_ticks(self) -> list[int]:
        """All ticks present in snapshot stream."""

    def list_agents(self) -> list[str]:
        """All agent IDs present."""

    def list_events(self) -> list[str]:
        """All unique event IDs across all ticks."""
```

### 4.2 Read-only contract

- Observer는 *snapshot stream을 변경하지 않음*
- 모든 view는 *immutable* (Pydantic 모델 그대로 반환)
- Getter만 — setter 없음

---

## 5. Salience Detector (Phase O2-B)

### 5.1 감지 후보 (Lee directive §4.4)

- **pressure spike** — world.scarcity_pressure tick-over-tick delta > threshold
- **blame target shift** — top blame target 변화
- **authority vigilance spike** — world.authority_vigilance jump
- **public suspicion jump** — world.public_suspicion jump
- **cohort split** — 2+ groups가 다른 dominant_mode
- **recovery turning point** — group dominant_mode "saturation" → "recovery"
- **saturation lock** — group dominant_mode "saturation" 5+ ticks 연속
- **low-activity but meaningful tension** — world.crowd_mood "tense" + active_events 0
- **agent state급변** — agent fear/shame delta > threshold

### 5.2 출력

- **top 5 salient moments** in window
- **top 3 unstable agents** in window
- **top 3 emerging world tensions** in window
- **current strongest event ripple**

### 5.3 평가 안 함

salience는 *attention pointer*이지 *quality verdict* 아님. "이 moment가 중요해 보임" — but "이게 좋은 이야기"는 절대 아님.

---

## 6. Phase 진행 (Lee directive §8)

| Phase | 산출물 | 상태 |
|---|---|---|
| **O1 — Snapshot Recorder** | `engine/observer/snapshot_schema.py` + `recorder.py` | **이번 LOOP** |
| **O2 — Observer Core API** | `engine/observer/core.py` + `salience.py` | **이번 LOOP** |
| O3 — Text Observer Reports | `scripts/observer/observer_report.py` | 다음 LOOP |
| O4 — Replay / Jump | `engine/observer/replay.py` | 다음 LOOP |
| O5 — Multi-lens Compare | `scripts/observer/compare_views.py` | 다음 LOOP |

### 매 Phase 검증
- Pytest test_observer suite 추가 (각 phase별)
- Engine integrity (no person hardcoding) 유지
- 기존 1500+ tests 회귀 zero

---

## 7. MVP 범위 (Lee directive §7)

### MVP 포함
- Snapshot Recorder (post-hoc, existing trajectory에서 생성)
- World View / Person View / Event View / Group View
- Salience top 5
- Tick jump (basic replay)
- Anchor seed comparison (minimal)

### MVP 제외
- Full GUI / live interactive dashboard
- Story quality scoring (관찰기 ≠ 평가기)
- Public-facing browser

---

## 8. Forbidden_now (Lee directive §10)

- World Observer를 곧바로 public UI로
- Story evaluator처럼 해석 자동화
- "좋은 이야기 / 나쁜 이야기" 자동 판정
- Branch C / renderer 문제와 observer를 한 번에 풀기 (분리)
- GUI 부터 만들기

→ **MVP = 기능적 텍스트 기반 observer**가 먼저.

---

## 9. lessons L33 등록 예정

"World Observer Layer 구현 패턴 — 관찰기 ≠ 평가기, additive layer 원칙". L18-L33 = 16 패턴.

---

## 10. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (이 spec)** | **2026-04-30** | **Lee directive에서 canonical로 옮김, Phase O1+O2 시작** |
