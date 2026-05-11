"""4-axis Discovery Rubric (v3.0 Phase 4 → Phase H 재설계).

Phase H (2026-04-23, Rule #24): 4축 = character_consistency +
scene_response_fit + context_break + novelty (structured deviation).
Canon critic은 hard + soft constraint, Causal critic은 보조.

Rule #14: rubric is evaluation-only, NOT a learning loss.

Discovery classification (Rule #13):
    §1 Canonical reproduction
    §2 Canon-compatible alternative
    §3 Character-consistent novel trajectory
    §4 Not-a-discovery (hardcoded / interpolation / noise)
"""

from engine.rubric.canon_critic import CanonCritic, CanonReport
from engine.rubric.causal_critic import CausalCritic, CausalReport
from engine.rubric.character_critic import CharacterCritic, CharacterReport
from engine.rubric.context_break_critic import ContextBreakCritic, ContextBreakReport
from engine.rubric.novelty_critic import NoveltyCritic, NoveltyReport
from engine.rubric.population_critic import (
    PopulationCritic,
    PopulationReport,
    world_history_to_trajectories,
)
from engine.rubric.rubric_evaluator import (
    DiscoveryClass,
    RubricEvaluator,
    RubricReport,
)
from engine.rubric.scene_response_critic import (
    SceneResponseCritic,
    SceneResponseReport,
)
from engine.rubric.world_critic import WorldCritic, WorldReport

__all__ = [
    "CharacterCritic", "CharacterReport",
    "SceneResponseCritic", "SceneResponseReport",
    "ContextBreakCritic", "ContextBreakReport",
    "CanonCritic", "CanonReport",
    "CausalCritic", "CausalReport",
    "NoveltyCritic", "NoveltyReport",
    "PopulationCritic", "PopulationReport",
    "WorldCritic", "WorldReport",
    "world_history_to_trajectories",
    "RubricEvaluator", "RubricReport",
    "DiscoveryClass",
]
