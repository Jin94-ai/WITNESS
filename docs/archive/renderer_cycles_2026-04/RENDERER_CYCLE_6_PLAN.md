# Renderer Cycle 6 Plan — Trilogy Act II escalation envelope (Patch J)

**Date**: 2026-04-29
**Source**: Cycle 5 후보 #5 (renderer_gate1_v6_samples.md §7) — Trilogy Act II 강조 mechanism
**Predecessor**: `RENDERER_CYCLE_5_PLAN.md` (Patch I — scene-level micro-action beat)
**Trigger**: Lee directive "Saturation에 도달해도 계속해서 Renderer 개선해" 지속.
**Lee v2 약점 추적**: "Trilogy Act I/II SAT 톤 차이를 더 벌려야" — Cycle 3 Patch F가 SAT outcome line 분리만 해결, *escalation 의미*는 미구현.

---

## 0. Cycle 6 motivation

### 0.1 Cycle 5 후 미해결 약점

Cycle 5 (Patch I) → scene-level micro-action 추가. Cycle 6 후보 5개 중 *작업 단가 작고 명확한 매핑* 우선.

| 후보 | 작업 단가 | 효과 | Cycle 6 결정 |
|---|---|---|---|
| named motif continuity | 큼 | 큰 coherence | Cycle 7 |
| **Trilogy Act II 강조** | **작음** | **sample-specific, Lee 명시 약점** | **선택 (Patch J)** |
| narrator distance | 큼 | 추상적 매핑 | Cycle 7+ |
| LOW_ACTIVITY × scenario | 작음 | 의도 충돌 가능 | skip |
| full omniscient → micro | 매우 큼 | architecture 변경 | skip (Cycle 5 additive로 부분 처리) |

### 0.2 Lee verbatim (재인용)

> "Trilogy modal 3-act: 구조 자체가 강하다. **Act I/II의 SAT 톤 차이는 더 벌려야 한다**." (Lee Gate 1 v2 §3)

Cycle 3 Patch F (5-line pool) → Act I/II가 다른 SAT scarcity outcome line 사용. 그러나 Act II의 *escalation 의미* (이미 한 번 떨어진 비난 위에 두 번째)가 narrative 본문에 *visible*하지 않음. epigraph만 있고 본문은 일반 SAT.

### 0.3 Patch J 전략

`scripts/story/generate_trilogy_view.py` *만* 수정. `render_story_ko.py` 무수정.

- Modal view에서 *Act II 본문 직전*에 escalation **preamble** (1-2 sentences) 삽입
- Modal view에서 *Act II 본문 직후*에 escalation **echo** (1 sentence) 삽입
- Act I + Act III는 변경 없음 — escalation 의미는 Act II에만 적용

---

## 1. Patch J — Act II escalation envelope

### 1.1 구현

```python
# Cycle 6 Patch J — Act II escalation envelope
ACT_II_PREAMBLE = (
    "(첫 비난의 굳음이 풀리지 않은 채, 두 번째 비난이 그 자리에 떨어졌다. "
    "사람들의 자세는 한 번이 아니라 두 번 멈춰 섰다.)"
)

ACT_II_ECHO = (
    "(같은 거리, 같은 자세, 그러나 두 번의 비난이 동시에 머물렀다. "
    "굳음은 한 결로 끝나지 않았다.)"
)
```

### 1.2 modal_lines 삽입 로직

기존 (Cycle 1-5):
```python
for anchor_id, act_title, signature in TRILOGY_ANCHORS:
    ...
    modal_lines.append(f"> {signature}")
    modal_lines.append("")
    modal_lines.append(narrative)
    modal_lines.append("")
    modal_lines.append("-" * 70)
```

Cycle 6 (Patch J):
```python
for anchor_id, act_title, signature in TRILOGY_ANCHORS:
    ...
    modal_lines.append(f"> {signature}")
    modal_lines.append("")
    # Patch J: Act II only — escalation preamble
    if anchor_id == "peter_scarcity_double":
        modal_lines.append(ACT_II_PREAMBLE)
        modal_lines.append("")
    modal_lines.append(narrative)
    modal_lines.append("")
    # Patch J: Act II only — escalation echo
    if anchor_id == "peter_scarcity_double":
        modal_lines.append(ACT_II_ECHO)
        modal_lines.append("")
    modal_lines.append("-" * 70)
```

### 1.3 효과

- Act II 본문 *진입 시* "두 번째 비난" 명시 — escalation 의미 visible
- Act II 본문 *종료 후* "두 번의 비난이 동시에 머물렀다" — accumulation 의미 visible
- Act I (한 번)과 Act III (세 번) 사이의 *깊어지는 굳음*이 narrative 구조에 반영
- 본문 자체는 변경 없음 (회귀 위험 zero)

### 1.4 Full view 처리

Full view (`scarcity_trilogy_full.txt`)는 5 seeds × 3 anchors 모두 표시 — modal envelope보다 *cross-seed 비교*가 목적. envelope 추가 시 noise 가중 — Full view는 *변경 없음*.

---

## 2. 검증

### 2.1 정량

| 지표 | Cycle 5 | Cycle 6 |
|---|---|---|
| Modal view 길이 | ~95 lines | ~99 lines (+4 lines for Act II envelope) |
| Full view | 변경 없음 | 변경 없음 |
| 96 narrative | 변경 없음 (render_story_ko.py 무수정) | 변경 없음 |
| test_story | 119 PASS | 119 PASS 유지 |
| forbidden audit | 96/96 clean | 96/96 clean (envelope은 모달뷰만 영향, generated/ 무관) |

### 2.2 정성

| Sample | Cycle 5 | Cycle 6 목표 |
|---|---|---|
| Trilogy Act I | epigraph + narrative | (변경 없음) |
| **Trilogy Act II** | **epigraph + narrative** | **epigraph + (NEW preamble) + narrative + (NEW echo)** |
| Trilogy Act III | epigraph + narrative | (변경 없음) |

---

## 3. HARNESS 자가감사 (H7)

- [x] **H1** Lee 평가 기준 trivial explanation 가능
- [x] **H2** 시도 안 한 대안: (a) Act II *본문* 자체 변경 (probe-aware mechanism, 너무 복잡), (b) Act II render_narrative 매개변수 추가 (architecture 변경)
- [x] **H3** Rule #1 verbatim — Cycle 6는 `scripts/story/generate_trilogy_view.py`만 수정
- [x] **H4** What could still be wrong: (i) parenthetical envelope이 narrative flow에 어색할 수 있음, (ii) "두 번째 비난" 강조가 Lee가 원했던 *깊이 차이*와 다를 수 있음 — Lee Gate 1 v3 평가가 falsification path
- [x] **H5** Lee verbatim "Act I/II 톤 차이를 더 벌려야" 보존
- [x] **H6** Lee가 "Act II envelope 멈춤" 가능 — frame-neutral
- [x] **H7** 이 doc — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음

---

## 4. 작업 순서

1. Patch J — `generate_trilogy_view.py`에 ACT_II_PREAMBLE + ACT_II_ECHO 정의 + modal_lines 삽입 로직
2. Trilogy 재생성
3. Act I/II/III 비교 검증 (Act II에 envelope 적용 확인)
4. before/after Cycle 5 → Cycle 6 diff doc
5. pytest test_story 119 PASS (영향 없어야 함)
6. progress + lessons L28

---

## 5. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1-4 | 2026-04-28~29 | dict 확장 패턴 (4 outcomes × 3 scenarios + LOW + opening) |
| Cycle 5 | 2026-04-29 | Patch I — scene-level micro-action beat (Stage 2.5) |
| **Cycle 6 (이 plan)** | **2026-04-29** | **Patch J — Trilogy Act II escalation envelope** |
| Cycle 7 후보 | TBD | named motif continuity / narrator distance |
