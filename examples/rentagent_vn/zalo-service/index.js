/**
 * Zalo Service — Express wrapper around zca-js.
 * Provides REST endpoints for Zalo authentication and messaging.
 */

import express from "express";
import cors from "cors";
import crypto from "crypto";
import authRouter from "./routes/auth.js";
import messageRouter from "./routes/message.js";

const app = express();
const PORT = process.env.ZALO_SERVICE_PORT || 8001;

// Middleware — restrict CORS to localhost origins only
app.use(cors({ origin: [`http://localhost:${PORT}`, "http://localhost:3000", "http://127.0.0.1:3000"] }));
app.use(express.json({ limit: "10mb" }));

// Security: Require API key for all endpoints
const API_KEY = process.env.ZALO_SERVICE_API_KEY || "dev-zalo-key-123";

app.use((req, res, next) => {
  const apiKeyHeader = req.headers["x-api-key"];

  if (!apiKeyHeader) {
    return res.status(401).json({ error: "Unauthorized: Missing API Key" });
  }

  const expectedBuf = Buffer.from(API_KEY, "utf8");
  const providedBuf = Buffer.from(apiKeyHeader, "utf8");

  // Prevent timing attacks by using timingSafeEqual
  // Must check length first to avoid thrown error by timingSafeEqual if lengths differ
  if (expectedBuf.length !== providedBuf.length || !crypto.timingSafeEqual(expectedBuf, providedBuf)) {
    return res.status(401).json({ error: "Unauthorized: Invalid API Key" });
  }

  next();
});

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "zalo-service" });
});

// Routes
app.use("/auth", authRouter);
app.use("/message", messageRouter);

// Error handling middleware — don't leak internal details to clients
app.use((err, req, res, next) => {
  console.error(`[Zalo Service Error] ${err.message}`);
  res.status(500).json({
    error: "Internal server error",
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: "Not found" });
});

// Start server
app.listen(PORT, () => {
  console.log(`Zalo service listening on http://localhost:${PORT}`);
});
