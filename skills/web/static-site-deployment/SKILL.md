---
name: static-site-deployment
description: "Use when deploying a static site free via Hermes MCP."
---

# Static Site Deployment & Monetization

Deploying a static/browser-only site (all HTML/CSS/JS, no server backend) to a free host, and optionally attaching an MCP server so Hermes can deploy updates directly.

## Host choice (free, no server backend)

- **Netlify** — best when user wants BOTH no-git upload AND an official MCP server for agent-driven deploys. 100GB bandwidth/mo free, free SSL. App subdomain works for building traffic.
- **Cloudflare Pages** — unlimited bandwidth, custom domains, direct-upload in browser (no git). MCP is Workers-centric, not for Pages deploy.
- **GitHub Pages** — free auto-deploy from a repo, but zero MCP and needs git (blocked on school/guest networks).
- **Netlify Drop** (app.netlify.com/drop): drag a ZIP, live in 30s, no account to start. Use for throwaway/instant deploy.

Decision rule: user wants "100% free" + "no git" → Netlify. User wants agent-deploy automation later → Netlify (only host with official MCP).

## Wire Netlify MCP into Hermes (stdio @netlify/mcp)

1. Configure via `hermes config set` — do NOT hand-edit config.yaml for MCP changes when the agent itself is editing (Hermes refuses direct writes to security-sensitive config; the config CLI is the sanctioned path):
   ```bash
   hermes config set mcp_servers.netlify.command npx
   hermes config set 'mcp_servers.netlify.args' '["-y","@netlify/mcp"]'
   hermes config set 'mcp_servers.netlify.env.NETLIFY_PERSONAL_ACCESS_TOKEN' 'YOUR_TOKEN'
   ```
2. **Env var is `NETLIFY_PERSONAL_ACCESS_TOKEN`** — not `NETLIFY_AUTH_TOKEN`. Wrong name = server connects but never authenticates.
3. Restart Hermes — MCP servers are NOT hot-reloaded; tools only appear after restart.
4. The token is a secret: put it in config/env, never a git repo.

## Auth & verification

- User must generate a PAT themselves (only they can): app.netlify.com → user icon → User settings → OAuth → New access token (starts `nfpa_`). A placeholder like `__PLACEHOLDER__` makes the MCP connect but **all calls return 401**.
- Verify auth by calling the get-user operation (`netlify_user_services_reader` with operation `get-user`) — 401 means the token is wrong/placeholder; success (user object) means authenticated and ready to deploy.
- Deploy requires `siteId` + `deployDirectory`. Never assume a new site: if the agent can't find the site ID, link first (`netlify link`) or ask the user to confirm. Do not silently create a new site.

## Git blocked but GitHub/gh still reachable

**Distinction:** `git` transport (push/pull over the network) can be blocked on a school/guest network while the `gh` CLI still works because it authenticates via a stored token (`gh auth status` shows `gho_...` token + `repo` scope). Operations that only need the API — `gh repo view`, `gh repo set-private`, `gh repo edit --visibility private` — can succeed even when `git push` would fail.

**Use `gh repo edit --visibility private --accept-visibility-change-consequences` (not `gh repo set-private`, which is not a valid subcommand on this `gh` version) to toggle visibility.** Check `gh auth status` first to confirm a token with `repo` scope is present.

**Do NOT assume that "git is blocked" means NO GitHub access** — check `gh auth status` first.

**`git push` fails `could not read Username for 'https://github.com': No such device or address`** — usually NOT a network block: a version-managed `gh` (mise/asdf) upgrade leaves `git config credential.https://github.com.helper` pointing at a deleted binary path (`.../mise/installs/gh/<old-ver>/.../bin/gh auth git-credential`). The token is fine; the helper path is stale. Fix without re-login or token regeneration: `gh auth setup-git` rewrites the helper to the current `gh` binary, then re-push. Diagnose with `git config --list --show-origin | grep -i credential` (shows the stale absolute path).

## Downloads stat on a static (no-backend) site is cosmetic-only

A hero stat like "0 Downloads" on a purely static site with no server-side counter reports a decorative number, not a live metric. Do not present it as live data. If a real number is wanted, wire it from a known constant (e.g. the README's game catalog count — "113 games") or drop the stat.

## Cloudflare Workers/Pages Asset Size Limits

Cloudflare Workers and Pages have hard limits that can cause deployment failures:

| Limit | Value | Affects |
|-------|-------|---------|
| Per-file asset | 25 MiB | Any single file (`Asset too large` error) |
| Workers total | 100 MiB | All uncompressed assets bundled together |
| Pages build | 50,000 files | Build output file count |

**Detection before deploy:**
```bash
# Find files over 25MB
find . -type f -size +25M

# Calculate total size
du -sh . --exclude='.git'

# Calculate compressed size for upload (Pages/Workers)
tar -czf - . --exclude='.git' | wc -c | awk '{print $1/1024/1024 " MB"}'
```

**Solutions for oversized assets:**
1. **Remove large games** - WebGL/Unity games are typically 5-50MB each; remove them
2. **External hosting** - Serve large bundles from R2, S3, or Netlify separately
3. **Use Netlify instead** - Higher/larger limits for game collections

See `references/cloudflare-limits.md` for detailed mitigation strategies and game type size profiles.

## Multi-threaded games — no `index.html` in each game folder

Many static game folders ship only numbered entry files (`1.html`, `3.html`, etc.) and **no `index.html`**. Downloading the repo from GitHub shows the folder exists but the default entry is missing, so links to `games/<name>/index.html` 404 on the live site.

**Symptom:** `grep -r 'href="games/' gamepage.html` reports N links; `ls games/<name>/` shows files but no `index.html`; live site 404s on those games.

**Fix:** for each such folder, create `games/<name>/index.html` with a refresh redirect to the real entry file (`<meta http-equiv="refresh" content="0; url=<real-entry>"/>`). Pick the real entry by listing the folder and choosing the top numbered file.

**Why this happens:** game authors bundle an index-less folder (the game runs from `1.html` or similar) and never commit an `index.html`. The portal's link points at a path that does not exist in the committed tree even though the folder and files are present.

## Neutralize "no ads" copy AFTER AdSense is wired in

After the AdSense snippet (`<script async src="...adsbygoogle.js?client=ca-pub-...">`) is on a page, any copy on that page or its legal/readme that says "no ads" or "ad-free" will get AdSense rejected. Neutralize it everywhere, in this order: (1) all HTML pages, (2) README / legal / terms text, (3) hero badge, meta description, lead paragraph, and any marketing copy mentioning "no ads".

Do a single grep after adding the snippet:

```bash
grep -ri 'no ads\|noad\|ad-free' --include='*.html' --include='*.md' --include='*.txt'
```

Replace each instance with a neutral phrase ("Free to Play", "No downloads", etc.) that does not contradict what the site now does. Do **not** leave a badge or stat saying "0 Ads" if the site now runs ads — that is the most visible contradiction and the first thing AdSense reviewers notice.

## Monetization notes (games/portal sites)

- Free .netlify.app subdomain may be flagged in AdSense review — real domain (~$10/yr at Cloudflare Registrar) eventually needed for approval.
- Ad networks for browser games: AdSense (easiest approval), AdinPlay/PlayWire/Venatus (game-native, higher CPM, need traffic), Adsterra (lowest approval bar, anti-adblock). Start with AdSense/Adsterra, upgrade when traffic clears 5k-10k monthly visits.
- A README claiming "non-commercial use only" conflicts with ad monetization — reconcile the legal/terms text before adding ads.
