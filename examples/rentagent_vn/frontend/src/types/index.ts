// ---------------------------------------------------------------------------
// Pipeline stages
// ---------------------------------------------------------------------------

export type PipelineStage =
  | "new"
  | "contacted"
  | "viewing"
  | "viewed"
  | "shortlisted"
  | "skipped";

export const PIPELINE_STAGES: {
  key: PipelineStage;
  label: string;
  color: string;
}[] = [
  { key: "new", label: "Mới", color: "bg-blue-500" },
  { key: "contacted", label: "Đã liên hệ", color: "bg-yellow-500" },
  { key: "viewing", label: "Hẹn xem", color: "bg-orange-500" },
  { key: "viewed", label: "Đã xem", color: "bg-purple-500" },
  { key: "shortlisted", label: "Chọn", color: "bg-green-500" },
  { key: "skipped", label: "Bỏ qua", color: "bg-muted-foreground" },
];

export const SKIP_REASONS = [
  { key: "too_far", label: "Quá xa" },
  { key: "price", label: "Giá không hợp" },
  { key: "bad_photos", label: "Ảnh xấu" },
  { key: "wrong_area", label: "Sai khu vực" },
  { key: "other", label: "Khác" },
] as const;

export type SkipReasonKey = (typeof SKIP_REASONS)[number]["key"];

// ---------------------------------------------------------------------------
// Data models (mirror backend)
// ---------------------------------------------------------------------------

export interface Listing {
  id: string;
  campaign_id: string;
  stage: PipelineStage;
  fingerprint?: string;
  title: string | null;
  description: string | null;
  price_vnd: number | null;
  price_display: string | null;
  deposit_vnd: number | null;
  address: string | null;
  district: string | null;
  city: string | null;
  area_sqm: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  listing_url: string | null;
  thumbnail_url: string | null;
  posted_date: string | null;
  source_platform: string | null;
  landlord_name: string | null;
  landlord_phone: string | null;
  landlord_zalo: string | null;
  landlord_facebook_url: string | null;
  landlord_contact_method: string | null;
  match_score: number | null;
  skip_reason: string | null;
  user_notes: string | null;
  scan_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  preferences: CampaignPreferences;
  sources: string[];
  scan_frequency: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CampaignPreferences {
  district?: string;
  city?: string;
  bedrooms?: number;
  bathrooms?: number;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  property_type?: string;
  notes?: string;
  [key: string]: unknown;
}

export interface Scan {
  id: string;
  campaign_id: string;
  job_id: string | null;
  status: "running" | "completed" | "failed";
  listings_found: number;
  new_listings: number;
  errors: Array<Record<string, unknown>>;
  started_at: string;
  completed_at: string | null;
}

export interface Activity {
  id: number;
  campaign_id: string;
  scan_id: string | null;
  event_type: string;
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface CampaignStats {
  total_listings: number;
  by_stage: Record<string, number>;
  new_today: number;
  total_scans: number;
}

// ---------------------------------------------------------------------------
// WebSocket message types
// ---------------------------------------------------------------------------

export type WSInbound = {
  type: "message";
  content: string;
  user_id: string;
  context_id: string;
};

export type WSOutbound =
  | { type: "ai"; content: string }
  | { type: "tool_progress"; content: string; metadata?: Record<string, unknown> }
  | { type: "tool_result"; content: string; metadata?: Record<string, unknown> }
  | { type: "error"; content: string }
  | { type: "pong" }
  | { type: "command"; content: string };

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Scan SSE events (real-time progress streaming)
// ---------------------------------------------------------------------------

export type ScanSSEEventType =
  | "started"
  | "progress"
  | "streaming_url"
  | "error"
  | "complete"
  | "done";

export interface ScanSSEEvent {
  type: ScanSSEEventType;
  url: string | null;
  timestamp: number;
  // type-specific fields
  purpose?: string; // progress
  streaming_url?: string; // streaming_url
  run_id?: string; // progress, streaming_url
  message?: string; // error
  job_id?: string; // started
  total_urls?: number; // started
  urls?: string[]; // started
  listings_found?: number; // complete
  errors?: number; // complete
  urls_scanned?: number; // complete
}

export interface ScanProgressStep {
  id: string;
  url: string;
  purpose: string;
  timestamp: number;
  duration?: number;
  status: "running" | "done";
}

export type ScanStreamStatus =
  | "idle"
  | "connecting"
  | "streaming"
  | "complete"
  | "error";

export interface ScanStreamState {
  scanId: string | null;
  status: ScanStreamStatus;
  steps: ScanProgressStep[];
  streamingUrls: Record<string, string>;
  activeUrl: string | null;
  totalUrls: number;
  completedUrls: number;
  listingsFound: number;
  startedAt: number | null;
}

// ---------------------------------------------------------------------------
// Zalo
// ---------------------------------------------------------------------------

export interface ZaloStatus {
  connected: boolean;
  phone_number: string | null;
  error: string | null;
}

// ---------------------------------------------------------------------------
// Outreach
// ---------------------------------------------------------------------------

export type OutreachStatus = "drafted" | "sent" | "failed" | "replied";

export interface OutreachMessage {
  id: string;
  listing_id: string;
  campaign_id: string;
  draft_text: string;
  final_text: string | null;
  status: OutreachStatus;
  landlord_phone: string | null;
  zalo_user_id: string | null;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export const OUTREACH_STATUS_LABELS: Record<OutreachStatus, string> = {
  drafted: "Đã soạn tin",
  sent: "Đã gửi",
  failed: "Lỗi",
  replied: "Đã phản hồi",
};
