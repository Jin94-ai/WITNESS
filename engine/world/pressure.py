"""Layer C -- Derived Pressures (v3 Phase 2 v2 §2.3, Dynamics Step 2).

Dynamics Step 2 변경 (2026-04-23):
    모든 8 pressure를 곱셈(AND) 구조에서 **가중합 + clip** 구조로 전환.
    이유 (외부 LLM 공통 지적):
      - Gemini: "곱셈은 All-or-Nothing. 한 인수가 0이면 전체 0."
      - ChatGPT: "AND 구조는 실제 사회적 압력과 안 맞음. 주효과 먼저."
    가중치 합 ≈ 10 (clip(0, 10) 범위에 맞춤).

Per v2 §2.4: 옵션 C -- Pressure는 별도 저장 안 함. 매 tick 계산.
v2 §16 함정 11: "Pressure를 Active 변수로 등록 금지."

Step 2.5 특별: sacred_salience는 hope 의존성 제거.
    religious_context + recent_sacred_event (exp decay, half-life 5 tick) +
    primary_figure_presence + loyalty[primary_figure]/10 + awe/10.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from engine.person.state_v3 import ActiveState
from engine.world.primitives import PrimitiveState

PRESSURE_NAMES = [
    "social_threat", "physical_threat", "shame_exposure",
    "loyalty_pull", "uncertainty", "urgency",
    "isolation_pressure", "sacred_salience",
]


@dataclass
class PressureVector:
    """Derived pressure snapshot. Computed per-tick, not stored as Active."""

    social_threat: float = 0.0
    physical_threat: float = 0.0
    shame_exposure: float = 0.0
    loyalty_pull: float = 0.0
    uncertainty: float = 0.0
    urgency: float = 0.0
    isolation_pressure: float = 0.0
    sacred_salience: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            name: getattr(self, name) for name in PRESSURE_NAMES
        }


# =============================================================================
# Event memory (Dynamics Step 2.6)
# =============================================================================
#
# Exponential decay with half-life 5 tick. Memory stores peak intensity
# per category. When multiple events in the same category fire, take max.

_HALF_LIFE = 5.0
_DECAY = math.pow(0.5, 1.0 / _HALF_LIFE)  # ~0.871 per tick

SACRED_EVENT_IDS = frozenset({
    "sacred_meal",
    "prayer_invitation",
    "miracle_witnessed",
    "forgiveness_offered",
    "restoration_moment",
})

ACCUSATION_EVENT_IDS = frozenset({
    "public_accusation",
    "crowd_mockery",
})


@dataclass
class EventMemory:
    """Per-category event intensity memory with exponential decay."""

    sacred: float = 0.0
    accusation: float = 0.0

    def decay(self) -> None:
        self.sacred *= _DECAY
        self.accusation *= _DECAY
        if self.sacred < 1e-4:
            self.sacred = 0.0
        if self.accusation < 1e-4:
            self.accusation = 0.0

    def note_event(self, event_id: str, intensity: float = 1.0) -> None:
        """Record event by category; take max with existing."""
        if event_id in SACRED_EVENT_IDS:
            self.sacred = max(self.sacred, intensity)
        if event_id in ACCUSATION_EVENT_IDS:
            self.accusation = max(self.accusation, intensity)


# =============================================================================
# PressureLayer
# =============================================================================

def _clip(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, x))


class PressureLayer:
    """Compute PressureVector from (PrimitiveState, ActiveState).

    Rule #12: returns PressureVector only; does NOT decide actions.
    Rule #16: Pressure is Layer C (derived), not stored beyond this tick.

    Dynamics Step 2: all formulas are weighted-sum + clip.
    """

    def __init__(
        self,
        *,
        event_memory: EventMemory | None = None,
    ) -> None:
        self._mem = event_memory if event_memory is not None else EventMemory()

    # ------------------------------------------------------------------
    # Event memory passthrough (caller drives tick boundaries)
    # ------------------------------------------------------------------

    @property
    def event_memory(self) -> EventMemory:
        return self._mem

    def decay_event_memory(self) -> None:
        self._mem.decay()

    def note_event(self, event_id: str, intensity: float = 1.0) -> None:
        self._mem.note_event(event_id, intensity)

    def set_recent_accusation(self, value: float) -> None:
        """Back-compat shim for Step 1 callers. Pushes accusation intensity
        into the memory as a one-shot (without decay tick)."""
        self._mem.accusation = max(0.0, min(1.0, value))

    # ------------------------------------------------------------------
    # Core compute
    # ------------------------------------------------------------------

    def compute(
        self,
        primitives: PrimitiveState,
        person_state: ActiveState,
    ) -> PressureVector:
        p = primitives
        s = person_state
        mem = self._mem

        # --- social_threat: accusation main effect, crowd + authority ---
        social_threat = _clip(
            5.0 * p.accusation_visibility
            + 3.0 * p.crowd_density
            + 2.0 * p.authority_presence,
        )

        # --- physical_threat: roman presence + volatility ---
        physical_threat = _clip(
            6.0 * p.roman_presence
            + 4.0 * p.volatility,
        )

        # --- shame_exposure: public_visibility + prior_failure + recent_accusation ---
        shame_exposure = _clip(
            4.0 * p.public_visibility
            + 3.0 * p.prior_failure_salience
            + 3.0 * mem.accusation,
        )

        # --- loyalty_pull: presence of the bonded figure + proximity of their suffering ---
        loyalty_pull = _clip(
            5.0 * p.primary_figure_presence
            + 5.0 * p.proximity_of_suffering,
        )

        # --- uncertainty: information_gap + decision_stakes ---
        uncertainty = _clip(
            5.0 * p.information_gap
            + 5.0 * p.decision_stakes,
        )

        # --- urgency: time_pressure + decision_criticality ---
        urgency = _clip(
            5.0 * p.time_pressure
            + 5.0 * p.decision_criticality,
        )

        # --- isolation_pressure: lack of group + lack of ally ---
        isolation_pressure = _clip(
            5.0 * (1.0 - p.group_cohesion)
            + 5.0 * (1.0 - p.ally_proximity),
        )

        # --- sacred_salience (Step 2.5): hope 의존성 제거 ---
        # religious_context + recent sacred event + figure presence +
        # loyalty[primary_figure]/10 + awe/10
        loyalty_pf = s.loyalty.get("primary_figure", 0.0)
        sacred_salience = _clip(
            3.0 * p.religious_context
            + 3.0 * mem.sacred
            + 2.0 * p.primary_figure_presence
            + 1.0 * (loyalty_pf / 10.0)
            + 1.0 * (s.awe / 10.0),
        )

        return PressureVector(
            social_threat=social_threat,
            physical_threat=physical_threat,
            shame_exposure=shame_exposure,
            loyalty_pull=loyalty_pull,
            uncertainty=uncertainty,
            urgency=urgency,
            isolation_pressure=isolation_pressure,
            sacred_salience=sacred_salience,
        )
