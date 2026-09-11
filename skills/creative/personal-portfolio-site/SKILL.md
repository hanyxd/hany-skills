---
name: personal-portfolio-site
description: Build the user's personal about/resume web pages.
metadata:
  hermes:
    tags: [portfolio, resume, personal-site, web]
---

# Personal Portfolio Site (this user)

Builds and iterates on the user's personal web pages. Current site lives in `/home/hany/web-test/` and is served with `python3 -m http.server 8080`. Pages: `index.html` (landing), `about.html` (bio/skills/projects/reading), `Hany_Elansari_Resume.html` (print-ready resume), `Hany_Elansari_CV.md` (plain-text CV). Live URLs are `<host>:8080/<page>`.

## Always-on rules

- **Identity facts come from the user's stated identity in memory — NOT freshly scraped system config.** Git config name/email and github-API handles can return a STALE alias the user stopped using (happened: system showed `hanyxd`/`h60930593`, real handle/email were `hanyxvip`/`moop85514@gmail.com`). Always cross-check a scraped handle against the saved user profile before writing it into pages.
- **Aesthetic standard for this user:** dark, refined surfaces (deep navy like `#080a10`/`#0b0d14`) with a warm gold accent (`#c8a455`) plus muted support hues (sage `#5dbf96`, lavender `#8e80b8`, ice `#7aa8cc`, rose `#b87a8c`) and warm off-white text (`#f2f0eb`). The user explicitly rejected harsh neon / cyberpunk palettes (bright pink/blue on near-black) as "color is bad." Default to this palette; never reach for neon.
- **Stick to the dark/gold aesthetic across all pages** so nav/footer cross-links look coherent.

## Workflow

1. Gather real details: user profile from memory first; if a CV/doc was pasted into the conversation, it is authoritative for skills/projects/awards. Reuse real, verifiable project names and descriptions (public GitHub repos, pasted CV). Mark genuinely-unknown stats as stats the user must confirm.
2. Build each page as a single self-contained HTML file (embedded CSS/JS), matching the aesthetic standard and the existing palette/section conventions.
3. Wire cross-page navigation: every page's top nav and footer link to siblings using relative paths, and use anchor deep-links where the target section exists (e.g. `about.html#projects`). Match the actual section id — don't guess (`#work` vs the real `#projects`).
4. Serve with `python3 -m http.server 8080` (background terminal), then verify.
5. Verify in headless chromium (BU_CDP_URL path from skill `hermes-browser-exec`):
   - Confirm each page renders via `document.body.innerText` — text-first, the agent cannot view images.
   - Click every cross-link and anchor deep-link, and assert the resulting `location.pathname` / hash. Both directions (about→resume, resume→about, home↔about).

## Pitfalls

- Scraped identity (git config name/email, github API handle) can be a stale alias the user dropped. The user's stated current identity in memory wins — always cross-check before branding a page with it.
- Get section ids right when building cross-links: verify the target `id` attribute exists before writing an anchor href, and re-check after any rename.
- A `// comment` line in a browser_exec code string is parsed as Python and throws SyntaxError — write JS lines without a leading `//` inside browser_exec code.
- `vision_analyze` on a captured screenshot may time out or return "no image" in this environment; rely on DOM text reads (`body.innerText`, `document.querySelector(...).getAttribute('href')`) for verification instead.
- When a user says "use my name" or shortens/changes a display name, apply it everywhere (nav brand, hero, about, footer, file names) in one pass — a rename left in one spot reads as a missed edit.
- Emoji preferences are user-specific: if the user flags an emoji (e.g. a religious one on a book card), swap it for a neutral icon and keep the rest of the section.
