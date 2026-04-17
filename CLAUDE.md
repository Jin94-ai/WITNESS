# Witness -- Claude 행동 강령

> 역사적 인물의 생애를 hazard-driven ensemble simulation으로 수천 회 돌리고
> 결과 분포를 관측하여 "무엇이 갈라지는 순간이었는가"를 발견하는 시스템.
> 첫 번째 인물: 베드로 (예수의 마지막 50일).

---

## ABSOLUTE RULES (절대 원칙)

1. **엔진/콘텐츠 분리**: `engine/`에 특정 인물 하드코딩 금지. `content/`에 엔진 로직 금지.
2. **정경 말씀 보존** (베드로 편): 예수님의 정경 말씀은 개역개정 본문 그대로. 재작성/변형 금지.
3. **예수 비에이전트화** (베드로 편): 예수의 행동은 고정 외부 입력(canonical timeline)으로만 존재.
4. **LLM 런타임 배제**: 시뮬레이션 루프에 LLM 관여 금지. LLM은 설계 파트너 + 사후 분석 보조로만.

---

## PROJECT IDENTITY (프로젝트 정체성)

### 근본 질문
> "이 사람의 삶에서, 무엇이 갈라지는 순간이었는가?"

### 방법론
**Agent-based, hazard-driven, ensemble historical simulator**

- 개별 시뮬레이션 결과가 아니라 **분포를 관측**
- 파라미터 공간의 지형도, 경로 유형 클러스터, 분기점(bifurcation) 탐지
- 역사적 경로(ground truth)가 가능성 지형에서 어디에 있는가

### 4층 엔진 구조
```
Layer 1: Universal Engine (인물/시대 비종속)
  - AgentState, 인과 규칙, hazard-driven 이벤트, 동적 해상도
Layer 2: Domain Module (인물의 전문 분야)
  - 베드로=신앙 여정, 반 고흐=회화, 베토벤=작곡
Layer 3: Era Module (시대 환경)
Layer 4: Biography Pack (인물 고유 데이터 + ground truth)
```

---

## MANDATORY PROTOCOLS

### 1. 프롬프트 크리틱
작업 시작 전 분석 피드백 먼저 제공.

### 2. 대화 우선, 실행 나중
승인 없이 코드 수정/파일 생성 금지.

### 3. 상태 동기화
- 세션 시작: `progress.md` -> `DESIGN.md`
- 작업 완료: `progress.md` 갱신

---

## TECH STACK

- **Language**: Python 3.11+
- **Schema**: Pydantic
- **Test**: pytest
- **Linter**: Ruff
- **Type Checker**: mypy
- **Analysis**: SALib (민감도), UMAP (차원 축소), HDBSCAN (클러스터링)
- **Data**: JSON, JSONL, Parquet (trajectory dataset)

### Commands
```bash
pytest                         # 전체 테스트
pytest --cov=engine            # 커버리지
ruff check . && mypy engine/   # 린트 + 타입
```

---

## PROJECT STRUCTURE

```
Witness/
├── engine/                      # Universal Engine (인물 비종속)
│   ├── core/
│   │   ├── state.py             # AgentState, PhysicalState, EmotionalState
│   │   ├── event.py             # ExternalEvent, StateEffect, ActionOption
│   │   ├── hazard.py            # HazardFunction, HazardEngine (핵심 전환)
│   │   └── world.py             # SimulationConfig
│   ├── rules/                   # 상태 전이 규칙
│   │   ├── base.py              # Rule Protocol, RuleEngine, RuleContext
│   │   ├── physical.py          # 피로, 배고픔, 건강
│   │   ├── emotional.py         # 감정 교차 효과
│   │   ├── social.py            # 관계, 고립
│   │   └── temporal.py          # 항상성, 일주기
│   ├── simulation/
│   │   ├── runner.py            # SimulationRunner (hazard-driven 루프)
│   │   ├── decision.py          # 확률적 행동 결정
│   │   ├── checkpoint.py        # Hindcasting 검증
│   │   ├── batch.py             # N회 앙상블 실행
│   │   └── analysis.py          # 분포 분석, 민감도
│   └── io/
│       ├── loader.py            # JSON 로더, 도메인 타입 레지스트리
│       └── trajectory.py        # Run-level 경로 데이터셋 저장
│
├── content/
│   └── peter/                   # Biography Pack: 베드로
│       ├── initial_state.json   # 초기 파라미터
│       ├── hazard_events.json   # Hazard 기반 이벤트 정의 (tick 고정 아님)
│       ├── checkpoints.json     # Ground truth 체크포인트
│       ├── domain_faith.py      # FaithJourneyState
│       └── canonical_timeline.json  # 예수 행동 (고정 외부 입력)
│
├── tests/
│   ├── test_engine/
│   └── test_peter/
│
├── CLAUDE.md                    # 이 파일
├── DESIGN.md                    # 설계도
├── README.md
└── progress.md                  # 세션 메모리
```

---

## CONTENT RULES (베드로 편)

### 신학적 기준
- 예수의 신성을 에이전트화하지 않음
- 고통을 영성 자원으로 삼지 않음
- 베드로의 죄를 도덕적 비난이 아닌 인간 조건의 이해로
- 교파적 편향 최소화

---

## VERIFICATION PROMPTS

**엔진/콘텐츠 경계:**
> `grep -r "peter\|Peter\|베드로" engine/` -- 결과 없어야 함

**Hazard 작동 확인:**
> 동일 초기조건, 다른 시드로 100회 돌렸을 때 이벤트 발생 tick이 분산되는가?

**분포 관측:**
> 파라미터 공간에서 경로 유형이 클러스터링되는가?

---

## STYLE GUIDELINES

- 이모지 금지, 간결, 기술적 정확성 우선, 객관적/중립적 톤

---

## FILE INTERDEPENDENCY

```
CLAUDE.md (행동 강령)
    ↓
DESIGN.md (설계도 — 아키텍처, 방법론, 스키마)
    ↓
progress.md (세션 메모리)
    ↓
실제 작업
```
