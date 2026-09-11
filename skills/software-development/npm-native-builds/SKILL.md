---
name: npm-native-builds
description: Use when an npm native binding (sharp) fails to build.
---

# Installing npm projects with native binding dependencies

## Procedure
1. Match the Node version the project requires (README / engines). Pin it with mise IF different from default and run all npm commands through it explicitly — mise only changes PATH in NEW shells, so use `mise exec node@<ver> -- npm ...` rather than trusting the current shell: `MISE_HTTP_TIMEOUT=120 mise use -g node@24`. The default 30s HTTP timeout drops the download; raise it.
2. Clone shallow (`git clone --depth 1`). A mid-clone reset (curl 56 / early EOF / Connection reset) is common on flaky links — retry the clone rather than diagnosing; a small retry loop resolves it.
3. `npm ci`. Prefer `ci` over `install`: `install` mutates the lockfile. Only reach for the native-binding hack below if `ci` actually fails.
4. Verify with `npm run doctor` (if the project has one), then start the dev server in the BACKGROUND of the terminal tool (`background=true`) — foreground `&`/piped server commands get rejected as long-lived processes — and health-check with `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>`.

## Pitfall: sharp / node-gyp prebuilt ordering (the classic sharp failure)
sharp's install script (`install/check.js`) runs BEFORE its prebuilt platform package `@img/sharp-linux-x64` is placed into the tree, its check fails, and npm falls back to a node-gyp SOURCE build which errors: "Attempting to build from source via node-gyp ... Please add node-addon-api to your dependencies." The source-build error is the SYMPTOM, not the cause — the cause is the prebuilt platform pkg never being present. `--ignore-scripts`/`SHARP_*` build knobs do NOT fix it.

Working fix (npm 9/10/11):
```
npm ci --ignore-scripts --no-audit --no-fund        # tree installs clean, no build
cd /tmp && npm pack @img/sharp-linux-x64@<ver> \
                @img/sharp-libvips-linux-x64@<ver>   # exact vers from lockfile/sharp pkg
mkdir -p node_modules/@img/sharp-linux-x64 node_modules/@img/sharp-libvips-linux-x64
tar xzf img-sharp-linux-x64-<ver>.tgz -C node_modules/@img/sharp-linux-x64 --strip-components=1
tar xzf img-sharp-libvips-linux-x64-<ver>.tgz -C node_modules/@img/sharp-libvips-linux-x64 --strip-components=1
node -e "console.log(require('sharp').versions)"   # must print libvips versions, not a build error
```

Other triggers of the same source-build fallback: a leaked `npm_config_build_from_source`/`npm_config_build-from-source` env var (check `env | grep build_from_source`, unset before retrying) and `useGlobalLibvips()` returning true in `sharp/lib/libvips.js`. The standalone `npm install @img/sharp-linux-x64` in an EMPTY dir succeeds — that proves the package is fetchable and the failure is tree-ordering, not network.

## Pitfalls that waste time
- After a failed sharp build, npm rolls the failed package dir back — `node_modules/sharp/install/check.js` and `node_modules/sharp/lib/` can be missing on the next probe. Re-run the full install rather than inspecting partial state.
- `npm ci` requires `package-lock.json` AND wipes node_modules. Never delete the lockfile to "reset"; restore it from git instead.
- The time-consuming false path is dropping to Node versions or reinstalling sharp standalone — neither addresses the real ordering problem. Go straight to `--ignore-scripts` + platform-pkg manual extraction.
