"""Sync Layer — bridge between World Engine and Person Engine (Spike 1D).

Implements the ChatGPT/Gemini "안 1" reconciliation from
WORLD_DESIGN_v1.1_amendments.md §1.3:

    1 world day = N person substeps (default 12, i.e. 2h per person tick).
    World Engine updates Layers 1-5 once per day.
    Person Engine receives an AgentPercept (local, partial view) per substep.
    Agent actions emit WorldEffect values; the Sync Layer aggregates them
    back per channel and hands the result to the next world tick via
    LayerContext.aggregated_effects.

Spike 1D scope — structural plumbing only:

- ``AgentPercept``: the local, partial view an agent receives from the world.
- ``SyncLayer``: produces percepts, accepts WorldEffects, aggregates per
  channel using the rule declared in WorldConfig.effect_channels.
- Integration with WorldTick stays optional: the demo runs the world end-
  to-end without agents, using ``SyncLayer.step_without_agents(...)``.

Spike 2 will wire the existing ``engine/simulation/SimulationWorld`` into
the 12-substep loop. Nothing in Spike 1D depends on engine/ — the rule
"engine/ 수정 금지" holds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable

from world.core.world_config import WorldConfig, WorldEffect, WorldEffectChannel
from world.core.world_state import WorldState

if TYPE_CHECKING:
    from engine.core.action import AgentAction
    from engine.core.environment import EnvironmentState
    from engine.simulation.checkpoint import ActionRecord


@dataclass(frozen=True)
class AgentPercept:
    """Local, partial view handed to an agent during one Person-Engine substep.

    Reviewer #5 (WORLD_DESIGN_v1.1 §2.5): *local percept, not global state*.
    The fields below are the minimum a Spike-2 agent would need from the
    Spike-1A/1B/1C world (calendar + crowd + economy + politics). Extended in
    later spikes with rumour list, visible factions, etc.
    """

    world_day_index: int
    """Shared counter — which world-day substep this percept belongs to."""

    person_substep: int
    """0..(substeps_per_day-1) within the current world day."""

    local_crowd_density: float
    """Current aggregate crowd density (Layer 5)."""

    days_to_next_passover: int
    """Calendar pressure signal (Layer 1)."""

    active_feast: str
    """Name of the active feast ('none' if outside a feast window)."""

    economic_stress: float
    """Normalised staple_price deviation above floor; 0 at floor, 1 at ceiling.
    Spike 2 agents will consume this as EnvironmentState.economic_pressure."""

    perceived_authority: float
    """Normalised roman_alertness above floor, plus a bonus when Pilate is
    personally in Jerusalem. Spike 2 agents feed this into fear / surveillance."""

    is_shabbat: bool
    """Shabbat flag (Layer 1) — Spike 2 agents may gate actions on this."""

    overflow_pressure: float = 0.0
    """Unit-normalised overflow above the crowd ceiling (Spike 2 A-2). 0 when
    the city is below capacity, >0 when pilgrims exceed Jerusalem's walls."""


_AUTHORITY_AGENTS = frozenset({"caiaphas", "pilate", "sanhedrin"})

_RUMOUR_KEYWORDS = (
    "rumor", "rumour", "inform", "betray", "speak", "teach",
    "cleanse", "miracle", "proclaim", "announce",
)


@dataclass
class AggregationBuffer:
    """Per-channel accumulator used by the sync layer between world ticks."""

    channel: WorldEffectChannel
    values: list[float] = field(default_factory=list)

    def add(self, value: float) -> None:
        self.values.append(value)

    def drain(self) -> float:
        result = self.channel.aggregate(self.values)
        self.values = []
        return result


class SyncLayer:
    """Bridge between world ticks and per-substep agent loops."""

    def __init__(self, config: WorldConfig, substeps_per_day: int = 12) -> None:
        self.config = config
        self.substeps_per_day = substeps_per_day
        self.buffers: dict[str, AggregationBuffer] = {
            ch.channel_id: AggregationBuffer(channel=ch)
            for ch in config.effect_channels
        }

    # ------------------------------------------------------------------
    # Percept production (hand to agents).

    def make_percept(self, state: WorldState, *, day_index: int, substep: int) -> AgentPercept:
        """Produce the local view for one agent substep.

        The sync layer is responsible for: (a) normalising world-layer values
        into units Person-Engine's EnvironmentState already understands, and
        (b) hiding state the agent should not see directly (e.g., Pilate's
        exact location; we expose only ``perceived_authority``).
        """
        econ_stress = self._normalise_economic_stress(state)
        authority = self._normalise_authority(state)
        overflow = self._normalise_overflow(state)
        return AgentPercept(
            world_day_index=day_index,
            person_substep=substep,
            local_crowd_density=state.crowd.crowd_density,
            days_to_next_passover=state.calendar.days_to_next_passover,
            active_feast=state.calendar.active_feast,
            economic_stress=econ_stress,
            perceived_authority=authority,
            is_shabbat=state.calendar.is_shabbat,
            overflow_pressure=overflow,
        )

    # ------------------------------------------------------------------
    # Spike 2 B-1: world → Person-Engine EnvironmentState.

    def world_to_environment(
        self, state: WorldState, previous: "EnvironmentState | None" = None,
    ) -> "EnvironmentState":
        """Translate a world snapshot into an EnvironmentState for the
        Person Engine's next substep session.

        Field mapping (reviewer #5 — percept-level, not global-state-level):

        - ``surveillance``   ← ``perceived_authority`` (0..1) × 10
        - ``crowd_pressure`` ← min(10, ``crowd_density``)  (already in 0..10)
        - ``threat_level``   ← peak(``surveillance``, Pilate-in-Jerusalem bonus)
        - ``time_pressure``  ← 10 × (1 - ``days_to_next_passover`` /
                                      ``PASSOVER_DAY``), clamped during feast
        - ``isolation_degree`` ← Shabbat flag × 2.0 (light bias)

        The ``previous`` argument is provided so future spikes can smooth
        rather than snap; Spike 2 ignores it and overwrites fully.
        """
        from engine.core.environment import EnvironmentState
        from world.environment.calendar import PASSOVER_DAY

        _ = previous  # reserved for Spike 3+ smoothing
        percept = self.make_percept(state, day_index=0, substep=0)
        surveillance = max(0.0, min(10.0, percept.perceived_authority * 10.0))
        crowd_pressure = max(0.0, min(10.0, percept.local_crowd_density))
        threat_level = surveillance
        if state.politics is not None and state.politics.pilate_location == "jerusalem":
            threat_level = max(0.0, min(10.0, surveillance + 1.0))
        if percept.days_to_next_passover > 0:
            time_pressure = max(
                0.0, min(10.0, 10.0 * (1.0 - percept.days_to_next_passover / PASSOVER_DAY)),
            )
        else:
            # During and after Passover window, time pressure eases back.
            time_pressure = 8.0 if percept.active_feast in {
                "passover", "unleavened_bread", "firstfruits",
            } else 0.0
        isolation = 2.0 if percept.is_shabbat else 0.0
        return EnvironmentState(
            surveillance=surveillance,
            crowd_pressure=crowd_pressure,
            threat_level=threat_level,
            time_pressure=time_pressure,
            isolation_degree=isolation,
        )

    # ------------------------------------------------------------------
    # Spike 2 B-2: agent actions → WorldEffects (generic, no action-name switch).

    def actions_to_effects(
        self,
        action_records: Iterable["ActionRecord"],
        known_actions: dict[str, "AgentAction"] | None = None,
    ) -> list[WorldEffect]:
        """Convert agent substep action records into WorldEffects.

        Generic mapping driven by two action properties (NOT action-name
        switches — reviewer #5):

        - ``visible_signal is not None``: the action is publicly observable →
          emit a ``publicity_shock`` effect.
        - Action that flows through ``observable_from`` to an authority figure
          (e.g., caiaphas) → emit an ``authority_threat`` effect.
        - Actions whose visible_signal OR action_id contains rumour-flavored
          keywords (English keyword list) map to rumour seeds. We check
          action_id as a fallback because content packs write their
          visible_signal in the scenario's native language (e.g. Korean for
          the Peter scenario), so only the action_id is portable.

        The caller passes ``known_actions`` (a map from action_id to the full
        AgentAction) so we can read those attributes without needing them on
        the record itself. If None, we fall back to record-only heuristics.
        """
        effects: list[WorldEffect] = []
        for record in action_records:
            vis_signal = self._record_visible_signal(record, known_actions)
            observable_from = self._record_observable_from(record, known_actions)
            action_id = str(getattr(record, "chosen_action", "") or "")

            if vis_signal is not None:
                # Public intensity — records do not carry intensity; use 1.0.
                effects.append(WorldEffect(
                    channel_id="publicity_shock",
                    value=1.0,
                    origin_agent=self._record_agent(record),
                ))
            if observable_from and any(
                obs in _AUTHORITY_AGENTS for obs in observable_from
            ):
                effects.append(WorldEffect(
                    channel_id="authority_threat",
                    value=1.0,
                    origin_agent=self._record_agent(record),
                ))
            # Rumour seed: keyword scan on BOTH visible_signal (if English)
            # AND action_id (always English per engine content convention).
            rumour_haystacks: list[str] = [action_id.lower()]
            if vis_signal is not None:
                rumour_haystacks.append(vis_signal.lower())
            if any(
                token in hay
                for hay in rumour_haystacks
                for token in _RUMOUR_KEYWORDS
            ):
                effects.append(WorldEffect(
                    channel_id="rumor_seed",
                    value=1.0,
                    origin_agent=self._record_agent(record),
                ))
        return effects

    @staticmethod
    def _record_visible_signal(
        record: "ActionRecord",
        known_actions: dict[str, "AgentAction"] | None,
    ) -> str | None:
        vis = getattr(record, "visible_signal", None)
        if isinstance(vis, str):
            return vis
        if known_actions is not None:
            act = known_actions.get(getattr(record, "chosen_action", ""))
            if act is not None and isinstance(act.visible_signal, str):
                return act.visible_signal
        return None

    @staticmethod
    def _record_observable_from(
        record: "ActionRecord",
        known_actions: dict[str, "AgentAction"] | None,
    ) -> list[str]:
        obs = getattr(record, "observable_from", []) or []
        if obs:
            return list(obs)
        if known_actions is not None:
            act = known_actions.get(getattr(record, "chosen_action", ""))
            if act is not None:
                return list(act.observable_from or [])
        return []

    @staticmethod
    def _record_agent(record: "ActionRecord") -> str:
        # ActionRecord does not carry agent_id directly; the runner wraps
        # this when submitting — fall back to 'unknown'.
        return getattr(record, "agent_id", "unknown") or "unknown"

    # ------------------------------------------------------------------
    # Effect ingress (agents → world).

    def submit_effect(self, effect: WorldEffect) -> None:
        buf = self.buffers.get(effect.channel_id)
        if buf is None:
            # Unknown channel: ignore silently to stay forward-compatible.
            # Spike 2 tests will assert against declared channels.
            return
        buf.add(effect.value)

    def drain_aggregated(self) -> dict[str, float]:
        """Collapse all buffers into a dict[channel_id → aggregated_value].

        Called once per world day, passed into ``WorldTick.tick(state, aggregated)``
        so the next tick sees the agents' accumulated influence. Spike 1A
        produced an empty dict here; Spike 2 will emit real values.
        """
        return {cid: buf.drain() for cid, buf in self.buffers.items()}

    # ------------------------------------------------------------------
    # Agent-less passthrough (Spike 1A/B/C demos).

    def step_without_agents(self) -> dict[str, float]:
        """Return the empty-aggregated-dict used when no agents are present.

        Spike 1A/B/C demos call this to remind callers (and future maintainers)
        that the sync-layer bridge is *present* in the loop, just dormant.
        """
        return {}

    # ------------------------------------------------------------------
    # Normalisation helpers (private).

    def _normalise_economic_stress(self, state: WorldState) -> float:
        if state.economy is None:
            return 0.0
        span = state.economy.price_ceiling - state.economy.price_floor
        if span <= 0:
            return 0.0
        return max(
            0.0,
            min(
                1.0,
                (state.economy.staple_price - state.economy.price_floor) / span,
            ),
        )

    def _normalise_overflow(self, state: WorldState) -> float:
        """Normalise overflow_pressure to [0, 1] using a simple saturating
        function so the percept stays in-range even in extreme runs."""
        raw = getattr(state.crowd, "overflow_pressure", 0.0) or 0.0
        if raw <= 0:
            return 0.0
        return min(1.0, raw / 10.0)

    def _normalise_authority(self, state: WorldState) -> float:
        if state.politics is None:
            return 0.0
        span = state.politics.alertness_ceiling - state.politics.alertness_floor
        if span <= 0:
            return 0.0
        normalised = (
            state.politics.roman_alertness - state.politics.alertness_floor
        ) / span
        # Presence bonus — Pilate personally being in Jerusalem adds pressure.
        if state.politics.pilate_location == "jerusalem":
            normalised = min(1.0, normalised + 0.1)
        return max(0.0, min(1.0, normalised))
