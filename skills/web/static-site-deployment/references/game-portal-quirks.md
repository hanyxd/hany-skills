---
title: Game portal quirks — static HTML game sites
---

# Game Portal Quirks

Specific pitfalls that show up on static HTML game portals (unblocked-games style, folders-per-game, no backend).

## Multi-threaded games — no `index.html` in each game folder

Many static game folders ship only numbered entry files (`1.html`, `3.html`, etc.) and **no `index.html`**. When you download the repo from GitHub, the folder exists but the default entry is missing, so any link to `games/<name>/index.html` 404s.

**Symptom:** `grep -r 'href="games/' gamepage.html` reports N links; `ls games/<name>/` shows files but no `index.html`; live site 404s on those games.

**Fix:** for each such folder, create `games/<name>/index.html` containing a refresh redirect to the real file:

```html
<meta http-equiv="refresh" content="0; url=<real-entry>"/>
```

Pick the real entry by listing the folder (`ls games/<name>/`) and choosing the top numbered file. Do this after confirming which file is the actual game entry — not every numbered file is a game.

**Why this happens:** game authors sometimes bundle an index-less folder (the game runs from `1.html` or similar) and never commit an `index.html`. The portal's link points at a path that does not exist in the committed tree, even though the folder and its files are present.

## Neutralize "no ads" copy before AdSense

After the AdSense snippet (`<script async src="...adsbygoogle.js?client=ca-pub-...">`) is on a page, **any copy on that page or its legal/readme that says "no ads" will get AdSense rejected**. Neutralize it everywhere, in this order:

1. All HTML pages (index.html, gamepage.html, settings, contact, 404).
2. README / legal / terms text.
3. Hero badge, meta description, lead paragraph, and any marketing copy that mentions "no ads" or "ad-free".

Do a single grep across the project after adding the snippet:

```bash
grep -ri 'no ads\|noad\|ad-free\|noad' --include='*.html' --include='*.md' --include='*.txt'
```

Replace each instance with a neutral phrase ("Free to Play", "No downloads", etc.) that does not claim the opposite of what the site now does. Do **not** leave a stat or badge saying "0 Ads" if the site now runs ads — it is the most visible contradiction and the first thing AdSense reviewers notice.

## "Downloads" stat on a static site is cosmetic-only

A hero stat labeled "0 Downloads" (or similar) on a purely static site with no backend is a decorative number — there is no server-side counter. Do not present it as a live metric; if the user wants a real number, wire it from a known constant (e.g. the game catalog count) or remove the stat.
