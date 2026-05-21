"""ONESHOT crawl script for WITNESS Phase 3.

Per docs/witness_crawl_directive.md (2026-05-11).
This is NOT a reusable framework. Run once, get data, done.

Output: data/raw/{title_id}/{ep:02d}.json (per_episode) or
        data/raw/{title_id}/synopsis_full.json (full_synopsis).
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "WITNESS-Research/0.1 (academic-portfolio)"
}

REQUEST_DELAY_SEC = 3.0

OUTPUT_ROOT = Path("data/raw")

SOURCES = [
    {
        "title_id": "penthouse_s1",
        "title_ko": "펜트하우스 시즌 1",
        "broadcaster": "SBS",
        "writer": "김순옥",
        "broadcast_date": "2020-10-26",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/펜트하우스(드라마)",
    },
    {
        "title_id": "married_world",
        "title_ko": "부부의 세계",
        "broadcaster": "JTBC",
        "writer": "주현",
        "broadcast_date": "2020-03-27",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/부부의 세계",
    },
    {
        "title_id": "wife_temptation",
        "title_ko": "아내의 유혹",
        "broadcaster": "SBS",
        "writer": "김순옥",
        "broadcast_date": "2008-11-03",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/아내의 유혹/줄거리",
    },
    {
        "title_id": "my_mans_woman",
        "title_ko": "내 남자의 여자",
        "broadcaster": "SBS",
        "writer": "김수현",
        "broadcast_date": "2007-04-02",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/내 남자의 여자",
    },
    {
        "title_id": "wives_club",
        "title_ko": "조강지처 클럽",
        "broadcaster": "SBS",
        "writer": "문영남",
        "broadcast_date": "2007-09-08",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/조강지처 클럽(SBS)",
    },
    {
        "title_id": "loved_perhaps",
        "title_ko": "사랑했나봐",
        "broadcaster": "MBC",
        "writer": "원영옥",
        "broadcast_date": "2012-10-15",
        "mode": "full_synopsis",
        "url": "https://namu.wiki/w/사랑했나봐(드라마)",
    },
]


def fetch_page(url: str) -> tuple[str, int]:
    """페이지를 가져와서 HTML 반환. 실패 시 ("", 0)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.text, len(resp.text)
        print(f"  [WARN] status {resp.status_code} for {url}")
        return "", 0
    except Exception as e:
        print(f"  [ERR] {e} for {url}")
        return "", 0


def extract_synopsis_text(html: str) -> str:
    """HTML에서 줄거리 텍스트만 추출.

    나무위키 페이지 구조 기반. selector는 site 구조 따라 조정 가능.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 나무위키 메인 컨텐츠 영역 시도 (여러 후보)
    content = (
        soup.select_one("article")
        or soup.select_one(".wiki-content")
        or soup.select_one("main")
        or soup.body
    )

    if content is None:
        return ""

    # 불필요 요소 제거
    for tag in content.select("nav, .toc, .footnote, .img-caption, .reference, script, style"):
        tag.decompose()

    text = content.get_text(separator="\n", strip=True)

    # 정규화
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def crawl_per_episode(source: dict) -> int:
    title_id = source["title_id"]
    saved = 0
    for ep_no, url in source["urls"].items():
        print(f"  [{title_id}] ep{ep_no:02d}: {url}")
        html, raw_len = fetch_page(url)
        if not html:
            time.sleep(REQUEST_DELAY_SEC)
            continue

        text = extract_synopsis_text(html)
        if len(text) < 50:
            print(f"    [WARN] extracted text too short ({len(text)} chars)")

        record = {
            "schema_version": "raw_synopsis_v1",
            "title_id": title_id,
            "title_ko": source["title_ko"],
            "episode_no": ep_no,
            "synopsis_text_ko": text,
            "broadcast_date": source["broadcast_date"],
            "broadcaster": source["broadcaster"],
            "writer": source["writer"],
            "source_url": url,
            "source_license": "CC BY-NC-SA 2.0 KR",
            "source_site": "namu_wiki",
            "collected_at_iso": datetime.now(timezone.utc).isoformat(),
            "collected_by": "oneshot_crawl_synopsis.py",
            "raw_html_length": raw_len,
            "extraction_notes": "",
        }
        out_path = OUTPUT_ROOT / title_id / f"{ep_no:02d}.json"
        save_json(record, out_path)
        saved += 1
        time.sleep(REQUEST_DELAY_SEC)
    return saved


def crawl_full_synopsis(source: dict) -> int:
    title_id = source["title_id"]
    url = source["url"]
    print(f"  [{title_id}] full: {url}")
    html, raw_len = fetch_page(url)
    if not html:
        time.sleep(REQUEST_DELAY_SEC)
        return 0

    text = extract_synopsis_text(html)
    if len(text) < 100:
        print(f"    [WARN] extracted text too short ({len(text)} chars)")

    record = {
        "schema_version": "raw_synopsis_v1",
        "title_id": title_id,
        "title_ko": source["title_ko"],
        "episode_no": 0,
        "synopsis_text_ko": text,
        "broadcast_date": source["broadcast_date"],
        "broadcaster": source["broadcaster"],
        "writer": source["writer"],
        "source_url": url,
        "source_license": "CC BY-NC-SA 2.0 KR",
        "source_site": "namu_wiki",
        "collected_at_iso": datetime.now(timezone.utc).isoformat(),
        "collected_by": "oneshot_crawl_synopsis.py",
        "raw_html_length": raw_len,
        "extraction_notes": "전체 작품 줄거리 (회차 미분할). 어노테이션 단계에서 phase 또는 회차 분할 필요.",
    }
    out_path = OUTPUT_ROOT / title_id / "synopsis_full.json"
    save_json(record, out_path)
    time.sleep(REQUEST_DELAY_SEC)
    return 1


def main() -> None:
    print("=" * 60)
    print("WITNESS Phase 3 — Oneshot Synopsis Crawler")
    print("=" * 60)

    total_saved = 0
    for source in SOURCES:
        print(f"\n[{source['title_id']}] {source['title_ko']}")
        if source["mode"] == "per_episode":
            total_saved += crawl_per_episode(source)
        elif source["mode"] == "full_synopsis":
            total_saved += crawl_full_synopsis(source)

    print(f"\n{'='*60}")
    print(f"Done. Saved {total_saved} files under {OUTPUT_ROOT}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
