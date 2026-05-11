# Rumor Propagation — Information Layer as Process (Phase 3 우선 2)

**작성:** 2026-04-24
**목적:** 정보를 `information_gap` scalar 1개 대신 **epidemic-style 전파 동학 + distortion + credibility** 을 가진 독립 layer로 설계.

---

## 0. 핵심 전환

**Before:** `PrimitiveState.information_gap: float` (0-1), EventMemory.accusation (half-life).

**After:** Rumor는 **개별 단위** (rumor item) + 네트워크 전파 + 왜곡 누적 + credibility decay.

---

## 1. Rumor Item 구조

```python
@dataclass
class Rumor:
    rumor_id: str                      # unique
    origin_tick: int                   # 생성 시점
    origin_source: str                 # agent_id 또는 event_id
    content_tag: str                   # "accusation" | "prophecy" | "secret" | "misdeed" | ...
    target_role: str | None            # 누구에 대한 rumor (role or agent_id)
    payload: dict                      # 내용 (e.g., "betrayal_by=agent_X")

    intensity: float                   # 0-1 (현재 강도)
    credibility: float                 # 0-1 (수신자들이 믿는 정도)
    distortion: float                  # 0-1 (원본 대비 왜곡)
    reach: set[str]                    # 전파된 agent_ids

    # Dynamics
    propagation_rate: float = 0.3      # tick당 확산 계수
    decay_rate: float = 0.15           # 무관심 decay
    distortion_gain: float = 0.05      # 각 전달마다 왜곡 증가
```

---

## 2. Propagation Process (매 tick)

### 2.1 Epidemic spread
각 tick, 각 rumor:

```python
for each rumor r:
    for each agent a in r.reach:
        for each neighbor n in a.social_network():
            if n not in r.reach:
                p_spread = (
                    r.intensity 
                    * r.credibility 
                    * r.propagation_rate 
                    * a.trust_by(n)                      # n이 a를 믿는 정도
                    * crowd.density_local(n)             # 공간적 proximity
                    * (1 - authority.suppression_level)  # 당국 억제
                )
                if rng() < p_spread:
                    r.reach.add(n)
                    r.distortion += r.distortion_gain    # 각 전달에 왜곡
                    r.intensity *= 0.98                  # 살짝 약화
```

### 2.2 Decay (수신자 이탈)
- `intensity[t+1] = intensity[t] × (1 - decay_rate)` per tick
- Intensity < 0.05 → rumor garbage-collected

### 2.3 Credibility drift
- Contradictory observation → `credibility -= 0.1`
- Authoritative confirmation → `credibility += 0.2`
- 주 소스 reputation 변화 → credibility 비례

---

## 3. Distortion Dynamics

### 3.1 누적
- 각 전달마다 `distortion += distortion_gain` (default 0.05)
- Distortion > 0.5 → rumor content_tag 가 바뀔 수 있음 (예: "회의" → "음모")

### 3.2 왜곡 유형
- `exaggeration`: 강도 증가 (사망자 수 부풀리기)
- `substitution`: 주체/대상 바뀜 (A가 한 것이 B가 한 것으로)
- `moral_inversion`: 선 → 악 해석 뒤집힘

---

## 4. Network topology (공간/관계 기반)

### 4.1 Local clustering
- 같은 location 에 있는 agent끼리 propagation_rate × 1.5
- 다른 faction 간은 × 0.5 (신뢰 장벽)

### 4.2 Hub agents
- `merchant` / `crowd_participant` role 은 propagation_rate × 1.3 (정보 hub)
- `spiritual_wanderer` 는 다른 geography로 전파 (isolated clusters 연결)

### 4.3 Authority suppression
- `institutional.law_enforcement_strength` 비례해서 rumor 전파 억제
- Rumor content_tag="accusation" 이면서 authority 피해자면 억제 강도 × 2

---

## 5. Rumor → Other Layers Coupling

| Target Layer | Coupling |
|---|---|
| **Crowd** | `rumor_intensity × reach_fraction → crowd.accusation_amplification` |
| **Social** | `negative rumor about agent X → social.reputation_network[X] -= intensity × 0.3` |
| **Institutional** | `rumor about authority legitimacy → institutional.authority_concentration[target] -= 0.15 × credibility` |
| **Symbolic** | `rumor with sacred/prophetic content → symbolic.sacred_salience_baseline += 0.1` |
| **Agent personal state** | `rumor about self with blame → agent.shame[public_group] += 0.2 × reach_fraction` |

---

## 6. Rumor 생성 소스

### 6.1 Event-triggered
- `public_accusation` event → accusation rumor 생성
- `betrayal_witnessed` → betrayal rumor
- `miracle_witnessed` → prophecy rumor

### 6.2 Agent-triggered
- `assert_loyalty` (loud public) → reputation rumor (positive)
- `flee` + witnesses → cowardice rumor
- `confess` (public) → guilt rumor

### 6.3 Environment-triggered
- Famine 지속 → "자원 비축 탓" 음모론 rumor (자동 생성)
- 성전 의식 전후 → 기적 rumor 자동 가능성

---

## 7. Engine 구현 최소 (Phase 5 필요 전)

```python
# engine/world/information/rumor_registry.py
class RumorRegistry:
    def __init__(self):
        self._rumors: dict[str, Rumor] = {}
        self._propagation_graph: dict[str, set[str]] = {}  # agent → neighbors

    def spawn(self, content_tag, target_role, origin_source, ...) -> Rumor: ...
    def step(self, tick: int) -> None:  # propagate + decay
    def get_active_rumors_about(self, target: str) -> list[Rumor]: ...
    def get_reach_fraction(self, rumor_id: str, population_size: int) -> float: ...
```

---

## 8. Phase 3 §5.7 완료 기준 매핑

| 기준 | 달성 방식 |
|---|---|
| 사람 없이 state 변경 | decay / credibility drift 자동 |
| 다른 layer와 coupling | §5 table 5개 layer 결합 |
| 비선형 world state 변화 | Phase transition: rumor reach > threshold → crowd dynamics 변화 → authority response → 추가 rumor |

---

## 9. Micro-world 예시 (Phase 5 연계)

**시나리오:** 10명 micro-world, 1명이 target_role=outsider.

**Rumor lifecycle:**
1. Tick 3: `crowd_mockery` event → accusation rumor spawn (intensity 0.8, reach={witness_agent})
2. Tick 4-7: merchant agent (hub) 전파 → reach=6/10
3. Tick 8: distortion 0.4 → "단순 실수" → "의도적 배신" 왜곡
4. Tick 10: authority agent → 억제 시도 → credibility 0.7 (강도 유지)
5. Tick 12-15: crowd alignment 상승 → blame_concentration on outsider
6. Tick 20: tipping point — phase transition to `lynch_mode` OR authority stops

**이 flow 는 handcraft 없이 emergent.**

---

**End of rumor propagation.**
