# WITNESS Demo Script v1 — 5분 시연 대본

**Date**: 2026-04-30
**Source**: `INTERNAL_DEMO_PACKAGE_V1.md` §4 5분 흐름
**Format**: `[시간] / [화면] / [클릭/조작] / [말할 내용]`
**Target duration**: **5분** (4:30 ~ 5:30 허용 범위)

---

## 0:00 ~ 0:30 — 도입 (한 줄 소개)

| 시간 | 화면 | 클릭 | 말할 내용 |
|---|---|---|---|
| 0:00 | (브라우저 explorer.html 진입 화면) | 없음 | "이건 WITNESS라는 프로젝트의 5분 데모입니다." |
| 0:10 | (동일) | 없음 | "한 줄로 요약하면 — **WITNESS는 텍스트 이야기 생성기가 아니라, 움직이는 세계를 도트 기반으로 관찰하고 그 안에서 이야기 후보를 발견하는 world simulation explorer입니다.**" |
| 0:25 | (동일) | 없음 | "지금부터 3 화면으로 보여드리겠습니다. 첫째 — 격동의 기본." |

---

## 0:30 ~ 2:00 — 화면 1: peter_scarcity_baseline

| 시간 | 화면 | 클릭 | 말할 내용 |
|---|---|---|---|
| 0:30 | Single-run view (default) | 없음 (이미 로드됨) | "이건 베드로의 일기 — 1 accusation, 200 ticks, 12명 agents. 화면을 보세요." |
| 0:40 | (동일, 시선을 timeline-bar로) | timeline-bar의 빨간 marker hover | "**timeline 아래쪽에 빨간 굵은 marker가 5개 있습니다**. 이게 시스템이 잡은 *중요한 순간*. 200 ticks 중 단 5개." |
| 1:00 | (동일) | 첫 번째 빨간 marker (tick 15) 클릭 | "tick 15로 jump. **검은 cursor**가 거기로 갑니다. 도트 색이 변하고, group zone 색이 변하는 게 보이죠." |
| 1:15 | (동일, 우측 candidate panel로 시선) | filter row 보여주기, "story_ready 5"  | "오른쪽 candidate panel — 시스템이 큐레이션한 후보 8개 중 **5개가 story_ready**. 클릭 한 번에 순회 가능." |
| 1:30 | (동일) | C03_t142 카드 클릭 | "tick 142로 점프. **파란 반투명 직사각형**이 timeline에 표시됩니다 — 이 후보가 걸친 구간." |
| 1:45 | (우측 packet panel로 시선) | 없음 | "왼쪽이 *visual*, 오른쪽이 *packet* — '왜 이 후보인지'를 설명. rationale + signals + classification 6 sections." |
| 1:55 | (동일) | 없음 | "여기까지가 *격동의 기본*. 다음은 — 같은 anchor가 어떤 운명들을 낳을 수 있는지." |

---

## 2:00 ~ 3:30 — 화면 2: peter_scarcity_triple cross-seed

| 시간 | 화면 | 클릭 | 말할 내용 |
|---|---|---|---|
| 2:00 | Anchor dropdown 보여주기 | dropdown → `peter_scarcity_triple` 선택 | "anchor를 *3 accusations* cell로 바꿉니다. 같은 시나리오, 더 많은 사건." |
| 2:10 | view toggle 보여주기 | view → `Cross-seed` 클릭 | "view를 *cross-seed*로 전환. 5 seeds를 한 화면에서 봅니다." |
| 2:20 | Cross-seed view 로드됨 | 상단 banner 가리키기 | "위에 outcome banner. **REC 3 · PARTIAL 1 · SAT 1**. 같은 config, 같은 parameters인데 — *seed만 다른데* outcome이 갈라집니다." |
| 2:40 | (동일, 5 row로 시선) | 없음 | "각 row가 1 seed. 배경 lane 색이 *각 seed별 다른 운명*을 보여줍니다. **녹색 = recovery**, **빨간 = saturation**, **회색 = partial**." |
| 3:00 | (동일) | seed 0 row 클릭 | "seed 0 클릭 — REC 5개 candidate 활성." |
| 3:10 | (동일) | seed 3 row 클릭 | "seed 3 클릭 — SAT, score-3 marker 1개뿐. *큰 외부 충격 없이 점진 누적*으로 SAT 진입한 사례." |
| 3:25 | (동일) | 없음 | "이게 **configuration sensitivity**입니다. 5 seeds로 *통계 증명*을 하는 게 아니라 — **시연**입니다. 같은 anchor가 어떤 운명들을 낳을 수 있는지." |

---

## 3:30 ~ 4:40 — 화면 3: vangogh_sacred_baseline

| 시간 | 화면 | 클릭 | 말할 내용 |
|---|---|---|---|
| 3:30 | Anchor dropdown | dropdown → `vangogh_sacred_baseline` 선택 | "이번에는 완전히 다른 시나리오 — 반 고흐의 sacred 시나리오. cross-seed view 자동 disabled (single-run만 export됨)." |
| 3:45 | Single-run view 자동 전환 | 없음 (자동) | "**timeline을 보세요. 빨간 marker가 0개**. 노란 marker만 가득 — 시스템이 잡은 *큰 순간 0개*." |
| 4:00 | (동일, group zone 보여주기) | 없음 | "group zone도 거의 정적. agent 8명, 거의 모두 calm. **격동이 없는 흐름**." |
| 4:15 | 우측 candidate panel | filter row "story_ready" 가리키기 | "candidate panel — **story_ready 0개**. 모두 6개가 회색 (low_activity_hold). 시스템이 *이 시나리오는 보류*로 분류." |
| 4:25 | (동일) | 없음 | "**중요**: 이건 *실패*가 아닙니다. **다른 dynamics**. WITNESS는 *좋은 이야기/나쁜 이야기를 자동 판정하지 않습니다*. 분류 정보를 사용자에게 그대로 전달." |

---

## 4:40 ~ 5:00 — 마무리 (3 layer 역할 정리)

| 시간 | 화면 | 클릭 | 말할 내용 |
|---|---|---|---|
| 4:40 | (vangogh 화면 유지) | 없음 | "지금까지 본 3 layer를 정리합니다." |
| 4:45 | (동일) | 없음 | "**Visual** = 세계 흐름을 먼저 보여줍니다. timeline / lane / outcome 분포." |
| 4:50 | (동일) | 없음 | "**Packet** = 왜 이 후보인지 설명합니다. rationale + signals." |
| 4:55 | (동일) | 없음 | "**Story** = 선택된 후보를 서사적으로 읽는 *선택* 출력입니다. v0.1에선 placeholder — *별도 CLI 도구*로 호출 가능." |
| 4:58 | (동일) | 없음 | "Visual + Packet만으로 *대부분 충분*했죠. 이게 v1의 결론입니다." |
| 5:00 | (동일) | 끝 | (마무리) |

---

## 추가 설명 핸들링 (FAQ)

데모 흐름 *안*에는 들어가지 않지만, 청중 질문 시 사용:

### Q. "story text가 없는 거 같은데?"
**A**: "Visual + Packet으로 *세계 흐름*과 *후보 식별*까지는 충분합니다. 후보의 *서사 흐름*이 필요하면 별도 CLI 도구가 있어요 — `python examples/demo_observer_story.py --render-story <id>`. 데모에서는 *visual 중심 메시지*가 주이라서 통합 안 했습니다."

### Q. "vangogh가 너무 조용한데, 흥미로워 보이지 않아."
**A**: "그게 바로 핵심입니다. WITNESS는 *좋은 이야기/나쁜 이야기를 자동 판정하지 않습니다*. peter scarcity 같은 격동 시나리오와 vangogh sacred 같은 contemplative 시나리오는 *다른 dynamics*인데, 시스템이 *둘 다 분류 정보로* 보여줘야 사용자가 판단할 수 있죠. story_ready 0이라는 것 자체가 정보입니다."

### Q. "5 seeds로 통계가 충분한가?"
**A**: "**통계 증명이 아니라 시연**입니다. 같은 anchor + 같은 config가 *어떤 운명들을 낳을 수 있는지*를 보여주는 *configuration sensitivity 시연*. 5 seeds는 한 화면 안에서 *대조 가능한 최대치*에 가깝습니다. 통계적 generalization은 별도 paper-grade 연구 영역."

### Q. "이걸 누가 쓰는 거야?"
**A**: "**Internal tool**입니다. 현재는 *내부 점검* + *프로젝트 직접 관계자 1-2명 manual 시연*이 대상. Public product 아닙니다 (UI / 안내문 부족). 향후 fork decision에서 *어디로 확장할지*는 별도 결정."

### Q. "intervention / what-if는 안 되나?"
**A**: "**관찰자 모드 only**입니다. 현재 v0.2에서 intervention은 명시적으로 차단됨 (Lee directive). 향후 fork 결정에서 *playable prototype* 방향이 선택되면 그때 검토합니다."

### Q. "engine 자체는?"
**A**: "Engine은 별도 검증 layer가 있습니다 — 1845 fast tests, ABSOLUTE Rule #1/#6 준수, paper-grade evidence (configuration sensitivity within-scenario). 이 데모는 *Visual layer*만 보여주고, engine evidence는 별도 자료입니다."

---

## 시연자 cheat sheet

### 단축키
- 타임라인 정밀 이동: **← / →** (single-run view에서만)
- (Play / Pause / Slider는 마우스만)

### Candidate ID 빠른 참조

#### peter_scarcity_baseline (story_ready)
- `C01_t15` (tick 15, person, 첫 번째 score-3)
- `C02_t25` (tick 25, person, early saturation)
- `P03_t66_agent_08` (tick 66, person, +2 related)
- **`C03_t142`** (tick 142, person, accusation pressure — *데모에서 클릭*)
- `C05_t147` (tick 147, person, +1 related)

#### peter_scarcity_triple cross-seed
- **seed 0** (REC, SR=5) — *데모에서 클릭*
- seed 1 (REC, SR=5)
- seed 2 (PARTIAL, SR=2)
- **seed 3** (SAT, SR=4, score-3=1) — *데모에서 클릭, 조용한 SAT 사례*
- seed 4 (REC, SR=4)

#### vangogh_sacred_baseline (low_activity_hold only)
- `W01_t50` (tick 50, world, accusation pressure)
- `E02_t100_public_denial` (tick 100, event, **sacred pressure**)
- `E03_t126_public_confession` (tick 126, event)

### Score-3 빨간 marker 위치 (데모 강조)

| Anchor | Score-3 ticks |
|---|---|
| peter_baseline | 15, 25, 142, 146, 147 |
| peter_triple seed 0 | 15, 25, 142, 146, 147 |
| peter_triple seed 1 | 15, 35, 175, 176, 177 |
| peter_triple seed 2 | 15 (only) |
| peter_triple seed 3 | 15 (only) |
| peter_triple seed 4 | 15, 29, 30, 172 |
| vangogh | (없음 — 모두 score-1) |

### Outcome banner 키워드
- **REC 3 / PARTIAL 1 / SAT 1** (peter_triple cross-seed) — nonmonotonic
- (selector 메모 verbatim: *"더 많은 accusation → 더 많은 recovery (counterintuitive)"*)

### 자주 헷갈리는 것
- ❌ "story 후보 5개" → ✅ "**story_ready** 후보 5개" (use_mode 명시 중요)
- ❌ "evidence" → ✅ "**시연**" (configuration sensitivity 강조 시)
- ❌ "안 좋은 시나리오" → ✅ "**다른 dynamics**" (vangogh 설명)

---

## 시간 압축 옵션 (4분)

청중 시간 압박 시 *2 화면 모드*:
- 0:00-0:30 도입
- 0:30-2:00 화면 1 (peter_baseline)
- 2:00-3:30 화면 2 (peter_triple cross-seed)
- 3:30-4:00 마무리 — vangogh 언급만 (*"sacred는 다른 dynamics, 별도 자료"*), 화면 전환 안 함

→ 단점: vangogh의 *조용한 dynamics* 메시지 누락. *Lee plan §6 verbatim*과 부합 안 함 가능.

→ 권장: **5분 풀 버전 그대로 진행**. 시간 압박이면 도입 / 마무리만 단축.

---

## 시간 확장 옵션 (7-10분)

청중 깊은 관심 시 추가 가능:
- 화면 1에서 V2-2 selected agent follow 시연 (agent dot 클릭 → tick 이동하며 panel 갱신)
- 화면 2에서 5 seeds 모두 클릭 (분포 detail)
- 화면 3에서 active events 비교 (peter vs vangogh sacred-specific)
- CLI 백업 도구 1개 시연

→ 단점: 5분 budget 초과. 시연자 판단.

---

## 한 줄 요약

> **5분 / 3 화면 / 한 가지 메시지: world simulation explorer.**

---

**Versioning**: v1 (this script) — 2026-04-30 Phase 6 시연 대본.
