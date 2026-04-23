# v0.5 논문 Outline — Witness Engine Research Prototype

> **잠정 제목**: "Trigger-Mediated Hazard-Driven Simulator for Historical Biographical Events: A Validation Framework"
>
> **목적**: 34 iteration을 학술적으로 봉인. 8-10개 핵심 발견으로 narrative 구성.

---

## Abstract 초안

Agent-based simulations of historical biographical events face a central validation problem: if models generate plausible outcomes, how do we distinguish genuine emergent causality from well-tuned pattern matching? We present **Witness**, a multi-agent hazard-driven simulator that models two distinct scenarios — Peter (4 agents, 500 ticks, passion narrative) and Van Gogh (3 agents, 150 ticks, Arles period) — using a shared symbolic engine. We introduce a **seven-layer validation framework** combining pattern-oriented modeling (POM), counterfactual ablation, event-relative checkpointing, partial holdout forecasting, explanation faithfulness via per-agent removal, cross-scenario isomorphism via KS test, and behavioral rate regression. Key findings: (1) arrest events emerge spontaneously in 100% of runs with no hardcoded timing; (2) Judas disillusionment acts as a dominant proximal driver (Cohen's d = -6.87, permutation p < 0.001); (3) behavioral rate signals outperform state signals as leading indicators at early horizons; (4) both scenarios exhibit a single rare-action bottleneck pattern (Phi > 0.95) — *sword_drawn* in Peter, *self_harm* in Van Gogh — suggesting structural isomorphism; and (5) normalized event timing distributions differ significantly between scenarios (KS D = 0.567, p < 0.01), supporting a **dual-layer hypothesis** where deep behavioral structure is shared but surface dynamics differ. We release the framework as a research prototype validated across 450+ tests and position it as groundwork for subsequent learned-drive extensions.

---

## 섹션 구조

### 1. Introduction (0.5p)
- 문제: biographical ABM의 검증 공백
- 접근: trigger-mediated, hazard-driven, multi-layer validation
- 기여: 7-layer framework + 2-scenario isomorphism + 재사용 가능한 검증 프로토콜

### 2. Related Work (0.5p)
- ABM validation: Grimm ODD, POM (Grimm et al.), docking
- Agent-based history: Epstein, Axtell
- Trigger/hazard systems in simulation
- Why Witness is different: symbolic + validated + cross-scenario

### 3. The Witness Engine (1.5p)
- 3.1 4-layer architecture (universal engine / domain / era / biography pack)
- 3.2 State model (fast emotion + slow irreversible)
- 3.3 Hazard-driven Poisson events
- 3.4 Trigger system (agent state + action → event)
- 3.5 Engine/content separation (0 hardcoding, 자동 검증)

### 4. Scenarios (0.5p)
- 4.1 Peter (4 agents, 500 ticks): Judas/Caiaphas/Crowd arrest scenario
- 4.2 Van Gogh (3 agents, 150 ticks): Gauguin departure scenario

### 5. Validation Framework (2p — 핵심)

**5.1 Pattern-Oriented Modeling (POM)**
- Peter 7 patterns, VG 5 patterns
- Current rules: 47.5% all_pass (n=40, bootstrap CI [32.5%, 62.5%])
- Phi analysis → bottleneck discovery

**5.2 Counterfactual Ablation**
- Judas removal: spontaneous arrest 100% → 0%
- Cohen's d = -6.87, permutation p < 0.001
- Parametric + non-parametric agreement

**5.3 Event-Relative Checkpointing**
- Tick-bound → event-relative: 35.5% → 80.3% match rate
- Why emergent timing breaks fixed checkpoints

**5.4 Explanation Faithfulness**
- Causal chain agent mention ↔ ablation impact: Spearman ρ = 1.0 (n=30)
- Non-mentioned agents have no impact

**5.5 Partial Holdout Forecast (External Validity)**
- Train/test split: disill@150 train 83%, test 88.9% (overfit gap -5.6%)
- Withdraw rate: 5-fold CV mean 72%, std 8.4%

**5.6 Cross-Scenario KS Test**
- Normalized arrest/departure tick: KS D=0.567, α=0.01 significant
- Surface timing distributions genuinely differ

**5.7 Behavioral Rate vs State Signal**
- Action count regression → all r > 0 (time confound)
- Action rate regression → withdraw r = -0.942 (leading indicator)
- Noise-robust (r ∈ [-0.98, -0.85] across noise=[0, 0.2])

### 6. Key Findings (1.5p)

**6.1 Emergent Event Generation**
- 100% spontaneous rate (n=100), mean arrest 199 ± 42, no bimodality (BIC Δ=-8.94)
- Arrest trigger CV=0.21 vs hazard CV=0.85 (dual stochasticity)

**6.2 Asymmetric Causation**
- Judas disill: 180 tick sensitivity
- Peter total state: 21 tick sensitivity (1/9)
- Peter = witness, Judas = proximal driver

**6.3 Cross-Scenario Structural Isomorphism**
- POM bottleneck pattern in both (Phi>0.95)
- Counterfactual role structure (driver + buffer)
- Behavioral signal identity (driver aggressive action rate)
- Emotional peak order (hope trough → grief peak → fear peak)

**6.4 Cross-Scenario Difference**
- KS test on normalized timing: D=0.567 (p<0.01)
- Decision window position differs (Peter 20-40%, VG 60-80%)
- **Dual-layer**: deep structure shared, surface dynamics scenario-specific

**6.5 Linear + Discrete Trigger Dynamics**
- Disill trajectory Linear R²=0.998 (≫ sigmoid 0.966, exp 0.784)
- 불연속성은 threshold trigger에서만 발생
- **"Linear accumulation + threshold-triggered regime switch"**

**6.6 Stable Attractor, Not Chaos**
- Initial perturbation (±0.5): effect 38 ticks
- Seed variance: std 42.8 ticks
- Perturbation < seed noise → stable attractor

**6.7 Terminal Saturation (해석 주의)**
- Judas domain fields: 10.0 ± 0.00 across n=30
- **Model structural artifact** (scale ceiling + rule topology)
- NOT claim: historical inevitability

**6.8 Behavioral Signal Precedence**
- Judas withdraw rate @ tick 100: 83.3% accuracy (2-class)
- Same HOLDOUT state-based: 63%
- VG parallel: gauguin critique rate r=-0.92
- **행동이 상태보다 선행하는 leading indicator**

### 7. Discussion (1p)

**7.1 Validation Framework Reusability**
- 34 iteration 중 24개 (70%)가 향후 학습 엔진 전환 시에도 재사용 가능
- Framework is the primary contribution, not specific results

**7.2 Limitations**
- No learning: rules hand-crafted
- Life fragment (50일) not full biography
- 2 scenarios insufficient for strong universality
- External dataset docking absent
- Human baseline comparison absent

**7.3 Methodological Notes (정직성)**
- "Phase transition"은 local gap 단축일 뿐 global dynamic은 linear
- "Terminal convergence ≠ historical inevitability" — model saturation
- "Structural isomorphism"은 2 scenarios로 주장 가능한 수준까지만

### 8. Future Work (0.5p)

- Latent Drive Bottleneck (v1.0)
- Relational graph extension (v1.1)
- Phase-linked life architecture (v1.2)
- Third scenario (협상형/정치형)
- Weak preference inference (v1.3)
- Narrative Witness layer (v2.0)

### 9. Conclusion (0.3p)

Witness demonstrates that multi-agent hazard-driven simulation of historical biographical events, when paired with a seven-layer validation framework, can produce emergent outcomes with verifiable causal structure and cross-scenario regularities. The primary contribution is not the specific findings but the **reusable validation protocol** that positions learned extensions on a solid baseline.

---

## 핵심 Figure 후보 (8개)

1. **Architecture diagram** — 4층 구조 + trigger/hazard flow
2. **POM bottleneck phi matrix** — Peter (sword_drawn Phi=0.95) ↔ VG (self_harm Phi=1.0)
3. **Counterfactual ablation bar chart** — full vs no-Judas vs no-Caiaphas vs no-Crowd spontaneous rates
4. **Spearman correlation heatmap** — disill@various ticks vs arrest_tick
5. **Linear trajectory fit** — disill over time with linear/exp/sigmoid overlay
6. **KS test CDF plot** — Peter normalized vs VG normalized
7. **Behavioral signal scatter** — withdraw rate vs arrest_tick with r=-0.94
8. **Emotional arc** — Peter fear/grief/hope arrest-relative (0, +25, +75 peaks)

---

## 작성 전 체크리스트

- [ ] 용어 최종 감사 ("phase transition" 0건, "historical inevitability" 0건)
- [ ] 8-10 핵심 발견만 narrative로, 중복 상관 분석 제거
- [ ] Universal 주장 언어 완화 (2 scenarios only)
- [ ] Limitations 섹션에 external validity 공백 명시
- [ ] Figure 재현 스크립트 repo 공개

---

## 저널 후보

- **JASSS** (Journal of Artificial Societies and Social Simulation) — ABM 주류
- **Social Science Computer Review** — 계량 사회과학
- **Digital Humanities Quarterly** — 역사/인문 교차
- 또는 arXiv preprint 먼저 → 피드백 수집 후 저널 결정

---

**Status**: Outline 완료. Draft 작성 1-2개월 예상. 용어 교정 및 Figure 생성은 v1.0 설계와 병렬.

**2026-04-19 업데이트**: 초안이 `PAPER_DRAFT_V06.md` (319 lines, §1–§9 prose + Appendix A/B/C + References)로 확장됨. 비제출 draft 상태 (수치는 repository 최신 상태, 일부 archived 테스트의 수치는 유지), 문헌 추가 및 figure 실제 렌더는 다음 단계.
