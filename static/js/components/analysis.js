import { escapeHtml } from "./utils.js";

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
