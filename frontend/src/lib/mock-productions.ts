export type ProductionStatus =
  | "draft"
  | "uploaded"
  | "processing"
  | "review_ready"
  | "approved"
  | "rendering"
  | "exported"
  | "failed";

export type Production = {
  id: string;
  title: string;
  description: string;
  status: ProductionStatus;
  style: string;
  duration: string;
  progress: number;
  updatedAt: string;
};

export const productions: Production[] = [
  {
    id: "prd_001",
    title: "Podcast bán hàng tự động",
    description: "Highlight ngắn từ podcast cho nội dung social.",
    status: "review_ready",
    style: "Podcast",
    duration: "02:34",
    progress: 100,
    updatedAt: "5 phút trước",
  },
  {
    id: "prd_002",
    title: "AI workflow education short",
    description: "Video giáo dục dạng slide ngắn cho TikTok.",
    status: "processing",
    style: "Education",
    duration: "01:18",
    progress: 68,
    updatedAt: "12 phút trước",
  },
  {
    id: "prd_003",
    title: "Luxury real estate showcase",
    description: "Video giới thiệu bất động sản phong cách luxury.",
    status: "uploaded",
    style: "Real Estate",
    duration: "03:42",
    progress: 28,
    updatedAt: "28 phút trước",
  },
];

export const activityItems = [
  {
    id: "act_001",
    title: "Production ready for review",
    description: "Podcast bán hàng tự động đã sẵn sàng để review.",
    time: "5 phút trước",
  },
  {
    id: "act_002",
    title: "AI processing started",
    description: "AI workflow education short đang được xử lý.",
    time: "12 phút trước",
  },
  {
    id: "act_003",
    title: "Upload completed",
    description: "Luxury real estate showcase đã upload xong.",
    time: "28 phút trước",
  },
];

export const statusLabel: Record<ProductionStatus, string> = {
  draft: "Draft",
  uploaded: "Uploaded",
  processing: "Processing",
  review_ready: "Review Ready",
  approved: "Approved",
  rendering: "Rendering",
  exported: "Exported",
  failed: "Failed",
};

export const statusTone: Record<
  ProductionStatus,
  "neutral" | "success" | "warning" | "danger" | "info" | "violet"
> = {
  draft: "neutral",
  uploaded: "info",
  processing: "violet",
  review_ready: "success",
  approved: "success",
  rendering: "warning",
  exported: "success",
  failed: "danger",
};