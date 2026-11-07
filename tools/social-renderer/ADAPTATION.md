# Adaptation notes (from existing box renderer)

Source zip: `existing-renderer-reference` → `video_poc/`.

| Legacy | Role here |
| --- | --- |
| `render3.py` | Logic folded into `lib/render_engine.py` + `cli.py` (config paths, cache, preview-first) |
| `template3.html` | Adapted as `templates/teal_phone_v1.html` (9:16 only; data-driven labels; static phone screen; local fonts) |
| `data2_generic.json` | Replaced by `samples/master_websites99_916.json` (no founding / first-3 / fictional badge) |
| `render2.py` / `template2.html` | Older 11.5s path — not ported; keep reference only |
| `licence/LICENCE_PROOF.md` | Copied as `fixtures/LICENCE_PROOF.md.reference_only` — provenance lead, not re-verified; **no audio bundled** |
| Counter Book PNGs | Optional refs under `vendor_assets/counter_book_ref/` (MTD-named still excluded from default masters) |

Intentionally **not** carried over: voiceover/comedy pipelines, café scroll frame packs (`scr3/`), hardcoded “Demo site · fictional business”, silent publication-ready defaults.
