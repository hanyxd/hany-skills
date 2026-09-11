---
name: rofi-desktop-menus
description: "Use when building or fixing rofi launcher menus on Linux."
---

# Rofi launcher & dmenu menus

Class: building and styling rofi menus (launcher, app list, tool picker, power menu) and wiring them to a keybind. This user runs Hyprland/Omarchy with kitty+foot terminals and expects dark, glassy, rounded menus with Nerd Font icons.

## Procedure

1. **Structure the menu script as: display list | rofi -dmenu | map back to action.** Keep the rofi-visible lines clean — icon + label only. Map to the action AFTER selection (`case "$chosen" in *Label) ... esac`), not by embedding `label|action-id` in the visible line: the raw `|action` delimiter leaks into the user-visible rows otherwise.
2. **`drun` mode only lists GUI apps with `.desktop` entries — useless for CLI tools.** nmap/hydra/wifite have no .desktop files, so `rofi -show drun` shows nothing. For a security-tool launcher, list actual binaries (e.g. from a scan script) and launch each in a terminal. This exact failure ("BlackArch apps not showing") is a drun-vs-CLI-tools mismatch, not a config bug.
3. **Terminal launch:** `if command -v kitty; then kitty -- bash -c "$1; exec bash" & elif command -v foot ...`.
4. **Wire the keybind in the Hyprland config** (this user: `~/.config/hypr/bindings.lua`, `o.bind("SUPER + B", ...)`), pointing at the script.

## Theming — rofi 2.0 syntax

- **rofi 2.0 removed/split the `border:` shorthand.** `border: 1px solid @color;` FAILS THE WHOLE PARSE — and a failed theme silently falls back to the plain default (a WHITE BOX, no error shown to you). Use `border-color:` + `border-size:` instead. This is the #1 cause of "my themed rofi renders as a white rectangle".
- **The list widget is `listview`, NOT `listbox`.** A theme that styles `listbox` but lists `listview` in `mainbox children` renders the inputbar ONLY — the item list never appears ("menu shows just Go.../input, no items"). Set `listview { lines: N; columns: 1; }`.
- A parse check via `rofi -theme X -dump-config` can LOOK successful while the real `-show run` emits `Failed to parse theme` — cheap tool retreat: cmd is `grep -iE 'fail|warn|error'` on `rofi -theme .rasi -show run </dev/null`, 0 matches = actually clean.
- For a glass card: `window { background-color: transparent; }` + `mainbox { background-color: rgba(...); border-radius: 22px; }` — the card's own bg, not the full-window.
- **Verify render by pixels, not eyeballs:** `grim` a capture, then Pillow-sample the center column for the expected card bg; a mid-screen solid WHITE block instead of navy = broken theme. See `image-text-extraction` for the vision fallback.

## Pitfalls

- A failed `.rasi` parse silently falls back to the default theme — you see a white box, not an error. Always run the grep-parse check above after editing.
- Selecting a Nerd-Font-delimited row with `${line##*|} -based stripping is fragile when the label itself contains the delimiter (or when icons/space sink the strip). Prefer map-back-by-label matching.
- On this desktop, tests that `source` the whole menu script hang (the menu body runs and waits on rofi). Test functions by extracting them, not by sourcing the file.
- Wire menu scripts to a keybind via the Hyprland bindings file, and keep a publish sync: this user keeps a copy in a menu dir (e.g. workspace) for the web/tool-launcher variant.

## References
- `references/rofi-rasi-syntax.md` — rofi 2.0 .rasi syntax cheat-sheet (border split, listview, parse-check, glass-card recipe) to copy and adapt.
