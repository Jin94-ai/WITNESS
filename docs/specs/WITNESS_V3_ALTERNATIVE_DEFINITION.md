# WITNESS v3.0 — Alternative Trajectory 정의 (Phase H.4)

**Status:** Rule #23 (ABSOLUTE) — Lee 2026-04-23 승인.
**Scope:** Rubric DiscoveryClass `CANON_COMPATIBLE_ALTERNATIVE` / `CHARACTER_CONSISTENT_NOVEL` 판정 기준.

---

## 0. 왜 이 정의가 필요한가

Phase G 분석(2026-04-23) 에서 다음이 확인됨:
- `plausible_alternative` category의 `canon_soft_drift` 분포가 `obvious_noise`와 0.7 unit 차이로 거의 겹침
- 현재 rubric은 "canonical이 아닌 것 전부"를 alternative로 분류하는 경향
- `noi_03`, `noi_13` 같은 맥락-붕괴 trajectory 가 `canon_compatible_alternative`로 오분류

Lee 진단:
> "alternative는 그냥 'canonical이 아닌 것'이 아닙니다. canonical과 다르지만 장면 적합성 + 캐릭터 일관성 + 인과 정합성을 유지하는 trajectory입니다."

이 정의 문서는 판정의 **구속력 있는 기준** 이다.

---

## 1. 정의 (verbatim Lee)

> **Alternative** = canonical과 다르지만 다음을 유지하는 trajectory:
> - 장면 적합성 (scene fit)
> - 캐릭터 일관성 (character consistency)
> - 인과 정합성 (causal coherence)

## 2. 판정 4 조건 (all must hold)

### 조건 A. Hard canon 위반 없음

- Action vocabulary 범위 내
- 시대착오 / 정경 직접 모순 / 신성 모독 signal 부재
- 운영화: `CanonCritic.is_canon_valid == True`

### 조건 B. Response family 인접성 (bounded plausibility)

모든 주요 canonical event (public_accusation, eye_contact, restoration_moment
등) 에 대해, trajectory의 응답이 **scene-expected family** 안에 있거나, 또는
adjacency 관계에 있는 family에 속함.

- `accusation` → defensive family (deny / withdraw / flee / hide) OR adjacent
  (silence / follow_at_distance)
- `eye_contact` → emotional-recognition family (weep / withdraw / confess)
- `restoration` → repair family (confess / assert_loyalty / follow)

완전 이탈 (accusation 에 `jump_into_sea` 등)은 **alternative 아님**.

- 운영화: `SceneResponseCritic.fit_rate >= scene_fit_min` (기본 0.5)

### 조건 C. Bounded plausible divergence (drift 범위)

- **canonical 평균 drift < alternative drift < noise 하한**
- Phase G 실측: canonical median 25, alternative 바람직 27-32, noise 29+ 경계
- drift가 canonical 수준이면 → **CANONICAL_REPRODUCTION** (alternative 아님)
- drift가 noise 수준이면 → **NOT_DISCOVERY_NOISE** (alternative 아님)
- 운영화: `reproduction_threshold < canon.soft_drift < noise_threshold`

### 조건 D. Motive-Action 연결 설명 가능

모든 action이 (a) 이전 state 변화로 설명되거나 (b) canonical event에
의해 trigger 됨. Unexplained/random action change = alternative 아님.

- 운영화: `ContextBreakCritic.is_context_coherent == True` AND
  `NoveltyCritic.branching_coherence >= 0.5`

---

## 3. DiscoveryClass와의 관계

| Class | 조건 |
|---|---|
| **CANONICAL_REPRODUCTION** | A + drift ≤ reproduction_threshold |
| **CANON_COMPATIBLE_ALTERNATIVE** | A + B + C + D 충족, novelty = meaningful 아닐 때 (copy band) |
| **CHARACTER_CONSISTENT_NOVEL** | A + B + C + D 충족, novelty = meaningful 추가 |
| **INVALID** | A 위반 (hard canon violation) |
| **NOT_DISCOVERY_NOISE** | B 또는 D 위반 (scene mismatch 또는 context break) |
| **NOT_DISCOVERY_HARDCODED** | 외부 주입된 event-firing만 존재 |
| **NOT_DISCOVERY_INTERPOLATION** | 학습 데이터 interpolation 소스 |

---

## 4. Phase G 경계 사례 재판정

정의 4 조건으로 재평가 시 기대되는 재분류:

| Trajectory | 원 label | 4 조건 체크 | 재분류 가능성 |
|---|---|---|---|
| `alt_07` (drift 27.0, deny 재현) | alternative | A ✓ / B ✓ / C: drift 27.0 ≤ canonical-P90 28.3 | → **canonical-like** (label 이동) |
| `alt_13` (drift 34.0) | alternative | A ✓ / B ? / C: drift 34 > alt 상한 32 → ✗ | → **noise** (label 이동 가능) |
| `noi_03` (drift 29, L1 context drift) | noise L1 | A ✓ / B: scene fit 저하 / D: context break | → **noise 유지** (rubric이 포착 해야) |
| `noi_13` (drift 29, L3 character break) | noise L3 | A ✓ / B ✗ / D ✗ | → **noise 유지** |

---

## 5. 금지 사항 (Rule #23 가이드라인)

- "canonical이 아닌 것 = alternative" 같은 느슨한 정의 사용 금지
- drift 수치만으로 alternative/noise 구분 금지 (Phase G 증명: 구분 불가)
- Character critic에서 smoothness 보상 금지 (Rule #22) — 같은 이유로
  alternative 정의에서도 "매끈함"을 가산점으로 쓰지 말 것
- 장면 이탈을 "창의적 해석" 으로 재포장 금지

---

## 6. 변경 이력

- 2026-04-23: 초안, Lee 승인 (Phase H.4)

---

**End of Alternative Definition spec.**
