# Baseline 실험 — Claude Code 작업 지시

> **목적**: 논문에서 "현재 시스템이 baseline보다 낫다"를 증명하기 위한 비교 실험.
> **핵심 원칙**: 기존 코드를 수정하지 않는다. 새 스크립트만 추가한다.
> **산출물**: `docs/paper_data/baseline_comparison.json` + `docs/paper_data/fig_baseline_*.png`

---

## 📋 복사용 프롬프트

```
PROJECT_DIRECTION_v2.md와 TECHNICAL_SUMMARY_FOR_REVIEW.md를 읽어라.

오늘 세션 목표: 논문용 Baseline 비교 실험 4종 + Ablation 계층 실험을 구현하고 실행한다.

## 배경
논문 리뷰어가 "이 시스템이 더 단순한 대안보다 나은가?"를 물을 것이다.
이를 방어하기 위해 4개 baseline과 5단계 ablation을 측정한다.

## 절대 규칙
1. engine/ 아래 기존 코드를 수정하지 않는다
2. content/ 아래 기존 파일을 수정하지 않는다
3. 모든 baseline은 기존 엔진의 옵션을 끄거나 빈 값을 주는 방식으로 구현
4. 새 파일은 scripts/ 아래에만 생성

## 작업 1: Baseline 4종 구현

scripts/baseline_comparison.py를 작성한다.

각 baseline은 Peter standalone 시나리오 기준, 10 seed × 300 tick.
모든 baseline에서 동일 측정:
  - arrest 발생률
  - arrest 평균 tick (발생 시)
  - causal chain 존재율 (inform→surveillance→betray→arrest)
  - POM 7-pattern all_pass rate
  - final fear mean
  - final hope mean

### Baseline A: No-Trigger
- SimulationWorld에 triggers=[] (빈 리스트) 전달
- hazard_events는 유지
- canonical_events는 유지
- behavior_profiles는 유지
- 목적: "trigger가 없으면 multi-agent causal chain이 생기지 않는다" 확인

### Baseline B: Exogenous-Only
- SimulationWorld에 hazard_events=[] (빈 리스트) 전달
- triggers=[] (빈 리스트)
- canonical_events만 유지 (고정 시점 이벤트만)
- behavior_profiles는 유지
- 목적: "hazard 없이 canonical events만으로는 timing 분포가 없다" 확인

### Baseline C: Single-Agent
- initial_states=[peter] (peter만)
- triggers=[] (cross-agent trigger 불가)
- hazard_events는 유지
- behavior_profiles={"peter": peter_profile} (peter만)
- 목적: "multi-agent 없이는 arrest가 자발 발생하지 않는다" 확인

### Baseline D: Random-Behavior
- behavior_profiles의 모든 agent에 대해:
  모든 action의 base_weight를 1.0으로, 모든 multiplier를 0.0으로 설정한
  수정된 profile을 메모리에서 생성 (파일 수정 금지)
- triggers, hazard_events, canonical_events 모두 유지
- 목적: "규칙 기반 행동 선택 없이는 POM이 깨진다" 확인

### Full System (비교 대상)
- 기존 _run_peter_standalone() 그대로
- 동일 10 seed로 측정

## 작업 2: Ablation 계층 실험

같은 스크립트 안에 ablation도 구현한다.

5단계 계층:

### Level 0: Hazard Only
- hazard_events만 유지
- triggers=[], canonical_events=[]
- single agent (peter만)
- 기본 behavior_profile

### Level 1: Hazard + Trigger
- hazard_events + triggers 유지
- canonical_events=[]
- single agent (peter만)

### Level 2: Hazard + Trigger + Multi-Agent
- hazard_events + triggers + 4 agents (peter, judas, caiaphas, crowd)
- canonical_events=[]

### Level 3: Hazard + Trigger + Multi-Agent + Canonical Events
- 모든 요소 유지 (= full system에서 slow_state 영향 측정을 위한 기준)

### Level 4: Full System
- 기존 그대로

각 Level에서 동일 측정 (arrest율, timing, causal chain, POM, 감정 final).

## 작업 3: 결과 저장

모든 결과를 docs/paper_data/baseline_comparison.json에 저장.

스키마:
{
  "schema_version": 1,
  "n_seeds": 10,
  "max_tick": 300,
  "baselines": {
    "no_trigger": { "arrest_rate": ..., "arrest_tick_mean": ..., ... },
    "exogenous_only": { ... },
    "single_agent": { ... },
    "random_behavior": { ... },
    "full_system": { ... }
  },
  "ablation": {
    "level_0_hazard_only": { ... },
    "level_1_hazard_trigger": { ... },
    "level_2_multi_agent": { ... },
    "level_3_with_canonical": { ... },
    "level_4_full_system": { ... }
  }
}

## 작업 4: Figure 생성

scripts/baseline_figures.py를 작성한다.
baseline_comparison.json을 읽어서:

### Fig 1: Baseline 비교 막대 그래프
- x축: 5개 조건 (A, B, C, D, Full)
- y축 4개 subplot:
  - arrest rate
  - POM all_pass rate
  - causal chain rate
  - arrest tick mean (발생 시)

### Fig 2: Ablation 계층 차트
- x축: Level 0-4
- y축: arrest rate + POM rate (이중 축 또는 subplot)
- "각 요소를 추가할수록 성능이 올라간다"를 시각적으로 보여줌

저장: docs/paper_data/fig_baseline_comparison.png, fig_ablation_hierarchy.png

## 작업 5: Plain text 요약

docs/paper_data/baseline_comparison.txt에 사람이 읽을 수 있는 요약 테이블 출력.

## 실행 순서
1. scripts/baseline_comparison.py 작성
2. 실행하여 baseline_comparison.json 생성
3. scripts/baseline_figures.py 작성
4. 실행하여 fig_*.png 생성
5. 전체 결과 보고

## 자율 진행 규칙
- 각 작업 완료마다 한 줄 로그 (예: "✅ 1/5 baseline_comparison.py 작성 완료")
- 에러 시 스스로 디버깅
- 기존 코드 수정 절대 금지
- behavior_profile 수정은 메모리 내에서만 (deepcopy 후 변경)
- 완료 후 최종 보고:
  - 생성된 파일 목록
  - baseline_comparison.json의 핵심 수치
  - "Full System이 모든 baseline보다 나은가?" YES/NO 판정
  - 예상과 다른 결과가 있으면 보고

시작해라.
```

---

## 실행 후 확인할 것

결과가 나오면 다음을 확인하세요:

### 예상되는 결과 (이렇게 나와야 정상)

| 조건 | arrest rate | causal chain | POM |
|------|------------|--------------|-----|
| No-Trigger | 낮음 (0-30%) | 0% (trigger 없으니 chain 불가) | 낮음 |
| Exogenous-Only | 100% (canonical에 arrest 있으면) | 0% (endogenous 아님) | 중간 |
| Single-Agent | 낮음 | 0% (Judas 없음) | 낮음 |
| Random-Behavior | 중간 | 낮음 | 낮음 (0-10%) |
| **Full System** | **100%** | **≥50%** | **≥30%** |

### 만약 예상과 다르면

- Full System이 baseline보다 안 나으면: 논문 claim 재검토 필요 → 저한테 가져오세요
- No-Trigger에서도 arrest가 높으면: arrest가 trigger와 무관하게 발생한다는 뜻 → trigger의 기여 재검증
- Random-Behavior에서 POM이 높으면: POM이 행동과 무관하다는 뜻 → POM 설계 재검토

### 결과 가져오기

baseline_comparison.json과 txt 파일을 저한테 보여주시면,
논문에 어떻게 넣을지 (표 형식, 서술 방식) 같이 정리해드릴게요.

---

## 이후 세션에서 사용할 프롬프트

Baseline이 완료되면 논문 구조 잡기로 넘어갑니다.
그때는 이 프롬프트를 쓰세요:

```
Baseline 실험이 완료되었다. 결과는 docs/paper_data/baseline_comparison.json에 있다.

다음 작업: 논문 초안에 들어갈 결과 섹션의 수치 테이블을 정리해라.

1. Table 1: System vs Baselines (arrest rate, causal chain, POM 비교)
2. Table 2: Ablation Hierarchy (Level 0-4 단계별 성능 변화)
3. Table 3: Cross-Scenario Summary (Peter/VG/Talleyrand 핵심 수치)

각 테이블을 docs/paper_data/paper_tables.md에 Markdown 형식으로 저장.
기존 코드 수정 금지.
```
