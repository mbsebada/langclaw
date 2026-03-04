# PRD-02 — Zalo Integration

| Field | Value |
|---|---|
| Phase | 2 of 4 |
| Status | Draft |
| Owner | TBD |
| Last updated | March 2026 |
| Depends on | PRD-01 shipped and stable |

---

## Overview

Phase 1 delivers listings to the webapp. Phase 2 brings the experience into Zalo — the app Vietnamese renters already use every day. Users connect their Zalo account once, after which: new match notifications land in their Zalo, they can message landlords with one tap, and post-viewing feedback is collected via a quick Zalo message from the agent.

This phase makes RentAgent feel ambient rather than something you have to remember to open.

---

## Goals

- Deliver scan results to the user on Zalo so they see them without opening the webapp
- Let the agent send first-contact messages to landlords on the user's behalf via their own Zalo
- Collect post-viewing reactions via Zalo for signal quality and preference learning
- Keep the webapp as the hub — Zalo is a delivery and action layer, not a replacement for the pipeline view

---

## Assumptions

- Vietnamese landlords respond to Zalo messages significantly faster than to any other contact method — this is the primary reason Zalo outreach matters
- In Vietnam, a phone number IS a Zalo ID — the agent can message any landlord whose phone number is on the listing without needing a separate Zalo handle
- Users are comfortable connecting their personal Zalo account to a third-party app IF the purpose is clearly explained and limited in scope
- Landlords in Vietnam typically reply within hours, so automated follow-up messages are not needed — one initial message is sufficient
- The Zalo cookie session remains valid for a meaningful period (days to weeks) before requiring re-authentication

---

## User Stories

**Zalo connection**

- As a user, I want to connect my Zalo account so that I can receive notifications and send messages without leaving Zalo
- As a user, I want a clear explanation of exactly what the app will do with my Zalo access before I connect so that I can make an informed decision
- As a user, I want to know when my Zalo session expires and be prompted to reconnect so that the integration doesn't silently break

**Shortlist notifications**

- As a user, I want to receive a Zalo notification when the agent finds new matching listings so that I know to open the app without checking it manually
- As a user, I want the notification to include the number of new matches so that I can decide immediately how urgent it is

**Landlord outreach**

- As a user, I want to send a message to a landlord with one tap from the listing card so that I don't have to manually compose and send the same type of message over and over
- As a user, I want to see and optionally edit the draft message before it's sent so that I'm always in control of what goes out under my name
- As a user, I want to see on the listing card whether my message was sent, and whether the landlord replied so that I always know the status without opening Zalo

**Post-viewing feedback**

- As a user, I want to receive a Zalo message asking for my reaction after I've viewed a property so that giving feedback is frictionless and happens while the impression is fresh
- As a user, I want to respond to the feedback prompt with a single tap (👍 / 😐 / 👎) so that it takes less than 5 seconds

---

## Functional Requirements

### Zalo connection setup

1. The Zalo connection setup is accessible from both the onboarding flow (optional step) and a dedicated settings screen. It must be possible to skip during onboarding and connect later.
2. Before asking for any credentials, the app displays a plain-language explanation of exactly three things: (a) the app will send notifications to the user's Zalo, (b) the app will send messages to landlords on the user's behalf, (c) the app will not read the user's existing Zalo conversations.
3. The connection flow provides step-by-step instructions for retrieving the user's Zalo session cookie from their browser. Instructions must include visual cues (browser name, where to find cookies).
4. After the user submits their cookie, the app tests the connection by sending a confirmation message to the user's own Zalo number. The app does not proceed to "connected" state until this test succeeds.
5. The app displays the connected Zalo phone number once authenticated so the user can verify it's the right account.
6. The app displays an estimated session expiry date (where determinable) and sends a reminder 2 days before expiry.
7. The connection settings page shows the current connection status at all times: Connected / Expired / Not connected.

### Shortlist notifications

8. When a scan completes and finds at least one new match, the agent sends a Zalo message to the user's connected account. The message states the number of new matches and prompts the user to open the app.
9. If the scan finds zero new matches, no Zalo notification is sent.
10. If the user's Zalo connection is inactive (expired or not set up), the notification is silently skipped — no error is shown to the user for a missed notification.

### Landlord outreach

11. Every listing card that has a landlord phone number must display a "Liên hệ chủ nhà" button.
12. Tapping the button opens a modal showing a pre-drafted Vietnamese message. The message must sound like a genuine inquiry from a renter — not a template, not a bot. The user can edit the message before sending.
13. The modal has two actions: Send and Cancel. Tapping Send dispatches the message via the user's connected Zalo to the landlord's phone number.
14. If the user has no active Zalo connection, tapping the button shows an explanation and a link to the connection setup screen rather than a broken experience.
15. After a message is sent, the listing card shows the status "Đã liên hệ" and the listing moves to the Contacted stage in the pipeline automatically.
16. The listing card must show whether the landlord has replied (replied / no reply). This status does not need to surface the reply content — just the fact of a reply.
17. Each outreach message for a given campaign must use slightly varied phrasing so that multiple messages sent to different landlords do not appear identical.

### Post-viewing feedback

18. When the user moves a listing to the "Viewed" stage (either via the webapp or any other trigger), the agent sends a Zalo message to the user within 5 minutes asking for their reaction.
19. The Zalo feedback message includes the property address so the user knows which property the question refers to.
20. The feedback is captured via the webapp (three-tap buttons on the listing card), not by parsing Zalo replies. The Zalo message directs the user to open the app to respond.
21. If the user submits a "Không phù hợp" (negative) reaction in the webapp, an optional free-text notes field appears for them to explain why.

---

## Non-Functional Requirements

- The Zalo outreach modal must open within 1 second of tapping the button
- A sent Zalo message must be dispatched within 10 seconds of the user tapping "Gửi"
- The app must not store the user's Zalo cookie in plaintext anywhere — it must be encrypted at rest
- If Zalo sending fails (network error, session expired), the app must notify the user with a clear error message and offer a path to retry or reconnect — it must never silently fail
- The post-viewing Zalo prompt must be sent within 5 minutes of stage change, not in real time (small delay acceptable)

---

## Out of Scope for This Phase

- Reading or displaying incoming Zalo messages inside the webapp (the user reads replies in their own Zalo app)
- Automated follow-up messages if a landlord doesn't reply
- Sending listing photos or documents over Zalo
- Group Zalo messages or broadcast messages to multiple landlords at once
- Any Zalo features beyond: sending messages to a specific phone number

---

## Success Metrics

| Metric | Target |
|---|---|
| Zalo connection rate | >60% of active users connect Zalo within their first week |
| Notification open rate | >50% of Zalo scan notifications result in a webapp open within 2 hours |
| Outreach usage | >70% of listings moved to Contacted have an outreach message sent via the app |
| Post-viewing feedback rate | >60% of listings moved to Viewed have a feedback reaction submitted |
| Outreach send success rate | >98% of attempted sends succeed (excluding expired sessions) |

---

## Open Questions

1. **Reply detection:** How does the app know a landlord has replied? Does the Zalo bridge need to poll for incoming messages, or is this only detectable if the user manually marks it in the webapp?
2. **Cookie expiry:** How long do Zalo sessions typically last in practice? This determines how often users need to re-authenticate and how disruptive that is.
3. **Outreach on behalf of:** Should the message make clear it's coming from the user's own account (which it is), or should there be any disclosure that a tool helped draft it? Vietnamese norms and any applicable regulations should be checked.
4. **Auto-outreach opt-in:** Should users be able to enable fully automatic outreach (agent sends without showing a preview) for high-scoring listings? If yes, what score threshold and what cancel window?
