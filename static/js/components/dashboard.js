import { escapeHtml, formatDate, statusLabel } from "./utils.js";

export function renderDashboardMetrics(elements, data) {
  elements.accountName.textContent = data.account.name;
  elements.planName.textContent = data.account.plan;
  elements.metricJobs.textContent = data.stats.jobs;
  elements.metricClips.textContent = data.stats.clips;
  elements.metricQuota.textContent = `${data.stats.quota_used}/${data.stats.quota_monthly}`;
  if ("value" in elements.sidebarQuota) {
    elements.sidebarQuota.value = `${data.stats.quota_used}/${data.stats.quota_monthly} credits`;
  } else {
    elements.sidebarQuota.textContent = `${data.stats.quota_used}/${data.stats.quota_monthly}`;
  }
  elements.metricModules.textContent = data.stats.rendering || 0;
}

export function renderJobs(container, jobs) {
  if (!jobs.length) {
    container.className = "project-grid empty";
    container.textContent = "Chưa có project nào.";
    return;
  }
  container.className = "project-grid";
  container.innerHTML = jobs
    .map(
      (job) => `
        <button class="job-row" type="button" data-job-id="${escapeHtml(job.job_id)}">
          <span class="job-thumb" aria-hidden="true"></span>
          <span class="job-main">
            <strong title="${escapeHtml(job.title || job.filename)}">${escapeHtml(job.title || job.filename)}</strong>
            <span>${escapeHtml(job.mode || "auto")} · ${escapeHtml(job.style || "talking-head")}</span>
          </span>
          <span class="status-pill ${job.status === "completed" ? "done" : ""}">${statusLabel(job.status)}</span>
          <span>${job.output_count} clip · ${formatDate(job.created_at)}</span>
        </button>
      `
    )
    .join("");
}

export function renderTasks(tasks = []) {
  if (!tasks.length) return "";
  return tasks
    .map((task) => `Clip ${task.clip_id}: ${statusLabel(task.status)}`)
    .join(" · ");
}

export function renderQueue(container, tasks = []) {
  if (!container) return;
  if (!tasks.length) {
    container.className = "queue-table empty";
    container.textContent = "Render clip để xem hàng đợi.";
    return;
  }
  container.className = "queue-table";
  container.innerHTML = tasks
    .map((task) => {
      const progress = task.status === "done" || task.status === "completed" ? 100 : task.status === "processing" ? 68 : task.status === "failed" ? 0 : 8;
      const pillClass = task.status === "failed" ? "error" : progress === 100 ? "done" : task.status === "pending" ? "queue" : "";
      return `
        <div class="queue-row">
          <strong>Clip ${task.clip_id}</strong>
          <span>${escapeHtml(task.aspect_ratio || "9:16")}</span>
          <span class="status-pill ${pillClass}">${statusLabel(task.status)}</span>
          <span class="progress" aria-label="${progress}%"><span style="--progress:${progress}%"></span></span>
          <span>${progress}%</span>
        </div>
      `;
    })
    .join("");
}
