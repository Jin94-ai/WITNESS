# Persona Profile Schema (Step E)

**작성:** 2026-04-23
**목적:** 인물 차이를 "새 변수/새 규칙"이 아니라 "공통 엔진 위의 파라미터 세트"로 표현.

---

## 0. 핵심 원칙

- 인물 = Shared Engine (generic) + PersonaProfile (scenario-specific parameters)
- 새 시나리오 추가 = profile parameters 초기화 + scenario binding. 엔진 코드 수정 X.
- Profile은 4개 축으로 구성: **pressure_sensitivity / motif_tendency / recovery_bias / relation_bias**
- 각 축 값은 [0, 2] 스칼라 (1.0 = 기본 human, < 1 = 감쇄, > 1 = 증폭).

---

## 1. 전체 Schema

```python
@dataclass
class PersonaProfile:
    name: str                   # "peter_passion", "judas_passion", ...
    description: str
    
    # (E-1) Pressure sensitivity — 각 pressure가 이 사람에게 얼마나 크게 작용하는가
    pressure_sensitivity: PressureSensitivity
    
    # (E-2) Motif tendency — 같은 activation 조건에서 어느 motif가 쉽게 발화되는가
    motif_tendency: MotifTendency
    
    # (E-3) Recovery / decay bias — 감정 회복 속도
    recovery_bias: RecoveryBias
    
    # (E-4) Relation bias — 어느 target에 주로 반응하는가
    relation_bias: RelationBias

    # (E-5) Scene interpretation (optional, content binding 에서 주입)
    scene_family_overrides: dict[str, list[str]] | None = None

    # (E-6) Action family priors within each motif
    # {motif_id: {action_id: prior_weight}}
    motif_action_priors: dict[str, dict[str, float]]
```

---

## 2. 각 축 필드

### E-1. PressureSensitivity (6 파라미터)

모든 기본값 1.0. 각 값 [0, 2].

```python
@dataclass
class PressureSensitivity:
    social_threat: float = 1.0        # 공적 고발에 얼마나 반응하는가
    shame_exposure: float = 1.0       # 수치 노출에 얼마나 반응
    loyalty_pull: float = 1.0         # 결속 대상 수난에 얼마나 반응
    uncertainty: float = 1.0
    urgency: float = 1.0
    isolation_pressure: float = 1.0
    sacred_salience: float = 1.0
```

### E-2. MotifTendency (8 파라미터, motif 개수와 대응)

```python
@dataclass
class MotifTendency:
    conceal: float = 1.0
    confess: float = 1.0
    withdraw: float = 1.0
    remain_present: float = 1.0
    confront: float = 1.0
    grieve: float = 1.0
    seek_repair: float = 1.0
    observe_wait: float = 1.0
```

### E-3. RecoveryBias (5 파라미터)

`engine/person/recovery_profile.py` 의 half-life를 모듈레이팅. 기본 1.0.

```python
@dataclass
class RecoveryBias:
    fear_recovery_rate: float = 1.0        # >1 = 빠른 회복
    guilt_decay_rate: float = 1.0
    grief_tail_strength: float = 1.0       # >1 = 더 긴 long tail
    confusion_decay_rate: float = 1.0
    trust_restoration_bias: float = 1.0    # trust 회복 속도
```

### E-4. RelationBias (4 파라미터)

```python
@dataclass
class RelationBias:
    primary_focus_attachment_strength: float = 1.0  # love/loyalty/trust 기본값 스케일
    peer_dependence: float = 1.0                    # peer_group 반응 스케일
    authority_reactivity: float = 1.0               # authority_group 반응
    public_exposure_sensitivity: float = 1.0        # public_group 기반 shame/fear
```

### E-5. Scene family overrides (optional)

scenario content의 scene_semantics.json에서 주입. 없으면 rubric DEFAULT 사용.

### E-6. Motif → action priors

동일 motif 안에서도 인물마다 주된 action이 다르다:

```python
# Peter: conceal 시 deny 우세
peter_conceal_prior = {
    "deny": 0.45,
    "stay_hiding": 0.20,
    "follow_at_distance": 0.20,
    "withdraw_in_fear": 0.15,
}

# Judas: conceal 시 withdraw 우세 (공개 deny 경향 낮음)
judas_conceal_prior = {
    "deny": 0.10,
    "stay_hiding": 0.40,
    "follow_at_distance": 0.30,
    "withdraw_in_fear": 0.20,
}
```

---

## 3. Peter profile 초안

```python
PETER_PROFILE = PersonaProfile(
    name="peter_passion",
    description="Peter, immediately loyal and impulsive disciple. High sacred_salience reactivity, strong primary_focus attachment.",
    
    pressure_sensitivity=PressureSensitivity(
        social_threat=1.2,       # accusation에 크게 반응 (canonical denial)
        shame_exposure=1.1,
        loyalty_pull=1.3,        # primary_focus suffering에 민감
        uncertainty=1.0,
        urgency=1.1,
        isolation_pressure=0.9,  # 사회적 동물로 isolation 자체 상대적 덜
        sacred_salience=1.4,     # 기적/성만찬에 강한 반응
    ),
    
    motif_tendency=MotifTendency(
        conceal=1.2,            # deny canonical
        confess=1.1,            # 최종 confess
        withdraw=1.0,
        remain_present=1.0,
        confront=1.3,           # 칼 빼는 임펄시브
        grieve=1.2,             # 통곡
        seek_repair=1.4,        # 매우 강함 (run_to_tomb, 복귀)
        observe_wait=0.8,       # 인내심 낮음
    ),
    
    recovery_bias=RecoveryBias(
        fear_recovery_rate=1.1,
        guilt_decay_rate=0.8,    # guilt 오래 지속 (restoration 필요)
        grief_tail_strength=1.0,
        confusion_decay_rate=0.9,
        trust_restoration_bias=1.2,   # 재결속 강함
    ),
    
    relation_bias=RelationBias(
        primary_focus_attachment_strength=1.4,
        peer_dependence=1.0,
        authority_reactivity=0.9,
        public_exposure_sensitivity=1.1,
    ),
    
    motif_action_priors={
        "conceal": {
            "deny": 0.45, "stay_hiding": 0.20,
            "follow_at_distance": 0.20, "withdraw_in_fear": 0.15,
        },
        "confess": {
            "confess": 0.50, "weep": 0.20, "assert_loyalty": 0.30,
        },
        "withdraw": {
            "follow_at_distance": 0.40, "stay_hiding": 0.30,
            "withdraw_in_fear": 0.20, "fall_asleep": 0.10,
        },
        "remain_present": {
            "follow_closely": 0.50, "discuss_with_disciples": 0.30,
            "stay_awake": 0.20,
        },
        "confront": {
            "draw_sword": 0.50, "assert_loyalty": 0.30, "flee": 0.20,
        },
        "grieve": {
            "weep": 0.60, "withdraw_in_fear": 0.20, "pray": 0.20,
        },
        "seek_repair": {
            "confess": 0.30, "assert_loyalty": 0.25,
            "follow_closely": 0.25, "run_to_tomb": 0.20,
        },
        "observe_wait": {
            "stay_awake": 0.40, "discuss_with_disciples": 0.40,
            "watch_quietly": 0.20,
        },
    },
)
```

---

## 4. Judas profile 초안

```python
JUDAS_PROFILE = PersonaProfile(
    name="judas_passion",
    description="Judas, calculating then remorseful. Lower primary_focus attachment (already eroded pre-betrayal), no repair path.",

    pressure_sensitivity=PressureSensitivity(
        social_threat=0.8,       # 공개 현장 회피, 은밀 선호
        shame_exposure=1.0,
        loyalty_pull=0.7,        # loyalty 이미 저하
        uncertainty=1.0,
        urgency=1.2,             # 계획 기한에 민감
        isolation_pressure=1.2,  # 이미 심리적으로 고립
        sacred_salience=0.8,     # sacred 반응 감쇄
    ),
    
    motif_tendency=MotifTendency(
        conceal=1.3,            # 은밀 움직임 기본
        confess=0.7,            # 공개 confess 극히 어려움
        withdraw=1.2,           # flee 선호
        remain_present=0.8,
        confront=0.6,           # 정면 대응 아님
        grieve=1.0,
        seek_repair=0.4,        # **결정적** — repair 경로 거의 없음
        observe_wait=1.3,       # 계획 집단에 대기 많음
    ),
    
    recovery_bias=RecoveryBias(
        fear_recovery_rate=0.9,
        guilt_decay_rate=0.5,    # **매우 낮음** — guilt가 despair로 가는 원인
        grief_tail_strength=1.3,
        confusion_decay_rate=1.0,
        trust_restoration_bias=0.5,  # trust 회복 거의 불가
    ),
    
    relation_bias=RelationBias(
        primary_focus_attachment_strength=0.7,  # 이미 이탈 시작
        peer_dependence=0.6,
        authority_reactivity=1.2,  # 대제사장에게 접근
        public_exposure_sensitivity=1.2,
    ),
    
    motif_action_priors={
        "conceal": {
            "deny": 0.10, "stay_hiding": 0.40,
            "follow_at_distance": 0.30, "withdraw_in_fear": 0.20,
        },
        "confess": {
            "return_token": 0.60, "confess": 0.20, "weep": 0.20,
        },
        "withdraw": {
            "flee": 0.40, "stay_hiding": 0.30,
            "follow_at_distance": 0.20, "fall_asleep": 0.10,
        },
        "remain_present": {
            "discuss_with_disciples": 0.40, "follow_closely": 0.30,
            "stay_awake": 0.30,
        },
        "confront": {
            "flee": 0.60, "draw_sword": 0.20, "assert_loyalty": 0.20,
        },
        "grieve": {
            "weep": 0.40, "withdraw_in_fear": 0.50, "pray": 0.10,
        },
        "seek_repair": {
            # Judas 에게 seek_repair 활성도 자체 낮음; 활성시에도 return 은밀
            "return_token": 0.50, "confess": 0.20, "flee": 0.30,
        },
        "observe_wait": {
            "stay_awake": 0.30, "discuss_with_disciples": 0.50,
            "watch_quietly": 0.20,
        },
    },
)
```

---

## 5. Profile 사용 방식 (PersonV3Loop 개선)

```python
loop = PersonV3Loop(
    scenario_path=Path("content/peter/v3"),   # 한 디렉토리로 통합
    persona_profile=PETER_PROFILE,
    seed=0,
)

# _decide_action 내부:
#   1. scene_recognizer(event_in) → scene_category (Step C)
#   2. motif_activator(state, pressures, events, profile) → motif activation dict
#   3. action_selector(motifs, profile.motif_action_priors, availability_gate)
#   4. returns action_id + provenance
```

---

## 6. Profile validation

Profile parameter 가 극단 값일 때 system behavior 합리적이어야.

- 모든 값 0: 응답 없음 (극단적 withdrawal 기대)
- 모든 값 1.0 + baseline profile: 기본 "generic human"
- 모든 값 2.0: 극도로 반응적 (모든 motif 동시 활성)

---

## 7. 구현 체크리스트 (ordered)

- [ ] `engine/persona/profile.py` 신설
  - PersonaProfile dataclass + 4 sub-dataclass
  - DEFAULT_PROFILE (baseline human, 모두 1.0)
- [ ] `engine/persona/motif.py` 신설
  - 8 motif activation 함수
  - activation * profile.motif_tendency[motif] 적용
- [ ] `engine/persona/selector.py` 신설
  - motif → action distribution (profile.motif_action_priors)
  - availability gate 통과 필터
- [ ] `content/peter/v3/profile.json` — Peter profile 파라미터
- [ ] `content/judas/v3/profile.json` — Judas profile 파라미터
- [ ] `PersonV3Loop` 수정: `persona_profile` argument + `_decide_action` 재구성 (Step C)

---

## 8. Profile 확장 시 주의

- 변수 추가 금지 (새 motif 추가도 12개 초과 금지).
- 파라미터 범위 초과 금지 (< 0 or > 2).
- Content 없이 profile 만으로 작동 가능해야 (profile이 motif 영향만 주도록, action 구체 로직은 engine 유지).

---

**End of Step E.**
