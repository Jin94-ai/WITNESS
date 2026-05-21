# Universal Engine → Drama Pipeline

> **30초 안에 파악**: 4문단 요약 + 메인 시각화 link.

📺 **메인 데모**: [index.html](index.html) — 브라우저로 바로. 다이어그램 + seed별 실제 결과 비교.

---

## 무엇을 만들었나

베드로의 인생을 컴퓨터 시뮬레이션으로 돌려서 "어느 날 무슨 일이 있었는지"를 한국어 요약으로 자동 생성하고, 그 요약을 한국 드라마 학습 모델(KoBART)에 넣어서 **드라마 풍 장면 대본으로 변환하는 파이프라인**. 한 번 실행하면 5단계가 자동으로 흐르고(약 20초), 입력 seed를 바꾸면 다른 시뮬레이션 결과 → 다른 드라마 장면이 나옵니다. 결정론적 시뮬레이션(같은 입력 → 같은 결과)과 ML 학습 모델(KoBART)을 **하나의 파이프라인**으로 연결한 것이 핵심입니다.

## 왜 만들었나

WITNESS 프로젝트의 원래 비전은 "시뮬레이션 + ML"의 결합이었습니다. 시뮬레이션은 **사건의 구조**(누가 누구에게 어떤 압력을 받아 어떻게 행동했나)를 결정하고, ML은 그 구조에 **표현의 옷**(드라마 대본 형식, 한국어 스타일)을 입히는 역할. 두 갈래가 따로 개발돼서 **연결되지 않은 채 종결**될 뻔했고, 이 데모가 그 연결고리를 실제로 만들어서 검증합니다. 면접·포트폴리오에서 "두 기술을 한 파이프라인으로 통합한 경험"을 보여주려는 목적.

## 어떻게 작동하나

5단계 chain:
1. **시뮬레이션** — `PhasedSimulationWorld`로 베드로 142일 인생을 결정론적으로 돌림 (seed 0/1/2 다르면 다른 결과).
2. **한국어 narrative 합성** — 시뮬레이션 결과 + 정경 사건 트리거 정보를 4-5개 phase window로 묶어 한국어 줄거리 생성.
3. **Summary 어댑터** — 각 window의 줄거리를 약 171자(KoBART 학습 시 평균 길이)로 자르고 `<fm_drama> Summary:` 형식으로 포장.
4. **KoBART 추론** — 한국 가족극/단막극 32K 페어로 fine-tune한 모델(`models/kobart_v2`)에 입력. fp16 GPU 추론, beam search.
5. **드라마 풍 장면 출력** — 학습된 `해설]/인물]/지문` 형식의 한 장면.

산출물 두 가지: 사람이 읽는 마크다운 (`pipeline_result.md`) + 자동화용 JSON (`pipeline_result.json`).

## 무엇을 배웠나

**작동한 것**: 전체 chain이 한 명령에 끝까지 흐름. 결정론(seed 동일=결과 동일) 보장. 입력 시드의 핵심 어휘(베드로/시몬/그물/예수)가 출력에 보존됨. 학습된 대본 형식이 자연스럽게 적용됨. **한계**: KoBART 학습 데이터(한국 가족극)와 입력 도메인(정경 narrative)이 달라서 출력 품질이 MVP 수준 — 반복 loop(`morpheme_repeat` 83% on Stage 2 eval), 일부 영어 토큰 hallucination. 1개 reference 기준 BLEU/ROUGE는 절대값 천장이 낮음(같은 입력에 valid 출력 다수 가능). **결론**: "드라마 학습이 완성됐다"가 아닌 "**MVP 수준 chain 검증**" — 구조 연결 가능성 입증, 출력 품질은 추가 학습/도메인 데이터 필요.

---

## 한눈에 chain

```
[Universal Engine]  →  [Life Arc]      →  [Summary Adapter]    →  [KoBART]     →  [드라마 풍 장면]
   시뮬레이션         한국어 timeline       171자 + control token    학습 모델       해설]/인물]
   (결정론)          (합성)                (정렬)                  (ML 추론)       (산출)
```

매 실행 ~20초.

## 실행

```bash
# 1) 한 번 실행 (시뮬레이션 → 드라마 출력)
python -m scripts.pipeline.universal_to_drama --seed 0 --genre fm_drama

# 2) 다른 seed / genre / 5단계 (수난 포함)
python -m scripts.pipeline.universal_to_drama --seed 1 --genre fs_drama
python -m scripts.pipeline.universal_to_drama --seed 3 --genre fm_drama --full-passion

# 3) 시각화 재생성 (모든 실행 결과 → index.html)
python -m scripts.pipeline.build_pipeline_visual
```

Python 3.11 + CUDA 권장. KoBART 체크포인트(`models/kobart_v2/`)는 gitignored — 학습 결과 별도 보관.

## 미리 만들어진 6 sample runs

| Seed | Genre | Days | Windows | elapsed |
|---:|---|---:|---:|---:|
| 0 | fm_drama (가족극) | 101.2 | 4 | 21s |
| 1 | fm_drama | 101.2 | 4 | 21s |
| 1 | fs_drama (단막극) | 101.2 | 4 | 21s |
| 2 | fm_drama | 101.2 | 4 | 21s |
| 2 | fs_drama | 101.2 | 4 | 21s |
| 3 | fm_drama + 수난 | 140+ | 5 | 28s |

각 폴더(`seed{N}_{genre}/`)에 `.md` + `.json` 두 형식.

## 정직성 (필수 disclosure)

✅ **검증됨**
- end-to-end chain 작동 (5단계 한 명령)
- 결정론 (같은 seed → 같은 결과)
- 시드 어휘 보존
- 학습된 장면 형식 적용

⚠️ **한계**
- 학습 도메인(한국 드라마) ≠ 입력 도메인(정경) → 어색한 출력
- KoBART 알려진 실패 모드: 반복 loop + 일부 영어 hallucination
- 1개 reference로 BLEU/ROUGE 평가 본질적 한계
- 실제 시청자 평가 없음 (구조 검증 단계)

📌 **claim 경계**
- "드라마 학습 완성"이 아닌 "MVP chain 검증"
- 출력은 가독성보다 *구조 연결 증거*

---

## Source

- 파이프라인: [scripts/pipeline/universal_to_drama.py](../../../scripts/pipeline/universal_to_drama.py) (340 lines)
- 시각화 빌더: [scripts/pipeline/build_pipeline_visual.py](../../../scripts/pipeline/build_pipeline_visual.py)
- 시뮬레이션 base: [engine/simulation/phased_world.py](../../../engine/simulation/phased_world.py) + [engine/observer/life_arc_narrative.py](../../../engine/observer/life_arc_narrative.py)
- 모델 학습 history: [docs/results/witness_final/](../../results/witness_final/) (11 정리 파일)
- Lessons L46-L55 (시각화 설계 근거): [lessons.md](../../../lessons.md)
