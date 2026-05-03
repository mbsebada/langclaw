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
const API_KEY = process.env.ZALO_SERVICE_API_KEY;

// Middleware — restrict CORS to localhost origins only
app.use(cors({ origin: [`http://localhost:${PORT}`, "http://localhost:3000", "http://127.0.0.1:3000"] }));
app.use(express.json({ limit: "10mb" }));

// Authentication middleware
app.use((req, res, next) => {
  // Always allow health checks
  if (req.path === "/health") {
    return next();
  }

  // If no API key is configured, warn but allow (for local dev fallback)
  if (!API_KEY) {
    console.warn("[SECURITY] ZALO_SERVICE_API_KEY is not set. Service is running without authentication!");
    return next();
  }

  const providedKey = req.headers["x-api-key"] || "";

  // Timing-safe comparison to prevent timing attacks
  const expectedBuf = Buffer.from(API_KEY);
  const providedBuf = Buffer.from(providedKey);

  if (providedBuf.length !== expectedBuf.length || !crypto.timingSafeEqual(expectedBuf, providedBuf)) {
    return res.status(401).json({ error: "Unauthorized" });
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
