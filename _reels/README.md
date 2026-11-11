# Reel template (music-only, no voiceover)

`build_reel.py` renders the fbad03 Reel B (£19 fix) format: 1080x1920, 4 scenes (hook, fixes, quote, end card), logo, music bed. Edit the scene text in the script for the next Reel.

Run: `pip install pillow` and have `ffmpeg` installed, then
`REEL_MUSIC=/path/to/licensed-track.mp3 REEL_OUT=out/next.mp4 python3 _reels/build_reel.py`

Optional env: `REEL_WORK` (frames and QA dir, default `_reels/work`), `REEL_LOGO`.
Fonts: Plus Jakarta Sans and Inter (Google Fonts); update the JK and IN paths if they live elsewhere.
Rules: £99 sites / £19 fixes, VAT line as in spec, no AI mentions, no reviews or ratings, UK English, music only. QA frames and a contact sheet are written to the work dir; check them before use.
Folder starts with `_`, so GitHub Pages (Jekyll) does not publish it.
Music licence: before any Reel is used, save `LICENCE_PROOF.md` next to it (track, source, licence terms, download date, proof link), as for City Loop. No proof, no Compliance sign-off.
