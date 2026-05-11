"""Role transition dynamics (B direction §14 condition 1 completion).

Agents can change role_id mid-simulation. Profile + affordance_pack +
info_access shift toward new role, while accumulated state (fear, shame,
guilt, trauma, relations) is preserved.

Design principles:
- Transitions happen via blend_factor in [0, 1]. 0 = no change, 1 = full
  overwrite. Default 0.6 — noticeable shift but prior identity visible.
- State is always preserved (agents carry their history).
- role_prior state overlays are not applied (would erase accumulated
  feelings); only profile + affordances + info_access change.
- Relation seeds are preserved as-is (agent already has relations).
- Provenance records a transition log entry.

Rule #1: Transitions use generic role ids only. Scenario content maps
canonical persons to role clusters and triggers.

Rule #12: transitions do not directly set agent.action. They shift the
profile which changes motif selection on subsequent ticks.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any

from engine.persona.profile import (
    MotifTendency,
    PersonaProfile,
    PressureSensitivity,
    RecoveryBias,
    RelationBias,
)
from engine.population.role_cluster import get_role_cluster


@dataclass
class RoleTransitionRecord:
    """Immutable record of a role transition event."""
    tick: int
    from_role: str
    to_role: str
    blend_factor: float
    reason: str = ""
    preserved_state_keys: list[str] = field(default_factory=list)


def _blend_dataclass(
    current: Any,
    prior_dict: dict[str, float],
    blend: float,
    baseline: float = 1.0,
) -> dict[str, float]:
    """Blend current dataclass values toward role prior.

    current_field_value * (1 - blend) + role_prior[field] * blend

    Fields present in current but not in prior_dict drift toward baseline
    by blend amount (so non-relevant sensitivities decay back to 1.0 in
    partial transitions).
    """
    out: dict[str, float] = {}
    for attr, cur_val in current.__dict__.items():
        if attr in prior_dict:
            target = float(prior_dict[attr])
        else:
            target = baseline
        new_val = float(cur_val) * (1.0 - blend) + target * blend
        out[attr] = max(0.0, min(2.0, new_val))
    return out


def blend_profile_toward_role(
    current_profile: PersonaProfile,
    new_role_id: str,
    *,
    blend_factor: float = 0.6,
    rng: random.Random | None = None,
    perturbation_variance: float = 0.05,
) -> PersonaProfile:
    """Return a new PersonaProfile blended toward new_role's priors.

    Args:
        current_profile: profile the agent currently has.
        new_role_id: role cluster id to blend toward.
        blend_factor: 0 = no change, 1 = overwrite to role prior. 0.6 default.
        rng: optional rng for small perturbation (identity when None).
        perturbation_variance: sigma of gaussian noise added post-blend.

    Returns:
        New PersonaProfile. motif_action_priors are preserved (same
        action repertoire, new motif weights).
    """
    if not 0.0 <= blend_factor <= 1.0:
        raise ValueError(f"blend_factor must be in [0, 1], got {blend_factor}")

    role = get_role_cluster(new_role_id)
    prior = role.profile_prior

    ps_blend = _blend_dataclass(
        current_profile.pressure_sensitivity,
        prior.get("pressure_sensitivity", {}),
        blend_factor,
    )
    mt_blend = _blend_dataclass(
        current_profile.motif_tendency,
        prior.get("motif_tendency", {}),
        blend_factor,
    )
    rb_blend = _blend_dataclass(
        current_profile.recovery_bias,
        prior.get("recovery_bias", {}),
        blend_factor,
    )
    rel_blend = _blend_dataclass(
        current_profile.relation_bias,
        prior.get("relation_bias", {}),
        blend_factor,
    )

    if rng is not None and perturbation_variance > 0:
        for bucket in (ps_blend, mt_blend, rb_blend, rel_blend):
            for k in bucket:
                bucket[k] = max(
                    0.0,
                    min(2.0, bucket[k] + rng.gauss(0.0, perturbation_variance)),
                )

    # Iter 7 — if target role has motif_action_priors override, use it.
    # Otherwise preserve the current profile's priors (same repertoire).
    if role.motif_action_priors is not None:
        new_priors = copy.deepcopy(role.motif_action_priors)
    else:
        new_priors = copy.deepcopy(current_profile.motif_action_priors)

    return PersonaProfile(
        name=current_profile.name,
        description=(
            f"{current_profile.description} | transitioned -> {new_role_id} "
            f"(blend={blend_factor:.2f})"
        ),
        pressure_sensitivity=PressureSensitivity(**ps_blend),
        motif_tendency=MotifTendency(**mt_blend),
        recovery_bias=RecoveryBias(**rb_blend),
        relation_bias=RelationBias(**rel_blend),
        motif_action_priors=new_priors,
        scene_family_overrides=current_profile.scene_family_overrides,
    )


@dataclass
class RoleTransitionResult:
    """Output of apply_role_transition — new profile + metadata."""
    new_profile: PersonaProfile
    new_role_id: str
    new_affordance_pack: list[str]
    new_info_access_level: str
    record: RoleTransitionRecord


def apply_role_transition(
    *,
    current_profile: PersonaProfile,
    current_role_id: str,
    new_role_id: str,
    tick: int,
    blend_factor: float = 0.6,
    reason: str = "",
    rng: random.Random | None = None,
    merge_affordances: bool = True,
) -> RoleTransitionResult:
    """Compute a role transition. Does not mutate inputs.

    Args:
        current_profile: agent's current profile.
        current_role_id: agent's current role id.
        new_role_id: target role id.
        tick: world tick at which transition occurs.
        blend_factor: profile blending weight.
        reason: free-text reason (e.g. "miracle_witness", "covert_bargain").
        rng: optional rng for perturbation.
        merge_affordances: if True, new pack = union(old, new role pack).
            If False, only new role's affordance pack (may restrict agent).

    Returns:
        RoleTransitionResult with new_profile, affordances, info_access,
        and a RoleTransitionRecord.
    """
    if new_role_id == current_role_id:
        raise ValueError(
            f"transition target same as current role '{current_role_id}'"
        )

    new_role = get_role_cluster(new_role_id)
    new_profile = blend_profile_toward_role(
        current_profile,
        new_role_id,
        blend_factor=blend_factor,
        rng=rng,
    )

    if merge_affordances:
        # Preserve old pack + add new pack items (deduped, order stable).
        # Old pack must come in via caller; handled at MicroWorld layer.
        new_pack = list(new_role.affordance_pack)
    else:
        new_pack = list(new_role.affordance_pack)

    record = RoleTransitionRecord(
        tick=tick,
        from_role=current_role_id,
        to_role=new_role_id,
        blend_factor=blend_factor,
        reason=reason,
    )

    return RoleTransitionResult(
        new_profile=new_profile,
        new_role_id=new_role_id,
        new_affordance_pack=new_pack,
        new_info_access_level=new_role.info_access_level,
        record=record,
    )
