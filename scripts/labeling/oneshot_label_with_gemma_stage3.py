"""ONESHOT Gemma 4 E4B labeling — Stage 3 (full work, 225 passages).

Per handoff v2 §5 옵션 A + stage2_2 review §7 선결 조건.

Stage 2.2 prompt v2 그대로 사용. 변경:
  - sample size: 50 → 225 (전체 미우나고우나)
  - characters 후처리 (phantom 제거 + dup 통일) 적용
  - GPU 100% mode (num_gpu=999)
  - 매 record fp.flush() (progress visibility)

Expected runtime: 92s × 225 = ~5.75 hours.

Run:
    python -m scripts.labeling.oneshot_label_with_gemma_stage3
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
from scripts.labeling.postprocess_characters import postprocess_characters

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
STAGE_SAMPLE_SIZE = 225  # 미우나고우나 전체 (모든 valid passages)
STAGE1_6_SAMPLE_SIZE = 10  # for overlap calc
STAGE2_2_SAMPLE_SIZE = 50  # for overlap calc

TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 64


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

[Pressure 선택 기준 — 가족극 우선순위 5]
1) 가족 내부 갈등 표면화 → group_tension (부부 다툼, 자식 반항, 시댁 신경전)
2) 책임/비난이 한 인물에게 몰림 → blame_concentration
3) 자신의 처지·실패에 대한 자괴감 → shame_self
4) public_suspicion / authority_vigilance는 **외부 공권력 또는 가족 외부의 평가·감시·처벌이 명시적으로 묘사된 경우만**. 가족 내부 의심·반대는 group_tension.
5) love는 *Pressure*다. 누군가에 대한 애착이 행동을 좌우할 때. **desires에 절대 넣지 마라.**

주의: PS/AV를 기본값처럼 쓰지 마라. 가족극 대부분은 group_tension / blame_concentration / shame_self / love.

[Desire 선택 기준 — survival 과사용 방지]
survival을 선택하기 전 다음을 확인하라.

1) 물리적 생존 위협(폭력·사망 가능성)이 명시되었는가?
2) 경제적 파산·실직 위협이 명시되었는가?
위 둘 중 하나가 명확하면 → survival.

아니면 다음 중 하나로 대체:
- 곤란한 상황을 피하려는 마음 → exposure_avoidance
- 자기 이름·체면·평판을 지키려는 마음 → identity_preservation
- 누군가의 곁에 남으려는 마음 → loyalty
- 결정하려는 의지 → commitment
- 관계를 지키려는 마음 → trust

love는 절대 desire에 넣지 마라. love는 Pressure다.
인물이 "사랑해서 행동한다" 같은 상황이면 → primary_pressures에 love, primary_desires에는 commitment 또는 loyalty.

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

[Few-shot 예시 1 — 가족 내부 갈등 (PS/AV 아닌 group_tension/blame)]
passage: "단풍이 백호에게 따지듯이 묻는다. 백호는 입을 다물고 외면한다. 어머니가 끼어들어 단풍을 나무란다."
출력:
{
  "characters": ["단풍", "백호", "어머니"],
  "primary_pressures": ["group_tension", "blame_concentration"],
  "secondary_pressures": [],
  "primary_desires": ["exposure_avoidance"],
  "secondary_desires": ["commitment"],
  "conflict_axis": "control_vs_exposure",
  "confidence": 0.85,
  "reasoning_brief": "가족 내부 갈등 표면화(group_tension), 단풍이 백호를 몰아세움(blame_concentration), 백호 회피(exposure_avoidance)."
}

[Few-shot 예시 2 — love가 pressure로 작동 (desire 아님)]
passage: "동지가 다친 백호를 보며 발만 동동 구른다. 무리해서라도 도우려 한다."
출력:
{
  "characters": ["동지", "백호"],
  "primary_pressures": ["love", "grief"],
  "secondary_pressures": [],
  "primary_desires": ["loyalty"],
  "secondary_desires": [],
  "conflict_axis": "atmosphere_vs_action",
  "confidence": 0.85,
  "reasoning_brief": "다친 사람에 대한 애착(love, pressure)이 행동을 좌우. 곁에 남으려는 마음(loyalty, desire)."
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
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "top_k": TOP_K,
                "num_gpu": 999,  # 모든 layer GPU 강제 (OOM 시 ollama가 알아서 줄임)
            },
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


def run_stage3() -> dict:
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

    print(f"[stage3] {len(sampled)} sampled, overlap with stage1.6: {len(overlap)}/10", file=sys.stderr)

    print(f"[stage3] warming up gemma4:e4b...", file=sys.stderr)
    t_wu = time.time()
    label_passage("테스트 씬: 두 사람이 말없이 서 있다.")
    print(f"[stage3] warmup {time.time()-t_wu:.1f}s", file=sys.stderr)

    private_path = PRIVATE_DIR / "work_e46069c4b4_stage3_private.jsonl"
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
            print(f"[stage3] {i}/{STAGE_SAMPLE_SIZE}: {p['passage_id']} (len={p['passage_length']})", file=sys.stderr)
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

            # characters 후처리 (handoff v2 §5 선결 조건 1)
            postprocess_log: dict = {}
            cleaned_characters: list[str] = []
            if "_error" not in label and isinstance(label.get("characters"), list):
                cleaned_characters, postprocess_log = postprocess_characters(
                    label["characters"], p["passage"]
                )

            private_rec = {
                "passage_id": p["passage_id"],
                "passage_length": p["passage_length"],
                "label": label,
                "validation_issues": issues,
                "characters_postprocessed": cleaned_characters,
                "characters_postprocess_log": postprocess_log,
                "elapsed_sec": elapsed,
                "model": MODEL_NAME,
                "stage": "stage3",
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
            fp.flush()  # 매 record마다 disk flush — progress visibility 보장
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

    # postprocess summary
    pp_records = [r for r in private_records if r.get("characters_postprocess_log")]
    pp_phantoms_total = sum(len(r["characters_postprocess_log"].get("phantoms_removed", [])) for r in pp_records)
    pp_dup_total = sum(len(r["characters_postprocess_log"].get("dup_unifications", {})) for r in pp_records)
    pp_records_with_phantom = sum(1 for r in pp_records if r["characters_postprocess_log"].get("phantoms_removed"))
    pp_records_with_dup = sum(1 for r in pp_records if r["characters_postprocess_log"].get("dup_unifications"))

    summary = {
        "stage": "stage3",
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
        "characters_postprocess": {
            "phantoms_removed_total": pp_phantoms_total,
            "dup_unifications_total": pp_dup_total,
            "records_with_phantom": pp_records_with_phantom,
            "records_with_dup": pp_records_with_dup,
        },
        "output_private": str(private_path.relative_to(ROOT)).replace("\\", "/"),
        "completed_at_iso": datetime.now(timezone.utc).isoformat(),
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.parse_args(argv)

    summary = run_stage3()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    (PUBLIC_DIR / "stage3_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
