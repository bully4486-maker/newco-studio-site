# Music licence proof (retrieved 25 Oct 2026, Europe/London)

## Track used: "City Loop" by wipics (OpenGameArt.org)
- Page: https://opengameart.org/content/city-loop-0
- File: https://opengameart.org/sites/default/files/city-loop.mp3 (saved: music/city-loop.mp3; MP3 tag shows GarageBand 10.3.4, i.e. human-made, uploaded 15 Apr 2020, before generative-AI music tools)
- Page text as retrieved: "License(s): CC0 ... Copyright/Attribution Notice: Public Domain ... City Loop. Has an upbeat feel to it."
- Saved copy of the page: licence/opengameart_city-loop_page.html
- CC0 1.0 deed: https://creativecommons.org/publicdomain/zero/1.0/ (saved: licence/cc0_1.0_deed.html). Key text: "The person who associated a work with this deed has dedicated the work to the public domain by waiving all of his or her rights ... You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission."
- No attribution needed. Residual risk: the uploader's own claim of authorship is not independently verified (true of any user-upload site, Pixabay included). Not registered with any Content ID system as far as can be known, but Meta's rights manager could in theory still flag it: check the ad status after upload.

## Why NOT Pixabay (the brief's first choice)
- pixabay.com and cdn.pixabay.com returned 403 / Cloudflare "Just a moment" bot challenges from the box, so no Pixabay track could be downloaded here. I did not try to get round the challenge.
- Pixabay Content Licence summary, retrieved via WebFetch from https://pixabay.com/service/license-summary/ : allows use "for free", "without having to attribute", and "Modify or adapt Content into new works"; prohibits Standalone redistribution, recognisable trademarks, misleading uses, and use in a trade-mark/business name. (Only the full licence at https://pixabay.com/service/terms/ is binding.) Commercial/ad use is allowed under it, but Pixabay Music tracks may be flagged by Content ID systems, so always check on upload.
- To swap in a Pixabay track: download it by hand in a normal browser, save the track page URL + a screenshot of its licence line here, then run: `ffmpeg -ss 0 -t 11.5 -i TRACK.mp3 -af "afade=t=in:st=0:d=0.4,afade=t=out:st=10:d=1.5,loudnorm=I=-18:TP=-1.5:LRA=7" -ar 48000 -ac 2 music/bed_feed.wav` (use I=-15 for reels), then `python3 render2.py data2_generic.json out/x.mp4 45 music/bed_feed.wav`.
