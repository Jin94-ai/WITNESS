"""Stage 2.2 — KoBART fine-tune on Summary2 data.

Per docs/witness_train_directive_2.md §2. Stage 1.2와 동일 (max_input_length만 변경).

Run (Python 3.11, CUDA):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage2_2_train_kobart_v2
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
DATA_DIR = ROOT / "data" / "processed" / "witness_v2"
MODEL_DIR = ROOT / "models" / "kobart_v2"
BEST_DIR = MODEL_DIR / "checkpoint-best"
LOG_PATH = MODEL_DIR / "training_log.json"

MODEL_NAME = "gogamza/kobart-base-v2"
SEED = 42

# Stage 1과 다름: input 256 (S2 174자 + control token 여유)
MAX_INPUT_LEN = 256
MAX_OUTPUT_LEN = 512
BATCH_SIZE = 4
GRAD_ACC = 4               # effective 16
LR = 5e-5
NUM_EPOCHS = 3
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01

DOC_TYPE_TOKENS = ["<fm_drama>", "<fs_drama>"]
EARLY_STOP_PATIENCE = 2


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
    """summary2 → passage."""

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
        input_text = f"{ctrl} Summary: {r['summary2']}"
        enc = self.tok(input_text, max_length=self.mi, truncation=True, padding=False)
        tgt = self.tok(text_target=r["passage"], max_length=self.mo, truncation=True, padding=False)
        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": tgt["input_ids"],
        }


def log_event(log_records: list[dict], **kv) -> None:
    rec = {"ts": round(time.time(), 1), **kv}
    log_records.append(rec)
    LOG_PATH.write_text(json.dumps({"events": log_records}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    set_seed_all(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[stage2.2] device: {device}", flush=True)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[stage2.2] loading tokenizer + model: {MODEL_NAME}", flush=True)
    tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
    added = tokenizer.add_special_tokens({"additional_special_tokens": DOC_TYPE_TOKENS})
    print(f"[stage2.2] added {added} special tokens, vocab={len(tokenizer)}", flush=True)

    model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.resize_token_embeddings(len(tokenizer))
    model.gradient_checkpointing_enable()
    model.to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[stage2.2] params: {n_params:,}", flush=True)

    train_recs = load_jsonl(DATA_DIR / "train.jsonl")
    val_recs = load_jsonl(DATA_DIR / "val.jsonl")
    print(f"[stage2.2] train={len(train_recs)} val={len(val_recs)}", flush=True)

    train_ds = WitnessPairDataset(train_recs, tokenizer, MAX_INPUT_LEN, MAX_OUTPUT_LEN)
    val_ds = WitnessPairDataset(val_recs, tokenizer, MAX_INPUT_LEN, MAX_OUTPUT_LEN)

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="longest", return_tensors="pt")
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collator,
                              num_workers=0, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collator,
                            num_workers=0, pin_memory=True)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    steps_per_epoch = math.ceil(len(train_loader) / GRAD_ACC)
    total_steps = steps_per_epoch * NUM_EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    scaler = GradScaler()

    print(f"[stage2.2] steps_per_epoch={steps_per_epoch}, total_steps={total_steps}", flush=True)

    log_records: list[dict] = []
    log_event(log_records, event="start", model_name=MODEL_NAME, train_size=len(train_ds),
              val_size=len(val_ds), epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, grad_acc=GRAD_ACC,
              effective_batch=BATCH_SIZE * GRAD_ACC, lr=LR, warmup_ratio=WARMUP_RATIO,
              weight_decay=WEIGHT_DECAY, max_input_len=MAX_INPUT_LEN, max_output_len=MAX_OUTPUT_LEN,
              seed=SEED, total_steps=total_steps, n_params=n_params)

    def evaluate(model, loader) -> float:
        model.eval()
        total_loss = 0.0
        total_tokens = 0
        with torch.no_grad():
            for batch in loader:
                batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
                with autocast(dtype=torch.float16):
                    out = model(**batch)
                lbl = batch["labels"]
                n_tok = (lbl != -100).sum().item()
                total_loss += out.loss.item() * n_tok
                total_tokens += n_tok
        model.train()
        return total_loss / max(1, total_tokens)

    best_val = float("inf")
    no_improve = 0
    global_step = 0
    optimizer.zero_grad()
    start_time = time.time()

    for epoch in range(NUM_EPOCHS):
        print(f"[stage2.2] === epoch {epoch+1}/{NUM_EPOCHS} ===", flush=True)
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
                    el = time.time() - epoch_start
                    avg = epoch_loss / epoch_steps
                    lr_now = scheduler.get_last_lr()[0]
                    print(f"[stage2.2] e{epoch+1} step {global_step}/{total_steps} loss={avg:.4f} lr={lr_now:.2e} el={el:.1f}s", flush=True)
                    log_event(log_records, event="step", epoch=epoch+1, step=global_step,
                              avg_loss=round(avg, 4), lr=lr_now)

        train_avg = epoch_loss / max(1, epoch_steps)
        val_loss = evaluate(model, val_loader)
        print(f"[stage2.2] epoch {epoch+1} done. train={train_avg:.4f} val={val_loss:.4f} t={time.time() - epoch_start:.1f}s", flush=True)
        log_event(log_records, event="epoch_end", epoch=epoch+1,
                  train_loss=round(train_avg, 4), val_loss=round(val_loss, 4))

        if val_loss < best_val:
            best_val = val_loss
            no_improve = 0
            BEST_DIR.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(BEST_DIR))
            tokenizer.save_pretrained(str(BEST_DIR))
            print(f"[stage2.2] saved best val={val_loss:.4f}", flush=True)
            log_event(log_records, event="save_best", epoch=epoch+1, val_loss=round(val_loss, 4))
        else:
            no_improve += 1
            print(f"[stage2.2] no improve {no_improve}/{EARLY_STOP_PATIENCE}", flush=True)
            if no_improve >= EARLY_STOP_PATIENCE:
                print(f"[stage2.2] EARLY STOP epoch {epoch+1}", flush=True)
                log_event(log_records, event="early_stop", epoch=epoch+1)
                break

    el = time.time() - start_time
    print(f"[stage2.2] done. total {el/60:.1f} min, best val_loss {best_val:.4f}", flush=True)
    log_event(log_records, event="done", elapsed_min=round(el/60, 1), best_val_loss=round(best_val, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
