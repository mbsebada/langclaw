## 2025-02-14 - Fix Missing Authentication on Zalo Microservice
**Vulnerability:** The internal Node.js Zalo microservice lacked API key authentication middleware, relying solely on network segmentation and CORS.
**Learning:** Internal microservices exposed to the local network are still vulnerable to SSRF (Server-Side Request Forgery) attacks or unauthorized direct access from other services on the same host if they lack their own authentication layer.
**Prevention:** Enforce API key authentication (or mutual TLS) on all internal microservices, using robust timing-safe comparison methods (like `crypto.timingSafeEqual`) to validate incoming requests even when proxied.
