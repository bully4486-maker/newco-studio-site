from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.banned import scan_text  # noqa: E402
from lib.validate import validate_config  # noqa: E402

SAMPLE = ROOT / "samples" / "master_websites99_916.json"


@pytest.fixture
def cfg():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def test_sample_config_valid_for_preview(cfg):
    assert validate_config(cfg, ROOT, for_video=False) == []


def test_sample_config_valid_for_video_with_test_only(cfg):
    assert validate_config(cfg, ROOT, for_video=True) == []


def test_rejects_missing_master_id(cfg):
    del cfg["master_id"]
    errs = validate_config(cfg, ROOT)
    assert any("master_id" in e for e in errs)


def test_rejects_banned_founding_copy(cfg):
    cfg["copy"]["footnote"] = "Founding offer for early customers"
    errs = validate_config(cfg, ROOT)
    assert any("founding_offer" in e for e in errs)


def test_rejects_fictional_badge(cfg):
    cfg["copy"]["phone_label"] = "Demo site · fictional business"
    errs = validate_config(cfg, ROOT)
    assert any("banned" in e or "phone_label" in e for e in errs)


def test_rejects_first_3_clients(cfg):
    cfg["copy"]["checks"][0] = "First 3 clients get a discount"
    errs = validate_config(cfg, ROOT)
    assert any("first_3_clients" in e for e in errs)


def test_rejects_mtd_ready(cfg):
    cfg["copy"]["end_title"] = "MTD-ready bookkeeping"
    errs = validate_config(cfg, ROOT)
    assert any("mtd_ready" in e for e in errs)


def test_rejects_hearth_crumb_republish(cfg):
    cfg["copy"]["hook_lines"][0] = "Hearth & Crumb style"
    errs = validate_config(cfg, ROOT)
    assert any("hearth_crumb" in e for e in errs)


def test_rejects_overflow_hook(cfg):
    cfg["copy"]["hook_lines"][0] = "A" * 40
    errs = validate_config(cfg, ROOT)
    assert any("hook_lines[0]" in e for e in errs)


def test_rejects_video_without_music(cfg):
    cfg["music"] = None
    errs = validate_config(cfg, ROOT, for_video=True)
    assert any("video requires music" in e for e in errs)


def test_rejects_platform_only_music(cfg):
    cfg["music"] = {
        "test_only": False,
        "title": "Some track",
        "artist_or_uploader": "x",
        "source_url": "https://example.com",
        "licence": "unknown",
        "licence_url": "https://example.com",
        "cross_platform_ok": True,
        "platform_only": True,
        "file": "fixtures/test_only_audio/TEST_ONLY_silent_1s.wav",
    }
    errs = validate_config(cfg, ROOT, for_video=True)
    assert any("platform_only" in e for e in errs)


def test_rejects_publication_claim_on_test_fixture(cfg):
    m = copy.deepcopy(cfg["music"])
    m["test_only"] = False
    m["cross_platform_ok"] = True
    m["title"] = "City Loop"
    m["licence"] = "CC0"
    cfg["music"] = m
    errs = validate_config(cfg, ROOT, for_video=True)
    assert any("TEST_ONLY" in e for e in errs)


def test_banned_voiceover_scan():
    assert "voiceover" in scan_text("Add a voice-over here")
    assert "comedy" in scan_text("quick comedy skit")
