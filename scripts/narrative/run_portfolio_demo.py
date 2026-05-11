"""Run Portfolio Demo — single command pipeline (Stage 0).

Per `docs/WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md` §0, §3, §13.

한 명령어로 전체 데모를 생성한다:
    Stage 1 (Simulation): observer dump 확인 / 필요시 생성
    Stage 2 (Observer):   moments 추출
    Stage 3 (Pressure):   PressureSummary 생성
    Stage 4 (Threads):    StoryThread + MomentLink
    Stage 5 (Candidates): StoryCandidate (named, conflict-tuned)
    Stage 6 (Seed Cards): StorySeedCard 변환 (일반인용 한국어)
    Stage 7 (Evidence):   evidence_report.md
    Stage 8 (HTML):       index.html (self-contained)

산출:
    docs/portfolio/demo/
        index.html                   ← 메인
        story_seed_cards.md
        story_seed_cards.json
        evidence_report.md
        pressure_summary.json
        demo_run_summary.json
        debug/
            (기존 내부 산출물 링크)

Usage:
    python scripts/narrative/run_portfolio_demo.py
    python scripts/narrative/run_portfolio_demo.py --anchor peter_scarcity_baseline --seed 0 --ticks 200
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.data_narrative import (  # noqa: E402
    extract_narrative_evidence,
)
from engine.observer.episode_outline import (  # noqa: E402
    build_episode_outline, render_episode_outline_md,
)
from engine.observer.universal_seed_adapter import (  # noqa: E402
    assemble_skeleton_output,
)


# Display-name overrides for general-audience surface.
# Engine module은 content-agnostic하므로 이름 매핑은 *content layer*인 이
# orchestrator에 위치한다. Per directive 2026-05-08: "Peter 대신 '베드로'
# 우선 사용. 단 내부 데이터/JSON은 기존 이름 유지 가능."
PETER_ANCHOR_NAME_OVERRIDES_KO: dict[str, str] = {
    "Peter":    "베드로",
    "Andrew":   "안드레",
    "James":    "야고보",
    "John":     "요한",
    "Judas":    "유다",
    "Caiaphas": "가야바",
    "Pilate":   "빌라도",
}
from engine.observer.identity_resolver import IdentityResolver  # noqa: E402
from engine.observer.moment_extractor import extract_moments  # noqa: E402
from engine.observer.pressure_summary import build_pressure_summary  # noqa: E402
from engine.observer.run_log import (  # noqa: E402
    PIPELINE_STEP_LABELS, RunLog, StepTimer, make_pipeline_steps, render_run_log_md,
)
from engine.observer.scene_brief import build_scene_brief  # noqa: E402
from engine.observer.story_audit import audit_pair, load_anchor_blocklist  # noqa: E402
from engine.observer.story_candidate_builder import build_story_candidates  # noqa: E402
from engine.observer.story_seed_card import build_seed_card  # noqa: E402
from engine.observer.story_viability import score_candidate  # noqa: E402
from engine.observer.thread_builder import build_story_threads, link_moments  # noqa: E402
from engine.observer.treatment import build_treatment  # noqa: E402

# Engine simulation entry — called fresh on every orchestrator run
sys.path.insert(0, str(ROOT / "scripts" / "visual"))
from export_dot_observer_data import export_dot_observer_data  # noqa: E402


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

# Role-based body for supporting seeds (S02~Sn). 수치 0, 일반인용 한국어.
_SUPPORTING_BODY_BY_ROLE: dict[str, str] = {
    "결정을 미루는 사람": (
        "{name}은(는) 압력을 느끼지만 바로 움직이지 않는다. "
        "그의 흐름은 결정을 미루는 시간이 어떻게 긴장으로 변하는지를 보여준다."
    ),
    "베드로를 지켜보는 목격자": (
        "{name}은(는) 같은 압력 안에 있지만 중심에서 행동하지 않는다. "
        "그는 베드로의 변화를 가까이서 지켜보는 시선이 될 수 있다."
    ),
    "지켜보는 사람": (
        "{name}은(는) 같은 압력 안에 있지만 중심에서 행동하지 않는다. "
        "그는 다른 인물의 변화를 가까이서 지켜보는 시선이 될 수 있다."
    ),
    "늦게 반응하는 인물": (
        "{name}은(는) 압력이 지나간 뒤에야 반응이 드러나는 인물이다. "
        "같은 상황에서도 반응의 속도가 다를 수 있음을 보여준다."
    ),
    "늦게 반응하는 사람": (
        "{name}은(는) 압력이 지나간 뒤에야 반응이 드러나는 인물이다. "
        "같은 상황에서도 반응의 속도가 다를 수 있음을 보여준다."
    ),
}

# Role-based title (보조 씨앗을 *역할별로 차별화* — directive §4)
_SUPPORTING_TITLE_BY_ROLE: dict[str, str] = {
    "결정을 미루는 사람":           "결정을 미루는 사람",
    "베드로를 지켜보는 목격자":     "지켜보는 사람",
    "지켜보는 사람":                "지켜보는 사람",
    "늦게 반응하는 인물":           "늦게 반응하는 사람",
    "늦게 반응하는 사람":           "늦게 반응하는 사람",
}


def _render_seed_cards_md(seeds: list, run_label: str, episode_outline=None) -> str:
    """일반인용 story-tone 씨앗 카드 — 수치 0.

    S01 (메인 씨앗)은 짧게 압축 — 이미 메인 에피소드에서 다뤄지므로 "중심축으로
    사용된다"만 명시. S02~S04 (보조 씨앗)은 *역할별로 차별화*된 title +
    수치 없는 단락. 수치 인용은 evidence_report.md / Technical Appendix로 분리.
    """
    from engine.observer.episode_outline import (
        resolve_korean_josa as _j,
    )

    def _to_korean_name(n: str) -> str:
        return PETER_ANCHOR_NAME_OVERRIDES_KO.get(n, n)

    head = f"""# WITNESS — 이야기 씨앗 카드

> 시뮬레이션 한 번을 돌리면, 그 안에서 여러 인물의 압력 흐름이 쌓이고
> 몇 개의 *이야기 씨앗*이 정리됩니다. 아래는 그 결과입니다.

> 시나리오: `{run_label}`
> 씨앗 수: **{len(seeds)}**

---

"""

    # episode_outline의 supporting_arcs를 seed_id로 빠르게 조회할 수 있도록.
    sup_role_by_seed: dict[str, str] = {}
    if episode_outline is not None:
        for sa in episode_outline.supporting_arcs:
            sup_role_by_seed[sa.seed_id] = sa.role_label
        main_title = episode_outline.title
    else:
        main_title = ""

    cards = []
    for i, s in enumerate(seeds, start=1):
        is_main = (i == 1)
        name_ko = _to_korean_name(s.main_character)
        usable = " · ".join(s.usable_for) if s.usable_for else "(미정)"
        if is_main:
            # S01: 짧게 — 메인 에피소드의 중심축
            title = s.title
            body = (
                f"{name_ko}은(는) 곁에 남으려 하지만, 압력이 커질수록 점점 "
                f"말하지 않는 쪽으로 밀려난다."
            )
            ref_line = (
                f"이 씨앗은 메인 에피소드 「{main_title}」의 중심축으로 사용됩니다."
                if main_title else
                "이 씨앗은 메인 에피소드의 중심축으로 사용됩니다."
            )
            card_md = f"""## {title}

> *메인 씨앗* · `{s.seed_id}` · 중심 인물: **{name_ko}**

{body}

{ref_line}

> {s.unresolved_question}

<details>
<summary>활용 / 근거 (접힘)</summary>

활용 가능: {usable}
검증 결과: **{s.confidence_label}** · 감사 결과: **{s.evidence_summary.audit_status}**

</details>
"""
        else:
            # S02~Sn: 역할별 차별화된 title + 본문
            # role_label은 placeholder ("을(를)" 등)를 포함할 수 있어
            # lookup 전에 josa resolve.
            role_raw = _j(sup_role_by_seed.get(s.seed_id, ""))
            role_title = _SUPPORTING_TITLE_BY_ROLE.get(role_raw, role_raw or "보조 흐름")
            body = _SUPPORTING_BODY_BY_ROLE.get(
                role_raw,
                f"{name_ko}은(는) 같은 압력 안에서 다른 속도로 흔들리는 인물이다."
            ).format(name=name_ko)

            card_md = f"""## {role_title}

> *보조 씨앗* · `{s.seed_id}` · 중심 인물: **{name_ko}**

{body}

> {s.unresolved_question}

<details>
<summary>활용 / 근거 (접힘)</summary>

활용 가능: {usable}
검증 결과: **{s.confidence_label}** · 감사 결과: **{s.evidence_summary.audit_status}** · 변화 신호 **{s.evidence_summary.evidence_count}개**

</details>
"""
        cards.append(_j(card_md))

    return head + "\n\n---\n\n".join(cards) + "\n"


def _render_evidence_report_md(seeds: list, audits: list, run_label: str) -> str:
    n_pass = sum(1 for a in audits if a.overall == "pass")
    n_risky = sum(1 for a in audits if a.overall == "risky")
    n_fail = sum(1 for a in audits if a.overall == "audit_fail")
    head = f"""# WITNESS — 검증 / 근거 리포트

> 시나리오: `{run_label}`

## 요약

이 데모에서 만들어진 이야기 씨앗은 임의로 작성된 것이 아니라, 시뮬레이션에서
반복적으로 나타난 *변화 흐름*에서 자동으로 추출된 것입니다.

| 항목 | 값 |
|---|---|
| 만들어진 씨앗 수 | **{len(seeds)}** |
| 감사 통과 | **{n_pass}** |
| 감사 주의 | {n_risky} |
| 감사 실패 | {n_fail} |

## 검증 항목 (각 씨앗마다 자동 적용)

- 없는 사건이 추가되지 않았는가?
- 대사가 만들어지지 않았는가?
- 감정 과잉 서술이 없는가?
- 시나리오 슬러그(EXT. / FADE IN 등)가 없는가?
- 시나리오별 금지 어구(`content/anchors/{run_label}/audit_blocklist.json`)에 걸리는가?

## 씨앗별 근거

"""
    rows = []
    for s, a in zip(seeds, audits):
        signals = ", ".join(s.evidence_summary.strongest_signals) or "(없음)"
        violations = ", ".join(f"`{v.phrase}`" for v in a.violations) or "없음"
        risky = ", ".join(f"`{r.phrase}`" for r in a.risky_phrases) or "없음"
        rows.append(f"""### {s.seed_id} — {s.title}

- **신뢰도**: `{s.confidence_label}`
- **감사 결과**: `{s.evidence_summary.audit_status}`
- **연결된 변화 신호**: {s.evidence_summary.evidence_count}개
- **주요 변화**: {signals}
- **위반 항목**: {violations}
- **주의 표현**: {risky}
- **위험 노트**: {s.risk_note}
""")
    return head + "\n\n".join(rows) + """

---

## 기술 부록 (개발자/면접관용)

상세 내부 산출물:

- `data/narrative/story_candidates.json` — 후보 카드 (검증자용)
- `data/narrative/story_threads.json` — 이야기 흐름 (그래프 단위)
- `data/narrative/moments.json` — 변화 신호 (atomic units)
- `data/narrative/story_viability_scores.json` — 100점 채점
- `data/narrative/story_viability_audit.json` — 자동 감사 raw

검증 스택:
- Stage A-D + F: 자동 — `scripts/narrative/build_story_viability_report.py`
- Stage E (인간 검토): `docs/portfolio/HUMAN_PICK_TEST_PACK.md`

---

*Generated by* `scripts/narrative/run_portfolio_demo.py`.
"""


# ---------------------------------------------------------------------------
# HTML rendering (self-contained, no external assets)
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<title>WITNESS · 시뮬레이션 + 에피소드 데모</title>
<style>
  :root {
    --bg: #14110d;
    --bg-soft: #1c1813;
    --bg-card: #221d18;
    --fg: #d6d0c7;
    --fg-dim: #8b827a;
    --accent: #e8c87a;
    --accent-soft: rgba(232, 200, 122, 0.08);
    --border: #2a221c;
    --robust: #7fc8a4;
    --moderate: #e8c87a;
    --weak: #d96b6b;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
                 "Pretendard", "Segoe UI", "Malgun Gothic", sans-serif;
    font-size: 15px;
    line-height: 1.7;
  }
  h1, h2, h3, h4 { font-weight: 600; margin: 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
         font-size: 0.85em; background: rgba(255,255,255,0.05);
         padding: 1px 4px; border-radius: 2px; }

  .container { max-width: 880px; margin: 0 auto; padding: 32px 24px 64px; }
  section { margin: 56px 0; }

  /* Hero */
  .hero {
    text-align: center;
    padding: 48px 24px;
    border-bottom: 1px solid var(--border);
  }
  .hero h1 {
    font-size: 28px;
    color: var(--accent);
    margin-bottom: 12px;
    letter-spacing: 0.02em;
  }
  .hero .tagline {
    color: var(--fg-dim);
    font-size: 16px;
    max-width: 580px;
    margin: 0 auto;
  }

  /* Run summary */
  .run-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }
  .run-summary .stat {
    background: var(--bg-soft);
    padding: 14px 16px;
    border-radius: 4px;
    border: 1px solid var(--border);
  }
  .run-summary .stat .label {
    font-size: 11px; color: var(--fg-dim);
    letter-spacing: 0.1em; text-transform: uppercase;
  }
  .run-summary .stat .value {
    font-size: 18px; color: var(--fg); margin-top: 4px;
  }

  h2.section-h {
    font-size: 18px;
    color: var(--accent);
    margin-bottom: 18px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  h2.section-h .pretitle {
    color: var(--fg-dim);
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    display: block;
    margin-bottom: 4px;
    font-weight: normal;
  }

  /* Pressure summary */
  .phases {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }
  .phase {
    background: var(--bg-soft);
    padding: 14px 16px;
    border-radius: 4px;
    border: 1px solid var(--border);
  }
  .phase .phase-label {
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .phase .phase-summary { font-size: 13px; }

  /* Pipeline narrative */
  .pipeline-steps ol {
    counter-reset: step;
    list-style: none;
    padding: 0;
  }
  .pipeline-steps li {
    counter-increment: step;
    padding: 10px 0 10px 40px;
    position: relative;
    border-bottom: 1px solid var(--border);
  }
  .pipeline-steps li:last-child { border-bottom: none; }
  .pipeline-steps li::before {
    content: counter(step);
    position: absolute; left: 0; top: 10px;
    color: var(--accent);
    font-weight: 600;
    width: 28px; height: 28px;
    border: 1px solid var(--accent);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
  }

  /* Story seed cards */
  .seed-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 24px 28px;
    margin-bottom: 20px;
  }
  .seed-card.main {
    border-color: var(--accent);
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-soft) 100%);
  }
  .seed-card .seed-marker {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--fg-dim);
    margin-bottom: 6px;
  }
  .seed-card.main .seed-marker { color: var(--accent); }
  .seed-card h3 {
    font-size: 22px;
    color: var(--fg);
    margin-bottom: 6px;
  }
  .seed-card.main h3 { font-size: 24px; color: var(--accent); }
  .seed-card .subtitle {
    color: var(--fg-dim); font-size: 13px; margin-bottom: 16px;
  }
  .seed-card .premise {
    font-size: 16px; line-height: 1.8; margin-bottom: 16px;
  }
  .seed-card h4 {
    font-size: 12px;
    color: var(--fg-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 14px; margin-bottom: 6px;
  }
  .seed-card .question {
    padding: 10px 14px;
    border-left: 3px solid var(--accent);
    background: var(--accent-soft);
    border-radius: 0 4px 4px 0;
    margin: 14px 0;
    font-style: italic;
  }
  .seed-card .meta-row {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    font-size: 12px;
  }
  .meta-chip {
    padding: 3px 10px;
    border: 1px solid var(--border);
    border-radius: 3px;
    color: var(--fg-dim);
  }
  .meta-chip strong { color: var(--fg); font-weight: 500; }
  .meta-chip.confidence { border-color: var(--accent); color: var(--accent); }

  details {
    background: var(--bg-soft);
    padding: 12px 16px;
    border-radius: 4px;
    margin-top: 12px;
    border: 1px solid var(--border);
  }
  details summary {
    cursor: pointer;
    color: var(--fg-dim);
    font-size: 12px;
    list-style: none;
  }
  details summary::before { content: "▸ "; }
  details[open] summary::before { content: "▾ "; }
  details .body { margin-top: 10px; font-size: 13px; }

  /* Evidence section */
  .evidence-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }
  .evidence-stat {
    background: var(--bg-soft);
    padding: 12px 16px;
    border-radius: 4px;
    border: 1px solid var(--border);
    text-align: center;
  }
  .evidence-stat .num {
    font-size: 22px; color: var(--accent); font-weight: 600;
  }
  .evidence-stat .label {
    font-size: 11px; color: var(--fg-dim); margin-top: 4px;
  }

  /* Pipeline Progress */
  .pipeline-progress {
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
    background: var(--bg-soft);
    padding: 18px 16px;
    border-radius: 6px;
    border: 1px solid var(--border);
  }
  .pp-step {
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    padding: 8px 12px;
    background: var(--bg-card);
    border: 1px solid var(--accent);
    border-radius: 4px;
    min-width: 110px;
    text-align: center;
  }
  .pp-num {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: var(--accent); color: var(--bg);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
  }
  .pp-label { color: var(--fg); font-size: 12px; line-height: 1.3; }
  .pp-dur { color: var(--fg-dim); font-size: 10px; }
  .pp-arrow { color: var(--accent); font-size: 16px; }

  /* Hero flow strip */
  .flow-strip {
    margin-top: 22px; padding: 14px 16px;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 6px;
    display: flex; flex-wrap: wrap; gap: 10px;
    align-items: center; justify-content: center;
    font-size: 13px; color: var(--fg);
  }
  .flow-step { padding: 4px 12px; background: var(--bg-card);
               border-radius: 4px; border: 1px solid var(--border); }
  .flow-arrow { color: var(--accent); font-weight: 700; }

  /* Episode Outline (MAIN) */
  .episode {
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-soft) 100%);
    border: 2px solid var(--accent);
    border-radius: 8px;
    padding: 32px 36px;
  }
  .ep-title {
    font-size: 30px; color: var(--accent);
    margin-bottom: 14px; line-height: 1.3;
  }
  .ep-logline {
    font-size: 17px; color: var(--fg);
    line-height: 1.7;
    margin-bottom: 18px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  .ep-meta {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-bottom: 18px;
  }
  .ep-h {
    font-size: 12px; color: var(--accent);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-top: 18px; margin-bottom: 8px;
  }
  .sup-arcs {
    display: grid; gap: 10px; margin-bottom: 8px;
  }
  .sup-arc {
    padding: 10px 14px;
    background: rgba(255,255,255,0.03);
    border-radius: 4px;
    border-left: 2px solid var(--fg-dim);
  }
  .role-label { color: var(--accent); font-size: 13px; }
  .ep-block { margin: 14px 0; padding: 0; }
  .ep-block p { margin: 4px 0 0; line-height: 1.7; }
  .three-part { margin: 4px 0 0; padding-left: 18px; }
  .three-part li { margin: 6px 0; line-height: 1.7; }
  .sup-list { margin: 4px 0 0; padding-left: 18px; list-style: disc; }
  .sup-list li { margin: 4px 0; }
  .ep-evidence-fold { margin-top: 24px; padding-top: 16px; border-top: 1px dashed var(--border); }
  .ep-evidence-fold summary { font-size: 12px; color: var(--fg-dim); }
  .ep-acts {
    display: grid; gap: 14px;
    margin-top: 16px; margin-bottom: 18px;
  }
  .ep-act { padding: 12px 16px; background: rgba(255,255,255,0.02);
            border-radius: 4px; border-left: 2px solid var(--accent); }
  .ep-act p { margin: 0; line-height: 1.7; }
  .ep-hook {
    padding: 14px 18px;
    background: var(--accent-soft);
    border-left: 3px solid var(--accent);
    border-radius: 0 4px 4px 0;
    margin: 18px 0 14px;
    font-style: italic;
    font-size: 16px;
  }

  /* Footer / appendix */
  footer {
    margin-top: 80px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--fg-dim);
    font-size: 12px;
  }
  footer code { font-size: 11px; }
</style>
</head>
<body>
<div class="container">

<!-- 1. Hero -->
<header class="hero">
  <h1>WITNESS · 세계 시뮬레이션에서 뽑아낸 이야기 개요</h1>
  <p class="tagline">
    먼저 세계를 움직입니다.<br>
    그다음 인물들이 압력 속에서 어떻게 흔들리는지 관찰하고,<br>
    그 흐름을 사람이 읽을 수 있는 <strong>이야기 개요</strong>로 정리합니다.
  </p>
  <div class="flow-strip">
    <span class="flow-step">시뮬레이션 실행</span>
    <span class="flow-arrow">→</span>
    <span class="flow-step">인물의 압력 흐름</span>
    <span class="flow-arrow">→</span>
    <span class="flow-step">이야기 개요</span>
    <span class="flow-arrow">→</span>
    <span class="flow-step">근거 / 감사</span>
  </div>
</header>

<!-- 2. Main Story Result (이야기 결과물 — 메인) -->
<section id="episodeSection">
  <h2 class="section-h"><span class="pretitle">메인 결과물</span>이번 시뮬레이션이 만든 이야기</h2>
  <div id="episodeOutline"></div>
</section>

<!-- 3. How It Was Generated (실행/파이프라인 압축 표시) -->
<section>
  <h2 class="section-h"><span class="pretitle">어떻게 만들어졌나</span>실행 흐름 (간단히)</h2>
  <div class="run-summary" id="runSummary"></div>
  <div class="pipeline-progress" id="pipelineProgress" style="margin-top:16px"></div>
  <details style="margin-top:16px">
    <summary>세계가 어떻게 움직였는지 (압력 3단계)</summary>
    <div class="phases" id="phases" style="margin-top:12px"></div>
    <p id="plainSummary" style="color: var(--fg); font-size: 14px; margin-top: 8px;"></p>
  </details>
</section>

<!-- 4. Story Seeds (보조 흐름) -->
<section>
  <h2 class="section-h"><span class="pretitle">보조 흐름</span>같은 시뮬레이션 안의 다른 인물들</h2>
  <p style="color: var(--fg-dim); font-size: 13px; margin-bottom: 16px;">
    위 메인 에피소드는 <strong>한 명의 중심 인물</strong>을 다룹니다. 같은
    시뮬레이션 안의 보조 인물들은 *서로 다른 보조 흐름*을 보여줍니다.
  </p>
  <div id="seedCards"></div>
</section>

<!-- 5. Evidence / Audit (접힘) -->
<section>
  <h2 class="section-h"><span class="pretitle">검증 / 근거</span>이 개요는 무엇에 기반했나</h2>
  <p style="color: var(--fg); font-size: 14px;">
    이 개요는 임의로 작성된 것이 아니라 시뮬레이션에서 자동으로 관측된
    <strong>변화 신호</strong>에서 조립되었습니다. 감사는 없는 사건 / 대사 /
    시나리오 슬러그 / 금지 어구를 자동 검사합니다.
  </p>
  <div class="evidence-grid" id="evidenceGrid" style="margin-top:12px"></div>

  <details style="margin-top:16px">
    <summary>관측된 변화 신호 (수치 근거)</summary>
    <div id="evidenceNarrative" style="margin-top:12px"></div>
  </details>

  <details style="margin-top:8px">
    <summary>씨앗별 상세 근거 보기</summary>
    <div class="body" id="evidenceDetail"></div>
  </details>
</section>

<!-- 5.5. Skeleton Output (anchor-clean universal seeds) — Phase 6 partial -->
<section>
  <h2 class="section-h"><span class="pretitle">뼈대 엔진 출력</span>universal seeds (anchor-clean)</h2>
  <p style="color: var(--fg); font-size: 14px;">
    위 메인 에피소드 / 보조 흐름은 <strong>특정 anchor (베드로)</strong>에 입혀진 표현입니다.
    아래는 같은 시뮬레이션의 <strong>anchor-agnostic universal seeds</strong> — 인물 이름 / 정경 사건 없이
    갈등 축 / 압력 / 욕망만으로 표현된 결정론적 뼈대 출력.
    <a href="../../witness_narrative_mode_plan.md">개편 plan</a>에 따른 살(ML) 엔진의 입력이 됩니다.
  </p>
  <details style="margin-top:12px">
    <summary>universal seeds 미리보기 (skeleton_output.json)</summary>
    <div id="skeletonSeeds" style="margin-top:12px"></div>
  </details>
</section>

<!-- 6. Technical Appendix (footer) -->
<footer>
  <p><strong>Technical Appendix</strong></p>
  <p>
    이 데모는 <code>scripts/narrative/run_portfolio_demo.py</code> 한 명령으로 생성됩니다.
    내부 파이프라인: <code>Simulation → Pressure → Threads → Episode Assembly → Seed Cards → Evidence</code>.
  </p>
  <p>
    <strong>뼈대 / 살 분리 (Narrative Mode Refactor 2026-05-09)</strong>:
    <a href="../../witness_narrative_mode_plan.md">개편 plan</a> ·
    <a href="skeleton_output.json">skeleton_output.json</a> (anchor-clean) ·
    FROZEN contract: <code>SkeletonOutput v1</code>.
  </p>
  <p>
    <strong>확장 데모</strong>:
    <a href="life_arc_demo.html">베드로 5막 timeline</a> ·
    <a href="life_arc_demo_by_week.html">주별 timeline</a> ·
    <a href="life_arc_seed_diversity.md">seed별 선택 차이</a>
    <span style="color:var(--fg-dim)">— phase-based simulation window. 실제 3년 전체 재현이 아니라 주요 phase를 압축해 테스트한 버전입니다.</span>
  </p>
  <p>
    상세 검증: <a href="../STORY_VIABILITY_REPORT.md">STORY_VIABILITY_REPORT.md</a> ·
    Plan §11 audit: <a href="PLAN_11_AUDIT.md">PLAN_11_AUDIT.md</a> ·
    Run log: <a href="run_log.md">run_log.md</a>.
  </p>
</footer>
</div>

<script type="application/json" id="data-payload">__DATA__</script>
<script>
"use strict";
const DATA = JSON.parse(document.getElementById("data-payload").textContent);

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Run summary
const rs = DATA.run_summary;
document.getElementById("runSummary").innerHTML = `
  <div class="stat"><div class="label">시나리오</div><div class="value">${escapeHtml(rs.scenario)}</div></div>
  <div class="stat"><div class="label">인물</div><div class="value">${rs.agents}명</div></div>
  <div class="stat"><div class="label">집단</div><div class="value">${rs.groups}개</div></div>
  <div class="stat"><div class="label">시간 단계</div><div class="value">${rs.ticks}</div></div>
  <div class="stat"><div class="label">에피소드</div><div class="value">${rs.episodes}</div></div>
  <div class="stat"><div class="label">씨앗 수</div><div class="value">${rs.seeds}</div></div>
  <div class="stat"><div class="label">감사 통과</div><div class="value">${rs.audit_pass} / ${rs.seeds}</div></div>
`;

// Pipeline Progress (visualizes the 6 steps actually completed)
const pipelineSteps = (DATA.run_log && DATA.run_log.pipeline_steps) || [];
const ppHtml = pipelineSteps.map(s => {
  const dur = s.duration_ms > 0 ? `<span class="pp-dur">${s.duration_ms}ms</span>` : "";
  return `
    <div class="pp-step">
      <div class="pp-num">${s.step_no}</div>
      <div class="pp-label">${escapeHtml(s.plain_label)}</div>
      ${dur}
    </div>
  `;
}).join('<div class="pp-arrow">→</div>');
document.getElementById("pipelineProgress").innerHTML = ppHtml ||
  '<p style="color: var(--fg-dim);">(파이프라인 로그 없음)</p>';

// Episode Outline (MAIN — story-tone, no numbers)
const ep = DATA.episode_outline;
const episodeSection = document.getElementById("episodeSection");
const episodeBox = document.getElementById("episodeOutline");
if (ep) {
  const threePartHtml = (ep.three_part_outline || []).map((line, i) => `
    <li><strong>${i+1}.</strong> ${escapeHtml(line)}</li>
  `).join("");

  const supHtml = (ep.supporting_arcs || []).map(s => `
    <li><strong>${escapeHtml(s.name)}</strong> — <span class="role-label">${escapeHtml(s.role_label)}</span></li>
  `).join("");

  const risksHtml = (ep.risk_notes || []).map(r =>
    `<li>${escapeHtml(r)}</li>`
  ).join("");

  episodeBox.innerHTML = `
    <article class="episode">
      <h3 class="ep-title">${escapeHtml(ep.title)}</h3>
      <p class="ep-logline">${escapeHtml(ep.one_line_story)}</p>

      <div class="ep-meta">
        <span class="meta-chip"><strong>중심 인물</strong>: ${escapeHtml(ep.main_character)}</span>
      </div>

      <div class="ep-block">
        <h4 class="ep-h">그가 원하는 것</h4>
        <p>${escapeHtml(ep.what_character_wants)}</p>
      </div>
      <div class="ep-block">
        <h4 class="ep-h">그를 밀어붙이는 압력</h4>
        <p>${escapeHtml(ep.what_pressures_them)}</p>
      </div>
      <div class="ep-block">
        <h4 class="ep-h">어떻게 변하는가</h4>
        <p>${escapeHtml(ep.how_it_changes)}</p>
      </div>

      <div class="ep-block">
        <h4 class="ep-h">이야기 흐름</h4>
        <ol class="three-part">${threePartHtml}</ol>
      </div>

      <div class="ep-hook">${escapeHtml(ep.unresolved_question)}</div>

      <div class="ep-block">
        <h4 class="ep-h">어디에 쓸 수 있는가</h4>
        <p>${escapeHtml(ep.why_usable)}</p>
      </div>

      <div class="ep-block">
        <h4 class="ep-h">보조 흐름</h4>
        <ul class="sup-list">${supHtml || '<li><em style="color:var(--fg-dim);">(보조 인물 없음)</em></li>'}</ul>
      </div>

      <details class="ep-evidence-fold">
        <summary>Evidence — 데이터 근거 (관측 수치)</summary>
        <div class="body">
          <p style="color: var(--fg-dim);"><strong>관측 logline:</strong> ${escapeHtml(ep.logline)}</p>
          <h5 style="margin-top:12px">${escapeHtml(ep.act_1.plain_label)}</h5>
          <p>${escapeHtml(ep.act_1.summary)}</p>
          <h5>${escapeHtml(ep.act_2.plain_label)}</h5>
          <p>${escapeHtml(ep.act_2.summary)}</p>
          <h5>${escapeHtml(ep.act_3.plain_label)}</h5>
          <p>${escapeHtml(ep.act_3.summary)}</p>
          <h5 style="margin-top:12px">왜 하나의 이야기처럼 읽히는가</h5>
          <p>${escapeHtml(ep.why_this_feels_like_a_story)}</p>
          <p style="color: var(--fg-dim); margin-top: 8px;">${escapeHtml(ep.evidence_summary)}</p>
          <ul style="color: var(--fg-dim); margin-top: 4px;">${risksHtml}</ul>
        </div>
      </details>
    </article>
  `;
} else {
  episodeBox.innerHTML = '<p style="color: var(--fg-dim);">(에피소드 개요가 만들어지지 않았습니다 — 이야기 씨앗을 먼저 확인하세요.)</p>';
}

// Move evidence narrative (관측된 변화 신호) — non-technical signals
const evNarrativeBox = document.getElementById("evidenceNarrative");
if (ep && evNarrativeBox) {
  evNarrativeBox.innerHTML = `
    <p style="color: var(--fg);">
      이 결과물은 사람이 임의로 쓴 이야기가 아닙니다.
      시뮬레이션에서 반복적으로 나타난 변화 신호를 바탕으로 조립되었습니다.
    </p>
    <ul style="color: var(--fg);">
      <li>중심 인물의 두려움이 오래 유지됨</li>
      <li>주변 압력이 함께 커짐</li>
      <li>후반으로 갈수록 행동이 줄어듦</li>
      <li>감사 결과: 없는 사건이나 대사 추가 없음</li>
    </ul>
    <p style="color: var(--fg-dim); font-size: 12px; margin-top: 8px;">
      구체 수치는 위 Episode 섹션의 <em>Evidence — 데이터 근거</em> 펼침 또는 Technical Appendix를 참조하세요.
    </p>
  `;
}

// Phases
const phasesHtml = (DATA.pressure_summary.pressure_phases || []).map(p => `
  <div class="phase">
    <div class="phase-label">${escapeHtml(p.plain_label)}</div>
    <div class="phase-summary">${escapeHtml(p.summary)}</div>
  </div>
`).join("");
document.getElementById("phases").innerHTML = phasesHtml;
document.getElementById("plainSummary").textContent =
  DATA.pressure_summary.plain_language_summary || "";

// Seed cards — *보조 흐름만* 표시 (S02~Sn). S01은 위 메인 에피소드에서 전담.
const cardsHtml = (DATA.seed_cards || []).slice(1).map((s, i) => {
  const usable = (s.usable_for || []).map(u =>
    `<span class="meta-chip">${escapeHtml(u)}</span>`).join("");
  const signals = (s.evidence_summary.strongest_signals || [])
    .map(sig => `<span class="meta-chip">${escapeHtml(sig)}</span>`).join("");
  return `
    <div class="seed-card">
      <div class="seed-marker">보조 흐름 · ${escapeHtml(s.seed_id)}</div>
      <h3>${escapeHtml(s.title)}</h3>
      <div class="subtitle">${escapeHtml(s.subtitle)}</div>

      <div class="premise">${escapeHtml(s.plain_premise)}</div>

      <h4>왜 흥미로운가</h4>
      <p>${escapeHtml(s.why_interesting)}</p>

      <h4>장면으로 만들면</h4>
      <p>${escapeHtml(s.scene_image)}</p>

      <div class="question">${escapeHtml(s.unresolved_question)}</div>

      <h4>활용 가능</h4>
      <div class="meta-row">${usable || '<span class="meta-chip">(미정)</span>'}</div>

      <div class="meta-row">
        <span class="meta-chip confidence">${escapeHtml(s.confidence_label)}</span>
        <span class="meta-chip">감사: <strong>${escapeHtml(s.evidence_summary.audit_status)}</strong></span>
        <span class="meta-chip">변화 신호: <strong>${s.evidence_summary.evidence_count}개</strong></span>
      </div>

      <details>
        <summary>주요 변화 신호 보기</summary>
        <div class="body">
          <div class="meta-row">${signals || '<span class="meta-chip">(없음)</span>'}</div>
          <p style="margin-top: 10px; color: var(--fg-dim);">
            <em>${escapeHtml(s.risk_note)}</em>
          </p>
        </div>
      </details>
    </div>
  `;
}).join("");
document.getElementById("seedCards").innerHTML = cardsHtml;

// Evidence summary grid
const ev = DATA.evidence;
document.getElementById("evidenceGrid").innerHTML = `
  <div class="evidence-stat"><div class="num">${ev.seeds_total}</div><div class="label">전체 씨앗</div></div>
  <div class="evidence-stat"><div class="num">${ev.strong_viable}</div><div class="label">바로 발전 가능</div></div>
  <div class="evidence-stat"><div class="num">${ev.viable_with_gaps}</div><div class="label">보완 필요</div></div>
  <div class="evidence-stat"><div class="num">${ev.audit_fail}</div><div class="label">감사 실패</div></div>
`;

// Evidence detail
const detailHtml = (DATA.evidence.per_seed || []).map(p => `
  <div style="margin-bottom: 12px;">
    <strong>${escapeHtml(p.seed_id)}</strong> ${escapeHtml(p.title)}<br>
    <span style="color: var(--fg-dim);">신뢰도: ${escapeHtml(p.confidence)} · 감사: ${escapeHtml(p.audit)} · 신호 ${p.evidence_count}개</span>
  </div>
`).join("");
document.getElementById("evidenceDetail").innerHTML = detailHtml;

// Skeleton output preview (Phase 6 partial — anchor-clean universal seeds)
const skeletonBox = document.getElementById("skeletonSeeds");
if (skeletonBox && DATA.skeleton_output && DATA.skeleton_output.seeds) {
  const seeds = DATA.skeleton_output.seeds;
  const ledger = DATA.skeleton_output.evidence_ledger || {};
  const seedRows = seeds.map(s => `
    <tr>
      <td><code>${escapeHtml(s.seed_id)}</code></td>
      <td><code>${escapeHtml(s.conflict_axis_id)}</code></td>
      <td>${(s.dominant_pressures || []).map(p => `<code>${escapeHtml(p)}</code>`).join(" ") || "—"}</td>
      <td>${(s.dominant_desires || []).map(d => `<code>${escapeHtml(d)}</code>`).join(" ") || "—"}</td>
      <td>${escapeHtml(s.confidence_label)}</td>
      <td>${escapeHtml(s.audit_status)}</td>
    </tr>
  `).join("");
  skeletonBox.innerHTML = `
    <p style="color: var(--fg-dim); font-size: 12px;">
      <strong>schema_version</strong>: <code>${escapeHtml(DATA.skeleton_output.schema_version)}</code> ·
      <strong>seeds</strong>: ${seeds.length} ·
      <strong>total_signals</strong>: ${ledger.total_signals || 0} ·
      <strong>audit pass / fail</strong>: ${ledger.audit_pass_count || 0} / ${ledger.audit_fail_count || 0}
    </p>
    <table style="width:100%; border-collapse: collapse; font-size: 13px;">
      <thead style="background: var(--bg-soft);">
        <tr>
          <th style="padding:6px; text-align:left;">id</th>
          <th style="padding:6px; text-align:left;">conflict_axis</th>
          <th style="padding:6px; text-align:left;">pressures</th>
          <th style="padding:6px; text-align:left;">desires</th>
          <th style="padding:6px; text-align:left;">confidence</th>
          <th style="padding:6px; text-align:left;">audit</th>
        </tr>
      </thead>
      <tbody>${seedRows}</tbody>
    </table>
    <p style="color: var(--fg-dim); font-size: 12px; margin-top: 8px;">
      이 표는 <em>anchor-clean</em> universal seeds. 한국어 이름 / 정경 사건 0.
      flesh engine (ML)이 이 contract만 input으로 받습니다.
    </p>
  `;
}
</script>
</body>
</html>
"""


def _render_html(payload: dict) -> str:
    return HTML_TEMPLATE.replace(
        "__DATA__", json.dumps(payload, ensure_ascii=False)
    )


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def main(anchor: str, seed: int, ticks: int, output_dir: str,
         observer_path: str | None = None,
         use_cache: bool = False) -> int:
    started = time.time()
    started_iso = time.strftime("%Y-%m-%dT%H:%M:%S")
    timer = StepTimer()

    # Stage 1 — Run engine simulation (fresh by default).
    # `use_cache=True` (or explicit --observer path) loads an existing dump
    # instead of running the engine — useful for fast re-render after a
    # template/HTML change. Default is *fresh run every time*.
    print(f"[1/6] Running world simulation (anchor={anchor}, seed={seed}, ticks={ticks})...")
    with timer.step("simulation"):
        if observer_path:
            obs_p = Path(observer_path)
            if not obs_p.exists():
                print(f"ERROR: observer path {obs_p} not found.", file=sys.stderr)
                return 1
            observer = json.loads(obs_p.read_text(encoding="utf-8"))
        elif use_cache:
            cached = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
            if cached.exists():
                observer = json.loads(cached.read_text(encoding="utf-8"))
            else:
                # cache miss → run engine anyway
                observer = export_dot_observer_data(
                    anchor_id=anchor, seed=seed, n_ticks=ticks,
                )
        else:
            # Default: fresh engine simulation every run
            observer = export_dot_observer_data(
                anchor_id=anchor, seed=seed, n_ticks=ticks,
            )
            # Persist the fresh dump so debug folder + downstream tools have it
            cached_path = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
            cached_path.parent.mkdir(parents=True, exist_ok=True)
            cached_path.write_text(
                json.dumps(observer, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    actual_anchor = observer.get("meta", {}).get("anchor_id", anchor)

    print(f"[2/6] Observing pressure changes...")
    with timer.step("pressure"):
        moments = extract_moments(observer)
        identity = IdentityResolver.from_observer(observer)
        pressure = build_pressure_summary(observer, identity_resolver=identity)

    print(f"[3/6] Mining story threads...")
    with timer.step("threads"):
        links = link_moments(moments)
        threads = build_story_threads(moments, links)
        candidates = build_story_candidates(threads, moments, identity)

    # Cross-seed lookup (optional)
    xs_path = ROOT / "data/narrative/cross_seed_story_patterns.json"
    cross_seed_freq: dict[str, int] = {}
    if xs_path.exists():
        xs = json.loads(xs_path.read_text(encoding="utf-8"))
        for pat in xs.get("character_patterns", []):
            cross_seed_freq[pat["pattern_value"]] = pat["seed_count"]

    # Score + audit + seed cards
    blocklist = load_anchor_blocklist(actual_anchor)
    seeds: list = []
    audits: list = []
    score_grades: list[str] = []

    # Build NarrativeEvidence once per candidate (data-driven body content).
    # Different seeds → different observer dumps → different evidence
    # → different Korean body text in seed cards / episode outline.
    candidate_evidence: dict[str, Any] = {}
    for c in candidates:
        if c.main_characters:
            try:
                candidate_evidence[c.story_candidate_id] = (
                    extract_narrative_evidence(
                        observer, c.main_characters[0],
                        identity_resolver=identity,
                    )
                )
            except Exception:
                candidate_evidence[c.story_candidate_id] = None

    print(f"[4/6] Assembling episode outline...")
    with timer.step("seed_cards"):
        for c in candidates:
            brief = build_scene_brief(c)
            treatment = build_treatment(c, brief)
            freq: int | None = None
            if c.main_characters:
                freq = cross_seed_freq.get(c.main_characters[0])
            sc = score_candidate(c, brief, treatment, cross_seed_frequency=freq)
            ar = audit_pair(brief, treatment, extra_blocklist=blocklist)
            ev = candidate_evidence.get(c.story_candidate_id)
            card = build_seed_card(
                c, brief, sc,
                audit_overall_status=ar.overall,
                evidence=ev,
            )
            seeds.append(card)
            audits.append(ar)
            score_grades.append(sc.grade)

    # Stage 4 — episode outline (NEW, data-driven via main candidate evidence)
    audit_pass_count = sum(1 for a in audits if a.overall == "pass")
    audit_fail_count = sum(1 for a in audits if a.overall == "audit_fail")
    episode_outline = None
    if candidates and seeds:
        with timer.step("episode"):
            main_evidence = candidate_evidence.get(candidates[0].story_candidate_id)
            # supporting evidence map (excluding main) for per-supporting one-lines
            sup_evidence_map = {
                cid: ev for cid, ev in candidate_evidence.items()
                if cid != candidates[0].story_candidate_id and ev is not None
            }
            episode_outline = build_episode_outline(
                candidates=candidates,
                seed_cards=seeds,
                pressure=pressure,
                audit_pass_count=audit_pass_count,
                audit_fail_count=audit_fail_count,
                evidence=main_evidence,
                supporting_evidence=sup_evidence_map,
                display_name_overrides=PETER_ANCHOR_NAME_OVERRIDES_KO,
            )

    print(f"[5/6] Building story seed cards...")
    # (seed cards already built in [4/6] timing block)
    print(f"[6/6] Rendering portfolio demo...")

    # Stage 7-8 outputs
    out = ROOT / output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    # JSON outputs
    cards_json = {
        "schema_version": "story_seed_cards_v1",
        "run_label": actual_anchor,
        "seed": seed,
        "cards": [s.to_dict() for s in seeds],
    }
    (out / "story_seed_cards.json").write_text(
        json.dumps(cards_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "pressure_summary.json").write_text(
        json.dumps(pressure.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    n_pass = sum(1 for a in audits if a.overall == "pass")
    n_strong = sum(1 for g in score_grades if g == "strong_viable")
    n_viable = sum(1 for g in score_grades if g == "viable_with_gaps")
    n_fail = sum(1 for a in audits if a.overall == "audit_fail")

    summary_payload = {
        "schema_version": "demo_run_summary_v1",
        "anchor_id": actual_anchor,
        "seed": seed,
        "ticks": observer.get("meta", {}).get("n_ticks", ticks),
        "agents": observer.get("meta", {}).get("agent_count", 0),
        "groups": observer.get("meta", {}).get("group_count", 0),
        "moments": len(moments),
        "links": len(links),
        "threads": len(threads),
        "candidates": len(candidates),
        "seeds": len(seeds),
        "audit_pass": n_pass,
        "audit_fail": n_fail,
        "strong_viable": n_strong,
        "viable_with_gaps": n_viable,
        "runtime_seconds": round(time.time() - started, 2),
    }
    (out / "demo_run_summary.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Markdown outputs
    (out / "story_seed_cards.md").write_text(
        _render_seed_cards_md(seeds, actual_anchor, episode_outline=episode_outline),
        encoding="utf-8",
    )
    (out / "evidence_report.md").write_text(
        _render_evidence_report_md(seeds, audits, actual_anchor), encoding="utf-8"
    )

    # Episode outline outputs
    if episode_outline is not None:
        (out / "episode_outline.md").write_text(
            render_episode_outline_md(episode_outline, actual_anchor),
            encoding="utf-8",
        )
        (out / "episode_outline.json").write_text(
            json.dumps({
                "schema_version": "episode_outline_v1",
                "run_label": actual_anchor,
                "outline": episode_outline.to_dict(),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Skeleton output (Phase 0 — anchor-clean universal seeds, FROZEN contract).
    # 기존 episode_outline / story_seed_cards 산출 *옆에* 함께 작성한다. flesh
    # engine (ML) layer가 이 파일만 input으로 받는다.
    skeleton_out = assemble_skeleton_output(
        candidates=candidates, seed_cards=seeds,
        anchor_id=actual_anchor, audits=audits,
    )
    (out / "skeleton_output.json").write_text(
        json.dumps(skeleton_out.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Run log outputs
    runtime = time.time() - started
    pipeline_steps = make_pipeline_steps(durations_ms=timer.durations_ms())
    run_log = RunLog(
        anchor_id=actual_anchor,
        seed=seed,
        ticks=summary_payload["ticks"],
        agents=summary_payload["agents"],
        groups=summary_payload["groups"],
        story_threads_found=len(threads),
        story_seeds_generated=len(seeds),
        episode_outlines_generated=1 if episode_outline else 0,
        audit_failures=n_fail,
        pipeline_steps=pipeline_steps,
        started_at_iso=started_iso,
        runtime_seconds=runtime,
    )
    (out / "run_log.md").write_text(render_run_log_md(run_log), encoding="utf-8")
    (out / "run_log.json").write_text(
        json.dumps(run_log.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # HTML output (Stage 8) — restructured: Episode-centric
    per_seed_evidence = [
        {
            "seed_id": s.seed_id,
            "title": s.title,
            "confidence": s.confidence_label,
            "audit": s.evidence_summary.audit_status,
            "evidence_count": s.evidence_summary.evidence_count,
        }
        for s in seeds
    ]
    html_payload = {
        "run_summary": {
            "scenario": actual_anchor,
            "agents": summary_payload["agents"],
            "groups": summary_payload["groups"],
            "ticks": summary_payload["ticks"],
            "seeds": summary_payload["seeds"],
            "episodes": 1 if episode_outline else 0,
            "audit_pass": summary_payload["audit_pass"],
            "audit_fail": summary_payload["audit_fail"],
        },
        "run_log": run_log.to_dict(),
        "pressure_summary": pressure.to_dict(),
        "episode_outline": episode_outline.to_dict() if episode_outline else None,
        "seed_cards": [s.to_dict() for s in seeds],
        "evidence": {
            "seeds_total": summary_payload["seeds"],
            "strong_viable": summary_payload["strong_viable"],
            "viable_with_gaps": summary_payload["viable_with_gaps"],
            "audit_fail": summary_payload["audit_fail"],
            "per_seed": per_seed_evidence,
        },
        "skeleton_output": skeleton_out.to_dict(),
    }
    (out / "index.html").write_text(_render_html(html_payload), encoding="utf-8")

    print()
    print("Done.")
    print(f"Open: {out / 'index.html'}")
    print()
    print(f"Episode outline: {1 if episode_outline else 0} · "
          f"Story seeds: {summary_payload['seeds']} "
          f"(strong={n_strong}, viable={n_viable}, audit_fail={n_fail}) · "
          f"Runtime: {round(runtime, 2)}s")
    return 0


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--anchor", default="peter_scarcity_baseline")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument("--output", default="docs/portfolio/demo")
    ap.add_argument("--observer", default=None,
                    help="명시적 observer JSON 경로 — 시뮬레이션을 *돌리지 않고* "
                         "이 dump를 그대로 사용. 디버깅용.")
    ap.add_argument("--use-cache", action="store_true",
                    help="data/visual/dot_observer_data_seed{N}.json 가 있으면 "
                         "그걸 재사용 (시뮬레이션 skip). 기본값은 매번 fresh 실행.")
    ns = ap.parse_args()
    sys.exit(main(ns.anchor, ns.seed, ns.ticks, ns.output,
                  ns.observer, ns.use_cache))


if __name__ == "__main__":
    cli()
