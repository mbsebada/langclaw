## 2025-02-28 - [Add API Key Auth to Node Proxy]
**Vulnerability:** Missing Authentication / Missing PII Sanitization
**Learning:** The Express/Node wrapper service exposed internal endpoints without API key validation. Furthermore, proxy routes had hardcoded a personal phone number, risking data leakage and accidental notifications to the wrong target.
**Prevention:** Implement `x-api-key` header validation using `crypto.timingSafeEqual` for all endpoints excluding `/health`, configure Python proxies to transmit this key, and parameterize identifiers rather than hardcoding.
