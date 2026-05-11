# Micro-World Specifications (Phase 5)

**작성:** 2026-04-24
**목적:** 8-12명 micro-world 3개로 shared engine + population grammar + world process가 실제 emergent dynamics 를 생성하는지 검증.

---

## 0. 원칙 (Lee §7.3)

**목적은 "좋은 story" 가 아님.**
- 구조가 어떤 흐름을 낳는지 확인
- Rumor → crowd → authority flow
- Sacred salience → costly confession/presence
- 반복 exposure → collapse/repair divergence

---

## 1. Micro-World 1 — "Accusation Scene" (생성된 부인/비난 flow)

**목표:** Peter scenario의 accusation arc를 **handcraft 없이** role + archetype 조합으로 재현.

### 1.1 Cast (10 agents)

| Agent | Role | Archetypes | 역할 |
|---|---|---|---|
| agent_01 | disciple_follower | impulsive, devoted | Peter analog |
| agent_02 | disciple_follower | detached, calculating | Judas analog |
| agent_03 | disciple_follower | devoted, hesitant | baseline disciple |
| agent_04 | priest | calculating, authority_sensitive | accuser |
| agent_05 | soldier_enforcer | protective, authority_sensitive | guard |
| agent_06 | crowd_participant | impulsive | witness 1 |
| agent_07 | crowd_participant | shame_sensitive | witness 2 (young) |
| agent_08 | crowd_participant | authority_defiant | witness 3 (반골) |
| agent_09 | family_anchor | protective, hesitant | agent_01 family |
| agent_10 | outsider | avoidant | peripheral observer |

### 1.2 World Setup

```json
{
  "world_id": "accusation_scene",
  "locations": {
    "priest_courtyard": {
      "visibility": 0.9, "crowdability": 0.7, "authority_reach": 0.9,
      "sacred_proximity": 0.3, "concealment": 0.1
    },
    "upper_room": {
      "visibility": 0.2, "crowdability": 0.3, "authority_reach": 0.1,
      "concealment": 0.7
    },
    "city_street": {
      "visibility": 0.6, "crowdability": 0.9, "authority_reach": 0.5
    }
  },
  "initial_agent_locations": {
    "agent_01-03": "upper_room",
    "agent_04-05": "priest_courtyard",
    "agent_06-08": "city_street",
    "agent_09": "family_home",
    "agent_10": "city_street_periphery"
  },
  "seed_events": [
    {"tick": 3, "event_id": "covert_bargain", "location": "priest_courtyard"},
    {"tick": 8, "event_id": "guard_approaches", "location": "upper_room"}
  ],
  "seed_rumors": [
    {
      "content_tag": "threat_to_authority",
      "target_role": "primary_focus",
      "intensity": 0.6, "credibility": 0.5,
      "origin_location": "priest_courtyard"
    }
  ]
}
```

### 1.3 Expected Emergent Flow (sample prediction)

- Tick 1-7: agent_01-03 upper_room에서 discuss / stay_awake
- Tick 3: covert_bargain → agent_02 role transition 시작 (disciple → elite_strategist)
- Tick 8-12: guard_approaches → agents 흩어짐 (flee / follow_at_distance based on archetype)
- Tick 13-17: agent_01 priest_courtyard 진입 (devoted + impulsive archetype 조합)
- Tick 17-20: accusation event → crowd_participant contagion → alignment_strength 상승
- Tick 17-20: agent_01 conceal motif (shame_sensitive X impulsive) → `deny` 3회 기대
- Tick 21+: agent_01 `grieve` motif + withdraw

### 1.4 검증 항목

**Structural (emergent 가 실제 생겼는가):**
- [ ] rumor propagated across roles
- [ ] crowd phase transition 발생
- [ ] authority reaction chain (arrest / release / threat)
- [ ] 1 agent 빼도 흐름 유지되는가

**Character (handcraft 없이 그럴듯한가):**
- [ ] agent_01 이 denial 가족을 보이는가 (but 특정 tick 아니어도 OK)
- [ ] agent_02 (detached+calculating) 이 escape 경로 잡는가
- [ ] 각 crowd_participant archetype에 따라 다른 반응

---

## 2. Micro-World 2 — "Sacred Gathering" (회중 내 경외/위기)

**목표:** 종교 의식이 sacred_salience + blame_concentration 상승으로 tipping — **Peter arc 와 다른 dynamics**.

### 2.1 Cast (8 agents)

| Agent | Role | Archetypes |
|---|---|---|
| agent_01 | spiritual_wanderer | devoted, authority_defiant | prophet figure |
| agent_02 | priest | shame_sensitive, calculating | establishment |
| agent_03-05 | disciple_follower | devoted, hesitant | followers |
| agent_06-07 | crowd_participant | impulsive, authority_sensitive |
| agent_08 | family_anchor | protective, hesitant | mother of followers |

### 2.2 World Setup
- Primary location: `temple_outer_court` (sacred_proximity 0.9, crowdability 0.8)
- Seasonal phase: `high_festival` → sacred_salience baseline +0.3
- No pre-seeded rumors; 전부 emergent

### 2.3 Expected Emergent Flow
- Prophet agent_01 의 `pray` / `discuss` → rumor "prophecy" 자동 생성 (§Rumor §6.3)
- agent_02 (priest) 의 `observe_wait` motif 지배 → 계산적 대기
- Sacred calendar high-phase → 모든 agent's sacred_salience_baseline +0.3
- **Tipping point:** agent_01 이 `confront` motif 발동 시 → 군중 fragmentation

### 2.4 검증 항목
- [ ] Sacred festival이 agent 반응에 영향 주는가
- [ ] Prophet → crowd alignment 분리 패턴
- [ ] Authority (priest) 대응 시점

---

## 3. Micro-World 3 — "Scarcity & Crowd" (자원 부족 → 비난)

**목표:** Material layer → Social layer coupling으로 **비기독교 scenario** 작동 실증.

### 3.1 Cast (12 agents)

| Agent | Role | Archetypes |
|---|---|---|
| agent_01 | merchant | calculating, opportunistic |
| agent_02 | family_anchor | protective, shame_sensitive |
| agent_03-05 | fisherman_laborer | impulsive, devoted(peer) |
| agent_06 | priest | authority_sensitive |
| agent_07-08 | soldier_enforcer | protective, authority_sensitive |
| agent_09-10 | crowd_participant | impulsive |
| agent_11 | outsider | avoidant, shame_sensitive |
| agent_12 | elite_strategist | calculating, detached |

### 3.2 World Setup
- `material.food_availability = 2.5` (famine 초기)
- `material.disease_prevalence = 0.2` (모자란 영양)
- `rumor_seeds`: "hoarding" against `merchant` (agent_01)
- `space`: multi-location (market_square, granary, poor_quarter)

### 3.3 Expected Emergent Flow
- Tick 1-5: hunger accumulation → fatigue, anger rise (`scarcity → fatigue` coupling)
- Tick 3-7: rumor "hoarding" 확산 (merchant 대상)
- Tick 8-10: crowd alignment + blame_concentration on agent_01
- Tick 11-15: authority (priest + soldier) 개입 or 방관
- Tick 16+: **Tipping**:
  - Authority 개입 → dispersal
  - Authority 방관 → lynch_mode or merchant flight

### 3.4 검증 항목
- [ ] Peter/Judas/VG 없어도 dynamics 발생
- [ ] Role cluster + archetype 조합으로 12 distinct agents 생성
- [ ] Crowd phase transition 관찰
- [ ] Cross-layer coupling (material → social → information → institutional)

---

## 4. 공통 측정 프로토콜

각 micro-world run 시 기록:

### 4.1 Per-tick
- Agent action distribution
- Motif distribution
- Rumor registry state (active rumors, reach, distortion)
- Crowd state (density, alignment, blame_concentration)
- Authority response events

### 4.2 Trajectory-level
- Information flow chart (rumor spawn → reach)
- Relation reconfiguration (before vs after)
- Crowd phase sequence
- Role transitions (if any)
- Emergent story-like arcs (tick structure)

### 4.3 검증 리포트 형식

```
# Micro-World <ID> Run Report

## Emergent patterns observed
- [pattern 1]: observed at ticks X-Y
- [pattern 2]: ...

## Role-driven divergence
- Agent X (role A, archetype B): dominant motif = ...
- Agent Y (role A, archetype C): dominant motif = ... (차이)

## Cross-layer coupling evidence
- material → social: ...
- rumor → crowd: ...

## Counterfactual
- "Agent Z 제거 시": flow 유지 / 붕괴 여부

## Story-likeness
- Tipping points observed: ...
- Meaningful arcs: ...
```

---

## 5. Phase 5 완료 기준 (Lee §7.6)

| 기준 | 달성 방식 |
|---|---|
| 주인공 한 명 직접 몰아가지 않아도 흐름 생김 | 3 world 공통 확인 |
| 1 agent 제거해도 world process 유지 | counterfactual run 수행 |
| World state가 action driver 로 작동 | pressure source 추적에서 확인 |

---

## 6. 구현 로드맵

1. `engine/world/micro_world.py` — Micro-world bootstrap
2. `engine/world/crowd/state.py` — CrowdState (CROWD_DYNAMICS spec)
3. `engine/world/information/rumor_registry.py` — RumorRegistry (RUMOR_PROPAGATION spec)
4. `engine/world/space/spatial_registry.py` — SpatialRegistry (SPACE_AS_AFFORDANCE spec)
5. `content/worlds/accusation_scene/world.json` + `population.json` + `rumors.json`
6. `scripts/run_micro_world.py` — runner

**첫 구현:** Micro-World 1 (accusation_scene) 만. 나머지 2개는 1 검증 후.

---

**End of micro-world specs.**
