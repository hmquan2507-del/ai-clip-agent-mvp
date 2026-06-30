let currentJob = null;

const uploadForm = document.querySelector("#uploadForm");
const uploadStatus = document.querySelector("#uploadStatus");
const suggestions = document.querySelector("#suggestions");
const renderBtn = document.querySelector("#renderBtn");
const outputsGrid = document.querySelector("#outputsGrid");
const jobsTable = document.querySelector("#jobsTable");
const workspaceMode = document.querySelector("#workspaceMode");
const assetBin = document.querySelector("#assetBin");
const timelineTracks = document.querySelector("#timelineTracks");
const editSteps = document.querySelector("#editSteps");
const transcriptBox = document.querySelector("#transcriptBox");

const accountName = document.querySelector("#accountName");
const planName = document.querySelector("#planName");
const metricJobs = document.querySelector("#metricJobs");
const metricClips = document.querySelector("#metricClips");
const metricQuota = document.querySelector("#metricQuota");
const metricModules = document.querySelector("#metricModules");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function formatDate(ts) {
  if (!ts) return "-";
  return new Date(ts * 1000).toLocaleString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
  });
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  const data = await response.json();
  accountName.textContent = data.account.name;
  planName.textContent = data.account.plan;
  metricJobs.textContent = data.stats.jobs;
  metricClips.textContent = data.stats.clips;
  metricQuota.textContent = `${data.stats.quota_used}/${data.stats.quota_monthly}`;
  metricModules.textContent = `${data.stats.workspace_modules} bước`;
  renderJobs(data.recent_jobs);
}

function renderJobs(jobs) {
  if (!jobs.length) {
    jobsTable.className = "jobs-table empty";
    jobsTable.textContent = "Chưa có job nào.";
    return;
  }
  jobsTable.className = "jobs-table";
  jobsTable.innerHTML = jobs
    .map(
      (job) => `
        <article class="job-row">
          <strong title="${escapeHtml(job.title || job.filename)}">${escapeHtml(job.title || job.filename)}</strong>
          <span>${escapeHtml(job.mode || "auto")} · ${escapeHtml(job.style || "talking-head")}</span>
          <span>${job.output_count} clip · ${job.asset_count || 0} asset</span>
          <span>${formatDate(job.created_at)}</span>
        </article>
      `
    )
    .join("");
}

function renderSuggestions(job) {
  currentJob = job;
  renderBtn.disabled = false;
  suggestions.classList.remove("empty");
  renderWorkspace(job.editor_workspace);
  renderTranscript(job.transcript);
  suggestions.innerHTML = job.suggestions
    .map(
      (clip) => `
        <article class="clip-card">
          <input type="checkbox" value="${clip.id}" checked aria-label="Chọn clip ${clip.id}" />
          <div>
            <div class="meta">
              <span>Clip ${clip.id}</span>
              <span>Bắt đầu ${formatTime(clip.start)}</span>
              <span>${Math.round(clip.duration)} giây</span>
            </div>
            <h3>${escapeHtml(clip.hook)}</h3>
            <p><strong>Caption:</strong> ${escapeHtml(clip.caption)}</p>
            <p><strong>CTA:</strong> ${escapeHtml(clip.cta)}</p>
          </div>
        </article>
      `
    )
    .join("");
}

function renderTranscript(transcript) {
  if (!transcript || !transcript.segments?.length) {
    transcriptBox.className = "transcript-box empty";
    transcriptBox.textContent = "Chưa có transcript.";
    return;
  }
  transcriptBox.className = "transcript-box";
  transcriptBox.innerHTML = `
    <div class="transcript-summary">
      <strong>${escapeHtml(transcript.source || "transcript")}</strong>
      <span>${statusLabel(transcript.status)}</span>
      <small>${escapeHtml(transcript.summary || "")}</small>
    </div>
    ${transcript.segments
      .slice(0, 8)
      .map(
        (segment) => `
          <article>
            <time>${formatTime(segment.start)} - ${formatTime(segment.end)}</time>
            <p>${escapeHtml(segment.text)}</p>
          </article>
        `
      )
      .join("")}
  `;
}

function statusLabel(status) {
  const map = {
    ready: "Sẵn sàng",
    planned: "Đang chờ",
    rendered: "Đã xuất",
  };
  return map[status] || status || "Đang chờ";
}

function renderWorkspace(workspace) {
  if (!workspace) return;
  workspaceMode.textContent = workspace.mode_label || "Editor workspace";

  assetBin.className = "asset-bin";
  assetBin.innerHTML = workspace.assets
    .map(
      (asset) => `
        <article class="asset-item">
          <span class="asset-type">${escapeHtml(asset.type)}</span>
          <strong>${escapeHtml(asset.name)}</strong>
          <small>${escapeHtml(asset.notes || "")}</small>
          <em class="state ${escapeHtml(asset.status)}">${statusLabel(asset.status)}</em>
        </article>
      `
    )
    .join("");

  timelineTracks.className = "timeline-tracks";
  timelineTracks.innerHTML = workspace.tracks
    .map(
      (track) => `
        <div class="track-row">
          <strong>${escapeHtml(track.name)}</strong>
          <span style="--items:${Math.max(1, Number(track.items) || 1)}"></span>
          <em>${statusLabel(track.status)}</em>
        </div>
      `
    )
    .join("");

  const firstClipSteps = workspace.steps.filter((step) => step.clip_id === 1);
  editSteps.className = "edit-steps";
  editSteps.innerHTML = firstClipSteps
    .map(
      (step) => `
        <article>
          <span>${String(step.order).padStart(2, "0")}</span>
          <div>
            <strong>${escapeHtml(step.title)}</strong>
            <p>${escapeHtml(step.notes)}</p>
          </div>
          <em class="state ${escapeHtml(step.status)}">${statusLabel(step.status)}</em>
        </article>
      `
    )
    .join("");
}

function renderOutputs(items) {
  outputsGrid.classList.remove("empty");
  outputsGrid.innerHTML = items
    .map(
      (item) => `
        <article class="output-card">
          <video src="${item.url}" controls playsinline></video>
          <a class="download" href="${item.url}" download>Tải ${escapeHtml(item.name)}</a>
        </article>
      `
    )
    .join("");
}

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  uploadStatus.textContent = "Đang upload và phân tích video...";
  renderBtn.disabled = true;
  const formData = new FormData(uploadForm);
  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Upload lỗi");
    uploadStatus.textContent = `Đã phân tích video ${Math.round(data.duration)} giây.`;
    renderSuggestions(data);
    await loadDashboard();
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
});

renderBtn.addEventListener("click", async () => {
  if (!currentJob) return;
  const selected = [...suggestions.querySelectorAll("input:checked")].map((input) => Number(input.value));
  if (!selected.length) {
    uploadStatus.textContent = "Anh chọn ít nhất 1 clip để render.";
    return;
  }
  renderBtn.disabled = true;
  renderBtn.textContent = "Đang render...";
  uploadStatus.textContent = "Đang xuất clip dọc 1080x1920 bằng ffmpeg...";
  try {
    const response = await fetch("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: currentJob.job_id, selected }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Render lỗi");
    renderOutputs(data.outputs);
    uploadStatus.textContent = `Đã render ${data.outputs.length} clip.`;
    await loadDashboard();
  } catch (error) {
    uploadStatus.textContent = error.message;
  } finally {
    renderBtn.disabled = false;
    renderBtn.textContent = "Render clip đã chọn";
  }
});

loadDashboard().catch(() => {
  jobsTable.className = "jobs-table empty";
  jobsTable.textContent = "Chưa load được dữ liệu dashboard.";
});
