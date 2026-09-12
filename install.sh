#!/usr/bin/env bash
# Hany Skill Library — installer
# Usage:
#   ./install.sh list                      list available skills (grouped by category)
#   ./install.sh <skill> ...               install one or more skills into ~/.hermes/skills
#   ./install.sh --all                     install every skill (curated + vendored)
#   ./install.sh --curated                 install only curated skills (excludes claude-code-imports)
#   ./install.sh --category web            install an entire category
#   ./install.sh -n                        dry run (show what would happen, change nothing)
#   ./install.sh remove <skill>            uninstall a skill (remove its symlink)
#   ./install.sh status                    show what's installed vs available
#
# Installs as SYMLINKS into ~/.hermes/skills, so the single source of truth stays
# in this repo and `git pull` updates installed skills automatically. Existing
# real (non-symlink) skills in ~/.hermes/skills are never overwritten — a
# collision is reported and skipped.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
DEST="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
MODE="install"          # install | remove | list | status
DRY=0
SELECT=()

say()  { printf '%s\n' "$*"; }
err()  { printf 'error: %s\n' "$*" >&2; }

usage() { sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

# Map a category name to a path under skills/. Resolves single-level categories
# (web/foo, creative/bar) and the vendored claude-code-imports tree.
resolve_skill() {
  local needle="$1"
  # direct: skills/<cat>/<skill> or skills/<skill>/SKILL.md (category-level skill)
  local hit
  hit=$(find "$SKILLS_ROOT" -maxdepth 3 -name SKILL.md -path "*/$needle/SKILL.md" 2>/dev/null | head -1)
  if [[ -n "$hit" ]]; then
    printf '%s' "$(dirname "$hit")"
    return 0
  fi
  # vendored nested (claude-code-imports/foo/bar)
  hit=$(find "$SKILLS_ROOT" -name SKILL.md -path "*/$needle/SKILL.md" 2>/dev/null | head -1)
  if [[ -n "$hit" ]]; then
    printf '%s' "$(dirname "$hit")"
    return 0
  fi
  return 1
}

all_skills() { find "$SKILLS_ROOT" -maxdepth 3 -name SKILL.md | sort; }

is_installed() { # $1 = skill dir absolute path
  local rel="${1#"$REPO_ROOT"/}"
  rel=${rel#skills/}
  [[ -L "$DEST/$rel" ]]
}

install_one() {
  local src="$1" rel="${1#"$REPO_ROOT"/}" dest
  rel=${rel#skills/}
  dest="$DEST/$rel"
  if [[ "$DRY" -eq 1 ]]; then
    say "  would link  $rel"
    return 0
  fi
  if [[ -L "$dest" ]]; then
    say "  already linked  $rel"
    return 0
  fi
  if [[ -e "$dest" ]]; then
    say "  SKIP (collision)  $rel  ->  $dest exists and is not a symlink"
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  ln -s "$src" "$dest"
  # make each script executable in its own tree (symlink keeps a real copy installed)
  say "  linked  $rel"
}

remove_one() {
  local rel="$1"
  local dest="$DEST/$rel"
  if [[ ! -L "$dest" ]]; then
    say "  not installed  $rel"
    return 0
  fi
  if [[ "$DRY" -eq 1 ]]; then
    say "  would unlink  $rel"
    return 0
  fi
  rm "$dest"
  # prune now-empty parent dirs we created
  local d
  d="$(dirname "$dest")"
  while [[ "$d" != "$DEST" ]]; do
    if [[ -n "$(ls -A "$d" 2>/dev/null)" ]]; then break; fi
    rmdir "$d"; d="$(dirname "$d")"
  done
  say "  removed  $rel"
}

# ---- select skills ----
[[ $# -eq 0 ]] && usage 1
for a in "$@"; do
  case "$a" in
    list)         MODE=list ;;
    --all)        MODE=install; SELECT=(ALL) ;;
    --curated)    MODE=install; SELECT=(CURATED) ;;
    --category)   MODE=install; CATEGORY="${2:-}"; shift 2; continue ;;
    -n|--dry-run) DRY=1 ;;
    remove)       MODE=remove ;;
    status)       MODE=status ;;
    -h|--help)    usage 0 ;;
    -*)           err "unknown flag: $a"; usage 1 ;;
    *)            SELECT+=("$a") ;;
  esac
done

if [[ "${CATEGORY:-}" ]]; then
  MODE=install
  if [[ -d "$SKILLS_ROOT/$CATEGORY" ]]; then
    mapfile -t SELECT < <(find "$SKILLS_ROOT/$CATEGORY" -maxdepth 3 -name SKILL.md)
  else
    avail=$(find "$SKILLS_ROOT" -maxdepth 1 -mindepth 1 -type d -printf '%f ' 2>/dev/null)
    err "category '$CATEGORY' not found (dirs: $avail)"; exit 1
  fi
fi

case "$MODE" in
  list)
    say "Available skills (in $REPO_ROOT):"
    for cat in "$SKILLS_ROOT"/*/; do
      [[ -d "$cat" ]] || continue
      cname="$(basename "$cat")"
      count=$(find "$cat" -maxdepth 3 -name SKILL.md | wc -l)
      [[ "$count" -eq 0 ]] && continue
      printf '  %-28s %s\n' "$cname" "($count)"
    done
    say
    say 'Install:  ./install.sh <skill> ...    or   ./install.sh --all'
    exit 0
    ;;
  status)
    say "Installed vs available (dest: $DEST)"
    if [[ ! -d "$DEST" ]]; then say "  (nothing installed — dest $DEST does not exist yet)"; fi
    local_skills=$(all_skills)
    while IFS= read -r s; do
      rel="${s#"$SKILLS_ROOT"/}"; rel=${rel%/SKILL.md}
      mark=" "
      [[ -L "$DEST/$rel" ]] && mark="✓"
      printf '  [%s] %s\n' "$mark" "$rel"
    done <<< "$local_skills"
    exit 0
    ;;
  remove)
    [[ ${#SELECT[@]} -eq 0 ]] && { err "nothing to remove"; exit 1; }
    say "Removing from $DEST:"
    for name in "${SELECT[@]}"; do
      while IFS= read -r s; do
        rel="${s#"$SKILLS_ROOT"/}"; rel=${rel%/SKILL.md}
        if [[ "$(basename "$rel")" == "$name" ]]; then remove_one "$rel"; fi
      done < <(all_skills)
    done
    exit 0
    ;;
esac

# ---- install ----
mkdir -p "$DEST"
say "Installing into $DEST ($([ "$DRY" -eq 1 ] && echo DRY RUN || echo live)):"

targets=()
if [[ "${SELECT[0]}" == "ALL" ]]; then
  while IFS= read -r s; do targets+=("$(dirname "$s")"); done < <(all_skills)
elif [[ "${SELECT[0]}" == "CURATED" ]]; then
  while IFS= read -r s; do
    [[ "$s" == */claude-code-imports/* ]] && continue
    targets+=("$(dirname "$s")")
  done < <(all_skills)
else
  for name in "${SELECT[@]}"; do
    # already a resolved path (from --category): install its dir directly
    if [[ "$name" == "$SKILLS_ROOT/"* && "$name" == *.md ]]; then
      targets+=("$(dirname "$name")")
      continue
    fi
    p="$(resolve_skill "$name" || true)"
    if [[ -z "$p" ]]; then
      err "skill '$name' not found (try ./install.sh list)"
      continue
    fi
    targets+=("$p")
  done
fi

if [[ ${#targets[@]} -eq 0 ]]; then err "nothing matched"; exit 1; fi
for t in "${targets[@]}"; do install_one "$t"; done
say "Done. Restart your Hermes session for new skills to appear in skills_list."