"""Taxonomy review 정보 수집 — 6 항목 일괄 실행.

Per docs/taxonomy_review_prompt.md.

해석/제안 없음. 정량 추출만. 6 출력 + SUMMARY.

Run:
    python -m scripts.labeling.taxonomy_review_run
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TL1_ZIP = ROOT / "data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/1.Training/라벨링데이터/TL1.zip"
STAGE3 = ROOT / "data" / "external_private" / "gemma_review" / "work_e46069c4b4_stage3_private.jsonl"
OUT_DIR = ROOT / "docs" / "results" / "taxonomy_review"


def load_jsonl(p: Path) -> list[dict]:
    out: list[dict] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


# ---------- Item 1: work_distribution ----------

def item1_work_distribution() -> dict:
    """AI-Hub 023 전체 작품 list (TL1.zip 기준)."""
    print("[item1] loading TL1.zip for work inventory...", file=sys.stderr)
    from drama_mining.data.loader import stream_aihub_023
    from drama_mining.data.preprocess import preprocess_entry

    works: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "passage_count": 0,
        "lengths": [],
        "years": set(),
        "doc_origins_raw": set(),
    })
    for raw in stream_aihub_023(TL1_ZIP):
        pp = preprocess_entry(raw)
        if not pp["is_valid"]:
            continue
        # group by (doc_type, doc_origin_base)
        key = (pp["doc_type"], pp["doc_origin_base"])
        works[key]["passage_count"] += 1
        works[key]["lengths"].append(pp["passage_length"])
        if pp["published_year"]:
            works[key]["years"].add(str(pp["published_year"]))
        works[key]["doc_origins_raw"].add(pp["doc_origin_raw"])

    items: list[dict] = []
    import hashlib
    for (doc_type, base), info in works.items():
        anon = "work_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:10]
        lens = info["lengths"]
        items.append({
            "anonymized_origin": anon,
            "doc_origin_base": base,
            "doc_type": doc_type,
            "years": sorted(info["years"]),
            "passage_count": info["passage_count"],
            "passage_length_mean": round(statistics.mean(lens), 1) if lens else 0,
            "passage_length_median": int(statistics.median(lens)) if lens else 0,
            "doc_origins_raw_count": len(info["doc_origins_raw"]),
        })
    items.sort(key=lambda x: -x["passage_count"])

    # filter drama only (fm + fs)
    drama_items = [x for x in items if x["doc_type"] in ("fm_drama", "fs_drama")]
    return {
        "schema_version": "work_distribution_v1",
        "total_distinct_works_all_types": len(items),
        "total_distinct_drama_works": len(drama_items),
        "drama_works": drama_items,
        "all_works_compact": [
            {"doc_type": x["doc_type"], "anonymized_origin": x["anonymized_origin"],
             "passage_count": x["passage_count"], "years": x["years"]}
            for x in items
        ],
    }


# ---------- Item 2: label_space_analysis ----------

def item2_label_space() -> dict:
    recs = load_jsonl(STAGE3)
    recs = [r for r in recs if "_error" not in r.get("label", {})]
    total = len(recs)

    def primary_key(r: dict) -> tuple:
        l = r["label"]
        pp = tuple(sorted(l.get("primary_pressures", []) or []))
        pd = tuple(sorted(l.get("primary_desires", []) or []))
        ax = l.get("conflict_axis", "")
        return (pp, pd, ax)

    def full_key(r: dict) -> tuple:
        l = r["label"]
        pp = tuple(sorted(l.get("primary_pressures", []) or []))
        sp = tuple(sorted(l.get("secondary_pressures", []) or []))
        pd = tuple(sorted(l.get("primary_desires", []) or []))
        sd = tuple(sorted(l.get("secondary_desires", []) or []))
        ax = l.get("conflict_axis", "")
        return (pp, sp, pd, sd, ax)

    prim_counts = Counter(primary_key(r) for r in recs)
    full_counts = Counter(full_key(r) for r in recs)

    def summarize(counts: Counter, total: int) -> dict:
        unique = len(counts)
        top = counts.most_common(10)
        top10_cov = sum(c for _, c in top) / total * 100
        singletons = sum(1 for _, c in counts.items() if c == 1)
        return {
            "unique_count": unique,
            "top_10_coverage_pct": round(top10_cov, 1),
            "singleton_count": singletons,
            "top_10_distribution": [{"combo": str(k), "count": c} for k, c in top],
        }

    # examples
    most_freq_combo = prim_counts.most_common(1)[0][0]
    most_freq_records = [r for r in recs if primary_key(r) == most_freq_combo][:3]
    singleton_records: list[dict] = []
    for r in recs:
        if prim_counts[primary_key(r)] == 1:
            singleton_records.append(r)
            if len(singleton_records) >= 3:
                break

    def excerpt(r: dict) -> dict:
        passage = r.get("passage", "")
        return {
            "passage_id": r["passage_id"],
            "passage_excerpt_60": passage[:60].replace("\n", " "),
        }

    return {
        "schema_version": "label_space_analysis_v1",
        "total_passages": total,
        "primary_combinations": summarize(prim_counts, total),
        "full_combinations": summarize(full_counts, total),
        "examples": {
            "most_frequent_primary_combo": {
                "combo": str(most_freq_combo),
                "count": prim_counts[most_freq_combo],
                "sample_passages": [excerpt(r) for r in most_freq_records],
            },
            "singleton_primary_combos": {
                "count": prim_counts.most_common()[-3:],
                "sample_passages": [excerpt(r) for r in singleton_records[:3]],
            },
        },
    }


# ---------- Item 3: within_label_diversity ----------

def item3_within_label_diversity() -> dict:
    """가장 빈번한 primary combo 안에서 passage 클러스터링."""
    recs = load_jsonl(STAGE3)
    recs = [r for r in recs if "_error" not in r.get("label", {})]

    def primary_key(r: dict) -> tuple:
        l = r["label"]
        pp = tuple(sorted(l.get("primary_pressures", []) or []))
        pd = tuple(sorted(l.get("primary_desires", []) or []))
        ax = l.get("conflict_axis", "")
        return (pp, pd, ax)

    counts = Counter(primary_key(r) for r in recs)
    top_combo = counts.most_common(1)[0][0]
    cluster_records = [r for r in recs if primary_key(r) == top_combo]
    passages = [r["passage"] for r in cluster_records]

    # try sentence-transformers; fallback to BoW
    embedding_model = None
    embeddings = None
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        embeddings = model.encode(passages, show_progress_bar=False)
        embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    except Exception as e:
        print(f"[item3] sentence-transformers unavailable ({e}); using char ngram TF-IDF", file=sys.stderr)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=2000)
            embeddings = vec.fit_transform(passages).toarray()
            embedding_model = "sklearn TfidfVectorizer char_wb 2-4grams"
        except Exception as e2:
            print(f"[item3] sklearn unavailable too ({e2}); SKIPPING clustering", file=sys.stderr)
            return {
                "schema_version": "within_label_diversity_v1",
                "selected_primary_combo": str(top_combo),
                "passages_count": len(passages),
                "embedding_model": None,
                "error": "clustering libraries unavailable",
            }

    # KMeans
    from sklearn.cluster import KMeans  # type: ignore
    from sklearn.metrics import silhouette_score  # type: ignore
    import numpy as np  # type: ignore

    cluster_analysis: dict = {}
    cluster_examples: dict = {}
    for k in (2, 3, 4, 5):
        if k >= len(passages):
            continue
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(embeddings)
        try:
            sil = float(silhouette_score(embeddings, labels))
        except Exception:
            sil = None
        sizes = Counter(labels.tolist())
        cluster_analysis[f"k={k}"] = {
            "silhouette": round(sil, 3) if sil is not None else None,
            "cluster_sizes": [sizes[i] for i in range(k)],
        }
        # examples — take 2 representatives per cluster
        if k == 3:  # pick k=3 for examples
            for cid in range(k):
                idxs = [i for i, l in enumerate(labels) if l == cid][:2]
                cluster_examples[f"cluster_{cid}"] = [
                    {
                        "passage_id": cluster_records[i]["passage_id"],
                        "passage_excerpt_120": cluster_records[i]["passage"][:120].replace("\n", " "),
                    }
                    for i in idxs
                ]

    return {
        "schema_version": "within_label_diversity_v1",
        "selected_primary_combo": str(top_combo),
        "passages_count": len(passages),
        "embedding_model": embedding_model,
        "cluster_analysis": cluster_analysis,
        "cluster_examples_k3": cluster_examples,
    }


# ---------- Item 4: work_passage_features ----------

FAMILY_PATTERN = re.compile(r"엄마|아버지|아빠|어머니|아들|딸|형(님)?|누나|동생|할머니|할아버지|시어머니|시아버지|며느리|사위|남편|아내|처제|언니")
AUTHORITY_PATTERN = re.compile(r"사장|회장|이사|부장|대표|장관|총리|판사|검사|의원|선생님|교수|상사|회장님|국장")
DIALOG_PATTERN = re.compile(r'(["“”].{0,200}?["“”])|(\b[가-힣A-Za-z]{1,8}\s*\(\s*[ENF]?\s*\))')


def _features_for_passages(passages: list[str]) -> dict:
    fam = []
    auth = []
    lens = []
    turns = []
    for p in passages:
        fam.append(len(FAMILY_PATTERN.findall(p)))
        auth.append(len(AUTHORITY_PATTERN.findall(p)))
        lens.append(len(p))
        turns.append(len(DIALOG_PATTERN.findall(p)))
    return {
        "n_passages": len(passages),
        "family_term_count_mean": round(statistics.mean(fam), 2) if fam else 0,
        "family_term_density_per_1000_chars": round(sum(fam) / max(1, sum(lens)) * 1000, 2),
        "authority_term_count_mean": round(statistics.mean(auth), 2) if auth else 0,
        "authority_term_density_per_1000_chars": round(sum(auth) / max(1, sum(lens)) * 1000, 2),
        "passage_length_mean": round(statistics.mean(lens), 1) if lens else 0,
        "dialogue_marker_mean": round(statistics.mean(turns), 2) if turns else 0,
    }


def item4_work_passage_features() -> dict:
    from drama_mining.data.loader import stream_aihub_023
    from drama_mining.data.preprocess import preprocess_entry
    import random
    rng = random.Random(42)

    # 미우나고우나 passages (전체 225)
    miu_passages: list[str] = []
    other_works: dict[str, list[str]] = defaultdict(list)

    # 다양한 카테고리 작품 선택 — 비드라마 카테고리 1개 + fs_drama 1개 + fm_drama 1개 (미우나고우나 외)
    target_works: dict[str, str] = {}  # doc_origin_base → category
    # We'll pick first 3 large works from different categories
    print("[item4] streaming TL1 for passage extraction...", file=sys.stderr)
    counts: dict[str, int] = defaultdict(int)
    work_passages: dict[str, list[str]] = defaultdict(list)
    for raw in stream_aihub_023(TL1_ZIP):
        pp = preprocess_entry(raw)
        if not pp["is_valid"]:
            continue
        base = pp["doc_origin_base"]
        if base == "미우나고우나":
            miu_passages.append(pp["passage"])
            continue
        work_passages[base].append(pp["passage"])
        counts[base] += 1

    # pick: largest non-미우나고우나 fm_drama, largest fs_drama, largest enter/history/culture
    # (we don't have doc_type per work easily here, so re-stream once more is wasteful;
    # instead, just pick top 3 by passage count regardless of category)
    largest = sorted(counts.items(), key=lambda x: -x[1])[:3]

    feature_comparison: dict = {
        "미우나고우나": _features_for_passages(miu_passages),
    }
    for base, _cnt in largest:
        sample = rng.sample(work_passages[base], min(50, len(work_passages[base])))
        # anonymize
        import hashlib
        anon = "work_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:10]
        feature_comparison[anon] = _features_for_passages(sample)

    return {
        "schema_version": "work_passage_features_v1",
        "miu_total_passages": len(miu_passages),
        "comparison_works_anonymized": [
            "work_" + __import__("hashlib").sha256(base.encode("utf-8")).hexdigest()[:10]
            for base, _ in largest
        ],
        "comparison_works_passage_counts": [
            {"anonymized_origin": "work_" + __import__("hashlib").sha256(base.encode("utf-8")).hexdigest()[:10],
             "total_passages_in_corpus": cnt,
             "sampled": min(50, cnt)}
            for base, cnt in largest
        ],
        "feature_comparison": feature_comparison,
        "regex_definitions": {
            "family": FAMILY_PATTERN.pattern,
            "authority": AUTHORITY_PATTERN.pattern,
            "dialogue_marker": "korean quote or 'Name (E)' marker",
        },
    }


# ---------- Item 5: taxonomy_dump.md (text) ----------

PROMPT_V2_TAXONOMY = """
## Pressures (11)
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

## Desires (8)
- loyalty: 곁에 남으려는 마음
- survival: 자기 보호
- control: 통제 의지
- exposure_avoidance: 드러나지 않으려는 마음
- identity_preservation: 이름을 지키려는 마음
- commitment: 결정하려는 의지
- trust: 관계를 지키려는 마음
- group_safety: 그룹 안전

## Conflict Axes (8)
- loyalty_vs_survival
- uncertainty_vs_commitment
- control_vs_exposure
- collective_fear_vs_scapegoating
- identity_vs_failure
- atmosphere_vs_action
- trust_vs_self_protection
- unknown

## Prompt v2 사용 기준 (Stage 2.2 / Stage 3 lock)

### Pressure 선택 기준 — 가족극 우선순위 5
1) 가족 내부 갈등 표면화 → group_tension
2) 책임/비난이 한 인물에게 몰림 → blame_concentration
3) 자신의 처지·실패에 대한 자괴감 → shame_self
4) public_suspicion / authority_vigilance는 *외부 공권력 또는 가족 외부의 평가·감시·처벌이 명시적으로 묘사된 경우만*. 가족 내부는 group_tension.
5) love는 *Pressure*다. desires에 절대 넣지 마라.

### Desire 선택 기준 — survival 과사용 방지
1) 물리적 생존 위협(폭력·사망 가능성)이 명시되었는가?
2) 경제적 파산·실직 위협이 명시되었는가?
위 둘 중 하나 명확하면 → survival.
아니면 exposure_avoidance / identity_preservation / loyalty / commitment / trust.

### Confidence calibration
- 0.90: 단일 장면이고 인물/압력/욕망/갈등축이 모두 매우 명확함
- 0.75: 대체로 명확하지만 일부 해석 여지가 있음
- 0.60: 여러 장면이 섞였거나 라벨 중 일부가 불확실함
- 0.45: 인물/압력/욕망은 일부 보이나 conflict_axis가 불명확함
- 0.30: 정보가 부족하거나 장면 의미가 거의 불명확함

### 절대 금지
- unknown in primary_pressures / secondary_pressures / primary_desires / secondary_desires
- love in primary_desires / secondary_desires
"""


def item5_taxonomy_dump() -> str:
    return f"""# Taxonomy Dump

> Per `docs/taxonomy_review_prompt.md` 항목 5.
> 별도 taxonomy JSON 파일은 `engine/observer/`에 부재. taxonomy는 prompt 안 inline 정의.
> Stage 2.2 / Stage 3 prompt v2 (locked) 그대로 복사.

{PROMPT_V2_TAXONOMY}

## 출처

- 원본 위치: `scripts/labeling/oneshot_label_with_gemma_stage2_2.py` / `oneshot_label_with_gemma_stage3.py`
- 별도 taxonomy.json 파일: 없음
"""


# ---------- Item 6: reasoning_analysis ----------

def item6_reasoning_analysis() -> dict:
    recs = load_jsonl(STAGE3)
    recs = [r for r in recs if "_error" not in r.get("label", {})]

    gt_records = []
    non_gt_records = []
    for r in recs:
        pp = r["label"].get("primary_pressures", []) or []
        if "group_tension" in pp:
            gt_records.append(r)
        else:
            non_gt_records.append(r)

    def reasoning_of(r: dict) -> str:
        return r["label"].get("reasoning_brief", "") or ""

    # keyword frequencies
    KEYWORDS = ["가족", "갈등", "긴장", "권위", "비난", "수치", "사랑", "배신", "결정",
                "어머니", "아버지", "엄마", "아빠", "남편", "아내", "딸", "아들", "형", "동생",
                "사장", "회사", "공권력", "이웃", "사회"]

    def keyword_count(records: list[dict], kw: str) -> int:
        return sum(reasoning_of(r).count(kw) for r in records)

    keyword_freq = {
        "in_GT": {kw: keyword_count(gt_records, kw) for kw in KEYWORDS},
        "in_non_GT": {kw: keyword_count(non_gt_records, kw) for kw in KEYWORDS},
    }

    # top noun/verb candidates — simple Korean morpheme: ekn-eojeol split
    # 간단 휴리스틱: 단어 (whitespace) 기준 top frequencies (4글자 이내 한국어 명사 위주 후보)
    def top_tokens(records: list[dict], n: int = 20) -> list[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for r in records:
            for tok in reasoning_of(r).split():
                # remove punctuation
                t = re.sub(r"[(){}\[\].,!?:;\"'~/-]", "", tok)
                if 2 <= len(t) <= 6 and re.search(r"[가-힣]", t):
                    counter[t] += 1
        return counter.most_common(n)

    gt_lengths = [len(reasoning_of(r)) for r in gt_records]
    non_gt_lengths = [len(reasoning_of(r)) for r in non_gt_records]

    return {
        "schema_version": "reasoning_analysis_v1",
        "total_reasonings": len(recs),
        "group_tension_records": len(gt_records),
        "non_group_tension_records": len(non_gt_records),
        "keyword_frequency": keyword_freq,
        "top_terms": {
            "in_GT": top_tokens(gt_records),
            "in_non_GT": top_tokens(non_gt_records),
        },
        "reasoning_length_mean": {
            "GT": round(statistics.mean(gt_lengths), 1) if gt_lengths else 0,
            "non_GT": round(statistics.mean(non_gt_lengths), 1) if non_gt_lengths else 0,
        },
    }


# ---------- Main ----------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Item 1: work_distribution ===", file=sys.stderr)
    r1 = item1_work_distribution()
    (OUT_DIR / "work_distribution.json").write_text(
        json.dumps(r1, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== Item 2: label_space_analysis ===", file=sys.stderr)
    r2 = item2_label_space()
    (OUT_DIR / "label_space_analysis.json").write_text(
        json.dumps(r2, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== Item 3: within_label_diversity ===", file=sys.stderr)
    r3 = item3_within_label_diversity()
    (OUT_DIR / "within_label_diversity.json").write_text(
        json.dumps(r3, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== Item 4: work_passage_features ===", file=sys.stderr)
    r4 = item4_work_passage_features()
    (OUT_DIR / "work_passage_features.json").write_text(
        json.dumps(r4, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== Item 5: taxonomy_dump.md ===", file=sys.stderr)
    r5 = item5_taxonomy_dump()
    (OUT_DIR / "taxonomy_dump.md").write_text(r5, encoding="utf-8")

    print("=== Item 6: reasoning_analysis ===", file=sys.stderr)
    r6 = item6_reasoning_analysis()
    (OUT_DIR / "reasoning_analysis.json").write_text(
        json.dumps(r6, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # SUMMARY.md
    summary_lines = [
        "# Taxonomy 재검토 정보 수집 보고서",
        "",
        "> Per `docs/taxonomy_review_prompt.md`. 정보 수집만. 해석/제안/결정 없음.",
        "",
        "## 항목별 핵심 숫자",
        "",
        f"### 항목 1: AI-Hub 023 작품 inventory",
        f"- 전체 distinct works (preprocess valid): {r1['total_distinct_works_all_types']}",
        f"- drama (fm + fs) distinct works: {r1['total_distinct_drama_works']}",
        f"- 미우나고우나 passage count: {next((w['passage_count'] for w in r1['drama_works'] if w['doc_origin_base']=='미우나고우나'), 'N/A')}",
        "",
        f"### 항목 2: Label space (Stage 3, 225 passages)",
        f"- Unique primary combinations: {r2['primary_combinations']['unique_count']}",
        f"- Top 10 primary combinations coverage: {r2['primary_combinations']['top_10_coverage_pct']}%",
        f"- Singleton primary combos: {r2['primary_combinations']['singleton_count']}",
        f"- Unique full combinations: {r2['full_combinations']['unique_count']}",
        f"- Top 10 full combinations coverage: {r2['full_combinations']['top_10_coverage_pct']}%",
        f"- Most frequent primary combo: count {r2['examples']['most_frequent_primary_combo']['count']}",
        "",
        f"### 항목 3: Within-label diversity",
        f"- Selected combo: {r3.get('selected_primary_combo')}",
        f"- Passages in combo: {r3.get('passages_count')}",
        f"- Embedding model: {r3.get('embedding_model')}",
    ]
    if "cluster_analysis" in r3:
        for k, v in r3["cluster_analysis"].items():
            summary_lines.append(f"- {k}: silhouette={v['silhouette']}, sizes={v['cluster_sizes']}")
    summary_lines.extend([
        "",
        f"### 항목 4: Cross-work passage features",
        f"- 미우나고우나 family_term_density_per_1000_chars: {r4['feature_comparison']['미우나고우나']['family_term_density_per_1000_chars']}",
        f"- 미우나고우나 authority_term_density_per_1000_chars: {r4['feature_comparison']['미우나고우나']['authority_term_density_per_1000_chars']}",
        "",
        "비교 작품 (anonymized) family / authority density:",
    ])
    for k, v in r4["feature_comparison"].items():
        if k == "미우나고우나":
            continue
        summary_lines.append(f"- {k}: family={v['family_term_density_per_1000_chars']} / authority={v['authority_term_density_per_1000_chars']}")
    summary_lines.extend([
        "",
        f"### 항목 5: Taxonomy dump",
        f"- 별도 taxonomy JSON 파일 없음. prompt v2 inline 정의 → taxonomy_dump.md에 추출.",
        "",
        f"### 항목 6: Reasoning analysis",
        f"- Total reasonings: {r6['total_reasonings']}",
        f"- group_tension records: {r6['group_tension_records']}",
        f"- non-group_tension records: {r6['non_group_tension_records']}",
        f"- reasoning length mean GT: {r6['reasoning_length_mean']['GT']}",
        f"- reasoning length mean non-GT: {r6['reasoning_length_mean']['non_GT']}",
        f"- keyword '가족' in GT: {r6['keyword_frequency']['in_GT']['가족']}",
        f"- keyword '가족' in non-GT: {r6['keyword_frequency']['in_non_GT']['가족']}",
        f"- keyword '갈등' in GT: {r6['keyword_frequency']['in_GT']['갈등']}",
        f"- keyword '갈등' in non-GT: {r6['keyword_frequency']['in_non_GT']['갈등']}",
        "",
        "## 미해결 의문 (Lee 결정 필요)",
        "",
        "- 미우나고우나 외 작품에서 group_tension 비율이 비슷한지는 *라벨링 없이는 단정 불가*. 항목 4의 family/authority term density는 *간접 신호*만 제공.",
        "- 항목 3 cluster silhouette이 0.x 이상이면 'taxonomy가 본문 다양성을 못 잡는다' 시그널이지만, *얼마나 강한 시그널인지*는 Lee 판단.",
        "- 항목 6 reasoning에서 '가족' 비중이 GT vs non-GT에서 어떻게 다른지가 *Gemma의 trigger 단어*를 보여주지만, 그것이 *taxonomy 한계*인지 *prompt 한계*인지 분리 안 됨.",
        "",
        "## 다음 단계 추천 없음",
        "",
        "이 보고서는 정보 수집만 함. 재검토 결정은 Lee와 Claude 대화로 별도 처리.",
        "",
        "## 산출 파일",
        "",
        "- `work_distribution.json`",
        "- `label_space_analysis.json`",
        "- `within_label_diversity.json`",
        "- `work_passage_features.json`",
        "- `taxonomy_dump.md`",
        "- `reasoning_analysis.json`",
        "- `SUMMARY.md` (이 파일)",
        "",
        "## Raw Exposure Audit",
        "",
        "- 작품명 원문은 항목 1의 `drama_works[].doc_origin_base`에서 노출 (review/audit 목적). 그 외 SUMMARY에선 anonymized hash만 표시.",
        "- raw passage 전문은 항목 2/3 examples에서 60~120자 excerpt만. 전문 노출 없음.",
        "- AI-Hub raw data 자체는 `data/023.../` (gitignored) 그대로.",
    ])
    (OUT_DIR / "SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print("=== ALL DONE ===", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
