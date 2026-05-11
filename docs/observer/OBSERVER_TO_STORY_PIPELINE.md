# Observer → Story Candidate Pipeline — Canonical Spec

**Date**: 2026-04-30
**Source**: `docs/WITNESS_OBSERVER_TO_STORY_PIPELINE_DIRECTIVE.md` (Lee directive)
**Status**: Phase P1-P5 구현 완료 (2026-04-30)
**용도**: Observer Layer가 잡은 salient moment / split / event ripple / world shift를 *story candidate*로 변환하는 파이프라인의 canonical 기준.

---

## 0. 핵심 목표

> **Observer가 포착한 흐름을 실제 story candidate로 연결하고, 그 결과를 사람이 확인 가능한 형태로 출력한다.**

Observer = 관찰만. Story Candidate Pipeline = *어떤 흐름을 이야기로 볼 것인가* selection layer.

---

## 1. ABSOLUTE 원칙

### Rule #1 (engine/ no person hardcoding)
- `engine/observer/candidate.py`에 person name 하드코딩 금지
- agent_id는 caller가 주입한 generic ID 그대로 노출

### Rule #6 (engine API preservation)
- 기존 Observer API 무수정
- Candidate Extractor는 *additive*

### 관찰기 ≠ 평가기 원칙 (Observer Layer 일관)
- Candidate = *추천*만, *판정* 안 함
- "best story" / "good asset" 자동 결정 금지
- Quality verdict 자동화 금지
- *탐색 효율* 향상에 집중

---

## 2. 5 Phase 구현 (Lee directive §15)

| Phase | 산출물 | 상태 |
|---|---|---|
| **P1** Candidate Extractor | `engine/observer/candidate.py` | 완료 (12 tests PASS) |
| **P2** Packet Builder | `scripts/observer/candidate_packet.py` | 완료 (13 tests PASS) |
| **P3** Render Link | `scripts/observer/render_candidate_story.py` | 완료 (10 tests PASS) |
| **P4** Demo Command | `examples/demo_observer_story.py` | 완료 (4-mode CLI 동작 확인) |
| **P5** Validation + Review | `docs/observer/OBSERVER_TO_STORY_VALIDATION.md` + `_REVIEW.md` | 완료 (Case A 성공 verdict) |

---

## 3. Story Candidate 정의 (Lee directive §5)

### 3.1 다음 중 하나 이상을 만족하면 candidate

1. **Salience spike** — pressure / blame target shift / public suspicion jump / authority vigilance spike
2. **Split / divergence** — group outcome divergence / same anchor seed 차이 / person vs world arc tension
3. **Turning point** — recovery turn / saturation lock / mixed bifurcation / event ripple turning point
4. **World-heavy moment** — 개인보다 세계 흐름이 더 강한 순간
5. **Low-activity but meaningful** — 사건 작지만 tension 있는 구간

### 3.2 NOT — 평가 안 함

- Story quality 점수화
- "Best story" 자동 결정
- "Good / bad asset" 자동 분류

---

## 4. Candidate 추출 방식 (Lee directive §6)

### 4.1 Minimal scoring (각 candidate의 measurable 항목)

- `salience_score` — Observer salience tag count at the tick
- `world_signal_strength` — world.blame_concentration / public_suspicion / authority_vigilance peak
- `split_signal` — number of distinct group dominant_modes at tick
- `event_ripple_strength` — active_events count + agent involvement
- `person_arc_movement` — agent delta tag count
- `closure_potential` — recovery_turning_point 또는 saturation_lock 발생 여부

### 4.2 정렬만, 자동 판정 안 함

- Top 5 salient candidates
- Top 3 world-heavy candidates
- Top 3 person-arc candidates
- Top 3 event-ripple candidates

---

## 5. Candidate Packet 포맷 (Lee directive §7)

각 candidate는 다음 6 fields로:

### A. Basic
- `candidate_id`: str
- `source_run`: str (anchor + seed)
- `tick_range`: tuple[int, int]
- `dominant_pressure`: str
- `dominant_mode`: str
- `candidate_type`: Literal["person", "event", "world", "mixed"]

### B. Why surfaced
- `signals`: list[str] (어떤 salience rule로 올라왔는가)

### C. Lens summaries (각 2-3줄)
- `person_lens`: str
- `event_lens`: str
- `world_lens`: str

### D. Story potential
- `potential_arcs`: list[str] — ["person", "event", "world"]
- `notes`: str — "demo용" / "strong candidate" / "hook 약함" 등

### E. Render link
- `render_recommended`: bool
- `render_lens`: Literal["person", "event", "world", "skip"] | None

### F. Human check (placeholder)
- `human_check`: Literal["keep", "interesting", "revise_later", "skip"] | None = None

---

## 6. Candidate-to-Story Link (Lee directive §3.3 + Phase P3)

### 6.1 MVP scope

candidate별 multi-lens text output 생성. 기존 Observer narrative_summary + observer_report 활용.

```python
render_candidate_story(candidate, observer, lens="person")
# → 한국어 prose narrative (lens-specific)
```

### 6.2 출력 layers

- Light: narrative_summary 함수 (한국어 prose)
- Detail: format_person_arc / format_event_view / format_world_trace 표
- Composite: light + detail 결합

### 6.3 Out of scope (full IR + render)

기존 `scripts/story/render_story_ko.py`는 *probe-shaped data* 입력. Observer snapshot → IR 변환은 *Phase P6+* 영역. MVP에서는 *light narrative*만.

---

## 7. Demo Command (Phase P4)

`examples/demo_observer_story.py` 4 modes:

| Mode | 동작 |
|---|---|
| `--list-candidates` | top 5 candidates 표시 (default) |
| `--packet <candidate_id>` | 단일 candidate packet 출력 |
| `--render-story <candidate_id>` | candidate render 결과 (multi-lens) |
| `--compare-lenses <candidate_id>` | 3 lens 비교 |

기본 입력: `peter_scarcity_baseline` canonical run (Lee directive §10 1순위).

---

## 8. 성공 기준 (Lee directive §11)

다음 중 4개 이상 충족 시 성공:

1. observer가 뽑은 candidate 3-5개가 실제로 story-worthy하게 보인다
2. 같은 candidate를 person/event/world lens로 볼 때 차이가 느껴진다
3. candidate packet만 읽어도 "왜 이게 후보인지" 이해된다
4. 최소 2개 candidate가 실제 story output으로 자연스럽게 이어진다
5. observer가 story selection의 앞단으로서 유용하다는 느낌이 든다
6. 시스템이 quality verdict를 하지 않으면서도 탐색 효율은 올라간다

---

## 9. Forbidden_now (Lee directive §14 verbatim)

- public browser UI
- story quality 자동 판정
- 더 많은 lens 추가
- candidate 점수 체계 비대화
- Branch C 추가 실험
- Talleyrand scenario
- PyTorch encoder
- Renderer 재시작
- Polished asset pack 자동화

→ 모두 **forbidden**. MVP scope 안에 머물기.

---

## 10. 분기 (Lee directive §13)

| Case | Trigger | 다음 단계 |
|---|---|---|
| A 성공 | 4+ 기준 충족 | Pipeline freeze 검토 / Story Explorer 방향 검토 |
| B 일부 약함 | 일부 기준만 | extractor 또는 packet 국소 수정 + 재검증 |
| C 전반 약함 | 다수 약함 | candidate logic 단순화 / lens 1축으로 축소 |

---

## 11. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (this spec)** | **2026-04-30** | **Lee directive 기반 canonical spec, Phase P1-P5 시작** |
