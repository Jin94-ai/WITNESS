"""SkeletonOutput contract — frozen interface between Skeleton and Flesh engines.

Per `docs/witness_narrative_mode_plan.md` §3.3:
    뼈대-살 분할이 작동하려면 인터페이스를 먼저 동결해야 한다. 이 구조가
    동결된 후에야 살 엔진(ML) 작업을 시작한다.

이 contract는 *변경 시 RFC 필수*. flesh engine은 SkeletonOutput에만 의존하고
skeleton engine 내부에 의존하지 않는다.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.observer.universal_story_seed import UniversalStorySeed

# ---------------------------------------------------------------------------
# Sub-structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvidenceLedger:
    """근거 레코드 — 모든 seed가 어떤 변화 신호에서 왔는지 기록.

    flesh engine은 *변환 후*에도 evidence_ledger의 신호를 보존해야 한다
    (Phase 5 audit). 변환이 evidence를 삭제 또는 위조하면 fail.
    """
    schema_version: str = "evidence_ledger_v1"
    total_signals: int = 0
    signals_per_seed: dict[str, int] = field(default_factory=dict)
    audit_pass_count: int = 0
    audit_fail_count: int = 0
    audit_risky_count: int = 0
    forbidden_token_violations: int = 0
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "total_signals": self.total_signals,
            "signals_per_seed": dict(self.signals_per_seed),
            "audit_pass_count": self.audit_pass_count,
            "audit_fail_count": self.audit_fail_count,
            "audit_risky_count": self.audit_risky_count,
            "forbidden_token_violations": self.forbidden_token_violations,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AuditTrail:
    """뼈대 엔진이 거친 audit 단계의 trail.

    Phase 2.5 (RFC-0001): unmapped pressure phrase / missing pressure seed /
    unknown axis count 추가. adapter가 *silent failure*를 남기지 않도록
    관측치를 모두 기록한다.
    """
    schema_version: str = "audit_trail_v1_1"
    stages_passed: tuple[str, ...] = ()
    forbidden_event_additions: int = 0
    forbidden_dialogue_generation: int = 0
    forbidden_slugline_use: int = 0
    unmapped_pressure_phrases: tuple[str, ...] = ()
    missing_pressure_seeds: tuple[str, ...] = ()
    unknown_axis_count: int = 0
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "stages_passed": list(self.stages_passed),
            "forbidden_event_additions": self.forbidden_event_additions,
            "forbidden_dialogue_generation": self.forbidden_dialogue_generation,
            "forbidden_slugline_use": self.forbidden_slugline_use,
            "unmapped_pressure_phrases": list(self.unmapped_pressure_phrases),
            "missing_pressure_seeds": list(self.missing_pressure_seeds),
            "unknown_axis_count": self.unknown_axis_count,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AnchorMetadata:
    """선택적 anchor-specific 정보 — flesh engine 또는 portfolio surface가
    universal seed를 anchor 버전으로 렌더링할 때 사용.

    None이어도 SkeletonOutput은 valid. flesh engine은 anchor 정보 없이도
    universal seed만으로 작동해야 한다.
    """
    anchor_id: str
    display_name_overrides: dict[str, str] = field(default_factory=dict)
    role_label_overrides: dict[str, str] = field(default_factory=dict)
    description_ko: str = ""

    def to_dict(self) -> dict:
        return {
            "anchor_id": self.anchor_id,
            "display_name_overrides": dict(self.display_name_overrides),
            "role_label_overrides": dict(self.role_label_overrides),
            "description_ko": self.description_ko,
        }


@dataclass(frozen=True)
class LifeStoryFlow:
    """선택적 long-form arc 정렬. Plan §3.4 — 압력 누적순 / 관계 거리 변화순 /
    시간순 / evidence-derived ordering만 허용. 장르적 재배열은 살 엔진의 일.

    Phase 2.5 (RFC-0001 §E): flow_roles 추가 — seed_id → flow_role 매핑.
    """
    schema_version: str = "life_story_flow_v1_1"
    ordering: str = "evidence_derived"          # "pressure_cumulative" /
                                                 # "time_chronological" /
                                                 # "evidence_derived" /
                                                 # "relationship_distance"
    ordered_seed_ids: tuple[str, ...] = ()
    flow_roles: dict[str, str] = field(default_factory=dict)
                                                 # 신규 (v1.1): seed_id → flow_role

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "ordering": self.ordering,
            "ordered_seed_ids": list(self.ordered_seed_ids),
            "flow_roles": dict(self.flow_roles),
        }


# ---------------------------------------------------------------------------
# SkeletonOutput — frozen contract
# ---------------------------------------------------------------------------

SKELETON_OUTPUT_VERSION = "skeleton_output_v1"


@dataclass(frozen=True)
class SkeletonOutput:
    """**FROZEN CONTRACT** between skeleton (rule-based) and flesh (ML) engines.

    Per Plan §3.3 — 변경 시 RFC 문서 작성 의무.

    Flesh engine consumes only this structure; it must never reach into
    skeleton internals.
    """
    schema_version: str = SKELETON_OUTPUT_VERSION
    seeds: tuple[UniversalStorySeed, ...] = ()
    flow: LifeStoryFlow | None = None
    evidence_ledger: EvidenceLedger = field(default_factory=EvidenceLedger)
    anchor_metadata: AnchorMetadata | None = None
    audit_trail: AuditTrail = field(default_factory=AuditTrail)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "seeds": [s.to_dict() for s in self.seeds],
            "flow": self.flow.to_dict() if self.flow else None,
            "evidence_ledger": self.evidence_ledger.to_dict(),
            "anchor_metadata":
                self.anchor_metadata.to_dict() if self.anchor_metadata else None,
            "audit_trail": self.audit_trail.to_dict(),
        }
