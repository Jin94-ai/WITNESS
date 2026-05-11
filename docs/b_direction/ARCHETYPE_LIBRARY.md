# Archetype Library — Reaction Style Templates (Phase 4 B)

**작성:** 2026-04-24
**목적:** Role과 **분리된** reaction style library. Agent = Role × Archetype × specific.

---

## 0. Archetype이 Role과 다른 이유

- **Role** = 구조적 위치 (priest / merchant / fisher)
- **Archetype** = 반응 스타일 (impulsive / calculating / avoidant)

같은 priest 라도 archetype 에 따라 같은 accusation 에 다른 반응:
- **Impulsive priest**: 즉각 공개 denial
- **Calculating priest**: 자원 이동 후 public silence
- **Shame-sensitive priest**: 은둔, 제도 탈퇴 검토

이 차이는 **profile parameter** 로 표현 (handcrafted 아님).

---

## 1. Archetype 12종

### 1.1 Reaction tempo

#### A1. `impulsive`
- motif_tendency: confront +0.3, conceal +0.2, observe_wait -0.3
- tempo: 즉각 반응
- Peter 성향의 핵심

#### A2. `calculating`
- motif_tendency: observe_wait +0.4, conceal +0.2
- deliberation_bias: 高
- Judas / elite_strategist 공통 core

#### A3. `hesitant`
- motif_tendency: observe_wait +0.3, remain_present +0.2, confront -0.3
- 결정 지연

### 1.2 Relation orientation

#### A4. `devoted`
- relation_bias.primary_focus_attachment_strength +0.4
- motif_tendency.seek_repair +0.3
- Peter-post-call, 충성 유형

#### A5. `detached`
- relation_bias.primary_focus_attachment_strength -0.3
- motif_tendency.withdraw +0.2, observe_wait +0.2
- Judas-style 이탈

#### A6. `protective`
- relation_bias: protected_other_concern +0.5 (새 축)
- motif_tendency.remain_present +0.2, confront +0.2
- family_anchor + soldier 공통

### 1.3 Shame/Authority sensitivity

#### A7. `shame_sensitive`
- pressure_sensitivity.shame_exposure +0.4
- recovery_bias.shame_persistence +0.3
- motif_tendency.conceal +0.2, withdraw +0.2

#### A8. `authority_sensitive`
- pressure_sensitivity.social_threat +0.3
- relation_bias.authority_reactivity +0.4
- 권력 앞에서 순응/공포

#### A9. `authority_defiant`
- relation_bias.authority_reactivity -0.3
- motif_tendency.confront +0.3
- 반권력 성향

### 1.4 Repair / exploit

#### A10. `repair_oriented`
- motif_tendency.seek_repair +0.4, confess +0.3
- recovery_bias.trust_restoration_bias +0.3
- 관계 복원 우선

#### A11. `opportunistic`
- motif_tendency.conceal +0.3, observe_wait +0.2
- pressure_sensitivity.urgency +0.2
- 상황 유리 시 행동

#### A12. `avoidant`
- motif_tendency.withdraw +0.4, observe_wait +0.2
- pressure_sensitivity.isolation_pressure -0.2 (견딤)
- outsider 핵심

---

## 2. Archetype stacking

**한 agent는 최대 2 archetype 조합** (Lee 권장: 과잉 방지).

```json
{
  "role": "fisherman_laborer",
  "archetypes": ["impulsive", "devoted"],
  "specific_overrides": {"motif_tendency.seek_repair": 1.5}
}
```

Application:
```python
profile = deep_copy(role.profile_prior)
for archetype in archetypes:
    apply_delta(profile, ARCHETYPE_DELTAS[archetype])
apply_delta(profile, specific_overrides)
perturb_profile(profile, variance=0.10)  # gaussian noise
```

---

## 3. Archetype 공식 정의 (JSON)

```json
{
  "archetype_id": "impulsive",
  "description": "Immediate reaction, low deliberation, swings between confront and conceal",
  "profile_deltas": {
    "motif_tendency": {
      "confront": 0.3,
      "conceal": 0.2,
      "observe_wait": -0.3
    },
    "pressure_sensitivity": {
      "urgency": 0.2
    },
    "tempo": {
      "impulsivity": 0.4,
      "deliberation_bias": -0.3
    }
  }
}
```

(`tempo` section은 Step E §4.2 E-5에 선언. 구현 시 추가.)

---

## 4. Peter / Judas / VG 재구성

**각 인물 = role × archetypes (handcrafted profile.json 대신)**

| Character | Role transition | Archetypes | 과거 specific overrides |
|---|---|---|---|
| Peter | `fisherman_laborer → disciple_follower` | `impulsive`, `devoted` | seek_repair 1.4, confront 1.3 |
| Judas | `disciple_follower → elite_strategist (pre-betrayal)` | `calculating`, `detached` | observe_wait 1.3, seek_repair 0.4 |
| VG | `spiritual_wanderer + family_anchor overlay` | `shame_sensitive`, `devoted` (to Theo) | grief_tail 1.5, peer_dependence 0.5 |

**기대 결과:** 기존 handcrafted profile 과 비슷한 parameter 자동 생성. **Role+Archetype 조합으로 80-90% 재현** 가능 목표.

---

## 5. Archetype Gap (현재 engine에서 표현 부족)

- **"절망/자기 파괴" archetype** (Judas + VG 필요) → 현재 motif 8개로 cover 안 됨. Lee 지적 "protect/exploit/attach/detach 추가 후보" 와 더불어 `despair` archetype 고려.
- **"정치적 계략" archetype** (Judas, elite 특수) → `calculating` + `detached` 조합으로 표현하나 "은밀 계획 실행" 별도 motif 필요할 수도 (Phase 2 motif 12개 제약 내 허용).

---

## 6. Archetype 조합으로 인물 생성 (예시)

### 6.1 새 agent "Barabbas" (반권력 저항자)
```python
role="outsider",
archetypes=["impulsive", "authority_defiant"],
specific_overrides={
    "motif_tendency.confront": 1.5,
    "pressure_sensitivity.physical_threat": 1.3
},
relations={"in_group": "zealot_band", "rival": "soldier_enforcer_group"}
```

### 6.2 새 agent "Mary of Magdala"
```python
role="disciple_follower",
archetypes=["devoted", "shame_sensitive"],
specific_overrides={
    "motif_tendency.grieve": 1.3,
    "motif_tendency.seek_repair": 1.2,
    "relation_bias.primary_focus_attachment_strength": 1.5
},
relations={"primary_focus": "jesus", "peer_group": "women_disciples"}
```

### 6.3 새 agent "Centurion"
```python
role="soldier_enforcer",
archetypes=["protective", "authority_sensitive"],
specific_overrides={
    "motif_tendency.remain_present": 1.2
},
relations={"peer_group": "roman_cohort", "protected_other": "own_servant"}
```

세 명 모두 **role + archetype + 최소 overrides** 로 기존 profile.json 없이 생성 가능.

---

## 7. 완료 기준 (Lee §6.7)

| 기준 | 달성 여부 |
|---|---|
| 새 agent "새 규칙 추가 없이" 생성 | ✓ role + archetypes + overrides |
| 8-12명 micro-world 자동 초기화 | ✓ generate_population 가능 |
| role + archetype + world position 만으로 agent 간 차이 | ✓ (본 문서 §4, §6) |

---

**End of Archetype Library.**
