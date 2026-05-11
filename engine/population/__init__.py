"""Population Engine (Step H/K implementation).

인물 = role_cluster + persona profile + relation seeds + initial state + world
binding. Handcraft 문서 없이 config 단위로 agent 생성.

Rule #1 준수: role 이름은 generic. 특정 인물/집단 고유명은 content binding에서만.
"""

from engine.population.generator import (
    AgentConfig,
    InstantiatedAgent,
    generate_population,
    instantiate_agent,
)
from engine.population.history_tags import (
    HISTORY_TAG_DELTAS,
    apply_recent_history,
)
from engine.population.role_cluster import (
    ROLE_CLUSTERS,
    RoleCluster,
    get_role_cluster,
)
from engine.population.transitions import (
    RoleTransitionRecord,
    RoleTransitionResult,
    apply_role_transition,
    blend_profile_toward_role,
)

__all__ = [
    "RoleCluster", "ROLE_CLUSTERS", "get_role_cluster",
    "AgentConfig", "InstantiatedAgent",
    "instantiate_agent", "generate_population",
    "HISTORY_TAG_DELTAS", "apply_recent_history",
    "RoleTransitionRecord", "RoleTransitionResult",
    "apply_role_transition", "blend_profile_toward_role",
]
