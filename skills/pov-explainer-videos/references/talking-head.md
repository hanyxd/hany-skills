# Manim talking-head / faceless-mascot scene

A frozen head where only eyes/mouth animate. Freeze = `self.add(...)` once; animate = `self.play(...)` only on the moving part. This avoids jitter and keeps the mask stable.

```python
from manim import *
BG="#0B0F14"; TEXT="#E8EAF0"; GREEN="#10B981"; GREY="#8A94A6"; RIM="#6B7280"

class TalkingHead(Scene):
    def construct(self):
        self.camera.background_color = BG
        # STATIC head (faceless): hood + void interior, added once
        hood = Circle(radius=1.85, color=RIM, stroke_width=3).shift(DOWN*0.1)
        void = Circle(radius=1.15, color=BG, fill_color="#04060A",
                      fill_opacity=1.0, stroke_width=2).shift(DOWN*0.1)
        headgrp = VGroup(hood, void)
        self.add(headgrp)  # freeze: only added, never in self.play(...)

        # MOUTH: line -> fat ellipse per char (lip-sync), then back to line
        mouth = Line(LEFT*0.28, RIGHT*0.28, color=TEXT, stroke_width=6).shift(DOWN*0.25)
        self.add(mouth)
        line = "The one who closes doors."
        for i, ch in enumerate(line):
            if ch == ' ':
                self.wait(0.12); continue
            m = Ellipse(width=0.5+0.24*((i*5)%3)/2.0, height=0.10+0.22*((i*7)%3)/2.0,
                        color=TEXT, stroke_width=6).shift(DOWN*0.25)
            self.play(Transform(mouth, m), run_time=0.09)
        self.play(Transform(mouth, Line(LEFT*0.28, RIGHT*0.28, color=TEXT,
                                        stroke_width=6).shift(DOWN*0.25)), run_time=0.25)
        self.wait(2.5)
        # EYES (only if a face is wanted): blink by squishing, pupils stay fixed
        # eyeL.animate.stretch_to_fit_height(0.08) -> back(0.5), wait 0.9 between
```

Mouth runs a full line here; to sync with real narration, generate the TTS line, measure its duration, and `adelay` the audio to the frame where the mouth opens.

Ambient animated background: `Rectangle` base + `Dot` glows (color=GREEN/BLUE, `fill_opacity` ~0.15) drifting via `glow.animate.move_to(...)`, and a breathing scale on the whole composite `VGroup.animate.scale(1.02/0.98)`.
