## 2026-04-24 - [Zalo Service Missing Authentication]
**Vulnerability:** The Zalo microservice in `examples/rentagent_vn/zalo-service` exposed sensitive routes (e.g., sending messages) without any authentication, meaning anyone accessing `localhost:8001` or any exposed port could send unauthorized messages.
**Learning:** Internal microservices, even if intended only for proxying from a main backend, still require defense-in-depth authentication mechanisms to prevent SSRF or internal network exploitation.
**Prevention:** Always require API keys (`crypto.timingSafeEqual`) on internal service-to-service communication paths, passing them securely in headers like `x-api-key`.
