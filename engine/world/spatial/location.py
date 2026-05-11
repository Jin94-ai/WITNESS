"""Location dataclass + affordance spec (SPACE_AS_AFFORDANCE.md)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

LocationTag = Literal[
    "public", "private", "outdoor", "indoor",
    "sacred", "commercial", "authority", "liminal",
    "water", "wilderness",
]


@dataclass
class Location:
    """Single location with affordance set."""
    location_id: str
    name: str = ""   # content binding (generic engine에는 ID만)
    tags: list[LocationTag] = field(default_factory=list)

    # Affordances (0-1)
    visibility: float = 0.5            # 누구나 볼 수 있는가
    concealment: float = 0.5           # 숨을 수 있는가
    crowdability: float = 0.3          # 사람 모일 수 있는가
    authority_reach: float = 0.3       # 권력이 손쓸 수 있는가
    sacred_proximity: float = 0.0      # 신성 공간 근접도

    # Connections
    escape_routes: list[str] = field(default_factory=list)  # adjacent location ids
    reachability: dict[str, float] = field(default_factory=dict)  # role → access score

    # Resource / info
    info_access_level: str = "public"  # "public" | "restricted" | "secret"
    resource_availability: dict[str, float] = field(default_factory=dict)

    # Dynamic
    agents_present: set[str] = field(default_factory=set)
    max_capacity: int = 1000

    def has_tag(self, tag: LocationTag) -> bool:
        return tag in self.tags

    def is_reachable_by_role(self, role_id: str) -> float:
        """Role access score (0-1). Default 1.0 (accessible) if not specified."""
        return self.reachability.get(role_id, 1.0)

    def affordance_summary(self) -> dict[str, float]:
        return {
            "visibility": self.visibility,
            "concealment": self.concealment,
            "crowdability": self.crowdability,
            "authority_reach": self.authority_reach,
            "sacred_proximity": self.sacred_proximity,
            "escape_routes_count": float(len(self.escape_routes)),
        }
