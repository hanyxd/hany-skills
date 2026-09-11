---
name: youtube-style-replication
description: "Replicate a YouTube channel's format and voice."
---

# YouTube Style Replication

Use when a user gives a YouTube channel and asks to "make something like it" — replicate its content style/format/voice, either as a sample or a full production. The deliverable is an ORIGINAL script/manuscript matching the channel's editorial machine, not a copy of any episode.

## Core rule

**Verify the channel's ACTUAL format before trusting any written style guide.** Users often paste a guide that describes a DIFFERENT channel than the one they link (e.g. a geometric-Manim explainer guide attached to a POV-documentary channel). Always pull the channel's real catalog and a real transcript; reconcile the guide against what the channel actually produces, and surface the mismatch to the user.

## Steps (in order)

1. **Get the channel's real catalog** with yt-dlp (no login, no browser, no bot-wall):
   ```
   yt-dlp --flat-playlist --print "%(duration)ss | %(title)s | %(id)s" "<channel_url>"
   ```
   Title patterns + durations reveal the format (episode length, naming template, subject range) at a glance. Determine the chapter/level structure from titles.

2. **Pull a representative transcript** — pick the closest existing episode (for a "white hat" video, grab the "black hat"/"dark web" sibling):
   ```
   yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt --output "x_%(id)s" "URL"
   ```

3. **Flatten the VTT to plain text and DE-DUPLICATE.** VTT cues overlap so each cue's text repeats 3x. Strip timestamp/cue lines and `<c>` tags, join, collapse whitespace:
   ```
   python3 -c "import re,sys; t=re.sub(r'<[^>]+>','',open(sys.argv[1]).read()); \
   t=re.sub(r'^\\d{2}:\\d{2}:[0-9.]+.*\\n','',t,flags=re.M); \
   print(re.sub(r'\\s+',' ',' '.join(l.strip() for l in t.splitlines() if l.strip())))" file.vtt
   ```

4. **Extract the format skeleton** from the flattened text — the recurring structural markers. For level/chapter channels, the openers are the signal. `grep -oE "Level [^>]{0,40}"` on the RAW vtt (sed out tags, `awk '!seen[$0]++'` to dedupe) surfaces the escalating nickname sequence that anchors the whole format.

5. **Distill the editorial voice into reusable rules**: level/chapter framing + nickname opener; direct-address "you"; grounded absurd specifics (city, dollar amount, folder name) that make a premise feel lived-in; ironic de-romanticization (every escalation secretly turns dull/bureaucratic); escalating titles; aphorism/punchline per section. Keep these as your authoring checklist — do NOT copy sentences.

6. **Author an ORIGINAL script** in that voice with fresh subject matter. For a new topic in a known template (e.g. "Your Life as Every Level of X"), preserve the template beats but invent the level nicknames, specifics, and moral pivot that fit the new subject.

7. **Offer a filmed preview** of the style look (title card + opening beats) using an animation tool (e.g. manim) so the user sees the visual too — but only after the voice/format deliverable lands. For a channel whose brand is a silent narrator avatar, build a minimal still-face talking-head (static head, only eyes/mouth animate) and a matching regenerated still -- see `references/manim-narrator-avatar.md`.

## Pitfalls

- **Prefer yt-dlp over web_extract for YouTube.** Direct channel-page extraction returns a 401 bot-wall; yt-dlp pulls catalog + auto-subs with no login. Don't waste turns on the browser/CDP for public video metadata when yt-dlp is the reliable path.
- **Don't trust a pasted style guide over the live channel** — reverse the two and reconcile. Formulate whether the requested "style" is the channel's real one or a misattributed one, and ask the user which to follow when they genuinely conflict.
- **Write original content, never copied lines.** The goal is the format's machinery (beats + voice), not its words — copying narration risks the existing episode and teaches nothing.
- **De-duplicate VTT text before reading it** or the transcript triples in length and the structure markers are buried in repetition.
