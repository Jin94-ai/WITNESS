"""Stage 2.4 — Evaluation v2: batched generation + resumable predictions.

Per docs/witness_train_directive_2.md §4.

수정 (v1 대비):
  - KoBART: batch 8 (was 4)
  - Qwen: batched + left-padding (was batch 1 → 너무 느림, ~25s/item)
  - predictions를 JSONL로 즉시 저장 → 재실행 시 generation skip (resumable)

3 layer auto metrics:
  Layer 1: BLEU / ROUGE / perplexity / length / overlap
  Layer 2: 20 random qualitative samples (KoBART v2 + Qwen LoRA outputs)
  Layer 3: failure mode auto-metrics (self_loop / morpheme_repeat / name_hallucination)
  Layer 4: Stage 1 KoBART failure re-measurement on v1 sample 20

Run (Python 3.11, CUDA):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage2_4_eval
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BartForConditionalGeneration,
    BitsAndBytesConfig,
    PreTrainedTokenizerFast,
    DataCollatorForSeq2Seq,
)
from peft import PeftModel

ROOT = Path(__file__).resolve().parents[2]
V2_DATA = ROOT / "data" / "processed" / "witness_v2"
KOBART_V2 = ROOT / "models" / "kobart_v2" / "checkpoint-best"
QWEN_ADAPTER = ROOT / "models" / "qwen15b_lora_v2" / "adapter"
QWEN_BASE = "Qwen/Qwen2.5-1.5B"

OUT_DIR = ROOT / "docs" / "results" / "witness_train_v2"
PRED_KOBART = OUT_DIR / "_preds_kobart_v2.jsonl"
PRED_QWEN = OUT_DIR / "_preds_qwen_lora.jsonl"

SEED = 42
NUM_QUAL_SAMPLES = 20

MAX_INPUT_LEN_BART = 256
MAX_OUTPUT_LEN_BART = 512
MAX_NEW_TOKENS_QWEN = 512
KOBART_GEN_BATCH = 8
QWEN_GEN_BATCH = 8


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


def save_preds(path: Path, preds: list[str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps({"pred": p}, ensure_ascii=False) + "\n")


def load_preds(path: Path) -> list[str]:
    return [json.loads(line)["pred"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_bart_input(r: dict) -> str:
    return f"<{r['doc_type']}> Summary: {r['summary2']}"


def build_qwen_prompt(r: dict) -> str:
    return f"<{r['doc_type']}> Summary: {r['summary2']}\n\nScript:"


# ---------- KoBART generation (batched) ----------

def generate_bart(model, tokenizer, records, device, batch_size=KOBART_GEN_BATCH) -> list[str]:
    out: list[str] = []
    model.eval()
    with torch.no_grad():
        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            inputs = [build_bart_input(r) for r in chunk]
            enc = tokenizer(inputs, padding=True, truncation=True,
                            max_length=MAX_INPUT_LEN_BART, return_tensors="pt").to(device)
            ids = model.generate(
                input_ids=enc.input_ids, attention_mask=enc.attention_mask,
                max_length=MAX_OUTPUT_LEN_BART, num_beams=4, length_penalty=1.0,
                no_repeat_ngram_size=3, early_stopping=True,
            )
            for j in range(ids.size(0)):
                out.append(tokenizer.decode(ids[j], skip_special_tokens=True))
            if (i // batch_size) % 20 == 0:
                print(f"[gen-bart] {i + len(chunk)}/{len(records)}", flush=True)
    return out


def perplexity_bart(model, tokenizer, records, device, batch_size=8) -> float:
    model.eval()
    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="longest", return_tensors="pt")
    total_loss = 0.0
    total_tokens = 0

    def feat(r):
        enc = tokenizer(build_bart_input(r), max_length=MAX_INPUT_LEN_BART, truncation=True, padding=False)
        tgt = tokenizer(text_target=r["passage"], max_length=MAX_OUTPUT_LEN_BART, truncation=True, padding=False)
        return {"input_ids": enc["input_ids"], "attention_mask": enc["attention_mask"], "labels": tgt["input_ids"]}

    feats = [feat(r) for r in records]
    with torch.no_grad():
        for i in range(0, len(feats), batch_size):
            batch = collator(feats[i : i + batch_size])
            batch = {k: v.to(device) for k, v in batch.items()}
            out = model(**batch)
            n_tok = (batch["labels"] != -100).sum().item()
            total_loss += out.loss.item() * n_tok
            total_tokens += n_tok
            if (i // batch_size) % 50 == 0:
                print(f"[ppl-bart] {i + len(feats[i:i+batch_size])}/{len(feats)}", flush=True)
    return math.exp(min(20, total_loss / max(1, total_tokens)))


# ---------- Qwen generation (batched, left-padded) ----------

def generate_qwen(model, tokenizer, records, device, batch_size=QWEN_GEN_BATCH) -> list[str]:
    out: list[str] = []
    model.eval()
    # decoder-only → left padding for generation
    orig_side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    try:
        with torch.no_grad():
            for i in range(0, len(records), batch_size):
                chunk = records[i : i + batch_size]
                prompts = [build_qwen_prompt(r) for r in chunk]
                enc = tokenizer(prompts, return_tensors="pt", padding=True,
                                truncation=True, max_length=512).to(device)
                ids = model.generate(
                    input_ids=enc.input_ids, attention_mask=enc.attention_mask,
                    max_new_tokens=MAX_NEW_TOKENS_QWEN, do_sample=False, num_beams=1,
                    no_repeat_ngram_size=3,
                    eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id,
                )
                gen_only = ids[:, enc.input_ids.size(1):]
                for j in range(gen_only.size(0)):
                    out.append(tokenizer.decode(gen_only[j], skip_special_tokens=True))
                if (i // batch_size) % 10 == 0:
                    print(f"[gen-qwen] {i + len(chunk)}/{len(records)}", flush=True)
    finally:
        tokenizer.padding_side = orig_side
    return out


def perplexity_qwen(model, tokenizer, records, device) -> float:
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for i, r in enumerate(records):
            prompt = build_qwen_prompt(r)
            target = " " + r["passage"] + tokenizer.eos_token
            prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            target_ids = tokenizer(target, add_special_tokens=False)["input_ids"]
            input_ids = prompt_ids + target_ids
            labels = [-100] * len(prompt_ids) + list(target_ids)
            if len(input_ids) > 1024:
                input_ids = input_ids[:1024]
                labels = labels[:1024]
            t_in = torch.tensor([input_ids], dtype=torch.long, device=device)
            t_lab = torch.tensor([labels], dtype=torch.long, device=device)
            t_am = torch.ones_like(t_in)
            out = model(input_ids=t_in, attention_mask=t_am, labels=t_lab)
            n_tok = (t_lab != -100).sum().item()
            total_loss += out.loss.item() * n_tok
            total_tokens += n_tok
            if i % 200 == 0:
                print(f"[ppl-qwen] {i+1}/{len(records)}", flush=True)
    return math.exp(min(20, total_loss / max(1, total_tokens)))


# ---------- Metrics ----------

def compute_bleu_rouge(predictions, references) -> dict:
    import sacrebleu
    from rouge_score import rouge_scorer
    bleu = sacrebleu.corpus_bleu(predictions, [references])
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
    r1, r2, rl = [], [], []
    for p, ref in zip(predictions, references):
        s = scorer.score(ref, p)
        r1.append(s["rouge1"].fmeasure)
        r2.append(s["rouge2"].fmeasure)
        rl.append(s["rougeL"].fmeasure)
    return {
        "bleu4": round(bleu.score, 4), "bleu4_bp": round(bleu.bp, 4),
        "rouge1_f": round(float(np.mean(r1)), 4),
        "rouge2_f": round(float(np.mean(r2)), 4),
        "rougeL_f": round(float(np.mean(rl)), 4),
    }


def overlap_ratio(seed: str, generated: str) -> float:
    if not seed or not generated:
        return 0.0
    sb = set(seed[i:i+2] for i in range(len(seed) - 1) if seed[i:i+2].strip())
    gb = set(generated[i:i+2] for i in range(len(generated) - 1) if generated[i:i+2].strip())
    return len(sb & gb) / len(sb) if sb else 0.0


_NAME_PATTERN = re.compile(r"([가-힣]{1,4})\]")
_TRIGRAM_REPEAT_MIN = 5
_COMMON_NAMES = {"해설", "여보", "어머", "엄마", "아빠", "아버지", "어머니", "오빠", "언니",
                 "동생", "할머니", "할아버지", "남편", "아내", "사장", "회장", "이사", "부장",
                 "선생", "선생님"}


def detect_morpheme_repeat(text: str) -> bool:
    if not text or len(text) < 6:
        return False
    counts: Counter[str] = Counter()
    for i in range(len(text) - 2):
        s = text[i:i+3]
        if re.fullmatch(r"[가-힣]{3}", s):
            counts[s] += 1
    return any(c >= _TRIGRAM_REPEAT_MIN for c in counts.values())


def detect_self_loop(text: str) -> bool:
    if not text:
        return False
    for s in re.split(r"[.!?\n]", text):
        names = _NAME_PATTERN.findall(s)
        if len(names) >= 2 and max(Counter(names).values()) >= 2:
            return True
    return False


def detect_name_hallucination(seed: str, gen: str) -> bool:
    seed_tokens = set(re.findall(r"[가-힣]{2,4}", seed))
    gen_names = set(_NAME_PATTERN.findall(gen))
    novel = gen_names - seed_tokens - _COMMON_NAMES
    return len(novel) > 0


def compute_failure_metrics(records, predictions, seed_key="summary2") -> dict:
    n = len(records)
    if n == 0:
        return {}
    sl = sum(detect_self_loop(p) for p in predictions)
    mr = sum(detect_morpheme_repeat(p) for p in predictions)
    nh = sum(detect_name_hallucination(r[seed_key], p) for r, p in zip(records, predictions))
    return {
        "self_loop_count": sl, "self_loop_rate": round(sl / n, 4),
        "morpheme_repeat_count": mr, "morpheme_repeat_rate": round(mr / n, 4),
        "name_hallucination_count": nh, "name_hallucination_rate": round(nh / n, 4),
    }


# ---------- Main ----------

def main() -> int:
    set_seed_all(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[stage2.4] device={device}", flush=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    test_recs = load_jsonl(V2_DATA / "test.jsonl")
    references = [r["passage"] for r in test_recs]
    print(f"[stage2.4] v2 test set: {len(test_recs)} pairs", flush=True)

    results = {
        "schema_version": "stage2_eval_v1",
        "v2_test_size": len(test_recs),
        "test_doc_type_dist": dict(Counter(r["doc_type"] for r in test_recs)),
        "metrics": {}, "failure_metrics": {},
        "model_paths": {
            "kobart_v2": str(KOBART_V2.relative_to(ROOT)).replace("\\", "/"),
            "qwen_lora": str(QWEN_ADAPTER.relative_to(ROOT)).replace("\\", "/"),
        },
        "generation_config": {
            "kobart": {"num_beams": 4, "no_repeat_ngram_size": 3, "max_length": MAX_OUTPUT_LEN_BART},
            "qwen": {"greedy": True, "no_repeat_ngram_size": 3, "max_new_tokens": MAX_NEW_TOKENS_QWEN},
        },
    }

    # ===== KoBART v2 =====
    print("\n[stage2.4] === KoBART v2 ===", flush=True)
    if PRED_KOBART.exists():
        kbart_preds = load_preds(PRED_KOBART)
        print(f"[stage2.4] loaded {len(kbart_preds)} cached KoBART preds", flush=True)
        bart_tok = PreTrainedTokenizerFast.from_pretrained(str(KOBART_V2))
        bart_model = BartForConditionalGeneration.from_pretrained(str(KOBART_V2)).to(device).eval()
    else:
        bart_tok = PreTrainedTokenizerFast.from_pretrained(str(KOBART_V2))
        bart_model = BartForConditionalGeneration.from_pretrained(str(KOBART_V2)).to(device).eval()
        t0 = time.time()
        kbart_preds = generate_bart(bart_model, bart_tok, test_recs, device)
        print(f"[stage2.4] kobart_v2 gen done. {time.time()-t0:.1f}s", flush=True)
        save_preds(PRED_KOBART, kbart_preds)

    kbart_metrics = compute_bleu_rouge(kbart_preds, references)
    print(f"[stage2.4] kobart_v2 bleu/rouge: {kbart_metrics}", flush=True)
    ppl = perplexity_bart(bart_model, bart_tok, test_recs, device)
    kbart_metrics["test_perplexity"] = round(ppl, 4)
    print(f"[stage2.4] kobart_v2 perplexity: {ppl:.4f}", flush=True)
    plens = [len(p) for p in kbart_preds]
    kbart_metrics["pred_length_mean"] = round(float(np.mean(plens)), 1)
    kbart_metrics["pred_length_median"] = int(np.median(plens))
    ovs = [overlap_ratio(r["summary2"], p) for r, p in zip(test_recs, kbart_preds)]
    kbart_metrics["seed_overlap_mean"] = round(float(np.mean(ovs)), 4)
    kbart_fail = compute_failure_metrics(test_recs, kbart_preds)
    print(f"[stage2.4] kobart_v2 failure: {kbart_fail}", flush=True)
    results["metrics"]["kobart_v2"] = kbart_metrics
    results["failure_metrics"]["kobart_v2"] = kbart_fail
    (OUT_DIR / "stage2_eval.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    del bart_model
    torch.cuda.empty_cache()

    # ===== Qwen LoRA =====
    print("\n[stage2.4] === Qwen LoRA ===", flush=True)
    qwen_tok = AutoTokenizer.from_pretrained(str(QWEN_ADAPTER), trust_remote_code=True)
    if qwen_tok.pad_token is None:
        qwen_tok.pad_token = qwen_tok.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    base = AutoModelForCausalLM.from_pretrained(QWEN_BASE, quantization_config=bnb,
                                                device_map={"": 0}, trust_remote_code=True)
    base.resize_token_embeddings(len(qwen_tok))
    qwen_model = PeftModel.from_pretrained(base, str(QWEN_ADAPTER)).eval()
    print("[stage2.4] qwen loaded", flush=True)

    if PRED_QWEN.exists():
        qwen_preds = load_preds(PRED_QWEN)
        print(f"[stage2.4] loaded {len(qwen_preds)} cached Qwen preds", flush=True)
    else:
        t0 = time.time()
        qwen_preds = generate_qwen(qwen_model, qwen_tok, test_recs, device)
        print(f"[stage2.4] qwen gen done. {time.time()-t0:.1f}s", flush=True)
        save_preds(PRED_QWEN, qwen_preds)

    qwen_metrics = compute_bleu_rouge(qwen_preds, references)
    print(f"[stage2.4] qwen bleu/rouge: {qwen_metrics}", flush=True)
    ppl = perplexity_qwen(qwen_model, qwen_tok, test_recs, device)
    qwen_metrics["test_perplexity"] = round(ppl, 4)
    print(f"[stage2.4] qwen perplexity: {ppl:.4f}", flush=True)
    plens = [len(p) for p in qwen_preds]
    qwen_metrics["pred_length_mean"] = round(float(np.mean(plens)), 1)
    qwen_metrics["pred_length_median"] = int(np.median(plens))
    ovs = [overlap_ratio(r["summary2"], p) for r, p in zip(test_recs, qwen_preds)]
    qwen_metrics["seed_overlap_mean"] = round(float(np.mean(ovs)), 4)
    qwen_fail = compute_failure_metrics(test_recs, qwen_preds)
    print(f"[stage2.4] qwen failure: {qwen_fail}", flush=True)
    results["metrics"]["qwen_lora"] = qwen_metrics
    results["failure_metrics"]["qwen_lora"] = qwen_fail
    (OUT_DIR / "stage2_eval.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    del qwen_model, base
    torch.cuda.empty_cache()

    # ===== Layer 4: Stage 1 KoBART failure re-measurement =====
    print("\n[stage2.4] === Stage 1 KoBART failure re-measurement (v1 sample 20) ===", flush=True)
    v1_path = ROOT / "docs" / "results" / "witness_train_v1" / "sample_outputs_20.jsonl"
    if v1_path.exists():
        v1 = load_jsonl(v1_path)
        v1_preds = [s.get("generated_first_200", "") for s in v1]
        v1_recs = [{"summary1": s.get("summary1", ""), "doc_type": s.get("doc_type", "")} for s in v1]
        v1_fail = compute_failure_metrics(v1_recs, v1_preds, seed_key="summary1")
        results["failure_metrics"]["kobart_v1_sample20"] = v1_fail
        print(f"[stage2.4] kobart_v1 sample20 failure: {v1_fail}", flush=True)

    # ===== Layer 2: 20 qualitative samples =====
    print("\n[stage2.4] === 20 random qualitative samples ===", flush=True)
    rng = random.Random(SEED)
    indices = rng.sample(range(len(test_recs)), min(NUM_QUAL_SAMPLES, len(test_recs)))
    samples = []
    for idx in indices:
        r = test_recs[idx]
        samples.append({
            "passage_id": r["passage_id"], "doc_type": r["doc_type"], "doc_origin": r["doc_origin"],
            "summary2": r["summary2"],
            "ground_truth_300": r["passage"][:300],
            "kobart_v2_300": kbart_preds[idx][:300],
            "qwen_lora_300": qwen_preds[idx][:300],
            "kobart_v2_overlap": round(overlap_ratio(r["summary2"], kbart_preds[idx]), 4),
            "qwen_lora_overlap": round(overlap_ratio(r["summary2"], qwen_preds[idx]), 4),
        })
    with (OUT_DIR / "sample_outputs_20.jsonl").open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    results["qual_sample_indices"] = indices
    (OUT_DIR / "stage2_eval.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "failure_metrics.json").write_text(json.dumps(results["failure_metrics"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[stage2.4] wrote eval outputs to {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
