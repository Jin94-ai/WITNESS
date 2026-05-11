"""SpatialRegistry — manages multiple Location instances + agent positions."""

from __future__ import annotations

from engine.world.spatial.location import Location


class SpatialRegistry:
    """Holds locations + agent→location mapping + movement operations.

    Generic: no proper names baked in. Content provides Location instances.
    """

    def __init__(self, locations: list[Location] | None = None) -> None:
        self._locations: dict[str, Location] = {
            loc.location_id: loc for loc in (locations or [])
        }
        # agent_id → location_id
        self._agent_locations: dict[str, str] = {}

    # -----------------------------------------------------------------
    # Location CRUD
    # -----------------------------------------------------------------

    def add_location(self, location: Location) -> None:
        self._locations[location.location_id] = location

    def get(self, location_id: str) -> Location:
        if location_id not in self._locations:
            raise KeyError(f"Unknown location '{location_id}'")
        return self._locations[location_id]

    def all(self) -> list[Location]:
        return list(self._locations.values())

    def count(self) -> int:
        return len(self._locations)

    # -----------------------------------------------------------------
    # Agent placement
    # -----------------------------------------------------------------

    def place(self, agent_id: str, location_id: str) -> None:
        """Place agent in location (removing from prior if any)."""
        # Remove from prior
        prior = self._agent_locations.get(agent_id)
        if prior and prior in self._locations:
            self._locations[prior].agents_present.discard(agent_id)

        # Add to new
        loc = self.get(location_id)
        loc.agents_present.add(agent_id)
        self._agent_locations[agent_id] = location_id

    def where(self, agent_id: str) -> str | None:
        return self._agent_locations.get(agent_id)

    def agents_at(self, location_id: str) -> set[str]:
        loc = self._locations.get(location_id)
        return set(loc.agents_present) if loc else set()

    def move(self, agent_id: str, to_location: str) -> bool:
        """Attempt to move agent. Returns True if successful.

        Constraints:
            - Target must be in escape_routes of current location, OR
              explicitly connected.
            - Agent must be present somewhere first.
        """
        current = self.where(agent_id)
        if current is None:
            # Not placed yet — allow direct placement
            self.place(agent_id, to_location)
            return True

        if current == to_location:
            return True  # no-op

        cur_loc = self._locations.get(current)
        if cur_loc is None:
            # Stale reference; re-place
            self.place(agent_id, to_location)
            return True

        if to_location not in cur_loc.escape_routes:
            return False  # not adjacent

        # Capacity check
        target_loc = self.get(to_location)
        if len(target_loc.agents_present) >= target_loc.max_capacity:
            return False

        self.place(agent_id, to_location)
        return True

    # -----------------------------------------------------------------
    # Affordance query — returns modifier for action availability
    # -----------------------------------------------------------------

    # Simple action → affordance requirement table (generic). Content layers
    # can extend.
    _AFFORDANCE_REQUIREMENTS: dict[str, dict[str, float]] = {
        "flee":             {"escape_routes_count_min": 1.0},
        "stay_hiding":      {"concealment_min": 0.5},
        "draw_sword":       {"authority_reach_max": 0.8},
        "public_accusation": {"visibility_min": 0.6, "crowdability_min": 0.4},
        "jump_into_sea":    {"has_water_tag": 1.0},
    }

    def is_action_affordable(
        self, agent_id: str, action: str,
    ) -> tuple[bool, str]:
        """Check if agent's current location affords the action.
        Returns (ok, reason_if_blocked)."""
        location_id = self.where(agent_id)
        if location_id is None:
            return True, "no location set"  # no-op when not placed
        loc = self.get(location_id)

        reqs = self._AFFORDANCE_REQUIREMENTS.get(action)
        if not reqs:
            return True, ""

        for key, threshold in reqs.items():
            if key == "escape_routes_count_min":
                if len(loc.escape_routes) < int(threshold):
                    return False, f"no escape routes at {location_id}"
            elif key == "concealment_min":
                if loc.concealment < threshold:
                    return False, f"insufficient concealment ({loc.concealment:.2f})"
            elif key == "authority_reach_max":
                if loc.authority_reach > threshold:
                    return False, f"authority_reach too high ({loc.authority_reach:.2f})"
            elif key == "visibility_min":
                if loc.visibility < threshold:
                    return False, f"visibility too low ({loc.visibility:.2f})"
            elif key == "crowdability_min":
                if loc.crowdability < threshold:
                    return False, f"insufficient crowdability ({loc.crowdability:.2f})"
            elif key == "has_water_tag":
                if not loc.has_tag("water"):
                    return False, f"no water tag at {location_id}"
        return True, ""
