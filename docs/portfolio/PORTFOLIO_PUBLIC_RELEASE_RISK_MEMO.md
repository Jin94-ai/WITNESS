# WITNESS — Portfolio Public Release Risk / Cleanup Memo

> 코드 / repo를 외부에 공개하기 *전* 반드시 점검할 risk 목록 + cleanup 체크리스트. 현 단계에서는 *결정만 보류*, 실제 작업은 별도 directive 시.

---

## 0. 본 memo의 목적

- 지금 *바로* GitHub 공개 하면 어떤 위험이 있는가?
- 공개 *전* 무엇을 감추거나 reframe해야 하는가?
- 공개 작업의 *결정 사항* 목록 (LICENSE, branch, asset 등)
- 다음 단계 3가지 옵션 — Lee 결정 대기

---

## 1. 지금 바로 공개하면 위험한 것

### 1.1 내부 로그 / 작업 흔적 (★★★ 즉시 차단 필요)

| 파일 / 디렉토리 | 위험 | 영향 |
|---|---|---|
| `progress.md` | 일자별 작업 로그 (개인 패턴 노출) | 외부 평가자에게 *과도한 internal flavor*, 자기 노출 부담 |
| `lessons.md` | meta-analysis (Lee 자기반성 / HARNESS 도출 과정) | Lee 표현 verbatim 노출, 한국어 내부 voice |
| `docs/archive/lee_directives_2026-04-30/` | 원본 Lee directive 파일들 (한국어) | 개인명 + Korean directive verbatim |
| `docs/archive/working_notes_*/` | 중간 작업 노트 | scope-reduction history, 미완성 thinking traces |
| `docs/sessions/` (있다면) | 세션 덤프 | 한국어 thinking trace, 개인 voice |

**즉시 조치**: 공개 시 `.gitignore` 추가 또는 별도 private branch 분리. 삭제 ≠ 권장 (Lee §"내부 로그 삭제하지 말 것").

### 1.2 한국어 / Lee 표현 verbatim (★★★ 차단 필수)

| 위험 표현 | 위치 | reframe 방법 |
|---|---|---|
| "Lee directive", "Lee §" | CLAUDE.md, archive, 일부 docs/ | "design specification" / "design spec §" |
| "Lee plan.md" verbatim | DESIGN.md, progress.md | "project plan" / "design plan" |
| "Lee 명시 / 권장 / 잠금" | 다수 docs | "specified / recommended / finalized" |
| "관찰기 ≠ 평가기" | docs/observer/, CLAUDE.md | "observer-not-evaluator design principle" |
| "ABSOLUTE Rule #1/#6" verbatim | CLAUDE.md, docs/ | "architectural constraint #1/#6" |
| "HARNESS H1-H8" verbatim | docs/HARNESS.md, CLAUDE.md | "8-rule self-evaluation framework" |
| "Case A / B / C / D" | 다수 검증 docs | "validation result (passed/partial/failed/incomplete)" |
| "forbidden_now" | progress.md, archive | "scope constraint / out-of-scope item" |
| "LOOP / 자율 LOOP / iter" | 다수 | "iteration / development cycle" |
| "Branch C" | docs/b_direction/ | "configuration sensitivity validation" |
| 한국어 verbatim quote | 여러 docs | English neutral 변환 (전체 reframe 필요) |

### 1.3 Working drafts / 비공개 자료 (★★ review 후 결정)

| 파일 | 위험 | 결정 필요 |
|---|---|---|
| `docs/research/PAPER_DRAFT_V06.md` | 동료 리뷰 전 working draft (319 lines) | 공개? 보류? peer review 통과 후? |
| `docs/research/PAPER_OUTLINE_V05.md` | working outline | 동일 |
| `docs/archive/REVIEW_RESPONSE_V1_2.md` | review 답변 working note | 비공개 권장 |
| Branch C 18 probes raw data | proprietary IP 가능성 | LLM provider terms 확인 필요 |
| `docs/b_direction/BRANCH_C_*` 다수 | external send 자료 | 외부 LLM 사용 흔적, 검토 필요 |

### 1.4 코드 / 파일명에 남은 흔적 (★ 점검 필요)

- `engine/`, `scripts/`, `tests/` 코드 자체에 한국어 주석 / 한국어 변수명이 있는지 grep
- 파일명에 `lee_*`, `_directive_*`, 한국어 파일명 등이 남아 있는지
- README.md / DESIGN.md 자체의 한국어 voice + Lee 표현 다수
- CLAUDE.md (현 행동 강령 자체) — *외부 공개 절대 금지* 또는 대폭 reframe

**확인 명령** (별도 directive 시):
```bash
grep -rE "Lee|이진석|HARNESS H|forbidden_now|관찰기" engine/ scripts/ tests/ --include="*.py"
grep -rE "Lee|이진석|HARNESS H|forbidden_now|관찰기" docs/ README.md DESIGN.md CLAUDE.md --include="*.md"
```

#### 1.4a Audit 실행 결과 (2026-05-01, autonomous iteration #2)

**`engine/` 검색 (`Lee directive|HARNESS H[1-8]|forbidden_now|관찰기 ≠ 평가기`)** — **6 hit, 모두 docstring 수준 reframing 필요**:

| 파일 | 라인 | 내용 |
|---|---|---|
| `engine/observer/__init__.py` | 4 | `관찰기 ≠ 평가기. Snapshot stream 위에서...` (모듈 docstring 한국어) |
| `engine/observer/core.py` | 9 | `원칙: 관찰기 ≠ 평가기. 관측 태그까지만, 해석/판정 안 함.` |
| `engine/observer/salience.py` | 7 | `감지 후보 (Lee directive §4.4):` |
| `engine/observer/snapshot_schema.py` | 89 | `Lee directive §5.1 schema.` |
| `engine/observer/recorder.py` | 137 | `Lee directive §5.1 schema 매핑.` |
| `engine/observer/candidate_curation.py` | 3 | `Per ... + Lee directive` |

→ 모두 *docstring* (실행 동작 영향 0). 별도 directive 시 reframe:
- "관찰기 ≠ 평가기" → "Observer-not-evaluator design principle"
- "Lee directive §4.4 / §5.1" → "design specification §4.4 / §5.1"

**`docs/portfolio/` 검색** — 60+ hit, 모두 *meta-section* (compliance 표 / forbidden 리스트 / 변환표 entry). 본문 사용 0건. 외부 공개 시 compliance 표 + forbidden 리스트는 *제거 또는 공개 분기에 미포함* 처리 필요.

**Substantive 항목 (reframe 또는 제거 필요)**:
- `PORTFOLIO_REPACK_PLAN.md:4` "**Source**: Lee directive" — 메타 헤더 → "Source: design specification" 또는 헤더 제거
- 모든 portfolio doc 끝의 `## ABSOLUTE 원칙 + Lee directive 준수` 섹션 — 외부 공개 분기에서 *전부 제거* (audit trail은 internal-only)

**플랫폼 무결성 확인**: 본 audit과 함께 `pytest -m "not slow and not archived"` 실행 — *1849 passed, 14 skipped, 0 failed* (67.29s). engine / observer / Director 모두 정상.

**Audit 작업은 본 LOOP 범위에서 *기록만*. 실제 reframing은 Lee §"public release 작업 금지" 그대로 보류 — 별도 directive 시.**

#### 1.4b 종합 audit (2026-05-01, autonomous iteration #3)

iteration #2에서 `engine/observer/`만 점검. 본 iteration에서 *전체 코드/문서 audit* 확장:

**Production code (별도 directive 시 reframe — 우선순위 ★★)**:

| Path | Hits | Files | 비고 |
|---|---|---|---|
| `engine/observer/` | 6 | 6 | 모두 docstring (실행 동작 영향 0) — iteration #2 §1.4a에 detail |
| `scripts/` | 11 | 9 | 대부분 docstring + 1-2 print statement. 주요 파일: `b_direction/analyze_s2_nonmonotonic.py`, `observer/candidate_packet.py`, `observer/narrative_summary.py`, `observer/observer_report.py`, `data_pipeline/fidelity_check.py`, `visual/export_cross_seed_visual_data.py`, `v3_measurement/generate_sanity_check.py`, `b_direction/test_d_prime_cross_seed.py`, `b_direction/test_seed_robustness.py` |
| `tests/` | 1 | 1 | `tests/test_observer/test_compare_views.py` (docstring) |
| `examples/` | 8 | 3 | demo 스크립트 — `demo_observer.py` (5), `demo_creative.py` (2), `demo_observer_story.py` (1) |
| **Production code 합계** | **26** | **19** | — |

**Root `.md` 파일 (별도 directive 시 reframe — 우선순위 ★★★)**:

| File | Hits | 비고 |
|---|---|---|
| `README.md` | 4 | 외부 첫 진입점, 가장 중요 |
| `DESIGN.md` | 6 | 4-layer 설명에 Lee 표현 |
| `CLAUDE.md` | 1 | 본 doc은 외부 공개 절대 금지 (별도 처리) |

**Docs (`docs/`, portfolio 제외)**:

- 약 **95+ 파일**에 forbidden phrase 포함 (총 200+ hit)
- 주요 내부 로그: `progress.md` (111 hit), `lessons.md` (74 hit) — *gitignored on public release* 처리
- `docs/observer/`, `docs/visual/`, `docs/demo/`, `docs/creative/` 등은 별도 reframe 또는 archive 분리 필요
- `docs/archive/` 다수 — 외부 공개 시 *gitignored* 또는 별도 branch 분리

**총합**: **109 .md 파일 + 19 .py 파일 = 128 파일에 reframe 필요**

**우선순위 권장 (별도 directive 시)**:

1. ★★★ Root `.md` (README, DESIGN, CLAUDE) reframe — 외부 첫 인상에 직접 영향
2. ★★ Production code (`engine/`, `scripts/`, `tests/`, `examples/`) docstring reframe — 코드 리뷰어 시야
3. ★ `docs/portfolio/` compliance 표 제거 — 공개 분기 작업 시 일괄
4. ☆ `docs/` 내부 로그 (`progress.md`, `lessons.md`, `docs/archive/`) — *공개 분기에 미포함* (gitignore 처리만, reframe 불필요)

**본 audit은 *기록만* — 실제 reframing은 Lee §"public release 작업 금지" 그대로 보류. 다음 LOOP에서 동일 audit 재실행 불필요 (본 결과 영구 보존).**

### 1.5 종교 / 신학 콘텐츠 (★ context-dependent)

| 파일 | 위험 | reframe 방법 |
|---|---|---|
| `content/peter/`, `content/judas/`, `content/caiaphas/` 정경 인용 | 종교적 colloquial 인상 | README에서는 "historical figures (e.g., Peter, Van Gogh)" 정도로 추상화 |
| `content/shared/scripture/` (개역개정 정경) | 저작권 (공유본 해당 없음 — 한국어 개역개정은 public domain 확인 필요) | LICENSE 결정 시 별도 명시 |
| `docs/HARNESS.md` 신학적 reasoning | religious flavor | reframe or omit from public docs |

---

## 2. 공개 전 감춰야 할 파일 / 용어 정리

### 2.1 `.gitignore` 추가 권장 항목

```gitignore
# Internal work logs
progress.md
lessons.md

# Archived directives (한국어 + Lee voice)
docs/archive/lee_directives_*/
docs/archive/working_notes_*/
docs/sessions/

# Working drafts (peer review 전)
docs/research/PAPER_DRAFT_V06.md
docs/research/PAPER_OUTLINE_V05.md
docs/archive/REVIEW_RESPONSE_*.md

# Generated visualization data (regenerate via scripts/)
data/visual/*.json

# IDE / OS
.vscode/
.idea/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/

# Personal memory
.claude/
```

### 2.2 외부어로 reframe 필요한 핵심 문서

| 파일 | 작업 | 우선순위 |
|---|---|---|
| `README.md` | `docs/portfolio/PORTFOLIO_README_DRAFT.md` 적용 | ★★★ |
| `CLAUDE.md` | *외부 공개 안 함* — 또는 minimal "developer guide"로 대폭 축소 | ★★★ |
| `DESIGN.md` | Lee 표현 / HARNESS verbatim 제거, 4-layer 설명만 유지 | ★★ |
| `docs/HARNESS.md` | "8-rule self-evaluation framework"로 reframe + 신학적 reasoning 제거 | ★★ |
| `docs/specs/` 다수 | spec 자체는 OK, Lee directive 인용 부분 reframe | ★ |

### 2.3 절대 외부 노출 금지 (★★★)

- ❌ `.claude/` 디렉토리 (Claude session memory)
- ❌ `progress.md`, `lessons.md` (개인 작업 로그)
- ❌ `docs/archive/lee_directives_*` (한국어 verbatim)
- ❌ Lee 개인명 / 이메일 / 한국어 verbatim 표현
- ❌ "HARNESS H1-H8" verbatim (reframe 후만 OK)
- ❌ "forbidden_now" 키워드
- ❌ "Case A/B/C" without "validation result" pairing

---

## 3. LICENSE 결정 필요

### 3.1 옵션 비교

| LICENSE | 특징 | WITNESS 적합도 |
|---|---|:---:|
| **MIT** | 가장 자유, 상업적 사용 OK, 책임 면제 | ★★★ (개인 portfolio 표준) |
| **Apache 2.0** | MIT + 특허 명시 + 변경 표시 의무 | ★★ (다소 corporate) |
| **BSD 3-Clause** | MIT 유사 + endorsement 금지 | ★★ |
| **GPL v3** | copyleft (파생물도 GPL 의무) | ★ (포트폴리오용 비권장) |
| **CC BY-NC 4.0** | 비상업적 사용만 | content/ 부분에는 검토 가치 |
| **No LICENSE** | 기본 저작권 (사용 권한 0) | ✗ (외부 사용 불가) |

### 3.2 결정 시 고려사항

1. **코드 vs content 분리** — engine/scripts/visual code는 MIT 가능. content/ (정경 인용 등)는 별도 license 가능 (CC BY-SA 4.0 / public domain attribution 등)
2. **취업용 portfolio**: MIT가 가장 적합 (employer가 깐깐하게 보지 않음)
3. **연구 / 학술**: Apache 2.0 + CITATION.cff
4. **현재 권장**: 결정 보류 → 첫 외부 공유 시점에 결정 (그 전에는 "All rights reserved" 상태로 private)

### 3.3 추가 자료 (LICENSE 결정 시)

- [ ] `LICENSE` 파일 (root)
- [ ] `CITATION.cff` (학술 인용 시)
- [ ] `NOTICE` (Apache 2.0 사용 시 third-party attribution)
- [ ] content/ 별도 license 명시 (필요 시)

---

## 4. Branch 전략 결정 필요

### 4.1 옵션 비교

| 옵션 | 작업 | 난이도 | 위험 |
|---|---|:---:|---|
| **A. Single public + .gitignore** | 현 main에 `.gitignore` 추가 + push | 낮음 | git history에 *과거* 내부 로그 노출 위험 — git filter-branch 또는 rewriting 필요 |
| **B. Separate `public` branch** | `public` branch 새로 생성, internal 파일 제거 후 squash, 별도 push | 중간 | history 분리, 깨끗하지만 main과 sync 부담 |
| **C. New repo (clean)** | 새 GitHub repo, 코드 + reframe된 docs만 import | 높음 | 가장 깨끗, 가장 많은 작업 |
| **D. Stay private + URL share** | 보류, 필요 시 specific URL로만 공유 (collaborator add) | 0 | 공개 효과 없음, 면접용으로만 |

### 4.2 git history 위험 (모든 옵션 공통)

- 현 git history에 한국어 commit 메시지 / Lee 표현 / progress.md 변경 흔적이 있을 수 있음
- 명령: `git log --all --pretty=format:"%h %s" | head -50` 으로 점검
- *Past commits는 .gitignore가 막지 못함* — git filter-branch 또는 BFG Repo-Cleaner로 history rewrite 필요 (opt B/C가 더 안전)

### 4.3 권장 (지금 단계)

- **현재**: 옵션 D (stay private) — 결정 보류
- **첫 외부 공유 시**: 옵션 C (new clean repo) 권장 — 가장 안전, 가장 깨끗
- **이유**: filter-branch / squash는 한 번 잘못하면 복구 어려움. clean import가 가장 reversible

---

## 5. Screenshot / GIF / Asset 필요

### 5.1 자산 목록 (자세한 내역: [PORTFOLIO_ASSET_CHECKLIST.md](PORTFOLIO_ASSET_CHECKLIST.md))

- **Screenshots × 3** — single-run / cross-seed / vangogh quiet (PNG 1920×1080)
- **GIFs × 3** — timeline scrub / candidate→packet / cross-seed click (각 < 2 MB, 5-10 sec)
- **Architecture diagram** — SVG 또는 PNG 1200px (현재 ASCII만 있음)

### 5.2 capture 작업 (현 LOOP 범위 밖)

- 추정 시간: ~2 시간 (capture 75 min + crop/optimize 30 min + linkage 15 min)
- 도구: Snipping Tool (Windows), OBS Studio 또는 ScreenToGif
- 위치: `docs/portfolio/assets/` (생성 필요)

### 5.3 capture 시 reframe 점검

- ✅ Anchor 이름이 `peter_scarcity_baseline` 등 — 외부에서 "scenario A / B / C" 명명도 고려
- ✅ Candidate ID (예: `C03_t142`) — 식별 가능 정보 없음, OK
- ⚠️ Outcome banner의 "REC / PARTIAL / SAT" — 약어 의미 caption 필요 ("recovery / partial / saturation")

---

## 6. 루트 README 적용 전 체크

### 6.1 현 README.md 위험

- Lee directive verbatim references 다수
- 한국어 voice (CLAUDE.md / DESIGN.md와 mixed)
- 내부 작업 흐름 / 실험 단계 명시 (외부에서 over-detail)

### 6.2 적용 절차 (별도 directive 시)

1. `docs/portfolio/PORTFOLIO_README_DRAFT.md`를 base로 복사
2. 회사명 / 본인명 / contact는 application 시 별도 결정
3. Quick start 명령 (3-line export + HTTP server) 실제 작동 검증
4. Architecture ASCII 다이어그램 → SVG diagram으로 교체 (option)
5. Validation 섹션 numbers 검증 (2,640+ tests, 97%+ coverage 등)
6. Limitations 섹션 정직성 검증
7. CLAUDE.md / DESIGN.md / progress.md / lessons.md 등 *내부* 문서 reference 제거

### 6.3 README 적용 후 추가 작업

- Root에 `LICENSE` 추가 (위 §3 결정 후)
- Root에 `CITATION.cff` 추가 (학술 인용 시)
- `docs/portfolio/assets/` 생성 + screenshot/GIF 배치
- `.github/` 폴더 (issue templates, PR templates) — optional

---

## 7. 내부 로그 / Lee directive / HARNESS 외부어 변환 (요약)

자세한 내역은 [INTERNAL_TO_EXTERNAL_TERMS.md](INTERNAL_TO_EXTERNAL_TERMS.md) 참조. 핵심 매핑:

```
INTERNAL                          EXTERNAL
─────────────                    ─────────────────
Lee directive            →       design specification
HARNESS                  →       self-evaluation framework
forbidden_now            →       scope constraints
Branch C                 →       configuration sensitivity validation
Case A                   →       validation result (passed)
관찰기 ≠ 평가기          →       observer-not-evaluator
story_ready              →       candidate suitable for narrative review
v0.1 freeze              →       v0.1 stable release
LOOP / 자율 LOOP        →       iteration / development cycle
ABSOLUTE Rule            →       architectural constraint
```

**Forbidden phrasing** (외부 공개 절대 금지):
- ❌ "AI 이야기 생성기" / "story generator" / "narrative AI"
- ❌ "신학 / 종교 시뮬레이터", "religious simulator"
- ❌ "그냥 / 취미로 / 재미로" → "internal exploration project"
- ❌ "Lee가 ~", "Lee §" — "design spec specifies"
- ❌ HARNESS H1-H8 verbatim — "8-rule self-evaluation framework"

---

## 8. 다음 단계 옵션 (Lee 결정 대기)

### Option C1 — Stay Internal Complete (현 권장)

**작업**: 0  
**효과**: 본 memo 포함 11 portfolio 문서를 *cover letter / 자기소개 / 면접* 자료로만 사용. 코드 / repo 공개 없음.

**장점**:
- 위험 0 (한국어 / Lee 표현 / 내부 로그 노출 0)
- 작업 부담 0 (LICENSE / branch / asset capture 모두 보류)
- 면접 / 자기소개에는 본 portfolio 문서로 충분

**단점**:
- "GitHub 가서 보세요" 라는 외부 reference link 없음
- 깊은 기술 면접에서 코드 walkthrough 어려움 — 본인 화면 share + 라이브 코드 리뷰 필요

**적합 시점**: 직무 지원 단계가 아닐 때 / 첫 면접 라운드 / 비기술 직무 / 코드 공개에 부담 느낄 때.

---

### Option B1 — Apply README Partial (limited public)

**작업**: ~2-3 시간 (README 적용 + .gitignore + LICENSE 결정 + 1차 reframe)

**구체적 작업**:
1. `docs/portfolio/PORTFOLIO_README_DRAFT.md`를 root `README.md`에 적용
2. `.gitignore`에 progress.md / lessons.md / Lee directive archive 추가
3. CLAUDE.md / DESIGN.md / docs/HARNESS.md 한국어 voice 1차 reframe
4. LICENSE 결정 (MIT 권장) + `LICENSE` 파일 추가
5. Branch 전략 — Option C (new clean repo) 또는 D (private + collaborator share) 결정
6. `docs/portfolio/` 폴더 그대로 commit (공개 자료)

**효과**: GitHub repo는 public이지만 *clean* 상태. 본 memo의 §1 위험은 모두 차단.

**미포함**: screenshot/GIF capture는 별도 단계 (Option A1).

**적합 시점**: 면접에서 "GitHub URL 주실 수 있나요?" 질문이 *반복적으로* 들어올 때. 또는 자신의 코드 보여주는 게 application 강도를 명확히 올릴 때.

---

### Option A1 — Asset Capture + Full Public Release

**작업**: ~5-6 시간 (Option B1 작업 + asset capture 2 시간 + README polish 1 시간)

**Option B1 작업 +**:
7. Screenshot × 3 capture (PNG 1920×1080)
8. GIF × 3 capture (< 2 MB each)
9. Architecture diagram SVG 변환
10. README에 asset link 통합
11. 최종 fresh-clone 테스트 (1 user, no prior context)
12. CITATION.cff (학술 인용 시)

**효과**: GitHub README가 visual + crisp. 외부 visitor가 *5분 내* 시스템을 이해 가능.

**적합 시점**: 직무 지원이 적극 단계 / 면접에서 GitHub demo 빈도 높음 / 학술 / 연구 라운드.

---

## 9. 옵션별 추천 매트릭스

| 사용자 상황 | 추천 옵션 |
|---|---|
| 이번 분기 application 안 함 | **C1** — 현 portfolio 문서로 충분 |
| 이번 분기 1-2 application | **C1** — cover letter snippet으로 가능, GitHub link 불필요 |
| 이번 분기 3+ application | **B1** — clean public repo로 차별화 |
| 학술 / 연구 라운드 | **A1** — citation + asset 필수 |
| 첫 면접 통과, 기술 라운드 임박 | **B1** + 면접 시 verbal demo + screen share |
| 보안 / 컴플라이언스 직무 | **C1** 유지 — 코드 공개 부담 ↑ |

---

## 10. 즉시 결정 vs 보류 매트릭스

### 즉시 결정 가능 (저비용, 가역)

- ✅ Option C1로 일단 stay (본 LOOP 종료 시점 기본)
- ✅ portfolio 문서 (지금까지 11개) 자체 사용 시작 (cover letter / interview)

### 별도 directive 필요 (고비용, 일부 비가역)

- ❗ LICENSE 결정 — 한 번 결정하면 변경에 social cost
- ❗ Branch 전략 — Option C (new repo)는 가역, Option B (filter-branch)는 비가역 위험
- ❗ Asset capture — 시간 ~2 시간, 한 번 결정 후 진행
- ❗ README 적용 — root 변경, 신중히

---

## 11. 본 LOOP 권장 결론

**현재 단계**: Option C1 (Stay Internal Complete)

**근거**:
1. 본 LOOP 작업으로 *11개 portfolio 문서* (이전 7 + 본 LOOP 4 + 본 memo 포함)가 cover letter / interview에 충분
2. LICENSE / branch / asset 결정은 *application 강도 / 면접 단계*가 명확해진 후가 안전
3. 코드 공개의 *비가역 위험* (git history rewrite, 한국어 흔적)이 *공개 가치*보다 큼 (현재 단계)
4. Lee §"public release 작업 금지" 누적 directive 준수

**다음 단계 trigger 조건**:
- 면접에서 GitHub URL 요구 빈도 > 30% → Option B1 검토
- 학술 / 연구 application → Option A1 검토
- Lee 별도 directive로 release 결정 → 본 memo §3-§6 작업 시작

---

## 12. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 금지" | ✅ — risk memo만, release 작업 0 |
| Lee §"screenshot/GIF capture 금지" | ✅ |
| Lee §"LICENSE 결정 금지" | ✅ — 옵션 비교만 |
| Lee §"branch 생성 금지" | ✅ — 옵션 비교만 |
| Lee §"내부 문서 삭제 금지" | ✅ |
| Lee §"새 기능 구현 금지" | ✅ |

---

## 13. 한 줄 요약

> **Public release 위험 감지 + cleanup checklist + 3가지 옵션 (C1 Stay Internal / B1 Apply README Partial / A1 Asset Capture). 본 LOOP 권장: **C1**. LICENSE / branch / asset 모두 별도 directive 시 결정. 현재는 11 portfolio 문서로 cover letter / interview 충분.**

---

**Versioning**: v1 (this risk memo) — 2026-05-01 stay-internal package.
