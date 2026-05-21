"""End-to-end pipeline: Universal Engine simulation → 드라마 풍 변환.

매 실행마다 *전체 chain* 작동:
  1. PhasedSimulationWorld 시뮬레이션 실행 (anchor + seed)
  2. life_arc_narrative로 한국어 timeline 합성
  3. 각 phase window → KoBART input format (171자 Summary)
  4. KoBART (Stage 2, S2 학습) 추론 → 드라마 풍 한 장면
  5. 결과 통합 (Universal narrative + 드라마 풍 변환) → md / json

Usage (Python 3.11, CUDA):
    "C:/Program Files/Python311/python.exe" -m scripts.pipeline.universal_to_drama \
        --seed 0 --genre fm_drama

    "C:/Program Files/Python311/python.exe" -m scripts.pipeline.universal_to_drama \
        --seed 1 --genre fs_drama --full-passion

Output: docs/portfolio/demo_universal_to_drama/seed{N}_{genre}/
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

KOBART_BEST_DIR = ROOT / "models" / "kobart_v2" / "checkpoint-best"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "portfolio" / "demo_universal_to_drama"

MAX_INPUT_LEN = 256
MAX_OUTPUT_LEN = 512
SUMMARY_TARGET_LEN = 171  # KoBART Stage 2 학습 시 S2 평균 171자


# ============================================================
# Step 1: Universal Engine simulation + life arc narrative
# ============================================================

def run_universal_simulation(seed: int, with_passion: bool):
    """매 실행마다 새 시뮬레이션 + life arc narrative 합성."""
    from engine.observer.life_arc_narrative import build_life_arc_narrative
    from engine.simulation.phased_world import PhasedSimulationWorld
    from examples.demo_phased import _build_config, _rules
    from scripts.narrative.run_life_arc_demo import PETER_PHASE_LABELS_KO

    print(f"[1/4] PhasedSimulationWorld 실행 (seed={seed}, passion={with_passion})...", flush=True)
    config = _build_config(with_passion=with_passion)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=seed)

    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or []) if p.canonical_events_path
    }

    print("[2/4] life_arc_narrative 합성 (한국어 timeline)...", flush=True)
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=seed,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy="by_phase",
    )
    return arc


# ============================================================
# Step 2: phase window → KoBART Summary format
# ============================================================

def window_to_summary(window, idx: int, max_len: int = SUMMARY_TARGET_LEN) -> str:
    """phase window의 plain_narrative를 KoBART Summary 형식으로 변환.

    Source: window.plain_narrative (life_arc_narrative.py가 합성한 한국어 본문)
            + canonical_events description 보강.
            첫 max_len + buffer 영역에서 자연 절단.
    """
    pn = getattr(window, "plain_narrative", "") or ""
    # 첫 줄 (보통 "이 시간대는 약 N일에 해당한다 ...") 제거
    lines = [ln.strip() for ln in pn.split("\n") if ln.strip()]
    body_lines = [ln for ln in lines if "이 시간대는 약" not in ln]
    body = " ".join(body_lines)
    # markdown 마커 정리
    body = body.replace("**", "").replace("*", "").replace("##", "").replace("→", "→")

    # canonical_events fallback
    events = getattr(window, "canonical_events", []) or []
    if not body and events:
        ev_descs: list[str] = []
        for ev in events[:3]:
            desc = ev.get("description") if isinstance(ev, dict) else getattr(ev, "description", "")
            if desc:
                ev_descs.append(desc.strip())
        body = ". ".join(ev_descs)

    if not body:
        body = f"베드로 인생 {idx}막의 흐름. 정경 사건 trigger 미일치 구간."

    # max_len + buffer로 자연 절단
    if len(body) > max_len + 40:
        cut = body[: max_len + 40]
        for sep in [". ", "! ", "? ", "다. "]:
            last = cut.rfind(sep)
            if last > max_len - 30:
                body = cut[: last + 1]
                break
        else:
            body = cut[:max_len] + "…"

    if not body.endswith((".", "다", "음", "함", "…")):
        body += "."
    return body


# ============================================================
# Step 3: KoBART 추론
# ============================================================

def kobart_infer_batch(summaries: list[str], doc_type: str = "fm_drama") -> list[str]:
    """매 실행 시 KoBART 체크포인트 로드 + batch 추론."""
    import torch
    from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast

    if not KOBART_BEST_DIR.exists():
        raise FileNotFoundError(f"KoBART checkpoint missing: {KOBART_BEST_DIR}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[3/4] KoBART 추론 (device={device}, doc_type={doc_type})...", flush=True)
    tokenizer = PreTrainedTokenizerFast.from_pretrained(str(KOBART_BEST_DIR))
    model = BartForConditionalGeneration.from_pretrained(str(KOBART_BEST_DIR)).to(device).eval()

    # KoBART input format (Stage 2 학습과 동일)
    inputs = [f"<{doc_type}> Summary: {s}" for s in summaries]
    out: list[str] = []
    with torch.no_grad():
        for i in range(0, len(inputs), 4):
            chunk = inputs[i : i + 4]
            enc = tokenizer(chunk, padding=True, truncation=True,
                            max_length=MAX_INPUT_LEN, return_tensors="pt").to(device)
            ids = model.generate(
                input_ids=enc.input_ids, attention_mask=enc.attention_mask,
                max_length=MAX_OUTPUT_LEN, num_beams=4,
                length_penalty=1.0, no_repeat_ngram_size=3, early_stopping=True,
            )
            for j in range(ids.size(0)):
                out.append(tokenizer.decode(ids[j], skip_special_tokens=True))
    return out


# ============================================================
# Step 4: 결과 통합 + 저장
# ============================================================

def render_pipeline_md(arc, summaries: list[str], drama_outputs: list[str],
                       seed: int, doc_type: str) -> str:
    lines = [
        f"# Universal Engine → Drama Pipeline (seed={seed}, genre={doc_type})",
        "",
        "> 매 실행마다 *전체 chain* 작동: PhasedSimulationWorld → life_arc_narrative → KoBART (Stage 2 S2).",
        f"> Anchor: peter_scarcity_baseline / Total days: {arc.total_days:.1f} / Windows: {len(arc.windows)}",
        "",
        "---",
        "",
    ]
    for i, (w, s, d) in enumerate(zip(arc.windows, summaries, drama_outputs), 1):
        label = getattr(w, "phase_label", "") or f"Window {i}"
        lines.extend([
            f"## {i}. {label}",
            "",
            "### Universal narrative (Summary 형식, KoBART 입력)",
            "",
            f"> {s}",
            "",
            "### 드라마 풍 변환 (KoBART 출력)",
            "",
            "```",
            d[:600] + ("..." if len(d) > 600 else ""),
            "```",
            "",
            "---",
            "",
        ])
    return "\n".join(lines)


def main(seed: int, with_passion: bool, doc_type: str, output_dir: Path) -> int:
    t0 = time.time()
    # Step 1+2: simulation + narrative
    arc = run_universal_simulation(seed=seed, with_passion=with_passion)

    # Step 2.5: windows → summaries
    summaries = [window_to_summary(w, idx=i+1) for i, w in enumerate(arc.windows)]
    for i, s in enumerate(summaries, 1):
        print(f"  window {i} summary ({len(s)}자): {s[:80]}…", flush=True)

    # Step 3: KoBART inference
    drama_outputs = kobart_infer_batch(summaries, doc_type=doc_type)

    # Step 4: 통합 출력
    print("[4/4] 결과 통합 + 저장...", flush=True)
    out_dir = output_dir / f"seed{seed}_{doc_type}"
    out_dir.mkdir(parents=True, exist_ok=True)

    md = render_pipeline_md(arc, summaries, drama_outputs, seed, doc_type)
    (out_dir / "pipeline_result.md").write_text(md, encoding="utf-8")

    payload = {
        "schema_version": "universal_to_drama_v1",
        "seed": seed,
        "doc_type": doc_type,
        "with_passion": with_passion,
        "anchor": "peter_scarcity_baseline",
        "total_days": arc.total_days,
        "windows": [
            {
                "phase_label": getattr(w, "phase_label", ""),
                "summary_input": s,
                "summary_input_len": len(s),
                "drama_output": d,
                "drama_output_len": len(d),
            }
            for w, s, d in zip(arc.windows, summaries, drama_outputs)
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out_dir / "pipeline_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    print(f"  → {out_dir / 'pipeline_result.md'}")
    print(f"  → {out_dir / 'pipeline_result.json'}")
    print(f"Total: {payload['elapsed_sec']}s")
    return 0


def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--genre", choices=["fm_drama", "fs_drama"], default="fm_drama",
                     help="KoBART control token (학습 시 fm_drama=가족극, fs_drama=단막극)")
    ap.add_argument("--full-passion", action="store_true")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR))
    args = ap.parse_args()
    return main(seed=args.seed, with_passion=args.full_passion,
                doc_type=args.genre, output_dir=Path(args.output))


if __name__ == "__main__":
    sys.exit(cli())
