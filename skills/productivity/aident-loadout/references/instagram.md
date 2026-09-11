# Instagram via Aident Loadout (composio:instagram_tools)

The Instagram connection works through the **Messenger for Instagram / Graph API** model — NOT the normal consumer Instagram app API. Messaging semantics are Facebook Messenger's. This matters for everything involving sending.

## Recipients are PSIDs, not usernames

`instagram_send_text_message` requires a `recipient_id` that is the recipient's **PSID** (Instagram-scoped user id, like `28514873514796725`), not a `@username`. Passing a username or a fabricated id fails HTTP 400 (code 100).

Resolve PSID from an existing conversation:
- `instagram_list_all_conversations` returns opaque conversation ids only (no participant names) — not directly useful for mapping a user to a conversation.
- `instagram_get_conversation {conversation_id}` resolves it: the response contains `messages[].from` and `messages[].to` each with `{id, username}`, plus thread participants. Grep for the target username, take its `id` as the PSID.
- `instagram_get_user_info` returns the *own* account's numeric `id` — use that as the caller's `ig_user_id`.

## The 24-hour messaging window (hard)

Instagram's Messenger API allows a business account to message a user ONLY inside a rolling 24-hour window measured from the user's LAST inbound message to the account. There is no cold-start DM:

- Sending to someone who has never messaged you, or whose last inbound message is > 24h old, fails **403 code 10, error_subcode 2534022: "This message is sent outside of allowed window."**
- The workflow for a requested DM therefore has one unavoidable requirement: get the recipient to message you first (within 24h), then send.
- "Reach out to X" for a stale thread will fail; tell the user the message cannot be delivered until X messages first, rather than retrying.

## Caller must supply its own IG id

Pass both `recipient_id` (their PSID) and `ig_user_id` (your business account's numeric id from `instagram_get_user_info`). Some tools also need `graph_api_version` (default `v21.0`).

## Read-only capability

Profile, media, stories, and insights reads work normally from the authenticated account (e.g. `instagram_get_user_info`, `instagram_get_ig_user_stories`, `instagram_get_ig_user_media`). Media listing may require the numeric `ig_user_id` as an argument.

## Distinguish wrapper success from delivery

The `aident capabilities execute` envelope returns `success:true` even when the Instagram API rejected the send (the 403 lives inside `output.data`, and `successful:false`/`error` appear in the nested payload). Always check the nested result before telling the user a message was delivered.
