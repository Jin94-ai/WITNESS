# WORLD_SPIKE_5 — Part 1: Jesus Agent + 공간 모델

**이 파일은 Part 1입니다. Part 2(Phase 5B + 5D)는 별도 파일에 있습니다.**
**Part 1이 완료되어 1137+ tests green, 세계가 안정적으로 작동한 후에 Part 2로 진행하십시오.**

---

## 0. 의도 — 반드시 먼저 읽을 것

이번 Spike의 목표는 **검증 실험이 아닙니다.**
**세계를 두껍게 만드는 것**이 목표입니다.

Spike 4까지 intervention framework가 완성됐지만,
그 위에서 돌리는 **세계 자체가 얇습니다**. Judas, 6 factions, 3 intervention —
이건 인과 구조를 증명하기엔 충분해도, "살아있는 세계"라고 부르기엔 부족합니다.

Spike 5는 세계를 살아있게 만듭니다. 검증 실험은 세계가 안정적으로
두꺼워진 이후(Spike 7+)에 다시 돌아옵니다.

**단, 한 가지 원칙을 지킵니다:**
나중에 graded control / noisy intervention / metric invariance 실험이
가능하도록 **구조적 여지**를 남겨두며 짓습니다. 지금 실험하지 않지만,
나중에 못 하게 만드는 설계는 피합니다.

### 한 줄 원칙
**"지금 실험하지 말고, 나중에 실험할 수 있는 세계를 지어라."**

---

## 1. ABSOLUTE RULES (기존 9개 유지 + 1개 추가)

기존 9개 규칙은 그대로 유지됩니다. 여기에 한 줄 추가:

**Rule #10. 세계 확장 Spike에서는 counterfactual 실험을 추가하지 않는다.**
기존 3개 intervention (`remove_judas`, `hazard_half`, `lenient_pilate`)은
회귀 테스트로만 유지합니다. Spike 5-6은 오직 세계 두께만 다룹니다.

---

## 2. 작업 범위 (Part 1)

이 파일에서 다룰 Phase는 두 개입니다:

- **Phase 5A** — Jesus Agent 구현
- **Phase 5C** — 공간 모델 도입

두 Phase를 묶은 이유: Jesus agent의 action은 공간 위에서 일어날 때
비로소 의미가 생깁니다. 따로 만들면 나중에 다시 꿰매야 하므로,
같은 Part에서 처리합니다.

**순서 권장:** 5C(공간 모델) → 5A(Jesus Agent)
공간 모델을 먼저 깔아두면 Jesus agent가 처음부터 공간을 전제로 설계됩니다.

---

## 3. Phase 5C — 공간 모델

### 3.1 목표

모든 agent가 같은 "공간"에 떠 있는 지금 구조를 깹니다.
정보 비대칭과 이동 비용이 생겨야 세계가 살아있습니다.

### 3.2 요구사항

#### 3.2.1 Location 개념

주요 장소 최소 6개:

| Location | 핵심 속성 |
|---|---|
| `temple` | crowd_density 높음, surveillance 중간, 경제 활동 중심 |
| `upper_room` | crowd_density 낮음, surveillance 낮음, 사적 공간 |
| `gethsemane` | crowd_density 낮음, surveillance 낮음, 예루살렘 외곽 |
| `praetorium` | crowd_density 중간, surveillance 매우 높음, 로마 관할 |
| `bethany` | crowd_density 낮음, surveillance 낮음, 예루살렘 근교 |
| `galilee_distant` | crowd_density 낮음, surveillance 거의 없음, 먼 거리 |

각 location 속성:
- `crowd_density: float` — 0.0 ~ 1.0
- `surveillance_level: float` — 0.0 ~ 1.0 (로마/산헤드린 감시 강도)
- `economic_activity: float` — 0.0 ~ 1.0

#### 3.2.2 Agent Position

- 각 agent는 매 substep에 하나의 location에 존재
- 이동은 비용/시간 소모: 같은 도시 내 2 substep, 도시 간(galilee_distant) 4 substep
- 이동 중 agent는 `location = "transit"` 상태 (rumour 수신 불가, 발신 가능)

#### 3.2.3 Rumour 전파의 공간화 ← **가장 중요**

**현재 rumour graph 구조를 `abstract network → spatial network`로 전환합니다.**

전파 규칙:
- 같은 location의 agent 사이: 기존 propagation rate의 **1.5×**
- 다른 location의 agent 사이: 기존 rate의 **0.3×** (전달자 agent가 있을 때만)
- transit 상태 agent는 "전달자" 역할 (location A에서 B로 이동하며 rumour 운반)

**왜 중요한가:**
외부 리뷰에서 "rumour가 물리 거리 기반인가 추상 네트워크 기반인가?"라는
질문을 받았습니다. 답을 **spatial**로 확정함으로써 나중 diffusion pattern
분석(scale-free vs localized)이 의미를 가집니다.

#### 3.2.4 정보 비대칭

- agent는 **자기 location의 state만** 정확히 알고, 다른 location은
  rumour/messenger를 통해 간접 인지
- Pilate는 galilee 소식을 늦게 듣습니다 (rumour 전파 지연)
- 베드로는 예수의 gethsemane 기도 내용을 모릅니다 (같은 장소에 없음)

구현 방식:
- agent가 decision을 내릴 때 참조하는 `world_state`는 **자기 location 기준**
- 다른 location 정보는 `rumour_inbox`를 통해서만 접근 가능
- rumour에는 `source_location`, `age_in_substeps` 속성 추가

### 3.3 테스트 요구사항 (Phase 5C)

counterfactual test 금지. behavior test만:

```
test_agent_at_temple_sees_temple_crowd_density
test_agent_at_gethsemane_cannot_see_praetorium_directly
test_rumour_propagates_faster_within_same_location
test_rumour_reaches_distant_location_via_transit_agent
test_agent_movement_takes_expected_substeps
test_pilate_receives_galilee_news_with_delay
```

### 3.4 산출물 (Phase 5C)

```
world/space/
  __init__.py
  location.py          # Location 클래스, 6개 정의
  position.py          # AgentPosition 관리
  movement.py          # 이동 로직 및 비용
  rumour_spatial.py    # rumour 전파 공간화
```

기존 `world/social/rumour.py`는 `rumour_spatial.py`를 import해서 사용하도록
수정. 기존 API 깨지 말 것 (ABSOLUTE RULE #6).

---

## 4. Phase 5A — Jesus Agent

### 4.1 목표

예수를 `canonical_events` 재생기가 아니라 **반응하는 agent**로 구현합니다.

### 4.2 요구사항

#### 4.2.1 behavior_profile 설계

action 종류 최소 5개:

| Action | 트리거 조건 (예시) | 세계 레이어 영향 |
|---|---|---|
| `teach` | 주변 disciple의 understanding < threshold | jesus_movement.influence + rumour seed (low intensity) |
| `heal` | 같은 location에 suffering agent 존재 | rumour seed (high intensity) + crowd_density pull |
| `confront` | pharisees/caiaphas가 같은 location | pharisees.alertness + roman_alertness (indirect) |
| `withdraw` | crowd_density > threshold OR fatigue 누적 | 모든 faction 영향 decay window |
| `bless` | 특정 agent와 1:1 상황 | 해당 agent state 직접 수정 (peter, judas 등) |

각 action은 **확률적 선택**. hard rule 금지. 주변 agent 상태에 따라 가중치 변화.

#### 4.2.2 Factions 레이어 직접 타격 메커니즘

**single-point failure 회피 구조 (★ 핵심):**

jesus.influence가 factions.jesus_movement로 가는 경로를 **반드시 복수화**합니다.

```
직접 경로:   jesus.teach  → jesus_movement.influence
간접 경로 1: jesus.heal   → rumour → jesus_movement.influence
간접 경로 2: disciple.witness (John, James 등) → rumour → jesus_movement.influence
간접 경로 3: crowd.testimony → rumour → jesus_movement.influence
```

**왜 복수화하는가:**
나중에 `remove_jesus` 실험을 했을 때 "jesus 한 명 = 전부" 구조로
붕괴되지 않도록 여지를 남깁니다. 지금 실험하지 않지만 **구조는 미리 심습니다.**
외부 리뷰의 "design-imposed causality" 지적에 대한 선제 대응입니다.

#### 4.2.3 canonical_events와의 관계

- canonical_events는 **제약조건(constraint)**으로만 작동
- 예: "AD 30 유월절 전 예루살렘 입성" → 해당 날짜에 `entered_jerusalem=true` 강제
- 그 외 시간에는 agent가 자유롭게 행동
- 정경 말씀은 ABSOLUTE RULE #2대로 재작성 금지 (개역개정 그대로)

구현 방식:
```python
# world/agents/jesus.py (의사코드)
def decide_action(self, world_state, own_state):
    # 1. Canonical constraint 먼저 체크
    if self._canonical_event_today(world_state.date):
        return self._resolve_canonical(world_state.date)

    # 2. 자유 행동 (확률적)
    candidates = self._compute_action_weights(world_state, own_state)
    return self._sample(candidates)
```

### 4.3 금지사항 (Phase 5A)

- `remove_jesus` intervention 지금 추가 금지 (Spike 7+에서 다룸)
- jesus의 신성에 대한 과대해석 금지 (ABSOLUTE RULE #3)
- jesus behavior가 다른 agent와 **질적으로 다른 특권**을 가지지 말 것
  - influence는 크되 mechanism은 동일해야 함
  - 즉, jesus도 Peter와 같은 BaseAgent 인터페이스를 따라야 함

### 4.4 테스트 요구사항 (Phase 5A)

counterfactual test 금지. behavior test만:

```
test_jesus_teaches_more_when_disciple_understanding_low
test_jesus_withdraws_when_crowd_density_high
test_jesus_heal_at_temple_generates_high_intensity_rumour
test_jesus_confront_pharisees_increases_roman_alertness
test_jesus_influence_reaches_factions_via_multiple_paths  # ← single-point 회피 검증
test_jesus_canonical_event_on_passover_triggers_entry
test_jesus_agent_uses_same_base_interface_as_peter
```

### 4.5 산출물 (Phase 5A)

```
world/agents/
  jesus.py              # Full Agent
  base.py               # BaseAgent 인터페이스 (기존 peter와 공유)
content/worlds/jerusalem_ad30/
  jesus_profile.json    # behavior weights, canonical constraints
```

---

## 5. 통합 요구사항

### 5.1 기존 시스템과의 호환성

- 기존 1137 tests는 **반드시 green 유지** (ABSOLUTE RULE #8)
- `world/` Layer DAG 유지 (ABSOLUTE RULE #7, test_layer_dag.py 통과)
- Spike 4의 `remove_judas`, `hazard_half`, `lenient_pilate` 회귀 테스트 pass 유지
- `engine/` public interface 건드리지 말 것 (ABSOLUTE RULE #6)

### 5.2 same-tick feedback 금지 (ABSOLUTE RULE #9)

공간 모델 도입으로 새로운 피드백 경로가 생길 수 있습니다:
- agent가 이동 → location state 변화 → 같은 substep에 다른 agent의 decision 영향

이건 **금지**입니다. 이동/state 변화는 다음 substep에 반영되어야 합니다.

### 5.3 문서

- `docs/world/WORLD_SPIKE_5_PART1_PROGRESS.md` — 진행 메모
- 각 Phase 완료 시 한 단락 요약
- 수치/실험 결과 포함 금지 (실험 아닙니다)
- **외부 리뷰 패킷 작성 금지** — 이번은 세계 구축 Spike

### 5.4 금지 목록 (재확인)

- 새로운 intervention JSON 추가 금지
- `demo_spike5_*.py` counterfactual 데모 금지
- 기존 Spike 4 결과 재실행/재분석 금지
- `paper_data/` 업데이트 금지
- 외부 리뷰 패킷 작성 금지

---

## 6. Part 1 완료 기준

다음이 모두 충족되면 Part 1 완료. 이후 Part 2로 진행:

- [ ] Jesus agent가 주변 상태에 반응해 행동합니다 (canonical 재생이 아닙니다)
- [ ] Jesus가 다른 agent와 동일한 BaseAgent 인터페이스를 사용합니다
- [ ] jesus → jesus_movement 경로가 복수화되어 있습니다 (최소 3경로)
- [ ] 주요 사건이 "어디서" 일어나는지 의미가 있습니다 (6개 location 작동)
- [ ] Rumour가 같은 장소 agent 사이에서 더 빠르게 퍼집니다
- [ ] Agent가 자기 location 외 정보를 rumour를 통해서만 인지합니다
- [ ] 기존 1137 tests + 신규 behavior tests 모두 green
- [ ] ruff clean, mypy world/ clean 유지
- [ ] Layer DAG test 통과 (순환 참조 없음)

---

## 7. 진행 중 막혔을 때

Lee가 세션 중에 확인할 수 있도록 다음 상황에서는 **바로 진행하지 말고
상황을 보고하십시오:**

1. ABSOLUTE RULES와 요구사항이 충돌할 때
2. 기존 1137 tests 중 green이 깨지는데 원인이 구조적일 때
3. Layer DAG 순환 참조를 피할 수 없는 설계 상황
4. 6개 location으로는 표현 불가능한 핵심 서사가 나타날 때
5. Jesus behavior의 확률 분포가 canonical_events와 충돌할 때

위 상황들은 **Lee의 설계 판단이 필요한 지점**입니다. 자율 결정 금지.

---

## 8. 한 줄 요약

**Part 1에서는 세계에 "어디"와 "반응하는 중심 인물"을 심습니다.
실험하지 말고, 나중에 실험할 수 있도록 구조를 남기십시오.**
