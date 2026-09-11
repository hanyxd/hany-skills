# Dead pacman lock recovery

When a pacman transaction is killed (terminal timeout, dropped session, hard kill) before it finishes, it leaves a stale `/var/lib/pacman/db.lck`. Pacman removes this lock on clean exit; a stale one exists because the process died without cleanup.

## Verify the lock is actually stale (never assume)
- `ps aux | grep pacman | grep -v grep` — if pacman is still running, do NOT touch the lock; wait.
- `fuser -v /var/lib/pacman/db.lck` — if any process holds it, it is live; do not remove.
- Check `/var/log/pacman.log` tail: a killed-before-download transaction logs the `Running 'pacman -S ...'` line but NOT a `transaction started` / `installed` pair. If that marker is missing, no partial install happened — the tx died during download and pacman's database is untouched.

## Clear the stale lock and resume
- `sudo rm -f /var/lib/pacman/db.lck` (root-owned — plain `rm` fails with permission denied).
- Re-run the original install. No `pacman -Syu` or freshness step is needed.

## Why this works
- Pacman is transaction-safe: dependencies for the whole set are downloaded first, then the transaction is committed atomically. A kill during download only discards packages-in-cache (re-downloadable), never a half-installed state. Clearing the lock is safe because you verified the DB is untouched.

## Prevent the recurrence (long installs)
- Run big `pacman -S` transactions in the background with `terminal(background=true, notify=true)` instead of a foreground call — a foreground timeout kills the transaction mid-download and leaves the stale lock. Background is the correct pattern for any multi-GB / many-package install.
