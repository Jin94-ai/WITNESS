# Witness v3.0 Event → Pressure Table

> **Spec**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) §5.4
> **Code**: [engine/pressure/event_pressure_map.py](../engine/pressure/event_pressure_map.py)

## 1. 구조

각 event id는 8개 pressure 변수에 대한 delta vector를 가진다. 이벤트 발생 시 `PressureField`에 delta가 더해진다 (이미 존재하는 압력은 `PressureDecay`로 decay 후 합산).

## 2. 전체 테이블 (20+ events)

| event_id | social_threat | physical_threat | shame_exposure | loyalty_pull | uncertainty | urgency | isolation_pressure | sacred_salience |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `public_accusation` | +3 | +1 | +4 | 0 | 0 | 0 | 0 | 0 |
| `public_exposure` | +2 | 0 | +3 | 0 | 0 | 0 | 0 | 0 |
| `crowd_mockery` | +4 | +1 | +5 | -1 | 0 | 0 | 0 | 0 |
| `crowd_pressure_spike` | +3 | 0 | 0 | 0 | 0 | +2 | 0 | 0 |
| `primary_figure_eye_contact` | 0 | 0 | +3 | +5 | 0 | 0 | 0 | +2 |
| `primary_figure_rebuke` | 0 | 0 | +4 | +2 | +2 | 0 | 0 | 0 |
| `primary_figure_suffering_visible` | 0 | +1 | 0 | +6 | 0 | +2 | 0 | +3 |
| `primary_figure_teaching` | 0 | 0 | 0 | +3 | -1 | 0 | 0 | +4 |
| `ally_nearby` | -2 | 0 | -1 | +2 | 0 | 0 | -3 | 0 |
| `ally_departed` | +1 | 0 | 0 | 0 | 0 | 0 | +3 | 0 |
| `peer_failure` | 0 | 0 | +1 | 0 | +2 | 0 | 0 | -1 |
| `guard_approaches` | +1 | +4 | 0 | 0 | 0 | +3 | 0 | 0 |
| `arrest_warrant` | 0 | +5 | 0 | 0 | +2 | +3 | 0 | 0 |
| `weapon_drawn_nearby` | 0 | +6 | 0 | 0 | 0 | +4 | 0 | 0 |
| `sacred_meal` | 0 | 0 | 0 | +3 | -1 | 0 | 0 | +5 |
| `prayer_invitation` | 0 | 0 | 0 | +2 | 0 | 0 | 0 | +3 |
| `miracle_witnessed` | 0 | 0 | 0 | +3 | -2 | 0 | 0 | +6 |
| `time_running_out` | 0 | 0 | 0 | 0 | +2 | +5 | 0 | 0 |
| `hidden_information_revealed` | 0 | 0 | +1 | 0 | -3 | 0 | 0 | 0 |
| `forgiveness_offered` | 0 | 0 | -3 | +3 | 0 | 0 | 0 | +4 |
| `restoration_moment` | 0 | 0 | -4 | +2 | 0 | 0 | 0 | +3 |

**총 21 events.** Spec §5.7 "최소 20개" 통과.

## 3. Decay 반감기 (spec §5.5)

각 pressure 변수의 half-life (ticks):

| pressure | half-life | 의미 |
|---|---:|---|
| social_threat | 2 | 군중 사건은 빠르게 사라짐 |
| physical_threat | 1.5 | 물리 위협은 상황 변화 시 즉시 | 
| shame_exposure | 5 | 공개 수치는 수 턴 지속 (spec §5.5) |
| loyalty_pull | 8 | 결속감은 오래 남음 |
| uncertainty | 3 | 정보 공백은 중간 지속 |
| urgency | 1 | 긴급성은 이벤트 후 즉시 감소 (spec §5.5) |
| isolation_pressure | 6 | 고립감은 장시간 | 
| sacred_salience | 20 | 거룩한 맥락은 장면 내내 지속 (spec §5.5) |

## 4. Peter 시나리오 매핑 (참고)

Engine의 generic event_id를 Peter 시나리오 특정 사건에 연결:

| generic event_id | Peter 시나리오 해석 |
|---|---|
| `primary_figure_eye_contact` | 수닭 울음 후 예수와 눈 마주침 (눅 22:61) |
| `primary_figure_suffering_visible` | 십자가 아래 예수의 고난 목격 |
| `primary_figure_rebuke` | "사탄아 내 뒤로 물러가라" |
| `primary_figure_teaching` | 산상수훈 등 가르침 장면 |
| `guard_approaches` | 겟세마네 체포 순간 |
| `weapon_drawn_nearby` | 말고의 귀 |
| `sacred_meal` | 최후의 만찬 |
| `miracle_witnessed` | 변화산, 물 위 걸음 등 |
| `forgiveness_offered` / `restoration_moment` | 디베랴 호수 3회 질문 |

이 매핑은 content 레벨 (`content/peter/pressure_events.json` — Phase 5+ 에서 작성 예정).

## 5. Rule #1 / Rule #12 준수

- Engine `event_pressure_map.py` 파일 내 특정 인물명 **0** (grep test로 검증됨)
- `PressureVector` 는 숫자만 반환. Action 결정 없음 (Rule #12 준수)

## 6. 한 줄 요약

**"21개 이벤트 × 8개 압력 = 168 scalar의 hand-crafted 테이블. Half-life 2-20 ticks로 각 압력이 다른 속도로 잔향."**
