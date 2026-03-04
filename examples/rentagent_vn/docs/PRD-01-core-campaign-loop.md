# PRD-01 — Core Campaign Loop

| Field | Value |
|---|---|
| Phase | 1 of 4 |
| Status | Draft |
| Owner | TBD |
| Last updated | March 2026 |

---

## Overview

This phase delivers the minimum viable version of RentAgent: a user can describe what they want to rent, add their Facebook group sources, and the agent will scan those groups daily and surface matching listings in a pipeline view. No Zalo, no neighborhood research — just a working scan loop that saves users from manually checking groups every day.

---

## Goals

- Let a user configure a rental search campaign in under 3 minutes using plain Vietnamese
- Have the agent autonomously scan configured Facebook groups and deliver matched listings without the user doing anything
- Give the user a clear, scannable view of all listings found and where they stand in the process
- Ensure users never see the same listing twice

---

## Assumptions

- Users already know which Facebook rental groups are active in their target area — they don't need the app to discover groups for them
- A Vietnamese-language chatbox is sufficient for preference input; no form-filling required
- SQLite is sufficient for single-user development; the DB choice is an implementation detail not covered here
- The TinyFish Web Agent API is available and can reliably extract post data from Facebook groups
- Users will check the webapp actively during their search campaign — push notifications are not required in this phase

---

## User Stories

**Campaign setup**

- As a user, I want to describe what I'm looking for in plain Vietnamese so that I don't have to fill out a rigid form
- As a user, I want to see a structured summary of what the agent understood from my description so that I can catch and fix any misinterpretation before the agent starts searching
- As a user, I want to add my own Facebook group URLs as sources so that the agent searches the specific communities I trust
- As a user, I want to choose how often the agent scans (daily or every 2 days) so that I can balance freshness against the agent's activity

**Scanning and matching**

- As a user, I want the agent to automatically scan my configured groups on a schedule so that I don't have to check them myself
- As a user, I want the agent to only surface listings that genuinely match my stated preferences so that I'm not wading through irrelevant results
- As a user, I want to see what the agent is doing while a scan is running so that I know it's working and not just frozen
- As a user, I want the agent to never show me a listing I've already seen so that I'm not wasting time reviewing duplicates

**Pipeline management**

- As a user, I want to see all my listings organized by stage (new, contacted, viewing scheduled, etc.) so that I always know where things stand with each property
- As a user, I want to expand any listing to see its full details so that I can evaluate it properly
- As a user, I want to skip a listing and tell the agent why so that the agent has signal to improve future results
- As a user, I want to manually move a listing between stages so that the pipeline reflects reality

---

## Functional Requirements

### Campaign setup

1. The app presents a chatbox as the entry point. The user describes their rental needs in Vietnamese. No form fields are shown before this step.
2. After the user submits their description, the agent displays a structured confirmation showing what it extracted: areas, budget range, number of bedrooms, any specific requirements, and move-in date if mentioned. Each field must be individually editable by the user before confirming.
3. If the agent cannot extract a required field (area or budget), it must ask the user for it specifically rather than proceeding with missing information.
4. After the user confirms their preferences, the app asks them to provide Facebook group URLs as sources. At least one source is required before the campaign can start.
5. The user selects a scan frequency: daily (default) or every 2 days.
6. The campaign starts immediately after setup. The first scan runs within 1 minute of campaign creation, not at the next scheduled time.

### Scanning

7. The agent scans all configured sources on the selected schedule without any user action.
8. During a scan, the app shows a real-time activity feed describing what the agent is currently doing in plain Vietnamese (e.g., "Đang quét nhóm X... tìm thấy 41 bài mới").
9. The agent must only surface listings that score above a minimum relevance threshold against the user's preferences. Every surfaced listing must include a plain-language explanation of why it matched.
10. Any listing the user has previously seen (regardless of what group it was posted in) must not be surfaced again, even if it appears in a new group or is reposted.
11. If a scan finds no new matching listings, the agent notifies the user quietly without creating alarm.
12. Scans that fail partway through (e.g., a group is inaccessible) must complete the remaining sources and report which groups succeeded and which did not — a partial failure must not abort the entire scan.

### Pipeline view

13. The webapp displays all listings in a horizontal pipeline with the following stages: New Matches, Contacted, Viewing Scheduled, Viewed, Shortlisted, Rejected.
14. The New Matches column must visually indicate when new listings have just arrived.
15. Each listing card must show at minimum: a thumbnail photo, price, area/district, and a match score.
16. Tapping or clicking a listing card opens a detail view showing: all photos, full match explanation, raw address, number of bedrooms, landlord phone number, and the original post text.
17. From the detail view, the user can skip a listing. Skipping requires selecting a reason from a predefined list: Too far / Price doesn't fit / Bad photos / Wrong area / Other.
18. The user can manually drag or tap to move any listing to any stage.
19. Listings moved to Rejected must not reappear in future scans (deduplication must account for rejected listings).

### Scan history and controls

20. The user can trigger a manual scan at any time from the dashboard with a single tap.
21. The dashboard shows: date and time of the last completed scan, date and time of the next scheduled scan, and total number of new listings found today.

---

## Non-Functional Requirements

- The webapp must load and be interactive within 3 seconds on a standard Vietnamese mobile connection (4G)
- A full scan of up to 5 groups must complete within 5 minutes
- The pipeline view must render correctly on both desktop browsers and mobile browsers (responsive layout)
- All user-facing text — including agent messages, UI labels, and error states — must be in Vietnamese by default
- The app must handle a scan failure (TinyFish unavailable, group inaccessible) without crashing or losing existing campaign data

---

## Out of Scope for This Phase

- Zalo integration of any kind (notifications, outreach, authentication)
- Neighborhood or area research
- Preference learning / improving scores based on feedback
- Zalo group scanning (Facebook only in this phase)
- Multiple simultaneous campaigns
- User accounts or authentication (single user assumed)

---

## Success Metrics

| Metric | Target |
|---|---|
| Campaign setup completion rate | >80% of users who start setup finish it |
| Time to complete setup | <3 minutes median |
| Scan reliability | >95% of scheduled scans complete without error |
| Duplicate listing rate | <1% of surfaced listings are ones the user has already seen |
| Scan completion time | <5 minutes for up to 5 groups |

---

## Open Questions

1. **Minimum match threshold:** What score qualifies a listing as a match? Too low = noise, too high = misses. Needs calibration with real data.
2. **Group post lookback window:** How far back should each scan look? 24 hours? 48 hours? Affects both coverage and scan speed.
3. **Maximum listings per scan:** Should there be a cap on how many new listings are delivered per scan (e.g., max 20)? Or surface everything that matches?
4. **Stage labels:** Are the Vietnamese stage names final? ("Mới", "Đã liên hệ", "Đặt lịch xem", "Đã xem", "Danh sách ngắn", "Đã loại")
