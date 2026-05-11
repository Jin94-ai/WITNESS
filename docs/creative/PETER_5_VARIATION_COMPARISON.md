# Peter Anchor 5 Variations — Side-by-Side Comparison

**Date**: 2026-04-28
**Purpose**: Lee Gate 2 (variation demo 판정) 직접 입력 보조. 5 variation 차이를 한 눈에.
**Source**: `outputs/creative_demo/peter_anchor_5_variations_ko.txt`

---

## 1. Anchor 정의

같은 시뮬레이션 입력으로 **seed만 다름**:
- Scenario: scarcity (Peter passion 환경 중 scarcity slice)
- Cast: 12 agents (merchant + 5 laborer + 가족 + authority + 2 enforcer + 2 crowd + outsider + elite_strategist)
- Placement: 곡물 창고 / 빈민가 / 시장 분산
- Events: 1 accusation against merchant @ t5, 1 guard_approaches @ t15
- Seeds: 0, 1, 2, 3, 4

---

## 2. Outcome 분포

| Seed | Final summary | 한 줄 톤 |
|---|---|---|
| 0 | SATURATION_DOMINATED | 굳었다 / 시간이 멈춘 듯 |
| 1 | RECOVERY_DOMINATED | 다시 일어섰다 / 어깨에서 무게가 풀렸다 |
| 2 | SATURATION_DOMINATED | 머물렀다 / 며칠이 지나도 자세는 같았다 |
| 3 | PARTIAL | 어중간한 자리 / 더 자라지도 풀리지도 않음 |
| 4 | RECOVERY_DOMINATED | 회복은 한꺼번에 오지 않았지만 / 분명히 다시 움직임 |

→ **3 distinct outcomes** (SAT × 2, REC × 2, PARTIAL × 1).

---

## 3. 5 variation 결말 paragraph 비교 (가장 분명한 차이 surface)

### Seed 0 (SATURATION)
> 사람들은 자리에 굳었다. 고백이 있었어도 무거움은 풀리지 않았고, 어떤 자리에서는 시간이 멈춘 것처럼 보였다. 같은 자세를 며칠 동안 유지하는 사람들의 모습이 거리에 남았다.

### Seed 1 (RECOVERY)
> 사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, 무거움은 조금씩 줄어들었다. 누가 먼저였는지는 분명하지 않았지만, 그 흐름은 거리 끝까지 닿았다.

### Seed 2 (SATURATION)
> 사람들은 자리에 굳었다. 고백이 있었어도 무거움은 풀리지 않았고, 어떤 자리에서는 시간이 멈춘 것처럼 보였다.

### Seed 3 (PARTIAL)
> 사람들은 일부만 흔들렸다. 큰 무너짐도, 분명한 회복도 보이지 않았다. 그 어중간한 자리에서 시간은 평소보다 느리게 흘렀고, 누구도 분명한 자세를 잡지 못한 채 다음 일이 무엇인지 짐작만 하고 있었다.

### Seed 4 (RECOVERY)
> 사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, 무거움은 조금씩 줄어들었다. 누가 먼저였는지는 분명하지 않았지만, 그 흐름은 거리 끝까지 닿았다.

→ **5 variation, 3 distinct narratives**.

---

## 4. 5 variation 마지막 sentence (ENDING_HOOK 차별화 검증)

Step A5 ending hook이 outcome별로 다른 *후크*를 부여:

| Seed | Outcome | Hook (J-Alpha 추가) |
|---|---|---|
| 0 | SAT | (variation pool에서 hash 선택) |
| 1 | REC | (variation pool) |
| 2 | SAT | (variation pool) |
| 3 | PARTIAL | (variation pool) |
| 4 | REC | (variation pool) |

각 ending hook은 outcome별 톤 보강:
- SAT hook 예: "그러나 그 굳음 안에서도 작은 떨림이 멈추지 않았다."
- REC hook 예: "다만 누구도 그 무거움이 정말 사라졌다고 확신하지는 못했다."
- PARTIAL hook 예: "분명한 끝이 오지 않은 채 시간은 한 걸음씩 흘렀다."

→ Lee가 outputs/creative_demo/peter_anchor_5_variations_ko.txt 끝부분 직접 확인 권장.

---

## 5. 같은 outcome 묶음 (seed 0+2 SAT, seed 1+4 REC) 차이는?

**Question**: seed 0과 2 둘 다 SAT인데 텍스트는 같은가?
**Answer**: 거의 같음 (variant_pick hash가 미세 차이만 부여). 핵심 차이는 *outcome 분기*에서 발생, *같은 outcome 안*에서는 거의 같음.

→ J-Alpha 시점에서 **outcome 다양성**은 입증됨. **outcome 안의 미세 variation**은 J-Beta에서 trace-level features 활용해 강화.

---

## 6. Lee Gate 2 직접 평가 항목

`outputs/creative_demo/peter_anchor_5_variations_ko.txt` 파일 직접 읽고:

### 6.1 5개가 정말 *다른* 이야기로 읽히는가?
- (YES / NO + 구체 이유)
- 같은 사건 (1 accusation against merchant @ t5)에서 출발해 **5 다른 결말**이 나오는 *서사적 의미*가 살아있는가?

### 6.2 IP 자산 가치
- 웹소설 anchor (예: "운명 변주 5선") 으로 쓸 수 있는가?
- 한 anchor에서 여러 결말이 나오는 게 *재미있는 narrative beat*인가?

### 6.3 가장 좋은 variation
- (Seed 0/1/2/3/4 + 이유)

### 6.4 가장 약한 variation
- (Seed 0/1/2/3/4 + 이유)

### 6.5 J-Beta 진행 가부
- 이 정도 quality에서 J-Beta 진행 가능?
- 아니면 J-Alpha 더 다듬어야 하는가?

---

## 7. 추가 고려사항

### 7.1 Seed 0 vs Seed 2 (둘 다 SAT) 거의 같음
**문제**: 같은 outcome 묶음은 텍스트 거의 같음.
**원인**: OUTCOME_POOLS가 outcome별 3 variant인데, hash collision으로 같은 selection 발생 가능.
**해결**: J-Beta에서 trace-level micro-features (cohort detail timing, blame propagation 패턴 등)를 IR atom으로 추가.

### 7.2 Seed 1 vs Seed 4 (둘 다 REC) 거의 같음
**같은 문제**. 같은 해결 방향.

### 7.3 Cross-seed 분리
- seed 0+2 (SAT) vs seed 1+4 (REC) vs seed 3 (PARTIAL): **3 묶음**
- 5 변주 효과는 *3 묶음 비교*에 있음. 묶음 안의 미세 차이는 J-Beta로.

---

## 8. Lee Gate 2 결정 옵션

| 옵션 | 의미 |
|---|---|
| (A) PASS — J-Beta 진행 | Peter anchor 5/6 + Lee 5+6 통과 → taxonomy 확장 / 70+ trajectory labeling / selector query API |
| (B) FAIL — Renderer 더 다듬기 | "outcome 안 미세 variation 부족" 문제 해결 후 재시도 |
| (C) PARTIAL PASS — Van Gogh 별도 작업 | Peter는 PASS, Van Gogh 진짜 simulator 별도 generator 작성 (별도 directive) |

Claude bias: **(A) 또는 (C)** 권장. (B)는 Peter PASS 무시하는 셈.

---

## 9. 다음 세션 시작 안내

1. 이 doc 읽고 Lee Gate 2 §6 답변
2. `outputs/creative_demo/peter_anchor_5_variations_ko.txt` 직접 읽고 Lee 직관 평가
3. PASS면 → J-Beta 시작 (별도 directive 또는 자율 진행)
4. FAIL면 → renderer 추가 cycle (Lee Gate 1 input 도착 후 RENDERER_DIAGNOSIS_ALPHA.md §3 카테고리 따라)

---

## 10. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | J-Alpha Gate 2 보조 doc. Lee 직접 평가 prep. |
