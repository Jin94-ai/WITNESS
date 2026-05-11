# Renderer Cycle 7 Plan — primary motif + closing line (Patch K)

**Date**: 2026-04-29
**Source**: Cycle 7 후보 #1 (RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md §5) — named motif continuity. *작은 implementation* 형태로 진행 (over-engineering 회피).
**Predecessor**: Cycle 6 Patch J (Trilogy Act II envelope), Retrospective doc
**Trigger**: Lee directive "Saturation에 도달해도 계속해서 Renderer 개선해" (Type D) 지속.

---

## 0. Cycle 7 motivation

### 0.1 Cycle 7는 Lee 미명시 영역 — over-engineering 위험 인지

Cycle 1-6 = Lee 명시 약점 5/5 + Cycle 5 후보 직접 대응.
Cycle 7 = Lee 미명시 자율 식별 후보 (named motif continuity).

over-engineering 위험 처리:
1. **작은 patch만** — 큰 architecture 변경 (coordinated pool selection 등) 회피
2. **additive only** — 기존 stages/pools 보존
3. **명시적 falsification path** — Lee Gate 1 v3 평가에서 *motif가 도움 안 됨*이면 즉시 rollback 가능
4. **scope cap** — Cycle 7 단일 Patch K. Cycle 8+로 확장 안 함.

### 0.2 Named motif 의도

현재 narrative coherence:
- Opening (e.g., "곡식이 비어 가는 계절...")
- Pressure (e.g., "상인의 이름이 처음 입에 올랐다")
- Outcome (scenario × outcome pool, e.g., "곡물 창고의 문은 닫힌 채")
- Aftereffect (authority + shame residue)

각 stage가 *독립적*으로 hash 선택 → motif coherence는 *우연에 의존*. 즉 한 narrative 안에 "곡물 창고" 모티프와 "시장 가격" 모티프가 혼재 가능 — 통일성 약함.

### 0.3 Patch K 전략 (작은)

*전 narrative motif coordination*은 큰 작업. 대신 **narrative *마지막* 1 sentence**에 motif coherence 추가 — 5 stages 끝난 후 *motif ring*을 닫는 closing line.

- Probe별 *primary motif* hash로 결정
- narrative 끝 (aftereffect 후) 1 sentence 추가:
  - scarcity → "곡식의 무게는 거리의 결과 함께 한동안 머물렀다."
  - accusation → "한 번 떨어진 이름의 자국은 거리 위에 그대로였다."
  - sacred → "성전 쪽으로 향했던 시선의 결은 다음 시각까지 옅게 남았다."

이 closing line은 *primary motif*를 *narrative 전체의 마지막 잔향*으로 명시 — coherence ring 효과.

---

## 1. Patch K 구현

### 1.1 SCENARIO_MOTIF_CLOSING_POOLS

```python
SCENARIO_MOTIF_CLOSING_POOLS = {
    "scarcity": [
        "곡식의 무게는 거리의 결과 함께 한동안 머물렀다.",
        "시장의 결은 다음 시각으로 천천히 옮겨 갔지만, 그 결의 흔적은 옅게라도 남았다.",
        "곡물 창고를 향한 시선이 거두어진 후에도, 그 시선이 머물렀던 자리는 평소와 같지 않았다.",
        "자루의 무게는 누구의 손에서도 완전히 풀리지 않았다.",
        "빈손과 찬손 사이의 결은 다음 며칠을 천천히 흘러갔다.",
    ],
    "accusation": [
        "한 번 떨어진 이름의 자국은 거리 위에 그대로였다.",
        "손가락이 향했던 방향의 결은 다음 시각까지 옅게라도 남았다.",
        "광장의 시선이 다시 평소의 결을 찾은 후에도, 그 시선이 한 번 모였던 자리는 평소와 같지 않았다.",
        "이름의 무게는 거두어지지 않은 채 거리의 결과 함께 흘러갔다.",
        "관청 안마당의 그림자가 옮겨 간 후에도, 그 그림자의 결은 거리 위에 잠시 머물렀다.",
    ],
    "sacred": [
        "성전 쪽으로 향했던 시선의 결은 다음 시각까지 옅게 남았다.",
        "기도 소리가 거두어진 후에도, 그 소리가 머물렀던 자리는 평소와 같지 않았다.",
        "성전 바깥뜰의 자리는 모임이 흩어진 후에도 그 결을 잠시 지녔다.",
        "침묵의 결은 거리의 결과 함께 다음 시각으로 흘러갔다.",
        "기도와 의심이 한 자리에 깊었던 시간은 거리 위에 옅게라도 남았다.",
    ],
}


def _motif_closing(probe_id: str, pressure_type: str) -> str:
    """Cycle 7 Patch K: probe별 primary motif closing line — narrative coherence ring."""
    pool = SCENARIO_MOTIF_CLOSING_POOLS.get(pressure_type)
    if not pool:
        return ""
    return variant_pick(probe_id, f"motif_closing_{pressure_type}", pool)
```

### 1.2 render_narrative() 통합

기존 (Cycle 6):
```python
paragraphs = [s1]
paragraphs.append(s2_with_transition)
paragraphs.append(s3_with_transition)
paragraphs.append(s4_with_transition)
paragraphs.append(s5)  # Stage 5: 사후 세계
return "\n\n".join(p for p in paragraphs if p.strip())
```

Cycle 7 (Patch K):
```python
paragraphs = [s1]
paragraphs.append(s2_with_transition)
paragraphs.append(s3_with_transition)
paragraphs.append(s4_with_transition)
paragraphs.append(s5)
# Cycle 7 Patch K — Stage 6: motif coherence ring (narrative 마지막 잔향)
motif_closing = _motif_closing(pid, pressure_type)
if motif_closing:
    paragraphs.append(motif_closing)
return "\n\n".join(p for p in paragraphs if p.strip())
```

### 1.3 LOW_ACTIVITY 처리

LOW_ACTIVITY는 별도 branch — "사건이 되지 못한" 의미라 motif coherence가 적합하지 않음. Patch K skip.

### 1.4 render_summary() 처리

Summary는 짧은 버전 (~600자). Closing line 추가 시 비율 변동 큼. Summary는 *변경 없음*.

---

## 2. 검증

### 2.1 정량

| 지표 | Cycle 6 | Cycle 7 목표 |
|---|---|---|
| 5 sample 평균 narrative 길이 | ~990자 | ~1030자 (+40자 / 1 sentence) |
| motif closing line 등장 (non-LOW probes) | 0 | 1 per probe |
| test_story | 119 PASS | 119 PASS 유지 |
| forbidden audit | 96/96 clean | 96/96 clean 유지 |

### 2.2 정성

| Sample | Cycle 6 | Cycle 7 목표 |
|---|---|---|
| P6 MIXED scarcity | aftereffect 마지막 stage 종료 | + 곡식/시장 motif closing |
| P9 SAT scarcity | aftereffect 끝 | + 자루/창고 motif closing |
| P10 REC accusation | aftereffect 끝 | + 이름/손가락 motif closing |
| P_PV_09 LOW_ACTIVITY | (변경 없음) | (변경 없음 — LOW branch separate) |

---

## 3. HARNESS 자가감사 (H7)

- [x] **H1** Lee 평가 기준 trivial explanation 가능
- [x] **H2** 시도 안 한 대안: (a) full coordinated motif (모든 stage motif 통일), (b) named motif tagging in pools (큰 작업), (c) narrator distance (Cycle 8+)
- [x] **H3** Rule #1 verbatim — Cycle 7는 `scripts/story/render_story_ko.py`만 수정
- [x] **H4** What could still be wrong:
  - (i) **over-engineering**: Lee 미명시 영역 — Lee 평가에서 *motif closing 불필요*이면 rollback
  - (ii) closing line이 narrative 흐름과 부조화 가능
  - (iii) 1 sentence만으로 *coherence ring* 효과가 약할 수 있음
  - → Lee Gate 1 v3 평가가 falsification path
- [x] **H5** Lee verbatim "renderer 개선" directive — *명시 약점 saturation 후의 자율 영역*임을 인지
- [x] **H6** Lee가 "Cycle 7 closing line 불필요"라 평가 시 즉시 rollback 가능 (단일 patch이라 회복 쉬움)
- [x] **H7** 이 doc — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음

---

## 4. Rollback path

Patch K는 *additive only*이므로 rollback 단순:
1. `SCENARIO_MOTIF_CLOSING_POOLS` 정의 제거
2. `_motif_closing()` 함수 제거
3. `render_narrative()`의 마지막 paragraph append 제거
4. 96 narrative 재생성

Lee가 "motif closing 부조화"라고 평가 시 즉시 rollback. 회귀 위험 ZERO (additive only).

---

## 5. 작업 순서

1. Patch K — `SCENARIO_MOTIF_CLOSING_POOLS` 신설 + `_motif_closing()` helper
2. render_narrative() 마지막 paragraph append
3. 96 narrative 재생성 + Trilogy + anchor variations
4. forbidden audit 96/96 clean
5. before/after Cycle 6 → Cycle 7 diff doc (`renderer_gate1_v8_samples.md`)
6. pytest test_story 119 PASS
7. progress + lessons L29

---

## 6. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1-4 | 2026-04-28~29 | dict 확장 패턴 (4 outcomes × 3 scenarios + LOW + opening) |
| Cycle 5 | 2026-04-29 | Patch I — scene-level micro-action (Stage 2.5) |
| Cycle 6 | 2026-04-29 | Patch J — Trilogy Act II escalation envelope (sample-specific meta) |
| Retrospective | 2026-04-29 | Cycles 1-6 통합 review |
| **Cycle 7 (이 plan)** | **2026-04-29** | **Patch K — primary motif closing line (coherence ring, Lee 미명시 over-engineering 위험 명시 후 진행)** |
| Cycle 8 후보 | TBD | 미정 — Lee 평가 결과에 따라 |
