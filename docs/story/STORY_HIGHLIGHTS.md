# Story Highlights — 48 Stories Curated Showcase

**Date**: 2026-04-28
**Phase**: Phase 4 follow-up — Lee가 직접 읽고 평가할 수 있게 인상적 케이스 큐레이션
**Source**: 12 baseline (P1-P12) + 36 Branch C (P_PV/P_CV/P_ED/P_S2)
**Total**: 48 narratives, 평균 803자

---

## 0. 사용법

이 문서는 Lee가 한 번에 **이야기 출력의 가장 중요한 케이스**를 읽고 evaluate하기 위함.
각 highlight은 1-2 문단 인용 + WHY 설명.

읽는 권장 순서: §1 → §3 → §5 → §6 (HIGHLIGHT만 본 뒤 §2 / §4는 비교 reference).

---

## 1. ⭐ HIGHLIGHT 1: P6 — MIXED scarcity (가장 풍부, 1253자)

**왜 이 케이스가 중요한가**: Configuration sensitivity의 가장 좋은 예. **같은 사건 (1 accusation against merchant) 아래에서 cohort split** — 한쪽은 회복, 한쪽은 굳음. Branch C 1차 evidence의 핵심 발견 ("MIXED outcome = 두 결의 시간이 동시에 흐른다")가 글에서 분명히 surface.

발췌:
> 빈손이 늘어 가던 어느 시각, 상인의 이름이 처음 입에 올랐다. 누군가 곡식을 숨겼다는 말이 시장 한구석에서 시작되었고, 그 말은 오래 걸리지 않아 거리 끝까지 닿았다.
>
> ... 비난은 흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 노동자들에게로 향했고, 다른 곳을 보던 사람도 결국 그 방향을 따라 고개를 돌렸다.
>
> ... 빈민가에서는 누군가의 입에서 시작된 고백이 다음 사람으로 넘어갔고, 그 흐름이 짐을 조금씩 덜어 갔다. 곡물 창고에서는 같은 말이 오가도 누구의 어깨에서도 짐이 풀리지 않았다. 두 자리는 가까이 있었지만, 다른 결의 시간이 흘렀다.

**핵심 표현**: "빈민가에서는… 곡물 창고에서는…" — 위치 의미 (D-1 location semantic) 작동. 두 cohort의 다른 결이 한 문장에 동시 surface.

**Story 전체 파일**: `docs/story/generated/P6_narrative_ko.txt`

---

## 2. ⭐ HIGHLIGHT 2: P_PV_09 — LOW_ACTIVITY (rare 1/48)

**왜 중요한가**: Branch C 1차 evidence에서 **유일하게 발견된 LOW_ACTIVITY case** (sacred + clustered placement, 모든 agents가 temple_inner에 모인 케이스). "사건이 시작되지 않은 시간"이 글로 남는가?

발췌:
> 특별한 일이 없는 날이었다. 사람들의 발걸음은 일상의 무게로 흘렀고, 거리에는 익숙한 소리만 남았다.
>
> 큰 사건은 없었다. 다만 작은 마찰들이 거리를 따라 가볍게 움직였고, 그 외에는 아무것도 멈추거나 시작되지 않았다.
>
> 큰 변화는 없었다. 사건이라 부를 만한 일도 없이, 시간은 흘러갔다.

**핵심 표현**: "특별한 일이 없는" / "큰 사건은 없었다" / "시간은 흘러갔다" — placement clustering이 만들어 낸 *비-사건성*이 톤으로 보존됨.

**Story 전체 파일**: `docs/story/generated/P_PV_09_narrative_ko.txt`

---

## 3. ⭐ HIGHLIGHT 3: P_PV_01 vs P_PV_02 — Placement reversal (Branch C 핵심 finding)

**왜 중요한가**: 같은 accusation, 같은 cast, **단지 placement만 inverted** → 결말이 정반대 (RECOVERY ↔ SATURATION).

### P_PV_01 (RECOVERY) 도입:
> 그 자리에 서 있던 사람들은 알고 있었다. 무언가가 곧 시작될 것이라는 것을.
>
> ... 한 사람이 제자를 가리켰다. 그것은 작게 시작되었지만, 분명한 손가락질이었다.
>
> ... 비난은 흩어지지 않고 한 방향으로 모였다. (이후 회복 진행)

### P_PV_02 (SATURATION) 도입:
> 공기는 이미 무거웠다. 광장과 관청 안마당과 좁은 거리 사이로 의심이 흐르고 있었고, 사람들은 그 흐름을 보지 않으려 애썼지만 보지 않을 수 없었다.
>
> ... 한 사람이 제자를 가리켰다. 그것은 작게 시작되었지만, 분명한 손가락질이었다.
>
> ... 비난은 옅게라도 거리에 떠다녔다. 분명한 손가락질은 아니었지만, 누구도 그 흐름을 모르지는 않았다. (이후 굳음 진행)

**대비**: 같은 첫 사건 ("한 사람이 제자를 가리켰다")이지만 **이후 분기가 정반대**. 공간 배치가 결을 바꾼다는 Branch C 1차 evidence가 글로 보존.

---

## 4. ⭐ HIGHLIGHT 4: P_S2_05 vs P_S2_08 — Nonmonotonic (event count)

**왜 중요한가**: Branch C에서 발견된 **nonmonotonic** finding ("triple accusations → RECOVERY"). 같은 시나리오 (scarcity, baseline crowd density), **단지 accusation 횟수만 1→3** 증가했는데 결말이 SATURATION → RECOVERY로 *역전*.

### P_S2_05 (double, SATURATION) 4단:
> 사람들은 자리에 굳었다. 고백이 있었어도 무거움은 풀리지 않았고, 어떤 자리에서는 시간이 멈춘 것처럼 보였다. 같은 자세를 며칠 동안 유지하는 사람들의 모습이 거리에 남았다.
>
> 사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다.

### P_S2_08 (triple, RECOVERY) 4단:
> 사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, 무거움은 조금씩 줄어들었다. 누가 먼저였는지는 분명하지 않았지만, 그 흐름은 거리 끝까지 닿았다.
>
> 흔들림은 가라앉았다. 누가 먼저랄 것도 없이 사람들의 어깨에서 무게가 풀렸다.

**대비**: "굳었다 / 자리에 머물렀다 / 시간이 멈춘 것처럼" vs "다시 자리를 잡았다 / 흔들림은 가라앉았다 / 어깨에서 무게가 풀렸다". **이야기 톤이 정확히 반대**.

→ Branch C가 만든 *반직관적* 발견 (더 많은 사건이 더 깊은 굳음을 만드는 게 아님)이 글로 surface.

---

## 5. ⭐ HIGHLIGHT 5: P12 — SATURATION sacred (가장 무거운 sacred 케이스)

**왜 중요한가**: Sacred 시나리오에서도 saturation이 가능함을 보여 줌 (보통 sacred는 RECOVERY-경향). P12는 sacred + 미세 cast 차이로 **신성한 자리에서도 무거움이 풀리지 않은 경우**.

발췌 (사후 단락):
> 사건이 끝난 자리에는 무언가가 남았다.
>
> 의심은 거리 위에 짙게 남았고, 며칠이 지나도 가벼워지지 않았다. 사람들의 인사는 짧아졌고, 시선은 더 빨리 비켜갔다. 권위의 시선도 거두어지지 않았다.

**핵심 표현**: 사후 잔존 (residue)이 multi-line으로 surface — 의심 / 권위 / 비난 모두 떠나지 않음.

**Story 전체 파일**: `docs/story/generated/P12_narrative_ko.txt`

---

## 6. ⭐ HIGHLIGHT 6: P_S2_01 — Recovery via low density (조건부 회복)

**왜 중요한가**: Branch C S2의 또 다른 발견 — **single accusation + low crowd density → RECOVERY**. 군중이 희박하면 비난이 propagate되지 않아 회복이 가능. Engine state surface gap이 잘 작동.

발췌:
> 빈손이 늘어 가던 어느 시각, 상인의 이름이 처음 입에 올랐다.
>
> 사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, 무거움은 조금씩 줄어들었다. 누가 먼저였는지는 분명하지 않았지만, 그 흐름은 거리 끝까지 닿았다.

**같은 시나리오의 SATURATION (P_S2_02 baseline density)와 직접 대비** 가능.

---

## 7. 통계 + 패턴

### 7.1 Outcome 분포 (48 stories)

| Outcome | N | 톤 시작 단어 |
|---|---:|---|
| RECOVERY_DOMINATED | 16 | "다시 일어섰다", "흔들림은 가라앉았다", "회복은 한꺼번에 오지 않았지만" |
| SATURATION_DOMINATED | 13 | "자리에 머물렀다", "그곳에서 움직이지 않았다", "무거움은 자리를 차지한 채" |
| MIXED | 5 | "한쪽은 회복했고 다른 쪽은 굳었다", "결은 둘로 갈렸다" |
| PARTIAL | 13 | "어딘가에서 멈춰 있었다", "어중간한 시간", "분명한 끝은 보이지 않았다" |
| LOW_ACTIVITY | 1 | "특별한 일이 없는 날이었다" |

### 7.2 시나리오별 다양성

| 시나리오 | 가장 인상적 케이스 |
|---|---|
| Scarcity | P6 (MIXED), P_S2_05/P_S2_08 (nonmonotonic pair) |
| Accusation | P_PV_01/P_PV_02 (placement reversal) |
| Sacred | P_PV_09 (LOW_ACTIVITY), P12 (SAT 희귀) |

### 7.3 길이 (Narrative)

- 가장 김: P6 1253자
- 가장 짧: P_PV_09 529자 (LOW_ACTIVITY는 자연스럽게 짧음)
- 평균: 803자

---

## 8. Lee를 위한 quick check

Story 출력의 *현재 상태*를 한 번에 보고 싶다면:

1. **P6** 읽기 — 가장 풍부 + cohort split
2. **P_PV_09** 읽기 — 가장 짧지만 LOW_ACTIVITY 톤 정확
3. **P_PV_01 / P_PV_02** 비교 — placement effect 직접 확인
4. **P_S2_05 / P_S2_08** 비교 — nonmonotonic effect 직접 확인

이 4가지로 16% (8/48 stories)를 보면 전체 quality 감 + Branch C 발견의 서사 가치가 다 보임.

---

## 9. 다음 우선순위 (Lee 결정용)

큐레이션 결과를 보고 Lee가 결정할 수 있는 옵션:

| 옵션 | 다음 작업 | 가치 |
|---|---|---|
| A | 현재 quality 만족 → Loop B / Loop D 미세 개선 | LOW |
| B | 길이 확장 — narrative 전체 1000자+ 도달 | MEDIUM |
| C | Story → 인터랙티브 layer (player view 단계) | HIGH (long-term) |
| D | Story output을 v0.6 paper Appendix에 incorporate | MEDIUM |
| E | 새 시나리오 추가 (engine touch 필요) | DEFER (forbidden) |

---

## 10. 결론

48 stories 종합 review 결과:

- **이야기 흐름 식별**: 12/12 baseline + 36/36 Branch C 모두 통과
- **Configuration sensitivity surface**: LOW_ACTIVITY / nonmonotonic / placement reversal 모두 글에 보임
- **Quality marginal**: P_PV_09 같이 짧은 케이스는 가독성보다 *정확성* 우선 (자연스러움)
- **Lee가 직접 읽기 좋은 케이스**: §1-§6 의 6 highlights

**Story Output MVP는 안정적으로 작동하며, Branch C 발견을 글로 surface한다**. 이 자체로 NEXT_STEPS Phase 4 entry 가치를 입증.
