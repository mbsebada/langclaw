## 2024-05-24 - Missing Authentication on Node.js Services Exposed via Proxy
**Vulnerability:** The Zalo internal Node.js service was unauthenticated, meaning any internal component or misconfigured proxy could execute arbitrary actions on behalf of the connected user, or a direct request to the service port could bypass API Gateway protections.
**Learning:** Internal services that handle sensitive integrations (like sending messages via an authenticated session) must implement their own authentication checks, rather than blindly trusting the internal network. Additionally, API key comparison in Node.js must be done via `crypto.timingSafeEqual` over buffers to prevent timing side-channels, and length checks must be performed explicitly to avoid exceptions when comparing unequal length buffers.
**Prevention:**
1. Always implement defense-in-depth by requiring an internal `x-api-key` header on internal microservices.
2. When comparing keys in Node.js, always use:
```javascript
const expectedBuf = Buffer.from(expectedApiKey);
const providedBuf = Buffer.from(providedApiKey);
if (expectedBuf.length !== providedBuf.length || !crypto.timingSafeEqual(expectedBuf, providedBuf)) {
  // reject
}
```
3. Ensure middleware fails securely (returning HTTP 500) if the required API key configuration is missing at startup or during execution.
