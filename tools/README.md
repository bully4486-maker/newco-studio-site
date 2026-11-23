# Tools (not product UI)

Offline production helpers. **Not** part of the studio website offer pages.

## Deploy warning (GitHub Pages)

This repo’s site is served from the repository root. If `tools/` is merged to the default branch without a Pages exclude, GitHub Pages will also expose these paths as static URLs.

Until a publish filter or a separate tooling repo exists: treat PRs that only add `tools/` as **tooling drafts** — merge only when exposure is acceptable or Pages is configured to omit `tools/`.

## Layout

| Path | Role |
| --- | --- |
| `social-renderer/` | Config-driven 9:16 music-only master / cover / contact-sheet CLI (adapted from local `video_poc`) |
| `../assets/social/` | Existing **static** 1080×1350 board pack (HTML → Chrome PNG). Different format; reuse brand facts, do not duplicate into video masters blindly |

Published Wed 11 Nov photo and both Thu 12 Nov Facebook Reels stay outside this folder’s remit.
