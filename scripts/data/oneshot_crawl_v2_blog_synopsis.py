"""ONESHOT v2 crawl: blog/wiki synopsis with section filtering.

Per docs/witness_crawl_v2_directive.md (2026-05-11).
NOT a reusable framework. Run once, get data, done.

v1 차이점:
- 사이트별 selector 분기 (tistory_macmugane / namu_wiki)
- namu_wiki는 헤딩 기반 섹션 필터링 (개요/기획의도/시놉시스/결말 등만)
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

HEADERS = {"User-Agent": "WITNESS-Research/0.2 (academic-portfolio)"}
REQUEST_DELAY_SEC = 3.0
OUTPUT_ROOT = Path("data/raw")

# 작품별 출처 (data/raw_v2/_source_decisions.json 와 sync)
SOURCES = [
    {
        "title_id": "penthouse_s1",
        "title_ko": "펜트하우스 시즌 1",
        "broadcaster": "SBS",
        "writer": "김순옥",
        "broadcast_date": "2020-10-26",
        "source_url": "https://macmugane.tistory.com/entry/펜트하우스-시즌1-시즌2-시즌3-줄거리-결말",
        "source_site": "tistory_macmugane",
        "extraction_strategy": "tistory_entry_content",
        "content_selector": ".entry-content",
        "source_license": "blog content - academic non-commercial use (출처 명시)",
    },
    {
        "title_id": "married_world",
        "title_ko": "부부의 세계",
        "broadcaster": "JTBC",
        "writer": "주현",
        "broadcast_date": "2020-03-27",
        "source_url": "https://namu.wiki/w/부부의 세계",
        "source_site": "namu_wiki",
        "extraction_strategy": "namu_section_filter",
        "included_sections": ["개요", "기획의도", "등장인물", "평가"],
        "source_license": "CC BY-NC-SA 2.0 KR",
    },
    {
        "title_id": "wife_temptation",
        "title_ko": "아내의 유혹",
        "broadcaster": "SBS",
        "writer": "김순옥",
        "broadcast_date": "2008-11-03",
        "source_url": "https://namu.wiki/w/아내의 유혹/줄거리",
        "source_site": "namu_wiki",
        "extraction_strategy": "namu_subpage_full",
        "included_sections": None,  # 전체 추출
        "source_license": "CC BY-NC-SA 2.0 KR",
    },
    {
        "title_id": "my_mans_woman",
        "title_ko": "내 남자의 여자",
        "broadcaster": "SBS",
        "writer": "김수현",
        "broadcast_date": "2007-04-02",
        "source_url": "https://namu.wiki/w/내 남자의 여자",
        "source_site": "namu_wiki",
        "extraction_strategy": "namu_section_filter",
        "included_sections": ["개요", "기획의도", "특징", "등장인물"],
        "source_license": "CC BY-NC-SA 2.0 KR",
    },
    {
        "title_id": "wives_club",
        "title_ko": "조강지처 클럽",
        "broadcaster": "SBS",
        "writer": "문영남",
        "broadcast_date": "2007-09-08",
        "source_url": "https://namu.wiki/w/조강지처 클럽(SBS)",
        "source_site": "namu_wiki",
        "extraction_strategy": "namu_section_filter",
        "included_sections": ["개요", "기획의도", "시놉시스", "등장인물", "결말"],
        "source_license": "CC BY-NC-SA 2.0 KR",
    },
    {
        "title_id": "loved_perhaps",
        "title_ko": "사랑했나봐",
        "broadcaster": "MBC",
        "writer": "원영옥",
        "broadcast_date": "2012-10-15",
        "source_url": "https://namu.wiki/w/사랑했나봐(드라마)",
        "source_site": "namu_wiki",
        "extraction_strategy": "namu_section_filter",
        "included_sections": ["개요", "등장인물", "예나 선정이 딸이에요"],
        "source_license": "CC BY-NC-SA 2.0 KR",
    },
]


def _normalize_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    # 시청률표 라인 제거
    lines = text.split("\n")
    filtered = []
    for line in lines:
        if re.match(r"^\s*\d+[회화]?\s*\|?\s*\d+\.?\d*\s*%", line):
            continue
        if re.match(r"^\s*\d{4}\.?\s*\d+\.?\s*\d+\.?\s*$", line):
            continue
        filtered.append(line)
    return "\n".join(filtered).strip()


def _strip_namu_heading_marker(heading_text: str) -> str:
    """'1.개요[편집]' → '개요'."""
    text = heading_text.replace("[편집]", "").strip()
    # leading section number "1." or "1.2." 제거
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
    return text.strip()


def extract_tistory_entry_content(html: str, selector: str) -> str:
    """티스토리 페이지: .entry-content 안의 텍스트만."""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(selector) or soup.select_one("article") or soup.body
    if content is None:
        return ""
    # 불필요 요소 제거
    for tag in content.select(
        "nav, header, footer, aside, .sidebar, .comments, .related, "
        ".tags, .share, .author-info, script, style, .advertisement, "
        ".ad, [class*='banner']"
    ):
        tag.decompose()
    text = content.get_text(separator="\n", strip=True)
    return _normalize_text(text)


_NAMU_HEADING_RE = re.compile(
    r"(\d+(?:\.\d+)*)\s*\.\s*([^\[\n]+?)\s*\[\s*편집\s*\]",
    re.DOTALL,
)


def extract_namu_sections(html: str, included_sections: list[str] | None) -> str:
    """namu.wiki 페이지: 전체 article 텍스트를 추출 후 헤딩 마커로 split.

    included_sections=None → 전체 article 텍스트.
    아닌 경우, '1.개요[편집]' 같은 헤딩 마커 line을 찾아 그 다음 헤딩 직전까지 수집.
    section_name이 included_sections의 어느 항목을 포함하면 수집.
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article") or soup.body
    if article is None:
        return ""

    # 불필요 요소 제거
    for tag in article.select("nav, .toc, script, style"):
        tag.decompose()

    full_text = article.get_text(separator="\n", strip=True)

    # 첫 번째 "1.개요[편집]" 또는 비슷한 top-level heading 위치 — 그 앞은 nav/카테고리 메타
    first_heading = _NAMU_HEADING_RE.search(full_text)
    if first_heading is not None:
        full_text = full_text[first_heading.start():]

    if included_sections is None:
        return _normalize_text(full_text)

    # 헤딩 마커 위치 찾기 (text-based)
    matches = list(_NAMU_HEADING_RE.finditer(full_text))
    if not matches:
        # fallback: heading marker 없으면 전체 텍스트
        return _normalize_text(full_text)

    collected_parts: list[str] = []
    for i, m in enumerate(matches):
        section_num = m.group(1)
        section_name = m.group(2).strip()

        # included check
        is_included = any(target in section_name for target in included_sections)
        if not is_included:
            continue

        # section body: heading end → next h2 heading start (or EOF)
        body_start = m.end()
        # next *top-level* h2 (depth 1 — no dot in section_num)
        # 즉, "2.기획의도" 다음 다른 "X.{name}" (X는 1자리) 헤딩까지
        body_end = len(full_text)
        is_top_level = "." not in section_num
        for j in range(i + 1, len(matches)):
            n_num = matches[j].group(1)
            n_is_top = "." not in n_num
            if is_top_level and n_is_top:
                body_end = matches[j].start()
                break
            if not is_top_level:
                # sub-section: next heading of *any* level stops
                body_end = matches[j].start()
                break

        section_body = full_text[body_start:body_end].strip()
        if section_body:
            collected_parts.append(f"## {section_name}\n{section_body}")

    text = "\n\n".join(collected_parts)
    return _normalize_text(text)


def extract_synopsis_text(html: str, source: dict) -> str:
    strat = source["extraction_strategy"]
    if strat == "tistory_entry_content":
        return extract_tistory_entry_content(html, source["content_selector"])
    if strat in ("namu_section_filter", "namu_subpage_full"):
        return extract_namu_sections(html, source.get("included_sections"))
    # fallback
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    return _normalize_text(body.get_text(separator="\n", strip=True))


def crawl_one(source: dict) -> tuple[bool, int]:
    """(success, text_length) 반환."""
    url = source["source_url"]
    title_id = source["title_id"]
    print(f"\n[{title_id}] {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"  [WARN] status {resp.status_code}")
            return False, 0
        html = resp.text
    except Exception as e:
        print(f"  [ERR] {e}")
        return False, 0

    text = extract_synopsis_text(html, source)
    text_len = len(text)
    if text_len < 1000:
        print(f"  [WARN] text too short: {text_len} chars")

    record = {
        "schema_version": "raw_synopsis_v2",
        "title_id": title_id,
        "title_ko": source["title_ko"],
        "episode_no": 0,
        "synopsis_text_ko": text,
        "broadcast_date": source["broadcast_date"],
        "broadcaster": source["broadcaster"],
        "writer": source["writer"],
        "source_url": url,
        "source_site": source["source_site"],
        "source_license": source["source_license"],
        "extraction_strategy": source["extraction_strategy"],
        "included_sections": source.get("included_sections"),
        "collected_at_iso": datetime.now(timezone.utc).isoformat(),
        "collected_by": "oneshot_crawl_v2_blog_synopsis.py",
        "raw_html_length": len(html),
        "extraction_notes": "헤딩 기반 섹션 필터 적용 (namu_wiki)." if source["source_site"] == "namu_wiki" else "tistory .entry-content 전체 추출.",
    }
    out_path = OUTPUT_ROOT / title_id / "synopsis_full.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] saved {text_len} chars")
    time.sleep(REQUEST_DELAY_SEC)
    return True, text_len


def main() -> None:
    print("=" * 60)
    print("WITNESS v2 Crawl - Blog/Wiki Synopsis")
    print("=" * 60)

    results: list[tuple[str, bool, int]] = []
    for source in SOURCES:
        ok, length = crawl_one(source)
        results.append((source["title_id"], ok, length))

    print(f"\n{'='*60}")
    success = sum(1 for _, ok, _ in results if ok)
    print(f"Done. {success}/{len(SOURCES)} succeeded.")
    for tid, ok, ln in results:
        flag = "OK" if ok else "FAIL"
        print(f"  [{flag}] {tid:20s} {ln:>6d} chars")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
