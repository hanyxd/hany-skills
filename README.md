<div align="center">

# 🧠 Hermes Skill Library

**147 agent skills — curated + vendored, version-controlled, ready to deploy.**

Hany's personal library of [Hermes Agent](https://hermes-agent.nousresearch.com/docs) skills.
Covers web development, AI agents, security, DevOps, creative production, research,
and productivity.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Skills](https://img.shields.io/badge/skills-147-4c1fff)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-maintained-green)

</div>

---

## Contents

- [Why this repo](#why-this-repo)
- [Quick start](#quick-start)
- [Manage installs](#managing-installs)
- [How it's organized](#how-the-library-is-organized)
- [Custom skills](#custom-skills)
- [Dedup policy](#deduplication-policy)
- [Catalog](#catalog)
- [Structure](#structure)
- [Development / adding a skill](#development)
- [What's NOT tracked](#whats-not-tracked)
- [Security note](#security-note)
- [License](#license)

## Why this repo

- **One repo, all skills** — every SKILL.md plus its references, templates, and scripts.
- **Searchable catalog** — `docs/CATALOG.md` lists every skill with a trimmed, ≤60-char
  description (the same lead the skill router actually reads).
- **Safe to share** — secrets, runtime state, and caches are gitignored. Only skill source ships.
- **Clean install/uninstall** — the `install.sh` CLI symlinks skills into `~/.hermes/skills`,
  detects collisions, and can remove them again.
- **Lenient license** — MIT. Fork it, use it, remix it.

## Quick start

```bash
# Install a single skill into ~/.hermes/skills (as a symlink)
./install.sh web-mode

# Install an entire category
./install.sh --category web

# Install every curated skill (excludes third-party vendored under claude-code-imports/)
./install.sh --curated

# Install literally everything
./install.sh --all

# See what would happen without changing anything
./install.sh -n --curated
```

Then restart your Hermes session and the skill appears in `skills_list`.

### Managing installs

```bash
./install.sh list                 # what's available, grouped by category
./install.sh status               # ✓ what's installed, [ ] what's not
./install.sh remove web-mode      # uninstall (removes the symlink, keeps the repo copy)
```

Skills install as **symlinks**, so the repo stays the single source of truth:
`git pull` updates installed skills automatically. A real (non-symlink) file that
already exists at the destination is never overwritten — it's reported as a collision
and skipped.

### Limitation (why symlinks, not copies)

This library is designed to be *installed live* from a checkout (symlinks read straight
from the repo). If you clone it elsewhere, re-run `./install.sh` to repoint the links.
A future `install.sh copy` mode could bake a snapshot; not implemented yet.

## How the library is organized

Two tiers, clearly separated:

- **Curated** (83 skills) — the actively maintained, hand-tended skills. These live at
  the top level of `skills/` (e.g. `skills/web/web-mode`, `skills/creative/manim-video`).
  Their frontmatter descriptions are kept ≤60 chars; the validator fails a PR if one
  drifts over.
- **Vendored** (64 skills) — third-party imports under `skills/claude-code-imports/`,
  kept intact and labeled with a `[t]` tag in the catalog. Their original long
  descriptions are preserved; the catalog trims them to the first sentence for display.
  Useful for reference, but considered upstream import — prefer the curated version when
  a name overlaps.

### Custom skills (authored for this library)

| Skill | What it does |
|---|---|
| **`web-mode`** | The **end-to-end website builder**. Orchestrates plan → design → build → QA → deploy, delegating each stage to the best specialist skill. |

## Deduplication policy

Duplicates across curated and vendored skill names are resolved in favor of the
**curated** version. Duplicated names that would shadow each other at install time are
fatal in the validator — the same name must exist in exactly one directory.

## Catalog

Browse the full searchable index: **[`docs/CATALOG.md`](docs/CATALOG.md)** — 147 skills
across 21 categories (`[t]` = third-party vendored).

Highlights by area:

- **Web** — `web-mode` (build), `static-site-deployment` (deploy free), `hermes-browser-exec` (drive browser)
- **Creative** — `claude-design`, `popular-web-designs` (54 real design systems), `manim-video`, `p5js`
- **AI agents** — `hermes-agent`, `codex`, `claude-code`, `opencode`, `browser-exec-cdp`
- **Backend** — `python-api-endpoint-creator`, `backend-api-design`, `database-patterns`, `security-checklist`
- **Security** — `js-security-audit`, `terraform-security-audit`, `security-checklist`
- **DevOps** — `terraform-*` (5), `ci-cd-patterns`, `service-debugging`
- **Research** — `deep-research`, `arxiv`, `market-research`, `grounded-citations`
- **Productivity** — `docx`, `pdf`, `xlsx`, `pptx`, `google-workspace`, `notion`, `airtable`

## Structure

```
.
├── install.sh               # symlink installer/uninstaller CLI
├── skills/                  # All skill directories (SKILL.md + refs/scripts/templates)
│   ├── web/                 # curated: web-mode, deployment, browser harness
│   ├── creative/            # curated: design, video, audio, art
│   ├── claude-code-imports/ # vendored: 64 third-party imports (labeled [t])
│   ├── ...                  # 21 categories total
├── docs/CATALOG.md          # Auto-generated searchable skill index
├── docs/index.html          # Docs site (GitHub Pages)
├── scripts/                 # Repo tooling (see Development)
└── LICENSE                  # MIT
```

## Development

The library is self-policing — a validation gate keeps the catalog, README, and docs
site in sync with what's actually on disk.

```bash
# Regenerate docs/CATALOG.md from the on-disk skill tree (run after adding a skill)
python3 scripts/gen-catalog.py

# Structural validation: frontmatter, name/dir match, dedup, description length,
# catalog accuracy, count claims
python3 scripts/validate-skills.py
```

Both run automatically on every push/PR via `.github/workflows/validate-library.yml`.
If you add or remove a skill, run `gen-catalog.py` and `validate-skills.py` and commit —
CI will otherwise reject the change.

### Adding a skill

1. Add the skill dir under `skills/<category>/<skill>/` with a SKILL.md.
2. Keep the frontmatter `description` to the **first sentence, ≤60 chars**.
3. `python3 scripts/gen-catalog.py && python3 scripts/validate-skills.py`
4. Commit the updated catalog.

## What's NOT tracked

For your safety, none of these are ever committed:

- Secrets — `.env`, `auth.json`, `config.yaml`
- Runtime state — databases, sessions, caches, locks
- Hermes machinery — `.hub/`, curator state, manifests
- **Machine-specific symlinks** — references to local absolute paths are never committed.

The `.gitignore` enforces all of this. If you fork, keep it.

## Security note

Some skills reference offensive tooling (e.g. `godmode`, in the `security` category).
They are research/educational and ship as-is under MIT. Review anything before enabling
it in a production workspace.

## License

MIT © 2026 Hany Elansari. See [LICENSE](LICENSE).