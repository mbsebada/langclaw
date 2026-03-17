## 2024-05-18 - Prevent Path Traversal in File Writes
**Vulnerability:** Arbitrary file write/path traversal in `examples/rentagent_vn/zalo-service/routes/auth.js` via the `/qr` endpoint accepting a user-controlled `qrPath` parameter.
**Learning:** Accepting paths for file writes from client requests directly without validation allows malicious actors to overwrite arbitrary files on the system or write to restricted directories (e.g. `../` or `/etc/`).
**Prevention:** Hardcode paths to files where dynamic paths aren't strictly necessary. If a dynamic path is required, thoroughly sanitize user input.
