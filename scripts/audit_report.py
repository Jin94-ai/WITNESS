"""HARNESS 보고서 자동 감사.

사용:
    python scripts/audit_report.py <report.md>
    python scripts/audit_report.py docs/person/DATA_PIPELINE_v1.md

출력: HARNESS 위반 목록 + 위반 수. 위반 ≥1 이면 exit code 1.

이 스크립트는 **보고서 제출 전 반드시 통과**해야 한다. 기계적 검증이므로
의지력에 의존하지 않음 (CLAUDE.md HARNESS CONSTRAINTS §H4, §H7, §H8).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# H4 -- 금지어 (보고서에서 단독 사용 금지)
BANNED_PHRASES = [
    "설계의 승리",
    "핵심 원천",
    "positive 증거",
    "준수 완료",
    "살아 움직인다",
    "파이프라인 완결",
    "품질 달성",
    "설계 승리",
]

# "작동한다" 는 단독 금지 (조건부화 필요)
UNCONDITIONAL_WORKING = re.compile(
    r"(?<!\s하에서\s)작동한다(?!\s\(조건)",
)

# H4 -- 필수 섹션 (synonyms accepted — first match wins)
REQUIRED_SECTIONS = [
    (
        "What could still be wrong",
        ["What could still be wrong", "Limitations", "Caveats",
         "What this evidence does NOT prove", "Negative findings"],
        "H4",
    ),
    (
        "What I did NOT try",
        ["What I did NOT try", "What was NOT tested", "Untested",
         "What I did not try"],
        "H4",
    ),
    (
        "Alternate interpretations",
        ["Alternate interpretations", "Alternative interpretations",
         "Alternate explanations", "Alternative explanations"],
        "H4",
    ),
]

# H5 -- Lee verbatim 인용 섹션 (작업 완료 보고서에 권장)
RECOMMENDED_SECTIONS = [
    ("Lee의 원래 지시", "H5"),
    ("축소한 지점", "H5"),
    ("HARNESS 자가감사", "H7"),
]

# H3 -- spec / Rule 언급 시 verbatim quote 패턴 필요
SPEC_RULE_MENTION = re.compile(r"(spec\s*§\d+(\.\d+)?|Rule\s*#\d+)", re.IGNORECASE)
VERBATIM_QUOTE = re.compile(r'\*["“][^"”]+["”]\*|> "[^"]+"|verbatim[:\s]')

# H8 -- sensitivity claim이 headline이면 ensemble disclosure 필요
SENSITIVITY_CLAIM = re.compile(
    r"(sensitivity\s+(ratio|rate|percent|%)|configuration\s+sensitivity|"
    r"per[\s-]?dimension\s+sensitivity|sensitivity\s+drop|delta\s+pp)",
    re.IGNORECASE,
)
ENSEMBLE_DISCLOSURE = re.compile(
    r"(ensemble|cross[\s-]?seed|seed=0[\s-]?only|single[\s-]?seed|"
    r"\d+\s*seeds?|across\s+seeds|seeds?\s*0\s*[-–]\s*\d+)",
    re.IGNORECASE,
)


def _strip_meta_mentions(text: str) -> str:
    """Strip lines whose purpose is to quote the banned phrase as a self-check,
    not to use it as a claim. This lets authors say "I did not use '금지어 X'"
    without the audit flagging it.
    """
    kept = []
    for line in text.split("\n"):
        stripped = line.strip()
        # self-check checklist lines (bullet + '사용 안 함' / 'banned' marker)
        if ("사용 안 함" in stripped or "사용 안함" in stripped
                or "not used" in stripped.lower()
                or "banned phrase" in stripped.lower()):
            continue
        # Explicit enumeration within the H4 guidance block
        if stripped.startswith("-") and "금지어" in stripped:
            continue
        kept.append(line)
    return "\n".join(kept)


def audit(text: str) -> list[tuple[str, str]]:
    """Return [(rule, message), ...]. Empty list = pass."""
    violations: list[tuple[str, str]] = []
    scannable = _strip_meta_mentions(text)

    # H4: banned phrases (excluding meta-mentions)
    for phrase in BANNED_PHRASES:
        if phrase in scannable:
            violations.append(("H4", f"banned phrase present: '{phrase}'"))

    # H4: '작동한다' unconditional (meta-mentions stripped)
    for match in UNCONDITIONAL_WORKING.finditer(scannable):
        ctx = scannable[max(0, match.start() - 30):match.end() + 30].replace("\n", " ")
        violations.append(("H4", f"unconditioned '작동한다' -- must be conditioned. context: ...{ctx}..."))

    # H4: required sections (synonyms accepted)
    for canonical_name, synonyms, rule in REQUIRED_SECTIONS:
        if not any(syn in text for syn in synonyms):
            violations.append(
                (rule,
                 f"missing required section: '{canonical_name}' (synonyms: {', '.join(synonyms[1:3])}...)"),
            )

    # H3: spec/Rule mention without verbatim quote
    spec_mentions = SPEC_RULE_MENTION.findall(text)
    if spec_mentions and not VERBATIM_QUOTE.search(text):
        uniq = sorted({m[0] for m in spec_mentions})
        violations.append((
            "H3",
            f"spec/Rule cited ({', '.join(uniq)}) but no verbatim quote / "
            f"'verbatim' marker found. H3 requires verbatim citation.",
        ))

    # H6: "Lee 판단" 언급 시 minimum 2 options
    lee_judgment = "Lee 판단" in text or "Lee 결정" in text or "Lee 허가" in text
    if lee_judgment:
        # Look for a table with options (| A | or | B | or markdown list)
        option_markers = len(re.findall(r"^\s*[|\-*]\s*(선택지|옵션|option)\s*[A-D1-9]", text, re.MULTILINE | re.IGNORECASE))
        # Match any row whose first cell contains A/B/C/D (optional bold,
        # optional trailing label text inside the same cell)
        option_rows = len(re.findall(
            r"^\s*\|\s*\*{0,2}[A-D]\*{0,2}[^|]*\|", text, re.MULTILINE,
        ))
        if option_markers + option_rows < 2:
            violations.append((
                "H6",
                "'Lee 판단' cited but fewer than 2 options presented with equal-weight. "
                "H6 requires at least 2 options + explicit bias confession.",
            ))

    # H7: self-audit block
    for section, rule in RECOMMENDED_SECTIONS:
        if section not in text:
            violations.append((rule, f"recommended section missing: '{section}'"))

    # H8: sensitivity claim without ensemble disclosure
    if SENSITIVITY_CLAIM.search(text) and not ENSEMBLE_DISCLOSURE.search(text):
        violations.append((
            "H8",
            "sensitivity claim present but no ensemble/seed disclosure. "
            "H8 requires 5+ seed ensemble for headline sensitivity ratios; "
            "single-seed must be explicitly disclosed (e.g. 'seed=0 only').",
        ))

    return violations


# Story output forbidden phrase scan (per docs/story/STORY_OUTPUT_SPEC.md §6)
STORY_FORBIDDEN = [
    "trajectory", "probe", "final summary", "annotated",
    "이 시뮬레이션", "이 trajectory", "이 probe", "이 결과", "데이터에 따르면",
]
STORY_FORBIDDEN_RAW_ID = re.compile(r"\b(P\d+|P_(?:PV|CV|ED|S2)_\d+|A\d+|L\d+|agent_\d+)\b")
STORY_FORBIDDEN_NUMBERS = re.compile(r"\b(peak|final|t=)\s*[\d.]+", re.IGNORECASE)


def audit_story(text: str) -> list[tuple[str, str]]:
    """Story-specific forbidden check."""
    violations: list[tuple[str, str]] = []
    for phrase in STORY_FORBIDDEN:
        if phrase in text:
            violations.append(("STORY", f"forbidden phrase: '{phrase}'"))
    for m in STORY_FORBIDDEN_RAW_ID.finditer(text):
        violations.append(("STORY", f"raw ID leak: '{m.group(0)}'"))
    for m in STORY_FORBIDDEN_NUMBERS.finditer(text):
        violations.append(("STORY", f"raw number: '{m.group(0)}'"))
    return violations


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/audit_report.py <report.md>")
        print("       python scripts/audit_report.py --stories  # audit all docs/story/generated/*.txt")
        return 2

    if sys.argv[1] == "--stories":
        story_dir = Path(__file__).resolve().parent.parent / "docs" / "story" / "generated"
        files = sorted(story_dir.glob("*_ko.txt"))
        if not files:
            print(f"No stories found in {story_dir}")
            return 2
        all_violations = 0
        per_file_fail = 0
        print(f"\nStory forbidden audit: {len(files)} files in {story_dir}")
        print("=" * 70)
        for f in files:
            text = f.read_text(encoding="utf-8")
            v = audit_story(text)
            if v:
                per_file_fail += 1
                all_violations += len(v)
                print(f"FAIL {f.name}: {len(v)} violation(s)")
                for rule, msg in v[:3]:
                    print(f"  - {msg}")
        if all_violations == 0:
            print(f"PASS -- {len(files)}/{len(files)} stories clean (0 violations across all files).")
            return 0
        print(f"\n{per_file_fail}/{len(files)} files failed, {all_violations} total violations.")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"file not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8")
    violations = audit(text)

    print(f"\nHARNESS audit: {path}")
    print("=" * 70)
    if not violations:
        print("PASS -- 0 violations.")
        return 0

    print(f"FAIL -- {len(violations)} violation(s):\n")
    by_rule: dict[str, list[str]] = {}
    for rule, msg in violations:
        by_rule.setdefault(rule, []).append(msg)
    for rule in sorted(by_rule):
        print(f"[{rule}]")
        for msg in by_rule[rule]:
            print(f"  - {msg}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
