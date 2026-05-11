# WITNESS — Target Roles & Positioning

> 외부 포트폴리오로 제출 시 직무별 *강조할 점 / 빼야 할 점*. 본 doc은 *positioning reference* — 실제 적용은 cover letter / resume 작성 시 사용.

---

## 0. 공통 핵심 메시지 (모든 직무 공통)

> *"Built a 4-layer agent-based simulation system with a self-contained visual explorer that surfaces emergent behavior through automated curation. 2,640+ unit tests, vanilla JS visualization (zero deps), strict architectural constraints (additive layers, no domain hardcoding). Designed an 8-rule self-evaluation framework for anti-bias engineering. Cross-seed view directly visualizes configuration sensitivity."*

**공통 강조 키워드**:
- agent-based simulation
- additive layer architecture
- visualization for validation
- configuration sensitivity
- anti-bias engineering
- zero-dependency visualization

**공통으로 빼야 할 점**:
- 신학적 / 종교적 문맥 (Peter, Van Gogh = "historical figures" 정도로만)
- 한국어 directive 흔적
- "Lee가 ~", 개인명 등장 표현
- HARNESS H1-H8 verbatim (reframe 필수)
- progress.md, lessons.md 인용

---

## 1. AI / ML Engineer

### 1.1 직무 적합도
🟡 **Medium fit** — ML 모델 학습이 *없는* 시스템이므로 직접적 ML 적합성은 낮음. 하지만 *AI 시스템 설계 사고 / 평가 프레임워크 / 검증 엔지니어링*은 강하게 어필 가능.

### 1.2 강조할 점

#### Anti-bias / evaluation engineering (★★★)
> *"8-rule self-evaluation framework that explicitly addresses single-seed conditioning, confirmation bias, and verbatim spec preservation — applicable to ML model evaluation pipelines."*

#### Cross-seed sensitivity validation (★★★)
> *"Designed and built a cross-seed visualization layer that directly shows configuration sensitivity (REC/PARTIAL/SAT outcome distributions across 5 seeds). Same architectural pattern is critical for ML hyperparameter sensitivity studies."*

#### Schema versioning + data contracts (★★)
> *"v1 + cross_seed_v1 schemas with append-only migration policy — pattern transfers directly to ML feature store / dataset versioning."*

#### Architectural rigor (★★)
> *"Strict 4-layer separation: simulation engine, observer/snapshot layer, candidate extraction/curation, visualization. Each layer is additive (no modification of earlier layers) — relevant to ML pipeline design (data → features → training → eval → serving)."*

#### Multi-agent reasoning (★)
> *"Hazard-driven Poisson event system across 12+ agents with emergent state transitions — adjacent to multi-agent RL settings."*

### 1.3 빼야 할 점

- ❌ "agent-based simulation" 단독 (ML 청자에게는 게임 / 시뮬레이션 게임으로 오해 유발)
- ❌ "narrative" / "story" 키워드 (ML 직무와 무관)
- ❌ "scripture", "biographical" 같은 도메인 특화 단어
- ❌ 구체적 인물 (Peter / Van Gogh 등) — "historical figures" 정도로만
- ❌ 시각화 detail (dot, zone, timeline scrubbing) — ML 엔지니어 입장에서는 핵심 아님

### 1.4 1-line bullet (resume용)

> *"Designed an 8-rule self-evaluation framework and cross-seed sensitivity validation pipeline for an agent-based simulation system, addressing single-seed conditioning bias and configuration-driven outcome variance — patterns directly applicable to ML model evaluation."*

### 1.5 인터뷰 포인트

- **"Why no ML in this project?"** → *"This was a deliberate scope choice — the simulation surfaces emergent behavior, but quality assessment is left to a human reviewer (observer-not-evaluator principle). Adding ML scoring would conflate two roles. The next iteration could absolutely add a learned salience scorer, but that's a separate decision."*
- **"How does this transfer to ML work?"** → *"Three patterns transfer directly: (1) cross-seed sensitivity studies (single-seed bias is a major ML reproducibility issue), (2) schema versioning for evaluation pipelines, (3) anti-bias engineering — most ML evaluation reports omit falsifiability criteria."*

---

## 2. Simulation Engineer

### 2.1 직무 적합도
🟢 **High fit** — 직접적 적합성 가장 높음.

### 2.2 강조할 점

#### Multi-agent state evolution (★★★)
> *"12-agent multi-state simulation with hazard-driven Poisson event system. State accumulates fear/hope/shame across ticks; events fire when thresholds crossed; events propagate through agent interaction."*

#### Architectural rigor (★★★)
> *"4-layer additive architecture with strict constraints: no domain hardcoding in engine layer (verified via grep), API stability across versions, schema versioning. 2,640+ unit tests."*

#### Configuration sensitivity validation (★★★)
> *"Cross-seed visualization shows REC/PARTIAL/SAT outcome distributions for the same configuration — addresses the single-seed bias common in simulation reporting."*

#### Cross-scenario universality (★★)
> *"Same engine code runs Peter, Van Gogh, and Talleyrand scenarios with content-only differences. Engine layer doesn't know which scenario it's running."*

#### Performance (★★)
> *"~1,000-1,300 ticks/sec per scenario, ~2 MB memory footprint. 200-tick × 12-agent runs in <1 second."*

#### Validation framework (★★)
> *"Pattern-Oriented Modeling (POM) validation, statistical analysis (Wilson proportion, Cohen's d), bifurcation detection."*

### 2.3 빼야 할 점

- ❌ "story" / "narrative" 강조 (Simulation Engineer는 dynamics에 관심)
- ❌ 시각화 detail은 *부차적*으로만 (강조점 X, 보조 결과)
- ❌ "agent-based" 너무 게임적으로 들리지 않게: "multi-agent state simulation" 또는 "hazard-driven event simulation"

### 2.4 1-line bullet

> *"Built a 4-layer hazard-driven multi-agent simulation system (2,640+ tests, no domain hardcoding) with cross-seed sensitivity validation, demonstrating same engine code on three independent scenarios with content-only differences."*

### 2.5 인터뷰 포인트

- **"What's the engine doing?"** → 위 architecture doc Q4 답변 활용
- **"How do you validate the simulation is correct?"** → POM + cross-seed + cross-scenario universality 3-축 답변
- **"Scaling to 1000 agents?"** → 솔직히 인정 + 어떻게 마이그레이션할지 (SVG → Canvas, 데이터 export trimming, layer separation 덕에 visual layer만 교체 가능)

---

## 3. Game AI / NPC Systems

### 3.1 직무 적합도
🟢 **High fit** — agent-based + state machine + emergent behavior 모두 게임 AI의 핵심.

### 3.2 강조할 점

#### Multi-agent state machine (★★★)
> *"Each agent maintains independent state vectors (fear, hope, shame, drives, beliefs). State transitions are hazard-driven (Poisson), not scripted — emergent group dynamics arise from individual agent rules."*

#### Crowd / cohort dynamics (★★★)
> *"Group-level dynamics emerge from agent interactions: cohort splits, saturation locks, mood shifts. The 'observer layer' detects these as 8 salience tag types automatically."*

#### Configuration-driven behavior diversity (★★★)
> *"Same agent configuration produces different macro-outcomes across seeds (REC/PARTIAL/SAT) — directly relevant to NPC behavior diversity without scripting every variant."*

#### Visualization for designer feedback (★★)
> *"Visual explorer surfaces 'where to look' (timeline markers) so a designer can quickly inspect emergent behavior without reading raw logs. Pattern transfers directly to NPC behavior debugging tools."*

#### State accumulation + threshold trigger (★★)
> *"Linear accumulation + threshold-triggered regime switch (R²=0.998 vs sigmoid 0.966 in calibration). Cleanly separable behavior model — not opaque ML."*

### 3.3 빼야 할 점

- ❌ "biographical / historical figures" 강조 (Game AI 청자는 fictional 캐릭터 / fantasy 환경 익숙)
- ❌ "scripture" / "religious" 문맥
- ❌ "validation framework" 너무 학술적으로 들림 — "designer testing tool" 등으로 reframe
- ❌ "story renderer" / "narrative" 부분 (게임 회사는 자체 narrative 시스템 있음)

### 3.4 1-line bullet

> *"Built a hazard-driven multi-agent state machine where group-level dynamics (crowd shifts, saturation locks) emerge from individual agent rules, with a visual explorer that surfaces emergent moments for designer inspection — pattern directly applicable to NPC behavior debugging."*

### 3.5 인터뷰 포인트

- **"How does this differ from behavior trees?"** → *"Behavior trees are scripted decision flows. This system uses hazard rates (Poisson process) so events fire stochastically based on accumulated state. Same configuration produces different outcomes per seed — useful for NPC behavior diversity without manually scripting variants."*
- **"How would this run in a game engine?"** → *"Engine layer is pure Python with no I/O dependencies — porting to C# / C++ for Unity/Unreal is straightforward. Visualization is Web-only currently, but the data export schema is engine-agnostic."*

---

## 4. Data Visualization / Interactive Tooling

### 4.1 직무 적합도
🟢 **High fit** — visual explorer 자체가 가장 직접적인 sample.

### 4.2 강조할 점

#### Self-contained visualization (★★★)
> *"Single HTML file (~700 lines, vanilla JS + SVG, zero external dependencies). HTTP server is the only requirement — no build step, no React/D3, no npm install."*

#### Color encoding system (★★★)
> *"Multi-channel encoding: agent state → dot fill, group mode → zone fill, salience score → marker color (3-tier opacity hierarchy), world mood → background tint. Each channel is independently meaningful."*

#### Cross-seed small multiples (★★★)
> *"Cross-seed view uses small-multiples pattern (5 seeds × 200 ticks on one screen) with outcome distribution banner. Direct visualization of configuration sensitivity."*

#### Interaction design (★★)
> *"Timeline scrubbing + click-to-jump + range overlay + filter toggle + side panel. All keyboard-accessible. Designed around 'where to look' (visual scan) → 'why it matters' (text packet) two-step flow."*

#### Visualization-for-validation pattern (★★)
> *"Visualization is a validation tool, not just a viewer. Cross-seed view enforces single-seed bias mitigation; salience markers expose what the curation pipeline considered noteworthy."*

### 4.3 빼야 할 점

- ❌ Backend / engine detail은 *지원 콘텍스트*로만
- ❌ "agent-based simulation" 단독 — "interactive simulation explorer"로 reframe
- ❌ ML / AI 키워드 (이 직무에는 무관)
- ❌ Statistical detail (Cohen's d, Wilson proportion 등)

### 4.4 1-line bullet

> *"Built a self-contained interactive simulation explorer (vanilla JS + SVG, zero dependencies) with multi-channel color encoding, timeline scrubbing, and cross-seed small multiples — designed as a validation tool, not just a viewer."*

### 4.5 인터뷰 포인트

- **"Why no D3 / React?"** → *"Three reasons: zero build step (HTTP server only), zero dependency footprint (one HTML file is the entire deliverable), and offline-once-data-loaded. For an internal exploration tool, framework overhead would be a liability — D3's data binding is overkill for a fixed schema with 12 agents."*
- **"How would this scale?"** → *"SVG renders 12 dots cleanly but 1000 would need Canvas. The data export is 824 KB single-run, 275 KB cross-seed — would need trimming for larger N. Architecture is layered, so swapping the visual layer is contained."*
- **"What's the design principle?"** → *"'Where to look' (timeline markers, lane colors) and 'why it matters' (packet panel) are visually separated but causally linked. Click on a marker → see the rationale. The visual is the entry point, the text is the explanation."*

---

## 5. Creative AI Tooling

### 5.1 직무 적합도
🟡 **Medium-High fit** — creative AI 청자가 *narrative emergence + story candidate curation* 부분에 직접 관심. 단, "no ML / no LLM in loop" 명확히 해야 (creative AI = generative AI 오해 방지).

### 5.2 강조할 점

#### Story candidate curation (★★★)
> *"3-mode candidate classification (suitable for narrative review / observation only / low-activity hold) without auto-judging story quality. The system surfaces candidates; a human reviewer makes the final call. Observer-not-evaluator principle."*

#### Emergent narrative dynamics (★★★)
> *"Narrative emerges from multi-agent state interaction, not from scripted plot. Same configuration produces different story arcs across seeds — surfaces 'what could have been' alternatives organically."*

#### Visualization for creative review (★★)
> *"Cross-seed view lets a writer/designer compare 5 narrative trajectories at a glance. Timeline markers point to high-salience moments worth narrative investigation."*

#### 8 salience tag types (★★)
> *"Curation engine detects 8 salience signal types (cohort split, saturation lock, agent state shift, etc.). Each tag is mechanically defined (no ML scoring) — interpretable and tunable."*

#### Anti-bias for creative tools (★)
> *"Self-evaluation framework warns about single-seed conditioning — relevant when creative tools claim 'this is the best output'. Cross-seed view is the practice of that warning."*

### 5.3 빼야 할 점

- ❌ "AI 이야기 생성기" / "story generator" 절대 금지 — generative AI / LLM 오해 유발
- ❌ "agent-based simulation" 단독 (creative 청자에게는 게임으로 들림)
- ❌ Statistical / engineering detail 너무 많이
- ❌ Test count / coverage % (creative 청자는 다른 가치 평가 기준)

### 5.4 1-line bullet

> *"Built an emergent-narrative simulation explorer where story candidates are auto-surfaced through 8 mechanically-defined salience signals — observer-not-evaluator design (system categorizes; human reviewer decides), with cross-seed view enabling 'what could have been' narrative comparison."*

### 5.5 인터뷰 포인트

- **"Is this generative AI?"** → *"No — there's no ML or LLM in the simulation loop. Story candidates are surfaced through mechanical salience tags, not generated. The system shows you 'where in the simulation interesting things happened' so a human writer can investigate, but it doesn't write the story itself."*
- **"How is this useful for creative tools?"** → *"Creative tooling often hides its decision logic ('the AI thought this was best'). This system makes the reasoning visible (rationale + signals + classification per candidate). A creative reviewer can disagree with a candidate's classification and override it — the tool is a research assistant, not an oracle."*
- **"Why not generate the narrative directly?"** → *"Two reasons: (1) we wanted to validate the simulation dynamics first before building text generation on top, (2) auto-generation conflates two roles (surfacing salience vs. judging quality). Splitting them keeps each layer interpretable."*

---

## 6. Cross-role positioning summary

| Role | Fit | Top 3 emphasis | Top 3 omit |
|---|:---:|---|---|
| AI / ML Engineer | 🟡 | self-evaluation framework, cross-seed sensitivity, architecture | story, narrative, biographical specifics |
| Simulation Engineer | 🟢 | hazard-driven engine, additive layers, validation framework | story renderer, visual prettiness |
| Game AI / NPC Systems | 🟢 | multi-agent state machine, emergent group dynamics, designer tool | scripture, validation framework academic | 
| Data Visualization | 🟢 | self-contained HTML, color encoding, cross-seed small multiples | engine internals, statistical detail |
| Creative AI Tooling | 🟡 | candidate curation, observer-not-evaluator, no LLM in loop | "story generator" framing, agent-based 단독 |

---

## 7. Cover letter / resume framing matrix

### Matrix: which subset of capabilities to lead with

| Subset to lead with | Roles |
|---|---|
| Engine + validation | AI/ML, Simulation |
| Engine + visualization | Simulation, Game AI |
| Visualization standalone | Data Viz |
| Curation + observer principle | Creative AI |
| Architecture + tests | All (always include 2,640+ tests) |

### One paragraph templates

**Template A — Simulation/Game AI variant**
> *"WITNESS is a 4-layer hazard-driven multi-agent simulation explorer (2,640+ tests, no domain hardcoding). Group-level dynamics emerge from individual agent state transitions; an observer layer detects 8 salience signal types automatically; a visual explorer (vanilla JS + SVG, zero deps) surfaces moments for inspection. Same engine code runs three independent scenarios with content-only differences. The cross-seed view directly visualizes configuration sensitivity — same input, 5 seeds, 3 distinct outcome classes."*

**Template B — Data Viz / Creative AI variant**
> *"WITNESS is an interactive simulation explorer that surfaces emergent moments through automated curation. Self-contained HTML (vanilla JS + SVG, zero dependencies) with multi-channel color encoding, timeline scrubbing, and cross-seed small multiples. The system categorizes candidates without judging story quality (observer-not-evaluator design) — visualization shows 'where to look', side panels show 'why it matters'."*

**Template C — AI/ML Engineer variant**
> *"WITNESS includes an 8-rule self-evaluation framework that explicitly addresses single-seed conditioning bias and falsifiability — patterns I designed for an agent-based simulation system but transfer directly to ML evaluation pipelines. Cross-seed validation, schema versioning, and additive layer architecture are the three engineering principles I'd carry into ML systems work."*

---

## 8. Application-specific reframing

### When applying to a game studio
- Lead with: emergent NPC behavior, designer tool, configuration-driven diversity
- Hide: religious context, paper draft, statistical analysis depth
- Demo flow: skip Van Gogh quiet flow scene, focus on cross-seed comparison

### When applying to an ML / AI research role
- Lead with: anti-bias engineering, cross-seed sensitivity studies, schema versioning
- Hide: story candidates, narrative output, visual prettiness
- Demo flow: 5-min architecture talk + 1 cross-seed screenshot

### When applying to a data viz / creative tool company
- Lead with: zero-dependency visualization, two-step interaction (visual → text), small multiples
- Hide: backend statistics, validation framework academic depth
- Demo flow: live timeline scrubbing → candidate click → cross-seed view

---

## 9. Forbidden positioning (모든 직무 공통)

- ❌ "AI 이야기 생성기" / "auto storyteller" / "narrative AI"
- ❌ "신학 시뮬레이터" / "religious simulator"
- ❌ "게임" 단독 (interactive visualization or simulation explorer로 reframe)
- ❌ "내가 자율로 만들었다" — "designed and built" 또는 "implemented based on design specs"
- ❌ "재미로 / 취미로" — "internal exploration project" 또는 "research prototype"
- ❌ Lee directive 언급 — "design specifications" 또는 "project requirements"

---

## 10. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 작업 금지" | ✅ positioning만, application 안 함 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |
| Lee §"이번 루프는 docs/portfolio/ 아래까지만" | ✅ |

---

## 11. 한 줄 요약

> **Target roles 5개 (AI/ML, Simulation, Game AI, Data Viz, Creative AI) × 강조/생략 매트릭스 + cover letter 템플릿 3개 + 직무별 인터뷰 포인트. 본 doc은 *positioning reference*, 실제 application 시 적합한 framing 선택.**

---

**Versioning**: v1 (this positioning) — 2026-04-30 portfolio repack.
