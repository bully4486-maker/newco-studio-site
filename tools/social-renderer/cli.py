#!/usr/bin/env python3
"""Offline NewCo social master renderer CLI.

Adapted from local video_poc/render3.py + template3.html.
No LLM / SaaS calls. Default output: PNG contact sheet + matching cover.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.cache import config_hash, is_fresh, write_record  # noqa: E402
from lib.render_engine import render_contact_sheet, render_video  # noqa: E402
from lib.validate import validate_config  # noqa: E402


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="NewCo social renderer (offline, config-driven)")
    p.add_argument("config", type=Path, help="Path to master JSON config")
    p.add_argument(
        "--mode",
        choices=("preview", "video", "validate"),
        default="preview",
        help="preview=contact sheet+cover (default); video needs music meta; validate=checks only",
    )
    p.add_argument("--out-dir", type=Path, default=ROOT / "out")
    p.add_argument("--cache-dir", type=Path, default=ROOT / ".cache")
    p.add_argument("--force", action="store_true", help="Ignore hash cache")
    p.add_argument("--batch", type=Path, help="Directory of *.json configs to render")
    args = p.parse_args(argv)

    configs: list[Path]
    if args.batch:
        configs = sorted(args.batch.glob("*.json"))
        if not configs:
            print(f"no configs in {args.batch}", file=sys.stderr)
            return 2
    else:
        configs = [args.config]

    exit_code = 0
    for cfg_path in configs:
        code = _run_one(cfg_path, args)
        exit_code = max(exit_code, code)
    return exit_code


def _run_one(cfg_path: Path, args: argparse.Namespace) -> int:
    cfg = load_config(cfg_path)
    for_video = args.mode == "video"
    errors = validate_config(cfg, ROOT, for_video=for_video)
    if errors:
        print(f"REJECT {cfg_path.name}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    if args.mode == "validate":
        print(f"OK {cfg['master_id']} ({cfg['template_id']})")
        return 0

    master = cfg["master_id"]
    out_dir = args.out_dir / master
    out_dir.mkdir(parents=True, exist_ok=True)
    template_path = ROOT / "templates" / f"{cfg['template_id']}.html"
    digest = config_hash(cfg, ROOT, template_path)

    if args.mode == "preview":
        sheet = out_dir / f"{master}_contact_sheet.png"
        cover = out_dir / f"{master}_cover_1080x1920.png"
        outputs = [sheet, cover]
        if not args.force and is_fresh(args.cache_dir, master, digest, outputs):
            print(f"CACHE hit {master} — skip (hash {digest[:12]})")
            return 0
        path, overflow = render_contact_sheet(cfg, ROOT, sheet)
        if overflow:
            print(f"OVERFLOW {master}:", file=sys.stderr)
            for o in overflow:
                print(f"  - {o}", file=sys.stderr)
            return 3
        write_record(args.cache_dir, master, digest, outputs)
        print(f"WROTE {path}")
        print(f"WROTE {cover}")
        print(f"HASH  {digest}")
        return 0

    # video
    video = out_dir / f"{master}_1080x1920.mp4"
    outputs = [video]
    if not args.force and is_fresh(args.cache_dir, master + ":video", digest, outputs):
        print(f"CACHE hit {master} video — skip (hash {digest[:12]})")
        return 0
    overflow = render_video(cfg, ROOT, video)
    if overflow:
        print(f"OVERFLOW/FFMPEG {master}:", file=sys.stderr)
        for o in overflow:
            print(f"  - {o}", file=sys.stderr)
        # treat layout overflow as failure; ffmpeg notes too
        if any(not o.startswith("ffmpeg") for o in overflow) or any(
            o.startswith("ffmpeg exit") for o in overflow
        ):
            return 3
    write_record(args.cache_dir, master + ":video", digest, outputs)
    size_mb = video.stat().st_size / (1024 * 1024)
    print(f"WROTE {video} ({size_mb:.1f} MB)")
    if cfg.get("music", {}).get("test_only"):
        print("NOTE: TEST ONLY audio — not publication-ready; do not claim a music licence.")
    print(f"HASH  {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
