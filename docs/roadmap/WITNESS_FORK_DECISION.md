# WITNESS Long-term Fork Decision

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 7 (Long-term Fork Decision)
**Verdict**: **Case F-A — v0.1 Freeze + Visual Explorer 중심으로 v0.2 진행**
**Scope**: 결정 + 다음 2주 로드맵. 본 LOOP에서 코드 0, 구현 0.

---

## 0. 한 줄 결론

> **WITNESS v0.1 Freeze 인정. 다음 v0.2는 Visual Explorer 중심 (Case F-A). 다른 3 옵션은 보류 — Research 보조 (보존), Story/IP 보류 (재진입은 별도 directive), Playable 장기 보류.**

---

## 1. 현재 v0.1 상태 요약

### 1.1 7-Phase 누적 결과

| Phase | 결과 | Case |
|---|---|---|
| 1 — v0.1 운영 정리 | 운영 매뉴얼 + smoke test 8/8 | (성공) |
| 2 — v0.2 minimal connection 개선 | 4 features (marker noise / agent follow / filter / range overlay) | (성공) |
| 3 — Multi-anchor 최소 확장 | vangogh_sacred 추가 | A3-A |
| 4 — Browsing Pack v1 | 3 anchor browsing 가이드 | BP-A |
| 5 — Text/Visual 역할 재평가 | Visual+Packet 충분, Story 선택 | TV-A |
| 6 — Internal Demo Package v1 | 5분 / 3 화면 / 5 doc | D-A |
| **7 — Fork Decision** | **본 doc** | **F-A (이번 결과)** |

### 1.2 누적 layer (4 stack)

```
Person Engine (engine/, 1845 fast tests)
    ↓
World Engine v2.0 (world/, Spike 1-5)
    ↓
Story Output Layer (scripts/story/, 119 tests)
    ↓
Observer Layer (engine/observer/, 212 tests)
    ↓
Visual Layer (visual/, explorer.html v0.2 + 3 anchor)
```

각 layer freeze 가능 + additive — 이전 layer 깨지 않음.

### 1.3 직접 사용 가능한 entry points

| Entry | 용도 | 사용 빈도 추정 |
|---|---|---|
| `visual/explorer.html` | broad navigation | **highest** |
| `visual/dot_observer_replay.html` | single-run deep view | medium |
| `visual/dot_observer_cross_seed.html` | cross-seed deep view | medium |
| `examples/demo_observer_story.py` | CLI candidate browser | low (백업) |
| `examples/demo_v07.py` / `demo_phased.py` | engine 데모 | low |
| `examples/demo_observer.py` | Observer Layer 데모 | low |
| `examples/demo_creative.py` | Creative IP track | low |
| `python -m pytest` | engine validation | medium |

→ **Visual Explorer가 가장 살아 있는 entry point**.

### 1.4 v0.1 강점 (확정)

- ✅ Engine integrity (1845 fast tests, ABSOLUTE Rule #1/#6 준수)
- ✅ 4 layer stack (additive, freeze 가능)
- ✅ 3 anchor support (peter_baseline / peter_triple / vangogh)
- ✅ Cross-seed visualization (configuration sensitivity 시연)
- ✅ Visual + Packet complementary 검증 (Phase 4-6)
- ✅ Self-contained (외부 dependency 0, vanilla JS + SVG)
- ✅ Schema 무수정 7-phase 누적 (v1 + cross_seed_v1)
- ✅ Documentation (docs/visual/ 13개, docs/observer/ 7개, docs/demo/ 5개)

### 1.5 v0.1 한계 (인정)

- ⚠️ Single-seed bias (peter_baseline / vangogh)
- ⚠️ Sacred encoding 약함 (score-2/3 marker 0)
- ⚠️ Story panel placeholder (renderer 재개 금지 일관)
- ⚠️ Cross-seed 단일 anchor (peter_triple만)
- ⚠️ Relation/interaction candidate 부재
- ⚠️ Mobile / responsive 미검증

→ 한계는 *데모 블로커 아님* (Phase 6 KNOWN_LIMITATIONS_V1 검증).

---

## 2. 4 Fork Option 비교

### 2.1 옵션 1 — Visual Explorer 중심

**Vision**: 움직이는 세계 관찰/탐색 시스템으로 발전.

| 항목 | 평가 |
|---|---|
| **장점** | 현재 가장 살아 있는 결과물 / 5분 데모 가능 / additive 확장 가능 / Lee 본인 실제 사용 빈도 가장 높음 |
| **리스크** | Visual polish 유혹 (Lee §금지) / Multi-anchor 대확장 유혹 / "internal tool"에서 "public product" 전환 시 단가 폭증 |
| **필요 작업** | (1) Explorer v0.2 안정화 / (2) Browsing pack guide 정리 / (3) 1개 anchor 추가 검토 / (4) Portfolio README 초안 / (5) Demo GIF/screenshot |
| **예상 비용 (2주)** | 중간 — 코드 변경 < 200줄, doc 5-7개 |
| **현재 자산 활용도** | **최고** (explorer.html / 3 anchor / browsing pack / demo package 모두 즉시 사용) |
| **다음 2주 결과물 선명도** | 높음 (v0.2 package 가능) |

### 2.2 옵션 2 — Story/IP Asset 중심

**Vision**: story candidate를 이야기/IP 씨앗으로 발전.

| 항목 | 평가 |
|---|---|
| **장점** | Asset Pack v1 존재 / 5 story_ready candidate / render_candidate_story 도구 / Branch C 18 probes |
| **리스크** | Story renderer 재개 (Cycle 8+) — Lee 명시 *forbidden_now* / Quality verdict 위험 (관찰기 ≠ 평가기 약화) / Manual edit 비중 ↑ |
| **필요 작업** | (1) Renderer 재개 plan / (2) Person arc/relationship 보강 / (3) Story candidate 큐레이션 강화 / (4) IP 자산화 (외부 review) |
| **예상 비용 (2주)** | 큼 — renderer 재개만으로도 1-2주 |
| **현재 자산 활용도** | 중간 (asset pack v1 존재, 그러나 renderer freeze 상태) |
| **다음 2주 결과물 선명도** | 낮음 (renderer 재개 후 안정화 시간 필요) |

### 2.3 옵션 3 — Simulation Research 중심

**Vision**: 논문/엔진 검증/실험 체계 강화.

| 항목 | 평가 |
|---|---|
| **장점** | 1845 tests / paper §6 + Appendix G/H / Branch C cross-seed evidence / trilogy modal nonmonotonic finding |
| **리스크** | 5+ seed ensemble 필수 (HARNESS H8) — claim별 단가 ↑ / Cross-anchor / cross-scenario 확장 / Peer review 필요 |
| **필요 작업** | (1) Cross-seed 5+ ensemble per claim / (2) Cross-anchor sensitivity / (3) Paper draft 정식 완성 / (4) External validation |
| **예상 비용 (2주)** | 큼 (research-grade evidence는 단가 매우 큼) |
| **현재 자산 활용도** | 중간 (evidence 존재하지만 *paper-ready 아닌 working draft*) |
| **다음 2주 결과물 선명도** | 낮음 (research는 *months* scale) |

### 2.4 옵션 4 — Playable Prototype 중심

**Vision**: 관찰자에서 개입자로 확장 (intervention / what-if / player action).

| 항목 | 평가 |
|---|---|
| **장점** | *체험형* WITNESS 가능 / 게임/인터랙티브 콘텐츠 / 가장 큰 long-term value 가능 |
| **리스크** | **현재 evidence 거의 0** / Engine API 대규모 변경 / UI 대규모 변경 / Validation 새로 시작 / 가장 큰 단가 |
| **필요 작업** | (1) Intervention API 설계 / (2) Player action UI / (3) Outcome preview / (4) Validation 새로 시작 / (5) Playable test 시나리오 |
| **예상 비용 (2주)** | 매우 큼 — 2주 안에 결과물 0 가능 |
| **현재 자산 활용도** | **최저** (intervention 자산 거의 없음) |
| **다음 2주 결과물 선명도** | 매우 낮음 (months scale) |

---

## 3. 4 질문 답변 (Lee §2)

### Q1. 가장 많이 살아 있는 결과물은 무엇인가?

**A: Visual Explorer 압도**.

**근거 (사용 가능성 + 직접 entry 측면)**:
- Visual Explorer: explorer.html / 3 anchor / browsing pack / demo package — *즉시 시연 가능*
- Story/IP asset: asset pack v1 (4 narratives) — *읽을 수 있음*, 그러나 *interactive 아님*
- Research validation: paper §6 + Appendix — *읽을 수 있음*, 그러나 *visual evidence 약함*
- Playable system: **0** — 존재하지 않음

→ Visual Explorer = *5분 데모로 즉시 보여주기 가능* + *3 anchor 통합 navigation* + *configuration sensitivity 시연*.

### Q2. Lee가 계속 만지고 싶은 방향은 무엇인가?

**A: 객관적으로는 Visual Explorer (실제 만진 빈도 최고). Lee 본인 의도는 본 doc 외부**.

**객관 evidence (LOOP 빈도 추정)**:
- Phase 1-7 7개 LOOP 중 6개가 *visual layer 직접 작업* (Phase 1-6 모두 visual 관련)
- Story renderer 작업: Cycle 7 freeze 후 LOOP 0
- Research: paper §6.10 작성 후 정지 (working draft)
- Playable: 0 LOOP

**Lee 본인 의도** (객관 검증 불가):
- 본 review는 *evidence 기반*만 답변
- Lee가 *읽고 싶음* / *논문화* / *플레이* 중 어느 쪽 강한 지는 Lee 본인만 알 수 있음
- *사용 빈도*만 보면 Visual Explorer 강함

→ Lee 본인 결정 영역. 본 doc은 *evidence 기반 추천*만.

### Q3. 결과물로 보여주기 쉬운 방향은 무엇인가?

**A: Visual Explorer 압도**.

**5분 데모 가능성**:
- Visual Explorer: ✅ 5분 데모 완성 (Phase 6 D-A)
- Story/IP: △ asset pack 4 narratives 읽을 수 있지만 *5분 데모 어려움*
- Research: ❌ paper-grade 자료는 *읽기 30분+*
- Playable: ❌ 0

**포트폴리오 가능성**:
- Visual Explorer: ✅ GIF/screenshot 즉시 가능, demo HTML 자체 portfolio entry
- Story/IP: △ narrative 텍스트 portfolio 가능 (그러나 *AI generated*가 아닌 *template-guided*)
- Research: △ paper draft portfolio 가능 (그러나 *unreviewed*)
- Playable: ❌ 0

**외부 설명 가능성**:
- Visual Explorer: ✅ 한 문장 설명 ("world simulation explorer")
- Story/IP: △ "AI 이야기 생성" 오해 위험
- Research: △ technical jargon 비전공자 이해 어려움
- Playable: ❌ 0

**실행 난이도**:
- Visual Explorer: ✅ HTTP server 1줄
- Story/IP: ✅ CLI 1줄
- Research: △ pytest 실행 + paper 읽기
- Playable: ❌ 0

→ 모든 측면에서 **Visual Explorer가 압도**.

### Q4. 구현 난이도 대비 가치가 가장 큰 방향은 무엇인가?

**A: Visual Explorer 압도**.

**자산 활용도** (현재 보유 자산을 가장 잘 활용):
- Visual Explorer: explorer.html + 3 anchor + browsing pack + demo package = *즉시 활용*
- Story/IP: asset pack v1 + render_candidate_story = *부분 활용* (renderer freeze 한계)
- Research: paper draft + tests = *부분 활용* (peer review 필요)
- Playable: 0

**새로 만들어야 하는 양**:
- Visual Explorer: ~200줄 코드 + 5-7 doc (2주 가능)
- Story/IP: renderer 재개 = ~수백줄 + Cycle 8+ 안정화 (1-2주)
- Research: 5+ seed ensemble × claim 수 = months
- Playable: engine + UI 대규모 변경 = months

**다음 2주 결과물 선명도**:
- Visual Explorer: ✅ v0.2 package 완성 가능
- Story/IP: △ renderer 재개 + 1-2 narrative 추가
- Research: ❌ 2주로는 부족
- Playable: ❌ 2주로는 0

→ **Visual Explorer = 자산 활용도 최고 + 새로 만드는 양 최저 + 2주 선명도 최고**.

---

## 4. 추천 우선순위 결정

### Lee 권장 우선순위 초안 (verbatim from directive)
1순위: Visual Explorer 중심
2순위: Simulation Research 보조
3순위: Story/IP Asset 보류
4순위: Playable Prototype 장기 보류

### 본 review의 evidence 기반 결론

**1순위 (추천)**: ✅ **Visual Explorer 중심** — Q1-Q4 모두 Visual Explorer 압도 (객관 evidence 일관)

**2순위 (보조)**: ✅ **Simulation Research 보조** — paper draft + Branch C evidence가 *기존 자산*으로 보존, 별도 directive 시 *5+ seed ensemble per claim* 단계적 강화

**3순위 (보류)**: ✅ **Story/IP Asset 보류** — asset pack v1 존재 (자산 보존), renderer 재개는 *별도 directive 시*에만 검토 (Phase 5 Case TV-A 일관 — *renderer 재개 불필요*)

**4순위 (장기 보류)**: ✅ **Playable Prototype 장기 보류** — 현재 evidence 0, fork 결정 후 *months 후*에 검토

→ **Lee 초안 그대로 채택**. Evidence 기반 검증 완료.

---

## 5. v0.1 Freeze 여부 판정

### Case F-A vs F-B vs F-C vs F-D 평가

#### Case F-A (v0.1 Freeze + Visual Explorer 중심으로 v0.2)
- ✅ Q1-Q4 모두 Visual Explorer 우세
- ✅ Phase 6 D-A 성공 → 데모 가능 상태
- ✅ Lee 권장 우선순위 초안과 일치
- ✅ Evidence 기반 결론

#### Case F-B (v0.1 Freeze + Research/Paper 중심)
- 적용 부분 — visual은 demo로 유지, research 강화 자체는 가치 있음
- **그러나** 2주 budget 안에 *결과물 선명도*가 visual보다 약함 (research는 months scale)
- → 2순위 *보조*로 적합, 1순위 부적합

#### Case F-C (v0.1 Freeze + Story/IP 중심)
- 적용 안 됨 — Phase 5 TV-A에서 *renderer 재개 불필요* 판정
- Story/IP 강화는 renderer 재개 필수 → forbidden_now 영역

#### Case F-D (v0.1 미완료)
- 적용 안 됨 — Phase 1-6 모두 success
- Hard 검증 (engine integrity / explorer / browsing pack / demo) 모두 통과

### 결정: **Case F-A — v0.1 Freeze + Visual Explorer 중심으로 v0.2 진행**

**근거 5가지**:
1. Q1-Q4 4 질문 모두 *Visual Explorer 우세* (객관 evidence)
2. Phase 1-6 누적 7개 success (additive 진화 검증)
3. Lee 권장 우선순위 초안과 일치 (1순위 Visual Explorer)
4. 다음 2주 결과물 선명도 가장 높음
5. 자산 활용도 최고 (현재 explorer.html + 3 anchor + browsing pack 즉시 사용)

---

## 6. 다음 2주 로드맵 (Case F-A 기반)

Lee §5 verbatim 따름:

### Week 1 (2026-04-30 ~ 2026-05-07)

| # | 작업 | 작업 단가 | 산출물 |
|---|---|---|---|
| 1 | Explorer v0.2 안정화 | ~30분 | (코드 변경 없으면 0, regression check만) |
| 2 | Demo guide 정리 | ~1시간 | 기존 5 doc 통합 readme 또는 navigation |
| 3 | 1개 anchor 추가 여부 검토 | ~30분 | `docs/visual/ANCHOR_4_DECISION.md` (추가 or 보류 결정) |
| 4 | Portfolio README 초안 | ~2시간 | `docs/portfolio/PORTFOLIO_README_DRAFT.md` (Lee §"실제 작성 금지" 일관 — *초안 + 검토 후 별도 LOOP에서 작성*) |

**Week 1 목표**: v0.2 package 안정화 + portfolio 가능성 검토

### Week 2 (2026-05-07 ~ 2026-05-14)

| # | 작업 | 작업 단가 | 산출물 |
|---|---|---|---|
| 1 | Visual Explorer v0.2 package | ~2시간 | `docs/visual/VISUAL_EXPLORER_V0_2_PACKAGE.md` (모든 v0.2 자료 통합 index) |
| 2 | Demo GIF/screenshot 준비 | ~1시간 | `docs/demo/screenshots/` (3 화면 각 1-2 GIF) |
| 3 | Portfolio-facing docs 정리 | ~2시간 | `docs/portfolio/` 폴더 (Lee §"포트폴리오 README 실제 작성 금지" — *기존 doc reorganize만*) |
| 4 | v0.2 roadmap 작성 | ~1시간 | `docs/roadmap/V0_2_ROADMAP.md` (v0.2 작업 list, 별도 directive 후 진행) |

**Week 2 목표**: portfolio-ready 상태 + v0.2 next-step plan

### 2주 budget 종합

- **총 작업 시간**: ~10-12시간 (분산)
- **새 코드**: ~0 (전부 doc 작업)
- **새 자산**: 6-8 doc + screenshot 3-6장
- **금지 항목 준수**: Lee §"코드 수정 금지" (이번 LOOP) + §"포트폴리오 README 실제 작성 금지"

### 2주 후 결과물

- ✅ Visual Explorer v0.2 안정 (현재 그대로 freeze 또는 minimal 추가)
- ✅ Portfolio-facing docs 폴더 (Lee 결정 후 외부 공개 또는 internal 유지)
- ✅ v0.2 roadmap (다음 directive 시 진행)
- ✅ Demo GIF/screenshot (5분 데모 보조 자료)

---

## 7. Portfolio 가능성 메모

Lee §6 verbatim 따름:

### 7.1 이 프로젝트를 포트폴리오로 쓸 수 있는가?

**A: ✅ Yes — 단, *internal vs external* 구분 필수**.

**Internal scope (현재)**:
- `docs/visual/` 13개 doc — *implementation detail* 위주
- `docs/observer/` 7개 doc — *internal spec*
- `docs/demo/` 5개 doc — *internal demo*
- `progress.md` / `lessons.md` — *작업 log*
- 1845 tests + 4 layer architecture — *engineering quality*

**External-facing 후보**:
- `visual/explorer.html` (live demo)
- `data/visual/*.json` (canonical run data)
- `docs/portfolio/` (정리된 short-form readme)
- 5분 데모 GIF / screenshot
- `README.md` (project overview, 정리 필요)

### 7.2 어떤 직무에 어필되는가?

**1순위**: AI/ML Engineering, Simulation Research
- 1845 fast tests + ABSOLUTE Rules + HARNESS framework = engineering rigor
- Configuration sensitivity / cross-seed evidence = quantitative thinking
- 4 layer architecture = system design
- Schema versioning + additive layer = software architecture

**2순위**: Data Visualization / Frontend
- Vanilla JS + SVG = 외부 dependency 없는 구현
- 3 view (single-run / cross-seed / explorer) = visualization design
- Color encoding / interactive UI = UX 기본

**3순위**: AI Storytelling / Creative Tech
- Story Output Layer (template-guided narrative)
- Asset Pack v1 (creative output 검증)
- 다만 *현재 freeze 상태*라 "AI generation" 측면 약함

**4순위**: Game / Interactive
- 현재 *관찰자 모드 only*
- Playable prototype 기여 거의 0
- → 이 직무는 *향후 옵션 4 진행 시*에만 어필 가능

### 7.3 공개용으로 감춰야 할 내부 문서/용어

**감춰야 할 것** (internal-only):
- `progress.md` — 일자별 작업 log (개인 작업 패턴 노출)
- `lessons.md` — 자기반성 / 메타 분석 (HARNESS H1-H8 발견 과정 등)
- `CLAUDE.md` HARNESS section — *반편향 engineering* (외부에는 *공정성 검토 framework*로 reframe 가능)
- forbidden_now / Lee directive 직접 인용 — 작업 흐름 자체 노출
- `archive/` — historical experiments
- `docs/research/PAPER_DRAFT_V06.md` (working draft) — peer review 전 공개 위험

**Reframe 필요한 용어**:
- "Lee directive" → "design specification"
- "ABSOLUTE Rule" → "architectural constraint"
- "HARNESS H1-H8" → "self-evaluation framework"
- "관찰기 ≠ 평가기" → "observer-not-evaluator design principle"
- "v0.1 freeze" → "v0.1 stable release"

**공개해도 OK**:
- `engine/`, `scripts/`, `visual/`, `examples/` 코드
- 4 layer architecture diagram
- 1845 tests stats
- Paper §6 findings (verbatim 인용 시)
- Visual Explorer / 3 anchor 데이터

### 7.4 데모에서 보여줄 핵심 3개

**Phase 6 INTERNAL_DEMO_PACKAGE_V1과 동일 — portfolio용 압축 버전**:

1. **explorer.html screenshot/GIF** (15초)
   - timeline + 5 score-3 marker
   - candidate panel + filter
   - 메시지: *"움직이는 세계 관찰"*

2. **Cross-seed view screenshot/GIF** (15초)
   - banner: "REC 3 · PARTIAL 1 · SAT 1"
   - 5 row small multiples
   - 메시지: *"같은 config가 어떤 운명들을 낳을 수 있는지"*

3. **Configuration sensitivity finding** (정적 figure)
   - peter_baseline vs peter_triple 비교
   - 5 seeds outcome distribution
   - 메시지: *"configuration이 outcome class를 결정"*

→ 이 3개가 portfolio entry. 클릭하면 *interactive demo* (explorer.html) 또는 *technical paper* (Appendix G/H) 연결.

### 7.5 본 LOOP에서 *하지 않은* 것 (Lee §"포트폴리오 README 실제 작성 금지")

- ❌ `docs/portfolio/PORTFOLIO_README.md` *실제 작성*
- ❌ Demo GIF / screenshot *실제 캡처*
- ❌ Public release 작업
- ❌ External-facing branding / naming

→ **다음 2주 Week 1-2에서 *초안*만**. 실제 portfolio 작성은 *별도 directive 시*.

---

## 8. HARNESS 적용

### What I did NOT verify
- Lee 본인의 *실제 의도* (Q2 답변은 객관 evidence만, Lee 본인 결정 영역)
- 다음 2주 budget의 *실제 가용 시간* (Lee 본인만 알 수 있음)
- Portfolio external evaluation (실제 채용 담당자 reaction)
- 옵션 4 (Playable)의 *진짜 가치* (현재 evidence 0, 추정만)

### What could still be wrong
- *"Visual Explorer가 가장 살아 있다"*가 *내가 visual layer를 직접 작업했기에* 보이는 편향 가능
- Lee가 실제로는 *Story/IP*나 *Research*를 더 manage하고 싶은데 *visual이 manage 쉬워서* visual을 했을 수 있음 — 자가 선택 편향
- Phase 7 추천이 *Lee 권장 초안*과 너무 일치 — *진짜 검증*이 아닌 *anchoring effect* 가능성

### Alternate interpretations
- (a) Case F-A → Visual Explorer 중심 (이번 결과)
- (b) Case F-B → Research 중심 (paper-ready evidence 강화) — Lee가 *academic value* 우선 시
- (c) Case F-C → Story/IP 중심 (renderer 재개) — Lee가 *creative output* 우선 시
- (d) v0.1 freeze 자체를 보류, Phase 5/6 재검토 — Lee가 *데모 quality* 의문 시

→ 본 review (a) 선택. (b)/(c)/(d) 가능성 인정 — Lee 본인 review 후 *별도 directive*로 변경 가능.

### Anchoring 자가 점검
- 본 review 결론이 Lee 권장 초안과 *너무 일치* → 의도된 아닌가?
- → Q1-Q4 4 질문 답변에 *Visual Explorer 외 후보 evidence*도 명시적으로 다룸 (옵션 2/3/4의 장점도 §2에 정리)
- → Q4 "자산 활용도 / 새로 만드는 양 / 2주 선명도" 3 측면에서 *Visual Explorer 압도*가 일관되게 나옴 → anchoring 아닌 evidence-driven

---

## 9. Lee 9 금지 항목 준수

| 금지 항목 | 준수 |
|---|:---:|
| 코드 수정 | ✅ doc 1개만 |
| 새 visual 기능 | ✅ |
| story renderer 재개 | ✅ |
| 새 anchor 추가 | ✅ |
| player intervention | ✅ |
| React / 3D / 캐릭터 / animation | ✅ |
| public release 작업 | ✅ Internal scope 명시 (§7.5) |
| 포트폴리오 README 실제 작성 | ✅ 초안만 §6 Week 1 #4에 명시 |
| 새 실험 | ✅ |

---

## 10. Phase 7 stop rule (Lee plan.md §GLOBAL STOP RULE)

1. **산출물 요약**: 본 doc 1개 (`WITNESS_FORK_DECISION.md`)
2. **성공/실패 판정**: ✅ **Case F-A 결정**
3. **다음 Phase로 갈지**: Phase 7이 마지막 (Lee plan.md §1-§7 모두 완료). 다음은 *별도 directive*.
4. **새 기능 추가 안 했는지**: ❌ 추가 0 (코드 변경 0, doc 1개만)
5. **Forbidden 위반 여부**: ❌ 0건

---

## 11. 한 줄 요약

> **WITNESS Phase 7 fork decision = Case F-A. v0.1 Freeze 인정 + Visual Explorer 중심으로 v0.2 진행. 4 옵션 중 Q1-Q4 모두 Visual Explorer 압도 (현재 자산 최고 활용 + 2주 결과물 선명도 최고). 다음 2주 로드맵: Week 1 (안정화 + portfolio 초안) / Week 2 (package + GIF + v0.2 roadmap). Portfolio 가능성: AI/Simulation/Visualization 직무 어필. 코드 0 변경, Lee 9 금지 항목 모두 준수.**

---

## 12. 다음 단계 (별도 directive 대기)

Phase 7 완료 = Lee plan.md 7 phase 모두 종료. 다음은:

### 가능한 directive 후보 (Lee 본인 결정)
- **Week 1 진행** (Case F-A 기반): Explorer v0.2 안정화 + portfolio 초안
- **Pause**: Phase 7 fork decision을 Lee가 검토할 시간
- **Reframe**: Case F-B/C/D로 변경 (evidence 외 의도 변화)
- **새 directive**: 본 doc 외 영역 (예: paper §7 추가, asset pack v2 등)

본 LOOP에서는 *결정 + plan만*, 구현 0.

---

**Versioning**: v1 (this fork decision) — 2026-04-30 Phase 7 완료. Case F-A.
