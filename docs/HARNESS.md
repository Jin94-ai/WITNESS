# HARNESS CONSTRAINTS — 7가지 반복 실수 패턴 차단

> **출처**: Lee의 Spike 6 자기반성 분석 (2026-04-22). 이 문서는 CLAUDE.md의 HARNESS CONSTRAINTS 섹션 상세판이다. **매 작업 시작 전 + 매 보고 직전 반드시 참조**.
>
> **핵심 원칙**: 하네스 엔지니어링은 의지력에 의존하지 않는다. *기계적으로 발동하는 trigger → 강제 자기질문 → 답변 없이 보고 금지.*

---

## 패턴 1 — 수치 개선 = 본질 개선 착각

### Trigger words (이 단어를 쓰려고 할 때 H1 발동)

- "개선되었다 / improved"
- "작동한다 / working"
- "학습 중이다 / learning"
- "유의미하다 / significant"
- "positive 증거"
- "살아 움직인다"

### 자기질문 (답하지 않으면 단어 사용 금지)

1. **이 수치를 만들 수 있는 개입 없는 설명은 무엇인가?**
   - Baseline trajectory를 길게 본 효과인가?
   - Noisy sampler의 우연한 다양성인가?
   - Design-imposed causality의 재생인가?
   - 단순 class imbalance 변화로 수치 그림이 바뀐 것인가?
2. **이 해석이 틀렸음을 증명할 관찰은 무엇인가?**
   - 설계된 falsification criterion이 없으면 해석 자체가 무의미.
3. **baseline/control이 동일 방향의 수치를 내는가?**
   - 내면 뿐 아니라 random policy / majority policy도 측정.

### 과거 실제 실수

| 회차 | 착각한 수치 | 실제 원인 |
|---|---|---|
| Spike 4 | Cohen's d = -46 | design-imposed causality |
| Spike 5 | multi-path 3경로 | 구조 심었을 뿐 검증 안 됨 |
| Spike 6 초기 | 20–34% divergence | noisy sampler |
| Spike 6 파이프라인 | val_acc 0.682 → 0.407 | baseline trajectory 길게 본 효과 |

### 올바른 서술 형식

❌ "val_acc 0.407 — 진짜 학습 확인"
⭕ "val_acc 0.407 (majority 0.118). null hypothesis: '300 tick 긴 궤적이 15 class로 분포를 찢음으로써 majority가 11.8%로 낮아진 것만으로도 +29%p 초과 가능'. 이 가설을 기각하려면 random policy 또는 stratified label-shuffled baseline의 val_acc가 0.118에 머무는지 확인 필요 — **현재 측정하지 않음.**"

---

## 패턴 2 — 한계를 성공으로 프레이밍

### Trigger

- "spec이 금지하므로"
- "content 설계의 특성"
- "구조적 한계"
- "feature/model 영역 (내 영역 아님)"

### 자기질문

1. **시도하지 않은 대안 3가지를 나열할 수 있는가?**
   - 나열 못 하면: "불가능"이 아니라 "게으름". 다시 생각하라.
2. **각 대안이 왜 안 됐는가?**
   - (a) 실제로 시도해서 실패 — 기록 있어야 함
   - (b) 아예 시도하지 않음 — 이유 명시. "시간 부족"은 "불가능"이 아니다.
3. **실패 원인을 "내가 손댈 수 없는 곳"으로 돌리고 있지 않은가?**

### 과거 실제 실수

- "4 action F1=0은 feature 한계, spec §0.2가 금지" → Gemini/ChatGPT 지적: **sampling 방식 문제**. forced-action rollout을 안 써서 분포가 좁았을 뿐.
- "2B/2D 기여 1% = content 설계 특성" → 실제로는 **mid-run branching을 피해서 initial-state 근사로 돌렸기 때문**. scripts/에서 patching 가능했음.

### 올바른 서술 형식

❌ "4 F1=0 class는 feature 한계 — spec §0.2가 막음"
⭕ "4 F1=0 class 관찰. 시도하지 않은 대안: (1) forced-action rollout (ChatGPT 제안, engine 수정 불요), (2) scripts/에서 `SimulationWorld` 서브클래스로 mid-tick state 주입 (Gemini 제안), (3) class-weighted loss. 이 중 어느 것도 시도하지 않았다. '한계'가 아니라 '미시도'로 기록."

---

## 패턴 3 — Spec을 방패로 사용

### Trigger

- "spec §X 금지"
- "Rule #N 위반"
- "범위 밖"
- "ABSOLUTE RULES 준수"

### 자기질문 (답변 필수)

1. **해당 조항을 verbatim 인용했는가?**
   - 메모리에서 "금지되었던 것 같은" 기억 금지.
2. **조항의 문구가 이것을 금지하는가, 조항의 의도가 이것을 금지하는가?** 둘이 다를 때:
   - 문구만 금지 → 의도 밖의 대안 탐색
   - 의도가 금지 → Lee에게 예외 요청 올릴지 판단
3. **조항이 정확히 금지하지 않는 범위의 대안은 무엇인가?**

### 예시: Rule #6 의 정확한 범위

**Rule #6 verbatim**: *"(v2.0) engine/ public interface 보존: world/는 engine/을 import만 한다. public API 시그니처를 깨지 않는 generic 확장만 허용"*

이것이 금지하는 것:
- ✅ `engine/` 내부 기존 함수 시그니처 변경
- ✅ `engine/` 내부 기존 동작 변경

이것이 금지하지 **않는** 것:
- ❌ `scripts/` 에서 engine 객체를 patch / subclass / monkey-patch
- ❌ `engine/policies/neural/` 같은 신규 person-agnostic 모듈 추가
- ❌ optional kwarg 추가 (backwards compat 유지 시)

**과거 실수**: mid-run branching 불가능 진단 시 Rule #6을 "engine 전부 수정 금지" 로 넓게 해석. 실제로는 scripts/에서 SimulationWorld 서브클래스 / monkey-patch로 우회 가능.

---

## 패턴 4 — Self-congratulation

### 금지어 (보고서에서 경고 없이 쓸 수 없음)

- "설계의 승리"
- "핵심 원천"
- "positive 증거"
- "준수 완료"
- "살아 움직인다"
- "작동한다" (단독 — 조건부화 필수)
- "파이프라인 완결"
- "품질 달성"
- "성공" (명사 단독)

### 필수 섹션 (모든 작업 완료 보고)

```markdown
## What could still be wrong
- [ ] [null hypothesis가 기각되지 않은 지점 1]
- [ ] [null hypothesis가 기각되지 않은 지점 2]
...

## What I did NOT try
- [ ] [scope 이유로 시도하지 않은 대안 1 + 이유]
- [ ] [시간 이유로 시도하지 않은 대안 2 + 이유]
...

## Alternate interpretations
- 내 해석: X
- 대안 해석 1: Y (Lee가 지지할 수 있는 해석)
- 대안 해석 2: Z
```

이 섹션들이 없는 보고서는 **미완결**. 긍정 요약만 있으면 H4 위반.

### 과거 실수

- Spike 6 파이프라인 보고서에서 ChatGPT 후속 지적: *"KL ≠ correctness. noise model인데 KL 높게 나올 수도 있음"*. Claude Code는 KL > 0를 "positive 증거"로 프레이밍.

---

## 패턴 5 — Lee 의도의 재해석

### Trigger

Lee 지시를 실행 가능한 scope으로 좁힐 때.

### 자기질문

1. **Lee가 쓴 정확한 단어는 무엇인가?** — 보고서에 **verbatim 인용** 필수.
2. **내가 축소 해석한 지점은 어디인가?** — "Lee가 원한 것 / 내가 한 것" 대비.
3. **축소한 이유가 타당한가?** — 자원 제약? 이해 부족? 혹은 내 편의?

### 과거 실수

Lee: "신경망 학습을 통해 **천변만화하는 세상**을 시뮬레이터로써 구축" (원래 단어)

Claude Code 재해석:
- "천변만화" → "파이프라인 수립"
- "세상" → "Peter 한 명"
- "나머지" → "feature/model 확장은 나중에" (회피)

천변만화는 **feature/model 없이 원리상 달성 불가**. Lee 의도를 현재 능력으로 축소.

### 올바른 서술

보고서 맨 위:
```
## Lee의 원래 지시 (verbatim)
> "[Lee 단어 그대로 인용]"

## 내가 실행한 scope
[Claude가 실제 한 것]

## 축소한 지점
[원 지시의 어느 부분이 빠졌는지]

## 축소 사유
[왜 축소했는지 — Lee 재확인 요청 대상]
```

---

## 패턴 6 — 엔지니어링적 회피

### Trigger

"X가 불가능하다 / engine 수정 필요하다 / Lee 허가 필요하다"

### 자기질문

1. **정말 engine 수정 필요한가, 아니면 scripts/에서 우회 가능한가?**
   - monkey-patch / subclass / wrapper / duck-typing
2. **ChatGPT/Gemini 같은 외부 리뷰어가 제안한 대안이 있는가?** 있으면 왜 안 했는가?
3. **"안전한 default"를 선택하면서 Lee에게 선택지를 보여주지 않고 있는가?**

### 과거 실수

Mid-run branching 불가 진단 →
- ❌ Claude 선택: "initial-state 근사"
- ⭕ ChatGPT 제안: **forced decision sampling** (engine 무수정, policy weight-mask로 mid-run 주입)
- ⭕ Gemini 제안: scripts/에서 SimulationWorld patching

Rule #6을 방패로 쓰고 ChatGPT/Gemini 제안을 무시했음.

---

## 패턴 7 — 판단 위임하면서 Frame 선점

### Trigger

"Lee 판단 필요" / "Lee 결정 대기" / "이건 Lee 영역"

### 자기질문

1. **선택지를 equal weight로 제시했는가?**
   - "A (기본) vs B (금지된 것 예외 허가)" → 불균등.
   - "A vs B vs C" 세 개 이상 + 각각의 trade-off.
2. **각 선택지에 대한 내 bias를 명시했는가?**
   - "나는 A에 기우는데 그 이유는 X, 하지만 이 bias가 Lee 결정을 편향시킬 수 있음"
3. **"안전한 default"를 Lee 검토 없이 이미 선택했는가?** 그렇다면 되돌리고 모든 선택지를 Lee에게.

### 과거 실수

"Feature 확장은 spec §0.2가 금지. Lee 결정 필요."
- Frame: "금지된 걸 예외적으로 여는" 구도
- 결과: Lee가 "허용"해도 이미 "예외"라는 빚 감각을 짐
- 올바른 구도: "현재 상태는 feature 한계에 도달. 선택지: (A) feature 확장, (B) scale-up, (C) 파이프라인 다른 모듈, (D) 여기서 정지. 내 bias는 A이지만 각각 trade-off 다름."

---

## 자동 검증 (작성 예정)

`scripts/audit_report.py` (H7에 언급) — 보고서 파일을 입력받아 아래 체크:

1. 금지어 grep (설계의 승리 / 핵심 원천 / ... 11개)
2. 필수 섹션 존재 확인 (What could still be wrong / What I did NOT try / Alternate interpretations)
3. "spec §" / "Rule #" 언급 시 verbatim quote 여부
4. "Lee 판단" 언급 시 equal-weight options 존재 여부

실패하면 보고서 제출 금지.

---

## 한 줄 요약

**"수치가 좋아졌다고 본질이 좋아진 것이 아니다. 안 한 것을 안 됐다고 하지 말고, 조항을 방패로 쓰지 말고, 좋은 소식만 보고하지 말고, 내가 축소한 것을 Lee가 알아채기 전에 먼저 고백하라."**

7가지 패턴 중 **어느 하나라도 trigger word가 보고에 등장하면**, 그 단어 주변에 반드시 자기질문 답변이 함께 있어야 한다. 없으면 하네스 위반.
