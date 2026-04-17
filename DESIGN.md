# Witness 설계도 v0.5

> 역사적 인물의 생애를 hazard-driven ensemble simulation으로 수천 회 돌리고
> 결과 분포를 관측하여 "무엇이 갈라지는 순간이었는가"를 발견하는 시스템.

---

## 0. 문서 이력

- v0.1: 일반 역사 인물 시뮬레이터의 추상 설계
- v0.2.1: 베드로 MVP 구체 설계 (선형 내러티브 리더 전제)
- v0.3: hazard-driven ensemble simulator로 전환
- v0.4: EnvironmentState 통합 + ablation 검증
- **v0.5: POM/PRIM/pyABC Model Selection/shapiq 4단계 검증 완료** (이 문서)

---

## 1. 프로젝트 정체성

### 1.1 한 줄 정의

> **Agent-based, hazard-driven, ensemble historical simulator.**
> 한 사람의 생애를 수천 번 시뮬레이션하고 결과 분포를 관측한다.

### 1.2 근본 질문

> "이 사람의 삶에서, 무엇이 갈라지는 순간이었는가?"

### 1.3 방법론

개별 결과가 아니라 **분포를 관측**:
- 파라미터 공간 지형도 (어떤 조건에서 어떤 경로)
- 경로 유형 클러스터링 (도주형, 부인형, 순교형)
- 분기점(bifurcation) 탐지 (변수를 조금 바꾸면 결과가 뒤집히는 임계점)
- 역사적 경로의 위치 (필연이었는가, 우연이었는가)

### 1.4 두 비전

- **비전 B (베이스)**: 인과 시뮬레이션. 시스템이 수천 번 돌리고 분포를 관측.
- **비전 A (나중)**: 내러티브 체험. 발견된 경로를 1인칭으로 체험.

---

## 2. 엔진 4층 구조

```
Layer 1: Universal Engine (인물/시대 비종속)
  ├── AgentState (물리/감정/관계/도메인)
  ├── HazardEngine (상태 기반 확률적 이벤트 발생)
  ├── RuleEngine (상태 전이 규칙)
  ├── ResolutionEngine (동적 해상도)
  ├── SimulationRunner (hazard-driven 루프)
  └── Analysis Pipeline (SALib, UMAP, HDBSCAN, pyABC)

Layer 2: Domain Module (인물의 전문 분야)
  - 베드로: FaithJourneyState (신앙 여정)
  - 반 고흐: (미래) 회화 모듈
  - 베토벤: (미래) 작곡 모듈

Layer 3: Era Module (시대 환경)
  - 1세기 팔레스타인

Layer 4: Biography Pack (인물 고유 데이터)
  - 초기 상태, hazard 이벤트, 체크포인트(ground truth)
```

---

## 3. Hazard-Driven 이벤트 시스템

v0.2.1의 tick 고정 이벤트를 대체. 핵심 전환:

```
기존: if tick == 152: 체포()
신규: hazard = f(fear, fatigue, confusion, ...) -> Poisson draw -> 체포()
```

### 3.1 HazardFunction

매 tick 상태에 따라 발생 확률 계산:
- `base_rate`: 상태 무관 기본률
- `factors`: 상태 기반 인자 목록 (field_path, weight, transform)
- `firing_probability = 1 - exp(-hazard * dt)` (Poisson process)

### 3.2 HazardEvent

- `preconditions`: 활성화 전제조건
- `anchor_window`: 발생 가능 tick 범위 (bounded stochasticity)
- `deadline_tick`: 미발생 시 강제 발동 (하위 호환)
- `cooldown`, `max_fires`: 발산 방지
- `effects_on_fire`, `action_options_on_fire`: 발동 시 효과

### 3.3 Competing Risks

eligible 이벤트들을 hazard 내림차순 정렬, 순차 발동 시도.
`max_fires_per_tick`으로 한 tick 과부하 방지.

### 3.4 Langevin 노이즈

매 tick 감정 상태에 가우시안 노이즈 주입 (`state_noise_scale`).
같은 상황에서도 미세한 심리적 요동으로 결과가 달라짐.

---

## 4. 상태 전이 규칙

### 4.1 물리 규칙
- FatigueRule, HungerRule, HealthRule

### 4.2 감정 규칙 (핵심: 교차 효과)
- FearResponseRule: 피로-공포 교차 증폭
- ConfusionRule: fatigue>7 AND fear>6 -> confusion 급등
- HopeRule, GriefRule, LoveRule

### 4.3 사회 규칙
- RelationshipDecayRule, GroupIsolationRule

### 4.4 시간 규칙
- HomeostasisRule (극단 -> 중앙 복귀), CircadianRule (일주기)

---

## 5. 동적 해상도

### 5.1 3-Tier

| Tier | 시간 단위 | 용도 |
|------|----------|------|
| Chronicle | 일~주 | 대부분의 생애 |
| Episode | 시간~일 | 이벤트 밀도 높은 구간 |
| Scene | 분~시간 | 분기점, 극한 긴장 |

### 5.2 전환 기준

1. **anchor_window**: 미리 지정된 고해상도 구간
2. **tension_trigger**: 긴장도(fear + confusion + fatigue + 감정 갈등)가 임계값 초과
3. **event_density**: 최근 N tick 내 이벤트 빈도가 임계 초과

---

## 6. 분석 파이프라인

### 6.1 전역 민감도 (SALib)
- **Morris 스크리닝**: 초기 탐색. 어떤 파라미터가 중요한지 빠르게 식별.
- **Sobol 분석**: 상호작용까지 보는 정밀 분석.

### 6.2 경로 클러스터링 (UMAP + HDBSCAN)
- Trajectory를 feature matrix로 변환
- UMAP 2D 임베딩
- HDBSCAN 밀도 기반 클러스터링
- "도주형", "부인형" 등 경로 유형 자연 출현 관측

### 6.3 분기점 탐지
- 파라미터 스윕 → 결과 분산 급증 지점 탐색
- 평균 기울기 급변 + 표준편차 급등 = bifurcation 후보

### 6.4 파라미터 보정 (pyABC)
- Approximate Bayesian Computation
- 역사 경로에 가장 가까운 파라미터 posterior 추정
- likelihood-free (시뮬레이터 내부를 모르는 상태에서 보정)

### 6.5 Trajectory 데이터셋
- 각 run을 JSONL 레코드로 저장
- seed, params, event_sequence, state_series, checkpoint_results, fired_events
- run-level 데이터가 모든 분석의 원본

---

## 7. 첫 인물: 베드로

### 7.1 범위
예수의 마지막 50일 (수난주간 + 부활 40일). 약 500 tick.

### 7.2 Ground Truth
성경 기록 = 체크포인트:
- 체포 시 칼을 뽑음 (요 18:10)
- 멀리서 따라감 (눅 22:54)
- 3회 부인 (마 26:69-75)
- 통곡 (마 26:75)
- 빈 무덤에 달려감 (눅 24:12)
- 디베랴에서 바다에 뛰어듦 (요 21:7)
- 회복 (요 21:15-17)

### 7.3 신학적 원칙
- 예수는 에이전트가 아님 (정경 타임라인 = 고정 외부 입력)
- 정경 말씀은 개역개정 그대로 (재작성 금지)
- 고통을 영성 자원으로 삼지 않음
- 베드로의 부인은 인간 조건의 이해로

### 7.4 관측 결과 (2000+ 회 hazard-driven, 파라미터 공간 탐색)

**경로 유형 분포:**
- 정경 경로 (따라감 + 3회 부인): 46.6%
- 도주형: ~29%
- 기타 (부분 부인, 고백 등): ~24%

**정경 경로의 분포 내 위치:**
- UMAP 중심에서 43rd percentile -- 극단이 아니라 자연스러운 위치
- "베드로의 경로는 특수한 조건의 희귀 결과가 아니라, 인간 조건의 자연스러운 귀결"

**Sobol 전역 민감도 (outcome: 부인 횟수):**

| 파라미터 | S1 (직접) | ST (전체) | 상호작용 |
|---------|-----------|-----------|---------|
| fear | 0.460 | 0.553 | 0.093 |
| love | 0.186 | 0.554 | 0.367 |
| hope | 0.101 | 0.511 | 0.409 |
| confusion | 0.104 | 0.466 | 0.362 |
| fatigue | 0.001 | 0.085 | 0.084 |

**핵심 발견 (v0.4 -- 환경 통합 + ablation 검증 후):**

1. **체포 분기 (도주 vs 따라감)**: love(31.8%) > hope(26.5%) > fear(22.9%) > surveillance(13.0%)
   - love <= 3.27 → 대부분 도주
   - love > 3.27 AND fear <= 4.76 → surveillance에 따라 follow/flee 갈림
2. **부인 분기 (deny3 vs 기타)**: hope(34.3%) = love(34.1%) = crowd_pressure(31.6%) -- fear/surveillance = 0%
   - "부인은 공포가 아니라, 희망/사랑의 부재 + 군중 압력의 결합"
3. **환경 효과**: surveillance 0→10에서 deny3 비율 88%→95%
4. **Rule ablation 결과**:
   - current(love+env): deny3=94%
   - identity/shame: deny3=78%
   - env_only: deny3=82%
   - uniform(baseline): deny3=14%
   - 모든 상태 기반 규칙이 baseline보다 5~7배 높음. 구조 차이가 크지만 방향은 일관.
5. **정경 경로**: 46.6% 출현, UMAP 중심 (outlier 아님)
6. **Sobol (환경 없이)**: fear 직접효과 크지만, love/hope 상호작용이 큼
7. **Morris (환경 포함)**: 부인에서 surveillance/crowd_pressure가 공동 1위, fear는 최하위
   - "외부 압력 모델이 없을 때 내부 상태가 과대평가되고 있었다" (ChatGPT 예측 적중)
8. **pyABC 보정**: 정경 조건 = fear=6.0, love=5.6, hope=2.0

### 7.5 검증 결과 (v0.5 -- POM/PRIM/Model Selection/shapiq)

**POM (Pattern-Oriented Modeling):**
- 7개 관측 패턴 동시 필터. current 규칙: 38.6% 통과. fear-only: 1.2%. uniform: 0%.
- POM이 규칙군을 32배 차이로 분리 (deny3 단독은 2배 차이).

**PRIM:**
- POM 통과 영역: love [1.4, 8.7], crowd [1.1, 7.2]. fear/hope 제한 없음.

**pyABC Model Selection:**
- current=100%, fear-only=0%, identity=0%. 유일한 유효 구조.

**shapiq (Shapley Interaction) -- 교정됨:**
- 3개 변수(fear/love/hope)에서: fear x love = 0.123 (1위)
- 5개 변수(+surveillance/crowd)에서: fear 단독 = 0.026, surveillance = 0.025 (공동 상위). fear x love = 0.014로 급락.
- **결론: shapiq 결과는 변수 세트에 의존. 특정 상호작용을 "핵심 동인"으로 확정하기 어려움.**
- **안정적인 것**: POM이 규칙군을 분리 (38.6% vs 1.2%)하는 것은 변수 세트 무관.

**Cross-Persona (베드로 vs 반 고흐):**
- 베드로: fear x love 상호작용이 핵심 (관계적 위기)
- 반 고흐: fear 단독이 핵심 (내적 위기)
- 공통: fear와 love가 상위 2개 변수. 인물을 넘어서는 핵심.

---

## 8. 기술 스택

- Python 3.11+
- Pydantic (스키마)
- pytest (테스트)
- SALib (민감도 분석)
- UMAP + sklearn HDBSCAN (클러스터링)
- pyABC (파라미터 보정)
- NumPy, pandas, scipy

---

## 9. 프로젝트 구조

```
Witness/
├── engine/
│   ├── core/
│   │   ├── state.py          # AgentState
│   │   ├── event.py          # ExternalEvent, StateEffect
│   │   ├── hazard.py         # HazardFunction, HazardEvent, HazardEngine
│   │   ├── environment.py    # EnvironmentState (외부 압력)
│   │   └── world.py          # SimulationConfig
│   ├── rules/
│   │   ├── base.py           # Rule Protocol, RuleEngine
│   │   ├── physical.py, emotional.py, social.py, temporal.py
│   ├── simulation/
│   │   ├── runner.py          # SimulationRunner (hazard-driven + legacy)
│   │   ├── decision.py        # 확률적 행동 결정
│   │   ├── checkpoint.py      # Hindcasting
│   │   ├── batch.py           # 앙상블 실행
│   │   ├── analysis.py        # SALib, UMAP, HDBSCAN, 분기점 탐지
│   │   ├── resolution.py      # 동적 해상도
│   │   └── calibration.py     # pyABC 파라미터 보정
│   └── io/
│       ├── loader.py          # JSON 로더
│       └── trajectory.py      # 경로 데이터셋 저장/로드
│
├── content/peter/             # Biography Pack: 베드로
│   ├── initial_state.json
│   ├── hazard_events.json
│   ├── canonical_events.json  # (legacy + interventions)
│   ├── checkpoints.json
│   └── domain_faith.py
│
├── tests/ (153개 테스트)
├── CLAUDE.md, DESIGN.md, README.md, progress.md
└── requirements.txt
```
