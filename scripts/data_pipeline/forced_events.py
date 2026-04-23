"""Phase A extension -- Forced sampling for canonical-event actions.

Phase A (forced_sampling.py) covered only the 6 voluntary actions that
``AgentBehaviorProfile.select_action`` produces. The remaining ~15 action
ids live inside ``canonical_events.json`` ``action_options`` and fire only
when the event triggers at a specific tick.

This module bypasses the event-trigger requirement by calling
``decide_action`` directly on the event's option list with a ForcingPolicy.
No simulation loop is run -- the (state, action) pair is purely:
"at this boundary state, if this event had fired now, the forced policy
would choose this action."

That pairing differs from Phase A in one important way (flagged in the
report's Alternate Interpretations): Phase A ran 1-tick simulation so
rule_engine applied once. Here no rule_engine is applied. Trade-off:
- simpler, no tick-scheduling concerns
- state == our override (no rule drift)
- but departs further from engine's natural trajectory distribution

The H4 self-check for this: this dataset is labeled ``source="forced_event"``
and downstream consumers can choose to include/exclude. Simulation-
fidelity remains Phase F's concern.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.core.event import ActionOption  # noqa: E402
from engine.core.state import AgentState  # noqa: E402
from engine.io.loader import load_events  # noqa: E402
from engine.simulation.decision import decide_action  # noqa: E402
from engine.simulation.training_samples import state_to_feature_vector  # noqa: E402
from scripts.data_pipeline._common import (  # noqa: E402
    CONTENT,
    make_peter_state,
    register_domain_types,
)
from scripts.data_pipeline.forced_sampling import ForcingPolicy  # noqa: E402

# ---------------------------------------------------------------------
# Boundary zones for canonical-event actions.
# Derived by inspecting each action's weight_formula state_multipliers
# and picking ranges that favour the action + satisfy preconditions.
# ---------------------------------------------------------------------

EVENT_BOUNDARY_ZONES: dict[str, dict[str, tuple[float, float]]] = {
    # scene_01 jerusalem entry -- mass action choice
    "join_crowd": {
        "hope": (6.0, 10.0), "love": (5.0, 10.0),
        "fear": (0.0, 4.0), "confusion": (0.0, 5.0),
    },
    "watch_quietly": {
        "fear": (4.0, 9.0), "confusion": (4.0, 9.0),
        "hope": (3.0, 8.0), "love": (3.0, 8.0),
    },
    # scene_05 foot washing
    "resist_washing": {
        "confusion": (5.0, 10.0), "fear": (3.0, 9.0),
        "identity_shift": (-5.0, 5.0),
    },
    "accept_washing": {
        "love": (6.0, 10.0), "hope": (5.0, 10.0),
        "confusion": (0.0, 5.0),
    },
    # scene_07 gethsemane
    "stay_awake": {
        "fatigue": (0.0, 5.0), "love": (6.0, 10.0),
        "fear": (3.0, 8.0),
    },
    "fall_asleep": {
        "fatigue": (7.0, 10.0), "hunger": (4.0, 10.0),
        "love": (3.0, 8.0),
    },
    # scene_08 arrest
    "draw_sword": {
        "fear": (5.0, 9.0), "love": (7.0, 10.0),
        "confusion": (3.0, 8.0), "event_trauma": (2.0, 7.0),
    },
    "flee": {
        "fear": (8.0, 10.0), "love": (0.0, 4.0),
        "fatigue": (4.0, 9.0),
    },
    "follow_at_distance": {
        "fear": (5.0, 8.0), "love": (5.0, 9.0),
        "confusion": (4.0, 9.0), "trust_scar": (1.0, 4.0),
    },
    # scene_09 denial
    "deny": {
        "fear": (8.0, 10.0), "moral_injury": (3.0, 9.0),
        "identity_shift": (-8.0, -2.0), "event_trauma": (4.0, 9.0),
    },
    "confess": {
        "love": (6.0, 10.0), "hope": (5.0, 10.0),
        "fear": (4.0, 9.0), "moral_injury": (5.0, 10.0),
    },
    # scene_12 empty tomb
    "run_to_tomb": {
        "hope": (6.0, 10.0), "love": (7.0, 10.0),
        "grief": (4.0, 9.0), "moral_injury": (5.0, 10.0),
    },
    "stay_hiding": {
        "fear": (7.0, 10.0), "moral_injury": (5.0, 10.0),
        "trust_scar": (3.0, 9.0), "identity_shift": (-8.0, -2.0),
    },
    # scene_15 tiberias
    "jump_into_sea": {
        "love": (8.0, 10.0), "hope": (7.0, 10.0),
        "identity_shift": (-4.0, 4.0), "moral_injury": (3.0, 9.0),
    },
    "stay_on_boat": {
        "love": (5.0, 9.0), "fatigue": (4.0, 9.0),
        "hope": (4.0, 9.0),
    },
}


def _sample_boundary(
    zone: dict[str, tuple[float, float]], rng: np.random.Generator,
) -> AgentState:
    """Sample uniformly inside the zone; fill other fields with defaults
    pulled from wider ranges to break the constant-feature problem."""
    kwargs: dict[str, float] = {}
    for field, (lo, hi) in zone.items():
        kwargs[field] = float(rng.uniform(lo, hi))
    defaults = {
        "fear": 5.0, "hope": 5.0, "grief": 1.0,
        "confusion": 5.0, "love": 5.0,
        "fatigue": float(rng.uniform(2, 8)),
        "hunger": float(rng.uniform(1, 6)),
        "health": float(rng.uniform(5, 9)),
        "moral_injury": float(rng.uniform(0, 5)),
        "identity_shift": float(rng.uniform(-5, 5)),
        "event_trauma": float(rng.uniform(0, 5)),
        "trust_scar": float(rng.uniform(0, 3)),
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)
    return make_peter_state(**kwargs)


def _build_event_options_map() -> dict[str, list[ActionOption]]:
    """action_id -> the ActionOption list containing it (for decide_action).

    Actions appearing in multiple denial events (deny/confess) use the
    first event's options list; decide_action only needs a valid list
    where the target action is present.
    """
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    by_action: dict[str, list[ActionOption]] = {}
    for event in events:
        opts = list(event.action_options or [])
        if not opts:
            continue
        for opt in opts:
            if opt.action_id not in by_action:
                by_action[opt.action_id] = opts
    return by_action


def harvest_forced_events(
    *, samples_per_action: int = 300, seed_base: int = 70_000,
) -> dict[str, Any]:
    register_domain_types()
    event_options = _build_event_options_map()
    rng = np.random.default_rng(0)

    X_rows: list[list[float]] = []
    actions: list[str] = []
    per_action_saved: dict[str, int] = {}
    per_action_rejected: dict[str, int] = {}

    for action_id, zone in EVENT_BOUNDARY_ZONES.items():
        options = event_options.get(action_id)
        if options is None:
            print(f"  [warn] {action_id} not in any canonical event, skipping")
            continue

        policy = ForcingPolicy(action_id)
        saved, rejected = 0, 0
        max_attempts = samples_per_action * 3

        for attempt in range(max_attempts):
            if saved >= samples_per_action:
                break
            state = _sample_boundary(zone, rng)
            # decide_action evaluates preconditions on each option; if the
            # target is excluded and weight mask gives 0 to others, fall
            # back to rule-based weights and another action may fire.
            try:
                chosen = decide_action(
                    state, options,
                    random.Random(seed_base + attempt),
                    policy=policy,
                )
            except Exception:
                rejected += 1
                continue
            if chosen is None or chosen.action_id != action_id:
                rejected += 1
                continue
            X_rows.append(state_to_feature_vector(state))
            actions.append(action_id)
            saved += 1

        per_action_saved[action_id] = saved
        per_action_rejected[action_id] = rejected
        print(
            f"  [event-forced] {action_id:<22} saved={saved}/{samples_per_action}  "
            f"rejected={rejected}",
        )

    X = np.asarray(X_rows, dtype=np.float32) if X_rows else np.zeros((0, 12), dtype=np.float32)
    return {
        "X": X, "actions": actions, "source": "forced_event",
        "per_action_saved": per_action_saved,
        "per_action_rejected": per_action_rejected,
    }


def main() -> int:
    out = ROOT / "data" / "person" / "pipeline_v2" / "forced_events"
    out.mkdir(parents=True, exist_ok=True)
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 300

    print(f"[Phase A ext] Event-action forced sampling: target {target}/action "
          f"x {len(EVENT_BOUNDARY_ZONES)} actions")
    harvest = harvest_forced_events(samples_per_action=target)

    from collections import Counter
    print(f"\n  total: {harvest['X'].shape[0]}")
    print(f"  distribution: {dict(Counter(harvest['actions']))}")

    np.save(out / "X.npy", harvest["X"])
    (out / "meta.json").write_text(
        json.dumps({
            "source": harvest["source"],
            "actions": harvest["actions"],
            "n_samples": int(harvest["X"].shape[0]),
            "per_action_saved": harvest["per_action_saved"],
            "per_action_rejected": harvest["per_action_rejected"],
            "target_per_action": target,
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
