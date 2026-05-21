"""Stage 1.3 — KoBART baseline evaluation.

Per docs/witness_train_directive_1.md §3.

Run (Python 3.11, CUDA):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage1_3_eval
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast, DataCollatorForSeq2Seq

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "witness_v1"
BEST_DIR = ROOT / "models" / "kobart_baseline_v1" / "checkpoint-best"
OUT_DIR = ROOT / "docs" / "results" / "witness_train_v1"

SEED = 42

MAX_INPUT_LEN = 128
MAX_OUTPUT_LEN = 512
GEN_BATCH = 4
EVAL_BATCH_PPL = 4
NUM_QUAL_SAMPLES = 20


def set_seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_jsonl(p: Path) -> list[dict]:
    out: list[dict] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def build_input(rec: dict) -> str:
    return f"<{rec['doc_type']}> Summary: {rec['summary1']}"


def generate_batch(model, tokenizer, records: list[dict], device, batch_size: int = GEN_BATCH) -> list[str]:
    """Beam search generation for each record."""
    out: list[str] = []
    model.eval()
    with torch.no_grad():
        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            inputs = [build_input(r) for r in chunk]
            enc = tokenizer(
                inputs, padding=True, truncation=True, max_length=MAX_INPUT_LEN,
                return_tensors="pt",
            ).to(device)
            ids = model.generate(
                input_ids=enc.input_ids,
                attention_mask=enc.attention_mask,
                max_length=MAX_OUTPUT_LEN,
                num_beams=4,
                length_penalty=1.0,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
            for j in range(ids.size(0)):
                out.append(tokenizer.decode(ids[j], skip_special_tokens=True))
            if (i // batch_size) % 25 == 0:
                print(f"[eval] generated {i + len(chunk)}/{len(records)}", flush=True)
    return out


def compute_perplexity(model, tokenizer, records: list[dict], device, batch_size: int = EVAL_BATCH_PPL) -> float:
    """Average per-token perplexity over test set (teacher-forced loss)."""
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="longest", return_tensors="pt")

    def to_features(r):
        enc = tokenizer(build_input(r), max_length=MAX_INPUT_LEN, truncation=True, padding=False)
        tgt = tokenizer(text_target=r["passage"], max_length=MAX_OUTPUT_LEN, truncation=True, padding=False)
        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": tgt["input_ids"],
        }

    feats = [to_features(r) for r in records]
    with torch.no_grad():
        for i in range(0, len(feats), batch_size):
            chunk = feats[i : i + batch_size]
            batch = collator(chunk)
            batch = {k: v.to(device) for k, v in batch.items()}
            out = model(**batch)
            n_tok = (batch["labels"] != -100).sum().item()
            total_loss += out.loss.item() * n_tok
            total_tokens += n_tok
            if (i // batch_size) % 50 == 0:
                print(f"[eval-ppl] {i + len(chunk)}/{len(feats)}", flush=True)
    avg_loss = total_loss / max(1, total_tokens)
    return math.exp(min(20, avg_loss))


def compute_bleu_rouge(predictions: list[str], references: list[str]) -> dict:
    """sacrebleu BLEU-4 + rouge_score ROUGE-1/2/L."""
    import sacrebleu
    from rouge_score import rouge_scorer

    # BLEU-4 (corpus-level)
    bleu = sacrebleu.corpus_bleu(predictions, [references])
    # ROUGE
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
    r1 = []
    r2 = []
    rl = []
    for p, ref in zip(predictions, references):
        s = scorer.score(ref, p)
        r1.append(s["rouge1"].fmeasure)
        r2.append(s["rouge2"].fmeasure)
        rl.append(s["rougeL"].fmeasure)
    return {
        "bleu4": round(bleu.score, 4),
        "bleu4_brevity_penalty": round(bleu.bp, 4),
        "rouge1_f": round(float(np.mean(r1)), 4),
        "rouge2_f": round(float(np.mean(r2)), 4),
        "rougeL_f": round(float(np.mean(rl)), 4),
    }


def overlap_ratio(seed: str, generated: str) -> float:
    """summary1 char-bigram overlap with generated. 시드 단어가 결과에 얼마나 나오는가."""
    if not seed or not generated:
        return 0.0
    seed_bigs = set(seed[i:i+2] for i in range(len(seed) - 1) if seed[i:i+2].strip())
    gen_bigs = set(generated[i:i+2] for i in range(len(generated) - 1) if generated[i:i+2].strip())
    if not seed_bigs:
        return 0.0
    return round(len(seed_bigs & gen_bigs) / len(seed_bigs), 4)


def main() -> int:
    set_seed_all(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[stage1.3] device={device}", flush=True)

    if not BEST_DIR.exists():
        print(f"[stage1.3] ERROR: best checkpoint not found at {BEST_DIR}", file=sys.stderr)
        return 1

    print(f"[stage1.3] loading model from {BEST_DIR}", flush=True)
    tokenizer = PreTrainedTokenizerFast.from_pretrained(BEST_DIR)
    model = BartForConditionalGeneration.from_pretrained(BEST_DIR).to(device)
    model.eval()

    test_recs = load_jsonl(DATA_DIR / "test.jsonl")
    print(f"[stage1.3] test set: {len(test_recs)} pairs", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Layer 1: quantitative
    print("[stage1.3] generating predictions...", flush=True)
    t0 = time.time()
    predictions = generate_batch(model, tokenizer, test_recs, device)
    print(f"[stage1.3] generation done. {time.time() - t0:.1f}s", flush=True)
    references = [r["passage"] for r in test_recs]

    metrics = compute_bleu_rouge(predictions, references)
    print("[stage1.3] BLEU/ROUGE:", metrics, flush=True)

    print("[stage1.3] computing perplexity...", flush=True)
    ppl = compute_perplexity(model, tokenizer, test_recs, device)
    metrics["test_perplexity"] = round(ppl, 4)
    print(f"[stage1.3] perplexity: {ppl:.4f}", flush=True)

    # length stats
    pred_lens = [len(p) for p in predictions]
    metrics["pred_length_mean"] = round(float(np.mean(pred_lens)), 1)
    metrics["pred_length_median"] = int(np.median(pred_lens))
    metrics["pred_max_len_hit_pct"] = round(sum(1 for L in pred_lens if L >= MAX_OUTPUT_LEN * 0.95) / len(pred_lens) * 100, 2)

    # Layer 3: sanity (overlap + doc_type tone)
    overlaps = [overlap_ratio(r["summary1"], p) for r, p in zip(test_recs, predictions)]
    metrics["seed_overlap_bigram_mean"] = round(float(np.mean(overlaps)), 4)
    fm_overlaps = [o for r, o in zip(test_recs, overlaps) if r["doc_type"] == "fm_drama"]
    fs_overlaps = [o for r, o in zip(test_recs, overlaps) if r["doc_type"] == "fs_drama"]
    metrics["seed_overlap_fm_drama"] = round(float(np.mean(fm_overlaps)) if fm_overlaps else 0, 4)
    metrics["seed_overlap_fs_drama"] = round(float(np.mean(fs_overlaps)) if fs_overlaps else 0, 4)

    (OUT_DIR / "stage1_kobart_eval.json").write_text(
        json.dumps({
            "schema_version": "stage1_kobart_eval_v1",
            "model_path": str(BEST_DIR.relative_to(ROOT)).replace("\\", "/"),
            "test_size": len(test_recs),
            "test_doc_type_dist": dict(Counter(r["doc_type"] for r in test_recs)),
            "metrics": metrics,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Layer 2: qualitative samples (20 random)
    rng = random.Random(SEED)
    sample_indices = rng.sample(range(len(test_recs)), min(NUM_QUAL_SAMPLES, len(test_recs)))
    samples = []
    for idx in sample_indices:
        r = test_recs[idx]
        samples.append({
            "passage_id": r["passage_id"],
            "doc_type": r["doc_type"],
            "summary1": r["summary1"],
            "ground_truth_first_200": r["passage"][:200],
            "generated_first_200": predictions[idx][:200],
            "seed_bigram_overlap": overlap_ratio(r["summary1"], predictions[idx]),
        })

    with (OUT_DIR / "sample_outputs_20.jsonl").open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"[stage1.3] wrote metrics + 20 samples to {OUT_DIR}", flush=True)

    # return summary for report writer
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
