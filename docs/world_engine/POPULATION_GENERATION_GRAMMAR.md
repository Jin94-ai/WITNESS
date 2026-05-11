# Population Generation Grammar (Step H)

**작성:** 2026-04-24
**목적:** 개별 인물 handcraft 중단. Role cluster + persona prior + world context로 agent population을 자동 생성.

---

## 0. 핵심 전환

**Before:**
> "다음 인물(유다, 바울, 반 고흐, ...) 을 어떻게 설계할까?"
> → 매 인물마다 Peter급 문서 + 변수 세트 + 규칙 튜닝

**After (목표):**
> "어떤 role cluster와 persona prior로 세계 안의 agent population을 생성할까?"
> → 인물 하나 = role 선택 + profile 샘플링 + relation seed + world context binding

---

## 1. Population Generation 파이프라인

```
world_context
    ↓
role_cluster_distribution (세계가 어떤 role을 얼마나 필요로 하는가)
    ↓
for each role:
    sample persona_profile from role's profile_prior (+ perturbation)
    sample relation_seeds from role's relation_template
    sample initial_state from role's state_prior (+ recent_history overlay)
    bind to world_context (location, faction, info access, etc.)
    → agent config
```

---

## 2. Role Cluster 정의 (10 초안)

각 role cluster는 **profile prior + relation template + action affordance pack** 을 가진다.

### 2.1 `fisher_laborer` (어부/노동자)

**특성:**
- primary_focus_attachment: 중간~높음 (생계 파트너)
- peer_dependence: 높음 (동료 노동자)
- authority_reactivity: 낮음 (권력과 거리)
- impulsivity: 중간~높음 (육체 노동)
- status_concern: 낮음

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "urgency": 1.1, "isolation_pressure": 0.9, "sacred_salience": 0.9
  },
  "motif_tendency": {
    "remain_present": 1.2, "confront": 1.1, "observe_wait": 0.9
  },
  "relation_bias": {
    "peer_dependence": 1.3, "authority_reactivity": 0.7
  }
}
```

**Relation template:** peer_group (동료 3-5), family (가족 필수), primary_focus (선택적)
**Affordances:** physical_labor, move_freely, gather_with_peers
**Info access:** 지역 소문 중심, 공식 정보 낮음
**Resource:** 일용 수입

**사례:** Peter (Galilean fisher), 광야 이스라엘 초기 상태

---

### 2.2 `disciple_follower` (제자/추종자)

**특성:**
- primary_focus_attachment: 매우 높음 (핵심)
- peer_dependence: 높음 (공동체 내 정체성)
- sacred_salience_sensitivity: 높음
- authority_reactivity: 중간 (종교 권위)
- belonging_need: 높음

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "sacred_salience": 1.4, "loyalty_pull": 1.3
  },
  "motif_tendency": {
    "remain_present": 1.1, "seek_repair": 1.2
  },
  "relation_bias": {
    "primary_focus_attachment_strength": 1.4, "peer_dependence": 1.2
  }
}
```

**Relation template:** primary_focus (필수), peer_group (공동체), authority_group (선택적 적대/의존)
**Affordances:** pray, discuss, follow_travel, witness_act
**Info access:** 스승 말씀 직접, 외부 정보 peer 경유
**Resource:** 공동 기금/기부

**사례:** Peter (post-call), 12 disciples 대부분, Judas (pre-betrayal)

---

### 2.3 `authority_priest` (종교/권력)

**특성:**
- status_concern: 높음
- authority_reactivity: 높음 (같은 layer 경쟁)
- public_exposure_sensitivity: 높음
- deliberation_bias: 높음 (즉흥 결정 회피)
- rival_awareness: 높음

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "shame_exposure": 1.3, "urgency": 1.2, "isolation_pressure": 0.7
  },
  "motif_tendency": {
    "confront": 1.2, "observe_wait": 1.3, "remain_present": 0.9
  },
  "relation_bias": {
    "authority_reactivity": 1.4, "public_exposure_sensitivity": 1.3
  }
}
```

**Relation template:** peer_group (동료 제사장), rival (경쟁 제사장), public_group (통치 대상), authority_group (상위 권력)
**Affordances:** convene_council, issue_ruling, summon_authority
**Info access:** 공식 정보 높음, 하층 소문 낮음
**Resource:** 제도 자원

**사례:** Caiaphas, 산헤드린 구성원

---

### 2.4 `merchant` (상인)

**특성:**
- status_concern: 중간
- deliberation_bias: 높음 (계산적)
- ambiguity_tolerance: 높음
- authority_reactivity: 중간 (세금/규제 관계)
- info_access_bias: 높음 (거래 네트워크)

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "uncertainty": 1.2, "urgency": 1.1
  },
  "motif_tendency": {
    "observe_wait": 1.3, "remain_present": 1.0
  },
  "relation_bias": {
    "peer_dependence": 1.0, "public_exposure_sensitivity": 1.1
  }
}
```

**Relation template:** peer_group (동업자), public_group (고객), authority_group (세관/제사장)
**Affordances:** trade, travel_routes, bribe, withhold_goods
**Info access:** 경제 동향 높음, 상점 왕래 소문 중간
**Resource:** 축적 자본 + 유동 자본

---

### 2.5 `outsider` (외부자)

**특성:**
- belonging_need: 양극화 (매우 높거나 매우 낮음)
- authority_reactivity: 낮음 또는 적대
- ambiguity_tolerance: 높음
- peer_dependence: 낮음

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "isolation_pressure": 1.3, "shame_exposure": 1.2
  },
  "motif_tendency": {
    "withdraw": 1.3, "observe_wait": 1.2, "confront": 0.8
  },
  "relation_bias": {
    "peer_dependence": 0.6
  }
}
```

**Relation template:** family (원거리 또는 단절), 우연한 peer, rival (많음)
**Affordances:** move_alone, stay_hiding, beg, witness_unobserved
**Info access:** 낮음
**Resource:** 빈곤

**사례:** 나병환자, 세리, 이방인

---

### 2.6 `family_anchor` (가족 중심)

**특성:**
- family_attachment: 매우 높음
- protected_other_concern: 높음 (부양 대상)
- risk_aversion: 높음
- impulsivity: 낮음

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "urgency": 1.2, "isolation_pressure": 1.1
  },
  "motif_tendency": {
    "remain_present": 1.3, "withdraw": 1.1
  },
  "relation_bias": {
    "primary_focus_attachment_strength": 1.3
  }
}
```

**Relation template:** family (필수, 강함), intimate_other (배우자/부모), peer_group (이웃)
**Affordances:** protect_family, gather_resource, refuse_risk
**Info access:** 가족/이웃 채널

**사례:** 마리아와 마르다, 일반 유대 가정주

---

### 2.7 `crowd_participant` (군중 구성원)

**특성:**
- individual agency 낮음 (군중에 흡수)
- volatility: 높음 (군중 에너지 반영)
- information_bias: 높음 (소문 영향 강)
- authority_reactivity: 양극화

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "social_threat": 1.3, "shame_exposure": 1.2
  },
  "motif_tendency": {
    "remain_present": 1.2, "confront": 1.2 (when crowd excited), "withdraw": 1.1 (when crowd fearful)
  },
  "relation_bias": {
    "public_exposure_sensitivity": 1.3
  }
}
```

**Relation template:** in_group (군중 그 자체), 약한 family, public_group (군중 밖)
**Affordances:** shout, stone, flee_with_crowd
**Info access:** 소문 기반, 변동적
**Resource:** 다양

**사례:** 예루살렘 군중, 성전 앞 인파

---

### 2.8 `soldier_enforcer` (군인/집행자)

**특성:**
- authority_reactivity: 상위 복종 + 하위 통제
- impulsivity: 중간~높음
- duty_orientation: 높음
- empathy_restraint: 높음 (역할 분리)

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "urgency": 1.3, "physical_threat": 1.2
  },
  "motif_tendency": {
    "confront": 1.3, "remain_present": 1.0
  },
  "relation_bias": {
    "authority_reactivity": 1.3
  }
}
```

**Relation template:** peer_group (동료 군인), authority_group (명령자), public_group (통제 대상)
**Affordances:** arrest, escort, use_weapon, refuse_order (드뭄)
**Info access:** 명령 정보

**사례:** 로마 군인, 성전 경비

---

### 2.9 `elite_strategist` (엘리트/계략가)

**특성:**
- deliberation_bias: 매우 높음
- information_access: 높음
- risk_tolerance: 중간
- rival_awareness: 매우 높음
- empathy_restraint: 중간

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "uncertainty": 1.3, "shame_exposure": 0.8
  },
  "motif_tendency": {
    "observe_wait": 1.4, "conceal": 1.2
  },
  "relation_bias": {
    "authority_reactivity": 1.2, "peer_dependence": 0.8
  }
}
```

**Relation template:** rival (필수), peer_group (작지만 전략적), authority_group (상하위)
**Affordances:** negotiate, inform_on, withhold_info, manipulate_crowd
**Info access:** 교차 네트워크, 상위
**Resource:** 정치 자본

**사례:** Judas (post-bargain), 헤롯 측근

---

### 2.10 `spiritual_wanderer` (영적 방랑자)

**특성:**
- sacred_salience_sensitivity: 매우 높음
- belonging_need: 낮음
- ambiguity_tolerance: 매우 높음
- impulsivity: 중간

**Profile prior:**
```json
{
  "pressure_sensitivity": {
    "sacred_salience": 1.5, "isolation_pressure": 0.7
  },
  "motif_tendency": {
    "observe_wait": 1.3, "seek_repair": 1.1
  },
  "relation_bias": {
    "authority_reactivity": 0.6, "peer_dependence": 0.6
  }
}
```

**Relation template:** sacred_focus (필수), 느슨한 peer
**Affordances:** wander, preach, fast, isolate
**Info access:** 공동체 바깥 관점

**사례:** 세례 요한, 광야의 예언자들

---

## 3. Role Cluster Schema (formal)

각 cluster는 아래 JSON 가능:

```json
{
  "role_id": "disciple_follower",
  "description": "...",
  "profile_prior": {
    "pressure_sensitivity": { ... },
    "motif_tendency": { ... },
    "recovery_bias": { ... },
    "relation_bias": { ... }
  },
  "profile_variance": 0.15,   // 랜덤 편차 범위
  "relation_template": {
    "required": ["primary_focus", "peer_group"],
    "optional": ["authority_group", "family"]
  },
  "affordance_pack": ["pray", "discuss", "follow_travel", "witness_act"],
  "info_access_level": "peer_network_high",
  "resource_prior": "communal_low"
}
```

---

## 4. Profile Sampling

새 agent 생성 시:

```python
def generate_agent(role_id: str, world_context, seed):
    role = ROLE_CLUSTERS[role_id]
    prior = role["profile_prior"]
    variance = role["profile_variance"]
    
    # Sample profile: prior + gaussian perturbation
    profile = deep_copy(prior)
    for axis in all_axes:
        profile[axis] += gauss(0, variance)
    
    # Sample relation seeds
    relations = {}
    for target_role in role["relation_template"]["required"]:
        relations[target_role] = world_context.get_instance(target_role)
    
    # Initial state from role prior + world context
    state = role["state_prior"].copy()
    state = apply_world_context(state, world_context)
    
    return Agent(profile, relations, state, role_id)
```

---

## 5. World-level Population Distribution

World는 role cluster 분포를 가진다:

```json
// content/worlds/judea_1st_century/population.json
{
  "world_id": "judea_1st_century_passion",
  "total_agents": 200,
  "role_distribution": {
    "fisher_laborer": 0.30,
    "disciple_follower": 0.06,  
    "authority_priest": 0.05,
    "merchant": 0.10,
    "outsider": 0.08,
    "family_anchor": 0.20,
    "crowd_participant": 0.15,
    "soldier_enforcer": 0.03,
    "elite_strategist": 0.02,
    "spiritual_wanderer": 0.01
  }
}
```

World가 `generate_population()` 하면 분포대로 agent 200명 자동 생성.

---

## 6. Named agent overlay (선택적)

Peter/Judas 같은 특정 인물은 cluster 위에 특수 profile overlay:

```json
// content/peter/v3/profile.json (기존)
{
  "base_role_cluster": "fisher_laborer",
  "transitioned_to": "disciple_follower",  // 서사 상 전환
  "profile_overrides": {
    "motif_tendency": {"seek_repair": 1.4, "confront": 1.3},
    "relation_bias": {"primary_focus_attachment_strength": 1.4}
  },
  "named_relations": {
    "primary_focus": "jesus",
    "peer_group": "twelve_disciples"
  }
}
```

즉 **Peter = fisher_laborer → disciple_follower + 특수 overlay**. 일반 경로로 설명 가능.

---

## 7. 완료 기준 점검 (Lee §12)

| 완료 기준 | 상태 |
|---|---|
| 6개 이상 role cluster 정의 | ✓ 10개 |
| 각 cluster가 profile prior + relation template 소유 | ✓ |
| 새 agent = role + profile + world context로 instantiate 가능 | ✓ schema 명시 |

**Step H 완료.**

---

## 8. 후속 작업

- 실제 RoleCluster dataclass 구현 (`engine/population/role_cluster.py`)
- World population generator (`engine/population/generator.py`)
- Judea 1st century world content (`content/worlds/judea_1st_century/`)

---

**End of Step H.**
