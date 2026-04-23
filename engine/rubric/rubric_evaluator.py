"""RubricEvaluator -- 4축 통합 + Rule #13 분류.

Spec §6 + discovery_definitions §5 flowchart:

    1. Hardcoded event firing?        → §4.3  (not a discovery)
    2. Hard constraint violated?       → §4.x Invalid
    3. Canon exact?                    → §1 CANONICAL_REPRODUCTION
    4. Rule interpolation / noise?     → §4.1 / §4.2 (not a discovery)
    5. Canon-compatible?               → §2 CANON_COMPATIBLE_ALTERNATIVE
    6. Character-consistent?           → §3 CHARACTER_CONSISTENT_NOVEL
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.rubric.canon_critic import CanonCritic, CanonReport
from engine.rubric.causal_critic import CausalCritic, CausalReport
from engine.rubric.character_critic import CharacterCritic, CharacterReport
from engine.rubric.novelty_critic import NoveltyCritic, NoveltyReport


class DiscoveryClass(str, Enum):
    INVALID = "invalid"                              # hard constraint violation
    NOT_DISCOVERY_HARDCODED = "not_discovery_hardcoded"  # §4.3
    NOT_DISCOVERY_INTERPOLATION = "not_discovery_interpolation"  # §4.1
    NOT_DISCOVERY_NOISE = "not_discovery_noise"      # §4.2
    CANONICAL_REPRODUCTION = "canonical_reproduction"  # §1
    CANON_COMPATIBLE_ALTERNATIVE = "canon_compatible_alternative"  # §2
    CHARACTER_CONSISTENT_NOVEL = "character_consistent_novel"  # §3


@dataclass
class RubricReport:
    character: CharacterReport
    canon: CanonReport
    causal: CausalReport
    novelty: NoveltyReport
    discovery_class: DiscoveryClass
    justification: list[str]  # which flowchart steps led here


class RubricEvaluator:
    """4-critic integration + Rule #13 classification."""

    def __init__(
        self,
        *,
        character: CharacterCritic,
        canon: CanonCritic,
        causal: CausalCritic,
        novelty: NoveltyCritic,
        character_min_composite: float = 0.5,
    ) -> None:
        self._char = character
        self._canon = canon
        self._causal = causal
        self._novelty = novelty
        self._char_min = character_min_composite

    def evaluate(
        self,
        records: list[dict[str, Any]],
        *,
        is_all_hardcoded: bool = False,
    ) -> RubricReport:
        # Step 1: check if the whole trajectory is hardcoded firings
        justification: list[str] = []
        if is_all_hardcoded:
            justification.append(
                "Step 1: trajectory is 100% hardcoded event firings → §4.3",
            )
            char = self._char.evaluate(records)
            canon = self._canon.evaluate(records)
            causal = self._causal.evaluate(records)
            novelty = self._novelty.evaluate(canon.soft_drift)
            return RubricReport(
                character=char, canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_HARDCODED,
                justification=justification,
            )

        # Step 2: canon critic (hard violation?)
        canon = self._canon.evaluate(records)
        if not canon.is_canon_valid:
            justification.append(
                f"Step 2: {len(canon.hard_violations)} hard constraint "
                f"violation(s) → INVALID",
            )
            char = self._char.evaluate(records)
            causal = self._causal.evaluate(records)
            novelty = self._novelty.evaluate(canon.soft_drift)
            return RubricReport(
                character=char, canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.INVALID,
                justification=justification,
            )

        # Novelty (step-3/4 split)
        novelty = self._novelty.evaluate(canon.soft_drift)

        # Step 3: canon reproducing (drift < copy_threshold)
        if canon.is_canon_reproducing:
            justification.append(
                f"Step 3: soft_drift={canon.soft_drift:.2f} ≤ "
                "reproduction_threshold → §1 CANONICAL_REPRODUCTION",
            )
            char = self._char.evaluate(records)
            causal = self._causal.evaluate(records)
            return RubricReport(
                character=char, canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.CANONICAL_REPRODUCTION,
                justification=justification,
            )

        # Step 4: noise band?
        if novelty.is_noise:
            justification.append(
                f"Step 4: drift={canon.soft_drift:.2f} > noise_threshold → §4.2",
            )
            char = self._char.evaluate(records)
            causal = self._causal.evaluate(records)
            return RubricReport(
                character=char, canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_NOISE,
                justification=justification,
            )

        # Step 5 / 6: meaningful novelty band -- check character consistency
        char = self._char.evaluate(records)
        causal = self._causal.evaluate(records)

        if char.composite >= self._char_min:
            justification.append(
                f"Step 6: character.composite={char.composite:.2f} ≥ "
                f"{self._char_min} → §3 CHARACTER_CONSISTENT_NOVEL",
            )
            return RubricReport(
                character=char, canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.CHARACTER_CONSISTENT_NOVEL,
                justification=justification,
            )

        justification.append(
            f"Step 5: canon-compatible (drift={canon.soft_drift:.2f}) but "
            f"character.composite={char.composite:.2f} < {self._char_min} → §2",
        )
        return RubricReport(
            character=char, canon=canon, causal=causal, novelty=novelty,
            discovery_class=DiscoveryClass.CANON_COMPATIBLE_ALTERNATIVE,
            justification=justification,
        )
