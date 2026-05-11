# WITNESS — Human Pick Test Pack

> **이 문서를 그대로 리뷰어에게 보내세요.** 5분 안에 응답 가능한 self-contained 패키지.
>
> 응답을 받으면 [aggregate_human_pick.py](../../scripts/narrative/aggregate_human_pick.py)로 자동 점수화 → Plan §9 통과 여부 판정.
>
> 마지막 갱신: 2026-05-08.

---

## 0. 리뷰어에게 (먼저 읽어주세요)

WITNESS는 **다중 에이전트 시뮬레이션에서 자동으로 *이야기 후보*를 추출하는 시스템**입니다. 시뮬레이션이 한 번 돌면 여러 인물 / 여러 갈등 축으로 *복수의 이야기 가능성*이 나옵니다.

이 문서에는 **4개의 후보(S01–S04)** 가 들어 있습니다. 각 후보는:

- **Premise** — 한 줄 요약 (이야기의 씨앗)
- **Arc summary** — 변화의 방향
- **Turning points** — 시뮬레이션이 잡은 *전환점*
- **Adaptation hooks** — film / novel / game 활용 제안
- **Unresolved question** — 다음 장면을 부르는 질문

**중요한 한 가지**: 시스템은 *완성된 소설/시나리오/대사를 쓰지 않습니다.* 그건 작가의 영역. 시스템은 *씨앗*까지만 surface합니다. 당신의 판단:

> *"이 씨앗으로 내가 (또는 누군가가) 실제 장면 / 에피소드 / 퀘스트로 발전시킬 수 있다고 느끼나?"*

5분 정도 읽고 §6 응답 양식만 채워서 회신해주시면 됩니다. 정직하게 — *데이터처럼 느껴진다*든지 *억지로 이야기화한 부분*도 솔직히 지적해주세요.

---

## 1. 시뮬레이션 맥락 (1분 read)

- 시나리오: **peter_scarcity_baseline** — 베드로 시대 / 자원 부족 + 권위 압력 상황
- 12 agents (4명은 named: Peter / John / Andrew / James, 8명은 익명 onlooker)
- 3 그룹: core disciples / outer crowd A / outer crowd B
- 200 ticks 시뮬레이션 (deterministic per seed)

이 시뮬레이션이 한 번 돌면 다음 4개의 *서로 다른 인물 중심* 이야기 후보가 나옵니다.

---

## 2. S01 — Loyalty Strained by Survival Pressure

> *시스템 자동 평가: **strong_viable** (점수 80+/100)*

### 한 줄
> Peter는 두려움과 대중의 압력이 충성을 점점 침묵으로 바꾸어가는 동안 그 자리에 머물려 한다.

### 누가 / 어디서
- **Main**: Peter
- **Supporting**: James / core disciples
- **Core conflict**: loyalty_vs_survival
- **Scene question**: *Peter는 생존 압력이 올라갈 때 충성을 지킬 것인가?*

### Arc
fear intensifies → authority pressure closes in → shame relaxes → fear eases → unresolved tension lingers

### 시뮬레이션이 잡은 전환점

| Tick | 사건 |
|---|---|
| 14 | Peter의 fear가 7.0 이상으로 14틱 동안 지속 (peak 10.00) |
| 15 | 권위 압력 상승 + 동시에 fear 상승 (co-occurrence) |
| 15 | world.authority_vigilance 상승 (+0.250) |

### 관계
- Peter ↔ core disciples: *그룹 내 압력은 지속되나 Peter는 여전히 자리에 있음*
- Peter ↔ James: 같은 압력(authority_vigilance, fear)을 *동시에* 받음 (co-occurring, 방향 신호 X)

### 활용 제안

| 매체 | hook |
|---|---|
| **Film** | 권위 압력이 방으로 들어올 때 Peter가 *물리적으로는 머물러 있지만 감정적으로 위축*되는 조용한 장면 |
| **Novel** | 충성이 천천히 두려움-주도 침묵으로 전환되는 챕터 |
| **Game** | 공적 의심이 Peter 주변에서 올라갈 때 *고백 / 숨김 / 침묵* 중 선택해야 하는 분기 |

### 풀리지 않은 질문
> 중심 인물은 그 자리에 머물 것인가, 아니면 압력 아래 물러날 것인가?

---

## 3. S02 — Uncertainty Lingers Without Commitment (Andrew)

> *시스템 자동 평가: **viable_with_gaps** (점수 65–79)*

### 한 줄
> Andrew는 그룹 옆에 머물지만 압력이 주변에서 올라가는 동안 *결정하지 못한 채* 머문다.

### 누가
- **Main**: Andrew
- **Supporting**: outer crowd B
- **Core conflict**: uncertainty_vs_commitment
- **Scene question**: *Andrew는 불확실성에도 불구하고 결정할 것인가?*

### Arc
mid-run에 fear가 일시적으로 올라왔다가 가라앉음 → 결국 결정 없는 상태로 종결

### 시뮬레이션이 잡은 전환점

| Tick | 사건 |
|---|---|
| 6 | Andrew shame_self 변화 시작 |
| ~50 | fear 일시적 상승 |
| ~140 | 다시 fear 상승, 결정 없음 |

### 활용 제안

| 매체 | hook |
|---|---|
| **Short story** | 방에 머물지만 결코 행동하지 못하는 인물에 관한 단편 |
| **Game branch** | 미뤄진 결정들이 닫힌 문으로 누적되는 분기 |

### 풀리지 않은 질문
> 결정의 순간이 올 것인가, 아니면 표류가 계속될 것인가?

---

## 4. S03 — Uncertainty Lingers Without Commitment (James)

> *시스템 자동 평가: **viable_with_gaps***

### 한 줄
> James는 *조건이 변하는 동안 결정 없이 지켜보기만* 한다.

### 누가
- **Main**: James
- **Supporting**: core disciples (Peter와 같은 그룹 L1)
- **Core conflict**: uncertainty_vs_commitment

### 특징
- Peter와 *같은 그룹*에 있음 — Peter가 strong-viable한 동안 James는 *그를 지켜보는* 위치
- 압력은 받지만 능동 행동은 적음 → *목격자 관점*이 강함

### 활용 제안 (S02와 비슷하지만 *목격자 시점* 가능)

---

## 5. S04 — Uncertainty Lingers Without Commitment (John)

> *시스템 자동 평가: **viable_with_gaps***

### 한 줄
> John은 결정의 순간 없이 *압력 아래 머문다*.

### 누가
- **Main**: John
- **Supporting**: outer crowd B (S02 Andrew와 같은 그룹)
- **Core conflict**: uncertainty_vs_commitment

### 특징
- John은 Andrew와 *같은 그룹*에 있음 — *그룹 내 두 무행동 인물*이 평행으로 흘러감
- 후반부(140+)에 fear 재상승 — *지연된 반응*

### 활용 제안 (S02 Andrew와 짝을 이루는 *2인 챕터* 가능)

---

## 6. 응답 양식

각 후보(S01-S04)에 대해 아래 7개 질문에 답해주세요. *5분 안에* 응답 가능합니다.

### 응답 방법

- 텍스트로 회신 (이메일 / 메시지) — 아래 양식 그대로 채워서
- 또는 [response template JSON](../../data/narrative/human_pick_responses_template.json)에 직접 입력 (개발자라면)

---

### S01 — Loyalty Strained by Survival Pressure (Peter)

```
Q1. 이 후보로 *실제로* 장면 / 에피소드 / 퀘스트를 만들 수 있다고 느끼나요?
   1=전혀  2=어렵다  3=어쩌면  4=가능  5=확실히
   답: __

Q4. 부족한 정보는 무엇인가요? (선택)
   답: 

Q5. *데이터처럼* 느껴지는 문장이 있다면? (선택)
   답:

Q6. *억지로 이야기화*한 느낌이 드는 부분? (선택)
   답:

Q7. 가장 적합한 매체?  film / novel / game / drama / none
   답: __
```

### S02 — Andrew (uncertainty)

```
Q1 (1-5):  __
Q4: 
Q5:
Q6:
Q7 (film/novel/game/drama/none):  __
```

### S03 — James (uncertainty, witness)

```
Q1 (1-5):  __
Q4: 
Q5:
Q6:
Q7 (film/novel/game/drama/none):  __
```

### S04 — John (uncertainty, parallel to Andrew)

```
Q1 (1-5):  __
Q4: 
Q5:
Q6:
Q7 (film/novel/game/drama/none):  __
```

### 전체 질문

```
Q2. 4 후보 중 가장 *쓰고 싶은* 후보는? (S01 / S02 / S03 / S04)
   답: __

Q3. 왜 그 후보를 골랐나요? (한 문장)
   답:
```

---

## 7. 회신 후 진행

응답을 받으면:

1. [data/narrative/human_pick_responses.json](../../data/narrative/human_pick_responses.json) 파일에 입력 ([템플릿](../../data/narrative/human_pick_responses_template.json) 복사 후 채움)
2. `python scripts/narrative/aggregate_human_pick.py` 실행
3. 결과: [docs/portfolio/HUMAN_PICK_RESULT.md](HUMAN_PICK_RESULT.md) 생성

**Plan §9 Pass criteria** (per candidate):
- Q1 평균 ≥ 3.5/5
- 선택률 (Q2에서 그 후보 선택 / 전체 리뷰어) ≥ 1/3
- Q6에서 동일 부분 over-inference 지적이 *반복*되지 않음

---

## 8. 리뷰어에게 — 마지막 부탁

- *친절함보다 정직함*. 약하면 약하다고 말해주세요.
- Q5/Q6는 *비어 있어도 OK*. 눈에 띄는 부분만 적어주세요.
- 5분 ↑ 걸리면 너무 길게 쓴 겁니다 — 핵심만.

응답 회신처: [당신이 의뢰한 사람의 이메일 / 메시지]

감사합니다.

---

*이 패키지는 [WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md §9](../WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md) Stage E 운영용. Stage A-D + F는 자동.*
