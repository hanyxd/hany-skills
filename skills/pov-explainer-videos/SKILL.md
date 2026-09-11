---
name: pov-explainer-videos
description: "POV life-story explainer scripts + faceless mascot videos."
---

# POV Narrated Explainer Videos

Use when the user wants a video (or script) in the style of narrated explainer/documentary channels ("The Explainer Boss", "Your Life at Every Level of X" POV stories) — a calm narrator walking the viewer level-by-level through a life/career, PLUS a talking-head mascot/avatar, ambient background, and narration audio.

## Reverse-engineer a reference channel's format FIRST
Do not guess a channel's style from its name or a pasted marketing blurb. Pull the real structure from its own videos:

```bash
yt-dlp --flat-playlist --print "%(duration)ss | %(title)s" "https://www.youtube.com/@CHANNEL/videos"   # the real catalog
# grab an episode's auto-subtitle and read the actual narration:
yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt --output "subs_%(id)s" "https://www.youtube.com/watch?v=VIDEO_ID"
# strip cue/<> tags to plain text, then split on the level markers:
python3 - <<'PY'
import re
vtt=open("subs_VIDEO.en.vtt").read()
txt=re.sub(r"<[^>]+>", "", vtt)
txt=re.sub(r"^\d{2}:\d{2}:\d{2}[^\n]*\n", "", txt, flags=re.M)
s=" ".join(l.strip() for l in txt.splitlines() if l.strip()); s=re.sub(r"\s+", " ", s)
for seg in re.split(r"(?=Level [a-zA-Z])", s):
    if seg.strip(): print(seg.strip()[:220]); print("=====")
PY
```
The level nicknames ("script kitty -> account thief -> system intruder -> ...") are the backplane — mirror them.

"The Explainer Boss" specifically is a **POV lifestyle/life journey narration**, NOT geometric animation despite the name. Check before assuming.

## The POV level format (user's spec)
- Open each level `Level N, <nickname>.` then a concrete micro-scene.
- Second-person direct address ("You"), grounded absurd specifics (exact dollar amounts, a router password, a folder named `final_final_v2_FINAL`).
- Ironic de-romanticization: the dangerous/glamorous job turns out dull bureaucratic grind ("It's boring. Astonishingly boring.").
- Escalating nicknames toward the top; each level ends on one aphorism/punchline.
- Honor the real turning point: with a "white hat"/defender subject, invert the arc to a moral pivot (closer-of-doors, mentor ending) instead of escalating crime.

## Talking-head mascot (Manim)
Reusable scene pattern — see `references/talking-head.md`. Key rules:
- Freeze the head: `self.add(headgrp, ...)` once; put ONLY the animated feature in `self.play(...)`.
- Animate only lips + eyes. Blink = `stretch_to_fit_height` squish on eye ellipses (0.12s down/up, wait ~0.9s between). Mouth = `Transform` a `Line` to a fat `Ellipse` per char (~0.09s), vary size by char index; Transform back at end.
- Faceless mascot: a hood shape with a filled darker circle as an empty void, no eyes/face — fewer uncanny artifacts, fits the anonymous-narrator tone.
- Background: dark base `#0B0F14` + low-opacity drifting `Dot` glows + a slow `scale(1.02/0.98)` breathing feel on the avatar.

## Audio (no GPU)
- Narration: `text_to_speech` tool for a calm narrator line, then mux aligned to mouth via `ffmpeg -i vid.mp4 -i tts.mp3 -filter_complex "[1:a]adelay=1500|1500[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -shortest out.mp4` (adelay ms = when the mouth opens).
- Ambient "hum" drone with no GPU/music service: generate a WAV from stdlib (`wave`+`struct`+`math`) — run `scripts/make_hum.py hum.wav`. Fade ffmpeg: `afade=t=in:d=1.5,afade=t=out:st=13:d=2`.
- Always verify the mux: `ffprobe -show_entries stream=codec_type` must show both `h264` and `aac`.

## AI-image + TTS vertical shorts (non-Manim)
For a faceless-vector still image + dry voice + ducked ambient BGM + overlaid typography stitched into a 9:16 (1080x1920@60) MP4, use the compositing recipe and pitfalls in `references/vertical-shorts.md`. Highlights: FFmpeg `drawtext` cannot shape Arabic (shape with PIL arabic-reshaper + bidi instead); Edge-TTS has no Arabic voices (use `gTTS`), and overlay language must match narration language; a variable font rendered by drawtext defaults to Regular weight (instantiate `wght:900` with fontTools).

## Pitfalls
- Heavy Manim scenes (ImageMobject + multi-second lagged animations at `-qm`) exceed the 180s foreground timeout. Render with `terminal(background=true, notify=true)` and wait on the handle.
- Manim CE v0.21 has no `JOINED`: `LineJointType` is in `manim.constants` with members AUTO/ROUND/BEVEL/MITER, set as an attribute (`mob.joint_type = LineJointType.ROUND`), not a `set_stroke(join_style=...)` kwarg — that raises TypeError.
