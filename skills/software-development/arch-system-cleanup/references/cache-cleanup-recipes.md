# Cache cleanup recipes (Arch)

## pacman package cache (`/var/cache/pacman/pkg`)
- Keep last N versions: `echo 'hp' | sudo -S paccache -rk2` (or `-rk1` to keep only the newest).
- Full clean: `echo 'hp' | sudo -S sh -c 'yes | pacman -Scc'` — also removes dangling `.sig` files and root-owned stale `download-*` temp dirs that paccache ignores. `yes | sudo -S pacman -Scc` alone fails: yes-output and the sudo password read collide on the same stdin.
- `paccache -rk2` reporting "no candidate packages found" while `du` still shows GBs is NORMAL when most packages have a single cached version — the space is real packages, not junk. Reclaim with `-rk1` or the full `-Scc`, never assume the cache is already clean.
- `du -sh /var/cache/pacman/pkg` without sudo under-reports (permission-denied on root-owned subdirs); use `sudo du`.

## AUR build cache (yay)
- `yay -Sc --noconfirm` clears `~/.cache/yay` (multi-GB possible) and is non-interactive, no sudo. Keep it as a follow-up when pacman/uv/browser are done.

## uv cache (`~/.cache/uv`, can reach multi-GB)
- Running uvx tools hold `~/.cache/uv/.lock`; every `uv cache prune` attempt then waits 300s and times out. Reliable path:
  `rm -rf ~/.cache/uv/archive-v0/* ~/.cache/uv/cache-v0/*`
- Safety: uv re-downloads deleted blobs on demand; already-running uvx tools (blender-mcp etc.) may re-download once at next launch. This is expected, not breakage.

## Brave / Chromium browser cache
- Real paths (profile is one level deeper than the obvious glob):
  `~/.cache/BraveSoftware/Brave-Browser/Default/Cache`
  `~/.cache/BraveSoftware/Brave-Browser/Default/Code Cache`
- `rm -rf` both; safe, rebuilds automatically. Confirm with a du drill-down first.

## journalctl logs
- `journalctl --disk-usage` counts active + archived journals (this machine ~300M, split across `/run/log/journal` and `/var/log/journal`).
- `--vacuum-size`/`--vacuum-time` only remove ARCHIVED journals, so they can report "freed 0B" while total stays high — the remainder is the active journal, which vacuum does not touch. To cap active too: set `SystemMaxUse=` in `/etc/systemd/journald.conf` and `systemctl restart systemd-journald`. ~300M is normal; do not chase it unless it is a real fraction of disk.

## Verification
- After each cleanup: `du -sh <dir>` again, then `df -h /` at the end; report a before/after table.
