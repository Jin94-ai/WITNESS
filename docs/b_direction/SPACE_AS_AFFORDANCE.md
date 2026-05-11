# Space as Affordance — Spatial Layer as Action Shaper (Phase 3 우선 3)

**작성:** 2026-04-24
**목적:** 공간을 "좌표" 또는 단순 location 문자열 대신 **agent action 가능성 지형** 을 결정하는 affordance 제공자로 재정의.

---

## 0. 핵심 전환

**Before:** `PrimitiveState.location: str = "unknown"` — 좌표/좌석 정보.

**After:** 각 location은 **affordance set** 를 가짐:
- visibility (누구 눈에 띄는가)
- reachability (누가 도달 가능한가)
- escape_routes (이탈 가능한가)
- crowdability (군집 가능한가)
- authority_reach (권력 개입 가능한가)
- sacred_proximity (신성 공간 근접도)

Agent는 현재 location의 affordance에 따라 action space가 **실제로 바뀜**.

---

## 1. Location Schema

```python
@dataclass
class Location:
    location_id: str
    name: str                         # content binding용 이름 (generic engine에는 ID만)

    # Affordances
    visibility: float                 # 0-1: 누구나 볼 수 있는가
    reachability: dict[str, float]    # role → reach score
    escape_routes: list[str]          # 인접 location id
    crowdability: float               # 0-1: 사람 모일 수 있는가
    authority_reach: float            # 0-1: 권력이 손쓸 수 있는가
    sacred_proximity: float           # 0-1: 신성 공간 근접도
    concealment: float                # 0-1: 숨을 수 있는가

    # Info / resource
    info_access_level: str            # "public" | "restricted" | "secret"
    resource_availability: dict[str, float]  # "food" / "shelter" / ...

    # Occupants (dynamic)
    agents_present: set[str]          # agent_id set
    max_capacity: int = 1000
```

---

## 2. Affordance → Action space modulation

Agent의 `_decide_action` 에서 availability gate가 현재 location 참조:

| Action | Location 요구 조건 |
|---|---|
| `flee` | `escape_routes > 0` |
| `stay_hiding` | `concealment > 0.5` |
| `public_accusation` (crowd event) | `visibility > 0.6` AND `crowdability > 0.4` |
| `pray` | free (어디든 가능) |
| `draw_sword` | `authority_reach < 0.8` (공권력 눈 앞에서는 어려움) |
| `jump_into_sea` | `location.tag includes "water"` |
| `run_to_tomb` | adjacent to `tomb_location` in reachability |
| `follow_at_distance` | `escape_routes > 0` AND visibility < 1.0 |

---

## 3. Location transition (이동 동학)

### 3.1 Movement cost
- 도보 1 tick 당 1 hop
- `soldier_enforcer` / `merchant` role 은 2 hops/tick (이동성 높음)
- `outsider` / disabled 는 0.5 hops/tick

### 3.2 Blocked movement
- authority_reach > 0.7 + agent.role = wanted_target → movement blocked
- crowd.density > 0.8 → movement cost × 2

### 3.3 Agent-driven vs environment-driven

- **Agent-driven:** explicit movement action (`flee` → chose escape_route)
- **Environment-driven:** crowd surge pushes agents; ally_departure event moves peer_group

---

## 4. Spatial Patterns (Emergent)

### 4.1 Public square
- high visibility + high crowdability + high authority_reach
- 사건 발생 시 즉각 군중 알림 + 공권력 개입
- accusation events 가 여기서 발생하면 amplification × 1.5

### 4.2 Private dwelling
- low visibility + low crowdability + low authority_reach
- 대화 / 음모 / 은신에 유리
- `covert_bargain` 같은 event 의 자연 배경

### 4.3 Sacred space (temple/shrine)
- high sacred_proximity
- sacred_salience pressure baseline +0.3 (모든 agent에게)
- taboo 위반 시 shame_exposure × 2

### 4.4 Liminal space (boat, wilderness)
- low crowdability + low authority_reach
- `spiritual_wanderer` affordance_pack 최적
- 개인 전환 / prophecy event 무대

### 4.5 Judgment space (court, council chamber)
- very high authority_reach
- agent가 강제 이동될 수 있음 (arrest → court)
- 정식 절차만 허용 — improvised action blocked

---

## 5. Space ↔ Other Layers Coupling

| Source → Target | Coupling |
|---|---|
| **Space → Crowd** | `crowdability × density → alignment_strength propagation` |
| **Space → Information** | `visibility → rumor spawn probability` ↑ |
| **Space → Institutional** | `authority_reach → action cost × (1 + reach × 0.5)` |
| **Space → Symbolic** | `sacred_proximity → sacred_salience baseline` |
| **Space → Material** | `resource_availability → hunger decay rate` |
| **Space → Person.fear** | `escape_routes == 0 → agent.fear baseline +0.5` |

---

## 6. Minimum Location Registry (Judea 1st century 예시)

10 micro-world locations:

| Location ID | Tags | Key affordances |
|---|---|---|
| `upper_room` | private, indoor | low visibility, high concealment, low crowdability |
| `gethsemane_garden` | outdoor, liminal | medium concealment, moderate escape_routes |
| `high_priest_courtyard` | public, authority | high visibility, high authority_reach |
| `temple_inner` | sacred | high sacred_proximity, restricted info |
| `temple_outer_court` | public, sacred | high visibility, high crowdability |
| `city_street` | public | medium visibility, high crowdability |
| `market_square` | public, commercial | very high visibility, crowdability |
| `fishing_shore` | outdoor, water | low visibility, escape to sea |
| `tomb_area` | outdoor, sacred | low visibility, low crowdability |
| `road_to_emmaus` | outdoor, liminal | low authority_reach, long |

각 location은 **`content/worlds/<world_id>/locations.json`** 에 정의.
Engine 은 affordance 만 사용.

---

## 7. Engine 구현 최소

```python
# engine/world/space/location.py
@dataclass
class Location: ...  # §1 schema

class SpatialRegistry:
    def __init__(self, locations: list[Location]): ...
    def get(self, location_id: str) -> Location: ...
    def agents_at(self, location_id: str) -> set[str]: ...
    def move(self, agent_id: str, from_loc: str, to_loc: str) -> bool: ...
    def apply_affordance_to_action_gate(
        self, agent: Agent, action: str, gate_context: GateContext
    ) -> bool: ...
```

---

## 8. Phase 3 §5.7 완료 기준 매핑

| 기준 | 달성 방식 |
|---|---|
| 사람 없이 state 갱신 | crowd 자동 분포 / seasonal movement / market openings |
| Action space 변화 | affordance → availability gate 결합 |
| 다른 layer coupling | §5 table 6개 layer 결합 |

---

## 9. Micro-world 예시 (Phase 5 연계)

**시나리오:** 3 locations (upper_room / city_street / high_priest_courtyard), 8 agents.

**Emergent flow:**
1. Tick 1-5: agents mostly in upper_room (private, concealment high)
2. Tick 6: city_street 에서 accusation rumor 발생
3. Tick 7-10: rumor 전파 → crowd_participant agents city_street로 이동
4. Tick 11-15: one outsider agent 가 courtyard로 끌려감 (authority_reach)
5. Tick 16-20: 거기 lynch_mode 진입 or defenders 개입

Space affordance가 각 단계 driver:
- rumor 확산은 street 가 market_square 연결돼서
- lynch는 courtyard 가 authority + crowd 동시 제공해서
- upper_room은 다른 flow 완전 격리

---

**End of space as affordance.**
