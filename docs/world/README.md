# docs/world/ — World Engine (v2.0) records

Artifacts produced by the World Engine (`world/` code path) and written
design / review documents for v2.0 work.
Kept separate from Person Engine records ([../person/](../person/)).

## Contents

- **[SPIKE_1_REVIEW.md](SPIKE_1_REVIEW.md)** — external-LLM review packet
  covering Spike 1A + 1B + 1C + 1D (Layer 1 calendar, Layer 2 economy,
  Layer 3 politics, Layer 5 crowd, Sync Layer bridge).
- **[SPIKE_2_REVIEW.md](SPIKE_2_REVIEW.md)** — external-LLM review packet
  covering Spike 2 Phase A (A-1/A-2/A-3 reviewer conditions) + Phase B
  (Person Engine × World Engine integrated runner, 6 integration tests).
- **[SPIKE_3_REVIEW.md](SPIKE_3_REVIEW.md)** — external-LLM review packet
  covering Spike 3 Phase 3A (factions independent) + 3B (crowd→militancy)
  + 3C (rumour graph) + 3D (rumour→jesus_movement influence). Headline
  finding: Judas removal collapses jesus_movement influence by 62% while
  pharisees (control) is unchanged — cross-layer counterfactual chain
  pinned in both snapshot + test.
- **[SPIKE_4_REVIEW.md](SPIKE_4_REVIEW.md)** — external-LLM review packet
  covering Spike 4 Phase 4A (InterventionSpec + Engine), 4B
  (BatchInterventionRunner + Cohen's d + permutation p-value), 4E (3
  canonical interventions in `content/interventions/`), 4F
  (`scripts/demo_spike4_interventions.py`). Framework validates Phase
  3D findings through an independent pipeline and produces
  per-intervention JSON artifacts for reuse.
- **[WORLD_SPIKE_5_PART1_PROGRESS.md](WORLD_SPIKE_5_PART1_PROGRESS.md)** —
  Spike 5 Part 1 progress memo: Phase 5C spatial model (`world/space/`,
  6 canonical locations + movement cost + rumour spatial propagation)
  and Phase 5A Jesus agent (`world/agents/jesus.py` + `content/jesus/`
  with 개역개정 citations + multi-path influence emitter). No new
  interventions added — world-expansion Spike per Rule #10.
- **[WORLD_SPIKE_5_PART2_PROGRESS.md](WORLD_SPIKE_5_PART2_PROGRESS.md)** —
  Spike 5 Part 2 progress memo: Phase 5B peripheral agents (Pilate +
  Caiaphas Full; Barabbas + John/James/Thomas Light) and Phase 5D
  economy enrichment (temple_economy + taxation + cross_economy
  coordinator). Graded-proximity foundation + hub-role pinned in
  behavior tests, still no new interventions.

- **[paper_data/world_numbers.json](paper_data/world_numbers.json)** —
  canonical numeric snapshot (Spike 1 agent-less world + Spike 2 integrated
  Peter 4-agent + Judas-removed counterfactual), regenerated via
  `python scripts/world_numbers.py`. Parallel to
  [../person/paper_data/paper_numbers.json](../person/paper_data/paper_numbers.json).
- **[paper_data/fig_spike1_world_peaks.png](paper_data/fig_spike1_world_peaks.png)**
  + **[paper_data/fig_spike2_counterfactual.png](paper_data/fig_spike2_counterfactual.png)**
  + **[paper_data/fig_spike3_counterfactual_chain.png](paper_data/fig_spike3_counterfactual_chain.png)**
  + **[paper_data/fig_spike4_interventions.png](paper_data/fig_spike4_interventions.png)** —
  snapshot figures, rendered from `world_numbers.json` + the 3
  `intervention_*.json` files via `python scripts/world_figures.py`.
  The Spike 3 figure is the visual companion to the counterfactual
  chain pinned in
  `tests/test_world/test_world_numbers_scripts.py::test_phase_3d_*`;
  the Spike 4 figure compares control vs intervention arms across the
  three canonical experiments (remove_judas, hazard_half,
  lenient_pilate).

## Future

- Spike 5 Part 3+ integration (wiring Jesus/Pilate/Caiaphas/Light
  agents + temple_economy + taxation into `IntegratedWorldRunner`),
  then Spike 7+ experiments that use the new graded-proximity structure
  — artifacts land here. Runtime simulation dumps go into
  [../../data/world/](../../data/world/).

## Source of truth

- Design: [../../WORLD_DESIGN.md](../../WORLD_DESIGN.md) +
  [../../WORLD_DESIGN_v1.1_amendments.md](../../WORLD_DESIGN_v1.1_amendments.md).
- Spike prompts: [../prompts/WORLD_SPIKE_1A.md](../prompts/WORLD_SPIKE_1A.md).
