"""Baseline comparison + Ablation hierarchy (baseline_experiment_prompt.md).

실행:
    python scripts/baseline_comparison.py

산출물:
    docs/person/paper_data/baseline_comparison.json
    docs/person/paper_data/baseline_comparison.txt

원칙:
- engine/ 수정 금지
- content/ 수정 금지
- behavior_profile은 메모리에서 deepcopy 후 변경
- 모든 baseline은 Peter standalone (50-day passion) 10 seed × 300 tick
"""

from __future__ import annotations

import copy
import json
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.peter.pom_scorecard import make_peter_scorecard
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
from engine.rules.slow_recovery import SlowStateFieldRecoveryRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.pom import evaluate_pom
from engine.simulation.world import SimulationWorld

CONTENT = ROOT / "content"
OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

for _name, _cls in [
    ("faith_journey", FaithJourneyState),
    ("betrayal_psychology", BetrayalPsychologyState),
    ("political_calculation", PoliticalCalculationState),
    ("crowd_dynamics", CrowdDynamicsState),
]:
    register_domain_type(_name, _cls)

N_SEEDS = 10
MAX_TICK = 300


# --------------------------------------------------------------------------
# 공통 helpers
# --------------------------------------------------------------------------


def _rules(with_slow_recovery: bool = False) -> RuleEngine:
    rules = [
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ]
    if with_slow_recovery:
        rules.append(SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.002,
            trust_scar_rate_per_hour=0.001,
        ))
    return RuleEngine(rules)


def _load_base():
    return {
        "peter": load_agent_state(CONTENT / "peter" / "initial_state.json"),
        "judas": load_agent_state(CONTENT / "judas" / "initial_state.json"),
        "caiaphas": load_agent_state(CONTENT / "caiaphas" / "initial_state.json"),
        "crowd": load_agent_state(CONTENT / "crowd" / "initial_state.json"),
        "events": load_events(CONTENT / "peter" / "canonical_events.json"),
        "triggers": load_triggers(CONTENT / "shared" / "triggers.json"),
        "hazards": load_hazard_events(CONTENT / "peter" / "hazard_events.json"),
        "profiles": {
            n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
            for n in ["peter", "judas", "caiaphas", "crowd"]
        },
    }


def _randomize_profile(profile: Any) -> Any:
    """behavior_profile deep-copy 후 모든 action을 base_weight=1, multipliers=[] 로.

    file 수정 금지 — 메모리 내에서만.
    """
    p = copy.deepcopy(profile)
    for action in p.actions:
        wf = action.weight_formula
        wf.base_weight = 1.0
        wf.state_multipliers = []
    return p


def _run_config(
    base: dict,
    *,
    triggers: Any,
    hazards: Any,
    events: Any,
    profiles: dict,
    agents: list[str],
    rules_engine: RuleEngine,
    seed: int,
) -> Any:
    agent_states = [base[a] for a in agents]
    config = SimulationConfig(
        initial_state=agent_states[0],
        initial_states=agent_states,
        max_tick=MAX_TICK, state_noise_scale=0.02,
        events=events if events else [],
        triggers=triggers if triggers else [],
        hazard_events=hazards if hazards else [],
    )
    return SimulationWorld(
        config, rules_engine,
        behavior_profiles={n: profiles[n] for n in agents if n in profiles},
    ).run(seed=seed)


# --------------------------------------------------------------------------
# 측정 함수들
# --------------------------------------------------------------------------


def _arrest_tick(result) -> int | None:
    """arrest 관련 event 발생 tick (canonical scene_08_arrest 또는 hazard arrest)."""
    for ev in getattr(result, "fired_events", []):
        eid = str(ev.get("event_id", ""))
        if "arrest" in eid.lower():
            return int(ev.get("tick", -1))
    return None


def _causal_chain_observed(result) -> bool:
    """inform → surveillance → betray → arrest 인과 체인 관측 여부.

    증거 수준 (각각 tick-ordered로 수집):
    1. inform:       Caiaphas action "inform_authorities" 또는 event_id "inform"
    2. surveillance: Caiaphas action "order_surveillance" 또는 trigger "surveillance"
    3. betray:       Judas action "betray" (또는 "conspire" 등)
    4. arrest:       event_id "arrest" 또는 trigger "arrest"

    순서대로 만나면 chain observed.
    """
    keywords = ["inform", "surveillance", "betray", "arrest"]
    timeline: list[tuple[int, str]] = []

    # fired_events
    for e in getattr(result, "fired_events", []):
        eid = str(e.get("event_id", "")).lower()
        t = int(e.get("tick", 0))
        timeline.append((t, eid))

    # fired_triggers
    for t in getattr(result, "fired_triggers", []):
        tid = str(t.get("trigger_id", "")).lower()
        tick = int(t.get("tick", 0))
        timeline.append((tick, tid))

    # action_histories
    action_histories = getattr(result, "action_histories", {})
    for aid, history in action_histories.items():
        for a in history:
            action_id = str(getattr(a, "chosen_action", "")).lower()
            tick = int(getattr(a, "tick", 0))
            # agent_id를 label에 포함해서 의미 보존
            timeline.append((tick, f"{aid}:{action_id}"))

    timeline.sort(key=lambda x: x[0])

    idx = 0
    for _tick, label in timeline:
        if keywords[idx] in label:
            idx += 1
            if idx == len(keywords):
                return True
    return False


def _multiagent_to_peter_sim_result(result) -> Any:
    """Peter POM scorecard는 단일 agent SimulationResult 기대. adapter.

    SimulationResult 최소 필드: action_history, state_snapshots, final_state, fired_events.
    """
    # action_history: Peter 것만 추출
    all_action_histories = getattr(result, "action_histories", {})
    peter_actions = all_action_histories.get("peter", [])

    # state_snapshots: Peter 것만 추출 (dict[tick -> state])
    all_snaps = getattr(result, "state_snapshots", {})
    peter_snaps = all_snaps.get("peter", {}) if isinstance(all_snaps, dict) else {}

    # final_state: Peter
    peter_final = getattr(result, "final_states", {}).get("peter")
    if peter_final is None:
        # fallback: last snapshot
        if peter_snaps:
            peter_final = peter_snaps[max(peter_snaps.keys())]

    return SimpleNamespace(
        action_history=peter_actions,
        state_snapshots=peter_snaps,
        final_state=peter_final,
        fired_events=getattr(result, "fired_events", []),
    )


def _pom_all_pass(result) -> bool:
    adapter = _multiagent_to_peter_sim_result(result)
    if adapter.final_state is None:
        return False
    try:
        ev = evaluate_pom(adapter, make_peter_scorecard())
        return all(ev.values())
    except Exception:
        return False


def _measure_condition(runs: list[Any]) -> dict[str, Any]:
    """공통 측정: arrest rate / tick mean / causal chain / POM / emotions."""
    arrest_ticks: list[int] = []
    chain_hits = 0
    pom_passes = 0
    final_fears: list[float] = []
    final_hopes: list[float] = []
    for r in runs:
        at = _arrest_tick(r)
        if at is not None and at > 0:
            arrest_ticks.append(at)
        if _causal_chain_observed(r):
            chain_hits += 1
        if _pom_all_pass(r):
            pom_passes += 1
        peter_state = getattr(r, "final_states", {}).get("peter")
        if peter_state is not None:
            final_fears.append(float(peter_state.emotions.fear))
            final_hopes.append(float(peter_state.emotions.hope))

    n = len(runs)
    return {
        "n_runs": n,
        "arrest_rate": len(arrest_ticks) / n if n else 0.0,
        "arrest_tick_mean": (
            round(statistics.mean(arrest_ticks), 2) if arrest_ticks else None
        ),
        "arrest_tick_stdev": (
            round(statistics.stdev(arrest_ticks), 2)
            if len(arrest_ticks) >= 2 else None
        ),
        "causal_chain_rate": chain_hits / n if n else 0.0,
        "pom_all_pass_rate": pom_passes / n if n else 0.0,
        "final_fear_mean": (
            round(statistics.mean(final_fears), 3) if final_fears else None
        ),
        "final_hope_mean": (
            round(statistics.mean(final_hopes), 3) if final_hopes else None
        ),
    }


# --------------------------------------------------------------------------
# Baseline 4종 + Full System
# --------------------------------------------------------------------------


def baseline_no_trigger(base: dict) -> dict[str, Any]:
    print("[baseline] no_trigger ...")
    runs = [
        _run_config(
            base, triggers=[], hazards=base["hazards"], events=base["events"],
            profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def baseline_exogenous_only(base: dict) -> dict[str, Any]:
    print("[baseline] exogenous_only ...")
    runs = [
        _run_config(
            base, triggers=[], hazards=[], events=base["events"],
            profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def baseline_single_agent(base: dict) -> dict[str, Any]:
    print("[baseline] single_agent ...")
    runs = [
        _run_config(
            base, triggers=[], hazards=base["hazards"], events=base["events"],
            profiles={"peter": base["profiles"]["peter"]},
            agents=["peter"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def baseline_random_behavior(base: dict) -> dict[str, Any]:
    print("[baseline] random_behavior ...")
    randomized = {
        n: _randomize_profile(p) for n, p in base["profiles"].items()
    }
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=randomized,
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def full_system(base: dict) -> dict[str, Any]:
    print("[baseline] full_system ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


# --------------------------------------------------------------------------
# Ablation hierarchy 5 levels
# --------------------------------------------------------------------------


def ablation_level_0(base: dict) -> dict[str, Any]:
    """Hazard only. single agent peter."""
    print("[ablation] level_0_hazard_only ...")
    runs = [
        _run_config(
            base, triggers=[], hazards=base["hazards"], events=[],
            profiles={"peter": base["profiles"]["peter"]},
            agents=["peter"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def ablation_level_1(base: dict) -> dict[str, Any]:
    """Hazard + Trigger. single agent."""
    print("[ablation] level_1_hazard_trigger ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=[], profiles={"peter": base["profiles"]["peter"]},
            agents=["peter"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def ablation_level_2(base: dict) -> dict[str, Any]:
    """Hazard + Trigger + Multi-Agent. no canonical events."""
    print("[ablation] level_2_multi_agent ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=[], profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def ablation_level_3(base: dict) -> dict[str, Any]:
    """Hazard + Trigger + Multi-Agent + Canonical Events. basic rules."""
    print("[ablation] level_3_with_canonical ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(with_slow_recovery=False), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


def ablation_level_4(base: dict) -> dict[str, Any]:
    """Full System: Level 3 + SlowStateFieldRecoveryRule opt-in."""
    print("[ablation] level_4_full_system ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=base["profiles"],
            agents=["peter", "judas", "caiaphas", "crowd"],
            rules_engine=_rules(with_slow_recovery=True), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_condition(runs)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def _fmt_cell(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _write_text_summary(out: dict) -> None:
    lines = []
    lines.append("Witness baseline comparison + ablation hierarchy")
    lines.append(f"(n_seeds={out['n_seeds']}, max_tick={out['max_tick']})")
    lines.append("=" * 78)
    lines.append("")

    header = f"{'condition':<26} {'arrest':>8} {'chain':>8} {'POM':>8} {'fear':>8} {'hope':>8}"
    lines.append(header)
    lines.append("-" * len(header))

    lines.append("[BASELINES vs FULL]")
    order = [
        "no_trigger", "exogenous_only", "single_agent",
        "random_behavior", "full_system",
    ]
    for k in order:
        d = out["baselines"][k]
        lines.append(
            f"{k:<26} "
            f"{_fmt_cell(d['arrest_rate']):>8} "
            f"{_fmt_cell(d['causal_chain_rate']):>8} "
            f"{_fmt_cell(d['pom_all_pass_rate']):>8} "
            f"{_fmt_cell(d['final_fear_mean']):>8} "
            f"{_fmt_cell(d['final_hope_mean']):>8}"
        )

    lines.append("")
    lines.append("[ABLATION HIERARCHY]")
    lines.append("-" * len(header))
    abl_order = [
        "level_0_hazard_only",
        "level_1_hazard_trigger",
        "level_2_multi_agent",
        "level_3_with_canonical",
        "level_4_full_system",
    ]
    for k in abl_order:
        d = out["ablation"][k]
        lines.append(
            f"{k:<26} "
            f"{_fmt_cell(d['arrest_rate']):>8} "
            f"{_fmt_cell(d['causal_chain_rate']):>8} "
            f"{_fmt_cell(d['pom_all_pass_rate']):>8} "
            f"{_fmt_cell(d['final_fear_mean']):>8} "
            f"{_fmt_cell(d['final_hope_mean']):>8}"
        )

    # verdict
    lines.append("")
    lines.append("=" * 78)
    full = out["baselines"]["full_system"]
    verdict_parts = []
    for k in ["no_trigger", "exogenous_only", "single_agent", "random_behavior"]:
        b = out["baselines"][k]
        arrest_better = full["arrest_rate"] >= b["arrest_rate"]
        chain_better = full["causal_chain_rate"] >= b["causal_chain_rate"]
        pom_better = full["pom_all_pass_rate"] >= b["pom_all_pass_rate"]
        all_three = arrest_better and chain_better and pom_better
        verdict_parts.append(
            f"  Full > {k}: arrest={arrest_better}, chain={chain_better}, "
            f"POM={pom_better}  [{'PASS' if all_three else 'MIXED'}]"
        )
    lines.append("VERDICT (Full System vs each baseline, 3 metrics):")
    lines.extend(verdict_parts)
    lines.append("")

    (OUT_DIR / "baseline_comparison.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8",
    )
    for line in lines:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    t0 = time.time()
    base = _load_base()

    out: dict[str, Any] = {
        "schema_version": 1,
        "n_seeds": N_SEEDS,
        "max_tick": MAX_TICK,
        "generated_at_seconds": time.time(),
        "notes": (
            "Baselines: Peter standalone (4 agent, 50-day passion scenario, "
            "10 seeds × 300 tick). Each baseline degrades ONE aspect from full "
            "system. Ablation hierarchy: incremental feature addition from "
            "hazard-only single-agent to full system."
        ),
    }

    out["baselines"] = {
        "no_trigger": baseline_no_trigger(base),
        "exogenous_only": baseline_exogenous_only(base),
        "single_agent": baseline_single_agent(base),
        "random_behavior": baseline_random_behavior(base),
        "full_system": full_system(base),
    }
    out["ablation"] = {
        "level_0_hazard_only": ablation_level_0(base),
        "level_1_hazard_trigger": ablation_level_1(base),
        "level_2_multi_agent": ablation_level_2(base),
        "level_3_with_canonical": ablation_level_3(base),
        "level_4_full_system": ablation_level_4(base),
    }

    out["total_runtime_seconds"] = round(time.time() - t0, 2)
    dest = OUT_DIR / "baseline_comparison.json"
    dest.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print()
    _write_text_summary(out)
    print(f"[done] wrote {dest} (total {out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
