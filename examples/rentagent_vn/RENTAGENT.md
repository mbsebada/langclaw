# RentAgent VN — Product Specification

> AI-Powered Rental Search Campaign Manager for Vietnamese locals.
> March 2026 · Draft v1.0

---

## Table of Contents

1. [Problem & Vision](#1-problem--vision)
2. [Target Users](#2-target-users)
3. [Core Concepts](#3-core-concepts)
4. [User Flows](#4-user-flows)
   - 4.1 Campaign Setup
   - 4.2 Agent Background Loop
   - 4.3 Shortlist Delivery & Pipeline Management
   - 4.4 Area Research
   - 4.5 Zalo Outreach
   - 4.6 Post-Viewing Feedback
5. [Screens & UI Specification](#5-screens--ui-specification)
6. [Content & Copy Guidelines](#6-content--copy-guidelines)
7. [Build Phases](#7-build-phases)
8. [Risks & Open Questions](#8-risks--open-questions)

---

## 1. Problem & Vision

### The Problem

Finding a rental in Vietnam is a weeks-long, full-time job. The market is fragmented — good listings live in specific Facebook groups, Zalo communities, and niche forum threads that only locals know about. There is no unified search. There is no standard API.

People spend 2–3 hours per day manually scanning groups, copy-pasting the same message to dozens of landlords, getting ghosted, and missing listings that disappeared in 2 hours. After 4–6 weeks of this, most people settle — not because the right place doesn't exist, but because finding it takes more sustained effort than anyone can maintain.

The experience is especially rough because it compounds: you're searching while also still living somewhere, dealing with lease end dates, and trying to schedule viewings around work. It is cognitively exhausting.

### The Vision

RentAgent turns a full-time job into a background task.

You describe what you want once, in plain Vietnamese. You add the Facebook and Zalo groups you know have good listings in your target area. The agent runs continuously — scanning those sources, filtering matches, researching each property, and managing landlord conversations on your behalf via your own Zalo account.

You interact with the product on your terms: check the webapp when you want to review your pipeline, respond to Zalo notifications when a good new match arrives, tap to schedule a viewing. The agent handles everything in between.

The goal is not to show you more listings. The goal is to get you to a signed lease, faster and with less stress, by doing the tedious work for you.

---

## 2. Target Users

### Primary: Vietnamese Locals Actively Searching

**Who they are:** Vietnamese people — most commonly in their 20s and 30s — searching for a rental in a major city (HCM City, Hanoi, Da Nang). They are actively looking, not browsing casually. They have a deadline (lease ending, relocation, new job).

**What they know:** They know which Facebook groups and Zalo communities have real listings in their target neighborhoods. They have Zalo and use it daily. They are comfortable messaging landlords on Zalo.

**What frustrates them:** Spending hours every day doing the same repetitive search. Seeing listings that disappeared before they could respond. Messaging landlords who never reply. Keeping track of 20 places across WhatsApp threads, screenshots, and mental notes.

**What they need:** An agent that works while they're at work, sleeping, or living their life — and surfaces only the listings worth their time.

### Secondary: Expats and Relocators

**Who they are:** Foreigners or Vietnamese people moving between cities who lack local knowledge of neighborhoods and don't know which groups to monitor.

**What's different for them:** They benefit more from the neighborhood research feature (Street View, amenities map) since they can't rely on local knowledge. They may need English-language support in the UI (Vietnamese listings, English interface).

**Out of scope for v1:** Focus entirely on the primary user first. Expat-specific features (English UI, translated listings) are a Phase 2 consideration.

---

## 3. Core Concepts

### Campaign

A **Campaign** is the central object in RentAgent. It's not a search — it's an ongoing, persistent effort that runs for weeks until the user finds and signs a lease.

A campaign has:
- A set of user preferences (area, budget, room type, requirements)
- A list of sources to monitor (specific FB and Zalo groups)
- A scan schedule (how often the agent checks for new listings)
- A pipeline of listings across different stages
- A history of feedback signals used to improve future matches

Users have one active campaign at a time. When they sign a lease, they close the campaign.

### Listings Pipeline

Every listing the agent finds passes through a pipeline of stages. This is not a passive list — it's a living record of where things stand with each property.

| Stage | Meaning |
|---|---|
| **New Matches** | Just surfaced by the agent. User hasn't acted yet. |
| **Contacted** | Agent has sent a Zalo message to the landlord. |
| **Viewing Scheduled** | Time and date confirmed with the landlord. |
| **Viewed** | User has visited the property. |
| **Shortlisted** | User considers this a top candidate. |
| **Rejected** | Removed from consideration (skipped or ruled out after viewing). |

### Preference Model

The preference model is the agent's understanding of what the user wants. It starts as the structured output of the user's initial description and evolves throughout the campaign based on feedback signals (skips, reactions, post-viewing notes).

The distinction between **declared preferences** (what you said you want) and **revealed preferences** (what you actually respond well to) is what makes the agent get better over time. A user might say they want a 1BR under 7M, but consistently skip listings in alleys and react positively to listings on main streets — the agent learns this and starts weighting location type even though it wasn't mentioned.

### Agent Activity

The agent is always doing something in the background. It is not a search button — it is an ongoing process that runs on a schedule. The user can see what it's doing at any time via the live activity feed, but they don't need to be present for it to work.

---

## 4. User Flows

---

### 4.1 Flow: Campaign Setup

This flow happens once, at the start of a search campaign. The goal is to configure the agent with enough information to start producing useful matches.

#### Step 1 — Natural Language Input

The user opens the webapp and sees a single chatbox with a placeholder:

> *"Mô tả phòng bạn đang tìm kiếm... (khu vực, giá, số phòng, yêu cầu đặc biệt...)"*

The user types freely in Vietnamese. The agent does not prompt them with a form — it reads whatever they write. Examples of valid inputs:

- *"Mình cần tìm phòng trọ ở Bình Thạnh hoặc Phú Nhuận, tầm 6–8 triệu, 1 phòng ngủ, có chỗ để xe máy, dọn vào trước 1/4."*
- *"Tìm căn hộ mini quận 3, dưới 10 triệu, đầy đủ nội thất, gần metro, 2 người ở."*
- *"Phòng trọ Cầu Giấy HN, 3–5tr, không cần nội thất, thang máy không quan trọng, nhưng cần yên tĩnh."*

The input can be as short or as detailed as the user wants. The agent extracts what it can and asks for clarification only on fields that are genuinely missing and important (e.g., if no area is mentioned at all).

#### Step 2 — Structured Confirmation

After the user submits, the agent replies with a structured confirmation displayed as editable tags/chips:

```
✅ Khu vực:       Bình Thạnh, Phú Nhuận
✅ Ngân sách:     6–8 triệu VND/tháng
✅ Loại phòng:    1 phòng ngủ
✅ Yêu cầu:       Chỗ để xe máy
✅ Dọn vào:       Trước 01/04/2026
```

Each chip is tappable and editable. The user can correct any misextracted field inline. Below the chips, a short plain-text confirmation: *"Mình sẽ tìm các phòng phù hợp với yêu cầu trên. Có gì cần sửa không?"*

The user confirms (or corrects) and moves to the next step.

#### Step 3 — Source Configuration

The user is shown a list of suggested Facebook and Zalo groups based on their stated areas. These are pre-populated suggestions — the user can accept them, remove ones they don't want, and add groups they personally know are active.

For each group, the user sees:
- Group name
- Platform (Facebook / Zalo)
- Estimated activity level (if detectable)
- A toggle to include / exclude

The user must add at least one source to proceed. They can return to this screen later to add or remove groups.

#### Step 4 — Scan Frequency

The user sets how often the agent scans. Options:
- **Mỗi ngày** (Every day) — recommended for active searches
- **Mỗi 2 ngày** — for less urgent searches

The default is daily. The first scan starts immediately after setup.

#### Step 5 — Zalo Connection (Optional at Setup)

The user is prompted to connect their Zalo account. This is needed for two things: receiving shortlist notifications on Zalo, and having the agent send messages to landlords on their behalf.

This step is **optional at setup** — the user can skip it and connect later. However, certain features (auto-outreach, Zalo notifications) will not be available until Zalo is connected.

If the user chooses to connect, they are taken through a cookie-based authentication flow (see Section 5 — Zalo Setup screen).

---

### 4.2 Flow: Agent Background Loop

This flow runs automatically on the configured schedule. The user is not involved — they may not even have the app open. The agent works silently and delivers results when done.

#### Step 1 — Trigger

The loop starts either on schedule (cron) or manually when the user taps "Scan Now" from the dashboard.

#### Step 2 — Scan Sources

The agent opens each configured Facebook and Zalo group using a stealth browser (via TinyFish Web Agent API) and scrolls through recent posts. It extracts:

- Post text (description, price, address, contact info)
- Photos attached to the post
- Poster's phone number (often = Zalo ID in Vietnam)
- Post timestamp

The agent streams intermediate progress back to the webapp in real time. If the webapp is open, the user sees the live activity feed updating:

> *Đang quét nhóm "Phòng Trọ Bình Thạnh"... tìm thấy 41 bài mới*
> *Đang lọc: 7 bài phù hợp tiêu chí...*
> *Đang kiểm tra thông tin căn hộ đường Đinh Tiên Hoàng...*

If the webapp is not open, the scan still completes — results are delivered via Zalo notification when done.

#### Step 3 — Deduplication

Every listing the agent has ever seen is stored. Before processing new listings, the agent deduplicates against the full history:

- If the listing was already seen and is currently in the pipeline → skip
- If the listing was seen and rejected by the user → skip
- If the listing was seen but has changed significantly (price dropped >10%, new photos) → re-surface with a "Updated" badge
- If the listing is genuinely new → process

#### Step 4 — Matching & Scoring

Each new, non-duplicate listing is scored against the user's preference model. The score reflects how many criteria are met, weighted by the revealed preference weights accumulated from feedback signals.

Match score is surfaced as a plain-language summary on the listing card, not just a number:
- *"Khớp 9/10 tiêu chí — không có thang máy nhưng tầng 2"*
- *"Ngân sách hơi vượt (8.5tr) nhưng đáp ứng tất cả yêu cầu khác"*
- *"Khu vực đúng, giá đúng — không có thông tin về chỗ để xe"*

Listings below a minimum match threshold (e.g., fewer than 5/10 criteria) are discarded.

#### Step 5 — Background Research

For each listing that passes the match threshold, the agent looks up:

- Building reputation (searches for the address in relevant Vietnamese forums, Facebook groups, Google)
- Known issues (flooding, noisy, poor management, water problems — these often appear in tenant reviews)
- Landlord signal — how responsive have similar landlords in the building been?

Research findings are summarized as short flags on the listing card. Red flags are surfaced prominently; absence of any notable issues is also noted.

#### Step 6 — Shortlist Curation & Delivery

From all matched listings, the agent selects the 3–5 best matches for the day's scan based on combined match score and research quality.

If fewer than 3 listings meet the threshold, all matches are included. If zero listings match, the agent sends a quiet notification: *"Hôm nay không có bài mới phù hợp. Mình sẽ kiểm tra lại vào ngày mai."*

The shortlist is:
- Added to the **New Matches** column in the webapp pipeline
- Sent as a Zalo notification to the user (if Zalo is connected)

---

### 4.3 Flow: Shortlist Review & Pipeline Management

This is the user's primary recurring interaction with the product. It happens after each scan delivers new matches.

#### Entry Points

The user can enter this flow from:
- A Zalo notification: *"RentAgent tìm thấy 4 phòng mới phù hợp với bạn 🏠"* → tap to open webapp
- The webapp dashboard directly

#### The Pipeline View

The pipeline is the central screen. It shows all active listings across their stages in a horizontal layout. Each listing is a card with:

- Primary photo
- Price (monthly)
- Address / area
- Match score badge (e.g., "9/10")
- Stage indicator
- Zalo status (Not contacted / Messaged / Replied / Confirmed)

The user navigates between cards within the New Matches column. For each card they can:

**View full details** — expands the card to show:
- Full photo carousel
- Full match score breakdown ("Khớp vì: khu vực ✓, giá ✓, 1PN ✓, xe máy ✓...")
- Background research flags
- Landlord contact info (phone / Zalo)
- Agent notes

**Trigger area research** — opens the Area Research flow (see 4.4)

**Trigger outreach** — opens the Zalo Outreach flow (see 4.5)

**Skip** — removes from active pipeline, prompts for a quick reason:
- Quá xa
- Giá không phù hợp
- Ảnh không ổn
- Khu vực không đúng
- Khác

The skip reason is stored as a feedback signal and used to update the preference model. Skipping is designed to be instant — one tap for the reason, done.

#### Moving Listings Through Stages

The agent moves listings to **Contacted** automatically when it sends a message. Users move listings to subsequent stages:

- After a landlord replies and they agree on a time → manually drag/tap to **Viewing Scheduled**
- After attending a viewing → app prompts them to move to **Viewed** and triggers the post-viewing feedback flow
- If they decide this is a strong candidate → move to **Shortlisted**
- If ruled out → **Rejected** (same quick-reason prompt as skip)

---

### 4.4 Flow: Area Research

On-demand, deep neighborhood research for a specific listing. Triggered from the listing card.

This feature is most valuable for:
- Properties in neighborhoods the user doesn't know well
- Properties where the listing photos are limited or unclear
- Verifying that the building matches what the listing describes

#### What the Agent Does

1. Takes the listing address and opens Google Maps via TinyFish
2. Searches for nearby amenities relevant to the user's stated priorities (e.g., if they mentioned "gần chợ" — finds the nearest wet market)
3. Enters Street View and navigates the immediate street, looking for:
   - Whether the alley/street is accessible by xe máy
   - Parking availability in front of the building
   - Whether the building exterior matches the listing photos
   - Obvious noise sources (karaoke bars, construction, markets)
   - Flood-risk indicators (drainage quality, elevation)
4. Synthesizes findings into a structured brief

#### Output — Neighborhood Brief

Displayed on the listing card as a collapsible section:

```
📍 Khu vực: Hẻm 5m, xe máy vào được, không có chỗ đỗ ô tô
🛍️ Gần nhất: Chợ Bà Chiểu (380m), Vinmart (1.1km)
🚇 Metro: Bến Thành (2.3km, tuyến 1)
⚠️ Lưu ý: Mặt tiền hẻm hơi hẹp — nên kiểm tra khi xem
✅ Ngoại thất khớp với ảnh đăng
```

The brief is stored permanently on the listing card. Running it again refreshes the data.

---

### 4.5 Flow: Zalo Outreach

The agent contacts landlords on the user's behalf via their own Zalo account.

#### Trigger Points

Outreach can be triggered in two ways:

**Manual:** User reviews a listing and taps "Liên hệ chủ nhà." They see a message draft and can edit before sending.

**Automatic (opt-in):** During campaign setup or from preferences, the user can enable "Tự động liên hệ khi tìm được phòng phù hợp." When enabled, the agent sends an outreach message automatically when a new listing scores above a threshold (e.g., 8/10). The user still sees the message in their Zalo — they just didn't have to tap a button.

#### Message Drafting

The agent drafts a message in natural Vietnamese, using the correct anh/chị/em register. The default template is informal and genuine:

> *"Chào anh/chị, em thấy phòng anh/chị đăng ở [tên nhóm]. Phòng còn trống không ạ? Em muốn hỏi thêm thông tin và xem phòng được không ạ?"*

The message is always shown to the user before sending (as a preview in the webapp or as a notification), with an option to edit. There is a short cancel window (30 seconds for auto-outreach mode).

The agent does not impersonate the user beyond what is standard in a rental inquiry. It does not claim to be the user by name unless the user has configured their name in preferences.

#### After Sending

- Listing moves to **Contacted** stage in the pipeline
- Zalo thread is linked to the listing card
- If the landlord replies, the reply is surfaced as a notification and shown in the listing card conversation view
- Because landlords in Vietnam typically respond quickly (same day or within hours), the agent does not send follow-up messages by default. If there is no reply after 48 hours, the agent surfaces a gentle prompt: *"Chủ nhà chưa trả lời — bạn có muốn gửi tin nhắn khác không?"*

---

### 4.6 Flow: Post-Viewing Feedback

After attending a viewing, the agent prompts the user for a quick reaction. This is the highest-signal feedback moment in the entire product.

#### Trigger

The agent detects the listing has entered **Viewed** stage and sends a Zalo message (or in-app notification if Zalo is not connected):

> *"Bạn vừa xem phòng ở [address]. Cảm nhận của bạn thế nào?"*

Three options, each one tap:

- 👍 **Thích** — strong positive signal
- 😐 **Tạm được** — neutral, still considering
- 👎 **Không phù hợp** — negative signal

After selecting, an optional free-text field appears: *"Bạn có muốn ghi chú thêm gì không? (không bắt buộc)"*

Examples of notes users might leave:
- *"Phòng ổn nhưng tiếng ồn từ đường lớn nhiều quá"*
- *"Chủ nhà thân thiện, phòng sạch, nhưng thang máy cũ"*
- *"Nhỏ hơn trong ảnh"*

#### How Feedback Affects the Preference Model

Feedback signals are used to update the preference model over time. The model shifts from matching declared criteria to matching revealed preferences. Examples:

- User consistently skips listings described as "hẻm" → agent reduces weight on alley properties even if area matches
- User reacts positively to listings with "view thoáng" notes → agent starts surfacing this as a filter
- User's post-viewing notes frequently mention "ồn ào" negatively → agent starts penalizing listings near traffic or nightlife

The user can see a simplified view of what the agent has learned about their preferences in the Preferences screen.

---

## 5. Screens & UI Specification

---

### 5.1 Setup Screen (Onboarding)

**Purpose:** Configure the campaign for the first time.

**Layout:** Single-page flow with 4 progressive steps. No sidebar, no navigation. Full focus on the task.

**Step indicators:** Simple progress dots at the top (1 of 4).

**Step 1 — Chatbox**
- Large text input area, placeholder in Vietnamese
- Subtle hint text below: *"Ví dụ: Phòng trọ Bình Thạnh, dưới 8 triệu, có chỗ để xe..."*
- Single CTA button: "Tiếp tục →"
- No character limit. Accept voice input if on mobile.

**Step 2 — Confirmation Chips**
- Agent response in a chat bubble above
- Below it: editable chips in a grid layout
- Each chip shows field name + extracted value. Tap to edit inline.
- If a field could not be extracted, show an empty chip with placeholder: *"Chưa có — thêm vào?"*
- CTA: "Xác nhận →"

**Step 3 — Sources**
- Title: *"Chọn nguồn tìm kiếm"*
- Pre-populated suggested groups (based on stated area)
- Each row: platform icon (FB/Zalo) + group name + toggle
- "Thêm nhóm khác" button opens a search/paste field for group URLs
- Minimum 1 source required. Show inline error if user tries to proceed with 0.
- CTA: "Tiếp tục →"

**Step 4 — Frequency + Zalo**
- Scan frequency: two radio options (daily / every 2 days). Default: daily.
- Zalo connection section: brief explanation of what it's used for, a "Kết nối Zalo" button
- This step is skippable — "Bỏ qua, kết nối sau" link below the CTA
- CTA: "Bắt đầu tìm kiếm 🚀"

---

### 5.2 Campaign Dashboard (Main Screen)

**Purpose:** The primary recurring screen. Shows the pipeline, stats, and current agent activity.

**Layout:** Three-zone layout
- Top bar: campaign name, scan status, "Scan Now" button
- Left column (narrow): stats sidebar — total listings seen, viewings scheduled, days active
- Main area: pipeline columns

**Pipeline Columns**
- Horizontal scroll on mobile, visible all at once on desktop
- Each column has a header with stage name and listing count badge
- **New Matches** column has a pulse/highlight effect when new listings just arrived
- Cards within each column are vertically stacked and scrollable

**Stats Bar (top of New Matches column)**
- Last scan: *"Hôm nay lúc 8:32"*
- Next scan: *"Ngày mai lúc 8:00"*
- New today: *"4 phòng mới"*

**Activity Feed Toggle**
- Floating button (bottom right): "Xem hoạt động agent"
- Opens a slide-up drawer showing the real-time activity stream
- While a scan is running, this button pulses
- Feed entries use plain Vietnamese: *"Đang quét nhóm... tìm thấy 12 bài mới... lọc theo tiêu chí..."*

---

### 5.3 Listing Card (Collapsed — in Pipeline)

**What it shows:**
- Thumbnail photo (cropped square)
- Price (large, prominent)
- Area / district
- Match score badge: green for 8+, yellow for 6–7, gray for below 6
- Stage tag
- Zalo status dot: gray (not contacted), yellow (messaged), green (replied)

**Tap action:** Expands to full listing detail.

---

### 5.4 Listing Card (Expanded — Full Detail)

**Layout:** Full-screen modal or side panel (desktop). Back button to return to pipeline.

**Sections:**

**Photos**
- Full-width carousel
- Swipeable. Photo count indicator.

**Key Info**
- Price (with "Đã thương lượng: Xtr" note if agent negotiated)
- Address
- Bedrooms, floor, building type
- Posted in: [group name] on [date]

**Match Score**
- Large score display: "9/10 tiêu chí"
- Expandable breakdown: each criterion listed with ✓ or ✗ and a short note
- If a criterion is unknown (not mentioned in listing): shown as "?" with note *"Không có thông tin — nên hỏi khi liên hệ"*

**Background Research**
- Card section with colored flag tags
- Green flags: *"Chủ nhà phản hồi nhanh (theo đánh giá)"*, *"Tòa nhà không có phản ánh tiêu cực"*
- Yellow flags: *"Khu vực hay ngập vào mùa mưa — nên hỏi tầng"*
- Red flags: *"Có 3 phản ánh về tiếng ồn lớn từ quán karaoke gần đó"*
- If no research available: *"Chưa có thông tin — bấm Nghiên cứu Khu Vực để tìm hiểu thêm"*

**Neighborhood Brief** (if area research has been run)
- Structured brief as described in Flow 4.4

**Landlord & Contact**
- Phone number
- Zalo status + link to open conversation in Zalo

**Actions**
- Primary: "Liên hệ chủ nhà" (if not yet contacted) / "Xem tin nhắn Zalo" (if contacted)
- Secondary: "Nghiên cứu khu vực" / "Lên lịch xem" / "Bỏ qua"
- Danger: "Loại bỏ" (moves to Rejected, prompts for reason)

**User Notes**
- Freetext field: *"Ghi chú của bạn..."*
- Auto-saved. Shown prominently after viewing.

---

### 5.5 Area Research View

**Trigger:** "Nghiên cứu khu vực" button on listing card.

**Layout:** Full-screen view with a loading state while the agent works.

**Loading state:** Shows animated progress — *"Đang mở Google Maps... Đang tìm tiện ích gần đó... Đang xem đường phố..."* — with a rough progress indicator (not exact %).

**Result view:**
- Map embed showing the listing pin + nearby POIs
- Structured brief below the map (see Flow 4.4 for format)
- "Cập nhật lại" button to re-run (refreshes data)
- Timestamp: *"Nghiên cứu lúc: [date]"*

---

### 5.6 Agent Activity Feed

**Access:** Floating button on dashboard → slide-up drawer.

**Content:** Chronological log of agent actions during the current or most recent scan.

Each entry shows:
- Timestamp (relative: *"2 phút trước"*)
- Plain Vietnamese description of the action
- Source group name when relevant
- Count when relevant (*"34 bài mới"*, *"6 bài khớp"*)

**States:**
- **Scanning (live):** Feed updates in real time. Top of drawer shows *"Đang quét... 🔄"*
- **Complete:** Top shows *"Hoàn thành lúc [time]"* with a summary: *"Tìm thấy 4 phòng mới phù hợp"*
- **No recent scan:** *"Chưa có hoạt động. Quét tiếp theo: ngày mai lúc 8:00"*

---

### 5.7 Preferences Screen

**Access:** Settings icon on dashboard header.

**Sections:**

**Tiêu chí tìm kiếm**
- Editable chips (same format as setup Step 2)
- "Lưu thay đổi" button triggers a re-filter of existing unseen listings against new criteria

**Học từ phản hồi của bạn** (What the agent has learned)
- Brief human-readable summary of revealed preferences:
  - *"Bạn thường bỏ qua các phòng trong hẻm nhỏ"*
  - *"Bạn phản hồi tốt hơn với phòng có ảnh chụp ban ngày"*
  - *"Bạn ưu tiên tầng cao hơn tầng 1–2"*
- "Đặt lại học" link to clear learned weights (with confirmation)

**Nguồn tìm kiếm**
- Current sources list with toggle to enable/disable
- "Thêm nguồn mới" button

**Lịch quét**
- Current frequency
- "Quét ngay" button

**Chiến dịch**
- "Tạm dừng chiến dịch" — pauses scanning without deleting data
- "Kết thúc chiến dịch" — marks as complete, archives all listings (confirmation required)

---

### 5.8 Zalo Setup Screen

**Access:** From onboarding Step 4, or from Preferences → Kết nối Zalo.

**Purpose:** Connect the user's Zalo account for outreach and notifications.

**Flow:**
1. Explanation screen: what Zalo access is used for (3 bullet points — notifications, messaging landlords, receiving feedback prompts). What it is NOT used for (anything else).
2. Step-by-step instructions for getting Zalo cookie from browser
3. Paste field for cookie string
4. Connection test: agent sends a test message to the user's own Zalo account to confirm connection
5. Success state: *"Zalo đã kết nối ✓ — Mã xác thực hết hạn sau X ngày"*

**Security note displayed prominently:**
> *"Mã này được mã hóa và chỉ dùng để gửi tin nhắn theo yêu cầu của bạn. Chúng mình không đọc tin nhắn của bạn."*

**Reconnection:** When the cookie expires (Zalo sessions typically expire after a period), the user receives a notification and is prompted to re-authenticate.

---

## 6. Content & Copy Guidelines

### Language

- All UI copy is in Vietnamese for the primary user
- Tone: friendly, informal, like a helpful friend — not corporate, not robotic
- Use "mình / bạn" (not "chúng tôi / quý khách")
- Agent-generated messages to landlords must use correct kinship pronouns (anh/chị/em) based on context — default to "anh/chị" for landlords (shows respect)

### Landlord Outreach Message Template

Default first contact message:

> *"Chào anh/chị, em thấy phòng anh/chị đăng ở [tên nhóm]. Phòng còn trống không ạ? Em muốn hỏi thêm thông tin và xem phòng được không ạ? Cảm ơn anh/chị."*

Guidelines:
- Keep it short — landlords receive many messages
- Never sound like a mass-sent bot message — avoid overly formal or templated language
- Rotate phrasing slightly across different outreach messages to reduce bot detection
- Never include the agent's name or any hint that it is automated (unless regulations require this — to be reviewed)

### Empty States

- No listings yet: *"Chiến dịch của bạn đang chạy. Mình sẽ thông báo khi tìm thấy phòng phù hợp."*
- Scan found nothing: *"Hôm nay không có bài mới phù hợp. Mình sẽ kiểm tra lại vào [date]."*
- No research available: *"Chưa có thông tin về khu vực này. Bấm để nghiên cứu."*

### Error States

- Zalo connection lost: *"Kết nối Zalo đã hết hạn — cần kết nối lại để gửi tin nhắn. [Kết nối lại]"*
- Source inaccessible: *"Không thể truy cập nhóm [X] trong lần quét này. Sẽ thử lại sau."*
- Scan failed: *"Lần quét vừa rồi gặp lỗi. [Thử lại ngay]"*

---

## 7. Build Phases

### Phase 1 — Core Campaign Loop

Everything needed to run a scan and surface matches. No Zalo, no research.

- Campaign setup flow (chatbox → preferences → sources → frequency)
- Basic listing extraction from Facebook groups via TinyFish
- Preference matching and scoring
- Listing deduplication
- Campaign pipeline view (webapp)
- New matches delivery (webapp only, no Zalo notifications yet)
- Agent activity feed (streaming)
- Basic skip/feedback (stage transitions, skip reasons)

**Success criterion:** A user can set up a campaign, the agent scans their configured FB groups daily, and new matching listings appear in the pipeline.

---

### Phase 2 — Zalo Integration

Adds Zalo as both a delivery channel and an outreach tool.

- Zalo connection flow (cookie auth)
- Shortlist notifications delivered via Zalo
- Manual landlord outreach via Zalo (draft → preview → send)
- Zalo conversation status tracking on listing cards
- Post-viewing feedback prompts via Zalo
- Auto-outreach opt-in setting

**Success criterion:** A user receives a Zalo notification when new matches arrive, taps to open the webapp, and can send a message to a landlord with one tap.

---

### Phase 3 — Research & Intelligence

Adds depth to each listing and makes the agent smarter over time.

- Background research subagent (building reputation, neighborhood lookup)
- Area research / Street View via TinyFish
- Preference learning model (feedback → weight updates → better matches)
- Zalo group scanning (in addition to Facebook groups)
- Research brief display on listing cards

**Success criterion:** A user can tap "Research Area" on any listing and receive a structured neighborhood brief within 60 seconds. Match quality measurably improves from week 1 to week 4 for active users.

---

### Phase 4 — Polish & Retention

- Campaign insights: *"Bạn đã xem 11 phòng. Phòng tốt nhất hiện tại là [X]."*
- Price tracking: alert when a listing's price drops
- Preference editing with live preview of how criteria change affects current pipeline
- Onboarding improvements based on real user behavior
- Performance: reduce scan time, improve extraction accuracy on edge cases

---

## 8. Risks & Open Questions

### 8.1 Zalo Cookie Authentication

**Risk:** zca-js is an unofficial third-party Zalo API. Zalo can update its internals and break the integration without notice. Cookie-based auth also creates a security surface — if the cookie is stolen or leaked, a bad actor can access the user's Zalo.

**Mitigations:**
- Encrypt cookies at rest, never log them
- Display a clear expiry countdown and prompt reconnection proactively
- Be fully transparent in UI about exactly what the connection is used for
- Build a fallback mode: if zca-js breaks, the agent drafts messages and opens a deep link for the user to send manually
- Monitor zca-js upstream for breaking changes

### 8.2 Facebook Group Access

**Risk:** Facebook actively detects and blocks non-human browsing. Scanning frequency may trigger bot detection. Private groups require a logged-in session.

**Mitigations:**
- TinyFish stealth profiles reduce detection surface
- Infrequent scanning (daily, not real-time) keeps volume low
- User-provided FB session cookie (same pattern as Zalo) for private group access
- Prioritize Zalo groups as a fallback — they are less aggressively protected

### 8.3 Listing Data Quality

**Risk:** Posts in rental groups are unstructured — photos, voice messages, vague pricing (*"giá thỏa thuận"*), unclear locations. Extraction accuracy will vary significantly.

**Mitigations:**
- Show raw listing post alongside extracted data so user can verify
- Mark low-confidence extractions with a *"?"* indicator
- Let users correct extractions inline — these corrections improve the model
- Treat missing required fields (no price, no area) as automatically low-priority, not rejected

### 8.4 Preference Learning Requires Volume

**Risk:** The preference model needs 5–10 feedback signals before it meaningfully diverges from declared preferences. New users get no benefit for the first week.

**Mitigation:**
- Do not over-promise personalization upfront
- Show a subtle progress indicator: *"Bạn đã cho 3 phản hồi — tiếp tục để kết quả chính xác hơn"*
- Prompt actively for feedback after each viewing

### 8.5 Open Questions

- **Zalo notification format:** What does a Zalo shortlist notification look like? Plain text? Rich card? What's the character limit? This constrains the delivery design.
- **Multi-city / multi-campaign:** Does a user ever run two campaigns at once (e.g., checking both HCM and Hanoi)? If yes, the campaign model needs to support multiple active campaigns. Assume single campaign for v1.
- **Photo handling:** Extracting photos from FB group posts is technically possible but adds complexity. For v1, can we show the original post link instead of hosting photos? To be decided.
- **Landlord reply forwarding:** When a landlord replies to the agent-sent Zalo message, does the reply appear in the webapp, in the user's own Zalo (it already does — it's their account), or both? The answer affects how conversation tracking works.
- **Vietnamese NLP edge cases:** Listings often use abbreviations (PN = phòng ngủ, PK = phòng khách, WC riêng, etc.). The extraction layer must handle these. Will need a Vietnamese rental vocabulary reference.
