#!/usr/bin/env python3
"""Music-only 1080x1920 Reel renderer.

Scenes and on-screen copy come from a JSON spec in `_reels/specs/`.
The frame (colours, type, logo, safe area, fade-through-teal, end card)
stays the house style from fbad03 Reel B / tpl_site99_phone_v1.

  python3 build_reel.py                 # render every spec to _reels/out/
  python3 build_reel.py --stills        # settled frames only (no video)
  python3 build_reel.py specs/one.json
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SPECS = HERE / 'specs'
OUT_DIR = HERE / 'out'
WORK = HERE / 'work'
LOGO = HERE / 'newco_studio_logo.png'
MUSIC = HERE / 'music' / 'city-loop.mp3'
FONT_DIR = HERE / 'fonts'
JK_FILE = FONT_DIR / 'PlusJakartaSans-Variable.ttf'
IN_FILE = FONT_DIR / 'Inter-Variable.ttf'

JK_URL = 'https://github.com/google/fonts/raw/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf'
IN_URL = 'https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf'
MUSIC_URL = 'https://opengameart.org/sites/default/files/city-loop.mp3'
MUSIC_PAGE = 'https://opengameart.org/content/city-loop-0'

BG, PANEL, MINT, WHITE = '#00292D', '#02505A', '#9CC4B8', '#FFFFFF'
ELLIPSE = '#013A40'
PHONE_CHROME = '#0B1416'
PHONE_SCREEN = '#F6F8F7'
ROW_LINE = '#D5DEDB'
W, H = 1080, 1920
SAFE_TOP, SAFE_BOT = 269, 1248
# Ink may slide down POP_PX at the start of a scene, so rest positions
# stay this far above the bottom of the safe box.
POP_PX = 28
INK_BOT = SAFE_BOT - POP_PX
SIDE = 65
FPS = 30
POP_S = 0.25
FADE_OUT = 5
FADE_IN = 5

FILLS = {'white': WHITE, 'mint': MINT, 'bg': BG, 'panel': PANEL}

# Prices that may appear on screen, by template. End card always carries £99 and £19.
ALLOWED_PRICES = {
    'tpl_site99_phone_v1': {'99', '19'},
    'tpl_fix19_phone_v1': {'99', '19'},
    'tpl_freecheck_v1': {'99', '19'},
    'tpl_etsy_seller_fees_v1': {'99', '19', '9.59'},
    'tpl_counterbook_sa_v1': {'99', '19', '11.99'},
}

BANNED = [
    r'\bartificial intelligence\b', r'\bchatgpt\b', r'\bai\b',
    r'demo site', r'\bfictional\b', r'\bfounding\b', r'first 3 clients',
    r'\bclients?\b', r'\breviews?\b', r'\bratings?\b', r'\btestimonials?\b',
    r'\bhurry\b', r'\blimited time\b', r'last chance', r"don't miss", r'dont miss',
    r'\bact now\b', r'today only', r'\bspots\b', r'selling fast', r'\burgent\b',
    r'mtd-ready', r'\boxfordshire\b', r'50/50', r'50 / 50', r'\bhandmade\b',
]

_FONT_CACHE: dict = {}


def ensure_fonts() -> tuple[str, str]:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = (
        (JK_FILE, JK_URL, 'Plus Jakarta Sans'),
        (IN_FILE, IN_URL, 'Inter'),
    )
    for path, url, label in pairs:
        if path.exists() and path.stat().st_size > 1000:
            continue
        sys.stderr.write(f'Downloading {label} from Google Fonts\n')
        urllib.request.urlretrieve(url, path)
    return str(JK_FILE), str(IN_FILE)


def ensure_music() -> Path:
    MUSIC.parent.mkdir(parents=True, exist_ok=True)
    marker = MUSIC.with_suffix('.downloaded.txt')
    if not MUSIC.exists() or MUSIC.stat().st_size < 1000:
        sys.stderr.write(f'Downloading City Loop from {MUSIC_URL}\n')
        urllib.request.urlretrieve(MUSIC_URL, MUSIC)
        marker.write_text(date.today().isoformat() + '\n')
    if not marker.exists():
        marker.write_text(date.today().isoformat() + '\n')
    return MUSIC


def font(path: str, size: int, weight: int) -> ImageFont.FreeTypeFont:
    key = (path, size, weight)
    hit = _FONT_CACHE.get(key)
    if hit is not None:
        return hit
    f = ImageFont.truetype(path, size)
    try:
        if 'Inter' in path:
            f.set_variation_by_axes([14, weight])
        else:
            f.set_variation_by_axes([weight])
    except Exception:
        pass
    _FONT_CACHE[key] = f
    return f


def ease_out(t: float) -> float:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return 1.0 - (1.0 - t) ** 3


def fill_of(name: str) -> str:
    return FILLS.get(name, name)


def face(name: str, jk: str, inn: str) -> str:
    return inn if name == 'inter' else jk


@dataclass
class Layer:
    name: str
    im: Image.Image
    x: int
    y: int
    delay: float = 0.0
    is_text: bool = True
    y_ink_top: int = 0
    y_ink_bottom: int = 0
    x_ink_left: int = 0
    x_ink_right: int = 0


def _measure(text, fnt):
    dummy = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    b = dummy.textbbox((0, 0), text, font=fnt)
    return b, b[2] - b[0], b[3] - b[1]


def make_text(name, text, x, y_top, size, fill, weight, path, delay, centre=False) -> Layer:
    fnt = font(path, size, weight)
    b, tw, th = _measure(text, fnt)
    if centre:
        x = (W - tw) // 2
    im = Image.new('RGBA', (max(tw, 1), max(th, 1)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-b[0], -b[1]), text, font=fnt, fill=fill)
    y_bot = y_top + th - 1
    if tw > (W - 2 * SIDE):
        raise SystemExit(f'{name!r} is {tw}px wide, max {W - 2 * SIDE}: {text!r}')
    if y_top < SAFE_TOP or y_bot > INK_BOT:
        raise SystemExit(f'{name!r} y {y_top}–{y_bot} outside {SAFE_TOP}–{INK_BOT}: {text!r}')
    if x < SIDE or x + tw - 1 > W - 1 - SIDE:
        raise SystemExit(f'{name!r} x {x}–{x + tw - 1} outside side margins: {text!r}')
    return Layer(name, im, x, y_top, delay, True, y_top, y_bot, x, x + tw - 1)


def centred(name, text, y, size, fill, weight, path, delay) -> Layer:
    return make_text(name, text, 0, y, size, fill, weight, path, delay, centre=True)


def background() -> Image.Image:
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.ellipse((620, 1380, 1400, 2160), fill=ELLIPSE)
    d.ellipse((-300, -260, 380, 420), fill=ELLIPSE)
    return im


def wordmark_layer(jk, delay=0.0) -> Layer:
    return centred('wordmark', 'NEWCO STUDIO', 308, 30, MINT, 800, jk, delay)


def logo_layer(y=360, size=200, delay=0.06) -> Layer:
    src = Image.open(LOGO).convert('RGBA')
    # Scale only. The white square and the mark are not redrawn.
    if src.size != (size, size):
        src = src.resize((size, size), Image.Resampling.LANCZOS)
    x = (W - size) // 2
    y_bot = y + size - 1
    if y < SAFE_TOP or y_bot > INK_BOT:
        raise SystemExit(f'logo y {y}–{y_bot} outside safe box')
    return Layer('logo', src, x, y, delay, False, y, y_bot, x, x + size - 1)


def line_spec(raw, default_size, default_fill, default_weight, default_font):
    if isinstance(raw, str):
        return raw, default_size, default_fill, default_weight, default_font
    return (
        raw['text'],
        raw.get('size', default_size),
        raw.get('fill', default_fill),
        raw.get('weight', default_weight),
        raw.get('font', default_font),
    )


def stack_centred(layers, lines, y, jk, inn, delay0=0.04, gap=10, name='line'):
    for i, raw in enumerate(lines):
        text, size, fill, weight, face_name = line_spec(raw, 64, 'white', 800, 'jakarta')
        layer = centred(
            f'{name}_{i+1}', text, y, size, fill_of(fill), weight,
            face(face_name, jk, inn), delay0 + i * 0.06,
        )
        layers.append(layer)
        y = layer.y_ink_bottom + 1 + gap
    return y


def draw_check(d, cx, cy, r, colour):
    d.line((cx - r, cy, cx - r // 3, cy + r), fill=colour, width=max(4, r // 2))
    d.line((cx - r // 3, cy + r, cx + r + 2, cy - r), fill=colour, width=max(4, r // 2))


def layout_hook_phone(scene, jk, inn):
    layers = [wordmark_layer(jk)]
    y = stack_centred(layers, scene['lines'], 368, jk, inn, 0.04, 8, 'hook')
    phone_top = y + 16
    ph = min(620, INK_BOT - phone_top + 1)
    if ph < 520:
        raise SystemExit(f'phone does not fit under the hook (height {ph})')
    pw = int(round(ph * 340 / 620))
    px = (W - pw) // 2
    im, extra = draw_phone(pw, ph, scene['phone'], px, phone_top, inn)
    layers.append(Layer(
        'phone', im, px, phone_top, 0.14, False,
        phone_top, phone_top + ph - 1, px, px + pw - 1,
    ))
    return background(), layers, extra


def draw_phone(pw, ph, ui, ox, oy, inn):
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    scale = ph / 620.0

    def S(n):
        return max(8, int(round(n * scale)))

    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=S(48), fill=PHONE_CHROME)
    pad = S(16)
    sx, sy, sr, sb = pad, pad, pw - pad - 1, ph - pad - 1
    d.rounded_rectangle((sx, sy, sr, sb), radius=S(36), fill=PHONE_SCREEN)
    notch_w = S(96)
    d.rounded_rectangle((pw // 2 - notch_w // 2, S(10), pw // 2 + notch_w // 2, S(26)), radius=S(8), fill=PHONE_CHROME)

    btn_h = S(44)
    btn_x0, btn_x1 = sx + S(22), sr - S(22)
    btn_y0 = sy + S(124)
    btn_y1 = btn_y0 + btn_h
    header_top = sy + S(36)
    header_bottom = btn_y1 + S(16)
    d.rectangle((sx, header_top, sr, header_bottom), fill=PANEL)

    extra = []

    def ui_text(name, text, lx, ly, size, fill, weight):
        fnt = font(inn, S(size), weight)
        b = d.textbbox((0, 0), text, font=fnt)
        tw, th = b[2] - b[0], b[3] - b[1]
        d.text((lx - b[0], ly - b[1]), text, font=fnt, fill=fill)
        ink_l, ink_r = ox + lx, ox + lx + tw - 1
        ink_top, ink_bot = oy + ly, oy + ly + th - 1
        if ink_l < SIDE or ink_r > W - 1 - SIDE or ink_top < SAFE_TOP or ink_bot > INK_BOT:
            raise SystemExit(f'{name} outside safe box: {text}')
        extra.append({
            'name': name, 'text': text,
            'y_top': ink_top, 'y_bottom': ink_bot,
            'x_left': ink_l, 'x_right': ink_r,
            'inside_269_1248': True,
        })
        return tw, th

    ui_text('phone_title', ui['title'], sx + S(22), sy + S(52), 26, WHITE, 800)
    ui_text('phone_sub', ui['subtitle'], sx + S(22), sy + S(90), 15, MINT, 600)

    if not (btn_x0 > sx and btn_x1 < sr and btn_y0 > sy and btn_y1 < sb):
        raise SystemExit('Get in touch button is not inside the phone screen')
    d.rounded_rectangle((btn_x0, btn_y0, btn_x1, btn_y1), radius=S(18), fill=MINT)
    label = ui.get('button', 'Get in touch')
    fbtn = font(inn, S(16), 700)
    bb = d.textbbox((0, 0), label, font=fbtn)
    ltw, lth = bb[2] - bb[0], bb[3] - bb[1]
    lx = btn_x0 + (btn_x1 - btn_x0 - ltw) // 2
    ly = btn_y0 + (btn_h - lth) // 2
    if lx < btn_x0 + S(6) or lx + ltw > btn_x1 - S(6) or ly < btn_y0 + S(4) or ly + lth > btn_y1 - S(4):
        raise SystemExit(f'button label does not fit inside the button: {label!r}')
    d.text((lx - bb[0], ly - bb[1]), label, font=fbtn, fill=BG)
    extra.append({
        'name': 'phone_button', 'text': label,
        'y_top': oy + ly, 'y_bottom': oy + ly + lth - 1,
        'x_left': ox + lx, 'x_right': ox + lx + ltw - 1,
        'button_inside_bezel': True,
        'inside_269_1248': True,
    })

    rows = ui.get('rows', ['Services', 'Prices', 'Contact'])
    header_bottom = btn_y1 + S(16)
    yy = header_bottom + S(8)
    gap = S(12)
    avail = (sb - S(10)) - yy
    row_h = min(S(112), (avail - gap * (len(rows) - 1)) // max(len(rows), 1))
    if row_h < S(64):
        raise SystemExit('phone rows do not fit inside the screen')
    for title in rows:
        box_bottom = yy + row_h
        if box_bottom >= sb:
            raise SystemExit(f'phone row {title!r} escapes the screen')
        d.rounded_rectangle((sx + S(16), yy, sr - S(16), box_bottom), radius=S(14), fill=WHITE, outline=ROW_LINE, width=2)
        ui_text(f'phone_row_{title.lower()}', title, sx + S(32), yy + S(16), 20, BG, 800)
        if row_h > S(70):
            for k in range(2):
                d.rounded_rectangle(
                    (sx + S(32), yy + S(52) + k * S(22), sr - S(48) - k * S(24), yy + S(64) + k * S(22)),
                    radius=S(5), fill=ROW_LINE,
                )
        yy = box_bottom + gap
    return im, extra


def layout_hook_type(scene, jk, inn):
    layers = [wordmark_layer(jk)]
    measured = []
    for raw in scene['lines']:
        text, size, fill, weight, face_name = line_spec(raw, 72, 'white', 800, 'jakarta')
        fnt = font(face(face_name, jk, inn), size, weight)
        _, tw, th = _measure(text, fnt)
        measured.append((text, size, fill, weight, face_name, th))
    gap = 12
    block = sum(m[5] for m in measured) + gap * (len(measured) - 1)
    region_top, region_bot = 400, 1140
    if block > region_bot - region_top:
        raise SystemExit('hook lines do not fit in the safe box')
    y = region_top + (region_bot - region_top - block) // 2
    for i, (text, size, fill, weight, face_name, th) in enumerate(measured):
        layers.append(centred(
            f'hook_{i+1}', text, y, size, fill_of(fill), weight,
            face(face_name, jk, inn), 0.04 + i * 0.06,
        ))
        y += th + gap
    return background(), layers, []


def layout_ticks(scene, jk, inn):
    layers = [wordmark_layer(jk)]
    y = 360
    title = scene.get('title')
    if title:
        layer = centred('ticks_title', title, y, scene.get('title_size', 56), WHITE, 800, jk, 0.04)
        layers.append(layer)
        y = layer.y_ink_bottom + 36
    items = scene['items']
    item_size = scene.get('item_size', 46)
    circle = 58
    avail = INK_BOT - y
    pitch = min(128, avail // len(items))
    if pitch < circle + 16:
        raise SystemExit('tick list does not fit in the safe box')
    sample = font(jk, item_size, 700)
    widths = []
    heights = []
    for label in items:
        _, tw, th = _measure(label, sample)
        widths.append(tw)
        heights.append(th)
    block = circle + 28 + max(widths)
    tick_x = max(SIDE, (W - block) // 2)
    lab_x = tick_x + circle + 28
    for i, label in enumerate(items):
        tw, th = widths[i], heights[i]
        row_y = y + i * pitch
        circ = Image.new('RGBA', (circle, circle), (0, 0, 0, 0))
        cd = ImageDraw.Draw(circ)
        cd.ellipse((0, 0, circle - 1, circle - 1), fill=MINT)
        draw_check(cd, circle // 2 - 2, circle // 2 - 2, 12, BG)
        if row_y < SAFE_TOP or row_y + circle - 1 > INK_BOT:
            raise SystemExit(f'tick {label!r} outside safe box')
        layers.append(Layer(
            f'tick_{i+1}', circ, tick_x, row_y, 0.10 + i * 0.06, False,
            row_y, row_y + circle - 1, tick_x, tick_x + circle - 1,
        ))
        lab_y = row_y + (circle - th) // 2
        layers.append(make_text(
            f'label_{i+1}', label, lab_x, lab_y, item_size, WHITE, 700, jk, 0.10 + i * 0.06,
        ))
    return background(), layers, []


def layout_panel(scene, jk, inn):
    layers = [wordmark_layer(jk)]
    y = stack_centred(layers, scene['lines'], 356, jk, inn, 0.04, 8, 'title')
    y += 16
    texts = scene['panel']
    size = scene.get('panel_size', 48)
    fnt = font(jk, size, 700)
    heights = [_measure(t, fnt)[2] for t in texts]
    gap = 20
    block = sum(heights) + gap * (len(texts) - 1)
    footnote = scene.get('footnote')
    foot_block = 0
    if footnote:
        foot_block = _measure(footnote, font(inn, 32, 600))[2] + 28
    room = INK_BOT - y - foot_block
    panel_h = max(block + 64, min(380, room))
    if block + 48 > panel_h:
        raise SystemExit('panel lines do not fit')
    x0, x1 = 120, 960
    y1 = y + panel_h
    im = Image.new('RGBA', (x1 - x0, panel_h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, x1 - x0 - 1, panel_h - 1), radius=36, fill=PANEL)
    layers.append(Layer('panel', im, x0, y, 0.12, False, y, y1 - 1, x0, x1 - 1))
    start = y + (panel_h - block) // 2
    yy = start
    for i, (text, th) in enumerate(zip(texts, heights)):
        layers.append(centred(f'panel_{i+1}', text, yy, size, MINT, 700, jk, 0.16 + i * 0.05))
        yy += th + gap
    if footnote:
        layers.append(centred('footnote', footnote, y1 + 22, 32, WHITE, 600, inn, 0.34))
    return background(), layers, []


def layout_sheet(scene, jk, inn):
    layers = [wordmark_layer(jk)]
    y = 348
    if scene.get('lines'):
        y = stack_centred(layers, scene['lines'], y, jk, inn, 0.04, 8, 'sheet_title')
        y += 12
    rows = scene['rows']
    row_h = 78
    header_h = 70
    panel_h = header_h + row_h * len(rows)
    if y + panel_h - 1 > INK_BOT:
        raise SystemExit(f'sheet is too tall ({y + panel_h} > {INK_BOT})')
    x0, x1 = 110, 970
    pw, phh = x1 - x0, panel_h
    im = Image.new('RGBA', (pw, phh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, phh - 1), radius=28, fill=PANEL)
    d.rounded_rectangle((10, header_h - 8, pw - 11, phh - 11), radius=20, fill=PHONE_SCREEN)
    hf = font(jk, 30, 700)
    left_h = scene.get('col_left', 'Per order')
    right_h = scene.get('col_right', 'In the sheet')
    hb = d.textbbox((0, 0), left_h, font=hf)
    d.text((28, (header_h - (hb[3] - hb[1])) // 2 - hb[1]), left_h, font=hf, fill=WHITE)
    rb = d.textbbox((0, 0), right_h, font=hf)
    rw = rb[2] - rb[0]
    d.text((pw - 28 - rw, (header_h - (rb[3] - rb[1])) // 2 - rb[1]), right_h, font=hf, fill=MINT)
    rf = font(jk, 36, 700)
    for i, row in enumerate(rows):
        ry = header_h + i * row_h
        if i:
            d.line((28, ry, pw - 28, ry), fill=ROW_LINE, width=2)
        cy = ry + row_h // 2
        d.ellipse((32, cy - 16, 64, cy + 16), fill=MINT)
        draw_check(d, 46, cy - 2, 8, BG)
        b = d.textbbox((0, 0), row, font=rf)
        th = b[3] - b[1]
        d.text((80, cy - th // 2 - b[1]), row, font=rf, fill=BG)
        tw = b[2] - b[0]
        if 80 + tw > pw - 36:
            raise SystemExit(f'sheet row too wide: {row!r}')
    layers.append(Layer('sheet', im, x0, y, 0.12, False, y, y + phh - 1, x0, x1 - 1))
    return background(), layers, []


def layout_endcard(scene, jk, inn):
    cta = scene.get('cta', 'Tap Send Message below')
    layers = [wordmark_layer(jk, 0.0)]
    layers.append(logo_layer(352, 196, 0.05))
    y = 568
    rows = [
        ('end_name', 'NewCo Studio', 60, WHITE, 800, jk, 0.10),
        ('end_price_1', 'Websites from £99', 46, MINT, 700, jk, 0.15),
        ('end_price_2', 'Fixes from £19', 46, MINT, 700, jk, 0.19),
        ('end_cta', cta, 42, WHITE, 800, jk, 0.23),
        ('end_url', 'studio.newcopacks.co.uk', 32, WHITE, 600, inn, 0.27),
        ('end_geo', 'UK-wide & worldwide, fully remote', 30, WHITE, 600, inn, 0.31),
    ]
    for name, text, size, col, weight, path, delay in rows:
        layer = centred(name, text, y, size, col, weight, path, delay)
        layers.append(layer)
        y = layer.y_ink_bottom + 14
    return background(), layers, []


LAYOUTS = {
    'hook_phone': layout_hook_phone,
    'hook_type': layout_hook_type,
    'ticks': layout_ticks,
    'panel': layout_panel,
    'sheet': layout_sheet,
    'endcard': layout_endcard,
}


def on_screen_strings(spec) -> list[str]:
    found = ['NEWCO STUDIO', 'NewCo Studio', 'Websites from £99', 'Fixes from £19', 'studio.newcopacks.co.uk', 'UK-wide & worldwide, fully remote']
    for scene in spec['scenes']:
        if scene.get('cta'):
            found.append(scene['cta'])
        elif scene['layout'] == 'endcard':
            found.append('Tap Send Message below')
        for key in ('title', 'footnote', 'col_left', 'col_right'):
            if scene.get(key):
                found.append(scene[key])
        for raw in scene.get('lines', []):
            found.append(raw['text'] if isinstance(raw, dict) else raw)
        for key in ('panel', 'items', 'rows'):
            found.extend(scene.get(key, []))
        phone = scene.get('phone') or {}
        for key in ('title', 'subtitle', 'button'):
            if phone.get(key):
                found.append(phone[key])
        found.extend(phone.get('rows', []))
    return found


def lint_spec(spec):
    tid = spec['template_id']
    if tid not in ALLOWED_PRICES:
        raise SystemExit(f'unknown template_id {tid}')
    strings = on_screen_strings(spec)
    blob = '\n'.join(strings)
    for pat in BANNED:
        if re.search(pat, blob, flags=re.IGNORECASE):
            raise SystemExit(f'banned wording {pat!r} in {spec.get("asset_id")}')
    prices = set(re.findall(r'£\s?(\d+(?:\.\d+)?)', blob))
    allowed = ALLOWED_PRICES[tid]
    extra = prices - allowed
    if extra:
        raise SystemExit(f'unexpected price {extra} on {tid}')
    if '99' not in prices or '19' not in prices:
        raise SystemExit('end card must show £99 and £19')
    joined = ' '.join(s['layout'] for s in spec['scenes'])
    if 'endcard' not in joined:
        raise SystemExit('spec is missing an end card')


def build_scenes(spec, jk, inn):
    lint_spec(spec)
    scenes = []
    bounds = []
    for idx, scene in enumerate(spec['scenes'], start=1):
        layout = scene['layout']
        if layout not in LAYOUTS:
            raise SystemExit(f'unknown layout {layout}')
        base, layers, extra = LAYOUTS[layout](scene, jk, inn)
        hold = float(scene['hold_s'])
        n = max(1, int(round(hold * FPS)))
        for layer in layers:
            bounds.append({
                'scene': idx,
                'name': layer.name,
                'y_top': layer.y_ink_top,
                'y_bottom': layer.y_ink_bottom,
                'x_left': layer.x_ink_left,
                'x_right': layer.x_ink_right,
                'inside_safe': SAFE_TOP <= layer.y_ink_top and layer.y_ink_bottom <= SAFE_BOT,
            })
        for row in extra:
            row = dict(row)
            row['scene'] = idx
            bounds.append(row)
        scenes.append({'base': base, 'layers': layers, 'frames': n, 'id': scene.get('id', layout)})
    bad = [b for b in bounds if not b.get('inside_safe', b.get('inside_269_1248', False))]
    if bad:
        raise SystemExit(f'safe-zone failed: {bad}')
    n_scenes = len(scenes)
    total = sum(s['frames'] for s in scenes) + (n_scenes - 1) * (FADE_OUT + FADE_IN)
    duration = total / FPS
    if not (15.0 <= duration <= 26.0):
        raise SystemExit(f'duration {duration:.2f}s is outside 15–26s')
    return scenes, bounds, duration, total


def compose(base, layers, t_local: float) -> Image.Image:
    frame = base.copy()
    for layer in layers:
        p = ease_out((t_local - layer.delay) / POP_S)
        if p <= 0:
            continue
        dy = int(round(POP_PX * (1.0 - p)))
        im = layer.im
        if p < 0.999:
            r, g, b, a = im.split()
            a = a.point(lambda v, al=p: int(v * al))
            im = Image.merge('RGBA', (r, g, b, a))
        frame.paste(im, (layer.x, layer.y + dy), im)
    return frame


def fade_towards(src, dst, p):
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return Image.blend(src.convert('RGB'), dst.convert('RGB'), p)


def settled_frame(scene):
    return compose(scene['base'], scene['layers'], t_local=2.0)


def render_stills(spec, scenes, work: Path):
    work.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, scene in enumerate(scenes, start=1):
        im = settled_frame(scene)
        path = work / f'0{i}_settled.png'
        im.save(path)
        paths.append(path)
    sheet = contact_sheet(paths)
    sheet.save(work / 'contact.png')
    return paths


def contact_sheet(paths: list[Path]) -> Image.Image:
    cell_w, cell_h = 360, 640
    sheet = Image.new('RGB', (cell_w * len(paths), cell_h), BG)
    for i, path in enumerate(paths):
        im = Image.open(path).convert('RGB').resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (i * cell_w, 0))
    return sheet


def verify_frame(path: Path, scene_no: int):
    im = Image.open(path).convert('RGB')
    pix = im.load()

    def is_type_pixel(r, g, b):
        if r > 200 and g > 200 and b > 200:
            return True
        if abs(r - 0x9C) < 45 and abs(g - 0xC4) < 45 and abs(b - 0xB8) < 45 and (r + g + b) > 280:
            return True
        if r < 40 and g < 50 and b < 55 and not (
            abs(r - 0x00) <= 8 and abs(g - 0x29) <= 16 and abs(b - 0x2D) <= 16
        ):
            return True
        return False

    unsafe = []
    for y in list(range(0, SAFE_TOP)) + list(range(SAFE_BOT + 1, H)):
        for x in range(0, W, 2):
            if is_type_pixel(*pix[x, y]):
                unsafe.append((x, y))
                break
    if unsafe:
        raise SystemExit(f'scene {scene_no} has type outside the safe box, e.g. {unsafe[:4]}')


def encode(spec, scenes, duration, out_mp4: Path):
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    music = ensure_music()
    cmd = [
        'ffmpeg', '-v', 'error', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
        '-stream_loop', '-1', '-i', str(music),
        '-filter_complex',
        (
            f'[1:a]atrim=0:{duration:.4f},afade=t=in:st=0:d=0.3,'
            f'afade=t=out:st={max(0.0, duration - 1.5):.4f}:d=1.5,'
            f'loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,aformat=channel_layouts=stereo[aout]'
        ),
        '-map', '0:v', '-map', '[aout]',
        '-t', f'{duration:.4f}',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-ar', '48000',
        '-movflags', '+faststart', '-map_metadata', '-1',
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    teal = background()
    mids = {}
    written = 0

    def write(im):
        nonlocal written
        proc.stdin.write(im.convert('RGB').tobytes())
        written += 1

    try:
        for i, scene in enumerate(scenes):
            # Scene 0 starts at t=0. Later scenes already used FADE_IN frames
            # of local time during the transition, so the hold continues.
            t0 = 0.0 if i == 0 else FADE_IN / FPS
            mid_k = scene['frames'] // 2
            for k in range(scene['frames']):
                t_local = t0 + k / FPS
                frame = compose(scene['base'], scene['layers'], t_local)
                if k == mid_k:
                    mids[i] = frame.copy()
                write(frame)
            if i < len(scenes) - 1:
                end_still = settled_frame(scene)
                for k in range(FADE_OUT):
                    p = (k + 1) / FADE_OUT
                    write(fade_towards(end_still, teal, p))
                nxt = scenes[i + 1]
                for k in range(FADE_IN):
                    p = (k + 1) / FADE_IN
                    frame = compose(nxt['base'], nxt['layers'], k / FPS)
                    write(fade_towards(teal, frame, p))
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f'ffmpeg failed with {rc}')
    except BrokenPipeError:
        rc = proc.wait()
        raise SystemExit(f'ffmpeg pipe broke, rc={rc}')
    return mids, written


def probe(path: Path) -> dict:
    raw = subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate,channels',
        '-of', 'json', str(path),
    ], text=True)
    return json.loads(raw)


def audio_mean_db(path: Path) -> float:
    proc = subprocess.run(
        ['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'volumedetect', '-f', 'null', '-'],
        capture_output=True, text=True,
    )
    blob = proc.stderr
    match = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?) dB', blob)
    if not match:
        raise SystemExit(f'could not read loudness of {path.name}\n{blob[-400:]}')
    return float(match.group(1))


def write_licence(path: Path, music: Path):
    digest = hashlib.sha256(music.read_bytes()).hexdigest()
    marker = music.with_suffix('.downloaded.txt')
    downloaded = marker.read_text().strip() if marker.exists() else date.today().isoformat()
    duration = subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=nw=1:nk=1', str(music),
    ], text=True).strip()
    path.write_text(
        f'''# Music licence proof

This Reel uses one music bed. No other track, voiceover, or TTS.

- Track: City Loop
- Author: wipics
- Source page: {MUSIC_PAGE}
- File downloaded: {MUSIC_URL}
- Terms: CC0 1.0 Universal (public domain). The person who associated the work with this deed has dedicated it to the public domain by waiving all of their rights to the work worldwide under copyright law, including all related and neighbouring rights, to the extent allowed by law. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission. Deed: https://creativecommons.org/publicdomain/zero/1.0/
- Download date: {downloaded}
- File duration: {duration} seconds
- SHA-256: `{digest}`
- Reference proof: ../licence/CITY_LOOP_LICENCE_PROOF.md

No attribution is required under CC0. The uploader's authorship claim is not independently verified.
'''
    )


def render_one(spec_path: Path, jk: str, inn: str, stills_only: bool) -> dict:
    spec = json.loads(spec_path.read_text())
    scenes, bounds, duration, total = build_scenes(spec, jk, inn)
    stem = spec_path.stem
    work = WORK / stem
    still_paths = render_stills(spec, scenes, work)
    for i, path in enumerate(still_paths, start=1):
        verify_frame(path, i)
    (work / 'text_bounds.json').write_text(json.dumps({
        'duration_s': duration,
        'frames': total,
        'elements': bounds,
    }, indent=2) + '\n')
    info = {
        'asset_id': spec['asset_id'],
        'template_id': spec['template_id'],
        'date': spec['date'],
        'weekday': spec.get('weekday', ''),
        'file': f'{stem}.mp4',
        'duration_s': round(duration, 3),
        'frames': total,
        'captions': spec['captions'],
        'links': spec['links'],
    }
    if stills_only:
        print(f'stills {stem} {duration:.2f}s')
        return info
    out_mp4 = OUT_DIR / f'{stem}.mp4'
    mids, written = encode(spec, scenes, duration, out_mp4)
    if written != total:
        raise SystemExit(f'frame count {written} != {total} for {stem}')
    mid_paths = []
    for i, im in mids.items():
        path = work / f'0{i+1}_mid.png'
        im.save(path)
        verify_frame(path, i + 1)
        mid_paths.append(path)
    cover = OUT_DIR / f'{stem}.cover.png'
    contact = OUT_DIR / f'{stem}.contact.png'
    # Cover is the settled hook, the frame people see as the thumbnail.
    Image.open(still_paths[0]).save(cover, optimize=True)
    contact_sheet(mid_paths).save(contact, optimize=True)
    write_licence(OUT_DIR / f'{stem}.LICENCE_PROOF.md', MUSIC)
    meta = probe(out_mp4)
    streams = meta['streams']
    video = next(s for s in streams if s['codec_type'] == 'video')
    audio = next(s for s in streams if s['codec_type'] == 'audio')
    got = float(meta['format']['duration'])
    if video.get('width') != W or video.get('height') != H:
        raise SystemExit(f'{stem} is {video.get("width")}x{video.get("height")}')
    if audio.get('codec_name') != 'aac':
        raise SystemExit(f'{stem} audio is {audio.get("codec_name")}')
    if abs(got - duration) > 0.15:
        raise SystemExit(f'{stem} duration {got} != {duration}')
    mean_db = audio_mean_db(out_mp4)
    if mean_db < -30:
        raise SystemExit(f'{stem} music is too quiet ({mean_db} dB)')
    info['mean_volume_db'] = mean_db
    info['probed_duration_s'] = round(got, 3)
    print(f'wrote {out_mp4.name} {got:.2f}s mean {mean_db:.1f} dB')
    return info


def write_schedule(rows: list[dict]):
    lines = [
        '# Reel schedule — 17 to 27 November 2026',
        '',
        'One music-only Reel per posting weekday. 16 November is already filled and is not in this batch.',
        'Post around 12:30 Europe/London. Same master on Facebook, Instagram and TikTok; captions and links differ.',
        'Do not publish from this file until the slot is confirmed empty.',
        '',
        'Music on every file: City Loop by wipics, CC0. See each `*.LICENCE_PROOF.md` and `../licence/CITY_LOOP_LICENCE_PROOF.md`.',
        '',
    ]
    for row in sorted(rows, key=lambda r: r['date']):
        y, m, d = row['date'].split('-')
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        when = f"{row['weekday']} {int(d)} {months[int(m)]} {y}"
        length = row.get('probed_duration_s', row['duration_s'])
        lines += [
            f'## {when}',
            '',
            f'- Date: {row["date"]}',
            f'- template_id: `{row["template_id"]}`',
            f'- asset_id: `{row["asset_id"]}`',
            f'- File: `{row["file"]}`',
            f'- Length: {length:.2f}s',
            f'- Cover: `{Path(row["file"]).stem}.cover.png`',
            f'- QA contact sheet: `{Path(row["file"]).stem}.contact.png`',
            f'- Licence: `{Path(row["file"]).stem}.LICENCE_PROOF.md`',
            '',
            '### Facebook caption',
            '',
            row['captions']['facebook'].strip(),
            '',
            '### Instagram and TikTok caption',
            '',
            row['captions']['instagram_tiktok'].strip(),
            '',
            '### Links',
            '',
        ]
        for key, url in row['links'].items():
            lines.append(f'- {key}: {url}')
        lines.append('')
    (OUT_DIR / 'SCHEDULE.md').write_text('\n'.join(lines))


def main(argv: list[str]):
    stills_only = '--stills' in argv
    args = [a for a in argv if a != '--stills']
    jk, inn = ensure_fonts()
    if not args:
        spec_paths = sorted(SPECS.glob('*.json'))
    else:
        spec_paths = [Path(a) if Path(a).is_absolute() else HERE / a for a in args]
    if not spec_paths:
        raise SystemExit(f'no specs in {SPECS}')
    if not stills_only:
        ensure_music()
    rows = []
    for path in spec_paths:
        rows.append(render_one(path, jk, inn, stills_only))
    if not stills_only and len(spec_paths) == len(list(SPECS.glob('*.json'))):
        write_schedule(rows)
        print(f'wrote {OUT_DIR / "SCHEDULE.md"}')


if __name__ == '__main__':
    main(sys.argv[1:])
