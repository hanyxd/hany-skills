---
name: blender-mcp
description: "Use when the user is working in Blender."
---

# Blender automation via Hermes MCP

The user runs Blender (EEVEE) with the official Blender MCP addon (`bl_ext.lab_blender_org.mcp`) listening on a socket, and Hermes has `mcp_servers.blender` configured to run `uvx blender-mcp`. Two ways to drive Blender:

## 1. Native MCP tools (`mcp_blender_*`)

Load ONLY at Hermes STARTUP — there is no hot reload. A session that predates the `mcp_servers` config, or an agent restarted mid-task, has none of these tools registered. Restart Hermes to get them into a live session.

## 2. Drive the addon socket directly (works in ANY session)

The Blender MCP addon accepts raw JSON frames on `127.0.0.1:9876` (env `BLENDER_HOST`/`BLENDER_PORT`). This bypasses MCP-tool registration entirely, so it works even when the MCP tools are absent. Use the bundled `scripts/bmcp.py` helper. See `references/addon-socket-protocol.md` for the exact frame format.

## Building/editing scenes

- Create objects with `bpy.ops.mesh.primitive_*_add(radius=..., location=..., scale=...)` — the addon's sandbox runs full Blender Python with `bpy`/`bpy.ops` available.
- Materials: `bpy.data.materials.new` + Principled BSDF. On EEVEE 5.x the specular input is `"Specular IOR Level"`, NOT `"Specular"` — guard both names.
- Deleting the default objects also deletes the default Camera; recreate it (`bpy.data.cameras.new` → `bpy.data.objects.new` → link) and set `scene.camera`, or the render is empty.
- Grab `scn = bpy.context.scene` at the top of the script — later blocks reference it and will NameError if it is only bound mid-file.
- Render via `scene.render.filepath = "/abs/path.png"; bpy.ops.render.render(write_still=True)`, then verify the file exists on disk.
- Build the scene in one multi-part script (body blobs, ears, face, tail curve, materials, camera), send it, fix the one error that surfaces, resend. Iterate on the full scene, not piecemeal.

## Verification

After rendering, confirm the PNG exists and load it with vision_analyze to self-review proportions/features before declaring success.

## Pitfalls

- Do NOT trust `hermes mcp test <server>`: it can report "Connection failed" after a long timeout even when the underlying `uvx blender-mcp` connects to Blender in milliseconds. To verify the link, run `timeout 25 uvx blender-mcp` and watch for "Connected to Blender at ...".
- The #1 wasted-time trap is the wire format: the old `send_command` shape `{"type": <cmd>, "params": {...}}` is what the `uvx blender-mcp` Python package emits, but the in-Blender addon (Blender 5.2, protocol 5) silently refuses it. Use `{"type":"execute","code":...,"strict_json":<bool>}` — always read the INSTALLED addon's `mcp_to_blender_server.py`, not the uv-cached server package, for the authoritative request shape.
- An addon response of `{"status":"error","message":"Client timed out"}` almost always means the frame was malformed (missing `\0` terminator or wrong `type` key), not that Blender is down.
- The addon only executes a request once it sees a `\0` terminator; responses are also `\0`-terminated — rstrip trailing `\0`/whitespace before `json.loads`.
- One request per socket connection; open, send, read to a `\0`, close. Do not keep the connection open across commands.

## Support files

- `scripts/bmcp.py` — reusable client: `run(code)` sends Blender-Python and returns parsed `{status, stdout, result}`.
- `references/addon-socket-protocol.md` — the exact frame + response shapes and where to read the authoritative source.
