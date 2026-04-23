"""Baseline comparison figures (baseline_experiment_prompt.md — task 4).

실행:
    python scripts/baseline_figures.py

입력: docs/person/paper_data/baseline_comparison.json
산출:
    docs/person/paper_data/fig_baseline_comparison.png (4 subplot 막대)
    docs/person/paper_data/fig_ablation_hierarchy.png (Level 0-4 추이)

기존 코드 수정 금지.
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
SRC = OUT_DIR / "baseline_comparison.json"


def _load() -> dict:
    if not SRC.exists():
        raise SystemExit(
            f"{SRC} not found. Run scripts/baseline_comparison.py first."
        )
    return json.loads(SRC.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Fig 1: Baseline comparison (4 subplot)
# --------------------------------------------------------------------------


def fig_baseline_comparison(data: dict) -> None:
    print("[fig] baseline_comparison ...")
    order = [
        ("no_trigger", "A. No-Trigger"),
        ("exogenous_only", "B. Exogenous-Only"),
        ("single_agent", "C. Single-Agent"),
        ("random_behavior", "D. Random-Behavior"),
        ("full_system", "Full System"),
    ]
    labels = [lab for _, lab in order]
    metrics = [
        ("arrest_rate", "arrest rate", "#1f77b4"),
        ("pom_all_pass_rate", "POM all-pass rate", "#2ca02c"),
        ("causal_chain_rate", "causal chain rate", "#d62728"),
        ("arrest_tick_mean", "arrest tick mean (if occurred)", "#ff7f0e"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (key, title, color) in zip(axes.flatten(), metrics):
        vals = []
        for k, _ in order:
            v = data["baselines"][k].get(key)
            vals.append(float(v) if v is not None else 0.0)
        # highlight Full System (마지막 bar)
        colors = [color] * (len(order) - 1) + ["#9467bd"]
        bars = ax.bar(range(len(order)), vals, color=colors)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(labels, rotation=15, fontsize=8, ha="right")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)

        # y-axis: rate metrics → 0-1; tick_mean → auto
        if "rate" in key:
            ax.set_ylim(0, 1.05)
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.02 if "rate" in key else 2.0),
                f"{v:.2f}" if "rate" in key else f"{v:.0f}",
                ha="center", va="bottom", fontsize=8,
            )

    fig.suptitle(
        f"Witness — Baseline Comparison (Peter standalone, "
        f"n={data['n_seeds']} seeds × {data['max_tick']} tick)",
        fontsize=12,
    )
    fig.tight_layout()
    dest = OUT_DIR / "fig_baseline_comparison.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  -> {dest}")


# --------------------------------------------------------------------------
# Fig 2: Ablation hierarchy (incremental feature addition)
# --------------------------------------------------------------------------


def fig_ablation_hierarchy(data: dict) -> None:
    print("[fig] ablation_hierarchy ...")
    order = [
        ("level_0_hazard_only", "L0\nhazard only"),
        ("level_1_hazard_trigger", "L1\n+trigger"),
        ("level_2_multi_agent", "L2\n+multi-agent"),
        ("level_3_with_canonical", "L3\n+canonical events"),
        ("level_4_full_system", "L4\nfull system"),
    ]
    labels = [lab for _, lab in order]

    arrest = [data["ablation"][k]["arrest_rate"] for k, _ in order]
    pom = [data["ablation"][k]["pom_all_pass_rate"] for k, _ in order]
    chain = [data["ablation"][k]["causal_chain_rate"] for k, _ in order]
    fear = [
        data["ablation"][k]["final_fear_mean"] or 0.0 for k, _ in order
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # LEFT: arrest / chain / POM rates
    x = np.arange(len(order))
    w = 0.27
    ax1.bar(x - w, arrest, w, label="arrest rate", color="#1f77b4")
    ax1.bar(x, chain, w, label="causal chain rate", color="#d62728")
    ax1.bar(x + w, pom, w, label="POM all-pass rate", color="#2ca02c")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_ylim(0, 1.1)
    ax1.set_ylabel("rate (over 10 seeds)")
    ax1.set_title("Incremental feature addition → outcome rates")
    ax1.legend(loc="lower right", fontsize=9)
    ax1.grid(axis="y", alpha=0.3)
    # value labels
    for i, (a, c, p) in enumerate(zip(arrest, chain, pom)):
        ax1.text(i - w, a + 0.02, f"{a:.2f}", ha="center", fontsize=7)
        ax1.text(i, c + 0.02, f"{c:.2f}", ha="center", fontsize=7)
        ax1.text(i + w, p + 0.02, f"{p:.2f}", ha="center", fontsize=7)

    # RIGHT: Peter emotion at end (final fear) — feature 추가가 "무게감"을 더하는지
    ax2.plot(x, fear, marker="o", color="#d62728", linewidth=2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8)
    ax2.set_ylabel("Peter final fear (mean of 10 seeds)")
    ax2.set_title("Emotional weight: fear accumulation vs feature layers")
    ax2.grid(alpha=0.3)
    ax2.set_ylim(0, 10)
    for i, v in enumerate(fear):
        ax2.text(i, v + 0.3, f"{v:.2f}", ha="center", fontsize=8)

    fig.suptitle(
        f"Witness — Ablation Hierarchy "
        f"(Peter, n={data['n_seeds']} seeds × {data['max_tick']} tick)",
        fontsize=12,
    )
    fig.tight_layout()
    dest = OUT_DIR / "fig_ablation_hierarchy.png"
    fig.savefig(dest, dpi=120)
    plt.close(fig)
    print(f"  -> {dest}")


def main() -> None:
    data = _load()
    fig_baseline_comparison(data)
    fig_ablation_hierarchy(data)
    print(f"[done] figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
