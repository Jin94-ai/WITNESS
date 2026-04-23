# v1.2 리뷰어 질문 응답 (Iter 20-28 이후)

> **대상**: `C:\Users\이진석\.claude\plans\frolicking-sleeping-whistle.md` §3의 6개 질문.
> **기록일**: 2026-04-19.
> **요약**: 외부 LLM(Gemini + ChatGPT) 리뷰 이후 v1.2 구현이 진행되어, 원래 질문의 상당수가 코드/테스트 증거로 해소됨.
> Peter 공생애 Phase 1-4 전체 아크가 phase-variable tick scale + slow state 전달 + absolute-time 분석 + inhibitor/slow recovery 기전을 포함하여 실행 가능. 아래는 질문별 현재 위치와 남은 의문점.

---

## Q1. Phase-variable tick scale의 타당성

**요약**: 기본 legacy(`per_tick`)는 보존되고, phase-variable `per_hour` 해석이 opt-in으로 추가됨.

**구현 증거**:
- `engine/core/hazard.py`: `HazardFunction.base_rate_unit: Literal["per_tick", "per_hour"] = "per_tick"` (Iter 27).
- `HazardEngine.evaluate_tick(tick_scale_hours=...)`: per_hour 이벤트만 `effective_dt = tick_scale_hours`를 사용. per_tick은 dt 그대로.
- `engine/simulation/world.py:274`: `tick_scale_hours=self._config.tick_scale_hours`를 전달.
- `tests/test_engine/test_hazard_per_hour.py` (9 tests): per_tick 기본 legacy 보존, per_hour 스케일링(2h/tick vs 24h/tick), 실시간 invariance, fallback.

**남은 의문**:
- Phase 경계에서 `state` 변화 rate의 불연속은 여전히 존재. `handoff`가 slow state만 carry-all하므로 fast state(emotions)는 phase마다 초기화 가능. 이는 "새 episode 시작"으로 해석 가능하지만, 장기 trajectory 분석 시 endpoint만 사용하는 게 안전 (`extract_final_states_at_phase_boundaries` 이미 제공).

**Linear R²=0.998류 메트릭**: 이제 반드시 `extract_field_trajectory_absolute` 또는 `extract_final_states_at_phase_boundaries`로 phase-stitched hours 좌표계에서 재계산해야 함. 기존 tick-based metric은 단일 phase 내에서만 유효.

---

## Q2. Phase 구분의 신학적 · 방법론적 타당성

**요약**: 5-phase 구조 확정. Phase 2 dense subwindow 제안은 Phase 3(고백/변화산)의 2h/tick dense 구간으로 흡수.

**현재 배치** (공관복음 Markan 순서 기본):
| Phase | 범위 | 근거 |
|-------|------|------|
| 01 소명 | Luke 5:1-11 | 어부 → 제자 (어획 기적) |
| 02 갈릴리 | Mark 3-9 | 12 사도 택정 (Mark 3:13-19부터 Judas 합류), 오병이어, 물 위 걸음 |
| 03 고백+변화산 | Mark 8:27-9:10 | 가이사랴 빌립보 고백 → 사탄 책망 → 변화산 |
| 04 여정 | Mark 10 | 예루살렘 접근, 3차 수난예고, 유다 공모 |
| 05 수난 | 기존 500 tick | legacy 보존 |

**Phase 2-3 경계**: 가이사랴 빌립보 고백(Mark 8:27)이 phase 3 시작. 오병이어는 phase 2 내부.
**Phase 5 시작**: 예루살렘 입성이 legacy tick 5. handoff는 이 지점 기준.

**Phase 2 희박성**: 60 tick(MVP) / 540 tick(full) — `demo_phased.py`에서 60 tick 실행 확인. 이후 dense subwindow는 필요 시 phase 2 내부 anchor_window로 해결 가능 (이미 `HazardEvent.anchor_window` 존재).

---

## Q3. Slow state 회복 메커니즘의 필요성과 위험

**요약**: Field-specific opt-in recovery rule 도입 (Iter 23). 기본 rate=0 = zero-effect. `event_trauma`는 의도적으로 회복 없음.

**구현 증거**:
- `engine/rules/slow_recovery.py`: `SlowStateFieldRecoveryRule`.
  - `moral_injury`: hope ≥ threshold (자기 용서는 희망 필요).
  - `trust_scar`: avg(relationships.trust) ≥ threshold (관계 재건).
  - `identity_shift`: hope+love 동시 threshold (음수 → 0 방향만).
  - `event_trauma`: **자연 회복 없음** — canonical intervention만.
- `tests/test_engine/test_slow_recovery.py` (19 tests): default zero-effect, 각 field 회복 조건, dt 스케일링, floor, PTSD 원칙.
- `demo_phased.py --with-recovery`: 실제 Phase 1-4 아크에서 moral_injury 1.30 → 1.23 소량 회복 관찰.

**"rare action bottleneck" 구조 붕괴 위험**:
- v0.7 Peter 수난 scenario에서 sword_drawn Phi=0.951은 legacy phase 5에서 계산됨.
- Legacy phase 5는 phases=None 모드로 실행되어 이 rule을 포함하지 않으므로 영향 없음.
- 3년 아크에 rule을 활성화할 때만 영향. rate=0.002/hour 기준 1시간에 0.002, 50일(1200h)에 최대 2.4 감소 — 단일 사건의 shock(+1.5)을 상쇄하기엔 느리지만 누적 효과는 있음.
- 튜닝은 content 수준의 결정이므로 engine 설계는 노출만 제공, 기본 비활성.

---

## Q4. MVP 선택: 소명(Luke 5) vs 대안

**현재 상태**: 소명(Phase 1)을 MVP로 선택한 것이 옳았음. 이후 Phase 2-4까지 점진 확장되어 전체 공생애가 실행 가능.

**증거**:
- `tests/test_engine/test_peter_calling.py`: Phase 1 단독 emergent 패턴 검증 (awe 평균 ≥ 3.0, obedience ≥ 2.0).
- `tests/test_engine/test_full_arc_phases_1_to_4.py`: 4 phase 연속 실행.
- `tests/test_engine/test_full_arc_with_phase_events.py`: 각 phase 자체 canonical_events 로드.
- `demo_phased.py`: 실제 실행 시 awe 0→6→8→10 progression, obedience 0→5→5.8→7.6→7.9 — canonical consistent.

**Handoff를 Phase 1만 지정하지 않은 이유**: Phase 2 진입 시 Peter state handoff가 실제로 필요했고, Judas agent introduction이 Phase 2 시작에 맞물림 (`_phase_initial_defaults` + `config.initial_states` fallback). 단독 phase 1 검증에 머물렀다면 이 기전 검증 기회가 없었음.

---

## Q5. v0.5/v0.7 검증 결과 보존

**요약**: Legacy mode (phases=None)은 코드 경로가 분리되어 기존 수치 100% 재현.

**구현 증거**:
- `PhasedSimulationWorld._run_legacy_mode`: phases=None이면 기존 `SimulationWorld`에 그대로 위임.
- `tests/test_engine/test_full_arc_with_passion.py::TestLegacyPhase5StillWorks`: legacy initial_state 로드 후 `MultiAgentResult`(not `PhasedMultiAgentResult`) 반환, `jesus_understanding="messiah_political"` 유지.
- `tests/test_engine/test_full_arc_phases_1_to_4.py::TestArchitecturalClaims::test_claim_legacy_mode_identical_to_v07`: 동일 seed에서 PhasedSimulationWorld와 SimulationWorld 결과가 bit-exact.
- `tests/test_engine/test_phase_canonical_events_loading.py::test_legacy_scenario_still_works`: v0.7 canonical_events 기본 경로 유지.

**Phase 4 → Phase 5 handoff 시 legacy 수치 영향**:
- MVP에서는 Phase 1-4와 Phase 5를 **분리 실행**. Phase 5는 독자적 legacy scenario로 남음.
- handoff를 연결하려면 Phase 4 end state → Phase 5 initial_state 매핑이 필요. 현재 `content/peter/phases/04_journey_to_jerusalem/handoff_to_05.json` 구조만 존재, 실제 연결은 미실행 (legacy 수치 보존 최우선).
- 연결할 경우 별도 mode ("linked-life")로 분기하고 기존 수치는 "legacy-phase5" mode로 유지 — 이는 계획서 §2.1에서 합의한 이원화.

---

## Q6. 연속 vs stitched 시뮬레이터

**요약**: **표면 연속 / 내부 stitched** 접근이 확정됨. `PhasedMultiAgentResult.per_phase_results`로 phase-local 결과도 접근 가능.

**구현 증거**:
- `engine/simulation/phased_world.py::PhasedMultiAgentResult`: `per_phase_results: dict[phase_id, MultiAgentResult]` + 전체 merged API.
- `PhasedMultiAgentResult.extract_absolute_trajectory(agent_id, field_path)`: absolute hours 좌표계 trajectory (phase stitch 자동).
- `engine/simulation/time_axis.py`: `ticks_to_absolute_hours`, `convert_phase_boundaries_to_hours`, `extract_field_trajectory_absolute`, `extract_final_states_at_phase_boundaries` — 분석 좌표계 선택 자유.

**Trade-off**:
- **연속 관점** (player view / 서사): `final_states`, `extract_absolute_trajectory`로 하나의 life arc로 조회.
- **Stitched 관점** (검증 / 통계): `per_phase_results["01_calling"]` 등 phase별 독립 결과에 직접 접근.
- **하이브리드 가능**: 둘 다 같은 result 객체에서 꺼낼 수 있음 — 분석 목적에 따라 선택.

---

## 진행 메트릭 (2026-04-19 현재)

| 지표 | v0.7 baseline | v1.2 현재 | 변화 |
|------|--------------|----------|------|
| Fast tests | 572 | **796** | +224 |
| Engine modules | 34 | 37+ | phase + time_axis + slow_recovery + inhibitor |
| Content phases | 1 (수난) | 5 (소명/갈릴리/고백/여정/수난) | +4 |
| Engine/content 분리 | 0 violations | 0 violations | (`test_integrity` 4 tests) |
| Ruff / mypy | clean | clean (stub warnings만) | - |

## 외부 리뷰 → 실제 반영 매핑

| 리뷰 지적 | 반영 위치 |
|----------|---------|
| "표면 연속 / 내부 stitched" 명명 (ChatGPT) | DESIGN.md v1.2 섹션, `PhasedMultiAgentResult` 설계 |
| "모든 rule dt-aware" (ChatGPT) | `RuleContext.dt_hours`, 모든 신규 rule이 per-hour rate + × dt |
| "absolute time 분석 좌표계" (ChatGPT) | `engine/simulation/time_axis.py` (Iter 22) |
| "Inhibitor Rules" (Gemini) | `engine/rules/inhibitor.py` (Iter 11), 통합 테스트 Iter 26 |
| "slow state field-specific recovery" (GPT+Gemini) | `engine/rules/slow_recovery.py` (Iter 23) |
| "legacy 수치 보존" (ChatGPT) | phases=None 분기 + `test_claim_legacy_mode_identical_to_v07` |
| "Phase 2 dense subwindow" (Gemini) | `HazardEvent.anchor_window`로 해결 가능 (기존 메커니즘 활용) |
| "canonical intervention = reparameterization shock, ≠ 완전 회복" | slow_recovery는 자연 mending만, intervention은 content 수준 shock |

---

## 남은 blockers (v1.2 완성 전)

1. Phase 4 → Phase 5 handoff 실제 배선 결정 (linked-life mode 분기 필요). 현재는 legacy 500 tick만 사용.
2. 3년 아크에서 실제 POM 검증 — Phase 1-4 emergent 패턴이 canonical ground truth와 부합하는지 ensemble 실행.
3. Inhibitor content-level 배치 — Judas disillusionment를 Peter.emotions.awe로 dampening하는 명시적 config.
