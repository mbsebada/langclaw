## 2024-04-12 - Missing Authentication on Node.js Service Endpoint
**Vulnerability:** The Zalo Node.js service exposed sensitive endpoints (`/auth/*` and `/message/*`) without any authentication requirements, allowing unauthorized internal or external access if improperly configured in production.
**Learning:** Microservices intended for internal communication must implement authentication (e.g., API keys) when deployed, even within a supposedly secure VPC or network.
**Prevention:** Implement API key authentication middleware using timing-safe comparisons (`crypto.timingSafeEqual`) for all sensitive routes across interconnected microservices.
