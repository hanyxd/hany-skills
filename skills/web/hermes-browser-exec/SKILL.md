---
name: hermes-browser-exec
description: "Use when driving Hermes browser_exec: launch/connect/login."
---

# Driving Hermes browser_exec (browser-harness)

The `browser_exec` tool drives a real Chromium via the browser-harness daemon.
It only works if the daemon can connect to a running Chrome. On Linux the
startup/connection path has sharp edges; here is the working procedure and
the pitfalls that cost the most time.

## Getting the daemon to connect (Linux)

Diagnose first: `browser-harness --doctor` shows whether Chrome is detected
and the daemon is alive. When `browser_exec` fails with
`daemon default didn't come up` and the log says `chrome-not-running`:

1. The harness's Linux detection, `supported_browser_running()`, only counts
   a Chromium whose user-data-dir is a **standard profile path** (e.g.
   `~/.config/chromium`) and which holds that dir's `SingletonLock`. A
   Chrome launched with a custom `--user-data-dir=/tmp/whatever` is
   invisible to the detector, so a hand-launched custom-profile instance is
   never enough by itself.
2. Working fix that bypasses the brittle profile detection: launch your own
   headless Chromium and point the harness at its CDP endpoint:
   ```
   chromium --headless=new --remote-debugging-port=9222 \
            --user-data-dir=/tmp/bhch --no-sandbox --disable-gpu about:blank
   # then, in the shell that invokes browser-harness / browser_exec:
   export BU_CDP_URL=http://127.0.0.1:9222
   ```
   With `BU_CDP_URL` (or `BU_CDP_WS`) set, `_is_local_chrome_mode()` is
   false and the daemon connects to your endpoint regardless of profile.
   Verify with `curl -s http://127.0.0.1:9222/json/version`.
3. **Clear stale daemon state before retrying.** The daemon writes
   `~/.config/browser-harness/runtime/<name>.pid` and `.../<name>.spawnlock`;
   a leftover lock after a crashed launch makes every retry fail fast with
   ``daemon didn't come up`` even when Chrome is fine. Remove
   `~/.config/browser-harness/runtime/bu-default.spawnlock` (and `.pid`)
   between attempts, and use `browser-harness --reload` to force a fresh
   daemon.
4. The daemon persists across CLI invocations once up. If a later call fails
   with `No target with given id found`, the attached tab was dropped — call
   `ensure_real_tab()` and re-read the page before acting.

## Interacting with the page

- Prefer the `fill_input(selector, text)` helper for typing into fields. A
   raw JS prototype-setter on an `input[type=...]` sometimes throws
   `No target with given id found` when the attached target has gone stale;
   `fill_input` (and `ensure_real_tab()` first) is the robust path.
- Text-first: read pages with `page_info()` + `js(document.body.innerText...)`
  rather than screenshots; the agent cannot view images.

## Login walls and bot detection (Google and others)

Signing into a real account through a headless/automated Chrome frequently
hits a hard block. Google in particular shows **"Couldn't sign you in — This
browser or app may not be secure"** after entering the email, before the
password step, when the session is flagged as automated. This is a durable
platform behavior, not a transient error; retrying the same headless session
will not clear it.

When that block appears, do NOT advise the user by echoing their password or
push through with more automation flags as the primary path. It may sometimes
be bypassed by relaunching Chrome with anti-automation flags
(`--disable-blink-features=AutomationControlled`, a real Chrome UA), but the
reliable route for an account the user actually owns is to drive the user's
**real, already-logged-in browser profile** instead (attach via CDP to their
normal Chrome), or have the user sign in manually and hand over the action.
Never ask the user to speak their password into chat as the first option —
offer it only in the signed-in-real-profile / manual route.

Don't treat a blocked sign-in as a reason to declare browser automation
"broken." The browser works fine for public pages and for logged-in-session
work; the block is specific to bot-detected logins.
