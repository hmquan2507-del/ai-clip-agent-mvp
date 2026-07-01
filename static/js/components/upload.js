import { escapeHtml } from "./utils.js";

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
