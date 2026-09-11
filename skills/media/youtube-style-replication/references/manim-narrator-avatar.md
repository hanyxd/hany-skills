# Manim narrator avatar (talking-head with a still face)

A minimal "still face" character whose headmobjects stay frozen and only the eyes and mouth animate — the classic silent narrator/avatar for an explainer channel film. Works in any `manim.Scene`.

## Core pattern: add static parts once, animate only moving parts
The failure shape is re-adding or re-transforming the whole head on every blink/speech, which makes it jitter. Add the static head via `self.add(...)` (never animating it), then `self.play` ONLY the eye and mouth mobjects.

```python
head = Circle(radius=1.7, ...)
headgrp = VGroup(head, ears, brow, nose)
self.add(headgrp, eyeL, eyeR, mouth)      # static: never re-animate positions

# blink = squash only the eye Ellipses, leave pupils fixed
self.play(eyeL.animate.stretch_to_fit_height(0.08),
          eyeR.animate.stretch_to_fit_height(0.08), run_time=0.12)
self.wait(0.08)
self.play(eyeL.animate.stretch_to_fit_height(0.5),
          eyeR.animate.stretch_to_fit_height(0.5), run_time=0.12)
```

## Lip-sync a narration line without audio
Mouth as a sequence of `Transform`s between open/closed `Ellipse`s (width/height vary per phoneme) while the frozen head stays put; blink once or twice mid-line.

```python
new_mouth = Ellipse(width=0.55+0.2*((i*5)%3)/2, height=0.12+0.22*((i*7)%3)/2, ...)
self.play(Transform(mouth, new_mouth), run_time=0.09)
```
Then `Transform` back to a thin resting `Line` and `self.wait`. Reads as "talking" without TTS; add narration audio in a later ffmpeg mux.

## Eyes must read on the background
On a dark background, BLACK-filled eyes need a faint contrasting rim or they vanish into the void. Put a thin grey `Ellipse` behind the black one and self.add it once with the head.

```python
EYE="#000000"; RIM="#6B7280"
eyeL = Ellipse(width=0.34, height=0.5, color=EYE, fill_color=EYE, fill_opacity=0.95).shift(...)
rimL  = Ellipse(width=0.36, height=0.52, color=RIM, stroke_width=1).shift(...)
```

## Match the avatar to a still / channel art
For an avatar also used as profile/banner image, match the animated character to one regenerated still: same palette (e.g. `#111827` bg + `#10B981` + `#3B82F6`), same eye shape/color and minimal mouth, flat vector style. Generate the still with `image_generate` at 1:1 (pfp) and 16:9 (banner).