## 2024-10-27 - [Hardcoded PII in Outreach Messages]
**Vulnerability:** A hardcoded phone number ("0334663383") was being used in `examples/rentagent_vn/api/routes/zalo.py` to send all Zalo outreach messages, overriding the actual landlord's phone number.
**Learning:** This exposes a specific test phone number and prevents the core functionality of contacting actual landlords from working. It represents a common pattern where development shortcuts (hardcoded values for testing) are accidentally left in the codebase.
**Prevention:** Avoid hardcoding specific identifiers, especially PII or test credentials, directly in code. Always use environment variables for overrides during testing or development (e.g., `ZALO_PHONE_OVERRIDE`).
