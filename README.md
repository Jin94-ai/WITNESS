# WITNESS

> 결정론적 인물 시뮬레이션 + ML 학습 모델을 **한 파이프라인으로 연결**한 narrative 생성 프로젝트.
> 시뮬레이션은 "어떤 일이 일어났나(구조)"를 만들고, ML은 "어떻게 표현할까(드라마 풍)"를 입힙니다.

---

## 5초로 보기

**메인 데모**: 브라우저로 [docs/portfolio/demo_universal_to_drama/index.html](docs/portfolio/demo_universal_to_drama/index.html) 열기.

5단계 파이프라인 다이어그램 + seed 바꾸면 다른 결과 + 정직성 disclosure. 외부 의존 0 (single HTML).

```
[시뮬레이션] → [한국어 narrative] → [Summary 정렬] → [KoBART] → [드라마 풍 장면]
   (결정론)      (4-5 phase windows)   (≈171자)         (학습)      (해설]/인물])
```

---

## 30초로 보기

1. **무엇**: 베드로(이외 8명 anchor) 인생을 컴퓨터 시뮬레이션으로 돌려서 한국어 줄거리 만들고, 한국 드라마 32K 페어로 학습한 KoBART 모델에 넣어서 드라마 풍 장면으로 변환.
2. **왜**: 결정론적 시뮬레이션과 ML 학습이 따로 개발되어 *연결되지 않은 상태*였음. 이 파이프라인이 두 갈래를 한 명령으로 잇는 연결고리.
3. **어떻게**: PhasedSimulationWorld 시뮬레이션 → `life_arc_narrative` 한국어 합성 → `<fm_drama> Summary: ...` 형식으로 정렬 → KoBART fp16 추론 → 대본 형식 출력. 한 번 실행 ~20초.
4. **무엇을 배웠나**: chain 자체는 작동하지만 학습 도메인(한국 가족극) ≠ 입력 도메인(정경) 때문에 출력은 MVP 수준. 반복 loop + 일부 hallucination. *"드라마 학습 완성"이 아닌 "MVP 수준 chain 검증"*.

상세: [docs/portfolio/demo_universal_to_drama/README.md](docs/portfolio/demo_universal_to_drama/README.md)

---

## 빠른 실행

### 의존성

- Python 3.11 (3.14는 PyTorch CUDA 미지원)
- CUDA GPU 권장 (8GB+, fp16 추론)
- `pip install -r requirements.txt` (torch / transformers 4.45.2 / peft / bitsandbytes 등)

### Pipeline (시뮬레이션 → 드라마 변환)

```bash
# 한 번 실행
python -m scripts.pipeline.universal_to_drama --seed 0 --genre fm_drama

# 다른 조합
python -m scripts.pipeline.universal_to_drama --seed 1 --genre fs_drama
python -m scripts.pipeline.universal_to_drama --seed 3 --genre fm_drama --full-passion

# 시각화 재생성
python -m scripts.pipeline.build_pipeline_visual

# 결과
docs/portfolio/demo_universal_to_drama/index.html        # 메인 시각화
docs/portfolio/demo_universal_to_drama/seed{N}_{genre}/  # 개별 run (.md + .json)
```

> 모델 체크포인트(`models/kobart_v2/`)는 `.gitignore`. 학습 재생성은 `scripts/witness_train/stage2_2_train_kobart_v2.py` (24분, RTX 2070 SUPER).

### 시뮬레이션 단독 (KoBART 없이)

```bash
# 베드로 인생 시뮬레이션 → 한국어 narrative
python -m scripts.narrative.run_life_arc_demo --seed 0

# 결과
docs/portfolio/demo/life_arc_demo.html
docs/portfolio/demo/life_arc_demo.md
docs/portfolio/demo/life_arc_demo.json
```

### 테스트

```bash
# Fast tests (~90초, 2,095 pass)
pytest -m "not slow and not archived" -q
```

---

## Repo 구조 (post-cleanup 2026-05-15)

```
engine/                    # Universal Engine (anchor-agnostic)
  core/ rules/ simulation/ rendering/
  observer/                # taxonomy + Story Emergence
  anchor/                  # AnchorRegistry (인물명 binding)
  {person,persona,population,world,...}/  # 시뮬레이션 코어

drama_mining/              # Track A: AI-Hub 023 데이터 로더
scripts/
  pipeline/                # 🆕 universal_to_drama end-to-end
  labeling/                # Track A 라벨링 (Gemma)
  witness_train/           # Track A 학습 (KoBART + Qwen LoRA)
  narrative/               # Story Emergence + Life Arc
  observer/ story/ skeleton/

content/                   # 8 인물 anchor + universal taxonomy
docs/
  portfolio/               # 외부 reviewer용 (메인 demo_universal_to_drama/)
  results/witness_final/   # Track A 종결 보고 (11 정리 파일)
  plans/                   # RFC + governance

archive/                   # 2026-05-15 cleanup 이동
  frozen_flesh_adapter/    # Genre Adapter (Phase 2.75-3.05) — history
  frozen_rubric/           # Discovery Candidate Classifier
  frozen_visual/           # PSD/PEP/WFO viewer track
  legacy_scripts/          # v0.5/v0.7 paper era
```

상세: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) + [docs/DEPRECATED_TRACKS.md](docs/DEPRECATED_TRACKS.md)

---

## 핵심 자산

| 자산 | 위치 | 설명 |
|---|---|---|
| **메인 시각화** | [docs/portfolio/demo_universal_to_drama/index.html](docs/portfolio/demo_universal_to_drama/index.html) | 5초 / 30초 / 5분 모든 깊이 |
| **포트폴리오 안내** | [docs/portfolio/README.md](docs/portfolio/README.md) | reviewer 진입점 |
| **Track A 종결 보고** | [docs/results/witness_final/](docs/results/witness_final/) | 11 정리 파일 (metrics / trajectory / discrepancies) |
| **설계서** | [DESIGN.md](DESIGN.md) | 아키텍처 + 4층 엔진 |
| **Lessons** | [lessons.md](lessons.md) | L1-L88 (4주 누적 패턴) |
| **HARNESS 원칙** | [docs/HARNESS.md](docs/HARNESS.md) | H1-H8 자가감사 |

---

## Project 상태

- **Track A (드라마 학습 ML)**: MVP 인정 후 마무리. KoBART Stage 2 best val_loss 2.95 / BLEU 7.53.
- **Universal Engine**: anchor-agnostic FROZEN contract (RFC-0001). 베드로 / 반 고흐 / 탈레랑 등 8 anchor 지원.
- **Pipeline (universal_to_drama)**: 2026-05-15 신규. 두 갈래 연결 완성.
- **테스트**: 2,095 fast pass / 0 fail / 0 regression (post-cleanup baseline).

---

## License / 데이터

- 코드: WIP 포트폴리오 (개인 프로젝트)
- AI-Hub 023 데이터: 비상업 학술 사용 (raw passage 재배포 금지). 학습 결과 공개 시 출처 인용 필수.
- 정경(성경) 텍스트: 개역개정 (공개 도메인 기준).

---

> **궁극 비전**: 플레이어가 역사적 인물의 삶을 *목격자*로 체험하는 narrative simulator.
> 묻습니다: **"무엇이 그 순간 갈림길을 만들었나?"**
