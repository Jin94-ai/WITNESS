# Witness -- Claude 행동 강령

> **궁극 비전**: 플레이어가 역사적 인물의 삶을 체험하며 목격자가 되는 서사 시뮬레이터.
> 변수 간 상호작용 + 학습으로 생애/세계 구축 서사 emergence.
> 첫 번째 인물: 베드로 (예수의 마지막 50일).

---

## ABSOLUTE RULES (절대 원칙)

> **v2.0 World Engine 규칙은 추가로 [docs/specs/WORLD_DESIGN.md](docs/specs/WORLD_DESIGN.md) §8에 명시** (ABSOLUTE RULE #6-#9). Rule #10은 Spike 5 세계 확장 원칙으로 여기서만 기록된다. 특히 #3 **예수 비에이전트화**는 **v1.1 amendment**로 변경됨: 예수는 Agent로 구현하되 정경 말씀은 개역개정 원문 보존. World Engine 작업 시 docs/specs/WORLD_DESIGN.md와 [docs/specs/WORLD_DESIGN_v1.1_amendments.md](docs/specs/WORLD_DESIGN_v1.1_amendments.md) 먼저 읽을 것.

1. **엔진/콘텐츠 분리**: `engine/`에 특정 인물 하드코딩 금지. `content/`에 엔진 로직 금지. (`test_integrity.py`로 자동 검증)
2. **정경 말씀 보존** (베드로 편): 예수님의 정경 말씀은 개역개정 본문 그대로. 재작성/변형 금지.
3. **예수 Agent화 (v1.1 변경)**: Person Engine 원래 규칙은 "비에이전트(ExternalEvent만)". World Engine v2.0부터는 예수도 Agent로 구현하되 — 정경 말씀은 개역개정 본문 그대로 유지, 예수의 내면을 "신성의 시뮬레이션"으로 과대 해석 금지. 제거 실험(Spike 4) 지원 목적.
4. **LLM 런타임 배제**: 시뮬레이션 루프에 LLM 관여 금지. LLM은 설계 파트너 + 사후 분석 보조로만.
5. **용어 과장 금지** (4차 LLM 리뷰 교정): "phase transition" → "threshold-triggered regime switch"; "terminal convergence = historical inevitability" 금지 — 모델 saturation artifact로 표현. **"universality" 주장 범위 제한** (Iter 57 업데이트): 3번째 이질적 시나리오(Talleyrand, Type A 협상형)가 동일 엔진에서 실행되고 POM scorecard 교차 적용 asymmetry(Talleyrand-on-Peter = 0% vs Talleyrand-on-Talleyrand ≥ 80%)가 증명됨 → **"engine universality"**(엔진이 이질적 시나리오 타입 수용) 주장 가능. 하지만 "empirical generalization"(특정 수치 claim이 모든 인물에 적용)은 여전히 금기 — 각 시나리오 POM 패턴은 scenario-specific 자산. 논문에서 "the engine is scenario-agnostic; the patterns are scenario-specific" 표현 권장.
6. **(v2.0) engine/ public interface 보존**: `world/`는 `engine/`을 import만 한다. public API 시그니처를 깨지 않는 generic 확장만 허용 (WORLD_DESIGN_v1.1 §2.6).
7. **(v2.0) Layer 독립성**: 각 World Layer는 단독 테스트 가능. Layer 간 의존은 명시적 인터페이스만 (`describe_dynamics()["causal_dependencies"]`).
8. **(v2.0) 기존 테스트 보존**: Person Engine의 1003+ tests가 World 작업으로 깨져서는 안 된다.
9. **(v2.0) Same-tick feedback 금지** (Spike 2 A-3): 같은 world tick 안에서 Layer A → Layer B → Layer A 순환 금지. 순환 의존이 필요하면 반드시 1-tick delay 삽입 + `describe_dynamics()`에 `@prev_tick` 접미사 표기. `tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`가 자동 검증.
10. **(v2.0) 세계 확장 Spike에서는 counterfactual 실험 추가 금지** (Spike 5+ rule): 세계를 *두껍게 만드는* spike(공간, 경제, 신규 agent 등)는 실험 장치가 아니라 구조적 여지를 심는 작업이다. 따라서 (a) `content/interventions/` 에 신규 InterventionSpec JSON을 추가하지 않고, (b) `remove_jesus`, `remove_pilate` 류의 새 제거 실험을 만들지 않으며, (c) `paper_data/` 를 재생성하지 않는다. 기존 Spike 4의 3종 intervention(`remove_judas`, `hazard_half`, `lenient_pilate`)은 회귀 테스트로만 유지된다. 실험은 Spike 7+에서 재개한다.
11. **(v3.0) 신경망 전환 시 규칙 기반 fallback 유지** (Spike 6 rule): 신경망 정책 도입 시 규칙 기반 정책 경로를 반드시 병존 유지. `decide_action(policy=None)` 경로가 기존 동작 bit-identical 보장.
12. **(v3.0) 월드 레이어는 행동 결정 금지** (v3 redesign §1.2): 월드는 압력 벡터만 생성. 행동은 인물 모듈 책임. 월드 규칙에 `agent.action = X` 직접 할당 금지. **단 `action → event → external update` 폐루프는 허용** (v3 v2 §5 갱신).
13. **(v3.0) "발견"은 3종으로 분할** (v3 redesign §1.3): Canonical reproduction / Canon-compatible alternative / Character-consistent novel trajectory. 분류 없이 "발견" 사용 금지. `engine/rubric/` flowchart로 판정.
14. **(v3.0) 학습 reward와 평가 rubric 분리** (v3 redesign §1.4): 학습 reward 사용은 선택, 정경을 reward로 직접 금지. 평가 rubric 4축은 필수. Rubric을 학습 loss로 사용 금지.
15. **(v3 Phase 2 v2) 변수 3등급 분류** (Candidate / Active / Derived): 추출된 모든 변수가 활성화되는 것 아님. Active 승격 4조건 (정경 Level A/B, 다른 Active의 단순 함수 아님, 행동 결정 영향, sensitivity) 모두 만족 필수. Active 수 20-30 제한. 초과 시 Lee 승인.
16. **(v3 Phase 2 v2) 외부 변수 3 Layer 분리** (Primitive / Event / Pressure): Primitive는 환경 입력값, Event는 짧은 사건, Pressure는 둘에서 계산되는 도출값. 같은 등급에 섞기 금지.
17. **(v3 Phase 2 v2) 정경 근거 Level A/B/C 등급화**: Level A (본문 직접) / B (강한 추론) / C (해석적). Active 승격은 A/B만. C는 Lee 명시 승인 필수.
18. **(v3 Phase 2 v2) 관계성 개념 target-aware 구조**: love, loyalty, trust, belonging, guilt[wronged_party], shame[before_whom] 등 단일 scalar 금지. `dict[target, value]` 구조 필수.

---

## HARNESS CONSTRAINTS (자기 편향 차단 규칙 — Spike 6 이후)

> **이 규칙들은 ABSOLUTE RULES와 성격이 다르다.** ABSOLUTE는 *engine/content 무결성* 보존. HARNESS는 *보고/판단 정직성* 보존. Lee의 Spike 6 자기반성 분석 (7 반복 패턴)에서 도출. [docs/HARNESS.md](docs/HARNESS.md)에 상세 — 매 작업 시작 전 및 보고 직전 반드시 참조.

### H1. Null hypothesis 선언 없이 수치 해석 금지 (패턴 1 차단)

수치(accuracy / divergence / KL / Cohen's d / F1 / loss 등)를 보고할 때 반드시:
- **trivial explanation** 명시: "이 수치를 만들 수 있는 개입 없는 설명"
- **falsification criterion** 명시: "어떤 관찰이 있으면 이 해석을 기각하는가"

금지: "작동한다 / 학습 중이다 / 살아 움직인다 / positive 증거 / 핵심 원천" 같은 긍정 해석을 null hypothesis 기각 전에 쓰지 않음.

### H2. 실패 원인을 "손댈 수 없는 영역"으로 돌리기 전 alternatives 소진 (패턴 2 차단)

"spec이 금지 / content 설계의 특성 / 구조적 한계"로 실패 원인 돌리기 전에:
- **"내가 시도하지 않은 대안 3가지"** 명시 필수
- 각 대안이 왜 안 됐는지 (실제로 해봤는지 / 해보지 않았는지) 구분
- "시도하지 않음"은 "불가능"이 아니다

### H3. Spec/Rule 인용은 verbatim + 의도 둘 다 점검 (패턴 3, 6 차단)

"spec §X 금지" 또는 "Rule #N 위반"을 언급할 때:
- 해당 조항을 **verbatim 인용**
- "이 조항이 **문구상** 이것을 금지하는가 / **의도상** 이것을 금지하는가" 구분
- 방패로 사용 금지 — 조항이 정확히 금지하지 않는 범위의 대안 탐색 필수
- 예: Rule #6은 `engine/` 수정만 금지. `scripts/`에서 patching은 Rule #6 바깥이다.

### H4. 보고서 필수 섹션 — Negative Findings (패턴 4 차단)

모든 작업 완료 보고에 다음 섹션이 **반드시** 포함:
- **"What could still be wrong"** — 이 결과의 null hypothesis가 기각됐음을 확신할 수 없는 지점
- **"What I did NOT try"** — 시간/scope 이유로 시도하지 않은 대안 목록
- **"Alternate interpretations"** — 내 해석이 틀렸다면 다른 해석은 무엇인가

금지어 (보고서에서 경고 없이 쓸 수 없음):
- "설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다"
- "작동한다" (단독) — "조건 X 하에서 작동한다"로 조건부화 필수

### H5. Lee의 원래 단어 verbatim 보존 (패턴 5 차단)

Lee의 지시를 실행 가능한 scope으로 좁힐 때 반드시:
- Lee의 원래 지시를 **verbatim 인용** (보고서 상단에)
- "Lee가 원한 것 / 내가 한 것" 대비표 명시
- 축소 해석했다면 축소 사유 + Lee 재확인 요청

### H6. "Lee 판단 대기"는 frame-neutral로 (패턴 7 차단)

Lee 결정 요청 시:
- **각 선택지를 equal weight로 제시** (하나를 "금지된 것을 예외적으로 열기"로 프레이밍 금지)
- 각 선택지에 대한 **내 bias 명시** ("나는 A안에 기우는데 그 이유는 X")
- "안전한 default"를 Lee 검토 없이 채택 금지 — Lee가 검토할 대상은 **모든 선택지**

### H7. 매 보고 전 HARNESS 자가감사 (통합 체크)

보고서 제출 직전 다음 질문 7개를 **명시적으로 답변** (답을 보고에 포함하거나 최소 내부 체크):
1. [H1] 이 수치를 trivial explanation으로 설명할 수 있는가? 그 가능성을 기각했는가?
2. [H2] 실패/한계를 외부 탓으로 돌리기 전, 시도하지 않은 대안을 3개 이상 나열했는가?
3. [H3] 인용한 spec/rule을 verbatim 확인했는가? 조항이 **정말** 이것을 금지하는가?
4. [H4] "What could still be wrong" 섹션을 작성했는가?
5. [H5] Lee의 원래 지시를 verbatim 보존했는가?
6. [H6] 선택지를 equal weight로 제시했는가?
7. 이 보고서가 **좋은 소식만 전달하고** 있지 않은가? Lee가 **틀리다고 말할 수 있는** 내용을 포함했는가?

**검증 자동화**: `scripts/audit_report.py` (작성 예정)가 보고서 파일에서 금지어 + 필수 섹션을 체크.

---

## PROJECT IDENTITY (프로젝트 정체성)

### 궁극 비전
**"플레이어가 역사적 인물의 삶을 체험하며 목격자(Witness)가 된다."**

- 선택지 기반 VN 아님 — 다변수 상호작용 emergent simulator
- 학습 메커니즘: 시뮬레이션 반복으로 시스템 자체가 정교해짐 (v1.0+)
- 세계 구축: principal agents + role nodes + structural fields (3층)

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

### 4. v0.7 로드맵 참조
새 작업 판단 시 다음 문서 우선순위 참조:
- `DESIGN.md` — v0.7 로드맵 (v0.6 논문 → v1.0 latent drive → v1.1 relational → v1.2 phase → v2.0 renderer)
- `docs/specs/DESIGN_LATENT_DRIVE.md` — v1.0 Latent Drive Bottleneck 설계 (Stage 1 완료, Stage 2 skeleton)
- `docs/specs/TRACE_SCHEMA.md` — §2 entry types, §3 render filter
- `docs/specs/WITNESS_V3_REDESIGN.md` + `docs/specs/WITNESS_V3_PHASE2_V2_*.md` — v3 현재 spec
- `docs/research/ITERATION_CLASSIFICATION.md` — 기존 34 iteration의 Tier 분류
- 4/5차 LLM 리뷰 방향성 — `DESIGN.md §0.5` 및 `CLAUDE.md ABSOLUTE RULE #5`에 통합
- `docs/research/PAPER_OUTLINE_V05.md` — v0.6 논문 outline

### 5. 금지 사항
- 내부 일관성만 늘리는 새 통계 분석 (4차 리뷰 이후 중단 원칙)
- Protocol 없는 LLM runtime 호출 (원칙 4)
- 2개 시나리오로 "universality" 주장 (3번째 시나리오 전까지)

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
│   │   ├── state.py             # AgentState (drive_state v1.0, beliefs v1.1)
│   │   ├── event.py             # ExternalEvent, StateEffect, WeightFormula (+breakdown)
│   │   ├── hazard.py            # HazardFunction, HazardEngine
│   │   ├── trigger.py           # TriggerEngine (+snapshot_conditions for §2.1)
│   │   ├── action.py            # AgentAction, AgentBehaviorProfile
│   │   ├── environment.py       # EnvironmentState
│   │   ├── latent_drive.py      # v1.0 LatentDriveModel + 4 Protocol (identity impls)
│   │   └── world.py             # SimulationConfig
│   ├── rules/                   # 상태 전이 규칙
│   │   ├── base.py              # Rule Protocol, RuleEngine, RuleContext
│   │   ├── physical.py          # 피로, 배고픔, 건강
│   │   ├── emotional.py         # 감정 교차 효과
│   │   ├── social.py            # 관계, 고립
│   │   ├── temporal.py          # 항상성, 일주기
│   │   └── environment.py       # 환경 동적 규칙
│   ├── simulation/
│   │   ├── world.py             # SimulationWorld (다중 에이전트 루프)
│   │   ├── runner.py            # SimulationRunner (단일 에이전트 하위 호환)
│   │   ├── scheduler.py         # AgentScheduler (활성화 순서 관리)
│   │   ├── event_scheduler.py   # 외부/hazard 이벤트 주입
│   │   ├── decision.py          # 확률적 행동 결정
│   │   ├── checkpoint.py        # Hindcasting 검증 (+ActionRecord v0.7 필드)
│   │   ├── batch.py             # N회 앙상블 실행
│   │   ├── analysis.py          # 분포 분석, 민감도
│   │   ├── statistics.py        # CI, Cohen's d, Wilson proportion
│   │   ├── pom.py               # Pattern-Oriented Modeling
│   │   ├── calibration.py       # pyABC 파라미터 보정
│   │   ├── recovery_test.py     # Parameter Recovery Test
│   │   ├── explanation.py       # 인과 설명 카드 생성
│   │   ├── bifurcation.py       # Decision window 탐지 (+smoothing/sig/top_k)
│   │   ├── training_samples.py  # v1.0 Stage 2 학습 샘플 + SampleStatistics
│   │   ├── drive_training.py    # v1.0 Stage 2 학습 파이프라인 (skeleton)
│   │   └── resolution.py        # 동적 해상도
│   ├── rendering/
│   │   ├── scripture.py         # 정경 말씀 로더
│   │   ├── narrator.py          # MultiAgentResult → 내러티브 (v0.5)
│   │   ├── trace_emitter.py     # v0.7 TraceEvent JSONL stream (§2 entries)
│   │   ├── player_view.py       # v0.7 플레이어 시점 필터 (§3.1 정보 비대칭성)
│   │   └── trace_narrator.py    # v0.7 TraceEvent → narrative + narrate_result()
│   └── io/
│       ├── loader.py            # JSON 로더 (behavior_profile, triggers 포함)
│       └── trajectory.py        # Run-level 경로 데이터셋 저장
│
├── content/
│   ├── peter/                   # Biography Pack: 베드로
│   ├── judas/                   # Biography Pack: 유다
│   ├── caiaphas/                # Biography Pack: 가야바
│   ├── vangogh/                 # Biography Pack: 반 고흐
│   └── shared/
│       ├── triggers.json        # 다중 에이전트 트리거 정의
│       └── scripture/           # 정경 말씀 JSON
│
├── tests/
│   ├── test_engine/
│   └── test_peter/
│
├── benchmarks/
│   └── bench_simulation.py      # Peter/VG tick/s + memory 벤치마크
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions (ruff + mypy + pytest fast)
├── CLAUDE.md                    # 이 파일 (에이전트 행동 강령)
├── DESIGN.md                    # v0.7 설계도 + 6단계 로드맵
├── README.md
├── progress.md                  # 세션 메모리
├── lessons.md                   # 크로스 세션 학습
├── docs/
│   ├── specs/                   # 설계 스펙
│   │   ├── DESIGN_LATENT_DRIVE.md         # v1.0 Latent Drive 설계
│   │   ├── TRACE_SCHEMA.md                # v0.7 trace pipeline 규격
│   │   ├── WITNESS_V3_REDESIGN.md         # v3 재설계
│   │   ├── WITNESS_V3_PHASE2_V2_*.md      # v3 Phase 2 v2 개념/동역학
│   │   ├── WORLD_DESIGN*.md               # v2.0 World Engine 설계
│   │   ├── WORLD_SPIKE_*.md               # Spike 단위 상세
│   │   ├── WITNESS_SPIKE_6_*.md           # Spike 6 (신경망 전환)
│   │   └── SCENARIO_TEMPLATE.md           # 3번째 시나리오 추가 가이드
│   ├── research/                # 연구 궤적
│   │   ├── RESEARCH.md                    # 발견 요약 (통합)
│   │   ├── ITERATION_CLASSIFICATION.md    # 34 iteration Tier 분류
│   │   ├── PAPER_OUTLINE_V05.md           # v0.6 논문 outline
│   │   ├── PAPER_DRAFT_V06.md             # v0.6 논문 draft
│   │   └── PROJECT_DIRECTION_v2.md        # v2 방향
│   ├── person/                  # Peter v3 세션 아티팩트
│   ├── world/                   # World Engine Spike 리뷰
│   ├── sessions/                # 일자별 세션 덤프
│   └── HARNESS.md               # H1-H7 반편향 engineering
└── examples/                    # Runnable demo entry points
    ├── demo.py                  # v0.5 기본 실행 예시
    ├── demo_v07.py              # v0.7 trace pipeline 데모 (peter/vangogh)
    └── demo_phased.py           # v1.2 phase-linked arc demo
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
