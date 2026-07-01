import { escapeHtml } from "./utils.js";

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
