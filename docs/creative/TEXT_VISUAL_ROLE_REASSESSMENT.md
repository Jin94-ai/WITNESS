# Text / Visual 역할 재평가 — Phase 5

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 5 + Phase 4 review의 `Phase 5 prep notes`
**Verdict**: **Case TV-A — Visual + Packet 중심으로 충분** → Phase 6 (Internal Demo Package v1) 즉시 진행 가능

---

## 0. 핵심 목적 (Lee §목표 verbatim)

> *"5분 안에 설명 가능한 내부 데모를 만들기 위해, 텍스트와 비주얼의 역할을 최종 정리한다. 핵심은 '텍스트를 더 개선할지'가 아니라, 데모에서 Visual / Packet / Story가 각각 어떤 역할을 맡아야 하는지 결정하는 것이다."*

→ 본 review는 *renderer 재개 검토*가 아니라 **각 layer의 역할 정의**.

---

## 1. Q1-Q4 답변

### Q1. 텍스트 story renderer를 재개할 필요가 있는가?

**A: 아니오 — 데모 v1에서 story text는 *선택*, *필수 아님*.**

#### 근거
- **Phase 4 Q6 검증**: visual + packet 조합이 text-only보다 나음 (peter 계열 ✅, vangogh △)
- **Phase 4 Q3 검증**: candidate 찾기 쉬움 (peter ✅, vangogh △ — 그러나 *기능 깨짐 아님*)
- **Phase 4 Phase 5 prep Q5-1 분석**: renderer 재개 가치는 *vangogh-style 조용한 anchor*에서만 부분적으로 의미 있음
- **현재 가용 자료**: `scripts/observer/render_candidate_story.py` (3-lens narration) 이미 작동 — *재개*가 아닌 *기존 자료 연결*만 필요

#### 세부 판단
- **Renderer full restart** = ❌ 불필요 (Lee plan §6 verbatim 일관)
- **Packet / static summary** = ✅ 충분
- **Story panel placeholder 유지 기간** = **Phase 6 데모 동안은 placeholder OK**, Phase 6 후 사용자 피드백 보고 결정
- **데모 v1에서 story text 필수 여부** = **선택**. 시연자(Lee)가 *특정 candidate에 대해 보충 설명할 때*만 CLI (`python examples/demo_observer_story.py --render-story <id>`)로 별도 호출

#### Caveat
- vangogh_sacred 같은 *story_ready 0 anchor*에서는 packet으로 *왜 이 anchor가 흥미로운지* 부족 — 그러나 본 한계는 *renderer 재개*가 아닌 *anchor 자체 특성 / curation rule 한계*로 분리

---

### Q2. Visual observer가 세계 흐름을 더 잘 보여주는가?

**A: 격동 anchor에서는 압도적, 조용한 anchor에서는 부분적.**

#### Anchor 별 Visual vs Text 비교

##### `peter_scarcity_baseline`

| 측면 | Visual 강 | Visual 약 |
|---|---|---|
| 200 ticks 동시 변화 | ✅ 5 score-3 marker 0.5초 식별 | — |
| L1 zone 색 변화 (12회 mode change) | ✅ 색 lane 직접 표시 | — |
| 4/12 dynamic agents | ✅ dot stroke + size 변화 visible | — |
| Cluster 식별 (15-25 / 142-147) | ✅ marker 분포 | — |
| 신호의 *의미* (예: authority_vigilance_spike 무엇인지) | — | ❌ packet 필수 |
| candidate의 *근거* (rationale) | — | ❌ packet 필수 |

→ **Visual 우세**. Text/packet은 *의미 보완* 역할.

##### `peter_scarcity_triple` cross-seed

| 측면 | Visual 강 | Visual 약 |
|---|---|---|
| Outcome distribution (REC 3/PARTIAL 1/SAT 1) | ✅ banner + 5 row 색 분포 0.5초 | — |
| seed별 score-3 timing 차이 (5/5/1/1/4) | ✅ marker visible per row | — |
| seed별 lane color ending | ✅ recovery 녹색 / saturation 빨강 | — |
| nonmonotonic finding | ✅ "REC 3 / SAT 1" 즉시 식별 | — |
| selector notes의 의미 ("more accusation → more recovery") | — | ❌ packet/text 필수 |
| seed별 candidate 분포 차이 (OO=0/2/1/2/2) | △ visual에 표시되지만 *해석*은 text 필요 | △ |

→ **Visual 압도** (configuration sensitivity 직관). Packet은 *seed별 detail* 보완.

##### `vangogh_sacred_baseline`

| 측면 | Visual 강 | Visual 약 |
|---|---|---|
| 조용한 흐름 (yellow only timeline) | ✅ peter와 비교 시 즉시 식별 | — |
| group lane 거의 정적 (mode change 1회) | ✅ 단조로운 배경 | — |
| 8 dots 거의 calm | ✅ visual 정보 밀도 낮음 | — |
| 사건 종류 차이 (miracle/prayer 등 sacred-specific) | — | ❌ active_events panel 필수 |
| story_ready 0의 *의미* | — | ❌ packet caveat 필수 |
| *왜 흥미로운지* | △ visual 단독 약함 | △ packet으로 보완 |

→ **Visual 부분 강** (조용함을 visual로 보여줌). Text/packet은 *왜 그것이 의미 있는지* 핵심 보완.

#### 종합
- **격동 anchor**: Visual 압도, Text 보조
- **운명 분기 (cross-seed)**: Visual 압도, Text 보조
- **조용한 anchor**: Visual + Text 균형 (Text 비중 ↑)

---

### Q3. 인물의 이야기 / 인물 간 이야기는 아직 별도 보강이 필요한가?

**A: v0.2 backlog로 분리. v0.1 필수 아님.**

#### 근거 분석

##### Person arc (인물의 이야기)
- **peter_scarcity_baseline**: 5 person candidates (`C01_t15`, `C02_t25`, `P03_t66_agent_08`, `C03_t142`, `C05_t147`) — V2-2 selected agent follow + Q1-Q4 person bucket 작동
- **vangogh_sacred_baseline**: person candidate **0개** (1/8 dynamic — anchor 특성)
- **현재 도구**: V2-2 agent follow + person lens narration (`render_candidate_story --lens person`)
- **결론**: peter에서는 **충분**, vangogh에서는 *anchor 자체*가 person arc 약함

##### Relation / Interaction (인물 간 이야기)
- **현재 candidate type**: person / event / world / mixed
- **relation/interaction bucket** *부재*
- **현재 도구**: `candidate.agents_involved` 필드에 *동시 발생 agents 목록*만 (관계 그 자체 표현 안 됨)
- **시간적 관계 추론**: timeline tick proximity로 *암시*만 가능

#### 판단
- **v0.1 필수**: ❌ 아님
  - Phase 4 Browsing Pack에서 *cohort_split / agent_state_shift* 신호로 *간접* 표현됨
  - Demo 5분 분량에서 relation candidate를 별도 강조할 시간 부족
- **v0.2 backlog**: ✅ 적합
  - Lee directive `docs/plan.md` Phase 5 §C "Interaction layer 필요" 분기 후보로 보존
  - 별도 directive 시 *relation candidate* 또는 *agent-pair lens* 추가 검토
- **사항**:
  - Lee §"bucket 추가 금지" 일관 — 본 LOOP에서 직접 추가 0
  - Phase 7 (Long-term Fork Decision)에서 *Interaction layer 필요한가*는 핵심 분기 (옵션 1 vs 4)

#### 결론
> Person arc는 anchor 특성에 따라 *현재 도구로 충분*. Relation/interaction은 v0.2 backlog로 분리, Phase 7 분기 결정에 위임.

---

### Q4. Sacred처럼 조용한 dynamics를 story_ready 0으로 둘 것인가?

**A: 그대로 두고 *다른 dynamics*로 인정. Sacred-specific 보강은 *별도 directive 필요*.**

#### 양 해석 검토

##### 해석 (a) — Story_ready 0 = 실패
- 사용자가 vangogh anchor 보고 "candidate가 없다 = 흥미롭지 않다"로 받아들임
- Curation rule이 sacred-blind로 판정
- → encoding 보강 필요

##### 해석 (b) — Story_ready 0 = 다른 dynamics
- Vangogh sacred는 *external pressure 없는 contemplative dynamics*
- 8 tag salience system이 *외부 충격* 위주로 설계됨 — sacred *내부 변화*는 score-2/3 trigger 못 함
- 그러나 *low_activity_hold 6개 candidate*은 *탐색 가능*한 후보로 보존
- → 시스템이 sacred 동학을 *적절히* 분류 (*"보류"*)

#### 결정: **해석 (b) 채택**

##### 근거
1. **Lee plan §6 verbatim**: "시스템은 좋은 이야기/나쁜 이야기를 자동 판정하지 않는다" — story_ready 0 = "render-ready 자동 판정 안 됨" → 사용자에게 *분류 정보 그대로 전달*
2. **관찰기 ≠ 평가기 원칙 일관**: low_activity_hold = "지금은 약하지만 tension seed가 있는 후보" (Q1-Q4 정의 verbatim) — 가치 있는 분류, 실패 표시 아님
3. **Lee §"sacred-specific metric 추가 금지"**: 본 LOOP에서 encoding 보강 금지
4. **Phase 4 Browsing Pack §C.3**: vangogh caveat을 *명시적으로 정직하게* 기록 → 사용자가 두 해석 모두 인지 가능

#### 데모 v1에서 다루는 방식
- Browsing pack §G "vangogh에서 candidate가 모두 회색" 자주 마주칠 질문에서 *정상 동작* 명시
- Demo script에서 vangogh 화면을 *"조용한 dynamics 예시"*로 시연 — 격동의 대비점

#### 향후 검토 (별도 directive 시)
- (i) Sacred-specific salience tag 추가 (예: `miracle_density`, `prayer_intensity`)
- (ii) 별도 bucket (예: `sacred_observation`)
- (iii) Story panel을 sacred에서만 *force-show* (renderer 재개 연계)
- 셋 다 *Lee §금지 항목* — 별도 directive 필요

---

## 2. Visual / Packet / Story 역할 분리

본 LOOP의 핵심 산출.

### 2.1 Visual

**역할**: *세계 흐름의 직관적 표시*.

#### 책임 (must show)
- **세계 흐름**: world tint (mood) + group zone (mode/tension)
- **시간 변화**: timeline cursor + Play/Pause + tick scrubbing
- **Seed별 운명 분기**: cross-seed small multiples (5 row outcome 분포)
- **Group / tension / salience 우선 표시**: timeline marker / zone radius / dot size

#### 보조 (nice to have)
- Agent dot stroke (salient 표시)
- Range overlay (selected candidate)

#### 명시적 비책임
- 신호의 *의미* 설명 → packet 영역
- 후보의 *서사* → story 영역 (선택)

### 2.2 Packet

**역할**: *왜 이 후보가 떠올랐는지의 설명*.

#### 책임 (must show)
- **WHY SURFACED**: rationale (한 문장)
- **SIGNALS**: tag chip 표시
- **CLASSIFICATION**: type / lens / use_mode
- **LOCATION**: tick + range + 폭

#### 보조 (nice to have)
- Related candidates (near-duplicate +N)
- Cross-seed outcome label (해당 seed의 운명)

#### 명시적 비책임
- 시각적 흐름 → visual 영역
- 사건 *전개의 서사* → story 영역 (선택)

### 2.3 Story

**역할**: *선택된 후보를 서사적으로 읽는 선택 출력*.

#### 책임 (when invoked)
- **3-lens narration**: person / event / world (`render_candidate_story.py` 기존 도구)
- **Lens-specific text**: person lens = focal agent 시간 변화 / event lens = 사건 ripple / world lens = 세계 metric 흐름
- **3-lens compare**: 같은 candidate를 다른 lens로 표현

#### v0.1에서 필수인지: **아님 (선택)**
- Demo v1에서는 *placeholder OK*
- Renderer 재개 0 (Lee §6 일관)
- 별도 CLI (`demo_observer_story.py --render-story`)로 *시연자가 필요할 때만* 호출

#### v0.2 backlog 후보
- Static precomputed story export (Lee §"renderer 재개 금지" 안에서 가능 — 기존 자료를 *static JSON*으로 export)
- Story panel actual content (Phase 4 Phase 5 prep Q5-1 검토 결과 = "정적 export로 충분")

---

## 3. Case TV 판정

### Case TV-A vs TV-B vs TV-C vs TV-D 평가

#### Case TV-A (Visual + Packet 중심으로 충분)
**조건 충족 여부**:
- Q1: ✅ Renderer 재개 불필요
- Q2: ✅ Visual이 핵심 흐름 보여줌 (peter 압도 / vangogh 부분)
- Q3: ✅ v0.1 필수 아님, v0.2 backlog
- Q4: ✅ story_ready 0 = 다른 dynamics (실패 아님)
- → **모든 조건 충족** ✅

#### Case TV-B (Story side panel에 static precomputed story만 필요)
**조건 충족 여부**:
- v0.1에서 *불필요* — TV-A로 진행 후 Phase 6 결과 보고 *별도 directive*로 검토 가능
- 즉시 plan 작성하면 *과한 사전 투자*

#### Case TV-C (텍스트 story 품질이 데모 병목)
**조건 충족 여부**:
- ❌ 적용 안 됨 — Q2 분석에서 visual이 *세계 흐름 보여주기*에 충분
- 텍스트 품질이 병목이라는 evidence 부재

#### Case TV-D (인물/관계 서사가 병목)
**조건 충족 여부**:
- ❌ Phase 4 + 5 평가 결과 *world/event/person/mixed 4 lens가 충분*
- Relation/interaction은 v0.2 backlog로 분리 (Q3 결정)

### 결정: **Case TV-A — Visual + Packet 중심으로 충분**

**근거 종합**:
1. Q1-Q4 모든 답변이 TV-A 일관
2. Phase 4 Browsing Pack 5/6 success가 TV-A의 *외부 evidence*
3. TV-B (static precomputed)는 *과한 사전 투자* — Phase 6 후 검토
4. TV-C/TV-D는 *직접 evidence 없음*
5. 데모 v1 5분 budget 안에 TV-A 충분 (Q2 visual 압도)

→ **Phase 6 (Internal Demo Package v1) 즉시 진행 가능**.

---

## 4. 5분 데모 목표 기준 결론

### Q. 5분 안에 WITNESS를 설명할 때 반드시 보여줘야 할 화면 3개는 무엇인가?

**A: 다음 3 화면 (각 ~1.5분 + 도입/마무리 0.5분)**:

#### 화면 1 — `peter_scarcity_baseline` Single-run (~1.5분)
- 진입: explorer.html → default
- 강조 포인트:
  - **Timeline의 score-3 5개 빨간 marker** (즉시 식별)
  - 도트 + group zone 색 변화 (L1 saturation → recovery)
  - Candidate panel "story_ready 5"
- **메시지**: *"세계가 흐르고, 어디가 중요한지 visual로 보인다."*

#### 화면 2 — `peter_scarcity_triple` Cross-seed (~1.5분)
- 전환: anchor dropdown → triple, view toggle → cross-seed
- 강조 포인트:
  - **Outcome banner** "REC 3 · PARTIAL 1 · SAT 1" (nonmonotonic)
  - 5 row lane 색 분포
  - Seed 0 vs Seed 3 클릭 → seed별 candidate 분포 차이
- **메시지**: *"같은 config가 어떤 운명들을 낳는지 (configuration sensitivity)."*

#### 화면 3 — `vangogh_sacred_baseline` Single-run (~1.5분)
- 전환: anchor dropdown → vangogh
- 강조 포인트:
  - **Timeline yellow only** (격동 anchor와 대비)
  - Group lane 정적 / dots 모두 calm
  - Candidate 6 모두 low_activity_hold (회색)
- **메시지**: *"다른 scenario family는 다른 dynamics. 시스템이 자동 판정하지 않는다 — 사용자가 분류 정보 보고 판단."*

### Q. 데모에서 story text가 없어도 설명 가능한가?

**A: ✅ Yes**. 3 화면 모두 visual + packet으로 충분히 설명 가능.

### Q. 데모에서 story text가 있다면 어느 순간에만 필요한가?

**A: 시연자(Lee)가 *특정 candidate*에 대해 *서사 흐름*을 보충 설명할 때만**. 예:
- 화면 1에서 `C03_t142` 클릭 후 "이 후보는 saturation cluster의 핵심"이라고 설명할 때
- 화면 3에서 `E02_t100_public_denial` (sacred pressure) 클릭 후 "sacred context에서 발생한 denial은 다른 의미"라고 설명할 때
- → CLI로 별도 호출: `python examples/demo_observer_story.py --render-story C03_t142 --lens person`
- → *데모 흐름 안에 통합 안 됨, 시연자 백업 도구*

### Q. 현재 상태에서 Phase 6으로 넘어가도 되는가?

**A: ✅ Yes**.

근거:
1. Case TV-A 판정 — 모든 4 sub-question이 TV-A 일관
2. 5분 데모 3 화면이 *현재 explorer.html*로 충분
3. Story text 부재가 *블로커 아님*
4. Phase 4 Browsing Pack v1 = 10-12분 budget — Phase 6은 *5분 압축 버전* (분량 가능)
5. Lee plan §"GLOBAL FORBIDDEN" 11 항목 모두 *현재 상태 유지로 준수*

---

## 5. Phase 6 준비 메모 (3 doc bullets)

### 5.1 `docs/demo/INTERNAL_DEMO_PACKAGE_V1.md` 후보 내용

- **목적**: 5분 내부 데모 시연 packaging
- **대상 사용자**: Lee 본인 (내부) + 잠재적으로 이해관계자 1-2명 (manual demo)
- **3 화면 시나리오**:
  - 화면 1: peter_baseline (격동의 기본)
  - 화면 2: peter_triple cross-seed (configuration sensitivity)
  - 화면 3: vangogh (다른 dynamics)
- **데모 환경**:
  - HTTP server 실행
  - 데이터 export 사전 완료 확인
  - explorer.html 접속
- **5분 흐름** (탑다운):
  1. 0:00-0:30 — 도입 ("WITNESS = 도트 기반 세계 관찰 + 후보 발견")
  2. 0:30-2:00 — 화면 1 (peter_baseline)
  3. 2:00-3:30 — 화면 2 (peter_triple cross-seed)
  4. 3:30-5:00 — 화면 3 (vangogh) + 마무리
- **백업 도구** (옵션):
  - `python examples/demo_observer_story.py --render-story <id>` (특정 candidate 서사 보충)
  - `python examples/demo_observer_story.py --packet <id>` (full packet text)

### 5.2 `docs/demo/DEMO_SCRIPT_V1.md` 후보 내용

- **5분 시연 대본** (시간 + 화면 + 말 + 클릭)
- **각 화면별 강조 포인트** (sec 단위)
- **자주 묻는 질문 (FAQ) 핸들링**:
  - "Story text가 없는데?" → "Visual + packet이 핵심. 서사는 별도 CLI."
  - "vangogh가 너무 조용해 보임" → "다른 scenario family. 시스템은 자동 판정 안 함."
  - "5 seeds로 충분한가?" → "통계 아닌 *configuration sensitivity 시연*."
- **시연자 cheat sheet** (단축키 / candidate ID / tick 번호)

### 5.3 `docs/demo/KNOWN_LIMITATIONS_V1.md` 후보 내용

- **Single-seed bias**: peter_baseline + vangogh 모두 seed=0 only
- **Sacred encoding**: vangogh score-2/3 marker 0개 (8 tag system이 sacred-blind)
- **Story panel placeholder**: 의도된 한계 (renderer 재개 금지)
- **Person candidate vangogh 0**: anchor 특성, fix 어려움
- **Cross-seed 단일 anchor**: peter_triple만 cross-seed 수행
- **Relation / Interaction candidate 부재**: v0.2 backlog (Phase 7 fork decision 대상)
- **5 seeds 통계 한계**: nonmonotonic finding은 *시연*이지 *증명 아님*
- **Mobile / tablet viewport 미검증**: desktop 800×500 가정

---

## 6. Phase 5 stop rule (Lee plan.md §GLOBAL STOP RULE)

1. **산출물 요약**: 본 doc 1개 (`TEXT_VISUAL_ROLE_REASSESSMENT.md`)
2. **성공/실패 판정**: ✅ **Case TV-A 성공**
3. **다음 Phase로 갈지**: ✅ Phase 6 (Internal Demo Package v1) 진행 가능
4. **새 기능 추가 안 했는지**: ❌ 추가 0 (코드 변경 0, doc 1개만)
5. **Forbidden 위반 여부**: ❌ 0건 (9 금지 항목 모두 미수행)

---

## 7. HARNESS 적용

### What I did NOT verify
- *실제* 5분 데모 시연 (Phase 6에서 검증)
- 사용자(Lee)가 본 review 결정에 동의하는지
- Demo 시연 시 청중 이해도

### What could still be wrong
- "Visual + packet 충분"이 **self-evaluation**일 뿐 — 실제 청중 reaction 다를 수 있음
- vangogh 화면이 *데모에 포함 적합한지*는 *Lee 판단* 필요 (사람에 따라 "조용한 anchor가 데모에 도움이 안 된다" 가능)
- 5분 budget이 *현실적*인지는 사용자 시연 후 검증

### Alternate interpretations
- (a) Case TV-A 충분 → Phase 6 (이번 결과)
- (b) 사용자가 vangogh를 데모에서 빼고 싶을 수 있음 → 2 anchor 데모 (peter baseline + cross-seed) 4분으로 압축 가능
- (c) Case TV-B static export가 *데모 매끄러움*에 가치 있음 → Phase 6 진행 후 *별도 directive*로 검토

→ 본 review (a) 선택. (b)/(c)는 Phase 6 *시연 결과 보고* 결정.

---

## 8. Lee 9 금지 항목 준수

| 금지 항목 | 준수 |
|---|:---:|
| 코드 수정 | ✅ doc 1개만, 코드 0 변경 |
| story renderer 재개 | ✅ |
| 새 visual 기능 | ✅ |
| sacred-specific metric 추가 | ✅ |
| bucket 추가 | ✅ |
| new anchor 추가 | ✅ |
| React / 3D / 캐릭터 / animation | ✅ |
| player intervention | ✅ |
| visual polish | ✅ |

---

## 9. 한 줄 요약

> **Phase 5 = Visual / Packet / Story 역할 정의. Q1-Q4 모두 TV-A 일관 (renderer 재개 불필요 / visual이 격동 anchor 압도 / 인물·관계 서사는 v0.2 backlog / sacred story_ready 0은 다른 dynamics 인정). 5분 데모 3 화면 (peter_baseline / peter_triple cross-seed / vangogh) — visual+packet only로 충분, story text 시연자 백업 도구. Case TV-A 성공 → Phase 6 (Internal Demo Package v1) 즉시 진행 가능. 코드 0 변경, Lee 9 금지 항목 모두 준수.**

---

**Versioning**: v1 (this reassessment) — 2026-04-30 Phase 5 완료. Case TV-A.
