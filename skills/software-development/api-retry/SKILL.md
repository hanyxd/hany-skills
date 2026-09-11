---
name: api-retry
version: 1.0.0
description: API error? Retry up to 10 times with exponential backoff.
---

# API Retry Skill

When an API request errors with a transient failure, retry it up to **10 times** instead of reporting failure immediately. This mirrors Claude's built-in resilience behavior.

## When to retry

Retry on transient errors:
- HTTP 408, 429 (rate limit), 500, 502, 503, 504
- Connection / timeout / socket errors
- Network hiccups
- Empty or truncated responses the server could have produced

Do NOT retry (permanent, will never succeed):
- 400, 401, 403, 404, 409, 422
- Auth/credential errors
- Malformed request payloads
- Validation failures

## Rules

1. Use **exponential backoff**: start at ~1s, double each attempt (1, 2, 4, 8 ... up to ~60s cap). Add small jitter to avoid thundering-herd retries.
2. Cap retries at **10** total attempts (default: 10 total, made explicit).
3. Log each attempt number + error so you can see progress.
4. After attempt 10 fails, STOP and report the error clearly to the user — do not loop forever.
5. For rate limits (429): if the response gives a `Retry-After` header, honor it instead of your backoff.
6. Keep the retry only around the failing call, not the whole program (unless the whole sequence is idempotent).
7. Only retry idempotent operations (GET, or POST you are sure didn't commit) — never blindly retry a POST that may have side effects.

## Reusable snippet (Python)

```python
import time, random

def call_with_retry(fn, attempts=10, base=1.0, cap=60.0):
    for i in range(1, attempts + 1):
        try:
            return fn()
        except Exception as e:
            if i == attempts:
                raise  # all retries exhausted
            delay = min(cap, base * (2 ** (i - 1))) + random.uniform(0, 0.5)
            print(f"attempt {i}/{attempts} failed ({e}); retrying in {delay:.1f}s")
            time.sleep(delay)
```

## Pitfalls

- Retrying a permanent 4xx wastes time and can lock an account / burn quota — check status code first.
- No backoff = your retries pile up and fail together. Always backoff.
- Retrying non-idempotent writes (unhandled POST/PUT/DELETE) can double-commit. Guard with an idempotency key if the API supports one.
- Infinite retry loops are worse than failure — the 10-attempt cap is the safety valve.
