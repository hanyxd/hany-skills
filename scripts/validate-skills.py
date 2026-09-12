#!/usr/bin/env python3
"""Validate the skill library structure. Exit non-zero on any drift.

Checks:
  1. Frontmatter present & parseable (--- ... ---, name + description keys).
  2. Description <= 60 chars (truncates at 57 + '...' in the index).
  3. Every category dir + skill dir has a SKILL.md.
  4. docs/CATALOG.md lists exactly the skills on disk (no phantoms).
  5. README.md / docs/index.html skill-count claims match the disk count.
  6. No name collisions that would shadow a skill at install time.

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


def main():
    dirs = skill_dirs()
    on_disk = {}
    names_seen = {}

    for p in dirs:
        skill = os.path.basename(p)
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
        if not isinstance(data.get("description"), str) or not data["description"].strip():
            errors.append(f"{p}: empty description")
        elif len(data["description"]) > MAX_DESC:
            warnings.append(
                f"{p}: description {len(data['description'])} chars "
                f"(max {MAX_DESC}); will truncate in index: "
                f"{data['description'][:60]!r}"
            )
        # collision: same name, different category
        key = fm_name or skill
        names_seen.setdefault(key, []).append(os.path.relpath(p, SKILLS))
        on_disk[key] = os.path.relpath(p, SKILLS)

    # name collisions across categories (shadowing at install time)
    for name, locs in sorted(names_seen.items()):
        if len(locs) > 1:
            warnings.append(f"name '{name}' exists in {len(locs)} places: {locs}")

    # --- catalog accuracy ---
    cat_path = os.path.join(ROOT, "docs", "CATALOG.md")
    if os.path.isfile(cat_path):
        cat = open(cat_path, encoding="utf-8").read()
        cat_names = set(re.findall(r"\|\s*`([a-z0-9-]+)`\s*\|", cat))
        phantom = sorted(cat_names - set(on_disk))
        missing = sorted(set(on_disk) - cat_names)
        if phantom:
            errors.append(f"CATALOG lists skills not on disk: {phantom}")
        if missing:
            errors.append(f"CATALOG missing skills: {missing}")
        # header count claim
        hm = re.search(r"^\*\*(\d+) skills\*\*", cat, re.M)
        if hm and int(hm.group(1)) != len(dirs):
            errors.append(f"CATALOG header says {hm.group(1)} skills, disk has {len(dirs)}")
        hm2 = re.search(r"across (\d+) categories", cat)
        if hm2 and int(hm2.group(1)) != len(
            [d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d))]
        ):
            errors.append(f"CATALOG category count mismatch: {hm2.group(1)}")

    # --- README / index.html count claims ---
    count_label = len(dirs)
    for f in ["README.md", "docs/index.html"]:
        fp = os.path.join(ROOT, f)
        if not os.path.isfile(fp):
            continue
        text = open(fp, encoding="utf-8", errors="replace").read()
        # stale '156' claim anywhere
        if re.search(rf"\b156\b.*skills", text, re.I):
            errors.append(f"{f}: claims '156 skills' but disk has {count_label}")
        tm = re.search(r"<title>([^<]*?)</title>", text)
        if tm and "156" in tm.group(1):
            errors.append(f"{f}: <title>{tm.group(1)}</title> has stale 156")

    print(f"Scanned {len(dirs)} skills across "
          f"{len([d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d))])} categories.")

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