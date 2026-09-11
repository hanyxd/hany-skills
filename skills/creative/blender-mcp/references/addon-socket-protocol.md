# Blender MCP addon socket protocol (protocol 5, Blender 5.2)

The authoritative source is the INSTALLED addon, not the uv-cached server package:

- Addon: `~/.config/blender/<ver>/extensions/lab_blender_org/mcp/mcp_to_blender_server.py`
- Server pkg: `~/.cache/uv/archive-v0/<hash>/blender_mcp/` (emit the OLD wire format — do not copy it)

## Request frame

Send one JSON object as UTF-8, terminated by a single `\x00` byte, one request per connection:

```json
{"type": "execute", "code": "<python>", "strict_json": true}
```

`strict_json` is REQUIRED (boolean or the addon errors "Internal error...without the required 'strict_json' boolean key"). The old `{"type": <cmd>, "params": {...}}` shape that the `uvx blender-mcp` package emits is silently refused by the addon.

Only `{"type":"execute"}` is accepted. `code` runs via `exec` inside a Blender namespace with `bpy` imported, so `bpy` and `bpy.ops` are available.

## Response frame

\x00-terminated JSON:

```json
{"status": "ok" | "error", "result": <anything>|null, "stdout": "...", "stderr": "..."}
```
- `status: "ok"` → check `result` / `stdout`.
- `status: "error"` → `message` holds a Python traceback from inside Blender.

## "Client timed out" explanation

`{"status":"error","message":"Client timed out"}` means the addon read some bytes but never saw a complete request — malformed JSON, the wrong `type` key, or missing `\0`. It is NOT Blender being down. Fix the frame, not Blender.

## Ports / host

Defaults `127.0.0.1:9876`, overridable via `BLENDER_HOST` / `BLENDER_PORT` env on the addon process.
