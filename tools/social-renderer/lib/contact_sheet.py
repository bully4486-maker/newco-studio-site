"""Compose an attractive PNG contact sheet from still frames."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def build_contact_sheet(
    frames: list[tuple[str, Path]],
    out_path: Path,
    *,
    title: str = "NewCo Studio · master preview",
    subtitle: str = "Automated layout preview — not a 9.0 creative/rights score",
    cols: int = 3,
    cell_w: int = 360,
    cell_h: int = 640,
    pad: int = 24,
    bg: tuple[int, int, int] = (0, 41, 45),
) -> Path:
    if not frames:
        raise ValueError("no frames for contact sheet")

    rows = (len(frames) + cols - 1) // cols
    header = 110
    width = cols * cell_w + (cols + 1) * pad
    height = header + rows * cell_h + (rows + 1) * pad + 40

    sheet = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(sheet)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except OSError:
        font_title = font_sub = font_lbl = ImageFont.load_default()

    draw.text((pad, 28), title, fill=(214, 230, 226), font=font_title)
    draw.text((pad, 68), subtitle, fill=(156, 196, 184), font=font_sub)

    for i, (label, path) in enumerate(frames):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = header + pad + r * (cell_h + pad)
        im = Image.open(path).convert("RGB")
        im = im.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        # label strip
        draw.rectangle([x, y + cell_h - 36, x + cell_w, y + cell_h], fill=(2, 80, 90))
        draw.text((x + 12, y + cell_h - 28), label, fill=(255, 255, 255), font=font_lbl)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "PNG", optimize=True)
    return out_path
