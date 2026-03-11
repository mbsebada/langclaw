## 2023-10-27 - Restrict Overly Permissive CORS Configuration
**Vulnerability:** The RentAgent VN FastAPI backend had a wildcard CORS configuration (`allow_methods=["*"]` and `allow_headers=["*"]`).
**Learning:** Default examples often use wildcard configurations for simplicity during development, but this introduces risks in production by allowing any method or header from allowed origins.
**Prevention:** Always restrict CORS policies to the minimum set of methods (`GET`, `POST`, `PATCH`, `OPTIONS` in this case) and headers (`Content-Type`, `Authorization`, `Accept`) required by the application's actual routes and frontend needs.
