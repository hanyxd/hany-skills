---
name: browser-exec-cdp
description: "Use when browser_exec fails: launch Chromium + BU_CDP_URL."
---

# Driving the Hermes browser tool (browser_exec / browser-harness)

The `browser_exec` tool runs scripts through a `browser-harness` daemon that connects to a Chrome/Chromium-family browser over CDP. When it errors it is almost always the daemon failing to find a supported browser, not the browser being broken.

## Symptom → diagnosis

`browser-harness: daemon default didn't come up -- check .../bu-default.log` whose log says `fatal: chrome-not-running: ...` means the daemon does not detect any running supported browser. Run `browser-harness --doctor`; a `[FAIL] chrome running` confirms it.

Mechanism (Linux): the daemon's `supported_browser_running()` only counts a Chromium whose `SingletonLock` symlink exists under a standard profile dir (`~/.config/chromium`, `~/.config/google-chrome`, etc.). A Chromium launched with a custom `--user-data-dir` (e.g. `/tmp/bh2`) is NOT detected even if its CDP endpoint answers on 9222.

## The reliable fix: launch headless Chrome + point the daemon at it via BU_CDP_URL

The daemon skips profile detection entirely when `BU_CDP_URL` is set and connects straight to that CDP HTTP endpoint.

1. Launch headless Chromium on the Hermes SSH/headless backend. Chromium binary is `/usr/bin/chromium` (or `CHROME_PATH`). Start as a Hermes background process, NOT with nohup/& (Hermes rejects shell-level backgrounding):

   ```
   chromium --headless=new --remote-debugging-port=9222 --user-data-dir=/tmp/bhch --no-sandbox --disable-gpu about:blank
   ```
   (background=true)

2. Verify CDP is up: `curl -s http://127.0.0.1:9222/json/version` returns a `webSocketDebuggerUrl`.

3. Run the daemon once with `BU_CDP_URL=http://127.0.0.1:9222` so it establishes and holds the connection. First clear stale runtime lock files so the daemon starts fresh:

   ```
   rm -f ~/.config/browser-harness/runtime/bu-default.spawnlock ~/.config/browser-harness/runtime/bu-default.pid
   BU_CDP_URL=http://127.0.0.1:9222 BH_AGENT_WORKSPACE=<workspace> browser-harness <<'PY'
   print(page_info())
   PY
   ```
   The binary lives at `/home/hany/.local/share/uv/tools/browser-use/bin/browser-harness` (not on PATH). Requires the CDP_URL env var exported in the SAME call so it propagates to the daemon it spawns.

4. Once the daemon is up and connected, `browser_exec` works on its own (the daemon persists across CLI invocations and the Hermes tool reuses it).

## Pitfalls

- Don't waste time launching a custom `--user-data-dir` Chromium and then calling `browser_exec` directly — custom dirs are invisible to the daemon's profile scan. The env-var route is what makes it connect.
- Export `BU_CDP_URL` in the same command/heredoc that invokes `browser-harness`; the daemon it spawns must inherit it.
- `browser-harness --doctor` is the fastest health probe.
- A fresh profile launches unsigned-in (good for isolation, but login-walled sites like Gmail will hit the Google sign-in page). Offer to attach the user's real signed-in Chrome profile instead of asking for credentials.
- The daemon preserves the attached tab across separate invocations — call `new_tab()` once per task, not on every script.
