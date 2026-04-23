"""Generate paper figures into docs/person/paper_data/*.png (PROJECT_DIRECTION_v2.md §6 — task 2).

Single-command entry point:
    python scripts/paper_figures.py

Figures:
- fig_peter_standalone_trajectory.png — Peter 50일 fear/hope/awe/grief trajectory (ensemble ±band)
- fig_pom_cross_scenario_heatmap.png — Talleyrand vs Peter scorecard pattern-by-pattern pass heatmap
- fig_stage2_feasibility_spectrum.png — logit acc vs majority, separability bar chart (Peter/VG/Talleyrand)
- fig_drive_tsne_peter.png — Peter drive samples 2D t-SNE (action class 색상)

기존 코드 수정 금지. matplotlib + sklearn만 사용.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.talleyrand.domain_diplomacy import DiplomacyState
from content.talleyrand.pom_scorecard import make_talleyrand_scorecard
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
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
from engine.simulation.pom import evaluate_pom
from engine.simulation.training_samples import state_to_feature_vector
from engine.simulation.world import SimulationWorld

CONTENT = ROOT / "content"
OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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


def _emotion_rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _run_peter_standalone(seed: int, max_tick: int = 300):
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    profiles = {
        n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
        for n in ["peter", "judas", "caiaphas", "crowd"]
    }
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )
    return SimulationWorld(
        config, _emotion_rules(), behavior_profiles=profiles,
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


def fig_peter_trajectory(n_seeds: int = 15) -> None:
    print("[fig] peter trajectory ensemble ...")
    axes_fields = ["fear", "hope", "grief", "awe"]
    # 수집: tick-indexed emotion values per seed
    by_tick: dict[int, dict[str, list[float]]] = {}
    for seed in range(n_seeds):
        r = _run_peter_standalone(seed)
        snaps = r.state_snapshots.get("peter", {})
        for tick, state in snaps.items():
            if tick > 300:
                continue
            by_tick.setdefault(tick, {f: [] for f in axes_fields})
            for f in axes_fields:
                by_tick[tick][f].append(float(getattr(state.emotions, f)))

    ticks = sorted(by_tick.keys())
    means = {f: [] for f in axes_fields}
    lows = {f: [] for f in axes_fields}
    highs = {f: [] for f in axes_fields}
    for t in ticks:
        for f in axes_fields:
            vals = by_tick[t][f]
            if not vals:
                means[f].append(np.nan)
                lows[f].append(np.nan)
                highs[f].append(np.nan)
                continue
            arr = np.array(vals)
            means[f].append(float(arr.mean()))
            lows[f].append(float(np.percentile(arr, 25)))
            highs[f].append(float(np.percentile(arr, 75)))

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = {"fear": "#d62728", "hope": "#2ca02c", "grief": "#9467bd", "awe": "#ff7f0e"}
    for f in axes_fields:
        ax.plot(ticks, means[f], color=colors[f], label=f, linewidth=1.5)
        ax.fill_between(ticks, lows[f], highs[f], color=colors[f], alpha=0.15)

    # arrest tick annotation
    ax.axvspan(119, 125, color="gray", alpha=0.2, label="arrest window")
    ax.set_xlabel("tick (1 tick ≈ 2 hours)")
    ax.set_ylabel("emotion (0-10)")
    ax.set_title(f"Peter ensemble emotion trajectory (n={n_seeds} seeds, IQR band)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    dest = OUT_DIR / "fig_peter_standalone_trajectory.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  → {dest}")


def fig_pom_cross_asymmetry(n_seeds: int = 10) -> None:
    """Talleyrand scorecard 패턴별 pass rate: Talleyrand runs vs Peter runs."""
    print("[fig] POM cross-scenario asymmetry heatmap ...")
    scorecard = make_talleyrand_scorecard()
    pattern_names = [p.name for p in scorecard]

    def _per_pattern_rate(runs):
        counts = {name: 0 for name in pattern_names}
        for r in runs:
            try:
                ev = evaluate_pom(r, scorecard)
                for name, passed in ev.items():
                    if passed:
                        counts[name] += 1
            except Exception:
                pass
        return [counts[n] / len(runs) for n in pattern_names]

    t_runs = [_run_talleyrand(s) for s in range(n_seeds)]
    p_runs = [_run_peter_standalone(s) for s in range(n_seeds)]

    t_rates = _per_pattern_rate(t_runs)
    p_rates = _per_pattern_rate(p_runs)

    data = np.array([t_rates, p_rates])

    fig, ax = plt.subplots(figsize=(10, 3.5))
    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["on Talleyrand runs", "on Peter runs"])
    ax.set_xticks(range(len(pattern_names)))
    ax.set_xticklabels(
        [n.replace("_", "\n") for n in pattern_names],
        rotation=0, fontsize=8,
    )
    ax.set_title(
        f"Talleyrand POM scorecard pass rate — scenario asymmetry (n={n_seeds})",
    )
    for i in range(2):
        for j in range(len(pattern_names)):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=9)
    plt.colorbar(im, ax=ax, label="pass rate")
    fig.tight_layout()
    dest = OUT_DIR / "fig_pom_cross_scenario_heatmap.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  → {dest}")


def fig_stage2_spectrum() -> None:
    """Peter / VG / Talleyrand logit acc vs majority + random separability bar chart."""
    print("[fig] Stage 2 feasibility spectrum ...")
    import json
    data_path = OUT_DIR / "paper_numbers.json"
    if not data_path.exists():
        print(f"  paper_numbers.json 없음 → paper_numbers.py 먼저 실행")
        return
    data = json.loads(data_path.read_text(encoding="utf-8"))
    peter = data["separability_spectrum"]["peter"]
    vg = data["separability_spectrum"]["vangogh"]
    tall = data["talleyrand_pom_and_stage2"]

    scenarios = ["Van Gogh", "Peter", "Talleyrand"]
    majority = [vg["majority"], peter["majority"], tall["stage2_majority_baseline"]]
    logit = [
        vg["logit_test_acc"], peter["logit_test_acc"], tall["stage2_logit_test_acc"],
    ]
    sep_rand = [
        vg["separability_random_projection"],
        peter["separability_random_projection"],
        tall["stage2_separability_random_projection"],
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    x = np.arange(len(scenarios))
    width = 0.35
    ax1.bar(x - width / 2, majority, width, label="majority baseline", color="#888888")
    ax1.bar(x + width / 2, logit, width, label="logit test acc", color="#1f77b4")
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios)
    ax1.set_ylabel("accuracy")
    ax1.set_title("Action prediction: logit vs majority")
    ax1.set_ylim(0, 1.0)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    for i, (m, lo) in enumerate(zip(majority, logit)):
        ax1.text(i - width / 2, m + 0.02, f"{m:.2f}", ha="center", fontsize=8)
        ax1.text(i + width / 2, lo + 0.02, f"{lo:.2f}", ha="center", fontsize=8)

    bars2 = ax2.bar(scenarios, sep_rand, color=["#2ca02c", "#1f77b4", "#d62728"])
    ax2.set_ylabel("Fisher ratio (random projection)")
    ax2.set_title("Drive class separability")
    ax2.axhline(0.5, color="gray", linestyle="--", alpha=0.5,
                label="feasibility threshold (0.5)")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)
    for bar, v in zip(bars2, sep_rand):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.1,
                 f"{v:.2f}", ha="center", fontsize=9)

    fig.tight_layout()
    dest = OUT_DIR / "fig_stage2_feasibility_spectrum.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  → {dest}")


def fig_drive_tsne_peter(n_seeds: int = 8) -> None:
    """Peter drive samples 2D t-SNE, action class 색상."""
    print("[fig] Peter drive t-SNE ...")
    results = collect_trajectories(
        lambda s: _run_peter_standalone(s), n_runs=n_seeds,
    )
    samples = [s for s in trajectories_to_samples(results) if s.action is not None]
    cnt = Counter(s.action for s in samples)
    keep = {a for a, n in cnt.items() if n >= 5}
    samples = [s for s in samples if s.action in keep]
    if len(samples) < 30:
        print(f"  sample 부족 ({len(samples)}) → skip")
        return
    # top-8 action classes만
    top8 = [a for a, _ in cnt.most_common(8) if a in keep]
    samples = [s for s in samples if s.action in top8]

    X = np.array([state_to_feature_vector(s.state) for s in samples])
    y = [s.action for s in samples]

    perplexity = min(30, max(5, len(samples) // 5))
    tsne = TSNE(
        n_components=2, perplexity=perplexity, random_state=0, init="pca",
    )
    Z = tsne.fit_transform(X)

    fig, ax = plt.subplots(figsize=(9, 7))
    cmap = plt.get_cmap("tab10")
    for i, action in enumerate(top8):
        mask = np.array([a == action for a in y])
        ax.scatter(
            Z[mask, 0], Z[mask, 1], s=14, alpha=0.6,
            color=cmap(i), label=f"{action} (n={int(mask.sum())})",
        )
    ax.set_title(
        f"Peter state → 2D (t-SNE, perplexity={perplexity}, n={len(samples)})",
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(fontsize=7, loc="best", framealpha=0.9)
    fig.tight_layout()
    dest = OUT_DIR / "fig_drive_tsne_peter.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  → {dest}")


def main() -> None:
    fig_peter_trajectory()
    fig_pom_cross_asymmetry()
    fig_stage2_spectrum()
    fig_drive_tsne_peter()
    print(f"[done] figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
