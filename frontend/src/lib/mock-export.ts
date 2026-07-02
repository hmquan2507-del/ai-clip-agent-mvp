export type ExportStatus =
  | "not_started"
  | "queued"
  | "rendering"
  | "completed"
  | "failed";

export type ExportPreset = {
  id: string;
  label: string;
  description: string;
  resolution: string;
  format: string;
};

export type ExportHistoryItem = {
  id: string;
  version: string;
  status: ExportStatus;
  format: string;
  resolution: string;
  fileSize: string;
  createdAt: string;
};

export const exportProduction = {
  id: "prd_001",
  title: "Podcast bán hàng tự động",
  status: "approved",
  style: "Podcast",
  duration: "02:34",
};

export const exportPresets: ExportPreset[] = [
  {
    id: "tiktok",
    label: "TikTok / Reels",
    description: "Vertical short video optimized for mobile.",
    resolution: "1080x1920",
    format: "MP4",
  },
  {
    id: "youtube",
    label: "YouTube",
    description: "Landscape video for standard YouTube upload.",
    resolution: "1920x1080",
    format: "MP4",
  },
  {
    id: "linkedin",
    label: "LinkedIn",
    description: "Business-focused square video.",
    resolution: "1080x1080",
    format: "MP4",
  },
];

export const exportHistory: ExportHistoryItem[] = [
  {
    id: "exp_001",
    version: "v1",
    status: "completed",
    format: "MP4",
    resolution: "1080x1920",
    fileSize: "42.6 MB",
    createdAt: "8 phút trước",
  },
  {
    id: "exp_002",
    version: "v0",
    status: "failed",
    format: "MP4",
    resolution: "1080x1920",
    fileSize: "-",
    createdAt: "20 phút trước",
  },
];

export const exportStatusLabel: Record<ExportStatus, string> = {
  not_started: "Not Started",
  queued: "Queued",
  rendering: "Rendering",
  completed: "Completed",
  failed: "Failed",
};

export const exportStatusTone: Record<
  ExportStatus,
  "neutral" | "success" | "warning" | "danger" | "info" | "violet"
> = {
  not_started: "neutral",
  queued: "warning",
  rendering: "violet",
  completed: "success",
  failed: "danger",
};