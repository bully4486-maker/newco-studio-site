"""Config validation: structure, banned copy, length/safe-area heuristics, music."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .banned import scan_many
from .music import validate_music

# 9:16 canvas; Meta/TikTok UI overlays eat edges. Matches video_poc template3 notes.
SAFE = {"w": 1080, "h": 1920, "x0": 65, "x1": 1015, "y0": 269, "y1": 1640}

# Heuristic text budgets (characters). Runtime overflow check is separate when Playwright runs.
LIMITS = {
    "hook_line": 28,
    "cap_kicker": 22,
    "cap_line": 36,
    "end_title": 40,
    "price": 24,
    "check": 42,
    "footnote": 64,
    "url": 48,
    "cta": 28,
    "phone_label": 36,
    "bottom_tag": 28,
}


def _flatten_copy(copy: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for key, val in copy.items():
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, list):
                    parts.extend(str(x) for x in item)
    return parts


def validate_config(cfg: dict[str, Any], root: Path, *, for_video: bool = False) -> list[str]:
    errors: list[str] = []

    for key in ("master_id", "template_id", "format", "copy", "assets"):
        if key not in cfg:
            errors.append(f"missing required field: {key}")

    if errors:
        return errors

    if not isinstance(cfg["master_id"], str) or not cfg["master_id"].strip():
        errors.append("master_id must be a non-empty string")
    if not isinstance(cfg["template_id"], str) or not cfg["template_id"].strip():
        errors.append("template_id must be a non-empty string")

    if cfg.get("format") != "916":
        errors.append("format must be '916' (shared FB/IG/TikTok master)")

    copy = cfg.get("copy") or {}
    if not isinstance(copy, dict):
        errors.append("copy must be an object")
        return errors

    required_copy = (
        "hook_lines",
        "caps",
        "end_title",
        "price",
        "checks",
        "footnote",
        "url",
        "cta",
        "phone_label",
        "bottom_tag",
    )
    for key in required_copy:
        if key not in copy:
            errors.append(f"copy.{key} is required")

    hooks = copy.get("hook_lines") or []
    if not isinstance(hooks, list) or not (1 <= len(hooks) <= 3):
        errors.append("copy.hook_lines must be 1–3 strings")
    else:
        for i, line in enumerate(hooks):
            if len(str(line)) > LIMITS["hook_line"]:
                errors.append(f"copy.hook_lines[{i}] exceeds {LIMITS['hook_line']} chars")

    caps = copy.get("caps") or []
    if not isinstance(caps, list) or len(caps) != 3:
        errors.append("copy.caps must be exactly 3 [kicker, body] pairs")
    else:
        for i, pair in enumerate(caps):
            if not isinstance(pair, list) or len(pair) != 2:
                errors.append(f"copy.caps[{i}] must be [kicker, body]")
                continue
            if len(str(pair[0])) > LIMITS["cap_kicker"]:
                errors.append(f"copy.caps[{i}][0] exceeds {LIMITS['cap_kicker']} chars")
            # body may contain <br>
            body_plain = str(pair[1]).replace("<br>", " ")
            for part in str(pair[1]).split("<br>"):
                if len(part) > LIMITS["cap_line"]:
                    errors.append(f"copy.caps[{i}] body line exceeds {LIMITS['cap_line']} chars")

    checks = copy.get("checks") or []
    if not isinstance(checks, list) or len(checks) != 3:
        errors.append("copy.checks must be exactly 3 strings")
    else:
        for i, c in enumerate(checks):
            if len(str(c)) > LIMITS["check"]:
                errors.append(f"copy.checks[{i}] exceeds {LIMITS['check']} chars")

    for field, lim in (
        ("end_title", "end_title"),
        ("price", "price"),
        ("footnote", "footnote"),
        ("url", "url"),
        ("cta", "cta"),
        ("phone_label", "phone_label"),
        ("bottom_tag", "bottom_tag"),
    ):
        val = str(copy.get(field, ""))
        if len(val) > LIMITS[lim]:
            errors.append(f"copy.{field} exceeds {LIMITS[lim]} chars")

    # Approved facts only — studio prices; no unverified Etsy VAT prices in copy.
    price = str(copy.get("price", ""))
    if "£" in price and "99" not in price and "19" not in price:
        errors.append(
            "copy.price mentions £ but not verified studio prices (£99 / £19); "
            "omit unverified Etsy VAT-inclusive figures"
        )

    banned = scan_many(_flatten_copy(copy) + [cfg.get("master_id", ""), cfg.get("template_id", "")])
    for hit in banned:
        errors.append(f"banned copy pattern: {hit}")

    # phone_label must not be the old fictional badge
    label = str(copy.get("phone_label", "")).lower()
    if "fictional" in label or label.strip() == "demo site":
        errors.append("copy.phone_label must not claim fictional/demo-site badge text")

    assets = cfg.get("assets") or {}
    for key in ("logo", "phone_screen"):
        rel = assets.get(key)
        if not rel:
            errors.append(f"assets.{key} is required")
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"assets.{key} not found: {rel}")

    # Reject historic MTD-named still as authority for MTD-ready claims (filename gate)
    phone = str(assets.get("phone_screen", "")).lower()
    if "mtd" in phone and "mtd_ready" not in banned:
        # Using the file is allowed for product UI screenshots, but copy must not say MTD-ready
        # (already gated). Warn-as-error if master_id implies mtd-ready.
        if "mtd" in str(cfg.get("master_id", "")).lower():
            errors.append("master_id must not imply MTD-ready from a filename alone")

    errors.extend(validate_music(cfg, root, for_video=for_video))

    tpl = root / "templates" / f"{cfg['template_id']}.html"
    if not tpl.is_file():
        errors.append(f"template not found: templates/{cfg['template_id']}.html")

    return errors


def safe_area_spec() -> dict[str, int]:
    return dict(SAFE)
