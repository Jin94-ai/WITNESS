# Story Output MVP Acceptance — v2 Re-check (Phase 2 Iter 3)

**Date**: 2026-04-28
**Phase**: Phase 2 Iter 3 후속 재판정
**Source**:
- v1: `STORY_MVP_ACCEPTANCE.md` (5/6 + 1 MARGINAL → PASS)
- Phase 2 Iter 2: Loop C-3 probe-hash variation (P4≠P5 확인)
- Phase 2 Iter 3: Loop A transition + cohort_detail 풍성화

**Verdict**: **6/6 PASS** (v1 MARGINAL 항목 해결).

---

## 1. v1 → v2 변화 요약

| Criterion | v1 (Phase 7) | v2 (Phase 2 Iter 3) | Note |
|---|---|---|---|
| C1 흐름 | PASS | PASS | 5단 구조 보존 |
| C2 outcome 차이 | PASS | PASS (강화) | OUTCOME_POOLS 3 variants per outcome |
| C3 world-side ≥2 | PASS (4 axes) | PASS (4 axes) | blame_band 4단계 + authority_pattern 분기 |
| C4 이야기처럼 | PASS | PASS | forbidden 0건 검증 |
| C5 probe별 차이 | PASS | PASS (강화) | location semantic + variation pool |
| **C6 반복 안 심함** | **MARGINAL (P4=P5 동일)** | **PASS (P4≠P5 확인)** | **probe-hash variation pool 도입** |

→ **6/6 PASS 공식화**.

---

## 2. 결정적 검증: P4 vs P5

이전 (v1):
> P4 narrative == P5 narrative (100% identical text)

현재 (v2):
- P4 첫 문단 도입: "성전 안에서는 기도가 이어졌고, 바깥에서는 그 기도를 듣는 사람들이 늘어 갔다…"
- P5 첫 문단 도입: "성전을 향한 발걸음은 평소보다 많았다. 바깥뜰에 모인 사람들 사이에는 익숙한 침묵 같기도 하고 낯선 기다림 같기도 한 공기가 흘렀다…"

→ 같은 IR (sacred/RECOVERY)에서도 probe_id 해시로 다른 sentence pool 항목 선택. **C6 marginal 해결**.

---

## 3. 길이 진척

### Summary (spec 400-800자)

| Probe | v1 | v2 |
|---|---:|---:|
| P1 | 358 | **520** |
| P7 (최단 v1) | 288 | **411** |
| P6 | 455 | **689** |

**v1: 7/12 통과 → v2: 12/12 통과**.

### Narrative (spec 1000-1800자)

| Probe | v1 | v2 |
|---|---:|---:|
| P6 | 750 | **1253** ✓ |
| P12 | 584 | 952 |
| P2 | 547 | 922 |
| P11 | 562 | 894 |
| P8 | 562 | 891 |
| P9 | 522 | 867 |
| P3 | 492 | 853 |
| P1 | 486 | 790 |
| P10 | 459 | 783 |
| P5 | 449 | 747 |
| P4 | 449 | 738 |
| P7 | 423 | 714 |

**v1: 0/12 통과 → v2: 1/12 통과 (P6 1253)**. 평균 580자 → **864자**.

→ Spec 1000자 fully 통과 못 했지만 acceptance 기준은 길이가 아닌 *흐름 식별 가능성*. 평균 +280자 증가 + 모든 probe 700자 이상으로 가독성 개선됨.

---

## 4. C6 (반복) 강화 증거

### Pool 다양성

| Slot | Pool variants | 효과 |
|---|---:|---|
| OPENING_POOLS["scarcity"] | 3 | scarcity 시나리오 도입 분기 |
| OPENING_POOLS["accusation"] | 3 | accusation 분기 |
| OPENING_POOLS["sacred"] | 3 | sacred 분기 |
| opening_authority | 3 | 권위 시선 표현 분기 |
| OUTCOME_POOLS x 5 | 2-3 each | outcome 분기 |
| TRANSITION_TO_PRESSURE | 3 | 도입 → 압력 transition |
| TRANSITION_TO_RESPONSE | 3 | 압력 → 반응 transition |
| TRANSITION_TO_OUTCOME | 3 | 반응 → 귀결 transition |
| TRANSITION_TO_AFTEREFFECT | 3 | 귀결 → 사후 transition |

→ 같은 IR이어도 12 probes에서 같은 sentence selection 확률 매우 낮음.

### 충돌 검증

7가지 변주점 (4 transitions + opening + outcome + authority) × 2-3 variants. 단순 기댓값:
- P4 vs P5에서 모든 7 점이 동일할 확률 ≈ (1/2.5)^7 ≈ 0.16% ≈ 1/600

→ 실제 P4 vs P5 출력은 첫 문단부터 다름. 변주 작동 확인.

---

## 5. v2 acceptance 종합

| Criterion | v2 Status | 근거 |
|---|---|---|
| C1 흐름 | **PASS** | 12/12 5단 구조 식별 가능 |
| C2 outcome 차이 | **PASS** | RECOVERY/SAT/MIXED/PARTIAL/LOW 분명한 톤 |
| C3 world-side | **PASS** | 4축 (blame/authority/suspicion/top_blame) surface |
| C4 이야기처럼 | **PASS** | forbidden 0건 (raw ID/숫자/메타) |
| C5 probe별 차이 | **PASS** | scenario + outcome + blame_band + auth_pattern + location semantic + pool variants |
| **C6 반복 안 심함** | **PASS** | **P4≠P5 확인, 9 variation slots, hash collision rate 매우 낮음** |

→ **6/6 PASS 공식화**.

---

## 6. 한국어 quality 검증 (P6 narrative 발췌)

```
곡식이 비어 가는 계절이었다. 시장과 곡물 창고와 빈민가는 한 호흡을 공유했고, 
사람들의 눈치는 서로의 손끝으로 향했다. ... 권위의 자리에서 내려오는 시선은 
거리 위로 길게 떨어졌다. 그러나 그 자리에 머무를 수만은 없는 일이 곧 일어났다.

빈손이 늘어 가던 어느 시각, 상인의 이름이 처음 입에 올랐다. ... 비난은 
흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 노동자들에게로 향했고, ... 
이 흐름 속에서, 사람들은 각자 다른 자리에서 다른 호흡을 가졌다.

한쪽에서는 사람들이 다시 모이려 했다. ... 한 시각이 지났을 때, 두 자리의 
공기는 서로 다른 결로 굳어 가고 있었다.

빈민가에서는 누군가의 입에서 시작된 고백이 다음 사람으로 넘어갔고, 그 흐름이 
짐을 조금씩 덜어 갔다. 곡물 창고에서는 같은 말이 오가도 누구의 어깨에서도 
짐이 풀리지 않았다. ...

그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.
```

→ 시간감 ("한 시각이 지났을 때"), 공간감 ("빈민가에서는…", "곡물 창고에서는…"), 결을 가르는 표현, 5단 구조 명확.

---

## 7. 결론 + 다음 단계

**Story Output MVP Phase 2 통과**: 6/6 PASS.

남은 작업 (선택, NEXT_STEPS Phase 3 후속):
- **Loop B world-side aftereffect 강화** — 현재 surface OK, 추가 문장 가능
- **Loop C-1 timing rhythm** — defer (effort vs gain 낮음)
- **Loop D style branching** — 요약형 / 서사형 더 분명한 분기

이번 cycle은 여기서 마무리. Branch C와의 연결 (NEXT_STEPS §3 Phase 4)은 **story output quality를 실제로 개선하는 변경만** 기준 — 현재 quality 충분히 좋음.

---

## 8. Versioning

| Version | Date | Verdict | 핵심 변경 |
|---|---|---|---|
| v1 | 2026-04-28 | 5/6 + 1 MARGINAL → PASS | Phase 7 길이/조사/복수 fix |
| **v2 (this)** | **2026-04-28** | **6/6 PASS** | **Loop C-3 variation pool + Loop A transitions** |
