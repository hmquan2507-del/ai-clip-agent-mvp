export function clipFromEditor(editor, currentJob) {
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

export function collectClipEdits(suggestionsContainer) {
  return [...suggestionsContainer.querySelectorAll(".clip-editor")].map((editor) => {
    const edit = { id: Number(editor.dataset.clipId) };
    editor.querySelectorAll("[data-field]").forEach((input) => {
      edit[input.dataset.field] = input.value;
    });
    return edit;
  });
}

export function selectedClipIds(suggestionsContainer) {
  return [...suggestionsContainer.querySelectorAll(".clip-card > input:checked")]
    .map((input) => Number(input.value));
}
