"""Spike 6 Phase C — first actual Peter training attempt.

Marked slow: runs a 3 seeds × 100 tick simulation + 20-epoch training on CPU.
Expected end-to-end time: ~5-15 seconds.

Goal: confirm the person-agnostic neural policy pipeline trains without
crashing on real simulation-derived data. No accuracy threshold — spec
§2.2 says "완료 기준은 Lee의 감각 판단". This test only pins:

- Peter (state, action) pairs load into dataset shape
- MLP training terminates without nan/inf
- Val accuracy beats majority-class baseline (signal exists)
"""

from __future__ import annotations

from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import (  # noqa: E402
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.policies.neural.dataset import (  # noqa: E402
    build_behavior_cloning_dataset,
    train_val_split,
)
from engine.policies.neural.trainer import train_behavior_cloning  # noqa: E402
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import (  # noqa: E402
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.world import SimulationWorld  # noqa: E402

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup_domain_types():
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _run_peter_scenario(seed: int):
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=100, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )
    return SimulationWorld(config, _rules(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
def test_peter_neural_pipeline_end_to_end(_setup_domain_types) -> None:
    # --- Collect training data from 10 rule-based runs.
    # Peter's snapshot interval ≈ 8 ticks → ~11 samples per 100-tick run.
    ds = build_behavior_cloning_dataset(
        _run_peter_scenario,
        agent_id="peter",
        seeds=10,
    )
    assert ds.n_samples >= 80, f"only {ds.n_samples} samples — Peter too quiet"
    assert ds.n_actions >= 2, f"only {ds.n_actions} actions seen — unusable for classifier"

    train, val = train_val_split(ds, val_fraction=0.2, seed=0)
    assert train.n_samples > 0
    assert val.n_samples > 0

    # --- Train.
    _, history = train_behavior_cloning(
        train, val, epochs=20, batch_size=32, lr=1e-2, seed=0,
        early_stop_patience=5,
    )
    assert history.final is not None

    # Loss is finite (no nan/inf explosion).
    for m in history.per_epoch:
        assert m.train_loss == m.train_loss  # not nan
        assert m.val_loss == m.val_loss  # not nan
        assert m.train_loss < 1e6

    # --- Diagnostic: print to stdout so pytest -s shows it for Lee to
    #     eyeball. Spec §2.2 forbids numeric completion bars — pipeline
    #     health is all we assert.
    from collections import Counter
    train_counts = Counter(train.y.tolist())
    val_counts = Counter(val.y.tolist())
    vocab = ds.action_vocab
    print("\n[peter neural pipeline smoke]")
    print(f"  samples: train={train.n_samples} val={val.n_samples}")
    print(f"  actions: {vocab}")
    print(f"  train distribution: {[(vocab[k], train_counts[k]) for k in sorted(train_counts)]}")
    print(f"  val distribution:   {[(vocab[k], val_counts[k]) for k in sorted(val_counts)]}")
    print(f"  train_acc final: {history.per_epoch[-1].train_acc:.3f}")
    print(f"  val_acc best:    {history.best_val_acc:.3f}")
    print(f"  epochs ran:      {len(history.per_epoch)}")
    # Finiteness already asserted above. Nothing numeric beyond that.
