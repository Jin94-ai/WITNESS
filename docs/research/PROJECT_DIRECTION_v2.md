# PROJECT DIRECTION v2.0 — 방향 재정의 및 다음 단계

> **이 문서는 프로젝트 소유자(Lee)와 설계 파트너(Claude, claude.ai)가 진행 점검 후 합의한 방향 재정의이다.**
> **Claude Code는 이 문서를 DESIGN.md와 동등한 권위로 취급할 것. 충돌 시 이 문서가 우선한다.**

---

## 1. 프로젝트 정체성 재정의

### 1.1 이전 정의 (v0.2.1, 폐기)

> "기독교인이 베드로의 시점으로 예수의 마지막 50일을 체험하는 텍스트 시뮬레이터"

이 정의는 MVP 시작 단계에서 범위를 좁히기 위한 것이었다. 프로젝트가 3 시나리오(Peter/VanGogh/Talleyrand)로 확장된 현재, 이 정의는 실제 프로젝트를 설명하지 못한다.

### 1.2 새 정의 (v2.0, 확정)

> **Kairos Engine은 학습 기반 세계 시뮬레이션 엔진이다. 역사적 인물의 생애를 hazard-driven multi-agent 시뮬레이션으로 재현하고, 데이터로부터 행동 패턴을 학습하여 인과적으로 타당한 서사를 생성하는 것이 목표이다.**

### 1.3 프로젝트 구조 (명확화)

```
Kairos Engine (핵심 목표: 학습 기반 세계 시뮬레이션 엔진)
│
├── 검증 수단: 역사적 인물 시뮬레이션
│   ├── Peter (1차, 완료/진행중) — 신앙 서사, Phase-linked life
│   ├── Van Gogh (2차, 완료) — 창작 서사
│   ├── Talleyrand (3차, universality 검증) — 정치 서사
│   └── [향후 확장] — 다른 구조 타입의 인물/시대
│
├── 사이드 상품: 베드로 신앙 체험 도구
│   └── Peter 시뮬레이션의 파생물 (별도 일정, 핵심 경로 아님)
│
└── 학술 산출물: 논문 / 대학원 포트폴리오
    └── 현재 최우선 과제
```

### 1.4 ABSOLUTE RULES 유지

기존 5개 ABSOLUTE RULES는 **모두 유지**한다. 정체성이 바뀌어도 엔진의 기술적/신학적 원칙은 변하지 않는다.

---

## 2. 현재 상태 평가 (설계 파트너 점검 결과)

### 2.1 잘 된 것

- **엔진/콘텐츠 분리가 실증됨**: 3 시나리오가 같은 엔진에서 작동, POM 교차 비대칭으로 검증
- **Phase-linked life architecture**: 5-phase Peter 아크, bit-exact legacy 보존
- **코드베이스 견고**: 1003 테스트, 97% 커버리지, ruff/mypy clean
- **학습 파이프라인 기초**: IdentityEncoder → FixedProjection → LDA, feasibility spectrum 측정

### 2.2 확인된 문제

- **Talleyrand Stage 2 실패**: 6가지 가설 소거 후 deferred. 근본 원인은 per-action state-sensitive profile 부재이거나, Talleyrand의 캐릭터 특성(행동 일관성)이 action diversity 기반 학습과 구조적 불일치. **추가 시도 중단 확정.**
- **사용자 대면 결과물 부재**: 숫자 기반 검증은 충분하지만, "사람이 읽을 수 있는 서사 출력"이 아직 미확인
- **논문 미작성**: 연구 가치가 논문으로 공개되지 않으면 실현되지 않음

### 2.3 Talleyrand 확정 판정

- **Stage 2 학습 대상에서 완전 제외**
- **POM universality proof 역할만 유지** (Iter 57 교차 비대칭)
- 논문에서 Talleyrand는 "universality 검증" 섹션에만 등장, Stage 2 표에는 Peter/VG만
- Talleyrand 추가 개선 작업 **금지** (매몰 비용 방지)

---

## 3. 향후 작업 우선순위 (확정)

### 3.1 순서

```
1순위: 논문 작성 (즉시 시작)
2순위: Stage 2 비선형 검증 (논문과 병행)
3순위: 이후 결정 (논문 완성 후)
```

### 3.2 1순위: 논문 작성

**목표**: arXiv preprint 또는 학회 제출 가능한 논문 1편

**논문 구조 (권장)**:

```
Title: (미정, 예: "Kairos: A Hazard-Driven Multi-Agent Engine 
        for Biographical Simulation with Learned Drive Models")

Abstract

1. Introduction
   - 세계 시뮬레이션의 필요성
   - 기존 접근의 한계 (Generative Agents, Paradox 게임, ALife)
   - 본 논문의 contribution

2. Related Work
   - Agent-Based Historical Simulation
   - Computational Narrative
   - Digital Evolution / ALife
   - LLM-based Agent Systems

3. System Architecture
   - Engine/Content 분리 원칙
   - Agent Model (BDI + Physical + Emotional + Domain)
   - Hazard-Driven Event System
   - Phase-Linked Life Architecture
   - Canonical Intervention 메커니즘

4. Content Scenarios
   - Peter: 신앙 서사 (5 phase, canonical transitions)
   - Van Gogh: 창작 서사
   - Talleyrand: 정치 서사 (universality 검증용)

5. Evaluation
   5.1 Engine Universality
       - POM cross-scenario asymmetry
       - "engine scenario-agnostic, patterns scenario-specific"
   5.2 Canonical Fidelity
       - Standalone mode 결과 (legacy benchmark)
       - Phase-linked mode 결과 (appendix 또는 본문 보조)
   5.3 Stage 2 Feasibility Spectrum
       - Peter/VG: learnable (LDA separability)
       - Talleyrand: not learnable (empirical 소거 과정)
   5.4 Statistical Validation
       - Cohen's d, arrest rates, multi-seed consistency

6. Discussion
   - Talleyrand 실패의 교훈
   - 학습의 한계와 가능성
   - "시뮬레이션" vs "narrative state machine" 구분

7. Limitations & Future Work
   - 비선형 학습 (MLP)
   - Relational Graph (v1.1)
   - 더 많은 시나리오 타입
   - 사용자 대면 체험 (베드로 신앙 도구)

8. Conclusion

Appendix
   A. 전체 Phase 구성표
   B. POM Scorecard 정의
   C. Canonical Events 목록
   D. Empirical Numbers 상세
   E. Talleyrand 가설 소거 과정
```

**Claude Code의 역할**:
- 논문에 필요한 수치/표/그래프 추출 스크립트 작성
- 기존 코드에서 논문용 실험 재현 스크립트 정리
- README / DESIGN 문서를 논문과 일관되게 갱신

**Claude Code가 하지 않을 것**:
- 논문 본문 작성 (Lee가 직접, 또는 claude.ai와 협력)
- 학술 프레이밍 결정 (설계 파트너 영역)

### 3.3 2순위: Stage 2 비선형 검증 (논문 병행)

**PyTorch MLP 도입 전에 먼저 해야 할 것**:

1. **t-SNE / UMAP 시각화** (sklearn으로 가능)
   - Peter/VG의 drive class 분포를 2D로 시각화
   - 비선형 구조가 눈에 보이는지 확인
   - 결과를 논문 Figure로 활용

2. **RBF kernel SVM** (sklearn으로 가능, torch 불필요)
   - LDA(linear) vs SVM(nonlinear) 비교
   - SVM이 LDA보다 의미 있는 이득 → 비선형 구조 존재 증거 → MLP 도입 정당화
   - SVM이 LDA와 비슷 → linear가 한계, MLP도 큰 이득 없을 것 → torch 도입 보류

3. **결과에 따라 분기**:
   - 비선형 이득 있음 → PyTorch MLP 구현 (torch 의존성 추가)
   - 비선형 이득 없음 → "linear LDA가 현재 데이터의 한계"로 논문에 보고, MLP는 Future Work

**Claude Code 작업 지시**:
```
engine/simulation/training_samples.py 또는 별도 analysis/ 디렉토리에:
- t-SNE/UMAP 시각화 스크립트 (matplotlib + sklearn)
- RBF SVM 비교 스크립트 (sklearn.svm.SVC)
- 결과를 논문용 figure/table로 저장
Peter와 VG 시나리오에 대해 실행
```

### 3.4 하지 않을 것 (명시적 금지)

다음 작업은 **논문 완성 전까지 착수하지 않는다**:

- [ ] Talleyrand 추가 개선 (Stage 2 시도, action 추가, rebalance 등)
- [ ] v1.1 Relational Graph 구현
- [ ] 4번째 시나리오 추가
- [ ] PyTorch MLP 구현 (SVM 검증 결과 전까지)
- [ ] 베드로 신앙 체험 UI 개발
- [ ] 새 엔진 모듈 추가

**이유**: 기능 개발의 관성을 끊고 논문으로 전환하기 위함. "조금만 더 만들면..."은 금지. 만든 것을 정리하고 쓰는 시간.

---

## 4. Loop 운영 규칙 개선

### 4.1 Exit Condition 필수화

앞으로 `/loop` 시작 시 반드시 exit condition을 명시:

```
/loop 시작 조건:
- 목표: [구체적 작업]
- 성공 기준: [측정 가능한 지표]
- 실패 기준: [N iteration 내 지표 미달 시 중단]
- 최대 iteration: [상한]
```

### 4.2 탐색 vs 실행 구분

- **탐색 작업** (가설 검증, 새 접근 시도): 최대 5 iteration. 실패 시 loop 중단 → 설계 재검토
- **실행 작업** (확정된 구현, 테스트 작성): iteration 제한 없음 (단 exit condition은 필수)

### 4.3 대형 결정은 loop 밖에서

다음 유형의 결정은 `/loop` 중에 내리지 않는다:
- 새 시나리오 추가
- 아키텍처 변경
- 의존성 추가 (torch 등)
- ABSOLUTE RULES 변경
- 논문 구조 변경

이런 결정이 필요하면 loop를 중단하고, Lee에게 보고 후 Lee가 claude.ai 설계 파트너와 상의 후 결정.

---

## 5. 용어 정리 (Claude Code가 사용할 용어)

| 이전 용어 | 새 용어 | 이유 |
|-----------|---------|------|
| legacy mode | **standalone mode** | "legacy"는 "곧 대체될 것" 뉘앙스. 실제로는 통제된 실험 모드 |
| linked-life mode | **phased mode** | 변경 없음, 유지 |
| ground truth | **canonical record** | 역사/성경 기록의 정확한 성격 반영 |
| historical accuracy | **source-constrained plausibility** | |
| default trajectory | **canonical reconstruction path** | |
| 신앙 체험 도구 | **사이드 상품 / derived application** | 핵심 경로가 아님을 명시 |
| universality | **engine scenario-agnosticism** | scope 제한 유지 |

---

## 6. 다음 Claude Code 세션 시작 프롬프트

```
PROJECT DIRECTION v2.0 문서를 읽어라. 이 문서가 DESIGN.md보다 우선한다.

핵심 변경:
1. 프로젝트 정체성이 "신앙 체험 도구"에서 "학습 기반 세계 시뮬레이션 엔진"으로 재정의됨
2. 최우선 과제가 "논문 작성 준비"로 전환됨
3. Talleyrand Stage 2 추가 시도는 확정 금지
4. 새 기능 개발은 논문 완성 전까지 동결

오늘 세션 목표:
논문 작성에 필요한 실험 재현 및 수치 추출 환경을 정리한다.

작업:
1. 현재 프로젝트의 모든 측정 가능한 수치를 추출하는 
   scripts/paper_numbers.py 스크립트 작성
   - Peter standalone: arrest rate, Cohen's d, multi-seed stats
   - Peter phased: 같은 수치 + phase별 상태 변화 요약
   - VG: 주요 수치
   - Talleyrand: POM scorecard 결과 + Stage 2 실패 수치
   - cross-scenario: POM asymmetry 결과
   - separability: Peter LDA vs random, VG random

2. 논문용 figure 생성 스크립트 scripts/paper_figures.py
   - Peter 50일 상태 변화 trajectory (fear, faith 등)
   - POM cross-scenario 비대칭 heatmap
   - Stage 2 feasibility spectrum 차트
   - t-SNE / UMAP 시각화 (Peter drive classes)

3. RBF SVM vs LDA 비교 스크립트 scripts/svm_comparison.py
   - Peter와 VG에 대해 실행
   - 결과 테이블 출력 (LDA acc vs SVM acc)

4. 결과를 docs/paper_data/ 디렉토리에 JSON + PNG로 저장

모든 스크립트는 `python scripts/paper_numbers.py` 한 줄로 실행 가능해야 한다.
기존 코드를 수정하지 말 것. 새 스크립트만 추가.
```

---

## 7. 설계 파트너(claude.ai)와의 연락 시점

다음 시점에 claude.ai 설계 파트너에게 돌아와서 점검받을 것:

1. **논문 구조 초안 완성 시** — 구조와 프레이밍 리뷰
2. **SVM 비교 결과 나왔을 때** — MLP 도입 여부 결정
3. **논문 초고 완성 시** — 전체 리뷰
4. **방향 전환이 필요할 때** — Claude Code loop에서 해결 안 되는 큰 결정

---

*PROJECT DIRECTION v2.0 끝*
*작성: Lee + Claude (claude.ai 설계 파트너)*
*일시: 2026-04-20*
