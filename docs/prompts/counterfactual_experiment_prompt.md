# 논문 최종 보완 실험 — Claude Code 작업 지시

> **목적**: 논문의 두 가지 핵심 비판 포인트를 방어하기 위한 추가 실험.
> **원칙**: 기존 engine/ content/ 코드 수정 금지. 새 스크립트만 scripts/ 아래에 추가.
> **산출물**: `docs/paper_data/causal_counterfactual.json` + `docs/paper_data/hazard_scaling.json` + figure 2장

---

## 📋 복사용 프롬프트

```
PROJECT_DIRECTION_v2.md를 읽어라.

오늘 세션 목표: 논문 방어를 위한 최종 2개 실험을 구현하고 실행한다.

## 배경

Baseline 실험(v2)에서 두 가지 문제가 드러났다:
1. Chain rate가 random(0.60) > full system(0.10) — "chain rate는 causal structure가 아니라 action frequency를 재는 것"이라는 비판
2. Endogenous arrest가 모든 조건에서 1.00 — "arrest가 항상 발생하도록 설계된 것 아닌가?"라는 비판

이를 방어하기 위해:
- 실험 1: Counterfactual causal 검증 (agent/trigger 제거 시 arrest 소멸 여부)
- 실험 2: Hazard scaling 검증 (hazard rate 축소 시 arrest rate 변화)

## 절대 규칙
1. engine/ 기존 코드 수정 금지
2. content/ 기존 파일 수정 금지
3. 새 파일은 scripts/ 아래에만

## 실험 1: Counterfactual Causal Metric

scripts/counterfactual_baseline.py를 작성한다.

Peter standalone 시나리오 기준, 각 조건 10 seed × 300 tick.

### 조건 설계

5개 조건을 실행한다:

조건 1: Full System (기준선)
- 기존 _run_peter_standalone() 그대로
- 4 agents: peter, judas, caiaphas, crowd
- triggers, hazard_events, canonical_events 모두 포함

조건 2: Judas 제거
- initial_states에서 judas 제거: [peter, caiaphas, crowd]
- behavior_profiles에서 "judas" 제거
- triggers, hazard_events, canonical_events 유지
- 목적: "Judas 없이도 arrest가 발생하는가?"

조건 3: Caiaphas 제거
- initial_states에서 caiaphas 제거: [peter, judas, crowd]
- behavior_profiles에서 "caiaphas" 제거
- 목적: "대제사장 없이도 인과 체인이 성립하는가?"

조건 4: Trigger 제거
- triggers=[] (빈 리스트)
- 나머지 모두 유지 (4 agents, hazard, canonical)
- 목적: "trigger 없이도 endogenous arrest가 가능한가?"

조건 5: Random Behavior + Judas 제거
- Judas 제거 (조건 2와 동일)
- 나머지 agent의 behavior_profile을 uniform random으로 (deepcopy 후 base_weight=1.0, multipliers 전부 0.0)
- 목적: "random에서 Judas 없으면 chain이 사라지는가?"

### 측정 항목 (각 조건에서)

- endogenous_arrest_rate: canonical arrest event 제외, trigger/hazard에 의한 arrest 발생률
- canonical_arrest_rate: scene_08 등 고정 시점 arrest
- arrest_mean_tick: endogenous arrest 발생 시 평균 tick
- arrest_std_tick: 표준편차
- chain_rate_v2: gap ≤ 30 tick 제약 적용
- chain_gaps: 평균 gap 구조 [inform→surv, surv→betray, betray→arrest]
- final_fear_mean
- final_hope_mean

### 핵심 검증 로직

실험 후 자동으로 다음을 판정:

1. "Judas 제거 시 endogenous arrest 소멸" → full의 causal dependency 증명
   - full endo_arrest ≥ 0.8 AND judas_removed endo_arrest ≤ 0.2 → CAUSAL_PASS
   - 그 외 → CAUSAL_FAIL

2. "Trigger 제거 시 chain 소멸" → trigger의 구조적 필수성
   - full chain ≥ 0.05 AND trigger_removed chain == 0.0 → TRIGGER_NECESSARY
   - 그 외 → TRIGGER_NOT_NECESSARY

3. "Random + Judas 제거 시 chain 소멸" → random의 chain이 구조적이 아님을 증명
   - random_no_judas chain < random_with_judas chain (baseline v2에서 0.60) → RANDOM_CHAIN_SPURIOUS
   - 그 외 → RANDOM_CHAIN_STRUCTURAL

## 실험 2: Hazard Scaling

scripts/hazard_scaling.py를 작성한다.

Peter standalone 시나리오 기준, 10 seed × 300 tick.
hazard_events.json의 모든 hazard event의 base_rate를 scaling factor로 곱한다.

### 조건 설계

6개 scaling factor: [1.0, 0.75, 0.50, 0.25, 0.10, 0.0]

각 factor에서:
- hazard_events를 deepcopy
- 모든 hazard event의 base_rate *= factor
- factor 0.0이면 hazard_events=[] (완전 제거)
- 나머지 (agents, triggers, canonical, profiles) 모두 유지

### 측정 항목

- endogenous_arrest_rate
- canonical_arrest_rate
- arrest_mean_tick (endogenous 발생 시)
- chain_rate_v2
- final_fear_mean

### 핵심 검증 로직

1. "scale 1.0 → 0.0으로 갈 때 endogenous arrest rate 변화 패턴"
   - 점진적 감소 → emergence (hazard rate가 event 확률을 조절)
   - 1.0에서 갑자기 0으로 → threshold (all-or-nothing, 설계의 산물)
   - 항상 1.0 → inevitability (hazard와 무관, 다른 메커니즘이 보장)

2. "endogenous arrest가 0이 되는 최소 factor" 기록

## 출력

### JSON 파일

docs/paper_data/causal_counterfactual.json:
{
  "schema_version": 1,
  "experiment": "counterfactual_causal",
  "conditions": {
    "full_system": { ... },
    "judas_removed": { ... },
    "caiaphas_removed": { ... },
    "trigger_removed": { ... },
    "random_no_judas": { ... }
  },
  "verdicts": {
    "causal_dependency": "CAUSAL_PASS / CAUSAL_FAIL",
    "trigger_necessity": "TRIGGER_NECESSARY / TRIGGER_NOT_NECESSARY",
    "random_chain_nature": "RANDOM_CHAIN_SPURIOUS / RANDOM_CHAIN_STRUCTURAL"
  }
}

docs/paper_data/hazard_scaling.json:
{
  "schema_version": 1,
  "experiment": "hazard_scaling",
  "factors": {
    "1.0": { ... },
    "0.75": { ... },
    ...
    "0.0": { ... }
  },
  "pattern": "emergence / threshold / inevitability",
  "collapse_factor": 0.XX (endogenous arrest가 0이 되는 최소 factor)
}

### Figure 파일

scripts/counterfactual_figures.py를 작성한다.

Fig 1: Counterfactual 비교 막대 그래프
- x축: 5개 조건
- y축: endogenous_arrest_rate + chain_rate_v2 (subplot)
- "Judas 제거 시 arrest 소멸"이 시각적으로 명확해야 함
- 저장: docs/paper_data/fig_counterfactual_comparison.png

Fig 2: Hazard scaling 곡선
- x축: scaling factor (1.0 → 0.0)
- y축: endogenous_arrest_rate
- 점진적 감소 vs 급격한 drop이 보여야 함
- 저장: docs/paper_data/fig_hazard_scaling_curve.png

### Plain text 요약

docs/paper_data/causal_counterfactual.txt
docs/paper_data/hazard_scaling.txt

## 실행 순서

1. scripts/counterfactual_baseline.py 작성 + 실행
2. scripts/hazard_scaling.py 작성 + 실행
3. scripts/counterfactual_figures.py 작성 + 실행
4. 전체 결과 보고

## 자율 진행 규칙
- 각 작업 완료마다 한 줄 로그
- 에러 시 스스로 디버깅
- 기존 코드 수정 절대 금지 (deepcopy로 파라미터 변경)
- 완료 후 최종 보고:
  - 생성된 파일 목록
  - causal_counterfactual.json의 3개 verdict
  - hazard_scaling.json의 pattern 판정
  - "Full system의 causal structure는 counterfactual로 검증되었는가?" YES/NO
  - 예상과 다른 결과 있으면 보고

시작해라.
```

---

## 예상 결과와 의미

### 실험 1 예상

| 조건 | endogenous arrest | chain |
|------|------------------|-------|
| Full system | ~1.00 | ~0.10 |
| Judas 제거 | **≤0.20** | **0.00** |
| Caiaphas 제거 | 중간 | ≤0.05 |
| Trigger 제거 | ~1.00 (hazard가 여전히) | **0.00** |
| Random + no Judas | ~1.00 | **≤0.10** |

이 결과가 나오면:
- "Judas 제거 → arrest 소멸" = **Judas가 인과적으로 필수**
- "Random에서도 Judas 없으면 chain 급감" = **random의 chain 0.60은 허상**
- 논문 claim: "counterfactual 제거 시 소멸하는 causal dependency가 full system에만 존재"

### 실험 2 예상

hazard를 줄이면 endogenous arrest가 점진적으로 줄어들 것. 
0.25 이하에서 급감하면 → "emergence" (특정 임계값 이상에서만 사건 발생)
어떤 factor에서도 1.00이면 → "inevitability" (hazard와 무관, 설계 문제)

## 이 실험 후 가능한 것

두 실험 결과가 나오면:
- **논문 구조 잡기(B단계) 진입 가능**
- Counterfactual 결과가 논문의 핵심 증거가 됨
- Baseline v2의 MIXED 결과가 "지표의 한계 발견 → counterfactual로 해결"이라는 contribution으로 전환
