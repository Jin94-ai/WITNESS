"""Character list 후처리 — phantom 제거 + dup 통일.

Per stage2_2_qualitative_review §5-2 + handoff v2 §4 선결 조건.

Phantom: passage에 등장하지 않는 인물 이름 제거
Dup: 같은 인물의 다른 표기 (예: 최여사 vs 최여자) 통일

NOT a reusable framework. Stage 3 후처리 전용.
"""

from __future__ import annotations

import unicodedata


def _normalize(s: str) -> str:
    """공백/제어문자 제거 + NFC."""
    return unicodedata.normalize("NFC", s.strip())


def _decompose_hangul(ch: str) -> tuple[int, int, int] | None:
    """한글 한 글자 → (초성, 중성, 종성) index. 한글 아니면 None."""
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        offset = code - 0xAC00
        cho = offset // (21 * 28)
        jung = (offset % (21 * 28)) // 28
        jong = offset % 28
        return cho, jung, jong
    return None


def jaso_distance(a: str, b: str) -> int:
    """한국어 자모 기반 edit distance (Levenshtein on jaso sequence).

    "최여사" vs "최여자" → 자모 한 개 차이.
    """
    def to_jaso(s: str) -> list[str]:
        out: list[str] = []
        for ch in s:
            d = _decompose_hangul(ch)
            if d is None:
                out.append(ch)
            else:
                cho, jung, jong = d
                out.append(f"c{cho}")
                out.append(f"j{jung}")
                if jong != 0:
                    out.append(f"f{jong}")
        return out

    sa, sb = to_jaso(a), to_jaso(b)
    m, n = len(sa), len(sb)
    if m == 0:
        return n
    if n == 0:
        return m
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if sa[i - 1] == sb[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[m][n]


def detect_dups(
    characters: list[str],
    *,
    max_jaso_distance: int = 1,
) -> dict[str, str]:
    """character list 안에서 dup 후보 → canonical 매핑.

    같은 list에서 자모 거리 ≤ max_jaso_distance인 쌍이 있으면
    첫 번째로 등장한 이름을 canonical로 통일.

    Returns: {original_name: canonical_name} (canonical과 같으면 자기 자신).
    """
    chars = [_normalize(c) for c in characters if c]
    canonical: dict[str, str] = {}
    seen: list[str] = []
    for c in chars:
        if not c:
            continue
        # 이미 등록됐으면 그 canonical 사용
        if c in canonical:
            continue
        # 기존 seen 중 자모 거리 가까운 것 찾기
        match = None
        for s in seen:
            if jaso_distance(c, s) <= max_jaso_distance and len(c) >= 2 and len(s) >= 2:
                match = s
                break
        if match is not None:
            canonical[c] = canonical[match]
        else:
            canonical[c] = c
            seen.append(c)
    return canonical


def detect_phantom(characters: list[str], passage: str) -> list[str]:
    """passage에 substring으로 등장하지 않는 character 이름 리스트."""
    norm_passage = _normalize(passage)
    phantom: list[str] = []
    for c in characters:
        nc = _normalize(c)
        if not nc:
            continue
        if nc not in norm_passage:
            phantom.append(c)
    return phantom


def postprocess_characters(
    characters: list[str],
    passage: str,
    *,
    drop_phantom: bool = True,
    dedupe: bool = True,
) -> tuple[list[str], dict]:
    """라벨링 결과의 characters 필드 정리.

    Returns:
        (cleaned_characters, change_log).
        change_log:
            {
                "input_count": int,
                "output_count": int,
                "phantoms_removed": [...],
                "dup_unifications": {original: canonical, ...},
            }
    """
    change_log = {
        "input_count": len(characters),
        "output_count": 0,
        "phantoms_removed": [],
        "dup_unifications": {},
    }

    # Step 1: dedupe
    if dedupe:
        canonical_map = detect_dups(characters)
        unified = [canonical_map.get(_normalize(c), c) for c in characters]
        for k, v in canonical_map.items():
            if k != v:
                change_log["dup_unifications"][k] = v
    else:
        unified = list(characters)

    # Remove exact duplicates after unification (preserve order)
    seen_set: set = set()
    deduped: list[str] = []
    for c in unified:
        nc = _normalize(c)
        if nc and nc not in seen_set:
            seen_set.add(nc)
            deduped.append(nc)

    # Step 2: phantom removal
    if drop_phantom:
        phantoms = detect_phantom(deduped, passage)
        change_log["phantoms_removed"] = phantoms
        final = [c for c in deduped if c not in phantoms]
    else:
        final = deduped

    change_log["output_count"] = len(final)
    return final, change_log
