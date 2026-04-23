"""Layer A -- World Primitives (v3 Phase 2 v2 §2.2).

지속 상태 (persistent environment values). 시뮬레이션 외부에서 주어지며,
Event(Layer B)에 의해 갱신될 수 있다.

v2 §2.2 예시:
    crowd_density, roman_presence, authority_presence, group_cohesion,
    time_of_day, location, group_presence, ...

Rule #1 준수: 필드명 generic. Scenario-specific values (e.g., '예루살렘 성전')
는 content에서 지정.

Rule #16 준수: 이 layer는 **Primitive만**. Event나 Pressure 섞지 않음.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TimeOfDay = Literal["dawn", "morning", "noon", "afternoon", "evening", "night"]


@dataclass
class WorldPrimitive:
    """Single primitive declaration (for registry)."""
    name: str
    description: str
    dtype: str  # "float" | "int" | "str" | "bool"
    range: tuple[float, float] | None = None  # for numeric


# =============================================================================
# PrimitiveState -- the actual runtime Layer A state
# =============================================================================

@dataclass
class PrimitiveState:
    """Layer A 현재 상태.

    v2 §2.2 초안 18개 primitives. Scenario content가 초기값 설정 + tick별 update.
    """

    # --- Spatial ---
    location: str = "unknown"            # e.g., "temple_courtyard"
    time_of_day: TimeOfDay = "noon"

    # --- Crowd / social ---
    crowd_density: float = 0.0           # 0-1
    ally_proximity: float = 0.0          # 0-1, 동료 근접도
    group_cohesion: float = 0.5          # 0-1, 집단 결속도

    # --- Authority presence ---
    authority_presence: float = 0.0      # 0-1, 종교/정치 권위자 거리
    roman_presence: float = 0.0          # 0-1, 로마 군인 존재
    religious_context: float = 0.0       # 0-1, 종교 의식 맥락 (성전/회당)

    # --- Figure presence ---
    primary_figure_presence: float = 0.0   # 0-1, 주된 결속 대상 존재
    primary_figure_visible: bool = False   # 시야 가능 여부

    # --- Information ---
    information_gap: float = 0.5         # 0-1, 정보 공백
    decision_stakes: float = 0.0         # 0-1, 결정의 중대성

    # --- Temporal context ---
    public_visibility: float = 0.0       # 0-1, 공개 노출도
    time_pressure: float = 0.0           # 0-1, 시간 압박

    # --- Memory aids (externalised) ---
    prior_failure_salience: float = 0.0  # 0-1, 과거 실패의 현재 활성도
    accusation_visibility: float = 0.0   # 0-1, 고발/비난의 가시성
    volatility: float = 0.0              # 0-1, 상황 변동성

    # --- State modifiers (can be updated by events) ---
    decision_criticality: float = 0.0    # 0-1
    proximity_of_suffering: float = 0.0  # 0-1, 고난의 근접도

    # ------------------------------------------------------------------
    # Transient primitive decay (D4 fix)
    # ------------------------------------------------------------------
    # Some primitives represent short-lived world state (threat signals,
    # accusation visibility, etc). Without explicit refresh from events,
    # they should relax toward baseline. Persistent primitives
    # (location, group_cohesion, religious_context, ...) do NOT decay.

    def decay_transients(self) -> None:
        """Apply small per-tick decay to transient threat/event signals.
        Called once per tick AFTER event-apply + BEFORE pressure compute."""
        rate = 0.08  # ~half-life 8 tick
        for name in (
            "accusation_visibility",
            "volatility",
            "time_pressure",
            "decision_criticality",
            "proximity_of_suffering",
            "public_visibility",
        ):
            cur = getattr(self, name)
            if cur > 0.0:
                setattr(self, name, max(0.0, cur - rate))


# =============================================================================
# Registry (for documentation + tests)
# =============================================================================

PRIMITIVE_REGISTRY: list[WorldPrimitive] = [
    WorldPrimitive("location", "현재 장소 식별자", "str"),
    WorldPrimitive("time_of_day", "하루 중 시간대 (6단계)", "str"),
    WorldPrimitive("crowd_density", "군중 밀도", "float", (0.0, 1.0)),
    WorldPrimitive("ally_proximity", "동료 근접도", "float", (0.0, 1.0)),
    WorldPrimitive("group_cohesion", "집단 결속도", "float", (0.0, 1.0)),
    WorldPrimitive("authority_presence", "권위자 거리", "float", (0.0, 1.0)),
    WorldPrimitive("roman_presence", "로마 군인 존재", "float", (0.0, 1.0)),
    WorldPrimitive("religious_context", "종교 의식 맥락", "float", (0.0, 1.0)),
    WorldPrimitive("primary_figure_presence", "주된 결속 대상 존재", "float", (0.0, 1.0)),
    WorldPrimitive("primary_figure_visible", "결속 대상 시야", "bool"),
    WorldPrimitive("information_gap", "정보 공백", "float", (0.0, 1.0)),
    WorldPrimitive("decision_stakes", "결정 중대성", "float", (0.0, 1.0)),
    WorldPrimitive("public_visibility", "공개 노출도", "float", (0.0, 1.0)),
    WorldPrimitive("time_pressure", "시간 압박", "float", (0.0, 1.0)),
    WorldPrimitive("prior_failure_salience", "과거 실패 활성도", "float", (0.0, 1.0)),
    WorldPrimitive("accusation_visibility", "고발 가시성", "float", (0.0, 1.0)),
    WorldPrimitive("volatility", "상황 변동성", "float", (0.0, 1.0)),
    WorldPrimitive("decision_criticality", "결정 임박도", "float", (0.0, 1.0)),
    WorldPrimitive("proximity_of_suffering", "고난 근접도", "float", (0.0, 1.0)),
]


def n_primitives() -> int:
    return len(PRIMITIVE_REGISTRY)
