"""Spike 4 — variable-intervention experiments.

Apply a deep-copied, mutated variant of WorldConfig + SimulationConfig
to an ensemble and compare the outcome distribution to a matched
control. This is the framework for "what if ~?" experiments
(WORLD_DESIGN.md §1.4).
"""

from world.intervention.batch import (
    ArmSummary,
    BatchInterventionRunner,
    ExperimentResult,
    SeedMetrics,
)
from world.intervention.engine import InterventionEngine, InterventionReport
from world.intervention.spec import InterventionSpec

__all__ = [
    "InterventionSpec",
    "InterventionEngine",
    "InterventionReport",
    "BatchInterventionRunner",
    "ExperimentResult",
    "ArmSummary",
    "SeedMetrics",
]
