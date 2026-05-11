"""Phase 3.0 v1.1 Pipeline — normalized JSONL → annotation_inputs/*.json.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10 + §12.

Mode A 호환 (수동 LLM annotation):
    각 record를 LLM에게 그대로 붙여넣을 수 있는 task JSON으로 변환.
    `annotate_episode_synopsis_v1` task schema (§12).

Output schema (§12):
    {
      "task": "annotate_episode_synopsis_v1",
      "record_id": "...",
      "genre_id": "...",
      "title_id": "...",
      "episode_number": ...,
      "synopsis_text": "...",
      "features_to_score": [...],
      "output_schema": "episode_annotation_v1"
    }

원칙:
    - 사용자가 각 *.json을 LLM (ChatGPT / Claude / Gemini 등)에 붙여넣어
      annotation_outputs/*.json 응답을 받음 (Mode A)
    - 자동 LLM API 호출은 후순위 (Mode C)
    - synopsis_text는 input에 포함됨 (annotation_inputs/는 .gitignore 보호)
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


# Phase 3.0 §11 + §12: feature set v1.1 (필수 7 + 추가 3)
DEFAULT_FEATURES_TO_SCORE = (
    "conflict_intensity_peak",
    "dangling_thread_generation",
    "cliffhanger_strength",
    "relationship_pressure",
    "hidden_information_pressure",
    "silence_or_avoidance",
    "emotional_suppression",
)

ANNOTATION_INPUT_TASK = "annotate_episode_synopsis_v1"
ANNOTATION_OUTPUT_SCHEMA = "episode_annotation_v1"


# Phase 3.0 §11 + ANNOTATION_GUIDE §2 + §6 feature 정의 (LLM annotator에게 inline 제공)
# annotation 품질을 위해 *각 feature가 무엇을 측정하는지*를 prompt에 명시.
FEATURE_DEFINITIONS_KO: dict[str, str] = {
    "conflict_intensity_peak": (
        "회차 안에서 관측되는 갈등 누적/폭발의 *최대* 강도 "
        "(0=갈등 거의 없음, 3=여러 인물로 확산, 5=중심이 강한 충돌·폭로·파국)"
    ),
    "dangling_thread_generation": (
        "회차에서 *새로 남겨진* 미해결 질문/의심/비밀/오해의 수와 강도 "
        "(0=미해결 0건, 3=미해결 갈등 2건+, 5=회차 말미가 거의 클리프행어 중심)"
    ),
    "cliffhanger_strength": (
        "회차 *말미*의 미해결 긴장이 다음 회차 진입을 견인하는 강도 "
        "(0=깔끔히 끝남, 3=여러 사건 미해결, 5=극단적 cliffhanger)"
    ),
    "relationship_pressure": (
        "인물 간 *관계*에서 발생하는 압력의 강도 (가족/연인/직장 등) "
        "(0=관계 압력 거의 없음, 3=관계 긴장 여러 인물 확산, 5=회차 중심이 관계 파탄)"
    ),
    "hidden_information_pressure": (
        "숨긴 진실/비밀이 인물에게 가하는 압력의 강도. 비밀 *내용*이 아닌 *존재* 자체가 만드는 압력 "
        "(0=숨긴 정보 없음, 3=비밀 2건+ 압박, 5=비밀이 회차 전체 지배)"
    ),
    "silence_or_avoidance": (
        "인물이 *말하지 않음 / 자리 피함 / 결정 미룸*의 강도 "
        "(0=모두 행동·말함, 3=여러 인물 회피, 5=침묵·회피가 회차의 중심 사건)"
    ),
    "emotional_suppression": (
        "인물이 감정을 *눌러두는* 강도. 표면은 평온하지만 안에서 누적되는 정도 "
        "(0=감정 표현 자유롭음, 3=여러 인물 억제, 5=억제가 회차의 중심)"
    ),
    # v1.1 legacy compat
    "revelation_density": (
        "회차당 새로 드러나는 *숨겨진 사실*의 수 "
        "(0=폭로 0건, 0.5=1건 큰 또는 2-3건 중간, 1.0=3건 이상 큰 폭로). 0.0~1.0 float"
    ),
    "coincidence_frequency": (
        "우연한 마주침/발견이 *결정타*가 되는 횟수 "
        "(0=우연 0건, 0.5=1건 결정적, 1.0=3건 이상 결정적). 0.0~1.0 float"
    ),
    "relationship_polarization": (
        "인물 관계가 *중간 지대 없이* 극과 극으로 가는 정도 "
        "(0=그라데이션, 0.5=절반 극단, 1.0=모든 주요 관계 극단). 0.0~1.0 float"
    ),
    "new_conflict_introduction_rate": (
        "회차당 *새로 시작되는* 갈등의 수 "
        "(0=새 갈등 0, 0.5=2건, 1.0=4건 이상). 0.0~1.0 float"
    ),
    "cliffhanger_intensity": (
        "회차 *말미*의 미해결 긴장 강도 (cliffhanger_strength와 의미 동일, 0.0~1.0 float)"
    ),
}


def _build_instructions_ko(features: tuple[str, ...]) -> str:
    """LLM annotator에게 줄 한국어 instructions. feature 정의 inline."""
    # Feature별 한 줄 정의
    feature_lines = []
    for f in features:
        defn = FEATURE_DEFINITIONS_KO.get(f, "(정의 없음 — ANNOTATION_GUIDE 참조)")
        feature_lines.append(f"  - **{f}**: {defn}")
    feat_text = "\n".join(feature_lines)

    return (
        "당신은 한국어 회차 줄거리 어노테이터입니다.\n\n"
        "**평가 규칙**:\n"
        "1. 각 feature를 *0-5 정수 level*로 평가하세요 "
        "(0=거의 없음, 1=약함, 2=명확, 3=확산, 4=강함, 5=회차의 중심).\n"
        "2. 각 feature의 evidence_quote는 *줄거리 원문에서 직접 인용*한 짧은 문구만. "
        "**새로 만들어내면 안 됩니다** (hallucination 검사 자동 실행).\n"
        "3. confidence.overall은 0.0-1.0 float (이 회차 줄거리가 모호하면 낮춤).\n"
        "4. 응답은 episode_annotation_v1 schema의 *JSON만* 출력. 자유 텍스트 금지.\n\n"
        f"**Features (Phase 3.0 §11 + ANNOTATION_GUIDE §2/§6)**:\n{feat_text}\n\n"
        "**주의**:\n"
        "- 한국어 줄거리임을 인지 (영어 아님).\n"
        "- evidence_quote는 짧게 (≤ 30자 권장).\n"
        "- 모호한 feature는 confidence를 낮추고 warnings에 메모.\n"
    )


def make_annotation_input(record: dict, features: tuple[str, ...]) -> dict:
    """EpisodeSynopsisRecord → annotation_input task JSON (§12)."""
    return {
        "task": ANNOTATION_INPUT_TASK,
        "record_id": record["record_id"],
        "genre_id": record["genre_id"],
        "title_id": record["title_id"],
        "episode_number": record["episode_number"],
        "synopsis_text": record["synopsis_text"],
        "features_to_score": list(features),
        "output_schema": ANNOTATION_OUTPUT_SCHEMA,
        "instructions_ko": _build_instructions_ko(features),
    }


def write_annotation_inputs(
    records: list[dict],
    out_dir: Path,
    features: tuple[str, ...],
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for r in records:
        path = out_dir / f"{r['record_id']}.json"
        payload = make_annotation_input(r, features)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        written += 1
    return written


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="normalized_synopsis.jsonl")
    ap.add_argument("--output", required=True, type=Path,
                     help="annotation_inputs/ output dir")
    ap.add_argument(
        "--features", nargs="+", default=list(DEFAULT_FEATURES_TO_SCORE),
        help="features_to_score (default: 7 features from Phase 3.0 §11)",
    )
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    records = load_jsonl(args.input)
    if not records:
        print("WARNING: no records in input", file=sys.stderr)

    written = write_annotation_inputs(
        records, args.output, tuple(args.features),
    )
    print(f"OK: {written} annotation_inputs written → {args.output}")
    print(f"  features: {len(args.features)} ({', '.join(args.features[:3])}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
