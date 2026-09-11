# BlackArch repo setup (add to a running Arch box)

Add the BlackArch security-tools repository to an existing Arch install. It does NOT replace the system — it adds a `[blackarch]` section that, once added, sits highest in pacman priority, so `pacman -Syst` will offer system upgrades from BlackArch mirrors from then on.

## Install (official script, does the whole thing)
```
curl -fsSL -o /tmp/strap.sh https://blackarch.org/strap.sh
chmod +x /tmp/strap.sh
sudo /tmp/strap.sh
```

What it does: fetches the pinned `blackarch-keyring-<VERSION>.tar.gz` + `.sig` over HTTPS, verifies the keyring signature, runs `pacman-key --init` + `pacman-key --populate` (initializes the local GPG keyring — needed on a fresh box), appends the `[blackarch]` Include to `/etc/pacman.conf`, runs `pacman -Syy`, and installs `blackarch-mirrorlist`. It prompts Y/n for the final mirrorlist install; pass `yes` via the wrapped-sh pattern.

## Install tools
- `blackarch-officials` (curated set of the most popular tools: nmap, hydra, wifite, john, metasploit, burpsuite, aircrack-ng, sqlmap, ...) — the sensible default.
- The full `blackarch` metapackage is ~10x heavier (2800+ packages) — avoid unless explicitly asked.
- `blackarch-officials` is a LARGE download: several hundred packages, many multi-hundred-MB security tools (metasploit, burpsuite, wordlists). Runs 10+ minutes even on a fast mirror. Always launch it with `terminal(background=true, notify=true)` — a foreground timeout kills it mid-download, and it creates a stale `/var/lib/pacman/db.lck` (recover per `references/pacman-lock-recovery.md`). Expect the package count to jump by several hundred (e.g. 1667 total after ~543 new this session); tools install as dependencies, not as literal `blackarch-`-named packages, so verify with `command -v <tool>` rather than `pacman -Q | grep blackarch`.
- Wordlists: there is NO `rockyou` package (`pacman -Ss rockyou` returns nothing; the package is missing from both arch and BlackArch). Use `assetnote-wordlists`, which installs to `/usr/share/assetnote-wordlists/` — NOT `/usr/share/wordlists/`. Point hydra/john/hashcat at the explicit assetnote path.
- Verify afterward: `command -v nmap hydra wifite john sqlmap msfconsole hashcat nikto gobuster searchsploit proxychains` etc. (fairly complete confirmation of the officials set).
