"""Context-Break Critic — Axis 3 of re-designed 4-axis rubric.

Phase H.2 (2026-04-23, Lee 지시).

Lee 정의 (Phase G Lee 분석 §4.2):
    context-break = affordance violation
                  + scene mismatch
                  + motive-action mismatch
                  + physical implausibility

**현재 rubric의 주 실패 원인**: `jump_into_sea`, `join_crowd` 같은 L3 noise가
drift 낮을 때 `canon_compatible_alternative`로 뜨는 문제. 이 critic이
보완.

Rule #1: affordance table은 generic scene category → action set. Scenario
content가 `scene_affordances.json`으로 override 가능.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ContextBreakReport:
    affordance_violations: int       # count of physically/scene-impossible actions
    scene_mismatch_count: int        # count of scene-inappropriate actions
    motive_gap_count: int            # count of state-action unjustified pairs
    total_actions: int
    break_rate: float                # all breaks / total
    is_context_coherent: bool        # break_rate < threshold
    notes: list[str]
    detail: list[dict]


# =============================================================================
# Default affordance table (generic, content-overridable)
# =============================================================================
#
# Format: action_id → list of required context conditions. Empty list means
# "always allowed". Conditions are predicates on state/primitives.

DEFAULT_AFFORDANCES: dict[str, list[str]] = {
    # Actions that require specific prior events / scene context
    "run_to_tomb": ["requires_recent_restoration"],
    "jump_into_sea": ["requires_boat_or_shore"],          # strict
    "stay_on_boat":  ["requires_boat_or_shore"],
    "draw_sword":    ["requires_active_threat"],
    "accept_washing": ["requires_sacred_meal_context"],
    "resist_washing": ["requires_sacred_meal_context"],
    "deny":          ["requires_accusation_within_2"],
    "confess":       ["requires_high_guilt_or_forgiveness"],
    "join_crowd":    ["requires_crowd_nearby"],

    # Generic actions have no affordance precondition
    "follow_closely": [],
    "follow_at_distance": [],
    "withdraw_in_fear": [],
    "stay_hiding": [],
    "fall_asleep": [],
    "flee": [],
    "stay_awake": [],
    "pray": [],
    "weep": [],
    "discuss_with_disciples": [],
    "assert_loyalty": [],
    "watch_quietly": [],
}


# Scene category → expected motive (state feature) profile. Rough lookup used
# to detect motive gaps. Each entry is a rule of the form:
#     (action, require_state_condition_description)
# The condition is checked against (state, primitives) via simple predicates.

MOTIVE_REQUIREMENTS: dict[str, dict[str, tuple[float, str]]] = {
    # Each inner dict: state_field → (min_value, direction)
    "flee":             {"fear": (3.0, ">=")},
    "deny":             {"fear": (2.0, ">=")},
    "withdraw_in_fear": {"fear": (2.0, ">=")},
    "weep":             {"grief_or_guilt": (2.0, ">=")},  # special
    "confess":          {"guilt_or_forgiveness": (3.0, ">=")},  # special
    "draw_sword":       {"anger": (2.0, ">="), "fear_ratio": (0.7, ">=")},
    "assert_loyalty":   {"loyalty_pf_or_love": (5.0, ">=")},
}


# =============================================================================
# Critic
# =============================================================================

class ContextBreakCritic:
    """Detect actions that break scene affordance / motive / physical context.

    A break is: (1) action tries to happen with missing precondition,
    (2) action contradicts the scene category at the tick, or (3) the state
    vector doesn't justify the action.
    """

    def __init__(
        self,
        *,
        affordances: dict[str, list[str]] | None = None,
        motive_requirements: dict[str, dict[str, tuple[float, str]]] | None = None,
        break_threshold: float = 0.15,
    ) -> None:
        self._afford = dict(affordances or DEFAULT_AFFORDANCES)
        self._motive = dict(motive_requirements or MOTIVE_REQUIREMENTS)
        self._break_t = break_threshold

    # -----------------------------------------------------------------
    # Affordance checks (context preconditions)
    # -----------------------------------------------------------------

    def _check_affordance(
        self, tick_idx: int, records: list[dict], action: str,
    ) -> tuple[bool, str]:
        """True if affordance satisfied; string = explanation if violated."""
        preconditions = self._afford.get(action, [])
        if not preconditions:
            return True, ""

        for pre in preconditions:
            if pre == "requires_recent_restoration":
                # Look back for restoration_moment / forgiveness_offered / miracle
                ok = self._event_within(records, tick_idx, {
                    "restoration_moment", "forgiveness_offered", "miracle_witnessed",
                }, within=3)
                if not ok:
                    return False, "no recent restoration within 3 ticks"
            elif pre == "requires_boat_or_shore":
                # Context-dependent (e.g., post-restoration scenes): this
                # action only fires within 5 ticks of restoration/miracle events.
                ok = self._event_within(records, tick_idx, {
                    "restoration_moment", "miracle_witnessed",
                }, within=5)
                if not ok:
                    return False, "jump/boat action outside shore/boat context"
            elif pre == "requires_active_threat":
                ok = self._event_within(records, tick_idx, {
                    "guard_approaches", "weapon_drawn_nearby", "arrest_warrant",
                }, within=2)
                if not ok:
                    return False, "no active threat within 2 ticks"
            elif pre == "requires_accusation_within_2":
                ok = self._event_within(records, tick_idx, {
                    "public_accusation", "crowd_mockery",
                }, within=2)
                if not ok:
                    return False, "no accusation within 2 ticks"
            elif pre == "requires_sacred_meal_context":
                ok = self._event_within(records, tick_idx, {
                    "sacred_meal",
                }, within=3)
                if not ok:
                    return False, "no sacred_meal within 3 ticks"
            elif pre == "requires_high_guilt_or_forgiveness":
                state = records[tick_idx].get("state", {})
                guilt = state.get("guilt", 0)
                if isinstance(guilt, dict):
                    guilt = max(guilt.values()) if guilt else 0
                forgiven = self._event_within(records, tick_idx, {
                    "forgiveness_offered", "restoration_moment",
                }, within=3)
                if float(guilt) < 3.0 and not forgiven:
                    return False, "confess with low guilt AND no forgiveness context"
            elif pre == "requires_crowd_nearby":
                state = records[tick_idx].get("state", {})
                primitives = records[tick_idx].get("primitives", {})
                # No primitives available in reference records; use a permissive default.
                if primitives:
                    crowd = primitives.get("crowd_density", 0)
                    if float(crowd) < 0.2:
                        return False, "join_crowd with crowd_density < 0.2"
                # Without primitives, check events: if accusation or gathering event, OK
                ok = self._event_within(records, tick_idx, {
                    "public_accusation", "crowd_mockery", "sacred_meal",
                    "betrayal_witnessed",
                }, within=2) or tick_idx <= 5  # early passion pilgrim context
                if not ok:
                    return False, "no crowd context found"
        return True, ""

    @staticmethod
    def _event_within(
        records: list[dict], tick_idx: int, event_set: set[str], within: int,
    ) -> bool:
        """Return True if any event in event_set fired within `within` ticks
        before (or at) tick_idx."""
        lo = max(0, tick_idx - within)
        for i in range(lo, tick_idx + 1):
            ev = records[i].get("event_in") or records[i].get("events") or []
            if isinstance(ev, str):
                ev = [ev]
            if any(e in event_set for e in ev):
                return True
        return False

    # -----------------------------------------------------------------
    # Motive checks (state justifies action?)
    # -----------------------------------------------------------------

    def _check_motive(
        self, record: dict, action: str,
    ) -> tuple[bool, str]:
        reqs = self._motive.get(action)
        if not reqs:
            return True, ""
        state = record.get("state", {})
        for field_name, (threshold, direction) in reqs.items():
            # Special aliases
            if field_name == "grief_or_guilt":
                grief = float(state.get("grief", 0))
                guilt = state.get("guilt", 0)
                if isinstance(guilt, dict):
                    guilt = max(guilt.values()) if guilt else 0
                val = max(grief, float(guilt))
            elif field_name == "guilt_or_forgiveness":
                guilt = state.get("guilt", 0)
                if isinstance(guilt, dict):
                    guilt = max(guilt.values()) if guilt else 0
                val = float(guilt)
            elif field_name == "fear_ratio":
                fear = float(state.get("fear", 0))
                anger = float(state.get("anger", 1e-6))
                val = anger / max(0.01, fear + anger)
            elif field_name == "loyalty_pf_or_love":
                val_l = float(state.get("loyalty_pf", 0))
                val_o = state.get("love", 0)
                if isinstance(val_o, dict):
                    val_o = max(val_o.values()) if val_o else 0
                val = max(val_l, float(val_o))
            else:
                val = float(state.get(field_name, 0))

            if direction == ">=" and val < threshold:
                return False, f"{action} but {field_name}={val:.2f} < {threshold}"
        return True, ""

    # -----------------------------------------------------------------
    # Scene mismatch (strong conflict between scene and action)
    # -----------------------------------------------------------------

    _STRONG_SCENE_CONFLICTS: list[tuple[str, set[str]]] = [
        # (event, actions that directly contradict scene) --
        # these trigger scene_mismatch count.
        ("public_accusation", {
            "discuss_with_disciples", "assert_loyalty",  # openly defying accusation
            "jump_into_sea",          # unrelated
            "stay_on_boat",           # unrelated
            "run_to_tomb",            # out of order
            "accept_washing",         # sacred meal action
            "pray",                   # not response to social pressure
        }),
        ("eye_contact", {
            "assert_loyalty",         # after being exposed, false loyalty
            "jump_into_sea",
            "stay_on_boat",
            "join_crowd",
            "run_to_tomb",
            "discuss_with_disciples",
        }),
        ("restoration_moment", {
            "deny",                   # contradicts restoration
            "jump_into_sea",          # not the turning point
            "stay_hiding",            # avoiding restoration
            "flee",
        }),
        ("guard_approaches", {
            "jump_into_sea",
            "stay_on_boat",
            "run_to_tomb",
            "accept_washing",
            "confess",                # wrong moment
        }),
    ]

    def _check_scene_mismatch(
        self, tick_idx: int, records: list[dict], action: str,
    ) -> tuple[bool, str]:
        events_in = records[tick_idx].get("event_in") or []
        if isinstance(events_in, str):
            events_in = [events_in]
        for ev in events_in:
            for scene, conflicts in self._STRONG_SCENE_CONFLICTS:
                if ev == scene and action in conflicts:
                    return False, f"{action} directly contradicts scene '{ev}'"
        return True, ""

    # -----------------------------------------------------------------
    # Top-level
    # -----------------------------------------------------------------

    def evaluate(self, records: list[dict[str, Any]]) -> ContextBreakReport:
        afford_breaks = 0
        scene_breaks = 0
        motive_breaks = 0
        detail: list[dict] = []

        for i, rec in enumerate(records):
            action = rec.get("action_id") or rec.get("action")
            if not action:
                continue
            entry = {"tick": rec.get("tick", i), "action": action,
                     "violations": []}

            ok, reason = self._check_affordance(i, records, action)
            if not ok:
                afford_breaks += 1
                entry["violations"].append({"type": "affordance", "reason": reason})

            ok, reason = self._check_scene_mismatch(i, records, action)
            if not ok:
                scene_breaks += 1
                entry["violations"].append({"type": "scene_mismatch", "reason": reason})

            ok, reason = self._check_motive(rec, action)
            if not ok:
                motive_breaks += 1
                entry["violations"].append({"type": "motive_gap", "reason": reason})

            if entry["violations"]:
                detail.append(entry)

        total = len(records)
        total_breaks = afford_breaks + scene_breaks + motive_breaks
        rate = total_breaks / max(1, total)
        coherent = rate < self._break_t

        return ContextBreakReport(
            affordance_violations=afford_breaks,
            scene_mismatch_count=scene_breaks,
            motive_gap_count=motive_breaks,
            total_actions=total,
            break_rate=rate,
            is_context_coherent=coherent,
            notes=[
                f"afford={afford_breaks}, scene={scene_breaks}, "
                f"motive={motive_breaks}",
                f"break_rate={rate:.3f} "
                f"({'coherent' if coherent else 'broken'})",
            ],
            detail=detail,
        )
