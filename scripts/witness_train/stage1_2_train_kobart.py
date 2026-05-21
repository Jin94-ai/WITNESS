"""Stage 1.2 — KoBART baseline fine-tune (gogamza/kobart-base-v2).

Per docs/witness_train_directive_1.md §2.

Plain PyTorch training loop (transformers.Trainer가 Windows에서 import 시 segfault).
fp16 + gradient checkpointing + gradient accumulation 직접 구현.

Run (Python 3.11, CUDA):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage1_2_train_kobart
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    BartForConditionalGeneration,
    PreTrainedTokenizerFast,
    DataCollatorForSeq2Seq,
    get_linear_schedule_with_warmup,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "witness_v1"
MODEL_DIR = ROOT / "models" / "kobart_baseline_v1"
BEST_DIR = MODEL_DIR / "checkpoint-best"
SAMPLE_PATH = MODEL_DIR / "sample_generations.jsonl"
LOG_PATH = MODEL_DIR / "training_log.json"

MODEL_NAME = "gogamza/kobart-base-v2"
SEED = 42

MAX_INPUT_LEN = 128
MAX_OUTPUT_LEN = 512
BATCH_SIZE = 4              # safe for 8GB VRAM with BART-base + fp16 + gradient ckpt
GRAD_ACC = 4                # effective batch 16
LR = 5e-5
NUM_EPOCHS = 3
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01

DOC_TYPE_TOKENS = ["<fm_drama>", "<fs_drama>"]

EARLY_STOP_PATIENCE = 2     # eval loss 2 epoch 연속 증가 시 중단


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


class WitnessPairDataset(Dataset):
    def __init__(self, records: list[dict], tokenizer, max_input_len: int, max_output_len: int) -> None:
        self.records = records
        self.tok = tokenizer
        self.mi = max_input_len
        self.mo = max_output_len

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict:
        r = self.records[idx]
        ctrl = f"<{r['doc_type']}>"
        input_text = f"{ctrl} Summary: {r['summary1']}"
        enc = self.tok(input_text, max_length=self.mi, truncation=True, padding=False)
        tgt = self.tok(text_target=r["passage"], max_length=self.mo, truncation=True, padding=False)
        # BART는 token_type_ids 받지 않음 — 명시적으로 제거
        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": tgt["input_ids"],
        }


def log_event(log_records: list[dict], **kv) -> None:
    rec = {"ts": round(time.time(), 1), **kv}
    log_records.append(rec)
    # also dump
    LOG_PATH.write_text(json.dumps({"events": log_records}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    set_seed_all(SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[stage1.2] device: {device}", flush=True)
    if device.type != "cuda":
        print("[stage1.2] WARNING: no CUDA available, will be very slow", flush=True)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[stage1.2] loading tokenizer + model: {MODEL_NAME}", flush=True)
    tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
    added = tokenizer.add_special_tokens({"additional_special_tokens": DOC_TYPE_TOKENS})
    print(f"[stage1.2] added {added} special tokens, vocab_size={len(tokenizer)}", flush=True)

    model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.resize_token_embeddings(len(tokenizer))
    model.gradient_checkpointing_enable()
    model.to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"[stage1.2] model params: {n_params:,}", flush=True)

    train_recs = load_jsonl(DATA_DIR / "train.jsonl")
    val_recs = load_jsonl(DATA_DIR / "val.jsonl")
    print(f"[stage1.2] train={len(train_recs)} val={len(val_recs)}", flush=True)

    train_ds = WitnessPairDataset(train_recs, tokenizer, MAX_INPUT_LEN, MAX_OUTPUT_LEN)
    val_ds = WitnessPairDataset(val_recs, tokenizer, MAX_INPUT_LEN, MAX_OUTPUT_LEN)

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="longest", return_tensors="pt")

    train_loader = DataLoader(
        train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collator,
        num_workers=0, pin_memory=True, drop_last=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collator,
        num_workers=0, pin_memory=True,
    )

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    steps_per_epoch = math.ceil(len(train_loader) / GRAD_ACC)
    total_steps = steps_per_epoch * NUM_EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler = GradScaler()

    print(f"[stage1.2] steps_per_epoch={steps_per_epoch}, total_steps={total_steps}", flush=True)

    log_records: list[dict] = []
    log_event(log_records,
              event="start",
              model_name=MODEL_NAME,
              train_size=len(train_ds), val_size=len(val_ds),
              epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, grad_acc=GRAD_ACC,
              effective_batch=BATCH_SIZE * GRAD_ACC,
              lr=LR, warmup_ratio=WARMUP_RATIO, weight_decay=WEIGHT_DECAY,
              max_input_len=MAX_INPUT_LEN, max_output_len=MAX_OUTPUT_LEN, seed=SEED,
              total_steps=total_steps, n_params=n_params)

    sample_rng = random.Random(SEED)
    sample_every = max(1, total_steps // 20)  # 5% steps
    sample_records: list[dict] = []

    def write_samples():
        with SAMPLE_PATH.open("w", encoding="utf-8") as f:
            for rec in sample_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def evaluate(model, loader) -> float:
        model.eval()
        total_loss = 0.0
        total_tokens = 0
        with torch.no_grad():
            for batch in loader:
                batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
                with autocast(dtype=torch.float16):
                    out = model(**batch)
                # weight by # of non-pad labels
                lbl = batch["labels"]
                n_tok = (lbl != -100).sum().item()
                total_loss += out.loss.item() * n_tok
                total_tokens += n_tok
        return total_loss / max(1, total_tokens)

    def sample_generate(rec: dict) -> str:
        model.eval()
        with torch.no_grad():
            input_text = f"<{rec['doc_type']}> Summary: {rec['summary1']}"
            enc = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=MAX_INPUT_LEN).to(device)
            ids = model.generate(
                **enc,
                max_length=MAX_OUTPUT_LEN,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        gen = tokenizer.decode(ids[0], skip_special_tokens=True)
        model.train()
        return gen

    best_val_loss = float("inf")
    no_improve = 0
    global_step = 0
    optimizer.zero_grad()

    start_time = time.time()
    for epoch in range(NUM_EPOCHS):
        print(f"[stage1.2] === epoch {epoch + 1}/{NUM_EPOCHS} ===", flush=True)
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        epoch_start = time.time()
        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
            with autocast(dtype=torch.float16):
                out = model(**batch)
                loss = out.loss / GRAD_ACC
            scaler.scale(loss).backward()

            if (step + 1) % GRAD_ACC == 0 or step + 1 == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1
                epoch_loss += loss.item() * GRAD_ACC
                epoch_steps += 1

                if global_step % 50 == 0:
                    elapsed = time.time() - epoch_start
                    avg_loss = epoch_loss / epoch_steps
                    lr_now = scheduler.get_last_lr()[0]
                    print(f"[stage1.2] epoch {epoch+1} step {global_step}/{total_steps} loss={avg_loss:.4f} lr={lr_now:.2e} elapsed={elapsed:.1f}s", flush=True)
                    log_event(log_records, event="step", epoch=epoch + 1, step=global_step,
                              avg_loss=round(avg_loss, 4), lr=lr_now)

                if global_step % sample_every == 0:
                    try:
                        rec = sample_rng.choice(val_recs)
                        gen = sample_generate(rec)
                        sample_records.append({
                            "step": global_step,
                            "passage_id": rec["passage_id"],
                            "doc_type": rec["doc_type"],
                            "summary1": rec["summary1"],
                            "ground_truth_first_200": rec["passage"][:200],
                            "generated_first_200": gen[:200],
                        })
                        write_samples()
                    except Exception as e:
                        print(f"[stage1.2] sample-gen step {global_step} error: {e}", flush=True)

        # end of epoch — eval
        train_avg = epoch_loss / max(1, epoch_steps)
        val_loss = evaluate(model, val_loader)
        print(f"[stage1.2] epoch {epoch+1} done. train_loss={train_avg:.4f} val_loss={val_loss:.4f} time={time.time() - epoch_start:.1f}s", flush=True)
        log_event(log_records, event="epoch_end", epoch=epoch + 1,
                  train_loss=round(train_avg, 4), val_loss=round(val_loss, 4))

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            no_improve = 0
            BEST_DIR.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(BEST_DIR))
            tokenizer.save_pretrained(str(BEST_DIR))
            print(f"[stage1.2] saved new best val_loss={val_loss:.4f} → {BEST_DIR}", flush=True)
            log_event(log_records, event="save_best", epoch=epoch + 1, val_loss=round(val_loss, 4))
        else:
            no_improve += 1
            print(f"[stage1.2] no improvement (patience {no_improve}/{EARLY_STOP_PATIENCE})", flush=True)
            if no_improve >= EARLY_STOP_PATIENCE:
                print(f"[stage1.2] EARLY STOP at epoch {epoch + 1}", flush=True)
                log_event(log_records, event="early_stop", epoch=epoch + 1)
                break

    elapsed = time.time() - start_time
    print(f"[stage1.2] training done. total time {elapsed/60:.1f} min, best val_loss {best_val_loss:.4f}", flush=True)
    log_event(log_records, event="done", elapsed_min=round(elapsed / 60, 1), best_val_loss=round(best_val_loss, 4))
    write_samples()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
