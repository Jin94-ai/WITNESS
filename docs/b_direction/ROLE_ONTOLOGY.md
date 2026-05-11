# Role Ontology — Social-Structural Identity (Phase 4 A)

**작성:** 2026-04-24
**목적:** Role = 사회-구조적 위치. Archetype = 반응 스타일. 두 축을 **명확히 분리**.

---

## 0. Role vs Archetype 분리 원칙

Lee §6.4: *"role과 archetype은 어떻게 분리할 것인가? 어떤 차이는 role에서 오고, 어떤 차이는 archetype에서 오는가?"*

**Role:** 사회-구조적 위치. "무엇이 가능하고 무엇이 제약되는가" 결정.
- 정보 접근, 권력 관계, 자원, affordance, 공간 이동성

**Archetype:** 반응 스타일. "같은 상황에서 어떻게 반응하는가" 결정.
- Profile parameter (motif tendency / recovery bias / relation bias)

**조합:** 같은 role + 다른 archetype = 다른 trajectory. 다른 role + 같은 archetype = 다른 trajectory.

---

## 1. Role Ontology (12 roles)

기존 10 role cluster를 확장하여 12 role로 고정 (Lee §6.3 예시 모두 포함):

### 1.1 Production roles

| Role | Description | 정보 접근 | 권력 | 자원 |
|---|---|---|---|---|
| **fisherman_laborer** | 어부, 농민, 기술자 | 지역 소문 | 낮음 | 생계 |
| **artisan** | 숙련 기술자 (도예, 목수, 대장장이) | 작업장 네트워크 | 낮음-중간 | 축적 가능 |
| **merchant** | 상인, 교역업자 | 교역 네트워크 高 | 중간 (돈) | 축적 자본 |

### 1.2 Authority roles

| Role | Description | 정보 접근 | 권력 | 자원 |
|---|---|---|---|---|
| **priest** | 종교 지도자 | 공식 정보 高 | 신성 권위 | 제도 자원 |
| **ruler** | 정치/군사 권력자 | 국가 정보 | 군사/행정 | 국가 자원 |
| **soldier_enforcer** | 군인, 경비, 집행관 | 명령 체인 | 물리적 | 공급됨 |

### 1.3 Community roles

| Role | Description | 정보 접근 | 권력 | 자원 |
|---|---|---|---|---|
| **disciple_follower** | 스승/지도자 추종자 | primary_focus 직접 | 낮음 (집단) | 공동 |
| **family_anchor** | 가정 중심 (부모, 가장) | 가족/이웃 | 가족 내 | 가정 |
| **crowd_participant** | 익명 군중 구성원 | 소문 기반 | 집단 일부 | 가변 |

### 1.4 Marginal roles

| Role | Description | 정보 접근 | 권력 | 자원 |
|---|---|---|---|---|
| **outsider** | 사회적 경계인 (질병자, 이방인, 낙인자) | 매우 낮음 | 없음 | 결핍 |
| **spiritual_wanderer** | 예언자, 방랑 교사, 은자 | 독립 관찰 | 도덕적 권위 | 최소 |
| **elite_strategist** | 전략가, 고문, 책사 | cross-network 高 | 정치 자본 | 정치 |

---

## 2. Role Dimensions (공식화)

각 role은 **5 구조 축** 으로 측정:

```python
@dataclass
class RoleStructuralProfile:
    information_access: float     # 0-1 (정보 접근성)
    power_reach: float            # 0-1 (영향력 범위)
    resource_stability: float     # 0-1 (자원 안정성)
    spatial_mobility: float       # 0-1 (이동 자유도)
    sanction_exposure: float      # 0-1 (처벌 노출도)
```

### 2.1 12 role의 dimension values

| Role | info | power | resource | mobility | sanction |
|---|---:|---:|---:|---:|---:|
| fisherman_laborer | 0.3 | 0.2 | 0.5 | 0.5 | 0.3 |
| artisan | 0.4 | 0.3 | 0.6 | 0.4 | 0.3 |
| merchant | 0.7 | 0.5 | 0.8 | 0.9 | 0.4 |
| priest | 0.8 | 0.8 | 0.9 | 0.3 | 0.2 |
| ruler | 0.9 | 1.0 | 1.0 | 0.7 | 0.1 |
| soldier_enforcer | 0.6 | 0.7 | 0.6 | 0.8 | 0.2 |
| disciple_follower | 0.5 | 0.2 | 0.4 | 0.6 | 0.4 |
| family_anchor | 0.4 | 0.3 | 0.5 | 0.3 | 0.3 |
| crowd_participant | 0.3 | 0.3 | 0.3 | 0.5 | 0.5 |
| outsider | 0.1 | 0.1 | 0.2 | 0.3 | 0.9 |
| spiritual_wanderer | 0.4 | 0.4 | 0.2 | 0.9 | 0.5 |
| elite_strategist | 0.9 | 0.7 | 0.8 | 0.7 | 0.4 |

---

## 3. Role → Action affordance mapping

각 role은 가능한 action의 base set을 정의:

```python
ROLE_AFFORDANCES: dict[str, set[str]] = {
    "fisherman_laborer": {
        "follow_closely", "discuss", "stay_awake", "assert_loyalty",
        "withdraw_in_fear", "flee", "pray", "draw_net",
    },
    "priest": {
        "convene_council", "issue_ruling", "bless", "curse",
        "discuss", "stay_awake", "withdraw_in_fear", "confess",
    },
    "soldier_enforcer": {
        "arrest", "escort", "draw_sword", "flee", "follow_closely",
        "stand_guard", "intimidate",
    },
    # ... (full mapping in content/worlds/.../role_affordances.json)
}
```

**장점:** Agent의 action vocabulary가 role에 의해 자동 결정. handcraft 불필요.

---

## 4. Role transitions

Agent의 role은 고정 아닐 수 있음:

### 4.1 Voluntary transitions
- `fisherman_laborer → disciple_follower` (religious call)
- `disciple_follower → spiritual_wanderer` (Paul-like)
- `crowd_participant → disciple_follower` (conversion)

### 4.2 Forced transitions
- `disciple_follower → outsider` (excommunication)
- `merchant → outsider` (bankruptcy + sanction)
- `family_anchor → outsider` (widow, orphan)

### 4.3 Narrative transitions (Peter example)
- tick 0: `fisherman_laborer`
- tick 5 (call): `fisherman_laborer → disciple_follower`
- tick 17-20 (denial): `disciple_follower` (내적 conflict; role 유지)
- tick 28 (restoration): `disciple_follower → elite_strategist` (shepherd)

Role transition은 **major life events** 로만 발생. tick 단위 fluid 금지.

---

## 5. Role priors → Profile interaction

`engine/population/role_cluster.py` 의 `profile_prior` 는 role 별 motif/relation bias.

**중요:** role prior는 **baseline**. 개별 agent는 archetype 과 profile_overrides 로 조정.

예:
- base fisherman_laborer: peer_dependence=1.3
- Peter-like override: primary_focus_attachment=1.4, seek_repair=1.4 (특수)
- 평범 어부: overrides 없음

---

## 6. Phase 4 §6.4 핵심 질문 답

### "Role과 archetype 어떻게 분리?"
- **Role = 구조적 가능 공간** (info_access, power, resource, mobility, sanction)
- **Archetype = 반응 스타일** (motif tendency, recovery, relation bias)
- Agent = role × archetype × specific profile_overrides × world_context

### "어떤 차이가 role / archetype?"
- **Role 차이:** "X는 arrest 가능하나 Y는 불가" — 구조 제약
- **Archetype 차이:** "같은 accusation에 X는 deny, Y는 confess" — 반응 스타일

### "개별 인물 고유성 어디서?"
- 4 축 조합:
  1. Role (12 중 하나, 드물게 전환)
  2. Archetype (ARCHETYPE_LIBRARY 에서 한두 개)
  3. Profile_overrides (specific adjustments)
  4. Relation seeds (누구와 관계)
  5. World position (어느 location, 어느 faction)

---

## 7. Micro-world role distribution 예시

8-12명 micro-world 권장 분포:

```json
{
  "disciple_follower": 3,
  "priest": 1,
  "soldier_enforcer": 1,
  "crowd_participant": 2,
  "outsider": 1,
  "elite_strategist": 1,
  "family_anchor": 1
  # Total: 10
}
```

다양한 role × archetype 조합으로 **생성된** agent 들 → emergent dynamics 관찰.

---

**End of role ontology.**
