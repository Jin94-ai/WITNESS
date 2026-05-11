"""RoleCluster definitions (Step H).

10 generic role clusters with profile_prior + relation_template +
affordance_pack + info_access + resource_prior.

각 cluster는 새 agent 의 "기본 인격 틀". Scenario content 가 cluster 위에
overlay (예: canonical 인물 = 두 role_cluster 전환 + 강한 profile
overrides).

Rule #1: 여기 어떤 cluster도 인물/집단 고유명 포함 금지.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RelationTemplate:
    """Required / optional target roles for a cluster."""
    required: list[str] = field(default_factory=list)
    optional: list[str] = field(default_factory=list)


@dataclass
class RoleCluster:
    """Parameterized role definition."""
    role_id: str
    description: str
    # Profile prior — partial PersonaProfile dicts keyed by section
    # (pressure_sensitivity / motif_tendency / recovery_bias / relation_bias)
    profile_prior: dict[str, dict[str, float]] = field(default_factory=dict)
    # Gaussian perturbation σ applied to sampled profile values
    profile_variance: float = 0.15
    # Target roles needed
    relation_template: RelationTemplate = field(default_factory=RelationTemplate)
    # Action affordances typical for this role
    affordance_pack: list[str] = field(default_factory=list)
    # Information access level tag
    info_access_level: str = "default"
    # Resource prior tag
    resource_prior: str = "default"
    # State prior — sparse overrides on default ActiveState baseline
    state_prior: dict[str, float] = field(default_factory=dict)
    # Iter 5 — role-conditional reading of world memory.
    # Default 1.0 (baseline). Cold/deliberative roles lower; hot/reactive
    # roles higher. Used to modulate shame_climate / authority_vigilance
    # → agent pressures in MicroWorld._compute_agent_pressures.
    climate_sensitivity: float = 1.0
    # Iter 7 — role-conditional motif→action priors. When non-None,
    # overrides the shared motif_action_priors for any agent of this
    # role. Enables roles to pick fundamentally different actions
    # under the same motif activation.
    motif_action_priors: dict[str, dict[str, float]] | None = None


# =============================================================================
# 10 Role Clusters (Step H)
# =============================================================================

ROLE_CLUSTERS: dict[str, RoleCluster] = {

    "fisher_laborer": RoleCluster(
        role_id="fisher_laborer",
        description=(
            "Manual-labor laborer (fisher, farmer, craftsman). Strong peer bonds, "
            "low authority reactivity, middle impulsivity."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "urgency": 1.1, "isolation_pressure": 0.9,
                "sacred_salience": 0.9,
            },
            "motif_tendency": {
                "remain_present": 1.2, "confront": 1.1, "observe_wait": 0.9,
            },
            "relation_bias": {
                "peer_dependence": 1.3, "authority_reactivity": 0.7,
            },
        },
        profile_variance=0.15,
        relation_template=RelationTemplate(
            required=["peer_group", "family"],
            optional=["primary_focus"],
        ),
        affordance_pack=[
            "follow_closely", "discuss_with_disciples", "stay_awake",
            "assert_loyalty", "withdraw_in_fear",
        ],
        info_access_level="peer_network_medium",
        resource_prior="subsistence_steady",
        state_prior={"vitality": 7.0, "hope": 5.0, "fatigue": 4.0},
        climate_sensitivity=1.1,
        # Iter 11 — peer-bonded practical labor cluster. Physical actions
        # + peer-visible stance. Less concealment, more assertion.
        motif_action_priors={
            "conceal": {"withdraw_in_fear": 0.50, "follow_at_distance": 0.30,
                        "stay_awake": 0.20},
            "confess": {"assert_loyalty": 0.50, "confess": 0.30,
                        "discuss_with_disciples": 0.20},
            "withdraw": {"withdraw_in_fear": 0.45,
                         "follow_at_distance": 0.30,
                         "fall_asleep": 0.25},
            "remain_present": {"follow_closely": 0.55,
                               "stay_awake": 0.30,
                               "discuss_with_disciples": 0.15},
            "confront": {"assert_loyalty": 0.55, "stay_awake": 0.30,
                         "follow_closely": 0.15},
            "grieve": {"withdraw_in_fear": 0.55, "stay_awake": 0.25,
                       "discuss_with_disciples": 0.20},
            "seek_repair": {"discuss_with_disciples": 0.50,
                            "assert_loyalty": 0.30,
                            "follow_closely": 0.20},
            "observe_wait": {"stay_awake": 0.50,
                             "discuss_with_disciples": 0.35,
                             "follow_closely": 0.15},
        },
    ),

    "disciple_follower": RoleCluster(
        role_id="disciple_follower",
        description=(
            "Committed follower of a primary_focus. High attachment to spiritual/"
            "ideological leader, high peer dependence, high sacred sensitivity."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "sacred_salience": 1.4, "loyalty_pull": 1.3,
            },
            "motif_tendency": {
                "remain_present": 1.1, "seek_repair": 1.2,
            },
            "relation_bias": {
                "primary_focus_attachment_strength": 1.4,
                "peer_dependence": 1.2,
            },
        },
        profile_variance=0.12,
        relation_template=RelationTemplate(
            required=["primary_focus", "peer_group"],
            optional=["authority_group", "family"],
        ),
        affordance_pack=[
            "follow_closely", "pray", "discuss_with_disciples", "stay_awake",
            "assert_loyalty", "weep", "confess", "withdraw_in_fear",
        ],
        info_access_level="primary_focus_direct",
        resource_prior="communal_shared",
        state_prior={"hope": 7.0, "awe": 7.0, "vitality": 7.0, "doubt": 2.0},
        climate_sensitivity=0.9,
        # Iter 11 — devotion-oriented. Prayer, confession, loyalty dominate.
        motif_action_priors={
            "conceal": {"withdraw_in_fear": 0.45,
                        "follow_at_distance": 0.30,
                        "stay_awake": 0.25},
            "confess": {"confess": 0.55, "assert_loyalty": 0.25,
                        "weep": 0.20},
            "withdraw": {"pray": 0.45, "follow_at_distance": 0.30,
                         "withdraw_in_fear": 0.25},
            "remain_present": {"follow_closely": 0.60, "pray": 0.25,
                               "stay_awake": 0.15},
            "confront": {"assert_loyalty": 0.55, "pray": 0.30,
                         "stay_awake": 0.15},
            "grieve": {"weep": 0.55, "pray": 0.30,
                       "withdraw_in_fear": 0.15},
            "seek_repair": {"confess": 0.45, "pray": 0.30,
                            "assert_loyalty": 0.25},
            "observe_wait": {"pray": 0.40, "stay_awake": 0.35,
                             "discuss_with_disciples": 0.25},
        },
    ),

    "authority_priest": RoleCluster(
        role_id="authority_priest",
        description=(
            "Religious or political authority figure. High status concern, "
            "deliberative, public-exposure sensitive, rival-aware."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "shame_exposure": 1.3, "urgency": 1.2,
                "isolation_pressure": 0.7,
            },
            "motif_tendency": {
                "confront": 1.2, "observe_wait": 1.3, "remain_present": 0.9,
            },
            "relation_bias": {
                "authority_reactivity": 1.4,
                "public_exposure_sensitivity": 1.3,
            },
        },
        profile_variance=0.10,
        relation_template=RelationTemplate(
            required=["peer_group", "authority_group", "public_group"],
            optional=["rival", "family"],
        ),
        affordance_pack=[
            "discuss_with_disciples", "assert_loyalty", "stay_awake",
            "confess", "withdraw_in_fear",
        ],
        info_access_level="official_high",
        resource_prior="institutional_resources",
        state_prior={"resolve": 7.0, "doubt": 1.5, "hope": 6.0},
        climate_sensitivity=0.6,
        # Iter 11 — status-conscious authority. Rarely flees / weeps.
        # Prefers public stance + observation + measured assertion.
        motif_action_priors={
            "conceal": {"stay_awake": 0.40, "follow_at_distance": 0.35,
                        "withdraw_in_fear": 0.25},
            "confess": {"assert_loyalty": 0.45, "confess": 0.30,
                        "discuss_with_disciples": 0.25},
            "withdraw": {"follow_at_distance": 0.45, "stay_awake": 0.30,
                         "withdraw_in_fear": 0.25},
            "remain_present": {"stay_awake": 0.50,
                               "discuss_with_disciples": 0.35,
                               "assert_loyalty": 0.15},
            "confront": {"assert_loyalty": 0.60,
                         "discuss_with_disciples": 0.30,
                         "stay_awake": 0.10},
            "grieve": {"stay_awake": 0.55,
                       "discuss_with_disciples": 0.30,
                       "withdraw_in_fear": 0.15},
            "seek_repair": {"discuss_with_disciples": 0.55,
                            "assert_loyalty": 0.30,
                            "stay_awake": 0.15},
            "observe_wait": {"stay_awake": 0.50,
                             "discuss_with_disciples": 0.35,
                             "follow_at_distance": 0.15},
        },
    ),

    "merchant": RoleCluster(
        role_id="merchant",
        description=(
            "Trader / business operator. Deliberative, ambiguity-tolerant, "
            "information-rich via trade networks."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "uncertainty": 1.2, "urgency": 1.1,
            },
            "motif_tendency": {
                "observe_wait": 1.3, "remain_present": 1.0,
            },
            "relation_bias": {
                "peer_dependence": 1.0, "public_exposure_sensitivity": 1.1,
            },
        },
        profile_variance=0.15,
        relation_template=RelationTemplate(
            required=["peer_group", "public_group", "family"],
            optional=["authority_group", "rival"],
        ),
        affordance_pack=[
            "discuss_with_disciples", "follow_closely",
            "stay_awake", "withdraw_in_fear",
        ],
        info_access_level="trade_network_high",
        resource_prior="accumulated_capital",
        state_prior={"doubt": 3.0, "resolve": 6.0, "vitality": 6.0},
        climate_sensitivity=0.8,
        # Iter 11 — deliberative mercantile. Weighs options, avoids
        # dramatic actions. Discussion-heavy, distance-maintaining.
        motif_action_priors={
            "conceal": {"follow_at_distance": 0.45, "stay_hiding": 0.30,
                        "withdraw_in_fear": 0.25},
            "confess": {"discuss_with_disciples": 0.50,
                        "confess": 0.30,
                        "assert_loyalty": 0.20},
            "withdraw": {"follow_at_distance": 0.50,
                         "withdraw_in_fear": 0.30,
                         "fall_asleep": 0.20},
            "remain_present": {"discuss_with_disciples": 0.45,
                               "stay_awake": 0.35,
                               "follow_closely": 0.20},
            "confront": {"discuss_with_disciples": 0.55,
                         "assert_loyalty": 0.30,
                         "stay_awake": 0.15},
            "grieve": {"withdraw_in_fear": 0.45,
                       "discuss_with_disciples": 0.35,
                       "stay_awake": 0.20},
            "seek_repair": {"discuss_with_disciples": 0.60,
                            "assert_loyalty": 0.25,
                            "follow_closely": 0.15},
            "observe_wait": {"discuss_with_disciples": 0.45,
                             "stay_awake": 0.40,
                             "follow_at_distance": 0.15},
        },
    ),

    "outsider": RoleCluster(
        role_id="outsider",
        description=(
            "Socially marginal (outcast, foreigner, diseased, stigmatized). "
            "High isolation pressure sensitivity, authority-distant or hostile."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "isolation_pressure": 1.3, "shame_exposure": 1.2,
            },
            "motif_tendency": {
                "withdraw": 1.3, "observe_wait": 1.2, "confront": 0.8,
            },
            "relation_bias": {
                "peer_dependence": 0.6,
            },
        },
        profile_variance=0.20,  # 더 큰 편차
        relation_template=RelationTemplate(
            required=[],
            optional=["family", "peer_group"],
        ),
        affordance_pack=[
            "withdraw_in_fear", "stay_hiding", "follow_at_distance",
            "watch_quietly",
        ],
        info_access_level="peripheral_low",
        resource_prior="deprivation",
        state_prior={"hope": 3.0, "grief": 4.0, "doubt": 5.0, "vitality": 4.0},
        climate_sensitivity=1.4,
        # Iter 11 — marginal. Heavy on withdrawal, quiet observation,
        # hiding. Rarely asserts or confronts.
        motif_action_priors={
            "conceal": {"stay_hiding": 0.55, "withdraw_in_fear": 0.30,
                        "follow_at_distance": 0.15},
            "confess": {"weep": 0.45, "withdraw_in_fear": 0.35,
                        "confess": 0.20},
            "withdraw": {"stay_hiding": 0.50, "withdraw_in_fear": 0.30,
                         "follow_at_distance": 0.20},
            "remain_present": {"watch_quietly": 0.50,
                               "follow_at_distance": 0.30,
                               "stay_hiding": 0.20},
            "confront": {"withdraw_in_fear": 0.45, "stay_hiding": 0.30,
                         "watch_quietly": 0.25},
            "grieve": {"weep": 0.55, "stay_hiding": 0.30,
                       "withdraw_in_fear": 0.15},
            "seek_repair": {"watch_quietly": 0.45,
                            "follow_at_distance": 0.35,
                            "stay_hiding": 0.20},
            "observe_wait": {"watch_quietly": 0.55,
                             "stay_hiding": 0.30,
                             "follow_at_distance": 0.15},
        },
    ),

    "family_anchor": RoleCluster(
        role_id="family_anchor",
        description=(
            "Family-centered figure. Low impulsivity, high family attachment, "
            "protective of dependents, risk-averse."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "urgency": 1.2, "isolation_pressure": 1.1,
            },
            "motif_tendency": {
                "remain_present": 1.3, "withdraw": 1.1,
            },
            "relation_bias": {
                "primary_focus_attachment_strength": 1.3,
            },
        },
        profile_variance=0.12,
        relation_template=RelationTemplate(
            required=["family"],
            optional=["intimate_other", "peer_group"],
        ),
        affordance_pack=[
            "follow_closely", "discuss_with_disciples", "stay_awake",
            "withdraw_in_fear", "pray",
        ],
        info_access_level="household_network",
        resource_prior="modest_household",
        state_prior={"love": 7.0, "hope": 5.0, "vitality": 6.0},
        climate_sensitivity=1.2,
        # Iter 11 — kin-protective. Close presence, prayer, protective
        # vigilance. Avoids dramatic public action.
        motif_action_priors={
            "conceal": {"withdraw_in_fear": 0.45, "follow_closely": 0.30,
                        "stay_awake": 0.25},
            "confess": {"pray": 0.45, "confess": 0.30,
                        "assert_loyalty": 0.25},
            "withdraw": {"withdraw_in_fear": 0.50, "follow_closely": 0.30,
                         "fall_asleep": 0.20},
            "remain_present": {"follow_closely": 0.60, "stay_awake": 0.25,
                               "pray": 0.15},
            "confront": {"assert_loyalty": 0.45, "follow_closely": 0.35,
                         "stay_awake": 0.20},
            "grieve": {"weep": 0.45, "pray": 0.35,
                       "withdraw_in_fear": 0.20},
            "seek_repair": {"pray": 0.45, "follow_closely": 0.30,
                            "discuss_with_disciples": 0.25},
            "observe_wait": {"stay_awake": 0.45, "follow_closely": 0.30,
                             "pray": 0.25},
        },
    ),

    "crowd_participant": RoleCluster(
        role_id="crowd_participant",
        description=(
            "Anonymous crowd member. High volatility, information-susceptible, "
            "follows crowd energy."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "social_threat": 1.3, "shame_exposure": 1.2,
            },
            "motif_tendency": {
                "remain_present": 1.2, "confront": 1.2, "withdraw": 1.1,
            },
            "relation_bias": {
                "public_exposure_sensitivity": 1.3,
            },
        },
        profile_variance=0.25,  # very variable
        relation_template=RelationTemplate(
            required=[],
            optional=["in_group", "family"],
        ),
        affordance_pack=[
            "follow_closely", "flee", "withdraw_in_fear",
            "watch_quietly", "discuss_with_disciples",
        ],
        info_access_level="rumor_based",
        resource_prior="variable",
        state_prior={"hope": 4.0, "fear": 3.0, "confusion": 3.0},
        climate_sensitivity=1.4,
        # Iter 11 — volatile anonymous. Flees easily, follows, watches.
        # Strong rumor-driven pivots but low individual accountability.
        motif_action_priors={
            "conceal": {"flee": 0.40, "withdraw_in_fear": 0.35,
                        "watch_quietly": 0.25},
            "confess": {"discuss_with_disciples": 0.40,
                        "watch_quietly": 0.30,
                        "follow_closely": 0.30},
            "withdraw": {"flee": 0.50, "withdraw_in_fear": 0.30,
                         "watch_quietly": 0.20},
            "remain_present": {"follow_closely": 0.50,
                               "watch_quietly": 0.30,
                               "discuss_with_disciples": 0.20},
            "confront": {"follow_closely": 0.40,
                         "discuss_with_disciples": 0.35,
                         "flee": 0.25},
            "grieve": {"withdraw_in_fear": 0.45, "watch_quietly": 0.35,
                       "flee": 0.20},
            "seek_repair": {"discuss_with_disciples": 0.50,
                            "follow_closely": 0.30,
                            "watch_quietly": 0.20},
            "observe_wait": {"watch_quietly": 0.50,
                             "discuss_with_disciples": 0.30,
                             "follow_closely": 0.20},
        },
    ),

    "soldier_enforcer": RoleCluster(
        role_id="soldier_enforcer",
        description=(
            "Military / enforcement role. Duty-oriented, authority-compliant, "
            "impulsive under threat, empathy-restrained."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "urgency": 1.3, "physical_threat": 1.2,
            },
            "motif_tendency": {
                "confront": 1.3, "remain_present": 1.0,
            },
            "relation_bias": {
                "authority_reactivity": 1.3,
            },
        },
        profile_variance=0.10,
        relation_template=RelationTemplate(
            required=["peer_group", "authority_group"],
            optional=["family"],
        ),
        affordance_pack=[
            "draw_sword", "flee", "confront_threat", "follow_closely",
            "stay_awake", "withdraw_in_fear",
        ],
        info_access_level="command_chain",
        resource_prior="service_provisioned",
        state_prior={"resolve": 7.0, "anger": 3.0, "vitality": 7.0},
        climate_sensitivity=0.7,
        # Iter 11 — duty-bound, threat-reactive. Confront-first response,
        # physical actions over deliberation.
        motif_action_priors={
            "conceal": {"stay_awake": 0.45, "follow_closely": 0.35,
                        "withdraw_in_fear": 0.20},
            "confess": {"assert_loyalty": 0.55, "stay_awake": 0.30,
                        "follow_closely": 0.15},
            "withdraw": {"follow_closely": 0.45, "stay_awake": 0.30,
                         "withdraw_in_fear": 0.25},
            "remain_present": {"stay_awake": 0.50, "follow_closely": 0.30,
                               "assert_loyalty": 0.20},
            "confront": {"draw_sword": 0.50, "assert_loyalty": 0.30,
                         "stay_awake": 0.20},
            "grieve": {"stay_awake": 0.55, "withdraw_in_fear": 0.25,
                       "follow_closely": 0.20},
            "seek_repair": {"follow_closely": 0.45,
                            "assert_loyalty": 0.35,
                            "stay_awake": 0.20},
            "observe_wait": {"stay_awake": 0.60, "follow_closely": 0.25,
                             "assert_loyalty": 0.15},
        },
    ),

    "elite_strategist": RoleCluster(
        role_id="elite_strategist",
        description=(
            "Political/strategic operator. Highly deliberative, "
            "information-rich, rival-aware, moderate risk tolerance."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "uncertainty": 1.3, "shame_exposure": 0.8,
            },
            "motif_tendency": {
                "observe_wait": 1.4, "conceal": 1.2,
            },
            "relation_bias": {
                "authority_reactivity": 1.2, "peer_dependence": 0.8,
            },
        },
        profile_variance=0.10,
        relation_template=RelationTemplate(
            required=["rival", "peer_group"],
            optional=["authority_group", "family"],
        ),
        affordance_pack=[
            "discuss_with_disciples", "follow_at_distance", "stay_hiding",
            "withdraw_in_fear", "stay_awake",
        ],
        info_access_level="cross_network_high",
        resource_prior="political_capital",
        state_prior={"resolve": 6.0, "doubt": 3.0, "hope": 5.0},
        climate_sensitivity=0.3,
        # Iter 7 — strategist picks deliberative/concealing actions
        # over the default emotional set. Weights sum to 1.0 per motif.
        motif_action_priors={
            "conceal": {"stay_hiding": 0.55, "follow_at_distance": 0.30,
                       "withdraw_in_fear": 0.15},
            "observe_wait": {"stay_hiding": 0.40, "follow_at_distance": 0.35,
                             "stay_awake": 0.25},
            "withdraw": {"follow_at_distance": 0.50,
                         "stay_hiding": 0.30,
                         "withdraw_in_fear": 0.20},
            "remain_present": {"follow_at_distance": 0.55,
                               "stay_awake": 0.30,
                               "discuss_with_disciples": 0.15},
            "confront": {"discuss_with_disciples": 0.60,
                         "follow_at_distance": 0.25,
                         "stay_awake": 0.15},
            "grieve": {"withdraw_in_fear": 0.55, "stay_hiding": 0.30,
                       "follow_at_distance": 0.15},
            "seek_repair": {"discuss_with_disciples": 0.60,
                            "follow_at_distance": 0.25,
                            "stay_awake": 0.15},
            "confess": {"discuss_with_disciples": 0.70,
                        "follow_at_distance": 0.20,
                        "stay_awake": 0.10},
        },
    ),

    "spiritual_wanderer": RoleCluster(
        role_id="spiritual_wanderer",
        description=(
            "Ascetic, prophet, or wandering teacher. High sacred salience, "
            "low belonging need, very ambiguity-tolerant."
        ),
        profile_prior={
            "pressure_sensitivity": {
                "sacred_salience": 1.5, "isolation_pressure": 0.7,
            },
            "motif_tendency": {
                "observe_wait": 1.3, "seek_repair": 1.1,
            },
            "relation_bias": {
                "authority_reactivity": 0.6, "peer_dependence": 0.6,
            },
        },
        profile_variance=0.20,
        relation_template=RelationTemplate(
            required=[],
            optional=["primary_focus", "family"],
        ),
        affordance_pack=[
            "pray", "stay_awake", "follow_at_distance", "watch_quietly",
            "discuss_with_disciples", "weep",
        ],
        info_access_level="independent_observation",
        resource_prior="ascetic_minimal",
        state_prior={"awe": 7.0, "resolve": 7.0, "hunger": 4.0, "vitality": 5.0},
        climate_sensitivity=0.5,
        # Iter 11 — ascetic/prophet. Prayer-centered, sparse words,
        # little flight, high endurance.
        motif_action_priors={
            "conceal": {"pray": 0.40, "watch_quietly": 0.35,
                        "stay_awake": 0.25},
            "confess": {"pray": 0.55, "confess": 0.30,
                        "discuss_with_disciples": 0.15},
            "withdraw": {"pray": 0.45, "watch_quietly": 0.30,
                         "follow_at_distance": 0.25},
            "remain_present": {"pray": 0.45, "stay_awake": 0.35,
                               "watch_quietly": 0.20},
            "confront": {"pray": 0.40,
                         "discuss_with_disciples": 0.35,
                         "stay_awake": 0.25},
            "grieve": {"weep": 0.45, "pray": 0.40,
                       "watch_quietly": 0.15},
            "seek_repair": {"pray": 0.55, "confess": 0.25,
                            "discuss_with_disciples": 0.20},
            "observe_wait": {"watch_quietly": 0.50, "pray": 0.30,
                             "stay_awake": 0.20},
        },
    ),
}


def get_role_cluster(role_id: str) -> RoleCluster:
    """Fetch a role cluster definition. Raises KeyError if unknown."""
    if role_id not in ROLE_CLUSTERS:
        raise KeyError(
            f"Unknown role_id '{role_id}'. Available: {list(ROLE_CLUSTERS)}"
        )
    return ROLE_CLUSTERS[role_id]
