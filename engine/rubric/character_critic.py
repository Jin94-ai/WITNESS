"""Character Consistency Critic — Axis 1 of re-designed 4-axis rubric.

**Phase H.1 재설계 (2026-04-23, Lee 지시).**

Rule #22: Character consistency는 smoothness가 아니다.
  - Fear oscillation / 급격한 장면 전환 자체를 impulsivity penalty로 쓰지 않음.
  - "매끈함" 금지. "Scene-appropriate response family에 속하는가"로 측정.

Lee 정의 (Phase H spec §5.1):
  character_consistency = target-aware relation 일관성
                        + 감정/의지의 장기 연속성
                        + recovery plausibility
                        + 핵심 장면 이후 성향 붕괴 없음

구체 축 3개:
  (1) relation_stability: loyalty/love/trust to primary_figure의 unexplained drop 없음
  (2) identity_retention: resolve + 핵심 관계 값이 trajectory 후반부에도 유지
  (3) recovery_plausibility: guilt/grief spike 후 repentance family 응답 있음

scene-appropriate response 측정은 별도 critic
(`engine/rubric/scene_response_critic.py`).

기존 impulsivity_score / oscillation_score는 삭제.
relationship_coherence는 scene_response_critic로 이동.

Rule #1: 이 critic은 person-agnostic. primary_figure 등 generic key만 사용.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CharacterReport:
    relation_stability: float      # 0-1
    identity_retention: float      # 0-1
    recovery_plausibility: float   # 0-1
    composite: float               # display only — decision은 passed_minimum_signature 사용 (review §2.3)
    notes: list[str]
    # Phase 3.05 rubric review §2.3 P1: minimum gate (단순 평균이 약한 축 덮는 문제 회피)
    passed_minimum_signature: bool = True   # 모든 축이 min threshold 이상이면 True
    weak_axes: tuple[str, ...] = ()         # min threshold 미만 축 명시
    calibration_status: str = "uncalibrated_phase3_placeholder"


REPENTANCE_FAMILY = frozenset({
    "weep", "confess", "pray", "withdraw_in_fear",
})


class CharacterCritic:
    """Measure trajectory's character consistency without smoothness bias.

    Phase 3.05 rubric review §2.3 P1:
        composite은 *display only* — 단순 평균은 약한 축의 신호를 덮어버린다.
        decision은 `passed_minimum_signature` (axis별 minimum gate).

    Args:
        unexplained_drop_threshold: If loyalty/love/trust to primary_figure
            drops by > this value within 1 tick without a canonical event,
            counts as instability.
        minimum_final_identity: At the end of trajectory, the max of
            loyalty[pf], love[pf], trust[pf] should be ≥ this value.
        repentance_response_window: ticks after guilt/grief spike to look
            for repentance-family action.
        relation_stability_min: minimum gate for relation_stability axis (uncalibrated).
        identity_retention_min: minimum gate for identity_retention axis (uncalibrated).
        recovery_plausibility_min: minimum gate for recovery_plausibility axis (uncalibrated).
    """

    def __init__(
        self,
        *,
        unexplained_drop_threshold: float = 2.0,
        minimum_final_identity: float = 4.0,
        repentance_response_window: int = 5,
        spike_threshold: float = 2.0,
        # Phase 3.05 review §2.3 P1: minimum gate per axis (uncalibrated placeholder)
        relation_stability_min: float = 0.5,
        identity_retention_min: float = 0.5,
        recovery_plausibility_min: float = 0.3,
    ) -> None:
        self._drop_t = unexplained_drop_threshold
        self._min_final = minimum_final_identity
        self._repent_window = repentance_response_window
        self._spike_t = spike_threshold
        # minimum gate thresholds
        self._rs_min = relation_stability_min
        self._ir_min = identity_retention_min
        self._rp_min = recovery_plausibility_min

    # -----------------------------------------------------------------
    # (1) relation_stability
    # -----------------------------------------------------------------

    def _relation_stability(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """Penalize large unexplained drops in loyalty[primary_figure] /
        love[primary_figure] / trust[primary_figure] across adjacent ticks."""
        if len(records) < 2:
            return 1.0, "trajectory too short"
        drops = 0
        windows = 0
        for i in range(len(records) - 1):
            s0 = records[i].get("state", {})
            s1 = records[i + 1].get("state", {})
            # "love" may be flattened to a scalar (max of dict); handle both.
            for key in ("loyalty_pf", "love", "trust_pf"):
                if key in s0 and key in s1:
                    v0, v1 = float(s0[key]), float(s1[key])
                    windows += 1
                    if v0 - v1 > self._drop_t:
                        # Large drop. Consider it "explained" only if a
                        # denial-like action occurred at this boundary.
                        action = records[i + 1].get("action_id")
                        if action != "deny":
                            drops += 1
            # Fallback: use "love" scalar
            if "love" in s0 and "love" in s1:
                v0, v1 = float(s0["love"]), float(s1["love"])
                windows += 1
                if v0 - v1 > self._drop_t:
                    action = records[i + 1].get("action_id")
                    if action != "deny":
                        drops += 1
        if windows == 0:
            return 1.0, "no relation keys observable"
        rate = drops / max(1, windows)
        score = max(0.0, 1.0 - rate * 3.0)  # every 1/3 drop rate → score 0
        return score, f"drops={drops}/{windows} (rate {rate:.3f})"

    # -----------------------------------------------------------------
    # (2) identity_retention
    # -----------------------------------------------------------------

    def _identity_retention(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """Did the agent retain core identity markers by the end?"""
        if not records:
            return 1.0, "empty trajectory"
        final = records[-1].get("state", {})
        # Pick the best available signal of "primary relation"
        candidates = []
        for k in ("loyalty_pf", "love", "trust_pf"):
            if k in final:
                candidates.append(float(final[k]))
        if not candidates:
            return 1.0, "no relation keys in final state"
        best = max(candidates)
        if best >= self._min_final:
            return 1.0, f"final_pf={best:.2f} ≥ {self._min_final}"
        # Linearly scale below threshold
        score = max(0.0, best / self._min_final)
        return score, f"final_pf={best:.2f} < {self._min_final}"

    # -----------------------------------------------------------------
    # (3) recovery_plausibility
    # -----------------------------------------------------------------

    def _recovery_plausibility(
        self, records: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """After a guilt or grief spike ≥ spike_threshold, check for at
        least one repentance-family action within the response window."""
        if len(records) < 2:
            return 1.0, "trajectory too short"
        # Detect spikes in guilt or grief (from state)
        def _get(state: dict, key: str) -> float:
            v = state.get(key, 0.0)
            if isinstance(v, dict):
                return max(v.values()) if v else 0.0
            return float(v)

        spikes_found = 0
        spikes_answered = 0
        for i in range(len(records) - 1):
            s0 = records[i].get("state", {})
            s1 = records[i + 1].get("state", {})
            for key in ("guilt", "grief"):
                v0 = _get(s0, key)
                v1 = _get(s1, key)
                if v1 - v0 >= self._spike_t:
                    spikes_found += 1
                    # Look for repentance in next N ticks
                    end = min(len(records), i + 1 + self._repent_window)
                    window_actions = [
                        records[j].get("action_id") for j in range(i + 1, end)
                    ]
                    if any(a in REPENTANCE_FAMILY for a in window_actions):
                        spikes_answered += 1
        if spikes_found == 0:
            return 1.0, "no guilt/grief spikes detected"
        score = spikes_answered / spikes_found
        return score, f"{spikes_answered}/{spikes_found} spikes answered"

    # -----------------------------------------------------------------
    # Top-level
    # -----------------------------------------------------------------

    def evaluate(self, records: list[dict[str, Any]]) -> CharacterReport:
        rs, rs_note = self._relation_stability(records)
        ir, ir_note = self._identity_retention(records)
        rp, rp_note = self._recovery_plausibility(records)
        composite = (rs + ir + rp) / 3.0

        # Phase 3.05 review §2.3 P1: minimum gate per axis (composite 평균이 약한 축 덮는 문제 회피)
        weak: list[str] = []
        if rs < self._rs_min:
            weak.append("relation_stability")
        if ir < self._ir_min:
            weak.append("identity_retention")
        if rp < self._rp_min:
            weak.append("recovery_plausibility")
        passed = len(weak) == 0

        return CharacterReport(
            relation_stability=rs,
            identity_retention=ir,
            recovery_plausibility=rp,
            composite=composite,
            notes=[rs_note, ir_note, rp_note],
            passed_minimum_signature=passed,
            weak_axes=tuple(weak),
        )
