"""Smoke tests for scripts/world_numbers.py + scripts/world_figures.py.

Rationale: the /loop pipeline regenerates world_numbers.json + figures
every cycle; a silent API break (e.g. new mandatory kwarg) would turn
every loop into a no-op. These tests run the smallest possible
invocation so CI and /loop both catch regressions within seconds.

We do NOT run the scripts' ``main()`` functions (those write to
``docs/world/paper_data/``). We call the pure helpers directly and
assert shape/invariants only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.io.loader import register_domain_type

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


_registered = False


def _register() -> None:
    global _registered
    if _registered:
        return
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
    _registered = True


# --------------------------------------------------------------------------
# world_numbers.py


def test_world_numbers_spike1_returns_expected_shape() -> None:
    from scripts.world_numbers import spike1_world_only

    result = spike1_world_only(n_seeds=2, n_days=20)
    assert result["n_seeds"] == 2
    assert result["n_days"] == 20
    assert len(result["per_seed"]) == 2

    keys = {
        "seed", "max_crowd", "max_overflow", "max_price", "max_alert",
        "passover_crowd", "shavuot_crowd", "day_30_crowd",
        "runaway_ceiling_hits",
        # Phase 3B fields (loop #12).
        "zealot_militancy_initial", "zealot_militancy_max",
        "zealot_militancy_at_passover", "zealot_militancy_day_30",
        "militancy_threshold_hits",
    }
    for s in result["per_seed"]:
        assert keys <= set(s), f"missing per-seed keys: {keys - set(s)}"
    # Crowd density must be within [baseline, ceiling].
    for s in result["per_seed"]:
        assert 0.0 <= s["max_crowd"] <= 10.0
        assert s["max_overflow"] >= 0.0
        assert 0.0 <= s["zealot_militancy_max"] <= 10.0
        assert s["militancy_threshold_hits"] >= 0

    agg = result["aggregate"]
    assert {
        "max_crowd_mean", "max_price_mean", "max_alert_mean",
        "passover_crowd_mean", "shavuot_crowd_mean",
        "zealot_militancy_max_mean", "zealot_militancy_passover_mean",
        "militancy_threshold_hits_mean",
    } <= set(agg)


def test_phase_3b_content_behaviour_pin() -> None:
    """Pin the *content-level* Phase 3B behaviour that world_numbers captures.

    Empirical baseline (2026-04-21, seed 0-4, 90 days, current AD-30 config):
        militancy_threshold_hits_mean ≈ 12 (crowd ≥ 5 for ~12 days around
            Passover + Shavuot)
        zealot_militancy_max_mean ≈ 9.25 (starting ~7.0 + 12*0.15 = 1.8
            then compounded with random walk)

    Threshold: the hits must be > 0 (Phase 3B edge is firing) and the
    max militancy must meaningfully exceed the initial floor (there IS a
    boost, not just noise). Future content changes may shift numbers but
    MUST keep the edge active."""
    from scripts.world_numbers import spike1_world_only

    result = spike1_world_only(n_seeds=2, n_days=90)
    agg = result["aggregate"]
    # The threshold edge must fire at least once on average.
    assert agg["militancy_threshold_hits_mean"] > 0, (
        "Phase 3B crowd→zealot edge did not fire in 90 days — "
        "either crowd ceiling dropped below 5 or the layer config is off."
    )
    # The boost must be visible above the initial floor (≈ 7.0).
    assert agg["zealot_militancy_max_mean"] > 7.5, (
        f"Zealot militancy max ({agg['zealot_militancy_max_mean']:.2f}) "
        f"did not rise materially above the initial ~7.0 floor."
    )


def test_world_numbers_integrated_summary_shape() -> None:
    """Smoke: _summarise_integrated runs with 1-seed ensemble.

    We use 1 seed × default 90 days to keep the smoke under 3 s while still
    exercising the full integrated pipeline.
    """
    _register()
    from scripts.world_numbers import _summarise_integrated

    result = _summarise_integrated(
        ["peter", "judas", "caiaphas", "crowd"],
        n_seeds=1, label="smoke_full",
    )
    assert result["label"] == "smoke_full"
    assert result["n_seeds"] == 1
    assert len(result["per_seed"]) == 1

    seed_row = result["per_seed"][0]
    assert seed_row["n_days"] == 90
    assert 0.0 <= seed_row["peter_final_fear"] <= 10.0
    assert seed_row["total_triggers"] >= 0
    assert seed_row["total_hazard_events"] >= 0
    assert 0 <= seed_row["days_with_effect"] <= 90

    agg = result["aggregate"]
    assert {
        "peter_fear_mean", "trigger_count_mean",
        "hazard_count_mean", "effect_days_mean",
        # Phase 3C rumour metrics (loop #14).
        "rumors_seeded_mean", "rumor_intensity_max_mean",
        # Phase 3D faction influence metrics (loop #16).
        "jesus_movement_final_influence_mean",
        "pharisees_final_influence_mean",
    } <= set(agg)


def test_phase_3d_judas_removal_collapses_jesus_movement_influence() -> None:
    """Phase 3D counterfactual chain — the full Spike 3 finding in one pin.

    Chain: Judas → rumour_seed → rumours.active_intensity → jesus_movement.

    Empirical baseline (2026-04-21, seed 0-2, 90 days, current AD-30 config):
        full 4 agents:    jesus_movement ≈ 9.90,  pharisees ≈ 6.18
        judas removed:    jesus_movement ≈ 3.80,  pharisees ≈ 6.18

    Guardrails:
    - Full-agent jesus_movement must rise materially above target (3.0).
    - Removing Judas must cut jesus_movement influence by ≥ 40% because
      the rumour pipeline collapses.
    - Pharisees (control, not rumour-sensitive) must stay within a narrow
      range across both conditions — the effect is specific, not global noise.
    """
    from scripts.world_numbers import _summarise_integrated

    full = _summarise_integrated(
        ["peter", "judas", "caiaphas", "crowd"],
        n_seeds=2, label="full_agents_3d_pin",
    )
    no_judas = _summarise_integrated(
        ["peter", "caiaphas", "crowd"],
        n_seeds=2, label="judas_removed_3d_pin",
    )
    full_jm = full["aggregate"]["jesus_movement_final_influence_mean"]
    nj_jm = no_judas["aggregate"]["jesus_movement_final_influence_mean"]
    full_phar = full["aggregate"]["pharisees_final_influence_mean"]
    nj_phar = no_judas["aggregate"]["pharisees_final_influence_mean"]

    assert full_jm is not None and nj_jm is not None
    assert full_jm > 5.0, (
        f"jesus_movement only reached {full_jm:.2f} with all 4 agents; "
        f"rumour pipeline is not firing."
    )
    drop = (full_jm - nj_jm) / full_jm
    assert drop >= 0.40, (
        f"Judas removal dropped jesus_movement by only {drop:.1%} "
        f"({full_jm:.2f} -> {nj_jm:.2f}). Expected ≥40% — the "
        f"Phase 3D chain Judas→rumour→jesus_movement is weakened."
    )
    # Pharisees control: both runs should be close (within 20%).
    assert full_phar is not None and nj_phar is not None
    assert abs(full_phar - nj_phar) / max(full_phar, nj_phar) < 0.2, (
        f"Pharisees control moved {full_phar:.2f} vs {nj_phar:.2f} — "
        f"Judas removal should NOT change a non-rumour-sensitive faction."
    )


# --------------------------------------------------------------------------
# world_figures.py


@pytest.fixture()
def numbers_file(tmp_path) -> Path:
    """Synthetic world_numbers.json for figure rendering smoke."""
    data = {
        "schema_version": 1,
        "spike1_world_only": {
            "n_seeds": 3,
            "n_days": 90,
            "per_seed": [
                {
                    "seed": i,
                    "max_crowd": 10.0,
                    "max_overflow": 2.0,
                    "max_price": 3.5 + i * 0.1,
                    "max_alert": 10.0,
                    "passover_crowd": 10.0,
                    "shavuot_crowd": 4.5,
                    "day_30_crowd": 1.2,
                    "runaway_ceiling_hits": 5,
                }
                for i in range(3)
            ],
            "aggregate": {
                "max_crowd_mean": 10.0,
                "max_price_mean": 3.6,
                "max_alert_mean": 10.0,
                "passover_crowd_mean": 10.0,
                "shavuot_crowd_mean": 4.5,
            },
        },
        "spike2_integrated_peter": {
            "label": "full_agents",
            "n_seeds": 3,
            "per_seed": [
                {"total_triggers": 200 + i, "total_hazard_events": 75,
                 "peter_final_fear": 9.8, "days_with_effect": 90,
                 "seed": i, "n_days": 90,
                 "peter_final_hope": 9.0, "judas_final_disillusionment": 10.0}
                for i in range(3)
            ],
            "aggregate": {
                "peter_fear_mean": 9.8,
                "trigger_count_mean": 201.0,
                "hazard_count_mean": 75.0,
                "effect_days_mean": 90.0,
            },
        },
        "spike2_judas_removed": {
            "label": "judas_removed",
            "n_seeds": 3,
            "per_seed": [
                {"total_triggers": 78 + i, "total_hazard_events": 72,
                 "peter_final_fear": 9.4, "days_with_effect": 90,
                 "seed": i, "n_days": 90,
                 "peter_final_hope": 9.1, "judas_final_disillusionment": None}
                for i in range(3)
            ],
            "aggregate": {
                "peter_fear_mean": 9.4,
                "trigger_count_mean": 79.0,
                "hazard_count_mean": 72.0,
                "effect_days_mean": 90.0,
            },
        },
    }
    path = tmp_path / "world_numbers.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_world_figures_renders_both_pngs(
    numbers_file, tmp_path, monkeypatch,
) -> None:
    """Run the two figure builders against a synthetic data file and
    verify they write PNGs without crashing."""
    from scripts import world_figures as wf

    monkeypatch.setattr(wf, "SRC", numbers_file)
    monkeypatch.setattr(wf, "OUT_DIR", tmp_path)

    wf.main()

    assert (tmp_path / "fig_spike1_world_peaks.png").exists()
    assert (tmp_path / "fig_spike2_counterfactual.png").exists()
    # Sanity: non-trivial size (>5 KB means matplotlib actually drew).
    for name in ("fig_spike1_world_peaks.png", "fig_spike2_counterfactual.png"):
        assert (tmp_path / name).stat().st_size > 5 * 1024
