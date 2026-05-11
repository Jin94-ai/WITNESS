"""Scene Response Fit Critic — Axis 2 of re-designed 4-axis rubric.

Phase H.1 (2026-04-23, Lee 지시).

Rule #22 measurement B:
    scene_response_fit = accusation → conceal/deny/confess/freeze family 에 속함
                       + eye_contact → weep/withdraw/grief 에 속함
                       + restoration → repair/confess/resolve 에 속함
                       + sacred_meal, prayer_invitation → reverent family

**Phase G 진단 교정 (Lee H.1)**: canonical이 response family에 속하면
점수 높게, smooth 한 non-response alternative는 점수 낮게.

Rule #1: scene→family mapping은 scenario-specific 하지 않은
"generic event category → action family" 형태로 유지. Scenario content가
추가 매핑을 주입할 수 있음.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SceneResponseReport:
    fit_rate: float                 # 0-1: fraction of scene-responses that fit
    n_scenes_observed: int
    per_scene_detail: list[dict]    # {tick, event_in, action, fit, family}
    notes: list[str]


# =============================================================================
# Default scene → response family mapping (generic, scenario-extensible)
# =============================================================================

DEFAULT_SCENE_RESPONSE_FAMILIES: dict[str, frozenset[str]] = {
    # Accusation scenes: social exposure demands defensive response
    "public_accusation": frozenset({
        "deny", "withdraw_in_fear", "fall_asleep", "flee",
        "follow_at_distance", "stay_hiding",
    }),
    "crowd_mockery": frozenset({
        "deny", "withdraw_in_fear", "flee", "stay_hiding",
    }),

    # Eye contact / confrontation scene: emotional turning point
    "eye_contact": frozenset({
        "weep", "withdraw_in_fear", "confess",
    }),

    # Physical threat: must-respond family
    "guard_approaches": frozenset({
        "draw_sword", "flee", "follow_at_distance", "withdraw_in_fear",
        "deny",  # denial under threat is plausible too
    }),
    "weapon_drawn_nearby": frozenset({
        "draw_sword", "flee", "follow_at_distance", "withdraw_in_fear",
    }),

    # Suffering / loss: grief-response family
    "primary_figure_suffering_visible": frozenset({
        "weep", "pray", "withdraw_in_fear", "follow_at_distance",
    }),
    "betrayal_witnessed": frozenset({
        "withdraw_in_fear", "weep", "pray", "follow_at_distance",
    }),
    "ally_departure": frozenset({
        "withdraw_in_fear", "follow_at_distance", "stay_hiding", "follow_closely",
    }),

    # Sacred / reverent scenes
    "sacred_meal": frozenset({
        "pray", "discuss_with_disciples", "stay_awake", "follow_closely",
    }),
    "prayer_invitation": frozenset({
        "pray", "stay_awake", "follow_closely",
    }),
    "miracle_witnessed": frozenset({
        "pray", "discuss_with_disciples", "assert_loyalty", "follow_closely",
    }),

    # Restoration / forgiveness: repair family
    "forgiveness_offered": frozenset({
        "confess", "weep", "assert_loyalty", "follow_closely",
    }),
    "restoration_moment": frozenset({
        "confess", "assert_loyalty", "follow_closely", "run_to_tomb",
    }),

    # Secondary-agent scenario events (generic ids)
    "covert_bargain": frozenset({
        "withdraw_in_fear", "follow_at_distance", "stay_hiding",
        "discuss_with_disciples",  # arranging logistics
    }),
    "identification_signal": frozenset({
        "assert_loyalty",  # e.g., false-loyalty signal
        "withdraw_in_fear",
    }),
    "remorse_trigger": frozenset({
        "weep", "withdraw_in_fear", "confess", "flee",
    }),
    "return_token": frozenset({
        "confess", "weep", "flee", "withdraw_in_fear",
    }),
}


class SceneResponseCritic:
    """Measure whether actions at event ticks fall within the scene-appropriate
    response family.

    Args:
        scene_families: mapping event_id → frozenset(allowed action_id)
        lookahead_ticks: how many ticks after event to consider the "response"
            (default 1 — action on same tick, since tick record already contains
            event_in + action at same tick).
        fit_threshold: if n_scenes_observed > 0, fit_rate ≥ this is a pass.
    """

    def __init__(
        self,
        *,
        scene_families: dict[str, frozenset[str]] | None = None,
        lookahead_ticks: int = 1,
        fit_threshold: float = 0.6,
    ) -> None:
        self._families = dict(scene_families or DEFAULT_SCENE_RESPONSE_FAMILIES)
        self._lookahead = lookahead_ticks
        self._fit_t = fit_threshold

    def register_family(self, event_id: str, family: frozenset[str]) -> None:
        """Allow content to extend families."""
        self._families[event_id] = family

    def evaluate(self, records: list[dict[str, Any]]) -> SceneResponseReport:
        if not records:
            return SceneResponseReport(
                fit_rate=1.0,
                n_scenes_observed=0,
                per_scene_detail=[],
                notes=["empty trajectory"],
            )

        detail: list[dict] = []
        fits = 0
        observed = 0

        for i, r in enumerate(records):
            # events_at_this_tick can come from `event_in` (list) or `events` dict
            events_in = r.get("event_in") or r.get("events") or []
            if isinstance(events_in, str):
                events_in = [events_in]
            for ev in events_in:
                family = self._families.get(ev)
                if family is None:
                    continue
                observed += 1
                # Response = action within lookahead window (this tick + next few)
                response_fit = False
                for j in range(i, min(len(records), i + self._lookahead + 1)):
                    action = records[j].get("action_id") or records[j].get("action")
                    if action in family:
                        response_fit = True
                        break
                if response_fit:
                    fits += 1
                detail.append({
                    "tick": r.get("tick"),
                    "event_in": ev,
                    "action": r.get("action_id") or r.get("action"),
                    "fit": response_fit,
                    "family_size": len(family),
                })

        if observed == 0:
            return SceneResponseReport(
                fit_rate=1.0,
                n_scenes_observed=0,
                per_scene_detail=detail,
                notes=["no recognized scenes in trajectory"],
            )
        fit_rate = fits / observed
        return SceneResponseReport(
            fit_rate=fit_rate,
            n_scenes_observed=observed,
            per_scene_detail=detail,
            notes=[
                f"scenes={observed}, fits={fits} (rate {fit_rate:.3f})",
                f"threshold pass: {fit_rate >= self._fit_t}",
            ],
        )
