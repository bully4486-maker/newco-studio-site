# Social pack — £99 one-page website

Ready for later posting. Nothing here has been published.

Brand line, prices and timings match the live site. The one-page website starts at £99. A written fixed quote comes back within 24 hours. The before-and-after frames are fictional illustrations, labelled on the images and in `captions.md`.

Regenerate the PNGs from `source/` with Chrome:

```bash
node assets/social/source/render.mjs
```

## Feed images

Portrait is 1080×1350 (4:5). Square is 1080×1080. Both suit a Facebook or LinkedIn image post. Use portrait in the feed. Use square where the placement crops to a square.

| File | Pixels | Size | Use |
| --- | --- | --- | --- |
| `price-1080x1350.png` | 1080×1350 | 221 KB | Facebook, LinkedIn. Price. |
| `price-1080x1080.png` | 1080×1080 | 186 KB | Facebook, LinkedIn. Price. |
| `speed-1080x1350.png` | 1080×1350 | 189 KB | Facebook, LinkedIn. How long it takes. |
| `speed-1080x1080.png` | 1080×1080 | 154 KB | Facebook, LinkedIn. How long it takes. |
| `included-1080x1350.png` | 1080×1350 | 241 KB | Facebook, LinkedIn. What’s included. |
| `included-1080x1080.png` | 1080×1080 | 204 KB | Facebook, LinkedIn. What’s included. |
| `before-after-1080x1350.png` | 1080×1350 | 221 KB | Facebook, LinkedIn. Fictional before/after. |
| `before-after-1080x1080.png` | 1080×1080 | 178 KB | Facebook, LinkedIn. Fictional before/after. |
| `faq-1080x1350.png` | 1080×1350 | 190 KB | Facebook, LinkedIn. FAQ. |
| `faq-1080x1080.png` | 1080×1080 | 166 KB | Facebook, LinkedIn. FAQ. |
| `how-1080x1350.png` | 1080×1350 | 223 KB | Facebook, LinkedIn. How it works. |
| `how-1080x1080.png` | 1080×1080 | 179 KB | Facebook, LinkedIn. How it works. |

## Carousel

Post these five slides in order, as one Facebook or LinkedIn carousel. All are 1080×1350.

| File | Size | Slide |
| --- | --- | --- |
| `carousel/01-offer-1080x1350.png` | 180 KB | Offer, from £99 |
| `carousel/02-included-1080x1350.png` | 233 KB | What’s included |
| `carousel/03-how-1080x1350.png` | 217 KB | How it works |
| `carousel/04-before-after-1080x1350.png` | 222 KB | Fictional before/after |
| `carousel/05-quote-1080x1350.png` | 133 KB | Quote form |

## Video

| File | Pixels | Size | Use |
| --- | --- | --- | --- |
| `one-page-99-slideshow.mp4` | 1080×1350, 11.6s, silent H.264 | 1.1 MB | Facebook, LinkedIn. Same five slides, short fades, no audio. |

ffmpeg 6.1.1 was available, so the clip is included. It is under 15 MB and has no audio track.

## Copy and source

| File | Size | What it is |
| --- | --- | --- |
| `captions.md` | 7 KB | Facebook caption, LinkedIn caption and 3 hashtag options for each graphic. |
| `source/posts.html` | 17 KB | Artboards. Open `?id=` to preview one. |
| `source/social.css` | 13 KB | Shared layout and type. |
| `source/render.mjs` | 7 KB | Headless Chrome renderer for the PNGs. |

Captions point at the quote form: https://studio.newcopacks.co.uk/#quote
