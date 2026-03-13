## 2025-02-17 - Hardcoded Phone Number Removal
**Vulnerability:** Hardcoded phone number `0334663383` in the Zalo API route, which could inadvertently route messages to the wrong person in production or leak PII.
**Learning:** Temporary test overrides shouldn't be hardcoded into the source file. Instead, use an environment variable (like `ZALO_PHONE_OVERRIDE`).
**Prevention:** Check for inline `TODO: remove hardcode` comments and use `os.environ` variables for debugging.
