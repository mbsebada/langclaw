## 2024-06-05 - [CRITICAL] Fix missing authentication and hardcoded sensitive data
**Vulnerability:** The Zalo proxy endpoints lacked authentication, and a hardcoded sensitive phone number was embedded directly within the logic.
**Learning:** Hardcoded data such as API keys and test phone numbers within proxy services present security risks. Exposed integration proxy endpoints without authentication controls can result in arbitrary malicious requests.
**Prevention:** Incorporate token/API Key validation inside the middleware of integration-level components and utilize environment variables for configuration details and test-overrides.
