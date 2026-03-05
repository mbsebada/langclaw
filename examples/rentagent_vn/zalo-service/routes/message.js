/**
 * Zalo message routes.
 */

import { Router } from "express";
import zaloClient from "../zalo-client.js";

const router = Router();

/**
 * POST /message/send
 * Send a message to a phone number.
 */
router.post("/send", async (req, res, next) => {
  try {
    const { phone, text } = req.body;

    if (!phone || !text) {
      return res.status(400).json({
        error: "Missing required fields: phone, text",
      });
    }

    const result = await zaloClient.sendMessage(phone, text);
    res.json(result);
  } catch (error) {
    next(error);
  }
});

/**
 * GET /message/status/:phone
 * Check if a landlord has replied.
 */
router.get("/status/:phone", (req, res) => {
  const { phone } = req.params;
  const status = zaloClient.getReplyStatus(phone);
  res.json(status);
});

export default router;
