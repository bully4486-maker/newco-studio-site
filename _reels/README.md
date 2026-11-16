# Reel template (music-only, no voiceover)

`build_reel.py` renders a 1080×1920, 30 fps Reel from a JSON spec. The frame stays the house style: teal `#00292D`, panels `#02505A`, mint `#9CC4B8`, Plus Jakarta Sans and Inter, and the original logo on its white square.

Service Reels and Etsy spreadsheet Reels end on the studio card: “NewCo Studio · websites from £99 · fixes from £19 · studio.newcopacks.co.uk”. Etsy Reels set the card line to “Shop on Etsy” and do not add a studio UTM. `tpl_book_payhip_v1` is the Payhip book card: a real cover and real pages from `assets/books/`, then the Payhip URL on its own. It does not use the studio end card, and it does not mention VAT.

Specs live in `specs/<date>_<template_id>.json`. Each one lists the scenes (hook, phone, ticks, panel, sheet, end card), the on-screen lines, and the captions.

Run, with Pillow and ffmpeg installed:

```bash
python3 _reels/build_reel.py            # every spec → out/
python3 _reels/build_reel.py --stills   # settled frames only, under work/
python3 _reels/build_reel.py specs/2026-11-17_tpl_site99_phone_v1.json
```

Fonts: if `fonts/PlusJakartaSans-Variable.ttf` or `fonts/Inter-Variable.ttf` is missing, the script downloads them from Google Fonts (OFL). The licence texts sit beside the files.

Music: City Loop by wipics, CC0, downloaded from OpenGameArt if `music/city-loop.mp3` is missing. Proof: `licence/CITY_LOOP_LICENCE_PROOF.md`. A full encode writes `out/<name>.LICENCE_PROOF.md` next to each mp4. No other track is used.

Each finished Reel also gets a cover PNG and a QA contact sheet in `out/`. A bare run leaves the 17–27 November files alone. Pass those spec paths to rebuild them; that rewrites `out/SCHEDULE.md`. Rendering the 30 November–18 December specs writes `out/SCHEDULE_2026-11-30_to_12-18.md` and `out/CONTACT_2026-11-30_to_12-18.png` (hook, middle scene, end card). Check the contact sheet before use: type stays inside y 269–1248, prices match the spec, and nothing is cut off.

Rules: £99 sites and fixes from £19 (VAT is not charged). Etsy buyer prices are VAT-inclusive (£9.59 UK Etsy Seller Bookkeeping, £11.99 Counter Book). No voiceover, no people, no reviews or ratings, UK English, music only.

The folder starts with `_`, so GitHub Pages (Jekyll) does not publish it. `work/` and `*.mp3` stay gitignored. The mp4s, covers, contact sheets and licence proofs in `out/` are committed.
