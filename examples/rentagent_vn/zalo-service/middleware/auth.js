/**
 * Authentication middleware for Zalo service.
 * Verifies API key from x-api-key header.
 */

import crypto from "crypto";

const expectedKey = process.env.ZALO_SERVICE_API_KEY || "dev-secret-key";
const expectedBuf = Buffer.from(expectedKey);

export function apiKeyAuth(req, res, next) {
  const providedKey = req.headers["x-api-key"] || "";
  const providedBuf = Buffer.from(providedKey);

  // Time-safe equality check to prevent timing attacks.
  // Must check length first to avoid crypto error with different buffer sizes.
  if (
    providedBuf.length !== expectedBuf.length ||
    !crypto.timingSafeEqual(providedBuf, expectedBuf)
  ) {
    return res.status(401).json({
      error: "Unauthorized",
      code: "INVALID_API_KEY",
    });
  }

  next();
}
