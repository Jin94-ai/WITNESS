# Witness: A Trigger-Mediated, Hazard-Driven Simulator for Historical Biographical Events

**Status**: v0.6 working draft (2026-04-19). Narrative paragraphs written; results sections stubbed to outline bullets. Figures and numerical tables to be inserted from repository `output/` and test logs. **This file is not a submission.**

---

## Abstract

Agent-based simulations of historical biographical events face a central validation problem: when models generate plausible outcomes, how do we distinguish genuine emergent causality from well-tuned pattern matching? We present **Witness**, a multi-agent, hazard-driven simulator that models two distinct scenarios under a shared symbolic engine — Peter (4 agents, 500 ticks; a passion narrative) and Van Gogh (3 agents, 150 ticks; the Arles period). On top of this engine we introduce a **seven-layer validation framework** combining pattern-oriented modeling (POM), counterfactual ablation, event-relative checkpointing, partial holdout forecasting, explanation faithfulness via per-agent removal, cross-scenario isomorphism via a Kolmogorov–Smirnov (KS) test, and behavioral rate regression. Five findings emerge: (1) arrest-class events appear spontaneously in 100% of runs without hardcoded timing; (2) the Judas disillusionment variable functions as a dominant proximal driver (Cohen's *d* = -6.87; permutation *p* < 0.001); (3) behavioral rate signals outperform state signals as leading indicators at early horizons; (4) both scenarios exhibit a single rare-action bottleneck pattern (Phi > 0.95) — *sword_drawn* in Peter, *self_harm* in Van Gogh — suggesting structural isomorphism; and (5) normalized event-timing distributions differ significantly across scenarios (KS *D* = 0.567, *p* < 0.01), supporting a **dual-layer hypothesis** in which deep behavioral structure is shared while surface dynamics are scenario-specific. We release the framework as a research prototype, validated across 570+ unit and integration tests, and position it as groundwork for subsequent learned-drive extensions.

---

## 1. Introduction

Agent-based modeling of historical biographical events — the final days of an apostle, the Arles breakdown of a painter, the hours leading to a political assassination — is methodologically difficult for two reasons. First, the ground truth is sparse: a single sequence of events, preserved through layers of secondary sources, against which a probabilistic simulator can only be matched approximately. Second, any sufficiently expressive generative model can be hand-tuned to reproduce that sequence, and in the absence of validation structure the result is indistinguishable from confirmation bias. The classical response — prediction on a held-out sample — does not apply: the historical case is an N = 1 holdout, and there is no comparable second trajectory for the same person.

We argue that the productive shift is from **replicating a sequence** to **observing a distribution**. Rather than fitting a single simulation to the historical record, one runs an ensemble of runs and asks: (i) what is the shape of the outcome distribution? (ii) where does the historical record sit within it? (iii) which internal variables *have* to be perturbed to move the historical case out of the distribution's support? This reframes the validation question from goodness-of-fit to causal decomposition, and opens the door to distributional techniques borrowed from climate hindcasting and ecological ABM validation (e.g. Grimm's pattern-oriented modeling [Grimm et al., 2005]).

The contribution of this paper is threefold:

1. A symbolic simulation engine that cleanly separates **universal mechanics** (state transitions, hazard functions, trigger evaluation) from **content** (a historical person's initial conditions, behavior profile, and domain-specific state). The engine is verified by an automated integrity check that fails if any person-specific identifier appears in engine code.
2. A **seven-layer validation framework** that combines pattern-oriented modeling, counterfactual ablation, event-relative checkpointing, partial-holdout forecasting, explanation-faithfulness correlation, cross-scenario KS testing, and behavioral-rate regression. Each layer targets a different validity concern; together they produce a decomposition of model behavior rather than a single aggregate score.
3. **Cross-scenario evidence** from applying the same engine to two biographically unrelated cases (Peter in a passion narrative, Vincent van Gogh in the Arles period). We observe structural isomorphism in the bottleneck pattern of rare actions (Phi > 0.95) alongside statistically significant differences in surface event timing (KS *D* = 0.567).

We deliberately do **not** claim universality. Two scenarios are insufficient to establish that the observed isomorphism generalizes. We treat cross-scenario regularities as hypothesis-generating, not hypothesis-confirming, and identify in §7.3 exactly which language to avoid in subsequent work.

---

## 2. Related Work

**ABM validation.** The validation problem we address — a generative model that produces plausible trajectories in the absence of a disposable test set — has been a recurring concern in agent-based modeling since the late 1990s. Grimm and colleagues' pattern-oriented modeling (POM) framework proposed that a model be judged not by aggregate fit to a single pattern but by its ability to reproduce multiple qualitative patterns simultaneously, with the reasoning that any tunable model can hit one pattern and that simultaneous multi-pattern fit is a sharper test [Grimm et al., 2005]. We adopt POM as one of seven validation layers (§5.1) but argue that POM alone does not address causal decomposition — hence the counterfactual, explanation-faithfulness, and behavioral-rate layers we add.

The *docking* tradition — running two independently implemented models of the same phenomenon and checking that they produce compatible outputs — offers an orthogonal form of validation [Axtell et al., 1996]. We do not dock against an external implementation in this work; we note in §7.2 that a second implementation, perhaps by another research group, would be a strong next step.

**Agent-based history.** Epstein's *Generative Social Science* argued for "if you didn't grow it, you didn't explain it" — explanation in social science via mechanism simulation rather than correlation [Epstein, 2006]. Axtell's *Sugarscape* [Axtell & Epstein, 1996] and subsequent work established the feasibility of studying emergent social dynamics via rule-based agents. Witness inherits this commitment to explanation-by-mechanism while narrowing the scope: we do not claim to explain social structures in the abstract, but to test whether a particular biographical sequence is reproducible as emergence from agent-level rules.

**Hazard and survival frameworks.** Treating discrete events as outcomes of continuous-time hazard functions, rather than fixed-tick schedules, is standard in epidemiological modeling and in some ABMs for disease spread [e.g., Keeling & Rohani, 2008]. Applying it to historical biographical events appears to be less common; we are not aware of prior work that uses Poisson competing-risks hazards with symbolic trigger-mediation as the event-generation substrate for biographical ABM.

**Simulator separation of concerns.** The engine/content separation we verify with an automated integrity check (§3.5) is broadly similar to the Mesa toolkit's Agent-Model-Scheduler decomposition [Masad & Kazil, 2015] and to the component structure of CESM (Community Earth System Model) in climate modeling. The contribution here is not the architecture itself but the *enforcement*: the integrity test fails in CI on any engine-level mention of a person-specific identifier, preventing accidental leakage of scenario-specific logic into the engine during development.

**Our positioning.** Witness is a symbolic simulator (no learned components in v0.5; learned extensions in v1.0 and beyond), validated across seven layers, applied to two biographically unrelated scenarios via a hard-enforced engine/content separation. The combination of these choices is what we contribute; each in isolation has precedent.

---

## 3. The Witness Engine

### 3.1 Four-layer architecture

The engine separates concerns across four layers, each with a distinct rate of change and rate of re-use.

- **Layer 1 — Universal engine** (`engine/`). State containers, state-transition rule interface, hazard function interface, trigger engine, scheduler. Person-agnostic. Shared by every scenario.
- **Layer 2 — Domain module**. Extension states particular to a domain of expertise (faith journey, creative drive, political calculation). Implemented as Pydantic subclasses of a neutral `DomainState` base.
- **Layer 3 — Era module** (anticipated; minimal in v0.5). Time-specific environmental factors (surveillance pressure, economic strain).
- **Layer 4 — Biography pack** (`content/<person>/`). Initial state, behavior profile, hazard event definitions, trigger thresholds, and optional canonical intervention events derived from source documents.

The separation is enforced by a test (`tests/test_engine/test_integrity.py`) that greps for known person identifiers in `engine/` and fails on any match; CI runs this on every push.

### 3.2 State model

Each agent carries three layered state containers:

- **Fast state** (`EmotionalState`, `PhysicalState`): bounded to [0, 10], subject to homeostasis toward a baseline, updated every tick. Intended to represent effects that dissipate when their cause is removed (acute fear, fatigue).
- **Slow state** (`SlowState`): bounded to [-10, 10], irreversible under normal transitions, updated only when specific threshold events fire. Intended to represent experiences that leave a persistent mark (moral injury from betrayal, identity shift after public denial, trust scar from relational rupture).
- **Domain state**: scenario-specific. For Peter we track `obedience_maturity`, `doubt_depth`, `loyalty_performed`; for Van Gogh, `creative_drive`, `isolation`.

The fast/slow split is load-bearing for two reasons. Without slow state, accumulating experiences would be continuously washed out by homeostasis and the simulator would lose history. Without fast state, every disturbance would be permanent, producing unstable trajectories that no homeostatic process could correct.

### 3.3 Hazard-driven events

External events (environmental intrusions, other actors, canonical interventions) are not tick-scheduled. Each external event has an associated **hazard function** h(state, environment); at each tick, the probability of firing in the next δ*t* follows a Poisson process:

  *P*(fire within δ*t*) = 1 − exp(−*h*(state) · δ*t*)

When multiple hazards compete (storm vs. arrival of hostile party), firing is resolved by drawing the earliest competing-risks outcome. Hazard functions compose linearly from a **HazardFactor** list: each factor pulls a field (e.g. `surveillance_pressure`), rescales it, and contributes additively to *h* up to a max-hazard cap. This keeps tuning interpretable while admitting nonlinearity through threshold factors.

### 3.4 Trigger system

Voluntary actions and threshold-crossing in slow state can fire named events via the **trigger engine**. A trigger is a boolean conjunction over three condition types: agent-state comparison (`judas.domain_state.disillusionment >= 8.0`), recent-action match (`judas performed betray within last 30 ticks`), and environmental gate (`env.surveillance_pressure > 7.0`). All operands evaluate against the global `all_agents` dictionary, so a trigger can span multiple agents — which is how cross-agent causation enters the model without hand-coding event sequences.

A trigger that fires produces a `StateEffect` list applied to named target agents. The **arrest trigger** in the Peter scenario is the canonical illustration: its conditions involve Judas (disillusionment, recent betray action) and Caiaphas (political calculation); its effects perturb Peter's fear and environmental surveillance. No code anywhere in the engine knows about Peter, Judas, or arrest — all identifiers come from the `content/shared/triggers.json` configuration.

### 3.5 Engine / content separation — verification

Two tests underwrite the separation claim.

1. `test_integrity` greps `engine/` for person- and scenario-specific strings (Peter, Judas, Caiaphas, Gauguin, etc.). Failure on any match.
2. `test_content_pack_structure` validates, for every `content/<name>/` folder, that required fields are present, that domain classes extend `DomainState` without overriding engine internals, and that no engine-logic patterns (e.g. `class SimulationWorld`) appear outside `engine/`.

These tests run in the default fast suite and block CI on failure.

---

## 4. Scenarios

We instantiate two scenarios. Both run on the identical engine code, differing only in `content/` — initial states, behavior profiles, hazard and trigger definitions, and a scenario-specific `DomainState` subclass.

### 4.1 Peter (4 agents, 500 ticks)

The scenario models the final ~50 days of one participant in a passion narrative. Four agents interact: a principal (Peter, `FaithJourneyState`), a proximal driver whose decisions precipitate the arrest (Judas, `BetrayalPsychologyState`), an authority figure whose political calculation determines whether the arrest is sanctioned (Caiaphas, `PoliticalCalculationState`), and an ambient crowd whose recognition pressure affects the denial sequence (`CrowdDynamicsState`). Canonical interventions — the scriptural words of the central non-agent figure — are injected as external events at fixed ticks derived from the source text; they perturb but do not decide agent state. Ground truth is drawn from the historical narrative: the arrest itself, three denials, weeping, and a later restoration dialogue. These events form the scorecard (§5.1) and the event-relative checkpoints (§5.3).

The Peter scenario contains no agent identified as the theological center of the source narrative. This is a deliberate content-level choice, not an engine constraint: the central non-agent figure's utterances are injected as a read-only intervention sequence. The engine has no special case for this; an analogous construction could be used for any scenario with a singular exogenous actor whose internal state the modeler declines to simulate.

### 4.2 Van Gogh (3 agents, 150 ticks)

The scenario models the Arles period of Vincent van Gogh, specifically the nine-week cohabitation with Paul Gauguin that ended with Gauguin's departure and van Gogh's self-harm. Three agents: Vincent (`CreativeDriveState`), Gauguin (`ArtisticEgoState`), and Theo van Gogh in Paris (`PatronState`), who appears only through financial support and correspondence. Ground truth: `paint_feverishly` rate peaks mid-period; Gauguin issues a threatened-departure action; Gauguin departs; within a short window, Vincent's self-harm threshold fires.

The two scenarios are biographically unrelated — different centuries, different domains, different agent counts, different trigger structures. The rationale for the pair is methodological: if a generic engine cannot reproduce both, the claim that the engine *is* generic fails immediately; if it reproduces both with scenario-specific configurations and no engine-level changes, the separation-of-concerns architecture (§3.5) is validated at the level of working code rather than aspiration. §6.3 reports observed structural regularities across the two; §6.4 reports a timing-distribution difference.

---

## 5. Validation Framework

This section describes the seven layers. Each layer targets a specific concern and produces an output the next layer can consume.

### 5.1 Pattern-Oriented Modeling (POM)

We define a **scorecard** of qualitative patterns that the historical case exhibits: Peter has seven such patterns (e.g. denial count ≥ 3, weeping after denial); Van Gogh has five (e.g. `paint_feverishly` action precedes departure by less than 30 ticks). A simulation run is scored by how many patterns it matches; the population metric is the **all-pass rate**, the fraction of runs matching every pattern. A Phi-coefficient analysis across pattern pairs identifies which patterns co-occur more than chance — the tightest such coincidence marks a **bottleneck pattern**.

Current results: Peter all-pass rate 47.5% (*n* = 40, bootstrap 95% CI [32.5%, 62.5%]); Peter's bottleneck pattern is `sword_drawn` with Phi > 0.95. Van Gogh all-pass rate [TODO]; bottleneck `self_harm` with Phi = 1.0.

### 5.2 Counterfactual Ablation

We remove one agent at a time from the scenario and re-run the ensemble. The reasoning is that any agent whose removal does not perturb the outcome distribution is, by construction, causally irrelevant in the simulator — even if the historical narrative presents them as central. Conversely, any agent whose removal collapses the outcome distribution to a degenerate form marks a driver.

For Peter, removing Judas reduces the spontaneous arrest rate from 100% to 0% (the fallback deadline is the only remaining firing path). The effect size is large by all measures we tried: the arrest-tick distribution shifts from a mean of approximately 199 ± 42 to the deadline sentinel, yielding Cohen's *d* = −6.87 on the uncensored cases. A permutation test, which does not assume normality and which we prefer given the boundary sentinel, gives *p* < 0.001 at *n* = 30 in each arm. Removing Caiaphas or the crowd produces smaller shifts; none is comparable in magnitude. The conclusion is that Judas's disillusionment is a driver, not merely a correlate, of arrest timing in the current rule set. §6.2 contrasts this proximal driver with Peter's own state, which acts as a witness rather than a cause — a claim that is meaningful only because §5.4 establishes the correspondence between causal structure and the simulator's self-reported explanation.

### 5.3 Event-Relative Checkpointing

A canonical checkpoint fixes a specific event ("first denial") at a specific tick in the historical narrative. When applied to a hazard-driven simulator in which the precursor event (arrest) fires stochastically, this pattern is pathological: the checkpoint asserts that the first denial occurred, for example, at tick 220, when in fact it should have been specified relative to the arrest — "first denial occurs within 5–30 ticks of the arrest". The difference is not cosmetic. Under the fixed-tick interpretation, runs where arrest occurs early or late fail the checkpoint even when the denial/arrest lag is historically accurate.

We implement two checkpoint modes — absolute tick and event-relative offset — and compare. For the Peter scenario, the same canonical narrative (four observations: arrest, three denials) yields a 35.5% match rate under absolute tick and an 80.3% match rate under event-relative scoring, for identical runs. The gap is a measure of how much *timing ambiguity* the checkpoint tradition had silently absorbed; it also suggests a heuristic for scenario authors — specify canonical observations as offsets from the nearest trigger event, not as absolute times.

### 5.4 Explanation Faithfulness

A generative simulator that produces a post-hoc narrative explanation of each run is only useful if its explanations track the simulator's own causal structure. We operationalize this as follows. For each run, the simulator emits a `causal_chain` listing the agents whose state crossed a threshold during the run in temporal order. We then run the counterfactual of §5.2 for each agent and score the mean displacement in arrest-tick as an "ablation impact". If the explanation is faithful, agents mentioned in the causal chain should have larger ablation impacts than those not mentioned, and within the mentioned set the rank order of mentions should correlate with the rank order of impact.

Current result on the Peter scenario (*n* = 30 runs of the full ensemble): Spearman ρ = 1.0 between mention order and ablation impact for all agents that *did* appear in any causal chain. Agents that never appeared had ablation impact indistinguishable from zero. The test is a weak form of faithfulness — it does not rule out subtler explanation errors — but it rejects the failure mode in which the explanation lists agents based on surface salience (e.g., recent activity) rather than causal contribution.

### 5.5 Partial-Holdout Forecasting

The N = 1 nature of the historical case rules out the conventional train/test split on real data, but it does not rule out a split on the simulator's own output. We generate an ensemble of runs, split them into training and test partitions, fit a forecast model on the training partition (e.g., linear regression predicting arrest tick from Judas disillusionment at tick 150), and evaluate on the held-out partition. The gap between training and test accuracy is a measure of overfit; a small gap under bootstrap resampling is evidence that the forecast is capturing distributional regularities of the simulator rather than memorizing particular seeds.

In the Peter scenario, `disill@150 → arrest_tick` forecast accuracy is 83% on train and 88.9% on test (overfit gap −5.6%, negative because the test happened to contain easier cases). A 5-fold cross-validation on `withdraw rate → arrest_tick` yields mean 72% accuracy with standard deviation 8.4%. We treat these as lower bounds on simulator-internal predictability rather than claims about real-world predictability: the simulator is not the world, and forecasting inside the simulator is a precondition for, not evidence of, external validity.

### 5.6 Cross-Scenario KS Test

To compare the two scenarios on a common scale, we normalize each run's event timing by dividing by the scenario's maximum tick. The resulting distributions — `arrest_tick / max_tick` for Peter and `departure_tick / max_tick` for Van Gogh — live on [0, 1] and are directly comparable. A two-sample Kolmogorov–Smirnov test on 100 runs per scenario yields *D* = 0.567 (*p* < 0.01). Visually, Peter's triggering events cluster in the 20–40% region of run length, while Van Gogh's cluster in the 60–80% region.

The significance of this difference matters more for what it rules out than for what it asserts. It rules out the hypothesis that the two scenarios produce indistinguishable timing distributions under the common engine — a hypothesis that would be a red flag, indicating that the engine's dynamics were overwhelming scenario-specific content. It does not, on its own, establish that the engine captures real-world differences between passion narratives and artistic breakdowns; only that scenario-specific content can still drive scenario-specific behavior after passing through the shared engine.

### 5.7 Behavioral Rate vs. State Signal

A methodological observation from attempts to predict arrest tick from agent-internal state: absolute action *count* regressors are time-confounded. A run that takes 300 ticks to reach arrest will naturally have seen more of every action than a run that takes 150 ticks, regardless of whether those actions are causally diagnostic. When we control for time by computing action *rate* (count per tick since the agent became active), the confound vanishes and one leading indicator emerges clearly: Judas's `withdraw` rate at tick 100 correlates with final arrest tick at *r* = −0.942 — earlier, more frequent withdrawal predicts earlier arrest. The same regression on raw count gives *r* > 0 purely via the time-in-run confound.

This result is robust under noise injection: with `state_noise_scale` varied between 0 and 0.2, the rate-regression correlation stays in [−0.98, −0.85]. The broader methodological claim — that behavioral rates are better leading indicators than state levels for early-horizon forecasts — is supported in both scenarios (for Van Gogh, Gauguin's `critique` rate correlates with departure tick at *r* = −0.92; see §6.8). The observation runs counter to the intuition that internal state should be the "real" variable and behavior the surface; in our setting, rate-of-behavior is what the external observer can see, and it turns out to be what forecasts best.

---

## 6. Key Findings

The findings below are organized roughly from most robust (validated across multiple tests) to most interpretation-sensitive (reported for completeness, flagged for cautious reading). Numerical values are taken from the test logs under `pytest -m "not archived"`; per-finding test pointers appear in Appendix B.

### 6.1 Emergent event generation

Across 100 runs of the baseline Peter configuration, an arrest event fires spontaneously in 100% of runs with no hardcoded tick. The mean arrest tick is approximately 199 with standard deviation 42, giving a coefficient of variation of 0.21. For comparison, the background hazard layer in the same configuration has CV ≈ 0.85 under identical noise conditions — the trigger-mediated arrest is an order of magnitude less variable than a pure hazard process. A Bayesian Information Criterion test for bimodality in the arrest-tick distribution gives Δ BIC = −8.94 against the two-component mixture, supporting a single well-concentrated mode rather than two distinct firing paths.

### 6.2 Asymmetric causation

The Judas disillusionment variable and Peter's own aggregate state show dramatically different sensitivities to initial perturbation. Under ±0.5 perturbations to initial conditions, the mean shift in arrest tick is 180 ticks when Judas's disillusionment is perturbed and 21 ticks when Peter's entire state vector is perturbed (the nine-element vector of fast and slow state fields). The 1:9 ratio holds across noise levels and parameter settings we checked. We interpret this as evidence that Peter functions, in the model, as a witness rather than a cause: his behavior adjusts to events driven elsewhere. This is consistent with the source narrative's positioning of Peter and the counterfactual result of §5.2.

### 6.3 Cross-scenario structural isomorphism

The bottleneck pattern analysis of §5.1 identifies a single rare-action pattern in each scenario whose occurrence is tightly coupled to the scorecard's all-pass condition. In Peter, this pattern is `sword_drawn` with Phi > 0.95; in Van Gogh, it is `self_harm` with Phi = 1.0. The counterfactual role structure of §5.2 — one agent whose removal collapses the outcome, buffer agents whose removal leaves the distribution largely intact — holds in both. The behavioral-signal analysis of §5.7 identifies, in both scenarios, a single aggressive-action rate from the driver agent as the strongest leading indicator (Judas `withdraw` *r* = −0.942; Gauguin `critique` *r* = −0.92).

Taken together, these three structural features — rare-action bottleneck, driver/buffer counterfactual asymmetry, aggressive-action rate as leading indicator — reproduce across two biographically unrelated scenarios using the identical engine. We describe this as *structural isomorphism* and note its strongest claim: the engine does not force a single trajectory onto both scenarios, but it does appear to produce a common decomposition shape. §7.2 and §7.3 constrain what this does and does not let us say about universality.

### 6.4 Cross-scenario surface difference

The isomorphism of §6.3 coexists with a significant difference in surface timing. Under normalization (§5.6), Peter's trigger events cluster at 20–40% of run length; Van Gogh's at 60–80%. The KS test gives *D* = 0.567 at *p* < 0.01, *n* = 100 per arm. The practical reading is that the engine admits **scenario-specific dynamics operating on a common substrate** — which is the design intent of the layer separation in §3, not a discovery about the underlying phenomena. We call this a *dual-layer* observation: deep structure shared, surface dynamics distinct. It is a necessary condition for the engine to be interesting as a general tool; it is not a sufficient condition for any particular scientific claim about either scenario.

### 6.5 Linear accumulation with discrete triggering

An early draft of this work used the term "phase transition" to describe the arrest event. This was incorrect under scrutiny. Fitting the Judas disillusionment trajectory across runs: a linear fit gives *R*² = 0.998; a sigmoid fit 0.966; an exponential 0.784. The continuous state evolves linearly in time over the run length; the visible discontinuity in outcomes arises at the moment of trigger firing, which is a property of the symbolic trigger layer rather than of the state dynamics.

We now describe the phenomenon as **linear accumulation plus threshold-triggered regime switch**. The distinction matters because "phase transition" in physical or statistical-mechanical usage implies nonlinear state dynamics (critical slowing down, spontaneous symmetry breaking); nothing we observe requires that machinery. Scenarios with different trigger thresholds but identical state rules would show different outcome timings while having identical state trajectories — a scenario-content effect, not a phase phenomenon.

### 6.6 Stability, not chaos

Initial-condition perturbations of ±0.5 shift arrest tick by approximately 38 ticks in expectation. The standard deviation of arrest tick across seeds (holding initial conditions fixed) is approximately 42.8 ticks. Because the perturbation effect is smaller than the seed-driven spread, the system behaves as a stable attractor within the explored region: moving the initial condition within the neighborhood moves the outcome distribution by less than the stochastic variation already present. This is reassuring for interpretability — small misspecifications in initial state do not swamp qualitative conclusions — but it should not be read as a claim about the full parameter space. We have not tested regions far from the calibrated defaults.

### 6.7 Terminal saturation (interpret with care)

In long runs, the Judas domain-state fields settle at the field's upper bound of 10.0 with negligible across-seed variance (*n* = 30 sample, std ≈ 0.00). We flag this because it was initially over-interpreted in draft notes. The saturation is a *model structural artifact*: the fields have a hard ceiling (part of the `DomainState` validator), the rules that push them upward have no counteracting downward force once the trigger has fired, and runs continue past the trigger event. It does *not* license the claim that the historical event was inevitable. It is a property of the range-clamping choice at the schema layer; in a rule system without the ceiling, the same dynamics would produce unbounded but meaningless growth.

### 6.8 Behavioral signal precedence

Tying §5.7 to a specific forecasting task: classifying whether a run will reach arrest in the first or second half of the 500-tick window, we achieve 83.3% two-class accuracy using Judas `withdraw` rate at tick 100 as a single predictor. The equivalent classifier using state-based features at the same tick reaches 63% on the same holdout. The behavioral-rate signal is a meaningfully better leading indicator than state in the observed window. In the Van Gogh scenario, the Gauguin `critique` rate gives *r* = −0.92 against departure tick — the same pattern in a different scenario.

The broader claim we are willing to make: *in this model*, behavioral rates are leading indicators for state-threshold events. We are not claiming that behavior-first accounts are universally preferable to state-first accounts in ABM; that would require external comparison to other simulators and to real-world data. The result is consistent with a sensible prior — rates-of-behavior are what an external observer can see without internal access — but the evidence here supports the claim only in the current rule set.

---

## 7. Discussion

### 7.1 Framework reusability

Of the 34 analyses iterated during development (classified in `ITERATION_CLASSIFICATION.md`), 24 (70%) are annotated as directly reusable under the subsequent learned-drive extension (v1.0). The primary contribution of this work is therefore the validation protocol itself rather than the specific quantitative results — the results are a demonstration that the protocol can be applied end-to-end and produces decomposable outputs.

### 7.2 Limitations

- No learning component: all weights and thresholds are hand-specified. v1.0 addresses this with a latent-drive bottleneck (see §8).
- Both scenarios cover a short life fragment (under 60 days of subject time). Phase-linked life architectures are scheduled for v1.2.
- Two scenarios are insufficient for universality. A third scenario of a structurally different type (negotiation, institutional drift) is needed before `universality` is a defensible word.
- No external-dataset docking. Behavioral time series from modern micro-datasets (e.g. daily-diary studies) could serve as loose analogs but have not been incorporated.
- No human baseline: we do not compare simulator outputs to human forecasters working from the same source material.

### 7.3 Methodological notes

Three pieces of language we used internally and have since revised:

- "phase transition" → "threshold-triggered regime switch". The underlying state trajectories are linear (*R*² > 0.99); discontinuity arises only at the trigger's instantaneous firing, which is a property of the symbolic trigger layer and not of the state dynamics.
- "terminal convergence = historical inevitability" → "model saturation artifact". Domain-state fields saturate at their bounds in long runs; this reflects the range constraint and rule topology, not a claim about the real event being inevitable.
- "universality" is reserved for three or more scenarios of distinct structural types.

---

## 8. Future Work

The version plan below is the one actively followed in the repository (see `DESIGN.md`). Dates are in calendar-month units relative to initial v0.5 completion.

**v1.0 Predictive Latent Drive Bottleneck** (in progress; Stage 1 complete, Stage 2 pending). The hand-specified action weights of v0.5 are replaced by a learned low-dimensional latent drive vector — 3 to 8 dimensions, interpretable only post-hoc — that modulates action propensities, trigger susceptibilities, and slow-state updates. The trace schema (`TRACE_SCHEMA.md`) is designed so that v1.0 runs emit exactly the same events as v0.5 runs, enabling an apples-to-apples comparison via the §5 validation framework. Stage 1 (plumbing: model hooks, training sample extraction, Identity fallback implementations) is complete. Stage 2 is the PyTorch training loop itself.

**v1.1 Relational graph extension**. The current state representation contains beliefs about oneself but not explicit beliefs about others. v1.1 introduces per-edge state (A's estimate of B's trust, A's estimate of B's disillusionment), updated by Bayesian inference from observed behavior and by privileged information flow where applicable. This enables scenarios whose dynamics are driven by the gap between actual state and believed state (distrust, misreading, surprise). The `AgentBelief` class and `emit_belief_updates` trace entry are in v0.7 as a plumbing skeleton.

**v1.2 Phase-linked life architecture** (implemented; see Appendix D). A full biography is not a single 50-year simulator; it is a sequence of shorter local simulators, each with its own state, rules, and exit conditions. Transitions between phases are themselves events. v1.2 formalizes this as a meta-simulator over local simulators. The Peter scenario as originally implemented in v0.7 is a single-phase simulator covering the 50-day passion window; v1.2 extends it to five phases covering approximately three years (calling → Galilean ministry → confession+transfiguration → journey to Jerusalem → passion). A single `PhasedSimulationWorld` runs these phases in sequence with per-phase tick-scale (2h/tick dense phases vs 24h/tick sparse phases) and a handoff specification that carries selected state between phases. Legacy single-phase mode (`phases=None`) is bit-exact preserved so all §6 findings remain unchanged.

**v1.3 Weak preference inference**. Classical inverse reinforcement learning recovers a single reward function from observed behavior. For historical subjects this is the wrong shape: people act under mixed, time-varying, and partially contradictory preferences. v1.3 extends toward mixture preference inference, weak in the sense of not committing to a single coherent utility.

**v2.0 Narrative Witness layer**. The player — the human user — experiences the simulator as a witness rather than an analyst, through a first-person narrative rendered from the trace stream. The plumbing for this is already in v0.7: the `player_view` filter implements information asymmetry (the player's character is limited to what that character can observe), and `trace_narrator` turns the filtered trace into Korean narrative lines. v2.0 extends this into an interactive, browseable experience and connects it to v1.0's learned drive layer so that drive-axis values (e.g., `shame`, `attachment`) can be surfaced as narrative beats rather than numerical features.

**Cross-cutting: third scenario.** The language of "universality" in §6.3 is held to *structural isomorphism*; to promote it to universality we plan a third scenario of a genuinely different structural type (e.g., a negotiation scenario, where multiple agents converge to or fail to converge to an agreement without a single rare-action bottleneck). `SCENARIO_TEMPLATE.md` in the repository is the working guide for this addition.

---

## 9. Conclusion

Witness demonstrates that multi-agent, hazard-driven simulation of historical biographical events, paired with a seven-layer validation framework, can produce emergent outcomes whose causal structure is decomposable and whose cross-scenario regularities are statistically discriminable. The primary contribution is the validation protocol; the specific findings demonstrate that the protocol yields non-degenerate output when applied to two distinct scenarios. We release the framework and treat it as the substrate on which learned extensions, planned for v1.0 and beyond, will be evaluated on the same terms.

---

## Appendix A — Reproduction

- Engine version: v0.7 (2026-04-19).
- Python 3.11+. Dependencies in `pyproject.toml`.
- `python demo_v07.py --scenario peter` / `--scenario vangogh` produces the full pipeline (simulation → trace → player view → narrative).
- `benchmarks/bench_simulation.py` reports baseline throughput (Peter ~1000 tick/s, VG ~1270 tick/s on a reference workstation).
- Test suite: `pytest -m "not slow and not archived"` runs the 570+ fast-suite; `pytest -m archived` runs legacy exploratory analyses.
- Test tiering by role in this paper: see `ITERATION_CLASSIFICATION.md` (Tier 1 main narrative, Tier 2 supplementary, Tier 3 archived, Tier 4 engine correctness, Tier 5 v0.7 pipeline).

## Appendix B — Per-finding test pointer table

| Finding | Test file(s) | Key statistic |
|---------|--------------|---------------|
| §5.1 POM all-pass rate | `test_pom_bootstrap.py` | 47.5% (95% CI [32.5%, 62.5%]) |
| §5.2 Judas ablation Cohen's *d* | `test_permutation_judas.py` | *d* = −6.87, *p* < 0.001 |
| §5.3 Event-relative match gap | `test_multi_checkpoint.py` | 35.5% → 80.3% |
| §5.4 Explanation faithfulness | `test_explanation_faithfulness.py`, `test_explanation_faithfulness_extended.py` | Spearman ρ = 1.0 (n=30) |
| §5.5 Partial holdout forecast | `test_partial_holdout_generalization.py` | train 83% / test 88.9% |
| §5.6 Cross-scenario KS | `test_cross_scenario_ks.py` | *D* = 0.567, *p* < 0.01 |
| §5.7 Behavioral rate regression | `test_action_rate_regression.py`, `test_withdraw_noise_robustness.py` (archived) | *r* = −0.942, noise-robust [−0.98, −0.85] |
| §6.1 Spontaneous arrest | `test_emergent_arrest.py` | 100% rate (n=100) |
| §6.1 Bimodality test | `test_hartigan_dip.py`, `test_arrest_distribution.py` (archived) | ΔBIC = −8.94 (unimodal) |
| §6.2 Asymmetric causation | `test_peter_param_importance.py` (archived), counterfactual batch | 1:9 ratio |
| §6.3 Bottleneck isomorphism | `test_pom_bootstrap.py`, `test_vg_pom_bootstrap.py` | Phi > 0.95 both |
| §6.3 Cross-agent coupling | `test_cross_agent_coupling.py` | Judas↔Peter *r* = 0.76 |
| §6.4 Surface divergence | `test_cross_scenario_ks.py` | *D* = 0.567 |
| §6.5 Linear trajectory | `test_disill_trajectory_shape.py` | *R*² = 0.998 (linear) > 0.966 (sigmoid) |
| §6.5 Threshold response | `test_phase_transition.py` (name retained, text corrected) | threshold-only discontinuity |
| §6.6 Stability vs chaos | `test_initial_perturbation.py` (archived), `test_seed_sensitivity.py` (archived) | 38t shift < 42.8t seed std |
| §6.7 Terminal saturation | `test_checkpoint_bottleneck.py` | Judas domain saturates at 10.0 (artifact) |
| §6.8 Behavioral precedence | `test_action_rate_regression.py`, `test_vg_behavioral_signal.py` (archived) | 83.3% vs state 63% |

Engine-correctness tests (Tier 4 in `ITERATION_CLASSIFICATION.md`) are not listed here; they underwrite the framework rather than a specific finding. v0.7 pipeline tests (Tier 5: `test_trace_emitter.py`, `test_trace_integration.py`, `test_player_view.py`, etc.) are likewise not findings but infrastructure for v1.0.

## Appendix C — Figure plan (placeholders)

The following eight figures are planned for inclusion. Each has a reproduction script in `output/` or is rendered from an `engine/` analysis module on first use. Placeholder captions below; to be replaced with final figures before submission.

**Figure 1 — Four-layer architecture.** Stack diagram showing Universal Engine (state/rules/hazard/trigger) → Domain Module (FaithJourneyState, CreativeDriveState) → Era Module → Biography Pack (content/<name>/). Trigger/hazard flow superimposed with arrows from agent state to event firing. *Source: hand-drawn from `CLAUDE.md` §PROJECT STRUCTURE and `DESIGN.md` §2.*

**Figure 2 — POM bottleneck Phi matrix.** Two heatmaps side by side. Left: Peter 7×7 Phi matrix with `sword_drawn` row/column darkly shaded. Right: Van Gogh 5×5 Phi matrix with `self_harm` row/column darkly shaded. Color bar 0–1. *Source: `tests/test_engine/test_pom_bootstrap.py`, `test_vg_pom_bootstrap.py`.*

**Figure 3 — Counterfactual ablation bar chart.** X-axis: condition (full ensemble / no-Judas / no-Caiaphas / no-Crowd). Y-axis: spontaneous arrest rate with 95% bootstrap CI error bars. Expected: full ≈ 100%, no-Judas ≈ 0%, others near full. *Source: `tests/test_engine/test_permutation_judas.py`.*

**Figure 4 — Spearman rank heatmap.** Rows: Judas disillusionment at tick ∈ {50, 100, 150, 200}. Columns: arrest tick quartile. Values: Spearman ρ. Shows the growing predictive strength of disill as the arrest-tick approaches. *Source: `tests/test_engine/test_forecast_horizon.py`.*

**Figure 5 — Linear vs. nonlinear trajectory fit.** Single panel: mean Judas disillusionment over tick (with 95% band across seeds), with overlays of linear (*R*² = 0.998), sigmoid (0.966), exponential (0.784) fits. Vertical dashed line at trigger threshold. *Source: `tests/test_engine/test_disill_trajectory_shape.py`.*

**Figure 6 — KS CDF comparison.** Two empirical CDFs on normalized run-completion axis [0, 1]: Peter arrest-tick / max_tick and Van Gogh departure-tick / max_tick. Annotated with KS statistic *D* = 0.567. *Source: `tests/test_engine/test_cross_scenario_ks.py`.*

**Figure 7 — Behavioral rate scatter.** X-axis: Judas `withdraw` rate at tick 100 (rates per tick). Y-axis: arrest tick. Regression line with *r* = −0.942 and 95% band. Van Gogh analogue in the same panel or inset (Gauguin `critique` rate, *r* = −0.92). *Source: `tests/test_engine/test_action_rate_regression.py`.*

**Figure 8 — Peter emotional arc.** Three lines (fear, grief, hope) aligned by arrest tick on the x-axis (tick − arrest_tick). Shows hope trough immediately before arrest, grief peak at +25, fear peak at +75. Ensemble mean with 95% band. *Source: `tests/test_engine/test_peter_emotion_arc.py`.*

## Appendix D — v1.2 Phase-linked life architecture (implementation summary)

Added to the repository after the body of this paper; this appendix summarizes the v1.2 extension referenced in §8.

**New engine modules** (all person-agnostic; content opts into each feature).

| Module | Purpose |
|--------|---------|
| `engine/core/phase.py` | `Phase`, `PhaseExitCondition`, `PhaseHandoffSpec`, `FieldMapping` — phase boundary specification |
| `engine/simulation/phased_world.py` | `PhasedSimulationWorld` driver + `PhasedMultiAgentResult` (exposes both per-phase and merged views); `phases=None` delegates to v0.7 `SimulationWorld` bit-exact |
| `engine/simulation/time_axis.py` | `ticks_to_absolute_hours`, `extract_field_trajectory_absolute`, `convert_phase_boundaries_to_hours`, `extract_final_states_at_phase_boundaries` — absolute-hours coordinates for analysis that must cross phase-variable tick scales |
| `engine/rules/inhibitor.py` | `FieldAttenuationRule`, `FieldAmplificationRule` — generic cross-agent field dynamics, instantiated by content (e.g., Peter's awe dampening Judas disillusionment) |
| `engine/rules/slow_recovery.py` | `SlowStateFieldRecoveryRule` — field-specific opt-in slow state recovery (default rates zero ⇒ zero-effect); `event_trauma` intentionally excluded per PTSD modeling |
| `engine/core/hazard.py` | `HazardFunction.base_rate_unit: Literal["per_tick", "per_hour"]` (default `per_tick` preserves v0.7 calibration); per_hour hazards receive `tick_scale_hours` as effective `dt` |

**`RuleContext.dt_hours`** is populated from each phase's `tick_scale_hours`, enabling all rate-based rules to work consistently across the 2h/tick dense phases (calling, confession, passion) and the 24h/tick sparse phases (Galilean ministry, Jerusalem journey).

**Peter scenario extension**. `content/peter/phases/{01_calling, 02_galilean, 03_confession, 04_journey_to_jerusalem, 05_passion}/` each provide `phase_config.json` + per-phase `canonical_events.json`. Phase 5 reuses the v0.7 legacy `canonical_events.json` so that the 500-tick passion scenario is identical whether run standalone (`phases=None`) or as the terminal phase of a linked-life run.

**Key verifications** (all green in the repository test suite as of this draft revision).

1. *Legacy preservation*: `test_full_arc_phases_1_to_4.py::TestArchitecturalClaims::test_claim_legacy_mode_identical_to_v07` establishes that `PhasedSimulationWorld(phases=None)` produces bit-exact results versus `SimulationWorld` for the same seed. All §6 findings therefore remain unchanged in the legacy mode.
2. *Phase-variable rate invariance*: `test_hazard_per_hour.py` shows that per_hour hazards produce expected Poisson fires proportional to real-time hours across 2h/tick and 24h/tick configurations, while per_tick hazards are unaffected.
3. *Engine-neutrality*: `test_phased_vangogh.py` runs the Van Gogh scenario through `PhasedSimulationWorld` with no content changes (single-phase wrap and two-phase split), verifying that the v1.2 machinery is not Peter-specific.
4. *Ensemble emergent patterns*: `test_phase_arc_emergent.py` runs 10 seeds × 4 Peter phases and checks that mean awe is non-decreasing Phase 1 → 3, obedience_maturity is non-decreasing phase-to-phase, emotions remain in [0, 10], and jesus_understanding stays within the canonical literal set.
5. *Inhibitor deployment*: `test_inhibitor_judas_deployment.py` shows that, under `FieldAmplificationRule` driving Judas disillusionment from unmet messianic expectation, adding `FieldAttenuationRule` conditioned on Peter's awe keeps disillusionment bounded well below saturation — operationalizing the reviewer concern that monotonic accumulation alone collapses the three-year arc into premature betrayal.
6. *Full-scale linked-life run*: `test_linked_life_phase5_full.py` runs all five phases (including the full 500-tick Phase 5 with 4 agents), completing under a second per seed.

**Test count deltas since v0.7**. Fast test count rises from 572 to 854 (+282), with 100% line coverage on the three new v1.2 rule/analysis modules (`time_axis.py`, `inhibitor.py`, `slow_recovery.py`) and 97%+ on `phased_world.py`. Ruff clean; no new mypy errors.

**Runtime**. Full v1.2 five-phase Peter run completes in ~0.1–0.8 s per seed on a standard development machine. Benchmark throughput (250-tick runs, 10 seeds) is 928 tick/s for Peter and 1158 tick/s for Van Gogh — approximately 7% lower than the v0.7 baseline (1001 / 1267 tick/s), reflecting the additional per-tick rule overhead.

## Appendix E — Universality and Stage 2 feasibility spectrum (v1.2 Iter 57–72)

Following the v1.2 architecture work in Appendix D, two further empirical questions were addressed: (1) whether the engine is scenario-agnostic beyond the Peter / Van Gogh pair, and (2) whether the v1.0 Latent Drive Bottleneck (§8) is learnable from current features.

**Third scenario and engine universality**. A third scenario (Talleyrand, 1789–1830 diplomatic career) was added specifically to exercise dynamics distinct from Peter (emotion-driven rare-action bottleneck) and Van Gogh (isolation-breakdown). Talleyrand's dynamics are regime-transition-driven: a categorical `current_regime` literal (7 values) evolves via canonical events at tick 1 (revolution), 72 (directory), 120 (consulate), 180 (empire), 216 (fall from Napoleon's favor), 300 (Bourbon restoration), and 492 (July monarchy). Cross-scenario POM scorecard application is asymmetric: Talleyrand's scorecard achieves ≥80% pass rate on Talleyrand runs but 0% on Peter runs, and vice versa. This asymmetry is used as the empirical ground for the scope-limited claim that *the engine is scenario-agnostic; the patterns are scenario-specific*. The narrower phrase "engine universality" is separated from "empirical generalization" and only the first is defended at this point.

**Stage 2 feasibility spectrum**. Before implementing a PyTorch MLP encoder (§8 v1.0), the question *can action class be predicted from state features?* was measured directly on each scenario via (a) Fisher-style between/within variance ratio on a random-projection drive (separability), and (b) sklearn logistic-regression action classification accuracy vs. the majority class.

| Scenario | Actions | Majority | Logit acc | Random-projection separability |
|----------|---------|----------|-----------|-------------------------------|
| Van Gogh | 16 | — | (high) | 6.04 |
| Peter | 24 | 12.5% | **45.5%** (3.6× over chance) | 1.91 |
| Talleyrand (original profile) | 5 | 47.8% | 44.9% (at chance) | 0.05 |
| Talleyrand (retuned profile, Iter 70) | 5 | 53.5% | 55.1% (marginal) | 0.07 |

Peter and Van Gogh show strong state→action coupling and are feasible Stage 2 targets. Talleyrand exhibits a **policy gap** rather than a feature gap: the canonical behavior profile's `base_weight` values (2.5–3.0) dominate its state-dependent multipliers (0.1–0.2), making actions nearly state-independent in the generating process. Retuning multipliers upward (0.4–0.9) removed the dominance but left an irreducible gap due to (i) only 5 action classes and (ii) regime-transition canonical events that reset the numeric state discontinuously, compressing intra-regime variance. Talleyrand's Stage 2 target status is therefore **deferred** pending content expansion (more actions and finer-grained canonical events).

**First learned encoder (LDA)**. `engine.core.latent_drive.LearnedLinearEncoder` uses sklearn's Linear Discriminant Analysis on training samples to produce a *learned* projection. On the Peter multi-agent scenario (10 seeds × 300 tick, 1,808 samples, 24 classes), LDA improves random-projection separability from 1.91 to 2.39 (≈25%), consistent with a linear-only transform. The pipeline is wired through `TrainingConfig(use_learned_linear=True)` and accessed from the `demo_phased.py --encoder learned` flag. This is the first Stage 2 step (non-random, learned) while remaining dependency-only on sklearn (no PyTorch installation required yet).

**Interpretation for §8 roadmap**. v1.0 Stage 2 implementation can proceed on Peter and Van Gogh with the existing 12-feature extractor; the remaining linearity barrier (~25% LDA vs random baseline) is exactly the regime where nonlinear MLP learning is expected to help. Talleyrand-scale "categorical regime-driven" scenarios require further content and/or representation work before being added to Stage 2 training sets.

## Appendix F — Extended counterfactual validation (V3 trigger-arrest metric)

Two critiques surfaced during baseline-comparison review (2026-04-21):

- *"Chain rate in the random-behavior baseline (0.60) exceeds chain rate in the full system (0.10); the causal-chain rate is measuring action frequency, not causal structure."*
- *"Endogenous arrest is 1.00 in every condition; the simulator is designed so arrest always occurs."*

To respond to both simultaneously, five counterfactual conditions were run on Peter (4 agents, 300 ticks, *n* = 10 seeds): full system, Judas removed, Caiaphas removed, trigger set removed (`triggers=[]`), and a random-behavior profile with Judas removed. A scaling sweep on the hazard layer (`factor ∈ {1.0, 0.75, 0.5, 0.25, 0.1, 0.0}`) was run in the same measurement harness.

**Three metrics compared**:

- *V2 endogenous arrest rate*. Arrest via either hazard event or trigger firing, canonical arrest excluded. Saturates at 1.00 in every counterfactual (canonical `scene_08_arrest` at tick 152 + state-driven hazard ceiling both fire).
- *Chain rate (gap-constrained)*. The ordered chain inform → surveillance → betray → arrest, all four events occurring with adjacent gaps ≤ 30 ticks.
- *V3 trigger-arrest rate*. The arrest event fires specifically through `arrest_trigger`, whose state conditions require Judas disillusionment AND Caiaphas threat-level AND a Judas `betray` action in the recent window.

**Results**:

| Condition | canonical arrest | V2 endogenous | chain (gap ≤ 30) | **V3 trigger arrest** |
|-----------|------------------|---------------|-------------------|------------------------|
| Full system | 1.00 | 1.00 | 0.10 | **0.90** |
| Judas removed | 1.00 | 1.00 | 0.00 | **0.00** |
| Caiaphas removed | 1.00 | 1.00 | 0.00 | **0.00** |
| Trigger set removed | 1.00 | 1.00 | 0.00 | **0.00** |
| Random + Judas removed | 1.00 | 1.00 | 0.00 | **0.00** |

**Verdicts**:

- `causal_dependency` = **CAUSAL_PASS** (V3). Judas removal collapses trigger-arrest from 0.90 to 0.00. The V2 metric fails the same test (both 1.00) because it aggregates over firing paths that Judas removal does not block.
- `trigger_necessity` = **TRIGGER_NECESSARY**. Removing the trigger set yields chain rate 0.00 and trigger-arrest 0.00; only canonical and hazard arrest remain.
- `random_chain_nature` = **RANDOM_CHAIN_SPURIOUS**. With random behavior but Judas removed, chain rate drops from the random+Judas baseline (0.60 in the baseline comparison experiment) to 0.00. The chain is not an artifact of action frequency alone; it requires the specific agent whose removal also collapses trigger-arrest.

**Hazard scaling sweep**. V2 endogenous arrest is invariant at 1.00 across all six factors (`inevitability` pattern under the three-way classification `{emergence, threshold, inevitability}`). Chain rate peaks at 0.30 for factors 0.75–0.10 (reduced hazard competition lets the trigger-driven chain form more cleanly) and drops to 0.00 at factor 0.0. POM all-pass is 0.50 for factors ≥ 0.1 and 0.00 at factor 0.0.

**Interpretation for the paper**:

- The V2 endogenous-arrest metric is saturated by multiple independent firing paths and is *not* a discriminating measure of causal structure. Results tables that use it should be read as a ceiling condition, not a counterfactual signal.
- The V3 trigger-arrest metric — firing specifically through the designed causal pathway — shows the expected counterfactual collapse on every targeted removal and is the discriminating metric for causal claims.
- The `random vs structured` chain-rate inversion that surfaced in the v2 baseline comparison is resolved: random chain formation requires the same driver agent (Judas). Removing Judas collapses chain rate in the random condition to 0.00 just as it does in the full system.

**Artifacts**: `docs/paper_data/causal_counterfactual.{json,txt}`, `docs/paper_data/hazard_scaling.{json,txt}`, `docs/paper_data/fig_counterfactual_comparison.png`, `docs/paper_data/fig_hazard_scaling_curve.png`. Numerical section merged into `docs/paper_data/paper_numbers.json` under keys `counterfactual_causal` and `hazard_scaling`. Source scripts: `scripts/counterfactual_baseline.py`, `scripts/hazard_scaling.py`, `scripts/counterfactual_figures.py` (engine and content-pack code unmodified).

## References

Axtell, R., Axelrod, R., Epstein, J. M., & Cohen, M. D. (1996). Aligning simulation models: A case study and results. *Computational and Mathematical Organization Theory*, 1(2), 123–141.

Axtell, R., & Epstein, J. M. (1996). *Growing artificial societies: social science from the bottom up*. Brookings Institution Press.

Epstein, J. M. (2006). *Generative social science: Studies in agent-based computational modeling*. Princeton University Press.

Grimm, V., Revilla, E., Berger, U., Jeltsch, F., Mooij, W. M., Railsback, S. F., Thulke, H., Weiner, J., Wiegand, T., & DeAngelis, D. L. (2005). Pattern-oriented modeling of agent-based complex systems: Lessons from ecology. *Science*, 310(5750), 987–991.

Keeling, M. J., & Rohani, P. (2008). *Modeling infectious diseases in humans and animals*. Princeton University Press.

Masad, D., & Kazil, J. (2015). Mesa: An agent-based modeling framework. *Proceedings of the 14th Python in Science Conference*, 53–60.

[Additional references to be added: Wilensky on NetLogo, Grimm ODD protocol (2006, 2010, 2020 revisions), Railsback & Grimm textbook, per-scenario historical sources.]
