# Policy Refactor Plan (Step C)

**작성:** 2026-04-24
**코드 상태:** 구현 완료 (이전 세션). 본 문서는 회고록 + 향후 개선 계획.

---

## 0. 목표

Direct action boost 구조 → **Scene recognizer → Motif activator → Action selector** 3단 구조 교체.

---

## 1. Before vs After

### 1.1 Before (B2 retune)

```python
# engine/person/loop.py::_decide_action (삭제된 코드)
accusation_fresh = ctx.has_any_recent(["public_accusation", "crowd_mockery"], within=0)
eye_contact_fresh = ctx.has_recent("eye_contact", within=1)
...
deny_w = 0.1 + 8.0 * (1.0 if accusation_fresh else 0.0) + ...
weep_w = 0.2 + ... + 6.0 * (1.0 if eye_contact_fresh else 0.0) + ...
# Scene → action direct 연결
```

문제:
- Peter canonical fit 전용
- Judas에 적용하면 의미 없음 (accusation event 없음)
- 다른 시나리오 확장 불가

### 1.2 After (Persona Engine)

```python
# engine/person/loop.py::_decide_action (현재)

# Stage 1: scene recognizer (events → event recency flags)
events_recent = {ev: 1 if age <= 3 else 0 for ev, age in ...}

# Stage 2: motif activator (pressure + state + profile → 8 motif activations)
motif_result = activate_motifs(state, pressures, events_recent, profile)

# Stage 3: action selector (top motifs → priors → availability → sample)
selection = select_action(motif_result, profile, availability_filter, rng)
return selection.action
```

---

## 2. 3단 구조 세부

### 2.1 Stage 1: Scene Recognizer

**입력:** `self._recent_event_last_fired` (event_id → last tick)
**출력:** `events_recent: dict[event_id, 1|0]`

**현재 구현:** 단순히 "최근 3 tick 내 발화" 플래그.

**향후 개선:**
- Scene category aggregation: 여러 event를 상위 scene으로 묶음
  - accusation_scene: {public_accusation, crowd_mockery}
  - exposure_scene: {eye_contact, betrayal_witnessed}
  - threat_scene: {guard_approaches, weapon_drawn_nearby}
  - sacred_scene: {sacred_meal, prayer_invitation, miracle_witnessed}
  - repair_scene: {forgiveness_offered, restoration_moment}
- Scene intensity (여러 event 동시 발화 시 상위 scene intensity)
- Scene duration (지속 중 vs 1회성)

### 2.2 Stage 2: Motif Activator

**입력:** state, pressures, events_recent, profile
**출력:** `MotifActivation` (8 motif activations + primary + top_two)

**현재 구현:** `engine/persona/motif.py`
- 8 sigmoid-based activation functions
- 각 motif는 pressure + state + event 가중합, sigmoid 적용
- `profile.motif_tendency[motif]` 로 개인 차 스케일

**향후 개선:**
- Cross-motif suppression (예: grieve 활성 시 conceal 감쇄)
- Scene-driven motif boost: recognized scene이 특정 motif를 기대 (scene_semantics.json 주입)
- Temporal inertia: 이전 tick의 primary motif가 다음 tick에 잔존력

### 2.3 Stage 3: Action Selector

**입력:** `MotifActivation`, profile, availability_filter
**출력:** `ActionSelection` (action, selected_motif, weights, blocked_actions, notes)

**현재 구현:** `engine/persona/selector.py`
- Top-2 motif blend (activation-weighted)
- 각 motif의 `motif_action_priors[action]` → weighted sum
- Availability filter (gate)
- Weighted random sample

**향후 개선:**
- Profile의 motif_action_priors를 state-conditioned (같은 motif라도 state에 따라 다른 priors)
- Blocked action의 유사-대안 제안 (run_to_tomb blocked → run_to_meeting_point 같은 near-neighbor)
- Temperature parameter (profile에 `decision_temperature` 추가해 결정 랜덤성 제어)

---

## 3. 치환 예시 (Direct boost → Motif boost)

Lee §7 완료 기준: direct action boost 50% 이상이 motif boost로 대체.

### 3.1 accusation_fresh → deny +8.0

**Before:** direct weight boost
**After:** 
- accusation event → shame_exposure/social_threat pressure 상승 (state transition Cat A1)
- conceal motif 활성 (state: shame↑ + social_threat↑)
- profile.motif_action_priors["conceal"]["deny"] = 0.45 (Peter)
- conceal 활성 → deny 선택 확률 증가

치환 ✓

### 3.2 eye_contact_fresh → weep +6.0

**Before:** direct boost
**After:**
- eye_contact event → grieve motif boost (`has_eye_contact` input)
- profile.motif_action_priors["grieve"]["weep"] = 0.60 (Peter)
- grieve 활성 → weep 우세

치환 ✓

### 3.3 restoration_fresh → confess +6.0

**Before:** direct boost
**After:**
- restoration_moment → has_restoration flag → seek_repair activation (profile bias 적용)
- profile.motif_action_priors["seek_repair"]["confess"] = 0.30 (Peter)
- seek_repair 활성 → confess 후보

치환 ✓

### 3.4 forgiveness_fresh → confess +2.0

**After:** 동일 경로 (`has_forgiveness` flag → seek_repair)

치환 ✓

### 3.5 eye_contact_fresh → deny × 0.15 (억제)

**Before:** direct multiplier
**After:** 
- eye_contact 시 grieve motif 활성 → top_2 에서 conceal 밀림 (cross-motif competition)
- 자연스러운 억제 효과

치환 ✓

**5개 치환 모두 완료** (Lee 완료 기준 달성).

---

## 4. Availability gate와의 관계

Gate는 engine/action/availability_gate.py 에 그대로 유지. 단, **gate가 motif 선택 후 action 필터링**에 사용된다는 위치가 명확해짐.

**순서:**
1. Motif activator가 motif 선택 (gate 고려 X)
2. Action selector가 motif의 action priors 조회
3. Gate로 각 action 필터링
4. 통과한 action 중 가중 sample

**왜 이 순서?**
- Motif는 "의도" 수준. 의도 자체는 availability와 무관.
- Action이 "실행" 수준. Gate는 실행 가능성 체크.
- 의도 → 실행 순서가 인간 의사결정과 일치.

---

## 5. 남은 리팩토링 (향후)

### 5.1 Scene recognizer 독립 모듈화

현재는 `_decide_action` 안에 인라인. `engine/persona/scene_recognizer.py` 로 분리하면 rubric critics (scene_response, context_break) 도 같은 recognizer 사용 가능.

### 5.2 Profile의 motif_tendency에 state conditioning

현재: `profile.motif_tendency.grieve = 1.2` 고정.
개선: `profile.motif_tendency_conditional({grieve: {when_guilt_high: 1.5, default: 1.2}})` 같은 조건부.

### 5.3 Motif → Action cross-scenario vocabulary

Peter/Judas scenarios에 공통 action vocab (follow_closely, discuss 등) + scenario-specific (run_to_tomb, jump_into_sea, join_crowd). profile의 action_priors 에서 scenario-specific action은 empty prior 로 두면 안전.

### 5.4 Temporal smoothing

현재 motif는 매 tick 독립 계산. 인간 행동은 관성이 있으므로:
```python
motif_smoothed[t] = 0.7 * motif_current[t] + 0.3 * motif_smoothed[t-1]
```
정도로 lag 필터. profile.motif_inertia 파라미터 추가.

---

## 6. 완료 기준 점검 (Lee §7)

| 완료 기준 | 상태 |
|---|---|
| direct action boost 50% 이상 motif boost 대체 | ✓ 5/5 (전부) |
| Peter와 Judas가 동일 motif vocabulary 공유 | ✓ 8 motif 동일, profile만 다름 |
| action score 계산에서 motif layer 명시적 | ✓ `ActionSelection.selected_motif` 필드 |

**Step C 공식 완료.**

---

## 7. 테스트 커버리지

`tests/test_persona/test_persona_engine.py` (13 tests):
- Motif activation behavior (4)
- Action selection + gate filter (2)
- Profile validation (2)
- Peter/Judas profile loading + comparison (3)
- Rule #1 grep (1)
- MotifTendency get fallback (1)

---

**End of Step C documentation.**
