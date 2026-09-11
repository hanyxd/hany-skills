---
name: aident-loadout
description: Access external apps via the Aident Loadout CLI.
version: 1.0.0
metadata:
  hermes:
    tags: [aident, loadout, cli, gmail, instagram, github, integrations]
---

# Aident Loadout (access layer for external apps)

This user's preferred way to reach external services — Gmail, Instagram, GitHub, researcher APIs (Exa/Firecrawl/Fal), etc. — is the `aident` CLI backed by Aident Loadout. It manages OAuth via Aident Vault and already has accounts connected, so App Passwords and Google Cloud Console OAuth setup should be the FALLBACK, not the first move.

## When to use

- User asks to read/send Gmail, use Instagram, GitHub, or any integration available in Aident Vault.
- User says to follow `https://aident.ai/SETUP.md` or references "the skill from aident ai".
- Existing himalaya/google-workspace paths are blocked (no App Password, OAuth not set up).

## Account facts

- Active Loadout account: moop85514@gmail.com (Hany El). The h60930593@gmail.com creds in ~/.hermes/.env are STALE — do not use them.
- Credentials/config: ~/.aident/credentials.json, ~/.aident/config.json.
- Set up ONCE (`aident setup --base-url https://loadout.aident.ai --client-name Hermes --json`); reinstall skill with `aident update --project`. Skill is also installed for Claude Code/Gemini/Codex/WorkBuddy via the updater.

## Core command shape

```bash
aident capabilities search --query "<what you need>" --scope '{"integrationId":"<integration>"}' --limit 10 --json
# inspect a schema:
aident capabilities get  --name "<canonical_action_name>" --parts inputSchema
# execute (canonical name from search/get):
aident capabilities execute --name "<canonical_action_name>" --input '<json>' --json
```

Canonical names look like `composio:gmail_tools:gmail_fetch_emails`, `composio:instagram_tools:instagram_send_text_message`. Always `search` first, then `get --parts inputSchema` to learn required args — do not assume parameter names from memory.

Check what's connected: `aident vault status --json`. Treat an integration as connected only when Vault confirms it.

## Gmail

Read the inbox with `composio:gmail_tools:gmail_fetch_emails`.

- ALWAYS pass `"verbose":false` unless you need full message bodies. With verbose:true the raw HTML payloads flood the terminal (1MB+ per message) and truncate output. verbose:false returns subject/sender/timestamp/labels and is ~75% faster.
- `"user_id":"me"`, `"label_ids":["INBOX"]`. Combining label_ids with is:/label: query logic silently over-restricts (AND logic); use one strategy consistently.
- `metadata_only`/`ids_only` are NOT interchangeable with verbose:false — they can return 0 rows (empty messages field is a valid no-results state). Use verbose:false.
- Unread = `"UNREAD" in labelIds`.
- Send with `gmail_send_email`; reply with `gmail_reply` (threads automatically).

## Instagram

Connection fits the Messenger/Graph API model, not the normal Instagram app API. Key quirks (see references/instagram.md):

- Recipients are addressed by **PSID** (Instagram-scoped user id), NOT username. Resolve it from an existing conversation via `instagram_get_conversation`, which returns participants and messages with `{id, username}`.
- You CANNOT initiate first-contact DMs via API, and you can only message someone within their 24-hour messaging window (last message to you < 24h ago). A send outside that window fails 403 "This message is sent outside of allowed window." — get the user to message you first, then send.
- Pass the business account IG id as `ig_user_id` (fetch via `instagram_get_user_info` → `id`, e.g. `17841473490190539`) plus recipient PSID.

## Verify artifacts

Loadout action results carry `success:true` on the wrapper even when the downstream provider rejected the call (e.g. IG send returned 403). Check the nested `output.data` / error fields before reporting delivery — wrapper success is not delivery.

## See also

- `references/instagram.md` — Instagram messaging PSID + window details.
- The installed `aident-skill` (your harness's copy, when present) holds the full CLI reference; this skill records the Hermes-specific workflow and pitfalls.
