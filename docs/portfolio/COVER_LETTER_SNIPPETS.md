# WITNESS — Cover Letter Snippets

> 직무별 cover letter 1문단 모음. 한국어 + 영어. 본 doc은 *재사용 가능한 paragraph 라이브러리*.

---

## 0. 사용 원칙

- 한 cover letter에 *모든 snippet 다 넣지 않음*. 1-2 문단만 발췌.
- 각 snippet은 *4-6 문장*, 약 100-150 단어 / 200-300자 한국어.
- 마지막 문장은 *지원 동기 / 회사와의 연결*로 ending — application 시 회사명 / 직무명 채워서 마무리.
- 숫자는 *항상* 포함.

---

## 1. AI / ML Engineer 지원용

### 1.1 한국어 (~250자)

> *지난 [N개월/년] 동안 'WITNESS'라는 개인 연구 프로젝트로 다중 에이전트 시뮬레이션 시스템과 그 평가 파이프라인을 직접 설계·구현했습니다. 12 에이전트의 hazard-driven Poisson 시뮬레이션 위에 2,640+ unit test와 8-rule self-evaluation 프레임워크를 구축했고, single-seed conditioning bias를 명시적으로 차단하는 cross-seed validation pipeline (5 seeds × 200 ticks)을 만들었습니다. 더 나아가 4-Axis Discovery Candidate Classifier를 29-cycle iteration으로 진화시켜 *학습 loss로 사용 금지 (Rule #14)* + *scalar 합산 금지* + *모든 threshold uncalibrated 명시* 같은 정직성 원칙을 시스템 contract로 코드화했습니다. 이 과정에서 anti-bias engineering이 ML evaluation pipeline에서도 동일하게 중요한 패턴임을 깊이 체감했습니다. [회사명]의 [직무명/팀] 역할은 안전하고 검증 가능한 AI 시스템을 만드는 작업이라고 이해했고, 제가 직접 설계·검증한 평가 프레임워크 경험이 직접 기여할 수 있는 영역이라고 생각합니다.*

### 1.2 English (~150 words)

> *Over the past [N months], I built a multi-agent simulation system called WITNESS as a personal research project, designing and implementing both the engine and its evaluation pipeline. On top of a 12-agent hazard-driven Poisson simulation, I built 2,640+ unit tests and an 8-rule self-evaluation framework, including a cross-seed validation pipeline (5 seeds × 200 ticks) that explicitly blocks single-seed conditioning bias. Through this work, I came to see anti-bias engineering as an equally important pattern in ML evaluation pipelines — most evaluation reports in practice omit falsifiability criteria. The [role/team] at [company] focuses on building trustworthy and verifiable AI systems, and the evaluation-framework work I designed and validated directly maps to that focus. I would bring that orientation as a contributor.*

---

## 2. Simulation Engineer 지원용

### 2.1 한국어 (~250자)

> *개인 연구 프로젝트 'WITNESS'에서 4-layer additive architecture로 다중 에이전트 hazard-driven 시뮬레이션 엔진을 직접 설계·구현했습니다. simulation engine, observer/snapshot layer, candidate extraction/curation, visual explorer가 각자 독립적으로 발전 가능한 구조로 분리되어 있고, engine layer는 도메인 하드코딩이 grep으로 검증되어 동일 코드가 베드로(수난 서사), 반 고흐(회화 활동), 탈레랑(정치 협상) 3 시나리오를 content-only 차이로 돌립니다. 2,640+ unit test, ~1,000-1,300 ticks/sec 성능, Pattern-Oriented Modeling으로 bottleneck 탐지 (Cohen's d=-6.87, p<0.001)와 cross-seed sensitivity (REC/PARTIAL/SAT 분포)를 검증했습니다. [회사명]의 시뮬레이션 작업은 [구체적 도메인]을 모델링하는 일이라고 이해했고, 동일한 architectural rigor와 검증 디시플린이 직접 기여할 수 있는 영역이라고 생각합니다.*

### 2.2 English (~150 words)

> *In my personal research project WITNESS, I designed and built a 4-layer additive multi-agent hazard-driven simulation engine. The simulation engine, observer/snapshot layer, candidate extraction/curation, and visual explorer are cleanly separated; the engine layer's no-domain-hardcoding rule is grep-verified, allowing the same engine code to run three independent scenarios (Peter, Van Gogh, Talleyrand) with content-only differences. Validated through 2,640+ unit tests, ~1,000-1,300 ticks/sec throughput, Pattern-Oriented Modeling (bottleneck detection, Cohen's d=-6.87, p<0.001), and cross-seed sensitivity analysis (REC/PARTIAL/SAT outcome distribution). I understand [company]'s simulation work involves modeling [specific domain], and the same architectural rigor and validation discipline I applied to WITNESS would translate directly to that work.*

---

## 3. Data Visualization / Interactive Tooling 지원용

### 3.1 한국어 (~250자)

> *개인 연구 프로젝트 'WITNESS'에서 vanilla JS + SVG, 0 external dependency, ~700 lines의 self-contained 인터랙티브 시뮬레이션 익스플로러를 직접 구현했습니다. multi-channel color encoding (agent state → dot fill, group mode → zone fill, salience → marker color 3-tier opacity, world mood → background tint)으로 200 tick × 12 agent의 dynamics를 한 화면에 표현하고, cross-seed view에서는 5 seeds × 200 ticks를 small multiples 패턴으로 배치해 configuration sensitivity (REC 3 / PARTIAL 1 / SAT 1) 분포를 직접 가시화했습니다. 'visual = 어디를 봐야 하는지', 'text panel = 왜 의미 있는지'의 두-단계 인터랙션 디자인이 핵심 결정이었습니다. [회사명]의 [툴/제품명]은 사용자가 복잡한 데이터를 빠르게 이해하도록 돕는 도구라고 이해했고, framework overhead 없이 의미 있는 인터랙션을 만들어본 경험이 기여할 수 있다고 생각합니다.*

### 3.2 English (~150 words)

> *In my personal research project WITNESS, I built a self-contained interactive simulation explorer in vanilla JS + SVG with zero external dependencies and ~700 lines of code. The multi-channel color encoding (agent state → dot fill, group mode → zone fill, salience score → 3-tier opacity marker, world mood → background tint) renders 200 ticks × 12 agents on a single screen; the cross-seed view uses small-multiples to visualize 5 seeds × 200 ticks side-by-side, directly surfacing configuration sensitivity (REC 3 / PARTIAL 1 / SAT 1) at a glance. The core interaction design — visual surfaces 'where to look', text panel surfaces 'why it matters' — was the key decision. [Company]'s [tool/product] helps users quickly grasp complex data; my experience building meaningful interaction without framework overhead would translate directly.*

---

## 4. Game AI / NPC Systems 지원용

### 4.1 한국어 (~250자)

> *개인 연구 프로젝트 'WITNESS'에서 12-NPC 다중 에이전트 state machine을 직접 설계했습니다. 각 NPC가 독립적인 state vector (fear, hope, shame, drives, beliefs)를 가지고 hazard-driven Poisson event로 stochastic하게 행동하며, threshold-triggered regime switch (linear R²=0.998 > sigmoid R²=0.966)로 해석 가능한 동역학을 유지합니다. 동일 NPC config × 5 seeds → REC 3 / PARTIAL 1 / SAT 1 outcome 분포로, behavior diversity를 매번 스크립팅하지 않고도 확보할 수 있음을 보였습니다. emergent group dynamics (cohort split, saturation lock 같은 매크로 패턴)는 8 mechanically-defined salience tag로 자동 검출되어, 디자이너가 timeline scrubbing으로 빠르게 inspect 가능합니다. [회사명]의 NPC 시스템은 [구체적 게임/엔진]에서 풍부한 행동을 만들어내는 일이라고 이해했고, opaque ML이 아니라 designer-tunable한 명시적 규칙으로 이를 달성한 경험이 직접 기여할 수 있는 영역이라고 생각합니다.*

### 4.2 English (~150 words)

> *In my personal research project WITNESS, I designed a 12-NPC multi-agent state machine. Each NPC maintains an independent state vector (fear, hope, shame, drives, beliefs); they act stochastically through hazard-driven Poisson events, with threshold-triggered regime switches (linear R²=0.998 outperforming sigmoid R²=0.966) producing interpretable dynamics. Same NPC configuration × 5 seeds produces REC 3 / PARTIAL 1 / SAT 1 outcome distribution — demonstrating behavior diversity without per-variant scripting. Emergent group dynamics (cohort splits, saturation locks) are auto-detected via 8 mechanically-defined salience tags, and a visual inspection tool with timeline scrubbing lets designers explore the system quickly. [Company]'s NPC systems work on [specific game/engine] — and the experience of producing rich behavior through designer-tunable explicit rules rather than opaque ML maps directly to that work.*

---

## 5. Creative AI / Storytelling Tool 지원용

### 5.1 한국어 (~250자)

> *개인 연구 프로젝트 'WITNESS'에서 LLM을 사용하지 않는 emergent narrative simulation 시스템을 직접 설계·구현했습니다. 다중 에이전트 시뮬레이션이 만들어내는 emergent 순간을 8 mechanically-defined salience signal로 자동 surface하고, 후보를 3 use mode (suitable for narrative review / observation only / low-activity hold)로 분류합니다. 핵심 설계 원칙은 'observer-not-evaluator' — 시스템이 자동으로 quality 판정을 하지 않고, 작가/디자이너가 최종 판단합니다. cross-seed view에서는 동일 configuration × 5 seeds → 5 narrative trajectory를 small-multiples로 비교해, "what could have been" 대안을 organic하게 제공합니다. 결정 로직이 black-box가 아니라 panel에 rationale + signal + classification으로 외부화되어 있어, 사용자가 disagree하고 override 할 수 있습니다. [회사명]의 [creative tool / storytelling 작업]은 [구체적 도메인]을 위한 도구라고 이해했고, interpretable + over-claim 차단 디자인 원칙이 직접 기여할 수 있는 부분이라고 생각합니다.*

### 5.2 English (~150 words)

> *In my personal research project WITNESS, I designed and built an emergent-narrative simulation system that uses no LLM. Eight mechanically-defined salience signals auto-surface emergent moments from multi-agent simulation; candidates are sorted into three use modes (suitable for narrative review / observation only / low-activity hold). The core principle is observer-not-evaluator — the system never auto-judges story quality; writers and designers make the final call. The cross-seed view compares 5 narrative trajectories side-by-side via small-multiples, organically surfacing 'what could have been' alternatives. The decision logic is not a black box: each candidate's rationale, signals, and classification are externalized in a side panel, and users can disagree and override the system's classification. [Company]'s [creative tool / storytelling work] focuses on [specific domain]; my experience designing interpretable systems that explicitly resist over-claim would translate directly.*

---

## 6. Common closer (선택) — 모든 직무에 추가 가능

### 6.1 한국어

> *WITNESS는 *공개 제품이 아니라 internal exploration*입니다. 코드 공개 결정도 의도적으로 보류 중이며, 현재는 architecture, validation framework, design rationale을 정리한 portfolio 문서로 제 디자인 의사결정을 보여드릴 수 있습니다. 면접에서 시간 주시면 5분 verbal demo + 추가 디테일을 공유드릴 수 있습니다.*

### 6.2 English

> *WITNESS is an internal exploration rather than a public product. The decision to release the code is intentionally on hold; for now, I can demonstrate my design reasoning through portfolio documents covering the architecture, validation framework, and design rationale. If we have time in the interview, I'd be happy to walk through a 5-minute verbal demo with additional detail.*

---

## 7. 사용 가이드

### 한국어 cover letter 구조 권장
```
1. 인사 + 지원 직무 명시 (1 문장)
2. 핵심 경험 — 위 §1-§5 중 1 직무 선택해서 그대로 또는 약간 수정 (1 문단)
3. (선택) 추가 경험 / 학력 / 다른 프로젝트 (1 문단)
4. 회사 / 직무와의 연결 (1 문단) — 위 snippet의 마지막 문장 활용
5. (선택) Common closer §6 — internal exploration임을 명시
6. 마무리 인사
```

### English cover letter 구조 권장
```
1. Greeting + position applied for (1 sentence)
2. Core experience — pick one of §1-§5, lightly customize (1 paragraph)
3. (Optional) Additional experience / education / other projects (1 paragraph)
4. Connection to company / role (1 paragraph) — use the closing sentence of the chosen snippet
5. (Optional) Common closer §6 — frame as internal exploration
6. Sign-off
```

---

## 8. 직무별 강조 매트릭스

| Snippet | Headline | Specific numbers | Tone |
|---|---|---|---|
| §1 AI/ML | Anti-bias evaluation pipeline | 2,640 tests, 8-rule, 5 seeds | analytical |
| §2 Simulation | Multi-agent engine + cross-scenario | 4-layer, ~1,000 ticks/sec, Cohen's d=-6.87 | rigorous |
| §3 Data Viz | Self-contained explorer + small multiples | 0 deps, ~700 lines, 5 seeds × 200 ticks | crafted |
| §4 Game AI | Multi-NPC state machine + diversity | linear R²=0.998, 5 seeds, 8 tags | designer-friendly |
| §5 Creative AI | Observer-not-evaluator + cross-seed comparison | no LLM, 3 use modes, 8 signals | thoughtful |

---

## 9. 금지 표현 (cover letter에서 사용 금지)

- ❌ "AI 이야기 생성기", "story generator", "narrative AI"
- ❌ "신학 / 종교 시뮬레이터", "religious simulator"
- ❌ "그냥 / 취미로 / 재미로" → "personal research project" / "internal exploration"
- ❌ "내가 자율로 만들었다" — "designed and built" / "implemented based on design specs"
- ❌ "Lee가 시켜서", "Lee directive", "Lee plan.md"
- ❌ "Claude / LLM이 만들어줬다" — *내가* 디자인 결정자임을 분명히
- ❌ HARNESS H1-H8 verbatim — "8-rule self-evaluation framework"
- ❌ 한국어 보존된 "관찰기 ≠ 평가기" — "observer-not-evaluator design principle"

---

## 10. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 금지" | ✅ — snippet 라이브러리만, application 안 함 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |

---

## 11. 한 줄 요약

> **5 직무 (AI/ML, Simulation, Data Viz, Game AI, Creative AI) × 한영 = 10 cover letter snippets + common closer + 사용 가이드 + 금지 표현. 본 doc은 *재사용 paragraph 라이브러리*, 실제 application 시 1-2개 발췌하고 회사명/직무명 채워 사용.**

---

**Versioning**: v1 (this snippets) — 2026-05-01 stay-internal package.
