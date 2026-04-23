"""Witness v3.0 person state -- 3-grade concept variables (v2 spec).

Per WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §1:
    - Candidate: extracted from scripture but not active (50-60)
    - Active:    live simulation state (20-30)
    - Derived:   computed from Active (not stored)

Rule #1 compliance: all field names generic. Scenario mapping in content/.
"""

from engine.person.state_candidates import CandidateRegistry, CandidateVariable
from engine.person.state_derived import DerivedCalculator
from engine.person.state_v3 import (
    ActiveState,
    EvidenceLevel,
    FaithStage,
    VariableGrade,
)

__all__ = [
    "ActiveState", "FaithStage",
    "EvidenceLevel", "VariableGrade",
    "CandidateRegistry", "CandidateVariable",
    "DerivedCalculator",
]
