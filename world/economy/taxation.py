"""Roman Taxation — Spike 5 Part 2 Phase 5D.2.

Collection intensity is driven by Pilate's ``political_pressure`` (via the
``pilate_political_pressure_last_tick`` input), and drives into zealot
militancy + crowd frustration on the *next* substep (Rule #9).

Independent of ``EconomyLayer`` (staple_price) — lives side-by-side.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaxationState:
    collection_intensity: float
    tax_collector_activity: float
    collection_cycle_day: int

    def snapshot(self) -> dict[str, float | int]:
        return {
            "collection_intensity": self.collection_intensity,
            "tax_collector_activity": self.tax_collector_activity,
            "collection_cycle_day": self.collection_cycle_day,
        }


@dataclass
class TaxationInputs:
    pilate_political_pressure_last_tick: float = 0.0
    dt_days: float = 1.0


class TaxationLayer:
    layer_id = "taxation"

    def __init__(self, *, config: dict[str, Any] | None = None) -> None:
        cfg = config or {}
        init = cfg.get("initial_state", {})
        dyn = cfg.get("dynamics", {})
        bounds = cfg.get("bounds", {})

        self._init_intensity = float(init.get("collection_intensity", 0.3))
        self._init_activity = float(init.get("tax_collector_activity", 0.4))
        self._init_cycle = int(init.get("collection_cycle_day", 30))

        self.pilate_gain = float(dyn.get("pilate_pressure_to_intensity_gain", 0.5))
        self.decay_per_day = float(dyn.get("intensity_decay_per_day", 0.02))
        self.intensity_to_zealot_gain = float(
            dyn.get("intensity_to_zealot_militancy_gain", 0.4),
        )
        self.intensity_to_frustration_gain = float(
            dyn.get("intensity_to_crowd_frustration_gain", 0.15),
        )

        self.intensity_floor = float(bounds.get("intensity_floor", 0.0))
        self.intensity_ceiling = float(bounds.get("intensity_ceiling", 1.0))
        self.activity_floor = float(bounds.get("activity_floor", 0.0))
        self.activity_ceiling = float(bounds.get("activity_ceiling", 1.0))

    @classmethod
    def from_config_path(cls, path: Path | str) -> "TaxationLayer":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(config=payload)

    def initial_state(self) -> TaxationState:
        return TaxationState(
            collection_intensity=self._init_intensity,
            tax_collector_activity=self._init_activity,
            collection_cycle_day=self._init_cycle,
        )

    def tick(self, state: TaxationState, inputs: TaxationInputs) -> TaxationState:
        dt = max(0.0, inputs.dt_days)
        pressure = max(0.0, inputs.pilate_political_pressure_last_tick)

        intensity = (
            state.collection_intensity
            + self.pilate_gain * pressure * dt
            - self.decay_per_day * dt
        )
        intensity = max(self.intensity_floor, min(self.intensity_ceiling, intensity))

        activity = state.tax_collector_activity + 0.5 * (intensity - state.tax_collector_activity) * dt
        activity = max(self.activity_floor, min(self.activity_ceiling, activity))

        return replace(
            state, collection_intensity=intensity, tax_collector_activity=activity,
        )

    def zealot_militancy_channel(self, state: TaxationState) -> float:
        return state.collection_intensity * self.intensity_to_zealot_gain

    def crowd_frustration_channel(self, state: TaxationState) -> float:
        return state.collection_intensity * self.intensity_to_frustration_gain
