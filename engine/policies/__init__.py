"""Policy adapters for behavior selection.

Spike 6 Stage 2 introduces an optional neural policy plug-point that the
existing ``decide_action`` can consult instead of rule-based weights.
Everything here is **person-agnostic** — agent-specific artifacts (trained
weights, feature config) live under ``content/<agent>/trained/``.

ABSOLUTE RULE #1 compliance: no file in ``engine/`` references a specific
person. Policy classes take feature vectors and action-id lists and return
weights — nothing else.
"""

from engine.policies.protocol import DecisionPolicy

__all__ = ["DecisionPolicy"]
