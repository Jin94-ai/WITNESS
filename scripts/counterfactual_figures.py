"""Counterfactual + hazard scaling figures (counterfactual_experiment_prompt.md — Fig 1, 2).

실행:
    python scripts/counterfactual_figures.py

입력:
    docs/person/paper_data/causal_counterfactual.json
    docs/person/paper_data/hazard_scaling.json

산출:
    docs/person/paper_data/fig_counterfactual_comparison.png
    docs/person/paper_data/fig_hazard_scaling_curve.png

기존 엔진/콘텐츠 코드 수정 금지. 읽기 전용 분석 layer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = ROOT / "docs" / "person" / "paper_data"
CF_SRC = OUT_DIR / "causal_counterfactual.json"
HZ_SRC = OUT_DIR / "hazard_scaling.json"


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"{path} not found. Run the corresponding experiment script first.")
    return json.loads(path.read_text(encoding="utf-8"))


# ===========================================================================
# Fig 1: Counterfactual comparison (5 conditions × 3 metrics)
# ===========================================================================


def fig_counterfactual_comparison(data: dict) -> None:
    print("[fig] counterfactual_comparison ...")
    order = [
        ("full_system",      "Full\nSystem"),
        ("judas_removed",    "Judas\nRemoved"),
        ("caiaphas_removed", "Caiaphas\nRemoved"),
        ("trigger_removed",  "Trigger\nRemoved"),
        ("random_no_judas",  "Random +\nNo Judas"),
    ]
    labels = [lab for _, lab in order]

    conds = data["conditions"]

    canonical = [conds[k]["canonical_arrest_rate"] for k, _ in order]
    endogenous = [conds[k]["endogenous_arrest_rate"] for k, _ in order]
    trigger = [conds[k].get("trigger_arrest_rate", 0.0) for k, _ in order]
    chain = [conds[k]["causal_chain_rate_gap_constrained"] for k, _ in order]

    # Highlight Full System (index 0) distinctly.
    full_color = "#9467bd"
    other_color = "#1f77b4"
    bar_colors = [full_color] + [other_color] * (len(order) - 1)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    panels = [
        (axes[0, 0], canonical,  "Canonical arrest rate",
         "Fixed scene_08 firing — same across all conditions (ceiling)", 1.1),
        (axes[0, 1], trigger,    "Trigger-fired arrest rate (V3)",
         "Key metric: arrest_trigger requires Judas disillusion + betray + Caiaphas threat", 1.1),
        (axes[1, 0], chain,      "Causal chain rate (gap ≤ 30 tick)",
         "inform → surveillance → betray → arrest within 30-tick gap", 0.5),
        (axes[1, 1], endogenous, "Endogenous arrest rate (V2, includes hazard)",
         "Includes hazard-driven arrest events — less discriminating", 1.1),
    ]
    for ax, vals, title, subtitle, ylim in panels:
        bars = ax.bar(range(len(order)), vals, color=bar_colors)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, ylim)
        ax.grid(axis="y", alpha=0.3)
        ax.text(
            0.5, -0.32, subtitle, transform=ax.transAxes,
            ha="center", va="top", fontsize=8, style="italic", color="gray",
        )
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + ylim * 0.02,
                f"{v:.2f}",
                ha="center", va="bottom", fontsize=9,
            )

    fig.suptitle(
        f"Witness — Counterfactual Causal Validation "
        f"(n={data['n_seeds']} seeds × {data['max_tick']} tick)\n"
        f"causal_dependency: {data['verdicts']['causal_dependency']}   "
        f"trigger_necessity: {data['verdicts']['trigger_necessity']}   "
        f"random_chain_nature: {data['verdicts']['random_chain_nature']}",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    dest = OUT_DIR / "fig_counterfactual_comparison.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


# ===========================================================================
# Fig 2: Hazard scaling curve
# ===========================================================================


def fig_hazard_scaling_curve(data: dict) -> None:
    print("[fig] hazard_scaling_curve ...")
    factors_sorted = sorted(
        [float(f) for f in data["factors"].keys()], reverse=True,
    )
    x = np.array(factors_sorted)

    def series(key: str, default: float = 0.0) -> np.ndarray:
        return np.array([
            data["factors"][f"{f:.2f}"].get(key, default) or default
            for f in factors_sorted
        ])

    canonical = series("canonical_arrest_rate")
    endogenous = series("endogenous_arrest_rate")
    trigger = series("trigger_arrest_rate")
    chain = series("causal_chain_rate_gap_constrained")
    pom = series("pom_all_pass_rate")

    pattern = data.get("pattern_analysis", {}).get("pattern", "?")
    collapse = data.get("pattern_analysis", {}).get("collapse_factor")
    collapse_str = f"{collapse:.2f}" if collapse is not None else "None"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # LEFT: arrest rates
    ax1.plot(x, canonical, marker="s", linewidth=2,
             color="#7f7f7f", label="canonical (scene_08)")
    ax1.plot(x, endogenous, marker="o", linewidth=2,
             color="#1f77b4", label="endogenous (V2, inc hazard)")
    if trigger.any():
        ax1.plot(x, trigger, marker="^", linewidth=2,
                 color="#d62728", label="trigger-fired (V3)")
    ax1.invert_xaxis()
    ax1.set_xlabel("hazard scaling factor")
    ax1.set_ylabel("arrest rate")
    ax1.set_ylim(-0.05, 1.1)
    ax1.set_title("Arrest rates vs hazard scaling")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="lower left", fontsize=9)
    for xi, v in zip(x, endogenous):
        ax1.text(xi, v + 0.03, f"{v:.2f}", ha="center", fontsize=7,
                 color="#1f77b4")

    # RIGHT: chain & POM (the metrics that actually vary)
    ax2.plot(x, chain, marker="D", linewidth=2,
             color="#d62728", label="causal chain (gap ≤ 30 tick)")
    ax2.plot(x, pom,   marker="o", linewidth=2,
             color="#2ca02c", label="POM all-pass")
    ax2.invert_xaxis()
    ax2.set_xlabel("hazard scaling factor")
    ax2.set_ylabel("rate")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Structural metrics vs hazard scaling")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="lower right", fontsize=9)
    for xi, v in zip(x, chain):
        ax2.text(xi, v + 0.03, f"{v:.2f}", ha="center", fontsize=7,
                 color="#d62728")

    fig.suptitle(
        f"Witness — Hazard Scaling (Peter standalone, "
        f"n={data['n_seeds']} seeds × {data['max_tick']} tick)\n"
        f"pattern: {pattern}   collapse_factor: {collapse_str}   "
        f"(Interpretation: canonical scene_08 ceiling masks "
        f"endogenous dynamics; chain/POM are the real signal)",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    dest = OUT_DIR / "fig_hazard_scaling_curve.png"
    fig.savefig(dest, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {dest}")


def main() -> None:
    cf = _load(CF_SRC)
    hz = _load(HZ_SRC)
    fig_counterfactual_comparison(cf)
    fig_hazard_scaling_curve(hz)
    print(f"[done] figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
