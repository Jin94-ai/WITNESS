"""Scripts package marker for rubric CLI tools (Phase 3.05).

Phase H + Phase 3.05 Rubric Design Review (`docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md`)
설계의 *실행 가능한 CLI 진입점*. engine/rubric/이 데이터구조를, scripts/rubric/이
실행 환경을 제공한다.

Rule #14: rubric은 evaluation-only — 학습 loss로 사용 0. 이 CLI는 *audit/classification*
도구일 뿐 training loop와 무관.
"""
