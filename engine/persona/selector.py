"""Motif → Action selector (Step C stage 3).

Selection flow:
    1. Pick top-2 motifs by activation.
    2. For each motif, read profile.motif_action_priors[motif] — dict of
       action → prior_weight.
    3. Weighted sum across top-2 motifs (weighted by activation).
    4. Filter by availability gate.
    5. Sample weighted.

Rule #1: no person/group hardcoding. Profile comes from content.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from engine.persona.motif import MotifActivation
from engine.persona.profile import PersonaProfile


@dataclass
class ActionSelection:
    """Output of motif-based action selection."""
    action: str
    selected_motif: str
    motif_activations: dict[str, float]
    action_weights: dict[str, float]       # post-filter distribution
    blocked_actions: list[str]             # filtered by availability gate
    notes: list[str] = field(default_factory=list)


def select_action(
    motif_result: MotifActivation,
    profile: PersonaProfile,
    *,
    availability_filter=None,
    rng: random.Random | None = None,
    default_action: str = "follow_closely",
    blend_power: float = 2.0,
) -> ActionSelection:
    """Select an action given motif activations + profile priors.

    Args:
        motif_result: output of activate_motifs()
        profile: PersonaProfile with motif_action_priors
        availability_filter: callable(action_id) → bool (True = allowed).
            If None, all actions allowed.
        rng: random.Random instance. Creates fresh if None.
        default_action: fallback if no action passes gate.
        blend_power: exponent for top-2 motif blending (Iter 3 default
            2.0 = quadratic; 1.0 = linear). Iter 61 exposed for ablation.

    Returns:
        ActionSelection with chosen action + provenance.
    """
    rng = rng or random.Random()
    notes: list[str] = []

    # Step 1: exponent-weighted blend of top-2 motifs
    # (Iter 3 tuned 2.0 = quadratic; favors primary motif)
    motif_a, motif_b = motif_result.top_two
    act_a = motif_result.activations[motif_a] ** blend_power
    act_b = motif_result.activations[motif_b] ** blend_power
    total_act = max(act_a + act_b, 1e-6)

    priors_a = profile.motif_action_priors.get(motif_a, {})
    priors_b = profile.motif_action_priors.get(motif_b, {})

    weights: dict[str, float] = {}
    for action, w in priors_a.items():
        weights[action] = weights.get(action, 0.0) + w * (act_a / total_act)
    for action, w in priors_b.items():
        weights[action] = weights.get(action, 0.0) + w * (act_b / total_act)

    # If profile gave no priors for top motifs, fall back to default
    if not weights:
        notes.append(
            f"no motif_action_priors for top motifs {motif_result.top_two}; "
            f"using default"
        )
        return ActionSelection(
            action=default_action,
            selected_motif=motif_result.primary_motif,
            motif_activations=dict(motif_result.activations),
            action_weights={default_action: 1.0},
            blocked_actions=[],
            notes=notes,
        )

    # Step 2: apply availability filter
    blocked: list[str] = []
    if availability_filter is not None:
        surviving: dict[str, float] = {}
        for action, w in weights.items():
            if availability_filter(action):
                surviving[action] = w
            else:
                blocked.append(action)
        if surviving:
            weights = surviving
        else:
            # All blocked → fallback
            notes.append(
                f"all motif-preferred actions blocked by gate "
                f"({motif_result.primary_motif}); fallback"
            )
            weights = {default_action: 1.0}

    # Step 3: normalize + sample
    total = sum(weights.values())
    if total <= 0:
        return ActionSelection(
            action=default_action,
            selected_motif=motif_result.primary_motif,
            motif_activations=dict(motif_result.activations),
            action_weights=weights,
            blocked_actions=blocked,
            notes=notes + ["weights sum to 0; default"],
        )
    r = rng.random() * total
    cumulative = 0.0
    chosen = default_action
    for action, w in weights.items():
        cumulative += w
        if r <= cumulative:
            chosen = action
            break

    # Identify which motif drove the chosen action (primary if that motif
    # had higher contribution)
    contrib_a = priors_a.get(chosen, 0.0) * (act_a / total_act)
    contrib_b = priors_b.get(chosen, 0.0) * (act_b / total_act)
    driver_motif = motif_a if contrib_a >= contrib_b else motif_b

    return ActionSelection(
        action=chosen,
        selected_motif=driver_motif,
        motif_activations=dict(motif_result.activations),
        action_weights={k: v / total for k, v in weights.items()},
        blocked_actions=blocked,
        notes=notes,
    )
