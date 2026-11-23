"""Playwright + optional ffmpeg renderer. Adapted from video_poc/render3.py."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from .contact_sheet import build_contact_sheet
from .music import resolve_audio_path


W, H = 1080, 1920
DEFAULT_FPS = 30
DEFAULT_DUR = 15.0
# Key times for contact sheet / covers (deterministic)
STILL_TIMES = [
    ("hook", 0.8),
    ("phone", 4.0),
    ("caps", 7.2),
    ("exit", 11.0),
    ("endcard", 14.0),
]
COVER_TIME = 4.0


def _page_payload(cfg: dict[str, Any], root: Path, *, cover: bool = False) -> dict[str, Any]:
    copy = cfg["copy"]
    assets = cfg["assets"]

    def uri(rel: str) -> str:
        return (root / rel).resolve().as_uri()

    return {
        "hook_lines": copy["hook_lines"],
        "caps": copy["caps"],
        "end_title": copy["end_title"],
        "price": copy["price"],
        "checks": copy["checks"],
        "footnote": copy["footnote"],
        "url": copy["url"],
        "cta": copy["cta"],
        "phone_label": copy["phone_label"],
        "bottom_tag": copy["bottom_tag"],
        "logo": uri(assets["logo"]),
        "phone_screen": uri(assets["phone_screen"]),
        "cover_mode": cover,
        "show_safe": bool(cfg.get("show_safe")),
    }


def _launch_page(template_path: Path, payload: dict[str, Any]):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        args=["--no-sandbox", "--force-color-profile=srgb"],
    )
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto(template_path.resolve().as_uri())
    page.wait_for_timeout(200)
    page.evaluate("d => setData(d)", payload)
    page.evaluate("() => document.fonts.ready")
    return pw, browser, page


def check_overflow_at(page, t: float) -> list[str]:
    result = page.evaluate("t => render(t)", t)
    issues = (result or {}).get("issues") or []
    return list(issues)


def scene_state_at(page, t: float) -> dict:
    return page.evaluate("t => sceneState(t)", t)


def assert_scene_exclusive(state: dict, *, expect_hook: bool, expect_end: bool, expect_cap: int | None) -> list[str]:
    """Return list of assertion failures for exclusive scene headlines."""
    fails: list[str] = []
    hook_on = state.get("hook", 0) >= 0.2
    end_on = state.get("end", 0) >= 0.2
    caps = state.get("caps") or []
    vis_caps = [i for i, o in enumerate(caps) if o >= 0.2]

    if expect_hook and not hook_on:
        fails.append(f"t={state.get('t')}: expected hook visible")
    if not expect_hook and hook_on:
        fails.append(f"t={state.get('t')}: hook ghost still visible ({state.get('hook'):.2f})")
    if expect_end and not end_on:
        fails.append(f"t={state.get('t')}: expected endcard visible")
    if not expect_end and end_on:
        fails.append(f"t={state.get('t')}: endcard unexpectedly visible")
    if expect_hook and vis_caps:
        fails.append(f"t={state.get('t')}: caps visible during hook: {vis_caps}")
    if expect_end and vis_caps:
        fails.append(f"t={state.get('t')}: caps visible during endcard: {vis_caps}")
    if expect_cap is not None:
        if expect_cap not in vis_caps:
            fails.append(f"t={state.get('t')}: expected cap[{expect_cap}] visible, got {vis_caps}")
        # At most one dominant cap (allow brief crossfade: max 2, but primary must win)
        if len(vis_caps) > 2:
            fails.append(f"t={state.get('t')}: too many caps visible: {vis_caps}")
        if vis_caps and caps[expect_cap] < max(caps) - 0.05:
            fails.append(f"t={state.get('t')}: cap[{expect_cap}] not dominant")
    return fails


def render_stills(
    cfg: dict[str, Any],
    root: Path,
    out_dir: Path,
    *,
    times: list[tuple[str, float]] | None = None,
) -> tuple[list[tuple[str, Path]], list[str]]:
    template_path = root / "templates" / f"{cfg['template_id']}.html"
    payload = _page_payload(cfg, root, cover=False)
    times = times or STILL_TIMES
    out_dir.mkdir(parents=True, exist_ok=True)

    pw, browser, page = _launch_page(template_path, payload)
    frames: list[tuple[str, Path]] = []
    overflow: list[str] = []
    try:
        for label, t in times:
            issues = check_overflow_at(page, t)
            for iss in issues:
                overflow.append(f"{label}@{t}: {iss}")
            path = out_dir / f"still_{label}_{t:.1f}.png"
            page.screenshot(path=str(path), type="png")
            frames.append((f"{label} t={t:.1f}s", path))
    finally:
        browser.close()
        pw.stop()
    return frames, overflow


def render_cover(cfg: dict[str, Any], root: Path, out_path: Path) -> list[str]:
    template_path = root / "templates" / f"{cfg['template_id']}.html"
    payload = _page_payload(cfg, root, cover=True)
    pw, browser, page = _launch_page(template_path, payload)
    try:
        issues = check_overflow_at(page, COVER_TIME)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out_path), type="png")
    finally:
        browser.close()
        pw.stop()
    return issues


def render_contact_sheet(cfg: dict[str, Any], root: Path, out_path: Path) -> tuple[Path, list[str]]:
    master = cfg["master_id"]
    stills_dir = out_path.parent / f"{master}_stills"
    frames, overflow = render_stills(cfg, root, stills_dir)
    # Also drop cover beside sheet
    cover_path = out_path.parent / f"{master}_cover_1080x1920.png"
    cover_issues = render_cover(cfg, root, cover_path)
    overflow.extend(f"cover: {x}" for x in cover_issues)
    build_contact_sheet(
        frames,
        out_path,
        title=f"NewCo · {master}",
        subtitle="Music-only template preview · automated checks ≠ human 9.0 gate",
    )
    return out_path, overflow


def render_video(cfg: dict[str, Any], root: Path, out_path: Path) -> list[str]:
    """Full 15s encode. Requires validated music (possibly TEST ONLY)."""
    template_path = root / "templates" / f"{cfg['template_id']}.html"
    fps = int(cfg.get("fps") or DEFAULT_FPS)
    dur = float(cfg.get("duration_s") or DEFAULT_DUR)
    audio = resolve_audio_path(cfg, root)
    payload = _page_payload(cfg, root, cover=False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-framerate", str(fps), "-vcodec", "png", "-i", "-",
    ]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += [
        "-vf", "format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-r", str(fps),
        "-movflags", "+faststart", "-map_metadata", "-1",
    ]
    if audio:
        cmd += ["-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += [str(out_path)]

    overflow: list[str] = []
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert ff.stdin is not None
    pw, browser, page = _launch_page(template_path, payload)
    try:
        n = int(fps * dur)
        for f in range(n):
            t = f / fps
            result = page.evaluate("t => render(t)", t)
            if f in (0, int(4 * fps), int(14 * fps)):
                for iss in (result or {}).get("issues") or []:
                    overflow.append(f"t={t:.2f}: {iss}")
            page.evaluate(
                """() => new Promise(r => {
                  const i = document.getElementById('scrimg');
                  if (i.complete && i.naturalWidth) r();
                  else i.onload = () => r();
                })"""
            )
            ff.stdin.write(page.screenshot(type="png"))
    finally:
        browser.close()
        pw.stop()
        ff.stdin.close()
        ff.wait()
    if ff.returncode:
        overflow.append(f"ffmpeg exit {ff.returncode}")
    # Sidecar music meta (never claim licence beyond config)
    meta_out = out_path.with_suffix(".music.json")
    meta_out.write_text(json.dumps(cfg.get("music") or {}, indent=2) + "\n", encoding="utf-8")
    return overflow
