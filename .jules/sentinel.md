## 2024-03-30 - [CRITICAL] Fix Hardcoded Phone Number in Zalo Outreach
**Vulnerability:** A hardcoded phone number ("0334663383") was used in the `send_outreach_message` endpoint, overriding the intended recipient's phone number.
**Learning:** Hardcoding sensitive or specific PII like phone numbers for testing directly in the source code can lead to unintended message routing and potential privacy breaches in production environments.
**Prevention:** Use environment variables (e.g., `ZALO_PHONE_OVERRIDE`) for test routing instead of hardcoding values directly in the application logic.
