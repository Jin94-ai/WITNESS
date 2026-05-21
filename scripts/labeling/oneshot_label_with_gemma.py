"""ONESHOT Gemma 4 E4B labeling — Stage 1 only (10 passages).

Per docs/witness_gemma_labeling_directive.md.

Run:
    python -m scripts.labeling.oneshot_label_with_gemma --stage 1

NOT a reusable framework. Stage 2/3는 별도 directive.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ollama

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import preprocess_entry

ROOT = Path(__file__).resolve().parents[2]
TL1_ZIP = ROOT / "data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/1.Training/라벨링데이터/TL1.zip"
OUTPUT_DIR = ROOT / "data" / "labeled"
PRIVATE_REVIEW_DIR = ROOT / "data" / "external_private" / "gemma_review"

# 작업 대상
TARGET_DOC_ORIGIN_BASE = "미우나고우나"
TARGET_ANONYMIZED = "work_e46069c4b4"  # SHA256[:10] of TARGET_DOC_ORIGIN_BASE
TARGET_DOC_TYPE = "fm_drama"
TARGET_YEAR = "2007"

MODEL_NAME = "gemma4:e4b"
RANDOM_SEED = 42
STAGE1_SAMPLE_SIZE = 10

# Generation params (directive §5.3)
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 64

# Per-call timeout (seconds). Gemma 4 E4B 평균 ~10-30s/passage 예상.
PER_CALL_TIMEOUT = 120.0


SYSTEM_PROMPT = """당신은 한국 드라마 씬을 분석하는 narrative analyst다.
각 씬(passage)을 읽고 universal taxonomy로 라벨링한다.

규칙:
1. JSON only로 응답. 자유 텍스트 금지.
2. characters는 씬에 등장하는 한국어 이름만.
3. primary_pressures는 가장 두드러진 1~2개 선택.
4. secondary_pressures는 0~2개 (없으면 빈 배열).
5. primary_desires는 1~2개.
6. conflict_axis는 정확히 1개 선택. 명확하지 않으면 "unknown".
7. confidence는 0.0~1.0 (씬이 명확할수록 높음).
8. reasoning_brief는 1~2문장 한국어 근거."""


USER_PROMPT_TEMPLATE = """다음은 한국 드라마의 한 씬이다.

[작품 정보]
연도: 2007
장르: 가족 드라마 (KBS 일일극)

[Taxonomy 정의]
Pressures:
  - fear: 위협/처벌 회피
  - shame_self: 수치심
  - hope: 보상에 대한 끌림
  - grief: 상실의 무게
  - confusion: 해석 불안정
  - love: 타자에 대한 애착
  - authority_vigilance: 권위자의 시선
  - public_suspicion: 사람들의 의심
  - blame_concentration: 비난이 한쪽으로 몰림
  - group_tension: 집단 분열
  - crowd_mood: 주변 분위기

Desires:
  - loyalty: 곁에 남으려는 마음
  - survival: 자기 보호
  - control: 통제 의지
  - exposure_avoidance: 드러나지 않으려는 마음
  - identity_preservation: 이름을 지키려는 마음
  - commitment: 결정하려는 의지
  - trust: 관계를 지키려는 마음
  - group_safety: 그룹 안전

Conflict Axes:
  - loyalty_vs_survival
  - uncertainty_vs_commitment
  - control_vs_exposure
  - collective_fear_vs_scapegoating
  - identity_vs_failure
  - atmosphere_vs_action
  - trust_vs_self_protection
  - unknown

[Few-shot 예시]
예시 passage: "엄마, 진짜 결혼할 거야. 어머니가 반대해도 동지를 포기 못합니다."
예시 출력:
{{
  "characters": ["만수", "어머니"],
  "primary_pressures": ["authority_vigilance"],
  "secondary_pressures": [],
  "primary_desires": ["love", "commitment"],
  "secondary_desires": [],
  "conflict_axis": "uncertainty_vs_commitment",
  "confidence": 0.85,
  "reasoning_brief": "어머니의 반대(권위 압박)에도 만수가 사랑하는 사람을 포기 못한다는 결정"
}}

[분석할 passage]
{PASSAGE_TEXT}

JSON으로만 응답하시오."""


# --- 유효 taxonomy (검증용) ---
VALID_PRESSURES = {
    "fear", "shame_self", "hope", "grief", "confusion", "love",
    "authority_vigilance", "public_suspicion", "blame_concentration",
    "group_tension", "crowd_mood",
}
VALID_DESIRES = {
    "loyalty", "survival", "control", "exposure_avoidance",
    "identity_preservation", "commitment", "trust", "group_safety",
}
VALID_CONFLICT_AXES = {
    "loyalty_vs_survival", "uncertainty_vs_commitment",
    "control_vs_exposure", "collective_fear_vs_scapegoating",
    "identity_vs_failure", "atmosphere_vs_action",
    "trust_vs_self_protection", "unknown",
}


def extract_target_passages() -> list[dict]:
    """TL1.zip에서 doc_origin_base == 미우나고우나 인 valid passages 추출."""
    print(f"[extract] loading TL1.zip (filter doc_origin_base == {TARGET_DOC_ORIGIN_BASE})...", file=sys.stderr)
    out: list[dict] = []
    for raw in stream_aihub_023(TL1_ZIP, categories=[TARGET_DOC_TYPE]):
        pp = preprocess_entry(raw)
        if pp["doc_origin_base"] == TARGET_DOC_ORIGIN_BASE and pp["is_valid"]:
            out.append(pp)
    print(f"[extract] {len(out)} valid passages found", file=sys.stderr)
    return out


def label_passage(passage_text: str, *, model: str = MODEL_NAME) -> tuple[dict, str]:
    """단일 passage 라벨링. (parsed_dict_or_error, raw_content)."""
    user_prompt = USER_PROMPT_TEMPLATE.replace("{PASSAGE_TEXT}", passage_text)
    raw_content = ""
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "top_k": TOP_K,
            },
            format="json",
        )
        raw_content = response["message"]["content"]
        parsed = json.loads(raw_content)
        return parsed, raw_content
    except json.JSONDecodeError as e:
        return {"_error": "json_parse", "_error_msg": str(e)}, raw_content
    except Exception as e:
        return {"_error": "ollama", "_error_msg": str(e)}, raw_content


def validate_schema(label: dict) -> dict:
    """schema/taxonomy 검증. returns dict of issues (empty = OK)."""
    issues: dict = {}
    required = ["characters", "primary_pressures", "secondary_pressures",
                "primary_desires", "secondary_desires", "conflict_axis",
                "confidence", "reasoning_brief"]
    missing = [k for k in required if k not in label]
    if missing:
        issues["missing_fields"] = missing

    # taxonomy validity
    for k in ("primary_pressures", "secondary_pressures"):
        vals = label.get(k, []) or []
        invalid = [v for v in vals if v not in VALID_PRESSURES]
        if invalid:
            issues.setdefault("invalid_pressures", []).extend(invalid)
    for k in ("primary_desires", "secondary_desires"):
        vals = label.get(k, []) or []
        invalid = [v for v in vals if v not in VALID_DESIRES]
        if invalid:
            issues.setdefault("invalid_desires", []).extend(invalid)
    axis = label.get("conflict_axis", "")
    if axis and axis not in VALID_CONFLICT_AXES:
        issues["invalid_conflict_axis"] = axis

    # confidence range
    conf = label.get("confidence")
    if conf is not None and not (isinstance(conf, (int, float)) and 0.0 <= float(conf) <= 1.0):
        issues["invalid_confidence"] = conf

    return issues


def run_stage1() -> dict:
    """Stage 1 실행. returns summary dict."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    all_passages = extract_target_passages()
    if not all_passages:
        return {"error": "no passages found", "target": TARGET_DOC_ORIGIN_BASE}

    print(f"[stage1] sampling {STAGE1_SAMPLE_SIZE} of {len(all_passages)} (seed={RANDOM_SEED})", file=sys.stderr)
    rng = random.Random(RANDOM_SEED)
    sample_pool = sorted(all_passages, key=lambda e: e["passage_id"])
    sampled = rng.sample(sample_pool, STAGE1_SAMPLE_SIZE)

    # warm-up call (모델 로딩 시간 분리)
    print("[stage1] warming up gemma4:e4b...", file=sys.stderr)
    t_wu = time.time()
    label_passage("테스트 씬: 두 사람이 말없이 서 있다.")
    print(f"[stage1] warmup done in {time.time()-t_wu:.1f}s", file=sys.stderr)

    out_path = OUTPUT_DIR / "work_e46069c4b4_stage1.jsonl"
    private_path = PRIVATE_REVIEW_DIR / "work_e46069c4b4_stage1_private.jsonl"
    results: list[dict] = []
    private_records: list[dict] = []
    t_total_start = time.time()
    success = 0
    json_parse_failed = 0
    schema_invalid = 0
    taxonomy_invalid = 0
    ollama_errors = 0

    with out_path.open("w", encoding="utf-8") as f, private_path.open("w", encoding="utf-8") as fp:
        for i, p in enumerate(sampled, 1):
            t_start = time.time()
            print(f"[stage1] {i}/{STAGE1_SAMPLE_SIZE}: {p['passage_id']} (len={p['passage_length']})", file=sys.stderr)
            label, raw_content = label_passage(p["passage"])
            elapsed = round(time.time() - t_start, 2)

            issues = {}
            if "_error" in label:
                if label["_error"] == "json_parse":
                    json_parse_failed += 1
                elif label["_error"] == "ollama":
                    ollama_errors += 1
            else:
                issues = validate_schema(label)
                if "missing_fields" in issues:
                    schema_invalid += 1
                taxonomy_keys = {"invalid_pressures", "invalid_desires", "invalid_conflict_axis"}
                if any(k in issues for k in taxonomy_keys):
                    taxonomy_invalid += 1
                if not issues:
                    success += 1

            # public-safe record (no raw passage)
            public_rec = {
                "passage_id": p["passage_id"],
                "passage_length": p["passage_length"],
                "label": label,
                "validation_issues": issues,
                "elapsed_sec": elapsed,
                "model": MODEL_NAME,
                "stage": "stage1",
                "index": i,
            }
            f.write(json.dumps(public_rec, ensure_ascii=False) + "\n")
            results.append(public_rec)

            # private record (raw passage included)
            private_rec = {
                **public_rec,
                "passage": p["passage"],
                "doc_origin_raw": p["doc_origin_raw"],
                "doc_origin_base": p["doc_origin_base"],
                "anonymized_origin": TARGET_ANONYMIZED,
                "raw_gemma_content": raw_content,
            }
            fp.write(json.dumps(private_rec, ensure_ascii=False) + "\n")
            private_records.append(private_rec)

    t_total = round(time.time() - t_total_start, 2)

    summary = {
        "stage": "stage1",
        "target_work": TARGET_ANONYMIZED,
        "target_year": TARGET_YEAR,
        "target_doc_type": TARGET_DOC_TYPE,
        "model": MODEL_NAME,
        "params": {"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K},
        "sample_seed": RANDOM_SEED,
        "total_processed": len(sampled),
        "success": success,
        "json_parse_failed": json_parse_failed,
        "schema_invalid": schema_invalid,
        "taxonomy_invalid": taxonomy_invalid,
        "ollama_errors": ollama_errors,
        "total_runtime_sec": t_total,
        "avg_seconds_per_passage": round(t_total / max(1, len(sampled)), 2),
        "output_public": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "output_private": str(private_path.relative_to(ROOT)).replace("\\", "/"),
        "completed_at_iso": datetime.now(timezone.utc).isoformat(),
    }

    # write summary
    summary_path = OUTPUT_DIR / "work_e46069c4b4_stage1_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", type=int, default=1, choices=[1])
    args = parser.parse_args(argv)

    if args.stage != 1:
        print("Only Stage 1 supported in this oneshot. Stage 2/3는 별도 directive.", file=sys.stderr)
        return 2

    summary = run_stage1()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
