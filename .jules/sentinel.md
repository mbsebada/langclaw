## 2024-05-24 - Missing Authentication on Zalo Proxy
**Vulnerability:** The proxy endpoints in `examples/rentagent_vn/api/routes/zalo.py` were not providing the required `x-api-key` header when forwarding requests to the Zalo Node.js service. This left the integration broken and potentially insecure if the backend relied entirely on proxy authentication for access control.
**Learning:** Always verify that backend service integrations correctly implement their designated authentication mechanisms (like API keys) to prevent unauthorized access and ensure end-to-end security between microservices.
**Prevention:** Ensure integration layers explicitly retrieve and pass configured credentials (e.g., via environment variables) when communicating with external or internal authenticated services.
