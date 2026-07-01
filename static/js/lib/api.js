export async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Có lỗi xảy ra");
  return data;
}

export function fetchDashboard() {
  return api("/api/dashboard");
}

export function fetchJob(jobId) {
  return api(`/api/jobs/${encodeURIComponent(jobId)}`);
}

export function uploadJob(formData) {
  return api("/api/upload", {
    method: "POST",
    body: formData,
  });
}

export function renderSelectedClips(jobId, selected, edits) {
  return api("/api/render", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id: jobId, selected, edits }),
  });
}
