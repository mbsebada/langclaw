## 2024-04-21 - Zalo Service Missing Authentication

**Vulnerability:** The Node.js Zalo proxy service (`examples/rentagent_vn/zalo-service/index.js`) had a CORS-only protection mechanism (`app.use(cors({ origin: [...] }))`) and completely lacked API key authentication for its core `/auth` and `/message` endpoints. While CORS protects against browser-based Cross-Site Request Forgery, it provides zero protection against direct server-to-server or cURL-based requests, leaving the service fully exposed.

**Learning:** CORS is a browser security feature, not an API authentication mechanism. Relying solely on CORS for an internal or external microservice leaves it completely vulnerable to direct access. Additionally, when implementing API key checks in Node.js, simple string comparison (`===`) is vulnerable to timing attacks.

**Prevention:** Always implement explicit API key (or equivalent) authentication middleware for all non-public endpoints. When comparing API keys in Node.js, use `crypto.timingSafeEqual` with `Buffer` objects, ensuring you check the byte lengths first (`expectedBuf.length !== providedBuf.length`) to prevent `timingSafeEqual` from throwing errors when lengths mismatch. Exempt only explicit public endpoints like `/health` by placing them before the authentication middleware.
