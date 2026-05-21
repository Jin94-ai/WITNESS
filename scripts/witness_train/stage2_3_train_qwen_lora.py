"""Stage 2.3 — Qwen2.5-1.5B + LoRA fine-tune on S2 data (4-bit quantized).

Per docs/witness_train_directive_2.md §3.

Causal LM training: input = prompt + target, prompt-token labels masked (-100).
Plain PyTorch loop (Trainer Windows segfault).

Run (Python 3.11, CUDA, ~8GB VRAM):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage2_3_train_qwen_lora
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
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    get_linear_schedule_with_warmup,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "witness_v2"
MODEL_DIR = ROOT / "models" / "qwen15b_lora_v2"
ADAPTER_DIR = MODEL_DIR / "adapter"
LOG_PATH = MODEL_DIR / "training_log.json"

MODEL_NAME = "Qwen/Qwen2.5-1.5B"
SEED = 42

MAX_SEQ_LEN = 1024
BATCH_SIZE = 1
GRAD_ACC = 16         # effective 16
LR = 2e-4
NUM_EPOCHS = 2
WARMUP_RATIO = 0.05
WEIGHT_DECAY = 0.01

DOC_TYPE_TOKENS = ["<fm_drama>", "<fs_drama>"]
EARLY_STOP_PATIENCE = 1   # 큰 모델 짧은 학습이라 patience 작게

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET = ["q_proj", "k_proj", "v_proj", "o_proj"]


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


def build_prompt(doc_type: str, summary2: str) -> str:
    return f"<{doc_type}> Summary: {summary2}\n\nScript:"


class CausalLMPairDataset(Dataset):
    """prompt + target 연결. prompt 부분 labels=-100 마스킹."""

    def __init__(self, records: list[dict], tokenizer, max_seq_len: int) -> None:
        self.records = records
        self.tok = tokenizer
        self.max_len = max_seq_len

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict:
        r = self.records[idx]
        prompt = build_prompt(r["doc_type"], r["summary2"])
        target = " " + r["passage"] + self.tok.eos_token  # leading space, then EOS

        # Encode prompt and target separately to find prompt boundary
        prompt_ids = self.tok(prompt, add_special_tokens=False)["input_ids"]
        target_ids = self.tok(target, add_special_tokens=False)["input_ids"]

        # Truncate target if total exceeds max_len (keep full prompt)
        if len(prompt_ids) >= self.max_len:
            prompt_ids = prompt_ids[: self.max_len - 1]
            target_ids = []
        else:
            target_ids = target_ids[: self.max_len - len(prompt_ids)]

        input_ids = prompt_ids + target_ids
        labels = [-100] * len(prompt_ids) + list(target_ids)  # prompt masked
        attention_mask = [1] * len(input_ids)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def collate(batch: list[dict], pad_token_id: int) -> dict:
    """Right-pad to max length in batch."""
    max_len = max(len(b["input_ids"]) for b in batch)
    input_ids = []
    attention_mask = []
    labels = []
    for b in batch:
        pad = max_len - len(b["input_ids"])
        input_ids.append(b["input_ids"] + [pad_token_id] * pad)
        attention_mask.append(b["attention_mask"] + [0] * pad)
        labels.append(b["labels"] + [-100] * pad)
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }


def log_event(log_records: list[dict], **kv) -> None:
    rec = {"ts": round(time.time(), 1), **kv}
    log_records.append(rec)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps({"events": log_records}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    set_seed_all(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[stage2.3] device: {device}", flush=True)
    if device.type != "cuda":
        print("[stage2.3] FATAL: CUDA required for 4-bit Qwen LoRA", file=sys.stderr)
        return 1

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[stage2.3] loading tokenizer: {MODEL_NAME}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    added = tokenizer.add_special_tokens({"additional_special_tokens": DOC_TYPE_TOKENS})
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"[stage2.3] added {added} special tokens, vocab={len(tokenizer)}", flush=True)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"[stage2.3] loading model in 4-bit...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map={"": 0},
        trust_remote_code=True,
    )
    model.resize_token_embeddings(len(tokenizer))
    print(f"[stage2.3] base model loaded. params (total): {sum(p.numel() for p in model.parameters()):,}", flush=True)

    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, target_modules=LORA_TARGET,
        lora_dropout=LORA_DROPOUT, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.gradient_checkpointing_enable()
    model.print_trainable_parameters()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"[stage2.3] trainable LoRA params: {trainable:,} / total {total:,} ({100*trainable/total:.2f}%)", flush=True)

    train_recs = load_jsonl(DATA_DIR / "train.jsonl")
    val_recs = load_jsonl(DATA_DIR / "val.jsonl")
    print(f"[stage2.3] train={len(train_recs)} val={len(val_recs)}", flush=True)

    train_ds = CausalLMPairDataset(train_recs, tokenizer, MAX_SEQ_LEN)
    val_ds = CausalLMPairDataset(val_recs, tokenizer, MAX_SEQ_LEN)

    pad_id = tokenizer.pad_token_id
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              collate_fn=lambda b: collate(b, pad_id),
                              num_workers=0, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False,
                            collate_fn=lambda b: collate(b, pad_id),
                            num_workers=0, pin_memory=True)

    optimizer = AdamW([p for p in model.parameters() if p.requires_grad], lr=LR, weight_decay=WEIGHT_DECAY)
    steps_per_epoch = math.ceil(len(train_loader) / GRAD_ACC)
    total_steps = steps_per_epoch * NUM_EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    print(f"[stage2.3] steps_per_epoch={steps_per_epoch}, total_steps={total_steps}", flush=True)

    log_records: list[dict] = []
    log_event(log_records, event="start", model_name=MODEL_NAME, train_size=len(train_ds),
              val_size=len(val_ds), epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, grad_acc=GRAD_ACC,
              effective_batch=BATCH_SIZE * GRAD_ACC, lr=LR, warmup_ratio=WARMUP_RATIO,
              weight_decay=WEIGHT_DECAY, max_seq_len=MAX_SEQ_LEN, seed=SEED,
              total_steps=total_steps, trainable_params=trainable, total_params=total,
              lora_r=LORA_R, lora_alpha=LORA_ALPHA, lora_target=LORA_TARGET)

    def evaluate(model, loader) -> float:
        model.eval()
        total_loss = 0.0
        total_tokens = 0
        with torch.no_grad():
            for batch in loader:
                batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
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
        print(f"[stage2.3] === epoch {epoch+1}/{NUM_EPOCHS} ===", flush=True)
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        epoch_start = time.time()
        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
            out = model(**batch)
            loss = out.loss / GRAD_ACC
            loss.backward()
            if (step + 1) % GRAD_ACC == 0 or step + 1 == len(train_loader):
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1
                epoch_loss += loss.item() * GRAD_ACC
                epoch_steps += 1
                if global_step % 20 == 0:
                    el = time.time() - epoch_start
                    avg = epoch_loss / epoch_steps
                    lr_now = scheduler.get_last_lr()[0]
                    print(f"[stage2.3] e{epoch+1} step {global_step}/{total_steps} loss={avg:.4f} lr={lr_now:.2e} el={el:.1f}s", flush=True)
                    log_event(log_records, event="step", epoch=epoch+1, step=global_step,
                              avg_loss=round(avg, 4), lr=lr_now)

        train_avg = epoch_loss / max(1, epoch_steps)
        val_loss = evaluate(model, val_loader)
        print(f"[stage2.3] epoch {epoch+1} done. train={train_avg:.4f} val={val_loss:.4f} t={time.time() - epoch_start:.1f}s", flush=True)
        log_event(log_records, event="epoch_end", epoch=epoch+1,
                  train_loss=round(train_avg, 4), val_loss=round(val_loss, 4))

        if val_loss < best_val:
            best_val = val_loss
            no_improve = 0
            ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(ADAPTER_DIR))   # PEFT saves adapter only
            tokenizer.save_pretrained(str(ADAPTER_DIR))
            print(f"[stage2.3] saved adapter best val={val_loss:.4f}", flush=True)
            log_event(log_records, event="save_best", epoch=epoch+1, val_loss=round(val_loss, 4))
        else:
            no_improve += 1
            print(f"[stage2.3] no improve {no_improve}/{EARLY_STOP_PATIENCE}", flush=True)
            if no_improve >= EARLY_STOP_PATIENCE:
                print(f"[stage2.3] EARLY STOP epoch {epoch+1}", flush=True)
                log_event(log_records, event="early_stop", epoch=epoch+1)
                break

    el = time.time() - start_time
    print(f"[stage2.3] done. total {el/60:.1f} min, best val_loss {best_val:.4f}", flush=True)
    log_event(log_records, event="done", elapsed_min=round(el/60, 1), best_val_loss=round(best_val, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
