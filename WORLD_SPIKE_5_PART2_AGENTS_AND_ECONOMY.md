# WORLD_SPIKE_5 — Part 2: 주변 인물 Agent + 경제 풍부화

**이 파일은 Part 2입니다. Part 1(Phase 5A + 5C)이 완료된 후에 진행하십시오.**
**Part 1의 완료 기준(1137+ tests green, Jesus agent 작동, 공간 모델 작동)을 먼저 확인하십시오.**

---

## 0. 의도 — 반드시 먼저 읽을 것

이번 Spike의 목표는 **검증 실험이 아닙니다.**
**세계를 두껍게 만드는 것**이 목표입니다.

Part 1에서 세계에 "어디"와 "반응하는 중심 인물"을 심었습니다.
Part 2에서는 세계에 **주변부**와 **하부구조**를 채웁니다.

**한 가지 원칙을 지킵니다:**
나중에 graded control / noisy intervention / metric invariance 실험이
가능하도록 **구조적 여지**를 남겨두며 짓습니다. 지금 실험하지 않지만,
나중에 못 하게 만드는 설계는 피합니다.

### 한 줄 원칙
**"지금 실험하지 말고, 나중에 실험할 수 있는 세계를 지어라."**

---

## 1. ABSOLUTE RULES

Part 1에서 추가된 Rule #10 유지:

**Rule #10. 세계 확장 Spike에서는 counterfactual 실험을 추가하지 않는다.**
기존 3개 intervention (`remove_judas`, `hazard_half`, `lenient_pilate`)은
회귀 테스트로만 유지합니다.

---

## 2. 작업 범위 (Part 2)

이 파일에서 다룰 Phase는 두 개:

- **Phase 5B** — 주변 인물 Agent 확장
- **Phase 5D** — 경제 레이어 풍부화

두 Phase를 묶은 이유: 주변 인물들(특히 Pilate, Caiaphas, 세리)은
경제 레이어와 직접 맞물립니다. Pilate의 정치적 압박은 세금 징수와,
Caiaphas의 성전 권위는 성전 경제와 엮여 있습니다.

**순서 권장:** 5B(인물) → 5D(경제)
인물이 먼저 있어야 경제 레이어가 "누구에게 어떻게 작용하는지"가 명확해집니다.

---

## 3. Phase 5B — 주변 인물 Agent 확장

### 3.1 목표

세계에 **중간층 agent**를 추가해서 "direct vs unrelated" 이분법을 깹니다.

외부 리뷰가 지적한 핵심:
> "지금 control(Pharisees)이 binary. chain proximity가 graded 되어야 함."

Part 2에서는 실험을 추가하지 않지만, **자연스럽게 graded proximity가
형성되는 세계**를 만듭니다.

### 3.2 추가할 agent (우선순위순)

#### 3.2.1 Pontius Pilate (Full Agent) — 최우선

**상태(state):**
- `alertness: float` — 0.0 ~ 1.0, 정치적 경계
- `political_pressure: float` — 0.0 ~ 1.0, 로마/산헤드린 양쪽 압박
- `wife_dream_influence: float` — canonical event, 특정 시점에만 활성화

**행동(actions):**
- `delay_judgment` — 판결 지연, political_pressure 완화 시도
- `consult_rome` — 로마 본국 확인 (rumour로 지연 반영)
- `wash_hands` — 책임 회피 (canonical constraint 존재)
- `order_action` — 직접 명령 (roman_alertness 급상승)

**연결:**
- factions.romans와 직접 연결
- factions.pharisees와 간접 연결 (Caiaphas를 통함)
- factions.zealots와 간접 연결 (세금 징수를 통함)

**중요:**
기존 `lenient_pilate` intervention은 Pilate agent의 `political_pressure`
parameter로 자연스럽게 흡수됩니다. intervention JSON은 그대로 두되,
내부 구현만 agent 기반으로 전환합니다.

#### 3.2.2 Caiaphas (Full Agent)

**상태:**
- `sanhedrin_authority: float` — 산헤드린 내 영향력
- `roman_relationship: float` — 로마와의 관계 (too close = pharisees 반감)
- `theological_anxiety: float` — 예수 운동에 대한 종교적 위기감

**행동:**
- `convene_sanhedrin` — 종교 회의 소집
- `appeal_to_rome` — 로마에 탄원 (pilate.political_pressure 증가)
- `temple_decree` — 성전 관련 결정 (temple_economy 영향)
- `confront_movement` — jesus_movement 직접 견제

**연결:**
- factions.pharisees와 factions.sadducees 양쪽에 연결된 **hub 역할**
- 이 hub 구조가 나중 graded control 실험의 핵심

#### 3.2.3 Barabbas (Light Agent)

**상태:**
- `imprisonment_status: enum` — imprisoned, released, escaped
- `zealot_reputation: float`

**특징:**
- 주로 jesus 재판 시점에 crowd choice 변수로 작동
- canonical constraint로 특정 시점에만 활성화
- factions.zealots와 강한 연결

#### 3.2.4 제자 확장 (Light Agent 3명)

| 제자 | behavior_profile 특징 |
|---|---|
| **John** | 신학적 이해 높음, confusion resistance 높음, witness action 빈도 높음 |
| **James** | 격정적, political_tension에 민감, zealot-leaning 반응 |
| **Thomas** | 의심형, rumour 신뢰도 낮음, evidence-seeking |

각자 다른 behavior_profile, 같은 사건에 다르게 반응합니다.

### 3.3 구조적 요구사항 (★ 핵심)

**Chain proximity를 자연스럽게 다층화할 것.**

지금 Pharisees만 통제군이지만, 세계가 두꺼워지면:

| 계층 | 대상 예시 |
|---|---|
| direct | peter, judas, jesus_movement, john |
| semi-related | caiaphas, pilate, zealots, james |
| indirect | barabbas, samaritan_travelers, thomas |
| unrelated | remote_galilean_villagers, far_diaspora |

이 계층이 **억지로 만들지 말고**, agent 간 자연스러운 연결에서 나오도록 설계합니다.

**검증 방법 (실험 아님, 구조 검증):**
- behavior test로 "caiaphas의 state 변화가 pharisees와 sadducees 양쪽에
  전달되는가"만 확인
- Cohen's d, p-value 계산 금지
- 나중(Spike 7+)에 graded control 실험을 할 때 이 구조가 자동으로 활용됨

### 3.4 테스트 요구사항 (Phase 5B)

counterfactual test 금지. behavior test만:

```
test_pilate_delays_judgment_under_political_pressure
test_pilate_wash_hands_triggered_by_canonical_constraint
test_caiaphas_convenes_sanhedrin_when_theological_anxiety_high
test_caiaphas_hub_role_connects_pharisees_and_sadducees
test_barabbas_activates_at_canonical_trial_scene
test_john_witness_action_more_frequent_than_thomas
test_thomas_rumour_trust_lower_than_james
test_james_reacts_to_political_tension_more_than_john
test_disciples_differ_in_response_to_same_event  # graded proximity 기초
```

### 3.5 산출물 (Phase 5B)

```
world/agents/
  pilate.py             # Full Agent
  caiaphas.py           # Full Agent
  light/
    __init__.py
    barabbas.py
    john.py
    james.py
    thomas.py
content/worlds/jerusalem_ad30/
  agents/
    pilate_profile.json
    caiaphas_profile.json
    light_disciples.json
    barabbas_profile.json
```

기존 `content/interventions/lenient_pilate.json`은 그대로 두되,
내부적으로 pilate agent의 `political_pressure` parameter를 조정하는
방식으로 전환. 기존 회귀 테스트 pass 유지.

---

## 4. Phase 5D — 경제 레이어 풍부화

### 4.1 목표

현재 `staple_price` 하나로 대표되는 경제를 **다층화**합니다.
**세 층이 독립적이지만 연결**되어야 합니다 (ABSOLUTE RULE #7).

### 4.2 세 경제 층

#### 4.2.1 Temple Economy (신규)

**구성 요소:**
- 환전상 수수료 (money_changer_fee)
- 희생제물 가격 (sacrifice_animal_price)
- 성전세 (temple_tax)

**동학:**
- 유월절 시즌 가격 급등 → crowd_frustration 누적
- Jesus의 `temple_cleansing` action이 이 층에 직접 타격 (canonical event)
- Caiaphas의 `temple_decree`가 가격 설정에 영향

**연결:**
- crowd_frustration → jesus_movement.sympathy (indirect path)
- temple_economy shock → pharisees.alertness (저항 위협)

#### 4.2.2 Roman Taxation (신규)

**구성 요소:**
- 세금 징수 주기 (tax_collection_cycle)
- 세리(tax_collector) 활동도
- 징수 강도 (collection_intensity)

**동학:**
- Pilate의 `political_pressure`가 높을수록 세금 징수 압박 증가
- zealot faction의 militancy와 연동 (세금 저항이 zealot 결집 요인)

**연결:**
- taxation_intensity → zealots.militancy (direct)
- taxation_intensity → crowd_frustration (widespread)

#### 4.2.3 일반 물가 (기존 유지)

기존 `staple_price` 그대로. calendar/crowd와 연동된 구현은 이미 완료됨.

### 4.3 구조적 요구사항

**세 층 사이의 indirect path가 반드시 작동해야 합니다:**

```
temple_economy shock
  → crowd_frustration
    → jesus_movement.sympathy  (indirect)

taxation_intensity up
  → zealots.militancy
    → roman_alertness  (indirect via factions)

staple_price spike (유월절)
  → general_discontent
    → rumour spawn rate 증가
```

같은 substep 내 피드백 금지 (ABSOLUTE RULE #9).
모든 전파는 다음 substep에 반영.

### 4.4 테스트 요구사항 (Phase 5D)

counterfactual test 금지. behavior test만:

```
test_temple_economy_passover_price_spike
test_jesus_temple_cleansing_disrupts_money_changer
test_caiaphas_temple_decree_adjusts_sacrifice_price
test_pilate_political_pressure_raises_taxation_intensity
test_taxation_spike_increases_zealot_militancy
test_temple_shock_reaches_jesus_movement_via_crowd_frustration
test_three_economies_independent_but_connected
test_no_same_tick_feedback_in_economy_layer  # Rule #9 회귀 방지
```

### 4.5 산출물 (Phase 5D)

```
world/economy/
  __init__.py           # 기존 파일 수정
  staple_price.py       # 기존 유지
  temple_economy.py     # 신규
  taxation.py           # 신규
  cross_economy.py      # 세 층 간 연결 관리
content/worlds/jerusalem_ad30/
  economy/
    temple_economy_config.json
    taxation_config.json
```

기존 `staple_price` 관련 테스트 전부 green 유지.

---

## 5. 통합 요구사항

### 5.1 기존 시스템과의 호환성

- Part 1 완료 시점의 tests (1137 + 5A/5C 신규 behavior tests) 모두 green 유지
- `world/` Layer DAG 유지 (test_layer_dag.py 통과)
- Spike 4 회귀 테스트 pass 유지 (`remove_judas`, `hazard_half`, `lenient_pilate`)
- `engine/` public interface 건드리지 말 것 (ABSOLUTE RULE #6)

### 5.2 same-tick feedback 금지 (ABSOLUTE RULE #9)

경제 레이어 확장으로 새 피드백 경로가 생깁니다:
- taxation → zealot militancy → roman alertness → taxation (순환 가능)

이 순환은 **다음 substep에 반영**되어야 합니다. 같은 substep 내에서
taxation → zealot → roman → taxation으로 돌아오면 **Rule #9 위반**입니다.

### 5.3 Layer DAG 재검증

Part 2 완료 후 Layer DAG:

```
calendar → crowd → economy → politics → factions → rumours → agents
                    ↑ temple_economy, taxation 모두 economy 레이어 내부
```

test_layer_dag.py가 이 구조를 자동 검증하도록 업데이트.

### 5.4 문서

- `docs/world/WORLD_SPIKE_5_PART2_PROGRESS.md` — 진행 메모
- 각 Phase 완료 시 한 단락 요약
- 수치/실험 결과 포함 금지
- **외부 리뷰 패킷 작성 금지**

### 5.5 금지 목록 (재확인)

- 새로운 intervention JSON 추가 금지
- `demo_spike5_*.py` counterfactual 데모 금지
- 기존 Spike 4 결과 재실행/재분석 금지
- `paper_data/` 업데이트 금지
- 외부 리뷰 패킷 작성 금지
- **`remove_jesus`, `remove_pilate`, `remove_caiaphas` 같은 신규 intervention 절대 금지**

---

## 6. Part 2 완료 기준

다음이 모두 충족되면 Spike 5 전체 완료 (Part 1 + Part 2):

- [ ] Pilate, Caiaphas가 Full Agent로 살아 있습니다
- [ ] Barabbas, John, James, Thomas가 Light Agent로 작동합니다
- [ ] 제자 3명이 같은 사건에 다르게 반응합니다 (behavior test 통과)
- [ ] Caiaphas가 pharisees/sadducees hub 역할을 수행합니다
- [ ] Temple Economy, Roman Taxation이 독립 모듈로 존재합니다
- [ ] 세 경제 층 간 indirect path가 작동합니다
- [ ] Jesus의 `temple_cleansing`이 temple economy에 타격을 줍니다
- [ ] Pilate의 political pressure가 taxation intensity에 연결됩니다
- [ ] 기존 모든 tests + 신규 behavior tests green
- [ ] ruff clean, mypy world/ clean 유지
- [ ] Layer DAG test 통과 (순환 참조 없음, same-tick feedback 없음)
- [ ] Spike 4 회귀 테스트 (3개 intervention) 모두 pass

---

## 7. 진행 중 막혔을 때

Lee가 세션 중에 확인할 수 있도록 다음 상황에서는 **바로 진행하지 말고
상황을 보고하십시오:**

1. ABSOLUTE RULES와 요구사항이 충돌할 때
2. 기존 tests green이 깨지는데 원인이 구조적일 때
3. Caiaphas hub 역할이 Layer DAG 순환을 유발할 때
4. Temple Economy ↔ Taxation 간 피드백이 same-tick으로 돌아올 때
5. `lenient_pilate` intervention 회귀 테스트가 agent 전환 후 깨질 때
6. 제자 3명의 behavior_profile이 기존 peter와 충돌할 때

위 상황들은 **Lee의 설계 판단이 필요한 지점**입니다. 자율 결정 금지.

---

## 8. Spike 5 전체 완료 후 상태

Part 1 + Part 2가 모두 완료되면 Witness v2.0 세계는 다음을 가집니다:

**인물 (Agents):**
- Full: Jesus, Peter, Judas, Pilate, Caiaphas (5)
- Light: John, James, Thomas, Barabbas (4)

**공간:**
- 6개 location, 이동 비용, 정보 비대칭

**경제:**
- 3층 (staple, temple, taxation) 독립적이지만 연결

**인과 구조적 여지 (미래 실험 대비):**
- jesus_movement로 가는 경로 최소 3개 (single-point 회피)
- chain proximity 4단계 자연 형성 (direct → unrelated)
- 경제 레이어 indirect path 3종 작동

**실험 상태:**
- 신규 intervention 0개
- 기존 Spike 4 intervention 3개 회귀 유지
- **실험은 Spike 7+에서 재개**

---

## 9. 한 줄 요약

**Part 2에서는 세계에 "주변부"와 "하부구조"를 채웁니다.
실험하지 말고, 나중에 실험할 수 있도록 graded proximity를 자연 형성시키십시오.**
