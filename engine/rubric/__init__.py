"""4-axis Discovery Rubric (v3.0 Phase 4).

Spec §6.2 verbatim:
    Axis 1: Character Consistency
    Axis 2: Canon Compatibility
    Axis 3: Causal Coherence
    Axis 4: Novelty under Constraint

Rule #14: rubric is evaluation-only, NOT a learning loss.

Discovery classification (Rule #13) uses these 4 axes to label a trajectory
as §1 Canonical reproduction / §2 Canon-compatible alternative /
§3 Character-consistent novel trajectory / §4 Not-a-discovery.
"""

from engine.rubric.canon_critic import CanonCritic, CanonReport
from engine.rubric.causal_critic import CausalCritic, CausalReport
from engine.rubric.character_critic import CharacterCritic, CharacterReport
from engine.rubric.novelty_critic import NoveltyCritic, NoveltyReport
from engine.rubric.rubric_evaluator import (
    DiscoveryClass,
    RubricEvaluator,
    RubricReport,
)

__all__ = [
    "CharacterCritic", "CharacterReport",
    "CanonCritic", "CanonReport",
    "CausalCritic", "CausalReport",
    "NoveltyCritic", "NoveltyReport",
    "RubricEvaluator", "RubricReport",
    "DiscoveryClass",
]
