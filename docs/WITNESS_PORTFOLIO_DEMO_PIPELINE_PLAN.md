# WITNESS Portfolio Demo Pipeline Plan

> 목표: WITNESS를 포트폴리오에서 바로 보여줄 수 있도록  
> **실행 → 중간 과정 시각화 → 일반인도 이해 가능한 Story Seed 결과물 → 근거/감사 레이어**까지 한 번에 생성하는 구조를 만든다.

---

## 0. 핵심 판단

현재 WITNESS는 내부적으로 다음 산출물을 갖고 있다.

```text
Simulation dump
→ Moment
→ MomentLink
→ StoryThread
→ NarrativeOpportunity
→ StoryCandidate
→ SceneBrief
→ Treatment
→ ViabilityReport
→ HumanPickTestPack
```

하지만 이 구조는 개발자/검증자에게는 의미가 있어도, 일반 사용자나 포트폴리오 리뷰어에게는 난해하다.

포트폴리오용 최종 구조는 다음처럼 보여야 한다.

```text
1. 실행한다
   ↓
2. 세계가 어떻게 움직였는지 보여준다
   ↓
3. 압력 변화가 이야기 흐름으로 묶이는 과정을 보여준다
   ↓
4. 일반인이 이해할 수 있는 Story Seed Cards가 나온다
   ↓
5. 필요하면 근거/감사 레이어를 펼쳐본다
```

즉, 내부 산출물은 유지하되, 포트폴리오 표면은 하나의 데모로 재구성한다.

---

## 1. 최종 포지셔닝

### 프로젝트명

```text
WITNESS Story Seed Demo
```

### 한 줄 설명

```text
WITNESS는 압력 기반 세계 시뮬레이션을 실행하고,
그 안에서 생겨난 변화 흐름을 일반인이 이해할 수 있는 이야기 씨앗 카드로 변환한다.
```

### 영어 포트폴리오 문장

```text
WITNESS runs a pressure-driven multi-agent world simulation and turns emerging character tensions into human-readable story seed cards, with optional evidence and audit layers.
```

### 피해야 할 표현

```text
AI가 이야기를 자동으로 씁니다
완성된 소설을 생성합니다
영화 시나리오를 만듭니다
세계가 살아 움직입니다
```

### 사용해야 할 표현

```text
이야기 씨앗을 채굴한다
장면/에피소드로 발전 가능한 후보를 보여준다
근거 추적 가능한 story seed를 만든다
창작자가 고를 수 있는 서사 입력을 제공한다
```

---

## 2. 최종 사용자 경험

포트폴리오 리뷰어가 보는 흐름은 아래와 같아야 한다.

```text
[Run Demo]
   ↓
[World Simulation Summary]
   ↓
[Pressure Timeline]
   ↓
[Story Thread Formation]
   ↓
[Story Seed Cards]
   ↓
[Evidence Toggle]
```

### 사용자가 이해해야 하는 단 하나의 메시지

```text
시뮬레이션을 돌렸더니,
세계 안의 압력 변화가 쌓였고,
그 변화가 몇 개의 이야기 씨앗으로 정리되었다.
```

---

## 3. CLI 실행 구조

### 최종 명령어

```bash
python -m witness narrative-demo
```

또는 현재 구조에 맞춘 스크립트형:

```bash
python scripts/narrative/run_portfolio_demo.py
```

### 옵션

```bash
python scripts/narrative/run_portfolio_demo.py \
  --anchor peter_scarcity_baseline \
  --seed 0 \
  --ticks 200 \
  --output docs/portfolio/demo
```

### 기본값

| 옵션 | 기본값 |
|---|---|
| anchor | peter_scarcity_baseline |
| seed | 0 |
| ticks | 200 |
| output | docs/portfolio/demo |
| format | html + md + json |

---

## 4. 최종 산출물 구조

명령어 한 번으로 아래 파일들이 생성되어야 한다.

```text
docs/portfolio/demo/
├── index.html                       # 메인 포트폴리오 데모
├── story_seed_cards.md              # 일반인용 이야기 씨앗 카드
├── story_seed_cards.json            # 카드 데이터
├── evidence_report.md               # 근거/감사 요약
├── demo_run_summary.json            # 실행 요약
└── assets/
    └── demo_data.js                 # index.html에 포함할 self-contained data
```

선택 산출물:

```text
docs/portfolio/demo/debug/
├── moments.json
├── story_threads.json
├── story_candidates.json
├── scene_briefs.md
├── treatments.md
├── viability_scores.json
└── audit.json
```

`debug/`는 포트폴리오 메인에 노출하지 않는다.

---

## 5. 파이프라인 단계

최종 데모 파이프라인은 8단계다.

```text
Stage 0. Demo Run Orchestration
Stage 1. World Simulation
Stage 2. Observer Snapshot
Stage 3. Pressure Summary
Stage 4. Story Thread Mining
Stage 5. Story Candidate Enrichment
Stage 6. Story Seed Card Translation
Stage 7. Evidence / Audit Packaging
Stage 8. Portfolio HTML Rendering
```

---

# Stage 0 — Demo Run Orchestration

## 목적

여러 기존 스크립트를 하나의 포트폴리오용 실행 명령으로 묶는다.

## 신규 파일

```text
scripts/narrative/run_portfolio_demo.py
```

## 역할

```text
1. 입력 옵션 파싱
2. 기존 pipeline 순차 실행
3. 중간 산출물 수집
4. 일반인용 card 생성
5. HTML demo 생성
6. 최종 경로 출력
```

## 의사 코드

```python
def main():
    args = parse_args()

    run_simulation(anchor=args.anchor, seed=args.seed, ticks=args.ticks)
    build_observer_dump()
    build_moments()
    build_story_threads()
    export_narrative_opportunities()
    build_story_candidates()
    build_scene_briefs()
    build_treatments()
    score_story_viability()
    audit_story_viability()

    build_story_seed_cards()
    build_demo_run_summary()
    build_portfolio_demo_html()

    print("Demo generated:")
    print("docs/portfolio/demo/index.html")
```

## 주의

- 이미 존재하는 내부 스크립트는 최대한 재사용한다.
- 새 layer는 additive로 추가한다.
- 기존 narrative mining 로직을 수정하지 않는다.
- 포트폴리오용 변환은 별도 모듈로 분리한다.

---

# Stage 1 — World Simulation

## 목적

세계가 실제로 구동되었음을 보여주는 기초 실행 단계.

## 입력

```text
anchor_id
seed
ticks
```

## 출력

```text
data/narrative/demo/simulation_result.json
```

또는 기존 dump를 재사용할 경우:

```text
data/visual/dot_observer_data.json
```

## 포트폴리오에서 보여줄 내용

```text
Scenario: peter_scarcity_baseline
Agents: 12
Groups: 3
Ticks: 200
Seed: 0
Runtime: X sec
```

## 일반인용 설명

```text
12명의 인물이 200단계 동안 자원 부족과 권위 압력 속에서 반응했습니다.
```

## 내부 용어 노출 금지

```text
deterministic per seed
Pydantic
hazard function
observer dump
```

이런 용어는 Evidence / Technical Appendix로만 보낸다.

---

# Stage 2 — Observer Snapshot

## 목적

시뮬레이션 결과를 관찰 가능한 상태 변화로 변환한다.

## 입력

```text
simulation_result.json
```

## 출력

```text
observer_snapshot.json
```

## 포트폴리오에서 보여줄 내용

숫자 전체가 아니라 요약만 보여준다.

```text
Observed:
- 12 agents
- 3 groups
- 200 time steps
- pressure changes detected
- candidate story threads found
```

## 일반인용 설명

```text
시스템은 각 인물의 두려움, 수치심, 희망,
집단 긴장, 대중의 의심, 권위 압력 변화를 관찰했습니다.
```

---

# Stage 3 — Pressure Summary

## 목적

“세계가 어떻게 움직였는가”를 한눈에 보여준다.

## 신규 모듈

```text
engine/observer/pressure_summary.py
```

## 신규 스크립트

```text
scripts/narrative/build_pressure_summary.py
```

## 출력

```text
data/narrative/demo/pressure_summary.json
docs/portfolio/demo/pressure_summary.md
```

## 데이터 모델

```python
@dataclass(frozen=True)
class PressureSummary:
    total_ticks: int
    dominant_world_pressure: str
    peak_pressure_tick: int
    pressure_phases: tuple[PressurePhase, ...]
    top_agent_pressures: tuple[AgentPressureSummary, ...]
    plain_language_summary: str
```

```python
@dataclass(frozen=True)
class PressurePhase:
    start_tick: int
    end_tick: int
    label: str
    plain_label: str
    summary: str
```

## 예시 출력

```markdown
## 세계 압력 흐름

초반에는 개인의 두려움이 빠르게 상승합니다.  
중반에는 권위 압력과 대중의 의심이 함께 올라갑니다.  
후반에는 몇몇 인물이 여전히 결정을 내리지 못한 채 남습니다.
```

## HTML 표현

```text
[초반: 두려움 상승] ━━━ [중반: 권위 압력] ━━━ [후반: 미해결 긴장]
```

## 내부 용어 변환표

| 내부 용어 | 일반인용 표현 |
|---|---|
| fear | 두려움 |
| shame_self | 수치심 |
| hope | 희망 |
| authority_vigilance | 권위 압력 |
| public_suspicion | 대중의 의심 |
| blame_concentration | 비난의 집중 |
| group_tension | 집단 긴장 |
| unresolved_thread | 풀리지 않은 긴장 |
| co-occurrence | 동시에 겹친 압력 |
| tick | 시간 단계 |

---

# Stage 4 — Story Thread Mining

## 목적

Moment와 Link를 이용해 이야기 흐름을 만든다.

## 기존 산출물

```text
data/narrative/story_threads.json
docs/portfolio/NARRATIVE_OPPORTUNITIES.md
```

## 포트폴리오에서 보여줄 내용

기술적 그래프 구조가 아니라 단순한 흐름으로 보여준다.

```text
Detected Story Threads:
1. Peter — 충성이 침묵으로 밀려나는 흐름
2. Andrew — 결정을 미루는 흐름
3. James — 목격자로 남는 흐름
4. John — 늦게 반응하는 흐름
```

## 금지

일반인용 화면에서는 아래를 숨긴다.

```text
MomentLink
same_agent
same_pressure
same_conflict_axis
temporal_continuity
component score
```

## 허용

근거 펼치기 영역에서는 표시 가능.

```text
이 흐름은 21개의 변화 신호에서 만들어졌습니다.
주요 근거: 두려움 지속, 권위 압력 상승, 미해결 긴장
```

---

# Stage 5 — Story Candidate Enrichment

## 목적

StoryThread를 창작자가 이해 가능한 후보로 강화한다.

## 기존 산출물

```text
docs/portfolio/STORY_CANDIDATES.md
data/narrative/story_candidates.json
```

## 개선 필요

현재 StoryCandidate는 아직 검증자용 표현이 많다.

예:

```text
loyalty_vs_survival
viable_with_gaps
source_inferred
```

이것을 Story Seed Card 변환 단계에서 제거한다.

---

# Stage 6 — Story Seed Card Translation

## 목적

일반인이 바로 이해할 수 있는 최종 결과물을 만든다.

## 신규 모듈

```text
engine/observer/story_seed_card.py
```

## 신규 스크립트

```text
scripts/narrative/build_story_seed_cards.py
```

## 입력

```text
data/narrative/story_candidates.json
docs/portfolio/SCENE_BRIEFS.md
docs/portfolio/ONE_PAGE_TREATMENTS.md
data/narrative/story_viability_scores.json
data/narrative/story_viability_audit.json
```

## 출력

```text
docs/portfolio/demo/story_seed_cards.md
docs/portfolio/demo/story_seed_cards.json
```

---

## StorySeedCard 데이터 모델

```python
@dataclass(frozen=True)
class StorySeedCard:
    seed_id: str
    title: str
    subtitle: str
    main_character: str
    plain_premise: str
    why_interesting: str
    scene_image: str
    unresolved_question: str
    usable_for: tuple[str, ...]
    confidence_label: str
    evidence_summary: EvidenceSummary
    risk_note: str
```

```python
@dataclass(frozen=True)
class EvidenceSummary:
    source_thread_id: str
    evidence_count: int
    strongest_signals: tuple[str, ...]
    audit_status: str
    technical_link: str | None = None
```

---

## StorySeedCard 출력 예시

```markdown
# 침묵으로 변해가는 충성

베드로는 끝까지 곁에 남고 싶다.  
하지만 사람들의 시선과 권위자의 압박이 커질수록,
그는 점점 말하지 않는 쪽을 선택하게 된다.

## 왜 흥미로운가

그는 배신자가 되고 싶지 않다.  
그런데 살아남으려는 마음이 충성을 조금씩 침묵으로 바꾼다.

## 장면으로 만들면

사람들이 수군거리는 방 안.  
베드로는 아직 그 자리에 있지만, 더 이상 앞에 나서지 않는다.

## 남는 질문

침묵도 충성일까, 아니면 이미 물러선 것일까?

## 활용 가능

단편 영화 / 소설 챕터 / 게임 선택지

## 근거 요약

이 씨앗은 21개의 변화 신호에서 만들어졌습니다.  
주요 신호: 두려움 지속, 권위 압력 상승, 미해결 긴장  
감사 결과: 통과
```

---

## 일반인용 제목 생성 규칙

기존 technical title을 일반 제목으로 변환한다.

| conflict | 일반 제목 |
|---|---|
| loyalty_vs_survival | 침묵으로 변해가는 충성 |
| uncertainty_vs_commitment | 결정을 미루는 사람 |
| control_vs_exposure | 드러날수록 조여오는 통제 |
| collective_fear_vs_scapegoating | 두려움이 누군가를 가리킬 때 |
| identity_vs_failure | 무너진 자리에서 남는 이름 |
| atmosphere_vs_action | 아무도 움직이지 않는 방 |

---

## 일반인용 premise 생성 규칙

### 입력

```text
Peter tries to stay present as fear and public pressure slowly turn loyalty into silence.
```

### 출력

```text
베드로는 끝까지 곁에 남고 싶다.
하지만 사람들의 시선과 권위자의 압박이 커질수록,
그는 점점 말하지 않는 쪽을 선택하게 된다.
```

### 규칙

- conflict label을 그대로 노출하지 않는다.
- pressure name을 일반 단어로 바꾼다.
- “시뮬레이션이 잡았다”는 말은 근거 영역으로 내린다.
- 한 문단은 2~3문장 이하.
- 문장은 감정적으로 과장하지 않는다.
- 없는 사건을 추가하지 않는다.

---

## 위험 표현 금지

일반인용 카드에서도 아래는 금지한다.

```text
그는 배신했다
그는 울부짖었다
그는 사람들 앞에서 고백했다
그는 도망쳤다
누군가 그를 고발했다
경비병이 그를 체포했다
```

원본 데이터가 명시하지 않는 구체 사건은 쓰지 않는다.

## 허용 표현

```text
말하지 않는 쪽을 선택하게 된다
앞에 나서지 않는다
물러서는 방향으로 기운다
결정을 미룬다
긴장이 남는다
주변의 압력이 커진다
```

---

# Stage 7 — Evidence / Audit Packaging

## 목적

일반인용 결과물의 신뢰 근거를 접힌 레이어로 제공한다.

## 출력

```text
docs/portfolio/demo/evidence_report.md
data/narrative/demo/evidence_summary.json
```

## Evidence UI 원칙

메인 카드에서는 간단히만 보여준다.

```text
근거: 21개 변화 신호
감사: 통과
```

자세한 근거는 접기 버튼으로 제공한다.

```html
<details>
  <summary>근거 보기</summary>
  ...
</details>
```

## Evidence 항목

```text
- Source thread
- Number of linked moments
- Main pressures
- Turning points
- Viability grade
- Audit status
- Risk note
```

## 일반인용 근거 예시

```markdown
### 근거 보기

이 이야기는 임의로 작성된 것이 아니라,
시뮬레이션에서 반복적으로 나타난 변화 흐름에서 만들어졌습니다.

- 연결된 변화 신호: 21개
- 주요 변화: Peter의 두려움 지속, 권위 압력 상승, 미해결 긴장
- 검증 결과: 장면/에피소드로 변환 가능
- 감사 결과: 없는 사건을 추가하지 않음
```

## 기술자용 링크

페이지 하단에 별도 제공.

```text
Technical appendix:
- StoryCandidate JSON
- SceneBrief
- Treatment
- Viability Report
- Audit JSON
```

---

# Stage 8 — Portfolio HTML Rendering

## 목적

포트폴리오에서 바로 열 수 있는 self-contained HTML을 만든다.

## 신규 스크립트

```text
scripts/narrative/build_portfolio_demo_html.py
```

## 출력

```text
docs/portfolio/demo/index.html
```

## 페이지 구성

```text
1. Hero
2. Run Summary
3. How the World Moved
4. From Pressure to Story Seeds
5. Story Seed Cards
6. Evidence / Audit
7. Technical Appendix
```

---

## 8.1 Hero

```text
WITNESS Story Seed Demo

A pressure-driven world simulation that surfaces story seeds from character tension.
```

한국어 버전:

```text
압력 기반 세계 시뮬레이션에서 이야기 씨앗을 찾아내는 데모
```

---

## 8.2 Run Summary

카드 형태로 표시.

```text
Scenario: Peter scarcity baseline
Agents: 12
Groups: 3
Ticks: 200
Story Seeds: 4
Audit Failures: 0
```

---

## 8.3 How the World Moved

압력 흐름을 3단계로 표시.

```text
초반 — 두려움이 오래 지속됨
중반 — 권위 압력과 대중의 의심이 커짐
후반 — 결정하지 못한 긴장이 남음
```

선택적으로 단순 bar/timeline 추가.

```text
Fear          ████████████░░░
Authority     ░░░██████░░░░░
Unresolved    ░░░░░░░███████
```

---

## 8.4 From Pressure to Story Seeds

중간 과정 설명.

```text
1. 인물과 집단의 상태 변화를 관찰합니다.
2. 반복되는 압력 변화를 연결합니다.
3. 인물 중심의 이야기 흐름으로 묶습니다.
4. 일반인이 읽을 수 있는 이야기 씨앗 카드로 바꿉니다.
```

---

## 8.5 Story Seed Cards

메인 영역.

카드마다:

```text
제목
한 줄 상황
왜 흥미로운가
장면으로 만들면
남는 질문
활용 가능
근거 요약
```

S01을 최상단에 크게 배치한다.

S02-S04는 보조 카드로 표시한다.

```text
Main Seed
- S01 Peter

Secondary Seeds
- S02 Andrew
- S03 James
- S04 John
```

---

## 8.6 Evidence / Audit

접힌 영역.

```text
Evidence and Audit

- 4 story seeds generated
- 1 strong viable
- 3 viable with gaps
- 0 audit failures
```

---

## 8.7 Technical Appendix

개발자/면접관용.

```text
Generated files:
- story_seed_cards.json
- evidence_report.md
- story_viability_scores.json
- story_viability_audit.json

Internal pipeline:
Simulation → Observer → Moments → Threads → Candidates → Seeds
```

---

# 9. 일반인용 문장 변환 규칙

## 9.1 금지어

일반인용 메인 카드에서는 아래 단어를 사용하지 않는다.

```text
tick
source_derived
source_inferred
co-occurrence
authority_vigilance
public_suspicion
blame_concentration
group_tension
viable_with_gaps
strong_viable
deterministic
cross-seed
MomentLink
StoryThread
NarrativeOpportunity
```

## 9.2 대체어

| 금지어 | 대체어 |
|---|---|
| tick | 시간 단계 / 흐름 |
| source_derived | 원본 변화 |
| source_inferred | 추론된 연결 |
| co-occurrence | 동시에 겹친 변화 |
| authority_vigilance | 권위자의 압박 |
| public_suspicion | 사람들의 의심 |
| blame_concentration | 비난이 한쪽으로 몰림 |
| group_tension | 집단의 긴장 |
| viable_with_gaps | 보완이 필요한 씨앗 |
| strong_viable | 바로 발전 가능한 씨앗 |
| cross-seed robust | 여러 실행에서도 반복됨 |

## 9.3 문장 길이

- 한 문장 40자 내외 권장
- 한 카드 200~350자 권장
- 근거 요약은 3줄 이내
- 기술 설명은 접힌 영역으로 이동

---

# 10. 구현 파일 목록

## 신규 파일

```text
engine/observer/pressure_summary.py
engine/observer/story_seed_card.py
engine/observer/portfolio_demo.py

scripts/narrative/run_portfolio_demo.py
scripts/narrative/build_pressure_summary.py
scripts/narrative/build_story_seed_cards.py
scripts/narrative/build_portfolio_demo_html.py
```

## 신규 테스트

```text
tests/test_narrative/test_pressure_summary.py
tests/test_narrative/test_story_seed_card.py
tests/test_narrative/test_portfolio_demo.py
tests/test_narrative/test_portfolio_demo_html.py
```

## 신규 문서

```text
docs/portfolio/demo/README.md
docs/portfolio/demo/story_seed_cards.md
docs/portfolio/demo/evidence_report.md
```

---

# 11. Acceptance Criteria

## 11.1 Functional

```text
[ ] `python scripts/narrative/run_portfolio_demo.py` 한 번으로 전체 데모가 생성된다.
[ ] `docs/portfolio/demo/index.html`이 생성된다.
[ ] 일반인용 `story_seed_cards.md`가 생성된다.
[ ] Evidence report가 생성된다.
[ ] 기존 internal JSON/MD 산출물과 연결된다.
```

## 11.2 General Audience Readability

```text
[ ] 메인 카드에 tick/source/co-occurrence 같은 내부 용어가 없다.
[ ] 첫 화면에서 “무엇을 하는 프로젝트인지” 10초 안에 이해된다.
[ ] S01 카드는 일반인이 장면을 떠올릴 수 있다.
[ ] S02-S04는 보조 씨앗으로 구분된다.
[ ] 기술 근거는 접힌 영역에 있다.
```

## 11.3 Evidence Discipline

```text
[ ] 없는 사건을 추가하지 않는다.
[ ] 대사를 생성하지 않는다.
[ ] 감정 과잉 서술을 하지 않는다.
[ ] 근거/감사 결과를 숨기지 않는다.
[ ] audit_fail이 있으면 카드에 표시한다.
```

## 11.4 Portfolio

```text
[ ] index.html 하나만 열어도 데모 흐름이 보인다.
[ ] 실행 명령이 README에 명시된다.
[ ] 생성된 결과물이 GitHub Pages 또는 로컬 브라우저에서 볼 수 있다.
[ ] 기술 면접관이 원하면 Appendix에서 내부 구조를 확인할 수 있다.
```

---

# 12. Human Review Protocol v2

기존 Human Pick Test Pack은 기술 검증용으로 남긴다.  
일반인용 리뷰는 새로 한다.

## 리뷰어에게 보여줄 것

```text
docs/portfolio/demo/index.html
```

또는

```text
docs/portfolio/demo/story_seed_cards.md
```

## 묻는 질문

```text
1. 첫 화면만 보고 무엇을 하는 프로젝트인지 이해했나요? (1-5)
2. S01 이야기가 장면으로 떠오르나요? (1-5)
3. 가장 흥미로운 이야기는 무엇인가요?
4. 이해가 막히는 단어가 있었나요?
5. 이걸 소설/영화/게임 아이디어로 쓸 수 있을 것 같나요? (1-5)
```

## 통과 기준

```text
Q1 평균 ≥ 4.0
Q2 평균 ≥ 3.5
Q5 평균 ≥ 3.5
이해 막힘 단어 3개 이하
```

---

# 13. 작업 순서

## Step 1 — Story Seed Card 변환기

```text
build_story_seed_cards.py
```

우선 MD/JSON만 만든다.  
HTML은 나중.

## Step 2 — Pressure Summary

```text
build_pressure_summary.py
```

세계가 어떻게 움직였는지 3단계 요약한다.

## Step 3 — Portfolio Demo HTML

```text
build_portfolio_demo_html.py
```

Story Seed Cards + Pressure Summary + Evidence를 한 페이지로 렌더한다.

## Step 4 — Run Orchestrator

```text
run_portfolio_demo.py
```

전체 파이프라인을 한 번에 실행한다.

## Step 5 — General Audience Review

일반인 3명에게 index.html만 보여주고 평가한다.

---

# 14. 최종 성공 정의

이 phase의 성공은 다음이다.

```text
명령어 한 번으로 데모가 생성되고,
브라우저에서 열면 세계 구동 → 중간 변화 → 이야기 씨앗 카드가 보이며,
일반인도 S01의 이야기를 10초 안에 이해할 수 있다.
```

실패는 다음이다.

```text
데모는 생성되지만,
일반인이 여전히 tick / pressure / viability 같은 내부 용어를 해석해야 한다.
```

---

# 15. 최종 한 줄 목표

> WITNESS의 포트폴리오 데모는 “내부 검증 문서 묶음”이 아니라,  
> **세계가 구동되고 그 안에서 이야기 씨앗이 생겨나는 과정을 한 화면에서 이해시키는 결과물**이어야 한다.

---

*End of plan.*
