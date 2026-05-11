"""PersonaProfile — scenario-parameterization of shared engine.

Step E (Persona Engine transition, 2026-04-23).

인물 = Shared Engine + PersonaProfile. 새 인물 추가 시 엔진 코드 수정 금지 —
profile 파라미터 + scenario binding만 생성.

모든 파라미터 기본 1.0 (baseline human). 0-2 범위.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PressureSensitivity:
    """E-1: 각 pressure가 이 사람에게 얼마나 크게 작용하는가."""
    social_threat: float = 1.0
    shame_exposure: float = 1.0
    loyalty_pull: float = 1.0
    uncertainty: float = 1.0
    urgency: float = 1.0
    isolation_pressure: float = 1.0
    sacred_salience: float = 1.0
    physical_threat: float = 1.0


@dataclass
class MotifTendency:
    """E-2: 같은 activation 조건에서 어느 motif가 쉽게 발화되는가."""
    conceal: float = 1.0
    confess: float = 1.0
    withdraw: float = 1.0
    remain_present: float = 1.0
    confront: float = 1.0
    grieve: float = 1.0
    seek_repair: float = 1.0
    observe_wait: float = 1.0

    def get(self, motif: str) -> float:
        return getattr(self, motif, 1.0)


@dataclass
class RecoveryBias:
    """E-3: 감정 회복 속도 modulator. > 1 = 빠른 회복."""
    fear_recovery_rate: float = 1.0
    guilt_decay_rate: float = 1.0
    grief_tail_strength: float = 1.0
    confusion_decay_rate: float = 1.0
    trust_restoration_bias: float = 1.0


@dataclass
class RelationBias:
    """E-4: 어느 target role에 주로 반응하는가."""
    primary_focus_attachment_strength: float = 1.0
    peer_dependence: float = 1.0
    authority_reactivity: float = 1.0
    public_exposure_sensitivity: float = 1.0


@dataclass
class PersonaProfile:
    """Full persona profile. Immutable once constructed.

    motif_action_priors: {motif_id: {action_id: prior_weight}}
        같은 motif 안에서도 인물마다 주된 action이 다름.
    """
    name: str
    description: str = ""

    pressure_sensitivity: PressureSensitivity = field(default_factory=PressureSensitivity)
    motif_tendency: MotifTendency = field(default_factory=MotifTendency)
    recovery_bias: RecoveryBias = field(default_factory=RecoveryBias)
    relation_bias: RelationBias = field(default_factory=RelationBias)

    motif_action_priors: dict[str, dict[str, float]] = field(default_factory=dict)

    # Optional scenario overrides (scene families etc.) — injected by content.
    scene_family_overrides: dict[str, list[str]] | None = None

    def validate(self) -> list[str]:
        """Return list of validation warnings (empty = OK)."""
        issues: list[str] = []
        for obj_name, obj in (
            ("pressure_sensitivity", self.pressure_sensitivity),
            ("motif_tendency", self.motif_tendency),
            ("recovery_bias", self.recovery_bias),
            ("relation_bias", self.relation_bias),
        ):
            for attr in obj.__dict__:
                v = getattr(obj, attr)
                if not (0.0 <= v <= 2.0):
                    issues.append(f"{obj_name}.{attr}={v} outside [0, 2]")
        for motif, priors in self.motif_action_priors.items():
            total = sum(priors.values())
            if abs(total - 1.0) > 0.05:
                issues.append(
                    f"motif_action_priors[{motif}] sums to {total:.3f}, not ~1.0"
                )
        return issues


# =============================================================================
# DEFAULT_PROFILE — baseline human (all 1.0)
# =============================================================================

def load_profile(path: Path | str) -> PersonaProfile:
    """Load PersonaProfile from JSON file (content/<scenario>/profile.json)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    # Strip leading-underscore comment keys
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    return PersonaProfile(
        name=data["name"],
        description=data.get("description", ""),
        pressure_sensitivity=PressureSensitivity(**data["pressure_sensitivity"]),
        motif_tendency=MotifTendency(**data["motif_tendency"]),
        recovery_bias=RecoveryBias(**data["recovery_bias"]),
        relation_bias=RelationBias(**data["relation_bias"]),
        motif_action_priors=dict(data["motif_action_priors"]),
    )


DEFAULT_PROFILE = PersonaProfile(
    name="baseline_human",
    description="Baseline generic human. All parameters 1.0. Use as starting"
                " point for new scenarios.",
    motif_action_priors={
        "conceal": {
            # deny is the defining conceal action — socially visible refusal.
            # Higher prior so motif signature transfers to action space.
            "deny": 0.50, "stay_hiding": 0.20,
            "follow_at_distance": 0.15, "withdraw_in_fear": 0.15,
        },
        "confess": {
            "confess": 0.50, "weep": 0.25, "assert_loyalty": 0.25,
        },
        "withdraw": {
            "follow_at_distance": 0.35, "stay_hiding": 0.25,
            "withdraw_in_fear": 0.25, "fall_asleep": 0.15,
        },
        "remain_present": {
            "follow_closely": 0.50, "discuss_with_disciples": 0.30,
            "stay_awake": 0.20,
        },
        "confront": {
            "draw_sword": 0.40, "assert_loyalty": 0.35, "flee": 0.25,
        },
        "grieve": {
            "weep": 0.50, "withdraw_in_fear": 0.25, "pray": 0.25,
        },
        "seek_repair": {
            "confess": 0.35, "assert_loyalty": 0.30,
            "follow_closely": 0.25, "run_to_tomb": 0.10,
        },
        "observe_wait": {
            "stay_awake": 0.40, "discuss_with_disciples": 0.40,
            "watch_quietly": 0.20,
        },
    },
)
