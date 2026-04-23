"""BatchInterventionRunner — Spike 4 Phase 4B paired-ensemble runner.

Given one ``InterventionSpec``, run two matched ensembles:

- **control arm**: ``n_seeds`` integrated runs with the unmodified
  world + base configs (spec ignored — the null control).
- **intervention arm**: ``n_seeds`` integrated runs with the spec
  applied via ``InterventionEngine``.

Both arms share the same seed range, so seed-paired comparisons are
possible (seed 0 control vs seed 0 intervention, etc.). The runner
collects key metrics per seed, computes aggregate comparison
statistics (mean delta, Cohen's d, permutation p-value), and returns
an ``ExperimentResult`` ready to serialise into
``docs/world/paper_data/intervention_<id>.json``.

Metrics tracked per seed (reuse of world_numbers conventions):

- ``trigger_count`` — sum of fired triggers over the run
- ``hazard_count`` — sum of fired hazard events
- ``rumors_seeded`` — RumorState.seeded_total at the final day
- ``rumor_intensity_max`` — max active_intensity across days
- ``jesus_movement_final_influence`` — if factions active
- ``pharisees_final_influence`` — control faction baseline
- ``peter_final_fear`` — if peter present in final_agent_states
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any

from engine.core.action import AgentBehaviorProfile
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from world.core.world_config import WorldConfig
from world.economy.economy import EconomyLayer
from world.environment.calendar import CalendarLayer
from world.factions.factions import FactionLayer
from world.intervention.engine import InterventionEngine
from world.intervention.spec import InterventionSpec
from world.politics.politics import PoliticsLayer
from world.simulation.integrated_runner import IntegratedWorldRunner
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer
from world.social.rumors import RumorLayer

METRIC_NAMES: tuple[str, ...] = (
    "trigger_count", "hazard_count", "rumors_seeded", "rumor_intensity_max",
    "jesus_movement_final_influence", "pharisees_final_influence",
    "peter_final_fear",
    # Time-to-threshold metrics — saturation-robust (see lesson 34/35).
    # Measures *when* the state crossed a reference level rather than its
    # final (possibly ceiling-clamped) value.
    "peter_fear_crosses_9_day",
    "roman_alertness_auc",
)


@dataclass(frozen=True)
class SeedMetrics:
    seed: int
    metrics: dict[str, float | None]


@dataclass(frozen=True)
class ArmSummary:
    label: str
    per_seed: list[SeedMetrics]
    aggregate: dict[str, float]


@dataclass(frozen=True)
class ExperimentResult:
    spec: InterventionSpec
    n_seeds: int
    n_days: int
    control: ArmSummary
    intervention: ArmSummary
    comparison: dict[str, dict[str, float]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "intervention_id": self.spec.intervention_id,
            "description": self.spec.description,
            "n_seeds": self.n_seeds,
            "n_days": self.n_days,
            "control": _arm_to_dict(self.control),
            "intervention": _arm_to_dict(self.intervention),
            "comparison": self.comparison,
        }


def _arm_to_dict(arm: ArmSummary) -> dict[str, Any]:
    return {
        "label": arm.label,
        "per_seed": [
            {"seed": s.seed, "metrics": s.metrics} for s in arm.per_seed
        ],
        "aggregate": arm.aggregate,
    }


class BatchInterventionRunner:
    """Run control + intervention ensembles, collect paired metrics."""

    def __init__(
        self,
        *,
        world_config_base: WorldConfig,
        sim_config_base: SimulationConfig,
        rule_engine: RuleEngine,
        behavior_profiles: dict[str, AgentBehaviorProfile],
        substeps_per_day: int = 12,
    ) -> None:
        self.world_config_base = world_config_base
        self.sim_config_base = sim_config_base
        self.rule_engine = rule_engine
        self.behavior_profiles = behavior_profiles
        self.substeps_per_day = substeps_per_day
        self._engine = InterventionEngine()

    # ------------------------------------------------------------------
    # Public API.

    def run_experiment(
        self, spec: InterventionSpec, *,
        n_seeds: int = 10, n_days: int = 90,
    ) -> ExperimentResult:
        null_spec = InterventionSpec(
            intervention_id=f"{spec.intervention_id}__control",
        )
        control = self._run_arm(null_spec, n_seeds, n_days, label="control")
        intervention = self._run_arm(
            spec, n_seeds, n_days, label="intervention",
        )
        comparison = self._compare(control, intervention)
        return ExperimentResult(
            spec=spec, n_seeds=n_seeds, n_days=n_days,
            control=control, intervention=intervention,
            comparison=comparison,
        )

    # ------------------------------------------------------------------
    # Arm execution.

    def _run_arm(
        self, spec: InterventionSpec, n_seeds: int, n_days: int, *, label: str,
    ) -> ArmSummary:
        per_seed: list[SeedMetrics] = []
        for seed in range(n_seeds):
            world_cfg, sim_cfg, _ = self._engine.apply(
                spec, self.world_config_base, self.sim_config_base,
            )
            # Re-apply seed to the world config since InterventionEngine
            # deep-copies first (preserves the seed but let's be explicit).
            world_cfg = _with_seed(world_cfg, seed)

            # Only use profiles for agents that remain after intervention.
            active_ids = {s.agent_id for s in sim_cfg.initial_states}
            profiles = {
                aid: p for aid, p in self.behavior_profiles.items()
                if aid in active_ids
            }

            world_tick = WorldTick(
                calendar_layer=CalendarLayer(),
                crowd_layer=CrowdLayer(),
                economy_layer=EconomyLayer(),
                politics_layer=PoliticsLayer(),
                faction_layer=FactionLayer(),
                rumor_layer=RumorLayer(),
                config=world_cfg,
            )
            runner = IntegratedWorldRunner(
                world_tick=world_tick,
                world_config=world_cfg,
                base_config=sim_cfg,
                rule_engine=self.rule_engine,
                behavior_profiles=profiles,
                substeps_per_day=self.substeps_per_day,
            )
            result = runner.run(n_days=n_days, seed=seed)
            per_seed.append(SeedMetrics(
                seed=seed, metrics=_extract_metrics(result),
            ))
        agg = _aggregate(per_seed)
        return ArmSummary(label=label, per_seed=per_seed, aggregate=agg)

    # ------------------------------------------------------------------
    # Comparison statistics.

    def _compare(
        self, control: ArmSummary, intervention: ArmSummary,
    ) -> dict[str, dict[str, float]]:
        result: dict[str, dict[str, float]] = {}
        for name in METRIC_NAMES:
            ctrl_vals = [
                s.metrics[name] for s in control.per_seed
                if s.metrics.get(name) is not None
            ]
            int_vals = [
                s.metrics[name] for s in intervention.per_seed
                if s.metrics.get(name) is not None
            ]
            if not ctrl_vals or not int_vals:
                continue
            ctrl_mean = statistics.fmean(ctrl_vals)  # type: ignore[arg-type]
            int_mean = statistics.fmean(int_vals)  # type: ignore[arg-type]
            cohens_d = _cohens_d(ctrl_vals, int_vals)  # type: ignore[arg-type]
            perm_p = _permutation_p_value(
                ctrl_vals, int_vals, n_permutations=500,  # type: ignore[arg-type]
            )
            result[name] = {
                "control_mean": round(ctrl_mean, 4),
                "intervention_mean": round(int_mean, 4),
                "mean_delta": round(int_mean - ctrl_mean, 4),
                "cohens_d": round(cohens_d, 4),
                "permutation_p_value": round(perm_p, 4),
            }
        return result


# ----------------------------------------------------------------------
# Helpers.

def _with_seed(world_cfg: WorldConfig, seed: int) -> WorldConfig:
    from dataclasses import replace as dc_replace
    return dc_replace(world_cfg, rng_seed=seed)


def _extract_metrics(result: Any) -> dict[str, float | None]:
    fw = result.final_world
    rumors_seeded = 0
    max_intensity = 0.0
    if fw is not None and fw.rumors is not None:
        rumors_seeded = fw.rumors.seeded_total
        for d in result.days:
            if d.world.rumors is not None:
                inten = d.world.rumors.active_intensity()
                if inten > max_intensity:
                    max_intensity = inten

    jm: float | None = None
    phar: float | None = None
    if fw is not None and fw.factions is not None:
        if "jesus_movement" in fw.factions.factions:
            jm = round(fw.factions.factions["jesus_movement"].influence, 4)
        if "pharisees" in fw.factions.factions:
            phar = round(fw.factions.factions["pharisees"].influence, 4)

    peter = result.final_agent_states.get("peter")
    peter_fear = (
        round(peter.emotions.fear, 4) if peter is not None else None
    )

    # Saturation-robust metrics (lessons 34/35): time-to-threshold and AUC.
    # Peter fear crosses 9.0 — if saturates on day X, X is the signal.
    # Fallback to n_days when never crossed.
    fear_day_crossing: float | None = None
    alertness_auc: float | None = None
    n_days_run = len(result.days)
    for d_idx, d in enumerate(result.days):
        p = d.agent_states.get("peter")
        if p is not None and fear_day_crossing is None:
            if p.emotions.fear >= 9.0:
                fear_day_crossing = float(d_idx + 1)  # 1-based day
        if d.world.politics is not None:
            if alertness_auc is None:
                alertness_auc = 0.0
            alertness_auc += float(d.world.politics.roman_alertness)
    if fear_day_crossing is None:
        fear_day_crossing = float(n_days_run) if n_days_run else None
    if alertness_auc is not None:
        alertness_auc = round(alertness_auc, 4)

    return {
        "trigger_count": float(len(result.total_triggers)),
        "hazard_count": float(len(result.total_events)),
        "rumors_seeded": float(rumors_seeded),
        "rumor_intensity_max": round(max_intensity, 4),
        "jesus_movement_final_influence": jm,
        "pharisees_final_influence": phar,
        "peter_final_fear": peter_fear,
        "peter_fear_crosses_9_day": fear_day_crossing,
        "roman_alertness_auc": alertness_auc,
    }


def _aggregate(per_seed: list[SeedMetrics]) -> dict[str, float]:
    agg: dict[str, float] = {}
    for name in METRIC_NAMES:
        values = [
            s.metrics[name] for s in per_seed
            if s.metrics.get(name) is not None
        ]
        if values:
            agg[f"{name}_mean"] = round(
                statistics.fmean(values),  # type: ignore[arg-type]
                4,
            )
    return agg


def _cohens_d(a: list[float], b: list[float]) -> float:
    """Standardised mean difference; pooled SD."""
    if len(a) < 2 or len(b) < 2:
        return 0.0
    va = statistics.variance(a)
    vb = statistics.variance(b)
    na, nb = len(a), len(b)
    pooled = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled == 0:
        return 0.0
    return (statistics.fmean(b) - statistics.fmean(a)) / pooled


def _permutation_p_value(
    a: list[float], b: list[float], n_permutations: int = 500,
) -> float:
    """Two-sided permutation test on mean difference."""
    obs_diff = abs(statistics.fmean(b) - statistics.fmean(a))
    combined = list(a) + list(b)
    na = len(a)
    extremes = 0
    rng = random.Random(0xBA7C4)
    for _ in range(n_permutations):
        shuffled = combined[:]
        rng.shuffle(shuffled)
        perm_diff = abs(
            statistics.fmean(shuffled[na:]) - statistics.fmean(shuffled[:na])
        )
        if perm_diff >= obs_diff:
            extremes += 1
    return extremes / n_permutations


# Fallback unused-import silencer for tiny toolchain complaints.
_ = asdict
