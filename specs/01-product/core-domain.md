# Core Domain

Status: Draft

Owner: Ho Quan

Version: 0.1

Related Epic: EPIC-02 AI Production Workspace

---

# Purpose

Định nghĩa Domain cốt lõi của AI Clip Agent.

Tài liệu này là Single Source of Truth cho toàn bộ Product, AI, Frontend, Backend và Database.

Nếu có bất kỳ thay đổi nào về Product, phải cập nhật tài liệu này trước khi thay đổi code.

---

# Product Definition

AI Clip Agent là một AI Video Production Platform.

Mục tiêu của sản phẩm KHÔNG phải là tạo một Video Editor.

Mục tiêu của sản phẩm là giúp người dùng tiết kiệm 80–95% thời gian chỉnh sửa video bằng AI.

Người dùng chỉ cần:

1. Upload video
2. Chọn Style
3. Chờ AI xử lý
4. Review
5. Export

AI thực hiện toàn bộ quy trình dựng video.

---

# Product Vision

Upload Once.

AI Edits Everything.

Review.

Export.

---

# Core Value

Người dùng KHÔNG mua AI.

Người dùng mua thời gian.

Giá trị lớn nhất của AI Clip Agent là giảm thời gian edit video từ nhiều giờ xuống chỉ còn vài phút.

---

# What AI Clip Agent IS

AI Clip Agent là:

- AI Video Production Platform
- AI Video Editor
- AI Clip Generator
- AI Production Pipeline
- AI Style Engine

---

# What AI Clip Agent IS NOT

AI Clip Agent KHÔNG phải:

- Premiere Pro
- CapCut
- Canva
- Timeline-first editor

Timeline chỉ xuất hiện khi Review.

Không phải trung tâm của sản phẩm.

---

# Primary User

Content Creator

YouTuber

TikToker

Marketing Team

Agency

Business Owner

Educator

---

# Core Workflow

Upload

↓

AI Production

↓

Review

↓

Export

---

# Core Domain Model

Workspace

↓

Production

↓

Source Video

↓

AI Pipeline

↓

Generated Clips

↓

Review

↓

Export

---

# Production

Production là Domain quan trọng nhất của hệ thống.

Một Production đại diện cho toàn bộ quá trình AI xử lý một video.

Production bao gồm:

- Source Video
- AI Jobs
- Generated Clips
- Review State
- Export State

---

# AI Pipeline

Một Production sẽ đi qua các bước:

Upload

↓

Transcript

↓

Scene Detection

↓

Speaker Detection

↓

Emotion Detection

↓

Highlight Detection

↓

Clip Selection

↓

Subtitle

↓

Sound Effects

↓

Background Music

↓

B-roll

↓

Motion

↓

Render

↓

Review

↓

Export

---

# Style Engine

Mỗi Production phải chọn một Style.

Ví dụ:

Talking Head

Podcast

Education

Finance

Gaming

Luxury

Business

Storytelling

Mỗi Style sẽ điều khiển:

- Subtitle
- Motion
- Zoom
- Sound FX
- Music
- B-roll
- CTA

---

# Review Philosophy

AI hoàn thành khoảng 90–95%.

Người dùng chỉ chỉnh sửa những phần cần thiết.

Review luôn nhanh hơn Edit.

---

# Product Principles

AI First

Production First

Review Instead Of Edit

Automation Over Manual Work

One Click Wherever Possible

Every Screen Must Save Time

---

# Success Metrics

Giảm thời gian edit >80%

Thời gian Review <5 phút

Nhiều video được tạo hơn trên mỗi người dùng

Ít thao tác thủ công hơn

---

# Future Vision

AI Clip Agent sẽ trở thành AI Video Production OS.

Thay vì chỉnh sửa video,

người dùng sẽ quản lý quá trình AI sản xuất video.

