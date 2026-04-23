"""Extract all paper-relevant numbers into docs/person/paper_data/*.json (PROJECT_DIRECTION_v2.md §6 — task 1).

Single-command entry point:
    python scripts/paper_numbers.py

Sections:
- peter_standalone: v0.7 legacy-mode (phases=None) arrest dynamics, Cohen's d
- peter_phased: 5-phase linked-life summary
- vangogh: 주요 수치
- talleyrand: POM scorecard + Stage 2 실패 수치
- cross_scenario: POM asymmetry
- separability: Peter LDA vs random, VG random
- benchmark: runtime + tick throughput

Output: docs/person/paper_data/paper_numbers.json  (+ sub-indices if volume grows)

기존 코드 수정 금지 — 이 스크립트는 public API만 사용한다.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

# Project root to sys.path for direct invocation
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis  # noqa: F401 (sanity)

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.talleyrand.domain_diplomacy import DiplomacyState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.latent_drive import FixedProjectionEncoder, LearnedLinearEncoder
from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.physical import FatigueRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.drive_training import (
    collect_trajectories,
    trajectories_to_samples,
)
from engine.simulation.phased_world import PhasedSimulationWorld
from engine.simulation.pom import evaluate_pom
from engine.simulation.training_samples import (
    compute_drive_action_diagnostics,
    drive_class_separability,
    state_to_feature_vector,
)
from engine.simulation.world import SimulationWorld

CONTENT = ROOT / "content"
OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------
# domain registration
# --------------------------------------------------------------------------

for _name, _cls in [
    ("faith_journey", FaithJourneyState),
    ("betrayal_psychology", BetrayalPsychologyState),
    ("political_calculation", PoliticalCalculationState),
    ("crowd_dynamics", CrowdDynamicsState),
    ("creative_drive", CreativeDriveState),
    ("artistic_ego", ArtisticEgoState),
    ("patron", PatronState),
    ("diplomacy", DiplomacyState),
]:
    register_domain_type(_name, _cls)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _emotion_rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _peter_profiles():
    return {
        n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
        for n in ["peter", "judas", "caiaphas", "crowd"]
    }


def _vg_profiles():
    return {
        n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
        for n in ["vangogh", "gauguin", "theo"]
    }


def _run_peter_standalone(seed: int, max_tick: int = 500):
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )
    return SimulationWorld(
        config, _emotion_rules(), behavior_profiles=_peter_profiles(),
    ).run(seed=seed)


def _run_peter_phased(seed: int) -> Any:
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    handoff = PhaseHandoffSpec(mappings=[
        FieldMapping("peter", f, "peter", f)
        for f in [
            "domain_state.obedience_maturity",
            "domain_state.jesus_understanding",
            "emotions.awe", "emotions.hope", "emotions.fear",
            "emotions.grief", "emotions.confusion", "emotions.love",
        ]
    ])
    phases = [
        Phase(
            phase_id="01_calling", agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            canonical_events_path=str(CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json"),
            handoff_to_next=handoff,
        ),
        Phase(
            phase_id="02_galilean", agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=60),
            canonical_events_path=str(CONTENT / "peter" / "phases" / "02_galilean" / "canonical_events.json"),
            handoff_to_next=handoff,
        ),
        Phase(
            phase_id="03_confession", agents_active=["peter", "judas"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=50),
            canonical_events_path=str(CONTENT / "peter" / "phases" / "03_confession" / "canonical_events.json"),
            handoff_to_next=handoff,
        ),
        Phase(
            phase_id="04_journey", agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=30),
            canonical_events_path=str(CONTENT / "peter" / "phases" / "04_journey_to_jerusalem" / "canonical_events.json"),
        ),
    ]
    config = SimulationConfig(
        initial_state=peter, initial_states=[peter, judas],
        max_tick=5000, state_noise_scale=0.02, phases=phases,
    )
    return PhasedSimulationWorld(config, _emotion_rules()).run(seed=seed)


def _run_vg(seed: int, max_tick: int = 150):
    vg = load_agent_state(CONTENT / "vangogh" / "initial_state.json")
    gauguin = load_agent_state(CONTENT / "gauguin" / "initial_state.json")
    theo = load_agent_state(CONTENT / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "vangogh" / "hazard_events.json")
    config = SimulationConfig(
        max_tick=max_tick, initial_state=vg,
        initial_states=[vg, gauguin, theo],
        triggers=triggers, hazard_events=hazards,
        state_noise_scale=0.05,
    )
    return SimulationWorld(
        config, _emotion_rules(), behavior_profiles=_vg_profiles(),
    ).run(seed=seed)


def _run_talleyrand(seed: int, max_tick: int = 500):
    t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
    events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
    profile = load_behavior_profile(CONTENT / "talleyrand" / "behavior_profile.json")
    config = SimulationConfig(
        initial_state=t, initial_states=[t],
        max_tick=max_tick, state_noise_scale=0.02, events=events,
    )
    rules = RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
        FatigueRule(), HomeostasisRule(),
    ])
    return SimulationWorld(
        config, rules, behavior_profiles={"talleyrand": profile},
    ).run(seed=seed)


def _arrest_tick(result) -> int | None:
    """'arrest' 관련 event 발생 tick."""
    for ev in getattr(result, "fired_events", []):
        eid = str(ev.get("event_id", ""))
        if "arrest" in eid:
            return int(ev.get("tick", -1))
    return None


# --------------------------------------------------------------------------
# section: peter_standalone (v0.7 legacy)
# --------------------------------------------------------------------------


def peter_standalone(n_seeds: int = 20) -> dict[str, Any]:
    print(f"[peter_standalone] {n_seeds} seeds × 500 tick ...")
    t0 = time.time()
    arrest_ticks: list[int] = []
    final_fears: list[float] = []
    for seed in range(n_seeds):
        r = _run_peter_standalone(seed)
        tick = _arrest_tick(r)
        if tick is not None:
            arrest_ticks.append(tick)
        final_fears.append(float(r.final_states["peter"].emotions.fear))
    dt = time.time() - t0
    arrest_rate = len(arrest_ticks) / n_seeds
    return {
        "n_seeds": n_seeds,
        "max_tick": 500,
        "arrest_rate": arrest_rate,
        "arrest_ticks": arrest_ticks,
        "arrest_tick_mean": statistics.mean(arrest_ticks) if arrest_ticks else None,
        "arrest_tick_stdev": (
            statistics.stdev(arrest_ticks) if len(arrest_ticks) >= 2 else None
        ),
        "arrest_tick_range": (
            [min(arrest_ticks), max(arrest_ticks)] if arrest_ticks else None
        ),
        "peter_final_fear_mean": statistics.mean(final_fears),
        "peter_final_fear_stdev": (
            statistics.stdev(final_fears) if len(final_fears) >= 2 else None
        ),
        "runtime_seconds": round(dt, 2),
    }


# --------------------------------------------------------------------------
# section: peter_phased
# --------------------------------------------------------------------------


def peter_phased(n_seeds: int = 10) -> dict[str, Any]:
    print(f"[peter_phased] {n_seeds} seeds × 4 phases ...")
    t0 = time.time()
    summaries: list[dict[str, Any]] = []
    for seed in range(n_seeds):
        r = _run_peter_phased(seed)
        phase_summary = {}
        for pid, phase_result in r.per_phase_results.items():
            state = phase_result.final_states["peter"]
            phase_summary[pid] = {
                "emotions_awe": round(float(state.emotions.awe), 3),
                "emotions_hope": round(float(state.emotions.hope), 3),
                "emotions_fear": round(float(state.emotions.fear), 3),
                "obedience_maturity": round(
                    float(state.domain_state.obedience_maturity), 3,
                ),
                "jesus_understanding": state.domain_state.jesus_understanding,
            }
        summaries.append({"seed": seed, "per_phase": phase_summary})
    dt = time.time() - t0
    return {
        "n_seeds": n_seeds,
        "phase_ids": ["01_calling", "02_galilean", "03_confession", "04_journey"],
        "tick_scales": [2.0, 24.0, 2.0, 24.0],
        "max_ticks_per_phase": [84, 60, 50, 30],
        "runtime_seconds": round(dt, 2),
        "samples": summaries[:3],  # 논문에서 대표 3개 seed만 표시
    }


# --------------------------------------------------------------------------
# section: vangogh
# --------------------------------------------------------------------------


def vangogh(n_seeds: int = 20) -> dict[str, Any]:
    print(f"[vangogh] {n_seeds} seeds × 150 tick ...")
    t0 = time.time()
    departures: list[int] = []
    final_fears: list[float] = []
    for seed in range(n_seeds):
        r = _run_vg(seed)
        for ev in getattr(r, "fired_events", []):
            eid = str(ev.get("event_id", ""))
            if "depart" in eid or "gauguin" in eid:
                departures.append(int(ev.get("tick", -1)))
                break
        final_fears.append(float(r.final_states["vangogh"].emotions.fear))
    dt = time.time() - t0
    return {
        "n_seeds": n_seeds,
        "max_tick": 150,
        "gauguin_departure_rate": len(departures) / n_seeds,
        "departure_tick_mean": (
            statistics.mean(departures) if departures else None
        ),
        "vangogh_final_fear_mean": statistics.mean(final_fears),
        "runtime_seconds": round(dt, 2),
    }


# --------------------------------------------------------------------------
# section: talleyrand (POM + Stage 2 실패 수치)
# --------------------------------------------------------------------------


def talleyrand_pom(n_seeds: int = 10) -> dict[str, Any]:
    from content.talleyrand.pom_scorecard import make_talleyrand_scorecard

    print(f"[talleyrand_pom] {n_seeds} seeds × 500 tick ...")
    t0 = time.time()
    scorecard = make_talleyrand_scorecard()
    results = [_run_talleyrand(s) for s in range(n_seeds)]
    pattern_passes = {p.name: 0 for p in scorecard}
    all_pass = 0
    for r in results:
        ev = evaluate_pom(r, scorecard)
        for name, passed in ev.items():
            if passed:
                pattern_passes[name] += 1
        if all(ev.values()):
            all_pass += 1

    # Stage 2 failure numbers
    samples = [s for s in trajectories_to_samples(results) if s.action is not None]
    cnt = Counter(s.action for s in samples)
    keep = {a for a, n in cnt.items() if n >= 3}
    samples = [s for s in samples if s.action in keep]
    X = np.array([state_to_feature_vector(s.state) for s in samples])
    y = np.array([s.action for s in samples])
    majority = max(set(y), key=list(y).count)
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y,
    )
    clf = LogisticRegression(max_iter=3000, C=1.0)
    clf.fit(Xtr, ytr)
    logit_acc = float(clf.score(Xte, yte))
    enc = FixedProjectionEncoder(dim=5, seed=0)
    sep = float(drive_class_separability(
        compute_drive_action_diagnostics(samples, enc),
    ))

    dt = time.time() - t0
    return {
        "n_seeds": n_seeds,
        "pattern_pass_counts": pattern_passes,
        "pattern_pass_rates": {
            name: count / n_seeds for name, count in pattern_passes.items()
        },
        "all_pass_count": all_pass,
        "all_pass_rate": all_pass / n_seeds,
        "stage2_action_classes_retained": sorted(keep),
        "stage2_action_class_counts": {
            a: int(c) for a, c in cnt.items() if a in keep
        },
        "stage2_majority_baseline": float(np.mean(y == majority)),
        "stage2_logit_test_acc": logit_acc,
        "stage2_separability_random_projection": sep,
        "stage2_verdict": "deferred (per PROJECT_DIRECTION_v2.md §2.3)",
        "runtime_seconds": round(dt, 2),
    }


# --------------------------------------------------------------------------
# section: cross_scenario (POM asymmetry)
# --------------------------------------------------------------------------


def cross_scenario_pom(n_seeds: int = 10) -> dict[str, Any]:
    from content.talleyrand.pom_scorecard import make_talleyrand_scorecard
    print(f"[cross_scenario_pom] {n_seeds} seeds × 2 scenarios ...")
    t0 = time.time()
    t_runs = [_run_talleyrand(s) for s in range(n_seeds)]
    p_runs = [_run_peter_standalone(s, max_tick=300) for s in range(n_seeds)]
    scorecard = make_talleyrand_scorecard()

    def _all_pass(runs):
        passed = 0
        for r in runs:
            try:
                ev = evaluate_pom(r, scorecard)
                if all(ev.values()):
                    passed += 1
            except Exception:
                pass
        return passed / len(runs)

    dt = time.time() - t0
    return {
        "n_seeds": n_seeds,
        "talleyrand_scorecard_on_talleyrand_runs": _all_pass(t_runs),
        "talleyrand_scorecard_on_peter_runs": _all_pass(p_runs),
        "asymmetry_gap": (
            _all_pass(t_runs) - _all_pass(p_runs)
        ),
        "runtime_seconds": round(dt, 2),
    }


# --------------------------------------------------------------------------
# section: separability (Peter LDA vs random, VG random)
# --------------------------------------------------------------------------


def separability_spectrum(n_seeds: int = 10) -> dict[str, Any]:
    print(f"[separability] Peter + VG, {n_seeds} seeds each ...")
    t0 = time.time()
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    def _measure(results, scenario_label):
        samples = [
            s for s in trajectories_to_samples(results) if s.action is not None
        ]
        cnt = Counter(s.action for s in samples)
        keep = {a for a, n in cnt.items() if n >= 3}
        samples = [s for s in samples if s.action in keep]
        if not samples:
            return None
        X = np.array([state_to_feature_vector(s.state) for s in samples])
        y = np.array([s.action for s in samples])
        majority = max(set(y), key=list(y).count)
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, test_size=0.3, random_state=0, stratify=y,
        )
        clf = LogisticRegression(max_iter=3000, C=1.0)
        clf.fit(Xtr, ytr)
        enc_fixed = FixedProjectionEncoder(dim=5, seed=0)
        sep_fixed = drive_class_separability(
            compute_drive_action_diagnostics(samples, enc_fixed),
        )
        # LDA (learned)
        enc_lda = LearnedLinearEncoder(dim=5)
        try:
            enc_lda.fit(samples)
            sep_lda = drive_class_separability(
                compute_drive_action_diagnostics(samples, enc_lda),
            )
        except Exception as e:
            sep_lda = None
            print(f"  [{scenario_label}] LDA fit failed: {e}")
        return {
            "scenario": scenario_label,
            "n_samples": len(samples),
            "n_action_classes": len(keep),
            "majority": float(np.mean(y == majority)),
            "logit_test_acc": float(clf.score(Xte, yte)),
            "separability_random_projection": float(sep_fixed),
            "separability_lda": float(sep_lda) if sep_lda is not None else None,
        }

    peter_runs = [_run_peter_standalone(s, max_tick=300) for s in range(n_seeds)]
    vg_runs = [_run_vg(s) for s in range(n_seeds)]

    dt = time.time() - t0
    return {
        "n_seeds": n_seeds,
        "peter": _measure(peter_runs, "peter"),
        "vangogh": _measure(vg_runs, "vangogh"),
        "runtime_seconds": round(dt, 2),
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def _merge_counterfactual(out: dict[str, Any]) -> None:
    src = OUT_DIR / "causal_counterfactual.json"
    if not src.exists():
        return
    d = json.loads(src.read_text(encoding="utf-8"))
    conds = d.get("conditions", {})
    verd = d.get("verdicts", {})

    def _cond(k: str) -> dict[str, float]:
        c = conds.get(k, {})
        return {
            "trigger_arrest": c.get("trigger_arrest_rate", 0.0),
            "chain": c.get("causal_chain_rate_gap_constrained", 0.0),
            "endogenous_arrest_v2": c.get("endogenous_arrest_rate", 0.0),
        }

    out["counterfactual_causal"] = {
        "n_seeds": d.get("n_seeds"),
        "max_tick": d.get("max_tick"),
        "chain_max_gap_tick": d.get("chain_max_gap_tick"),
        "source": "docs/person/paper_data/causal_counterfactual.json",
        "key_metrics_by_condition": {
            k: _cond(k) for k in (
                "full_system", "judas_removed", "caiaphas_removed",
                "trigger_removed", "random_no_judas",
            ) if k in conds
        },
        "verdicts": {
            "causal_dependency_v3": verd.get(
                "causal_dependency_v3", verd.get("causal_dependency"),
            ),
            "trigger_necessity": verd.get("trigger_necessity"),
            "random_chain_nature": verd.get("random_chain_nature"),
        },
        "interpretation": (
            "V2 endogenous_arrest saturates at 1.0 across all "
            "counterfactuals (canonical scene_08 + state-driven hazard "
            "ceiling). V3 trigger_arrest (arrest_trigger, requires Judas "
            "disillusion + Caiaphas threat + betray action) is the "
            "discriminative metric."
        ),
        "runtime_seconds": d.get("total_runtime_seconds"),
    }


def _merge_hazard_scaling(out: dict[str, Any]) -> None:
    src = OUT_DIR / "hazard_scaling.json"
    if not src.exists():
        return
    d = json.loads(src.read_text(encoding="utf-8"))
    factors = d.get("factors_applied", [])
    per = d.get("factors", {})
    pat = d.get("pattern_analysis", {})

    def _col(key: str) -> list[float]:
        return [per.get(f"{f:.2f}", {}).get(key, 0.0) or 0.0 for f in factors]

    out["hazard_scaling"] = {
        "n_seeds": d.get("n_seeds"),
        "max_tick": d.get("max_tick"),
        "chain_max_gap_tick": d.get("chain_max_gap_tick"),
        "source": "docs/person/paper_data/hazard_scaling.json",
        "factors": factors,
        "endogenous_arrest_by_factor": _col("endogenous_arrest_rate"),
        "chain_by_factor": _col("causal_chain_rate_gap_constrained"),
        "pom_all_pass_by_factor": _col("pom_all_pass_rate"),
        "pattern": pat.get("pattern"),
        "collapse_factor": pat.get("collapse_factor"),
        "interpretation": (
            "V2 endogenous_arrest hazard-insensitive due to canonical "
            "scene_08 ceiling. Chain rate shows emergence shape (peak at "
            "mid-factor, collapse at factor 0)."
        ),
        "runtime_seconds": d.get("total_runtime_seconds"),
    }


def main() -> None:
    overall_t0 = time.time()
    out: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_seconds": time.time(),
        "notes": (
            "Numbers extracted by scripts/paper_numbers.py per "
            "PROJECT_DIRECTION_v2.md §6. Legacy terminology: "
            "'standalone mode' = phases=None, 'phased mode' = phases=[01..]."
        ),
    }
    out["peter_standalone"] = peter_standalone()
    out["peter_phased"] = peter_phased()
    out["vangogh"] = vangogh()
    out["talleyrand_pom_and_stage2"] = talleyrand_pom()
    out["cross_scenario_pom"] = cross_scenario_pom()
    out["separability_spectrum"] = separability_spectrum()

    # Merge counterfactual/hazard_scaling summaries if their JSON exists.
    # These are produced by scripts/counterfactual_baseline.py and
    # scripts/hazard_scaling.py. Missing = skip (backward compat).
    _merge_counterfactual(out)
    _merge_hazard_scaling(out)

    out["total_runtime_seconds"] = round(time.time() - overall_t0, 2)

    dest = OUT_DIR / "paper_numbers.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[done] wrote {dest} (total {out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
