# Spike 2 실행 지시 — 리뷰어 조건 해결 + Person Engine 연결

---

## 📋 복사용 프롬프트

```
WORLD_DESIGN.md, WORLD_DESIGN_v1.1_amendments.md, WORLD_SPIKE_1A.md,
SPIKE_1_REVIEW.md를 읽어라.

오늘 세션은 2단계로 진행한다.
Phase A: 외부 리뷰어 조건 3개 해결 (Spike 2 진입 전 필수)
Phase B: Spike 2 — Person Engine을 World Engine에 연결

## 절대 규칙
1. engine/의 public interface를 깨는 수정 금지
2. content/ 기존 파일 수정 금지
3. 기존 1003+ 테스트 보존
4. world/ 기존 Spike 1 테스트 62개 보존

---

## Phase A: 리뷰어 조건 해결 (Spike 2 진입 전)

외부 리뷰어(ChatGPT)가 Spike 2 진행 조건으로 제시한 5개 중
지금 해결할 3개:

### A-1. Sync aggregation rule 명확화

WorldConfig.effect_channels에 선언된 각 채널에 대해
aggregation 전략을 명시하고, SyncLayer.drain_aggregated()가
이를 실제로 적용하도록 구현한다.

구현:
- effect_channels의 각 채널에 aggregation_mode가 이미 있음
  (sum/mean/max/threshold)
- drain_aggregated()가 mode에 따라 실제 집계하도록 구현
- 테스트: 가짜 WorldEffect 10개를 주입하고 각 mode별로
  올바르게 집계되는지 검증

### A-2. overflow_pressure 추가

CrowdLayer에 overflow_pressure 변수 추가.
crowd_density가 ceiling에 도달했을 때, ceiling 초과분을
별도 변수로 추적한다.

구현:
- CrowdState에 overflow_pressure: float 추가
- crowd_density 갱신 시:
  raw = (계산된 밀도, clamp 전)
  crowd_density = clamp(raw, baseline, ceiling)
  overflow_pressure = max(0.0, raw - ceiling)
- overflow_pressure는 Spike 2에서 agent의 percept에 포함될 수 있음
  (지금은 저장만)
- 테스트: 유월절 peak에서 overflow_pressure > 0 확인
- 테스트: 평시에 overflow_pressure == 0 확인

### A-3. same-tick feedback 금지 룰

ABSOLUTE RULES에 추가:
"같은 world tick 안에서 Layer A → Layer B → Layer A 순환 금지.
 순환 의존이 필요한 경우 반드시 1-tick delay를 삽입한다."

구현:
- WORLD_DESIGN.md 또는 별도 문서에 이 룰 명문화
- WorldTick.tick()에 주석으로 이 원칙 기록
- 현재 tick order (calendar → crowd → economy → politics)가
  이 룰을 만족하는지 자동 검증하는 테스트 추가
  (각 Layer의 입력이 "이미 업데이트된 Layer" 또는 "이전 tick의 Layer"만
   참조하는지 확인)

Phase A 완료 조건:
- A-1, A-2, A-3 각각 테스트 통과
- 기존 62 world tests + 기존 1003+ engine tests 여전히 green
- Phase A 완료 후 Phase B 진행

---

## Phase B: Spike 2 — Person Engine을 World Engine에 연결

### 목표
"기존 베드로 4-agent 시뮬레이션이 세계 안에서 돌아간다."

### 핵심 구조

```
WorldTick (1일)
  ├── Layer 1-5 업데이트 (기존 Spike 1 그대로)
  ├── Sync Layer: world → percept 변환
  ├── Person Engine: 12 substep (각 2시간)
  │   ├── substep 1: agent 상태 업데이트 (기존 engine 규칙)
  │   ├── substep 2: ...
  │   └── substep 12: ...
  ├── Sync Layer: agent 행동 집계 → WorldEffect
  └── WorldEffect를 다음 tick의 world에 반영
```

### 구현 순서

#### B-1. world → agent 변환 (하향 인과)

SyncLayer.make_percept()는 이미 skeleton이 있다.
이것을 기존 engine의 EnvironmentState에 매핑한다.

```python
def world_to_environment(self, world_state: WorldState) -> EnvironmentState:
    percept = self.make_percept(world_state)
    return EnvironmentState(
        surveillance=percept.perceived_authority,
        crowd_pressure=percept.crowd_density_norm,
        time_pressure=percept.days_to_passover_norm,
        # 기존 engine이 이해하는 필드로 매핑
    )
```

engine/의 EnvironmentState에 필드가 부족하면,
person-agnostic한 generic 필드를 추가하는 것은 허용.
(ABSOLUTE RULE #6 완화 조항: public interface를 깨지 않는 확장은 허용)

#### B-2. agent → world 변환 (상향 인과)

12 substep 동안 agent가 수행한 action들을 WorldEffect로 변환.

```python
def actions_to_effects(self, agent_actions: List[AgentAction]) -> List[WorldEffect]:
    effects = []
    for action in agent_actions:
        if action.visible_signal:  # 공개적 행동만 세계에 영향
            effects.append(WorldEffect(
                channel_id="publicity_shock",
                value=action.intensity or 1.0,
            ))
    return effects
```

action 이름별 switch문을 만들지 않는다.
대신 action의 속성(visible_signal, intensity 등)을 기반으로
generic하게 WorldEffect를 생성한다.

#### B-3. 통합 실행기

world/simulation/integrated_runner.py를 작성한다.

```python
class IntegratedWorldRunner:
    """세계 + 인물을 함께 실행"""
    
    def run(self, world_config, agent_configs, n_days=90, seed=0):
        # 1. 세계 초기화
        # 2. agent 초기화 (기존 engine의 load_agent_state 등 사용)
        # 3. 매일:
        #    a. world layers 업데이트
        #    b. world → EnvironmentState 변환
        #    c. 12 substep: engine의 규칙으로 agent 업데이트
        #    d. agent actions → WorldEffect 집계
        #    e. WorldEffect → 다음 tick의 world에 반영
        # 4. 결과 반환
```

#### B-4. 최소 통합 테스트

1. "세계 안의 베드로": Peter standalone을
   IntegratedWorldRunner로 실행했을 때 에러 없이 90일 완주하는가?

2. "세계의 영향": 세계 모드의 Peter fear가
   전기 모드(기존)와 다른가? (세계의 맥락이 영향을 주므로 달라야 정상)

3. "endogenous arrest 유지": 세계 모드에서도
   arrest가 자발 발생하는가?

4. "상향 인과 존재": agent의 행동이
   다음 날 world state에 반영되는가?
   (publicity_shock > 0인 날이 존재하는가?)

5. "제거 테스트": Judas를 제거하고 세계 모드로 실행했을 때
   arrest 패턴이 달라지는가?

#### B-5. 데모 스크립트

scripts/demo_world_integrated.py를 작성한다.

출력 형식:
```
Witness World — Jerusalem AD 30 (Integrated, seed=0)
Agents: peter, judas, caiaphas, crowd

Day  1: Nisan  1  crowd=2.1  price=1.0  alert=2.0  pilate=caesarea
  [peter] fear=1.2 hope=6.0 actions: pray, follow_closely
  [judas] disill=2.0 actions: discuss
  
Day 13: Nisan 14 [PASSOVER] crowd=10.0 price=3.5 alert=8.7 pilate=jerusalem
  [peter] fear=5.8 hope=3.2 actions: withdraw_in_fear
  [judas] disill=7.3 actions: inform_authorities  ← 상향 인과
  → WorldEffect: publicity_shock=0.0, authority_threat=1.0

Day 14: Nisan 15  crowd=10.0 price=3.8 alert=9.2 pilate=jerusalem
                                              ↑ 어제의 authority_threat 반영
  ...
```

세계의 숫자와 agent의 행동이 같은 화면에 보여야 한다.
"세계가 agent에 영향을 주고, agent가 세계에 영향을 주는" 양방향 인과가
눈에 보여야 한다.

### Spike 2 성공 기준

1. IntegratedWorldRunner가 에러 없이 90일 완주
2. 세계 모드 Peter fear가 전기 모드와 유의하게 다름
3. endogenous arrest가 세계 모드에서도 발생
4. agent → world 상향 인과가 최소 1개 관측
5. Judas 제거 시 세계 모드 결과가 달라짐
6. 기존 1003+ engine tests 여전히 green
7. 기존 62+ world tests 여전히 green

### 하지 않을 것
- 예수 Agent (Spike 3 이후)
- Tier 2/3 Agent 분류 (나중에)
- 종파 Layer (Spike 3)
- 변수 조정 실험 (Spike 4)
- percept interpolation (조건 5, 지금은 1일 1회 업데이트로 시작.
  문제가 드러나면 그때 해결)
- Jesus dominance 제어 (조건 4, 예수가 아직 없으므로 해당 없음)

## 자율 진행 규칙
- Phase A 완료 → Phase B 자동 진행
- 각 B-단계 완료마다 한 줄 로그
- 에러 시 스스로 디버깅
- engine/ 수정이 필요하면 person-agnostic 확장만 (기존 API 시그니처 유지)
- 완료 후 최종 보고:
  - 생성/수정된 파일 목록
  - Phase A 3개 조건 통과 여부
  - Spike 2 성공 기준 7개 통과 여부
  - 세계 모드 vs 전기 모드 Peter fear 비교 수치
  - 예상과 다른 결과 있으면 보고

시작해라.
```
