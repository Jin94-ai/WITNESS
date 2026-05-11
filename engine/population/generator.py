"""Agent generator (Step K implementation).

7-field config → instantiated agent with profile + relations + state.

Bulk generation for a world population via role distribution.
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
from engine.population.history_tags import apply_recent_history
from engine.population.role_cluster import RoleCluster, get_role_cluster

# =============================================================================
# Config + output dataclasses
# =============================================================================

@dataclass
class AgentConfig:
    """Minimum 7-field config for an agent."""
    agent_id: str
    role_cluster: str
    profile_overrides: dict[str, dict[str, float]] = field(default_factory=dict)
    relation_seeds: dict[str, Any] = field(default_factory=dict)
    initial_state_seed: dict[str, float] = field(default_factory=dict)
    recent_history: str = ""
    faction_affiliation: dict[str, Any] = field(default_factory=dict)
    info_access_level: str | None = None  # override role default if set
    seed: int | None = None


@dataclass
class InstantiatedAgent:
    """Output of instantiate_agent(): ready-to-sim bundle."""
    agent_id: str
    role_id: str
    profile: PersonaProfile
    relations: dict[str, Any]
    initial_state: dict[str, Any]
    affordance_pack: list[str]
    info_access_level: str
    resource_prior: str
    faction_affiliation: dict[str, Any]
    provenance: dict[str, Any]  # record of how this agent was built


# =============================================================================
# Profile sampling
# =============================================================================

def _deep_merge(base: dict, overrides: dict) -> dict:
    """Merge overrides into base recursively. Does not mutate base."""
    out = copy.deepcopy(base)
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _perturb_profile(
    profile_dict: dict[str, dict[str, float]],
    variance: float,
    rng: random.Random,
) -> dict[str, dict[str, float]]:
    """Apply gaussian perturbation to each numeric value. Clamp to [0, 2]."""
    out = {}
    for section, params in profile_dict.items():
        out[section] = {}
        for k, v in params.items():
            if isinstance(v, (int, float)):
                perturbed = float(v) + rng.gauss(0, variance)
                out[section][k] = max(0.0, min(2.0, perturbed))
            else:
                out[section][k] = v
    return out


def _build_persona_profile(
    name: str, description: str, profile_dict: dict,
) -> PersonaProfile:
    """Build PersonaProfile from nested dict. Missing fields get defaults."""
    ps_dict = profile_dict.get("pressure_sensitivity", {})
    mt_dict = profile_dict.get("motif_tendency", {})
    rb_dict = profile_dict.get("recovery_bias", {})
    rel_dict = profile_dict.get("relation_bias", {})
    return PersonaProfile(
        name=name,
        description=description,
        pressure_sensitivity=PressureSensitivity(**ps_dict),
        motif_tendency=MotifTendency(**mt_dict),
        recovery_bias=RecoveryBias(**rb_dict),
        relation_bias=RelationBias(**rel_dict),
        motif_action_priors=profile_dict.get("motif_action_priors", {}),
    )


# =============================================================================
# Relations
# =============================================================================

def _build_relations(
    role: RoleCluster,
    seeds: dict[str, Any],
) -> dict[str, Any]:
    """Populate relation map from role template + provided seeds.

    Validates: required roles must have a seed (raise ValueError if missing).
    Optional roles without seeds are null.
    """
    relations: dict[str, Any] = {}
    for req_role in role.relation_template.required:
        if req_role not in seeds:
            raise ValueError(
                f"role '{role.role_id}' requires relation '{req_role}' "
                "but none provided in config.relation_seeds"
            )
        relations[req_role] = seeds[req_role]
    for opt_role in role.relation_template.optional:
        if opt_role in seeds:
            relations[opt_role] = seeds[opt_role]
        else:
            relations[opt_role] = None
    # Include any extra seeds not in template
    for k, v in seeds.items():
        if k not in relations:
            relations[k] = v
    return relations


# =============================================================================
# Initial state
# =============================================================================

# Default baseline state (neutral human). Used as starting point.
DEFAULT_BASELINE_STATE: dict[str, float] = {
    "fear": 2.0, "hope": 5.0, "grief": 1.0, "confusion": 2.0,
    "joy": 4.0, "anger": 2.0, "awe": 3.0, "fatigue": 3.0,
    "hunger": 2.0, "vitality": 6.0, "doubt": 2.0, "resolve": 5.0,
    "trauma": 0.5,
}


def _build_state(
    role: RoleCluster, seed_overrides: dict[str, float], history: str,
) -> dict[str, float]:
    state = copy.deepcopy(DEFAULT_BASELINE_STATE)
    # Apply role prior
    for k, v in role.state_prior.items():
        state[k] = float(v)
    # Apply config seed overrides
    for k, v in seed_overrides.items():
        if k in state:
            state[k] = max(0.0, min(10.0, float(v)))
    # Apply recent history free-text tags
    apply_recent_history(state, history)
    return state


# =============================================================================
# Main API
# =============================================================================

def instantiate_agent(
    config: AgentConfig | dict,
) -> InstantiatedAgent:
    """Instantiate a single agent from a minimum 7-field config.

    Accepts either an AgentConfig dataclass or a dict (will be coerced).
    """
    if isinstance(config, dict):
        config = AgentConfig(**{
            k: v for k, v in config.items()
            if k in AgentConfig.__dataclass_fields__
        })

    rng = random.Random(config.seed)
    role = get_role_cluster(config.role_cluster)

    # 1. Profile: role prior + user overrides + gaussian perturbation
    merged = _deep_merge(role.profile_prior, config.profile_overrides)
    perturbed = _perturb_profile(merged, role.profile_variance, rng)
    profile = _build_persona_profile(
        name=config.agent_id,
        description=f"Generated from role '{role.role_id}'",
        profile_dict=perturbed,
    )
    # Attach sensible motif_action_priors if not overridden. Pulled from
    # DEFAULT_PROFILE (baseline) as safe fallback.
    if not profile.motif_action_priors:
        from engine.persona.profile import DEFAULT_PROFILE
        profile.motif_action_priors = copy.deepcopy(
            DEFAULT_PROFILE.motif_action_priors
        )

    # 2. Relations (required + optional)
    relations = _build_relations(role, config.relation_seeds)

    # 3. Initial state
    state = _build_state(
        role, config.initial_state_seed, config.recent_history,
    )

    # 4. Info access: override if provided, else role default
    info_access = config.info_access_level or role.info_access_level

    provenance = {
        "role_id": role.role_id,
        "profile_perturbation_seed": config.seed,
        "recent_history_applied": bool(config.recent_history),
        "relation_seeds_keys": list(config.relation_seeds.keys()),
        "override_sections": list(config.profile_overrides.keys()),
    }

    return InstantiatedAgent(
        agent_id=config.agent_id,
        role_id=role.role_id,
        profile=profile,
        relations=relations,
        initial_state=state,
        affordance_pack=list(role.affordance_pack),
        info_access_level=info_access,
        resource_prior=role.resource_prior,
        faction_affiliation=dict(config.faction_affiliation),
        provenance=provenance,
    )


def generate_population(
    role_distribution: dict[str, float],
    total_agents: int,
    *,
    seed_base: int = 0,
    id_prefix: str = "agent",
) -> list[InstantiatedAgent]:
    """Bulk-generate agents according to role distribution.

    Args:
        role_distribution: {role_id: proportion}. Should sum to ~1.0.
        total_agents: total number of agents to create.
        seed_base: base RNG seed for reproducibility.
        id_prefix: prefix for auto-generated agent_ids.

    Returns:
        list of InstantiatedAgent. Count may vary slightly from total_agents
        due to rounding.
    """
    agents: list[InstantiatedAgent] = []
    counter = 0
    for role_id, proportion in role_distribution.items():
        n = max(1, int(round(total_agents * proportion)))
        for i in range(n):
            config = AgentConfig(
                agent_id=f"{id_prefix}_{role_id}_{i:03d}",
                role_cluster=role_id,
                relation_seeds={},
                seed=seed_base + counter,
            )
            # Required relations are skipped gracefully for bulk gen:
            # we generate placeholder relation names.
            role = get_role_cluster(role_id)
            for req in role.relation_template.required:
                config.relation_seeds[req] = f"placeholder_{req}_{role_id}"
            agents.append(instantiate_agent(config))
            counter += 1
    return agents
