# WITNESS — Resume Bullets (Final, Text-first)

> **2026-05-06 update**: 이 resume bullets는 Reporting Layer (text brief)
> 중심으로 작성되었다. Narrative Mining Engine 추가 이후, 가장 강한 한 줄은:
>
> > "Built a *Narrative Mining Engine* over a multi-agent simulation —
> > extracts Story Thread candidates with full provenance ledger, ships
> > a self-contained static HTML console, no external dependencies."
>
> 한국어:
>
> > "다중 에이전트 시뮬레이션 위에 *서사 채굴 엔진*을 구축 — 압력 변화 →
> > Moment → MomentLink → StoryThread → NarrativeOpportunity 5단 파이프라인을
> > deterministic rule로 구현, provenance class를 모든 출력에 부여, 정적
> > HTML 콘솔을 외부 의존성 0으로 배포."
>
> 이 한 줄을 §2.3/§2.4 bullets 중 어느 것과도 교체해 사용 가능.

> Replaces the earlier draft at [APPLICATION_RESUME_BULLETS.md](APPLICATION_RESUME_BULLETS.md)
> for the post-pivot framing. Use this version when applying.

---

## 0. Why a "Final" version

The prior draft framed WITNESS around the visualization layer. After the
text-first pivot ([WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](../WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)),
the strongest claim is the *audit-driven pivot itself* — which produced a
methodology, not a visual.

Use the bullets below as a library; pick 3–5 per application based on the
target role. Do not concatenate them all.

---

## 1. Core numbers (always include at least one)

| Item | Value |
|---|---|
| Engine fast tests | **2,026 passing** (deterministic per seed) |
| Visual regression tests | 72 passing (frozen at v0.6 baseline) |
| Report tests | 18 passing (brief builder + provenance table) |
| Architecture | **4-layer** (engine → observer → reporting → visual frozen) |
| Audit vocabulary | **3-class** (source_derived / source_inferred / not_used) |
| Brief field rows audited | **160** rows / 5 candidates (59% derived / 25% inferred / 16% excluded) |
| Visual track sub-tracks | 5 attempted, all frozen with measured verdicts |
| Pivot decision | driven by 27.9% staged-only audit failure (PEP / VT-B) |
| Provenance audit reproducibility | re-runnable on any observer dump in <1 s |
| Engine throughput | ~1,000–1,300 ticks/sec |
| External dependencies | **0** (vanilla Python + Markdown; no Phaser / React / PixiJS) |

---

## 2. AI / ML Engineer roles

### 2.1 Korean — short (3 bullets)

- **에이전트 시뮬레이션의 검증 파이프라인 설계** — 2,026 unit test 위에 *audit instrument* (3-class provenance vocabulary) 구축. 자체 출력에 대해 *source-derived / source-inferred / not-used* 분류를 강제, sensitivity claim에 5+ seed 앙상블 의무화 등 8-rule self-evaluation 프레임워크.
- **Audit-driven product pivot** — visual prototype의 27.9% staged-only 비율을 audit으로 측정해 visual track 전체 freeze 결정. 동일 audit vocabulary를 text-first brief에 transfer하여 *측정 가능한 honesty*를 product 표면으로 전환.
- **4-layer additive architecture** (engine → observer → reporting → visual frozen) — 각 layer는 이전 layer 무수정. 도메인 하드코딩 grep 자동 검증. schema versioning append-only.

### 2.2 Korean — extended (5 bullets)

- **에이전트 시뮬레이션 + 평가 파이프라인 설계** — 12-에이전트 hazard-driven Poisson 시뮬레이션 위에 결정론적 시드, deterministic dump, 2,026 fast test로 검증된 reproducible run 인프라.
- **Observer Layer (additive non-evaluator)** — engine output을 수정하지 않고 candidate 추출, signal-lens 점수, 3-bucket curation. 관찰기와 평가기의 분리 원칙을 코드 레벨에서 강제.
- **Provenance audit instrument** — visual track의 hand-staging을 측정하기 위해 만든 3-class vocabulary (source_derived / source_inferred / staged_only)가 그대로 text brief의 per-block class-tag로 transfer. 160 row field-level ledger가 portfolio 산출물.
- **Audit-driven pivot decision** — PEP cutscene playback의 27.9% staged ratio가 측정되자마자 visual track 전체 freeze. 메인 산출물을 polished visual에서 evidence-backed text brief로 전환. *측정이 product 결정을 강제한 사례*.
- **Engineering quality** — ruff + mypy 0 errors, 2,026 fast / domain / full 3-tier pytest, 외부 의존성 0, 8-rule HARNESS self-evaluation framework.

### 2.3 English — short (3 bullets)

- **Designed and built an audit-driven evaluation pipeline for a multi-agent simulation observer**. Built a 3-class provenance vocabulary (source_derived / source_inferred / not_used) into the report generator, scoring 160 field rows across candidate cards. 2,026 fast unit tests, deterministic per seed.
- **Pivoted the project's main deliverable from a visual prototype to a text-first observer brief based on a measured audit failure** (27.9% staged-only ratio in the visual playback). Transferred the audit vocabulary from the visual track to the text track, producing a portfolio claim of *measurable honesty* rather than polished output.
- **Implemented a 4-layer additive architecture** (engine → observer → reporting → visual frozen). Each layer is *additive* — downstream layers do not modify upstream artifacts. Schema versioning is append-only. No external runtime dependencies.

### 2.4 English — extended (5 bullets)

- **Multi-agent simulation infrastructure**: 12-agent / 3-group hazard-driven Poisson simulation with deterministic seeds, reproducible dumps, and 2,026 fast unit tests. Engine throughput ~1,000–1,300 ticks/sec.
- **Observer / Curation layer (additive, non-evaluating)**: extracts event candidates from per-tick state changes via signal detectors and lens scoring, classifies each candidate into 3 use-mode buckets. Engine output is never modified by the observer; the boundary is enforced by `grep` checks in CI.
- **Provenance audit instrument**: a 3-class vocabulary (source_derived / source_inferred / staged_only) developed during a visual experiment that became the foundation for the project's user-facing report. The same audit method scores 160 field rows in the text brief and produced the verdict for freezing the visual track.
- **Audit-driven product pivot**: the visual playback layer was frozen after its audit returned a 27.9% staged-only ratio. The main deliverable was substituted with an evidence-backed text brief that scores ≥95% source-backed under the same audit. The pivot decision was driven by measurement, not by aesthetic judgment.
- **Engineering quality**: ruff + mypy 0 errors, 3-tier pytest layout (fast / domain / full), zero external runtime dependencies, an 8-rule self-evaluation framework that requires falsification criteria and ≥5-seed ensembles for any sensitivity claim.

---

## 3. Simulation / Game-AI roles

### 3.1 Korean (3 bullets)

- **Hazard-driven multi-agent 시뮬레이션** — 12 agent × 3 group × 200 tick × Poisson 사건 분포. agent dynamics (fear/hope/shame), group dynamics (mode/tension), world dynamics (mood/blame/suspicion/authority) 분리 모델링.
- **8 event type vocabulary** — public_denial / public_confession / public_accusation / forgiveness_emitted / visible_grief / visible_withdrawal / guard_approaches / discussion_emitted. emit는 engine 결정, 시각화는 별도 layer.
- **Deterministic-per-seed reproducibility** — 동일 seed → 동일 candidate set → 동일 brief. 2,026 fast test가 regression 차단. visual 실패가 engine 결정에 영향 0.

### 3.2 English (3 bullets)

- **Hazard-driven multi-agent simulation** — 12 agents in 3 groups over 200 ticks with Poisson event firing. Agent dynamics (fear / hope / shame), group dynamics (mode / tension), and world dynamics (mood / blame / suspicion / authority) are separately modeled and tested.
- **Engine-controlled event vocabulary** — 8 event types (denial / confession / accusation / forgiveness / grief / withdrawal / authority approach / discussion). Event emission is engine-deterministic; visualization is a strictly separate (and now frozen) layer.
- **Deterministic-per-seed reproducibility** — same seed produces same candidate set produces same brief. 2,026 fast tests guard the regression boundary. The visual track's freeze did not affect engine determinism.

---

## 4. AI Product / Systems roles

### 4.1 Korean (3 bullets)

- **AI 시스템에서 *측정 기반 product pivot* 사례** — visual prototype을 audit (3-class vocabulary)으로 평가, 27.9% staged 측정 직후 visual freeze + text-first 전환 결정. 5초 사용성 테스트 fail까지 portfolio surface로 기록.
- **Provenance class를 product surface로** — 모든 brief block에 source_derived / source_inferred / not_used 클래스 태그. 외부 검토자가 *어느 한 줄*의 출처를 추적 가능. RAG / agent system의 hallucination 추적과 동형 패턴.
- **Honest negative-result documentation** — visual freeze decision을 sunk cost가 아닌 *방법론 추출*로 framing. case study + visual appendix + resume bullet에 일관 transfer.

### 4.2 English (3 bullets)

- **A documented case of audit-driven product pivot in an AI system**: built a 3-class provenance vocabulary to score a visual prototype, measured 27.9% staged-only content, and pivoted the main deliverable to text — recording the 5-second usability test fail as a portfolio asset, not as a regret.
- **Provenance class as a product surface**: every block of the brief carries a `source_derived / source_inferred / not_used` tag. External reviewers can audit any single line. The pattern is transferable to any RAG or agent system that mixes raw output and interpretation.
- **Honest negative-result documentation**: the visual freeze decision is framed as *methodology extraction*, not sunk cost. The case study, the visual appendix, and the resume bullets all carry the same framing consistently.

---

## 5. Engineering manager / Tech lead variants

(Single bullet — pick one)

- **(Korean)** WITNESS 프로젝트에서 5주에 걸친 visual prototype의 audit failure (27.9% staged-only)를 신호로 *deliverable 자체를 substitute*하는 결정을 driving. 측정 vocabulary를 그대로 새 deliverable의 audit basis로 transfer해 후퇴가 아닌 방법론 추출로 portfolio 정렬. 2,026 test + 0 external deps + 4-layer additive architecture가 결정의 인프라 기반.
- **(English)** Drove a deliverable-substitution decision on the WITNESS project after a 5-week visual prototype's audit returned a 27.9% staged-only ratio. Transferred the audit vocabulary to the replacement deliverable so the pivot read as methodology extraction rather than retreat. Backed by 2,026 tests, zero external runtime dependencies, and a 4-layer additive architecture.

---

## 6. What NOT to write

These framings undercut the project's actual claim. Avoid:

- "Built an AI story generator" — WITNESS does not generate stories.
- "Visualized a multi-agent simulation" — the visual track is frozen.
  Claiming it as a deliverable contradicts the freeze decision.
- "Pivoted away from a failed visual experiment" — the experiment
  produced an audit instrument; "failed" is the wrong adjective.
- "Plan to ship the visual version" — explicitly out of scope until
  Phase 14 (Engine Event Log Adapter), which is deferred.
- "Religious / theological simulator" — domain content (peter, vangogh,
  talleyrand) is configurable, not central to the engineering claim.

---

## Cross-reference

- **Case study (full narrative)**: [WITNESS_CASE_STUDY_TEXT_FIRST.md](WITNESS_CASE_STUDY_TEXT_FIRST.md)
- **5-min demo (portfolio variant)**: [WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md](WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md)
- **Brief sample**: [WITNESS_OBSERVER_BRIEF_SAMPLE.md](WITNESS_OBSERVER_BRIEF_SAMPLE.md)
- **Visual experiment appendix**: [WITNESS_VISUAL_EXPERIMENT_APPENDIX.md](WITNESS_VISUAL_EXPERIMENT_APPENDIX.md)
- **Earlier draft (replaced)**: [APPLICATION_RESUME_BULLETS.md](APPLICATION_RESUME_BULLETS.md)
