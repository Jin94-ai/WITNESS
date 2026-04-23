# WORLD_DESIGN 수정안 — v1.1 방향 전환 메모

> **이 문서는 WORLD_DESIGN.md v1.0에 대한 수정 방향을 정리한 것이다.**
> **Gemini + ChatGPT 리뷰 반영 + Lee의 3가지 새 결정을 포함.**
> **WORLD_DESIGN.md v2.0으로 통합 시 이 문서의 내용을 반영할 것.**

---

## 1. Lee의 새 결정 3가지

### 1.1 예수를 변수로 전환 (ABSOLUTE RULE #3 변경)

**이전**: 예수는 비에이전트. ExternalEvent/CanonicalIntervention으로만 존재.
**변경**: 예수도 다른 인물과 같은 Agent로 구현한다.

**이유**: Gemini가 정확히 지적함 — *"세계의 가장 큰 동력인 예수가 고정 이벤트면, 세계는 예정된 연극 무대에 불과하다."* 세계 시뮬레이션에서 "예수가 없었다면?"을 실험하려면 예수가 제거 가능한 변수여야 한다. 고정 이벤트는 제거 불가.

**구현 방향**:
- 예수를 Agent로 구현하되, **특별한 속성**을 가진 Agent
- 예수의 행동은 behavior_profile로 정의 (다른 agent와 동일 메커니즘)
- 예수의 가르침/기적은 agent의 action으로 구현 → 주변 agent와 세계에 영향
- **정경 말씀은 여전히 개역개정 원문 유지** (ABSOLUTE RULE #2는 유지)
- 예수 Agent 제거 시 세계가 어떻게 달라지는지 실험 가능

**신학적 주의**: 
- 이건 "예수의 신성을 부정하는 것"이 아니라, "시뮬레이션 안에서 예수의 영향력을 측정 가능하게 만드는 것"
- 예수 Agent의 behavior_profile이 *다른 agent와 질적으로 다를 수 있음* (예: 더 높은 influence, 더 넓은 perception)
- 이 결정이 Lee의 신앙과 어떻게 조화하는지는 Lee가 판단할 문제

**ABSOLUTE RULE #3 수정안**:
- 이전: "예수 비에이전트화 — ExternalEvent/CanonicalIntervention으로만 존재"
- 수정: "예수는 Agent로 구현하되, 정경 말씀(개역개정)은 행동 텍스트로 보존. 예수의 내면 상태를 '신성의 시뮬레이션'으로 과대 해석하지 않는다."

### 1.2 Agent 경량화 — 3-Tier Agent 시스템

**문제**: 세계에 수십~수백 명의 agent가 필요한데, 모든 agent를 기존 엔진의 Full Agent(감정 10개 + slow state + domain state + 관계)로 만들면 O(N²) 관계 계산 + 메모리/연산 폭발.

**해법**: 게임/시뮬레이션 업계의 **LOD (Level of Detail)** 기법을 적용. Agent를 3단계로 분류:

```
┌─────────────────────────────────────────────┐
│  Tier 1: Full Agent (주요 인물, 3-8명)       │
│  기존 engine의 Agent 그대로                   │
│  감정, slow state, domain, 관계, 행동 선택    │
│  예: 베드로, 유다, 가야바, 예수, 빌라도        │
├─────────────────────────────────────────────┤
│  Tier 2: Light Agent (조연, 10-30명)         │
│  축소된 상태 (감정 3개 + 역할 + 소속)          │
│  단순화된 행동 (3-5개 action만)               │
│  관계는 Tier 1과만 (Tier 2끼리는 없음)         │
│  예: 다른 제자들, 바라바, 니고데모, 로마 장교   │
├─────────────────────────────────────────────┤
│  Tier 3: Statistical Agent (군중, 수백-수천)  │
│  개별 agent가 아니라 통계적 집단               │
│  분포로 표현 (밀도, 분위기, 소속 비율)          │
│  개별 행동 없음, Layer 5(사회)의 일부           │
│  예: 순례자, 예루살렘 시민, 성전 방문객         │
└─────────────────────────────────────────────┘
```

**각 Tier의 구체적 차이**:

| | Tier 1 (Full) | Tier 2 (Light) | Tier 3 (Statistical) |
|---|---|---|---|
| 상태 변수 | 12+ (감정 5, 물리 3, slow 4, domain N) | 5-6 (fear, hope, loyalty, role, faction) | 분포 파라미터만 (mean, variance) |
| 행동 선택 | behavior_profile (10+ actions) | 단순 규칙 (3-5 actions) | 없음 (집단 동역학) |
| 관계 추적 | 모든 Tier 1 + 선택적 Tier 2 | Tier 1과만 | 없음 |
| 메모리 | ~500 bytes/agent | ~100 bytes/agent | ~20 bytes/group |
| 업데이트 비용 | O(1) per tick (무거움) | O(1) per tick (가벼움) | O(1) per group |
| 제거 실험 | 가능 (counterfactual) | 가능 | 그룹 단위만 |

**핵심 이점**:
- Tier 1 × Tier 1 관계: 최대 8×8 = 64 (관리 가능)
- Tier 2 × Tier 1 관계: 최대 30×8 = 240 (관리 가능)
- Tier 2 × Tier 2 관계: **없음** (O(N²) 회피)
- Tier 3: 개별 계산 없음 (통계적 집단)

**Tier 승격/강등**:
- 세계에서 특정 인물이 중요해지면 Tier 3→2→1로 승격 가능
- 예: 바라바가 체포되기 전에는 Tier 3(군중의 일부). 체포 후 Tier 2. 재판 장면에서 Tier 1 후보.
- 이 승격 메커니즘은 Spike 3 이후에 구현. 처음엔 고정.

**참고 문헌/기법**:
- LOD (Level of Detail): 게임 엔진의 표준 기법. 거리/중요도에 따라 오브젝트의 복잡도를 조절
- Hybrid crowd simulation: 개인 agent + 연속체 역학을 결합하여 수만 명을 시뮬레이션
- LOD adjustments에서 agent가 시뮬레이션 초점에서 멀어지면 행동을 단순화하고, 가까운 agent만 상세 시뮬레이션
- Lazy evaluation으로 비핵심 agent의 내부 상태 업데이트를 필요할 때까지 지연
- 통계적 집단 모델: 개별 입자의 행동이 사실상 동질적이면 집계 방정식으로 모델링하는 것이 더 효율적
- 인지적 가시거리: Gemini가 제안한 "주인공 중심 인지 범위 내만 관계 계산"

### 1.3 인물엔진 + 월드엔진 분리

**이전**: engine/(인물) + world/(세계)가 한 프로젝트 안에서 world가 engine을 호출
**변경**: 두 엔진이 명시적으로 분리되어 상호작용

```
┌──────────────────┐     ┌──────────────────┐
│  Person Engine   │◄───►│  World Engine     │
│  (기존 engine/)  │     │  (신규 world/)    │
│                  │     │                  │
│  - Agent 상태    │────►│  - 환경 동역학    │
│  - 감정 규칙     │     │  - 경제 동역학    │
│  - 행동 선택     │     │  - 정치 동역학    │
│  - Hazard/Trigger│◄────│  - 사회 동역학    │
│  - 인과 체인     │     │  - 종파 동역학    │
│                  │     │                  │
│  Tick: 2시간     │     │  Tick: 1일       │
└──────────────────┘     └──────────────────┘
        │                        │
        └───────┬────────────────┘
                │
        ┌───────▼────────┐
        │  Sync Layer    │
        │  (동기화 계층)  │
        │                │
        │  1 world day   │
        │  = 12 person   │
        │    substeps    │
        └────────────────┘
```

**Sync Layer의 역할** (ChatGPT의 "안 1" 채택):
1. World Engine이 1일 단위로 환경/경제/정치/사회를 업데이트
2. 그 결과를 Person Engine이 이해하는 EnvironmentState로 변환
3. Person Engine이 그 하루 안에서 12 substep (각 2시간) 실행
4. 12 substep의 agent 행동을 집계하여 World Engine에 반영
5. 다음 날로 진행

**이 구조의 이점**:
- engine/ 코드를 수정할 필요 없음 (Person Engine은 기존 그대로)
- World Engine을 독립적으로 개발/테스트 가능
- 시간 해상도 충돌 해결 (ChatGPT가 지적한 핵심 문제)
- 나중에 다른 World (arles_1888)를 만들 때 Person Engine 재사용

---

## 2. 리뷰 반영 — 핵심 수정 사항

### 2.1 동역학 규칙 명시 (ChatGPT: "존재론이지 동역학이 아니다")

v1.0에서 각 Layer에 변수 목록만 있고 갱신 규칙이 없었음. 수정:

**모든 Layer 변수에 최소한 다음을 명시해야 함**:
1. 갱신 방정식 또는 규칙 유형
2. 시간 상수 (얼마나 빠르게 변하는가)
3. 관측 가능한 출력

**Layer 2 (경제) 예시**:
```
staple_price(t+1) = clamp(
    staple_price(t) * 0.95                    # 자연 안정화
    + pilgrim_influx(t) * 0.3                 # 순례자 → 수요 증가
    - harvest_yield(t) * 0.2                  # 수확 → 공급 증가
    + noise(0, 0.05)                          # 일상 변동
, min=1.0, max=10.0)

시간 상수: 일 단위, 느린 변화
관측 출력: staple_price (agent에게 경제 압박으로 전달)
```

**Layer 3 (정치) 예시**:
```
roman_alertness(t+1) = clamp(
    roman_alertness(t) * 0.9                  # 자연 감소 (긴장 완화)
    + crowd_density(t) > threshold ? 1.0 : 0  # 임계값 초과 시 급증
    + faction_militancy_max(t) * 0.2          # 무장 세력 활동
    + rumor_intensity(t) * 0.1                # 소문에 의한 경계
, min=0, max=10)

시간 상수: 일 단위, 절기 전후 반응
관측 출력: roman_alertness → agent fear에 영향
```

### 2.2 Layer 간 인과에 제동 장치 (ChatGPT: "지연, 완충, 포화가 없다")

모든 cross-layer 연결에 다음 중 하나 이상 필수:
- **Delay**: 물가 상승 → 불만은 3-5일 지연 후 반응
- **Threshold**: 군중 밀도가 임계값 넘어야 로마 경계 급증
- **Saturation**: 이미 높은 값은 추가 상승 둔화 (clamp 또는 diminishing returns)
- **Competing cause**: 메시아 기대는 불만만으로 안 오르고 "상징적 사건"도 필요

### 2.3 세계 성공 기준 수치화 (ChatGPT: "살아있다가 너무 문학적")

Spike 1 성공 기준:
```
1. 유월절 window에서 crowd_density가 baseline 대비 3배 이상 peak
2. staple_price가 유월절 전후 상승-하강 곡선 보임
3. roman_alertness가 절기 전 평균 대비 +2σ 이상 증가
4. no-agent world 100 seeds에서 trivial flatline 비율 < 10%
5. 90일 실행 후 세계 상태가 초기와 유의하게 다름 (KL divergence > threshold)
```

### 2.4 Layer 4/5 경계 재정의 (ChatGPT)

```
Layer 4 = Organized Groups (조직된 집단)
  - membership, resources, leadership, doctrine, coordination
  - "행위자 집합"

Layer 5 = Population Fields (인구 수준 신호)  
  - rumor prevalence, crowd density, public mood, expectation climate
  - "분포적 사회장"
```

이 구분으로 자기증폭 루프 방지. Layer 4의 faction이 Layer 5의 mood를 올리고, mood가 다시 faction을 올리는 루프에 반드시 delay + threshold 삽입.

### 2.5 world↔agent 인터페이스 추상화 (ChatGPT)

**하향 (세계→개인)**: global state가 아니라 **local percept**
```python
class AgentPercept:
    """agent가 인지하는 세계의 부분적 정보"""
    local_crowd_density: float    # 이 agent 주변의 군중
    heard_rumors: List[str]       # 최근 들은 소문
    perceived_authority: float    # 느끼는 권위 압박
    visible_factions: List[str]   # 인지하는 주변 세력
    economic_stress: float        # 느끼는 경제 압박
```

**상향 (개인→세계)**: action 이름이 아니라 **effect primitive**
```python
class WorldEffect:
    """agent 행동이 세계에 미치는 표준화된 영향"""
    publicity_shock: float = 0.0      # 공개적 행동의 파급
    faction_delta: Dict[str, float]   # 종파 영향력 변화
    authority_threat: float = 0.0     # 권위에 대한 위협
    rumor_seed: Optional[str] = None  # 새 소문 생성
```

이러면 action 이름에 따른 switch문이 아니라, 모든 action이 표준화된 effect를 세계에 전달.

### 2.6 engine/ 수정 원칙 완화 (ChatGPT)

**이전**: engine/ 수정 절대 금지
**수정**: engine/의 public interface를 깨는 수정은 금지. 단, person-agnostic한 interface 확장은 허용.

**허용되는 변경**:
- EnvironmentState에 generic 필드 추가
- AgentPercept 같은 새 추상 타입 추가
- Action → WorldEffect 변환 인터페이스 추가

**금지되는 변경**:
- 기존 API의 시그니처 변경
- 기존 테스트를 깨는 변경
- 특정 인물 하드코딩

### 2.7 Spike 1 범위 추가 축소 (ChatGPT)

v1.0 Spike 1에서 제거:
- 기후/농업 (Layer 1에서 달력만 남김)
- 성전 수입 (경제는 staple_price 하나만)
- 산헤드린 내부 정치
- 소문 전파 네트워크

v1.1 Spike 1 최소 범위:
```
Layer 1: 달력 + 절기
Layer 2: staple_price + pilgrim_influx (2개 변수만)
Layer 3: roman_alertness + 빌라도 location (2개 변수만)
Layer 5: crowd_density (1개 변수만)
Sync Layer: 1 world day = 12 person substeps
Demo: 90일 no-agent 실행 → 측정 → 성공 기준 검증
```

---

## 3. 관측 지표 (ChatGPT: "지금부터 정의해야")

세계가 완성된 후 변수 조정 실험에서 비교할 지표들:

```
world_metrics:
  crowd_density_peak: float         # 유월절 군중 최고치
  staple_price_range: [min, max]    # 물가 변동 범위
  roman_alertness_auc: float        # 로마 경계 곡선 아래 면적
  faction_influence_share: Dict     # 종파별 영향력 비율
  rumor_cascade_size: float         # 소문 전파 규모
  arrest_timing: Optional[int]      # 체포 발생 tick (있으면)

agent_metrics:
  fear_trajectory: List[float]      # 시간별 fear
  faith_trajectory: List[float]     # 시간별 faith (Peter)
  action_entropy: float             # 행동 다양성
  relationship_stability: float     # 관계 안정도

comparison_metrics:
  trajectory_divergence: float      # 두 조건 간 경로 차이 (KL)
  event_timing_shift: float         # 사건 타이밍 이동량
  outcome_probability: float        # 특정 결과의 확률 변화
```

---

## 4. ABSOLUTE RULES 수정판

1. engine/ 코드 내 특정 인물 참조 금지 (유지)
2. 정경 말씀 재작성 금지 — 개역개정 원문 보존 (유지)
3. ~~예수 비에이전트화~~ → **예수는 Agent로 구현하되, 정경 말씀은 행동 텍스트로 보존. 예수의 내면을 "신성의 시뮬레이션"으로 과대 해석하지 않는다.** (수정)
4. LLM 런타임 배제 (유지)
5. 용어 과장 금지 (유지)
6. engine/ public interface를 깨는 수정 금지 (완화된 수정)
7. Layer 독립성 유지 (유지)
8. 기존 테스트 보존 (유지)

---

## 5. 다음 단계

이 수정안을 Lee가 승인하면:
1. WORLD_DESIGN.md v2.0으로 통합
2. Claude Code용 Spike 1 프롬프트 재작성 (축소된 범위 + Sync Layer + 3-Tier Agent)
3. Spike 1 실행

---

*WORLD_DESIGN 수정안 v1.1 끝*
