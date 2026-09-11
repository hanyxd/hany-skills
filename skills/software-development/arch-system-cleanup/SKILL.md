---
name: arch-system-cleanup
description: "Use when freeing disk space or cleaning caches on Arch."
---

# Arch system cleanup

## Procedure
1. Measure before cleaning — never guess what is big:
   - `df -h /` for overall usage
   - `sudo du -sh /var/cache/pacman/pkg /var/log` (sudo needed: subdirs are root-owned and cause permission-denied noise)
   - `journalctl --disk-usage`
   - `du -sh ~/.cache/* 2>/dev/null | sort -rh | head -15` and `du -sh ~/* 2>/dev/null | sort -rh | head -10` to locate the heavy caches/dirs
2. Clean each cache from largest down. Per-cache commands and verification: `references/cache-cleanup-recipes.md`.
3. Re-measure (`df -h /` + du of cleaned dirs) and report a before/after table. User wants concise copy-paste command blocks and a before/after summary, not prose.

## Always-on rules
- Run multi-GB / many-package `pacman -S` installs in the background (`terminal(background=true, notify=true)`) — a foreground timeout kills the transaction mid-download and leaves a stale `/var/lib/pacman/db.lck`. Recovering from that is `references/pacman-lock-recovery.md`.
- Piped sudo + interactive prompts: `echo 'hp' | sudo -S <cmd>` breaks on any [y/N] prompt — sudo consumes the piped line as the password, then the program's prompt reads EOF and misbehaves. For prompt-driven commands, wrap the inner command so the prompt stream is separate: `echo 'hp' | sudo -S sh -c 'yes | pacman -Scc'`.
- uv cache: `uv cache prune` blocks (~300s default) on the uv lock whenever ANY `uv tool`-installed process is running (e.g. a blender-mcp daemon). Check `ps aux | grep -E 'uv|uvx'` and `fuser ~/.cache/uv/.lock` first. Do not fight the lock — `rm -rf ~/.cache/uv/archive-v0/* ~/.cache/uv/cache-v0/*` is safe: uv re-downloads on demand, and the dir rebuilds (~75M skeleton stays).
- Verify paths with a `du -sh` drill-down before `rm`: cache layouts are deeper than convenience globs expect (Chromium-family: `~/.cache/BraveSoftware/Brave-Browser/Default/Cache` — profile dir is the extra level; `*/Cache` globs silently match nothing).
- **Before deleting a flat cache, check whether it could be a live dependency, not just a cache.** `~/.cache/ms-playwright/` holds the exact browser builds (`chromium_headless_shell-<rev>`) that Hermes's image-analysis and browser backends launch by pinned revision path. Deleting it 502s those services until the exact `chromium_headless_shell-<pinned-rev>`-style dir is restored.
  - Restore when the pinned rev is a newer playwright-core builds to a DIFFERENT rev: `find ~/.cache/ms-playwright -maxdepth 3 -name chrome-headless-shell` to see what full builds you do have, then SYMLINK the pinned rev dir to a present full build: `rm -rf <pinned-dir> && ln -sfn <present-full-rev-dir> <pinned-dir>` — the backends launch by the pinned *path*, so a symlink satisfies them. (An accidental empty dir from a failed download also needs a real binary behind it.)
  - Treat `~/.cache/ms-playwright` as a reinstall-at-your-own-risk dir: ask before clearing, or restore with `cd <hermes agent dir> && npx -y playwright-core@<bundled-version> install chromium`.
  - Bitrot check: `du` alone can't tell a live dep from junk — check `ps`/service logs for what references the dir before declaring it cache.
- When pacman cleanup tools report "no candidates" but `du` still shows GBs, du is the truth — see the pacman recipe for the actual mechanisms.

## References
- `references/cache-cleanup-recipes.md` — per-cache recipes: pacman, yay/AUR, uv, Brave/Chromium, journalctl, verification steps.
- `references/pacman-lock-recovery.md` — recovering a stale `/var/lib/pacman/db.lck` from a killed transaction; verify-stale-then-clear workflow.
- `references/blackarch-repo-setup.md` — adding the BlackArch security-tools repo to an existing Arch box (strap.sh) and installing `blackarch-officials`.
