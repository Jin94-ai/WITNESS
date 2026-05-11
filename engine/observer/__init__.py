"""World Observer Layer — engine module.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md`:
관찰기 ≠ 평가기. Snapshot stream 위에서 다양한 lens (World/Person/Group/Event)
+ zoom + salience를 제공하는 read-only observation layer.

ABSOLUTE Rule #1: no person hardcoding.
ABSOLUTE Rule #6: existing engine API 무수정 (additive layer only).
"""

from __future__ import annotations

from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)

__all__ = [
    "AgentSnapshot",
    "GroupSnapshot",
    "Snapshot",
    "WorldSnapshot",
]
