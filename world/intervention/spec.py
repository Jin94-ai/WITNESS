"""InterventionSpec — declarative counterfactual-experiment specification.

Spike 4 Phase 4A data model. One ``InterventionSpec`` = one
counterfactual: "what if we removed Judas?" / "what if hazard rates
were halved?" / "what if Pilate were lenient?". A spec never mutates
input configs; the ``InterventionEngine`` deep-copies then applies.

Each optional field represents one intervention primitive. Specs may
combine multiple primitives in a single experiment (e.g. remove Judas
AND halve hazard rates), though single-primitive experiments are the
recommended baseline.

Fields are intentionally loose (all optional, None = no-op) so content
packs can compose interventions by filling a subset. Unknown fields on
the dict form are silently ignored by the engine — forward-compatible.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InterventionSpec:
    """Declarative description of one counterfactual experiment."""

    intervention_id: str
    description: str = ""

    # --- Faction primitives ---------------------------------------------
    faction_influence_scale: dict[str, float] | None = None
    """Per-faction multiplier applied to initial_influence + target_influence."""

    faction_remove: list[str] | None = None
    """Faction ids to remove entirely from the factions_config."""

    faction_add: dict[str, dict[str, Any]] | None = None
    """New factions to inject (merged into factions_config['factions'])."""

    # --- Rumour primitives ----------------------------------------------
    rumor_spread_rate_scale: float | None = None
    """Scale factor on rumors_config.spread_rate_per_day."""

    rumor_credibility_decay_scale: float | None = None
    """Scale factor on rumors_config.credibility_decay_per_day."""

    # --- World-layer primitives -----------------------------------------
    hazard_rate_scale: float | None = None
    """Scale factor on hazard_events[*].hazard.base_rate (Person Engine side)."""

    crowd_trigger_threshold_override: float | None = None
    """Override politics_config.crowd_trigger_threshold."""

    pilate_bonus_override: float | None = None
    """Override politics_config.pilate_bonus."""

    pilate_approach_lead_days_override: int | None = None
    """Override politics_config.pilate_approach_lead_days."""

    # --- Calendar primitives --------------------------------------------
    passover_amplitude_scale: float | None = None
    """Scale factor on calendar_config.passover_amplitude."""

    # --- Agent primitives (Person Engine) -------------------------------
    agent_remove: list[str] | None = None
    """Agent ids to drop from the initial_states list."""

    # --- Metadata / auditing --------------------------------------------
    extras: dict[str, Any] = field(default_factory=dict)
    """Free-form dict for experiment metadata; engine ignores."""

    def is_null(self) -> bool:
        """True if this spec would apply no changes (control identity)."""
        return all(
            getattr(self, f) in (None, {}, [])
            for f in (
                "faction_influence_scale", "faction_remove", "faction_add",
                "rumor_spread_rate_scale", "rumor_credibility_decay_scale",
                "hazard_rate_scale", "crowd_trigger_threshold_override",
                "pilate_bonus_override", "pilate_approach_lead_days_override",
                "passover_amplitude_scale", "agent_remove",
            )
        )

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "InterventionSpec":
        """Parse from a dict (as loaded from a JSON content-pack file)."""
        known = {
            "intervention_id", "description",
            "faction_influence_scale", "faction_remove", "faction_add",
            "rumor_spread_rate_scale", "rumor_credibility_decay_scale",
            "hazard_rate_scale", "crowd_trigger_threshold_override",
            "pilate_bonus_override", "pilate_approach_lead_days_override",
            "passover_amplitude_scale", "agent_remove", "extras",
        }
        unknown = {k: payload[k] for k in payload if k not in known}
        extras = dict(payload.get("extras", {}))
        extras.update(unknown)  # forward-compat: keep unknown fields traceable
        return cls(
            intervention_id=payload["intervention_id"],
            description=payload.get("description", ""),
            faction_influence_scale=payload.get("faction_influence_scale"),
            faction_remove=payload.get("faction_remove"),
            faction_add=payload.get("faction_add"),
            rumor_spread_rate_scale=payload.get("rumor_spread_rate_scale"),
            rumor_credibility_decay_scale=payload.get(
                "rumor_credibility_decay_scale",
            ),
            hazard_rate_scale=payload.get("hazard_rate_scale"),
            crowd_trigger_threshold_override=payload.get(
                "crowd_trigger_threshold_override",
            ),
            pilate_bonus_override=payload.get("pilate_bonus_override"),
            pilate_approach_lead_days_override=payload.get(
                "pilate_approach_lead_days_override",
            ),
            passover_amplitude_scale=payload.get("passover_amplitude_scale"),
            agent_remove=payload.get("agent_remove"),
            extras=extras,
        )

    @classmethod
    def load(cls, path: Path | str) -> "InterventionSpec":
        """Load a spec from a JSON file on disk."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_json(payload)
