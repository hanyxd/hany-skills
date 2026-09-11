---
name: arch-storage-cleanup
description: Use when freeing disk space on Arch Linux.
---

# Arch Linux storage cleanup

## Order: map first, clean caches, then runtimes, never data

1. **Map before touching anything.** `df -h / /home /var`, then `du -xhd1 /home/<user> | sort -rh | head -15`. Drill into `.local` and `.cache` with `du -xh --max-depth=2` when those dominate. The single biggest item is often hidden in `.local/share/mise/installs` or `.cache/uv`.
2. **Present a plan, run the safe block, ask before destructive waves.** Group into: safe rebuildable caches (auto-run), reinstallable runtimes (ask), personal data (ask, never auto-delete).

## Safe block (all rebuildable caches)

```bash
# pacman pkg cache: keep last 2 + foreign, drop rest (needs sudo for this user)
echo 'hp' | sudo -S paccache -rk2 && echo 'hp' | sudo -S paccache -ruk0
# tool caches
uv cache clean
rm -rf ~/.cache/yay ~/.cache/ms-playwright ~/.cache/.bun ~/.npm
rm -rf ~/.gradle/caches
```

`paccache -rk2` keeps the last 2 installed versions; `-ruk0` removes all uninstalled package files. Check orphans first with `pacman -Qtdq | wc -l`.

## Pitfalls

- **`uv cache clean` on a multi-GB cache can exceed the 180s foreground timeout** — launch it with `terminal(background=true, notify=true)` and let the whole safe block run there, then poll with `process_manage`. Don't churn a foreground call that times out mid-clean.
- **mise runtime installs (`~/.local/share/mise/installs`) can be ~11G for a single node version** — the biggest single recoverable item, but check `mise ls` before uninstalling. An ACTIVE default (pinned in `~/.config/mise/config.toml`) must NOT be removed; only spare/unlisted versions are safe to `mise uninstall`. Removing the active default breaks the user's tooling.
- **Clearing browser cache (`~/.cache/BraveSoftware`, etc.) logs the user out of all their browser sessions.** Warn before touching it; ask rather than auto-deleting.
- **Do NOT delete `~/.cache/ms-playwright` as part of a routine clean** — Hermes' `vision_analyze` backend needs `chromium_headless_shell-<pinned version>` there and silently breaks (returns "no image" / bad gateway) until reinstalled. If you must free it, warn the user that image analysis will fail until `npx playwright-core@<pinned> install chromium` is run again.
- **Never delete personal data dirs (`.local/share/Steam`, `.minecraft`, project code) without explicit confirmation** — flag them as data, not cache.
- **Flutter**: ~1.8G SDK in home plus ~1.1G in `~/.cache/yay/flutter`; only remove if the user confirms they're not actively building Flutter.

## Report

Give a before/after number per item. State what was left untouched and why (active runtime, logout side-effect, personal data). Offer the deferred waves when the safe block is still running.
