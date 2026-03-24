## 2024-05-18 - [CRITICAL] Fix missing authentication on Zalo microservice
**Vulnerability:** The Zalo Node.js service exposed sensitive messaging and authentication endpoints without any API key or token verification, allowing any internal process to hijack the connection.
**Learning:** Internal microservices (like the Zalo Node.js service) must enforce authentication (e.g., via API keys) to prevent unauthorized access even if bound to localhost, ensuring defense in depth.
**Prevention:** Require API keys via environment variables for all internal service communication.
