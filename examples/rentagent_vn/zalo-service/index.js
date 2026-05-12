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
const EXPECTED_API_KEY = process.env.ZALO_SERVICE_API_KEY || "zalo-dev-key";

// Middleware — restrict CORS to localhost origins only
app.use(cors({ origin: [`http://localhost:${PORT}`, "http://localhost:3000", "http://127.0.0.1:3000"] }));
app.use(express.json({ limit: "10mb" }));

// API Key Authentication Middleware
app.use((req, res, next) => {
  // Exempt health check from authentication
  if (req.path === "/health") {
    return next();
  }

  const providedKey = req.headers["x-api-key"];

  if (!providedKey) {
    return res.status(401).json({ error: "Unauthorized: Missing API key" });
  }

  try {
    const expectedBuf = Buffer.from(EXPECTED_API_KEY);
    const providedBuf = Buffer.from(providedKey);

    if (expectedBuf.length !== providedBuf.length || !crypto.timingSafeEqual(expectedBuf, providedBuf)) {
      return res.status(401).json({ error: "Unauthorized: Invalid API key" });
    }
  } catch (error) {
    // Catch potential errors like providedKey not being a valid string for Buffer
    return res.status(401).json({ error: "Unauthorized: Invalid API key format" });
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
