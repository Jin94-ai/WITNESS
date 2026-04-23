"""Temple Economy — Spike 5 Part 2 Phase 5D.1.

Independent sub-layer that tracks money-changer fee, sacrifice animal price,
and temple tax; plus a ``crowd_frustration`` scalar that is the indirect
channel into ``jesus_movement.sympathy`` (see cross_economy.py).

Rule #6/#7 preserved: this module does NOT modify ``EconomyState`` or
``world/economy/economy.py``. It carries its own state dataclass.

Rule #9 preserved: state mutations from external events (Jesus cleansing,
Caiaphas decree) are consumed as *pending inputs* and applied on the next
``tick(...)`` call — never same-substep.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TempleEconomyState:
    money_changer_fee: float
    sacrifice_animal_price: float
    temple_tax: float
    crowd_frustration: float

    def snapshot(self) -> dict[str, float]:
        return {
            "money_changer_fee": self.money_changer_fee,
            "sacrifice_animal_price": self.sacrifice_animal_price,
            "temple_tax": self.temple_tax,
            "crowd_frustration": self.crowd_frustration,
        }


@dataclass
class TempleEconomyInputs:
    """Inputs consumed once per tick. Mutations on the same tick stay buffered."""
    active_feast: str = "none"
    jesus_cleansing_fired_last_tick: bool = False
    caiaphas_decree_intensity_last_tick: float = 0.0
    dt_days: float = 1.0


class TempleEconomyLayer:
    layer_id = "temple_economy"

    def __init__(self, *, config: dict[str, Any] | None = None) -> None:
        cfg = config or {}
        init = cfg.get("initial_state", {})
        dyn = cfg.get("dynamics", {})
        bounds = cfg.get("bounds", {})

        self._init_fee = float(init.get("money_changer_fee", 1.0))
        self._init_sacrifice = float(init.get("sacrifice_animal_price", 2.0))
        self._init_tax = float(init.get("temple_tax", 0.5))
        self._init_frustration = float(init.get("crowd_frustration", 0.0))

        self.passover_fee_mult = float(dyn.get("passover_fee_multiplier", 2.5))
        self.passover_sacrifice_mult = float(dyn.get("passover_sacrifice_multiplier", 2.0))
        self.passover_frustration_gain = float(dyn.get("passover_crowd_frustration_gain", 0.08))
        self.cleansing_fee_drop = float(dyn.get("cleansing_fee_drop_factor", 0.2))
        self.cleansing_sacrifice_drop = float(dyn.get("cleansing_sacrifice_drop_factor", 0.3))
        self.decree_fee_adjust = float(dyn.get("decree_fee_adjust_per_unit", 0.4))
        self.decree_sacrifice_adjust = float(dyn.get("decree_sacrifice_adjust_per_unit", 0.5))
        self.frustration_decay = float(dyn.get("frustration_decay_per_day", 0.05))
        self.frustration_to_sympathy = float(dyn.get("frustration_to_jesus_sympathy_gain", 0.12))

        self.fee_floor = float(bounds.get("fee_floor", 0.5))
        self.fee_ceiling = float(bounds.get("fee_ceiling", 5.0))
        self.sacrifice_floor = float(bounds.get("sacrifice_floor", 1.0))
        self.sacrifice_ceiling = float(bounds.get("sacrifice_ceiling", 8.0))
        self.frustration_ceiling = float(bounds.get("crowd_frustration_ceiling", 1.0))

    @classmethod
    def from_config_path(cls, path: Path | str) -> "TempleEconomyLayer":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(config=payload)

    def initial_state(self) -> TempleEconomyState:
        return TempleEconomyState(
            money_changer_fee=self._init_fee,
            sacrifice_animal_price=self._init_sacrifice,
            temple_tax=self._init_tax,
            crowd_frustration=self._init_frustration,
        )

    def tick(
        self, state: TempleEconomyState, inputs: TempleEconomyInputs,
    ) -> TempleEconomyState:
        fee = state.money_changer_fee
        sacrifice = state.sacrifice_animal_price
        frustration = state.crowd_frustration
        dt = max(0.0, inputs.dt_days)

        if inputs.active_feast == "passover":
            fee = fee * self.passover_fee_mult
            sacrifice = sacrifice * self.passover_sacrifice_mult
            frustration = frustration + self.passover_frustration_gain * dt

        if inputs.jesus_cleansing_fired_last_tick:
            fee = fee * (1.0 - self.cleansing_fee_drop)
            sacrifice = sacrifice * (1.0 - self.cleansing_sacrifice_drop)

        decree = inputs.caiaphas_decree_intensity_last_tick
        if decree != 0.0:
            fee = fee + self.decree_fee_adjust * decree
            sacrifice = sacrifice + self.decree_sacrifice_adjust * decree

        frustration = frustration - self.frustration_decay * dt
        frustration = max(0.0, min(self.frustration_ceiling, frustration))
        fee = max(self.fee_floor, min(self.fee_ceiling, fee))
        sacrifice = max(self.sacrifice_floor, min(self.sacrifice_ceiling, sacrifice))

        return replace(
            state,
            money_changer_fee=fee,
            sacrifice_animal_price=sacrifice,
            crowd_frustration=frustration,
        )

    def frustration_channel(self, state: TempleEconomyState) -> float:
        """Exported channel into jesus_movement.sympathy (indirect)."""
        return state.crowd_frustration * self.frustration_to_sympathy
