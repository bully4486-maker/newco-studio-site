# Social pack scores

Method: nine categories, as on the published fb2_99 post (8.7). Each is 0–10. Overall is the mean of the eight scored categories, to 1 decimal. Speed is n/a and is left out of the mean. Pass is 8.5 or above.

An author scored the boards first. A reviewer from another model family then scored them, more than once, after each rework. The lower overall stands. These tables are that reviewer’s scores.

Compliance, shipped assets: pass. No claim that a model does the work. No local-service framing. No voice. Prices are the published ones. Demos are labelled fictional.

Provenance: pass. Log at the bottom.

## speed-1080x1350.png

| Category | Score | Note |
| --- | --- | --- |
| Visual | 8.7 | Sand board, dark time cards, Paws phone. |
| Typography | 8.6 | “24 hours” carries the board. Deck and labels stay at or above 28px. |
| Imagery | 8.3 | Live Paws Parlour capture. The banner is intact. Type inside the phone is small, which is what a real page looks like at this size. |
| Layout | 8.6 | The three cards fill the column beside the phone. |
| Trust | 8.8 | 24 hours, a few days, date in the quote. Demo labelled. |
| Mobile | 8.6 | 1080×1350. Secondary type holds up. |
| Call to action | 8.7 | URL and “Get a fixed quote”. |
| Originality | 8.0 | Same phone-and-column system as the rest of the pack. The hook is its own. |
| Speed | n/a | |
| **Overall** | **8.5** | PASS. Weakest: Originality. Author had scored this higher. The review stands. |

## included-1080x1350.png

| Category | Score | Note |
| --- | --- | --- |
| Visual | 8.6 | Four numbered rows and the Halvercroft phone. |
| Typography | 8.6 | Row text at 28px and up. |
| Imagery | 8.3 | Live Halvercroft capture. The demo’s own headline says “plain English”. That is the page, not our hook. |
| Layout | 8.6 | Rows fill the height. |
| Trust | 8.8 | The list matches the site. Hosting stays in your name. Demo labelled. |
| Mobile | 8.6 | Descriptions are 28px. |
| Call to action | 8.7 | URL and button. |
| Originality | 7.9 | The four-row shape is familiar. The hook is “What you get in the build.” |
| Speed | n/a | |
| **Overall** | **8.5** | PASS. Weakest: Originality. |

## faq-1080x1350.png

| Category | Score | Note |
| --- | --- | --- |
| Visual | 8.6 | White cards on sand, Paws phone. |
| Typography | 8.6 | Questions 28px, answers larger. |
| Imagery | 8.3 | Live Paws capture next to the demo answer. |
| Layout | 8.6 | Four cards fill. |
| Trust | 8.9 | The answers are the site’s FAQ, including that the demos are fictional. |
| Mobile | 8.6 | On the 28px floor for the question labels. |
| Call to action | 8.7 | URL and button. |
| Originality | 7.9 | Hook is “Worth asking first.” |
| Speed | n/a | |
| **Overall** | **8.5** | PASS. Weakest: Originality. |

## how-1080x1350.png

| Category | Score | Note |
| --- | --- | --- |
| Visual | 8.6 | Mint plates, dark numerals, Halvercroft phone. |
| Typography | 8.6 | Numerals are 48px on mint, not the old faint circles. |
| Imagery | 8.3 | Live Halvercroft capture. |
| Layout | 8.6 | Four steps fill the column. |
| Trust | 8.8 | Brief, quote, build, hand-over. You approve, then pay. |
| Mobile | 8.6 | The step numbers read at a thumbnail. |
| Call to action | 8.7 | URL and button. |
| Originality | 8.0 | Hook is “Four steps, then it’s yours.” |
| Speed | n/a | |
| **Overall** | **8.5** | PASS. Weakest: Originality. |

## Captions

The review scored the longer caption file, which also covered boards that were later withheld. The shipped file is those four sections with nothing new added. Mean of Typography, Trust, Call to action and Originality.

| Category | Score | Note |
| --- | --- | --- |
| Visual | n/a | |
| Typography | 8.6 | Short. UK English. Different shape per post. |
| Imagery | n/a | |
| Layout | n/a | |
| Trust | 9.0 | Fictional demos are named as fictional. No testimonials. |
| Mobile | n/a | |
| Call to action | 8.3 | Each one ends on the quote URL. The line above it is not always the same button label. |
| Originality | 8.2 | Hashtag sets are no longer one pool reshuffled. Some facts repeat because they are the offer. |
| Speed | n/a | |
| **Overall** | **8.5** | PASS. Weakest: Call to action. |

## Withheld

Not in the folder. Reviewer overalls from the last pass that looked at each one:

| Asset | Overall | Weakest | Verdict |
| --- | --- | --- | --- |
| price-1080x1350.png | 8.4 | Originality 8.0 | FAIL |
| price square | 8.2 | Layout | FAIL |
| speed square | 8.4 | Originality | FAIL |
| included square | 8.4 | Originality | FAIL |
| faq square | 8.4 | Originality | FAIL |
| how square | 8.4 | Originality | FAIL |
| before-after-1080x1350.png | 8.4 | Mobile 7.9 | FAIL |
| before-after square | 8.0 | Layout | FAIL |
| carousel/01-offer-1080x1350.png | 8.4 | Originality 8.0 | FAIL |
| carousel/02-included-1080x1350.png | 8.5 | Originality | PASS as a slide, withheld with the set |
| carousel/03-how-1080x1350.png | 8.5 | Originality | PASS as a slide, withheld with the set |
| carousel/04-before-after-1080x1350.png | 8.3 | Mobile 7.9 | FAIL |
| carousel/05-quote-1080x1350.png | 8.5 | Originality | PASS as a slide, withheld with the set |
| one-page-99-slideshow.mp4 | 8.3 | Originality | FAIL |

Slides 02, 03 and 05 cleared 8.5 and were still withheld. Posting them would publish “02/05”, “03/05” and “05/05” without the slides that failed.

## Provenance log

26 October 2026. exiftool 12.76. `source/strip_and_check.sh`.

The earlier text-only `how-1080x1350.png` was flagged for a possible XMP marker. Its chunks were IHDR, IDAT, IEND only. A `xmp` byte sequence was inside a compressed IDAT, not an XMP packet. The rebuilt file has those same chunk types, a search finds no `xmp` bytes, and the check PASSes.

```
PASS assets/social/source/shots/halvercroft-hero.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/source/shots/hearth-hero.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/source/shots/paws-hero.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/source/shots/halvercroft-crop.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/source/shots/hearth-crop.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/source/shots/paws-crop.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/faq-1080x1350.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/how-1080x1350.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/included-1080x1350.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
PASS assets/social/speed-1080x1350.png (no XMP/IPTC/EXIF/C2PA/JUMBF)
```
