# fbad03 Creative B — Cursor recut spec (desk only)

Render a new music-only 9:16 Reel for the £19 website-fix hook, from the existing `tpl_site99_phone_v1` template. Do not publish, upload, or spend. Do not use files from `it_guide_videos/pilot_build/build.py`, and do not use any asset that shows “demo site”, “fictional”, “founding” or “first 3 clients” (rejected paths are listed in `/workspace/tiktok_launch/MANIFEST.md`).

## Output
- File: `/workspace/ads/fbad03_reelB_fix19.mp4`
- 1080×1920, 9–15 seconds (target 13.2s), H.264 + AAC 48 kHz stereo, 30 fps, yuv420p, `+faststart`, no metadata
- Music only: no voiceover, no TTS, never silent
- Loudness: integrated about −14 LUFS, true peak capped at −1.5 dBTP, 0.3s fade-in, 1.5s fade-out

## Input files (use only these)
- Renderer to copy and adapt: `/workspace/reels/exp-2026-11-09-site99/work/build.py` (`tpl_site99_phone_v1`)
- Style reference frames: `/workspace/reels/exp-2026-11-09-site99/frames/` and `qa/contact_sheet.jpg`
- Logo: `/workspace/newco_studio_logo.png` (original white square, never redrawn)
- Music: `/workspace/video_poc/music/city-loop.mp3` (CC0 “City Loop” by wipics; proof `/workspace/video_poc/licence/LICENCE_PROOF.md`)
- Fonts (already on the box, as in the template): Plus Jakarta Sans and Inter under `/usr/share/fonts/truetype/sand-box/google/`
- Brand: background `#00292D`, panels `#02505A`, mint `#9CC4B8`, text `#FFFFFF`, small “NEWCO STUDIO” wordmark at y=320–342

## Safe zones
Keep all type, ticks, price figures, the URL, the logo and the scene-1 phone (chrome included) inside y 269–1248 and the side 6%:
- Top reserved: y = 0–268 (top 14%)
- Usable: y = 269–1248, x = 65–1015
- Bottom reserved: y = 1249–1919 (bottom 35% begins at y=1248; do not let ink fall below 1248)
The organic site99 master used a looser bottom bound (y=1560). Assert bounds in the renderer. Decorative background ellipses may extend outside the box.

## Motion and transitions
- Each scene: text (and the phone / logo) slides up ~28px and fades in over 0.25s, cubic ease-out, staggered. Hold is then static so mid-scene QA bounds are stable.
- Between scenes: fade out to the teal background, then fade in the next scene. Do not crossfade two headlines. Target duration 13.2s.

## Frames (4 cards; fade-out-then-in; holds sum with fades to 13.2s)

**1 — Hook, 3.0s hold** (`qa/v2/01_mid.png`)
- On-screen: “Broken button?” / “From £19”
- Under the hook, a generic phone mockup (same “Your Business” / “Services · Prices · Contact” device as the template — no trade name). The “Get in touch” button must sit fully inside the phone bezel, with padding from the screen edges. No “demo”, “fictional”, “before” or “broken site” label.

**2 — What we fix, 3.07s hold** (`qa/v2/02_mid.png`)
- On-screen title: “What we fix, from £19”
- Four mint ticks, one per line: “Broken links” · “Broken buttons” · “Details out of date” · “Layout on phones”
- No fictional business name.

**3 — Quote, 3.0s hold** (`qa/v2/03_mid.png`)
- Title: “Written fixed quote” / “within 24 hours”
- Panel: “No call.” / “No obligation.” / “Fixed price first.”
- Under the panel: “Prices as stated. VAT is not charged.”

**4 — End card, 3.13s hold** (`qa/v2/04_mid.png`)
- Logo (unchanged) · “NewCo Studio”
- “Websites from £99” / “Fixes from £19”
- “Tap Send Message below”
- Small “studio.newcopacks.co.uk”
- “UK-wide & worldwide, fully remote”

## Do not put on screen
AI, demo site, fictional, founding, first 3 clients, MTD-ready, clients, reviews, testimonials, scarcity, Oxfordshire, payment splits (fixes are paid once approved, not 50/50), or any URL UTM.

## QA
ffprobe must show 1080×1920 and an audio stream. Duration 9–15s. Confirm music is audible (not a silent or near-silent track). Mid-scene frames, a 1→2 transition grab, numerical y-bounds and a contact sheet go in `/workspace/ads/fbad03_reelB/qa/v2/`. Confirm every text element is inside y 269–1248. v1 of the master is kept at `/workspace/ads/fbad03_reelB_fix19_v1.mp4`.
