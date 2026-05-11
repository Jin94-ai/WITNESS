"""Demo: Creative IP track (J-Alpha + J-Beta) - single entry point.

Usage:
    python examples/demo_creative.py                # 기본 (요약 출력)
    python examples/demo_creative.py --trilogy      # scarcity trilogy 3-act narrative
    python examples/demo_creative.py --all-anchors  # 5 anchors x 5 seeds = 25 stories 생성
    python examples/demo_creative.py --status       # Creative IP track 진행 상태

J-Alpha + J-Beta Creative IP Track:
- "같은 anchor의 5 seed가 서로 다른 한국어 이야기로 읽히는가?" 가설 1차 증명 (PASS 5/6)
- 5 anchor library + scarcity trilogy nonmonotonic IP narrative

산출 파일은 모두 outputs/creative_demo/ 에 위치.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def cmd_status() -> int:
    print("=" * 70)
    print("WITNESS Creative IP Track - Status (2026-04-28)")
    print("=" * 70)
    print()
    print("J-Alpha (1차 증명): PASS 5/6 (Peter scarcity baseline)")
    print("J-Beta (확장): selector queryable + 5 anchors + scarcity trilogy")
    print()
    print("Anchors (5):")
    print("  - peter_scarcity_baseline (PASS, 3 distinct outcomes)")
    print("  - peter_scarcity_high_density (READY, 자율 follow-up 발견)")
    print("  - peter_scarcity_double (J-Beta, 2 distinct, escalation)")
    print("  - peter_scarcity_triple (J-Beta, REC modal - nonmonotonic)")
    print("  - vangogh_sacred_baseline (FAIL, transparency 보존)")
    print()
    print("Scarcity Trilogy (1/2/3 accusations):")
    print("  Act I  - 한 번의 비난: SAT modal")
    print("  Act II - 두 번의 비난: SAT modal (escalation)")
    print("  Act III - 세 번의 비난: REC modal (nonmonotonic 회복)")
    print()
    print("Outputs (outputs/creative_demo/):")
    out_dir = ROOT / "outputs" / "creative_demo"
    if out_dir.exists():
        for f in sorted(out_dir.glob("*.txt")):
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.1f} KB)")
    else:
        print("  (Run --all-anchors or --trilogy first)")
    print()
    print("Renderer 상태: Cycle 7 FREEZE (Lee Type E directive, 2026-04-29)")
    print("  v3 평가 완료. Cycle 8 진행 안 함. Branch C 결과 후 분기.")
    print("  결정 doc: docs/creative/RENDERER_FREEZE_DECISION.md")
    print()
    print("Lee Gate (대기) 1개:")
    print("  Branch C send -> docs/b_direction/BRANCH_C_18_PROBES_SEND_BUNDLE.md")
    print("  (18 probe 익명화 P_NEW_01..18, GPT-5.5 paste-ready)")
    print("  응답 저장: docs/b_direction/BRANCH_C_GPT55_RESPONSE_RAW.md")
    print()
    print("Branch C 결과 자동 분기:")
    print("  Case S (4/5+ PASS) -> creative asset pack v1 plan")
    print("  Case M (2-3 PASS) -> 내부 데모만, Branch C lock 보류")
    print("  Case F (실패)     -> renderer 중단, 구조/평가 재검토")
    print()
    print("  Renderer 진행 상태 (6 cycles 누적, 2026-04-29):")
    print("    Cycle 1 (자율, 4-28): scarcity opening 5 / cross-scenario REC / anchor signature")
    print("    Cycle 2 (Lee v2 부분 통과 후): A/B/C - phrase de-template + outcome rhythm + LOW branch")
    print("    Cycle 3 (Type D 1차):       D/E/F - scenario x outcome SAT/MIXED + opening/pool 확장")
    print("    Cycle 4 (Type D 2차):       G/H   - accusation REC sharpness + PARTIAL x scenario")
    print("    Cycle 5 (Type D 3차):       I     - scene-level micro-action (Stage 2.5 zoom-in)")
    print("    Cycle 6 (Type D 4차):       J     - Trilogy Act II escalation envelope")
    print("    Retrospective (this LOOP): docs/creative/RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md")
    print()
    print("  Lee v2 약점 5/5 모두 처리 완료. Pool: 30 -> 176 sentence templates (+487%).")
    print("  119/119 test_story PASS / 96/96 forbidden audit clean (회귀 ZERO).")
    print()
    print("  Gate 1 v3 (대기): Lee 평가 시 Cycle 1-6 누적 효과 확인")
    print("    Lee 평가 양식: docs/creative/RENDERER_GATE1_V3_RESULTS.md")
    print("    Cycle별 sample diff: gate1_v3/v4/v5/v6/v7_samples.md (5 file)")
    print()
    print("  (참고) Gate 2 (variation IP 가치): A (PASS) 응답 -> J-Beta 진행 완료")
    print()
    print("Type B-2 directive (POST_TYPE_B_EXTERNAL_GATE, 2026-04-29):")
    print("  4 경우 분기 ready-to-resume:")
    print("    A) Gate 1 v2 명확 -> docs/creative/RENDERER_CYCLE_2_PLAN.md (우선 개선 2/3)")
    print("    B) GPT-5.5 강 긍정 -> docs/b_direction/BRANCH_C_LOCK_DECISION.md + creative asset pack")
    print("    C) GPT-5.5 애매 -> Branch C hold + creative output 중심")
    print("    D) Renderer 매우 부정 -> docs/creative/RENDERER_CORE_REPAIR_PLAN.md (style 이전 core repair)")
    print("  자율 가능 (결과 수신 후): plan doc / before-after sample / variation review update")
    print("  forbidden_now 9 (Type B 7 + research deepening + paper 확장 + 새 자율 루프)")
    print()
    print("주요 docs:")
    print("  docs/CREATIVE_TRACK_TRANSITION.md - 트랙 전환 공식")
    print("  docs/WITNESS_NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md - Type B directive (forbidden_now 명시)")
    print("  docs/WITNESS_POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE.md - Type B-2 (외부 판독 분기 사전 정의)")
    print("  docs/creative/J_BETA_PROGRESS.md - J-Beta 진행")
    print("  docs/creative/PETER_5_VARIATION_COMPARISON.md - Anchor 1 평가")
    print("  docs/creative/PETER_TWO_ANCHOR_COMPARISON.md - cell 비교")
    print("  docs/creative/VARIATION_READING_REVIEW.md - J-Alpha verdict")
    return 0


def cmd_trilogy() -> int:
    print("Generating scarcity trilogy (modal 3-act + full 15-story view)...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "story" / "generate_trilogy_view.py")],
        env={"PYTHONHASHSEED": "0", "PATH": str(Path.cwd())},
    )
    return result.returncode


def cmd_all_anchors() -> int:
    print("Generating 5 anchor variation bundles (25 stories)...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "story" / "generate_anchor_variations.py")],
        env={"PYTHONHASHSEED": "0", "PATH": str(Path.cwd())},
    )
    return result.returncode


def main() -> int:
    if len(sys.argv) < 2:
        return cmd_status()  # default: status

    arg = sys.argv[1]
    if arg == "--status":
        return cmd_status()
    if arg == "--trilogy":
        return cmd_trilogy()
    if arg == "--all-anchors":
        return cmd_all_anchors()

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
