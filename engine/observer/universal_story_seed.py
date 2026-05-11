"""UniversalStorySeed — anchor-agnostic story seed.

Per `docs/witness_narrative_mode_plan.md` Phase 0:
    뼈대 엔진은 universal seed만 출력한다. anchor-specific 표현
    (인물 이름 / 시대 배경 등)은 별도 AnchorRegistry가 보관한다.

이 모듈은 *뼈대 엔진의 출력 unit*을 정의한다:
    - 인물 이름 / 정경 사건 / 시대 배경 같은 anchor-specific 정보 없음
    - 보편 conflict axis / pressure / desire taxonomy로만 표현
    - audit / evidence ledger와 호환

기존 anchor-bound seed (인물명, 정경 ref 포함)에서 anchor-clean 버전을
별도 모듈(universal_seed_adapter)이 추출한다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Taxonomy loaders
# ---------------------------------------------------------------------------

_TAXONOMY_ROOT = Path(__file__).resolve().parents[2] / "content" / "universal"


def load_pressure_taxonomy() -> dict[str, dict[str, Any]]:
    p = _TAXONOMY_ROOT / "pressure_taxonomy.json"
    return json.loads(p.read_text(encoding="utf-8"))["pressures"]


def load_desire_taxonomy() -> dict[str, dict[str, Any]]:
    p = _TAXONOMY_ROOT / "desire_taxonomy.json"
    return json.loads(p.read_text(encoding="utf-8"))["desires"]


def load_conflict_axes() -> dict[str, dict[str, Any]]:
    p = _TAXONOMY_ROOT / "conflict_axes.json"
    return json.loads(p.read_text(encoding="utf-8"))["axes"]


# ---------------------------------------------------------------------------
# Universal seed dataclass
# ---------------------------------------------------------------------------

UNIVERSAL_STORY_SEED_VERSION = "universal_story_seed_v1_1"


@dataclass(frozen=True)
class UniversalStorySeed:
    """Anchor-agnostic story seed (v1.1, RFC-0001).

    No character names, no scripture refs, no historical events. Pure
    conflict-axis + pressure/desire pattern + agent-role abstraction.

    v1 → v1.1 (Phase 2.5):
        - main_role / main_archetype 책임 분리
        - supporting_archetypes 신규
        - change_pattern / arc_direction / relationship_function / flow_role 신규
        - turning_points_count를 top-level로 승격
    """
    seed_id: str                              # e.g. "S01"
    conflict_axis_id: str                     # key into conflict_axes.json
    main_role: str                            # 서사 기능 (protagonist 등)
    main_archetype: str = ""                  # 인물 유형 (loyal_under_pressure 등)
    dominant_pressures: tuple[str, ...] = ()  # pressure_taxonomy ids
    dominant_desires: tuple[str, ...] = ()    # desire_taxonomy ids
    supporting_archetypes: tuple[str, ...] = ()  # 신규 (v1.1)
    supporting_roles: tuple[str, ...] = ()    # universal role labels
    pressure_pattern: dict[str, Any] = field(default_factory=dict)
                                              # deprecated v1 호환용. 신규 필드는
                                              # change_pattern / turning_points_count
                                              # / flow_role 등 top-level 사용.
    change_pattern: str = ""                  # 신규 (v1.1): stay_present_then_withdraw 등
    arc_direction: str = ""                   # 신규 (v1.1): visibility_to_silence 등
    relationship_function: str = ""           # 신규 (v1.1): contrast_to_main 등
    flow_role: str = ""                       # 신규 (v1.1): main_arc / witness_arc 등
    turning_points_count: int = 0             # 신규 (v1.1)
    confidence_label: str = ""                # "strong_viable" / "viable_with_gaps"
    audit_status: str = "pass"                # "pass" / "risky" / "audit_fail"
    evidence_count: int = 0                   # raw count (data-cited only)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": UNIVERSAL_STORY_SEED_VERSION,
            "seed_id": self.seed_id,
            "conflict_axis_id": self.conflict_axis_id,
            "main_role": self.main_role,
            "main_archetype": self.main_archetype,
            "dominant_pressures": list(self.dominant_pressures),
            "dominant_desires": list(self.dominant_desires),
            "supporting_archetypes": list(self.supporting_archetypes),
            "supporting_roles": list(self.supporting_roles),
            "pressure_pattern": dict(self.pressure_pattern),
            "change_pattern": self.change_pattern,
            "arc_direction": self.arc_direction,
            "relationship_function": self.relationship_function,
            "flow_role": self.flow_role,
            "turning_points_count": self.turning_points_count,
            "confidence_label": self.confidence_label,
            "audit_status": self.audit_status,
            "evidence_count": self.evidence_count,
            "notes": list(self.notes),
        }

    @staticmethod
    def from_dict(d: dict) -> "UniversalStorySeed":
        return UniversalStorySeed(
            seed_id=d["seed_id"],
            conflict_axis_id=d["conflict_axis_id"],
            main_role=d.get("main_role", ""),
            main_archetype=d.get("main_archetype", ""),
            dominant_pressures=tuple(d.get("dominant_pressures", [])),
            dominant_desires=tuple(d.get("dominant_desires", [])),
            supporting_archetypes=tuple(d.get("supporting_archetypes", [])),
            supporting_roles=tuple(d.get("supporting_roles", [])),
            pressure_pattern=dict(d.get("pressure_pattern", {})),
            change_pattern=d.get("change_pattern", ""),
            arc_direction=d.get("arc_direction", ""),
            relationship_function=d.get("relationship_function", ""),
            flow_role=d.get("flow_role", ""),
            turning_points_count=int(d.get("turning_points_count", 0)),
            confidence_label=d.get("confidence_label", ""),
            audit_status=d.get("audit_status", "pass"),
            evidence_count=int(d.get("evidence_count", 0)),
            notes=tuple(d.get("notes", [])),
        )
