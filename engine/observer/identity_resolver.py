"""Agent / Group / Pressure identity resolution — Stage 5.1-5.3.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §5.

Maps internal IDs (`agent_03`, `L1`, `fear`) to creator-readable labels.

Three lookup strategies, in priority order:
    1. `content/{anchor_id}/identity_map.json` — explicit per-anchor mapping
    2. Archetype inference from observer initial state (rule-based, deterministic)
    3. Pass-through (return ID as-is)

ABSOLUTE Rules:
    - Rule #1: no person hardcoding *in code*. Names live in content/, not here.
    - Rule #6: existing observer / mining API is not modified — this is an
      additive Stage 5 module.
    - Plan §10.1: identity mapping is *not plot hardcoding*. The map says
      "who is who", not "what they will do".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Identity dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentIdentity:
    """Display-side metadata for one agent.

    `display_name` is the only required field; everything else is optional
    enrichment that Stage 6 (StoryCandidate) can consume.
    """
    agent_id: str
    display_name: str
    archetype: str = "unknown"          # e.g. "loyal_disciple", "external_authority"
    role: str = ""                      # narrative role (e.g. "disciple")
    dramatic_function: str = ""         # e.g. "loyal follower under fear"
    initial_desire: str = ""
    core_vulnerability: str = ""

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "archetype": self.archetype,
            "role": self.role,
            "dramatic_function": self.dramatic_function,
            "initial_desire": self.initial_desire,
            "core_vulnerability": self.core_vulnerability,
        }


@dataclass(frozen=True)
class GroupIdentity:
    group_id: str
    display_name: str
    function: str = ""
    risk: str = ""

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "display_name": self.display_name,
            "function": self.function,
            "risk": self.risk,
        }


# ---------------------------------------------------------------------------
# Pressure translation (verbatim phrases per plan §5.3)
# ---------------------------------------------------------------------------

_PRESSURE_PHRASES_RISE = {
    "fear":                  "fear intensifies",
    "hope":                  "hope steadies",                  # hope rising = recovery
    "shame_self":            "shame accumulates",
    "authority_vigilance":   "authority pressure closes in",
    "public_suspicion":      "public suspicion rises",
    "blame_concentration":   "blame begins to concentrate",
    "group_tension":         "group tension sharpens",
    "crowd_mood":            "crowd mood shifts",
}

_PRESSURE_PHRASES_FALL = {
    "fear":                  "fear eases",
    "hope":                  "resolve weakens",
    "shame_self":            "shame relaxes",
    "authority_vigilance":   "authority pressure recedes",
    "public_suspicion":      "public suspicion settles",
    "blame_concentration":   "blame disperses",
    "group_tension":         "group tension softens",
    "crowd_mood":            "crowd mood shifts",
}


def translate_pressure(name: str, direction: str = "rise") -> str:
    """Map a raw pressure name to a neutral, creator-readable phrase.

    Plan §5.3: this is *not* prose. It's a fixed dictionary of phrases.
    No engine-state interpretation, no embellishment.
    """
    if direction == "fall":
        return _PRESSURE_PHRASES_FALL.get(name, name)
    return _PRESSURE_PHRASES_RISE.get(name, name)


# ---------------------------------------------------------------------------
# Archetype inference (fallback when no identity_map.json exists)
# ---------------------------------------------------------------------------

def _infer_archetype_from_initial_state(
    agent_initial: dict[str, Any],
) -> tuple[str, str]:
    """Return (archetype, dramatic_function) inferred from initial state.

    Pure function over the observer dump's first-tick agent record. The
    inference rules are deterministic and content-free — they do not name
    the character, only categorize the *shape* of their starting profile.
    """
    fear = float(agent_initial.get("fear", 0.0))
    hope = float(agent_initial.get("hope", 5.0))
    shame = float(agent_initial.get("shame_self", 0.0))
    state = agent_initial.get("dominant_state", "calm")

    if fear < 1.5 and hope >= 5.0 and state == "calm":
        return ("loyal_presence", "stays close, low initial fear")
    if fear >= 5.0 or state in ("tense", "fragmenting"):
        return ("strained_presence", "starts under pressure")
    if hope < 3.0:
        return ("low_hope_actor", "starts with weakened resolve")
    if shame >= 3.0:
        return ("burdened_actor", "carries existing shame")
    return ("background_presence", "unremarkable starting profile")


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class IdentityResolver:
    """Resolve agent_id / group_id to display labels.

    Construction:
        resolver = IdentityResolver.from_observer(observer_dump)
        # → looks up content/{anchor_id}/identity_map.json if it exists,
        #   otherwise infers archetypes from the dump itself.

    Usage:
        resolver.agent_label("agent_03")    # → display name from map, or "agent_03 (archetype)"
        resolver.group_label("L1")          # → "disciple cluster" or "L1"
    """

    def __init__(
        self,
        anchor_id: str,
        agent_map: dict[str, AgentIdentity],
        group_map: dict[str, GroupIdentity],
    ) -> None:
        self.anchor_id = anchor_id
        self._agents = agent_map
        self._groups = group_map

    # --- factories -----------------------------------------------------

    @classmethod
    def from_observer(
        cls,
        observer: dict[str, Any],
        content_root: Optional[Path] = None,
    ) -> "IdentityResolver":
        meta = observer.get("meta", {})
        anchor_id = meta.get("anchor_id", "unknown")

        # Step 1: load explicit identity_map.json if present
        explicit_agents: dict[str, AgentIdentity] = {}
        explicit_groups: dict[str, GroupIdentity] = {}
        if content_root is None:
            content_root = Path("content")
        # Anchor metadata lives under content/anchors/{anchor_id}/ — separate
        # from agent packs (single-character profiles) which have engine-load schema.
        map_path = content_root / "anchors" / anchor_id / "identity_map.json"
        if map_path.exists():
            data = json.loads(map_path.read_text(encoding="utf-8"))
            for aid, info in (data.get("agents") or {}).items():
                explicit_agents[aid] = AgentIdentity(
                    agent_id=aid,
                    display_name=info.get("display_name", aid),
                    archetype=info.get("archetype", "unknown"),
                    role=info.get("role", ""),
                    dramatic_function=info.get("dramatic_function", ""),
                    initial_desire=info.get("initial_desire", ""),
                    core_vulnerability=info.get("core_vulnerability", ""),
                )
            for gid, info in (data.get("groups") or {}).items():
                explicit_groups[gid] = GroupIdentity(
                    group_id=gid,
                    display_name=info.get("display_name", gid),
                    function=info.get("function", ""),
                    risk=info.get("risk", ""),
                )

        # Step 2: archetype-infer for any agent NOT in the explicit map
        ticks = observer.get("ticks") or []
        if ticks:
            for a in ticks[0].get("agents", []):
                aid = a["id"]
                if aid in explicit_agents:
                    continue
                archetype, function = _infer_archetype_from_initial_state(a)
                explicit_agents[aid] = AgentIdentity(
                    agent_id=aid,
                    display_name=aid,  # fallback — no name available
                    archetype=archetype,
                    role="",
                    dramatic_function=function,
                )
            # Groups: minimal fallback if not in explicit map
            for g in ticks[0].get("groups", []):
                gid = g["id"]
                if gid in explicit_groups:
                    continue
                explicit_groups[gid] = GroupIdentity(
                    group_id=gid,
                    display_name=gid,
                    function="",
                    risk="",
                )

        return cls(anchor_id=anchor_id,
                   agent_map=explicit_agents,
                   group_map=explicit_groups)

    # --- lookups -------------------------------------------------------

    def agent_label(self, agent_id: str) -> str:
        """Return display_name; fall back to '{id} ({archetype})'."""
        ident = self._agents.get(agent_id)
        if ident is None:
            return agent_id
        if ident.display_name and ident.display_name != agent_id:
            return ident.display_name
        if ident.archetype and ident.archetype != "unknown":
            return f"{agent_id} ({ident.archetype})"
        return agent_id

    def agent_identity(self, agent_id: str) -> AgentIdentity:
        return self._agents.get(agent_id) or AgentIdentity(
            agent_id=agent_id,
            display_name=agent_id,
            archetype="unknown",
        )

    def group_label(self, group_id: str) -> str:
        ident = self._groups.get(group_id)
        if ident is None or not ident.display_name:
            return group_id
        return ident.display_name

    def group_identity(self, group_id: str) -> GroupIdentity:
        return self._groups.get(group_id) or GroupIdentity(
            group_id=group_id, display_name=group_id,
        )

    # --- bulk export ---------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "anchor_id": self.anchor_id,
            "agents": {aid: a.to_dict() for aid, a in self._agents.items()},
            "groups": {gid: g.to_dict() for gid, g in self._groups.items()},
        }
