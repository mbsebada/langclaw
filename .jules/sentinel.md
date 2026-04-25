## 2025-04-25 - [CRITICAL] Missing Authentication on Node.js Service
**Vulnerability:** The Zalo Node.js service endpoints (`/auth` and `/message`) were exposed without any authentication, allowing unauthorized access to trigger actions and send messages.
**Learning:** Internal microservices (like the Zalo service wrapped for the Python API) must have their own authentication layer, even if they are "internal" endpoints intended only for the proxy, because they are bound to a port and can be reached directly.
**Prevention:** Implement API key or token-based authentication via middleware for all non-health endpoints on internal services, and verify that the calling proxy passes the expected credentials.
