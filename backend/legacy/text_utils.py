from config import FONT

def wrap(text, limit=24):
    words = str(text or "").strip().split()
    lines = []
    line = []
    length = 0
    for word in words:
        next_len = length + len(word) + (1 if line else 0)
        if line and next_len > limit:
            lines.append(" ".join(line))
            line = [word]
            length = len(word)
        else:
            line.append(word)
            length = next_len
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines[:3])

def drawtext_escape(text, limit=24):
    text = wrap(text, limit=limit)
    return escape_text(text)

def escape_text(text):
    return (
        str(text).replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace("\n", "\\n")
    )

def draw_lines(text, limit, max_lines, font_size, y, color="white", border=5):
    lines = wrap(text, limit=limit).splitlines()[:max_lines]
    filters = []
    for index, line in enumerate(lines):
        safe = escape_text(line)
        filters.append(
            f"drawtext=fontfile={FONT}:text='{safe}':fontcolor={color}:fontsize={font_size}:"
            f"x=(w-text_w)/2:y={y + index * int(font_size * 1.12)}:"
            f"borderw={border}:bordercolor=black@0.9"
        )
    return ",".join(filters)
