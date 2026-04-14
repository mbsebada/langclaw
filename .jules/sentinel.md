# Sentinel Journal

## 2025-04-14 - Fix Hardcoded Zalo Phone Number
**Vulnerability:** Hardcoded override phone number in Zalo integration.
**Learning:** Even in test or example code, hardcoding specific user phone numbers exposes PII and causes accidental messages to be sent. Overrides should be managed via environment variables.
**Prevention:** Rely on environment variables like `ZALO_PHONE_OVERRIDE` to inject test identifiers instead of committing them.
