# WITNESS — 세계에서 생겨난 한 편의 이야기 개요 (포트폴리오 데모)

> 이 폴더는 **명령어 한 번**으로 생성되는 자기완결형 데모입니다.
> 메인 산출물은 [index.html](index.html) — 브라우저로 열기만 하면 됩니다.

## 한 화면에 보이는 흐름 (정보 위계 v3, 2026-05-08)

```
1. Hero          — "세계 시뮬레이션 → 한 편의 이야기 개요" (10초 이해)
2. Main Story    — 메인 에피소드 개요
                   (Title / One-line / 중심 인물 / What He Wants /
                    What Pressures Him / How It Changes /
                    Three-part Outline / Unresolved Question / Why This Is Usable)
3. How It Was    — 어떻게 만들어졌나 (실행 결과 + 파이프라인 진행, 압축 표시)
   Generated      └ 압력 3단계는 접힘
4. Story Seeds   — 보조 흐름 (S02~S04, 같은 시뮬레이션 안의 다른 인물들)
5. Evidence      — 무엇에 기반했나 (관측 신호 + 수치 근거는 접힘)
6. Technical
   Appendix      — 확장 데모 / 검증 / Plan §11 audit 링크
```

**원칙**:
- 메인 영역에는 **수치 / tick / source / co-occurrence / authority_vigilance** 등 내부 용어 0
- 데이터 인용 logline (예: "200단계 중 약 39단계 동안...")은 *Evidence 접힘*에만
- S01은 메인 에피소드의 중심으로 노출, S02~S04는 보조 흐름 카드로 분리

---

## 빠른 시작

### 데모 생성

```bash
python scripts/narrative/run_portfolio_demo.py
```

**매 실행마다 엔진 시뮬레이션을 새로 돌립니다** — observer dump가 stale일 일 없음. 기본값: `peter_scarcity_baseline` 시나리오, seed 0, 200 ticks. 약 0.3초 안에 시뮬레이션 + 데이터 변환 + HTML 생성 완료.

**Life Arc Narrative — 베드로 공생애 142일 timeline** (2026-05-08):

엔진 phased 시뮬레이션을 돌려 *베드로 공생애*를 시간대별로 보여주는 narrative 생성:

```bash
python scripts/narrative/run_life_arc_demo.py --seed 0 --full-passion
# → docs/portfolio/demo/life_arc_demo.md (5막, 142.8일, 15 정경 사건)
# → docs/portfolio/demo/life_arc_demo.json (raw 데이터)
```

각 사건마다 *시뮬레이션 베드로의 선택*이 표시됨 (engine 출력). 다른 seed로 돌리면 같은 사건에 대해 다른 선택이 나옴. 정경 사건 description은 `content/peter/phases/*/canonical_events.json`에서 verbatim 인용 (성서 reference 포함).

| 사건 | seed 0 선택 | seed 7 선택 |
|---|---|---|
| 부르심 (눅 5:3) | 그물 손질 (`wash_nets`) | 가까이서 말씀 경청 (`listen_attentively`) |
| 발씻음 (요 13) | 거부 (`resist_washing`) | 순종 (`accept_washing`) |
| 1차 부인 (마 26:69) | 고백 (`confess`) | (다른 trigger) |
| 빈 무덤 (눅 24) | 숨어 있음 (`stay_hiding`) | 무덤으로 달려감 (`run_to_tomb`) |

자동 비교 표 (3 seeds 한 번에):

```bash
python scripts/narrative/demo_life_arc_seed_diversity.py --seeds 0,7,11
# → docs/portfolio/demo/life_arc_seed_diversity.md
# 15 정경 사건 중 ~11개에서 seed별 다른 선택 (⚡ marker)
```

산출물 형식 (모두 자동 생성):

| 파일 | 윈도우 | 용도 |
|---|---|---|
| `life_arc_demo.md` / `.html` / `.json` | 5 phases (1-5막) | 기본 |
| `life_arc_demo_by_week.md` / `.html` / `.json` | 21 weeks | 시간 흐름 세밀 |
| `life_arc_seed_diversity.md` | (3 seeds 비교 표) | engine-driven 검증 |

```bash
# 모든 산출 (5 phase + 21 week + HTML 포함)
python scripts/narrative/run_life_arc_demo.py --full-passion
python scripts/narrative/run_life_arc_demo.py --full-passion --window by_week
```

HTML은 self-contained (외부 자산 0, ~30 KB) — 브라우저로 바로 열림.

---

**다른 seed → 다른 본문** (Data-driven Synthesizer, 2026-05-08):

이야기 본문 (logline / 3 acts / 씨앗 카드 premise / why)은 *engine observer dump의 실제 수치*에서 직접 합성됩니다. 시뮬레이션 결과가 달라지면 본문도 달라집니다.

| seed | 두려움 지속 | 행동 변화 | 분위기 긴장 단계 |
|---|---|---|---|
| 0 | 39단계 | 8회 → 6회 | 52% |
| 3 | 28단계 | 7회 → 0회 | 23% |
| 7 | 29단계 | 8회 → 0회 | 25% |

(`engine/observer/data_narrative.py` — `extract_narrative_evidence()` → `evidence_to_logline / _premise / _act_summary` 등)

이 표 자체는 *자동 생성*이며, [`seed_diversity_demo.md`](seed_diversity_demo.md)가 매 실행 산출물입니다:

```bash
python scripts/narrative/demo_seed_diversity.py --seeds 0,3,7
# → docs/portfolio/demo/seed_diversity_demo.md (수치 비교 + Logline + Act 3)
```

**캐시 모드** (시뮬레이션 skip — 디버깅용):

```bash
python scripts/narrative/run_portfolio_demo.py --use-cache
```

`data/visual/dot_observer_data_seed{N}.json`이 있으면 그걸 재사용. HTML / 본문 변경만 빠르게 반영하고 싶을 때.

### 다른 시나리오 / 시드

```bash
python scripts/narrative/run_portfolio_demo.py --anchor peter_scarcity_baseline --seed 3
python scripts/narrative/run_portfolio_demo.py --observer data/visual/dot_observer_data_seed4.json
```

### 결과 보기

```bash
# 메인 — 브라우저로 열기
open docs/portfolio/demo/index.html
# 또는
python -m http.server 8000
# http://localhost:8000/docs/portfolio/demo/index.html
```

---

## 산출 파일

| 파일 | 용도 | 누가 보나 |
|---|---|---|
| `index.html` | **메인 데모** (self-contained, 외부 의존 0) | 일반인 / 포트폴리오 리뷰어 |
| `episode_outline.md` | **에피소드 개요** (한국어, 한 편) | 일반인 / 작가 |
| `episode_outline.json` | 에피소드 데이터 | 개발자 |
| `story_seed_cards.md` | 이야기 씨앗 카드 (한국어, 보조 4개) | 일반인 |
| `story_seed_cards.json` | 카드 데이터 | 개발자 |
| `run_log.md` | 실행 로그 (6단계 파이프라인) | 검토자 |
| `run_log.json` | 실행 통계 raw | 자동화 도구 |
| `pressure_summary.json` | 압력 흐름 3단계 | 개발자 |
| `evidence_report.md` | 검증 / 근거 리포트 | 검토자 |
| `demo_run_summary.json` | 실행 요약 | 자동화 도구 |

---

## 일반인용 표현 원칙

이 데모는 *내부 용어를 노출하지 않습니다*. 일반인용 메인 화면에서는:

| 내부 용어 | 일반인용 표현 |
|---|---|
| `tick` | 시간 단계 |
| `authority_vigilance` | 권위자의 압박 |
| `public_suspicion` | 사람들의 의심 |
| `blame_concentration` | 비난이 한쪽으로 몰림 |
| `group_tension` | 집단의 긴장 |
| `co-occurrence` | 동시에 겹친 변화 |
| `loyalty_vs_survival` | 침묵으로 변해가는 충성 (제목으로) |
| `viable_with_gaps` | 보완이 필요한 씨앗 |
| `strong_viable` | 바로 발전 가능한 씨앗 |
| `audit_pass` | 감사 통과 |

자세한 변환표는 [WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md §3](../../WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md) 참조.

---

## 검증 — 이 씨앗들은 *임의로 만든 게 아닙니다*

각 카드는 시뮬레이션의 *변화 신호*에서 자동으로 추출되며, 다음을 자동 검증합니다:

| 검증 항목 | 기준 |
|---|---|
| 없는 사건 추가 | 0 (Stage F audit) |
| 대사 생성 | 금지 (forbidden token: 따옴표 + 동사-of-saying) |
| 시나리오 슬러그 | 금지 (`EXT.` / `FADE IN` 등) |
| 시나리오별 금지 어구 | `content/anchors/{anchor_id}/audit_blocklist.json` |
| 감정 과잉 narration | 금지 (`weeping`, `screamed` 등 keyword 검사) |

전체 검증 흐름:

```
Story Candidate (검증자용)
  → Scene Brief        (Stage B, 6 sections)
  → 1-page Treatment   (Stage C, 3 acts)
  → Viability Score    (Stage D, 100점 모델)
  → Evidence Audit     (Stage F, 자동 keyword + blocklist)
  → Story Seed Card    (일반인용 한국어, 메인 출력)
```

상세 검증 리포트는 별도 [STORY_VIABILITY_REPORT.md](../STORY_VIABILITY_REPORT.md) 참조.

---

## 일반인 리뷰 (Plan §12 v2)

리뷰어 3명에게 [index.html](index.html)만 보여주고 다음 5개 질문:

```
1. 첫 화면만 보고 무엇을 하는 프로젝트인지 이해했나요? (1-5)
2. S01 이야기가 장면으로 떠오르나요? (1-5)
3. 가장 흥미로운 이야기는 무엇인가요?
4. 이해가 막히는 단어가 있었나요?
5. 이걸 소설/영화/게임 아이디어로 쓸 수 있을 것 같나요? (1-5)
```

**Plan §12 통과 기준**:
- Q1 평균 ≥ 4.0
- Q2 평균 ≥ 3.5
- Q5 평균 ≥ 3.5
- 이해 막힘 단어 3개 이하

(기존 [HUMAN_PICK_TEST_PACK.md](../HUMAN_PICK_TEST_PACK.md)는 *기술 검증*용 — 별개)

---

## debug/ 폴더

검증자 / 개발자용 내부 산출물 링크. 메인 데모에서는 *숨겨집니다* (포트폴리오 리뷰어에게 보일 필요 없음).

```
debug/
  story_candidates.json    # Stage 5 (검증자용 카드)
  story_threads.json       # Stage 4 (그래프 단위)
  moments.json             # Stage 2 (atomic units)
  story_viability_scores.json
  story_viability_audit.json
```

---

## 현재 결과 요약 (2026-05-08, peter_scarcity_baseline seed=0)

```
Story seeds:    4
Strong viable:  1   (S01 침묵으로 변해가는 충성)
Viable w/gaps:  3   (S02-S04 결정을 미루는 사람)
Audit fail:     0
Runtime:        ~0.04s
HTML size:      ~16 KB (self-contained)
Body content:   data-driven (observer dump 수치 인용; seed별 본문 다름)
```

→ **Plan §11 Acceptance**: Functional ✅ / Readability ✅ / Evidence ✅ / Portfolio ✅ — 상세는 [PLAN_11_AUDIT.md](PLAN_11_AUDIT.md)

---

## 관련 문서

- Plan: [docs/WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md](../../WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md)
- 검증 리포트: [docs/portfolio/STORY_VIABILITY_REPORT.md](../STORY_VIABILITY_REPORT.md)
- Human Pick (기술 검증): [docs/portfolio/HUMAN_PICK_TEST_PACK.md](../HUMAN_PICK_TEST_PACK.md)
- 사용 가이드: [docs/STORY_VIABILITY_USER_GUIDE.md](../../STORY_VIABILITY_USER_GUIDE.md)
