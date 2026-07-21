export type ExportRenderContract = {
  contract_version?: string;
  snapshot_id: string;
  production_id: string;
  timeline_revision: number;
  timeline: Record<string, unknown>;
  created_at: string;
  render_options?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  checksum: string;
  requested_by?: string | null;
  correlation_id?: string | null;
};

export type ExportSubmissionData = {
  queue_job_id: string;
  production_id: string;
  snapshot_id: string;
  timeline_revision: number;
  idempotency_key: string;
  duplicate: boolean;
};

export type ExportSubmissionResponse = {
  success: boolean;
  data: ExportSubmissionData | null;
  error_code: string | null;
  error: string | null;
};

export type ExportRenderStatusData = {
  queue_job_id: string;
  production_id: string;
  queue_type: string;
  status: string;
  progress: number;
  error: string | null;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  updated_at: string | null;
};

export type ExportRenderStatusResponse = {
  success: boolean;
  data: ExportRenderStatusData;
};

export type ExportRuntimePhase =
  | "idle"
  | "submitting"
  | "queued"
  | "polling"
  | "completed"
  | "failed"
  | "cancelled";

export type ExportRuntimeState = {
  phase: ExportRuntimePhase;
  submission: ExportSubmissionData | null;
  status: ExportRenderStatusData | null;
  error: string | null;
};

export const initialExportRuntimeState: ExportRuntimeState = {
  phase: "idle",
  submission: null,
  status: null,
  error: null,
};
