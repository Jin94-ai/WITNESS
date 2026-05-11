"""Novelty Critic -- Axis 4 of re-designed 4-axis rubric.

Phase H.5 (2026-04-23, Lee 지시).

Rule #24: Novelty는 distance (canon_drift) 재사용 금지. Structured deviation만.

기존 (Phase G까지): novelty_drift == canon_soft_drift → 독립 축 아님.
새 설계: **structured deviation** — 차이가 의미 있는 방식인가 측정.

3 측정 축:
  (1) response_family_variation: 핵심 장면에서 family 안 vs 밖 (0 = 전부 안 = canon copy, 1 = 전부 밖)
  (2) branching_coherence: action 변화가 state 변화 또는 event로 설명 가능한가
  (3) action_diversity: 단순 복사가 아닌 독자 궤적 (entropy 기반)

structured_deviation = family_variation × (1.5 - branching_coherence), clipped [0,1]
  - canon copy: family_variation 낮음 → dev 낮음 → band=copy
  - meaningful: family_variation 중간 + branching_coherence 높음 → dev 중간 → band=meaningful
  - noise: family_variation 높음 + branching_coherence 낮음 → dev 높음 → band=noise

정식 canon_drift는 CanonCritic이 소유. 이 critic은 자체 계산.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log
from typing import Any


@dataclass
class NoveltyReport:
    response_family_variation: float  # 0-1
    branching_coherence: float        # 0-1
    action_diversity: float           # 0-1 (entropy-normalized)
    structured_deviation: float       # composite 0-1
    novelty_band: str                 # "copy" | "meaningful" | "noise"
    notes: list[str]
    # Phase 3.05 rubric review §2.4 P1 — 보강 (backwards compat: default values)
    changed_axes: tuple[str, ...] = ()        # 어느 axis가 canon에서 벗어났는지 명시
    interpretation: str = ""                  # human-readable summary
    calibration_status: str = "uncalibrated_phase3_placeholder"

    # Back-compat read-only fields (deprecated; some callers still read these)
    @property
    def is_copy(self) -> bool:
        return self.novelty_band == "copy"

    @property
    def is_noise(self) -> bool:
        return self.novelty_band == "noise"

    @property
    def copy_like(self) -> bool:
        """Phase 3.05 review §2.4 — alias for is_copy with friendlier name."""
        return self.is_copy

    @property
    def noise_like(self) -> bool:
        """Phase 3.05 review §2.4 — alias for is_noise."""
        return self.is_noise

    @property
    def structured_difference_score(self) -> float:
        """Phase 3.05 review §2.4 — friendlier alias for structured_deviation.
        review §2.4: "차이가 *의미 있는 방식*인가" — structured_difference is the metric."""
        return self.structured_deviation

    @property
    def canon_distance(self) -> float:
        """Legacy alias for structured_deviation. Rule #24 decouples this
        from canon_soft_drift."""
        return self.structured_deviation


# Scene → expected response family (mirrors scene_response_critic).
_FAMILY_MAP: dict[str, frozenset[str]] = {
    "public_accusation": frozenset({
        "deny", "withdraw_in_fear", "fall_asleep", "flee",
        "follow_at_distance", "stay_hiding",
    }),
    "eye_contact": frozenset({"weep", "withdraw_in_fear", "confess"}),
    "guard_approaches": frozenset({
        "draw_sword", "flee", "follow_at_distance", "withdraw_in_fear", "deny",
    }),
    "weapon_drawn_nearby": frozenset({
        "draw_sword", "flee", "follow_at_distance", "withdraw_in_fear",
    }),
    "primary_figure_suffering_visible": frozenset({
        "weep", "pray", "withdraw_in_fear", "follow_at_distance",
    }),
    "sacred_meal": frozenset({
        "pray", "discuss_with_disciples", "stay_awake", "follow_closely",
    }),
    "prayer_invitation": frozenset({
        "pray", "stay_awake", "follow_closely",
    }),
    "forgiveness_offered": frozenset({
        "confess", "weep", "assert_loyalty", "follow_closely",
    }),
    "restoration_moment": frozenset({
        "confess", "assert_loyalty", "follow_closely", "run_to_tomb",
    }),
    "ally_departure": frozenset({
        "withdraw_in_fear", "follow_at_distance", "stay_hiding", "follow_closely",
    }),
    "betrayal_witnessed": frozenset({
        "withdraw_in_fear", "weep", "pray", "follow_at_distance",
    }),
    "miracle_witnessed": frozenset({
        "pray", "discuss_with_disciples", "assert_loyalty", "follow_closely",
    }),
}


class NoveltyCritic:
    """Measure structured deviation — differences from canon that are
    meaningful (plausible branching) vs random (noise).

    Rule #24: This critic DOES NOT read canon_soft_drift. All features
    are computed from trajectory actions + state sequence.

    Args:
        meaningful_low:  structured_deviation < this → "copy" band
        meaningful_high: structured_deviation > this → "noise" band
        in between → "meaningful" band
    """

    def __init__(
        self,
        *,
        meaningful_low: float = 0.25,
        meaningful_high: float = 0.75,
        # Backward-compat constructor args (Phase G callers still pass these;
        # they are ignored under Rule #24 — logged in notes).
        copy_threshold: float | None = None,
        noise_threshold: float | None = None,
    ) -> None:
        self._low = meaningful_low
        self._high = meaningful_high
        self._legacy_copy = copy_threshold
        self._legacy_noise = noise_threshold

    # -----------------------------------------------------------------
    # (1) response_family_variation
    # -----------------------------------------------------------------

    def _family_variation(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """Fraction of scene-responses that are OUT of expected family.
        0 = all in family (canon copy); 1 = all out (possible noise)."""
        total = 0
        in_family = 0
        for r in records:
            events_in = r.get("event_in") or r.get("events") or []
            if isinstance(events_in, str):
                events_in = [events_in]
            for ev in events_in:
                if ev in _FAMILY_MAP:
                    action = r.get("action_id") or r.get("action")
                    total += 1
                    if action in _FAMILY_MAP[ev]:
                        in_family += 1
        if total == 0:
            return 0.5, "no recognizable scenes"
        variation = 1.0 - (in_family / total)
        return variation, f"in_family={in_family}/{total}, variation={variation:.3f}"

    # -----------------------------------------------------------------
    # (2) branching_coherence
    # -----------------------------------------------------------------

    def _branching_coherence(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """Do state changes or events explain each action change?"""
        if len(records) < 2:
            return 1.0, "trajectory too short"
        changes = 0
        explained = 0
        for i in range(len(records) - 1):
            a0 = records[i].get("action_id") or records[i].get("action")
            a1 = records[i + 1].get("action_id") or records[i + 1].get("action")
            if a0 == a1:
                continue
            changes += 1
            # Events next tick explain change
            events_in = records[i + 1].get("event_in") or records[i + 1].get("events") or []
            if isinstance(events_in, str):
                events_in = [events_in]
            if events_in:
                explained += 1
                continue
            # Else look for state delta
            s0 = records[i].get("state", {})
            s1 = records[i + 1].get("state", {})
            for key in ("fear", "grief", "confusion", "anger", "hope", "awe"):
                v0 = s0.get(key, 0.0)
                v1 = s1.get(key, 0.0)
                if (isinstance(v0, (int, float)) and isinstance(v1, (int, float))
                        and abs(float(v1) - float(v0)) >= 0.5):
                    explained += 1
                    break
        if changes == 0:
            return 1.0, "no action changes"
        coh = explained / changes
        return coh, f"explained={explained}/{changes} action changes"

    # -----------------------------------------------------------------
    # (3) action_diversity (Shannon entropy, normalized)
    # -----------------------------------------------------------------

    def _action_diversity(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        actions = [
            r.get("action_id") or r.get("action")
            for r in records
        ]
        actions = [a for a in actions if a]
        if not actions:
            return 0.0, "empty"
        counts = Counter(actions)
        n = sum(counts.values())
        entropy = -sum((c / n) * log(c / n) for c in counts.values())
        max_ent = log(min(len(counts), n)) if len(counts) > 1 else 1.0
        norm = min(1.0, entropy / max_ent) if max_ent > 0 else 0.0
        return (
            norm,
            f"entropy={entropy:.3f} norm={norm:.3f} "
            f"n_unique={len(counts)}",
        )

    # -----------------------------------------------------------------
    # Top-level
    # -----------------------------------------------------------------

    def evaluate(
        self,
        records: list[dict[str, Any]] | float,
    ) -> NoveltyReport:
        """Accept trajectory records.

        Backward-compat: if a float (canon_soft_drift) is passed, raise a
        clear error (Rule #24 explicitly forbids distance-based novelty).
        """
        if isinstance(records, (int, float)):
            raise TypeError(
                "NoveltyCritic.evaluate(float) is deprecated. "
                "Rule #24 decouples novelty from canon_drift. "
                "Pass `records: list[dict]` instead."
            )

        fv, fv_note = self._family_variation(records)
        bc, bc_note = self._branching_coherence(records)
        ad, ad_note = self._action_diversity(records)

        # structured_deviation = family_variation × (1.5 - bc); clipped [0, 1]
        # (canon copy: fv=0 → 0; noise: high fv + low bc → high dev)
        dev = max(0.0, min(1.0, fv * (1.5 - bc)))

        if dev < self._low:
            band = "copy"
        elif dev > self._high:
            band = "noise"
        else:
            band = "meaningful"

        notes = [fv_note, bc_note, ad_note,
                 f"band={band} (structured_deviation={dev:.3f})"]
        if self._legacy_copy is not None or self._legacy_noise is not None:
            notes.append(
                f"(legacy thresholds ignored per Rule #24: "
                f"copy_t={self._legacy_copy}, noise_t={self._legacy_noise})"
            )

        # Phase 3.05 review §2.4 P1: changed_axes (어느 axis가 canon에서 벗어났는지)
        # 휴리스틱: 각 axis가 평균보다 멀리 떨어졌으면 changed.
        # uncalibrated placeholder threshold (0.3-0.7 외 영역 = "변화 있음")
        changed: list[str] = []
        if fv > 0.5:
            changed.append("response_family_variation")
        if bc < 0.5:
            changed.append("branching_coherence")
        if ad > 0.6:
            changed.append("action_diversity")

        # Phase 3.05 review §2.4: human-readable interpretation
        interp_parts = {
            "copy": "정경 복사에 가까움 — meaningful difference 없음",
            "meaningful": "구조적으로 다른 trajectory — discovery 후보 가능",
            "noise": "noise 가능성 높음 — 인과 설명 약하거나 무작위 deviation",
        }
        interpretation = interp_parts.get(band, "unknown band")
        if changed:
            interpretation += f" (변화 axis: {', '.join(changed)})"

        return NoveltyReport(
            response_family_variation=fv,
            branching_coherence=bc,
            action_diversity=ad,
            structured_deviation=dev,
            novelty_band=band,
            notes=notes,
            changed_axes=tuple(changed),
            interpretation=interpretation,
        )
