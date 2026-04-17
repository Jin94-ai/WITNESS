# Witness

> Agent-based, hazard-driven, ensemble historical simulator.
>
> Run a person's life thousands of times. Observe the distribution.
> Ask: **"What was the moment that made the difference?"**

---

## What it does

Witness simulates a historical figure's life as a stochastic process. Events don't happen at fixed times -- they emerge probabilistically from the agent's internal state and environmental pressure. Run it thousands of times with varied parameters, and observe which paths emerge, which conditions produce which outcomes, and where the bifurcation points are.

**First subject**: Peter (last 50 days of Jesus).
**Second subject**: Van Gogh (Arles period, Gauguin's visit).

## Quick start

```bash
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Peter demo (100 runs)
python main.py

# Van Gogh (50 runs)
python main.py --person vangogh --runs 50

# Run all tests
pytest
```

## How it works

### Hazard-driven events

Events don't fire at `tick == 152`. Instead:
```
hazard = f(fear, fatigue, surveillance, crowd_pressure, ...)
P(event) = 1 - exp(-hazard * dt)
```

Same person, same initial conditions, different seed → different event timing → different life path.

### Fast/slow state

- **Fast state** (emotions): fear, hope, grief, confusion, love. Homeostasis pulls toward baseline.
- **Slow state** (scars): moral_injury, breach_count, event_trauma, identity_shift. Irreversible accumulation.

### Pattern-Oriented Modeling (POM)

Instead of matching one metric (deny3 rate), we match 7 patterns simultaneously:
- no_flee, sword_drawn, triple_denial, grief_peak, moral_injury, identity_damage, eventual_hope

Result: current rules pass 38.6%, fear-only passes 1.2%, uniform passes 0%. POM separates rule families 32x.

### Environment

Surveillance, crowd pressure, threat level affect both hazard firing and action decisions. Direction is consistent: higher pressure → more crisis behavior.

## Validated findings

| Finding | Evidence |
|---------|----------|
| Current rule structure is uniquely valid | pyABC Model Selection: 100% (Peter), 84% (Van Gogh) |
| POM separates rule families 32x | 38.6% vs 1.2% vs 0% |
| Interaction structure depends on variable set | shapiq: 3-var vs 5-var results differ completely |
| Environment → crisis direction consistent | surveillance sweep: deny3 88%→95% |
| Flee rate is environment-independent | 29% stable across all conditions |
| Parameter Recovery | PASS (true params in recovered box) |

## Project structure

```
engine/                    # Universal engine (person-agnostic)
  core/                    # AgentState, HazardEngine, EnvironmentState
  rules/                   # Physical, emotional, social, temporal rules
  simulation/              # Runner, batch, analysis, POM, PRIM, calibration
  io/                      # Loader, trajectory dataset

content/                   # Biography packs (person-specific data only)
  peter/                   # 10 hazard events, 7 checkpoints, FaithJourneyState
  vangogh/                 # 5 hazard events, 4 checkpoints, CreativeDriveState

tests/                     # 213 tests, 89% coverage
docs/                      # ODD Protocol, session prompts
```

## Tech stack

Python 3.11+ / Pydantic / pytest / SALib / UMAP / sklearn HDBSCAN / shapiq / pyABC / EMA Workbench / XGBoost / matplotlib

## Analysis tools included

| Tool | Purpose |
|------|---------|
| POM | Multi-pattern validation filter |
| PRIM (EMA Workbench) | Scenario discovery -- parameter boxes |
| pyABC Model Selection | Compare competing rule structures |
| shapiq | Shapley interaction decomposition |
| Sobol / Morris (SALib) | Global sensitivity analysis |
| UMAP + HDBSCAN | Path clustering |
| Decision Tree | Bifurcation surface extraction |

## Adding a new person

1. Create `content/[name]/` with:
   - `initial_state.json` -- starting parameters
   - `hazard_events.json` -- events with hazard functions
   - `checkpoints.json` -- ground truth observations
   - `domain_[name].py` -- domain-specific state (extends DomainState)
   - `pom_scorecard.py` -- validation patterns

2. Register domain type in your script:
   ```python
   from engine.io.loader import register_domain_type
   register_domain_type("your_domain", YourDomainState)
   ```

3. Run: `python main.py --person [name]`

No engine code modification needed. Verified with dummy "artist" person + real Van Gogh.
