# rofi 2.0 .rasi syntax cheat-sheet

Verified against rofi 2.0.0-dirty on this user's Arch/Hyprland box.

## The parse-killers (rofi 2.0)

- `border: 1px solid @color;` → INVALID. rofi 2.0 split the shorthand:
  - `border-color: @color;`
  - `border-size: 1px;`
  - `border-radius: 22px;` (unchanged)
- Any parse failure makes rofi silently fall back to its DEFAULT theme — the user sees a plain WHITE BOX where the glass card should be, and NO error is shown. The only reliable parse check:

  ```bash
  timeout 3 rofi -theme ~/.config/rofi/foo.rasi -show run </dev/null 2>&1 | grep -iE 'fail|warn|error' || echo clean
  ```

  `-dump-config` is NOT a reliable check — it can exit 0 while `-show run` still reports `Failed to parse theme`.

## The list widget is `listview`, not `listbox`

- The dmenu item list is `listview`. A theme that styles a `listbox` widget while `mainbox children:` lists `listview` renders ONLY the inputbar — the items never appear ("the menu shows just the Go.../input, no list").
- Required for the list to render:

  ```rasi
  mainbox { children: [ inputbar, listview ]; }
  listview { lines: 10; columns: 1; spacing: 2px; }
  ```

## Glass-card recipe

```rasi
*  { background-color: transparent; }            /* root: transparent, no white flash */
window  { background-color: transparent; location: center; anchor: center; }
mainbox { background-color: rgba( 11,19,36,0.85 ); border-color: #2A3B60;
          border-size: 1px; border-radius: 22px; padding: 12px; }
```

- The card's translucent bg lives on `mainbox`, NOT `window`. `transparency: "real"` is not the mechanism and is not needed.
- `element selected` uses `background-color` + `border-color`/`border-size` (same split syntax).

## Rendering verification without a working vision tool

1. Launch the menu on the Wayland session: `setsid bash ~/.config/rofi/menu.sh &` (background), sleep ~2s.
2. `grim /tmp/shot.png` (grim exists on this desktop; Wayland native).
3. Pillow-sample the center column:
   - expect the card bg color in the middle (e.g. `(10,18,34)` navy)
   - a solid WHITE block where the card should be = theme failed, fell back to default
   - see `image-text-extraction` skill for OCR when the vision tool is down.

## Script structure that avoids delimiter leak

Feed rofi ONLY icon+label lines; map to the action after selection:

```bash
chosen=$(printf '%s
' "..." | rofi -dmenu -p 'Go...' -theme "$THEME")
case "$chosen" in
  *Apps)   apps_menu ;;
  *Update) terminal 'sudo pacman -Syu' ;;
esac
```

Embedding `label|action` in the visible line leaks the raw `|action` into the user's rows.
