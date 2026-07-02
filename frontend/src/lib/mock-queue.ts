export type QueueStatus =
  | "queued"
  | "processing"
  | "review_ready"
  | "completed"
  | "failed"
  | "cancelled";

export type QueueProduction = {
  id: string;
  title: string;
  style: string;
  status: QueueStatus;
  stage: string;
  progress: number;
  eta: string;
  updatedAt: string;
};

export type WorkerStatus = {
  id: string;
  name: string;
  role: string;
  status: "online" | "busy" | "idle" | "offline";
  currentTask: string;
};

export const queueProductions: QueueProduction[] = [
  {
    id: "prd_002",
    title: "AI workflow education short",
    style: "Education",
    status: "processing",
    stage: "Highlight Detection",
    progress: 68,
    eta: "3 phút",
    updatedAt: "vừa xong",
  },
  {
    id: "prd_004",
    title: "Business finance reel",
    style: "Finance",
    status: "queued",
    stage: "Waiting for worker",
    progress: 8,
    eta: "9 phút",
    updatedAt: "2 phút trước",
  },
  {
    id: "prd_001",
    title: "Podcast bán hàng tự động",
    style: "Podcast",
    status: "review_ready",
    stage: "Review Ready",
    progress: 100,
    eta: "Sẵn sàng",
    updatedAt: "5 phút trước",
  },
];

export const pipelineSteps = [
  { label: "Upload", status: "done" as const },
  { label: "Transcript", status: "done" as const },
  { label: "Scene Detection", status: "done" as const },
  { label: "Highlight Detection", status: "active" as const },
  { label: "Subtitle", status: "waiting" as const },
  { label: "Review", status: "waiting" as const },
  { label: "Export", status: "waiting" as const },
];

export const workers: WorkerStatus[] = [
  {
    id: "worker_transcript",
    name: "Transcript Worker",
    role: "Speech recognition",
    status: "idle",
    currentTask: "Waiting for job",
  },
  {
    id: "worker_ai",
    name: "AI Analysis Worker",
    role: "Scenes, highlights, prompts",
    status: "busy",
    currentTask: "Highlight Detection",
  },
  {
    id: "worker_subtitle",
    name: "Subtitle Worker",
    role: "Subtitle generation",
    status: "online",
    currentTask: "Ready",
  },
  {
    id: "worker_render",
    name: "Render Worker",
    role: "Preview and export render",
    status: "online",
    currentTask: "Ready",
  },
];

export const queueStatusLabel: Record<QueueStatus, string> = {
  queued: "Queued",
  processing: "Processing",
  review_ready: "Review Ready",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
};

export const queueStatusTone: Record<
  QueueStatus,
  "neutral" | "success" | "warning" | "danger" | "info" | "violet"
> = {
  queued: "warning",
  processing: "violet",
  review_ready: "success",
  completed: "success",
  failed: "danger",
  cancelled: "neutral",
};