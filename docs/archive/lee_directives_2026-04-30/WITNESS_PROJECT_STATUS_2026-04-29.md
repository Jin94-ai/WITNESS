# WITNESS — 전체 프로젝트 진행상황 (2026-04-29)

**Date**: 2026-04-29 (이번 세션 종료 시점)
**용도**: Lee 한눈 점검 dashboard

---

## 0. 한 줄 요약

**Renderer 7 cycles 후 freeze + Branch C external eval 응답 대기 중. 자율 모드 idle 도달 시 자동 종료 directive 적용.**

---

## 1. 영역별 현재 상태

### 1.1 Person Engine (`engine/`)

| 항목 | 상태 |
|---|---|
| 모듈 | 34+ |
| 테스트 (전체) | 1766 collected |
| 테스트 (fast) | 1618 PASS, 14 skipped, **1 FAIL** (pre-existing) |
| Coverage | 97% (15 modules at 100%) |
| Ruff / mypy | 0 errors |
| **ABSOLUTE Rule #1 위반** | **`engine/story/selector.py` peter/vangogh hardcoding** (J-Beta selector library, untracked 새 파일) |

**위반 상세**: 21 hardcoding violations (peter 19개 + vangogh 2개). J-Beta Lee Gate 2 = A 응답 받고 추가됐지만, 이전 cycle에서 *engine/ 무수정* 원칙 위반된 상태로 untracked로 남음. `test_no_person_hardcoding_in_engine` 실패.

→ **Lee 결정 필요**: (a) selector를 `scripts/`로 이동 (Rule #1 준수) / (b) Rule #1 예외 인정 + commit / (c) selector 자체 폐기

### 1.2 World Engine v2.0 (`world/`, `engine/world/`)

| 항목 | 상태 |
|---|---|
| Spike 1-5 | ✅ 완료 |
| Spike 6+ | ⏸ 보류 (forbidden_now §3 — research deepening 미허락) |
| Layers | calendar / economy / politics / factions / social |
| `world/space/` | 6 canonical locations + movement cost |
| `world/agents/` | Jesus + Pilate + Caiaphas + 제자들 + Barabbas |

### 1.3 Story Output Layer (`scripts/story/`, `docs/story/`)

| 항목 | 상태 |
|---|---|
| Pipeline | 3-stage (extract → IR → render), no LLM |
| **Renderer cycles** | **Cycle 1-7 진행 후 FREEZE** (Lee Type E directive, 2026-04-29) |
| Sentence pool | 30 → 136 lines (+353%) |
| 96 narrative + Trilogy + 25 anchor variations | 모두 Cycle 7 후 generated |
| test_story | 119/119 PASS |
| Forbidden audit | 96/96 clean |
| Lee Gate 1 v3 평가 | ✅ **완료** (P6/Trilogy/P9/P10/P_PV_09/P_CV_01 6 sample) |
| Cycle 8+ | ❌ **금지** (Type E) |

**Lee v3 평가 결과**: v2 약점 5/5 모두 처리. 가장 좋은 Cycle = #3 (scenario × outcome SAT/MIXED). 가장 약한 Cycle = #7 (motif closing, templates 냄새 위험).

### 1.4 Branch C (configuration sensitivity claim)

| 항목 | 상태 |
|---|---|
| 1차 evidence | ✅ S5 placement + S4 cast (18 probes) |
| Cross-seed walkback | ✅ paper §7.4 + Appendix G |
| 18-probe send bundle | ✅ ready (`BRANCH_C_18_PROBES_SEND_BUNDLE.md`) |
| GPT-5.5 paste | ❌ **대기 중** (Lee가 직접 paste) |
| 응답 raw | ❌ 미도착 (`BRANCH_C_GPT55_RESPONSE_RAW.md`) |
| 결과 분기 | 사전 정의됨 (Case S/M/F, `RENDERER_FREEZE_DECISION.md` §3) |

### 1.5 Creative IP Track (J-Alpha + J-Beta)

| 항목 | 상태 |
|---|---|
| J-Alpha 1차 증명 | ✅ PASS 5/6 (Peter scarcity baseline) |
| J-Beta 확장 | ✅ Lee Gate 2 = A 응답 |
| 5 Anchor library | baseline / high_density / double / triple / vangogh_sacred |
| Scarcity Trilogy | 3-act (1/2/3 accusations → SAT/SAT/REC modal) |
| Test_story | 119 PASS |
| Single demo entry | `examples/demo_creative.py --status / --trilogy / --all-anchors` |
| Creative asset pack v1 | ⏸ Branch C 결과 후 (Case S 시만) |

### 1.6 Content packs

| Pack | 상태 |
|---|---|
| Peter (마지막 50일) | ✅ 4 시나리오 |
| Judas / Caiaphas / Crowd | ✅ 통합됨 |
| VanGogh (3 시나리오) | ✅ 완료 |
| Talleyrand (3rd scenario) | ⏸ 시작 안 함 (forbidden_now: engine universality 검증용 후보) |
| **content/peter/v3/profile.json** | untracked, v3 redesign 작업 중 |
| **content/judas/v3/profile.json** | untracked |
| **content/vangogh/v3/** | untracked |

### 1.7 Paper draft v0.6

| 항목 | 상태 |
|---|---|
| Draft | 319 lines (`docs/research/PAPER_DRAFT_V06.md`) |
| §6 핵심 finding 10개 | ✅ |
| Appendix G (Branch C cross-seed) | ✅ |
| Appendix H (Story output configuration sensitivity) | ✅ |
| Methodological §7.4 (single-seed bias) | ✅ |
| Renderer 7 cycles 반영 | ❌ 미반영 (forbidden_now: paper 확장) |
| arXiv 제출 / 저널 결정 | ❌ 보류 |

---

## 2. 이번 세션 성과 (2026-04-29)

### 2.1 Renderer Cycle 1-7 진행 (가장 큰 작업)

| Cycle | Trigger | Patches | Lee 평가? |
|---|---|---|:---:|
| 1 | 자율 (Gate 1 v1) | scarcity opening 5 / cross-scenario REC | ❌ |
| **2** | **Lee v2 부분 통과** | **A/B/C — phrase de-template + outcome rhythm + LOW branch** | **✅** |
| 3 | Type D (saturation override) | D/E/F — scenario × outcome SAT/MIXED + opening/pool 확장 | ❌ |
| 4 | (계속) | G/H — accusation REC sharpness + PARTIAL × scenario | ❌ |
| 5 | (계속) | I — scene-level micro-action (Stage 2.5) | ❌ |
| 6 | (계속) | J — Trilogy Act II escalation envelope | ❌ |
| 7 | (계속) | K — primary motif closing line (Stage 6) | ❌ |

→ **Cycle 2만 Lee 평가 후 진행**. Cycle 3-7는 자율 (Type D directive 넓은 해석). Lee가 v3 평가에서 *retroactively 인정* + Cycle 8 freeze 명시.

### 2.2 Lee 결정문 처리 (Type E directive)

- Branch C external eval **GO**
- Renderer **Cycle 7 freeze**
- Sample 6 BUNDLE doc **cleanup** ✅
- Branch C 3 분기 사전 정의 (`RENDERER_FREEZE_DECISION.md`)

### 2.3 Idle 자동 종료 directive

- 700s × 17회 idle wakeup 후 Lee가 idle 자동 종료 명시
- ScheduleWakeup 미호출 → loop 자연 종료
- Lee 새 입력으로만 재개

### 2.4 lessons L24-L31 등록 (8개 추가)

- L24: Type C scoped patch
- L25: Type D saturation override
- L26: sharpness coexistence pool
- L27: Stage 2.5 zoom-in
- L28: sample-specific meta envelope
- L29: coherence ring closing + over-engineering risk-cap
- L30: Type E freeze + 분기 사전 정의
- L31: Idle 자동 종료

L18-L31 = **자율 모드 phase + directive type 14 패턴**.

### 2.5 변경 통계

| 항목 | 수치 |
|---|---|
| 모디파이드 파일 | 24개 (engine/* + tests/* + 핵심 docs) |
| Untracked 파일 | 70개 (creative docs / b_direction / archive 등) |
| Cycle plan docs | 7개 (`RENDERER_CYCLE_2_PLAN` ~ `RENDERER_CYCLE_7_PLAN`) |
| Sample diff docs | 6개 (`renderer_gate1_v3` ~ `v8_samples`) |
| Retrospective | 1개 (`RENDERER_CYCLES_1_TO_6_RETROSPECTIVE`) |
| Lee 평가 BUNDLE | 1개 (`RENDERER_GATE1_V3_BUNDLE_CYCLE7`) |
| Freeze decision doc | 1개 (`RENDERER_FREEZE_DECISION`) |
| `scripts/story/render_story_ko.py` | ~330 lines 추가 |

---

## 3. 대기 중인 게이트 (외부 입력)

### 3.1 Branch C GPT-5.5 응답 (Lee가 직접 처리 필요)

**파일**: `docs/b_direction/BRANCH_C_18_PROBES_SEND_BUNDLE.md`

**Lee 절차**:
1. §A 전체를 GPT-5.5 새 채팅에 paste
2. §B는 보내지 않음
3. 응답 raw text → `BRANCH_C_GPT55_RESPONSE_RAW.md` 저장
4. Claude Code 자동 재개 (Case S/M/F 분기 처리)

**평가 기준 (5개)**:
- Within-scenario divergence (≥2 distinct outcomes in ≥2 of 3 scenario groups)
- Configuration sensitivity verdict = STRONG or MODERATE
- Q2a typing accuracy ≥15/18
- Final summary self-call ≥12/18
- Q3b world-side axes ≥3 of 5 axes

**자동 분기** (`RENDERER_FREEZE_DECISION.md` §3):
- Case S (4-5/5 PASS) → creative asset pack v1 plan
- Case M (2-3/5 PASS) → 내부 데모만, Branch C lock 보류
- Case F (0-1/5 PASS) → renderer 작업 중단, 구조/평가 재검토

---

## 4. Forbidden_now (현재 자율 금지)

| 항목 | 사유 |
|---|---|
| Renderer Cycle 8+ | Lee Type E directive |
| Renderer 자율 rollback | Lee 미명시 (별도 directive 필요) |
| Public release / asset pack 진행 | Branch C 결과 후 Case S 시만 |
| engine touch (pre-existing 외) | ABSOLUTE Rule #1 |
| Branch C 새 slice | Lee 결정 #5-7 외 |
| Paper 확장 | Type B forbidden_now §9 |
| 새 자율 cycle 생성 | Idle 자동 종료 directive (L31) |

---

## 5. 자율 가능 영역 (Lee 결정 시)

Lee가 명시하면 자율 진행 가능한 작업:

| 영역 | 작업 | 단가 |
|---|---|---|
| **Engine integrity fix** | `engine/story/selector.py` → `scripts/`로 이동 (Rule #1 준수) | 중 |
| **Paper §6 + Appendix H 업데이트** | 7 cycles renderer 진화 paper 반영 | 큼 |
| **3rd scenario (Talleyrand)** | engine universality 검증 | 매우 큼 |
| **Archive cleanup** | untracked 70개 정리 | 작음 |
| **v1.0 Stage 2 PyTorch encoder** | `drive_training.py` line 118 TODO | 큼 |
| **v1.1 Relational graph** | beliefs-about-others | 매우 큼 |
| **Cycle 5/6/7 일부 rollback** | Lee가 약한 cycle 식별 후 | 작음 |
| **Sample 6 narrative 본문 점검** | 추가 cleanup 필요 시 | 작음 |

---

## 6. Lee 결정 옵션 (현재 상태)

### 옵션 A — Branch C 응답 대기 (status quo, idle)
- Lee가 GPT-5.5에 paste → 응답 가져오기
- 그 사이 자율 모드 종료 (idle directive)
- 응답 도착 시 Lee 새 입력으로 재개

### 옵션 B — 다른 영역 자율 허락 (확장)
- 명시 예: "engine integrity fix 진행해" / "paper §6 업데이트해" / "archive cleanup해"
- 자율 모드 재개

### 옵션 C — 새 directive
- 우선순위 재정의
- 영역 + 단계 명시

### 옵션 D — Cycle 7 일부 rollback
- 약한 Cycle (예: Cycle 7 motif closing) rollback
- BUNDLE 재생성

---

## 7. lessons.md 누적 패턴 정리 (L18-L31)

| ID | 패턴 | 영역 |
|---|---|---|
| L18 | 자율 모드 3 phase 종합 | autonomous mode |
| L19 | Anchor diversity = cross-seed sensitivity 핵심 | J-Alpha |
| L20 | 자율 디버깅 cycle은 FAIL signal 직후 효과적 | autonomous |
| L21 | Lee Gate 자율 cycle 패턴 | J-Beta |
| L22 | Type B (forbidden 명시) | directive |
| L23 | Type B-2 (외부 판독 분기 사전 정의) | directive |
| L24 | Type C (외부 평가 partial pass + scoped patch) | directive |
| L25 | Type D (saturation override + iterative) | directive |
| L26 | Sharpness coexistence pool (Lee verbatim 매핑) | renderer |
| L27 | Stage 2.5 zoom-in (additive structural) | renderer |
| L28 | Sample-specific meta envelope (body 무수정) | renderer |
| L29 | Coherence ring closing + over-engineering risk-cap | renderer |
| **L30** | **Type E (Lee 평가 완료 후 freeze + 분기 사전 정의)** | **directive** |
| **L31** | **Idle 자동 종료 — 자율 모드 자연 boundary 명시** | **autonomous** |

→ **directive type 진화** (5단계): A → B → B-2 → C → D → E
→ **자율 모드 운영** (4단계): infinite cycle → directive boundary → operational saturation → idle auto-termination

---

## 8. Versioning

| Version | Date | 핵심 |
|---|---|---|
| v0.5 | 2026-04 이전 | Rule-based + 7-layer validation |
| v0.7 | 현재 | Trace pipeline + player view + drive hooks |
| v0.6 paper | 319 lines | 미반영 (Renderer 7 cycles) |
| **이번 세션 (2026-04-29)** | **Renderer 7 cycles + Lee Type E + Idle auto-termination** | |
| v1.0 | TBD | Predictive Latent Drive Bottleneck (PyTorch) |
| v1.1 | TBD | Relational graph |
| v1.2 | TBD | Phase-linked life architecture |
| v2.0 | TBD | Narrative Witness Layer (interactive 체험) |
