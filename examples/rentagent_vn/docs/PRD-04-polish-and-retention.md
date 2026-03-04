# PRD-04 — Polish & Retention

| Field | Value |
|---|---|
| Phase | 4 of 4 |
| Status | Draft |
| Owner | TBD |
| Last updated | March 2026 |
| Depends on | PRD-01, PRD-02, PRD-03 shipped and stable |

---

## Overview

A rental search in Vietnam lasts 4–8 weeks. Phase 4 addresses what happens in the middle and end of that journey: decision fatigue, preference drift, and the need to make a final call. This phase adds insights that help users make decisions, alerts when a listing they cared about gets cheaper, makes preference editing easy, and hardens the Vietnamese language handling so edge cases don't confuse the agent. Nothing structurally new — everything here improves what already exists.

---

## Goals

- Help users make faster decisions by surfacing what they've learned about their own preferences over the course of the campaign
- Reduce the chance a user misses a good deal because a listing they liked dropped in price
- Make it easy to update preferences mid-campaign without starting over
- Eliminate the most common cases where the agent misunderstands Vietnamese rental queries

---

## Assumptions

- Users in week 4 of a campaign have different needs than users in week 1 — they have more data and need help synthesizing it, not more listings
- Price drops on listings a user was interested in are high-signal events worth interrupting them for
- Users' stated preferences at campaign start often don't perfectly capture what they respond to — they should be able to adjust without restarting
- The most common NLP failures are abbreviations and shorthand (PN, Q3, ĐĐNT, 8tr) that are obvious to Vietnamese renters but ambiguous to a general-purpose language model

---

## User Stories

**Campaign insights**

- As a user who has been searching for 3+ weeks, I want to see a summary of what I've learned so far so that I can make progress toward a decision rather than searching indefinitely
- As a user, I want the summary to include a concrete recommendation (e.g., "your top candidate is still X") so that I have something actionable to act on
- As a user, I want the insight to surface patterns I might not have noticed myself (e.g., "you consistently skip listings in alleys") so that I can consciously decide whether to update my search area

**Price drop alerts**

- As a user who viewed or shortlisted a listing, I want to be notified if the asking price drops so that I don't miss a deal on a property I was already interested in
- As a user, I want the price drop alert to tell me the old price and the new price so that I can immediately assess whether it changes my interest
- As a user, I want to be notified about price drops via Zalo (if connected) so that I see it without opening the app

**Preference editing**

- As a user, I want to update my search preferences at any point in the campaign without starting a new campaign so that I don't lose my pipeline history when my priorities shift
- As a user, I want to see a preview of how my updated preferences would affect my current listing pool before I save changes so that I can avoid accidentally filtering out listings I care about
- As a user, I want my learned preferences (from feedback signals) to survive a manual preference update so that the agent doesn't lose what it has learned

**Vietnamese language robustness**

- As a user, I want to be able to use common Vietnamese rental abbreviations (PN, Q3, ĐĐNT, etc.) in my initial description and have the agent correctly interpret them so that I don't have to write everything out in full
- As a user, I want the agent to correctly handle shorthand prices ("8tr", "8.5 triệu", "dưới 10tr") without asking me to clarify so that setup feels fast and natural

**Error and degradation states**

- As a user, I want to know when the app is having trouble (disconnected, scan failed, Zalo expired) via a clear, non-alarming message so that I understand what's happening and know what to do
- As a user, I want scan failures to be retried automatically without me having to do anything so that one bad network moment doesn't break my daily updates

---

## Functional Requirements

### Campaign insights

1. The app generates a campaign insight summary once per day, after the daily scan completes, and displays it at the top of the pipeline view.
2. The insight is also available on demand — the user can tap a "Tóm tắt chiến dịch" option from the campaign menu to generate it immediately.
3. The insight must be written in plain, conversational Vietnamese. Maximum 3 sentences.
4. The insight must include at least two of the following data points: days the campaign has been active, number of properties viewed, top-rated current candidate (if any), most common skip reason (if skip count ≥ 3), most productive source group.
5. If the campaign has been active for more than 21 days and has no listings in "Shortlisted" stage, the insight should gently surface this and suggest a concrete action (e.g., revisiting the top-viewed listing or broadening the area).
6. The insight banner is dismissible per session and does not reappear until a new insight is generated.

### Price drop alerts

7. When a listing that the user has NOT rejected reappears in a scan with a price lower than previously recorded, and the price difference is at least 300,000 VND, the app treats this as a price drop event.
8. Price drops on listings in the "Viewed" or "Shortlisted" stages trigger a Zalo notification (if the user's Zalo is connected). Listings in earlier stages update their card silently.
9. The Zalo price drop notification includes: the property address, the old price, and the new price. It does not require any action — it is informational only.
10. The listing card must visually indicate that a price has dropped: show both the new price (prominent) and the old price (struck through or noted as "giảm từ Xtr").
11. A price drop notification is only sent once per listing per price change event — not re-sent on every subsequent scan.

### Preference editing

12. The Preferences screen allows the user to edit all fields from their original setup: areas, budget range, number of bedrooms, and requirements.
13. As the user edits any field, the app shows a live preview below the form: "Với tiêu chí mới: X phòng hiện tại vẫn phù hợp, Y phòng sẽ không còn khớp." This preview updates within 1 second of each change (debounced).
14. Saving preference changes does not reset or modify the learned preference weights from feedback signals.
15. The user cannot save preferences that would result in zero listings remaining in their current pipeline without an explicit confirmation warning: "Thay đổi này sẽ loại bỏ tất cả phòng hiện tại. Bạn có chắc không?"
16. The Preferences screen displays a read-only summary of what the agent has learned, separate from the editable fields. This section has its own "Đặt lại" (reset) button that only resets learned weights, not the declared preferences.

### Vietnamese language robustness

17. The agent must correctly interpret the following abbreviations and shorthand without asking for clarification:
    - District abbreviations: Q1–Q12, BT (Bình Thạnh), PN (Phú Nhuận), TB (Tân Bình), BC (Bình Chánh), CG (Cầu Giấy), DD or ĐĐ (Đống Đa)
    - Room types: 1PN, 2PN (phòng ngủ), CAMA (chung cư mini), NT (nội thất), ĐĐNT or ĐĐ NT (đầy đủ nội thất)
    - Price formats: Xtr, X.5tr, X-Ytr, dưới Xtr, khoảng Xtr, từ X đến Y triệu
    - Requirements: WC riêng, để xe / bãi xe, ban công / BC, TM (thang máy), thú cưng / pet, yên tĩnh / yên
18. If the agent extracts an abbreviation it is not confident about, it must show both its interpretation and the original text in the confirmation chips, rather than silently substituting the full form.
19. When a description contains a price range with conditions (e.g., "6tr không nội thất hoặc 8tr có nội thất"), the agent must take the higher budget as budget_max and add the relevant condition as a requirement — not ask for clarification.

### Error states and resilience

20. The webapp must display a non-alarming status banner in the following states:
    - WebSocket disconnected for more than 10 seconds: "Mất kết nối. Đang thử lại..."
    - Last scan failed: "Lần quét trước gặp lỗi. [Thử lại ngay]"
    - Zalo session expired: "Kết nối Zalo hết hạn. [Kết nối lại]"
21. Failed scans must be automatically retried once, 15 minutes after the failure, without user action.
22. If a scan fails twice in a row, the user receives a Zalo notification (if connected) or an in-app notification prompting them to check the app.
23. All error messages must be in Vietnamese and written in a calm, matter-of-fact tone — no exclamation marks, no alarming language.

---

## Non-Functional Requirements

- Preference editing preview must respond within 1 second of a field change
- Campaign insight generation must complete within 10 seconds of being triggered
- Price drop detection must happen within the same scan that finds the updated listing — not in a separate background job
- The app must recover from a WebSocket disconnect and reconnect automatically without the user losing any unsaved state

---

## Out of Scope for This Phase

- Multiple campaigns (still single campaign per user)
- User accounts, authentication, or multi-device sync
- Exporting the campaign history or listing data
- Any features related to post-signing (lease review, move-in checklist, etc.)
- Automated negotiation with landlords

---

## Success Metrics

| Metric | Target |
|---|---|
| Campaign completion rate | >40% of campaigns that reach week 3 result in a listing moved to "Shortlisted" |
| Insight engagement | >50% of users who receive a campaign insight do not dismiss it immediately (dwell time >5 seconds) |
| Price drop notification tap rate | >60% of Zalo price drop notifications result in the user opening the app within 4 hours |
| Preference edit rate | >25% of campaigns that run for 2+ weeks have at least one preference update |
| NLP clarification rate | <5% of setup inputs require the agent to ask a follow-up question due to unrecognized abbreviations |
| Scan retry success | >80% of failed scans succeed on the automatic retry |

---

## Open Questions

1. **Insight timing:** Should insights be generated immediately after a scan (potentially during the user's morning routine) or at a fixed time like 8pm? Timing affects how useful the insight feels.
2. **Price drop threshold:** 300,000 VND was chosen arbitrarily. Is this the right threshold? A 500,000 drop on a 5M listing (10%) feels different from a 300,000 drop on a 10M listing (3%). Should the threshold be percentage-based?
3. **Preference edit history:** Should the app keep a history of preference changes so the user can see what they changed and when? Useful for reflection, adds complexity.
4. **Insight tone:** If the campaign has been running 30 days with no progress, how direct should the insight be? "Bạn đã tìm 30 ngày chưa chốt được phòng nào" could feel discouraging — but sugarcoating it isn't helpful either.
5. **Abbreviation coverage:** The list of recognized abbreviations in requirement 17 covers HCM City and Hanoi districts. Hanoi has different district names (Hoàn Kiếm, Ba Đình, Hoàng Mai, etc.). Is a Hanoi-specific abbreviation list needed or can it be deferred?
