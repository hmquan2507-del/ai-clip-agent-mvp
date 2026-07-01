import { escapeHtml, formatTime, statusLabel } from "./utils.js";

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
