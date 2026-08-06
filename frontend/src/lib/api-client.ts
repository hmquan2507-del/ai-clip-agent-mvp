export interface ApiProduction {
  id: string;
  title: string;
  description?: string;
  status: "draft" | "uploaded" | "processing" | "review_ready" | "approved" | "rendering" | "exported" | "failed";
  style?: string;
  duration?: string;
  progress?: number;
  updatedAt?: string;
}

export interface ApiAiBrainRunResult {
  production_id: string;
  status: "started" | "running" | "completed" | "error";
  results?: Record<string, unknown>;
}

export interface ApiRenderJob {
  job_id: string;
  production_id: string;
  status: "queued" | "rendering" | "completed" | "failed";
  progress: number;
}

export interface ApiProductionAsset {
  id: string;
  production_id: string;
  filename: string;
  mime_type: string | null;
  size_bytes: number | null;
  storage_path: string;
  duration: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  video_codec: string | null;
  audio_codec: string | null;
  has_audio: boolean | null;
  media_url: string;
  created_at: string;
  updated_at: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/** The backend serves uploaded/rendered files under /media/*, relative to
 * its own origin (not the frontend's) - resolve it to an absolute URL. */
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith("/media/")) {
    const origin = API_BASE_URL.replace(/\/api\/v1\/?$/, "");
    return `${origin}${url}`;
  }
  return url;
}

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });
    if (!res.ok) {
      console.warn(`API request failed: ${res.status} ${res.statusText}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`API network connection offline: ${endpoint}`, err);
    return null;
  }
}

export const apiClient = {
  baseUrl: API_BASE_URL,

  async getProductions(): Promise<ApiProduction[] | null> {
    return fetchJson<ApiProduction[]>("/productions");
  },

  async getProduction(id: string): Promise<ApiProduction | null> {
    return fetchJson<ApiProduction>(`/productions/${encodeURIComponent(id)}`);
  },

  async createProduction(data: { title: string; description?: string; style?: string; workspace_id?: string }): Promise<ApiProduction | null> {
    return fetchJson<ApiProduction>("/productions", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: data.workspace_id ?? "00000000-0000-0000-0000-000000000001",
        title: data.title,
        description: data.description,
        style: data.style,
      }),
    });
  },

  async runAiBrain(productionId: string): Promise<ApiAiBrainRunResult | null> {
    return fetchJson<ApiAiBrainRunResult>(`/productions/${encodeURIComponent(productionId)}/ai-brain/run`, {
      method: "POST",
    });
  },

  async getProductionAssets(productionId: string): Promise<ApiProductionAsset[] | null> {
    return fetchJson<ApiProductionAsset[]>(
      `/uploads/production/${encodeURIComponent(productionId)}`,
    );
  },

  async uploadSourceVideo(productionId: string, file: File): Promise<{ id?: string; asset_id?: string } | null> {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_BASE_URL}/uploads/production/${encodeURIComponent(productionId)}/source-video`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async runTimelineComposer(productionId: string): Promise<{ status?: string } | null> {
    return fetchJson<{ status?: string }>(`/productions/${encodeURIComponent(productionId)}/timeline-composer/run`, {
      method: "POST",
    });
  },

  async submitRenderJob(contract: { production_id: string; snapshot_id: string; checksum: string }): Promise<ApiRenderJob | null> {
    return fetchJson<ApiRenderJob>("/render/jobs", {
      method: "POST",
      body: JSON.stringify(contract),
    });
  },
};
