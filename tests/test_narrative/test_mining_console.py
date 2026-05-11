"""Smoke tests for the Narrative Mining Console (Phase 5)."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_mining_console",
        ROOT / "scripts" / "narrative" / "build_mining_console.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_mining_console"] = mod
    spec.loader.exec_module(mod)
    return mod


bmc = _load_builder()


def _run(tmp_path, *, with_data: bool = True):
    """Run the console builder. If with_data=False, point at empty fixtures."""
    out = tmp_path / "console.html"
    if with_data:
        bmc.main(
            "data/narrative/narrative_opportunities.json",
            "data/narrative/story_threads.json",
            "data/narrative/moments.json",
            "data/visual/dot_observer_data.json",
            str(out),
        )
    else:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        for name in ("ops.json", "threads.json", "moments.json", "observer.json"):
            (empty_dir / name).write_text("{}", encoding="utf-8")
        bmc.main(
            str(empty_dir / "ops.json"),
            str(empty_dir / "threads.json"),
            str(empty_dir / "moments.json"),
            str(empty_dir / "observer.json"),
            str(out),
        )
    return out


def test_console_html_renders(tmp_path):
    out = _run(tmp_path)
    html = out.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>")
    assert "WITNESS" in html
    assert "Narrative Mining Console" in html


def test_console_embeds_data_payloads(tmp_path):
    out = _run(tmp_path)
    html = out.read_text(encoding="utf-8")
    # Each application/json block carries a non-empty JSON object
    for tag_id in ("data-opportunities", "data-threads", "data-moments", "data-meta"):
        m = re.search(
            rf'<script type="application/json" id="{tag_id}">(.*?)</script>',
            html, re.DOTALL,
        )
        assert m is not None, f"{tag_id} script tag missing"
        payload = json.loads(m.group(1))
        assert isinstance(payload, dict)


def test_console_embedded_threads_match_source(tmp_path):
    out = _run(tmp_path)
    html = out.read_text(encoding="utf-8")
    src_threads = json.loads(
        Path("data/narrative/story_threads.json").read_text(encoding="utf-8")
    )
    m = re.search(
        r'<script type="application/json" id="data-threads">(.*?)</script>',
        html, re.DOTALL,
    )
    embedded = json.loads(m.group(1))
    src_ids = [t["thread_id"] for t in src_threads.get("threads", [])]
    emb_ids = [t["thread_id"] for t in embedded.get("threads", [])]
    assert src_ids == emb_ids


def test_console_no_external_assets(tmp_path):
    out = _run(tmp_path)
    html = out.read_text(encoding="utf-8")
    # Plan §11: no external lib / asset
    forbidden = (
        "<script src=", "<link rel=\"stylesheet\"",
        "fonts.googleapis", "cdn.jsdelivr", "unpkg.com", "ajax.googleapis",
    )
    for f in forbidden:
        assert f not in html, f"forbidden external asset reference: {f}"


def test_console_handles_empty_data_gracefully(tmp_path):
    """When all input files are empty {} dicts, builder should not crash and
    HTML should still render (no thread cards but page intact)."""
    out = _run(tmp_path, with_data=False)
    html = out.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "WITNESS" in html


def test_console_no_hardcoded_hero():
    src = (ROOT / "scripts" / "narrative" / "build_mining_console.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden hero '{forbidden}' in console builder"


def test_console_self_contained_size_reasonable(tmp_path):
    out = _run(tmp_path)
    size = out.stat().st_size
    # Self-contained but should not balloon (200 ticks × 12 agents = ~824KB observer
    # but we only embed moments/threads/ops, ~50KB total)
    assert 10_000 < size < 500_000, f"console size {size} outside expected band"
