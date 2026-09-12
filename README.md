<div align="center">

# 🧠 Hermes Skill Library

**155 agent skills — version-controlled, documented, ready to deploy.**

A curated library of [Hermes Agent](https://hermes-agent.nousresearch.com/docs) skills
covering web development, AI agents, security, DevOps, creative production, research,
and productivity. Includes the custom [`web-mode`](#custom-skills) orchestrator —
a single skill that drives the whole website pipeline end-to-end.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Skills](https://img.shields.io/badge/skills-155-4c1fff)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-maintained-green)

</div>

---

## Why this repo

- **One repo, all skills** — every SKILL.md plus its references, templates, and scripts.
- **Searchable catalog** — `docs/CATALOG.md` lists all 155 skills with one-line descriptions.
- **Safe to share** — secrets, runtime state, and caches are gitignored. Only skill source ships.
- **Lenient license** — MIT. Fork it, use it, remix it.

## Quick start

Skills live under `~/.hermes/skills/`. To import a skill into a Hermes Agent install:

```bash
# Copy a single skill (example: the web-mode orchestrator)
mkdir -p ~/.hermes/skills/web
cp -r skills/web/web-mode ~/.hermes/skills/web/web-mode

# Or a whole category
cp -r skills/creative ~/.hermes/skills/
```

Restart your Hermes session and the skill appears in `skills_list`.

> Skills are matched by description on every prompt — above ~60 meaningful characters
> they truncate and lose routing signal. Where a source description was verbose we
> trimmed it in the catalog; the full text is always in the SKILL.md itself.

## Custom skills

These were authored for this library and are the starting points worth knowing:

| Skill | What it does |
|---|---|
| **`web-mode`** | The **end-to-end website builder**. Orchestrates plan → design → build → QA → deploy, delegating each stage to the best specialist skill instead of recreating it. |

## Catalog

Browse the full searchable index: **[`docs/CATALOG.md`](docs/CATALOG.md)** — 155 skills across 23 categories.

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
├── skills/                  # All skill directories (SKILL.md + refs/scripts/templates)
│   ├── web/                 # web-mode, deployment, browser harness
│   ├── creative/            # design, video, audio, art
│   ├── autonomous-ai-agents/
│   ├── software-development/
│   ├── claude-code-imports/ # 72 imported dev skills
│   ├── productivity/        # docx/pdf/xlsx/pptx, docs, apps
│   ├── research/
│   ├── ...                  # 23 categories total
├── docs/CATALOG.md          # Auto-generated searchable skill index
├── scripts/                 # Repo tooling (see Development)
└── LICENSE                  # MIT
```

## Development

The library is self-policing — a validation gate keeps the catalog, README, and
docs site in sync with what's actually on disk.

```bash
# Regenerate docs/CATALOG.md from the on-disk skill tree (run after adding a skill)
python3 scripts/gen-catalog.py

# Structural validation: frontmatter, name/dir match, catalog accuracy, counts
python3 scripts/validate-skills.py
```

Both run automatically on every push/PR via `.github/workflows/validate-library.yml`.
If you add or remove a skill, run `gen-catalog.py` and commit the updated
`docs/CATALOG.md` — CI will otherwise reject the change.

## What's NOT tracked

For your safety, none of these are ever committed:

- Secrets — `.env`, `auth.json`, `config.yaml`
- Runtime state — databases, sessions, caches, locks
- Hermes machinery — `.hub/`, curator state, manifests

The `.gitignore` enforces all of this. If you fork, keep it.

## Security note

Some skills in the `claude-code-imports` and `security` categories reference
offensive tooling (e.g. `godmode`). They are research/educational and ship as-is
under MIT. Review anything before enabling it in a production workspace.

## License

MIT © 2026 Hany Elansari. See [LICENSE](LICENSE).