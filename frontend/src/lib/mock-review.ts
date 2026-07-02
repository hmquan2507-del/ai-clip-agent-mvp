export type ReviewSuggestionType =
  | "highlight"
  | "subtitle"
  | "broll"
  | "music"
  | "cta";

export type ReviewSuggestion = {
  id: string;
  type: ReviewSuggestionType;
  title: string;
  description: string;
  confidence: number;
  timestamp: string;
};

export type TranscriptSegment = {
  id: string;
  speaker: string;
  start: string;
  end: string;
  text: string;
  confidence: number;
};

export const reviewProduction = {
  id: "prd_001",
  title: "Podcast bán hàng tự động",
  status: "review_ready",
  style: "Podcast",
  duration: "02:34",
  progress: 100,
};

export const transcriptSegments: TranscriptSegment[] = [
  {
    id: "seg_001",
    speaker: "Speaker 1",
    start: "00:00",
    end: "00:12",
    text: "Hôm nay chúng ta sẽ nói về cách tự động hóa quy trình bán hàng bằng AI.",
    confidence: 0.94,
  },
  {
    id: "seg_002",
    speaker: "Speaker 1",
    start: "00:13",
    end: "00:31",
    text: "Điểm quan trọng nhất là không bắt đầu từ công cụ, mà bắt đầu từ workflow.",
    confidence: 0.91,
  },
  {
    id: "seg_003",
    speaker: "Speaker 2",
    start: "00:32",
    end: "00:48",
    text: "Nếu hệ thống hiểu đúng dữ liệu khách hàng, AI có thể đề xuất bước tiếp theo rất nhanh.",
    confidence: 0.88,
  },
];

export const reviewSuggestions: ReviewSuggestion[] = [
  {
    id: "sug_001",
    type: "highlight",
    title: "Strong opening hook",
    description: "Đoạn mở đầu có giá trị cao để dùng làm short video.",
    confidence: 92,
    timestamp: "00:00–00:12",
  },
  {
    id: "sug_002",
    type: "subtitle",
    title: "Subtitle timing looks good",
    description: "Subtitle đủ ngắn và dễ đọc trên mobile.",
    confidence: 89,
    timestamp: "00:13–00:31",
  },
  {
    id: "sug_003",
    type: "broll",
    title: "Add workflow diagram B-roll",
    description: "AI đề xuất thêm B-roll minh họa workflow bán hàng.",
    confidence: 84,
    timestamp: "00:32–00:48",
  },
];

export const subtitlePreview = [
  {
    id: "sub_001",
    time: "00:00",
    text: "Tự động hóa bán hàng bằng AI",
  },
  {
    id: "sub_002",
    time: "00:13",
    text: "Đừng bắt đầu từ công cụ. Hãy bắt đầu từ workflow.",
  },
  {
    id: "sub_003",
    time: "00:32",
    text: "AI có thể đề xuất bước tiếp theo rất nhanh.",
  },
];