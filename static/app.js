import {
  renderAnalysis,
  renderDashboardMetrics,
  renderEditSteps,
  renderJobs,
  renderOutputs,
  renderSuggestions,
  renderTasks,
  renderTimelinePreview,
  renderTranscript,
  renderVideoPreview,
  renderWorkspace,
} from "./components.js";

let currentJob = null;
let queuePoll = null;

const uploadForm = document.querySelector("#uploadForm");
const uploadStatus = document.querySelector("#uploadStatus");
const videoInput = uploadForm.querySelector('input[type="file"]');
const videoPreviewPanel = document.querySelector("#videoPreviewPanel");
const analysisGrid = document.querySelector("#analysisGrid");
const suggestions = document.querySelector("#suggestions");
const renderBtn = document.querySelector("#renderBtn");
const outputsGrid = document.querySelector("#outputsGrid");
const jobsTable = document.querySelector("#jobsTable");
const workspaceMode = document.querySelector("#workspaceMode");
const assetBin = document.querySelector("#assetBin");
const timelineTracks = document.querySelector("#timelineTracks");
const editSteps = document.querySelector("#editSteps");
const transcriptBox = document.querySelector("#transcriptBox");
const timelinePreview = document.querySelector("#timelinePreview");

const dashboardElements = {
  accountName: document.querySelector("#accountName"),
  planName: document.querySelector("#planName"),
  metricJobs: document.querySelector("#metricJobs"),
  metricClips: document.querySelector("#metricClips"),
  metricQuota: document.querySelector("#metricQuota"),
  metricModules: document.querySelector("#metricModules"),
  sidebarQuota: document.querySelector("#sidebarQuota"),
};

const workspaceElements = {
  workspaceMode,
  assetBin,
  timelineTracks,
  editSteps,
};

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Có lỗi xảy ra");
  return data;
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  renderDashboardMetrics(dashboardElements, data);
  renderJobs(jobsTable, data.recent_jobs);
}

async function loadJob(jobId, { focus = true } = {}) {
  const job = await api(`/api/jobs/${encodeURIComponent(jobId)}`);
  showJob(job);
  uploadStatus.textContent = `Đã mở lại job ${job.title || job.filename}.`;
  if (focus) document.querySelector("#clips")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showJob(job) {
  currentJob = job;
  renderBtn.disabled = !job.suggestions?.length;
  renderAnalysis(analysisGrid, job);
  renderSuggestions(suggestions, job);
  renderWorkspace(workspaceElements, job.editor_workspace, job.suggestions?.[0]?.id || 1);
  renderTranscript(transcriptBox, job.transcript);
  renderOutputs(outputsGrid, job.outputs || []);
  renderTimelinePreview(timelinePreview, job.suggestions?.[0]);
  updateQueueStatus(job);
}

function updateQueueStatus(job) {
  clearQueuePoll();
  const taskText = renderTasks(null, job.render_tasks || []);
  if (taskText) uploadStatus.textContent = taskText;
  const hasOpenTask = (job.render_tasks || []).some((task) => ["pending", "processing"].includes(task.status));
  if (hasOpenTask) {
    queuePoll = window.setInterval(async () => {
      if (!currentJob) return;
      try {
        const refreshed = await api(`/api/jobs/${encodeURIComponent(currentJob.job_id)}`);
        showJob(refreshed);
        await loadDashboard();
      } catch (error) {
        uploadStatus.textContent = error.message;
        clearQueuePoll();
      }
    }, 4000);
  }
}

function clearQueuePoll() {
  if (queuePoll) window.clearInterval(queuePoll);
  queuePoll = null;
}

function clipFromEditor(editor) {
  if (!editor) return null;
  const clipId = Number(editor.dataset.clipId);
  const base = currentJob?.suggestions?.find((clip) => Number(clip.id) === clipId) || {};
  const data = { ...base, edit_plan: { ...(base.edit_plan || {}) } };
  editor.querySelectorAll("[data-field]").forEach((input) => {
    const field = input.dataset.field;
    if (field === "broll" || field === "sfx") {
      data.edit_plan[field] = input.value.split("\n").map((item) => item.trim()).filter(Boolean);
    } else if (field === "subtitle_style" || field === "music") {
      data.edit_plan[field] = input.value;
    } else {
      data[field] = input.value;
    }
  });
  return data;
}

function collectClipEdits() {
  return [...suggestions.querySelectorAll(".clip-editor")].map((editor) => {
    const edit = { id: Number(editor.dataset.clipId) };
    editor.querySelectorAll("[data-field]").forEach((input) => {
      edit[input.dataset.field] = input.value;
    });
    return edit;
  });
}

suggestions.addEventListener("input", (event) => {
  const editor = event.target.closest(".clip-editor");
  renderTimelinePreview(timelinePreview, clipFromEditor(editor));
});

suggestions.addEventListener("change", (event) => {
  const card = event.target.closest(".clip-card");
  if (!card) return;
  const editor = card.querySelector(".clip-editor");
  const clip = clipFromEditor(editor);
  renderTimelinePreview(timelinePreview, clip);
  renderEditSteps(editSteps, currentJob?.editor_workspace, clip?.id || 1);
});

jobsTable.addEventListener("click", async (event) => {
  const row = event.target.closest("[data-job-id]");
  if (!row) return;
  uploadStatus.textContent = "Đang mở lại job...";
  try {
    await loadJob(row.dataset.jobId);
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
});

videoInput.addEventListener("change", () => {
  renderVideoPreview(videoPreviewPanel, videoInput.files?.[0]);
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearQueuePoll();
  uploadStatus.textContent = "Đang upload và phân tích video...";
  renderBtn.disabled = true;
  const formData = new FormData(uploadForm);
  try {
    const data = await api("/api/upload", {
      method: "POST",
      body: formData,
    });
    uploadStatus.textContent = `Đã phân tích video ${Math.round(data.duration)} giây.`;
    showJob(data);
    await loadDashboard();
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
});

renderBtn.addEventListener("click", async () => {
  if (!currentJob) return;
  const selected = [...suggestions.querySelectorAll(".clip-card > input:checked")].map((input) => Number(input.value));
  if (!selected.length) {
    uploadStatus.textContent = "Anh chọn ít nhất 1 clip để render.";
    return;
  }
  renderBtn.disabled = true;
  renderBtn.textContent = "Đang render...";
  uploadStatus.textContent = "Đang xuất clip dọc 1080x1920 bằng ffmpeg...";
  try {
    const data = await api("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: currentJob.job_id, selected, edits: collectClipEdits() }),
    });
    if (data.queued) {
      uploadStatus.textContent = `Đã đưa ${data.tasks.length} clip vào render queue.`;
      currentJob.render_tasks = data.tasks;
      updateQueueStatus(currentJob);
      await loadDashboard();
      return;
    }
    renderOutputs(outputsGrid, data.outputs);
    uploadStatus.textContent = `Đã render ${data.outputs.length} clip.`;
    await loadJob(currentJob.job_id, { focus: false });
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
