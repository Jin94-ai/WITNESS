# Cross-Layer Couplings (Step J)

**작성:** 2026-04-24
**목적:** 6 world layer 간 coupling rule 20+ 정의. **레이어 수보다 coupling 풍부함이 중요**.

---

## 0. Coupling 분류 체계

각 coupling은 다음 속성을 가짐:
- **source_layer**, **target_layer**
- **rule**: 논리/공식
- **dynamics_type**: human-driven / structure-driven / environment-driven
- **polarity**: positive (증폭) / negative (억제) / threshold
- **lag**: immediate / slow (tick 단위)

---

## 1. Coupling 목록 (25개)

### Material-driven

#### C01. Material → Social (scarcity → cohesion loss)
- **Rule:** `material.food_availability < 3.0 AND duration > 5 ticks → social.community_cohesion decreases 0.02/tick`
- **dynamics_type:** structure-driven
- **polarity:** negative
- **lag:** slow (5-tick buffer)
- **rationale:** 자원 부족 지속 시 공동체 갈등 증가

#### C02. Material → Institutional (abundance → tax yield)
- **Rule:** `material.food_availability > 8.0 → institutional.tax_yield_rate +0.01/tick`
- **dynamics_type:** structure-driven
- **polarity:** positive
- **lag:** slow
- **rationale:** 잉여 자원이 제도 자원 추출 가능케 함

#### C03. Material → Social (plague → crowd dispersal)
- **Rule:** `material.disease_prevalence > 0.5 → social.crowd_density_distribution[public] -0.3`
- **dynamics_type:** environment-driven (disease transmission)
- **polarity:** negative
- **lag:** immediate

#### C04. Material → Institutional (famine → legitimacy decline)
- **Rule:** `material.food_availability < 2.0 for >10 ticks → institutional.institutional_inertia -0.1 (권위 훼손 가속)`
- **dynamics_type:** environment-driven
- **polarity:** negative
- **lag:** slow (10-tick)

### Institutional-driven

#### C05. Institutional → Social (enforcement → crowd suppression)
- **Rule:** `institutional.law_enforcement_strength × institutional.punishment_harshness → social.crowd_density_distribution[public] decay factor ×0.9`
- **dynamics_type:** human-driven (공권력 active 집행)
- **polarity:** negative
- **lag:** immediate

#### C06. Institutional → Symbolic (authority → sacred legitimacy)
- **Rule:** `institutional.authority_concentration > 0.7 → symbolic.sacred_calendar_phase events gain +0.15 weight`
- **dynamics_type:** human-driven
- **polarity:** positive
- **lag:** slow

#### C07. Institutional → Informational (censorship → rumor distortion)
- **Rule:** `institutional.law_enforcement_strength > 0.6 → informational.info_distortion_rate +0.1/tick (공식 정보 vs 뒷소문 격차)`
- **dynamics_type:** human-driven
- **polarity:** positive (distortion 증가)
- **lag:** immediate

#### C08. Institutional → Material (tax extraction → scarcity)
- **Rule:** `institutional.tax_yield_rate × population_size → material.food_availability -0.05/tick`
- **dynamics_type:** human-driven
- **polarity:** negative
- **lag:** seasonal

### Social-driven

#### C09. Social → Informational (cohesion → rumor veracity)
- **Rule:** `social.community_cohesion > 0.7 → informational.source_trustworthiness[in_group] +0.2`
- **dynamics_type:** human-driven
- **polarity:** positive
- **lag:** immediate

#### C10. Social → Symbolic (reputation → honor)
- **Rule:** `social.reputation_network[agent] × 0.6 → symbolic.honor_score[agent]`
- **dynamics_type:** human-driven
- **polarity:** positive
- **lag:** immediate

#### C11. Social → Institutional (faction power → authority)
- **Rule:** `social.faction_alliances[faction].size / total_pop × institutional.authority_concentration (faction별)`
- **dynamics_type:** human-driven
- **polarity:** positive
- **lag:** slow

#### C12. Social → Informational (crowd density → rumor diffusion speed)
- **Rule:** `social.crowd_density_distribution[public] × informational.rumor_intensity propagation_rate = base × (1 + density × 0.5)`
- **dynamics_type:** human-driven
- **polarity:** accelerator
- **lag:** immediate

### Informational-driven

#### C13. Informational → Social (rumor → reputation collapse)
- **Rule:** `informational.rumor_intensity[agent] > threshold AND informational.source_trustworthiness > 0.5 → social.reputation_network[agent] -0.3`
- **dynamics_type:** human-driven
- **polarity:** negative
- **lag:** slow (3-tick)

#### C14. Informational → Institutional (public truth → legitimacy damage)
- **Rule:** `informational.secret_containment break + target_is_authority → institutional.authority_concentration[target] -0.15`
- **dynamics_type:** human-driven
- **polarity:** negative
- **lag:** slow

#### C15. Informational → Symbolic (prophecy → sacred boost)
- **Rule:** `informational.rumor_intensity_map[prophecy_tag] > 0.7 AND source_trustworthiness[sacred] > 0.6 → symbolic.sacred_salience_baseline +0.15`
- **dynamics_type:** human-driven
- **polarity:** positive
- **lag:** slow

### Symbolic-driven

#### C16. Symbolic → Institutional (sacred period → authority boost)
- **Rule:** `symbolic.sacred_calendar_phase in {high_festival} → institutional.authority_concentration[religious] +0.10`
- **dynamics_type:** structure-driven (calendar 자동)
- **polarity:** positive
- **lag:** cyclic

#### C17. Symbolic → Social (taboo violation → community expulsion)
- **Rule:** `symbolic.shame_taboos[violated] AND violator in community → social.community_cohesion for violator_group -0.2`
- **dynamics_type:** human-driven
- **polarity:** negative (제재)
- **lag:** immediate

#### C18. Symbolic → Personal state (sacred calendar phase → sacred_salience baseline)
- **Rule:** `symbolic.sacred_calendar_phase = high → all agents.pressure.sacred_salience_baseline +0.3`
- **dynamics_type:** structure-driven
- **polarity:** positive
- **lag:** cyclic

### Temporal-meta

#### C19. Temporal → All (event_residue decay)
- **Rule:** `temporal.event_residue_stack[event] half-life varies by layer (Material 90d / Institutional 365d / Social 30d / Informational 15d / Symbolic 180d)`
- **dynamics_type:** structure-driven
- **polarity:** decay
- **lag:** continuous

#### C20. Temporal → Any (tipping point trigger)
- **Rule:** `IF sum of slow_variables across layers crosses temporal.tipping_threshold THEN regime_switch`
- **dynamics_type:** meta
- **polarity:** regime shift
- **lag:** threshold-based

### Cascading couplings

#### C21. Material → Social → Informational (scarcity → gossip about hoarders)
- **Rule:** C01 triggers → `informational.rumor_intensity_map["hoarding"] +0.2`
- **dynamics_type:** cascading
- **lag:** 2 steps

#### C22. Institutional shock → Symbolic → Social (execution ritual → shame spread)
- **Rule:** `institutional.punishment_event (public) → symbolic.shame_taboo invoked → social.crowd_density -0.2 (분산)`
- **dynamics_type:** cascading
- **lag:** immediate

#### C23. Informational → Social → Institutional (rumor → faction split → authority challenge)
- **Rule:** `informational.rumor_intensity about authority legitimacy → social.faction_alliances split → institutional.authority_concentration -0.1`
- **dynamics_type:** cascading
- **lag:** 3 steps, slow

### Environment-pure

#### C24. Environment → Material (climate → food)
- **Rule:** `climate.harshness determines harvest multiplier in food production function`
- **dynamics_type:** environment-driven
- **polarity:** modulator
- **lag:** seasonal

#### C25. Environment → Social (season → gathering cadence)
- **Rule:** `temporal.seasonal_phase = festival → social.crowd_density_distribution baseline +0.3`
- **dynamics_type:** environment-driven
- **polarity:** positive
- **lag:** cyclic

---

## 2. 분류 통계

### 2.1 Dynamics type
- human-driven: 11 (C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C17)
- structure-driven: 5 (C01, C02, C16, C18, C19)
- environment-driven: 4 (C03, C04, C24, C25)
- cascading: 3 (C21, C22, C23)
- meta: 1 (C20)

**Human-driven 약 44%, non-human 약 56%** — Rule #5 "세계는 사람만으로 돌아가지 않는다" 준수.

### 2.2 Polarity
- positive: 9
- negative: 10
- decay/modulator: 5
- regime shift: 1

### 2.3 Lag distribution
- immediate: 10
- slow (3-10 tick): 8
- seasonal/cyclic: 5
- threshold-based: 2

---

## 3. Coupling 구현 (JSON schema)

```json
{
  "coupling_id": "C01",
  "source_layer": "material",
  "target_layer": "social",
  "rule": {
    "condition": {"material.food_availability": "< 3.0", "duration": "> 5"},
    "effect": {"social.community_cohesion": "-0.02/tick"}
  },
  "dynamics_type": "structure-driven",
  "polarity": "negative",
  "lag_ticks": 5,
  "human_required": false
}
```

전체 coupling 저장:
`content/worlds/<world_id>/couplings.json`

---

## 4. 완료 기준 점검 (Lee §14)

| 완료 기준 | 상태 |
|---|---|
| 20+ coupling 정의 | ✓ 25개 |
| human-driven / structure-driven / environment-driven 분류 포함 | ✓ 11 / 5 / 4 (+ cascading/meta) |
| 각 coupling에 source, target, expected effect 기록 | ✓ |

**Step J 완료.**

---

## 5. 후속 작업

- Coupling 실행 엔진 구현 (`engine/world/coupling_engine.py`)
- 각 coupling를 매 tick or lag마다 평가
- Conflict resolution (여러 coupling이 같은 state 변경 시 우선순위)

---

**End of Step J.**
