## 2024-05-24 - Missing Authentication in Zalo Proxy Service
**Vulnerability:** The Node.js Zalo integration service lacked any authentication mechanisms, allowing unauthenticated internal or external access to sensitive messaging endpoints.
**Learning:** Integration services or sidecars running locally or on internal networks often omit authentication under the false assumption that network boundaries provide sufficient security.
**Prevention:** Always implement service-to-service authentication (e.g., using API keys and `crypto.timingSafeEqual`) on all microservices and proxy endpoints, adhering to zero-trust principles regardless of network topology.

## 2024-05-24 - Variable Scope and Refactoring Regressions
**Vulnerability:** Hardcoded target phones are problematic, but replacing them with fallback variables requires matching variable scopes. Replacing `phone = "hardcode"` with `target_phone = os.environ.get("OVERRIDE", phone)` introduced a `NameError` because `phone` wasn't defined.
**Learning:** Refactoring hardcoded values into environment variables must be done carefully to avoid breaking code logic, specifically concerning variable scope limits.
**Prevention:** Always review the exact line being changed and ensure that any variable references are either declared in scope or properly passed as arguments before making refactoring changes.
