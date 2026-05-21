# WITNESS — Application Resume Bullets

> 이력서 / LinkedIn / 자기소개서용 bullet 모음. 직무별 / 한영 / 길이별 변형. 본 doc은 *재사용 가능한 문장 라이브러리*.

---

## 0. 사용 원칙

- 한 application에 *모든 bullet 다 넣지 않음*. 직무별 강조점에 맞는 3-5개만 선택.
- 숫자는 *항상 포함* (2,640+ tests, 3 anchors, 5-seed, 0 deps 등) — 없으면 임팩트 약함.
- 동사는 *능동형* (designed, built, implemented, validated). "I made"가 아닌 "Designed and built".
- "AI 이야기 생성기" / "story generator" / "religious simulator" 등 forbidden phrasing은 [INTERNAL_TO_EXTERNAL_TERMS.md](INTERNAL_TO_EXTERNAL_TERMS.md) §13 참조.

---

## 1. 핵심 숫자 (모든 bullet에서 활용)

| 항목 | 값 |
|---|---|
| Unit tests | **2,640+** (97%+ coverage; +800 since Phase 3.05/3.1 prep + Rubric directive) |
| Architecture | **4-layer** (engine → observer → candidate pipeline → visual explorer) |
| Scenarios | **3** (Peter, Van Gogh, Talleyrand — same engine, content-only differences) |
| Cross-seed | **5 seeds × 200 ticks** (configuration sensitivity validation) |
| Visual explorer | **vanilla JS + SVG, 0 external dependencies, ~700 lines** |
| Engine throughput | **~1,000-1,300 ticks/sec** per scenario |
| Salience tag types | **8** (cohort split, saturation lock, agent state shift, etc.) |
| Curation modes | **3** (suitable for narrative review / observation only / low-activity hold) |
| Self-evaluation rules | **8** (anti-bias engineering framework) |
| Anchors | **3** (peter_scarcity_baseline / peter_scarcity_triple / vangogh_sacred_baseline) |
| Phase 3.1 baselines | **3 targets** (A: seed-genre fit / B: episode intensity / C: ranked top-K) — all No-ML weighted score + portfolio assets, 외부 의존 0 |
| Rubric directive | **29 cycle** evolution — 4-Axis Discovery Candidate Classifier (8-step flowchart, review §2.3/§2.4/§2.5/§2.6/§3/§5/§H8 all validated, 124+ rubric tests). Rule #14 (학습 loss 0) + scalar 합산 0 + uncalibrated_phase3_placeholder 명시. |
| Doc-reality automation | **registry + regex dual** (cycle 33-38) — 130 internal markdown links auto-verified across docs/portfolio + docs/plans, 0 broken |

---

## 2. AI / ML Engineer 지원용

### 2.1 한국어 — 짧은 버전 (3 bullet)

- **에이전트 기반 시뮬레이션의 평가 파이프라인 설계** — 2,640+ unit test 위에 single-seed bias를 명시적으로 다루는 8-rule self-evaluation 프레임워크 구축. configuration sensitivity는 cross-seed (5 seeds × 200 ticks) 시각화로 직접 검증. **4-Axis Discovery Candidate Classifier** (29 cycle 진화) — Rule #14 (학습 loss 0) + scalar 합산 0 + uncalibrated threshold 명시로 fake claim 회피.
- **4-layer additive architecture** (simulation → observer → curation → visualization) — 도메인 하드코딩 금지를 grep으로 검증, schema versioning (v1 + cross_seed_v1) append-only 정책.
- **Anti-bias engineering** — null hypothesis 선언, falsifiability criterion, 5+ seed 앙상블을 sensitivity claim의 필수 조건으로 명문화. ML evaluation pipeline에 직접 이식 가능.

### 2.2 한국어 — 긴 버전 (5 bullet)

- **에이전트 기반 시뮬레이션의 평가 파이프라인 설계 및 구현** — 12-에이전트 hazard-driven Poisson 시뮬레이션 위에 8-rule self-evaluation 프레임워크 구축. single-seed conditioning bias, falsifiability criterion 누락 등 ML 평가에서도 흔한 함정을 시스템적으로 차단.
- **4-layer additive architecture** — simulation engine, observer/snapshot layer, candidate extraction/curation, visual explorer로 분리. 각 layer는 *additive* (이후 layer가 이전 layer 수정 안 함). 도메인 하드코딩 금지를 grep으로 자동 검증.
- **Cross-seed configuration sensitivity validation** — 동일 configuration × 5 seeds → REC 3 / PARTIAL 1 / SAT 1 outcome 분포 직접 가시화. single-seed run의 함정을 시각으로 막음.
- **Schema versioning + data contract** — v1 (single-run) + cross_seed_v1 (multi-seed aggregate) append-only 정책. ML feature store / dataset versioning 패턴과 동형.
- **테스트 및 코드 품질 엔지니어링** — 2,640+ pytest, 97%+ coverage, ruff + mypy 0 errors, 3-tier 실행 (fast / domain / full).

### 2.3 English — short (3 bullet)

- **Designed an evaluation pipeline for an agent-based simulation system** — built an 8-rule self-evaluation framework on top of 2,640+ unit tests that explicitly addresses single-seed conditioning bias; cross-seed validation (5 seeds × 200 ticks) directly visualizes configuration sensitivity.
- **Implemented a 4-layer additive architecture** (simulation → observer → curation → visualization) with domain-hardcoding prohibition (grep-verified) and append-only schema versioning (v1 + cross_seed_v1).
- **Anti-bias engineering framework** — codified null-hypothesis declaration, falsifiability criteria, and 5+ seed ensemble requirements for sensitivity claims; pattern transfers directly to ML evaluation pipelines.

### 2.4 English — long (5 bullet)

- **Designed and implemented an evaluation pipeline for a 12-agent hazard-driven Poisson simulation** — built an 8-rule self-evaluation framework that systematically addresses single-seed conditioning bias and missing falsifiability criteria — failure modes common in ML evaluation as well.
- **Architected a 4-layer additive system** — simulation engine → observer/snapshot layer → candidate extraction/curation → visual explorer. Each layer is additive (later layers don't modify earlier). Domain-hardcoding prohibition is grep-verified; engine layer doesn't know which scenario it's running.
- **Built a cross-seed configuration sensitivity validation pipeline** — same configuration × 5 seeds produces REC 3 / PARTIAL 1 / SAT 1 outcome distribution, directly visualized through small-multiples view. Forces the user to see the distribution rather than trust a single seed.
- **Schema versioning + data contracts** — v1 (single-run) + cross_seed_v1 (multi-seed aggregate) with append-only migration policy. Pattern is isomorphic to ML feature store / dataset versioning.
- **Test and code quality engineering** — 2,640+ pytest with 97%+ coverage on critical modules, ruff + mypy with 0 errors, 3-tier test execution (fast / domain / full).

---

## 3. Simulation Engineer 지원용

### 3.1 한국어 — 짧은 버전

- **다중 에이전트 hazard-driven 시뮬레이션 엔진 설계** — 12 에이전트, 3 그룹, 200 tick 단위, ~1,000-1,300 ticks/sec 성능. P(event) = 1 - exp(-h·dt) Poisson process.
- **Cross-scenario universality** — 동일 엔진 코드로 Peter, Van Gogh, Talleyrand 3 시나리오 실행 (content-only 차이). 엔진 layer는 어떤 시나리오를 돌리는지 모름.
- **Pattern-Oriented Modeling (POM) 검증** — bottleneck 탐지 (sword_drawn Phi=0.951), counterfactual ablation, configuration sensitivity 직접 가시화.

### 3.2 한국어 — 긴 버전

- **다중 에이전트 hazard-driven 시뮬레이션 엔진 설계 및 구현** — Python 3.11+ + Pydantic schema validation, 12 에이전트 × 3 그룹 × 200 tick, ~1,000-1,300 ticks/sec, ~2 MB memory 풋프린트.
- **4-layer additive architecture** — simulation engine, observer/snapshot, candidate extraction/curation, visual explorer 완전 분리. 엔진에 도메인 하드코딩 금지 (grep으로 자동 검증), schema versioning으로 layer 간 contract 보장.
- **Cross-scenario universality** — 동일 엔진 코드가 Peter (수난-부활-승천), Van Gogh (회화 활동), Talleyrand (정치 협상) 3 시나리오를 돌림. content/[scenario]/ 데이터 변경만으로 새 시나리오 추가 가능.
- **검증 프레임워크** — Pattern-Oriented Modeling (POM) all-pass 47.5% [32.5, 62.5], counterfactual ablation (Cohen's d=-6.87, p<0.001), Spearman ρ=1.0 explanation faithfulness, cross-seed sensitivity (REC/PARTIAL/SAT 분포).
- **단일 seed bias 차단** — sensitivity ratio가 headline claim이면 5+ seed 앙상블 필수로 명문화 (8-rule self-evaluation framework H8). cross-seed visual로 distribution을 강제 표시.

### 3.3 English — short

- **Designed a hazard-driven multi-agent simulation engine** — 12 agents × 3 groups × 200 ticks at ~1,000-1,300 ticks/sec, with Poisson event model P(event) = 1 - exp(-h·dt).
- **Cross-scenario universality** — same engine code runs three independent scenarios (Peter, Van Gogh, Talleyrand) with content-only differences; engine layer doesn't know which scenario it's running.
- **Pattern-Oriented Modeling (POM) validation** — bottleneck detection (Cohen's d=-6.87, permutation p<0.001), counterfactual ablation, cross-seed sensitivity visualization.

### 3.4 English — long

- **Designed and built a hazard-driven multi-agent simulation engine** — Python 3.11+ with Pydantic schema validation; 12 agents × 3 groups × 200 ticks at ~1,000-1,300 ticks/sec; ~2 MB memory footprint per scenario; Poisson event model.
- **4-layer additive architecture** — simulation engine, observer/snapshot layer, candidate extraction/curation, visual explorer. Strict no-domain-hardcoding rule in engine layer (grep-verified); schema versioning enforces inter-layer contracts.
- **Cross-scenario universality validated** — same engine runs Peter (Passion narrative), Van Gogh (creative practice), and Talleyrand (political negotiation) scenarios. New scenarios are added by dropping a content pack into `content/[name]/`, with zero engine modification.
- **Validation framework** — Pattern-Oriented Modeling all-pass 47.5% [32.5, 62.5], counterfactual ablation (Cohen's d=-6.87, p<0.001), Spearman ρ=1.0 explanation faithfulness, cross-seed sensitivity (REC/PARTIAL/SAT distribution made visible).
- **Codified anti-bias engineering** — 8-rule self-evaluation framework explicitly mandates 5+ seed ensemble for any sensitivity claim, blocking single-seed conditioning bias common in simulation reporting.

---

## 4. Game AI / NPC Systems 지원용

### 4.1 한국어 — 짧은 버전

- **다중 에이전트 state machine 설계** — 12 NPC 각자 독립 state vector (fear / hope / shame / drives), threshold-triggered regime switch (linear R²=0.998 > sigmoid 0.966) — opaque ML 아닌 해석 가능한 동역학.
- **창발적 그룹 동역학** — 개별 에이전트 룰에서 cohort split, saturation lock 등 매크로 패턴 자동 검출 (8 salience tag types).
- **Configuration-driven behavior diversity** — 동일 NPC config × seed → 다른 outcome (REC/PARTIAL/SAT). 스크립팅 없이 behavior 다양성.

### 4.2 한국어 — 긴 버전

- **다중 에이전트 state machine 설계** — 12 NPC가 각자 독립 state vector (fear, hope, shame, drives, beliefs)를 가지고 시간에 따라 변화. hazard-driven Poisson event로 stochastic 행동, threshold-triggered regime switch (linear R²=0.998).
- **창발적 crowd / cohort 동역학** — 개별 에이전트 룰만으로 그룹 수준의 cohort split, saturation lock, mood shift가 emergent하게 발생. observer layer가 8 salience tag로 자동 검출 (cohort split, saturation lock, agent state shift, world mood swing 등).
- **Configuration-driven behavior diversity** — 동일 config × 5 seeds → REC 3 / PARTIAL 1 / SAT 1 outcome. NPC 행동 다양성을 매번 스크립팅하지 않고도 확보.
- **Designer feedback tool** — vanilla JS + SVG visual explorer로 200 tick × 12 NPC의 emergent 행동을 timeline scrubbing + click-to-jump으로 빠르게 탐색. 비주얼은 "어디를 봐야 하는지", side panel은 "왜 surface됐는지"를 분리해서 제공.
- **Linear accumulation + threshold-triggered regime switch** — sigmoid (R²=0.966)보다 linear (R²=0.998)이 더 적합한 분리형 행동 모델. opaque ML이 아니라 디자이너가 tunable한 명시적 규칙.

### 4.3 English — short

- **Designed a multi-agent state machine** — 12 NPCs each maintain independent state vectors (fear / hope / shame / drives); threshold-triggered regime switch (linear R²=0.998 outperforms sigmoid R²=0.966) — interpretable dynamics, not opaque ML.
- **Emergent group dynamics** — cohort splits, saturation locks, and mood shifts emerge from individual agent rules and are auto-detected via 8 salience tag types.
- **Configuration-driven behavior diversity** — same NPC configuration × 5 seeds produces 3 distinct outcome classes (REC/PARTIAL/SAT) without manual scripting.

### 4.4 English — long

- **Designed and built a multi-agent state machine** — 12 NPCs each maintain independent state vectors (fear, hope, shame, drives, beliefs) evolving over time; hazard-driven Poisson events produce stochastic actions, with threshold-triggered regime switch (linear R²=0.998).
- **Emergent crowd / cohort dynamics** — group-level patterns (cohort split, saturation lock, mood shift) emerge from individual agent rules; an observer layer auto-detects them via 8 salience tag types (cohort split, saturation lock, agent state shift, world mood swing, etc.).
- **Configuration-driven NPC behavior diversity** — same configuration × 5 seeds produces REC 3 / PARTIAL 1 / SAT 1 outcome distribution, demonstrating behavior diversity without per-variant scripting.
- **Designer-facing inspection tool** — vanilla JS + SVG visual explorer with timeline scrubbing + click-to-jump enables rapid inspection of 200-tick × 12-NPC emergent behavior; visual surfaces "where to look", side panel surfaces "why it matters".
- **Interpretable rule design** — linear accumulation + threshold-triggered regime switch (R²=0.998 vs sigmoid R²=0.966) — designer-tunable explicit rules rather than opaque ML.

---

## 5. Data Visualization / Interactive Tooling 지원용

### 5.1 한국어 — 짧은 버전

- **Self-contained interactive simulation explorer** — vanilla JS + SVG, 0 external deps, ~700 lines, single HTML 파일. build step 없음, npm install 없음, HTTP server만 필요.
- **Multi-channel color encoding** — agent state → dot fill, group mode → zone fill, salience score → marker color (3-tier opacity), world mood → background tint. 각 channel 독립 의미.
- **Cross-seed small multiples** — 5 seeds × 200 ticks 한 화면, outcome banner로 distribution 직접 가시화.

### 5.2 한국어 — 긴 버전

- **Self-contained interactive simulation explorer 구현** — vanilla JS + SVG, 0 external dependencies, ~700 lines, 단일 HTML 파일. build step 0, npm install 0, HTTP server만 필요. 데이터 export 후 offline 동작.
- **Multi-channel color encoding system** — agent state → dot fill color, group mode → zone fill color, salience score → marker color (3-tier opacity hierarchy: low/mid/high), world mood → background tint. 4 channel이 각자 독립적으로 의미를 운반.
- **Cross-seed small multiples** — 5 seeds × 200 ticks를 한 화면에 small-multiples 패턴으로 배치. outcome distribution banner ("REC 3 · PARTIAL 1 · SAT 1")로 single-seed bias를 시각으로 차단.
- **Two-step interaction design** — visual ("어디를 봐야 하는지" — timeline marker, lane color, candidate filter)과 text ("왜 의미 있는지" — packet 패널의 rationale + signals)의 분리. click → tick jump + range overlay + 패널 동기화.
- **Visualization-for-validation pattern** — 단순 viewer가 아니라 검증 도구. cross-seed view 자체가 single-seed bias mitigation 메커니즘. salience marker는 curation pipeline이 무엇을 noteworthy로 봤는지 외부화.

### 5.3 English — short

- **Self-contained interactive simulation explorer** — vanilla JS + SVG, 0 external dependencies, ~700 lines, single HTML file. No build step, no npm install — HTTP server is the only requirement.
- **Multi-channel color encoding** — agent state → dot fill, group mode → zone fill, salience → marker color (3-tier opacity), world mood → background tint. Each channel is independently meaningful.
- **Cross-seed small multiples** — 5 seeds × 200 ticks on one screen with outcome distribution banner — directly visualizes configuration sensitivity.

### 5.4 English — long

- **Built a self-contained interactive simulation explorer** — vanilla JS + SVG, zero external dependencies, ~700 lines, single HTML file. No build step, no npm install; HTTP server is the only requirement; runs offline once data is exported.
- **Multi-channel color encoding system** — agent state → dot fill, group mode → zone fill, salience score → marker color (3-tier opacity hierarchy: low / mid / high), world mood → background tint. Four channels carry orthogonal meaning.
- **Cross-seed small multiples** — 5 seeds × 200 ticks on one screen via small-multiples pattern, with an outcome distribution banner ("REC 3 · PARTIAL 1 · SAT 1") that visually blocks single-seed bias.
- **Two-step interaction design** — visual ("where to look" — timeline markers, lane colors, candidate filter) and text ("why it matters" — rationale + signals in the packet side panel) are visually separated but causally linked. Click → tick jump + range overlay + panel sync.
- **Visualization-as-validation pattern** — the visual explorer is not just a viewer but a validation tool. Cross-seed view is itself a single-seed-bias mitigation mechanism; salience markers externalize what the curation pipeline considered noteworthy.

---

## 6. Creative AI Tooling 지원용

### 6.1 한국어 — 짧은 버전

- **Story candidate auto-curation** (LLM 미사용) — 8 mechanically-defined salience signal로 emergent 순간을 자동 surface, 3 use mode로 분류. 시스템은 quality 판정 안 함 (observer-not-evaluator).
- **Cross-seed narrative comparison** — 동일 config × 5 seeds → 5 narrative trajectory를 한 번에 비교. "what could have been" 대안 organic 표시.
- **Interpretable creative tooling** — 각 candidate의 rationale + signal + classification을 panel로 외부화. 작가/디자이너가 disagree하고 override 가능.

### 6.2 한국어 — 긴 버전

- **Story candidate auto-curation 시스템 설계** — LLM / ML 미사용. 8 mechanically-defined salience signal (cohort split, saturation lock, agent state shift 등)로 multi-agent 시뮬레이션의 emergent 순간을 자동 surface. 후보를 3 use mode로 분류 (suitable for narrative review / observation only / low-activity hold) — quality 판정 없이 categorization만.
- **Observer-not-evaluator 디자인 원칙** — 시스템이 "이게 좋은 이야기다"라고 판정하지 않음. surface + categorize는 자동, 최종 평가는 사람 reviewer. creative tooling의 over-claim을 디자인으로 차단.
- **Cross-seed narrative comparison view** — 동일 config × 5 seeds → 5 narrative trajectory를 small-multiples로 비교. "이번엔 이렇게 됐지만 다른 seed에서는 어떻게 됐을까"의 organic 답변.
- **Interpretable candidate panel** — 각 candidate에 rationale + signal + classification + location + related candidates를 표시. 작가/디자이너가 시스템 분류와 disagree하고 override 가능. 의사결정 로직이 black-box가 아님.
- **Anti-bias for creative claims** — 8-rule self-evaluation framework는 "이 출력이 최고다" 같은 single-seed-conditioned 주장을 명시적으로 경고. cross-seed view는 그 경고의 실천 도구.

### 6.3 English — short

- **Story candidate auto-curation** (no LLM) — 8 mechanically-defined salience signals auto-surface emergent moments and classify them into 3 use modes; system never judges story quality (observer-not-evaluator).
- **Cross-seed narrative comparison** — same configuration × 5 seeds produces 5 narrative trajectories side-by-side, organically surfacing "what could have been" alternatives.
- **Interpretable creative tooling** — each candidate's rationale, signals, and classification are externalized in a side panel; writers/designers can disagree and override.

### 6.4 English — long

- **Designed a story candidate auto-curation system without LLM/ML** — 8 mechanically-defined salience signals (cohort split, saturation lock, agent state shift, etc.) auto-surface emergent moments from multi-agent simulation. Candidates are sorted into 3 use modes (suitable for narrative review / observation only / low-activity hold) — categorization only, no quality verdict.
- **Observer-not-evaluator design principle** — the system does not auto-judge "this is a good story". Surfacing + categorization are automatic; final assessment is left to a human reviewer. Designed to block creative-tooling over-claim.
- **Cross-seed narrative comparison view** — same configuration × 5 seeds produces 5 narrative trajectories in small-multiples — organically answers "what could have been" alongside what actually happened.
- **Interpretable candidate panel** — each candidate exposes rationale, signals, classification, location, and related candidates. Writers/designers can disagree and override the system's classification — the decision logic is not a black box.
- **Anti-bias engineering for creative claims** — 8-rule self-evaluation framework explicitly warns against single-seed-conditioned over-claim ("this output is the best"); cross-seed view is the operational practice of that warning.

---

## 6.5 End-to-End Pipeline (시뮬레이션 + ML 통합, 2026-05-15 신규)

> 결정론적 시뮬레이션과 KoBART fine-tuning을 *하나의 파이프라인*으로 연결한 작업. 두 기술 통합 경험 강조용.

### 핵심 한 줄 (사용자 제시 안)

- **결정론적 시뮬레이션 기반 narrative 생성과 KoBART fine-tuning을 결합한 end-to-end pipeline 설계 및 구현** — 5단계 chain (시뮬레이션 → 한국어 합성 → Summary 정렬 → KoBART 추론 → 드라마 풍 출력) 한 명령 실행, 20초/run.

### 한국어 — 짧은 버전 (3 bullet)

- **End-to-end pipeline 설계**: 결정론적 multi-agent 시뮬레이션과 KoBART (한국어 BART, 32K 페어 fine-tune) 추론을 5단계 chain으로 통합. 한 명령 실행 시 시뮬레이션부터 드라마 풍 장면 생성까지 ~20초.
- **두 도메인 연결 설계**: 시뮬레이션 출력의 한국어 narrative를 KoBART 학습 형식(`<genre> Summary:` 171자 ±)으로 정렬하는 어댑터 작성. 결정론(seed 동일 → 결과 동일) + ML 추론 결합 가능성 검증.
- **정직성 시각화**: portfolio용 single-HTML (60KB, 외부 의존 0) — 5단계 다이어그램 + 6 sample runs + ✅/⚠️/📌 disclosure 섹션으로 *작동한 부분*과 *MVP 한계* (도메인 mismatch, 반복 loop) 분리 명시.

### 한국어 — 긴 버전 (5 bullet)

- **End-to-end pipeline 설계 및 구현** — 5단계 chain: (1) `PhasedSimulationWorld` 결정론적 시뮬레이션, (2) `life_arc_narrative` 한국어 timeline 합성, (3) Summary 어댑터로 KoBART 학습 형식(171자, control token) 정렬, (4) KoBART (Stage 2, 32K 페어 fine-tune, val_loss 2.95) fp16 GPU 추론, (5) 드라마 풍 장면 출력. 한 명령 실행 ~20초.
- **두 도메인 연결 문제 해결** — 결정론적 시뮬레이션 출력과 ML 학습 입력 사이의 schema gap을 어댑터 layer로 흡수. seed/genre를 CLI argument로 노출 → 매 실행 변인 분리 검증 가능.
- **MVP 한계의 정직한 disclosure** — 학습 도메인(한국 가족극) ≠ 입력 도메인(정경) → 반복 loop + 일부 hallucination. portfolio HTML에 ✅ 검증/⚠️ 한계/📌 claim 경계 3 섹션 분리. *"학습 완성"이 아닌 "MVP chain 검증"* 명시.
- **재현 가능 + 결정론 보장** — `random/numpy/torch/cuda` seed 4중 고정, 6 sample runs (seed 0~3 × fm/fs_drama) 사전 생성, JSON + MD 두 포맷 산출.
- **시각화 설계 — L46-L55 lessons 적용** — visual track 교훈 (어휘 patch ≠ 구성 fix / data-first vs UI-first / provenance gap) 명시적 인용, 데이터 두 column (Universal 입력 vs KoBART 출력) side-by-side로 변환 가시화.

### English — short (3 bullet)

- **End-to-end pipeline integrating deterministic simulation and ML fine-tuned inference** — 5-step chain: PhasedSimulationWorld → Korean narrative synthesis → Summary adapter → KoBART (Stage 2, 32K-pair fine-tune) → drama-style scene. Single command, ~20s/run.
- **Schema gap adapter** — bridged deterministic simulation output and ML training input format (`<genre> Summary: ...`, ~171 chars). Seed/genre exposed as CLI args for per-run variable isolation.
- **Honest MVP disclosure visualization** — single-HTML portfolio asset (60KB, zero external deps): 5-step diagram + 6 sample runs + ✅/⚠️/📌 sections separating *verified*, *known limitations* (domain mismatch, repetition loops), and *claim boundaries*.

### English — long (5 bullet)

- **Designed and implemented end-to-end pipeline integrating deterministic multi-agent simulation and KoBART (Korean BART) fine-tuned inference** — 5-step chain executable via single CLI command in ~20 seconds, generating drama-style scene from anchor + seed.
- **Resolved cross-domain schema gap** — built an adapter mapping deterministic simulation narrative to ML training format (171-char Korean summary with control tokens), exposing seed and genre as CLI parameters for ablation.
- **Maintained reproducibility** — 4-way seed lock (random/numpy/torch/cuda), 6 pre-built sample runs (seed 0–3 × fm/fs_drama), dual-format output (Markdown + JSON).
- **Honest portfolio surface** — 60KB self-contained HTML with three-section disclosure: validated chain operation, known limitations (domain mismatch between training data and inputs), and explicit claim boundaries (*"MVP chain verification, not trained drama generation"*).
- **Applied visual design lessons (L46–L55) from frozen visual track** — composition-first over vocabulary patches, data-first IR over UI-first cutscenes, side-by-side input/output columns making transformation auditable.

---

## 7. Common bullet (모든 직무 공통, 1-2개 추가 가능)

### Korean
- **2,640+ unit tests / 97%+ coverage on critical modules / ruff + mypy 0 errors / 3-tier 실행 (fast / domain / full).**
- **Schema versioning (v1 + cross_seed_v1) append-only 정책으로 layer 간 데이터 contract 보장.**

### English
- **2,640+ unit tests, 97%+ coverage on critical modules, ruff + mypy with 0 errors, 3-tier test execution (fast / domain / full).**
- **Schema versioning (v1 + cross_seed_v1) with append-only migration policy enforces data contracts between layers.**

---

## 8. 사용 가이드

### 한국어 application 작성 시
1. 직무에 맞는 §2-§6 중 *long version* 선택
2. 5 bullet 중 가장 강한 3-4개만 발췌
3. §7 common bullet 1개 추가 (테스트/스키마 — 신뢰성 신호)
4. forbidden phrasing ([INTERNAL_TO_EXTERNAL_TERMS.md](INTERNAL_TO_EXTERNAL_TERMS.md) §13) 점검

### English application 작성 시
1. 동일 절차, English 버전 선택
2. 동사는 *과거형* 능동 (designed, built, implemented, validated)
3. 숫자는 그대로 보존

### LinkedIn About 섹션
- Common one-paragraph: [TARGET_ROLES_AND_POSITIONING.md](TARGET_ROLES_AND_POSITIONING.md) §7 Template A/B/C 활용
- Bullet은 §2-§6에서 직무별 *short version* 3 bullet 사용

---

## 9. 금지 표현 (resume에서 사용 금지)

- ❌ "AI 이야기 생성기", "story generator", "narrative AI"
- ❌ "신학 시뮬레이터", "religious simulator"
- ❌ "그냥 만들었다", "취미로", "재미로" → "as a research project" / "internal exploration"
- ❌ "Lee directive", "Lee plan.md"
- ❌ "HARNESS H1-H8" verbatim → "8-rule self-evaluation framework"
- ❌ "Case A / B / C" → "validation result (passed / partial / failed)"
- ❌ "관찰기 ≠ 평가기" → "observer-not-evaluator design principle"
- ❌ "AI 자율" / "Claude가 만든" — *내가* 설계자임을 분명히

---

## 10. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 금지" | ✅ — bullet 라이브러리만, application 안 함 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |

---

## 11. 한 줄 요약

> **5 직무 (AI/ML, Simulation, Game AI, Data Viz, Creative AI) × 한영 × 짧은/긴 버전 = 20 set of bullets + 공통 bullet + 사용 가이드 + 금지 표현. 본 doc은 *재사용 라이브러리*, 실제 application 시 직무별 3-5 bullet 발췌.**

---

**Versioning**: v1 (this bullets) — 2026-05-01 stay-internal package.
