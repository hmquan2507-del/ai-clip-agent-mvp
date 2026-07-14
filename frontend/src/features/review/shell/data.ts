import type {
  LucideIcon,
} from "lucide-react";

import {
  Captions,
  Clapperboard,
  ImagePlus,
  Music2,
  Palette,
  Sparkles,
  Type,
  WandSparkles,
} from "lucide-react";

export interface ReviewToolItem {
  id: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
}

export interface ReviewTimelineClipFixture {
  id: string;
  label: string;
  start: number;
  width: number;
  tone:
    | "video"
    | "broll"
    | "subtitle"
    | "audio";
}

export interface ReviewTimelineTrackFixture {
  id: string;
  label: string;
  icon: LucideIcon;
  clips: ReviewTimelineClipFixture[];
}

export const reviewTools:
  ReviewToolItem[] = [
    {
      id: "media",
      label: "Media",
      icon: ImagePlus,
      active: true,
    },
    {
      id: "text",
      label: "Văn bản",
      icon: Type,
    },
    {
      id: "captions",
      label: "Phụ đề",
      icon: Captions,
    },
    {
      id: "audio",
      label: "Âm thanh",
      icon: Music2,
    },
    {
      id: "brand",
      label: "Thương hiệu",
      icon: Palette,
    },
    {
      id: "effects",
      label: "Hiệu ứng",
      icon: WandSparkles,
    },
    {
      id: "ai",
      label: "AI Tools",
      icon: Sparkles,
    },
  ];

export const timelineTracks:
  ReviewTimelineTrackFixture[] = [
    {
      id: "video-primary",
      label: "Video chính",
      icon: Clapperboard,
      clips: [
        {
          id: "hook",
          label: "Hook mở đầu",
          start: 0,
          width: 26,
          tone: "video",
        },
        {
          id: "body",
          label: "Nội dung chính",
          start: 27,
          width: 45,
          tone: "video",
        },
        {
          id: "cta",
          label: "CTA",
          start: 73,
          width: 25,
          tone: "video",
        },
      ],
    },
    {
      id: "broll",
      label: "B-roll",
      icon: ImagePlus,
      clips: [
        {
          id: "broll-1",
          label: "Sản phẩm",
          start: 13,
          width: 18,
          tone: "broll",
        },
        {
          id: "broll-2",
          label: "Dashboard",
          start: 44,
          width: 22,
          tone: "broll",
        },
      ],
    },
    {
      id: "subtitle",
      label: "Phụ đề",
      icon: Captions,
      clips: [
        {
          id: "sub-1",
          label:
            "Sai lầm khiến video...",
          start: 0,
          width: 31,
          tone: "subtitle",
        },
        {
          id: "sub-2",
          label:
            "Bạn đang bỏ lỡ...",
          start: 32,
          width: 33,
          tone: "subtitle",
        },
        {
          id: "sub-3",
          label:
            "Thử ngay hôm nay",
          start: 66,
          width: 32,
          tone: "subtitle",
        },
      ],
    },
    {
      id: "audio",
      label: "Nhạc nền",
      icon: Music2,
      clips: [
        {
          id: "music",
          label:
            "Future Pulse · 92 BPM",
          start: 0,
          width: 98,
          tone: "audio",
        },
      ],
    },
  ];

export const rulerMarks = [
  "00:00",
  "00:05",
  "00:10",
  "00:15",
  "00:20",
  "00:25",
];