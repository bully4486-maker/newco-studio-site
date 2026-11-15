# Reel template (music-only, no voiceover)

`build_reel.py` renders a 1080×1920, 30 fps Reel from a JSON spec. The frame stays the house style: teal `#00292D`, panels `#02505A`, mint `#9CC4B8`, Plus Jakarta Sans and Inter, the original logo on its white square, and the end card “NewCo Studio · websites from £99 · fixes from £19 · studio.newcopacks.co.uk”.

Specs live in `specs/<date>_<template_id>.json`. Each one lists the scenes (hook, phone, ticks, panel, sheet, end card), the on-screen lines, and the captions.

Run, with Pillow and ffmpeg installed:

```bash
python3 _reels/build_reel.py            # every spec → out/
python3 _reels/build_reel.py --stills   # settled frames only, under work/
python3 _reels/build_reel.py specs/2026-11-17_tpl_site99_phone_v1.json
```

Fonts: if `fonts/PlusJakartaSans-Variable.ttf` or `fonts/Inter-Variable.ttf` is missing, the script downloads them from Google Fonts (OFL). The licence texts sit beside the files.

Music: City Loop by wipics, CC0, downloaded from OpenGameArt if `music/city-loop.mp3` is missing. Proof: `licence/CITY_LOOP_LICENCE_PROOF.md`. A full encode writes `out/<name>.LICENCE_PROOF.md` next to each mp4. No other track is used.

Each finished Reel also gets a cover PNG and a QA contact sheet in `out/`. `out/SCHEDULE.md` is rewritten when every spec is rendered. Check the contact sheet before use: type stays inside y 269–1248, prices match the spec, and nothing is cut off.

Rules: £99 sites and fixes from £19 (VAT is not charged). Etsy buyer prices are VAT-inclusive (£9.59 UK Etsy Seller Bookkeeping, £11.99 Counter Book). No voiceover, no people, no reviews or ratings, UK English, music only.

The folder starts with `_`, so GitHub Pages (Jekyll) does not publish it. `work/` and `*.mp3` stay gitignored. The mp4s, covers, contact sheets and licence proofs in `out/` are committed.
