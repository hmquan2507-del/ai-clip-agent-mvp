# AI Clip Agent MVP

MVP local cho hướng sản phẩm: **SaaS video editor AI-first**. User upload video lên, phần mềm tạo workspace edit gồm Footage, Subtitle, B-roll, Sound effect, Nhạc nền và Export. Có 2 luồng chính: edit nguyên clip thô hoặc cắt video dài thành nhiều clip rồi edit từng clip.

## Chạy thử

```bash
cd /home/chotnhanh/.openclaw/workspace/ai-clip-agent-mvp
python3 server.py
```

Mở:

```text
http://localhost:8765
```

## Luồng hiện có

- Upload video dài hoặc video thô.
- Chọn kiểu xử lý: tự động, clip thô ngắn, hoặc video dài.
- Chọn độ dài mỗi clip: 15/30/45/60/90 giây.
- Nhập yêu cầu riêng của khách để định hướng hook/caption.
- Nhập caption chính, niche và mục tiêu video.
- Tạo transcript bằng `faster-whisper` nếu môi trường đã cài; nếu chưa có thì tạo transcript scaffold để workspace vẫn chạy đủ flow.
- Hệ thống đề xuất 3-8 đoạn cắt theo thời lượng video.
- Clip suggestion ưu tiên lấy hook từ transcript segment khi có dữ liệu transcript.
- Tạo Editor Workspace cho từng job: Footage, Subtitle, B-roll, Sound effect, Nhạc nền, Export.
- Lưu asset bin và các bước edit cho từng clip vào SQLite.
- Render clip dọc 1080x1920 bằng `ffmpeg`.
- Thêm hook đầu video, caption và CTA cuối.
- Xuất file MP4 để tải xuống.
- Lưu account demo, job, suggestion, output và quota vào SQLite.
- Dashboard có sidebar, thống kê quota, editor workspace, job gần đây và output trong phiên.

## Template render hiện có

- `talking-head`: mặc định cho sản phẩm chính, crop video thành format người nói dọc, nền blur, hook trên đầu, caption lớn phía dưới, CTA và progress bar.
- `classic`: video dọc đơn giản có hook/caption/CTA.
- `raw-edited`: style theo clip mẫu của anh Quân, gồm nền lưới tối, nhãn RAW/EDITED, khung raw bên trái, khung edited bên phải, caption lớn và timeline giả lập phía dưới.

## Cấu trúc MVP SaaS

```text
ai-clip-agent-mvp/
  server.py                  # HTTP server, API, SQLite, ffmpeg render
  worker.py                  # Render worker for queued production-style jobs
  storage.py                 # Local/S3/R2 storage adapters
  .env.example               # Production storage/env template
  static/
    index.html               # Dashboard UI
    styles.css               # UI/UX SaaS layout
    app.js                   # Fetch API, render state, dashboard state
  data/
    ai_clip_agent.sqlite3    # Database local
    jobs/                    # File upload và video output
```

## Database MVP

- `accounts`: account demo và gói dùng thử.
- `jobs`: video upload, mode xử lý, style render, yêu cầu khách.
- `jobs.storage_provider`, `storage_key`, `storage_url`, `file_size`, `mime_type`, `expires_at`: metadata file/video để production không lưu binary trong DB.
- `suggestions`: clip đề xuất, thời điểm bắt đầu, hook/caption/CTA.
- `transcript_segments`: transcript theo mốc thời gian, dùng làm input cho highlight/subtitle.
- `editor_assets`: asset workspace gồm footage, subtitle, B-roll, SFX, music.
- `editor_steps`: các bước edit cho từng clip.
- `render_tasks`: hàng đợi render để web server không phải xử lý video nặng trực tiếp.
- `outputs`: video đã render.

## API nội bộ

- `GET /api/dashboard` - account demo, quota, stats, recent jobs.
- `POST /api/upload` - upload video và tạo suggestions.
- `POST /api/uploads/presign` - tạo signed URL cho browser upload trực tiếp lên S3/R2 khi dùng production storage.
- `POST /api/render` - render các clip đã chọn.

## Render Queue

Local MVP mặc định dùng:

```text
RENDER_MODE=sync
```

Production nên dùng:

```text
RENDER_MODE=queue
python3 worker.py
```

Khi `RENDER_MODE=queue`, API `/api/render` chỉ tạo record trong `render_tasks` và trả về trạng thái queued. Worker riêng sẽ lấy từng task pending, render bằng ffmpeg, cập nhật output. Đây là nền để scale nhiều worker sau này thay vì làm nặng web server.

## Storage Production

MVP local dùng `STORAGE_PROVIDER=local` và lưu file trong `data/jobs/`.

Production nên dùng `STORAGE_PROVIDER=r2` hoặc `s3`:

```text
Browser -> /api/uploads/presign -> upload thẳng lên R2/S3
API/DB -> chỉ lưu metadata: storage_key, file_size, mime_type, duration, status
Render worker -> đọc video từ object storage khi cần render
Output -> lưu lại object storage, DB chỉ lưu link/key
```

Database không lưu binary video. App server chính không nên giữ file lớn lâu dài.

## Logic sản phẩm chính

- Clip thô ngắn (`raw_clip`): edit nguyên clip theo format talking-head.
- Video dài (`long_video`): cắt thành nhiều clip ngắn, từng clip đều render theo format talking-head.
- Tự động (`auto`): video từ 90 giây trở xuống được xem là clip thô; dài hơn 90 giây được xem là video dài.
- Workspace editor luôn được tạo sau upload để user thấy đầy đủ quy trình edit, kể cả khi một vài track như B-roll/SFX/music mới ở trạng thái planned.
- Transcript là bước đầu của AI editor: khi `faster-whisper` có sẵn, hệ thống tạo transcript thật; khi chưa có, hệ thống tạo scaffold để không làm gãy flow MVP.

## Giới hạn bản MVP

- Chưa có LLM highlight scoring, nên đoạn hay mới ưu tiên transcript segment hoặc fallback theo thời lượng.
- Chưa gọi model AI ngoài, hook/caption vẫn là transcript/template.
- Chưa có đăng nhập thật, thanh toán, workspace nhiều khách.
- Chưa có hàng đợi render cho nhiều người dùng cùng lúc.
- B-roll, SFX và music hiện là workspace layer/planned asset; render thực tế mới áp dụng footage, subtitle/caption và loudnorm.

## Bước nâng cấp kế tiếp

- Thêm transcript bằng Whisper/faster-whisper.
- Dùng LLM để chọn đoạn có nội dung hấp dẫn thật.
- Thêm nhiều template caption theo ngành: livestream, spa, coach, bất động sản.
- Thêm lưu project, quota theo gói và tài khoản người dùng.
- Thêm landing page bán gói dùng thử.
