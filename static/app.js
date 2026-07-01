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
import { clipFromEditor, collectClipEdits, selectedClipIds } from "./js/lib/clip-edits.js";
import { elements } from "./js/lib/dom.js";
import { fetchDashboard, fetchJob, renderSelectedClips, uploadJob } from "./js/lib/api.js";
import { clearQueuePoll, getCurrentJob, setCurrentJob, setQueuePoll } from "./js/lib/state.js";

async function loadDashboard() {
  const data = await fetchDashboard();
  renderDashboardMetrics(elements.dashboard, data);
  renderJobs(elements.jobsTable, data.recent_jobs);
}

async function loadJob(jobId, { focus = true } = {}) {
  const job = await fetchJob(jobId);
  showJob(job);
  elements.uploadStatus.textContent = `Đã mở lại job ${job.title || job.filename}.`;
  if (focus) document.querySelector("#clips")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showJob(job) {
  setCurrentJob(job);
  elements.renderBtn.disabled = !job.suggestions?.length;
  renderAnalysis(elements.analysisGrid, job);
  renderSuggestions(elements.suggestions, job);
  renderWorkspace(elements.workspace, job.editor_workspace, job.suggestions?.[0]?.id || 1);
  renderTranscript(elements.transcriptBox, job.transcript);
  renderOutputs(elements.outputsGrid, job.outputs || []);
  renderTimelinePreview(elements.timelinePreview, job.suggestions?.[0]);
  updateQueueStatus(job);
}

function updateQueueStatus(job) {
  clearQueuePoll();
  const taskText = renderTasks(job.render_tasks || []);
  if (taskText) elements.uploadStatus.textContent = taskText;
  const hasOpenTask = (job.render_tasks || []).some((task) => ["pending", "processing"].includes(task.status));
  if (!hasOpenTask) return;
  setQueuePoll(window.setInterval(refreshCurrentJob, 4000));
}

async function refreshCurrentJob() {
  const currentJob = getCurrentJob();
  if (!currentJob) return;
  try {
    const refreshed = await fetchJob(currentJob.job_id);
    showJob(refreshed);
    await loadDashboard();
  } catch (error) {
    elements.uploadStatus.textContent = error.message;
    clearQueuePoll();
  }
}

function bindSuggestionEditor() {
  elements.suggestions.addEventListener("input", (event) => {
    const editor = event.target.closest(".clip-editor");
    renderTimelinePreview(elements.timelinePreview, clipFromEditor(editor, getCurrentJob()));
  });

  elements.suggestions.addEventListener("change", (event) => {
    const card = event.target.closest(".clip-card");
    if (!card) return;
    const editor = card.querySelector(".clip-editor");
    const clip = clipFromEditor(editor, getCurrentJob());
    renderTimelinePreview(elements.timelinePreview, clip);
    renderEditSteps(elements.workspace.editSteps, getCurrentJob()?.editor_workspace, clip?.id || 1);
  });
}

function bindJobsTable() {
  elements.jobsTable.addEventListener("click", async (event) => {
    const row = event.target.closest("[data-job-id]");
    if (!row) return;
    elements.uploadStatus.textContent = "Đang mở lại job...";
    try {
      await loadJob(row.dataset.jobId);
    } catch (error) {
      elements.uploadStatus.textContent = error.message;
    }
  });
}

function bindUploadForm() {
  elements.videoInput.addEventListener("change", () => {
    renderVideoPreview(elements.videoPreviewPanel, elements.videoInput.files?.[0]);
  });

  elements.uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearQueuePoll();
    elements.uploadStatus.textContent = "Đang upload và phân tích video...";
    elements.renderBtn.disabled = true;
    try {
      const data = await uploadJob(new FormData(elements.uploadForm));
      elements.uploadStatus.textContent = `Đã phân tích video ${Math.round(data.duration)} giây.`;
      showJob(data);
      await loadDashboard();
    } catch (error) {
      elements.uploadStatus.textContent = error.message;
    }
  });
}

function bindRenderButton() {
  elements.renderBtn.addEventListener("click", async () => {
    const currentJob = getCurrentJob();
    if (!currentJob) return;
    const selected = selectedClipIds(elements.suggestions);
    if (!selected.length) {
      elements.uploadStatus.textContent = "Anh chọn ít nhất 1 clip để render.";
      return;
    }
    elements.renderBtn.disabled = true;
    elements.renderBtn.textContent = "Đang render...";
    elements.uploadStatus.textContent = "Đang xuất clip dọc 1080x1920 bằng ffmpeg...";
    try {
      const data = await renderSelectedClips(currentJob.job_id, selected, collectClipEdits(elements.suggestions));
      if (data.queued) {
        elements.uploadStatus.textContent = `Đã đưa ${data.tasks.length} clip vào render queue.`;
        setCurrentJob({ ...currentJob, render_tasks: data.tasks });
        updateQueueStatus(getCurrentJob());
        await loadDashboard();
        return;
      }
      renderOutputs(elements.outputsGrid, data.outputs);
      elements.uploadStatus.textContent = `Đã render ${data.outputs.length} clip.`;
      await loadJob(currentJob.job_id, { focus: false });
      await loadDashboard();
    } catch (error) {
      elements.uploadStatus.textContent = error.message;
    } finally {
      elements.renderBtn.disabled = false;
      elements.renderBtn.textContent = "Render clip đã chọn";
    }
  });
}

function boot() {
  bindSuggestionEditor();
  bindJobsTable();
  bindUploadForm();
  bindRenderButton();
  loadDashboard().catch(() => {
    elements.jobsTable.className = "jobs-table empty";
    elements.jobsTable.textContent = "Chưa load được dữ liệu dashboard.";
  });
}

boot();
