## 2025-02-13 - [Hardcoded PII and Missing Auth in Zalo Integration]
**Vulnerability:** A hardcoded phone number ("0334663383") was present in the `send_outreach_message` endpoint, leaking PII and hardcoding logic. In addition, the `_proxy_to_zalo` helper was missing the `x-api-key` header to authenticate properly with the external Zalo Node.js service.
**Learning:** Development test values or missing headers for internal microservices can accidentally make it to production, leading to unauthorized service access or misrouting of sensitive outreach messages.
**Prevention:** Rely on environment variable overrides like `ZALO_PHONE_OVERRIDE` to switch logic for testing, avoiding hardcoded PII. In proxy services, verify authentication mechanisms (like API keys) are passed uniformly.
