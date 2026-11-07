from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.cache import config_hash, is_fresh, write_record  # noqa: E402


def test_hash_stable_and_changes_with_copy(tmp_path: Path):
    cfg = json.loads((ROOT / "samples" / "master_websites99_916.json").read_text(encoding="utf-8"))
    tpl = ROOT / "templates" / f"{cfg['template_id']}.html"
    h1 = config_hash(cfg, ROOT, tpl)
    h2 = config_hash(cfg, ROOT, tpl)
    assert h1 == h2
    cfg["copy"]["cta"] = "Ask for a quote"
    h3 = config_hash(cfg, ROOT, tpl)
    assert h3 != h1


def test_cache_skip_when_outputs_exist(tmp_path: Path):
    out = tmp_path / "sheet.png"
    out.write_bytes(b"png")
    cache_dir = tmp_path / "cache"
    write_record(cache_dir, "m1", "abc", [out])
    assert is_fresh(cache_dir, "m1", "abc", [out])
    assert not is_fresh(cache_dir, "m1", "zzz", [out])
    out.unlink()
    assert not is_fresh(cache_dir, "m1", "abc", [out])
