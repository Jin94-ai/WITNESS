# WITNESS — Project Overview (Structure + Core Code)

> 한 파일짜리 종합 자료: 디렉토리 구조 + 5-layer 아키텍처 + 핵심 코드 시그니처 + data flow + 현재 상태.
> 이 문서를 읽으면 *프로젝트가 무엇이고, 어떤 코드가 핵심이며, 어떻게 작동하는지* 30분 안에 파악 가능.
>
> 마지막 갱신: 2026-05-06 (Narrative Mining Engine 도입 후)

---

## 0. 한 줄 요약

WITNESS = **World-first Narrative Mining Engine**. 압력 기반 다중 에이전트
시뮬레이션을 구동하고, 그 안에서 발생하는 변화를 *Moment → MomentLink →
StoryThread → NarrativeOpportunity*로 채굴한다. 고정 주인공 / 고정 플롯 없음.
*Visual track은 frozen* — 메인 산출물은 텍스트 brief + Narrative Opportunities + 정적 HTML 콘솔.

---

## 1. 5-Layer 아키텍처

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 5: Visual (frozen, experiment record only)                 │
│  visual/*.html — pixel/scene/event-playback/world-flow viewers   │
│  → 모두 freeze. portfolio appendix.                              │
├──────────────────────────────────────────────────────────────────┤
│ Layer 4: Narrative Mining (active, USER-FACING DELIVERABLE)      │
│  engine/observer/moment.py     — Moment dataclass                │
│  engine/observer/thread.py     — MomentLink + StoryThread        │
│  engine/observer/thread_builder.py — link + thread mining        │
│  engine/observer/narrative_opportunity.py — creator-facing card  │
│  scripts/narrative/build_moments.py / build_story_threads.py /   │
│  export_narrative_opportunities.py / build_mining_console.py     │
│  → docs/portfolio/NARRATIVE_OPPORTUNITIES.md                     │
│  → docs/portfolio/narrative_mining_console.html (정적 HTML)      │
├──────────────────────────────────────────────────────────────────┤
│ Layer 3: Reporting (active, narrative mining 입력 surface)        │
│  scripts/report/build_observer_brief.py  → Markdown brief        │
│  scripts/report/build_provenance_table.py → 160-row ledger       │
│  → docs/demo/, docs/portfolio/                                   │
├──────────────────────────────────────────────────────────────────┤
│ Layer 2: Observation + Curation (active)                         │
│  engine/observer/  — 4 lens (World/Person/Group/Event)           │
│  + candidate extraction (8 signal types) + 3-bucket curation     │
├──────────────────────────────────────────────────────────────────┤
│ Layer 1: Engine (active, deterministic per seed)                 │
│  engine/core/, engine/rules/, engine/simulation/                 │
│  → hazard-driven multi-agent + Pydantic state                    │
└──────────────────────────────────────────────────────────────────┘
```

**Additive 원칙**: 위 layer는 아래 layer를 *수정하지 않는다*. Layer 4
(Narrative Mining)는 Layer 2 (Observer)의 출력 dump를 읽고 새 layer를
파생할 뿐, engine/observer 코드 무수정.

---

## 2. 디렉토리 구조 (전체)

```
Witness/
├── engine/                          # Layer 1+2 (시뮬레이터 + 관찰기)
│   ├── core/
│   │   ├── state.py                 # AgentState (Pydantic, 0-10 정규화)
│   │   ├── event.py                 # ExternalEvent, StateEffect, WeightFormula
│   │   ├── hazard.py                # HazardFunction + HazardEngine (확률 이벤트)
│   │   ├── trigger.py               # TriggerEngine (조건 기반 이벤트)
│   │   ├── action.py                # AgentAction, AgentBehaviorProfile
│   │   ├── environment.py           # EnvironmentState
│   │   ├── phase.py                 # v1.2 Phase / PhaseHandoffSpec
│   │   ├── latent_drive.py          # v1.0 LatentDriveModel + 4 Protocol
│   │   └── world.py                 # SimulationConfig
│   ├── rules/                       # 상태 전이 규칙
│   │   ├── base.py                  # Rule Protocol, RuleEngine
│   │   ├── physical.py / emotional.py / social.py / temporal.py
│   │   └── slow_recovery.py
│   ├── simulation/
│   │   ├── world.py                 # SimulationWorld (다중 에이전트 메인 루프)
│   │   ├── runner.py                # SimulationRunner (단일 에이전트 호환)
│   │   ├── phased_world.py          # v1.2 PhasedSimulationWorld
│   │   ├── batch.py                 # N회 앙상블 실행
│   │   ├── checkpoint.py            # Hindcasting 검증
│   │   ├── pom.py                   # Pattern-Oriented Modeling
│   │   └── statistics.py            # CI / Cohen's d / Wilson
│   ├── observer/                    # Layer 2 — 관찰기 (additive, 무판정)
│   │   ├── snapshot_schema.py       # 4 Pydantic 모델
│   │   ├── recorder.py              # record_snapshot() + SnapshotStream
│   │   ├── core.py                  # Observer 4 lens API
│   │   ├── salience.py              # 8 tag types + top-N
│   │   ├── candidate.py             # StoryCandidate + 4 extractor
│   │   ├── candidate_curation.py    # 3-bucket + temporal diversity
│   │   └── adapter.py               # MultiAgentResult → Observer
│   ├── world/                       # World Engine v2.0 (Spike 1-6)
│   ├── person/                      # Person v3 (state, transitions)
│   ├── rendering/                   # narrator / trace_emitter / player_view
│   └── io/                          # JSON loader / trajectory dumper
│
├── content/                         # Biography Pack (engine 비종속)
│   ├── peter/   judas/   caiaphas/   vangogh/   talleyrand/
│   └── shared/triggers.json + scripture/
│
├── scripts/
│   ├── report/                      # Layer 3 — 텍스트 리포트 생성기 (Phase 11+)
│   │   ├── build_observer_brief.py            # 메인 brief 생성
│   │   └── build_provenance_table.py          # 필드 단위 ledger
│   ├── observer/
│   │   ├── observer_report.py                 # 4 lens 텍스트 리포트
│   │   ├── candidate_packet.py                # 6-field 패킷
│   │   └── render_candidate_story.py          # 3-lens narration
│   ├── visual/                      # Layer 4 — 모두 frozen
│   │   ├── build_world_flow_events.py         # WFO adapter (frozen)
│   │   ├── audit_world_flow_traceability.py   # ✅ audit instrument (active)
│   │   └── build_event_playbacks.py           # PEP builder (frozen)
│   ├── story/                       # Story Output Layer (회귀 금지)
│   ├── audit_report.py              # HARNESS H4-H8 자동 검증
│   └── b_direction/                 # Branch B/C 실험 기록
│
├── visual/                          # Layer 4 frozen viewers (수정 금지)
│   ├── explorer.html                # 데이터 explorer (active)
│   ├── dot_observer_replay.html     # 200-tick replay (active)
│   ├── pixel_world_static.html      # PW-S2-C frozen
│   ├── pixel_scene.html             # PW-SC-B frozen
│   ├── pixel_event_playback.html    # VT-B frozen (27.9% staged)
│   └── world_flow_observer.html     # freeze (5초 테스트 fail)
│
├── data/
│   ├── visual/                      # Layer 2 산출물 dump
│   │   ├── dot_observer_data.json              # peter_scarcity_baseline (824KB)
│   │   ├── dot_observer_data_triple.json       # peter_scarcity_triple
│   │   ├── dot_observer_data_vangogh.json      # vangogh_sacred_baseline
│   │   ├── world_flow_events.json              # WFO 3-window IR
│   │   └── world_flow_events_long.json         # WFO 200-tick IR
│   ├── report/
│   │   └── provenance_table.json    # Phase 12 machine-readable
│   ├── story/   person/   world/    # 기타 산출물
│
├── tests/                           # 1,922 fast + 91 visual+report
│   ├── test_engine/   test_peter/   test_vangogh/   test_talleyrand/
│   ├── test_observer/ (212 tests)
│   ├── test_visual/   (72 tests, 모두 regression guard)
│   └── test_report/   (19 tests — Phase 11+12)
│
├── examples/                        # Runnable demo entry points
│   ├── demo.py / demo_v07.py / demo_phased.py
│   ├── demo_observer.py / demo_observer_story.py
│   ├── demo_story.py / demo_creative.py
│
├── docs/
│   ├── INDEX.md                     # 마스터 인덱스
│   ├── WITNESS_OVERVIEW.md          # ← 이 파일
│   ├── HARNESS.md                   # H1-H8 anti-bias engineering
│   ├── PROJECT_STRUCTURE.md         # 디렉토리 트리 (구버전)
│   ├── WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md  # 현재 메인 directive
│   ├── ARCHIVE_POLICY.md
│   ├── CANONICAL_MANIFEST.md
│   ├── demo/                        # Phase 11+12 텍스트 산출물
│   │   ├── WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md
│   │   ├── WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md
│   │   └── WITNESS_TEXT_FIRST_DEMO_SCRIPT.md
│   ├── portfolio/                   # Phase 13 Portfolio Package
│   │   ├── WITNESS_CASE_STUDY_TEXT_FIRST.md
│   │   ├── WITNESS_OBSERVER_BRIEF_SAMPLE.md
│   │   ├── WITNESS_VISUAL_EXPERIMENT_APPENDIX.md
│   │   ├── WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md
│   │   ├── WITNESS_RESUME_BULLETS_FINAL.md
│   │   └── (12 prior-cycle docs — architecture / interview / risk memo / etc.)
│   ├── visual/                      # Visual track 기록 + freeze decision
│   │   ├── VISUAL_TRACK_FREEZE_DECISION.md
│   │   ├── ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md   # Phase 14 design-only
│   │   ├── WORLD_FLOW_OBSERVER_VIEWER_SPEC.md
│   │   ├── WORLD_FLOW_TRACEABILITY_AUDIT.md           # WFO-A 100%
│   │   └── VISUAL_TRACEABILITY_AUDIT.md               # PEP VT-B 27.9% staged
│   ├── observer/   story/   research/   specs/   sessions/
│
├── README.md / DESIGN.md / CLAUDE.md / progress.md / lessons.md
├── benchmarks/bench_simulation.py
├── .github/workflows/ci.yml
└── main.py                          # 단일/다중 모드 entry
```

---

## 3. Layer 1 — Engine (시뮬레이션 인프라)

### 3.1 핵심 데이터 모델 — `engine/core/state.py`

Pydantic으로 0–10 범위 강제. 불변 스냅샷 (`model_copy`로 갱신).

```python
class PhysicalState(BaseModel):
    fatigue: float = Field(0.0, ge=0.0, le=10.0)
    hunger: float = Field(0.0, ge=0.0, le=10.0)
    health: float = Field(10.0, ge=0.0, le=10.0)
    location: str = "unknown"

class EmotionalState(BaseModel):
    fear: float = Field(0.0, ge=0.0, le=10.0)
    hope: float = Field(5.0, ge=0.0, le=10.0)
    grief: float = Field(0.0, ge=0.0, le=10.0)
    confusion: float = Field(0.0, ge=0.0, le=10.0)
    love: float = Field(5.0, ge=0.0, le=10.0)
    awe: float = Field(0.0, ge=0.0, le=10.0)  # v1.2

class AgentState(BaseModel):
    physical: PhysicalState
    emotional: EmotionalState
    relationships: list[Relationship] = []
    drive_state: DriveState | None = None        # v1.0
    beliefs: BeliefState | None = None           # v1.1
    moral_injury: float = 0.0                    # v1.2 slow state
    event_trauma: float = 0.0
    identity_shift: float = 0.0
    trust_scar: float = 0.0
```

### 3.2 Hazard 기반 이벤트 — `engine/core/hazard.py`

Tick 고정 이벤트를 hazard function으로 대체. *Competing risks* — 같은 tick에 여러 이벤트가 hazard로 경쟁.

```python
class HazardFactor(BaseModel):
    field_path: str        # "emotional.fear" 같은 경로
    weight: float = 1.0
    transform: Literal["linear", "inverse", "threshold"]
    threshold: float = 5.0
    source: Literal["agent", "environment"] = "agent"

    def compute(self, state, environment) -> float:
        """현재 상태에서 hazard 인자값 (0~1 정규화)"""
        ...

class HazardFunction(BaseModel):
    event_name: str
    factors: list[HazardFactor]
    base_rate: float
    precondition: list[str] = []   # 발산 방지

# 핵심 전환:
#   기존: if tick == 152: arrest()
#   신규: hazard = sum(factor.compute() * weight)
#         if rng.random() < 1 - exp(-hazard * dt): arrest()
```

### 3.3 다중 에이전트 메인 루프 — `engine/simulation/world.py`

Mesa의 Model 패턴. 매 tick 6 단계 실행.

```python
class MultiAgentResult(BaseModel):
    """다중 에이전트 시뮬레이션 결과."""
    agents: dict[str, AgentTimeline]
    triggered_events: list[TriggeredEvent]
    config: SimulationConfig

class SimulationWorld:
    """매 tick:
      1. 에이전트 활성화 순서 결정 (AgentScheduler)
      2. 각 에이전트: 자발적 행동 + 규칙 적용 (RuleEngine)
      3. 트리거 평가 → 이벤트 주입 (TriggerEngine)
      4. Hazard 평가 → 확률적 이벤트 (HazardEngine)
      5. 환경 동적 규칙 (EnvironmentDynamicsRule)
      6. 상태 스냅샷 저장
    """
    def step(self) -> dict[str, AgentState]: ...
    def run(self, ticks: int) -> MultiAgentResult: ...
```

### 3.4 Phase-linked life — `engine/simulation/phased_world.py` (v1.2)

5 phase E2E (소명 → 갈릴리 → 고백 → 여정 → 수난). PhaseHandoffSpec으로 slow state 전달.

| Phase | 기간 | tick scale | 핵심 |
|---|---|---|---|
| 01 소명 | ~1주 (84 tick) | 2h/tick | Luke 5 어획 |
| 02 갈릴리 | ~18mo (540 tick) | 24h/tick | 12 사도, 오병이어 |
| 03 고백/변화산 | ~1.5주 (150 tick) | 2h/tick | 가이사랴 빌립보 |
| 04 여정 | ~3mo (90 tick) | 24h/tick | 3차 수난예고 |
| 05 수난 | 42일 (500 tick) | 2h/tick | 기존 v0.7 (legacy) |

---

## 4. Layer 2 — Observer + Curation (관찰기, 무판정)

### 4.1 4-lens API — `engine/observer/core.py`

ABSOLUTE Rule: 관찰기 ≠ 평가기. 관측 태그까지만, 해석/판정 안 함.

```python
class Observer:
    """Read-only view over snapshot stream.

    4 lenses:
      - get_world_view(tick)         # crowd_mood / blame / suspicion / authority
      - get_person_view(agent_id, tick)  # 1 agent arc
      - get_group_view(group_id, tick)   # group dynamics
      - get_event_view(event_name)       # event ripple
    """
    def __init__(self, snapshots: list[Snapshot]):
        self._snapshots = sorted(snapshots, key=lambda s: s.tick)
        self._tick_index = {s.tick: s for s in snapshots}
```

Snapshot schema (`engine/observer/snapshot_schema.py`):

```python
class WorldSnapshot(BaseModel):
    crowd_mood: Literal["calm", "agitated", "tense"]
    blame_concentration: float   # 0.0–1.0
    public_suspicion: float
    authority_vigilance: float

class GroupSnapshot(BaseModel):
    id: str                                                  # "L1", "L2", "L3"
    dominant_mode: Literal["low_activity", "partial", "split", "saturated"]
    tension: float
    member_count: int

class AgentSnapshot(BaseModel):
    id: str
    group_id: str
    x: int; y: int                 # canvas-space (NOT tile)
    fear: float; hope: float; shame_self: float
    dominant_state: Literal["calm", "agitated", "tense", "fragmenting", "withdrawn"]
    salient: bool

class Snapshot(BaseModel):
    tick: int
    world: WorldSnapshot
    groups: list[GroupSnapshot]
    agents: list[AgentSnapshot]
    active_events: list[str]
```

### 4.2 Candidate 추출 — `engine/observer/candidate.py`

8 signal types로 점수 계산 → top-N 후보.

```python
@dataclass
class StoryCandidate:
    candidate_id: str          # "C01_t15"
    tick: int
    tick_range: tuple[int, int]
    candidate_type: Literal["person", "event", "world", "mixed"]
    strongest_lens: str        # which lens has max signal weight
    agents_involved: list[str]
    events_involved: list[str]
    rationale: str             # "Surfaced by signal_a, signal_b"
    signals: list[str]
    salience_score: int
    dominant_pressure: str

# 8 signal types (engine/observer/salience.py):
#   authority_vigilance_spike, cohort_split, agent_state_shift,
#   public_event_cluster, blame_concentration_jump, mood_shift,
#   group_tension_breach, salient_agent_persistence
```

### 4.3 Curation — `engine/observer/candidate_curation.py`

3-bucket 분류 + temporal diversity + near-dup 제거. *분류만*, quality verdict 아님.

```python
def curate_candidates(
    candidates: list[StoryCandidate],
    *,
    story_ready_min_salience: int = 2,
    temporal_min_gap: int = 8,
) -> CurationResult:
    """
    1. near_duplicate_reduce — 인접 candidate 군집화
    2. assign_use_mode → 'story_ready' / 'observation_only' / 'low_activity_hold'
    3. temporal_diversity — story_ready bucket min tick gap 적용
    """
```

---

## 5. Layer 3 — Reporting (narrative mining 입력 surface)

### 5.1 Brief builder — `scripts/report/build_observer_brief.py`

Observer dump → Markdown brief (367 lines / 5 candidate cards). 매 block에 provenance class tag.

```python
@dataclass
class CandidateSnapshot:
    candidate: dict[str, Any]
    world_at_tick: dict[str, Any]
    groups_at_tick: list[dict[str, Any]]
    focal_agents: list[dict[str, Any]]
    active_events_at_tick: list[Any]
    world_mood_window: list[str]

def get_tick(observer, tick_value: int) -> dict:
    """tick *value* 기반 lookup (list index ≠ tick value, off-by-one safe)."""
    cache = observer.setdefault("_tick_value_index", None)
    if cache is None:
        cache = {t["tick"]: t for t in observer["ticks"]}
        observer["_tick_value_index"] = cache
    if tick_value not in cache:
        keys = sorted(cache.keys())
        tick_value = max(keys[0], min(keys[-1], tick_value))
    return cache[tick_value]

def render_brief(observer, run_label, modes) -> str:
    cands = filter_candidates(observer, modes)
    snaps = [collect_snapshot(observer, c) for c in cands]
    # Markdown sections:
    #   §1 Executive summary    §2 Run context
    #   §3 Timeline             §4 Candidate cards
    #   §5 Provenance table     §6 Observer judgment
    #   §7 Visual experiment    §8 Limitations
    #   §9 Next steps
```

**Provenance class** (모든 block에 명시):
- `source_derived` — observer raw field
- `source_inferred` — bounded rule output
- `not_used` — visual staging (명시적 제외)

### 5.2 Provenance Table — `scripts/report/build_provenance_table.py`

필드 단위 ledger (160 rows / 5 candidates).

```python
@dataclass(frozen=True)
class FieldSpec:
    name: str
    cls: Literal["source_derived", "source_inferred", "not_used"]
    confidence: Literal["high", "medium", "low"]
    source: str        # "observer.ticks[t].world.crowd_mood" 같은 경로
    note: str = ""

CANDIDATE_FIELDS = (...)        # 13 specs (candidate_id ~ related_candidate_ids)
WORLD_TICK_FIELDS = (...)       # 4 specs
GROUP_TICK_FIELDS = (...)       # 3 specs
AGENT_TICK_FIELDS = (...)       # 7 specs
NOT_USED_FIELDS = (...)         # 5 specs (visual staging — 명시 제외)

# 결과:
#   Total field rows: 160
#   source_derived:  95 (59.4%)
#   source_inferred: 40 (25.0%)
#   not_used:        25 (15.6%)
```

### 5.3 Brief generator는 schema-agnostic

같은 builder가 anchor 무관 작동. test에서 lock-in:

```python
ALT_DUMPS = [
    ("dot_observer_data_triple.json",   "peter_scarcity_triple",   False),
    ("dot_observer_data_vangogh.json",  "vangogh_sacred_baseline", True),  # hold-only
]

def test_brief_builder_generalizes_to_alt_anchors(tmp_path):
    for src, label, include_holds in ALT_DUMPS:
        bob.main(str(src), str(tmp_path / f"brief_{label}.md"),
                 run_label=label, include_holds=include_holds)
```

---

## 5.5 Layer 4 — Narrative Mining Engine (현재 메인 산출물, Phase 1-5)

### 5.5.1 핵심 데이터 모델 — `engine/observer/moment.py`

Frozen dataclass. 8 moment types (agent_state_shift / group_tension_shift /
world_pressure_shift / conflict_marker / unresolved_thread / event_ripple /
choice_pattern / relationship_drift). Provenance class on every record.

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
    groups: tuple[str, ...] = ()
    pressures: tuple[str, ...] = ()
    signals: tuple[str, ...] = ()
    summary: str = ""
    salience_score: float = 0.0
    provenance: ProvenanceClass = "source_derived"

    def __post_init__(self):
        # tick must lie within tick_range; salience in [0,1]; tuple-only
        ...
```

### 5.5.2 5 추출 패밀리 — `engine/observer/moment_extractor.py`

Deterministic, no rng. Threshold tuning lives in `MomentThresholds` dataclass.

```python
@dataclass(frozen=True)
class MomentThresholds:
    agent_state_delta: float = 1.5         # 0–10 scale
    group_tension_delta: float = 0.15      # 0–1 scale
    world_pressure_delta: float = 0.08
    sustained_pressure_min_ticks: int = 8
    sustained_pressure_threshold: float = 7.0
    conflict_window: int = 3
    min_tick_gap_per_agent: int = 4

# Extractor families:
#   A. _extract_agent_state_shifts   — fear/hope/shame/state delta
#   B. _extract_group_tension_shifts — tension delta or mode change
#   C. _extract_world_pressure_shifts — mood / authority / blame / suspicion
#   D. _extract_conflict_markers     — co-occurring multi-source signals
#   E. _extract_unresolved_threads   — sustained pressure runs

def extract_moments(observer, thresholds=None) -> list[Moment]:
    """Sorted by (tick, moment_id) — stable output."""
```

### 5.5.3 MomentLink — `engine/observer/thread.py`

7 link types. Edge weight is base × decay(tick gap).

```python
LinkType = Literal[
    "same_agent", "same_group", "same_relationship",
    "same_pressure", "same_conflict_axis",
    "causal_order", "temporal_continuity",
]

@dataclass(frozen=True)
class MomentLink:
    source_moment_id: str
    target_moment_id: str
    link_type: LinkType
    weight: float
    rationale: str
```

### 5.5.4 link_moments — `thread_builder.link_moments`

```python
@dataclass(frozen=True)
class LinkThresholds:
    max_gap: int = 30                # primary tick budget
    max_gap_unresolved: int = 60     # extended for unresolved_thread
    same_agent_weight: float = 0.85
    same_group_weight: float = 0.65
    same_pressure_weight: float = 0.55
    same_conflict_axis_weight: float = 0.75
    causal_order_weight: float = 0.50
    temporal_continuity_weight: float = 0.30
    decay_horizon: int = 50

def link_moments(moments, thresholds=None) -> list[MomentLink]:
    """For each pair within gap budget, evaluate each link family
    independently. temporal_continuity is *fallback* only — emits if no
    structural link fired for the pair."""
```

### 5.5.5 StoryThread — `engine/observer/thread.py`

Frozen dataclass. Provenance is `source_inferred` (rule output, not raw).

```python
ArcDirection = Literal[
    "stability_to_breakdown", "fear_to_withdrawal",
    "trust_to_distance", "loyalty_to_betrayal_risk",
    "confusion_to_commitment", "isolation_to_dependence",
    "tension_to_collective_action", "unknown",
]

@dataclass(frozen=True)
class StoryThread:
    thread_id: str
    title: str
    main_agents: tuple[str, ...]
    supporting_agents: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    core_conflict: str = "unknown"
    arc_direction: ArcDirection = "unknown"
    moment_ids: tuple[str, ...] = ()
    start_tick: int = 0
    end_tick: int = 0
    pressure_history: tuple[str, ...] = ()
    relationship_drift: tuple[str, ...] = ()
    unresolved_question: str = ""
    story_potential_score: float = 0.0
    usable_as: tuple[str, ...] = ()
    provenance: str = "source_inferred"
```

### 5.5.6 build_story_threads — agent-centric mining

Why **not** plain connected-components: 1,727 links over 105 moments collapses
to a single mega-component (driven by `temporal_continuity`). Instead:

```python
def _mine_threads_by_agent(moments, links):
    """For each main agent, group moments where they appear, then attach
    bridge moments (no-agent world/group moments linked via same_pressure or
    same_conflict_axis). Each agent → one candidate thread."""

def _mine_threads_by_group(moments, links):
    """Group-centric fallback for orphan group/world moments."""

def build_story_threads(moments, links, thresholds=None) -> list[StoryThread]:
    agent_comps = _mine_threads_by_agent(moments, links)
    group_comps = _mine_threads_by_group(moments, links)
    # filter: min 3 moments + score ≥ min_score_for_inclusion
    # sort: descending score, then start_tick
    # reassign T01 = strongest
    ...
```

(Lesson L56 records this design choice.)

### 5.5.7 8 score factors — sum to 1.0 per plan §6.2

```python
@dataclass(frozen=True)
class ThreadThresholds:
    min_moments_per_thread: int = 3
    min_score_for_inclusion: float = 0.40
    strong_score: float = 0.80      # → "strong"
    usable_score: float = 0.60      # → "usable"
    weak_score:   float = 0.40      # → "weak"
    # Eight weighted factors (must sum to 1.0):
    w_change: float          = 0.20    # max salience proxy
    w_continuity: float      = 0.15    # tighter cluster → higher
    w_conflict: float        = 0.20    # explicit conflict_marker bonus
    w_relationship: float    = 0.15    # group_tension + multi-agent
    w_pressure: float        = 0.10    # distinct pressure count
    w_resolution_gap: float  = 0.10    # final unresolved_thread bonus
    w_multi_agent: float     = 0.05    # ≥3 agents
    w_creative_use: float    = 0.05    # has agent + world + group layers
```

### 5.5.8 Conflict + arc inference (deterministic, no LLM)

```python
def _infer_core_conflict(component) -> str:
    if fear_up and (auth_up or sus_up):
        return "loyalty_vs_survival"
    if tension_up and blame_up:
        return "collective_fear_vs_scapegoating"
    if auth_up and sus_up:
        return "control_vs_exposure"
    if hope_down and shame_up:
        return "identity_vs_failure"
    # ... 8 conflict labels total

def _infer_arc_direction(component) -> ArcDirection:
    if fear_up and (shame_up or has_unresolved):
        return "fear_to_withdrawal"
    # ... 7 arc labels + "unknown"
```

### 5.5.9 NarrativeOpportunity — `engine/observer/narrative_opportunity.py`

Creator-facing card layered over StoryThread.

```python
OpportunityRank = Literal["strong", "usable", "weak", "hold"]

@dataclass(frozen=True)
class NarrativeOpportunity:
    thread_id: str
    title: str
    logline: str               # deterministic, by conflict family
    core_conflict: str
    arc_direction: str
    unresolved_question: str
    creative_uses: tuple[str, ...]   # film_scene / novel_chapter / game / drama
    score: float
    rank: OpportunityRank
    main_agents: tuple[str, ...]
    moment_count: int
```

### 5.5.10 Pipeline

```python
# 4 sequential CLI stages (each writes JSON, no in-memory chain required)
build_moments.py             → data/narrative/moments.json (105)
build_story_threads.py       → moment_links.json (1,727) + story_threads.json (4)
export_narrative_opportunities.py → narrative_opportunities.json + .md
build_mining_console.py      → narrative_mining_console.html (56KB self-contained)
```

Cross-anchor verified: same pipeline runs on `peter_scarcity_baseline`
(105 moments / 4 threads), `peter_scarcity_triple` (99 / 4), and
`vangogh_sacred_baseline` (16 / 1) without code changes.

---

## 6. Layer 5 — Visual (frozen, audit instrument 보존)

### 6.1 Freeze 상태

| 파일 | 등급 | 사유 |
|---|---|---|
| `pixel_world_static.html` | PW-S2-C | 어휘 patch ≠ 구성 fix |
| `pixel_scene.html` | PW-SC-B | static medium 한계 |
| `pixel_event_playback.html` | VT-B (72.1% src / **27.9% staged**) | hand-staged cutscene |
| `world_flow_observer.html` | freeze | 5초 테스트 fail (subtle > legible) |

### 6.2 Audit instrument는 active — `scripts/visual/audit_world_flow_traceability.py`

PEP / WFO 모두에 적용 가능한 provenance auditor. Visual 트랙의 *진짜* 산출물.

```python
def collect_actions(world_flow) -> list[dict]: ...
def class_counts(actions) -> dict[str, int]: ...
def decide_case(backed_ratio, staged_ratio) -> str:
    """
    WFO-A: backed ≥ 80% AND staged ≤ 20%
    WFO-B: backed ≥ 50%
    WFO-C: otherwise
    """
```

이 audit vocabulary가 Layer 3의 Brief generator에 *그대로 transfer*되어 per-block class tag로 작동. Visual track의 실패가 Reporting layer 정직성의 prerequisite을 만들었다.

### 6.3 WFO Adapter (frozen) — `scripts/visual/build_world_flow_events.py`

Engine event log adapter MVP. 100% source-backed (WFO-A) but viewer-less.

```python
def main(in_path, out_path, mode: Literal["windows", "long_form"] = "windows"):
    """
    'windows':   3 candidate-defined tick windows (PEP-comparable)
    'long_form': single synthetic window covering ticks [0, 199]
                 → 200 ticks × 12 agents + synthetic guard
                 → 768 visual_actions, 144 derived + 624 inferred + 0 staged
    """
```

---

## 7. Data Flow (시뮬레이션 → 사용자)

```
[1] python main.py --multi
      ↓
[2] SimulationWorld.run(ticks=200, seed=0)         # Layer 1 engine
      ↓
[3] MultiAgentResult (in-memory)
      ↓
[4] Observer.adapter(result)                       # Layer 2 — post-hoc
      ↓
[5] snapshot stream + candidates + 3-bucket curation
      ↓
[6] data/visual/dot_observer_data.json             # ~824 KB JSON dump
      │
      ├─── Layer 3 (Reporting) ─────────────────────────────────────┐
      ↓                                                             ↓
[7a] python scripts/report/build_observer_brief.py       [7b] python scripts/report/build_provenance_table.py
      ↓                                                             ↓
[8a] docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md   [8b] docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md
                                                                   + data/report/provenance_table.json
      │
      └─── Layer 4 (Narrative Mining) — *현재 메인 산출물* ─────────┐
      ↓                                                             ↓
[9]  python scripts/narrative/build_moments.py                      → data/narrative/moments.json (105)
      ↓
[10] python scripts/narrative/build_story_threads.py                → data/narrative/moment_links.json (1,727)
                                                                    + data/narrative/story_threads.json (4)
      ↓
[11] python scripts/narrative/export_narrative_opportunities.py     → docs/portfolio/NARRATIVE_OPPORTUNITIES.md
                                                                    + data/narrative/narrative_opportunities.json
      ↓
[12] python scripts/narrative/build_mining_console.py               → docs/portfolio/narrative_mining_console.html
                                                                      ← USER FACES THIS (56KB self-contained)

(Layer 5 Visual — frozen):
[6] dot_observer_data.json
      ↓
[6'] python scripts/visual/build_world_flow_events.py
      ↓
[7'] data/visual/world_flow_events_long.json  (WFO-A IR)
      ↓
[8'] visual/world_flow_observer.html  (frozen — 5초 테스트 fail)
```

**Cross-anchor verified**: 동일 파이프라인이 `peter_scarcity_baseline` (105 moments / 4 threads),
`peter_scarcity_triple` (99 / 4), `vangogh_sacred_baseline` (16 / 1)에서
코드 변경 없이 작동. 입력만 다르면 출력도 다른 정직한 generalization.

---

## 8. 실행 진입점 (Quick reference)

| 목적 | 명령 | 산출물 |
|---|---|---|
| 다중 에이전트 시뮬레이션 (Peter, 100 runs) | `python main.py --multi` | 콘솔 통계 |
| Phase-linked 시뮬레이션 (v1.2) | `python examples/demo_phased.py --seed 0` | 콘솔 + JSONL |
| Trace pipeline (v0.7) | `python examples/demo_v07.py --scenario peter` | trace events |
| Story output (단일) | `python examples/demo_story.py` | 한국어 .txt |
| Observer-Story pipeline | `python examples/demo_observer_story.py --curated` | 후보 카드 |
| **Observer Brief 생성 (메인 산출물)** | `python scripts/report/build_observer_brief.py` | docs/demo/*.md |
| **Provenance Table 생성** | `python scripts/report/build_provenance_table.py --json data/report/provenance_table.json` | .md + .json |
| WFO 데이터 빌드 (frozen) | `python scripts/visual/build_world_flow_events.py --mode long_form` | JSON IR |
| WFO traceability audit | `python scripts/visual/audit_world_flow_traceability.py` | audit MD |
| 빠른 회귀 테스트 | `pytest -m "not slow and not archived"` | 1,922 passed |
| 리포트 테스트만 | `pytest tests/test_report/` | 19 passed |
| HARNESS 자동 검증 | `python scripts/audit_report.py <report.md>` | 자가감사 결과 |

---

## 9. 테스트 분포 (1,922 fast + 91 visual+report)

| 디렉토리 | tests | 영역 |
|---|---|---|
| `tests/test_engine/` | ~400 | core / rules / simulation |
| `tests/test_peter/` | ~150 | POM / ablation / KS |
| `tests/test_vangogh/` | ~100 | scenario universality |
| `tests/test_talleyrand/` | ~80 | 3rd scenario (engine universality) |
| `tests/test_world/` | ~250 | World Engine v2.0 (Spike 1-6) |
| `tests/test_world_process/` | ~150 | Process layers |
| `tests/test_observer/` | 212 | 4 lens + candidate + curation + adapter |
| `tests/test_story/` | 119 | Story output (한국어 narrative) |
| `tests/test_action/`, `test_persona/`, `test_population/`, `test_rubric/` | ~250 | 보조 영역 |
| **`tests/test_visual/`** | **72** | regression guard (track frozen) |
| **`tests/test_report/`** | **19** | brief (11) + provenance table (8) — Phase 11+12 |

---

## 10. 핵심 원칙 (CLAUDE.md 발췌)

### 엔진/콘텐츠 분리
```bash
grep -r "peter\|Peter\|베드로" engine/   # 결과 항상 0건
```

### Layer 추가 규칙
- 모든 새 layer는 *additive*. 위 layer는 아래 layer 무수정.
- 새 anchor / scenario / metric / event type 도입은 *명시적 directive 필요*.

### HARNESS — 보고 정직성 (H1-H8)
- H1: 수치 보고 시 trivial explanation + falsification criterion
- H4: 보고서 필수 — *What could still be wrong / What I did NOT try / Alternate interpretations*
- H7: 보고 직전 자가감사 8항목 응답
- H8: sensitivity ratio가 headline claim이면 5+ seed ensemble 필수

### 금지어 (verbatim)
"설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다", "작동한다" (단독)

---

## 11. 현재 상태 (2026-05-06)

### 무엇이 작동하는가

| 구성 요소 | 상태 |
|---|---|
| 다중 에이전트 시뮬레이터 (engine/) | ✅ deterministic per seed, 2,026 tests |
| Observer + Curation 파이프라인 | ✅ 212 tests, 3 anchor 검증 |
| Story Output Layer (한국어 narrative) | ✅ 119 tests (회귀 금지 — 메인 산출물 아님) |
| Observer Brief 자동 생성기 (Phase 11) | ✅ Reporting layer — 19 tests, narrative mining 입력 |
| Provenance Table 자동 생성기 (Phase 12) | ✅ Reporting layer — 8 tests |
| **Moment Extractor (Phase 1)** | ✅ Narrative Mining — 18 tests / 105 moments |
| **Moment Linking (Phase 2)** | ✅ Narrative Mining — 15 tests / 1,727 links |
| **Story Thread Builder (Phase 3)** | ✅ Narrative Mining — 20 tests / 4 threads (cross-anchor lock-in) |
| **Narrative Opportunity Export (Phase 4)** | ✅ Narrative Mining — 11 tests |
| **Mining Console HTML (Phase 5)** | ✅ Narrative Mining — 7 tests / 56KB self-contained |
| **IdentityResolver (Stage 5 / Phase A)** | ✅ Story Emergence — 10 tests / 3-tier lookup |
| **StoryCandidate + builder (Stage 6 / Phase B+C)** | ✅ Story Emergence — 16 tests / 4 named cards |
| **Cross-seed Pattern (Phase E)** | ✅ Story Emergence — 7 tests / **6 robust / 0 anomaly across 5 seeds** |
| **Story Candidate Console (Phase F)** | ✅ Story Emergence — 23KB self-contained HTML |
| Visual track 5 sub-tracks | ❌ 모두 frozen |
| Audit instrument (WVT / WFO) | ✅ active — text brief + narrative mining + story emergence의 vocabulary 기반 |

### 무엇이 결과물인가 (문서 빼고)

1. **시뮬레이션 인프라** — 2,026 fast tests deterministic
2. **데이터 dump** — 824 KB JSON per run (peter / triple / vangogh + 5 seeds)
3. **자동 생성 Markdown brief** — 367 lines, regenerable in <1s
4. **자동 생성 Provenance ledger** — 160 rows .md + .json
5. **자동 생성 Story Threads** — 4 threads / 1,727 links / 105 moments
6. **자동 생성 Narrative Opportunities** — 4 cards + 56 KB mining console
7. **자동 생성 Story Candidates** — 4 *named* cards (Peter / Andrew / James / John) + 23 KB candidate console
8. **Cross-seed robustness report** — 5 seeds × full pipeline → 6/6 robust patterns / 0 anomaly
9. **Frozen viewers** — 4 HTML 파일, 실행 가능하나 portfolio main 아님

→ 외부 사용자 surface 둘로 늘어남:
- 데이터 mining 시각화: `narrative_mining_console.html`
- 창작자 카드: `story_candidate_console.html` (cross-seed 배지 포함)

### Pivot 핵심 framing (갱신)

> *"Visual의 audit instrument가 text brief의 정직성을 만들고, text brief의 Moment 추출이 Story Thread mining을 가능하게 했고, identity 매핑이 익명 ID를 named character로 승격하고, cross-seed가 narrative structure 자체가 *seed-stable*임을 증명했다. 즉 시뮬레이션 *세계 구조*가 일관된 narrative 패턴을 produce — 우연이 아니다."*

---

## 12. 다음 단계 후보

Story Emergence Phase A-F 완료 후 *모든 plan 단계 충족*. 남은 후보가 본질적으로 작아진다:

| 옵션 | 설명 | 결과물 |
|---|---|---|
| **A. 휴면 (실제 사용)** | 외부 트리거(면접 / 지원 / 피드백) 후 재개. 현 패키지로 충분 | 추가 0 |
| **B. 외부 LLM peer review** | 현 portfolio + 두 console을 외부 모델에 검토 요청. EXTERNAL_REVIEW_BRIEF.md 활용 | 외부 신호 |
| **C. cross-anchor portfolio** | 3 anchor (peter/triple/vangogh) Story Candidate set 비교. *익명 fallback도 작동함* 보강 | 추가 portfolio doc |
| **D. Phase 14 활성화** | Engine Event Log Adapter (visual 부활). narrative mining이 *덜 필요하게* 만들어 우선순위 낮음 | plan 갱신 필요 |
| **E. natural-language enrichment** | premise / arc 한 단계 더 풍부하게. plan §14.4 위배 위험 — 새 directive 필요 | "이야기" 수준에 더 가까움 |
| **F. 자체 종료** | 더 추가하면 over-engineering. 현 패키지로 portfolio 사용 | ✓ |

> Note: Phase 14 (visual 부활)의 *우선순위는 낮아진 채로 유지*. Story Emergence가
> "세계가 굴러간다"와 "여러 인물이 다른 갈등으로 surface한다"를 visual 없이
> 보여주는 surface (static HTML console + named candidate cards + cross-seed robustness)를
> 만들었기 때문. Visual은 *nice-to-have*이지 portfolio blocker 아님.

---

## 13. 핵심 docs 빠른 링크

- 메인 directive: [WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)
- 메인 산출물: [demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- 케이스 스터디: [portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md](portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md)
- Visual freeze 결정: [visual/VISUAL_TRACK_FREEZE_DECISION.md](visual/VISUAL_TRACK_FREEZE_DECISION.md)
- Phase 14 design notes: [visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md](visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md)
- 행동 강령: [../CLAUDE.md](../CLAUDE.md)
- 4-layer 설계: [../DESIGN.md](../DESIGN.md)
- 마스터 인덱스: [INDEX.md](INDEX.md)
- 설계 트리 (구버전): [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- HARNESS 자가감사: [HARNESS.md](HARNESS.md)
- 세션 메모리: [../progress.md](../progress.md)
- 크로스 세션 학습: [../lessons.md](../lessons.md) (L1-L55, L46-L55 visual track cluster)

---

*Generated 2026-05-06. 이 문서는 프로젝트 구조 + 핵심 코드의 단일 진입점이다.*
*30분 리뷰용으로 설계됐다. 더 깊이는 위 13. 빠른 링크에서.*
