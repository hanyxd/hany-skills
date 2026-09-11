---
name: web-mode
description: "Use when building websites. Plan, design, build, QA, deploy."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [web, design, frontend, html, css, js, deployment, prd]
---

# Web Mode — End-to-End Website Building

One skill that drives the whole process of making a website: scope it, design it (non-generic), build it, test it in a real browser, and ship it free.

This skill is the **orchestrator**. It links out to deeper skills for specialized work instead of re-implementing them, so you stay current with the referenced skills.

## Workflow

Run these in order. Stop early only if the user's request makes a step unnecessary.

### 1. Scope (before writing code)

- Ask concise questions if the brief is ambiguous: audience, fidelity, pages, style/brand, whether it needs a backend. Skip questions when the direction is clear.
- If reverse-engineering or cloning a reference site, or the user wants a feature list from a live app, use the **web-to-prd** skill to crawl it and extract a full spec (features, epics, stories, screenshots).
- For any genuinely creative work (new idea, no clear brief), load **brainstorming** first.

### 2. Design (non-generic UI)

- Follow the design process in **claude-design**: commit to ONE surface archetype (Monitor / Operate / Compare / Configure / Decide-Learn / Explore / Command-Inspect) before touching any tokens. The hero + three equal feature cards layout is correct ONLY for Decide/Learn surfaces.
- Run the slop self-audit from claude-design (10 tells) before polishing, and repair matched to the diagnosis (compositional tells → re-layout, not recolor).
- If the user wants a known brand's look ("make it look like Stripe / Linear / Vercel / Notion"), load the matching template from **popular-web-designs** (`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`) for exact colors, type, and component values, and let claude-design drive the process.
- If the deliverable is a machine-readable token spec (DESIGN.md), use **design-md** instead.

### 3. Choose the stack

- **Standalone HTML single-file artifact** (landing, prototype, deck, one-off): plain HTML/CSS/JS, self-contained, embedded CSS/JS, no heavy deps. Use **claude-design** standards (modern CSS: variables, grid, container queries, real focus/hover states, `prefers-reduced-motion`, responsive, 44px+ hit targets, semantic HTML).
- **React/Next/Vite app UI with components**: use **ui-styling** (shadcn/ui + Tailwind). Install with `npx shadcn@latest init` then `npx shadcn@latest add button card dialog form`. Use utility-first Tailwind, mobile-first responsive, Radix accessibility.
- **Backend/API needed**: use **python-api-endpoint-creator** + **python-best-practices** (FastAPI) and **database-patterns** / **database-table-creator** for schema. For Micronaut/Kotlin stacks instead, load **kotlin-best-practices** + **testing-strategies** + **security-checklist**.
- **Content is a real site but keep it simple**: rebuild as static HTML. Don't over-engineer.

### 4. Build

- Write files with `write_file`. Keep source inspectable.
- For a serious app (2+ pages, real UI), implement in the repo's actual stack — do not force a standalone artifact.
- Every element earns its place: no filler copy, no fake stats, no decorative icons, no AI slop sections. Mark placeholder copy as draft.
- Mobile-first responsive, dark mode if it fits the brand.

### 5. QA (real browser verification)

- Minimal verification: file exists at stated path, HTML saved completely, syntax checks pass.
- Better: open in a real browser. Use the **browser-qa** skill (Playwright) or the Hermes `browser_exec` browser harness on this host (see memory note about launching Chromium with `--remote-debugging-port=9222` + `BU_CDP_URL`). Check console errors, primary viewport screenshot, key interactions, light/dark, responsive breakpoints.
- Never claim browser verification unless it actually happened.

### 6. Deploy (free)

- Use the **static-site-deployment** skill. Default free no-git host: **Netlify** (free SSL, 100GB/mo, official MCP for agent deploys). Cloudflare Pages = unlimited bandwidth; GitHub Pages needs git (blocked on school networks). Netlify Drop for throwaway/instant.
- Wire Netlify MCP via `hermes config set mcp_servers.netlify.*` with env `NETLIFY_PERSONAL_ACCESS_TOKEN` (not AUTH_TOKEN), then restart Hermes; verify with get-user. Deploy requires `siteId` + `deployDirectory`.
- Respect Cloudflare asset limits: per-file 25 MiB, total 100 MiB compressed (see skill).

## Skill map (sub-skills referenced)

| Need | Load this skill |
|---|---|
| Reverse-engineer a live site into a spec | web-to-prd |
| Creative ideation / unclear brief | brainstorming |
| Design process + taste + anti-slop | claude-design |
| Match a known brand's look | popular-web-designs |
| Token spec file (DESIGN.md) | design-md |
| Real component UI (shadcn/Tailwind) | ui-styling |
| FastAPI backend | python-api-endpoint-creator, python-best-practices |
| Database schema | database-patterns, database-table-creator |
| Kotlin/Micronaut backend | kotlin-best-practices, testing-strategies, security-checklist |
| Browser QA | browser-qa (Playwright) |
| Free deployment | static-site-deployment |

## Deliverable / report

When done, report briefly:
- exact file path(s) or deploy URL
- what was built
- verification status (what was and wasn't verified)
- next suggested action

Never report "done" if the file was not actually written or the deploy did not actually succeed.
