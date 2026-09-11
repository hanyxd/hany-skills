---
name: ssh-remote-access
description: Use when setting up or running SSH to reach remote machines.
---

# SSH remote access

Procedure for establishing SSH into a machine from this Hermes host (non-interactive terminal).

## 1. Identify the target

- If Tailscale is in play, `tailscale status` lists nodes and their 100.x IPs.
- For plain LAN access (no VPN), find the real local interface IP:
  `ip -4 addr show | grep 'inet ' | grep -v 127.0.0.1 | grep -v '\b100\.'`
  The `100.` exclusion drops Tailscale's CGNAT range so you get the actual LAN address (e.g. 192.168.x.x). Verify that's the interface you want (wlp2s0 etc).

## 2. Ensure sshd is running

`Connection refused` on port 22 means the server is down or disabled. On Arch it's often disabled by default:

    ssh -o StrictHostKeyChecking=no user@host 'true'   # first: is it refused?
    echo 'hp' | sudo -S systemctl enable --now sshd   # then start + persist

Confirm it listens on all interfaces, not just loopback:

    ss -tlnp | grep sshd    # want 0.0.0.0:22 and [::]:22

## 3. Key auth — REQUIRED in non-interactive terminal

A non-interactive shell cannot answer an SSH password prompt, and with no display there is no `ssh-askpass` (you'll see `ssh_askpass: exec(...ssh-askpass): No such file`). Password/`Permission denied (publickey,password)` is therefore the normal outcome here — do not keep retrying password auth.

Set up an Ed25519 key once per target user:

    ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 -q   # if no key exists yet
    cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys

For first connects against an unpinned host key, add `-o StrictHostKeyChecking=no` (host key verification fails non-interactively until the key is accepted once).

## Pitfalls

- Password auth will NEVER succeed from the Hermes terminal — go straight to key auth instead of retrying. The askpass failure is a symptom of a headless terminal, not a config bug.
- Tailscale SSH is not transparent: connecting to a Tailscale 100.x IP still requires the remote sshd + your key. Tailscale routing is about reachability, not about bypassing sshd.
- Wi-Fi LAN IPs are dynamic (`192.168.12.138` can change on reconnect). If the user needs a stable LAN address, that is a router DHCP reservation or static config, not something SSH fixes.
- `hostname -I` is invalid on coreutils (`hostname: invalid option -- 'I'`); use `ip -4 addr` instead.
- User wants concise, ready-to-execute command blocks and piped-sudo automation (`echo 'hp' | sudo -S ...`) — build commands that way, keep explanation minimal.
