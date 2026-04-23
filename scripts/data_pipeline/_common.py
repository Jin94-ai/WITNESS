"""Common simulation setup — shared across Phase 2 modules.

Person-agnostic in spirit (uses the 4 canonical Peter-scenario agents);
kept in scripts/ (not engine/) to preserve Rule #1.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.state import AgentState, EmotionalState, PhysicalState, SlowState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def register_domain_types() -> None:
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)


def make_rule_engine() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def load_peter_profiles() -> dict:
    return {
        "peter": load_behavior_profile(CONTENT / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT / "crowd" / "behavior_profile.json"),
    }


def load_default_peter_state() -> AgentState:
    return load_agent_state(CONTENT / "peter" / "initial_state.json")


def make_peter_state(
    *,
    fear: float = 5.0, hope: float = 5.0, grief: float = 5.0,
    confusion: float = 5.0, love: float = 5.0,
    fatigue: float = 3.0, hunger: float = 2.0, health: float = 8.0,
    moral_injury: float = 0.0, identity_shift: float = 0.0,
    event_trauma: float = 0.0, trust_scar: float = 0.0,
) -> AgentState:
    """Clone Peter's default state and override scalar fields."""
    peter = copy.deepcopy(load_default_peter_state())
    peter.emotions = EmotionalState(
        fear=fear, hope=hope, grief=grief, confusion=confusion, love=love,
    )
    peter.physical = PhysicalState(fatigue=fatigue, hunger=hunger, health=health)
    peter.slow_state = SlowState(
        moral_injury=moral_injury, identity_shift=identity_shift,
        event_trauma=event_trauma, trust_scar=trust_scar,
    )
    return peter


def build_config(max_tick: int = 100, *, peter_override: AgentState | None = None) -> SimulationConfig:
    peter = peter_override if peter_override is not None else load_default_peter_state()
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )


def run_peter(
    seed: int, max_tick: int = 100,
    *, peter_override: AgentState | None = None,
) -> Any:
    cfg = build_config(max_tick=max_tick, peter_override=peter_override)
    world = SimulationWorld(cfg, make_rule_engine(), behavior_profiles=load_peter_profiles())
    return world.run(seed=seed)


def run_peter_with_policy(
    seed: int, max_tick: int = 1,
    *, peter_override: AgentState | None = None,
    policies: dict[str, Any] | None = None,
) -> Any:
    """Run with a ``DecisionPolicy`` injected per agent (Phase A forced sampling).

    Default ``max_tick=1`` is the forced-sampling pattern: set up the boundary
    state, force one action selection, record, done.
    """
    cfg = build_config(max_tick=max_tick, peter_override=peter_override)
    world = SimulationWorld(
        cfg, make_rule_engine(),
        behavior_profiles=load_peter_profiles(),
        policies=policies,
    )
    return world.run(seed=seed)
