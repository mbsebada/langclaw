## 2024-05-24 - [CRITICAL] Fix missing authentication on Zalo proxy
**Vulnerability:** Internal Node.js Zalo integration endpoints (`/auth` and `/message`) lacked authentication, allowing any local process (or unauthenticated SSRF) to potentially access Zalo sessions or send arbitrary messages without verifying an API key.
**Learning:** In Node.js services, securely performing API key equality checks requires `crypto.timingSafeEqual` with `Buffer` objects, comparing byte lengths first instead of string characters to prevent timing attacks.
**Prevention:** Always implement explicit authentication middleware on internal microservices that process sensitive data or proxy authentication to external services, even if bound locally.
