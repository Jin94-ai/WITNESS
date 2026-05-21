# WITNESS Portfolio — Reading Order

> Last updated: 2026-05-15 (post-cleanup) — 외부 reviewer / 면접관 / 새 사용자가 30초 ~ 5분 안에 이해.

---

## 1. 메인 데모 (먼저 보세요)

### 1.1 Universal Engine → Drama Pipeline 🆕

```
docs/portfolio/demo_universal_to_drama/index.html
```

**5초 인상**: WITNESS의 *전체 chain*이 한눈에. 결정론적 시뮬레이션(베드로 anchor) → 한국어 narrative → KoBART 학습 모델 → 한국 드라마 풍 한 장면. 5단계 다이어그램 + seed/genre 선택 시 다른 결과. 매 실행 ~20초.

→ [demo_universal_to_drama/README.md](demo_universal_to_drama/README.md) — 사용법 + 6 sample runs + 정직성 disclosure

### 1.2 Life Arc Narrative

```
docs/portfolio/demo/life_arc_demo.html
```

**5초 인상**: 베드로 시뮬레이션 142일 (실측 101.2일) 한국어 timeline. 4 phase (소명/갈릴리/고백/여정) + 정경 사건 + seed별 다른 행동 선택.

재생성:
```bash
python -m scripts.narrative.run_life_arc_demo --seed 0
```

### 1.3 Story Emergence Console

```
docs/portfolio/narrative_mining_console.html
docs/portfolio/story_candidate_console.html
```

**5초 인상**: 시뮬레이션에서 *의미 있는 순간*(Moment) 자동 추출 → Thread → Opportunity. 105 moments / by_type + by_provenance 분류.

---

## 2. 학습 트랙 — Track A 종결 보고

```
docs/results/witness_final/                    # 11 정리 파일
  ├── inventory.json                           # 산출물 119개
  ├── metrics_summary.md                       # 라벨링 + 학습 + 실패 모드
  ├── qualitative_summary.md                   # 정성 평가
  ├── trajectory.md                            # 시간순 event
  ├── data_spec.md                             # 데이터 파이프라인
  ├── model_spec.md                            # 3 모델 학습 설정
  ├── env.md                                   # 환경 + 알려진 이슈
  ├── taxonomy_summary.md                      # 뼈대 정의 + 표현 공간
  ├── labeling_track_summary.md                # Stage별 분포
  ├── learning_inputs_summary.md               # 학습 입력 검증
  └── discrepancies.md                         # 데이터 불일치 7건
```

**핵심 수치**:
- Gemma 라벨링: Stage 2 54% → 2.2 88% → Stage 3 ChatGPT 60% (평가자 28%p 차이)
- group_tension primary 218/225 (97%) — attractor 패턴
- KoBART Stage 1 (S1): BLEU 6.12 / Stage 2 (S2): **BLEU 7.53** / Qwen LoRA: BLEU 5.66
- Universal Taxonomy 표현 공간: 704 조합 중 111 (16%) 사용

---

## 3. 면접 / 자소서용 자산

| 문서 | 용도 |
|---|---|
| [APPLICATION_RESUME_BULLETS.md](APPLICATION_RESUME_BULLETS.md) | 이력서 bullets |
| [COVER_LETTER_SNIPPETS.md](COVER_LETTER_SNIPPETS.md) | 자기소개서 |
| [INTERVIEW_STORY_BANK.md](INTERVIEW_STORY_BANK.md) | 면접 답변 후보 |
| [DEMO_GUIDE_FOR_PORTFOLIO.md](DEMO_GUIDE_FOR_PORTFOLIO.md) | 5분 라이브 데모 |
| [VERBAL_DEMO_SCRIPT_5MIN.md](VERBAL_DEMO_SCRIPT_5MIN.md) | 구두 demo 스크립트 |
| [TARGET_ROLES_AND_POSITIONING.md](TARGET_ROLES_AND_POSITIONING.md) | 지원 역할 매핑 |
| [WITNESS_RESUME_BULLETS_FINAL.md](WITNESS_RESUME_BULLETS_FINAL.md) | 최종 bullet |

---

## 4. 아키텍처 + 위험 메모

| 문서 | 용도 |
|---|---|
| [ARCHITECTURE_FOR_PORTFOLIO.md](ARCHITECTURE_FOR_PORTFOLIO.md) | reviewer용 아키텍처 |
| [PORTFOLIO_PUBLIC_RELEASE_RISK_MEMO.md](PORTFOLIO_PUBLIC_RELEASE_RISK_MEMO.md) | 공개 위험 |
| [PORTFOLIO_ASSET_CHECKLIST.md](PORTFOLIO_ASSET_CHECKLIST.md) | 자산 체크리스트 |
| [PORTFOLIO_README_DRAFT.md](PORTFOLIO_README_DRAFT.md) | reviewer용 GitHub README 초안 |

---

## 5. 추가 데모 (선택)

| 문서 | 내용 |
|---|---|
| [STORY_VIABILITY_REPORT.md](STORY_VIABILITY_REPORT.md) | Story Viability validation 결과 |
| [HUMAN_PICK_RESULT.md](HUMAN_PICK_RESULT.md) + [HUMAN_PICK_TEST_PACK.md](HUMAN_PICK_TEST_PACK.md) | 사람 선택 비교 |
| [NARRATIVE_OPPORTUNITIES.md](NARRATIVE_OPPORTUNITIES.md) | 채굴된 narrative opportunities |
| [STORY_CANDIDATES.md](STORY_CANDIDATES.md) | 후보 목록 |
| [SCENE_BRIEFS.md](SCENE_BRIEFS.md) + [ONE_PAGE_TREATMENTS.md](ONE_PAGE_TREATMENTS.md) | 장면/원페이지 treatment |
| [CROSS_SEED_STORY_PATTERNS.md](CROSS_SEED_STORY_PATTERNS.md) | seed 간 패턴 |
| [INTERNAL_TO_EXTERNAL_TERMS.md](INTERNAL_TO_EXTERNAL_TERMS.md) | 내부 용어 → 외부 용어 매핑 |

---

## 6. Archive 안내

2026-05-15 cleanup으로 archive 이동된 자산:
- Genre Adapter (Flesh ①) + Phase 3.0/3.1 prep → `archive/frozen_flesh_adapter_2026_05_15/`
- Rubric (Discovery Candidate Classifier) → `archive/frozen_rubric_2026_05_15/`
- Visual track (PSD/PEP/WFO) → `archive/frozen_visual_2026_05_15/`
- Legacy scripts (v0.5/v0.7 paper era) → `archive/legacy_scripts_2026_05_15/`

→ [docs/DEPRECATED_TRACKS.md](../DEPRECATED_TRACKS.md) — 정책 + active 트랙 정의

---

## 7. 한 줄

**현재 메인** = [demo_universal_to_drama/index.html](demo_universal_to_drama/index.html) (5단계 chain 시각화 + 6 runs)
**Track A 종결 보고** = [docs/results/witness_final/](../results/witness_final/) (11 정리 파일)
**면접 자료** = §3
