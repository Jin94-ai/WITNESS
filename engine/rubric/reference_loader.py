"""Reference trajectory set loader (Phase G Step G1).

Loads the externally-generated reference set
(`data/reference/witness_trajectories_45.json`) produced by GPT for
threshold calibration.

Rule #19: Content of this file is read-only for Claude Code. Only
schema validation and structured access.

Schema (version "witness.v3.trajectory-set.0.1"):
    top-level: {schema_version, project, count, split, notes, trajectories}
    trajectory: {metadata, ticks}
      metadata: {trajectory_id, category, noise_level, length, ...}
      ticks: list of {tick, event_in, action, event_out, state}
        state: {scalar_fields..., target_aware_fields...}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

SCHEMA_VERSION = "witness.v3.trajectory-set.0.1"
# Phase H.3 relabeled version (Lee approved Rule #19 temp suspension)
SCHEMA_VERSION_V2 = "witness.v3.trajectory-set.0.2"
ACCEPTED_SCHEMA_VERSIONS = (SCHEMA_VERSION, SCHEMA_VERSION_V2)
EXPECTED_COUNT = 45
EXPECTED_LENGTH = 30

Category = Literal["canonical_like", "plausible_alternative", "obvious_noise"]

SCALAR_FIELDS: tuple[str, ...] = (
    "fear", "hope", "grief", "confusion", "joy", "anger", "awe",
    "fatigue", "hunger", "vitality", "doubt", "resolve", "trauma",
)
TARGET_AWARE_FIELDS: tuple[str, ...] = (
    "love", "loyalty", "trust", "belonging", "guilt", "shame",
)


@dataclass
class TickRecord:
    tick: int
    event_in: list[str]
    action: str
    event_out: str | None
    state: dict[str, Any]


@dataclass
class ReferenceTrajectory:
    metadata: dict[str, Any]
    ticks: list[TickRecord]

    @property
    def trajectory_id(self) -> str:
        return str(self.metadata["trajectory_id"])

    @property
    def category(self) -> str:
        return str(self.metadata["category"])

    @property
    def noise_level(self) -> int | None:
        v = self.metadata.get("noise_level")
        return int(v) if v is not None else None


@dataclass
class ReferenceSet:
    schema_version: str
    project: str
    count: int
    split: dict[str, Any]
    notes: str
    trajectories: list[ReferenceTrajectory]

    canonical_like: list[ReferenceTrajectory] = field(default_factory=list)
    plausible_alternative: list[ReferenceTrajectory] = field(default_factory=list)
    obvious_noise: list[ReferenceTrajectory] = field(default_factory=list)

    noise_level_1: list[ReferenceTrajectory] = field(default_factory=list)
    noise_level_2: list[ReferenceTrajectory] = field(default_factory=list)
    noise_level_3: list[ReferenceTrajectory] = field(default_factory=list)

    def __post_init__(self) -> None:
        for t in self.trajectories:
            if t.category == "canonical_like":
                self.canonical_like.append(t)
            elif t.category == "plausible_alternative":
                self.plausible_alternative.append(t)
            elif t.category == "obvious_noise":
                self.obvious_noise.append(t)
                if t.noise_level == 1:
                    self.noise_level_1.append(t)
                elif t.noise_level == 2:
                    self.noise_level_2.append(t)
                elif t.noise_level == 3:
                    self.noise_level_3.append(t)

    def get(self, trajectory_id: str) -> ReferenceTrajectory:
        for t in self.trajectories:
            if t.trajectory_id == trajectory_id:
                return t
        raise KeyError(trajectory_id)


# =============================================================================
# Loading + validation
# =============================================================================

class ReferenceSchemaError(ValueError):
    """Raised when reference JSON violates the declared schema."""


def _validate_state(state: dict[str, Any], traj_id: str, tick: int) -> None:
    for name in SCALAR_FIELDS:
        if name not in state:
            raise ReferenceSchemaError(
                f"{traj_id}.tick{tick}: scalar field '{name}' missing",
            )
        v = state[name]
        if not isinstance(v, (int, float)):
            raise ReferenceSchemaError(
                f"{traj_id}.tick{tick}: '{name}' not numeric (got {type(v).__name__})",
            )
        if not (0.0 <= float(v) <= 10.01):
            raise ReferenceSchemaError(
                f"{traj_id}.tick{tick}: '{name}'={v} out of [0, 10.01]",
            )
    for name in TARGET_AWARE_FIELDS:
        if name not in state:
            raise ReferenceSchemaError(
                f"{traj_id}.tick{tick}: target-aware field '{name}' missing",
            )
        d = state[name]
        if not isinstance(d, dict):
            raise ReferenceSchemaError(
                f"{traj_id}.tick{tick}: '{name}' not dict",
            )
        for k, v in d.items():
            if not isinstance(v, (int, float)):
                raise ReferenceSchemaError(
                    f"{traj_id}.tick{tick}: {name}[{k}]={v} not numeric",
                )
            if not (0.0 <= float(v) <= 10.01):
                raise ReferenceSchemaError(
                    f"{traj_id}.tick{tick}: {name}[{k}]={v} out of [0, 10.01]",
                )


def _validate_tick(raw: dict[str, Any], traj_id: str) -> TickRecord:
    required = {"tick", "event_in", "action", "event_out", "state"}
    missing = required - set(raw.keys())
    if missing:
        raise ReferenceSchemaError(
            f"{traj_id}: tick record missing keys {missing}",
        )
    tick_num = int(raw["tick"])
    event_in_raw = raw["event_in"]
    if not isinstance(event_in_raw, list):
        raise ReferenceSchemaError(
            f"{traj_id}.tick{tick_num}: event_in must be list",
        )
    _validate_state(raw["state"], traj_id, tick_num)
    return TickRecord(
        tick=tick_num,
        event_in=[str(e) for e in event_in_raw],
        action=str(raw["action"]),
        event_out=(str(raw["event_out"]) if raw["event_out"] is not None else None),
        state=raw["state"],
    )


def _validate_trajectory(raw: dict[str, Any]) -> ReferenceTrajectory:
    if "metadata" not in raw or "ticks" not in raw:
        raise ReferenceSchemaError(
            f"trajectory missing 'metadata' or 'ticks': keys={list(raw.keys())}",
        )
    meta = raw["metadata"]
    for field_name in ("trajectory_id", "category", "length"):
        if field_name not in meta:
            raise ReferenceSchemaError(
                f"metadata missing '{field_name}'",
            )
    traj_id = str(meta["trajectory_id"])
    category = str(meta["category"])
    if category not in ("canonical_like", "plausible_alternative", "obvious_noise"):
        raise ReferenceSchemaError(f"{traj_id}: unknown category '{category}'")

    length = int(meta["length"])
    if length != EXPECTED_LENGTH:
        raise ReferenceSchemaError(
            f"{traj_id}: length {length} != expected {EXPECTED_LENGTH}",
        )
    ticks_raw = raw["ticks"]
    if len(ticks_raw) != length:
        raise ReferenceSchemaError(
            f"{traj_id}: tick count {len(ticks_raw)} != declared length {length}",
        )
    ticks = [_validate_tick(t, traj_id) for t in ticks_raw]
    return ReferenceTrajectory(metadata=meta, ticks=ticks)


def load_reference_set(path: Path | str) -> ReferenceSet:
    """Load + validate the reference set file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if data.get("schema_version") not in ACCEPTED_SCHEMA_VERSIONS:
        raise ReferenceSchemaError(
            f"schema_version {data.get('schema_version')!r} not in "
            f"{ACCEPTED_SCHEMA_VERSIONS!r}",
        )
    count = int(data.get("count", -1))
    if count != EXPECTED_COUNT:
        raise ReferenceSchemaError(
            f"count {count} != expected {EXPECTED_COUNT}",
        )
    trajs_raw = data.get("trajectories", [])
    if len(trajs_raw) != count:
        raise ReferenceSchemaError(
            f"trajectories length {len(trajs_raw)} != count {count}",
        )
    trajectories = [_validate_trajectory(t) for t in trajs_raw]

    return ReferenceSet(
        schema_version=data["schema_version"],
        project=str(data.get("project", "")),
        count=count,
        split=data.get("split", {}),
        notes=str(data.get("notes", "")),
        trajectories=trajectories,
    )


# =============================================================================
# Default location
# =============================================================================

def default_path() -> Path:
    """Standard reference set location."""
    return Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "witness_trajectories_45.json"
