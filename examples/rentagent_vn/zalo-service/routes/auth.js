/**
 * Zalo authentication routes.
 */

import { Router } from "express";
import zaloClient from "../zalo-client.js";

const router = Router();

/**
 * POST /auth/cookie
 * Login with cookie credentials.
 */
router.post("/cookie", async (req, res, next) => {
  try {
    const { cookie, imei, userAgent } = req.body;

    if (!cookie || !imei || !userAgent) {
      return res.status(400).json({
        error: "Missing required fields: cookie, imei, userAgent",
      });
    }

    const result = await zaloClient.loginWithCookie(cookie, imei, userAgent);
    res.json(result);
  } catch (error) {
    next(error);
  }
});

/**
 * POST /auth/qr
 * Generate QR code for login.
 */
router.post("/qr", async (req, res, next) => {
  try {
    const qrPath = req.body.qrPath || "./qr.png";
    const result = await zaloClient.loginWithQR(qrPath);
    res.json(result);
  } catch (error) {
    next(error);
  }
});

/**
 * GET /auth/status
 * Get current connection status.
 */
router.get("/status", (req, res) => {
  const status = zaloClient.getStatus();
  res.json(status);
});

/**
 * POST /auth/logout
 * Disconnect and clear session.
 */
router.post("/logout", async (req, res, next) => {
  try {
    const result = await zaloClient.logout();
    res.json(result);
  } catch (error) {
    next(error);
  }
});

export default router;
