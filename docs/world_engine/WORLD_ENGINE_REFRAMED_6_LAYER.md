# World Engine 6-Layer Reframed (Step I)

**작성:** 2026-04-24
**목적:** 기존 6-layer (calendar/crowd/economy/politics/factions/rumours) 를 **정적 카테고리 → process engine** 으로 재정의.

---

## 0. 핵심 전환

**기존 6-layer 의 문제:**
- 폴더 분류 수준 (calendar / crowd / economy / ...)
- 각 layer가 데이터 저장소로만 작동
- 사람 없이는 update 안 됨
- Layer 간 coupling 명시 약함

**재정의 원칙 (Lee §13):**
- 각 layer는 **state + process + shock + slow variable + decay + coupling** 보유
- 사람 independent update 가능 (일부)
- 다른 layer와 명시적 coupling

---

## 1. 재정의된 6 Layer

### Layer 1 — Material Layer (물질)

**무엇을 담는가:** 자원 / 생산·소비 / 이동성 / 환경 제약 / 질병·기후.

| 항목 | 설명 |
|---|---|
| **Stored state** | food_availability, transport_feasibility, climate_harshness, disease_prevalence, resource_scarcity |
| **Update process** | 생산 함수 (계절 × 인구), 소비 함수 (인구 × 기본 수요), 기후 stochastic |
| **Shock input** | 기근, 폭풍, 전염병 발발 |
| **Slow variable** | 소작 관계 누적 부채 (multi-year) |
| **Decay / accumulation** | 재고 감쇄 (소비), 기후 영향 long-term drift |
| **Coupling targets** | → Social Layer (자원 경쟁 → 갈등), → Institutional (세금 저항), → Temporal (누적 부채) |
| **Human-independent** | ✓ 기후/질병은 사람 없이 진행 |

### Layer 2 — Institutional Layer (제도)

**무엇을 담는가:** 법 / 권력 / 종교 제도 / 처벌 기대 / 제도 관성.

| 항목 | 설명 |
|---|---|
| **Stored state** | authority_concentration, law_enforcement_strength, religious_doctrine_pressure, punishment_harshness, institutional_inertia |
| **Update process** | 권력자 의사결정 (governed by elite_strategist agents), 제도 응답 지연 |
| **Shock input** | 궁정 쿠데타, 종교 개혁 운동, 외세 점령 |
| **Slow variable** | 제도 정당성 (multi-year, 단일 이벤트로 무너지지 않음) |
| **Decay / accumulation** | 권력 누적 (세대), 법 enforcement 강도 주기적 |
| **Coupling targets** | → Social (처벌 공포 → 군중 위축), → Symbolic (권력 = 신성), → Material (세금 → 자원 추출) |
| **Human-independent** | 부분 (제도 관성은 사람 action 없이도 유지) |

### Layer 3 — Social Layer (사회)

**무엇을 담는가:** 가족 / 파벌 / 공동체 / 평판 / 군중 구조.

| 항목 | 설명 |
|---|---|
| **Stored state** | faction_alliances, community_cohesion, reputation_network, crowd_density_distribution, family_network |
| **Update process** | 가십 전파 (stochastic, 네트워크 topology), 공동체 의식 (집합 행위 → 결속 상승), 군중 모임 (이벤트 촉발) |
| **Shock input** | 공개 사건 (처형, 치유, 스캔들), 집단 이주 |
| **Slow variable** | 가문 간 혈맥 기억 (multi-generation) |
| **Decay / accumulation** | 평판 누적 (정보 레이어에서 유입), 결속 decay (시간에 따라 희미) |
| **Coupling targets** | → Informational (평판 → 소문 확산), → Symbolic (공동체 명예), → Institutional (파벌 → 권력 기반) |
| **Human-independent** | 낮음 (주로 인간 상호작용 기반) |

### Layer 4 — Informational Layer (정보)

**무엇을 담는가:** 소문 / 비밀 / 왜곡 / 신뢰도 / 정보 지연.

| 항목 | 설명 |
|---|---|
| **Stored state** | rumor_intensity_map, secret_containment, info_distortion_rate, source_trustworthiness, info_delay_profile |
| **Update process** | 소문 확산 (epidemic-style), 왜곡 증폭 (반복 전달), 소실 decay |
| **Shock input** | 공개 발언, 예언, 목격 증언, 문서 공개 |
| **Slow variable** | 신뢰 네트워크 구조 (long-term) |
| **Decay / accumulation** | 소문 decay (half-life), 왜곡 누적 (반복 × 네트워크 규모) |
| **Coupling targets** | → Social (소문 → 평판), → Institutional (정보 → 권력 정당성 훼손), → Symbolic (예언 → 신성) |
| **Human-independent** | 낮음 (확산은 사람 경유) |

### Layer 5 — Symbolic Layer (상징)

**무엇을 담는가:** 명예 / 수치 / 신성 / 정체성 / 규범 / 금기.

| 항목 | 설명 |
|---|---|
| **Stored state** | honor_codes, shame_taboos, sacred_calendar_phase, identity_markers, norm_pressure, taboo_sanctity |
| **Update process** | 의식/의례 (ritual) 순환, 금기 위반 → 수치 pressure 상승, 신성 이벤트 → sacred_salience 상승 |
| **Shock input** | 성전 모독, 신성 기적, 공개 수치, 정체성 붕괴 사건 |
| **Slow variable** | 금기 구조 (세대), 명예 코드 (long-term) |
| **Decay / accumulation** | 수치 잔향 (multi-tick), 의식 효과 waning |
| **Coupling targets** | → Institutional (종교 권위), → Social (명예 ↔ 평판), → Temporal (의식 주기) |
| **Human-independent** | 중간 (의식 주기는 calendar 따라 자동) |

### Layer 6 — Temporal-Dynamic Layer (시간)

**무엇을 담는가:** 누적 / decay / seasonal rhythm / event residue / tipping point / path dependence.

| 항목 | 설명 |
|---|---|
| **Stored state** | event_residue_stack, seasonal_phase, path_dependence_markers, tipping_point_thresholds, regime_state |
| **Update process** | 매 tick 모든 layer의 slow variable 누적 → tipping check, seasonal phase 진행 |
| **Shock input** | 여러 layer의 동시 shock (cascading) |
| **Slow variable** | 자기 자신 (메타 레이어) |
| **Decay / accumulation** | 모든 다른 layer의 decay 계산 host |
| **Coupling targets** | **모든 layer** — meta 레이어로 작동 |
| **Human-independent** | ✓ (시간은 사람 없이도 진행) |

---

## 2. Layer 간 Coupling 요약 표

| Source → Target | Coupling | 방향 |
|---|---|---|
| Material → Social | 자원 부족 → 결속 저하 / 갈등 | 하향 음 |
| Material → Institutional | 자원 잉여 → 세금 가능, 부족 → 저항 | 양방향 |
| Institutional → Social | 처벌 공포 → 군중 위축 | 억제 |
| Institutional → Symbolic | 권력 의식 → 신성 주입 | 정당화 |
| Social → Informational | 결속 → 정보 신뢰 | 증폭 |
| Social → Symbolic | 평판 ↔ 명예 | 쌍방 |
| Informational → Social | 소문 → 평판 변화 | 단방향 |
| Informational → Institutional | 공개 진실 → 권위 훼손 | 억제 |
| Informational → Symbolic | 예언 → 신성 상승 | 증폭 |
| Symbolic → Institutional | 신성 → 권력 정당성 | 쌍방 |
| Symbolic → Social | 금기 위반 → 공동체 퇴출 | 제재 |
| Temporal → All | 누적/decay 관리 | 메타 |

**최소 12개 coupling 정의됨.** (Step J에서 20개로 확장.)

---

## 3. Non-human dynamics 체크

Lee §13 완료 기준: *"각 레이어가 사람 없이도 일정 부분 world state를 바꿀 수 있다"*.

| Layer | Non-human update 예시 |
|---|---|
| Material | 기후 순환, 질병 전파, 자원 자연 감소 |
| Institutional | 제도 관성 (정책 비활성 유지), 법 자동 집행 타이머 |
| Social | (약함 — 사람 기반 주로) 군중 밀도 감쇄 |
| Informational | 소문 자연 decay (전달 없어도 약해짐) |
| Symbolic | Sacred calendar 진행 (축제 자동 도래) |
| Temporal | 시간 진행 자체 |

**6/6 layer가 non-human update 최소 1개 보유.** 완료 기준 충족.

---

## 4. 각 Layer의 JSON 스키마 초안

```json
{
  "layer_id": "material",
  "state": {
    "food_availability": {"type": "scalar", "range": [0, 10], "init": 6.0},
    "transport_feasibility": {"type": "scalar", "range": [0, 1], "init": 0.7},
    "climate_harshness": {"type": "scalar", "range": [0, 1], "init": 0.3},
    "disease_prevalence": {"type": "scalar", "range": [0, 1], "init": 0.1}
  },
  "process": [
    {"name": "production", "fn": "harvest_function",
     "inputs": ["climate", "population_size"], "outputs": ["food_availability"],
     "triggered_by": "seasonal_tick"},
    {"name": "consumption", "fn": "consumption_function",
     "inputs": ["population_size"], "outputs": ["food_availability"],
     "triggered_by": "every_tick"}
  ],
  "shock_inputs": [
    "famine", "storm", "epidemic_outbreak"
  ],
  "slow_variables": [
    "tenant_debt_accumulation"
  ],
  "decay": {
    "climate_harshness_drift": {"half_life_ticks": 90}
  },
  "couplings": [
    {"target_layer": "social",
     "rule": "food_availability < 3 → community_cohesion decreases 0.02/tick"},
    {"target_layer": "institutional",
     "rule": "food_availability > 8 → tax_yield increases 0.01/tick"}
  ],
  "human_independent_processes": ["weather_cycle", "disease_transmission"]
}
```

---

## 5. 기존 Spike 1-5 world와의 통합 (Rule #6 준수)

| 기존 layer | 재정의 mapping |
|---|---|
| calendar | **Temporal Layer** (seasonal phase / sacred calendar) + Symbolic Layer (의식 주기) |
| crowd | **Social Layer** (군중 밀도 / 공동체 역학) |
| economy | **Material Layer** (자원/소비/생산) |
| politics | **Institutional Layer** (권력 / 법) |
| factions | **Social Layer** (파벌) + Institutional (권력 기반) |
| rumours | **Informational Layer** |

기존 6 layer가 6 재정의 layer에 대응하지만, mapping이 1:1 아님 (일부는 2개 layer로 분해).

**기존 1003+ tests green 유지 필수.** 통합은 점진적으로:
1. 기존 world/ 모듈 유지
2. `world/` 에 process/shock/slow_variable 필드 추가 (기존 구조 깨지 않음)
3. 신규 layer는 `world/reframed/` 하위 신설 → 마이그레이션 완료 후 교체

---

## 6. 완료 기준 점검 (Lee §13)

| 완료 기준 | 상태 |
|---|---|
| 각 레이어가 process 소유 (단순 저장소 아님) | ✓ 6/6 |
| 각 레이어가 human-independent update 일부 가능 | ✓ 6/6 |
| 각 레이어가 2개 이상 타 레이어와 coupling | ✓ 6/6 |

**Step I 완료.**

---

## 7. 후속 작업 (Step J 연계)

이 reframe은 layer 내부 구조 정의. Step J에서 coupling rules 20+ 명시적 정의.

---

**End of Step I.**
