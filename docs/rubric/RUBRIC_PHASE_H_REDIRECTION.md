# Rubric Phase H Redirection (Step L)

**작성:** 2026-04-24
**목적:** Phase G/H에서 발견된 rubric 구조 문제를 Persona/World 전환 구조와 연결. 재설계 방향 확정.

---

## 0. Phase G 문제 요약 (이미 진단)

1. Canonical의 `character_composite` 가 **최저** (critic이 smoothness 보상 → canonical 급전환 감점)
2. Alternative ↔ Noise `drift` 겹침 (gap 0.7)
3. `causal_smoothness` 세 category에서 **구분력 없음**
4. `novelty_critic` 이 `canon_drift` 재사용 → **독립 축 아님**

**Phase H에서 해결:**
- Character critic 재작성 (relation_stability / identity_retention / recovery_plausibility)
- SceneResponseCritic 신설
- ContextBreakCritic 신설
- Novelty structured_deviation

---

## 1. Persona/World 전환과의 연결

Phase H Rubric 구조는 **Persona Engine 의 motif layer** 와 자연스럽게 결합:

| Rubric 축 | Persona/World 연결 |
|---|---|
| **scene_response_fit** | Scene recognizer output + motif activation 일치도 |
| **character_consistency** | Profile 의 identity markers 유지 + motif transition 의 profile-appropriate 여부 |
| **context_break_score** | World affordance (role cluster + info access + physical location) 와 action 일치 |
| **structured_novelty** | Motif path divergence from canonical (distance 아님, motif 구조 차이) |

---

## 2. 구조 변경 권고

### L-1. scene_response_fit (기존 유지 + 강화)

**현재:** `engine/rubric/scene_response_critic.py` — event_id → action family 매핑.

**권고 강화:**
- Motif layer와 연결: "scene X에서 motif Y 가 활성되어야 하는가" 검증
- Scene → expected motif (1차), motif → expected action family (2차)

### L-2. character_consistency (강화)

**현재:** relation_stability / identity_retention / recovery_plausibility.

**권고 강화:**
- Profile alignment: 관찰된 motif distribution vs `profile.motif_tendency`
  - Peter profile expects seek_repair=1.4, conceal=1.2 → 높은 활성 기대
  - 관찰 분포가 profile에 부합하면 high score
- Relation trajectory: target-aware relations 의 long-term 궤적이 role cluster 예상과 일치

### L-3. context_break_score (현재 유지 + 확장)

**현재:** affordance / scene_mismatch / motive_gap.

**권고 확장:**
- World-level affordance: role_cluster 가 허용하는 action pool
  - fisher_laborer 가 "convene_council" → context break
  - priest 가 "physical_labor" → context break
- Info access violation: agent가 모를 정보에 반응 (예: 멀리 있는 사건에 즉각 반응)
- Resource/spatial violation: 현재 상태에서 불가능한 행동

### L-4. structured_novelty (재정의 강화)

**현재:** `family_variation × (1.5 - branching_coherence)`.

**권고 재정의:**
- **motif deviation structure** 사용:
  - Same motif path, different action realization = meaningful novelty
  - Different motif path, but coherent with profile/role = plausible novelty
  - Different motif path, incoherent = noise
- 예: Peter canonical 은 conceal→grieve→seek_repair. Alternative는 seek_repair 없이 grieve 로 끝 (motif 궤적 다르지만 profile 적합). Noise는 conceal 없이 observe_wait 만 (profile 불일치).

---

## 3. Distance 중심 탈피

Lee §16 핵심: *"rubric은 distance 중심에서 벗어나야 한다"*.

### 3.1 Distance를 유지하는 영역

- `canon_soft_drift` — edit distance. **1차 filter** 로만 (완전 이탈 감지).
- Hard constraint (`canon_valid`) — gate.

### 3.2 Distance를 대체하는 영역

- **Novelty 구분**: distance 아닌 motif structure 차이
- **Alternative 판정**: drift 아닌 scene_fit + motive coherence + role affordance
- **Character**: flip count 아닌 profile alignment

---

## 4. 새 rubric flowchart (H+L 통합)

```
1. is_all_hardcoded?                          → NOT_DISCOVERY_HARDCODED
2. canon hard violation?                      → INVALID
3. context_break_rate high (role/affordance/motive)? → NOT_DISCOVERY_NOISE
4. scene_response_fit low AND character_consistency low? → NOT_DISCOVERY_NOISE
5. canon_soft_drift ≤ reproduction_threshold? → CANONICAL_REPRODUCTION
6. motif path profile-consistent AND scene-fit OK AND context OK? → CHARACTER_CONSISTENT_NOVEL
7. canon-compatible + scene-fit OK (but motif path not novel) → CANON_COMPATIBLE_ALTERNATIVE
```

**변화:**
- Novelty_band 단독 gate 제거 (3-4 통합)
- Motif path coherence 가 6 step의 주 feature

---

## 5. Persona Profile 알고 판정

새 rubric은 agent의 PersonaProfile 을 입력으로 받아 **profile-adjusted** 기준 적용.

```python
evaluator.evaluate(
    records,
    profile=agent.profile,           # NEW: profile alignment check
    role_cluster=agent.role,         # NEW: affordance check
    world_context=world.context,     # NEW: info/spatial validation
)
```

---

## 6. World Engine coupling 과의 연결

Context break 판정에 world state 참조:

```python
# agent action = "draw_sword" at tick T
# world.institutional.law_enforcement_strength at T = 0.9 (high)
# → action affordance reduced (무기 소지 위험) → context break weighted 1.3×
```

즉 rubric 이 **world 상태 민감** 하게 작동.

---

## 7. 완료 기준 점검 (Lee §16)

| 완료 기준 | 상태 |
|---|---|
| Persona/world 리팩토링이 rubric 재설계와 연결 | ✓ (Motif + Role + World coupling) |
| 평가 기준이 scene-fit / character-fit / context-break 쪽으로 이동 | ✓ (L-1/L-2/L-3) |

---

## 8. 구현 우선순위

1. **L-2 강화** (character_consistency에 profile alignment) — 작은 코드
2. **L-3 확장** (role_cluster affordance 추가) — 중간 코드
3. **L-4 재정의** (motif path-based novelty) — 큰 코드. Motif history 추적 필요.
4. L-1 보강 — scene recognizer와 연계 (선택)

---

## 9. 철학 전환 명시

**Distance-based:** "이 trajectory가 canonical에서 얼마나 먼가"
**Structure-based:** "이 trajectory의 motif 구조가 profile/role/scene과 얼마나 정합적인가"

두 번째가 새 중심. Canonical copy를 좋은 결과로 보지 않고, **coherent trajectory (Canonical일 수도, alternative일 수도)** 를 좋은 결과로 본다.

---

**End of Step L.**
