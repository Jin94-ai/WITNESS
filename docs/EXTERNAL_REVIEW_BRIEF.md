# WITNESS — External Review Brief

> **이 문서를 다른 AI 모델에게 *그대로 붙여넣어* 점검받기 위한 self-contained brief**.
> 외부 AI는 파일 시스템 접근 불가 가정. 핵심 산출물은 본문에 verbatim 포함.
> 마지막 갱신: 2026-05-06 (Story Emergence Phase A-F 완료 후).

---

## 0. 검토 요청 (한 문단)

이 프로젝트는 *World-first Narrative Mining Engine*을 표방한다 — 압력 기반 다중 에이전트 시뮬레이션을 돌리고, 그 안에서 발생하는 변화를 연결해 *여러 서사 후보*를 채굴한다. **이전 검토 시점**에서 "이야기 수준이 아니다 (generic logline + 익명 ID)"라는 한계가 인정됐고, 그 후 *Story Emergence Phase A-F* 도입으로 **named characters + conflict-tuned premises + cross-seed robustness** 추가됨. 5 layer + 2,026 fast tests + 5-seed × full pipeline cross-seed 분석 (6/6 robust patterns / 0 anomaly). 외부 검토자에게 묻고 싶은 것: (a) 새로 추가된 *named candidate + cross-seed* layer가 portfolio claim을 *얼마나* 강화했나? (b) "이야기 수준"에 *얼마나 더 가까워졌나*? (c) 다음 단계 우선순위. **§8의 7개 질문에 답해주면 된다.**

---

## 1. 프로젝트 정의

**한 줄**: WITNESS는 압력 기반 다중 에이전트 시뮬레이션을 구동한 뒤, 그 안에서 발생하는 인물 변화 / 관계 변화 / 집단 긴장 / 갈등 누적을 연결해 *여러 서사 후보를 채굴*하는 시스템이다.

**의도된 입출력**:

```
입력: 시뮬레이션 dump (200 ticks × N agents × 압력 / 상태 / 이벤트)
   ↓
중간: Moment(변화 단위) → MomentLink → StoryThread(연결된 변화) → NarrativeOpportunity(창작용 카드)
   ↓
출력: 정적 HTML 콘솔 + Markdown 카드 + JSON ledger
       (창작자가 "어느 thread를 가져다 쓸지" 고를 수 있는 형태)
```

**의도적 *비*포지셔닝**:
- ❌ 한 인물 이야기 하드코딩 엔진
- ❌ 정해진 플롯 재생 스토리 렌더러
- ❌ AI 소설 자동 생성기
- ❌ 픽셀 월드 / 컷신 시각화

**도메인 콘텐츠**: 베드로 (예수의 마지막 50일) / 반 고흐 / 탈레랑 — 모두 `content/` 디렉토리에 분리. `engine/`은 인물 비종속 (`grep -r "peter\|Peter\|베드로" engine/` 결과 0건 자동 검증).

---

## 2. 5-Layer 아키텍처

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 5: Visual (frozen, audit instrument만 active)              │
│  pixel_world / scene_director / event_playback / world_flow      │
├──────────────────────────────────────────────────────────────────┤
│ Layer 4: Narrative Mining + Story Emergence (현재 메인)           │
│                                                                  │
│  Stage 1-4 (Moment → Link → Thread → Opportunity):               │
│   → docs/portfolio/NARRATIVE_OPPORTUNITIES.md                    │
│   → docs/portfolio/narrative_mining_console.html (56KB)          │
│                                                                  │
│  Stage 5 (Identity / Group / Pressure resolver):                 │
│   → content/anchors/{anchor_id}/identity_map.json (옵션)         │
│   → archetype fallback (매핑 없을 때)                            │
│                                                                  │
│  Stage 6 (StoryCandidate + TurningPoint, 18 fields):             │
│   → docs/portfolio/STORY_CANDIDATES.md (4 named cards)           │
│   → data/narrative/story_candidates.json                         │
│                                                                  │
│  Stage 7 (Cross-seed + Console):                                 │
│   → docs/portfolio/CROSS_SEED_STORY_PATTERNS.md (5 seeds)        │
│   → docs/portfolio/story_candidate_console.html (23KB)           │
├──────────────────────────────────────────────────────────────────┤
│ Layer 3: Reporting (Story Emergence 입력 surface)                 │
│  Observer dump → Markdown brief + 160-row provenance table       │
├──────────────────────────────────────────────────────────────────┤
│ Layer 2: Observation + Curation                                  │
│  4 lens + candidate extraction + 3-bucket curation               │
├──────────────────────────────────────────────────────────────────┤
│ Layer 1: Engine                                                  │
│  Hazard-driven multi-agent + Pydantic state                      │
│  → deterministic per seed                                        │
└──────────────────────────────────────────────────────────────────┘
```

**Additive 원칙**: 위 layer는 아래 layer를 *수정하지 않는다*.

**Provenance class** (모든 layer 산출물에 적용):
- `source_derived` — observer raw field
- `source_inferred` — bounded rule applied to source signals
- `not_used` — visual staging field (명시적 제외)
- `staged_only` — visual track 한정, hand-authored

---

## 3. 현재 실측 수치

| 항목 | 값 |
|---|---|
| Engine fast tests | **2,026 passing** (deterministic per seed) |
| Visual tests | 72 passing (frozen, regression guard만) |
| Report tests (Phase 11-12) | 19 passing |
| Narrative tests (Phase 1-5) | 69 passing |
| Story Emergence tests (A-F) | 33 passing (10 identity + 16 candidate + 7 cross-seed) |
| Total | ~2,180 (slow + archived 포함) |
| External dependencies (runtime) | **0** (vanilla Python + Markdown + Canvas) |
| Mining console size | 56 KB self-contained HTML |
| Story candidate console size | 23 KB self-contained HTML |
| Engine throughput | ~1,000–1,300 ticks/sec |

**Pipeline 결과 (peter_scarcity_baseline)**:
```
105 moments   (50 agent_state_shift + 36 world_pressure_shift +
               12 group_tension_shift + 6 unresolved_thread + 1 conflict_marker)
1,727 links   (5 link types: same_agent / same_group / same_pressure /
               same_conflict_axis / temporal_continuity)
4 threads     (1 strong score 0.802, 3 weak)
4 narrative opportunities
```

**Cross-anchor 검증** (동일 builder, 입력만 교체):
| Anchor | Agents | Moments | Threads | Strongest |
|---|---|---|---|---|
| peter_scarcity_baseline | 12 | 105 | 4 | strong (0.80) |
| peter_scarcity_triple | 12 | 99 | 4 | strong |
| vangogh_sacred_baseline | 8 | 16 | 1 | weak |

→ Quiet scenario(반 고흐)는 fewer moments → fewer threads. 정직한 generalization.

**Cross-seed robustness** (peter_scarcity_baseline × 5 seeds × full pipeline):

| Pattern | Frequency | Robustness |
|---|---|---|
| `uncertainty_vs_commitment` | 5/5 | **robust** |
| `loyalty_vs_survival` | 4/5 | **robust** |
| `Peter` (main char) | 5/5 | **robust** |
| `John` (main char) | 5/5 | **robust** |
| `Andrew` (main char) | 5/5 | **robust** |
| `James` (main char) | 5/5 | **robust** |
| Total: 6 patterns / robust=6 / **anomaly=0** | | |

→ *Narrative structure가 seed-stable*. 같은 anchor에서 5 seeds 모두 동일 4 main + 동일 2 conflict family produce. 이는 *우연이 아닌 세계 구조 자체*가 narrative 패턴을 결정한다는 직접 증거. **Phase E 도입의 핵심 portfolio claim**.

---

## 4. Pivot trajectory (왜 이 모양이 됐나)

```
[Phase 1-10] Engine + Observer + Curation 안정화 (1,800+ tests)
   ↓
[Phase 1-7 visual]
   ├ Pixel World Static V1/V2  → PW-S2-C (test-grid 인상)
   ├ Pixel Scene Director       → PW-SC-B (static 한계)
   ├ Pixel Event Playback (PEP) → VT-B  ← audit이 27.9% staged-only 측정 → freeze
   ├ World Flow Observer (WFO)  → WFO-A (100% source-backed but viewer-less)
   └ WFO Polished Viewer        → freeze (5초 사용성 테스트 fail)
   ↓
[중간 결정] Visual track의 *진짜 산출물*은 viewer가 아니라
            *audit instrument* (provenance class vocabulary)였다는 회고
   ↓
[Phase 11-13 text-first]
   ├ Observer Brief (auto-generated Markdown)
   ├ 160-row Provenance Table (.md + .json)
   └ Portfolio package (case study + 5min demo + resume bullets)
   ↓
[중간 진단] 단일 brief가 "사건 후보"는 잡지만 "이야기 축적"은 못 보여줌
   ↓
[Phase 1-5 narrative mining (현재)]
   ├ Moment extractor (5 families, deterministic)
   ├ Moment linking (7 link types, agent-centric mining)
   ├ Story Thread builder (8 score factors, conflict/arc 추론)
   ├ Narrative Opportunity export (creator-facing card)
   └ Static HTML console (self-contained 56KB)
```

**핵심 framing claim**:
> *"Visual track 5주가 audit instrument를 만들었고, 그 instrument가 visual을 freeze하고 text brief를 ship할 권한을 줬다. Text brief의 Moment 추출이 Story Thread mining을 가능하게 만들었다. Pivot은 retreat이 아니라 **방법론 추출**."*

---

## 5. 핵심 산출물 발췌 (verbatim)

### 5.1 Observer Brief 한 candidate card (Layer 3)

```
### C01_t15 — tick 15 (range 13–17)

One-line: story_ready candidate surfaced via authority_vigilance_spike,
cohort_split, agent_state_shift on lens person (salience 3).

What happened (source-derived)
- 12 agents in scope at tick 15
- Active events: guard_approaches, discussion_emitted, public_denial,
  visible_withdrawal, discussion_emitted
- World mood across window: agitated → agitated → agitated → agitated → agitated

World snapshot at tick
- crowd_mood: agitated
- blame_concentration: 0.280
- public_suspicion: 0.150
- authority_vigilance: 0.250

Group state at tick
| group | mode          | tension | members |
| L1    | partial       | 0.539   | 4       |
| L2    | low_activity  | 0.100   | 4       |
| L3    | low_activity  | 0.100   | 4       |

Focal agent state (sample)
| agent_03 | L1 | fragmenting | fear 8.73 | hope 4.00 | salient ★ |
| agent_05 | L3 | fragmenting | fear 8.30 | hope 4.00 | salient ★ |
| (10 others calm at fear 1.30)

Why story_ready (source-inferred)
- Rationale: Surfaced by authority_vigilance_spike, cohort_split,
  agent_state_shift
- Strongest lens: person
- Dominant pressure: none_clear
- Salience score: 3

Provenance
- Source-derived: tick / tick_range / agents_involved / events_involved /
  world / group / agent state at tick (raw observer fields)
- Source-inferred: rationale / signals / candidate_type / strongest_lens /
  salience_score / dominant_pressure / use_mode (rule outputs)
- Not used: synthetic guard movement / tile-grid positions /
  walking-frame timeline / hand-authored cutscene cues / speech-bubble staging
```

### 5.2 Story Candidate (Stage 6 / Phase B+C — *named characters*, post Iter 1)

```
## S01 — Loyalty Strained by Survival Pressure

> source thread: T01 · conflict: loyalty_vs_survival
> main: Peter · supporting / context: James, core disciples

### One-line premise

Peter tries to stay present as fear and public pressure slowly turn loyalty
into silence.

### Arc summary

fear intensifies → authority pressure closes in → shame relaxes →
fear eases → unresolved tension lingers

### Key turning points

| Tick | Label                       | Provenance      | Summary |
| 14   | sustained pressure begins   | source_derived  | Peter fear stays above 7.0 for 14 ticks (peak 10.00) |
| 15   | co-occurring pressure       | source_inferred | agents fear rises while authority_vigilance rises (co-occurrence at t=15) |
| 15   | world pressure shift        | source_derived  | world.authority_vigilance rises (+0.250) |

### Relationship dynamics

- Peter ↔ core disciples: sustained pressure on Peter while group co-presence
  persists (group context only).
- Peter ↔ James: parallel pressure shifts in authority_vigilance, fear
  (co-occurring within thread, not a directional relationship signal).

### Adaptation hooks

- film_scene:    A quiet scene where Peter stays physically present but
                 emotionally withdraws as authority pressure enters the room.
- novel_chapter: A chapter tracking the slow conversion of loyalty into
                 fear-driven silence.
- game_quest_branch: The player must choose to confess, hide, or stay silent
                     as public suspicion rises around Peter.

### Evidence

Built from 21 linked moments across 3 pressure type(s) and 4 moment type(s).
provenance: source_derived=20, source_inferred=1, not_used=0

### Risk notes

- No dialogue generated.
- No unstated event added.
- Premise is inferred from pressure pattern, not directly authored by the engine.
```

→ 동일 thread를 *Stage 6 enrichment* 후 view. agent_03 → "Peter" (identity_map.json
적용), generic logline → conflict-tuned premise, raw moment list → categorized
turning points. plan §10.2 forbidden tokens (대사 / 시나리오 슬러그 / 감정 narration) 0.

---

## 6. 핵심 코드 시그니처

### 6.1 Moment dataclass (frozen)

```python
MomentType = Literal[
    "agent_state_shift", "relationship_drift", "group_tension_shift",
    "world_pressure_shift", "choice_pattern", "conflict_marker",
    "event_ripple", "unresolved_thread",
]

@dataclass(frozen=True)
class Moment:
    moment_id: str
    tick: int
    tick_range: tuple[int, int]
    moment_type: MomentType
    agents: tuple[str, ...] = ()
    pressures: tuple[str, ...] = ()
    salience_score: float = 0.0
    provenance: ProvenanceClass = "source_derived"
```

### 6.2 Story Thread mining (agent-centric, NOT plain connected-components)

```python
def _mine_threads_by_agent(moments, links):
    """For each main agent, group their moments + bridge no-agent moments
    via same_pressure / same_conflict_axis links."""

# Why agent-centric: plain union-find collapses 105 moments into 1
# mega-component due to temporal_continuity links (634/1727). Tested
# explicitly. See lessons.md L56.
```

### 6.3 8 score factors (sum to 1.0)

```python
score = (0.20 * change          # max salience proxy
       + 0.15 * continuity      # tighter cluster → higher
       + 0.20 * conflict        # explicit conflict_marker bonus
       + 0.15 * relationship    # group_tension + multi-agent
       + 0.10 * pressure        # distinct pressure count
       + 0.10 * resolution_gap  # final unresolved_thread bonus
       + 0.05 * multi_agent     # ≥3 agents
       + 0.05 * creative_use)   # has agent + world + group layers
```

### 6.4 Conflict / arc inference (deterministic, no LLM)

```python
def _infer_core_conflict(component) -> str:
    if fear_up and (auth_up or sus_up):  return "loyalty_vs_survival"
    if tension_up and blame_up:           return "collective_fear_vs_scapegoating"
    if auth_up and sus_up:                return "control_vs_exposure"
    if hope_down and shame_up:            return "identity_vs_failure"
    # ... 8 conflict labels total

def _infer_arc_direction(component) -> ArcDirection:
    if fear_up and (shame_up or has_unresolved):  return "fear_to_withdrawal"
    # ... 7 arc labels + "unknown"
```

### 6.5 Logline / title / question — *deterministic templates per conflict*

```python
_TITLE_BY_CONFLICT = {
    "loyalty_vs_survival": "Loyalty Strained by Survival Pressure",
    "control_vs_exposure": "Authority Tightens as Suspicion Spreads",
    # ... 8 entries
}

_LOGLINE_BY_CONFLICT = {
    "loyalty_vs_survival":
        "Central agents stay in place under rising pressure until survival "
        "instinct begins to outweigh loyalty.",
    # ... 8 entries
}
```

→ **이 부분이 "이야기 수준이 아니다"의 핵심 원인**. §7 참조.

---

## 7. 정직한 한계 (본인 인정)

사용자가 직접 점검 후 "이야기가 나오는 수준이냐?"라고 물었고, 답변:

> **아니다. 이건 *이야기*가 아니라 *이야기 가능성 카드*다.**

| 결손 | 현 상태 |
|---|---|
| 캐릭터 이름 / 역할 | `agent_03` 익명 ID — content/peter/profile.json에 *이름은 있음*, narrative mining이 *안 씀* |
| 구체 사건 묘사 | "fear rises +1.57" 수치만, "경비병이 다가오자 두려움이 솟구쳤다"가 아님 |
| 장면 / 관계 컨텍스트 | tick 숫자만, 시간/장소/관계 0 |
| 극적 결정점 | 단순 변화 누적, 결정/전환/해소 구조 없음 |
| 자연어 logline | conflict family당 *하나의 고정 template* (모든 `loyalty_vs_survival`이 같은 문장) |

**이건 의도된 결과**: plan §14.4 "No Story Writing 원칙"이 명시적으로 "완성된 장면 대사 / 소설 본문 / 영화 시나리오 / 감정 과잉 서술 생성하지 말 것"을 금지함.

→ 즉 현 산출물은 *plan 의도대로 정확히 만들어짐*. 그러나 *plan의 의도*와 *사용자가 "이야기"라고 부를 때 기대하는 것* 사이에 gap이 존재함.

**다음 가능 layer (구현 안 함)**:
- B (low-cost): agent_id → 이름 매핑 (`agent_03 → peter`). content/에 데이터 있음. plan 위배 X.
- C (high-cost / plan 위배): 자연어 logline / 사건 묘사 / 장면 generation. story_renderer 회귀 위험.

---

## 8. 외부 AI에게 묻고 싶은 점 (7 questions)

답변은 가능한 *구체적*으로 — "그렇다 / 아니다 + 이유 + 대안"이 이상적.

### Q1. 5-layer 아키텍처가 정합한가, 또는 over-engineering인가?

특히 Layer 3 (Reporting)와 Layer 4 (Narrative Mining)가 *별개 layer로 분리될 가치*가 있는가, 아니면 합쳐야 하는가?

### Q2. "Audit instrument transfer" framing이 portfolio claim으로 강한가?

> *"Visual track의 audit instrument가 text brief의 정직성을 만들고, narrative mining의 모든 출력에도 같은 vocabulary가 적용된다 — 그래서 visual freeze는 retreat이 아닌 방법론 추출이다."*

이 framing이 면접 / 채용 / portfolio 검토에서 *살아남는* 메시지인가? 또는 후post-rationalization으로 들리나?

### Q3. **Stage 6 Story Candidate**가 portfolio impact를 *얼마나* 강화했는가?

§5.2의 *new* S01 카드 (named "Peter" + conflict-tuned premise + categorized turning points + cross-seed robustness)를 보고:

(a) 이전 generic logline 버전 대비 *얼마나* 강해졌나? "이야기 수준"에 가까워졌나?
(b) 그러나 plan §14.4가 forbidden한 *완성된 prose / dialogue / screenplay*는 여전히 안 만들어 — 이게 충분한가, 더 나아가야 하나?
(c) 만약 더 나아가야 한다면, 어떤 layer를 추가해야 (a) 정직성을 유지하며 (b) 진짜 "이야기"라고 부를 수 있는가?

### Q4. Story Thread mining이 *agent-centric*인 게 합리적인가?

원래 plan §5.1은 "connected component 또는 path 후보"를 제시. 실제 구현은 union-find가 mega-thread로 수렴해서 *agent-centric mining*으로 우회 (lessons L56). 이 결정이 합리적인가, 또는 더 나은 graph 알고리즘이 있는가?

### Q5. 8 conflict label + 8 arc label은 *임의적*인가?

```
loyalty_vs_survival, trust_vs_self_protection, collective_fear_vs_scapegoating,
control_vs_exposure, identity_vs_failure, uncertainty_vs_commitment,
atmosphere_vs_action, unknown
```

이 카테고리화가 (a) 다중 에이전트 시뮬레이션의 *natural* 갈등 분류인가, (b) 베드로 시나리오에 over-fit인가, (c) 다른 시나리오에 generalize 가능한가? Vangogh 시나리오에서 1 thread만 나온 게 (b) 증거인가, (c) 정직한 generalization인가?

**Q5b (cross-seed 결과 추가 질문)**: 5 seeds × peter_scarcity_baseline에서 6/6 robust patterns / 0 anomaly가 나왔다. 이것이 (a) 시뮬레이션이 *narrative-deterministic*임을 증명하는 강력한 portfolio claim인가, (b) anchor가 너무 strong해서 모든 seed가 같은 결과로 collapse하는 *문제*인가, (c) seed 5개가 너무 적어 통계적으로 의미 없는가? 외부 검토자의 통계적 직관 필요.

### Q6. 이 패키지로 *현재 수준*에서 어디에 지원 가능한가?

- AI / ML Engineer (LLM eval / RAG / agent system)
- Simulation Engineer (game AI / NPC system)
- AI Product
- 그 외?

각 직무별로 *강점이 어떻게 매핑되는가* + *부족한 부분이 무엇인가*.

### Q7. 다음 단계 우선순위 (이전 Q7의 A+C는 이미 완료 — 새 옵션)

이전 Q7에서 A (agent identity) + C (cross-seed)는 *모두 완료*. 새 옵션:

| 옵션 | 비용 | 가치 |
|---|---|---|
| **A. 외부 사용 (이대로 면접 / 지원)** | 0 | 외부 피드백 받고 우선순위 재조정 |
| **B. 자연어 enrichment (plan §14.4 위배 위험)** | 1-2주 + directive | 진짜 "이야기" 수준 — story_renderer 회귀 위험 |
| **C. cross-anchor portfolio doc** | 0.5d | 3 anchor (peter/triple/vangogh) Story Candidate 비교 — *익명 fallback도 작동함* 보강 |
| **D. Phase 14 visual revival** | 2-4주 + directive | narrative mining이 *덜 필요하게* 만들어 우선순위 *낮음* |
| **E. 이번 사이클로 종료** | 0 | 핵심 산출물 충분 — *over-engineering 영역* |

검토자 추천: **A / B / C / D / E 중 어느 것 + 이유?**

---

## 9. 부록 — 핵심 파일 위치 (외부 AI가 깊이 보고 싶을 때)

| 영역 | 경로 |
|---|---|
| 현 active plan | `docs/WITNESS_NARRATIVE_MINING_PLAN.md` |
| 이전 plan (visual freeze) | `docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md` |
| 30분 review | `docs/WITNESS_OVERVIEW.md` |
| 케이스 스터디 | `docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md` |
| 현 메인 산출물 (creator-facing) | `docs/portfolio/NARRATIVE_OPPORTUNITIES.md` |
| 현 메인 산출물 (UI) | `docs/portfolio/narrative_mining_console.html` (56KB) |
| Visual freeze 결정 | `docs/visual/VISUAL_TRACK_FREEZE_DECISION.md` |
| Phase 14 design notes | `docs/visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md` |
| 행동 강령 (HARNESS) | `docs/HARNESS.md` |
| Lessons (L1–L56) | `lessons.md` (L46-L55 visual cluster, L56 mega-component 회피) |

| 핵심 모듈 (Layer 4 Narrative Mining) | 경로 |
|---|---|
| Moment dataclass | `engine/observer/moment.py` |
| Moment 추출 (5 families) | `engine/observer/moment_extractor.py` |
| MomentLink + StoryThread dataclass | `engine/observer/thread.py` |
| 링크 + 스레드 빌더 | `engine/observer/thread_builder.py` |
| Narrative Opportunity 모델 | `engine/observer/narrative_opportunity.py` |
| 4 sequential CLI | `scripts/narrative/build_moments.py / build_story_threads.py / export_narrative_opportunities.py / build_mining_console.py` |

| 핵심 모듈 (Layer 3 Reporting) | 경로 |
|---|---|
| Brief builder | `scripts/report/build_observer_brief.py` |
| Provenance table builder | `scripts/report/build_provenance_table.py` |

---

## 10. 외부 AI에게 — 응답 형식 제안

이상적인 응답:

```
Q1: [yes/no] — [이유, 1-2 문장]. [대안 또는 보강 제안].
Q2: [strong/weak/post-rationalization] — [이유]. [대안 framing].
Q3: ...
...

종합 평가:
- 가장 강한 점: [...]
- 가장 약한 점: [...]
- 권장 다음 단계: [Q7 옵션 A/B/C/D 중] — [이유]
- portfolio 사용 가능 직무: [...]
- 보류해야 할 직무 또는 framing: [...]
```

검토자에게 부탁:
- *친절함보다 정직함*. 약한 부분은 약하다고 말해도 된다.
- *대안 제시*. "이건 안 좋다"보다 "이렇게 하면 더 낫다"가 가치 있다.
- *직무별 적합도*. 한국어 / 영어 시장 차이 있으면 명시.

---

*이 문서는 외부 AI 점검 1회용. 검토 후 응답은 다음 directive로 사용된다. End.*
