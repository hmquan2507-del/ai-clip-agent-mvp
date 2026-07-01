import { escapeHtml, formatDate, statusLabel } from "./utils.js";

export function renderDashboardMetrics(elements, data) {
  elements.accountName.textContent = data.account.name;
  elements.planName.textContent = data.account.plan;
  elements.metricJobs.textContent = data.stats.jobs;
  elements.metricClips.textContent = data.stats.clips;
  elements.metricQuota.textContent = `${data.stats.quota_used}/${data.stats.quota_monthly}`;
  elements.sidebarQuota.textContent = `${data.stats.quota_used}/${data.stats.quota_monthly}`;
  elements.metricModules.textContent = `${data.stats.workspace_modules} bước`;
}

export function renderJobs(container, jobs) {
  if (!jobs.length) {
    container.className = "jobs-table empty";
    container.textContent = "Chưa có job nào.";
    return;
  }
  container.className = "jobs-table";
  container.innerHTML = jobs
    .map(
      (job) => `
        <button class="job-row" type="button" data-job-id="${escapeHtml(job.job_id)}">
          <strong title="${escapeHtml(job.title || job.filename)}">${escapeHtml(job.title || job.filename)}</strong>
          <span>${escapeHtml(job.mode || "auto")} · ${escapeHtml(job.style || "talking-head")}</span>
          <span>${statusLabel(job.status)} · ${job.output_count} clip</span>
          <span>${formatDate(job.created_at)}</span>
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
