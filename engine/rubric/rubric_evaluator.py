"""RubricEvaluator -- Phase H 4축 독립 통합 + Rule #13 분류.

**Phase H (2026-04-23, Lee 지시)** + **Phase 3.05 Rubric Design Review (2026-05-11)** flowchart:

    1. Hardcoded event firing?                      → §4.3 (NOT_DISCOVERY_HARDCODED)
    2. Hard constraint violated?                    → INVALID_CANON_VIOLATION
    3. Causal coherence below minimum gate?         → NOT_DISCOVERY_INCOHERENT  (rubric review §2.2 P0)
    4. Context-break rate ≥ threshold?              → §4.2 NOT_DISCOVERY_NOISE
    5. Scene response fit + character consistency low? → NOT_DISCOVERY_NOISE
    6. Canon exact (drift < reproduction_threshold)?   → §1 CANONICAL_REPRODUCTION
    7. Novelty=meaningful AND scene_fit=pass AND char=pass AND context coherent?
                                                    → §3 CHARACTER_CONSISTENT_NOVEL_CANDIDATE  (rubric review §2.1)
    8. else canon-compatible + scene fit OK         → §2 CANON_COMPATIBLE_CHARACTER_DRIFT  (rubric review §2.1)

Rule #24: novelty critic은 records 기반. canon_drift 재사용 금지.
Rule #22: character critic은 smoothness 금지.
Rule #13: 발견 3종 분류 유지.
Rule #14: rubric을 학습 loss로 사용 금지 (review §1.3 — neural trainer가 rubric import 0).

**Non-Claims** (review §3): 이 evaluator는 신학적/문학적 정답을 증명하지 않는다.
생성된 trajectory가 (1) canon-compatible, (2) causally explainable, (3) trait-consistent,
(4) non-copy/non-noise인지 *분류*한다. 최종 label은 **candidate class**로 해석.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.rubric.canon_critic import CanonCritic, CanonReport
from engine.rubric.causal_critic import CausalCritic, CausalReport
from engine.rubric.character_critic import CharacterCritic, CharacterReport
from engine.rubric.context_break_critic import ContextBreakCritic, ContextBreakReport
from engine.rubric.novelty_critic import NoveltyCritic, NoveltyReport
from engine.rubric.scene_response_critic import (
    SceneResponseCritic,
    SceneResponseReport,
)


class DiscoveryClass(str, Enum):
    """Phase 3.05+ rubric review (WITNESS_V3_RUBRIC_DESIGN_REVIEW.md §2.1):
    출력 label은 *truth claim*이 아니라 *candidate class*로 해석되어야 한다.
    `_CANDIDATE` suffix가 명시된 두 final 분류 (positive case)는 evaluator가
    "발견 후보"를 분류하는 것이지 "발견 확정"이 아님을 표면화한다.
    """

    # Negative/gate classes (not discovery candidates)
    INVALID = "invalid"                                          # INVALID_CANON_VIOLATION의 backwards-compat alias
    INVALID_CANON_VIOLATION = "invalid_canon_violation"          # rubric review §2.1 정식 명칭
    NOT_DISCOVERY_HARDCODED = "not_discovery_hardcoded"
    NOT_DISCOVERY_INTERPOLATION = "not_discovery_interpolation"
    NOT_DISCOVERY_INCOHERENT = "not_discovery_incoherent"        # rubric review §2.2 causal gate fail
    NOT_DISCOVERY_NOISE = "not_discovery_noise"

    # Canon-locked / reproduction
    CANONICAL_REPRODUCTION = "canonical_reproduction"

    # Discovery candidate classes (positive — but candidate not truth)
    CANON_COMPATIBLE_ALTERNATIVE = "canon_compatible_alternative"  # legacy alias
    CANON_COMPATIBLE_CHARACTER_DRIFT = "canon_compatible_character_drift"  # rubric review §2.1 정식
    CHARACTER_CONSISTENT_NOVEL = "character_consistent_novel"      # legacy alias
    CHARACTER_CONSISTENT_NOVEL_CANDIDATE = "character_consistent_novel_candidate"  # rubric review §2.1 정식


@dataclass
class RubricReport:
    character: CharacterReport
    scene_response: SceneResponseReport
    context_break: ContextBreakReport
    canon: CanonReport
    causal: CausalReport
    novelty: NoveltyReport
    discovery_class: DiscoveryClass
    justification: list[str]


class RubricEvaluator:
    """Phase H 4축 독립 통합 (character + scene + context + novelty) + canon gate.

    No composite scalar per Rule #14 / Lee §5 instruction:
    "단일 scalar 합산 금지 (4축 독립 유지)."

    The 4 main axes each vote independently; discovery_class is decided by
    the flowchart combining them.
    """

    def __init__(
        self,
        *,
        character: CharacterCritic,
        scene_response: SceneResponseCritic,
        context_break: ContextBreakCritic,
        canon: CanonCritic,
        causal: CausalCritic,
        novelty: NoveltyCritic,
        character_min_composite: float = 0.5,
        scene_fit_min: float = 0.5,
        causal_smoothness_min: float = 0.4,
    ) -> None:
        self._char = character
        self._scene = scene_response
        self._ctx = context_break
        self._canon = canon
        self._causal = causal
        self._novelty = novelty
        self._char_min = character_min_composite
        self._scene_fit_min = scene_fit_min
        # Phase 3.05 review §2.5 — causal gate (uncalibrated placeholder)
        self._causal_min = causal_smoothness_min
        # 모든 threshold가 calibration 전 placeholder임을 명시 (review §2.7)
        self.calibration_status: str = "uncalibrated_phase3_placeholder"

    def evaluate(
        self,
        records: list[dict[str, Any]],
        *,
        is_all_hardcoded: bool = False,
    ) -> RubricReport:
        justification: list[str] = []

        # Always compute all axes (independent evaluation).
        char = self._char.evaluate(records)
        scene = self._scene.evaluate(records)
        ctx = self._ctx.evaluate(records)
        canon = self._canon.evaluate(records)
        causal = self._causal.evaluate(records)
        novelty = self._novelty.evaluate(records)

        # Step 1: hardcoded
        if is_all_hardcoded:
            justification.append("Step 1: all hardcoded firings → §4.3")
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_HARDCODED,
                justification=justification,
            )

        # Step 2: hard violation
        if not canon.is_canon_valid:
            justification.append(
                f"Step 2: {len(canon.hard_violations)} hard violation(s) → INVALID_CANON_VIOLATION",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.INVALID_CANON_VIOLATION,
                justification=justification,
            )

        # Step 3: causal coherence gate (rubric review §2.2 P0)
        # 인과 설명 불가능한 trajectory는 novelty/character와 무관하게 NOT_DISCOVERY_INCOHERENT.
        # WITNESS 핵심 주장 = "상태 변화에서 결과가 나왔다" — causal coherence 미달 시 discovery 후보 자격 박탈.
        if causal.smoothness_score < self._causal_min:
            justification.append(
                f"Step 3: causal.smoothness_score={causal.smoothness_score:.3f} < "
                f"{self._causal_min} (uncalibrated, unexplained_jumps={causal.unexplained_jumps}) "
                f"→ NOT_DISCOVERY_INCOHERENT",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_INCOHERENT,
                justification=justification,
            )

        # Step 4: context-break critic — secondary noise gate under Phase H
        if not ctx.is_context_coherent:
            justification.append(
                f"Step 4: context_break.rate={ctx.break_rate:.3f} "
                f"(afford={ctx.affordance_violations}, "
                f"scene={ctx.scene_mismatch_count}, "
                f"motive={ctx.motive_gap_count}) → §4.2 NOISE",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_NOISE,
                justification=justification,
            )

        # Step 5: novelty band = noise (structured deviation too high)
        if novelty.novelty_band == "noise":
            justification.append(
                f"Step 5: novelty.structured_deviation="
                f"{novelty.structured_deviation:.3f} > noise band → §4.2 NOISE",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.NOT_DISCOVERY_NOISE,
                justification=justification,
            )

        # Step 6: canon exact reproduction
        if canon.is_canon_reproducing:
            justification.append(
                f"Step 6: soft_drift={canon.soft_drift:.2f} ≤ "
                f"reproduction_threshold → §1 CANONICAL_REPRODUCTION",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.CANONICAL_REPRODUCTION,
                justification=justification,
            )

        # Step 7: character-consistent novel candidate? (rubric review §2.1: CANDIDATE suffix)
        # Requires: novelty=meaningful + character minimum_signature pass + scene fit high
        # Phase 3.05 review §2.3 P1: composite 평균 대신 *axis별 minimum gate*가 decision source.
        # composite은 backwards compat용 fallback (passed_minimum_signature 없는 critic 호환).
        char_ok = (
            char.passed_minimum_signature
            if hasattr(char, "passed_minimum_signature")
            else char.composite >= self._char_min
        )
        scene_ok = scene.fit_rate >= self._scene_fit_min

        if novelty.novelty_band == "meaningful" and char_ok and scene_ok:
            char_detail = (
                f"passed_signature=True, weak_axes={list(char.weak_axes)}"
                if hasattr(char, "weak_axes")
                else f"composite={char.composite:.2f}≥{self._char_min}"
            )
            justification.append(
                f"Step 7: novelty=meaningful, character[{char_detail}], "
                f"scene_fit={scene.fit_rate:.2f}≥{self._scene_fit_min} "
                f"→ §3 CHARACTER_CONSISTENT_NOVEL_CANDIDATE",
            )
            return RubricReport(
                character=char, scene_response=scene, context_break=ctx,
                canon=canon, causal=causal, novelty=novelty,
                discovery_class=DiscoveryClass.CHARACTER_CONSISTENT_NOVEL_CANDIDATE,
                justification=justification,
            )

        # Step 8: canon-compatible character drift (rubric review §2.1 정식 명칭)
        # canon valid but not reproduction, character/scene threshold 미달
        char_detail = (
            f"weak_axes={list(char.weak_axes)}"
            if hasattr(char, "weak_axes") and char.weak_axes
            else f"composite={char.composite:.2f} (min {self._char_min})"
        )
        justification.append(
            f"Step 8: canon-compatible, drift={canon.soft_drift:.2f}, "
            f"novelty={novelty.novelty_band}, "
            f"character[{char_detail}], "
            f"scene_fit={scene.fit_rate:.2f} (min {self._scene_fit_min}) → §2 CANON_COMPATIBLE_CHARACTER_DRIFT",
        )
        return RubricReport(
            character=char, scene_response=scene, context_break=ctx,
            canon=canon, causal=causal, novelty=novelty,
            discovery_class=DiscoveryClass.CANON_COMPATIBLE_CHARACTER_DRIFT,
            justification=justification,
        )
