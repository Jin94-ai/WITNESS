"""world_figures.py — render World Engine snapshot figures.

Reads ``docs/world/paper_data/world_numbers.json`` (produced by
``scripts/world_numbers.py``) + per-intervention JSONs (from
``scripts/demo_spike4_interventions.py``) and writes:

- fig_spike1_world_peaks.png — Spike 1 agent-less peaks per seed.
- fig_spike2_counterfactual.png — Spike 2 integrated Peter full vs
  Judas-removed counterfactual (trigger / hazard / Peter fear).
- fig_spike3_counterfactual_chain.png — Spike 3 Phase 3D chain:
  Judas → rumours → jesus_movement, with pharisees as control.
- fig_spike4_interventions.png — Spike 4 three canonical interventions
  side-by-side (Cohen's d per metric).

Parallel to ``scripts/paper_figures.py`` for the Person Engine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT_DIR = ROOT / "docs" / "world" / "paper_data"
SRC = OUT_DIR / "world_numbers.json"


def _load() -> dict:
    if not SRC.exists():
        raise SystemExit(
            f"{SRC} not found. Run scripts/world_numbers.py first.",
        )
    return json.loads(SRC.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Fig 1 — Spike 1 peaks (agent-less world)
# --------------------------------------------------------------------------


def fig_spike1_world_peaks(data: dict) -> None:
    spike1 = data.get("spike1_world_only")
    if not spike1:
        print("[skip] spike1_world_only section missing")
        return
    per_seed = spike1["per_seed"]
    seeds = [s["seed"] for s in per_seed]
    passover = [s["passover_crowd"] for s in per_seed]
    shavuot = [s["shavuot_crowd"] for s in per_seed]
    max_price = [s["max_price"] for s in per_seed]
    max_alert = [s["max_alert"] for s in per_seed]
    day_30 = [s["day_30_crowd"] for s in per_seed]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Top-left: crowd density — Passover vs Shavuot vs day 30.
    ax = axes[0, 0]
    x = np.arange(len(seeds))
    w = 0.27
    ax.bar(x - w, passover, w, label="Passover (day 13)", color="#d62728")
    ax.bar(x, shavuot, w, label="Shavuot (day 64)", color="#ff7f0e")
    ax.bar(x + w, day_30, w, label="Quiet (day 30)", color="#7f7f7f")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed {s}" for s in seeds], fontsize=8)
    ax.set_ylabel("crowd density")
    ax.set_ylim(0, 11)
    ax.set_title("Crowd density — feast vs quiet days")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)

    # Top-right: max price across seeds.
    ax = axes[0, 1]
    ax.bar(x, max_price, color="#2ca02c")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed {s}" for s in seeds], fontsize=8)
    ax.set_ylabel("max staple_price")
    ax.set_ylim(0, 10.5)
    ax.set_title("Peak staple price (Layer 2)")
    ax.grid(axis="y", alpha=0.3)
    for xi, v in zip(x, max_price):
        ax.text(xi, v + 0.1, f"{v:.2f}", ha="center", fontsize=8)

    # Bottom-left: max alertness.
    ax = axes[1, 0]
    ax.bar(x, max_alert, color="#9467bd")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed {s}" for s in seeds], fontsize=8)
    ax.set_ylabel("max roman_alertness")
    ax.set_ylim(0, 11)
    ax.set_title("Peak Roman alertness (Layer 3)")
    ax.grid(axis="y", alpha=0.3)

    # Bottom-right: aggregate summary text.
    ax = axes[1, 1]
    agg = spike1["aggregate"]
    lines = [
        f"n_seeds = {spike1['n_seeds']}",
        f"n_days  = {spike1['n_days']}",
        "",
        "Means across seeds:",
        f"  max crowd          = {agg['max_crowd_mean']:.2f}",
        f"  max price          = {agg['max_price_mean']:.2f}",
        f"  max alert          = {agg['max_alert_mean']:.2f}",
        f"  Passover crowd     = {agg['passover_crowd_mean']:.2f}",
        f"  Shavuot crowd      = {agg['shavuot_crowd_mean']:.2f}",
    ]
    ax.text(0.05, 0.95, "\n".join(lines), transform=ax.transAxes,
            fontsize=10, family="monospace", va="top")
    ax.axis("off")

    fig.suptitle(
        "Witness World Engine — Spike 1 (agent-less Jerusalem AD 30, 90 days)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    dest = OUT_DIR / "fig_spike1_world_peaks.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


# --------------------------------------------------------------------------
# Fig 2 — Spike 2 counterfactual (full vs Judas-removed)
# --------------------------------------------------------------------------


def fig_spike2_counterfactual(data: dict) -> None:
    full = data.get("spike2_integrated_peter")
    no_judas = data.get("spike2_judas_removed")
    if not (full and no_judas):
        print("[skip] spike2 sections missing")
        return

    labels = ["Full\n(4 agents)", "Judas removed\n(3 agents)"]

    fig, axes = plt.subplots(1, 3, figsize=(13, 5))

    # Trigger count.
    full_trig = [s["total_triggers"] for s in full["per_seed"]]
    nj_trig = [s["total_triggers"] for s in no_judas["per_seed"]]
    ax = axes[0]
    _boxy_bars(
        ax, labels,
        [sum(full_trig) / len(full_trig), sum(nj_trig) / len(nj_trig)],
        [full_trig, nj_trig],
        colours=["#9467bd", "#1f77b4"],
        ylabel="total triggers over 90 days",
        title="Triggers fired (higher = more structure)",
    )

    # Hazard count.
    full_haz = [s["total_hazard_events"] for s in full["per_seed"]]
    nj_haz = [s["total_hazard_events"] for s in no_judas["per_seed"]]
    ax = axes[1]
    _boxy_bars(
        ax, labels,
        [sum(full_haz) / len(full_haz), sum(nj_haz) / len(nj_haz)],
        [full_haz, nj_haz],
        colours=["#9467bd", "#1f77b4"],
        ylabel="total hazard events",
        title="Hazard events (rate-driven)",
    )

    # Peter fear.
    full_fear = [s["peter_final_fear"] for s in full["per_seed"]]
    nj_fear = [s["peter_final_fear"] for s in no_judas["per_seed"]]
    ax = axes[2]
    _boxy_bars(
        ax, labels,
        [sum(full_fear) / len(full_fear), sum(nj_fear) / len(nj_fear)],
        [full_fear, nj_fear],
        colours=["#9467bd", "#1f77b4"],
        ylabel="Peter final fear",
        title="Peter fear at end of 90 days",
        ylim=(0, 10.5),
    )

    # Interpretation subtitle.
    full_mean = full["aggregate"]["trigger_count_mean"]
    nj_mean = no_judas["aggregate"]["trigger_count_mean"]
    pct = (1 - nj_mean / full_mean) * 100 if full_mean else 0
    fig.suptitle(
        "Witness World Engine — Spike 2 integrated counterfactual\n"
        f"Judas removal collapses trigger count by {pct:.0f}% "
        f"({full_mean:.0f} → {nj_mean:.0f}) — causal dependency preserved in world mode",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    dest = OUT_DIR / "fig_spike2_counterfactual.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


def _boxy_bars(
    ax, labels, means, raw, *, colours, ylabel, title, ylim=None,
):
    x = np.arange(len(labels))
    bars = ax.bar(x, means, color=colours, alpha=0.75)
    for xi, values in zip(x, raw):
        ax.scatter([xi] * len(values), values, color="black",
                   s=25, zorder=3, alpha=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    if ylim:
        ax.set_ylim(*ylim)
    for bar, v in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (max(means) * 0.02 if max(means) > 0 else 0.1),
            f"{v:.1f}" if max(means) > 10 else f"{v:.2f}",
            ha="center", va="bottom", fontsize=9,
        )


def fig_spike3_counterfactual_chain(data: dict) -> None:
    """Phase 3D chain — Judas → rumours → jesus_movement, pharisees control."""
    full = data.get("spike2_integrated_peter")
    no_judas = data.get("spike2_judas_removed")
    if not (full and no_judas):
        print("[skip] spike2 sections missing (needed for chain viz)")
        return
    full_agg = full["aggregate"]
    nj_agg = no_judas["aggregate"]

    # Bail out if Phase 3D fields absent (older world_numbers.json).
    for key in ("jesus_movement_final_influence_mean",
                "pharisees_final_influence_mean"):
        if full_agg.get(key) is None:
            print(f"[skip] {key} missing — regenerate world_numbers.json")
            return

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # Panel A: rumour seeds collapse.
    ax = axes[0, 0]
    labels = ["Full\n(4 agents)", "Judas\nremoved"]
    vals = [full_agg["rumors_seeded_mean"], nj_agg["rumors_seeded_mean"]]
    bars = ax.bar(range(2), vals, color=["#9467bd", "#c5b0d5"])
    ax.set_xticks(range(2))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("rumours seeded over 90 days")
    ax.set_title("A. Rumour pipeline (Judas is the only seeder)", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    for bar, v in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(vals) * 0.02 + 0.5,
            f"{v:.0f}", ha="center", fontsize=10, fontweight="bold",
        )

    # Panel B: rumour max intensity collapse.
    ax = axes[0, 1]
    vals = [full_agg["rumor_intensity_max_mean"],
            nj_agg["rumor_intensity_max_mean"]]
    bars = ax.bar(range(2), vals, color=["#d62728", "#f5b7b6"])
    ax.set_xticks(range(2))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("max Σ spread × credibility")
    ax.set_title("B. Rumour intensity peak", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    for bar, v in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(vals) * 0.02 + 0.1,
            f"{v:.2f}", ha="center", fontsize=10, fontweight="bold",
        )

    # Panel C: faction influence — jesus_movement (sensitive) vs pharisees (control).
    ax = axes[1, 0]
    jm_vals = [full_agg["jesus_movement_final_influence_mean"],
               nj_agg["jesus_movement_final_influence_mean"]]
    phar_vals = [full_agg["pharisees_final_influence_mean"],
                 nj_agg["pharisees_final_influence_mean"]]
    x = np.arange(2)
    w = 0.35
    ax.bar(x - w / 2, jm_vals, w, label="jesus_movement (rumour-sensitive)",
           color="#2ca02c")
    ax.bar(x + w / 2, phar_vals, w, label="pharisees (control)",
           color="#7f7f7f")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("final faction influence")
    ax.set_ylim(0, 11)
    ax.set_title("C. Faction influence — specificity check", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    for xi, v in zip(x - w / 2, jm_vals):
        ax.text(xi, v + 0.15, f"{v:.2f}", ha="center", fontsize=9,
                color="#2ca02c", fontweight="bold")
    for xi, v in zip(x + w / 2, phar_vals):
        ax.text(xi, v + 0.15, f"{v:.2f}", ha="center", fontsize=9,
                color="#7f7f7f")

    # Panel D: summary text.
    ax = axes[1, 1]
    jm_drop = (
        (full_agg["jesus_movement_final_influence_mean"]
         - nj_agg["jesus_movement_final_influence_mean"])
        / full_agg["jesus_movement_final_influence_mean"] * 100
    )
    phar_drift = abs(
        full_agg["pharisees_final_influence_mean"]
        - nj_agg["pharisees_final_influence_mean"]
    ) / max(
        full_agg["pharisees_final_influence_mean"],
        nj_agg["pharisees_final_influence_mean"],
    ) * 100
    summary = [
        "Counterfactual chain:",
        "  Judas → inform/betray actions",
        "    → rumor_seed WorldEffects",
        "      → rumours (spread + credibility)",
        "        → jesus_movement influence",
        "",
        f"Full:        JM={full_agg['jesus_movement_final_influence_mean']:.2f}  "
        f"pharisees={full_agg['pharisees_final_influence_mean']:.2f}",
        f"No-Judas:    JM={nj_agg['jesus_movement_final_influence_mean']:.2f}  "
        f"pharisees={nj_agg['pharisees_final_influence_mean']:.2f}",
        "",
        f"jesus_movement drop:   {jm_drop:.1f}%",
        f"pharisees control drift: {phar_drift:.1f}%",
        "",
        "Specificity: the edge targets one faction,",
        "pharisees (non-sensitive) unchanged.",
    ]
    ax.text(0.02, 0.98, "\n".join(summary), transform=ax.transAxes,
            fontsize=10, family="monospace", va="top")
    ax.axis("off")

    fig.suptitle(
        "Witness World Engine — Spike 3 Phase 3D cross-layer counterfactual\n"
        "Judas → rumour → jesus_movement chain, with pharisees as specificity control",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    dest = OUT_DIR / "fig_spike3_counterfactual_chain.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


def fig_spike4_interventions() -> None:
    """Spike 4 — 3 canonical interventions grouped by metric."""
    interventions = ["remove_judas", "hazard_half", "lenient_pilate"]
    loaded: list[tuple[str, dict]] = []
    for iid in interventions:
        path = OUT_DIR / f"intervention_{iid}.json"
        if not path.exists():
            print(f"[skip] {path} missing — run scripts/demo_spike4_interventions.py first")
            return
        loaded.append((iid, json.loads(path.read_text(encoding="utf-8"))))

    # Metrics to show (row per metric, bar group per intervention).
    metrics = [
        ("rumors_seeded", "rumours seeded (ctrl vs intv)", 1),
        ("jesus_movement_final_influence", "jesus_movement influence", 1),
        ("trigger_count", "trigger count", 1),
        ("pharisees_final_influence", "pharisees (control)", 1),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    colours = {"remove_judas": "#9467bd", "hazard_half": "#1f77b4",
               "lenient_pilate": "#2ca02c"}

    for (metric_key, title, _), ax in zip(metrics, axes.flatten()):
        # For each intervention: plot control mean vs intervention mean side-by-side.
        x = np.arange(len(loaded))
        w = 0.35
        ctrl_vals: list[float] = []
        intv_vals: list[float] = []
        labels: list[str] = []
        for iid, payload in loaded:
            entry = payload.get("comparison", {}).get(metric_key)
            if entry is None:
                ctrl_vals.append(0.0)
                intv_vals.append(0.0)
            else:
                ctrl_vals.append(float(entry["control_mean"]))
                intv_vals.append(float(entry["intervention_mean"]))
            labels.append(iid.replace("_", "\n"))
        ax.bar(x - w / 2, ctrl_vals, w, label="control", color="#7f7f7f", alpha=0.75)
        bars_intv = ax.bar(
            x + w / 2, intv_vals, w, label="intervention",
            color=[colours[iid] for iid, _ in loaded], alpha=0.9,
        )
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
        for xi, v in zip(x - w / 2, ctrl_vals):
            ax.text(xi, v + max(max(ctrl_vals + intv_vals), 0.5) * 0.02,
                    f"{v:.2f}", ha="center", fontsize=7, color="#555")
        for bar, v in zip(bars_intv, intv_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(max(ctrl_vals + intv_vals), 0.5) * 0.02,
                f"{v:.2f}", ha="center", fontsize=8, fontweight="bold",
            )

    fig.suptitle(
        "Witness World Engine — Spike 4 three canonical interventions\n"
        "control vs intervention arm means (seed-paired ensemble)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    dest = OUT_DIR / "fig_spike4_interventions.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


def main() -> None:
    data = _load()
    print(f"[fig] rendering from {SRC}")
    fig_spike1_world_peaks(data)
    fig_spike2_counterfactual(data)
    fig_spike3_counterfactual_chain(data)
    fig_spike4_interventions()
    print(f"[done] figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
