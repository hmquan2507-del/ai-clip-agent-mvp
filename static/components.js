export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function formatTime(seconds) {
  const m = Math.floor(Number(seconds || 0) / 60);
  const s = Math.floor(Number(seconds || 0) % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function formatDate(ts) {
  if (!ts) return "-";
  return new Date(ts * 1000).toLocaleString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
  });
}

export function statusLabel(status) {
  const map = {
    done: "Hoàn tất",
    failed: "Lỗi",
    pending: "Đang chờ",
    planned: "Đang chờ",
    processing: "Đang xử lý",
    queued: "Đang xếp hàng",
    ready: "Sẵn sàng",
    rendered: "Đã xuất",
    suggested: "Đã đề xuất",
  };
  return map[status] || status || "Đang chờ";
}

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

export function renderVideoPreview(container, file) {
  if (!file) {
    container.className = "video-preview empty";
    container.textContent = "Chưa chọn video để xem preview.";
    return;
  }
  const url = URL.createObjectURL(file);
  container.className = "video-preview";
  container.innerHTML = `
    <video src="${url}" controls playsinline muted></video>
    <div>
      <strong>${escapeHtml(file.name)}</strong>
      <span>${(file.size / 1024 / 1024).toFixed(1)} MB · ${escapeHtml(file.type || "video")}</span>
    </div>
  `;
}

export function renderAnalysis(container, job) {
  const analysis = job.video_analysis;
  if (!analysis) return;
  container.className = "analysis-grid";
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
  container.innerHTML = items
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

export function renderSuggestions(container, job) {
  if (!job.suggestions?.length) {
    container.className = "suggestions empty";
    container.textContent = "Job này chưa có clip đề xuất.";
    return;
  }
  container.className = "suggestions";
  container.innerHTML = job.suggestions
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
            ${renderClipPlan(clip.edit_plan)}
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
}

function renderClipPlan(plan) {
  if (!plan) return "";
  return `
    <div class="clip-plan">
      <label>Subtitle style
        <input data-field="subtitle_style" value="${escapeHtml(plan.subtitle_style || "")}" />
      </label>
      <label>B-roll
        <textarea data-field="broll" rows="3">${escapeHtml((plan.broll || []).join("\n"))}</textarea>
      </label>
      <label>SFX
        <textarea data-field="sfx" rows="2">${escapeHtml((plan.sfx || []).join("\n"))}</textarea>
      </label>
      <label>Music
        <input data-field="music" value="${escapeHtml(plan.music || "")}" />
      </label>
    </div>
  `;
}

export function renderTranscript(container, transcript) {
  if (!transcript || !transcript.segments?.length) {
    container.className = "transcript-box empty";
    container.textContent = "Chưa có transcript.";
    return;
  }
  container.className = "transcript-box";
  container.innerHTML = `
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

export function renderWorkspace(elements, workspace, clipId = 1) {
  if (!workspace) return;
  elements.workspaceMode.textContent = workspace.mode_label || "Editor workspace";
  elements.assetBin.className = "asset-bin";
  elements.assetBin.innerHTML = workspace.assets.map(renderAsset).join("");
  elements.timelineTracks.className = "timeline-tracks";
  elements.timelineTracks.innerHTML = workspace.tracks.map(renderTrack).join("");
  renderEditSteps(elements.editSteps, workspace, clipId);
}

function renderAsset(asset) {
  return `
    <article class="asset-item">
      <span class="asset-type">${escapeHtml(asset.type)}</span>
      <strong>${escapeHtml(asset.name)}</strong>
      <small>${escapeHtml(asset.notes || "")}</small>
      <em class="state ${escapeHtml(asset.status)}">${statusLabel(asset.status)}</em>
    </article>
  `;
}

function renderTrack(track) {
  return `
    <div class="track-row">
      <strong>${escapeHtml(track.name)}</strong>
      <span style="--items:${Math.max(1, Number(track.items) || 1)}"></span>
      <em>${statusLabel(track.status)}</em>
    </div>
  `;
}

export function renderEditSteps(container, workspace, clipId = 1) {
  const steps = (workspace?.steps || []).filter((step) => Number(step.clip_id) === Number(clipId));
  if (!steps.length) {
    container.className = "edit-steps empty";
    container.textContent = "Chưa có bước edit cho clip.";
    return;
  }
  container.className = "edit-steps";
  container.innerHTML = steps
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

export function renderTimelinePreview(container, clip) {
  if (!clip) {
    container.className = "timeline-preview empty";
    container.textContent = "Chọn clip để xem timeline preview.";
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
  container.className = "timeline-preview";
  container.innerHTML = rows
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

export function renderOutputs(container, items = []) {
  if (!items.length) {
    container.className = "output-grid empty";
    container.textContent = "Chưa có video xuất ra trong phiên này.";
    return;
  }
  container.className = "output-grid";
  container.innerHTML = items
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

export function renderTasks(container, tasks = []) {
  if (!tasks.length) return "";
  return tasks
    .map((task) => `Clip ${task.clip_id}: ${statusLabel(task.status)}`)
    .join(" · ");
}
