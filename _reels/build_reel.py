#!/usr/bin/env python3
"""fbad03 Creative B v2 — music-only 9:16 Reel, recut from tpl_site99_phone_v1.

Fixes vs v1 (kept at /workspace/ads/fbad03_reelB_fix19_v1.mp4):
1. All type (wordmark, phone UI, end-card CTA / UK-wide line) inside y 269–1248.
2. Scene 1 'Get in touch' button fully inside the phone bezel.
3. Scene transitions are fade-out-then-in through the teal background, not a headline crossfade.
4. End card CTA is 'Tap Send Message below' (small URL kept).
5. 0.25s ease-out slide/pop-in per text group, staggered, so it is not a static slideshow.

No VO. Never silent. No banned wording.
"""
from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import os
HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('REEL_WORK', str(HERE / 'work')))
FR, QA = ROOT / 'frames' / 'v2', ROOT / 'qa' / 'v2'
OUT = Path(os.environ.get('REEL_OUT', str(HERE / 'out' / 'reel.mp4')))
LOGO = Path(os.environ.get('REEL_LOGO', str(HERE / 'newco_studio_logo.png')))
MUSIC = Path(os.environ.get('REEL_MUSIC', str(HERE / 'music.mp3')))
JK = '/usr/share/fonts/truetype/sand-box/google/Plus Jakarta Sans/PlusJakartaSans-VariableFont_wght.ttf'
IN = '/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf'

BG, PANEL, MINT, WHITE = '#00292D', '#02505A', '#9CC4B8', '#FFFFFF'
ELLIPSE = '#013A40'
PHONE_CHROME = '#0B1416'
PHONE_SCREEN = '#F6F8F7'
ROW_LINE = '#DDE5E3'
W, H = 1080, 1920
# Top 14% = 268.8px, bottom 35% starts at 1248. Type must sit inside y 269–1248 inclusive.
SAFE_TOP, SAFE_BOT = 269, 1248
SIDE = 65
FPS = 30
POP_S = 0.25
POP_PX = 28

# Timing in frames. Fades are out-then-in through teal, never a crossfade of two headlines.
# 90+5+5+92+5+5+90+5+5+94 = 396 frames = 13.20s
SCENE_FRAMES = [90, 92, 90, 94]
FADE_OUT = 5
FADE_IN = 5


def font(path, size, weight):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight] if 'Jakarta' in path else [14, weight])
    except Exception:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def ease_out(t: float) -> float:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return 1.0 - (1.0 - t) ** 3


@dataclass
class Layer:
    name: str
    im: Image.Image  # RGBA
    x: int
    y: int  # rest position (top of this layer)
    delay: float = 0.0
    is_text: bool = True
    y_ink_top: int = 0
    y_ink_bottom: int = 0
    x_ink_left: int = 0
    x_ink_right: int = 0


def _ink_bounds(im: Image.Image):
    """Bounding box of non-transparent pixels, or None."""
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    alpha = im.getchannel('A')
    box = alpha.getbbox()
    return box


def make_text(name, text, y_top, size, fill=WHITE, weight=800, path=JK, delay=0.0) -> Layer:
    f = font(path, size, weight)
    dummy = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    b = dummy.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-b[0], -b[1]), text, font=f, fill=fill)
    x = (W - tw) // 2
    y_bot = y_top + th - 1
    assert tw <= (W - 2 * SIDE), (name, text, tw)
    assert SAFE_TOP <= y_top and y_bot <= SAFE_BOT, (name, text, y_top, y_bot)
    assert x >= SIDE and x + tw - 1 <= W - 1 - SIDE, (name, text, x, x + tw)
    return Layer(name, im, x, y_top, delay, True, y_top, y_bot, x, x + tw - 1)


def make_text_at(name, text, x, y_top, size, fill=WHITE, weight=800, path=JK, delay=0.0) -> Layer:
    f = font(path, size, weight)
    dummy = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    b = dummy.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-b[0], -b[1]), text, font=f, fill=fill)
    y_bot = y_top + th - 1
    assert SAFE_TOP <= y_top and y_bot <= SAFE_BOT, (name, text, y_top, y_bot)
    assert x >= SIDE and x + tw - 1 <= W - 1 - SIDE, (name, text, x, x + tw)
    return Layer(name, im, x, y_top, delay, True, y_top, y_bot, x, x + tw - 1)


def background() -> Image.Image:
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.ellipse((620, 1380, 1400, 2160), fill=ELLIPSE)
    d.ellipse((-300, -260, 380, 420), fill=ELLIPSE)
    return im


def wordmark_layer(delay=0.0) -> Layer:
    # Clearly inside the safe box, not tight against y=269.
    return make_text('wordmark', 'NEWCO STUDIO', 320, 30, MINT, 800, JK, delay)


def phone_mockup() -> tuple[Image.Image, int, int, list[Layer]]:
    """Phone with a complete 'Get in touch' button fully inside the bezel.

    The whole device, including chrome, sits inside y 269–1248.
    Returns (image, x, y, text layers for bounds reporting — already composited).
    """
    # Hook occupies ~320–560; phone starts at 600 and must end by 1248.
    pw, ph = 340, 620  # 600+620-1=1219, inside 1248
    x, y = (W - pw) // 2, 600
    assert y >= SAFE_TOP and y + ph - 1 <= SAFE_BOT, (y, y + ph)
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=48, fill=PHONE_CHROME)
    pad = 16
    sx, sy, sr, sb = pad, pad, pw - pad - 1, ph - pad - 1
    d.rounded_rectangle((sx, sy, sr, sb), radius=36, fill=PHONE_SCREEN)
    # notch
    d.rounded_rectangle((pw // 2 - 48, 10, pw // 2 + 48, 26), radius=8, fill=PHONE_CHROME)

    fi = lambda s, wt=700: font(IN, s, wt)
    header_bottom = sy + 168
    d.rectangle((sx, sy + 42, sr, header_bottom), fill=PANEL)
    # Phone UI type — positions are relative to the phone image; convert to canvas below.
    ui = []

    def ui_text(name, text, lx, ly, size, fill, weight=800):
        fnt = fi(size, weight)
        b = d.textbbox((0, 0), text, font=fnt)
        # draw so ink top is ly
        d.text((lx, ly - b[1]), text, font=fnt, fill=fill)
        tw, th = b[2] - b[0], b[3] - b[1]
        ink_top = y + ly
        ink_bot = y + ly + th - 1
        ink_l = x + lx
        ink_r = x + lx + tw - 1
        assert SAFE_TOP <= ink_top and ink_bot <= SAFE_BOT, (name, ink_top, ink_bot)
        ui.append({
            'name': name, 'text': text,
            'y_top': ink_top, 'y_bottom': ink_bot,
            'x_left': ink_l, 'x_right': ink_r,
        })

    ui_text('phone_title', 'Your Business', sx + 22, sy + 58, 26, WHITE, 800)
    ui_text('phone_sub', 'Services · Prices · Contact', sx + 22, sy + 96, 15, MINT, 500)

    # Button fully inside the screen, with padding from every edge of the bezel/screen.
    btn_h = 40
    btn_x0 = sx + 22
    btn_x1 = sr - 22
    btn_y0 = sy + 118
    btn_y1 = btn_y0 + btn_h
    assert btn_x0 > sx and btn_x1 < sr and btn_y0 > sy and btn_y1 < sb
    d.rounded_rectangle((btn_x0, btn_y0, btn_x1, btn_y1), radius=18, fill=MINT)
    label = 'Get in touch'
    fbtn = fi(16, 700)
    bb = d.textbbox((0, 0), label, font=fbtn)
    ltw, lth = bb[2] - bb[0], bb[3] - bb[1]
    # Centre the label inside the button; confirm it does not overflow the button.
    lx = btn_x0 + (btn_x1 - btn_x0 - ltw) // 2
    ly = btn_y0 + (btn_h - lth) // 2
    assert btn_x0 + 6 <= lx and lx + ltw <= btn_x1 - 6, (lx, ltw, btn_x0, btn_x1)
    assert btn_y0 + 4 <= ly and ly + lth <= btn_y1 - 4, (ly, lth, btn_y0, btn_y1)
    d.text((lx, ly - bb[1]), label, font=fbtn, fill=BG)
    ink_top = y + ly
    ink_bot = y + ly + lth - 1
    assert SAFE_TOP <= ink_top and ink_bot <= SAFE_BOT
    ui.append({
        'name': 'phone_button', 'text': label,
        'y_top': ink_top, 'y_bottom': ink_bot,
        'x_left': x + lx, 'x_right': x + lx + ltw - 1,
        'button_box_local': [btn_x0, btn_y0, btn_x1, btn_y1],
        'button_box_canvas': [x + btn_x0, y + btn_y0, x + btn_x1, y + btn_y1],
        'screen_box_canvas': [x + sx, y + sy, x + sr, y + sb],
        'bezel_box_canvas': [x, y, x + pw - 1, y + ph - 1],
        'button_inside_bezel': True,
    })

    # Three content rows, all inside the screen.
    yy = header_bottom + 20
    row_h = 112
    gap = 14
    for title in ['Services', 'Prices', 'Contact']:
        box_bottom = yy + row_h
        assert box_bottom < sb, (title, box_bottom, sb)
        d.rounded_rectangle((sx + 16, yy, sr - 16, box_bottom), radius=14, fill=WHITE, outline=ROW_LINE, width=2)
        ui_text(f'phone_row_{title.lower()}', title, sx + 32, yy + 16, 20, BG, 800)
        for k in range(2):
            d.rounded_rectangle(
                (sx + 32, yy + 52 + k * 22, sr - 48 - k * 24, yy + 64 + k * 22),
                radius=5, fill=ROW_LINE,
            )
        yy = box_bottom + gap

    return im, x, y, ui


def tick_row(label, y, delay) -> tuple[Layer, Layer]:
    """Mint tick + label as two layers, label y matches circle."""
    row_h = 60
    # Circle on a small RGBA canvas
    circ = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    cd = ImageDraw.Draw(circ)
    cd.ellipse((0, 0, 59, 59), fill=MINT)
    check_f = font(IN, 44, 800)
    # Centre a checkmark
    bb = ImageDraw.Draw(circ).textbbox((0, 0), '✓', font=check_f)
    ctw, cth = bb[2] - bb[0], bb[3] - bb[1]
    cd.text(((60 - ctw) // 2 - bb[0], (60 - cth) // 2 - bb[1]), '✓', font=check_f, fill=BG)
    cx = 230
    assert SAFE_TOP <= y and y + row_h - 1 <= SAFE_BOT, ('tick', label, y)
    tick = Layer(f'tick_{label}', circ, cx, y, delay, False, y, y + 59, cx, cx + 59)
    lab = make_text_at(f'label_{label}', label, 320, y + 8, 48, WHITE, 700, JK, delay)
    return tick, lab


def logo_layer(y=360, size=200, delay=0.08) -> Layer:
    logo = Image.open(LOGO).convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
    x = (W - size) // 2
    y_bot = y + size - 1
    assert SAFE_TOP <= y and y_bot <= SAFE_BOT, ('logo', y, y_bot)
    return Layer('logo', logo, x, y, delay, False, y, y_bot, x, x + size - 1)


def panel_layer(x0, y0, x1, y1, delay=0.06) -> Layer:
    im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=36, fill=PANEL)
    assert SAFE_TOP <= y0 and y1 - 1 <= SAFE_BOT, ('panel', y0, y1)
    return Layer('quote_panel', im, x0, y0, delay, False, y0, y1 - 1, x0, x1 - 1)


def build_scenes():
    bounds = []
    scenes = []  # list of (base_rgb, layers)

    def record(scene, layers, extra=None):
        rows = []
        for L in layers:
            if L.y_ink_top or L.is_text:
                rows.append({
                    'scene': scene,
                    'name': L.name,
                    'y_top': L.y_ink_top,
                    'y_bottom': L.y_ink_bottom,
                    'x_left': L.x_ink_left,
                    'x_right': L.x_ink_right,
                    'inside_269_1248': SAFE_TOP <= L.y_ink_top and L.y_ink_bottom <= SAFE_BOT,
                })
        if extra:
            rows.extend(extra)
        bounds.extend(rows)
        return rows

    # --- Scene 1: hook + phone ---
    base1 = background()
    layers1 = [wordmark_layer(0.0)]
    layers1.append(make_text('hook_1', 'Broken button?', 370, 84, WHITE, 800, JK, 0.04))
    layers1.append(make_text('hook_2', 'From £19', 370 + 84 + 10, 84, WHITE, 800, JK, 0.10))
    phone_im, px, py, phone_ui = phone_mockup()
    layers1.append(Layer('phone', phone_im, px, py, 0.12, False, py, py + phone_im.size[1] - 1, px, px + phone_im.size[0] - 1))
    record(1, layers1, [
        {**u, 'scene': 1, 'inside_269_1248': SAFE_TOP <= u['y_top'] and u['y_bottom'] <= SAFE_BOT}
        for u in phone_ui
    ])
    scenes.append((base1, layers1))

    # --- Scene 2: what we fix ---
    base2 = background()
    layers2 = [wordmark_layer(0.0)]
    layers2.append(make_text('fixes_title', 'What we fix, from £19', 390, 62, WHITE, 800, JK, 0.04))
    y = 520
    for i, label in enumerate(['Broken links', 'Broken buttons', 'Details out of date', 'Layout on phones']):
        tick, lab = tick_row(label, y, delay=0.10 + i * 0.06)
        layers2.extend([tick, lab])
        y += 130
    record(2, layers2)
    scenes.append((base2, layers2))

    # --- Scene 3: quote ---
    base3 = background()
    layers3 = [wordmark_layer(0.0)]
    layers3.append(make_text('quote_1', 'Written fixed quote', 390, 66, WHITE, 800, JK, 0.04))
    layers3.append(make_text('quote_2', 'within 24 hours', 390 + 66 + 10, 66, WHITE, 800, JK, 0.08))
    # Panel and its three lines. Keep the VAT line clearly above 1248.
    panel_y0, panel_y1 = 600, 980
    layers3.append(panel_layer(140, panel_y0, 940, panel_y1, 0.10))
    lines = ['No call.', 'No obligation.', 'Fixed price first.']
    # Vertically centre the three lines in the panel with size 52, gap 22.
    f52 = font(JK, 52, 700)
    dummy = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    line_h = dummy.textbbox((0, 0), 'No obligation.', font=f52)
    lh = line_h[3] - line_h[1]
    block = 3 * lh + 2 * 22
    start = panel_y0 + (panel_y1 - panel_y0 - block) // 2
    for i, ln in enumerate(lines):
        layers3.append(make_text(f'quote_panel_{i+1}', ln, start + i * (lh + 22), 52, MINT, 700, JK, 0.14 + i * 0.05))
    layers3.append(make_text('vat', 'Prices as stated. VAT is not charged.', 1020, 34, WHITE, 500, IN, 0.28))
    record(3, layers3)
    scenes.append((base3, layers3))

    # --- Scene 4: end card ---
    base4 = background()
    layers4 = [wordmark_layer(0.0)]
    layers4.append(logo_layer(360, 200, 0.06))
    layers4.append(make_text('end_name', 'NewCo Studio', 580, 64, WHITE, 800, JK, 0.10))
    layers4.append(make_text('end_price_1', 'Websites from £99', 660, 48, MINT, 700, JK, 0.14))
    layers4.append(make_text('end_price_2', 'Fixes from £19', 660 + 48 + 10, 48, MINT, 700, JK, 0.18))
    layers4.append(make_text('end_cta', 'Tap Send Message below', 800, 48, WHITE, 800, JK, 0.22))
    layers4.append(make_text('end_url', 'studio.newcopacks.co.uk', 864, 30, WHITE, 500, IN, 0.26))
    layers4.append(make_text('end_geo', 'UK-wide & worldwide, fully remote', 914, 34, WHITE, 500, IN, 0.30))
    record(4, layers4)
    scenes.append((base4, layers4))

    # Final assertion on every recorded bound
    bad = [r for r in bounds if not r.get('inside_269_1248', False)]
    if bad:
        raise SystemExit(f'safe-zone assertion failed: {bad}')
    return scenes, bounds


def compose(base: Image.Image, layers: list[Layer], t_local: float) -> Image.Image:
    """t_local is seconds from the start of the scene (including fade-in)."""
    frame = base.copy()
    for L in layers:
        p = ease_out((t_local - L.delay) / POP_S)
        if p <= 0:
            continue
        alpha = p
        dy = int(round(POP_PX * (1.0 - p)))
        y = L.y + dy
        layer = L.im
        if alpha < 0.999:
            # multiply alpha channel
            r, g, b, a = layer.split()
            a = a.point(lambda v, al=alpha: int(v * al))
            layer = Image.merge('RGBA', (r, g, b, a))
        frame.paste(layer, (L.x, y), layer)
    return frame


def fade_towards(src: Image.Image, dst: Image.Image, p: float) -> Image.Image:
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return Image.blend(src.convert('RGB'), dst.convert('RGB'), p)


def render(scenes, bounds):
    FR.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)

    # Pre-render a settled still for each scene (for QA and for fade sources).
    settled = []
    hold_end_t = [(n / FPS) for n in SCENE_FRAMES]  # seconds of scene content before fade-out
    for i, (base, layers) in enumerate(scenes):
        still = compose(base, layers, t_local=2.0)  # well after pop-ins
        still.save(FR / f'0{i+1}_settled.png')
        settled.append(still)

    teal = background()
    n_scenes = len(scenes)
    total_frames = sum(SCENE_FRAMES) + (n_scenes - 1) * (FADE_OUT + FADE_IN)
    duration = total_frames / FPS

    mid_frame_index = []
    idx = 0
    for i, n in enumerate(SCENE_FRAMES):
        mid_frame_index.append(idx + n // 2)
        idx += n
        if i < n_scenes - 1:
            idx += FADE_OUT + FADE_IN

    cmd = [
        'ffmpeg', '-v', 'error', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
        '-i', str(MUSIC),
        '-filter_complex',
        f'[1:a]atrim=0:{duration:.4f},afade=t=in:st=0:d=0.3,afade=t=out:st={duration-1.5:.4f}:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[aout]',
        '-map', '0:v', '-map', '[aout]',
        '-t', f'{duration:.4f}',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-ar', '48000',
        '-movflags', '+faststart', '-map_metadata', '-1',
        str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    qa_saved = {}

    def write(im: Image.Image, fi: int):
        proc.stdin.write(im.convert('RGB').tobytes())
        if fi in mid_frame_index:
            si = mid_frame_index.index(fi) + 1
            path = QA / f'0{si}_mid.png'
            im.convert('RGB').save(path)
            qa_saved[si] = str(path)

    fi = 0
    try:
        for i, (base, layers) in enumerate(scenes):
            n = SCENE_FRAMES[i]
            for k in range(n):
                t_local = k / FPS
                frame = compose(base, layers, t_local)
                write(frame, fi)
                fi += 1
            if i < n_scenes - 1:
                end_still = settled[i]
                start_next = compose(scenes[i + 1][0], scenes[i + 1][1], t_local=0.0)
                # Fade out to teal, then fade in the next scene from teal.
                # Next scene at t_local=0 has no text yet (p=0), so headlines cannot overlap.
                for k in range(FADE_OUT):
                    p = (k + 1) / FADE_OUT
                    write(fade_towards(end_still, teal, p), fi)
                    fi += 1
                for k in range(FADE_IN):
                    p = (k + 1) / FADE_IN
                    nxt = compose(scenes[i + 1][0], scenes[i + 1][1], t_local=k / FPS)
                    write(fade_towards(teal, nxt, p), fi)
                    fi += 1
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f'ffmpeg failed with {rc}')
    except BrokenPipeError:
        rc = proc.wait()
        raise SystemExit(f'ffmpeg pipe broke, rc={rc}')

    assert fi == total_frames, (fi, total_frames)

    # Contact sheet of mid-scene QA frames
    ins = []
    for i in range(1, 5):
        ins += ['-i', qa_saved[i]]
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', *ins,
         '-filter_complex',
         'scale=270:480[0s];[1]scale=270:480[1s];[2]scale=270:480[2s];[3]scale=270:480[3s];[0s][1s][2s][3s]hstack=inputs=4',
         str(QA / 'contact_sheet.jpg')],
        check=True,
    )

    # Also grab a frame in the middle of the 1→2 fade-out to prove no overlapping headlines.
    # (Re-extract from the finished file.)
    t_fade = SCENE_FRAMES[0] / FPS + (FADE_OUT / 2) / FPS
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-ss', f'{t_fade:.4f}', '-i', str(OUT),
         '-frames:v', '1', str(QA / 'transition_1_to_2.png')],
        check=True,
    )

    (QA / 'text_bounds.json').write_text(json.dumps({
        'safe_box': {'y_top': SAFE_TOP, 'y_bottom': SAFE_BOT, 'x_left': SIDE, 'x_right': W - 1 - SIDE},
        'duration_s': duration,
        'total_frames': total_frames,
        'fps': FPS,
        'elements': bounds,
    }, indent=2) + '\n')

    return duration, total_frames, bounds


def verify_qa_frames(bounds):
    """Scan mid-scene QA frames: no white/mint/dark-UI type in reserved bands."""
    def is_type_pixel(p):
        r, g, b = p
        # white typography
        if r > 200 and g > 200 and b > 200:
            return True
        # mint typography
        if abs(r - 0x9C) < 45 and abs(g - 0xC4) < 45 and abs(b - 0xB8) < 45 and (r + g + b) > 280:
            return True
        # near-black UI text on a light phone screen (not the dark teal background)
        if r < 40 and g < 50 and b < 55 and not (abs(r - 0x00) <= 8 and abs(g - 0x29) <= 16 and abs(b - 0x2D) <= 16):
            return True
        return False

    report = []
    for i in range(1, 5):
        path = QA / f'0{i}_mid.png'
        im = Image.open(path).convert('RGB')
        pix = im.load()
        unsafe = []
        for y in list(range(0, SAFE_TOP)) + list(range(SAFE_BOT + 1, H)):
            for x in range(W):
                if is_type_pixel(pix[x, y]):
                    unsafe.append(y)
                    break
        # Measured ink of light/mint text inside the frame
        ys = []
        for y in range(SAFE_TOP, SAFE_BOT + 1):
            for x in range(W):
                r, g, b = pix[x, y]
                if (r > 200 and g > 200 and b > 200) or (
                    abs(r - 0x9C) < 45 and abs(g - 0xC4) < 45 and abs(b - 0xB8) < 45 and r + g + b > 280
                ):
                    ys.append(y)
                    break
        report.append({
            'scene': i,
            'measured_light_text_y': [min(ys), max(ys)] if ys else None,
            'type_pixels_outside_safe_box': (min(unsafe), max(unsafe), len(unsafe)) if unsafe else None,
        })
        if unsafe:
            raise SystemExit(f'scene {i} has type pixels outside y {SAFE_TOP}–{SAFE_BOT}: {report[-1]}')
    return report


def main():
    scenes, bounds = build_scenes()
    duration, total_frames, bounds = render(scenes, bounds)
    measured = verify_qa_frames(bounds)
    print('duration', duration)
    print('frames', total_frames)
    print('wrote', OUT)
    print('TEXT BOUNDS (rest positions, y 269–1248 required):')
    for r in bounds:
        print(f"  scene {r['scene']:>1}  {r['name']:<24}  y {r['y_top']:>4}–{r['y_bottom']:<4}  "
              f"x {r.get('x_left','?'):>4}–{r.get('x_right','?'):<4}  ok={r['inside_269_1248']}")
    print('QA frame scan:', json.dumps(measured))


if __name__ == '__main__':
    main()
