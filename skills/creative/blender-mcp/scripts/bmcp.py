#!/usr/bin/env python3
"""Driver for the Blender MCP addon's raw socket (127.0.0.1:9876).

Works whether or not Hermes' MCP tools are registered, because it talks
straight to the addon's TCP listener. Call run(code) with Blender-Python.
"""
import json, socket

HOST, PORT = "127.0.0.1", 9876


def run_bpy(code, strict_json=False, timeout=120):
    msg = {"type": "execute", "code": code, "strict_json": strict_json}
    payload = json.dumps(msg).encode("utf-8") + b"\x00"  # \x00 terminator is required
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall(payload)
    chunks = []
    while True:
        try:
            c = s.recv(8192)
            if not c:
                break
            chunks.append(c)
            if b"\x00" in b"".join(chunks):
                break
        except socket.timeout:
            break
    s.close()
    raw = b"".join(chunks).rstrip(b"\x00").strip()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        return {"error": f"bad response: {e}", "raw": raw[:500].decode(errors='replace')}


def run(code, **kw):
    r = run_bpy(code, **kw)
    if r.get("status") == "error":
        return {"error": r.get("message"), "stderr": r.get("stderr", "").strip()}
    return {"status": r.get("status"), "stdout": r.get("stdout", "").strip(), "result": r.get("result")}
