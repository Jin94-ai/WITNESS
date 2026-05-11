# Response Motif Layer 설계 (Step B)

**작성:** 2026-04-23
**목적:** 직접 action boost 대체. scene cue → motif activation → action realization 의 중간 층.

---

## 0. 설계 원칙

1. **8 motif로 시작**. 12개 이상 확장 금지.
2. **각 motif는 generic** — 특정 인물/상황 이름 금지.
3. **motif는 pressure + state 함수** (event 이름 직접 의존 금지, 단 event는 pressure 경유 허용).
4. **각 motif는 action family를 가짐** — 1 motif = 여러 action. Persona profile이 bias 결정.

---

## 1. 8 Motif 정의

### 1.1 `conceal` — 사회적 은폐

- **활성 조건**: `shame_exposure` 높음 + `social_threat` 높음 + (fear ≥ 3.0 또는 accusation_visibility 높음)
- **의미**: 자신의 정체/실수가 사회적 적발될 위험이 있을 때 숨김/부인/회피로 대응
- **연결 actions**: `deny`, `stay_hiding`, `follow_at_distance`, `withdraw_in_fear`
- **canonical vs alt vs noise에서의 역할**: 
  - canonical: Peter의 부인 장면 — 강한 conceal
  - alternative: 약한 conceal (follow_at_distance)
  - noise: conceal activation 있는데 엉뚱한 action (예: jump_into_sea)

### 1.2 `confess` — 자기 노출

- **활성 조건**: `guilt[primary_focus]` 높음 + `hope` 유지 + (forgiveness event recent OR restoration context)
- **의미**: 자기 잘못을 외부에 드러내고 책임을 수용
- **연결 actions**: `confess`, `weep` (공개 통곡), `assert_loyalty` (재선언), `return_token`
- **역할**: canonical restoration 장면, Judas의 후회

### 1.3 `withdraw` — 물리/사회적 철수

- **활성 조건**: `isolation_pressure` 높음 OR (fear 높음 + ally_proximity 낮음)
- **의미**: 상황에서 물리적/사회적으로 떨어짐. 적극 대응도 자백도 아닌 중간 응답.
- **연결 actions**: `follow_at_distance`, `stay_hiding`, `fall_asleep`, `withdraw_in_fear`
- **역할**: canonical 장면의 회피 반응, alternative의 주된 응답

### 1.4 `remain_present` — 현상 유지

- **활성 조건**: 다른 motif 활성도 낮음 AND core relation (love/loyalty) 유지
- **의미**: 극적 변화 없이 지속. 일상적/과정적 응답.
- **연결 actions**: `follow_closely`, `discuss_with_disciples`, `stay_awake`
- **역할**: 평시 기본 상태. pre-passion 기간.

### 1.5 `confront` — 정면 대응

- **활성 조건**: `anger` 높음 + `physical_threat` 있음 + core relation 강함
- **의미**: 위협에 물리/언어적 저항
- **연결 actions**: `draw_sword`, `assert_loyalty`, `flee` (fight-or-flight에서 flight 쪽)
- **역할**: canonical 칼 뽑는 장면, 위협 상황 즉각 반응

### 1.6 `grieve` — 애도

- **활성 조건**: `grief` 높음 OR (guilt 높음 + eye_contact/exposure event recent) OR loss cue 있음
- **의미**: 상실/실패를 처리하기 위한 정서적 표현
- **연결 actions**: `weep`, `withdraw_in_fear` (조용한 retreat), `pray`
- **역할**: canonical 통곡 장면, 정서적 전환점

### 1.7 `seek_repair` — 회복 추구

- **활성 조건**: `guilt` 높음 + `hope` 잔존 + `trust[primary_focus]` 유지 + repair context (forgiveness/restoration event)
- **의미**: 관계/상황 회복을 위한 능동적 움직임
- **연결 actions**: `confess`, `assert_loyalty`, `follow_closely` (복귀), `run_to_tomb` (추격/찾음)
- **역할**: canonical restoration 장면, 재연결 서사

### 1.8 `observe_wait` — 관찰/대기

- **활성 조건**: `uncertainty` 높음 + `urgency` 낮음 + motif 지배성 없음
- **의미**: 상황 판단을 위한 수동 대기. Action 선택 유예.
- **연결 actions**: `watch_quietly`, `stay_awake`, `discuss_with_disciples` (정보 수집)
- **역할**: 정보 공백기 기본. canonical에서 낮은 빈도.

---

## 2. Motif activation 공식 (초안)

각 motif는 [0, 1] activation 반환. 여러 motif 동시 활성 가능.

```python
def activate_motifs(state, pressures, events_recent, profile) -> dict[str, float]:
    conceal = sigmoid(
        0.5 * pressures.shame_exposure / 10
      + 0.4 * pressures.social_threat / 10
      + 0.3 * max(0, state.fear - 3) / 7
      - 1.5
    ) * profile.conceal_tendency

    confess = sigmoid(
        0.5 * guilt_primary / 10
      + 0.3 * state.hope / 10
      + 0.4 * float(has_forgiveness_context)
      - 1.0
    ) * profile.confess_tendency

    withdraw = sigmoid(
        0.4 * pressures.isolation_pressure / 10
      + 0.3 * state.fear / 10
      + 0.2 * (1 - ally_proximity)
      - 1.0
    ) * profile.withdraw_tendency

    remain_present = sigmoid(
        0.5 * (1 - max_pressure_among_others / 10)
      + 0.3 * love_primary / 10
      - 0.2
    ) * profile.remain_tendency

    confront = sigmoid(
        0.5 * state.anger / 10
      + 0.4 * pressures.physical_threat / 10
      + 0.3 * loyalty_max / 10
      - 1.5
    ) * profile.confront_tendency

    grieve = sigmoid(
        0.5 * state.grief / 10
      + 0.3 * guilt_primary / 10
      + 0.4 * float(has_exposure_event_recent)
      - 1.0
    ) * profile.grief_expression_tendency

    seek_repair = sigmoid(
        0.4 * guilt_primary / 10
      + 0.3 * state.hope / 10
      + 0.3 * trust_primary / 10
      + 0.3 * float(has_repair_context)
      - 1.2
    ) * profile.repair_tendency

    observe_wait = sigmoid(
        0.4 * pressures.uncertainty / 10
      - 0.3 * pressures.urgency / 10
      - 0.2  # base penalty so wait 는 defaultish에서만
    ) * 1.0  # no specific profile tendency
```

Sigmoid는 Soft gating. 활성화 합계는 nomalize 하거나 top-k 선택.

---

## 3. Motif → Action selection

각 motif activation 에서 action distribution.

**Step 1**: Activation top-k motifs 선택 (예: top 2).
**Step 2**: 각 motif 의 action family 에서 action을 선택. 이때:
- **Persona profile bias**: 같은 motif 안에서도 Peter는 deny 우세, Judas는 withdraw 우세 (profile 파라미터)
- **Availability gate**: 기존 gate 유지, motif가 선택한 action 중 gate 통과만
- **State modulation**: motif family 안에서 state 상태에 따른 weight

예:
```
motif activation {conceal: 0.75, grieve: 0.20, remain_present: 0.05}
→ primary = conceal
→ conceal action family: [deny, stay_hiding, follow_at_distance, withdraw_in_fear]
→ Peter profile bias (conceal_action_prior): {deny: 0.5, stay_hiding: 0.2, follow_at_distance: 0.2, withdraw_in_fear: 0.1}
→ availability gate 통과: 전부 pass (accusation recent)
→ weighted sample → deny
```

---

## 4. Motif table by scene category (규범적)

자세한 mapping은 `content/scenario/scene_semantics.json` 에서 override 가능.

| Scene cue | Primary motifs (raise) | Suppressed motifs |
|---|---|---|
| accusation / public exposure | conceal, withdraw | remain_present |
| eye_contact / exposure turning | grieve, seek_repair | conceal |
| physical threat / weapon | confront, withdraw | remain_present |
| loss / suffering | grieve, withdraw | remain_present |
| sacred / reverent | remain_present, observe_wait | confront |
| forgiveness / restoration | seek_repair, confess | conceal, withdraw |
| uncertainty / info gap | observe_wait | confront |

이 표는 generic이고 각 scenario content가 override할 수 있다.

---

## 5. Peter vs Judas motif 비교 (Step G 예시)

| Motif | Peter 전형 | Judas 전형 |
|---|---|---|
| conceal | deny (canonical 3회) | withdraw/flee |
| confess | 최종 confess (restoration) | return_token (silver 반환) |
| withdraw | follow_at_distance | flee |
| confront | draw_sword | (none; 전형 없음) |
| grieve | weep (canonical) | remorse → despair |
| seek_repair | assert_loyalty, run_to_tomb | 부재 (Judas에게는 repair 경로 없음) |
| remain_present | follow_closely, discuss | (pre-betrayal discuss only) |
| observe_wait | fall_asleep (Gethsemane) | covert_bargain 전 대기 |

**핵심 차이 (profile 축):**
- Peter: `seek_repair_tendency` 높음. `confront_tendency` 중간.
- Judas: `repair_tendency` 낮음. `conceal_tendency` 는 은밀(covert)한 형태, 공개 deny 아님.

---

## 6. Motif와 4축 Rubric의 관계

- **scene_response_fit (H.1)**: "primary motif가 scene에 맞는가"로 재해석 가능. scene → expected motif set → actions.
- **character_consistency (H.1)**: motif 활성도의 profile consistency. Peter profile이면 conceal/repair가 지배적이어야.
- **context_break (H.2)**: motif 없이 발화된 action = motive gap.
- **novelty structured_deviation (H.5)**: 같은 motif 안에서 다른 action 선택 = meaningful variation, 다른 motif 에서 fire = noise 가능성 높음.

즉 motif layer가 rubric 이해를 높여주는 **해석 공용어**가 됨.

---

## 7. 구현 체크리스트

- [ ] `engine/person/motif.py` 신설
- [ ] Motif activation 함수 (Persona profile 입력)
- [ ] Motif → action sampling 함수
- [ ] `_decide_action` 3-stage로 교체 (Step C)
- [ ] `engine/rubric/scene_response_critic.py` → motif 기반 재해석 (선택)
- [ ] Provenance 추가: `selected_motif`, `alternative_motifs`, `motif_action_family`

---

**End of Step B.**
