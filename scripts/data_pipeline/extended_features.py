"""Phase B -- Event context feature.

Spec §3.2 verbatim:
    extended_features = [
        # 기존 12 feature
        fear, hope, grief, confusion, love,
        fatigue, hunger, health,
        moral_injury, identity_shift, event_trauma, trust_scar,
        # 신규 3-5 feature
        recent_event_id,       # 최근 발생 event의 categorical ID
        time_since_event,      # 최근 event로부터 경과 tick
        hazard_proximity,      # 가까운 hazard까지 거리 (optional)
    ]

15-dim extended feature. Backward compat: original `state_to_feature_vector`
untouched (scripts/ 수준 신규 함수, Rule #6 내부).

`recent_event_id` encoding: stable integer index into a canonical event
vocabulary. ``0`` reserved for "no event yet seen".

`time_since_event` / `hazard_proximity` normalized to [0, 1] by ``max_tick``
so the MLP doesn't need to learn an extra scale.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.core.state import AgentState
from engine.simulation.training_samples import state_to_feature_vector

# Stable event vocabulary -- ordered list, index position is the encoded ID.
# Index 0 reserved for "no event yet". canonical events + hazard templates
# observed across Peter baseline harvest.
EVENT_VOCAB: list[str] = [
    "__none__",  # index 0
    # canonical events
    "scene_01_jerusalem_entry",
    "scene_02_temple_cleansing",
    "scene_03_olivet_discourse",
    "scene_04_passover_preparation",
    "scene_05_foot_washing",
    "scene_06_last_supper",
    "scene_07_gethsemane",
    "scene_08_arrest",
    "scene_09_denial_1",
    "scene_09_denial_2",
    "scene_09_denial_3",
    "scene_10_crucifixion",
    "scene_11_sabbath",
    "scene_12_empty_tomb",
    "scene_13_road_to_emmaus",
    "scene_14_upper_room",
    "scene_15_tiberias",
    "scene_16_restoration",
    "scene_17_ascension",
    # hazards / triggers observed
    "last_supper",
    "gethsemane",
    "arrest",
    "denial_challenge",
    "empty_tomb",
    "tiberias_encounter",
    "temple_tension",
    "surveillance_escalation",
    "crowd_pressure_spike",
    "intelligence_received",
    "crowd_pressure_event",
    "voluntary",  # placeholder when action came from profile, not event
]

_VOCAB_INDEX = {name: i for i, name in enumerate(EVENT_VOCAB)}


def event_id_to_index(event_id: str | None) -> int:
    """Encode event_id as stable integer. Unknown → 0 (same as 'none')."""
    if event_id is None:
        return 0
    return _VOCAB_INDEX.get(event_id, 0)


def state_to_extended_feature_vector(
    state: AgentState,
    *,
    recent_event_id: str | None = None,
    time_since_event: float = 0.0,
    hazard_proximity: float = 1.0,
    max_tick_norm: float = 200.0,
) -> list[float]:
    """12-dim base + 3-dim context = 15-dim.

    Args:
        state: AgentState (12-dim base via state_to_feature_vector)
        recent_event_id: most recent fired event id at or before current tick
        time_since_event: ticks since that event (clamp/normalize)
        hazard_proximity: ticks until next scheduled hazard (or 1.0 if far)

    Returns:
        list[float] length 15.
    """
    base = state_to_feature_vector(state)  # 12
    eid = event_id_to_index(recent_event_id)
    # Normalize categorical index to [0, 1] for MLP stability.
    # The MLP can still learn categorical boundaries; index is just a compact encoding.
    eid_norm = eid / max(1, len(EVENT_VOCAB) - 1)
    t_norm = min(1.0, max(0.0, time_since_event / max_tick_norm))
    hp_norm = min(1.0, max(0.0, hazard_proximity / max_tick_norm))
    return base + [eid_norm, t_norm, hp_norm]


def extract_event_context_per_tick(result: Any) -> dict[int, dict[str, Any]]:
    """From a MultiAgentResult, build per-tick context:
        {tick: {recent_event_id: str, time_since_event: int, hazard_proximity: int}}
    """
    fired = list(getattr(result, "fired_events", []))
    fired_ticks = [(int(e["tick"]), str(e["event_id"])) for e in fired]
    fired_ticks.sort()

    # Max tick
    all_peter = result.state_snapshots.get("peter", {})
    max_tick = max(all_peter.keys()) if all_peter else 0

    ctx: dict[int, dict[str, Any]] = {}
    most_recent_event_id: str | None = None
    most_recent_event_tick: int | None = None
    fired_idx = 0

    for t in range(max_tick + 1):
        # Advance fired_idx past events at or before t
        while fired_idx < len(fired_ticks) and fired_ticks[fired_idx][0] <= t:
            most_recent_event_tick, most_recent_event_id = (
                fired_ticks[fired_idx][0], fired_ticks[fired_idx][1],
            )
            fired_idx += 1
        time_since = (t - most_recent_event_tick) if most_recent_event_tick is not None else max_tick
        # Hazard proximity: ticks until next event at or after t
        next_ev_tick = None
        for ev_tick, _ in fired_ticks:
            if ev_tick >= t:
                next_ev_tick = ev_tick
                break
        hp = (next_ev_tick - t) if next_ev_tick is not None else max_tick
        ctx[t] = {
            "recent_event_id": most_recent_event_id,
            "time_since_event": time_since,
            "hazard_proximity": hp,
        }
    return ctx


def serialize_vocab(path: Path | str) -> None:
    """Persist the event vocab for reproducibility (feature_config.json sibling)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps({"event_vocab": EVENT_VOCAB, "n_vocab": len(EVENT_VOCAB)},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


__all__ = [
    "EVENT_VOCAB",
    "event_id_to_index",
    "state_to_extended_feature_vector",
    "extract_event_context_per_tick",
    "serialize_vocab",
]
