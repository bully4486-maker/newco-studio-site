from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.render_engine import render_contact_sheet, render_cover  # noqa: E402
from lib.validate import validate_config  # noqa: E402

SAMPLE = ROOT / "samples" / "master_websites99_916.json"


@pytest.mark.slow
def test_contact_sheet_and_cover(tmp_path: Path):
    cfg = json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert validate_config(cfg, ROOT, for_video=False) == []
    sheet = tmp_path / "contact.png"
    path, overflow = render_contact_sheet(cfg, ROOT, sheet)
    assert path.is_file()
    assert path.stat().st_size > 10_000
    cover = tmp_path / f"{cfg['master_id']}_cover_1080x1920.png"
    # render_contact_sheet writes cover beside sheet using master id naming in parent
    cover_actual = sheet.parent / f"{cfg['master_id']}_cover_1080x1920.png"
    assert cover_actual.is_file()
    # Soft assert: overflow list must be empty for the approved sample
    assert overflow == [], overflow


def test_cover_dimensions(tmp_path: Path):
    from PIL import Image

    cfg = json.loads(SAMPLE.read_text(encoding="utf-8"))
    out = tmp_path / "cover.png"
    issues = render_cover(cfg, ROOT, out)
    assert out.is_file()
    im = Image.open(out)
    assert im.size == (1080, 1920)
    assert issues == []
