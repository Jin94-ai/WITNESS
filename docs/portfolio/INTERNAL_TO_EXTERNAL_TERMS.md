# WITNESS — Internal-to-External Terms 변환표

> 외부(채용/리뷰어) 설명 시 *반드시 변환*. 내부 용어 그대로 쓰면 외부 문맥에서 *비공식적이고 사적*으로 들림.

---

## 0. 변환 원칙

1. **Personal name → role-based term**: "Lee directive" → "design specification"
2. **Internal jargon → general technical term**: "HARNESS" → "self-evaluation framework"
3. **Project history label → outcome label**: "Case A" → "validation result"
4. **Korean honorifics / colloquial → English neutral**: "관찰기 ≠ 평가기" → "observer-not-evaluator design principle"
5. **Implementation-specific → user-facing**: "story_ready" → "candidate suitable for narrative review"

---

## 1. Process / governance terms

| Internal | External | Reasoning |
|---|---|---|
| Lee directive | design specification (or "design spec") | Personal reference → role |
| Lee 명시 | design intent / scope constraint | Korean attribution → neutral |
| 권장 | recommended | Korean → English neutral |
| 명시 | explicit | Korean → English |
| 자율 LOOP / Loop / iter | iteration / development cycle | Internal jargon → standard |
| Phase 1-7 | phased development | Phase 번호는 OK, *Lee plan.md*는 reframe |
| forbidden_now | scope constraints / out-of-scope items | Internal flag → standard |
| Out of scope | out-of-scope (그대로) | OK as-is |

---

## 2. Validation / decision terms

| Internal | External |
|---|---|
| Case A / BP-A / EX-A / D-A / F-A / TV-A / V-A / CS-A / A3-A | validation result (passed) |
| Case B / EX-B / etc. | validation result (partial) |
| Case C / EX-C / etc. | validation result (failed) — needs re-design |
| Case D-D | validation incomplete |
| Stop rule | phase completion criteria |
| Success criteria | acceptance criteria |
| Failure criteria | regression conditions |
| 잠금 / freeze | finalize / freeze (그대로 OK) |
| 리뷰 | review (그대로 OK) |
| 검증 | validation (그대로 OK) |

---

## 3. HARNESS framework terms

| Internal | External |
|---|---|
| HARNESS H1-H8 | self-evaluation framework (8-rule anti-bias engineering) |
| H1 null hypothesis | "specify falsifying observation before claiming positive findings" |
| H2 alternatives soaking | "list alternatives before attributing to external causes" |
| H3 spec verbatim | "cite specifications verbatim" |
| H4 negative findings | "document what could still be wrong" |
| H5 verbatim 보존 | "preserve original instruction before scope reduction" |
| H6 frame-neutral | "present options frame-neutrally" |
| H7 self-audit | "8-question report self-audit" |
| H8 single-seed conditioning | "use 5+ seed ensemble for sensitivity claims" |
| 자가감사 | self-audit |
| HARNESS 자가 점검 | self-evaluation check |

---

## 4. Engine / architecture terms

| Internal | External |
|---|---|
| 4-layer architecture | 4-layer architecture (그대로 OK) |
| ABSOLUTE Rule #1/#6 | architectural constraint #1/#6 |
| Rule #1 (no person hardcoding) | engine layer separation principle (no domain hardcoding) |
| Rule #6 (engine API preservation) | API stability constraint (engine layer is frozen) |
| 관찰기 ≠ 평가기 | observer-not-evaluator design principle |
| Additive layer 패턴 | additive layer pattern |
| Schema versioning | schema versioning (그대로 OK) |
| 버전 freeze | version freeze (그대로 OK) |

---

## 5. Branch C / configuration sensitivity terms

| Internal | External |
|---|---|
| Branch C | configuration sensitivity validation |
| Branch C 1차 evidence | first-round configuration sensitivity evidence |
| Branch C lock decision | configuration sensitivity validation (locked claim) |
| 18 probes | 18-probe validation set |
| GPT-5.5 send / response | external LLM-based readability evaluation |
| Locked claim | validated claim |
| Cross-seed ensemble | cross-seed (multi-seed) ensemble |

---

## 6. Story output / candidate terms

| Internal | External |
|---|---|
| story candidate | narrative candidate |
| story_ready | candidate suitable for narrative review |
| observation_only | candidate kept for observation, not narrative use |
| low_activity_hold | low-activity candidate kept for inspection |
| 3-bucket curation | 3-mode classification |
| Q1-Q4 curation | curation pipeline (4 phases) |
| P1-P5 pipeline | candidate extraction pipeline (5 phases) |
| O1-O7 observer | observer layer (7 phases) |
| use_mode | candidate use mode |
| strongest_lens | primary perspective (lens) |
| salience tag | salience tag (그대로 OK — 8 types: cohort split, saturation lock, etc.) |
| candidate packet | candidate packet (그대로 OK) |
| rationale | rationale (그대로 OK) |

---

## 7. Visualization / explorer terms

| Internal | External |
|---|---|
| Visual Observer | visual observer (그대로 OK) |
| Visual Explorer v0/v0.1/v0.2 | visual explorer v0.x |
| Dot Visual Observer | dot-based visual observer |
| MVP | minimum viable prototype (or "MVP" 그대로 OK) |
| V2 minimal interaction | V2 minimal interaction features |
| Cross-seed view | cross-seed view (그대로 OK) |
| Small multiples | small multiples (academic term, OK) |
| Anchor | anchor (config preset, OK with brief explanation) |
| Anchor 2 / Anchor 3 | second anchor / third anchor |
| broad navigation entry | broad navigation entry |
| deep view | detailed (deep) view |

---

## 8. Renderer / story track terms

| Internal | External |
|---|---|
| Renderer Cycle 1-7 | renderer iteration 1-7 |
| Renderer freeze | renderer is intentionally frozen |
| Cycle 7 freeze 후 historical | post-freeze historical artifacts |
| story renderer 재개 | renderer restart (intentionally not in scope) |
| Asset Pack v1 | asset pack v1 (그대로 OK) |
| J-Alpha / J-Beta | creative iteration alpha / beta |
| Creative IP track | creative output track |

---

## 9. Outcome / scenario terms

| Internal | External |
|---|---|
| REC outcome | recovery outcome |
| SAT outcome | saturation outcome |
| MIXED outcome | mixed outcome |
| PARTIAL outcome | partial outcome |
| Peter scenario | Peter scenario (그대로 OK, biographical) |
| Van Gogh scenario | Van Gogh scenario (그대로 OK) |
| Talleyrand scenario | Talleyrand scenario (그대로 OK) |
| 정경 / canonical scripture | canonical scripture (그대로 OK with brief explanation) |
| nonmonotonic finding | nonmonotonic relationship (counterintuitive: more X → more Y) |

---

## 10. Project status terms

| Internal | External |
|---|---|
| v0.1 freeze | v0.1 stable release |
| v0.2 진행 | v0.2 next iteration |
| Internal Demo Package v1 | internal demo package v1 |
| Browsing Pack v1 | browsing pack v1 |
| 데모 가능 상태 | demo-ready state |
| 5분 데모 | 5-minute live demo |
| 작업 영역 | working area |
| archive | archive (그대로 OK) |

---

## 11. Korean idiom / structure → English

| Internal (Korean) | External (English) |
|---|---|
| ~을 인정한다 | confirm / acknowledge |
| ~을 명시한다 | specify / indicate |
| ~을 검증한다 | validate |
| ~을 보존한다 | preserve |
| ~을 분리한다 | separate / decouple |
| ~으로 흡수됨 | absorbed into |
| ~으로 갈라짐 | branches into |
| 핵심 메시지 | key message |
| 한 줄 요약 | one-line summary |
| 한 줄 요약 | one-liner / TL;DR |

---

## 12. Sentence-level reframing examples

### Example 1
- **Internal**: *"Lee directive `WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md` §0 verbatim — 도트 기반 흐르는 세계 관찰 + 줌인/줌아웃 + 이야기 후보 발견."*
- **External**: *"As specified in the design spec: dot-based visualization for flowing world observation, with zoom-in/zoom-out, surfacing story candidates."*

### Example 2
- **Internal**: *"HARNESS H8 단일 seed conditioning warns sensitivity ratio가 headline claim이면 5+ seed ensemble 필수."*
- **External**: *"The self-evaluation framework's 8th rule warns about single-seed conditioning bias: any sensitivity claim should use a 5+ seed ensemble."*

### Example 3
- **Internal**: *"Phase 7 fork decision = Case F-A. v0.1 Freeze + Visual Explorer 중심으로 v0.2 진행."*
- **External**: *"Phase 7 fork decision: stable v0.1 release; v0.2 will focus on Visual Explorer."*

### Example 4
- **Internal**: *"vangogh story_ready 0개 = 실패가 아닌 다른 dynamics 인정."*
- **External**: *"Van Gogh's zero candidates classified as 'suitable for narrative review' is not a failure — it indicates contemplative dynamics that the 8 salience tags don't fire on. The system preserves this honestly rather than auto-tuning."*

### Example 5
- **Internal**: *"관찰기 ≠ 평가기 원칙 일관 — 시스템은 좋은 이야기/나쁜 이야기 자동 판정 안 함."*
- **External**: *"Observer-not-evaluator design principle: the system categorizes candidates without judging story quality. Final assessment is left to a human reviewer."*

---

## 13. Forbidden phrases (외부 문맥에서 절대 금지)

- ❌ "Lee가 X라고 했다" → "the design spec specifies X"
- ❌ "내가 X를 했다" (in resume bullet) → "implemented X" or "designed X"
- ❌ "그냥 만들었다 / 자동으로" → "designed and implemented"
- ❌ "재미로" → "as a research project" or "as an internal exploration"
- ❌ "AI 이야기 생성기" → "agent-based simulation" (절대 ML/AI generation 오해 유발 금지)
- ❌ "게임처럼" → "interactive visualization"

---

## 14. Forbidden internal references in public docs

- ❌ `progress.md` reference
- ❌ `lessons.md` reference
- ❌ `docs/archive/lee_directives_*` reference
- ❌ `forbidden_now` term
- ❌ Korean Lee directive verbatim quotes
- ❌ HARNESS H1-H8 verbatim (only reframed version OK)
- ❌ "Case X" without context (always pair with "validation result")

---

## 15. Quick reference card (1 page)

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
low_activity_hold        →       low-activity candidate
observation_only         →       candidate kept for observation
v0.1 freeze              →       v0.1 stable release
LOOP / 자율 LOOP        →       iteration / development cycle
명시                     →       explicit / specified
ABSOLUTE Rule            →       architectural constraint
```

---

## 16. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 작업 금지" | ✅ 변환표만, 적용 안 함 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |

---

## 17. 한 줄 요약

> **Internal-to-External terms 변환표 = 14 카테고리 + 5 sentence-level examples + forbidden phrases. 외부(채용/리뷰어) 설명 시 *반드시 reframe*. 본 doc은 *reference*, 실제 적용은 PORTFOLIO_README_DRAFT 적용 시 사용.**

---

**Versioning**: v1 (this terms) — 2026-04-30 portfolio repack.
