"""World Observer — snapshot Pydantic schemas.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §3.

각 tick의 세계 상태를 *light view*로 기록. engine state schema의 subset.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WorldSnapshot(BaseModel):
    """World-level state at one tick.

    All quantitative fields are 0.0-1.0 (normalized intensity).
    crowd_mood는 categorical tag.
    """

    crowd_mood: Literal["calm", "tense", "agitated", "fragmenting"] = Field(
        default="calm",
        description="군중 분위기 categorical (calm < tense < agitated < fragmenting)",
    )
    blame_concentration: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="비난이 한 대상에 집중된 정도",
    )
    public_suspicion: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="공적 의심 누적도",
    )
    authority_vigilance: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="권위의 경계 강도",
    )
    scarcity_pressure: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="자원 부족 압력",
    )


class GroupSnapshot(BaseModel):
    """Cohort/location/role-based group state at one tick."""

    id: str = Field(description="Group ID (location ID, role tag, cohort id 등)")
    dominant_mode: Literal[
        "saturation", "recovery", "mixed", "low_activity", "partial"
    ] = Field(
        default="low_activity",
        description="이 group의 dominant outcome mode",
    )
    tension: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="group-level 긴장도",
    )
    member_count: int = Field(
        default=0, ge=0,
        description="이 group에 속한 agent 수",
    )


class AgentSnapshot(BaseModel):
    """One agent's state at one tick — light view.

    engine.core.state.AgentState의 *subset*. observer가 보기 좋은 형태.

    delta는 직전 tick 대비 주요 변화 tags. 예: ["fear_up", "shame_self_down"].
    """

    id: str = Field(description="Agent ID")
    role: str = Field(
        default="generic",
        description="Generic role tag — 'follower', 'crowd', 'authority' 등 (no person name)",
    )
    fear: float = Field(default=0.0, ge=0.0, le=10.0)
    hope: float = Field(default=5.0, ge=0.0, le=10.0)
    shame_self: float = Field(default=0.0, ge=0.0, le=10.0)
    delta: list[str] = Field(
        default_factory=list,
        description="직전 tick 대비 주요 변화 tags (e.g. 'fear_up')",
    )


class Snapshot(BaseModel):
    """One tick's complete observation — observer 입력 단위.

    Lee directive §5.1 schema.
    """

    tick: int = Field(ge=0, description="Simulation tick")
    active_events: list[str] = Field(
        default_factory=list,
        description="이 tick에 활성 이벤트 ID 목록",
    )
    world: WorldSnapshot = Field(
        default_factory=WorldSnapshot,
        description="World-level state",
    )
    groups: list[GroupSnapshot] = Field(
        default_factory=list,
        description="Group-level snapshots",
    )
    agents: list[AgentSnapshot] = Field(
        default_factory=list,
        description="Agent-level snapshots",
    )
    salience_hints: list[str] = Field(
        default_factory=list,
        description="이 tick에서 감지된 salience tags (e.g. 'accusation_spike')",
    )

    def get_agent(self, agent_id: str) -> AgentSnapshot | None:
        """Lookup agent by ID."""
        for a in self.agents:
            if a.id == agent_id:
                return a
        return None

    def get_group(self, group_id: str) -> GroupSnapshot | None:
        """Lookup group by ID."""
        for g in self.groups:
            if g.id == group_id:
                return g
        return None
