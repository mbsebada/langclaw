## 2024-03-01 - [Hardcoded Test Values in Production APIs]
**Vulnerability:** A hardcoded test phone number was left in the Zalo messaging route (`examples/rentagent_vn/api/routes/zalo.py`), overriding real user data.
**Learning:** Hardcoded test overrides must never be committed without conditional checks (like environment variables). This causes actual production outreach messages to be directed to the wrong recipients, violating data integrity and user expectations.
**Prevention:** Always use environment-driven test overrides (e.g., `ZALO_PHONE_OVERRIDE`) instead of hardcoding test data.
