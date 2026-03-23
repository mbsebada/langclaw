## 2024-05-20 - Unauthenticated Internal Microservice Endpoints
**Vulnerability:** Internal microservices (like the Zalo Node.js service) lacked authentication on sensitive endpoints (e.g. sending messages, logging in/out). While they might be meant to only be called by the proxy, without a firewall or explicit binding, they are exposed to the local network or anyone who can hit the port.
**Learning:** Even internal helper services need authentication when handling sensitive actions or PII. We cannot assume that only our proxy will ever call them.
**Prevention:** Always implement basic authentication (like a shared API key header, `x-api-key`) on internal microservices to restrict access.
