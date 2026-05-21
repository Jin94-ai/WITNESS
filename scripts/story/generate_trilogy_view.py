"""J-Beta — Scarcity Trilogy bundled story.

3 anchor (1/2/3 accusations) × 5 seeds = 15 stories를 다음 두 view로 묶음:

1. **Modal view** (`scarcity_trilogy_modal.txt`): 각 anchor의 modal outcome seed
   하나만 narrative로 → 3-act trilogy. IP 자산 직접 가치.

2. **Full cross-seed view** (`scarcity_trilogy_full.txt`): 15 stories all,
   cross-anchor 시퀀스 비교 가능.

Per `docs/creative/J_BETA_PROGRESS.md` §5 (다음 J-Beta 작업 1순위).
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

from scripts.story.build_narrative_ir import build_ir
from scripts.story.extract_story_features import parse_probe
from scripts.story.generate_anchor_variations import world_to_annotated_text
from scripts.story.render_story_ko import render_narrative, render_summary
from scripts.story.selector import get_anchor_by_id, get_variations

TRILOGY_ANCHORS = [
    (
        "peter_scarcity_baseline",
        "Act I — 한 번의 비난",
        "이 모든 것은, 그 첫 비난이 떨어진 시각으로부터 시작되었다.",
    ),
    (
        "peter_scarcity_double",
        "Act II — 두 번의 비난, 깊어지는 굳음",
        "이미 한 번 떨어진 비난은, 잊혀지기 전에 두 번째가 따라왔다.",
    ),
    (
        "peter_scarcity_triple",
        "Act III — 세 번째 비난, 풀려나는 결",
        "비난이 세 번 거리에 닿았을 때, 사람들은 더 이상 첫 번째와 두 번째를 구분하지 못했다.",
    ),
]

# Cycle 6 Patch J — Act II only escalation envelope.
# Lee v2 약점 "Act I/II SAT 톤 차이를 더 벌려야" 직접 대응. preamble은 narrative 진입 시
# escalation 의미 명시, echo는 narrative 종료 후 accumulation 의미 명시.
ACT_II_PREAMBLE = (
    "(첫 비난의 굳음이 풀리지 않은 채, 두 번째 비난이 그 자리에 떨어졌다. "
    "사람들의 자세는 한 번이 아니라 두 번 멈춰 섰다.)"
)

ACT_II_ECHO = (
    "(같은 거리, 같은 자세, 그러나 두 번의 비난이 동시에 머물렀다. "
    "굳음은 한 결로 끝나지 않았다.)"
)


def render_one(anchor, seed):
    """Return (outcome, summary, narrative) for one (anchor, seed)."""
    pairs = get_variations(anchor, max_seeds=anchor.seed_count)
    world = next(w for s, w in pairs if s == seed)
    probe_label = f"{anchor.anchor_id}_seed{seed}"
    annotated_text, fs = world_to_annotated_text(world, probe_label, anchor.anchor_id, seed)
    features = parse_probe(annotated_text)
    features["probe_id"] = probe_label
    ir = build_ir(features)
    ir["probe_id"] = probe_label
    summary = render_summary(ir)
    narrative = render_narrative(ir)
    return fs, summary, narrative


def find_modal_seed(anchor):
    """Run all 5 seeds, find the seed whose outcome matches modal (most common)."""
    pairs = get_variations(anchor, max_seeds=anchor.seed_count)
    outcomes = []
    for seed, world in pairs:
        probe_label = f"{anchor.anchor_id}_seed{seed}"
        annotated_text, fs = world_to_annotated_text(world, probe_label, anchor.anchor_id, seed)
        outcomes.append((seed, fs))
    modal_outcome = Counter(o for _, o in outcomes).most_common(1)[0][0]
    # Pick lowest seed matching modal (deterministic)
    for seed, fs in outcomes:
        if fs == modal_outcome:
            return seed, modal_outcome, outcomes
    raise RuntimeError("No modal found")


def main():
    out_dir = ROOT / "outputs" / "creative_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # Modal view — 3-act trilogy with one seed per anchor
    # ============================================================
    print("Generating scarcity trilogy modal view (3 acts)...")
    modal_lines = [
        "=" * 70,
        "SCARCITY TRILOGY — 운명의 세 결",
        "=" * 70,
        "",
        "같은 도시, 같은 사람들, 같은 곡식이 비어 가는 계절.",
        "변하는 것은 단 하나, 비난의 횟수.",
        "한 번 / 두 번 / 세 번의 비난이 같은 자리에 닿을 때, 결말은 어떻게 갈라지는가.",
        "",
        "(scarcity 시나리오의 modal seed 한 편씩 — 같은 cell의 가장 흔한 결말)",
        "",
        "=" * 70,
        "",
    ]

    summaries = []
    for anchor_id, act_title, signature in TRILOGY_ANCHORS:
        anchor = get_anchor_by_id(anchor_id)
        modal_seed, modal_outcome, outcomes = find_modal_seed(anchor)
        fs, summary, narrative = render_one(anchor, modal_seed)
        summaries.append((act_title, modal_outcome, outcomes))

        modal_lines.append("")
        modal_lines.append(f"### {act_title}")
        modal_lines.append(f"  (modal: {modal_outcome}, seed={modal_seed})")
        modal_lines.append("")
        # Gate 1 자율 cycle #3: anchor signature line — trilogy 내 각 anchor 정체성
        modal_lines.append(f"> {signature}")
        modal_lines.append("")
        # Cycle 6 Patch J: Act II only — escalation preamble (narrative 진입 직전)
        if anchor_id == "peter_scarcity_double":
            modal_lines.append(ACT_II_PREAMBLE)
            modal_lines.append("")
        modal_lines.append(narrative)
        modal_lines.append("")
        # Cycle 6 Patch J: Act II only — escalation echo (narrative 종료 직후)
        if anchor_id == "peter_scarcity_double":
            modal_lines.append(ACT_II_ECHO)
            modal_lines.append("")
        modal_lines.append("-" * 70)

    # 마지막 trilogy meta — anchor signature 강화
    modal_lines.extend([
        "",
        "=" * 70,
        "TRILOGY META — Three Acts of the Same Beginning",
        "=" * 70,
        "",
        "한 번의 비난은 어떤 자리를 굳히고, 두 번의 비난은 그 굳음을 깊게 했다.",
        "그러나 세 번째 비난이 닿았을 때, 무언가가 풀려났다.",
        "",
        "이것은 같은 도시, 같은 사람들의 세 가지 운명이다.",
        "변한 것은 단 하나, 비난이 거리에 닿은 횟수.",
        "",
        "각 anchor의 5 seed 분포 (5 가능 운명, 모달이 가장 흔한 결말):",
    ])
    for act_title, modal, outcomes in summaries:
        seqs = " ".join(o[:3] for _, o in outcomes)
        modal_lines.append(f"  {act_title}: {seqs}  (modal: {modal})")
    modal_lines.extend([
        "",
        "→ 같은 anchor의 5 seed가 항상 같은 결말은 아니다.",
        "  Act III에서는 SAT보다 REC가 우세하지만, 여전히 2/5는 굳어 있다.",
        "  '풀려남'은 보장이 아니라 가능성일 뿐이다.",
    ])

    modal_path = out_dir / "scarcity_trilogy_modal.txt"
    modal_path.write_text("\n".join(modal_lines), encoding="utf-8")
    print(f"  -> {modal_path}")

    # ============================================================
    # Full view — 15 stories all
    # ============================================================
    print("\nGenerating scarcity trilogy full cross-seed view (15 stories)...")
    full_lines = [
        "=" * 70,
        "SCARCITY TRILOGY — Full Cross-Seed Variation",
        "=" * 70,
        "",
        "3 anchor (1/2/3 accusations) x 5 seeds = 15 stories.",
        "Cross-anchor sequence per seed — 같은 seed가 다른 cell에서 어떻게 변하는가.",
        "",
        "=" * 70,
    ]
    for anchor_id, act_title, signature in TRILOGY_ANCHORS:
        anchor = get_anchor_by_id(anchor_id)
        full_lines.append("")
        full_lines.append(f"### {act_title}: {anchor_id}")
        full_lines.append(f"> {signature}")
        full_lines.append("")
        for seed in range(anchor.seed_count):
            fs, summary, narrative = render_one(anchor, seed)
            full_lines.append(f"--- seed={seed} (final: {fs}) ---")
            full_lines.append("")
            full_lines.append("[Narrative]")
            full_lines.append(narrative)
            full_lines.append("")
            full_lines.append("-" * 70)

    full_path = out_dir / "scarcity_trilogy_full.txt"
    full_path.write_text("\n".join(full_lines), encoding="utf-8")
    print(f"  -> {full_path}")

    print("\nDone.")
    print("\nFiles:")
    print(f"  Modal view (3 acts): {modal_path}")
    print(f"  Full view (15 stories): {full_path}")


if __name__ == "__main__":
    main()
