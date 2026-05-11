# WITNESS Portfolio — Reading Order

> Last updated: 2026-05-10 (Phase 2.9 hierarchy 정리)

이 폴더는 *외부 reviewer / 면접관 / 새 사용자*가 WITNESS를 30초 ~ 5분 안에
이해할 수 있도록 정리된 portfolio 자산이다. 메인 → evidence → appendix
순으로 읽는다.

---

## 1. Main Portfolio Demos (먼저 보세요)

### 1.1 Genre Comparison Demo (메인)

```
docs/portfolio/demo_genre_comparison/index.html
```

**5초 인상**: 같은 universal skeleton이 *한국 아침 막장 드라마* vs *일본
정적 드라마*로 서로 다르게 펼쳐지는 모습을 side-by-side로 보여준다.

### 1.2 Flesh Baseline Demo (Phase 3.1 prep)

```
docs/portfolio/demo_flesh_baseline/index.html
```

**5초 인상**: 각 universal seed가 어떤 장르 flesh와 잘 맞는지를 *설명 가능한
weighted rule score*로 보여준다. 점수마다 reason_features (axis match /
pressure overlap) 첨부. ML 0 / fine-tuning 0.

→ [docs/portfolio/FLESH_BASELINE_DEMO.md](FLESH_BASELINE_DEMO.md) — Target A (seed × profile fit) + Target B (episode intensity, script-only) + Target C (ranked top-K, 아래) + bridge + verifier 모두 cover.

### 1.2.0 Episode Intensity Demo (Phase 3.1 Target B, fixture-only)

```
docs/portfolio/demo_episode_intensity/index.html
```

**5초 인상**: 10 episodes × 2 genres (= 20 intensity points) — 각 *에피소드*가 장르 시그니처 (한국 아침 막장 / 일본 정적)에 얼마나 부합하는지 weighted score. title × genre arc bar chart + per-record feature contributions. **Fictional fixture-only** banner — `tests/fixtures/annotation_public_safe/` (가공된 가상 인물) 기반, 실제 방송 데이터 0.

→ schema_version `episode_intensity_v1` (Plan §22.2 Target B, cycle 10 + cycle 40 fixture-only deploy). Operating Guide §9 deploy 카테고리: `fixture-only`. Phase 3.0 pilot 진입 후 실제 데이터로 교체 가능. 재현 명령: `scripts/annotation/{run_episode_intensity, build_episode_intensity_demo}.py --fixture-only`.

### 1.2.1 Adaptation Recommendation Demo (Phase 3.1 Target C, prep)

```
docs/portfolio/demo_adaptation_recommendation/index.html
```

**5초 인상**: 4 universal seed 각각에 대해 *어떤 장르로 각색하면 좋은지* ranked top-K 추천. Target A의 flat list를 *seed별 grouped + score 내림차순*으로 재구성. 1순위 장르 분포 bar + seed별 ranked card view. Non-Claims + Prep-mode (rulebook-only) + uncalibrated banner.

→ schema_version `adaptation_recommendation_v1` (Plan §22.3 Target C, cycle 17-19). 재현 명령: `scripts/narrative/run_adaptation_recommendation.py` + `scripts/narrative/build_adaptation_recommendation_demo.py`.

### 1.2.2 Rubric Discovery Candidate Classifier Demo (Phase 3.05, 29 cycle)

```
docs/portfolio/demo_rubric/README.md                        (cover doc)
docs/portfolio/demo_rubric/ensemble_visualization.html      (Result-11 visual asset)
docs/portfolio/demo_rubric/character_discrimination.{json,md}      (review §5 empirical)
docs/portfolio/demo_rubric/alignment_*.{json,md}            (review §2.5 P1 extended)
docs/portfolio/demo_rubric/character_axis_anti_*.{json,md}  (cycle 26 N-case ensemble)
```

**5초 인상**: 4-Axis Discovery **Candidate Classifier** (Character / Canon / Causal / Novelty 독립 critic + 8-step flowchart). 8 trajectory variants → 7 distinct discovery classes 모두 시연. 3 ensembles (cross_scenario 19/20 + multi_agent 14/15 + multi_seed 4/5) HTML 통합. review §2.3 minimum gate / §2.5 pressure-action alignment / §5 discrimination 양방향 empirical 입증.

→ [docs/witness_rubric_design.md](../witness_rubric_design.md) + [docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](../WITNESS_V3_RUBRIC_DESIGN_REVIEW.md) — 29 cycle 누적 / 123+ tests / Acceptance §7 17+/17+ ✅. Rule #14 (학습 loss 0) + scalar 합산 0 + uncalibrated_phase3_placeholder 명시.

### 1.3 (메인 vs prep 차이)

| 측면 | Genre Comparison | Flesh Baseline |
|---|---|---|
| 단계 | Phase 2.8 (완료) | Phase 3.1 prep (Phase 3.0 후 갱신) |
| 입력 | SkeletonOutput v1.1 + 2 rulebooks | SkeletonOutput v1.1 + 2 GenreProfiles |
| 출력 | side-by-side 회차 흐름 | seed별 genre fit score + recommendation |
| ML 사용 | 0 | 0 (Phase 3.0 데이터로도 No-ML 유지) |

**무엇이 보이는가**:
- 장르 렌즈 (한 줄 요약) preview
- 입력 universal skeleton (4 anchor-clean seeds)
- 두 장르 column: 회차 흐름 (rhythm × phase template), 마지막 질문(cliffhanger)
- 왜 다르게 나오는가 (rulebook conflict_amplifier 인용)
- Evidence preservation (펼침)
- Technical Appendix (펼침)

**audit**: pass + quality_warnings 0건 (자동 검증)

→ [docs/portfolio/GENRE_ADAPTER_DEMO.md](GENRE_ADAPTER_DEMO.md) — 어댑터 사용법 / 신뢰성 검증 / 시연 절차

---

## 2. Core Evidence

### 2.1 Skeleton Output (universal seed)

```
docs/portfolio/demo/skeleton_output.json
docs/portfolio/demo/index.html              (Peter scarcity baseline)
```

input universal skeleton의 deployed 샘플. anchor-clean (인물 이름 / 정경 사건 0).

### 2.2 Genre Comparison Output

```
docs/portfolio/demo_genre_comparison/comparison.json
data/narrative/genre_comparison_output.json   (machine-readable mirror)
```

머신 판독용 cross-genre 변환 결과. comparison_summary로 두 장르 차이 요약.

### 2.3 Audit Reports

```
docs/plans/GENRE_ADAPTER_MVP_AUDIT.md         (Phase 2.75)
docs/plans/GENRE_ADAPTER_POLISH_AUDIT.md      (Phase 2.8)
docs/plans/VALIDATION_REPORT_2026_05_09_FIXES.md  (Phase 2.5)
```

- Phase 2.5: skeleton output v1.1 의미 보존성 검증 (Phase 3 GO 판정)
- Phase 2.75: rule-based adapter 작동 증명 (Phase 3 GO 판정)
- Phase 2.8: portfolio polish (12/12 acceptance, No-Go 0건)

### 2.4 Schema Version Map

```
docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md
```

`skeleton_output_v1` (frozen container) / `universal_story_seed_v1_1` /
`genre_adapted_output_v1_1` / `genre_comparison_output_v1` 관계 설명.

### 2.5 RFC

```
docs/plans/RFC_TEMPLATE.md
docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md   (RFC-0001, approved)
```

---

## 3. Single-genre Demos (Appendix)

```
docs/portfolio/demo_genre/index.html              (한국 아침 막장 드라마)
docs/portfolio/demo_genre_japanese/index.html     (일본 정적 드라마)
```

각 장르 단일 변환 결과. comparison demo가 메인이지만, 단일 장르 톤을 자세히
보고 싶을 때 사용.

---

## 4. Earlier Demos (Appendix)

이전 단계 산출물. Phase 2.9 정리 후 *appendix*로 분류 — 메인 흐름이 아니라
점진적 개선 과정의 evidence.

### 4.1 Peter Story Demo (Phase 2 portfolio)

```
docs/portfolio/demo/index.html                 (Peter scarcity baseline)
docs/portfolio/demo/episode_outline.md
docs/portfolio/demo/story_seed_cards.md
docs/portfolio/demo/run_log.md
docs/portfolio/demo/evidence_report.md
```

universal skeleton의 *deployed sample* (Phase 2 portfolio demo). Genre Adapter의
입력으로 사용.

### 4.2 Life Arc Narrative

```
docs/portfolio/demo/life_arc_demo.html         (5 phases)
docs/portfolio/demo/life_arc_demo_by_week.html (21 weeks)
docs/portfolio/demo/life_arc_seed_diversity.md
```

베드로 공생애 142일 timeline narrative — Phase 2 prep 단계 산출물.

### 4.3 Story Candidate Cards

```
docs/portfolio/STORY_CANDIDATES.md
docs/portfolio/CROSS_SEED_STORY_PATTERNS.md
docs/portfolio/story_candidate_console.html
```

Phase 2 prep — Story Emergence 단계 cards (4 candidates: Peter / Andrew /
James / John).

### 4.4 Visual Prototypes (frozen)

```
docs/visual/VISUAL_TRACK_FREEZE_DECISION.md
docs/portfolio/WITNESS_VISUAL_EXPERIMENT_APPENDIX.md
```

5 sub-track visual experiment 모두 frozen (2026-05-06 결정). 메인 산출물 아님.

---

## 5. Resume / Cover Letter / Interview

```
docs/portfolio/APPLICATION_RESUME_BULLETS.md
docs/portfolio/COVER_LETTER_SNIPPETS.md
docs/portfolio/INTERVIEW_STORY_BANK.md
docs/portfolio/DEMO_GUIDE_FOR_PORTFOLIO.md
docs/portfolio/INTERNAL_TO_EXTERNAL_TERMS.md
```

지원서 / 면접 / 시연 문서 — Phase 2.9 후속 정리 가능.

---

## 6. 어떻게 시연하는가

### 30초 소개

```
"WITNESS는 결정론적 시뮬레이션 엔진(뼈대) + rule-based 장르 변환기(살)의
이중 구조 포트폴리오입니다. 같은 universal skeleton이 한국 아침 막장
드라마와 일본 정적 드라마로 서로 다르게 펼쳐지는 과정을 보여줍니다."
```

→ [demo_genre_comparison/index.html](demo_genre_comparison/index.html)을 연다.

### 5초 안에 보이는 것

1. 두 장르 lens preview (한 줄씩)
2. universal skeleton 4 seeds (plain Korean labels)
3. side-by-side 회차 흐름 (rhythm step별 다른 한 줄)
4. 마지막 질문(cliffhanger)이 장르마다 다름

### 60초 follow-up

- "왜 다르게 나오는가" 섹션 (rulebook conflict_amplifier)
- evidence preservation (source_seed_id / conflict_axis 보존)
- audit pass + quality_warnings 0건

### 5분 deep dive

- Phase 2.5 validation fix → universal_story_seed v1.1
- Phase 2.75 rule-based MVP → GenreAdaptedOutput
- Phase 2.8 polish → structured outline + lens + soft audit
- Phase 3.0 plan (사용자 승인 대기)

---

## 7. 한 줄 결론

```
Genre Comparison Demo가 메인.
나머지는 evidence + appendix.
ML Flesh Engine은 Phase 3.0 통과 후 진행 예정.
```
