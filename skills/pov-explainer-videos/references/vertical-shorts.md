# 9:16 Vertical Short Pipeline (AI image + TTS + FFmpeg)

The still-image compositing path, distinct from Manim scenes: a generated vector illustration + dry voiceover + ducked ambient BGM + post-composited text, stitched by FFmpeg. Output: 1080x1920 @ 60fps MP4.

## Standard recipe (all-English)
```bash
# generate clean vector art (STRICT negative: text/typography/letters/foreign script, 3D, realistic features, gradients)
# clean 576x1024 portrait images cover-scale fine to 1080x1920
ffmpeg -y -loop 1 -framerate 60 -i clean.png -i voiceover.wav -i bg.mp3 \
  -filter_complex \
  "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
    drawtext=fontfile=Font-Bold.ttf:text='LINE 1':fontcolor=white:fontsize=80:
    x=(w-text_w)/2:y=(h-text_h)/2-140:shadowcolor=black@0.8:shadowx=4:shadowy=4:
    enable='between(t,0.5,8)'[v];
   [2:a]volume=0.08[bg];
   [1:a][bg]amix=inputs=2:duration=first[audio]" \
  -map "[v]" -map "[audio]" -r 60 -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest final.mp4
```
- Duck BGM to ~8-12% (`volume=0.08`) so the voice stays the focus.
- Cycle multiple caption lines with separate `drawtext` filters each gated by `enable='between(t,a,b)'`, snapping each in over the matching narration phrase.
- Always verify with `ffprobe -show_entries stream=codec_type`: must show h264 + aac, and `format=duration` equals the voice length when using `-shortest`.

## Arabic / RTL script overlays — do NOT use drawtext
`ffmpeg drawtext` (and Manim's Pango) rasterize Unicode but do NOT join Arabic letters. Correct connected RTL text must be shaped in PIL first:
```bash
source .venv/bin/activate && uv pip install arabic-reshaper python-bidi   # plus fonttools for weights
```
```python
from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
rt = get_display(arabic_reshaper.reshape("نص عربي"))          # proper RTL joining
# render onto an RGBA layer w/ blurred dark drop-shadow, alpha-paste onto the frame
```
- Confirm shaping will work: `PIL.features.check('raqm')` must be True.
- Use a real heavy Arabic font — `Noto Sans Arabic Black` ships with Arch (`/usr/share/fonts/noto/NotoSansArabic-Black.ttf`). Cairo/Tajawal come via AUR but `ttf-tajawal` build can fail; Noto is the reliable fallback.

## Arabic (non-English) narration
Edge-TTS (`text_to_speech` tool) has **no Arabic voices** — it returns empty audio for `lang=ar`. For Arabic narration use `gTTS`: `gtts-cli --lang ar "النص" --output voiceover.wav` (installed via `uv pip install gTTS`). Then normalize: `ffmpeg -i voiceover.wav -ac 1 -ar 48000 voiceover_48k.wav`. **The overlay language must match the narration language**, or the piece reads broken.

## Ambient background music without any music service
`scripts/make_hum.py` (sacred-hum drone: detuned low chord stack + subtle vinyl crackle + sparse hats + slow swell, stereo WAV). For a fuller dark-ambient bed, extend the same approach (detuned sine pad + lowpass + crackle). Encode to mp3: `ffmpeg -i x.wav -q:a 2 -b:a 192k x.mp3`.

## Font pitfalls
- A variable TTF passed to `drawtext` renders at its **default instance (often Regular/Thin)** regardless of the name. To get a real Black weight: `fontTools.varLib.instancer.instantiateVariableFont(TTFont(vf), {'wght': 900}, inplace=False).save('Font-Black.ttf')` (`uv pip install fonttools`).
- `curl`-fetched "font" files can be 50-byte redirects, not TTFs. Check with `file`: must say `TrueType Font`.
- For English text, Montserrat Black must be instantiated from the Google variable font (or use a preinstalled Noto Sans / Adwaita Sans and skip the download).

## Faceless vector art prompt core
Keep the negative prompt tight so the compositing gets a blank canvas: forbid `text, fonts, typography, letters, words, watermark, foreign/arabic script, 3D render, realistic eyes/nose/mouth, realistic skin texture, messy lines, gradients`. Flat-2D + cell shading + solid dark background (`#090D16`-ish) + studio rim light reads as the shared aesthetic.
