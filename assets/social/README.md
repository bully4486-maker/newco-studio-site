# Social pack — £99 one-page website

Ready for later posting. Nothing here has been published.

Four portrait boards cleared the house gate. The standing score is the lower of the author score and an independent review. Anything under 8.5 was rendered, scored, and left out of this folder.

Brand, prices and timings match the live site. A one-page website starts at £99. A written quote comes back within 24 hours, usually sooner. Fixes start at £19. The phones are fresh mobile captures of the live demos. Each one is labelled “Demo site · fictional business”.

Regenerate the shipped PNGs:

```bash
node assets/social/source/capture.mjs
node assets/social/source/render.mjs
bash assets/social/source/strip_and_check.sh assets/social/source/shots/*.png assets/social/*.png
```

`render.mjs` only writes the four boards below. The other artboards are still in `source/posts.html`.

## Shipped images

1080×1350. Facebook or LinkedIn feed.

| File | Size | Use | Standing score |
| --- | --- | --- | --- |
| `speed-1080x1350.png` | 1080×1350, 538,910 bytes | How long it takes. Paws Parlour demo. | 8.5 |
| `included-1080x1350.png` | 1080×1350, 602,894 bytes | What’s in the £99 build. Halvercroft demo. | 8.5 |
| `faq-1080x1350.png` | 1080×1350, 540,752 bytes | Four answers. Paws Parlour demo. | 8.5 |
| `how-1080x1350.png` | 1080×1350, 590,837 bytes | Four steps. Halvercroft demo. | 8.5 |

## Withheld

Scored by the reviewer under 8.5, so not in this folder:

| Board | Reviewer overall | Why it stayed under |
| --- | --- | --- |
| Price, both sizes | 8.4 | Originality 8.0, and empty bands above and below the copy. |
| Speed, included, FAQ, how squares | 8.1–8.4 | Tight squares. The phone was small and the caption wrapped. |
| Before / after, both sizes, and carousel 04 | 8.0–8.4 | In-phone type sat under the 28px floor once the phone was small enough to fit beside the drawing. |
| Carousel 01 | 8.4 | Originality 8.0. |
| Carousel 05 | 8.5 on the last pass | Not shipped on its own. It is slide 05 of a set whose other slides failed, and it still carries “05/05”. |
| Carousel 02 and 03 | 8.5 | Same reason. They read as slides 02 and 03 of a five-slide post. |
| Silent slideshow | 8.3 | Same frames, and the crossfade ghosted the type. ffmpeg is available. The clip was built, scored, and not kept. |

## Copy and source

| File | What it is |
| --- | --- |
| `captions.md` | Facebook caption, LinkedIn caption and 3 hashtag options for each shipped board. |
| `SCORE.md` | Standing scores, withheld scores, and the metadata PASS log. |
| `source/posts.html` | All artboards, including the ones not shipped. |
| `source/social.css` | Shared layout and type. |
| `source/render.mjs` | Headless Chrome renderer for the four shipped boards. |
| `source/capture.mjs` | Mobile captures of the live demos. |
| `source/shots/` | Those captures, stripped. |
| `source/strip_and_check.sh` | Metadata strip and check. |

Captions point at https://studio.newcopacks.co.uk/#quote

## Metadata

`strip_and_check.sh` on 26 October 2026, exiftool 12.76. Every shipped PNG and every source shot printed `PASS`. The log is in `SCORE.md`.

The previous `how-1080x1350.png` had been flagged for a possible XMP marker. That file’s PNG chunks were only IHDR, IDAT and IEND. The byte sequence `xmp` sat inside a compressed IDAT, not in an XMP chunk. The rebuilt file has the same chunk types, contains no `xmp` bytes, and PASSes the strip check.
