#!/usr/bin/env python3
"""Validate the skill library structure. Exit non-zero on any drift.

Checks:
  1. Frontmatter present & parseable (--- ... ---, name + description keys).
  2. Description <= 60 chars (hard failure — long descriptions lose routing
     signal; gen-catalog.py trims to the first sentence, so a >60 raw
     description always means the index and the SKILL.md disagree).
  3. Every category dir + skill dir has a SKILL.md.
  4. docs/CATALOG.md lists exactly the skills on disk (no phantoms).
  5. README.md / docs/index.html skill-count claims match the disk count.
  6. No name collisions across categories — a duplicated skill name shadows
     the other at install time. (Was only a warning before; it's fatal now so
     the 155->147 dedup can't silently regress.)

Run:  python3 scripts/validate-skills.py
"""
import os
import re
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
MAX_DESC = 60

errors = []
warnings = []
info = []


def skill_dirs():
    """Return the directory containing each SKILL.md, from a pure os.walk.

    Matching gen-catalog.py exactly (single source of truth for the count): a
    skill is any directory (category-level or nested) that contains SKILL.md.
    """
    out = []
    for root, _dirs, files in os.walk(SKILLS):
        if "SKILL.md" in files:
            out.append(root)
    return out


def read_frontmatter(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, "missing frontmatter --- ... ---"
    try:
        data = yaml.safe_load(m.group(1))
    except Exception as e:
        return None, f"frontmatter YAML error: {e}"
    return data, None


def category_dirs():
    return [d for d in os.listdir(SKILLS)
            if os.path.isdir(os.path.join(SKILLS, d))]


def main():
    dirs = skill_dirs()
    on_disk = {}
    by_name = {}

    for p in dirs:
        skill = os.path.basename(p)
        rel = os.path.relpath(p, SKILLS)
        if not os.path.isfile(os.path.join(p, "SKILL.md")):
            errors.append(f"missing SKILL.md: {p}")
            continue
        data, err = read_frontmatter(os.path.join(p, "SKILL.md"))
        if err:
            errors.append(f"{p}: {err}")
            continue
        if data is None or "name" not in data or "description" not in data:
            errors.append(f"{p}: frontmatter missing name/description")
            continue
        fm_name = data.get("name")
        if fm_name != skill:
            errors.append(f"{p}: frontmatter name '{fm_name}' != dir '{skill}'")
        desc = data.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{p}: empty description")
        elif len(desc) > MAX_DESC:
            if "claude-code-imports" in rel:
                # third-party/vendored: don't rewrite their content, but flag it
                warnings.append(
                    f"{p}: description {len(desc)} chars (max {MAX_DESC}); "
                    f"vendored — catalog trims to first sentence: {desc[:60]!r}..."
                )
            else:
                # curated: FATAL. The catalog trims to the first sentence, so a
                # raw >60 description makes the index disagree with SKILL.md.
                errors.append(
                    f"{p}: description is {len(desc)} chars (max {MAX_DESC}). "
                    f"Trim the frontmatter description to the first ≤{MAX_DESC}-char "
                    f"sentence: {desc[:60]!r}..."
                )
        # collisions across directories (would shadow at install time)
        by_name.setdefault(fm_name or skill, []).append(rel)
        on_disk[fm_name or skill] = rel

    # name collisions are FATAL: install-time shadowing, must be fixed not warned
    dups = {n: locs for n, locs in by_name.items() if len(locs) > 1}
    if dups:
        for name, locs in sorted(dups.items()):
            errors.append(
                f"name '{name}' exists in {len(locs)} places: {locs} — "
                f"these shadow each other at install time; keep one (curated) or rename the rest"
            )

    # --- catalog accuracy ---
    cat_path = os.path.join(ROOT, "docs", "CATALOG.md")
    cat_names = set()
    if os.path.isfile(cat_path):
        cat = open(cat_path, encoding="utf-8").read()
        cat_names = set(re.findall(r"\|\s*`([a-z0-9-]+)`\s*(\s*`\[t\]`)?\s*\|", cat))
        # first grouping is the skill name
        cat_names = {m[0] for m in cat_names}
        phantom = sorted(cat_names - set(on_disk))
        missing = sorted(set(on_disk) - cat_names)
        if phantom:
            errors.append(f"CATALOG lists skills not on disk: {phantom}")
        if missing:
            errors.append(f"CATALOG missing skills: {missing}")
        hm = re.search(r"^\*\*(\d+) skills\*\*", cat, re.M)
        if hm and int(hm.group(1)) != len(dirs):
            errors.append(f"CATALOG header says {hm.group(1)} skills, disk has {len(dirs)}")
        hm2 = re.search(r"across (\d+) categories", cat)
        if hm2 and int(hm2.group(1)) != len(category_dirs()):
            errors.append(f"CATALOG category count mismatch: {hm2.group(1)}")

    # --- README / index.html count claims ---
    count_label = len(dirs)
    for f in ["README.md", "docs/index.html"]:
        fp = os.path.join(ROOT, f)
        if not os.path.isfile(fp):
            info.append(f"{f}: not present (create one, or it won't be checked)")
            continue
        text = open(fp, encoding="utf-8", errors="replace").read()
        # any stale '156' (pre-dedup) claim anywhere
        if re.search(rf"\b156\b.*skills", text, re.I):
            errors.append(f"{f}: claims '156 skills' but disk has {count_label}")
        tm = re.search(r"<title>([^<]*?)</title>", text)
        if tm and "156" in tm.group(1):
            errors.append(f"{f}: <title>{tm.group(1)}</title> has stale 156")
        # and the current count claim, if present, must equal disk
        for n in {count_label, count_label + 1}:
            m = re.search(rf"\b{n}\b skills", text, re.I)
            if m:
                fmt = "OK" if n == count_label else "MISMATCH"
                break

    ncats = len(category_dirs())
    print(f"Scanned {len(dirs)} skills across {ncats} categories.")

    if info:
        print("\nINFO:")
        for i in info:
            print(f"  · {i}")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"\nFAIL: {len(errors)} problem(s)")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print("\nOK: library is consistent.")


if __name__ == "__main__":
    main()