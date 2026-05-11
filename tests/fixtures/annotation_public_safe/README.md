# Phase 3.0 v1.1 — Public-safe Annotation Fixtures

> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §8.2.

이 디렉토리의 fixture는 **순수 fictional / 저작권 안전한 샘플**이다.
실제 방송 회차 데이터가 아니다 — Mode A 파이프라인이 작동하는지 *외부 데이터
없이* 검증하기 위한 demo 샘플.

```text
사용 목적:
  1. Phase 3.0 §10.2 실행 흐름 시연 (정상 path)
  2. 신규 사용자가 Mode A 운영 절차를 따라할 수 있는 reference
  3. CI / fast suite에서 e2e 파이프라인 동작 검증

내용:
  - synopsis_raw_demo/    fictional synopsis 5개 (titleA × 5)
  - annotation_outputs_demo/  fictional 2-model annotation (10 outputs)

원칙:
  - 모든 텍스트는 가공된 가상 인물 (시뮬레이터의 universal seed에서 inspired)
  - 특정 작품 / 인물명 모방 0
  - 한국어 기본
  - 저작권 위험 0 (fixture/ 안에서만 추적)
```

---

## 사용

```bash
# 1. raw → normalized
python scripts/data/normalize_synopsis.py \
    --input tests/fixtures/annotation_public_safe/synopsis_raw_demo \
    --output /tmp/phase3_demo_norm.jsonl

# 2. validate
python scripts/data/validate_synopsis_dataset.py \
    --input /tmp/phase3_demo_norm.jsonl

# 3. annotation_inputs
python scripts/data/build_annotation_inputs.py \
    --input /tmp/phase3_demo_norm.jsonl \
    --output /tmp/phase3_demo_inputs

# 4. (실제 pilot에서는 수동 LLM annotation)
#    Demo에서는 미리 만들어둔 annotation_outputs_demo/를 사용
cp tests/fixtures/annotation_public_safe/annotation_outputs_demo/*.json /tmp/phase3_demo_outputs/

# 5. validate outputs + hallucination check
python scripts/annotation/validate_annotation_outputs.py \
    --input /tmp/phase3_demo_outputs \
    --synopsis /tmp/phase3_demo_norm.jsonl \
    --hallucination-report /tmp/halluc.json

# 6. feature matrix
python scripts/annotation/build_feature_matrix.py \
    --input /tmp/phase3_demo_outputs \
    --output /tmp/feat_matrix.csv

# 7. reliability
python scripts/annotation/build_reliability_report.py \
    --features /tmp/feat_matrix.csv \
    --output /tmp/reliability.json
```

---

*이 fixture는 *공개 가능*. 모든 텍스트는 fictional이며 외부 작품을
인용하지 않는다.*
