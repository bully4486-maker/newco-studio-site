"""Deterministic content-hash cache: skip unchanged renders."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_inputs(cfg: dict[str, Any], root: Path, template_path: Path) -> dict[str, str]:
    """Stable map of input path -> sha256 for hashing."""
    items: dict[str, str] = {}
    items[str(template_path.relative_to(root))] = _file_sha256(template_path)

    assets = cfg.get("assets") or {}
    for key in ("logo", "phone_screen"):
        rel = assets.get(key)
        if not rel:
            continue
        p = root / rel
        if p.is_file():
            items[rel] = _file_sha256(p)

    music = cfg.get("music") or {}
    if music.get("file"):
        mp = root / music["file"]
        if mp.is_file():
            items[music["file"]] = _file_sha256(mp)

    # fonts referenced by template convention
    for font in ("vendor_assets/fonts/jakarta.woff2", "vendor_assets/fonts/inter.woff2"):
        fp = root / font
        if fp.is_file():
            items[font] = _file_sha256(fp)

    return items


def config_hash(cfg: dict[str, Any], root: Path, template_path: Path) -> str:
    payload = {
        "config": cfg,
        "inputs": collect_inputs(cfg, root, template_path),
        "renderer": "social-renderer/0.1.0",
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def cache_record_path(cache_dir: Path, master_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in master_id)
    return cache_dir / f"{safe}.json"


def is_fresh(cache_dir: Path, master_id: str, digest: str, outputs: list[Path]) -> bool:
    rec = cache_record_path(cache_dir, master_id)
    if not rec.is_file():
        return False
    try:
        data = json.loads(rec.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if data.get("hash") != digest:
        return False
    return all(p.is_file() for p in outputs)


def write_record(cache_dir: Path, master_id: str, digest: str, outputs: list[Path]) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    rec = {
        "hash": digest,
        "outputs": [str(p) for p in outputs],
    }
    cache_record_path(cache_dir, master_id).write_text(
        json.dumps(rec, indent=2) + "\n", encoding="utf-8"
    )
