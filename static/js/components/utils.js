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
