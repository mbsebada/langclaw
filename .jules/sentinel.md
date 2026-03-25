## 2025-03-12 - Hardcoded Override Bypassing Business Logic
**Vulnerability:** A hardcoded phone number in the Zalo messaging integration (`examples/rentagent_vn/api/routes/zalo.py`) bypassed the logic to send to the listing's actual `landlord_phone`.
**Learning:** Hardcoded overrides intended for testing, if left in code, can lead to real user data/messages being misdirected to unexpected or unauthorized parties. Environmental configurations should be used for test overrides rather than hardcoded logic.
**Prevention:** Use environment variables (like `ZALO_PHONE_OVERRIDE`) for testing overrides. Ensure test code or debug code is properly guarded or removed before production.
