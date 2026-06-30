let currentJob = null;

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

function renderVideoPreview(file) {
  if (!file) {
    videoPreviewPanel.className = "video-preview empty";
    videoPreviewPanel.textContent = "Chưa chọn video để xem preview.";
    return;
  }
  const url = URL.createObjectURL(file);
  videoPreviewPanel.className = "video-preview";
  videoPreviewPanel.innerHTML = `
    <video src="${url}" controls playsinline muted></video>
    <div>
      <strong>${escapeHtml(file.name)}</strong>
      <span>${(file.size / 1024 / 1024).toFixed(1)} MB · ${escapeHtml(file.type || "video")}</span>
    </div>
  `;
}

function renderAnalysis(job) {
  const analysis = job.video_analysis;
  if (!analysis) return;
  analysisGrid.className = "analysis-grid";
  const items = [
    ["Thời lượng", `${Math.round(analysis.duration)} giây`],
    ["Kích thước", `${analysis.width || "-"}x${analysis.height || "-"}`],
    ["FPS", analysis.fps || "-"],
    ["Tỷ lệ", analysis.is_vertical ? "Dọc" : "Ngang/vuông"],
    ["Video codec", analysis.video_codec || "-"],
    ["Audio", analysis.has_audio ? analysis.audio_codec || "Có" : "Không có audio"],
    ["Kiểu xử lý", analysis.recommended_action || "-"],
    ["Storage", `${job.storage_provider || "local"} · ${job.storage_key || job.filename}`],
  ];
  analysisGrid.innerHTML = items
    .map(
      ([label, value]) => `
        <article>
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `
    )
    .join("");
}

function renderSuggestions(job) {
  currentJob = job;
  renderBtn.disabled = false;
  suggestions.classList.remove("empty");
  renderAnalysis(job);
  renderWorkspace(job.editor_workspace);
  renderTranscript(job.transcript);
  suggestions.innerHTML = job.suggestions
    .map(
      (clip) => `
        <article class="clip-card">
          <input type="checkbox" value="${clip.id}" checked aria-label="Chọn clip ${clip.id}" />
          <div class="clip-editor" data-clip-id="${clip.id}">
            <div class="meta">
              <span>Clip ${clip.id}</span>
              <span>${Number(clip.highlight_score || 50)} điểm</span>
              <span>Bắt đầu ${formatTime(clip.start)}</span>
              <span>${Math.round(clip.duration)} giây</span>
            </div>
            <label>Hook
              <textarea data-field="hook" rows="2">${escapeHtml(clip.hook)}</textarea>
            </label>
            <p><strong>Lý do chọn:</strong> ${escapeHtml(clip.reason || "Đoạn phù hợp để edit thành clip ngắn.")}</p>
            ${clip.keywords?.length ? `<p><strong>Keyword:</strong> ${clip.keywords.map(escapeHtml).join(", ")}</p>` : ""}
            ${clip.edit_plan ? `
              <div class="clip-plan">
                <label>Subtitle style
                  <input data-field="subtitle_style" value="${escapeHtml(clip.edit_plan.subtitle_style || "")}" />
                </label>
                <label>B-roll
                  <textarea data-field="broll" rows="3">${escapeHtml((clip.edit_plan.broll || []).join("\n"))}</textarea>
                </label>
                <label>SFX
                  <textarea data-field="sfx" rows="2">${escapeHtml((clip.edit_plan.sfx || []).join("\n"))}</textarea>
                </label>
                <label>Music
                  <input data-field="music" value="${escapeHtml(clip.edit_plan.music || "")}" />
                </label>
              </div>
            ` : ""}
            <label>Caption
              <textarea data-field="caption" rows="2">${escapeHtml(clip.caption)}</textarea>
            </label>
            <label>CTA
              <input data-field="cta" value="${escapeHtml(clip.cta)}" />
            </label>
          </div>
        </article>
      `
    )
    .join("");
  renderTimelinePreview(job.suggestions[0]);
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

function renderTimelinePreview(clip) {
  if (!clip) {
    timelinePreview.className = "timeline-preview empty";
    timelinePreview.textContent = "Chọn clip để xem timeline preview.";
    return;
  }
  const plan = clip.edit_plan || {};
  const duration = Math.max(8, Number(clip.duration) || 30);
  const brollItems = plan.broll?.length ? plan.broll : ["B-roll gợi ý"];
  const sfxItems = plan.sfx?.length ? plan.sfx : ["SFX hook", "SFX chuyển ý"];
  const rows = [
    { label: "Footage", items: [{ text: `Clip ${clip.id} · ${Math.round(duration)}s`, start: 0, width: 100, type: "footage" }] },
    { label: "Subtitle", items: [
      { text: clip.hook || "Hook", start: 0, width: 28, type: "subtitle" },
      { text: clip.caption || "Caption", start: 30, width: 42, type: "subtitle" },
      { text: clip.cta || "CTA", start: 76, width: 22, type: "subtitle" },
    ] },
    { label: "B-roll", items: brollItems.slice(0, 3).map((item, index) => ({ text: item, start: 12 + index * 26, width: 22, type: "broll" })) },
    { label: "SFX", items: sfxItems.slice(0, 3).map((item, index) => ({ text: item, start: 4 + index * 34, width: 10, type: "sfx" })) },
    { label: "Music", items: [{ text: plan.music || "Nhạc nền", start: 0, width: 100, type: "music" }] },
  ];
  timelinePreview.className = "timeline-preview";
  timelinePreview.innerHTML = rows
    .map(
      (row) => `
        <div class="preview-row">
          <strong>${escapeHtml(row.label)}</strong>
          <div>
            ${row.items
              .map(
                (item) => `
                  <span class="${escapeHtml(item.type)}" style="--start:${item.start};--width:${item.width}">
                    ${escapeHtml(item.text)}
                  </span>
                `
              )
              .join("")}
          </div>
        </div>
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
  renderTimelinePreview(clipFromEditor(editor));
});

suggestions.addEventListener("change", (event) => {
  const card = event.target.closest(".clip-card");
  if (!card) return;
  renderTimelinePreview(clipFromEditor(card.querySelector(".clip-editor")));
});

videoInput.addEventListener("change", () => {
  renderVideoPreview(videoInput.files?.[0]);
});

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
      body: JSON.stringify({ job_id: currentJob.job_id, selected, edits: collectClipEdits() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Render lỗi");
    if (data.queued) {
      uploadStatus.textContent = `Đã đưa ${data.tasks.length} clip vào render queue.`;
      await loadDashboard();
      return;
    }
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
