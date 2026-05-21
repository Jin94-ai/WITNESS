"""ONESHOT Gemma 4 E4B labeling — Stage 2.1 (low-temperature stability test).

Per Stage 2.1 Directive.

Same 50 passages, same seed=42, Stage 1.6 prompt locked.
Only model parameters changed: temperature=0.2, top_p=0.9, top_k=40.

Goal:
  - taxonomy invalid 0 검증 (Stage 2의 2/50 leakage 해결 여부)
  - label stability comparison vs Stage 2

Run:
    python -m scripts.labeling.oneshot_label_with_gemma_stage2_1
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import ollama

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import preprocess_entry

ROOT = Path(__file__).resolve().parents[2]
TL1_ZIP = ROOT / "data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/1.Training/라벨링데이터/TL1.zip"
PUBLIC_DIR = ROOT / "docs" / "results" / "gemma_labeling_poc"
PRIVATE_DIR = ROOT / "data" / "external_private" / "gemma_review"

TARGET_DOC_ORIGIN_BASE = "미우나고우나"
TARGET_ANONYMIZED = "work_e46069c4b4"
TARGET_DOC_TYPE = "fm_drama"
TARGET_YEAR = "2007"

MODEL_NAME = "gemma4:e4b"
RANDOM_SEED = 42
STAGE_SAMPLE_SIZE = 50
STAGE1_6_SAMPLE_SIZE = 10  # for overlap calc

TEMPERATURE = 0.2
TOP_P = 0.9
TOP_K = 40


# --- System prompt — Stage 1.6 LOCKED (no modifications) ---
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
8. reasoning_brief는 1~2문장 한국어 근거.

주의: love는 Pressure taxonomy에만 있다. primary_desires 또는 secondary_desires에 love를 넣지 마라.

중요:
"unknown"은 conflict_axis 필드에서만 사용할 수 있다.
primary_pressures, secondary_pressures, primary_desires, secondary_desires에는 "unknown"을 절대 넣지 마라.

압력이나 욕망이 불명확하면:
- pressures/desires에는 가장 근접한 허용 taxonomy를 선택하거나
- secondary_* 배열을 비워둔다.

절대 금지:
- "unknown" in primary_pressures
- "unknown" in secondary_pressures
- "unknown" in primary_desires
- "unknown" in secondary_desires"""


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

[Pressure 사용 기준 — 과다 라벨 방지]
- public_suspicion: 단순히 사람이 옆에 있거나 공공장소라는 이유만으로 선택하지 마라. 반드시 누군가의 비밀, 행동, 관계, 평판이 타인의 의심 대상이 될 때만 선택한다.
- authority_vigilance: 단순한 대화 상대가 아니라 부모, 상사, 어른, 투자자, 사회적 위계자가 평가하거나 압박할 때만 선택한다.
- blame_concentration: 명확히 책임/비난이 한 인물에게 몰릴 때만 선택한다.
- group_tension: 셋 이상의 관계에서 갈등 분위기가 실제로 형성될 때만 선택한다.

[Confidence calibration]
- 0.90: 단일 장면이고 인물/압력/욕망/갈등축이 모두 매우 명확함
- 0.75: 대체로 명확하지만 일부 해석 여지가 있음
- 0.60: 여러 장면이 섞였거나 라벨 중 일부가 불확실함
- 0.45: 인물/압력/욕망은 일부 보이나 conflict_axis가 불명확함
- 0.30: 정보가 부족하거나 장면 의미가 거의 불명확함

추가 규칙:
- 한 passage 안에 서로 다른 장면이 2개 이상 섞여 있으면 confidence를 0.60 이하로 낮춰라.
- 갈등축이 명확하지 않으면 conflict_axis는 "unknown"을 선택하고 confidence를 0.60 이하로 낮춰라.

[복합 passage 처리]
- 한 passage에 여러 장면이 섞여 있으면 가장 narrative pressure가 강한 장면 하나를 기준으로 라벨링한다.
- 장면 간 주제가 서로 다르면 confidence를 낮춘다.
- 서로 무관한 사건들이 섞여 있으면 conflict_axis는 "unknown"을 허용한다.

[Few-shot 예시]
예시 passage: "엄마, 진짜 결혼할 거야. 어머니가 반대해도 동지를 포기 못합니다."
예시 출력:
{
  "characters": ["만수", "어머니"],
  "primary_pressures": ["authority_vigilance"],
  "secondary_pressures": ["love"],
  "primary_desires": ["commitment", "trust"],
  "secondary_desires": [],
  "conflict_axis": "uncertainty_vs_commitment",
  "confidence": 0.85,
  "reasoning_brief": "어머니의 반대(권위 압박)에도 만수가 사랑하는 사람을 포기 못한다는 결정"
}

[분석할 passage]
__PASSAGE_TEXT__

JSON으로만 응답하시오."""


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
    print(f"[extract] filter doc_origin_base == {TARGET_DOC_ORIGIN_BASE}", file=sys.stderr)
    out: list[dict] = []
    for raw in stream_aihub_023(TL1_ZIP, categories=[TARGET_DOC_TYPE]):
        pp = preprocess_entry(raw)
        if pp["doc_origin_base"] == TARGET_DOC_ORIGIN_BASE and pp["is_valid"]:
            out.append(pp)
    print(f"[extract] {len(out)} valid passages", file=sys.stderr)
    return out


def label_passage(passage_text: str) -> tuple[dict, str]:
    user_prompt = USER_PROMPT_TEMPLATE.replace("__PASSAGE_TEXT__", passage_text)
    raw_content = ""
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K},
            format="json",
        )
        raw_content = response["message"]["content"]
        return json.loads(raw_content), raw_content
    except json.JSONDecodeError as e:
        return {"_error": "json_parse", "_error_msg": str(e)}, raw_content
    except Exception as e:
        return {"_error": "ollama", "_error_msg": str(e)}, raw_content


def validate_schema(label: dict) -> dict:
    """Stage 2 hard fail validation (directive §3)."""
    issues: dict = {}
    required = ["characters", "primary_pressures", "secondary_pressures",
                "primary_desires", "secondary_desires", "conflict_axis",
                "confidence", "reasoning_brief"]
    missing = [k for k in required if k not in label]
    if missing:
        issues["missing_fields"] = missing

    # taxonomy hard-fail rules
    pp = label.get("primary_pressures", []) or []
    sp = label.get("secondary_pressures", []) or []
    pd = label.get("primary_desires", []) or []
    sd = label.get("secondary_desires", []) or []

    # unknown leakage
    if "unknown" in pp:
        issues["unknown_in_primary_pressures"] = True
    if "unknown" in sp:
        issues["unknown_in_secondary_pressures"] = True
    if "unknown" in pd:
        issues["unknown_in_primary_desires"] = True
    if "unknown" in sd:
        issues["unknown_in_secondary_desires"] = True

    # love leakage to desires
    if "love" in pd:
        issues["love_in_primary_desires"] = True
    if "love" in sd:
        issues["love_in_secondary_desires"] = True

    # generic taxonomy validity
    for k, vals in [("primary_pressures", pp), ("secondary_pressures", sp)]:
        invalid = [v for v in vals if v not in VALID_PRESSURES]
        if invalid:
            issues.setdefault("invalid_pressures", []).extend(invalid)
    for k, vals in [("primary_desires", pd), ("secondary_desires", sd)]:
        invalid = [v for v in vals if v not in VALID_DESIRES]
        if invalid:
            issues.setdefault("invalid_desires", []).extend(invalid)
    axis = label.get("conflict_axis", "")
    if axis and axis not in VALID_CONFLICT_AXES:
        issues["invalid_conflict_axis"] = axis

    conf = label.get("confidence")
    if conf is not None and not (isinstance(conf, (int, float)) and 0.0 <= float(conf) <= 1.0):
        issues["invalid_confidence"] = conf

    return issues


def compute_stage1_6_passage_ids(all_passages: list[dict]) -> set[str]:
    """Stage 1.6과 동일 방식으로 10개 sample 추출 → passage_ids."""
    rng = random.Random(RANDOM_SEED)
    pool = sorted(all_passages, key=lambda e: e["passage_id"])
    sample10 = rng.sample(pool, STAGE1_6_SAMPLE_SIZE)
    return {e["passage_id"] for e in sample10}


def run_stage2_1() -> dict:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

    all_passages = extract_target_passages()
    if not all_passages:
        return {"error": "no passages"}

    # deterministic 50-sample (separate RNG instance)
    rng = random.Random(RANDOM_SEED)
    pool = sorted(all_passages, key=lambda e: e["passage_id"])
    sampled = rng.sample(pool, STAGE_SAMPLE_SIZE)
    sampled_ids = {e["passage_id"] for e in sampled}

    # overlap with Stage 1.6's 10 passages
    stage1_6_ids = compute_stage1_6_passage_ids(all_passages)
    overlap = sampled_ids & stage1_6_ids

    print(f"[stage2_1] {len(sampled)} sampled, overlap with stage1.6: {len(overlap)}/10", file=sys.stderr)

    print(f"[stage2_1] warming up gemma4:e4b...", file=sys.stderr)
    t_wu = time.time()
    label_passage("테스트 씬: 두 사람이 말없이 서 있다.")
    print(f"[stage2_1] warmup {time.time()-t_wu:.1f}s", file=sys.stderr)

    private_path = PRIVATE_DIR / "work_e46069c4b4_stage2_1_private.jsonl"
    private_records: list[dict] = []
    t_total_start = time.time()
    success = 0
    json_parse_failed = 0
    schema_missing = 0
    taxonomy_invalid = 0
    ollama_errors = 0

    with private_path.open("w", encoding="utf-8") as fp:
        for i, p in enumerate(sampled, 1):
            t_start = time.time()
            print(f"[stage2_1] {i}/{STAGE_SAMPLE_SIZE}: {p['passage_id']} (len={p['passage_length']})", file=sys.stderr)
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
                    schema_missing += 1
                hard_fail_keys = (
                    "unknown_in_primary_pressures", "unknown_in_secondary_pressures",
                    "unknown_in_primary_desires", "unknown_in_secondary_desires",
                    "love_in_primary_desires", "love_in_secondary_desires",
                    "invalid_pressures", "invalid_desires", "invalid_conflict_axis",
                )
                if any(k in issues for k in hard_fail_keys):
                    taxonomy_invalid += 1
                if not issues:
                    success += 1

            private_rec = {
                "passage_id": p["passage_id"],
                "passage_length": p["passage_length"],
                "label": label,
                "validation_issues": issues,
                "elapsed_sec": elapsed,
                "model": MODEL_NAME,
                "stage": "stage2_1",
                "index": i,
                "is_stage1_6_overlap": p["passage_id"] in stage1_6_ids,
                "passage": p["passage"],
                "doc_origin_raw": p["doc_origin_raw"],
                "doc_origin_base": p["doc_origin_base"],
                "anonymized_origin": TARGET_ANONYMIZED,
                "raw_gemma_content": raw_content,
                "lee_review": {
                    "characters_ok": None,
                    "pressure_ok": None,
                    "desire_ok": None,
                    "conflict_axis_ok": None,
                    "confidence_ok": None,
                    "overall": None,
                    "note": "",
                },
            }
            fp.write(json.dumps(private_rec, ensure_ascii=False) + "\n")
            private_records.append(private_rec)

    t_total = round(time.time() - t_total_start, 2)

    confidences = [r["label"].get("confidence") for r in private_records if "_error" not in r["label"]]
    conf_floats = [float(c) for c in confidences if c is not None]
    conf_unique = sorted(set(conf_floats))

    pressure_counter = Counter()
    desire_counter = Counter()
    conflict_counter = Counter()
    elapsed_list = []
    for r in private_records:
        elapsed_list.append(r["elapsed_sec"])
        if "_error" in r["label"]:
            continue
        for p in r["label"].get("primary_pressures", []) or []:
            pressure_counter[f"primary:{p}"] += 1
        for p in r["label"].get("secondary_pressures", []) or []:
            pressure_counter[f"secondary:{p}"] += 1
        for d in r["label"].get("primary_desires", []) or []:
            desire_counter[f"primary:{d}"] += 1
        for d in r["label"].get("secondary_desires", []) or []:
            desire_counter[f"secondary:{d}"] += 1
        conflict_counter[r["label"].get("conflict_axis", "")] += 1

    # issue summary
    issue_counts = Counter()
    for r in private_records:
        for k in r["validation_issues"].keys():
            issue_counts[k] += 1

    summary = {
        "stage": "stage2_1",
        "target_work": TARGET_ANONYMIZED,
        "target_year": TARGET_YEAR,
        "target_doc_type": TARGET_DOC_TYPE,
        "model": MODEL_NAME,
        "params": {"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K},
        "sample_seed": RANDOM_SEED,
        "sample_size": STAGE_SAMPLE_SIZE,
        "pool_size": len(all_passages),
        "stage1_6_overlap_count": len(overlap),
        "stage1_6_overlap_ids": sorted(overlap),
        "total_processed": len(sampled),
        "success": success,
        "json_parse_failed": json_parse_failed,
        "schema_missing": schema_missing,
        "taxonomy_invalid": taxonomy_invalid,
        "ollama_errors": ollama_errors,
        "total_runtime_sec": t_total,
        "avg_seconds_per_passage": round(t_total / max(1, len(sampled)), 2),
        "min_seconds_per_passage": round(min(elapsed_list), 2) if elapsed_list else 0,
        "max_seconds_per_passage": round(max(elapsed_list), 2) if elapsed_list else 0,
        "confidence_unique_count": len(conf_unique),
        "confidence_unique_values": conf_unique,
        "confidence_distribution": {f"{c:.2f}": conf_floats.count(c) for c in conf_unique},
        "primary_pressure_distribution": dict(pressure_counter),
        "primary_desire_distribution": dict(desire_counter),
        "conflict_axis_distribution": dict(conflict_counter),
        "validation_issue_counts": dict(issue_counts),
        "output_private": str(private_path.relative_to(ROOT)).replace("\\", "/"),
        "completed_at_iso": datetime.now(timezone.utc).isoformat(),
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.parse_args(argv)

    summary = run_stage2_1()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    (PUBLIC_DIR / "stage2_1_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
