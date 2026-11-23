"""Per-scene exclusive headline visibility — catches hook-ghost regressions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.render_engine import (  # noqa: E402
    STILL_TIMES,
    _launch_page,
    _page_payload,
    assert_scene_exclusive,
    scene_state_at,
)
from lib.validate import validate_config  # noqa: E402

SAMPLE = ROOT / "samples" / "master_websites99_916.json"

# Contact-sheet sample times → expected exclusive scene
EXPECT = {
    "hook": dict(expect_hook=True, expect_end=False, expect_cap=None),
    "phone": dict(expect_hook=False, expect_end=False, expect_cap=0),
    "caps": dict(expect_hook=False, expect_end=False, expect_cap=1),
    "exit": dict(expect_hook=False, expect_end=False, expect_cap=2),
    "endcard": dict(expect_hook=False, expect_end=True, expect_cap=None),
}


@pytest.fixture(scope="module")
def page_bundle():
    cfg = json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert validate_config(cfg, ROOT, for_video=False) == []
    assert "Menu, hours" not in json.dumps(cfg)
    template_path = ROOT / "templates" / f"{cfg['template_id']}.html"
    payload = _page_payload(cfg, ROOT, cover=False)
    pw, browser, page = _launch_page(template_path, payload)
    yield cfg, page
    browser.close()
    pw.stop()


@pytest.mark.parametrize("label,t", STILL_TIMES)
def test_exclusive_headline_per_still(page_bundle, label, t):
    _cfg, page = page_bundle
    state = scene_state_at(page, t)
    fails = assert_scene_exclusive(state, **EXPECT[label])
    assert fails == [], fails


@pytest.mark.parametrize("label,t", STILL_TIMES)
def test_no_layout_overlap_flags(page_bundle, label, t):
    _cfg, page = page_bundle
    page.evaluate("t => render(t)", t)
    result = page.evaluate("() => measureOverflow()")
    issues = result.get("issues") or []
    overlap = [i for i in issues if i.startswith("overlap:") or "hook" in i]
    assert overlap == [], f"{label}@{t}: {overlap}"


def test_sample_rejects_cafe_hook_copy():
    cfg = json.loads(SAMPLE.read_text(encoding="utf-8"))
    cfg["copy"]["hook_lines"] = ["Menu, hours & booking,", "one page"]
    errs = validate_config(cfg, ROOT, for_video=False)
    assert any("cafe_specific_hook" in e for e in errs)
