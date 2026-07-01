from config import FONT
from text_utils import draw_lines, drawtext_escape
from utils import run

def render_clip(input_path, output_path, suggestion, style="classic"):
    if style == "talking-head":
        return render_talking_head_clip(input_path, output_path, suggestion)
    return render_classic_clip(input_path, output_path, suggestion)

def render_classic_clip(input_path, output_path, suggestion):
    hook = drawtext_escape(suggestion["hook"])
    caption = drawtext_escape(suggestion["caption"])
    cta = drawtext_escape(suggestion["cta"])
    vf = (
        "scale=1080:-2:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawbox=x=0:y=0:w=iw:h=330:color=black@0.50:t=fill,"
        f"drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize=58:"
        "line_spacing=16:x=(w-text_w)/2:y=82:box=1:boxcolor=black@0.25:boxborderw=22,"
        "drawbox=x=0:y=1515:w=iw:h=405:color=black@0.62:t=fill,"
        f"drawtext=fontfile={FONT}:text='{caption}':fontcolor=white:fontsize=54:"
        "line_spacing=14:x=(w-text_w)/2:y=1580:box=1:boxcolor=black@0.20:boxborderw=18,"
        f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=#ffe066:fontsize=42:"
        "x=(w-text_w)/2:y=1788"
    )
    run([
        "ffmpeg",
        "-y",
        "-ss",
        str(suggestion["start"]),
        "-t",
        str(suggestion["duration"]),
        "-i",
        str(input_path),
        "-vf",
        vf,
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output_path),
    ])

def render_talking_head_clip(input_path, output_path, suggestion):
    hook_lines = draw_lines(suggestion["hook"], limit=16, max_lines=2, font_size=46, y=56)
    caption_lines = draw_lines(suggestion["caption"], limit=17, max_lines=2, font_size=56, y=1530)
    cta_lines = draw_lines(suggestion["cta"], limit=22, max_lines=1, font_size=40, y=1772, color="0xffe066", border=4)
    filter_complex = (
        "[0:v]split=2[bgsrc][fgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=18:2,eq=brightness=-0.10:saturation=0.92[bg];"
        "[fgsrc]scale=980:1742:force_original_aspect_ratio=increase,"
        "crop=980:1742,setsar=1[fg];"
        "[bg]drawbox=x=0:y=0:w=1080:h=250:color=black@0.36:t=fill,"
        "drawbox=x=0:y=1490:w=1080:h=430:color=black@0.55:t=fill[base];"
        "[base][fg]overlay=50:130[tmp];"
        "[tmp]drawbox=x=50:y=130:w=980:h=1742:color=white@0.55:t=4,"
        f"{hook_lines},"
        f"{caption_lines},"
        f"{cta_lines},"
        "drawbox=x=0:y=1908:w=1080:h=12:color=white@0.18:t=fill,"
        "drawbox=x=0:y=1908:w=760:h=12:color=0xffe066@0.95:t=fill[v]"
    )
    run([
        "ffmpeg",
        "-y",
        "-ss",
        str(suggestion["start"]),
        "-t",
        str(suggestion["duration"]),
        "-i",
        str(input_path),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ])
