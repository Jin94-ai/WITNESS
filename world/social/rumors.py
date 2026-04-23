"""RumorLayer — Layer 5 rumour graph (Spike 3 Phase 3C skeleton).

Population-level rumour dynamics. Independent of factions in this loop;
cross-layer edges (rumour → faction influence, rumour intensity → agent
percept) arrive in a later loop after the aggregation plumbing is
extended.

Data model:
    Rumor      (rumor_id, content, source_agent, spread, credibility, age_days)
    RumorState (tuple of active Rumor records + seeded/expired counters)

Update rules per tick (reviewer #1 — explicit dynamics):

    # 1. Age advance.
    age_days(t+1) = age_days(t) + dt_days

    # 2. Spread drift toward asymptote driven by crowd density.
    #    crowd contributes proportional to (crowd - baseline) so a quiet
    #    city does not inflate rumour reach.
    spread(t+1) = clamp(
          spread(t)
        + spread_rate_per_day
          * (crowd_density(t) - baseline_density)
          * (1 - spread(t))
          * dt_days
        - spread_decay_per_day * spread(t) * dt_days
    , 0.0, 1.0)

    # 3. Credibility drifts toward zero over time unless refreshed.
    credibility(t+1) = clamp(
          credibility(t)
        - credibility_decay_per_day * dt_days
    , 0.0, 1.0)

    # 4. Garbage-collect (age > max_age_days OR spread == 0 AND credibility == 0).

Seeding: the ``ctx.aggregated_effects["rumor_seed"]`` channel is watched
at each tick. The SyncLayer's THRESHOLD aggregation collapses multiple
agent-substep rumour emissions into a boolean-ish 0/1 value per day; if
non-zero, one fresh Rumor record is appended (content comes from the
configured ``seed_content`` template + a sequence id). Richer per-seed
content is added later; Spike 3C just proves seeding works.

Brakes (reviewer #2):
- saturation via clamp on spread/credibility.
- `spread_decay_per_day` keeps long-lived, unreinforced rumours from
  pinning at 1.0.
- garbage collection removes dead rumours so memory stays bounded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import Rumor, RumorState


@dataclass
class _RumorParams:
    spread_rate_per_day: float
    spread_decay_per_day: float
    credibility_decay_per_day: float
    initial_spread: float
    initial_credibility: float
    max_age_days: float
    max_active_rumors: int
    seed_content: str


class RumorLayer:
    """Layer 5 rumour sub-state (Spike 3 Phase 3C skeleton)."""

    layer_id = "rumors"

    def __init__(self) -> None:
        self._params = _RumorParams(
            spread_rate_per_day=0.05,
            spread_decay_per_day=0.03,
            credibility_decay_per_day=0.02,
            initial_spread=0.05,
            initial_credibility=0.8,
            max_age_days=30.0,
            max_active_rumors=40,
            seed_content="unspecified_rumor",
        )
        self._seed_counter = 0

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> RumorState:
        self._params = _RumorParams(
            spread_rate_per_day=float(config.get("spread_rate_per_day", 0.05)),
            spread_decay_per_day=float(config.get("spread_decay_per_day", 0.03)),
            credibility_decay_per_day=float(
                config.get("credibility_decay_per_day", 0.02),
            ),
            initial_spread=float(config.get("initial_spread", 0.05)),
            initial_credibility=float(config.get("initial_credibility", 0.8)),
            max_age_days=float(config.get("max_age_days", 30.0)),
            max_active_rumors=int(config.get("max_active_rumors", 40)),
            seed_content=str(config.get("seed_content", "unspecified_rumor")),
        )
        self._seed_counter = 0
        seeds = config.get("initial_rumors", [])
        initial: list[Rumor] = []
        for seed in seeds:
            initial.append(self._new_rumor(
                content=seed.get("content", self._params.seed_content),
                source_agent=seed.get("source_agent", "unknown"),
                spread=float(seed.get("spread", self._params.initial_spread)),
                credibility=float(seed.get(
                    "credibility", self._params.initial_credibility,
                )),
                age_days=float(seed.get("age_days", 0.0)),
                source_location=seed.get("source_location"),
                age_in_substeps=int(seed.get("age_in_substeps", 0)),
            ))
        return RumorState(rumors=tuple(initial), seeded_total=len(initial))

    def tick(self, state: RumorState, ctx: LayerContext) -> RumorState:
        dt = max(0.0, ctx.dt_days)
        crowd = ctx.world_snapshot.crowd
        drive = max(0.0, crowd.crowd_density - crowd.baseline_density)

        # 1. age + dynamics.
        updated: list[Rumor] = []
        for r in state.rumors:
            new_age = r.age_days + dt
            if new_age > self._params.max_age_days:
                continue  # expire
            spread_rise = (
                self._params.spread_rate_per_day * drive
                * (1.0 - r.spread) * dt
            )
            spread_decay = self._params.spread_decay_per_day * r.spread * dt
            new_spread = max(0.0, min(1.0, r.spread + spread_rise - spread_decay))
            new_cred = max(
                0.0,
                min(1.0, r.credibility
                   - self._params.credibility_decay_per_day * dt),
            )
            # Drop completely dead rumours early.
            if new_spread <= 1e-6 and new_cred <= 1e-6:
                continue
            updated.append(Rumor(
                rumor_id=r.rumor_id,
                content=r.content,
                source_agent=r.source_agent,
                spread=new_spread,
                credibility=new_cred,
                age_days=new_age,
                # Phase 5C: carry spatial fields forward if present on input.
                source_location=r.source_location,
                age_in_substeps=r.age_in_substeps,
            ))

        expired_this_tick = len(state.rumors) - len(updated)

        # 2. seeding from aggregated_effects["rumor_seed"] (THRESHOLD: 0 or 1).
        seeded_this_tick = 0
        seed_signal = ctx.aggregated_effects.get("rumor_seed", 0.0) if ctx.aggregated_effects else 0.0
        if seed_signal and seed_signal > 0.0:
            if len(updated) < self._params.max_active_rumors:
                updated.append(self._new_rumor(
                    content=self._params.seed_content,
                    source_agent="aggregated",
                    spread=self._params.initial_spread,
                    credibility=self._params.initial_credibility,
                    age_days=0.0,
                ))
                seeded_this_tick = 1

        return RumorState(
            rumors=tuple(updated),
            seeded_total=state.seeded_total + seeded_this_tick,
            expired_total=state.expired_total + expired_this_tick,
        )

    # ------------------------------------------------------------------
    # Helpers

    def _new_rumor(
        self, *,
        content: str,
        source_agent: str,
        spread: float,
        credibility: float,
        age_days: float,
        source_location: str | None = None,
        age_in_substeps: int = 0,
    ) -> Rumor:
        self._seed_counter += 1
        return Rumor(
            rumor_id=f"rumor-{self._seed_counter}",
            content=content,
            source_agent=source_agent,
            spread=max(0.0, min(1.0, spread)),
            credibility=max(0.0, min(1.0, credibility)),
            age_days=max(0.0, age_days),
            source_location=source_location,
            age_in_substeps=max(0, age_in_substeps),
        )

    def describe_dynamics(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "phase": "3C_independent_skeleton",
            "update_rule": (
                "age += dt; "
                "spread += rate*(crowd-base)*(1-spread)*dt - decay*spread*dt; "
                "credibility -= cred_decay*dt; "
                "GC if age>max_age or (spread==0 and cred==0); "
                "seed if aggregated_effects[rumor_seed] > 0"
            ),
            "causal_dependencies": [
                "crowd.crowd_density",
                "aggregated_effects.rumor_seed",
            ],
            "brake_type": (
                "saturation (clamp 0..1) + decay + age expiry + max_active_rumors cap"
            ),
            "spread_rate_per_day": self._params.spread_rate_per_day,
            "spread_decay_per_day": self._params.spread_decay_per_day,
            "credibility_decay_per_day": self._params.credibility_decay_per_day,
            "max_age_days": self._params.max_age_days,
            "max_active_rumors": self._params.max_active_rumors,
        }
