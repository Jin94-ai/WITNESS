# Agent Initialization Recipe (Step K)

**작성:** 2026-04-24
**목적:** Handcraft 문서 없이 world에 agent를 꽂을 수 있는 최소 입력 템플릿.

---

## 0. 핵심 전환

**Before:** Peter 한 명 추가에 `content/peter/v3/{initial_state, canonical_events, targets, profile, ...}.json` + 도메인 모듈 + canonical data.

**After:** 7필드 config 하나로 agent 생성.

---

## 1. Minimum Agent Config Schema

```json
{
  "agent_id": "fisher_1",
  "role_cluster": "fisher_laborer",       // H Step role
  "profile_overrides": {                   // optional, persona profile perturbation
    "motif_tendency": {"confront": 1.2}
  },
  "relation_seeds": {                      // target role → named/indexed instance
    "primary_focus": "jesus",
    "peer_group": ["fisher_2", "fisher_3"],
    "family": "fisher_1_family"
  },
  "initial_state_seed": {                  // optional, sparse overrides
    "hope": 7.0, "fear": 2.0
  },
  "recent_history": "witnessed miracle 2 days ago",  // free-text context
  "faction_affiliation": {                 // optional
    "in_group": "galilean_fishers",
    "authority_group": null
  },
  "info_access_level": "peer_network_high" // inherits from role but can override
}
```

**총 7 fields (Lee §15 요구 사항).**

---

## 2. Instantiation 알고리즘

```python
def instantiate_agent(config: dict, world_context) -> Agent:
    # 1. Role cluster lookup
    role = ROLE_CLUSTERS[config["role_cluster"]]
    
    # 2. Profile: role prior + overrides + random perturbation
    profile = deep_copy(role["profile_prior"])
    if config.get("profile_overrides"):
        deep_merge(profile, config["profile_overrides"])
    apply_perturbation(profile, variance=role["profile_variance"], seed=config.get("seed"))
    
    # 3. Relations: role template + seeds
    relations = build_relations(
        template=role["relation_template"],
        seeds=config.get("relation_seeds", {}),
        world_context=world_context,
    )
    
    # 4. Initial state: role state_prior + seed overrides + world_context effects
    state = deep_copy(role["state_prior"])
    state.update(config.get("initial_state_seed", {}))
    state = apply_world_context(state, world_context, relations)
    
    # 5. Recent history → event residue (symbolic layer)
    if config.get("recent_history"):
        apply_recent_history_tag(state, config["recent_history"])
    
    # 6. Info access: inherit from role, override if specified
    info_access = config.get("info_access_level", role["info_access_level"])
    
    # 7. Faction: optional
    factions = config.get("faction_affiliation", {})
    
    return Agent(
        id=config["agent_id"],
        profile=profile,
        relations=relations,
        state=state,
        role=config["role_cluster"],
        info_access=info_access,
        factions=factions,
    )
```

---

## 3. 예시 agent 3명 (Lee §15 완료 기준)

### 3.1 임의 Galilean 어부 "Jonah bar Simon"

```json
{
  "agent_id": "jonah_bar_simon",
  "role_cluster": "fisher_laborer",
  "profile_overrides": {
    "motif_tendency": {"observe_wait": 1.1, "confront": 0.9}
  },
  "relation_seeds": {
    "peer_group": ["peter_sim", "andrew_sim"],  // existing agents
    "family": "jonah_family"
  },
  "initial_state_seed": {"fatigue": 6.0, "hope": 5.0},
  "recent_history": "good catch yesterday, family relieved",
  "faction_affiliation": {"in_group": "galilean_fishers"},
  "info_access_level": "peer_network_medium"
}
```

→ 엔진은 fisher_laborer prior + 위 overrides 로 즉시 agent 생성. handcraft 문서 불필요.

### 3.2 임의 Jerusalem 상인 "Eliezer"

```json
{
  "agent_id": "eliezer_merchant",
  "role_cluster": "merchant",
  "profile_overrides": {},
  "relation_seeds": {
    "peer_group": ["competing_merchant_1", "competing_merchant_2"],
    "authority_group": "sanhedrin_taxation_dept",
    "family": "eliezer_family"
  },
  "initial_state_seed": {"doubt": 3.0, "resolve": 6.0},
  "recent_history": "tax increase notice received last week",
  "faction_affiliation": {"rival": "competing_merchant_1"},
  "info_access_level": "trade_network_high"
}
```

### 3.3 임의 crowd participant "unnamed_zealot_bystander"

```json
{
  "agent_id": "zealot_bystander_47",
  "role_cluster": "crowd_participant",
  "profile_overrides": {
    "motif_tendency": {"confront": 1.4, "observe_wait": 0.6}
  },
  "relation_seeds": {
    "in_group": "zealot_sympathizers",
    "family": "unnamed_family_47"
  },
  "initial_state_seed": {"anger": 5.0, "hope": 4.0},
  "recent_history": "brother arrested by Romans 6 months ago",
  "faction_affiliation": {"in_group": "zealot_sympathizers"},
  "info_access_level": "crowd_rumor_medium"
}
```

**세 명 모두 Peter급 문서 없이 config 수준으로 정의 가능.**

---

## 4. World-level Bulk Generation

개별 config 대신 분포 기반 대량 생성:

```python
def generate_world_population(world_context, total_agents=200):
    distribution = world_context.population_distribution  # role → proportion
    agents = []
    for role_id, proportion in distribution.items():
        n = int(total_agents * proportion)
        for i in range(n):
            config = {
                "agent_id": f"{role_id}_{i}",
                "role_cluster": role_id,
                # 나머지 role 기본값 상속
            }
            agent = instantiate_agent(config, world_context)
            agents.append(agent)
    return agents
```

200명 자동 생성 (예: Judea 1st century world).

---

## 5. Recent History → State 영향

"recent_history" 자유 텍스트는 엔진이 해석. 최소 구현:

```python
RECENT_HISTORY_TAGS = {
    "witnessed miracle": {"awe": +2.0, "hope": +1.0, "sacred_salience_exposure": 1.0},
    "family illness": {"grief": +1.5, "fear": +1.0},
    "tax increase": {"fear": +0.5, "anger": +1.0, "resolve": +0.5},
    "brother arrested": {"anger": +2.0, "grief": +1.0, "authority_reactivity": +0.3},
    "good catch": {"hope": +1.0, "vitality": +0.5},
}
```

Free-text matcher:
```python
def apply_recent_history_tag(state, text):
    for tag, delta in RECENT_HISTORY_TAGS.items():
        if tag in text.lower():
            for field, amount in delta.items():
                state[field] = clip(state[field] + amount, 0, 10)
```

더 정교한 버전: LLM pre-process (out-of-loop, Rule #4 준수). 사용 시 사전 분석 단계에서만.

---

## 6. Named vs Unnamed agents

| 형태 | 특성 | 예시 |
|---|---|---|
| **Named** (canonical 인물) | 추가 `profile_overrides` 강함, `relation_seeds` 고정, 때로 canonical event 소유 | Peter, Judas, Caiaphas |
| **Unnamed** (population agents) | role_cluster prior 그대로, relations 자동 생성, canonical event 없음 | 군중 구성원, 이름 없는 어부, 상인 |

두 형태 모두 같은 engine에서 작동. Named = Unnamed + overlay.

---

## 7. 완료 기준 점검 (Lee §15)

| 완료 기준 | 상태 |
|---|---|
| Peter/Judas 외 agent 3명을 handcraft 없이 config으로 초기화 | ✓ (Jonah, Eliezer, Zealot bystander) |

**Step K 완료.**

---

## 8. 구현 로드맵

- `engine/population/role_cluster.py` — RoleCluster dataclass + ROLE_CLUSTERS registry
- `engine/population/generator.py` — `instantiate_agent()` + `generate_world_population()`
- `engine/population/history_tags.py` — recent history → state delta
- `content/worlds/judea_1st_century/population.json` — 분포
- `content/worlds/judea_1st_century/role_clusters/` — 10 cluster 정의

---

**End of Step K.**
