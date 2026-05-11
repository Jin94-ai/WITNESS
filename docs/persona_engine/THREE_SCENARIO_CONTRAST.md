# Three-Scenario Persona Engine Universality Evidence

**작성:** 2026-04-24
**범위:** Peter / Judas / Van Gogh 세 scenario가 동일 엔진 위에서 profile만으로 작동.
**Lee 원칙 준수:** Rule #5 (3번째 scenario) / Rule #21 (튜닝 대상 아님, contrast bench).

---

## 0. 핵심 주장

> **같은 PersonV3Loop + persona engine 위에서 세 다른 인물이 서로 다른 profile 파라미터만으로 완전히 다른 motif 분포와 action 시퀀스를 생성한다.**

engine 코드 수정 없음. scenario별 handcraft 문서 없음.

---

## 1. 측정 조건

- 엔진: `PersonV3Loop` + `engine/persona` (3-stage motif mediation)
- seed: 0
- ticks: 30
- 각 scenario: `content/<name>/v3/{initial_state,canonical_events,profile}.json`

---

## 2. Motif 분포 비교

| Motif | Peter | Judas | Van Gogh |
|---|---:|---:|---:|
| observe_wait | 0 | **23** | **16** |
| remain_present | **22** | 7 | 1 |
| conceal | 4 | 0 | 0 |
| grieve | 2 | 0 | 2 |
| confront | 1 | 0 | 0 |
| seek_repair | 1 | 0 | **5** |
| withdraw | 0 | 0 | 4 |
| confess | 0 | 0 | 2 |

**3 distinct signatures — same engine:**
- **Peter**: 적극 참여형 (remain_present 지배 → 사건 반응 시 conceal/grieve/confront)
- **Judas**: 수동 관찰형 (observe_wait 압도적)
- **Van Gogh**: 고립 궤적 (observe_wait + withdraw + seek_repair + confess)

---

## 3. Profile 파라미터 대비

| Parameter | Peter | Judas | VG | 차이 해석 |
|---|---:|---:|---:|---|
| **Pressure sensitivity** | | | | |
| social_threat | 1.2 | 0.8 | **0.7** | VG는 고립형 (사회적 위협 덜 민감) |
| loyalty_pull | 1.3 | 0.7 | **1.4** | VG 형제에 강한 결속 |
| sacred_salience | 1.4 | 0.8 | **1.5** | VG 창작=sacred |
| isolation_pressure | 0.9 | 1.2 | **1.3** | VG 고립 민감 |
| **Motif tendency** | | | | |
| conceal | 1.2 | 1.3 | 1.0 | Peter/Judas 공개 회피; VG 해당 없음 |
| withdraw | 1.0 | 1.2 | **1.4** | VG 가장 강함 |
| grieve | 1.2 | 1.0 | **1.4** | VG 애도 강함 |
| seek_repair | 1.4 | 0.4 | 1.2 | Peter 최강, Judas 최약, VG 중상 |
| observe_wait | 0.8 | 1.3 | 1.1 | Judas 최강 |
| **Recovery bias** | | | | |
| grief_tail_strength | 1.0 | 1.3 | **1.5** | VG 애도 long tail 가장 강함 |
| trust_restoration_bias | 1.2 | 0.5 | 0.9 | Peter 재결속 강함 |
| **Relation bias** | | | | |
| peer_dependence | 1.0 | 0.6 | **0.5** | VG 가장 peer-독립 |
| primary_focus_attachment | 1.4 | 0.7 | **1.5** | VG Theo 결속 가장 강함 |

---

## 4. Scenario-canonical 궤적 정합성 (정성 평가)

### 4.1 Peter (passion week)
- conceal activated at accusation scene (T17-20) — 부인 맥락 일치
- grieve 2회 (후반) — 통곡 맥락 부분 일치
- seek_repair 1회 - 복귀 신호

### 4.2 Judas (passion week)
- observe_wait 압도 — "계산/대기" 스타일 일치
- 공개 deny 없음 — Judas 은밀성 반영 ✓
- seek_repair 0회 — 회복 경로 부재 반영 ✓

### 4.3 Van Gogh (Arles period)
- T1-2 grieve (초기 우울)
- T6-16 observe_wait (Gauguin 도착부터 관계 관찰)
- T17-21 withdraw (ally_departure → 공개_accusation → self_harm_impulse)
- T24-28 seek_repair (Theo 편지 → confess / assert_loyalty → restoration)
- **심리적 내러티브 arc가 순서대로 분포됨** ✓

---

## 5. Action diversity

| | Peter | Judas | VG |
|---|---:|---:|---:|
| distinct actions | 9 | 4 | 9 |
| top action | follow_closely (9) | discuss_with_disciples (16) | stay_awake (8), discuss (8) |
| canonical-defining actions (deny/weep/confess) | 0/2/0 | 0/0/0 | 0/2/3 |

VG에서 confess 3회는 motif_action_priors["seek_repair"]["confess"]=0.40 반영.

---

## 6. Engine Universality 증거

### 6.1 코드 수정 없음
- `engine/person/loop.py` — 수정 없음
- `engine/persona/*.py` — 수정 없음
- 새 event 3개 (creative_surge / creative_conflict / self_harm_impulse) 만 `engine/world/events.py` 에 generic 추가

### 6.2 Content 추가만
- `content/vangogh/v3/{initial_state,canonical_events,profile}.json`

### 6.3 Handcraft 문서 없음
- VG 전용 행동 규칙 / canonical sequence 튜닝 / direct boost 없음

### 6.4 Profile 파라미터만으로 차이 발생
- 같은 motif activation 공식
- 같은 action vocabulary
- 다른 motif_tendency + pressure_sensitivity + action_priors

---

## 7. Rule #5 "universality" 주장 범위

**주장 가능한 것:**
- **Engine universality (partial)** — 엔진이 이질적 scenario 3개를 수용함
- Profile 파라미터 공간의 **이질성 표현 능력** 증명

**주장 불가한 것:**
- "엔진이 모든 인간 반응을 표현한다" — 3 scenario는 작은 sample
- "특정 수치가 모든 인물에 적용된다" — scenario-specific
- "Rule #13 발견 판정이 범용 유효" — 여전히 rubric 재조정 가능성

Lee 2026-04 경고 유지: *"the engine is scenario-agnostic; the patterns are scenario-specific"*.

---

## 8. HARNESS 자가감사 (H7)

### H1 null hypothesis
"VG가 다른 분포를 보인 것은 profile이 다르니 자명" → trivial. 맞음.

그러나 **새로운 claim**: "VG scenario-specific handcraft 없이 작동". 이 claim 의 trivial explanation:
- "엔진이 이미 Peter/Judas에 적응돼 있어서 비슷한 passion arc를 가진 VG도 자동 작동함" → **부분 타당**. VG Arles 가 passion arc와 비슷 (accusation / betrayal / restoration) 인 것은 맞음.
- 더 이질적 scenario (예: 전쟁 영웅, 농민 봉기) 에서도 작동 여부 미증명.

### H4 what could still be wrong
- 3 scenario 전부 "passion / crisis → remorse / repair" 궤적. 유사 구조.
- 완전 다른 장르 (comedy, romance, coming-of-age) 테스트 안 됨.
- VG recovery profile이 grief_tail_strength 높음에도 tick 30 내 회복 강제 (forgiveness_offered event) — 자연 회복 경로 아직 불확실.

### H6 다음 방향 (equal-weight)

**K1**: 4번째 scenario 추가 (완전 이질: 전쟁 영웅 / 일반 농민 등)
**K2**: L-2 강화 (character_critic 에 profile alignment)
**K3**: Bulk population 시뮬레이션 실측 (20-50 agents)
**K4**: 6-layer world engine 실제 구현 (Step I 문서 → 코드)

**내 bias**: K4 (world layer 실제 engine) → K3 (population 실측). 이유: Steps A-L 문서 완성되어 있고, 다음은 구현 측면 강화.

---

**End of three-scenario contrast.**
