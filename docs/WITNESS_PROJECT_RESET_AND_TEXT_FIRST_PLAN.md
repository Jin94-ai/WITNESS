# WITNESS 프로젝트 정리 및 추후 계획안

작성일: 2026-05-02  
현재 결정: **Visual-first 확장 중단, Text-first Observer Brief 중심으로 전환**  
프로젝트 상태: **시뮬레이션/Observer/Visual 실험을 거쳐, 포트폴리오용 핵심 산출물을 Evidence-backed Text Report로 재정렬**

---

## 0. 한 줄 결론

WITNESS는 지금부터 “픽셀 비주얼 데모”가 아니라, **다중 에이전트 세계에서 발생한 사건 후보를 관찰하고, 그 근거를 추적 가능한 리포트로 정리하는 Observer System**으로 정리한다.

비주얼 트랙은 실패가 아니라 실험 결과로 남긴다. 다만 현재 포트폴리오의 메인 산출물로는 적합하지 않다.

---

## 1. 프로젝트 핵심 정의

### 1.1 WITNESS란 무엇인가

WITNESS는 단순한 이야기 생성기가 아니다.

WITNESS는 다음 흐름을 목표로 하는 시스템이다.

```text
Simulated World
→ Agent / Group / Event / State 변화
→ Observer Layer
→ Candidate Extraction
→ Curation
→ Evidence-backed Observer Brief
```

핵심 가치는 다음에 있다.

1. 세계를 시뮬레이션한다.
2. 시뮬레이션 결과에서 의미 있는 변화와 사건 후보를 관찰한다.
3. 후보를 `story_ready`, `observation_only`, `low_activity_hold` 등으로 분류한다.
4. 후보가 왜 중요한지 signal, lens, agent state, tick evidence로 설명한다.
5. 사람이 읽을 수 있는 근거 기반 리포트로 만든다.

### 1.2 하지 않는 것

WITNESS는 현재 단계에서 다음이 아니다.

```text
❌ 소설 자동 생성기
❌ 픽셀 게임
❌ 플레이어 개입형 시뮬레이션
❌ 월드맵 리플레이 도구
❌ 예쁜 영상 생성기
❌ story renderer 중심 데모
```

현재 포지셔닝은 다음이 맞다.

```text
✅ Multi-agent simulation observer
✅ Event candidate detection system
✅ Evidence-backed narrative analysis tool
✅ Simulation-to-report pipeline
✅ Traceability-first AI system prototype
```

---

## 2. 지금까지의 주요 진행 흐름

## 2.1 Engine + Observer + Curation

현재까지 가장 안정적인 기반은 Engine / Observer / Curation 계층이다.

검증 상태:

```text
Engine fast suite: 1874 passing
Visual unit tests: 43 passing
PSD tests: 18 passing
PEP tests: 25 passing
```

주요 기능:

- 시뮬레이션 실행
- tick 기반 상태 변화 관찰
- snapshot / lens / candidate extraction
- story_ready / observation_only / low_activity_hold 분류
- candidate curation
- provenance / traceability 실험

판단:

```text
이 계층은 WITNESS의 핵심 자산이다.
포트폴리오에서도 이 부분을 중심으로 보여줘야 한다.
```

---

## 2.2 Visual Track 전체 실험 요약

Visual track은 총 6단계를 거쳤다.

| 단계 | 결과 | 상태 |
|---|---|---|
| Pixel World Static S1 | PW-S1-B. 테스트 그리드 인상 | 보류 |
| Pixel World Static S2 Patch | PW-S2-C. 여전히 dashboard | 보류 |
| Pixel Scene Director Redirection | 어휘 patch ≠ 구성 fix 진단 | 완료 |
| PSD MVP + LC1 Patch | PW-SC-B. static medium 한계 | frozen |
| Pixel Event Playback MVP | cutscene playback 가능성 확인 | 실험 완료 |
| WVT Pass | VT-B. 72.1% source-backed, 27.9% staged-only | frozen |

### 핵심 교훈

```text
비주얼이 불가능한 것은 아니다.
하지만 현재 데이터 구조로는 visual이 source-derived world flow를 직접 증명하지 못하고,
hand-authored staging / template / inferred composition이 많이 섞인다.
```

Visual track에서 증명한 것:

- Canvas primitive로 pixel world / scene / event playback 구현 가능
- timeline event playback 가능
- agent move / face / speech / emote / pose_change 가능
- static scene보다 짧은 cutscene이 상호작용 전달에는 낫다
- traceability audit으로 visual provenance gap을 측정 가능

Visual track에서 증명하지 못한 것:

- 실제 engine world flow가 화면에 직접적으로 살아난다는 것
- 사용자가 설명 없이 직관적으로 사건을 이해한다는 것
- 포켓몬식 세계 관찰 감각
- visual timeline이 source world state와 강하게 1:1 매핑된다는 것

최종 판단:

```text
Visual은 부록으로 보존한다.
포트폴리오 메인 산출물로 확장하지 않는다.
```

---

## 2.3 WVT Pass 결과

World-to-Visual Traceability Pass 결과:

```text
total events:        43
source_derived:      12 (27.9%)
source_inferred:     19 (44.2%)
staged_only:         12 (27.9%)
combined source-backed: 72.1%
staged ratio:           27.9%
```

Per-playback:

```text
C01 authority_pressure: 83.3% source-backed
C02 saturation_split:   81.3% source-backed
C03 confession_cluster: 53.3% source-backed
```

해석:

- 핵심 사건은 어느 정도 source-backed다.
- 하지만 crowd 배치, 일부 movement, tile 좌표는 template-authored다.
- visual은 “완전한 mock”은 아니지만, “실제 engine replay”도 아니다.

결론:

```text
PEP는 VT-B partial success로 freeze.
Candidate 확장 금지.
다음 메인 트랙은 Text-first Observer Brief.
```

---

## 3. 왜 Text-first로 전환하는가

## 3.1 비주얼이 어려웠던 진짜 이유

비주얼이 어려웠던 이유는 그래픽 품질 문제가 아니다.

진짜 문제는 다음이다.

```text
Engine output이 아직 visual-ready event log 형태가 아니다.
Observer output은 의미 있는 후보와 signal/lens를 잘 제공하지만,
각 agent의 위치, 행동, 대상, 상호작용, 상태 변화가 연속적인 visual event log로 정리되어 있지는 않다.
```

그래서 visual을 만들려면 중간에 연출적 해석이 필요했다.

예:

```text
confession signal → speech bubble
forgiveness signal → supporter moves inward
cohort split → agents move apart
authority pressure → synthetic guard approaches
```

이 과정에서 staged-only가 생긴다.

## 3.2 텍스트가 현재 더 강한 이유

텍스트 리포트는 WITNESS의 핵심 가치를 더 직접적으로 보여줄 수 있다.

텍스트가 잘 보여줄 수 있는 것:

```text
- 어떤 tick에서 변화가 발생했는가
- 어떤 agent가 중요해졌는가
- 어떤 signal/lens가 candidate를 띄웠는가
- 왜 story_ready인가
- 무엇이 source-derived이고 무엇이 inferred인가
- 시스템이 무엇을 알고, 무엇을 해석했는가
```

비주얼은 설명 없이는 애매하지만, Observer Brief는 다음을 명확히 보여준다.

```text
Simulation evidence
→ Observer interpretation
→ Candidate judgment
→ Human-readable report
```

## 3.3 중요한 구분

Text-first 전환은 story renderer 회귀가 아니다.

```text
❌ Text Story Renderer
✅ Evidence-backed Observer Brief
```

금지해야 할 방향:

```text
- 감성적인 완성형 이야기로 포장
- 원본 근거 없이 narrative만 생성
- story renderer cycle 재개
- 소설처럼 읽히는 결과물에 집중
```

가야 할 방향:

```text
- 관찰 리포트
- candidate card
- evidence table
- provenance summary
- system decision log
```

---

## 4. 새 메인 트랙: Observer Brief v1

## 4.1 목표

Observer Brief v1의 목표는 다음이다.

```text
peter_scarcity_baseline run에서 발생한 story_ready candidates를
근거 기반 리포트로 정리하여,
WITNESS가 “세계의 사건 후보를 관찰하고 설명하는 시스템”임을 보여준다.
```

## 4.2 핵심 산출물

새 메인 산출물:

```text
1. scripts/report/build_observer_brief.py
2. docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md
3. docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md
4. docs/visual/VISUAL_TRACK_FREEZE_DECISION.md
5. docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md
6. docs/portfolio/WITNESS_VISUAL_EXPERIMENT_APPENDIX.md
```

---

## 5. Observer Brief v1 문서 구조

최종 리포트는 다음 구조를 권장한다.

```md
# WITNESS Observer Brief — peter_scarcity_baseline

## 1. Executive Summary
- 이 run에서 어떤 변화가 발생했는가
- 가장 중요한 candidate는 무엇인가
- 세계 상태가 어떤 방향으로 변했는가

## 2. Run Context
- anchor
- scenario
- tick range
- observer/candidate source
- lens set

## 3. Timeline of Notable Events
- t15: authority pressure
- t25: saturation split
- t142: confession / forgiveness cluster

## 4. Candidate Cards
### C01_t15 — Authority Pressure
- What happened
- Agents involved
- Evidence
- Signals / lenses
- Why story_ready
- Confidence / caveats

### C02_t25 — Saturation Split
...

### C03_t142 — Confession Cluster
...

## 5. Provenance Table
| Candidate | Source tick | Agents | Signals | Derived | Inferred | Caveat |

## 6. Observer Judgment
- story_ready vs observation_only 기준
- candidate curation 결과
- strongest lens

## 7. Visual Experiment Note
- Pixel World → PSD → PEP → WVT 결과
- 왜 visual을 freeze했는가
- 왜 text-first가 현재 더 신뢰 가능한가

## 8. Limitations
- 아직 engine event log adapter 미흡
- visual-ready world flow 미구축
- staged-only visual gap 존재

## 9. Next Steps
- Engine Event Log Adapter
- World Flow Observer v0
- Text brief 자동화 고도화
```

---

## 6. Candidate Card 권장 포맷

각 candidate는 카드 형식으로 정리한다.

```md
## C01_t15 — Authority Pressure

### One-line Summary
경비/권위 압박이 초반 scarcity 상황에서 두 focal agent의 위축 반응을 만든다.

### What Happened
- t15 전후로 authority pressure signal이 상승했다.
- agent_09와 agent_03이 focal로 관찰되었다.
- 주변 agent들이 해당 사건의 witness 역할로 분류되었다.

### Why It Matters
- 단순 이동이나 잡음이 아니라, 이후 cohort split으로 이어지는 초기 압력 장면이다.
- story_ready candidate로 볼 수 있는 tension seed를 제공한다.

### Evidence
| Evidence Type | Source |
|---|---|
| tick | 15 |
| candidate_id | C01_t15 |
| use_mode | story_ready |
| strongest_lens | person / group / event |
| source signals | ... |
| involved agents | agent_09, agent_03, ... |

### Provenance
- Source-derived:
  - candidate tick
  - focal agents
  - core signal
- Inferred:
  - authority pressure interpretation
  - witness role
- Not used:
  - visual staged movement

### Caveat
이 brief는 source observer data에 기반하지만, 완성형 story가 아니라 candidate interpretation이다.
```

---

## 7. 포트폴리오 포지셔닝

## 7.1 프로젝트 소개 문장

영문:

```text
WITNESS is an observer system for simulated multi-agent worlds. It detects meaningful event candidates from world-state changes and produces evidence-backed observer briefs with provenance.
```

국문:

```text
WITNESS는 다중 에이전트 세계에서 발생한 상태 변화와 사건 흐름을 관찰하고, 의미 있는 사건 후보를 근거 기반 리포트로 정리하는 시스템입니다.
```

## 7.2 포트폴리오 핵심 메시지

```text
I initially explored pixel-based visualizations, but traceability audits showed that visual staging introduced unsupported interpretation. I pivoted to evidence-backed observer briefs to preserve grounding and system trust.
```

국문 요약:

```text
초기에는 픽셀 기반 시각화를 시도했지만, traceability audit 결과 visual staging이 근거 없는 해석을 일부 포함한다는 문제가 드러났다. 그래서 MVP 단계에서는 시스템 신뢰도를 보존하기 위해 evidence-backed observer brief로 전환했다.
```

## 7.3 포트폴리오에서 강조할 역량

- 시스템 설계
- simulation-to-report pipeline
- agent/event/state modeling
- observation layer 설계
- provenance / traceability 기준 수립
- 실험 결과에 따른 제품 방향 전환
- visual prototype의 실패를 검증 가능한 의사결정으로 정리한 점

---

## 8. Visual Track 처리 방침

## 8.1 Freeze Decision

Visual track은 다음 상태로 보존한다.

```text
Pixel World Static: archived / failed as primary visual
Pixel Scene Director: frozen, PW-SC-B
Pixel Event Playback: frozen, VT-B
WVT Audit: retained as evidence of traceability-first decision
```

## 8.2 Visual을 완전히 버리지 않는 이유

Visual track은 다음 가치가 있다.

```text
- product exploration 기록
- medium mismatch 검증 사례
- traceability audit 사례
- portfolio appendix
- future visual-ready event log 설계 근거
```

## 8.3 Visual을 메인으로 쓰지 않는 이유

```text
- 사용자 직관성 부족
- 영어/internal debug UI 혼재
- staged-only 비중 존재
- world flow보다 cutscene mock처럼 보임
- 현재 포트폴리오 메인 가치와 어긋남
```

---

## 9. 다음 구현 계획

## Phase 11 — Text-first Observer Brief

### 목표

WITNESS의 핵심 가치를 텍스트 리포트로 정리한다.

### 산출물

```text
scripts/report/build_observer_brief.py
docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md
docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md
docs/visual/VISUAL_TRACK_FREEZE_DECISION.md
docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md
```

### 구현 순서

1. 기존 observer/candidate data 구조 확인
2. peter_scarcity_baseline candidate 3개를 brief card로 변환
3. evidence/provenance 필드 추출
4. markdown report builder 작성
5. brief 문서 생성
6. visual freeze decision 문서 작성
7. portfolio case study 작성
8. demo script 5분 버전 작성
9. 전체 INDEX / progress / lessons 업데이트
10. engine/observer tests 재확인

---

## Phase 12 — Provenance Table 강화

### 목표

각 candidate의 source-backed 정도를 텍스트 리포트에서 명확히 보여준다.

### 산출물

```text
docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md
scripts/report/build_provenance_table.py
```

### 포함 항목

```text
- candidate_id
- tick / tick_range
- use_mode
- strongest_lens
- agents involved
- source signals
- source-derived facts
- inferred interpretation
- unsupported / not visualized
- confidence / caveat
```

---

## Phase 13 — Portfolio Package v1

### 목표

WITNESS를 외부 공유 가능한 포트폴리오 패키지로 정리한다.

### 산출물

```text
docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md
docs/portfolio/WITNESS_OBSERVER_BRIEF_SAMPLE.md
docs/portfolio/WITNESS_VISUAL_EXPERIMENT_APPENDIX.md
docs/portfolio/WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md
docs/portfolio/WITNESS_RESUME_BULLETS_FINAL.md
```

### 구성

1. Problem
2. System Architecture
3. Observer Layer
4. Candidate Extraction
5. Evidence-backed Brief
6. Visual Experiment + Pivot
7. Results
8. Lessons
9. Next Step

---

## Phase 14 — Engine Event Log Adapter 설계 유지

Text-first로 전환하더라도 visual을 영구 폐기하지 않는다.

향후 visual을 다시 살리려면 다음이 먼저 필요하다.

```text
Engine Event Log Adapter
→ visual-ready world_flow_events_v1
→ persistent actor state
→ source-derived movement / action / state delta
→ World Flow Observer
```

하지만 이 작업은 현재 포트폴리오 메인 산출물 이후로 미룬다.

우선순위:

```text
1. Text-first Observer Brief
2. Portfolio Case Study
3. Provenance Table
4. Engine Event Log Adapter 설계 유지
5. Visual 재도전 여부 판단
```

---

## 10. 금지 사항

Text-first 전환 후에도 다음은 금지한다.

```text
- story renderer 재개 금지
- 감성 소설 출력 중심으로 회귀 금지
- visual polish 추가 금지
- PEP candidate 확장 금지
- 새 anchor 금지
- 새 scenario 금지
- 새 engine metric 금지
- player intervention 금지
- playable 구현 금지
- timeline scrub 금지
- Phaser / React / PixiJS 도입 금지
- 외부 asset 도입 금지
```

허용되는 작업:

```text
- observer brief 생성
- evidence table 생성
- provenance/caveat 정리
- portfolio 문서화
- visual freeze decision 문서화
- demo script 정리
```

---

## 11. 평가 기준

## 11.1 Text-first Demo 성공 기준

```text
TF-A:
- candidate 3개가 각각 근거 기반으로 설명됨
- story_ready 판단 이유가 명확함
- source-derived / inferred 구분이 있음
- 포트폴리오용 case study로 바로 사용 가능

TF-B:
- 리포트는 가능하지만 evidence/provenance가 약함
- 일부 candidate 설명이 추상적임
- 추가 table/format 보강 필요

TF-C:
- 텍스트도 story renderer처럼 보임
- system value보다 narrative output처럼 보임
- observer/candidate 구조가 드러나지 않음
```

## 11.2 포트폴리오 성공 기준

```text
PF-A:
- 5분 설명 가능
- 시스템 구조가 명확함
- visual pivot이 실패가 아니라 합리적 판단으로 보임
- AI product / simulation / agent system 직무에 연결 가능

PF-B:
- 자료는 있으나 메시지가 분산됨
- visual 실패처럼 보일 위험 있음
- case study narrative 정리 필요

PF-C:
- 그냥 여러 실험을 벌인 프로젝트처럼 보임
- 핵심 가치가 불명확함
```

---

## 12. 다음 세션용 실행 프롬프트

```text
WITNESS는 Visual-first 확장을 중단하고 Text-first Observer Brief 중심으로 전환한다.

현재 상태:
- Pixel World Static: 보류
- Pixel Scene Director: PW-SC-B frozen
- Pixel Event Playback: VT-B frozen, 72.1% source-backed / 27.9% staged-only
- Engine + Observer + Curation은 안정

결정:
비주얼은 포트폴리오 appendix로 보존한다.
메인 산출물은 Evidence-backed Observer Brief로 전환한다.
story renderer로 회귀하지 않는다.

다음 작업:
Phase 11 — Text-first Observer Brief 구현.

산출물:
1. scripts/report/build_observer_brief.py
2. docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md
3. docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md
4. docs/visual/VISUAL_TRACK_FREEZE_DECISION.md
5. docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md

원칙:
- story renderer 금지
- 감성 소설 금지
- candidate/evidence/provenance 중심
- source-derived / inferred / caveat 명확히 구분
- visual track은 appendix로만 사용
- PEP 확장 금지
- 새 anchor/scenario/metric 금지

목표:
WITNESS를 “다중 에이전트 세계의 상태 변화와 사건 후보를 관찰하고 근거 기반 리포트로 정리하는 시스템”으로 포트폴리오에 제시한다.
```

---

## 13. 최종 판단

비주얼을 시도한 것은 잘못이 아니다.

오히려 이번 visual track은 다음을 밝혀냈다.

```text
- 예쁜 화면보다 source traceability가 더 중요하다.
- 현재 engine output은 아직 visual-ready world flow가 아니다.
- hand-authored visual staging은 포트폴리오 신뢰도를 떨어뜨릴 수 있다.
- WITNESS의 현재 강점은 observer/candidate/provenance 구조다.
```

따라서 지금 방향 전환은 후퇴가 아니다.

```text
Visual-first prototype
→ Traceability audit
→ Text-first Observer Brief
```

이 흐름 자체가 WITNESS의 포트폴리오 스토리다.

