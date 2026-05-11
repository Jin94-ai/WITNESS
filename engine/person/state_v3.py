"""ActiveState (v3 Phase 2 v2) -- 3등급 중 Active 변수만.

Per WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md:
- §1: 3등급 분류 (Candidate / Active / Derived)
- §3: 정경 근거 Level A/B/C
- §4: 관계 변수 target-aware dict 구조
- §10 Rule #15-18

초안 (provisional) -- Active 승격은 Lee 명시 승인 필요.
모든 변수는 기본 provisional=True. Lee 승인 시 provisional=False.

Rule #1 준수: 인물-특정 이름 없음. Target은 string key로 content가 결정.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# Metadata types (v2 §1.2, §3.2, §4.2)
# =============================================================================

EvidenceLevel = Literal["A", "B", "C"]  # v2 §3.2
VariableGrade = Literal["candidate", "active", "derived"]  # v2 §1.1
VariableStructure = Literal["scalar", "target_aware"]  # v2 §4.2

FaithStage = Literal[
    "none", "follower", "tested", "failed", "restored", "shepherd", "foundation",
]


class VariableMeta(BaseModel):
    """Metadata for each declared variable. Used at registration time,
    not per-tick (so storing these in a separate registry is fine).
    """
    name: str
    grade: VariableGrade
    evidence_level: EvidenceLevel
    structure: VariableStructure
    # provisional: True = Claude 초안 / False = Lee 승인됨.
    # 기본값 False로 flip (2026-04-22 Lee 승인).
    provisional: bool = False
    scripture_references: list[str] = Field(default_factory=list)
    default_targets: list[str] = Field(default_factory=list)  # for target_aware


# =============================================================================
# ActiveState (v2 Active 등급 -- 20-30개)
# =============================================================================
#
# 초안 선정 기준 (v2 §1.2 4조건 적용 추정):
#   (1) 정경 Level A/B (대부분 A)
#   (2) 다른 Active의 단순 합/차 아님
#   (3) 행동 결정 영향
#   (4) Sensitivity: 미실측 (Phase B 후 검증)
#
# 초안이므로 모든 field에 provisional=True 의미. ActiveState instance는
# field value 만 저장. Metadata는 ACTIVE_VARIABLES_META 에 분리.


class ActiveState(BaseModel):
    """Active 변수 19개 (Dynamics Step 1: faith_stage는 Derived로 강등).

    Scalar fields: 단일 float
    Target-aware fields: dict[str, float] (string key = target id from content)

    Step 1 rationale: faith_stage(none/follower/.../foundation)는 서사 압축
    레이블, 관찰자의 사후 태그. Active에 두면 leakage 발생. Derived로 이동.
    """

    # --- Scalar person concepts (Level A, 11) ---
    fear: float = Field(0.0, ge=0.0, le=10.0, description="두려움 (A)")
    hope: float = Field(0.0, ge=0.0, le=10.0, description="소망 (A)")
    grief: float = Field(0.0, ge=0.0, le=10.0, description="슬픔 (A)")
    confusion: float = Field(0.0, ge=0.0, le=10.0, description="혼란 (A)")
    joy: float = Field(0.0, ge=0.0, le=10.0, description="기쁨 (A)")
    anger: float = Field(0.0, ge=0.0, le=10.0, description="분노 (A)")
    awe: float = Field(0.0, ge=0.0, le=10.0, description="경외 (A)")
    fatigue: float = Field(0.0, ge=0.0, le=10.0, description="피로 (A)")
    hunger: float = Field(0.0, ge=0.0, le=10.0, description="배고픔 (A)")
    vitality: float = Field(0.0, ge=0.0, le=10.0, description="활력 (A, health 재명명)")
    doubt: float = Field(0.0, ge=0.0, le=10.0, description="의심 (A)")

    # --- Target-aware relational concepts (Level A, 5) ---
    # v2 §4 required dict[target, value] structure
    love: dict[str, float] = Field(default_factory=dict, description="사랑 [target] (A)")
    loyalty: dict[str, float] = Field(default_factory=dict, description="충성 [target] (A/B)")
    trust: dict[str, float] = Field(default_factory=dict, description="신뢰 [target] (A)")
    belonging: dict[str, float] = Field(default_factory=dict, description="소속 [group] (B)")
    guilt: dict[str, float] = Field(default_factory=dict, description="죄책 [wronged_party] (B)")

    # --- Scripture-trace concepts (Level B, 2) ---
    shame: dict[str, float] = Field(default_factory=dict, description="수치 [before_whom] (B)")
    resolve: float = Field(0.0, ge=0.0, le=10.0, description="결의 (B)")

    # --- Trajectory-level state (Level B, 1) ---
    trauma: float = Field(0.0, ge=0.0, le=10.0, description="외상 (B)")

    def n_active_scalar(self) -> int:
        # fear, hope, grief, confusion, joy, anger, awe, fatigue,
        # hunger, vitality, doubt, resolve, trauma
        return 13

    def n_active_target_aware(self) -> int:
        return 6  # love, loyalty, trust, belonging, guilt, shame

    def n_active_total(self) -> int:
        # 13 scalar + 6 target_aware = 19 (faith_stage removed → Derived)
        return self.n_active_scalar() + self.n_active_target_aware()


# =============================================================================
# ACTIVE_VARIABLES_META -- registry for all Active variables
# =============================================================================
# Claude's provisional draft. Lee reviews each row, flips provisional to False.

ACTIVE_VARIABLES_META: list[VariableMeta] = [
    # Scalar emotion/state (11)
    VariableMeta(name="fear", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["마태복음 14:30 '두려워 빠져 들어가게'"]),
    VariableMeta(name="hope", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=[]),  # Content supplies scenario-specific refs
    VariableMeta(name="grief", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["마태복음 26:75 '심히 통곡'"]),
    VariableMeta(name="confusion", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["마가복음 9:6 '무엇이라 말할지 몰라'"]),
    VariableMeta(name="joy", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["누가복음 24:41 '기뻐하고 놀라워'"]),
    VariableMeta(name="anger", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["요한복음 18:10 '칼을 빼어 대제사장의 종을 쳐'"]),
    VariableMeta(name="awe", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["누가복음 5:8 '나를 떠나소서'"]),
    VariableMeta(name="fatigue", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["마태복음 26:40 '잠시도 깨어 있을 수 없더냐'"]),
    VariableMeta(name="hunger", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["누가복음 22:15 '유월절 먹기를 원하고 원하였노라'"]),
    VariableMeta(name="vitality", grade="active", evidence_level="A", structure="scalar"),
    VariableMeta(name="doubt", grade="active", evidence_level="A", structure="scalar",
                 scripture_references=["마태복음 14:31 '믿음이 적은 자여 왜 의심하였느냐'"]),
    # Target-aware relational (5) — Step D: generic role ontology
    # Content scenarios bind role → concrete instance via targets.json
    VariableMeta(name="love", grade="active", evidence_level="A",
                 structure="target_aware",
                 default_targets=["primary_focus", "peer_group", "family"],
                 scripture_references=["요한복음 21:17 '주님을 사랑하는 줄 주께서 아시나이다'"]),
    VariableMeta(name="loyalty", grade="active", evidence_level="A",
                 structure="target_aware",
                 default_targets=["primary_focus", "peer_group"],
                 scripture_references=["요한복음 13:37 '주를 위하여 내 목숨을 버리겠나이다'"]),
    VariableMeta(name="trust", grade="active", evidence_level="A",
                 structure="target_aware",
                 default_targets=["primary_focus", "peer_group"]),
    VariableMeta(name="belonging", grade="active", evidence_level="B",
                 structure="target_aware",
                 default_targets=["peer_group", "public_group"]),
    VariableMeta(name="guilt", grade="active", evidence_level="B",
                 structure="target_aware",
                 default_targets=["primary_focus", "self"],
                 scripture_references=["마태복음 26:75 '밖에 나가서 심히 통곡'"]),
    # Secondary (Level B) scalars
    VariableMeta(name="shame", grade="active", evidence_level="B",
                 structure="target_aware",
                 default_targets=["public_group", "peer_group", "self"]),
    VariableMeta(name="resolve", grade="active", evidence_level="B", structure="scalar"),
    # Trajectory (faith_stage removed Step 1 → Derived)
    VariableMeta(name="trauma", grade="active", evidence_level="B",
                 structure="scalar"),
]


def count_active() -> int:
    """Returns count of Active-grade variables currently registered."""
    return sum(1 for m in ACTIVE_VARIABLES_META if m.grade == "active")


def active_variable_names() -> list[str]:
    """Names of all Active variables."""
    return [m.name for m in ACTIVE_VARIABLES_META if m.grade == "active"]


def target_aware_names() -> list[str]:
    """Names of variables with target_aware structure."""
    return [m.name for m in ACTIVE_VARIABLES_META if m.structure == "target_aware"]
