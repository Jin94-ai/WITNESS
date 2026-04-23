# Scenario Template — 새 시나리오 추가 가이드

> ChatGPT 5차 리뷰 지적: "universality 주장은 3번째 시나리오 이전까지 보류."
>
> 본 문서는 3번째 시나리오를 **Peter/VG와 동역학이 다른** 형태로 추가하기 위한 템플릿.

---

## 1. 동역학 타입 분류

현재 시나리오:

| 시나리오 | 타입 | 구조 |
|---------|------|------|
| Peter | **Accumulation → Threshold → Rare-action bottleneck** | Judas disill 누적 → threshold 8 → betray → arrest |
| VG | 동일 타입 (Accumulation → Threshold → Rare-action) | Gauguin frust 누적 → threshold 8 → depart |

**문제**: 두 시나리오가 같은 타입 → "universality"는 하나의 동역학 클래스에 국한됨. 진짜 universality는 **다른 타입 시나리오가 같은 엔진에서 작동**할 때 주장 가능.

## 2. 3번째 시나리오 권장 타입 (ChatGPT 제안)

### Type A — 협상형 (Negotiation/Diplomatic)
- 단일 임계 사건 대신 **점진적 합의 형성** 또는 **결렬**
- 여러 agent가 서로 파라미터 조정
- 예: 역사적 조약 협상, 외교적 중재
- 후보 인물: Cavour의 이탈리아 통일 협상, Talleyrand의 Vienna Congress, 링컨의 노예제 폐지 입법

### Type B — 느린 제도 변화 (Slow Institutional Change)
- 개인 결정 아닌 **집단/제도의 느린 이동**
- Principal agent + role nodes + structural fields 활용
- 예: 경제 체제 이행, 종교개혁, 산업혁명 초기
- 후보 인물: 루터의 95개조 → 교회개혁, Marx의 저술 → 정치 운동

### Type C — 집단 조정 (Collective Coordination)
- 여러 agent의 **동시 조율** 필요
- 한 agent의 의지로 좌우 안 됨
- 예: 전쟁 지휘, 혁명 조직
- 후보 인물: Lenin의 1917 시점 Bolshevik 조직화

**권장**: **Type A (협상형)** — Peter/VG의 linear accumulation과 가장 대비됨.

## 3. Content Pack 구조 체크리스트

새 시나리오 추가 시 `content/[name]/` 하위에 다음 파일 필요:

### 3.1 필수 파일

```
content/
  [main_agent]/                # 주인공 (e.g., "cavour")
    initial_state.json         # 초기 AgentState (emotions, physical, domain_state)
    behavior_profile.json      # voluntary actions + weight formulas
    domain_[name].py           # DomainState 서브클래스 (scenario 특화)
    pom_scorecard.py           # 7±2 개 POM pattern 정의

  [supporting_agent_1]/        # 상호작용 대상 (e.g., "napoleon_iii")
    initial_state.json
    behavior_profile.json
    domain_[name].py

  [scenario_name]/             # 시나리오 공유 (e.g., "italian_unification")
    triggers.json              # 다중 agent trigger 정의
    hazard_events.json         # Poisson 이벤트
    canonical_events.json      # 정경 intervention (optional)
    checkpoints.json           # Hindcasting 검증용
    checkpoints_multi.json     # event-relative 확장
```

### 3.2 Domain state 설계 원칙

```python
# content/[name]/domain_[name].py
from engine.core.state import DomainState
from pydantic import Field

class NegotiationPsychologyState(DomainState):
    """협상가의 심리 상태. Peter/VG와 대비되게 단일 threshold 아닌
    여러 축의 상호 조정을 모델링."""
    type: str = Field(default="negotiation_psychology")

    trust_in_counterpart: float = Field(default=5.0, ge=0.0, le=10.0)
    leverage: float = Field(default=5.0, ge=0.0, le=10.0)  # 협상력
    urgency: float = Field(default=3.0, ge=0.0, le=10.0)   # 시간 압력
    concession_made: float = Field(default=0.0, ge=0.0, le=10.0)
    counterpart_concession: float = Field(default=0.0, ge=0.0, le=10.0)
```

### 3.3 Trigger 설계 — Type A 예시

```json
{
  "trigger_id": "treaty_signed",
  "state_conditions": [
    {"agent_id": "a", "field_path": "domain_state.concession_made", "operator": "gte", "value": 5.0},
    {"agent_id": "b", "field_path": "domain_state.counterpart_concession", "operator": "gte", "value": 5.0},
    {"agent_id": "a", "field_path": "domain_state.trust_in_counterpart", "operator": "gte", "value": 4.0}
  ],
  "event_template_id": "signing_ceremony",
  "deadline_tick": 180
}
```

**Peter/VG 대비**: 단일 driver 변수 누적 → 임계 아닌 **여러 변수의 동시 조정** → 임계.

### 3.4 POM Scorecard — 협상형

```python
def make_negotiation_scorecard() -> list[PatternCriterion]:
    return [
        # 1. 상호 양보 (양측 agent에서 concession 발생)
        PatternCriterion("mutual_concession", ...),
        # 2. 신뢰 증가 (협상 중 trust 상승 구간 존재)
        PatternCriterion("trust_building", ...),
        # 3. 결렬 없음 (deadline 전 무신뢰 붕괴 없음)
        PatternCriterion("no_breakdown", ...),
        # 4. 명시적 양보 행동
        PatternCriterion("concession_action", ...),
        # 5. 조약 체결 (trigger 발동)
        PatternCriterion("treaty_signed", ...),
        # 6. 역사적 데드라인 준수
        PatternCriterion("deadline_met", ...),
        # 7. 상호 이익 (양측 final state에 개선)
        PatternCriterion("mutual_benefit", ...),
    ]
```

## 4. Integration 단계

### 4.1 Domain type 등록
```python
# tests/test_engine/test_[scenario].py 최상단
register_domain_type("negotiation_psychology", NegotiationPsychologyState)
```

### 4.2 기존 검증 프레임워크 재사용
- `pom_filter` — 새 scorecard 적용
- `test_counterfactual` — agent 하나 제거 실험
- `test_bifurcation_detection` — 분기점 탐지
- `test_partial_holdout_generalization` — train/test split
- `test_trace_integration` — trace emitter 작동

**기존 24개 재사용 분석이 그대로 작동해야 함** (ITERATION_CLASSIFICATION.md Tier A).

### 4.3 Universality 검증 가능 조건

3번째 시나리오 추가 후 **다음이 확인되어야 "universality" 주장 유효**:

1. POM bottleneck pattern 존재 (단, rare-action 구조인지 다른 구조인지 확인)
2. Counterfactual 비대칭 존재 (driver agent vs buffer agent)
3. Cross-scenario KS test: 3 scenario 모두 분포 다름
4. 만약 3 scenario 모두 "rare-action bottleneck" 구조면 → universality 주장 가능
5. 만약 3번째가 "continuous coordination" 구조면 → **부분 universality** (accumulation 시나리오에만)

## 5. Playbook — 새 시나리오 추가 단계

1. **Identity 결정**: 인물 + 사건 + 타입 (A/B/C)
2. **사료 수집**: 주요 agent의 행동/상태 추정 (biography)
3. **Initial state 설계**: 베이스라인 파라미터 (±1σ 여유)
4. **Domain state 설계**: 3~5개 특화 field
5. **Behavior profile 설계**: 5~8개 voluntary action (base_weight + 2~3 multipliers)
6. **Trigger 설계**: 2~4개 (driver, buffer, emergency)
7. **Hazard events**: 시대 배경 이벤트 5~10개
8. **Canonical checkpoints**: 역사 사료 기반 체크포인트 3~5개
9. **POM scorecard**: 7±2 패턴
10. **Test 작성**:
    - `test_emergent_[event].py` — 사건 자발 발생 검증
    - `test_counterfactual_[name].py` — driver 제거 실험
    - `test_pom_[name].py` — POM 통과율
11. **Universality 비교**:
    - `test_cross_3scenario.py` — Peter/VG/Newone KS test
    - `test_isomorphism_3scenario.py` — POM bottleneck 구조 비교
12. **Document**: `RESEARCH.md` 갱신, 3rd scenario 발견 추가

## 6. 현재 상태

- 템플릿 작성: ✅
- 시나리오 결정: ❌ (인물 + 타입 필요)
- Content pack scaffold: ❌
- Universality 검증: ❌ (3번째 필요)

**다음 단계 선택**:
- Option 1: 사용자와 함께 인물 결정 후 scaffold 진행
- Option 2: 자체 판단으로 Type A 후보 1명 택해 skeleton content pack 만들기 (예: Cavour + 이탈리아 통일)

---

## 7. v1.2 Phase-linked 아크 (optional, long-life scenarios)

시나리오가 **단일 local window** (Peter 50일, VG 150 tick)이면 §3-§6만 따라도 충분. 하지만 **전 생애** 또는 **여러 시대 구간**을 모델링하려면 v1.2 phase 아키텍처를 사용하라.

### 7.1 언제 phase를 사용할까

- 시나리오가 **자연스러운 단계 구분**을 가지는 경우 (e.g., Peter 공생애 5 phase — 소명 → 갈릴리 → 고백 → 여정 → 수난).
- **시간 해상도가 구간마다 다른** 경우 (dense 2h/tick vs sparse 1일/tick).
- **agent introduction 시점이 다른** 경우 (Judas는 Phase 2부터, Caiaphas는 Phase 5부터).

단일 phase면 phases=None + legacy `SimulationConfig` 그대로 사용 — v1.2 overhead 없음.

### 7.2 Content 파일 구조 (phase-linked)

```
content/[name]/
  initial_state_[entry_phase].json    # phase 시작 시점의 agent state
  phases/
    01_[phase_name]/
      phase_config.json               # tick_scale_hours, max_tick, canonical_events_path
      canonical_events.json           # 이 phase 내부에서만 fire되는 이벤트
      handoff_to_02.json              # 다음 phase 매핑 (optional, 마지막 phase 생략)
    02_[next_phase]/
      phase_config.json
      canonical_events.json
      handoff_to_03.json
    ...
```

### 7.3 Phase/Handoff 로드 (Python)

```python
from engine.io.loader import load_phase, load_handoff_spec

phase_01 = load_phase(
    Path("content/[name]/phases/01_name/phase_config.json"),
    agents_active=["main_agent"],
    handoff_to_next=load_handoff_spec(
        Path("content/[name]/phases/01_name/handoff_to_02.json"),
    ),
)
```

### 7.4 관찰된 Peter 패턴 (참조)

| Peter Phase | tick_scale | max_tick | Agents | 특징 |
|-------------|-----------|----------|--------|------|
| 01 소명 | 2h | 84 | peter | Luke 5 어획 기적, peter solo |
| 02 갈릴리 | 24h | 540 | +judas | sparse 18개월, Judas 합류 |
| 03 고백 | 2h | 150 | peter+judas | 가이사랴 빌립보, 변화산 |
| 04 여정 | 24h | 90 | peter+judas | 3차 수난예고 |
| 05 수난 | 2h | 500 | +caiaphas+crowd | legacy v0.7 재사용 |

**교훈**: dense-sparse 교대 패턴이 사료 밀도와 맞음. handoff는 slow_state carry-all + fast state (emotions, domain_state) 선별 매핑.
