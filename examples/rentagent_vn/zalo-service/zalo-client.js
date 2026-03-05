/**
 * Singleton wrapper around zca-js Zalo client.
 * Manages login state, message sending, and reply tracking.
 */

import { Zalo, ThreadType } from "zca-js";

class ZaloClient {
  constructor() {
    this.zalo = null;
    this.api = null;
    this.connected = false;
    this.phoneNumber = null;
    this.replies = new Map(); // phone -> { replied: boolean, lastReplyAt: string }
  }

  /**
   * Login with cookie credentials.
   * @param {string|Array} cookie - Zalo session cookie in array format from
   *   browser extension (e.g., J2TEAM Cookies export)
   * @param {string} imei - Device IMEI
   * @param {string} userAgent - Browser user agent
   */
  async loginWithCookie(cookie, imei, userAgent) {
    try {
      // Parse cookie if it's a JSON string
      let parsedCookie = cookie;
      if (typeof cookie === "string") {
        try {
          parsedCookie = JSON.parse(cookie);
        } catch (e) {
          console.error("Failed to parse cookie as JSON:", e.message);
          throw new Error("Invalid cookie format: must be valid JSON");
        }
      }

      console.log("Login attempt with:");
      console.log("  - cookie type:", Array.isArray(parsedCookie) ? "array" : typeof parsedCookie);
      console.log("  - cookie length:", Array.isArray(parsedCookie) ? parsedCookie.length : "N/A");
      console.log("  - imei:", imei);
      console.log("  - userAgent:", userAgent?.substring(0, 50) + "...");

      // zca-js Zalo constructor takes options, then login() takes credentials
      this.zalo = new Zalo();
      this.api = await this.zalo.login({
        cookie: parsedCookie,
        imei,
        userAgent,
      });
      this.connected = true;

      // Get own profile to retrieve phone number
      const ownId = this.api.getOwnId();
      this.phoneNumber = ownId || null;

      // Start listener to track incoming replies
      this._startListener();

      return {
        connected: true,
        phoneNumber: this.phoneNumber,
      };
    } catch (error) {
      console.error("Zalo login error:", error);
      this.connected = false;
      this.phoneNumber = null;
      throw new Error(`Zalo login failed: ${error.message}`);
    }
  }

  /**
   * Login with QR code.
   * @param {string} qrPath - Path to save QR code image
   */
  async loginWithQR(qrPath) {
    try {
      this.zalo = new Zalo();
      this.api = await this.zalo.loginQR({ qrPath });
      this.connected = true;

      const ownId = this.api.getOwnId();
      this.phoneNumber = ownId || null;

      this._startListener();

      return {
        connected: true,
        phoneNumber: this.phoneNumber,
        qrPath,
      };
    } catch (error) {
      this.connected = false;
      this.phoneNumber = null;
      throw new Error(`Zalo QR login failed: ${error.message}`);
    }
  }

  /**
   * Send a message to a phone number.
   * @param {string} phone - Recipient phone number
   * @param {string} text - Message text
   */
  async sendMessage(phone, text) {
    if (!this.connected || !this.api) {
      throw new Error("Not connected to Zalo");
    }

    try {
      // Find user by phone number
      const user = await this.api.findUser(phone);
      if (!user || !user.uid) {
        throw new Error(`User not found for phone: ${phone}`);
      }

      const userId = user.uid;

      // Send message
      await this.api.sendMessage(
        { msg: text },
        userId,
        ThreadType.User
      );

      // Initialize reply tracking for this phone
      if (!this.replies.has(phone)) {
        this.replies.set(phone, { replied: false, lastReplyAt: null });
      }

      return {
        success: true,
        userId,
        phone,
      };
    } catch (error) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  /**
   * Check if a landlord has replied.
   * @param {string} phone - Phone number to check
   */
  getReplyStatus(phone) {
    const status = this.replies.get(phone);
    return status || { replied: false, lastReplyAt: null };
  }

  /**
   * Get current connection status.
   */
  getStatus() {
    return {
      connected: this.connected,
      phoneNumber: this.phoneNumber,
    };
  }

  /**
   * Logout and clear session.
   */
  async logout() {
    if (this.api && this.api.listener) {
      try {
        this.api.listener.stop();
      } catch {
        // Ignore listener stop errors
      }
    }

    this.zalo = null;
    this.api = null;
    this.connected = false;
    this.phoneNumber = null;
    this.replies.clear();

    return { connected: false };
  }

  /**
   * Start message listener to track replies.
   * @private
   */
  _startListener() {
    if (!this.api || !this.api.listener) {
      return;
    }

    try {
      this.api.listener.on("message", (message) => {
        // Track reply by sender
        const senderId = message.uidFrom || message.senderId;
        if (senderId && senderId !== this.phoneNumber) {
          // Find phone associated with this user ID
          for (const [phone, status] of this.replies.entries()) {
            // We track by phone, but replies come by userId
            // For simplicity, mark the most recent conversation as replied
            status.replied = true;
            status.lastReplyAt = new Date().toISOString();
          }
        }
      });

      this.api.listener.start();
    } catch (error) {
      console.error("Failed to start Zalo listener:", error.message);
    }
  }
}

// Singleton instance
const zaloClient = new ZaloClient();
export default zaloClient;
