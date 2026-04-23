"""IntegratedWorldRunner — Spike 2 B-3: Person Engine × World Engine.

Drives the two engines in lockstep:

    for each world day:
        1. WorldTick advances Layer 1..5 by dt_days=1.0.
        2. SyncLayer translates the new WorldState to a Person-Engine
           EnvironmentState.
        3. SimulationWorld runs N substeps (default 12, i.e. 2h/tick) with
           the injected environment + the agent states carried from the
           previous day.
        4. SyncLayer converts the substep action history into WorldEffects
           (publicity_shock / authority_threat / rumor_seed).
        5. The aggregated effects flow into LayerContext for the NEXT
           world tick — so agents affect tomorrow's world, not today's.

Guardrails honoured:

- ``engine/`` is only *imported*; no source modified.
- Multi-day continuity: agent states carry forward; ``state.tick`` is
  monotonically offset by ``day * substeps_per_day`` before each session
  so triggers / hazard rates see a continuous tick axis even though each
  session runs ``1..substeps_per_day`` internally.
- Canonical ``ExternalEvent`` scheduling is off by default in integrated
  mode because those events use absolute tick anchors that do not map
  cleanly onto the world-day partition. Triggers + hazard_events (which
  are state-driven / rate-driven) remain active.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.core.action import AgentBehaviorProfile
from engine.core.environment import EnvironmentState
from engine.core.state import AgentState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.checkpoint import ActionRecord
from engine.simulation.world import MultiAgentResult, SimulationWorld
from world.core.world_config import WorldConfig
from world.core.world_state import WorldState
from world.simulation.sync_layer import SyncLayer
from world.simulation.world_tick import WorldTick


@dataclass
class IntegratedDaySnapshot:
    """Per-world-day telemetry row."""

    day_index: int
    world: WorldState
    agent_states: dict[str, AgentState]
    agent_actions: dict[str, list[ActionRecord]]
    aggregated_effects_in: dict[str, float]
    aggregated_effects_out: dict[str, float]
    environment_applied: EnvironmentState
    fired_triggers: list[dict[str, Any]] = field(default_factory=list)
    fired_events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class IntegratedResult:
    """Aggregate result of an N-day integrated run."""

    seed: int
    n_days: int
    substeps_per_day: int
    days: list[IntegratedDaySnapshot]
    final_agent_states: dict[str, AgentState]
    total_triggers: list[dict[str, Any]] = field(default_factory=list)
    total_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def final_world(self) -> WorldState:
        return self.days[-1].world if self.days else None  # type: ignore[return-value]


class IntegratedWorldRunner:
    """Drives World Engine + Person Engine in a coupled day-by-day loop."""

    def __init__(
        self,
        *,
        world_tick: WorldTick,
        world_config: WorldConfig,
        base_config: SimulationConfig,
        rule_engine: RuleEngine,
        behavior_profiles: dict[str, AgentBehaviorProfile],
        sync_layer: SyncLayer | None = None,
        substeps_per_day: int = 12,
        disable_canonical_events: bool = True,
    ) -> None:
        self.world_tick = world_tick
        self.world_config = world_config
        self.base_config = base_config
        self.rule_engine = rule_engine
        self.behavior_profiles = behavior_profiles
        self.sync_layer = sync_layer or SyncLayer(
            world_config, substeps_per_day=substeps_per_day,
        )
        self.substeps_per_day = substeps_per_day
        self.disable_canonical_events = disable_canonical_events
        # Build a lookup so sync_layer can resolve action_id → AgentAction
        # attributes (visible_signal, observable_from) without extending
        # ActionRecord.
        self._action_index: dict[str, Any] = {}
        for profile in behavior_profiles.values():
            for action in profile.actions:
                self._action_index[action.action_id] = action

    # ------------------------------------------------------------------
    # Run.

    def run(self, n_days: int | None = None, seed: int = 0) -> IntegratedResult:
        days_to_run = n_days if n_days is not None else self.world_config.total_ticks
        world_state = self.world_tick.initial_world_state()

        agent_states: dict[str, AgentState] = {
            s.agent_id: s.model_copy(deep=True)
            for s in self.base_config.get_all_initial_states()
        }
        previous_env: EnvironmentState | None = None
        aggregated_in: dict[str, float] = {}

        snapshots: list[IntegratedDaySnapshot] = []
        cumulative_triggers: list[dict[str, Any]] = []
        cumulative_events: list[dict[str, Any]] = []

        for day in range(days_to_run):
            # 1. Advance world (feeds in yesterday's aggregated effects).
            world_state = self.world_tick.tick(world_state, aggregated=aggregated_in)

            # 2. World → EnvironmentState.
            env_state = self.sync_layer.world_to_environment(
                world_state, previous=previous_env,
            )
            previous_env = env_state

            # 3. Run substeps_per_day Person-Engine ticks.
            session_result = self._run_session(
                day=day,
                agent_states=agent_states,
                env=env_state,
                seed=seed,
            )
            agent_states = {
                aid: s.model_copy(deep=True)
                for aid, s in session_result.final_states.items()
            }
            cumulative_triggers.extend(session_result.fired_triggers)
            cumulative_events.extend(session_result.fired_events)

            # 4. Agent → World effects.
            session_actions = self._collect_actions_with_agent_id(
                session_result.action_histories,
            )
            effects = self.sync_layer.actions_to_effects(
                session_actions, known_actions=self._action_index,
            )
            for effect in effects:
                self.sync_layer.submit_effect(effect)
            aggregated_out = self.sync_layer.drain_aggregated()

            snapshots.append(IntegratedDaySnapshot(
                day_index=world_state.calendar.day_index,
                world=world_state,
                agent_states=agent_states,
                agent_actions=dict(session_result.action_histories),
                aggregated_effects_in=dict(aggregated_in),
                aggregated_effects_out=dict(aggregated_out),
                environment_applied=env_state,
                fired_triggers=list(session_result.fired_triggers),
                fired_events=list(session_result.fired_events),
            ))

            aggregated_in = aggregated_out

        return IntegratedResult(
            seed=seed,
            n_days=days_to_run,
            substeps_per_day=self.substeps_per_day,
            days=snapshots,
            final_agent_states=agent_states,
            total_triggers=cumulative_triggers,
            total_events=cumulative_events,
        )

    # ------------------------------------------------------------------
    # Session (one world day = N person substeps).

    def _run_session(
        self,
        *,
        day: int,
        agent_states: dict[str, AgentState],
        env: EnvironmentState,
        seed: int,
    ) -> MultiAgentResult:
        # Apply a continuous-tick offset so triggers / cooldowns see a
        # monotone axis even though SimulationWorld resets tick at 1.
        tick_offset = day * self.substeps_per_day
        shifted_states = [
            s.model_copy(update={"tick": tick_offset})
            for s in agent_states.values()
        ]
        session_config = self.base_config.model_copy(update={
            "initial_states": shifted_states,
            "initial_state": shifted_states[0],
            "environment": env,
            "max_tick": self.substeps_per_day,
            "events": [] if self.disable_canonical_events else self.base_config.events,
            "interventions": (
                [] if self.disable_canonical_events
                else self.base_config.interventions
            ),
            # phases off in integrated mode — world handles time.
            "phases": None,
        })
        world_sim = SimulationWorld(
            config=session_config,
            rule_engine=self.rule_engine,
            behavior_profiles=self.behavior_profiles,
        )
        # Per-session deterministic seed so different days decorrelate.
        session_seed = _combine_seeds(seed, day)
        return world_sim.run(seed=session_seed)

    # ------------------------------------------------------------------
    # Helpers.

    def _collect_actions_with_agent_id(
        self,
        action_histories: dict[str, list[ActionRecord]],
    ) -> list[ActionRecord]:
        """Flatten action histories + inject agent_id onto each record.

        ActionRecord has no agent_id field, so we attach it as a Pydantic
        __pydantic_extra__ attribute when the model allows, otherwise via
        object attribute — whichever the version supports.
        """
        out: list[ActionRecord] = []
        for agent_id, records in action_histories.items():
            for record in records:
                # ActionRecord is a pydantic model; attach agent_id via
                # model_copy(update) only if the field exists. Fall back to
                # setattr for diagnostics-only access.
                enriched = record.model_copy()
                try:
                    object.__setattr__(enriched, "agent_id", agent_id)
                except Exception:
                    pass
                out.append(enriched)
        return out


def _combine_seeds(base: int, day: int) -> int:
    # Python 3.14 random.Random() only accepts None/int/float/str/bytes —
    # collapse the (base, day) pair into a stable 32-bit int.
    return (hash(("integrated", int(base), int(day))) & 0x7FFFFFFF)
