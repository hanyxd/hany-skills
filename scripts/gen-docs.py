#!/usr/bin/env python3
"""Generate docs/index.html — a searchable/filterable skill browser.

Reads the same skill tree as gen-catalog.py and emits a single self-contained
HTML file (no JS/CSS dependencies) with:
  - a live search box (filter by name or description)
  - a category filter
  - curated vs vendored [t] badges
  - install commands per skill (echo of the symlink target)

Run:  python3 scripts/gen-docs.py   (writes docs/index.html)
"""
import html
import os
import re
import json
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
OUT = os.path.join(ROOT, "docs", "index.html")
VENDORED = "claude-code-imports"


def read_frontmatter(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}


def skill_desc(path):
    raw = str(read_frontmatter(path).get("description", "") or "").strip()
    raw = re.sub(r"\s+", " ", raw)
    if not raw:
        return "*(no description)*"
    first = re.split(r"(?<=[.!?])\s+", raw, maxsplit=1)[0]
    if len(first) > 60:
        return first[:57] + "..."
    return first


def collect_skills():
    skills = []
    for cat in sorted(os.listdir(SKILLS)):
        cap = os.path.join(SKILLS, cat)
        if not os.path.isdir(cap):
            continue
        entries = []
        for d in sorted(os.listdir(cap)):
            p = os.path.join(cap, d)
            if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
                entries.append((d, p))
        if os.path.isfile(os.path.join(cap, "SKILL.md")):
            entries.append((cat, cap))
        for name, path in entries:
            sk = os.path.join(path, "SKILL.md")
            is_vendored = VENDORED in path.split(os.sep)
            skills.append({
                "name": name,
                "desc": skill_desc(sk),
                "cat": cat,
                "cat_nice": cat.replace("-", " ").title(),
                "vendored": is_vendored,
                "rel": os.path.relpath(path, SKILLS),
            })
    return skills


def build_html(skills):
    total = len(skills)
    curated = sum(1 for s in skills if not s["vendored"])
    vendored = total - curated
    categories = sorted({s["cat"] for s in skills})

    cards = []
    for s in skills:
        badge = ' <span class="t" title="Third-party vendored">[t]</span>' if s["vendored"] else ""
        cards.append(
            f'<div class="card" data-cat="{html.escape(s["cat"], quote=True)}" '
            f'data-name="{html.escape(s["name"].lower())}">'
            f'<div class="cname"><span class="n">{html.escape(s["name"])}</span>{badge}</div>'
            f'<div class="d">{html.escape(s["desc"])}</div>'
            f'<div class="rel">{html.escape(s["rel"])}</div>'
            f'</div>'
        )
    cards_html = "\n    ".join(cards)

    options = "".join(
        f'<option value="{html.escape(c, quote=True)}">{html.escape(c.replace("-", " ").title())}</option>'
        for c in categories
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hermes Skill Library — {total} Skills</title>
<meta name="description" content="A curated + vendored library of {total} Hermes Agent skills across web, creative, security, DevOps, research, and productivity.">
<style>
  :root{{--bg:#0b0d10;--surface:#11151b;--surface2:#161b22;--text:#e6edf3;--muted:#8b949e;--border:#21262d;--accent:#4c1fff;--accent2:#7c3aed;--good:#3fb950;--mono:"SFMono-Regular",ui-monospace,Menlo,monospace}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
  header.hero{{padding:64px 0 40px;border-bottom:1px solid var(--border)}}
  .kicker{{color:var(--accent2);font:600 13px var(--mono);letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px}}
  h1{{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:800;letter-spacing:-.03em;line-height:1.1}}
  h1 .grad{{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}}
  .sub{{color:var(--muted);font-size:1.05rem;max-width:60ch;margin:14px 0 24px}}
  .stats{{display:flex;gap:36px;margin-top:28px;flex-wrap:wrap}}
  .stat b{{font-size:1.7rem;font-weight:800;display:block;line-height:1}}
  .stat span{{color:var(--muted);font-size:.82rem}}
  .controls{{display:flex;gap:14px;flex-wrap:wrap;align-items:center;padding:22px 0 8px}}
  input[type=search]{{flex:1;min-width:220px;background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:11px 14px;font-size:.95rem}}
  input[type=search]:focus{{outline:none;border-color:var(--accent2)}}
  select{{background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:11px 14px;font-size:.95rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;padding:18px 0 60px}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;transition:.15s}}
  .card:hover{{border-color:var(--accent2);transform:translateY(-2px)}}
  .cname{{display:flex;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap}}
  .cname .n{{font:700 1.02rem var(--mono);color:var(--accent2)}}
  .card .t{{font:600 10px var(--mono);color:var(--surface);background:var(--accent2);padding:1px 6px;border-radius:10px;letter-spacing:.03em}}
  .card .d{{color:var(--muted);font-size:.87rem;margin-bottom:8px}}
  .card .rel{{font:500 10px var(--mono);color:var(--good);opacity:.75;word-break:break-all}}
  .empty{{color:var(--muted);padding:40px 0;text-align:center;font-size:1.05rem}}
  footer{{padding:32px 0;color:var(--muted);font-size:.85rem;border-top:1px solid var(--border)}}
  footer a{{color:var(--text);text-decoration:none}}
  .hide{{display:none}}
</style>
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="kicker">Hermes Agent · Skill Library</div>
    <h1><span class="grad">{total} skills</span>, one <span class="grad">library</span></h1>
    <p class="sub">Curated + vendored Hermes Agent skills. Click into a card's path for its install command, or use the repo's <span class="grad" style="background:initial;color:var(--accent2)">./install.sh</span> CLI.</p>
    <div class="stats">
      <div class="stat"><b>{total}</b><span>total skills</span></div>
      <div class="stat"><b>{curated}</b><span>curated</span></div>
      <div class="stat"><b>{vendored}</b><span>vendored [t]</span></div>
      <div class="stat"><b>{len(categories)}</b><span>categories</span></div>
    </div>
  </div>
</header>
<main class="wrap">
  <div class="controls">
    <input type="search" id="q" placeholder="Search skills… (name or description)">
    <select id="cat"><option value="">All categories</option>{options}</select>
    <label class="stat" style="display:flex;gap:8px;align-items:center;color:var(--muted);font-size:.85rem">
      <input type="checkbox" id="hideVend"> <span>Hide vendored [t]</span>
    </label>
  </div>
  <div class="grid" id="grid">
    {cards_html}
  </div>
  <div class="empty hide" id="empty">No skills match your filters.</div>
</main>
<footer>
  <div class="wrap">Hermes Skill Library — auto-generated by <code>scripts/gen-docs.py</code>. ·
    <a href="https://github.com/hanyxd/hany-skills">GitHub</a></div>
</footer>
<script>
  const grid=document.getElementById('grid'),empty=document.getElementById('empty'),
        q=document.getElementById('q'),cat=document.getElementById('cat'),hideV=document.getElementById('hideVend');
  function apply(){{
    const qv=q.value.trim().toLowerCase();
    const cv=cat.value;
    let shown=0;
    for(const card of grid.children){{
      const name=card.dataset.name, desc=card.querySelector('.d').textContent.toLowerCase();
      const c=card.dataset.cat, vend=!!card.querySelector('.t');
      const okQ=!qv || name.includes(qv) || desc.includes(qv);
      const okC=!cv || c===cv;
      const okV=!(hideV.checked && vend);
      const show=okQ&&okC&&okV;
      card.classList.toggle('hide',!show);
      if(show) shown++;
    }}
    empty.classList.toggle('hide',shown>0);
  }}
  [q,cat,hideV].forEach(el=>el.addEventListener('input',apply));
  apply();
</script>
</body>
</html>
"""
    return page


def main():
    skills = collect_skills()
    open(OUT, "w", encoding="utf-8").write(build_html(skills))
    n_vend = sum(1 for s in skills if s["vendored"])
    print(f"Wrote {OUT}: {len(skills)} skills ({len(skills)-n_vend} curated, {n_vend} vendored)")


if __name__ == "__main__":
    main()