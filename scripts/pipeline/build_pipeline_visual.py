"""Build portfolio visualization for Universal Engine → Drama Pipeline.

모든 docs/portfolio/demo_universal_to_drama/seed*_*/pipeline_result.json을
수집해 single self-contained HTML로 시각화.

설계 원칙 (lessons L46-L55):
  - 구성 차원 우선 (배치/위계) > 어휘 patch (색상)
  - audit instrument 정직성 — 무엇이 실제 시뮬레이션이고 무엇이 학습 출력인지 분리
  - 5초 테스트: 한눈에 chain 보임 + 실제 데이터 검증 가능

Usage:
    "C:/Program Files/Python311/python.exe" -m scripts.pipeline.build_pipeline_visual

Output: docs/portfolio/demo_universal_to_drama/index.html
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "docs" / "portfolio" / "demo_universal_to_drama"


# ============================================================
# Data collection
# ============================================================

def collect_runs() -> list[dict]:
    runs = []
    for sub in sorted(DEMO_DIR.glob("seed*_*")):
        f = sub / "pipeline_result.json"
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            d["run_id"] = sub.name
            runs.append(d)
    return runs


# ============================================================
# HTML rendering
# ============================================================

def esc(s: str | None) -> str:
    return html.escape(s or "", quote=True)


def truncate(s: str, n: int = 500) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + "…"


def render_html(runs: list[dict]) -> str:
    runs_json = json.dumps(runs, ensure_ascii=False)

    # Pipeline diagram boxes
    diagram = """
    <div class="diagram">
      <div class="step" data-step="1">
        <div class="step-num">1</div>
        <div class="step-name">Universal Engine</div>
        <div class="step-detail">PhasedSimulationWorld<br>anchor + seed</div>
        <div class="step-meta">결정론적</div>
      </div>
      <div class="arrow">→</div>
      <div class="step" data-step="2">
        <div class="step-num">2</div>
        <div class="step-name">Life Arc</div>
        <div class="step-detail">한국어 narrative<br>phase windows</div>
        <div class="step-meta">합성</div>
      </div>
      <div class="arrow">→</div>
      <div class="step" data-step="3">
        <div class="step-num">3</div>
        <div class="step-name">Summary Adapter</div>
        <div class="step-detail">≈171자 추출<br>&lt;genre&gt; Summary 형식</div>
        <div class="step-meta">정렬</div>
      </div>
      <div class="arrow">→</div>
      <div class="step kobart" data-step="4">
        <div class="step-num">4</div>
        <div class="step-name">KoBART</div>
        <div class="step-detail">Stage 2 S2 학습<br>123.9M params · fp16</div>
        <div class="step-meta">ML 추론</div>
      </div>
      <div class="arrow">→</div>
      <div class="step output" data-step="5">
        <div class="step-num">5</div>
        <div class="step-name">드라마 풍 장면</div>
        <div class="step-detail">해설] / 인물]<br>대본 형식</div>
        <div class="step-meta">산출</div>
      </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Universal Engine → Drama Pipeline — WITNESS</title>
<style>
  :root {{
    --bg: #fafaf9;
    --fg: #1a1a1a;
    --muted: #6b6b6b;
    --border: #d4d4d2;
    --accent: #2c5f7c;
    --kobart: #7a4a8c;
    --output: #2d6a3e;
    --input-bg: #f0f4f7;
    --output-bg: #f5f0f7;
    --warn-bg: #fef9e7;
    --warn-border: #e0c068;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 0;
    font-family: -apple-system, "Segoe UI", "Noto Sans KR", sans-serif;
    background: var(--bg); color: var(--fg);
    line-height: 1.55;
    font-size: 14px;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px 32px 48px; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ margin: 0 0 4px; font-size: 22px; font-weight: 600; }}
  .subtitle {{ color: var(--muted); font-size: 13px; }}
  .project-tag {{
    display: inline-block; padding: 2px 8px; margin-right: 8px;
    background: var(--accent); color: white; border-radius: 3px; font-size: 11px;
    font-weight: 500; letter-spacing: 0.3px;
  }}

  /* Pipeline diagram */
  section h2 {{ font-size: 16px; margin: 28px 0 12px; font-weight: 600; }}
  .diagram {{
    display: flex; align-items: stretch; gap: 6px;
    background: white; padding: 18px;
    border: 1px solid var(--border); border-radius: 6px;
    margin-bottom: 8px; overflow-x: auto;
  }}
  .step {{
    flex: 1; min-width: 140px;
    padding: 10px 12px;
    background: var(--input-bg);
    border-radius: 5px;
    display: flex; flex-direction: column;
    text-align: center;
    position: relative;
  }}
  .step.kobart {{ background: var(--output-bg); }}
  .step.output {{ background: #ecf6ee; }}
  .step-num {{
    position: absolute; top: -8px; left: -8px;
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--fg); color: white;
    font-size: 12px; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
  }}
  .step.kobart .step-num {{ background: var(--kobart); }}
  .step.output .step-num {{ background: var(--output); }}
  .step-name {{ font-weight: 600; font-size: 13px; margin-bottom: 4px; }}
  .step-detail {{ font-size: 11px; color: var(--muted); line-height: 1.4; }}
  .step-meta {{
    font-size: 10px; margin-top: 6px;
    color: var(--muted); font-style: italic;
  }}
  .arrow {{
    display: flex; align-items: center;
    color: var(--muted); font-size: 18px;
    padding: 0 2px;
  }}

  .diagram-caption {{
    font-size: 11px; color: var(--muted);
    margin-top: 4px; margin-bottom: 24px;
  }}

  /* Run selector */
  .selector {{
    background: white; padding: 14px 18px;
    border: 1px solid var(--border); border-radius: 6px;
    display: flex; gap: 16px; align-items: center;
    margin-bottom: 16px; flex-wrap: wrap;
  }}
  .selector label {{ font-size: 12px; color: var(--muted); margin-right: 6px; }}
  .selector select {{
    padding: 5px 10px; border: 1px solid var(--border);
    border-radius: 3px; font-size: 13px;
    background: var(--bg);
  }}
  .meta-chips {{
    margin-left: auto; display: flex; gap: 8px;
    font-size: 11px;
  }}
  .chip {{
    padding: 3px 8px; background: var(--input-bg);
    border-radius: 3px; color: var(--muted);
  }}
  .chip strong {{ color: var(--fg); }}

  /* Window cards */
  .window-card {{
    background: white; border: 1px solid var(--border);
    border-radius: 6px; margin-bottom: 14px; overflow: hidden;
  }}
  .window-head {{
    background: #f5f5f3; padding: 8px 14px;
    border-bottom: 1px solid var(--border);
    font-weight: 600; font-size: 13px;
    display: flex; justify-content: space-between;
  }}
  .window-head .lens {{ font-size: 11px; color: var(--muted); font-weight: normal; }}
  .window-body {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0;
  }}
  .col {{ padding: 12px 14px; }}
  .col + .col {{ border-left: 1px solid var(--border); background: var(--output-bg); }}
  .col-label {{
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;
    color: var(--muted); margin-bottom: 6px; font-weight: 600;
  }}
  .col-label .badge {{
    display: inline-block; padding: 1px 6px; margin-left: 6px;
    border-radius: 2px; font-size: 9px; background: var(--accent); color: white;
    text-transform: none; letter-spacing: 0;
  }}
  .col + .col .col-label .badge {{ background: var(--kobart); }}
  .col-content {{
    font-size: 12.5px; line-height: 1.55;
    white-space: pre-wrap; word-break: break-word;
    color: #2a2a2a;
  }}

  /* Disclosure */
  .disclosure {{
    background: var(--warn-bg); border: 1px solid var(--warn-border);
    padding: 14px 18px; border-radius: 5px;
    margin-top: 24px; font-size: 12.5px;
  }}
  .disclosure h3 {{ margin: 0 0 8px; font-size: 13px; }}
  .disclosure ul {{ margin: 4px 0; padding-left: 20px; }}
  .disclosure li {{ margin: 2px 0; }}

  footer {{
    margin-top: 32px; padding-top: 16px;
    border-top: 1px solid var(--border);
    font-size: 11px; color: var(--muted);
  }}
  code {{
    background: #efeeec; padding: 1px 5px;
    border-radius: 2px; font-size: 11px;
    font-family: "SF Mono", Consolas, monospace;
  }}
</style>
</head>
<body>
<div class="container">

  <header>
    <h1><span class="project-tag">WITNESS</span>Universal Engine → Drama Pipeline</h1>
    <div class="subtitle">결정론적 시뮬레이션 + ML 학습 결합 — Anchor 시뮬레이션을 한국 드라마 풍으로 변환</div>
  </header>

  <section>
    <h2>1. 파이프라인 구조</h2>
    {diagram}
    <div class="diagram-caption">
      매 실행 시 5단계 모두 작동 (~20초). Step 1–3은 결정론적 (seed 동일 시 같은 결과), Step 4 KoBART는 fp16 추론.
    </div>
  </section>

  <section>
    <h2>2. 실행 결과 (다른 seed / genre 선택)</h2>
    <div class="selector">
      <div><label>Seed:</label><select id="sel-seed"></select></div>
      <div><label>Genre:</label><select id="sel-genre"></select></div>
      <div class="meta-chips" id="meta-chips"></div>
    </div>
    <div id="windows-container"></div>
  </section>

  <section>
    <h2>3. 정직성 — 무엇이 실제이고 무엇이 한계인가</h2>
    <div class="disclosure">
      <h3>✅ 검증된 부분</h3>
      <ul>
        <li><strong>전체 chain end-to-end 작동</strong>: 시뮬레이션 → narrative → KoBART → 출력이 한 명령으로.</li>
        <li><strong>결정론</strong>: seed 0 / seed 1 결과 다름. 같은 seed 반복 시 같은 결과.</li>
        <li><strong>시드 어휘 보존</strong>: KoBART 출력에 입력 시드의 핵심 토큰 (베드로 / 시몬 / 그물 / 예수) 유지.</li>
        <li><strong>장면 형식</strong>: 학습된 대본 형식 (<code>해설]</code> / <code>인물명]</code>) 자연 적용.</li>
      </ul>
      <h3>⚠️ 한계 (도메인 mismatch)</h3>
      <ul>
        <li><strong>학습 도메인</strong>: KoBART는 한국 가족극 / 단막극 32K 페어로 학습 — 정경 narrative 도메인 외.</li>
        <li><strong>반복 loop</strong>: KoBART 알려진 실패 모드 (<code>morpheme_repeat</code> 83% on Stage 2 eval). "어머님! 어머님!" 등 학습 데이터 패턴 누설.</li>
        <li><strong>일부 영어 토큰 hallucination</strong>: 학습 데이터 OOV로 인한 fallback.</li>
        <li><strong>1개 reference로 평가 불가</strong>: 같은 시드 → 다수의 valid 결과 존재 가능 — BLEU/ROUGE 절대값 천장 낮음.</li>
      </ul>
      <h3>📌 포트폴리오 claim 한계</h3>
      <ul>
        <li>"드라마 학습이 완료됐다"가 아닌 "<strong>MVP 수준의 chain 검증</strong>".</li>
        <li>출력은 <em>가독성</em>이 아닌 <em>구조 검증</em>의 증거.</li>
        <li>실제 한국 드라마 시청자 평가는 진행하지 않음.</li>
      </ul>
    </div>
  </section>

  <footer>
    데이터: <code>scripts/pipeline/universal_to_drama.py</code>가 매 실행 시 생성.
    Anchor: <code>peter_scarcity_baseline</code> (다른 anchor 추가는 별도 작업).
    Model: KoBART Stage 2 (val_loss 2.9516, BLEU-4 7.53).
    Lessons: L46–L55 (visual track 교훈 — 어휘 patch ≠ 구성 fix).
  </footer>

</div>

<script>
const RUNS = {runs_json};

function unique(arr) {{ return [...new Set(arr)]; }}

function render() {{
  const seedSel = document.getElementById('sel-seed');
  const genreSel = document.getElementById('sel-genre');
  const seed = parseInt(seedSel.value);
  const genre = genreSel.value;
  const run = RUNS.find(r => r.seed === seed && r.doc_type === genre);
  const container = document.getElementById('windows-container');
  const meta = document.getElementById('meta-chips');
  if (!run) {{
    container.innerHTML = '<div style="padding:12px;color:#888">해당 조합의 run 없음. 다른 seed/genre 시도.</div>';
    meta.innerHTML = '';
    return;
  }}
  meta.innerHTML = `
    <span class="chip">elapsed <strong>${{run.elapsed_sec}}s</strong></span>
    <span class="chip">windows <strong>${{run.windows.length}}</strong></span>
    <span class="chip">total days <strong>${{run.total_days.toFixed(1)}}</strong></span>
    <span class="chip">anchor <strong>${{run.anchor}}</strong></span>
  `;
  container.innerHTML = run.windows.map((w, i) => `
    <div class="window-card">
      <div class="window-head">
        <span>Window ${{i+1}}${{w.phase_label ? ' — ' + w.phase_label : ''}}</span>
        <span class="lens">input ${{w.summary_input_len}}자 → output ${{w.drama_output_len}}자</span>
      </div>
      <div class="window-body">
        <div class="col">
          <div class="col-label">Universal Engine 합성 <span class="badge">결정론적</span></div>
          <div class="col-content">${{escapeHtml(w.summary_input)}}</div>
        </div>
        <div class="col">
          <div class="col-label">KoBART 변환 <span class="badge">ML 추론</span></div>
          <div class="col-content">${{escapeHtml(w.drama_output)}}</div>
        </div>
      </div>
    </div>
  `).join('');
}}

function escapeHtml(s) {{
  return (s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);
}}

function init() {{
  const seeds = unique(RUNS.map(r => r.seed)).sort((a,b) => a-b);
  const genres = unique(RUNS.map(r => r.doc_type));
  const seedSel = document.getElementById('sel-seed');
  const genreSel = document.getElementById('sel-genre');
  seeds.forEach(s => {{ const o=document.createElement('option'); o.value=s; o.textContent='seed '+s; seedSel.appendChild(o); }});
  genres.forEach(g => {{ const o=document.createElement('option'); o.value=g; o.textContent=g; genreSel.appendChild(o); }});
  seedSel.addEventListener('change', render);
  genreSel.addEventListener('change', render);
  render();
}}
init();
</script>
</body>
</html>
"""


def main() -> int:
    runs = collect_runs()
    if not runs:
        print(f"[visual] No runs in {DEMO_DIR}", file=sys.stderr)
        return 1
    print(f"[visual] collected {len(runs)} runs:", file=sys.stderr)
    for r in runs:
        print(f"  {r['run_id']}: {len(r['windows'])} windows, {r['elapsed_sec']}s", file=sys.stderr)
    html_str = render_html(runs)
    out = DEMO_DIR / "index.html"
    out.write_text(html_str, encoding="utf-8")
    print(f"[visual] wrote {out} ({len(html_str):,} chars)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
