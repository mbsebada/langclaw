## 2024-03-19 - Removed hardcoded test phone number from Zalo integration

**Vulnerability:** A hardcoded testing phone number was accidentally left in the production route for sending Zalo messages, causing all outreach messages to be sent to that number instead of the landlord's phone number.
**Learning:** Hardcoded overrides for testing can easily slip into production code if not properly conditionalized using environment variables or configuration flags.
**Prevention:** Use environment variables (like `ZALO_PHONE_OVERRIDE`) for temporary overrides and ensure that defaults always fall back to the actual data values rather than fixed strings. Avoid putting `TODO: remove` comments in critical code paths without tracking them in an issue tracker before deployment.
