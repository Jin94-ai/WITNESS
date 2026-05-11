"""v3 Phase 2 v2 integrated pipeline -- PersonV3Loop.

Event → Primitive update → Pressure → Person decision → Action → Event (closed loop, v2 §5).

Rule #6 준수: 기존 SimulationWorld 무수정. 별도 pipeline.
Rule #12 준수: 월드(events, primitives, pressure)는 압력만 생성, 행동은 policy 결정.
Rule #15-18 준수: ActiveState 20 + target-aware + 3 Layer 분리 + Level A/B only.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.action.action_event_mapper import ActionEventMapper
from engine.action.availability_gate import GateContext, is_available
from engine.person.state_derived import DerivedCalculator
from engine.person.state_transitions import (
    StateTransitionEngine,
    TransitionContext,
)
from engine.person.state_v3 import ActiveState
from engine.persona import (
    DEFAULT_PROFILE,
    PersonaProfile,
    activate_motifs,
    select_action,
)
from engine.world.events import EventRegistry
from engine.world.pressure import PressureLayer, PressureVector
from engine.world.primitives import PrimitiveState


@dataclass
class TrajectoryRecord:
    """One-tick snapshot for later Rubric evaluation."""
    tick: int
    action_id: str
    state: dict[str, Any]        # ActiveState snapshot (serialisable)
    pressures: dict[str, float]  # PressureVector snapshot
    derived: dict[str, float]    # DerivedCalculator output
    fired_events: list[str]      # event_ids fired THIS tick
    event_category: str          # "canonical" / "action_caused" / "voluntary"
    action_kind: str             # rough category for CharacterCritic
    fear_like: float             # For oscillation tracking
    # Step F: decision provenance (None for non-motif-mediated legacy paths)
    selected_motif: str | None = None
    motif_activations: dict[str, float] | None = None
    blocked_actions: list[str] | None = None
    dominant_pressure: str | None = None
    guilt_source: str | None = None
    shame_source: str | None = None


class PersonV3Loop:
    """v3 integrated simulation loop.

    Single-agent (scenario provided by content/). Rule-based policy default;
    can be swapped for neural policy (Rule #11 dual-path compatibility).
    """

    def __init__(
        self,
        *,
        initial_state_path: Path | str,
        canonical_events_path: Path | str,
        persona_profile: PersonaProfile | None = None,
        policy: Any | None = None,
        seed: int = 0,
    ) -> None:
        self._rng = random.Random(seed)
        self.state = self._load_initial_state(initial_state_path)
        self.events = EventRegistry()
        self.mapper = ActionEventMapper()
        self.derived = DerivedCalculator()
        self.pressure_layer = PressureLayer()
        self.primitives, self.schedule = self._load_scenario(canonical_events_path)
        self.policy = policy  # None → rule-based default
        self.transitions = StateTransitionEngine()
        # Step E: persona profile (default = baseline human). Scenario content
        # can override by passing profile explicitly.
        self.profile: PersonaProfile = persona_profile or DEFAULT_PROFILE

        self.trajectory: list[TrajectoryRecord] = []
        # event_id -> last-fired tick_index (for availability gate)
        self._recent_event_last_fired: dict[str, int] = {}
        # running tick index, for Recent lookup
        self._current_tick: int = 0
        # Step F: last decision provenance, filled by _decide_action
        self._last_selection = None

    @staticmethod
    def _load_initial_state(path: Path | str) -> ActiveState:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        kwargs: dict[str, Any] = {}
        kwargs.update(payload.get("scalar", {}))
        kwargs.update(payload.get("target_aware", {}))
        kwargs.update(payload.get("categorical", {}))
        return ActiveState(**kwargs)

    def _load_scenario(
        self, path: Path | str,
    ) -> tuple[PrimitiveState, dict[int, list[str]]]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        prim_defaults = payload.get("primitive_defaults", {})
        primitives = PrimitiveState(**prim_defaults)
        schedule: dict[int, list[str]] = {}
        for ev in payload.get("events", []):
            t = int(ev["tick"])
            schedule.setdefault(t, []).append(str(ev["event_id"]))
        return primitives, schedule

    # -----------------------------------------------------------------
    # Single tick
    # -----------------------------------------------------------------

    def tick(self, tick_index: int) -> TrajectoryRecord:
        self._current_tick = tick_index

        # 0. Decay event memory BEFORE this tick's events fire
        self.pressure_layer.decay_event_memory()

        # 1. Fire canonical events scheduled for this tick
        fired_this_tick: list[str] = []
        for event_id in self.schedule.get(tick_index, []):
            self.events.apply_to_primitives(event_id, self.primitives)
            self.pressure_layer.note_event(event_id, intensity=1.0)
            self._recent_event_last_fired[event_id] = tick_index
            fired_this_tick.append(event_id)

        # 1b. Transient primitive decay (D4 fix: prevents accusation/volatility
        # from staying at ceiling without refresh).
        self.primitives.decay_transients()

        # 2. Compute pressures (Layer C, Derived-only)
        pressures = self.pressure_layer.compute(self.primitives, self.state)

        # 3. Person decision (Dynamics Step 3: 2-stage availability gate)
        action_id = self._decide_action(pressures)

        # 4a. Apply Dynamics Step 4 direct edges (categories A–E)
        self.transitions.apply(
            self.state, self.primitives,
            TransitionContext(events_this_tick=list(fired_this_tick),
                              last_action=None),
        )

        # 4b. Apply action-specific consequences + pressure-side effects
        self._update_state_from_pressures_and_action(pressures, action_id)

        # 5. Action → Event → Primitive (closed loop, v2 §5)
        action_event_id = self.mapper.trigger_event_id(action_id)
        event_category = "canonical" if fired_this_tick else "action_caused" if action_event_id else "voluntary"
        if action_event_id is not None:
            self.events.apply_to_primitives(action_event_id, self.primitives)
            self.pressure_layer.note_event(action_event_id, intensity=1.0)
            self._recent_event_last_fired[action_event_id] = tick_index
            fired_this_tick.append(action_event_id)

        # 6. Record (with Step F provenance)
        derived_values = self.derived.compute_all(self.state)
        sel = self._last_selection
        pv = pressures.to_dict()
        dominant_pressure = max(pv, key=pv.get) if pv else None
        record = TrajectoryRecord(
            tick=tick_index,
            action_id=action_id,
            state=self._serialize_state(),
            pressures=pv,
            derived=derived_values,
            fired_events=fired_this_tick,
            event_category=event_category,
            action_kind=self._action_kind(action_id),
            fear_like=self.state.fear,
            # Step F provenance
            selected_motif=sel.selected_motif if sel else None,
            motif_activations=dict(sel.motif_activations) if sel else None,
            blocked_actions=list(sel.blocked_actions) if sel else None,
            dominant_pressure=dominant_pressure,
            guilt_source=self._infer_guilt_source(fired_this_tick),
            shame_source=self._infer_shame_source(fired_this_tick),
        )
        self.trajectory.append(record)
        return record

    def run(self, n_ticks: int) -> list[TrajectoryRecord]:
        for t in range(1, n_ticks + 1):
            self.tick(t)
        return self.trajectory

    # -----------------------------------------------------------------
    # Rule-based policy (default)
    # -----------------------------------------------------------------

    # Action vocabulary (subset of BC vocab, Rule #1 generic action_ids)
    ACTIONS: tuple[str, ...] = (
        "follow_closely", "pray", "discuss_with_disciples",
        "assert_loyalty", "withdraw_in_fear", "weep",
        "deny", "confess", "stay_awake", "fall_asleep",
        "draw_sword", "flee", "follow_at_distance",
        "stay_hiding", "run_to_tomb",
    )

    def _decide_action(self, pressures: PressureVector) -> str:
        """3-stage motif-mediated decision (Persona Engine transition, Step C).

        Stage 1: scene recognizer (recent events → event-recent flags)
        Stage 2: motif activator (pressure + state + profile → motif activations)
        Stage 3: action selector (top motifs + priors + availability gate)

        Direct action boosts (accusation → deny +8, etc.) removed per
        Persona Engine transition. All scene → action routing goes through
        motif layer. Persona differences expressed via profile parameters
        (content/<scenario>/profile.json), not engine code.

        Selection provenance stored on self._last_selection for trace.
        """
        # ---- Stage 1: scene recognizer (event recency flags) ----
        events_recent = {
            ev: 1 if (self._current_tick - t) <= 3 else 0
            for ev, t in self._recent_event_last_fired.items()
        }

        # ---- Stage 2: motif activator (persona profile modulates) ----
        motif_result = activate_motifs(
            state=self.state,
            pressures=pressures.to_dict(),
            events_recent=events_recent,
            profile=self.profile,
        )

        # ---- Stage 3: action selector with availability gate ----
        gate_ctx = GateContext(
            state=self.state,
            primitives=self.primitives,
            recent_events={
                ev: self._current_tick - t
                for ev, t in self._recent_event_last_fired.items()
            },
            tick_index=self._current_tick,
        )

        def _available(action: str) -> bool:
            return is_available(action, gate_ctx)

        selection = select_action(
            motif_result=motif_result,
            profile=self.profile,
            availability_filter=_available,
            rng=self._rng,
            default_action="follow_closely",
        )

        # Store provenance for TrajectoryRecord (Step F)
        self._last_selection = selection
        return selection.action

    # -----------------------------------------------------------------
    # Direct edges update (v2 §6 simplified)
    # -----------------------------------------------------------------

    def _update_state_from_pressures_and_action(
        self, pressures: PressureVector, action_id: str,
    ) -> None:
        """Action-specific consequences (grief path 3 + denial/confess/etc).

        Dynamics Step 4: bulk of pressure/event edges moved to
        StateTransitionEngine. This method now only handles action-caused
        side-effects. Passive trauma accumulation remains here.
        """
        # ---- grief path 3: action-induced expression ----
        if action_id == "weep":
            self.state.grief = min(10.0, self.state.grief + 0.5)
            # weeping partially relieves shame[self]
            if "self" in self.state.shame:
                self.state.shame["self"] = max(0.0, self.state.shame["self"] - 0.2)
        elif action_id == "withdraw_in_fear":
            self.state.grief = min(10.0, self.state.grief + 0.2)
            # withdrawal mildly reduces public shame but raises self-shame
            self.state.shame["self"] = min(10.0,
                self.state.shame.get("self", 0.0) + 0.2)

        # ---- denial / confess / flee / follow ----
        if action_id == "deny":
            self.state.guilt["primary_figure"] = min(10.0,
                self.state.guilt.get("primary_figure", 0.0) + 1.5)
            self.state.shame["self"] = min(10.0,
                self.state.shame.get("self", 0.0) + 0.8)
            self.state.loyalty["primary_figure"] = max(0.0,
                self.state.loyalty.get("primary_figure", 0.0) - 0.5)
        elif action_id == "confess":
            self.state.resolve = min(10.0, self.state.resolve + 0.5)
            self.state.guilt["primary_figure"] = max(0.0,
                self.state.guilt.get("primary_figure", 0.0) - 0.5)
        elif action_id == "flee":
            self.state.fear = min(10.0, self.state.fear + 0.5)
        elif action_id == "follow_closely":
            self.state.loyalty["primary_figure"] = min(10.0,
                self.state.loyalty.get("primary_figure", 0.0) + 0.1)
        elif action_id == "assert_loyalty":
            self.state.loyalty["primary_figure"] = min(10.0,
                self.state.loyalty.get("primary_figure", 0.0) + 0.2)
            self.state.resolve = min(10.0, self.state.resolve + 0.2)
        elif action_id == "pray":
            self.state.awe = min(10.0, self.state.awe + 0.15)
            if self.state.grief > 0:
                self.state.grief = max(0.0, self.state.grief - 0.1)

        # ---- Passive trauma accumulation: grief+guilt slowly surfaces trauma ----
        guilt_max = max(self.state.guilt.values()) if self.state.guilt else 0.0
        if self.state.grief > 5 or guilt_max > 5:
            self.state.trauma = min(10.0, self.state.trauma + 0.1)

        # Note: faith_stage is Derived now (Dynamics Step 1). Computed per-tick
        # via state_derived.faith_stage_tag(state). No direct mutation.

    # -----------------------------------------------------------------
    # Serialisation helpers
    # -----------------------------------------------------------------

    def _serialize_state(self) -> dict[str, Any]:
        d = self.state.model_dump()
        return d

    def _action_kind(self, action_id: str) -> str:
        if action_id in {"flee", "withdraw_in_fear", "stay_hiding", "follow_at_distance"}:
            return "avoid"
        if action_id in {"follow_closely", "assert_loyalty", "draw_sword", "run_to_tomb"}:
            return "approach"
        if action_id in {"pray", "weep", "confess"}:
            return "express"
        if action_id in {"deny", "fall_asleep"}:
            return "defensive"
        return "neutral"

    # -----------------------------------------------------------------
    # Step F: provenance inference helpers
    # -----------------------------------------------------------------

    _GUILT_SOURCE_EVENTS = {
        "public_accusation": "social_accusation",
        "crowd_mockery": "social_accusation",
        "betrayal_witnessed": "peer_failure",
        "eye_contact": "exposure",
        "primary_figure_suffering_visible": "vicarious_guilt",
    }
    _SHAME_SOURCE_EVENTS = {
        "public_accusation": "public_exposure",
        "crowd_mockery": "public_exposure",
        "eye_contact": "intimate_exposure",
        "betrayal_witnessed": "peer_failure",
    }

    def _infer_guilt_source(self, fired_events: list[str]) -> str | None:
        for ev in fired_events:
            if ev in self._GUILT_SOURCE_EVENTS:
                return self._GUILT_SOURCE_EVENTS[ev]
        return None

    def _infer_shame_source(self, fired_events: list[str]) -> str | None:
        for ev in fired_events:
            if ev in self._SHAME_SOURCE_EVENTS:
                return self._SHAME_SOURCE_EVENTS[ev]
        return None
