# Story Unit Taxonomy (Minimal — J-Alpha)

**Date**: 2026-04-28
**Phase**: J-Alpha Step A2
**Source**: `WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` §4.4 Step A2
**Status**: Minimal (3 units only). Full taxonomy는 J-Beta로 연기.

---

## 0. 목적

J-Alpha 5-variation demo가 작동하기 위한 *최소* taxonomy. Layer 2 (Story Unit Taxonomy) 의 minimal viable scaffolding.

> **3개 unit만 정의**: Person Arc / Event Arc / World Arc

Time-slice는 unit이 아니라 **slicing parameter**로 둠.

---

## 1. 3 Story Units

### 1.1 Person Arc — 인물 변화의 단위

**정의**: 한 agent의 fast/slow state 변화 궤적 (drive, emotion, belief).

**최소 시그널**:
- shame / awe / fear peak + final
- belief shift (예: jesus_understanding 4 단계 변화)
- communal_role 변화 (예: disciple → failed → restored)
- moral_injury / event_trauma 누적

**Story 출력에서**:
- "사람들이 흔들렸지만 다시 자리를 잡았다" (recovery)
- "어떤 자리에서는 시간이 멈춘 것처럼 보였다" (saturation)

**Anchor 예시**:
- Peter shame arc (P1-P12 baseline의 cohort outcomes)
- 개별 agent의 trace-level 변화

---

### 1.2 Event Arc — 사건 발생의 단위

**정의**: 외부/내부 이벤트의 발생 + 반응 + 사후 패턴.

**최소 시그널**:
- accusations_count + 시점 분포
- confessions / forgiveness 누적 패턴
- guard_approaches / miracle_witnessed 같은 trigger
- failure_mode (shame_cap / no_forgiveness_uptake / ...)

**Story 출력에서**:
- "비난은 흩어지지 않고 한 방향으로 모였다"
- "고백은 멈추지 않고 이어졌고, 용서한다는 말도 그만큼 거리 위에 떠다녔다"

**Anchor 예시**:
- 1 accusation → cascade
- 3 accusations spread vs clustered (Branch C S2)
- miracle 1/3/5 frequency (Branch C S3)

---

### 1.3 World Arc — 세계 상태의 단위

**정의**: crowd / authority / public attention layer의 변화.

**최소 시그널**:
- crowd_blame total peak/final
- public_suspicion peak/final
- authority_vigilance peak/final
- top_blame_target (v4 — interpersonal axis)

**Story 출력에서**:
- "의심이 거리 위로 짙게 깔렸다"
- "권위의 시선은 끝까지 느슨해지지 않았다"
- "사람들의 눈은 노동자들에게로 향했다"

**Anchor 예시**:
- Branch C placement variation (S5)
- Branch C cast composition (S4)

---

## 2. 3 Units 간 관계

```
World Arc (외부 압력)
    ↓ 영향
Event Arc (사건 발생)
    ↓ trigger
Person Arc (개인 반응)
    ↓ 누적
[story 5단 구조]
```

**5단 구조 매핑**:
| Story Stage | 주된 Unit |
|---|---|
| 도입 (opening) | World Arc |
| 압력 상승 (pressure) | Event Arc + World Arc |
| 반응 분기 (response) | Person Arc |
| 귀결 (outcome) | Person Arc + Event Arc |
| 사후 세계 (aftereffect) | World Arc |

---

## 3. Time-slice는 unit이 아니다

**중요**: time-slice는 **separate unit이 아니라 slicing parameter**.

같은 trajectory를:
- 전체 200 ticks → "passion week" 전체 이야기
- ticks 5-50 → "accusation 직후" 짧은 이야기
- ticks 100-200 → "recovery phase" 이야기

→ 같은 trajectory의 다른 windowing. unit 추가 X.

---

## 4. Anchor 정의

**Anchor** = "같은 World/Event 조건에서 출발하는 trajectory cluster의 묶음".

Concrete: 같은 cast composition + 같은 placement + 같은 seed_events + 다른 seed.

J-Alpha curated set:
- Peter anchor 1 (예: scarcity baseline + 5 seeds)
- Van Gogh anchor 1 (예: sacred baseline + 5 seeds)

→ J-Alpha selector는 anchor → 5 variations 묶음만 반환.

---

## 5. 무엇을 하지 말 것 (J-Beta로 연기)

다음은 J-Beta에서:

- **Story Unit 추가**: ~~Group Arc~~, ~~Cohort Arc~~, ~~Conflict Arc~~ 등
- **Cross-anchor query**: "어떤 anchor가 가장 흥미로운가?"
- **Trajectory labeling**: 70+ trajectory를 unit별 분류
- **Selector scoring**: arc 강도 점수
- **Genre mode**: novel / drama / webtoon 분기

→ J-Alpha는 *이 3 unit만으로* demo 작동 검증.

---

## 6. 검증 (J-Alpha 성공 시)

이 minimal taxonomy로 작성된 5-variation demo가 §1.1-1.3 3 unit 모두 텍스트에서 식별 가능하면:
- Layer 2 minimal scaffolding 충분
- J-Beta에서 unit 확장 (Group / Conflict / Genre 등)

이 minimal로 부족하면:
- J-Alpha 실패 신호 → diagnose 후 unit 추가 또는 spec 변경

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 minimal (this) | 2026-04-28 | J-Alpha Step A2. 3 unit (Person/Event/World) only. |
| (future v2 full) | TBD | J-Beta 시작 시 확장 → `STORY_UNIT_TAXONOMY.md` 별도 |
