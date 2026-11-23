# NewCo social renderer (offline tooling)

Isolated under `tools/social-renderer/`. **Not part of the public website deploy.** No chatbot, publishing, scheduling, paid APIs, or LLM calls.

Adapted from the existing local box renderer (`video_poc/render3.py` + `template3.html`): same Playwright → PNG frames → optional ffmpeg path, rewritten as a **config-driven** CLI with validation, hash cache, matching covers, and a branded endcard.

## Why this exists

Reduce repeated Grok/model calls for ordinary re-renders. Copy and layout live in JSON + HTML. Humans still own creative taste, rights, and the **9.0 quality target** against external guidance — automated checks are not a self-certified score.

## Outputs

| Mode | Command | Result |
| --- | --- | --- |
| Preview (default) | `python3 cli.py samples/master_websites99_916.json` | Contact sheet PNG + `*_cover_1080x1920.png` |
| Validate | `python3 cli.py samples/….json --mode validate` | Schema / banned-copy / music meta checks |
| Video | `python3 cli.py samples/….json --mode video` | 1080×1920 mp4 (music metadata required) |
| Batch | `python3 cli.py x.json --batch samples/` | All JSON masters in a folder |

Hash cache (`.cache/`) skips unchanged masters unless `--force`.

## Music rules

- Future public videos **must** have **music** — no voiceover / narration / TTS / people / comedy pipelines in this tool.
- Supply a **cross-platform licensed** file plus `music` metadata (`title`, `artist_or_uploader`, `source_url`, `licence`, `licence_url`, `cross_platform_ok: true`, `file`).
- Do **not** copy platform-only library tracks.
- With no licensed audio: use `fixtures/test_only_audio/` (filenames + meta must say **TEST ONLY**). That path is for plumbing only — **not publication-ready**, and it must not claim a real licence.
- `fixtures/LICENCE_PROOF.md.reference_only` is an older provenance lead only; audio from that lead is **not** bundled and was **not** re-verified here.

## Sample master

`samples/master_websites99_916.json` — Keith-style **dark teal + central phone + large headline + endcard**.

- Studio facts: **£99** one-page / fixes **from £19**; VAT not charged; quote https://studio.newcopacks.co.uk/websites-99/
- Phone: Halvercroft crop labelled **Example of our work** (not the old “Demo site · fictional business” badge; not Hearth & Crumb café frames)
- Etsy UK VAT-inclusive prices: **omitted** (not verified in this pass)
- Analytics: week-ending 6 Nov 2026 organic data is sparse (0 interactions on sampled posts) — **insufficient to declare a template winner**

Captions for FB / IG / TikTok: `samples/captions_fb_ig_tt.md`.

**Do not** alter published Wed 11 Nov photo or either Thu 12 Nov Facebook Reel from this tool.

## Tests

```bash
cd tools/social-renderer
python3 -m pytest tests/ -q
# slower Playwright stills:
python3 -m pytest tests/test_render_preview.py -q
```

Coverage: validation, banned speech/copy, music metadata, hash cache, overflow/safe-area, contact-sheet render.

## Archive for box reuse

```bash
./scripts/make_archive.sh
```

Writes a zip under `../../../../../../opt/cursor/artifacts/` when run in Cloud Agent, or `archive/` locally — source, README, samples, tests, fixtures, preview PNG if present.

## Remaining human limits

- Rights clearance for music and product screenshots
- Platform AI / branded-content disclosures
- Creative quality vs external 9.0 guidance
- Live Etsy price checks before any shop pricing appears in a master
- Spacing / recycle decisions for strong eligible posts (no blind duplicates; no deletion of old posts)
