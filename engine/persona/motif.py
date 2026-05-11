"""Response Motif Layer (Step B).

8 motifs between scene cues and actions. Activation functions are generic
(pressure + state based), scaled by PersonaProfile.motif_tendency.

Rule #1: no person/group proper names.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from engine.persona.profile import PersonaProfile

MOTIF_NAMES: tuple[str, ...] = (
    "conceal",
    "confess",
    "withdraw",
    "remain_present",
    "confront",
    "grieve",
    "seek_repair",
    "observe_wait",
)


@dataclass
class MotifActivation:
    """Activation output from motif layer."""
    activations: dict[str, float]           # motif → [0, 1]
    primary_motif: str                      # top-activation
    top_two: tuple[str, str]                # top 2 motifs (ordered)
    primary_activation: float
    notes: list[str]


# =============================================================================
# Helpers
# =============================================================================

def _sigmoid(x: float) -> float:
    if x > 30:
        return 1.0
    if x < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _get_state_scalar(state: Any, name: str) -> float:
    """Read a scalar attribute. Works for both ActiveState object and flat dict."""
    if hasattr(state, name):
        return float(getattr(state, name))
    if isinstance(state, dict):
        return float(state.get(name, 0.0))
    return 0.0


def _get_target_max(state: Any, field: str) -> float:
    """Read max value of a target-aware dict field."""
    if hasattr(state, field):
        d = getattr(state, field)
    elif isinstance(state, dict):
        d = state.get(field, {})
    else:
        return 0.0
    if isinstance(d, dict) and d:
        return float(max(d.values()))
    if isinstance(d, (int, float)):
        return float(d)
    return 0.0


def _get_target_value(state: Any, field: str, role: str = "primary_focus") -> float:
    """Read target-aware dict[role] value (falls back to primary_figure for
    backward compat)."""
    if hasattr(state, field):
        d = getattr(state, field)
    elif isinstance(state, dict):
        d = state.get(field, {})
    else:
        return 0.0
    if not isinstance(d, dict):
        return 0.0
    for k in (role, "primary_figure"):  # v3 legacy alias
        if k in d:
            return float(d[k])
    return 0.0


# =============================================================================
# Activation functions (generic, profile-scaled)
# =============================================================================

def _conceal(state, pressures, events_recent, profile) -> float:
    shame_exp = pressures.get("shame_exposure", 0.0) / 10.0
    social_threat = pressures.get("social_threat", 0.0) / 10.0
    fear = _get_state_scalar(state, "fear") / 10.0
    score = (
        0.5 * shame_exp
        + 0.4 * social_threat
        + 0.3 * max(0.0, fear - 0.3)
    )
    base = _sigmoid(4.0 * score - 1.5)
    return min(1.0, base * profile.pressure_sensitivity.shame_exposure
                       * profile.motif_tendency.conceal)


def _confess(state, pressures, events_recent, profile) -> float:
    guilt = _get_target_max(state, "guilt") / 10.0
    hope = _get_state_scalar(state, "hope") / 10.0
    # Iter 34: include forgiveness_emitted (spawned by peer confessions)
    # and public_confession (empathic propagation). Enables autonomous
    # confess cascade without external forgiveness_offered trigger.
    has_forgiveness = float(events_recent.get("forgiveness_offered", 0))
    has_restoration = float(events_recent.get("restoration_moment", 0))
    has_forgiveness_emitted = float(events_recent.get("forgiveness_emitted", 0))
    has_public_confession = float(events_recent.get("public_confession", 0))
    peer_confess_signal = max(has_forgiveness_emitted, has_public_confession)
    score = (
        0.5 * guilt
        + 0.2 * hope
        + 0.4 * max(has_forgiveness, has_restoration, peer_confess_signal)
    )
    base = _sigmoid(4.0 * score - 1.5)
    return min(1.0, base * profile.motif_tendency.confess)


def _withdraw(state, pressures, events_recent, profile) -> float:
    isolation = pressures.get("isolation_pressure", 0.0) / 10.0
    fear = _get_state_scalar(state, "fear") / 10.0
    score = 0.5 * isolation + 0.5 * fear
    base = _sigmoid(4.0 * score - 1.2)
    return min(1.0, base * profile.motif_tendency.withdraw
                       * profile.pressure_sensitivity.isolation_pressure)


def _remain_present(state, pressures, events_recent, profile) -> float:
    # Inverse to other pressures. Higher when most pressures low.
    max_pressure = max(
        pressures.get(k, 0.0) for k in (
            "social_threat", "shame_exposure", "physical_threat",
            "isolation_pressure",
        )
    ) / 10.0
    love_primary = _get_target_value(state, "love", "primary_focus") / 10.0
    loyalty_primary = _get_target_value(state, "loyalty", "primary_focus") / 10.0
    score = (
        0.5 * (1.0 - max_pressure)
        + 0.25 * love_primary
        + 0.25 * loyalty_primary
    )
    base = _sigmoid(4.0 * score - 1.5)
    return min(1.0, base * profile.motif_tendency.remain_present)


def _confront(state, pressures, events_recent, profile) -> float:
    anger = _get_state_scalar(state, "anger") / 10.0
    physical_threat = pressures.get("physical_threat", 0.0) / 10.0
    loyalty = _get_target_max(state, "loyalty") / 10.0
    score = (
        0.5 * anger
        + 0.4 * physical_threat
        + 0.3 * loyalty
    )
    base = _sigmoid(4.0 * score - 2.0)
    return min(1.0, base * profile.motif_tendency.confront
                       * profile.pressure_sensitivity.physical_threat)


def _grieve(state, pressures, events_recent, profile) -> float:
    grief = _get_state_scalar(state, "grief") / 10.0
    guilt = _get_target_max(state, "guilt") / 10.0
    has_eye_contact = float(events_recent.get("eye_contact", 0))
    has_suffering = float(events_recent.get("primary_figure_suffering_visible", 0))
    score = (
        0.5 * grief
        + 0.3 * guilt
        + 0.3 * max(has_eye_contact, has_suffering)
    )
    base = _sigmoid(4.0 * score - 1.3)
    return min(1.0, base * profile.motif_tendency.grieve)


def _seek_repair(state, pressures, events_recent, profile) -> float:
    """seek_repair requires something to repair (guilt > threshold OR
    explicit repair context). Hope/trust modulate but don't drive."""
    guilt = _get_target_max(state, "guilt") / 10.0
    hope = _get_state_scalar(state, "hope") / 10.0
    trust_primary = _get_target_value(state, "trust", "primary_focus") / 10.0
    has_forgiveness = float(events_recent.get("forgiveness_offered", 0))
    has_restoration = float(events_recent.get("restoration_moment", 0))

    # Gate: need guilt or repair context. Without either, no seek_repair.
    gate = max(guilt - 0.2, has_forgiveness, has_restoration)
    if gate <= 0:
        return 0.0

    score = (
        0.5 * guilt
        + 0.2 * hope
        + 0.2 * trust_primary
        + 0.4 * max(has_forgiveness, has_restoration)
    )
    base = _sigmoid(4.0 * score - 2.0) * gate
    return min(1.0, base * profile.motif_tendency.seek_repair)


def _observe_wait(state, pressures, events_recent, profile) -> float:
    uncertainty = pressures.get("uncertainty", 0.0) / 10.0
    urgency = pressures.get("urgency", 0.0) / 10.0
    score = 0.5 * uncertainty - 0.3 * urgency
    base = _sigmoid(4.0 * score - 0.5)
    return min(1.0, base * profile.motif_tendency.observe_wait)


_MOTIF_FUNCS = {
    "conceal":        _conceal,
    "confess":        _confess,
    "withdraw":       _withdraw,
    "remain_present": _remain_present,
    "confront":       _confront,
    "grieve":         _grieve,
    "seek_repair":    _seek_repair,
    "observe_wait":   _observe_wait,
}


# =============================================================================
# Top-level
# =============================================================================

def activate_motifs(
    state: Any,
    pressures: dict[str, float],
    events_recent: dict[str, int],
    profile: PersonaProfile,
) -> MotifActivation:
    """Compute activation level for each motif.

    Args:
        state: ActiveState instance or flat dict with state fields.
        pressures: {pressure_name: value 0-10}
        events_recent: {event_id: 1 if within lookback else 0}
        profile: PersonaProfile modulating activations.

    Returns:
        MotifActivation with per-motif [0, 1] and top-2.
    """
    activations: dict[str, float] = {}
    for name, fn in _MOTIF_FUNCS.items():
        activations[name] = fn(state, pressures, events_recent, profile)

    # Sort descending
    ranked = sorted(activations.items(), key=lambda kv: -kv[1])
    primary = ranked[0][0]
    primary_v = ranked[0][1]
    top_two = (ranked[0][0], ranked[1][0] if len(ranked) > 1 else ranked[0][0])

    notes = [f"primary={primary} ({primary_v:.2f})"]
    if primary_v < 0.2:
        notes.append("all motifs weak — default to remain_present")
        primary = "remain_present"
        top_two = ("remain_present", ranked[0][0])

    return MotifActivation(
        activations=activations,
        primary_motif=primary,
        top_two=top_two,
        primary_activation=activations[primary],
        notes=notes,
    )
