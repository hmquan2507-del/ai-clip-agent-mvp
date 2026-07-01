import { escapeHtml, formatTime } from "./utils.js";

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
