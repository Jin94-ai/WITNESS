# Renderer Cycle 5 Plan — scene-level micro-action beat (Patch I)

**Date**: 2026-04-29
**Source**: Cycle 5 후보 #1 (renderer_gate1_v5_samples.md §6) — scene-level local action beats (omniscient → micro)
**Predecessor**: `RENDERER_CYCLE_4_PLAN.md` (Patch G/H — accusation REC sharpness + PARTIAL × scenario)
**Trigger**: Lee directive "Saturation에 도달해도 계속해서 Renderer 개선해" 지속.

---

## 0. Cycle 5 motivation

### 0.1 Cycle 1-4 마무리 = dict 확장 패턴 종료

Cycle 1-4 누적:
- 4 outcomes (REC/SAT/MIXED/PARTIAL) × 3 scenarios = 12 pools 모두 채워짐
- LOW_ACTIVITY 전용 5-stage branch
- OPENING accusation/sacred 6 / scarcity 5 / low 2 / other 2

→ *dict 확장 패턴*은 자연 종료. 다음 Cycle은 *architecture 변경*.

### 0.2 Cycle 5 후보 5개 중 우선순위

| # | 후보 | 작업 단가 | 효과 | Cycle 5 결정 |
|---|---|---|---|---|
| 1 | scene-level micro-action beats | 중간 | **큰 narrative depth** | **선택** |
| 2 | named motif continuity | 큼 | 큰 coherence | Cycle 6 |
| 3 | LOW_ACTIVITY × scenario | 작음 | "부재의 긴장" 의도와 충돌 가능 | skip |
| 4 | narrator distance control | 큼 | 추상적, 매핑 어려움 | Cycle 6+ |
| 5 | Trilogy Act II 강조 | 작음 | sample-specific만 | Cycle 6 |

### 0.3 Lee 의도 (renderer_gate1_v3_samples.md §6.1 Cycle 4 후보 §6 Cycle 5 후보)

> "scene-level local action beats (단일 인물의 미시 행동)"

= 현재 모든 narrative가 *omniscient observer* perspective ("사람들은 자리에 굳었다" / "거리는 평소처럼 흘렀다"). Lee 의도 = *concrete individual action* ("한 사람이 손을 들었다", "두 발걸음이 한쪽으로 향했다") 추가하여 narrative depth 강화.

---

## 1. Patch I — scene-level micro-action beat

### 1.1 전략

**완전 omniscient → micro 전환은 큰 architecture 변경**. Cycle 5는 *additive*: 기존 omniscient 구조 유지하면서 *Stage 2.5* (Stage 2 pressure 후 ↔ Stage 3 response 전)에 *작은 micro-action sentence* 1개 삽입.

### 1.2 효과

- 추상 (omniscient) → 구체 (concrete individual) 전환
- pressure에서 response로 넘어가는 *transition*이 *visible body action*으로 표현됨
- narrative depth 증가 (현재 ~900자 → ~950자 예상)

### 1.3 구현

```python
# Cycle 5 Patch I: scene-level micro-action beats (추가 stage 2.5)
SCENARIO_MICRO_ACTION_POOLS = {
    "scarcity": [
        "한 사람이 자기 손을 잠시 내려다보았다가, 다시 거리 쪽으로 들어 올렸다.",
        "두 발걸음이 시장 쪽으로 향하다가 한 박자 늦게 멈췄다.",
        "누군가 자루의 매듭을 만지작거리다가 다시 손을 내려놓았다.",
        "한 사람이 거리 끝쪽을 한참 바라보다가 천천히 고개를 돌렸다.",
        "자루를 들었던 손이 한 박자 흔들리다가 다시 자리를 잡았다.",
    ],
    "accusation": [
        "한 사람의 눈이 평소보다 길게 한 자리에 머물렀다.",
        "두어 걸음이 한쪽으로 향하다가 한 박자 늦게 다른 쪽으로 옮겨 갔다.",
        "한 사람이 손을 들려다 멈추고, 그 손을 천천히 내려놓았다.",
        "누군가의 시선이 한 사람의 얼굴에서 떨어지지 않았다. 그 시선은 거두어지지 않았다.",
        "한 사람의 발걸음이 광장 한가운데에서 한 박자 머뭇거렸다.",
    ],
    "sacred": [
        "한 사람이 무릎을 꿇으려다, 다시 자세를 잡았다.",
        "두 손이 마주잡혔다가 천천히 풀렸다.",
        "한 사람의 시선이 성전 쪽을 향하다가 다시 거리 쪽으로 돌아왔다.",
        "누군가 입을 열려다 그대로 닫았다. 그 침묵이 거리까지 닿았다.",
        "한 사람이 한 걸음 앞으로 나아갔다가, 그 자리에 다시 멈춰 섰다.",
    ],
}


def _micro_action(probe_id: str, pressure_type: str) -> str:
    """Cycle 5 Patch I: scene-level micro-action beat."""
    pool = SCENARIO_MICRO_ACTION_POOLS.get(pressure_type)
    if not pool:
        return ""
    return variant_pick(probe_id, f"micro_action_{pressure_type}", pool)
```

### 1.4 render_narrative() 통합

Stage 2.5 위치 — Stage 2 (pressure_arc 끝) 직후 + transition_to_response 직전:

```python
# Stage 2: 압력 상승
s2 = _initial_tension(ir["initial_tension"]) + " " + _pressure_arc(ir["pressure_arc"], pressure_type)

# Cycle 5 Patch I — Stage 2.5: scene-level micro-action beat
micro = _micro_action(pid, pressure_type)
if micro:
    s2 = s2 + " " + micro

# (existing) s2_with_transition = s2 + " " + variant_pick(pid, "transition_to_response", TRANSITION_TO_RESPONSE)
```

이렇게 하면 Stage 2 끝부분에 *concrete individual action*이 삽입되어 omniscient 흐름 안에서 *zoom-in moment*가 생김.

### 1.5 LOW_ACTIVITY 처리

LOW_ACTIVITY는 별도 branch (`_render_narrative_low_activity()`)이므로 Patch I 영향 없음. LOW_ACTIVITY는 자체적으로 micro-action 형태의 sign 이미 포함 ("누군가 무엇인가를 말하려다 입을 다물었다") — 재처리 불필요.

---

## 2. 검증

### 2.1 정량

| 지표 | Cycle 4 | Cycle 5 목표 |
|---|---|---|
| 5 sample 평균 narrative 길이 | ~960자 | ~1010자 (+1 sentence per non-LOW probe) |
| micro-action 등장 (non-LOW probes) | 0 | 1 per probe |
| test_story | 119 PASS | 119 PASS 유지 |
| forbidden audit | 96/96 clean | 96/96 clean 유지 |

### 2.2 정성

| Sample | Cycle 4 | Cycle 5 목표 |
|---|---|---|
| P6 MIXED scarcity | omniscient throughout | + 자루/시장 micro-action |
| P9 SAT scarcity | 시간 정지 + 자루 그대로 | + 손/자루 manipulation micro-action |
| P10 REC accusation | sharpness coexistence (Cycle 4) | + 시선/걸음 micro-action |
| P_PV_09 LOW_ACTIVITY | 부재의 긴장 5 stage | (변경 없음 — LOW branch separate) |
| P_CV_01 MIXED accusation | accusation MIXED tone | + 광장 micro-action |

---

## 3. HARNESS 자가감사 (H7)

- [x] **H1** Lee 평가 기준 trivial explanation 가능
- [x] **H2** 시도 안 한 대안: (a) full omniscient → micro 전환 (architecture 변경, 너무 큼), (b) named motif coordinated pool (Cycle 6), (c) narrator distance (Cycle 6+)
- [x] **H3** Rule #1 verbatim — Cycle 5는 `scripts/story/`만 수정
- [x] **H4** What could still be wrong: (i) micro-action sentence가 omniscient 문맥과 부조화, (ii) 1 sentence 추가만으로 "depth" 효과 작을 수 있음 — Lee Gate 1 v3 평가가 falsification path
- [x] **H5** Lee verbatim "scene-level local action beats" 보존
- [x] **H6** Lee가 "Cycle 5 멈춤 / 다른 후보 우선" 가능 — frame-neutral
- [x] **H7** 이 doc — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음

---

## 4. 작업 순서

1. Patch I — SCENARIO_MICRO_ACTION_POOLS 신설 + `_micro_action()` helper
2. render_narrative() Stage 2.5 삽입
3. 5 sample + 96 narrative 재생성 (--all + --branch-c) + Trilogy + anchor variations
4. forbidden audit 96/96 clean
5. before/after Cycle 4 → Cycle 5 diff doc
6. pytest test_story 119 PASS
7. progress + lessons L27

---

## 5. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 | 2026-04-28 | scarcity opening + cross-scenario REC + anchor signature |
| Cycle 2 | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY branch |
| Cycle 3 | 2026-04-29 | Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion |
| Cycle 4 | 2026-04-29 | Patch G/H — accusation REC sharpness + PARTIAL × scenario (대칭성) |
| **Cycle 5 (이 plan)** | **2026-04-29** | **Patch I — scene-level micro-action beat (additive Stage 2.5)** |
| Cycle 6 후보 | TBD | named motif / Trilogy Act II / narrator distance / LOW × scenario |
