# PRD-03 — Research & Intelligence

| Field | Value |
|---|---|
| Phase | 3 of 4 |
| Status | Draft |
| Owner | TBD |
| Last updated | March 2026 |
| Depends on | PRD-01 and PRD-02 shipped and stable |

---

## Overview

Phase 3 makes RentAgent meaningfully smarter than a basic search filter. Every matched listing gets automated background research before it reaches the user. Users can request a deeper neighborhood analysis for any listing — including a visual walkthrough via Street View. The agent also begins learning from the user's reactions over time, improving match quality as the campaign progresses. Zalo groups are added as a first-class source alongside Facebook.

---

## Goals

- Give users actionable context on every listing before they decide whether to contact the landlord
- Let users virtually "visit" a neighborhood before committing to an in-person viewing
- Make match quality measurably better by week 4 than it was in week 1
- Expand coverage to Zalo rental groups, which are often more active and less scraped than Facebook for certain Vietnamese cities

---

## Assumptions

- Users care about neighborhood context but won't research it themselves — it needs to be proactively surfaced, not buried in a tab they have to open
- Vietnamese rental listings often omit details that can be inferred from public sources (flood history, building reputation)
- Most meaningful preference learning happens through skip reasons and post-viewing reactions, not through declared preference updates
- Zalo group posts have a similar structure to Facebook group posts and can be extracted with the same approach
- The same landlord frequently posts the same listing across multiple groups — content-based deduplication is necessary to prevent duplicate cards in the pipeline

---

## User Stories

**Background research**

- As a user, I want to see known issues or red flags about a listing's building or area before I contact the landlord so that I don't waste time visiting a property with obvious problems
- As a user, I want research results to be pre-loaded when I open a listing card so that I don't have to wait
- As a user, I want negative findings surfaced prominently so that I can't accidentally miss a red flag

**Area research (on demand)**

- As a user, I want to do a deep-dive on any listing's neighborhood with a single tap so that I can virtually assess the area before scheduling a viewing
- As a user, I want to know whether the street is accessible by motorbike and whether there is parking so that I know before visiting
- As a user, I want to see what amenities are nearby (markets, supermarkets, bus stops) so that I can judge the location's convenience for my daily life
- As a user, I want a Street View-based description of the building's exterior and surrounding street so that I can check if it matches the listing photos

**Preference learning**

- As a user, I want the agent to get better at understanding what I actually like over the course of my campaign so that I spend less time skipping irrelevant listings in week 4 than I did in week 1
- As a user, I want to see a plain-language summary of what the agent has learned about my preferences so that I can verify it has understood me correctly
- As a user, I want to reset the learned preferences if they've gone in the wrong direction so that I can start fresh without losing my campaign history

**Zalo groups**

- As a user, I want to add Zalo group URLs as sources alongside Facebook groups so that the agent scans all the communities where I know good listings are posted

---

## Functional Requirements

### Background research

1. Every listing that passes the match threshold must have background research completed before it is delivered to the user. The user must never see a listing card with an empty research section.
2. Background research covers two areas: (a) building and landlord reputation based on publicly available reviews and forum mentions, and (b) flood risk for the listing's area.
3. Research findings are displayed on the listing card as color-coded flags: red for serious issues, yellow for minor concerns worth asking about, green for positive signals or absence of issues.
4. Each flag must be a plain Vietnamese sentence of no more than 80 characters. No jargon, no links, no citations — just the finding.
5. If research fails for a listing (source unavailable), the listing is still delivered with a flag indicating research could not be completed. The listing is not held back.
6. A maximum of 5 flags are shown per listing. Red flags take priority over yellow, yellow over green.

### Area research (on demand)

7. Every listing card must include a "Nghiên cứu khu vực" button that triggers a one-time deep neighborhood analysis.
8. While the analysis is running, the listing card shows a loading state with a plain-language progress description ("Đang mở Google Maps... Đang xem đường phố..."). The user can navigate away and return — the research continues in the background and the result will be there when they come back.
9. The area research result must include at minimum: street type (main road or alley), motorbike accessibility (yes/no/unknown), parking availability (yes/no/unknown), flood risk assessment (low/medium/high/unknown), a list of the 3 closest amenities with approximate walking distance, and a plain-language comment on whether the building exterior matches the listing photos.
10. All area research results are displayed in Vietnamese.
11. The result is cached permanently on the listing card — running it again refreshes the data but the old result remains visible until the refresh completes.
12. Area research must complete within 90 seconds in the happy path. If it takes longer, the user sees a timeout message and a retry option.

### Preference learning

13. Every skip reason and every post-viewing feedback reaction must update the campaign's preference model.
14. The preference model adjusts match scores for future listings based on observed patterns. Examples: consistently skipping listings in a particular area reduces that area's weight; consistently reacting positively to listings with many photos increases the photo count signal.
15. Preference weight changes must be gradual (no single signal should dramatically change results) and bounded (weights cannot go to zero for any criterion the user originally stated).
16. The Preferences screen must display a plain-language summary of what the agent has learned, updated after every 5 feedback signals.
17. The summary must be specific and actionable (e.g., "Bạn thường bỏ qua phòng trong hẻm" not "Preferences updated").
18. A "Đặt lại học" (Reset learning) option must be available. Activating it requires a confirmation step and resets only the learned weights — the user's declared preferences and campaign history are not affected.

### Zalo group sources

19. During campaign setup and on the source management screen, users must be able to add Zalo group URLs as sources alongside Facebook group URLs.
20. The app must auto-detect whether a URL is a Facebook group or a Zalo group and label it accordingly — the user must not have to specify the type manually.
21. Zalo group listings must flow through the same matching, deduplication, and research pipeline as Facebook listings. They are displayed identically in the pipeline.

### Deduplication hardening

22. Deduplication must detect the same listing even when it is posted in multiple groups with different post URLs. Two listings are considered the same if they share the same landlord phone number, the same price, and the same approximate area.
23. When a duplicate is detected, the app keeps only one listing card in the pipeline. If the duplicate appears in a group the user values more highly (based on prior reaction patterns), the source label is updated accordingly.

---

## Non-Functional Requirements

- Background research must complete for all listings in a scan batch before the shortlist notification is sent (research cannot be deferred to after notification)
- Area research must complete within 90 seconds for addresses in major Vietnamese cities (HCM, Hanoi, Da Nang)
- The preference model must update within 5 seconds of a feedback signal being recorded
- Adding Zalo group sources must not increase overall scan time by more than 50% compared to an equivalent number of Facebook sources

---

## Out of Scope for This Phase

- Research for listings that were already delivered in previous phases (no retroactive enrichment)
- Research into landlord identity beyond what's publicly available (no private data lookup)
- Learning from preference text edits (only from feedback signals — skip reasons and post-viewing reactions)
- Neighborhood research in cities other than HCM, Hanoi, and Da Nang in initial release

---

## Success Metrics

| Metric | Target |
|---|---|
| Research coverage | 100% of delivered listings have at least one research flag |
| Area research usage | >40% of listings in "Viewed" stage have area research completed |
| Area research completion rate | >90% of area research requests complete within 90 seconds |
| Learning improvement | Average match score of listings user reacts positively to increases by >0.1 between week 1 and week 4 |
| Skip rate trend | Weekly skip rate decreases by >20% from week 1 to week 4 for active campaigns |
| Zalo source adoption | >30% of users with Zalo groups add at least one Zalo source |

---

## Open Questions

1. **Research timing:** Background research adds latency to scan delivery. What's the acceptable delay between a scan completing and the user receiving their notification — 5 minutes? 10 minutes? This determines how much parallelism is needed.
2. **Flood risk data quality:** Which sources reliably cover Vietnamese urban flood risk? Google search results are inconsistent. Are there better sources (e.g., city planning department maps)?
3. **Preference learning transparency:** How much detail should the learning summary show? Showing "you skip listings in Quận 7" might feel intrusive to some users. Is this a setting or always on?
4. **Zalo group access:** Do Zalo groups require a logged-in Zalo session to read? If yes, does the Phase 2 Zalo connection double as access for Zalo group scanning, or is separate authentication needed?
5. **Learning reset UX:** When a user resets their learned preferences, should the app show them a preview of what will change ("this will un-learn 3 patterns") or just a generic confirmation?
